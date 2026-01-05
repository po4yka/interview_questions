---
id: kotlin-128
title: "Structured Concurrency / Структурированная параллельность"
aliases: ["Structured Concurrency", "Структурированная параллельность"]

# Classification
topic: kotlin
subtopics: [cancellation, coroutines, structured-concurrency]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive guide on Structured Concurrency

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-coroutines, c-kotlin, q-actor-pattern--kotlin--hard, q-advanced-coroutine-patterns--kotlin--hard]

# Timestamps
created: 2025-10-12
updated: 2025-11-10

tags: [cancellation, coroutines, difficulty/hard, exception-handling, kotlin, scope, structured-concurrency]
---
# Вопрос (RU)
> Что такое структурированная параллельность в Kotlin? Объясните иерархию родитель-потомок корутин, распространение отмены, распространение исключений и разницу между coroutineScope, supervisorScope и withContext.

---

# Question (EN)
> What is structured concurrency in Kotlin? Explain parent-child coroutine hierarchy, cancellation propagation, exception propagation, and differences between coroutineScope, supervisorScope, and withContext.

## Ответ (RU)

**Структурированная параллельность** гарантирует, что корутины следуют чёткой иерархии родитель-потомок, обеспечивая автоматическое распространение отмены, предсказуемое распространение исключений и корректную очистку ресурсов. См. также [[c-kotlin]] и [[c-coroutines]].

### Основные Принципы

1. **Иерархия**: Корутины формируют отношения родитель-потомок.
2. **Время жизни**: Время жизни потомка привязано к родителю.
3. **Отмена**: Распространяется от родителя к потомкам.
4. **Исключения**: По умолчанию исключения потомка (в обычных скоупах) распространяются к родителю и отменяют сиблингов.
5. **Завершение**: Родитель ждёт всех потомков.

### Иерархия Корутин

```kotlin
import kotlinx.coroutines.*

suspend fun example() = coroutineScope {  // Родительский scope
    launch {                                // Потомок 1
        launch {                            // Внук
            delay(1000)
            println("Grandchild")
        }
        delay(500)
        println("Child 1")
    }
    
    launch {                                // Потомок 2
        delay(300)
        println("Child 2")
    }
    
    println("Parent waiting...")
    // Родитель ждёт завершения всех потомков и внуков
}

// Примерный вывод:
// Parent waiting...
// Child 2 (после 300 мс)
// Child 1 (после 500 мс)
// Grandchild (после 1000 мс)
// example() вернётся только после завершения всех корутин
```

### coroutineScope

Создаёт новый scope с новым дочерним Job, который ждёт всех своих потомков:

```kotlin
suspend fun processData() = coroutineScope {
    val deferred1 = async { loadData1() }
    val deferred2 = async { loadData2() }
    
    val result1 = deferred1.await()
    val result2 = deferred2.await()
    
    result1 + result2
    // coroutineScope завершится только после завершения обоих async
}

suspend fun loadData1(): Int {
    delay(1000)
    return 42
}

suspend fun loadData2(): Int {
    delay(500)
    return 58
}
```

**Обработка исключений:**

```kotlin
suspend fun withExceptions() {
    try {
        coroutineScope {
            launch {
                delay(100)
                throw Exception("Child failed")
            }
            
            launch {
                delay(500)
                println("This will be cancelled before it prints")
            }
        }
    } catch (e: Exception) {
        println("Caught: ${e.message}")
        // Caught: Child failed
    }
}

// При сбое ЛЮБОГО потомка в coroutineScope:
// 1. Все сиблинги отменяются.
// 2. Первое исключение пробрасывается родителю.
// 3. Родительский scope завершается с ошибкой.
```

### supervisorScope

Создаёт scope с SupervisorJob, где сбой одной дочерней корутины не отменяет её "соседей". Однако, если исключение не обработано внутри дочерней корутины, `supervisorScope` завершится с этим исключением и пробросит его наверх.

```kotlin
suspend fun withSupervisor() = supervisorScope {
    val job1 = launch {
        delay(100)
        throw Exception("Job 1 failed")
    }
    
    val job2 = launch {
        delay(500)
        println("Job 2 completed")  // Может выполниться, даже если Job 1 упал
    }
    
    // Если исключение Job 1 не перехвачено, supervisorScope пробросит его после завершения тела,
    // при этом Job 2 остаётся независимым.
}

// Сбой Job 1 не отменяет Job 2 автоматически.
// Неперехваченное исключение всё равно выходит из supervisorScope к родителю.
```

**Кейс: независимые задачи**

```kotlin
class DataSyncer {
    suspend fun syncAll() = supervisorScope {
        // Каждая синхронизация независима
        launch {
            try {
                syncUsers()
            } catch (e: Exception) {
                logError("Users sync failed", e)
            }
        }
        
        launch {
            try {
                syncPosts()
            } catch (e: Exception) {
                logError("Posts sync failed", e)
            }
        }
        
        launch {
            try {
                syncComments()
            } catch (e: Exception) {
                logError("Comments sync failed", e)
            }
        }
        
        // Исключения из дочерних корутин локально обработаны;
        // supervisorScope завершается нормально.
    }
    
    private suspend fun syncUsers() { delay(1000) }
    private suspend fun syncPosts() { delay(1000) }
    private suspend fun syncComments() { delay(1000) }
    private fun logError(msg: String, e: Exception) = println("$msg: $e")
}
```

### withContext

Переключает контекст выполнения (например, диспетчер) для вызывающей корутины. Он:
- создаёт новый комбинированный контекст для блока;
- использует родительский Job, если не указан другой;
- приостанавливает вызывающую корутину до завершения блока (и его потомков).

```kotlin
suspend fun loadUser(id: Int): User = withContext(Dispatchers.IO) {
    // Переключается на IO-диспетчер, вызывающая корутина приостанавливается
    database.getUser(id)
}

// vs coroutineScope
suspend fun loadUserScope(id: Int): User = coroutineScope {
    // Создаёт новый дочерний Job, но остаётся на текущем диспетчере по умолчанию
    database.getUser(id)
}
```

### Распространение Отмены

**Родитель -> потомок:**

```kotlin
suspend fun parentCancellation() = coroutineScope {
    val job = launch {
        repeat(5) { i ->
            delay(500)
            println("Child: $i")
        }
    }
    
    delay(1500)
    cancel() // Отмена родительского scope
    
    // Потомок будет автоматически отменён
}

// Вывод:
// Child: 0
// Child: 1
// Child: 2
// (затем отмена)
```

**Потомок -> родитель (через исключение):**

```kotlin
suspend fun childException() {
    try {
        coroutineScope {
            launch {
                delay(100)
                throw Exception("Child failed")
            }
            
            launch {
                repeat(10) {
                    delay(200)
                    println("Sibling: $it")
                }
            }
        }
    } catch (e: Exception) {
        println("Parent caught: ${e.message}")
    }
}

// Потомок кидает исключение -> scope завершается с ошибкой ->
// родитель ловит исключение, второй потомок отменяется и не успевает напечатать.
```

### Стратегии Обработки Исключений

**Стратегия 1: try-catch в дочерней корутине**

```kotlin
coroutineScope {
    launch {
        try {
            riskyOperation()
        } catch (e: Exception) {
            // Локальная обработка
            println("Handled in child: $e")
        }
    }
}
```

**Стратегия 2: supervisorScope / SupervisorJob**

```kotlin
supervisorScope {
    launch {
        riskyOperation() // Может упасть, не отменяя сиблингов
    }
    
    launch {
        anotherOperation() // Продолжит работу, даже если сосед упал
    }
}
```

**Стратегия 3: CoroutineExceptionHandler**

```kotlin
val handler = CoroutineExceptionHandler { _, exception ->
    println("Caught: ${exception.message}")
}

val scope = CoroutineScope(SupervisorJob() + handler)

scope.launch {
    throw Exception("Error")
    // Будет перехвачено handler для корня; не "роняет" весь процесс
}
```

### Реальный Пример: Параллельная Загрузка Данных

```kotlin
class UserProfileLoader(
    private val userApi: UserApi,
    private val postsApi: PostsApi,
    private val friendsApi: FriendsApi
) {
    suspend fun loadProfile(userId: Int): UserProfile = coroutineScope {
        // Все запросы в параллели
        val userDeferred = async { userApi.getUser(userId) }
        val postsDeferred = async { postsApi.getPosts(userId) }
        val friendsDeferred = async { friendsApi.getFriends(userId) }
        
        val user = userDeferred.await()
        val posts = postsDeferred.await()
        val friends = friendsDeferred.await()
        
        // Если ЛЮБОЙ запрос падает (и не обработан), остальные отменяются,
        // а исключение пробрасывается вызывающему коду.
        UserProfile(user, posts, friends)
    }
    
    suspend fun loadProfileResilient(userId: Int): UserProfile = supervisorScope {
        val userDeferred = async {
            try {
                userApi.getUser(userId)
            } catch (e: Exception) {
                null
            }
        }
        
        val postsDeferred = async {
            try {
                postsApi.getPosts(userId)
            } catch (e: Exception) {
                emptyList()
            }
        }
        
        val friendsDeferred = async {
            try {
                friendsApi.getFriends(userId)
            } catch (e: Exception) {
                emptyList()
            }
        }
        
        UserProfile(
            user = userDeferred.await(),
            posts = postsDeferred.await(),
            friends = friendsDeferred.await()
        )
        // Устойчивый вариант: каждая ошибка обрабатывается независимо,
        // supervisorScope завершается нормально.
    }
}

data class UserProfile(val user: User?, val posts: List<Post>, val friends: List<User>)
```

### Иерархия Job

```kotlin
fun demonstrateJobHierarchy() = runBlocking {
    val parentJob = launch {
        println("Parent started")
        
        val child1 = launch {
            println("Child 1 started")
            delay(1000)
            println("Child 1 completed")
        }
        
        val child2 = launch {
            println("Child 2 started")
            delay(500)
            println("Child 2 completed")
        }
        
        println("Parent waiting for children")
        child1.join()
        child2.join()
        println("Parent completed")
    }
    
    parentJob.join()
    println("All completed")
}

// Иерархия Job:
// parentJob
//    child1
//    child2
```

### Таблица Сравнения

| Функция | coroutineScope | supervisorScope | withContext |
|--------|----------------|-----------------|-------------|
| Создаёт новый Job | Да (дочерний Job) | Да (SupervisorJob) | Нет (наследует Job, можно переопределить) |
| Поведение исключений дочерних | Исключение отменяет сиблингов, пробрасывается родителю | Не отменяет сиблингов, но неперехваченное пробрасывается из scope наружу | Исключения из блока пробрасываются вызывающему коду |
| Ждёт потомков | Да | Да | Ждёт завершения тела и любых потомков внутри блока |
| Меняет диспетчер | Нет | Нет | Да (опционально) |

### Продвинутые Паттерны

**Паттерн 1: timeout с очисткой**

```kotlin
suspend fun withTimeoutExample() = coroutineScope {
    val job = launch {
        try {
            longRunningOperation()
        } finally {
            cleanup() // Гарантированно выполнится при отмене или завершении
        }
    }
    
    withTimeout(5000) {
        job.join()
    }
}
```

**Паттерн 2: Корректная отмена (graceful cancellation)**

```kotlin
suspend fun gracefulOperation() = coroutineScope {
    val job = launch {
        try {
            while (isActive) { // Проверяем отмену
                processItem()
                delay(100)
            }
        } finally {
            withContext(NonCancellable) {
                // Очистка, которая должна завершиться
                saveState()
            }
        }
    }
    
    // Триггер отмены может быть добавлен здесь при необходимости
}
```

**Паттерн 3: Очистка ресурсов**

```kotlin
suspend fun withResource() = coroutineScope {
    val resource = acquireResource()
    
    try {
        launch {
            useResource(resource)
        }
    } finally {
        resource.release()
        // Гарантированно вызывается даже при отмене scope
    }
}
```

### Рекомендации (Best Practices)

#### DO (делайте):

```kotlin
// Используйте coroutineScope для связанных задач
suspend fun loadData() = coroutineScope {
    val a = async { loadA() }
    val b = async { loadB() }
    combine(a.await(), b.await())
}

// Используйте supervisorScope для независимых задач
suspend fun syncAll() = supervisorScope {
    launch { syncUsers() }
    launch { syncPosts() }
}

// Обрабатывайте отмену
launch {
    try {
        work()
    } finally {
        cleanup()
    }
}

// Проверяйте isActive в циклах
while (isActive) {
    processNext()
}
```

#### DON'T (не делайте):

```kotlin
// Не глотайте CancellationException
try {
    work()
} catch (e: Exception) {
    if (e is CancellationException) throw e
}

// Не используйте GlobalScope для структурированной работы
GlobalScope.launch {
    // Нет структурированной параллельности: время жизни не привязано к компоненту
}

// Не блокируйте потоки
launch {
    Thread.sleep(1000) // Плохо, используйте delay(1000)
}

// Не забывайте про обработку исключений в корневых scope
coroutineScope {
    launch {
        riskyOperation() // Сбой отменит сиблингов и пробросится наверх
    }
}
```

### Тестирование Структурированной Параллельности

```kotlin
@Test
fun testCancellation() = runTest {
    val job = launch {
        repeat(10) {
            delay(100)
        }
    }
    
    delay(250)
    job.cancel()
    
    assertFalse(job.isActive)
}

@Test
fun testExceptionPropagation() = runTest {
    var caught = false
    try {
        coroutineScope {
            launch {
                throw Exception("Failed")
            }
        }
    } catch (e: Exception) {
        caught = true
    }
    assertTrue(caught)
}
```

---

## Answer (EN)

**Structured concurrency** ensures that coroutines follow a clear parent-child hierarchy, providing automatic cancellation propagation, predictable exception propagation, and proper resource cleanup. See also [[c-kotlin]] and [[c-coroutines]].

### Core Principles

1. **Hierarchy**: Coroutines form parent-child relationships.
2. **Lifetime**: Child lifetime is bound to its parent.
3. **Cancellation**: Propagates from parent to children.
4. **Exceptions**: By default, child exceptions (in regular scopes) cancel siblings and propagate to the parent.
5. **Completion**: Parent waits for all children.

### Coroutine Hierarchy

```kotlin
import kotlinx.coroutines.*

suspend fun example() = coroutineScope {  // Parent scope
    launch {                                // Child 1
        launch {                            // Grandchild
            delay(1000)
            println("Grandchild")
        }
        delay(500)
        println("Child 1")
    }
    
    launch {                                // Child 2
        delay(300)
        println("Child 2")
    }
    
    println("Parent waiting...")
    // Parent waits for ALL children and grandchildren
}

// Output:
// Parent waiting...
// Child 2 (after 300ms)
// Child 1 (after 500ms)
// Grandchild (after 1000ms)
// example() returns only after all complete
```

### coroutineScope

Creates a new scope with a new child Job that waits for all its children:

```kotlin
suspend fun processData() = coroutineScope {
    val deferred1 = async { loadData1() }
    val deferred2 = async { loadData2() }
    
    val result1 = deferred1.await()
    val result2 = deferred2.await()
    
    result1 + result2
    // coroutineScope completes only after both async coroutines finish (successfully or exceptionally)
}

suspend fun loadData1(): Int {
    delay(1000)
    return 42
}

suspend fun loadData2(): Int {
    delay(500)
    return 58
}
```

**Exception handling:**

```kotlin
suspend fun withExceptions() {
    try {
        coroutineScope {
            launch {
                delay(100)
                throw Exception("Child failed")
            }
            
            launch {
                delay(500)
                println("This will be cancelled before it prints")
            }
        }
    } catch (e: Exception) {
        println("Caught: ${e.message}")
        // Caught: Child failed
    }
}

// When ANY child fails in coroutineScope:
// 1. All siblings are cancelled
// 2. The first failure propagates to the parent
// 3. The parent scope completes exceptionally and throws
```

### supervisorScope

Creates a scope with a SupervisorJob where one child’s failure does not cancel its siblings. However, if a child’s exception is not handled within that child, `supervisorScope` itself will complete exceptionally and rethrow the exception to its parent.

```kotlin
suspend fun withSupervisor() = supervisorScope {
    val job1 = launch {
        delay(100)
        throw Exception("Job 1 failed")
    }
    
    val job2 = launch {
        delay(500)
        println("Job 2 completed")  // Can still execute even if Job 1 fails
    }
    
    // If Job 1's exception is not caught, supervisorScope will rethrow it
    // after its body completes (while preserving Job 2's independence).
}

// Job 1 failure does not automatically cancel Job 2.
// Unhandled exception still escapes from supervisorScope to its caller.
```

**Use case: Independent tasks**

```kotlin
class DataSyncer {
    suspend fun syncAll() = supervisorScope {
        // Each sync is independent
        launch {
            try {
                syncUsers()
            } catch (e: Exception) {
                logError("Users sync failed", e)
            }
        }
        
        launch {
            try {
                syncPosts()
            } catch (e: Exception) {
                logError("Posts sync failed", e)
            }
        }
        
        launch {
            try {
                syncComments()
            } catch (e: Exception) {
                logError("Comments sync failed", e)
            }
        }
        
        // Failures are isolated by local try/catch; supervisorScope itself
        // completes normally if exceptions are handled.
    }
    
    private suspend fun syncUsers() { delay(1000) }
    private suspend fun syncPosts() { delay(1000) }
    private suspend fun syncComments() { delay(1000) }
    private fun logError(msg: String, e: Exception) = println("$msg: $e")
}
```

### withContext

Switches the coroutine context (e.g., dispatcher) of the current coroutine. It:
- creates a new combined context for the block;
- uses the parent Job unless another Job is provided;
- suspends until the block (and its children) completes.

```kotlin
suspend fun loadUser(id: Int): User = withContext(Dispatchers.IO) {
    // Switches to IO dispatcher
    // Caller is suspended until this block completes
    database.getUser(id)
}

// vs coroutineScope
suspend fun loadUserScope(id: Int): User = coroutineScope {
    // Creates new child Job but stays on current dispatcher by default
    database.getUser(id)
}
```

**Key differences:**

```kotlin
// withContext: Changes dispatcher or context, inherits Job (unless overridden)
suspend fun example1() = withContext(Dispatchers.IO) {
    // Runs on IO dispatcher
    // Uses parent's Job by default
    // Suspends caller until completion
}

// coroutineScope: Same dispatcher (unless changed inside), new child Job
suspend fun example2() = coroutineScope {
    // Runs on current dispatcher
    // Creates new child Job
    // Waits for all child coroutines in this scope
}

// supervisorScope: Same dispatcher, SupervisorJob
suspend fun example3() = supervisorScope {
    // Runs on current dispatcher
    // Uses SupervisorJob semantics
    // Child failures don't cancel siblings, but unhandled ones still escape
}
```

### Cancellation Propagation

**Parent to child:**

```kotlin
suspend fun parentCancellation() = coroutineScope {
    val job = launch {
        repeat(5) { i ->
            delay(500)
            println("Child: $i")
        }
    }
    
    delay(1500)
    cancel() // Cancel parent scope
    
    // Child is automatically cancelled
}

// Output:
// Child: 0
// Child: 1
// Child: 2
// (then cancelled)
```

**Child to parent (with exception):**

```kotlin
suspend fun childException() {
    try {
        coroutineScope {
            launch {
                delay(100)
                throw Exception("Child failed")
            }
            
            launch {
                repeat(10) {
                    delay(200)
                    println("Sibling: $it")
                }
            }
        }
    } catch (e: Exception) {
        println("Parent caught: ${e.message}")
    }
}

// Output:
// (after 100ms)
// Parent caught: Child failed
// Sibling never prints (cancelled)
```

### Exception Handling Strategies

**Strategy 1: Try-catch in child**

```kotlin
coroutineScope {
    launch {
        try {
            riskyOperation()
        } catch (e: Exception) {
            // Handle locally
            println("Handled in child: $e")
        }
    }
}
```

**Strategy 2: supervisorScope / SupervisorJob**

```kotlin
supervisorScope {
    launch {
        riskyOperation() // Can fail without cancelling siblings
    }
    
    launch {
        anotherOperation() // Continues even if sibling fails
    }
}
```

**Strategy 3: CoroutineExceptionHandler**

```kotlin
val handler = CoroutineExceptionHandler { _, exception ->
    println("Caught: ${exception.message}")
}

val scope = CoroutineScope(SupervisorJob() + handler)

scope.launch {
    throw Exception("Error")
    // Caught by handler for this root coroutine; doesn't crash the process
}
```

### Real-World Example: Parallel Data Loading

```kotlin
class UserProfileLoader(
    private val userApi: UserApi,
    private val postsApi: PostsApi,
    private val friendsApi: FriendsApi
) {
    suspend fun loadProfile(userId: Int): UserProfile = coroutineScope {
        // Launch all requests in parallel
        val userDeferred = async { userApi.getUser(userId) }
        val postsDeferred = async { postsApi.getPosts(userId) }
        val friendsDeferred = async { friendsApi.getFriends(userId) }
        
        // Wait for all to complete
        val user = userDeferred.await()
        val posts = postsDeferred.await()
        val friends = friendsDeferred.await()
        
        // If ANY request fails (and not handled), all others are cancelled
        // and the exception is propagated to the caller.
        UserProfile(user, posts, friends)
    }
    
    suspend fun loadProfileResilient(userId: Int): UserProfile = supervisorScope {
        val userDeferred = async {
            try {
                userApi.getUser(userId)
            } catch (e: Exception) {
                null // Continue even if user request fails
            }
        }
        
        val postsDeferred = async {
            try {
                postsApi.getPosts(userId)
            } catch (e: Exception) {
                emptyList()
            }
        }
        
        val friendsDeferred = async {
            try {
                friendsApi.getFriends(userId)
            } catch (e: Exception) {
                emptyList()
            }
        }
        
        UserProfile(
            user = userDeferred.await(),
            posts = postsDeferred.await(),
            friends = friendsDeferred.await()
        )
        // Resilient: Each failure handled independently; supervisorScope completes normally.
    }
}

data class UserProfile(val user: User?, val posts: List<Post>, val friends: List<User>)
```

### Job Hierarchy

```kotlin
fun demonstrateJobHierarchy() = runBlocking {
    val parentJob = launch {
        println("Parent started")
        
        val child1 = launch {
            println("Child 1 started")
            delay(1000)
            println("Child 1 completed")
        }
        
        val child2 = launch {
            println("Child 2 started")
            delay(500)
            println("Child 2 completed")
        }
        
        println("Parent waiting for children")
        child1.join()
        child2.join()
        println("Parent completed")
    }
    
    parentJob.join()
    println("All completed")
}

// Job hierarchy:
// parentJob
//    child1
//    child2
```

### Comparison Table

| Feature | coroutineScope | supervisorScope | withContext |
|--------|----------------|-----------------|-------------|
| Creates new Job | Yes (child Job) | Yes (SupervisorJob) | No (inherits Job unless overridden) |
| Exception semantics | Child failure cancels siblings and is rethrown to parent | Child failure does not cancel siblings; unhandled failure is rethrown from scope | Exceptions from block are rethrown to caller |
| Waits for children | Yes | Yes | Yes, waits for block and its children |
| Changes dispatcher | No | No | Yes (optional) |
| Typical use case | Related tasks, all must succeed or fail together | Independent tasks, failure isolation | Change dispatcher/context for a suspending block |

### Advanced Patterns

**Pattern 1: Timeout with cleanup**

```kotlin
suspend fun withTimeoutExample() = coroutineScope {
    val job = launch {
        try {
            longRunningOperation()
        } finally {
            cleanup() // Always runs when job is cancelled or completes
        }
    }
    
    withTimeout(5000) {
        job.join()
    }
}
```

**Pattern 2: Graceful cancellation**

```kotlin
suspend fun gracefulOperation() = coroutineScope {
    val job = launch {
        try {
            while (isActive) { // Check cancellation
                processItem()
                delay(100)
            }
        } finally {
            withContext(NonCancellable) {
                // Cleanup that must complete
                saveState()
            }
        }
    }
    
    // Example cancellation trigger could be placed here if needed
}
```

**Pattern 3: Resource cleanup**

```kotlin
suspend fun withResource() = coroutineScope {
    val resource = acquireResource()
    
    try {
        launch {
            useResource(resource)
        }
    } finally {
        resource.release()
        // Guaranteed to run even if scope is cancelled
    }
}
```

### Best Practices

#### DO:

```kotlin
// Use coroutineScope for related tasks
suspend fun loadData() = coroutineScope {
    val a = async { loadA() }
    val b = async { loadB() }
    combine(a.await(), b.await())
}

// Use supervisorScope for independent tasks
suspend fun syncAll() = supervisorScope {
    launch { syncUsers() }
    launch { syncPosts() }
}

// Handle cancellation
launch {
    try {
        work()
    } finally {
        cleanup()
    }
}

// Check isActive in loops
while (isActive) {
    processNext()
}
```

#### DON'T:

```kotlin
// Don't blindly swallow CancellationException
try {
    work()
} catch (e: Exception) {
    // If you catch Exception, rethrow CancellationException to avoid breaking cancellation
    if (e is CancellationException) throw e
}

// Don't use GlobalScope for structured work
GlobalScope.launch {
    // No structured concurrency: lifetime is not bound to any component
}

// Don't block coroutine threads
launch {
    Thread.sleep(1000) // Bad!
    // Use delay(1000) instead
}

// Don't forget exception handling in root scopes
coroutineScope {
    launch {
        riskyOperation() // Failure will cancel siblings and propagate
    }
}
```

### Testing Structured Concurrency

```kotlin
@Test
fun testCancellation() = runTest {
    val job = launch {
        repeat(10) {
            delay(100)
        }
    }
    
    delay(250)
    job.cancel()
    
    assertFalse(job.isActive)
}

@Test
fun testExceptionPropagation() = runTest {
    // For suspending tests, use runTest + try/catch instead of assertThrows
    var caught = false
    try {
        coroutineScope {
            launch {
                throw Exception("Failed")
            }
        }
    } catch (e: Exception) {
        caught = true
    }
    assertTrue(caught)
}
```

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Coroutine Context and Dispatchers](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)
- [Structured Concurrency](https://kotlinlang.org/docs/coroutines-basics.html#structured-concurrency)
- [Coroutine Exceptions](https://kotlinlang.org/docs/exception-handling.html)

## Related Questions

- [[q-actor-pattern--kotlin--hard]]
- [[q-advanced-coroutine-patterns--kotlin--hard]]
- [[q-coroutine-dispatchers--kotlin--medium]]
- [[q-flow-basics--kotlin--easy]]

## MOC Links

- [[moc-kotlin]]
