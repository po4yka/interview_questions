---
id: kotlin-128
title: "Structured Concurrency / Структурированная параллельность"
aliases: ["Structured Concurrency, Структурированная параллельность"]

# Classification
topic: kotlin
subtopics:
  - cancellation
  - coroutines
  - exception-handling
  - scope
  - structured-concurrency
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
related: [q-actor-pattern--kotlin--hard, q-advanced-coroutine-patterns--kotlin--hard, q-coroutine-dispatchers--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [cancellation, coroutines, difficulty/hard, exception-handling, kotlin, scope, structured-concurrency]
date created: Sunday, October 12th 2025, 3:22:19 pm
date modified: Saturday, November 1st 2025, 5:43:23 pm
---
# Вопрос (RU)
> Что такое структурированная параллельность в Kotlin? Объясните иерархию родитель-потомок корутин, распространение отмены, распространение исключений и разницу между coroutineScope, supervisorScope и withContext.

---

# Question (EN)
> What is structured concurrency in Kotlin? Explain parent-child coroutine hierarchy, cancellation propagation, exception propagation, and differences between coroutineScope, supervisorScope, and withContext.

## Ответ (RU)

**Структурированная параллельность** гарантирует, что корутины следуют чёткой иерархии родитель-потомок, обеспечивая автоматическое распространение отмены, обработку исключений и очистку ресурсов.

### Основные Принципы

1. **Иерархия**: Корутины формируют отношения родитель-потомок
2. **Время жизни**: Время жизни потомка привязано к родителю
3. **Отмена**: Распространяется от родителя к потомкам
4. **Исключения**: Исключения потомка распространяются к родителю
5. **Завершение**: Родитель ждёт всех потомков

### coroutineScope

Создаёт новый скоуп, который ждёт всех потомков:

```kotlin
suspend fun processData() = coroutineScope {
    val deferred1 = async { loadData1() }
    val deferred2 = async { loadData2() }
    
    deferred1.await() + deferred2.await()
    // coroutineScope ждёт завершения обоих
}
```

### supervisorScope

Создаёт скоуп где сбои не отменяют соседей:

```kotlin
suspend fun withSupervisor() = supervisorScope {
    launch {
        throw Exception("Сбой задачи 1")
    }
    
    launch {
        println("Задача 2 выполняется") // Всё равно выполнится!
    }
}
```

### withContext

Переключает контекст без создания нового скоупа:

```kotlin
suspend fun loadUser(id: Int): User = withContext(Dispatchers.IO) {
    // Переключается на IO диспетчер
    database.getUser(id)
}
```

### Таблица Сравнения

| Функция | coroutineScope | supervisorScope | withContext |
|---------|---------------|-----------------|-------------|
| Создаёт новый Job | Да | Да (SupervisorJob) | Нет |
| Распространение исключений | К родителю | Останавливается | К родителю |
| Ждёт потомков | Да | Да | Нет потомков |
| Меняет диспетчер | Нет | Нет | Да (опционально) |

---

## Answer (EN)

**Structured concurrency** ensures that coroutines follow a clear parent-child hierarchy, providing automatic cancellation propagation, exception handling, and resource cleanup.

### Core Principles

1. **Hierarchy**: Coroutines form parent-child relationships
2. **Lifetime**: Child lifetime bound to parent
3. **Cancellation**: Propagates from parent to children
4. **Exceptions**: Child exceptions propagate to parent
5. **Completion**: Parent waits for all children

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

Creates a new scope that waits for all children:

```kotlin
suspend fun processData() = coroutineScope {
    val deferred1 = async { loadData1() }
    val deferred2 = async { loadData2() }
    
    val result1 = deferred1.await()
    val result2 = deferred2.await()
    
    result1 + result2
    // coroutineScope waits for both to complete
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
                println("This won't execute")
            }
        }
    } catch (e: Exception) {
        println("Caught: ${e.message}")
        // Caught: Child failed
    }
}

// When ANY child fails:
// 1. All siblings are cancelled
// 2. Exception propagates to parent
// 3. Parent scope cancels and throws exception
```

### supervisorScope

Creates a scope where failures don't cancel siblings:

```kotlin
suspend fun withSupervisor() = supervisorScope {
    val job1 = launch {
        delay(100)
        throw Exception("Job 1 failed")
    }
    
    val job2 = launch {
        delay(500)
        println("Job 2 completed")  // Still executes!
    }
    
    // Parent doesn't fail, continues execution
}

// Job 1 fails, but Job 2 continues
// supervisorScope doesn't throw exception
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
        
        // All syncs run independently
        // One failure doesn't affect others
    }
    
    private suspend fun syncUsers() { delay(1000) }
    private suspend fun syncPosts() { delay(1000) }
    private suspend fun syncComments() { delay(1000) }
    private fun logError(msg: String, e: Exception) = println("$msg: $e")
}
```

### withContext

Switches context without creating new scope:

```kotlin
suspend fun loadUser(id: Int): User = withContext(Dispatchers.IO) {
    // Switches to IO dispatcher
    // Returns immediately after block completes
    database.getUser(id)
}

// vs coroutineScope
suspend fun loadUserScope(id: Int): User = coroutineScope {
    // Creates new scope but stays on same dispatcher
    database.getUser(id)
}
```

**Key differences:**

```kotlin
// withContext: Changes dispatcher, inherits Job
suspend fun example1() = withContext(Dispatchers.IO) {
    // Runs on IO dispatcher
    // Uses parent's Job
    // Returns immediately
}

// coroutineScope: Same dispatcher, new Job
suspend fun example2() = coroutineScope {
    // Runs on current dispatcher
    // Creates new Job
    // Waits for all children
}

// supervisorScope: Same dispatcher, SupervisorJob
suspend fun example3() = supervisorScope {
    // Runs on current dispatcher
    // Creates SupervisorJob
    // Failures don't cancel siblings
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

**Strategy 2: SupervisorJob**

```kotlin
supervisorScope {
    launch {
        riskyOperation() // Can fail without affecting siblings
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
    // Caught by handler, doesn't crash
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
        
        UserProfile(user, posts, friends)
        // If ANY request fails, all are cancelled
        // Exception propagates to caller
    }
    
    suspend fun loadProfileResilient(userId: Int): UserProfile = supervisorScope {
        val userDeferred = async {
            try {
                userApi.getUser(userId)
            } catch (e: Exception) {
                null // Continue even if fails
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
        // Resilient: Each failure handled independently
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
|---------|---------------|-----------------|-------------|
| Creates new Job | Yes | Yes (SupervisorJob) | No |
| Exception propagation | To parent | Stops at scope | To parent |
| Waits for children | Yes | Yes | No children |
| Changes dispatcher | No | No | Yes (optional) |
| Use case | Related tasks | Independent tasks | Switch context |

### Advanced Patterns

**Pattern 1: Timeout with cleanup**

```kotlin
suspend fun withTimeout() = coroutineScope {
    val job = launch {
        try {
            longRunningOperation()
        } finally {
            cleanup() // Always runs
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
        // Guaranteed to run even if cancelled
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
// Don't suppress cancellation
try {
    work()
} catch (e: Exception) {
    // Swallows CancellationException!
}

// Don't use GlobalScope
GlobalScope.launch {
    // No structured concurrency!
}

// Don't block coroutine threads
launch {
    Thread.sleep(1000) // Bad!
    // Use delay(1000)
}

// Don't forget exception handling
coroutineScope {
    launch {
        riskyOperation() // Can cancel all siblings!
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
    assertThrows<Exception> {
        coroutineScope {
            launch {
                throw Exception("Failed")
            }
        }
    }
}
```

---

## References

- [Coroutine Context and Dispatchers](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)
- [Structured Concurrency](https://kotlinlang.org/docs/coroutines-basics.html#structured-concurrency)
- [Coroutine Exceptions](https://kotlinlang.org/docs/exception-handling.html)

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Related Questions

- [[q-actor-pattern--kotlin--hard]]
- [[q-advanced-coroutine-patterns--kotlin--hard]]
- [[q-coroutine-dispatchers--kotlin--medium]]
- [[q-flow-basics--kotlin--easy]]

## MOC Links

- [[moc-kotlin]]
