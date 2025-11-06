---
id: kotlin-239
title: "What are CoroutineContext elements and how do they combine? / Элементы CoroutineContext"
aliases: [CoroutineContext Elements, Элементы CoroutineContext]
topic: kotlin
subtopics: [context, coroutines]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
created: "2025-10-12"
updated: "2025-11-06"
tags: ["context", "coroutines", "difficulty/hard", "dispatcher", "job", "kotlin"]
description: "Comprehensive guide to CoroutineContext elements and how they combine in Kotlin coroutines"
moc: moc-kotlin
related: [c-coroutines, c-structured-concurrency, q-coroutine-job-lifecycle--kotlin--medium]
---

# Вопрос (RU)

> Что такое элементы CoroutineContext и как они комбинируются? Объясните Job, CoroutineDispatcher, CoroutineName, CoroutineExceptionHandler и как работает оператор +.

# Question (EN)

> What are CoroutineContext elements and how do they combine? Explain Job, CoroutineDispatcher, CoroutineName, CoroutineExceptionHandler, and how the + operator works.

---

## Answer (EN)

**CoroutineContext** is a persistent indexed set of `Element` instances that provide configuration and behavior for coroutines. It's a fundamental concept in Kotlin coroutines that controls execution context, job hierarchy, error handling, and debugging.

### Core Concept

`CoroutineContext` is like a map where:
- **Keys** are singleton `CoroutineContext.Key` objects
- **Values** are `CoroutineContext.Element` instances
- Each element has a unique key type
- Elements combine using the `+` operator

```kotlin
interface CoroutineContext {
    operator fun <E : Element> get(key: Key<E>): E?
    operator fun plus(context: CoroutineContext): CoroutineContext
    fun minusKey(key: Key<*>): CoroutineContext

    interface Element : CoroutineContext {
        val key: Key<*>
    }

    interface Key<E : Element>
}
```

---

### The Four Standard Elements

#### 1. Job - Lifecycle and Cancellation

**Purpose**: Manages coroutine lifecycle, parent-child relationships, and cancellation.

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    // Job is automatically created for every coroutine
    val job = launch {
        println("Job: $coroutineContext[Job]")
    }

    println("Parent job: $coroutineContext[Job]")
    println("Child job: $job")

    job.join()
}
// Output:
// Parent job: BlockingCoroutine{Active}@...
// Child job: StandaloneCoroutine{Active}@...
// Job: StandaloneCoroutine{Active}@...
```

**Key Characteristics**:
- Every coroutine has a Job
- Child jobs inherit parent's Job
- Cancelling parent cancels all children
- Job completion waits for all children

```kotlin
fun main() = runBlocking {
    val parentJob = launch {
        val child1 = launch {
            repeat(1000) { i ->
                println("Child 1: $i")
                delay(100)
            }
        }

        val child2 = launch {
            repeat(1000) { i ->
                println("Child 2: $i")
                delay(100)
            }
        }

        delay(500)
        println("Parent cancelling")
    }

    parentJob.join()
    println("All done")
}
// Parent cancellation stops both children
```

**SupervisorJob**: Independent child failure

```kotlin
fun main() = runBlocking {
    val supervisor = SupervisorJob()

    with(CoroutineScope(coroutineContext + supervisor)) {
        val child1 = launch {
            delay(100)
            throw Exception("Child 1 failed")
        }

        val child2 = launch {
            repeat(5) { i ->
                delay(200)
                println("Child 2: $i")
            }
        }

        joinAll(child1, child2)
    }
}
// Child 2 continues even when Child 1 fails
```

---

#### 2. CoroutineDispatcher - Execution Thread

**Purpose**: Determines which thread(s) the coroutine uses for execution.

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    // Dispatchers.Default - CPU-intensive work
    launch(Dispatchers.Default) {
        println("Default: ${Thread.currentThread().name}")
        // Heavy computation
    }

    // Dispatchers.IO - I/O operations
    launch(Dispatchers.IO) {
        println("IO: ${Thread.currentThread().name}")
        // Network, file I/O
    }

    // Dispatchers.Main - UI thread (Android/Desktop)
    // launch(Dispatchers.Main) { /* UI updates */ }

    // Dispatchers.Unconfined - Not confined to any thread
    launch(Dispatchers.Unconfined) {
        println("Unconfined before: ${Thread.currentThread().name}")
        delay(100)
        println("Unconfined after: ${Thread.currentThread().name}")
    }

    delay(500)
}
```

**Custom Dispatchers**:

```kotlin
import java.util.concurrent.Executors

val customDispatcher = Executors.newFixedThreadPool(4).asCoroutineDispatcher()

fun main() = runBlocking {
    launch(customDispatcher) {
        println("Custom: ${Thread.currentThread().name}")
    }

    delay(100)
    customDispatcher.close() // Must close custom dispatchers
}
```

**limitedParallelism** (Kotlin 1.6+):

```kotlin
fun main() = runBlocking {
    // Limit parallelism for I/O operations
    val limitedIO = Dispatchers.IO.limitedParallelism(2)

    repeat(10) { i ->
        launch(limitedIO) {
            println("Task $i on ${Thread.currentThread().name}")
            delay(1000)
        }
    }

    delay(2000)
}
// Only 2 tasks run in parallel despite 10 launched
```

---

#### 3. CoroutineName - Debugging

**Purpose**: Provides meaningful names for debugging and logging.

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    launch(CoroutineName("DataLoader")) {
        println("Running: ${coroutineContext[CoroutineName]}")
        launch(CoroutineName("DatabaseQuery")) {
            println("Running: ${coroutineContext[CoroutineName]}")
        }
    }

    delay(100)
}
// Output:
// Running: CoroutineName(DataLoader)
// Running: CoroutineName(DatabaseQuery)
```

**Debugging with names**:

```kotlin
fun fetchUserData() = CoroutineScope(
    Dispatchers.IO + CoroutineName("UserDataFetcher")
).launch {
    try {
        // Simulate network call
        delay(1000)
        println("Data fetched by ${coroutineContext[CoroutineName]}")
    } catch (e: Exception) {
        println("Error in ${coroutineContext[CoroutineName]}: $e")
    }
}
```

---

#### 4. CoroutineExceptionHandler - Error Handling

**Purpose**: Handles uncaught exceptions in coroutines.

```kotlin
import kotlinx.coroutines.*

val handler = CoroutineExceptionHandler { context, exception ->
    println("Caught $exception in ${context[CoroutineName]}")
}

fun main() = runBlocking {
    val job = GlobalScope.launch(handler + CoroutineName("ErrorProne")) {
        throw RuntimeException("Oops!")
    }

    job.join()
}
// Output: Caught java.lang.RuntimeException: Oops! in CoroutineName(ErrorProne)
```

**Important Rules**:

1. **Only works with launch**, not async (async stores exception in Deferred)

```kotlin
fun main() = runBlocking {
    val handler = CoroutineExceptionHandler { _, e ->
        println("Caught: $e")
    }

    // ✅ Works with launch
    launch(handler) {
        throw Exception("Launch exception")
    }

    // ❌ Doesn't work with async
    val deferred = async(handler) {
        throw Exception("Async exception")
    }

    try {
        deferred.await() // Exception thrown here
    } catch (e: Exception) {
        println("Caught from await: $e")
    }
}
```

2. **Must be installed in root coroutine**

```kotlin
fun main() = runBlocking {
    val handler = CoroutineExceptionHandler { _, e ->
        println("Handler caught: $e")
    }

    // ❌ Won't work - not in root coroutine
    launch {
        launch(handler) {
            throw Exception("Not caught by handler")
        }
    }

    // ✅ Works - in root coroutine
    launch(handler) {
        throw Exception("Caught by handler")
    }

    delay(100)
}
```

3. **SupervisorJob affects exception propagation**

```kotlin
fun main() = runBlocking {
    val handler = CoroutineExceptionHandler { _, e ->
        println("Caught: $e")
    }

    val supervisor = SupervisorJob()

    with(CoroutineScope(coroutineContext + supervisor + handler)) {
        launch {
            throw Exception("Child 1 failed")
        }

        launch {
            delay(200)
            println("Child 2 still running")
        }
    }

    delay(300)
}
// Child 2 continues because SupervisorJob isolates failures
```

---

### How Elements Combine: The + Operator

**Fundamental Rule**: Right side wins for duplicate keys.

```kotlin
import kotlinx.coroutines.*

fun main() = runBlocking {
    val context1 = Dispatchers.Default + CoroutineName("First")
    val context2 = Dispatchers.IO + CoroutineName("Second")

    val combined = context1 + context2

    println("Dispatcher: ${combined[CoroutineDispatcher]}")
    println("Name: ${combined[CoroutineName]}")
}
// Output:
// Dispatcher: Dispatchers.IO
// Name: CoroutineName(Second)
```

**Combining Multiple Elements**:

```kotlin
val handler = CoroutineExceptionHandler { _, e ->
    println("Error: $e")
}

val fullContext =
    Dispatchers.IO +
    CoroutineName("DataProcessor") +
    handler +
    Job()

fun main() = runBlocking {
    launch(fullContext) {
        println("Context has:")
        println("  Dispatcher: ${coroutineContext[CoroutineDispatcher]}")
        println("  Name: ${coroutineContext[CoroutineName]}")
        println("  Job: ${coroutineContext[Job]}")
        println("  Handler: ${coroutineContext[CoroutineExceptionHandler]}")
    }

    delay(100)
}
```

**Order Matters**:

```kotlin
fun main() = runBlocking {
    // Last dispatcher wins
    val context1 = Dispatchers.Default + Dispatchers.IO
    println(context1[CoroutineDispatcher]) // Dispatchers.IO

    // Last name wins
    val context2 =
        CoroutineName("First") +
        CoroutineName("Second") +
        CoroutineName("Third")
    println(context2[CoroutineName]) // CoroutineName(Third)
}
```

---

### Context Inheritance

**Child coroutines inherit parent context**:

```kotlin
fun main() = runBlocking {
    launch(Dispatchers.Default + CoroutineName("Parent")) {
        println("Parent:")
        println("  Thread: ${Thread.currentThread().name}")
        println("  Name: ${coroutineContext[CoroutineName]}")

        // Child inherits dispatcher and name
        launch {
            println("Child (inherited):")
            println("  Thread: ${Thread.currentThread().name}")
            println("  Name: ${coroutineContext[CoroutineName]}")
        }

        // Child can override
        launch(Dispatchers.IO + CoroutineName("Child")) {
            println("Child (overridden):")
            println("  Thread: ${Thread.currentThread().name}")
            println("  Name: ${coroutineContext[CoroutineName]}")
        }

        delay(100)
    }

    delay(200)
}
```

**Job Inheritance is Special**:

```kotlin
fun main() = runBlocking {
    val parentJob = Job()

    launch(parentJob) {
        println("Child job: ${coroutineContext[Job]}")
        println("Parent job: ${coroutineContext[Job]?.parent}")
        println("Are they same? ${coroutineContext[Job]?.parent == parentJob}")
    }

    delay(100)
}
// Child gets NEW Job with parent reference to parentJob
```

---

### Practical Patterns

#### Pattern 1: Repository with Context

```kotlin
class UserRepository(
    private val dispatcher: CoroutineDispatcher = Dispatchers.IO
) {
    private val repositoryContext =
        dispatcher +
        CoroutineName("UserRepository") +
        SupervisorJob()

    private val scope = CoroutineScope(repositoryContext)

    suspend fun fetchUser(id: String): User = withContext(dispatcher) {
        // Network call
        delay(1000)
        User(id, "User $id")
    }

    fun observeUser(id: String): Flow<User> = flow {
        while (currentCoroutineContext().isActive) {
            emit(fetchUser(id))
            delay(5000)
        }
    }.flowOn(dispatcher)

    fun cleanup() {
        scope.cancel()
    }
}
```

#### Pattern 2: Configurable Worker

```kotlin
class DataProcessor(
    dispatcher: CoroutineDispatcher = Dispatchers.Default,
    name: String = "DataProcessor"
) {
    private val handler = CoroutineExceptionHandler { _, e ->
        println("[$name] Error: $e")
    }

    private val context =
        dispatcher +
        CoroutineName(name) +
        handler +
        SupervisorJob()

    private val scope = CoroutineScope(context)

    fun processData(data: List<Int>) = scope.launch {
        println("Processing on ${Thread.currentThread().name}")

        data.chunked(10).forEach { chunk ->
            launch {
                // Process chunk
                chunk.forEach { item ->
                    if (item < 0) throw IllegalArgumentException("Negative: $item")
                    println("Processed: $item")
                }
            }
        }
    }
}

fun main() = runBlocking {
    val processor = DataProcessor(
        dispatcher = Dispatchers.Default.limitedParallelism(2),
        name = "NumberProcessor"
    )

    processor.processData(List(100) { it })
    delay(1000)
}
```

#### Pattern 3: Testing with TestDispatcher

```kotlin
import kotlinx.coroutines.test.*
import org.junit.Test

class RepositoryTest {
    @Test
    fun testDataFetch() = runTest {
        val testDispatcher = StandardTestDispatcher(testScheduler)
        val repo = UserRepository(testDispatcher)

        val job = launch {
            val user = repo.fetchUser("123")
            assertEquals("User 123", user.name)
        }

        // Advance virtual time
        advanceUntilIdle()

        job.join()
    }
}
```

---

### Context Propagation Rules

#### Rule 1: Explicit Context Overrides Inherited

```kotlin
fun main() = runBlocking(Dispatchers.Default + CoroutineName("Parent")) {
    // Child inherits Default dispatcher
    launch {
        println("Inherited: ${Thread.currentThread().name}")
    }

    // Child overrides with IO dispatcher
    launch(Dispatchers.IO) {
        println("Overridden: ${Thread.currentThread().name}")
    }

    delay(100)
}
```

#### Rule 2: Job is Always New

```kotlin
fun main() = runBlocking {
    val parentJob = coroutineContext[Job]!!

    launch {
        val childJob = coroutineContext[Job]!!
        println("Same job? ${childJob == parentJob}") // false
        println("Parent? ${childJob.parent == parentJob}") // true
    }

    delay(100)
}
```

#### Rule 3: withContext Temporarily Overrides

```kotlin
suspend fun fetchData() = withContext(Dispatchers.IO) {
    println("Fetching on: ${Thread.currentThread().name}")
    // Temporarily on IO dispatcher
    delay(1000)
    "Data"
}

fun main() = runBlocking(Dispatchers.Default) {
    println("Main on: ${Thread.currentThread().name}")
    val data = fetchData() // Switches to IO
    println("Back to: ${Thread.currentThread().name}") // Back to Default
}
```

---

### Advanced: Custom Context Elements

```kotlin
import kotlinx.coroutines.*
import kotlin.coroutines.*

// Custom element for request tracing
data class RequestId(val id: String) : AbstractCoroutineContextElement(RequestId) {
    companion object Key : CoroutineContext.Key<RequestId>

    override fun toString(): String = "RequestId($id)"
}

// Extension for easy access
val CoroutineContext.requestId: String?
    get() = this[RequestId]?.id

suspend fun processRequest() {
    val reqId = currentCoroutineContext().requestId
    println("Processing request: $reqId")

    withContext(Dispatchers.IO) {
        println("On IO, request: ${coroutineContext.requestId}")
    }
}

fun main() = runBlocking {
    launch(RequestId("REQ-123")) {
        processRequest()
    }

    launch(RequestId("REQ-456")) {
        processRequest()
    }

    delay(100)
}
```

---

### Common Anti-Patterns

#### ❌ Anti-Pattern 1: Ignoring Dispatcher

```kotlin
// Bad: Blocking I/O on Default dispatcher
suspend fun loadUser() = withContext(Dispatchers.Default) {
    // This blocks a Default thread!
    File("user.json").readText()
}

// Good: I/O on IO dispatcher
suspend fun loadUser() = withContext(Dispatchers.IO) {
    File("user.json").readText()
}
```

#### ❌ Anti-Pattern 2: GlobalScope

```kotlin
// Bad: GlobalScope breaks structured concurrency
fun fetchData() {
    GlobalScope.launch {
        // This coroutine lives forever!
    }
}

// Good: Use proper scope
class Repository(private val scope: CoroutineScope) {
    fun fetchData() = scope.launch {
        // Properly managed lifecycle
    }
}
```

#### ❌ Anti-Pattern 3: Ignoring Exception Handler Scope

```kotlin
// Bad: Handler in child coroutine
launch {
    val handler = CoroutineExceptionHandler { _, e ->
        println("Won't be called!")
    }

    launch(handler) {
        throw Exception("Not caught")
    }
}

// Good: Handler in root coroutine
val handler = CoroutineExceptionHandler { _, e ->
    println("Caught: $e")
}

launch(handler) {
    throw Exception("Caught correctly")
}
```

---

### Performance Considerations

#### 1. Context Switching Overhead

```kotlin
// Expensive: Many context switches
suspend fun processItems(items: List<Int>) {
    items.forEach { item ->
        withContext(Dispatchers.IO) { // Switch for each item
            processItem(item)
        }
    }
}

// Better: Switch once
suspend fun processItems(items: List<Int>) = withContext(Dispatchers.IO) {
    items.forEach { item ->
        processItem(item)
    }
}
```

#### 2. Dispatcher Pool Sizing

```kotlin
// Too many threads
val hugDispatcher = Executors.newFixedThreadPool(1000).asCoroutineDispatcher()

// Right-sized for CPU work
val cpuDispatcher = Dispatchers.Default // Runtime.availableProcessors()

// Right-sized for I/O
val ioDispatcher = Dispatchers.IO // max(64, availableProcessors())
```

#### 3. Context Element Allocation

```kotlin
// Creates new context objects frequently
fun process() = runBlocking {
    repeat(1000) {
        launch(CoroutineName("Worker-$it")) { // New CoroutineName each time
            delay(10)
        }
    }
}

// Reuse when possible
fun process() = runBlocking {
    val baseName = CoroutineName("Worker")
    repeat(1000) {
        launch(baseName) { // Reuse same CoroutineName
            delay(10)
        }
    }
}
```

---

### Testing Strategies

#### Strategy 1: Inject Dispatchers

```kotlin
class DataService(
    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO,
    private val defaultDispatcher: CoroutineDispatcher = Dispatchers.Default
) {
    suspend fun processData(): Result = withContext(ioDispatcher) {
        val raw = loadRawData()
        withContext(defaultDispatcher) {
            compute(raw)
        }
    }
}

// Test
@Test
fun testProcessData() = runTest {
    val service = DataService(
        ioDispatcher = StandardTestDispatcher(testScheduler),
        defaultDispatcher = StandardTestDispatcher(testScheduler)
    )

    val result = service.processData()
    assertEquals(expected, result)
}
```

#### Strategy 2: Test Context Propagation

```kotlin
@Test
fun testContextPropagation() = runTest {
    val customElement = RequestId("TEST-123")

    launch(customElement) {
        assertEquals("TEST-123", coroutineContext.requestId)

        withContext(Dispatchers.IO) {
            // Custom element propagates
            assertEquals("TEST-123", coroutineContext.requestId)
        }
    }
}
```

#### Strategy 3: Test Exception Handling

```kotlin
@Test
fun testExceptionHandler() = runTest {
    var caughtException: Throwable? = null

    val handler = CoroutineExceptionHandler { _, e ->
        caughtException = e
    }

    val job = launch(handler) {
        throw TestException()
    }

    job.join()
    assertNotNull(caughtException)
    assertTrue(caughtException is TestException)
}
```

---

## Ответ (RU)

**CoroutineContext** — это постоянный индексированный набор элементов `Element`, которые предоставляют конфигурацию и поведение для корутин. Это фундаментальная концепция в Kotlin корутинах, управляющая контекстом выполнения, иерархией задач, обработкой ошибок и отладкой.

### Основная концепция

`CoroutineContext` работает как карта, где:
- **Ключи** — это singleton-объекты `CoroutineContext.Key`
- **Значения** — это экземпляры `CoroutineContext.Element`
- Каждый элемент имеет уникальный тип ключа
- Элементы комбинируются оператором `+`

```kotlin
interface CoroutineContext {
    operator fun <E : Element> get(key: Key<E>): E?
    operator fun plus(context: CoroutineContext): CoroutineContext
    fun minusKey(key: Key<*>): CoroutineContext

    interface Element : CoroutineContext {
        val key: Key<*>
    }

    interface Key<E : Element>
}
```

---

### Четыре стандартных элемента

#### 1. Job - Жизненный цикл и отмена

**Назначение**: Управляет жизненным циклом корутины, отношениями родитель-потомок и отменой.

**Ключевые характеристики**:
- Каждая корутина имеет Job
- Дочерние Job наследуют родительский Job
- Отмена родителя отменяет всех потомков
- Завершение Job ожидает завершения всех потомков

```kotlin
fun main() = runBlocking {
    val parentJob = launch {
        val child1 = launch {
            repeat(1000) { i ->
                println("Потомок 1: $i")
                delay(100)
            }
        }

        val child2 = launch {
            repeat(1000) { i ->
                println("Потомок 2: $i")
                delay(100)
            }
        }

        delay(500)
        println("Родитель отменяется")
    }

    parentJob.join()
}
```

**SupervisorJob**: Независимость сбоев потомков

```kotlin
fun main() = runBlocking {
    val supervisor = SupervisorJob()

    with(CoroutineScope(coroutineContext + supervisor)) {
        val child1 = launch {
            delay(100)
            throw Exception("Потомок 1 упал")
        }

        val child2 = launch {
            repeat(5) { i ->
                delay(200)
                println("Потомок 2: $i")
            }
        }

        joinAll(child1, child2)
    }
}
// Потомок 2 продолжает работу даже когда Потомок 1 падает
```

---

#### 2. CoroutineDispatcher - Поток выполнения

**Назначение**: Определяет, на каком потоке(ах) выполняется корутина.

```kotlin
fun main() = runBlocking {
    // Dispatchers.Default - вычислительные задачи
    launch(Dispatchers.Default) {
        println("Default: ${Thread.currentThread().name}")
    }

    // Dispatchers.IO - операции ввода-вывода
    launch(Dispatchers.IO) {
        println("IO: ${Thread.currentThread().name}")
    }

    // Dispatchers.Unconfined - не привязан к потоку
    launch(Dispatchers.Unconfined) {
        println("Unconfined до: ${Thread.currentThread().name}")
        delay(100)
        println("Unconfined после: ${Thread.currentThread().name}")
    }

    delay(500)
}
```

**limitedParallelism** (Kotlin 1.6+):

```kotlin
fun main() = runBlocking {
    val limitedIO = Dispatchers.IO.limitedParallelism(2)

    repeat(10) { i ->
        launch(limitedIO) {
            println("Задача $i на ${Thread.currentThread().name}")
            delay(1000)
        }
    }

    delay(2000)
}
// Только 2 задачи выполняются параллельно из 10 запущенных
```

---

#### 3. CoroutineName - Отладка

**Назначение**: Предоставляет осмысленные имена для отладки и логирования.

```kotlin
fun main() = runBlocking {
    launch(CoroutineName("ЗагрузчикДанных")) {
        println("Выполняется: ${coroutineContext[CoroutineName]}")
        launch(CoroutineName("ЗапросБД")) {
            println("Выполняется: ${coroutineContext[CoroutineName]}")
        }
    }

    delay(100)
}
```

---

#### 4. CoroutineExceptionHandler - Обработка ошибок

**Назначение**: Обрабатывает неперехваченные исключения в корутинах.

```kotlin
val handler = CoroutineExceptionHandler { context, exception ->
    println("Перехвачено $exception в ${context[CoroutineName]}")
}

fun main() = runBlocking {
    val job = GlobalScope.launch(handler + CoroutineName("СОшибкой")) {
        throw RuntimeException("Упс!")
    }

    job.join()
}
```

**Важные правила**:

1. **Работает только с launch**, не с async

```kotlin
fun main() = runBlocking {
    val handler = CoroutineExceptionHandler { _, e ->
        println("Перехвачено: $e")
    }

    // ✅ Работает с launch
    launch(handler) {
        throw Exception("Исключение в launch")
    }

    // ❌ Не работает с async
    val deferred = async(handler) {
        throw Exception("Исключение в async")
    }

    try {
        deferred.await() // Исключение выбрасывается здесь
    } catch (e: Exception) {
        println("Перехвачено из await: $e")
    }
}
```

2. **Должен быть установлен в корневой корутине**

3. **SupervisorJob влияет на распространение исключений**

---

### Как комбинируются элементы: оператор +

**Фундаментальное правило**: Правая сторона выигрывает для дублирующих ключей.

```kotlin
fun main() = runBlocking {
    val context1 = Dispatchers.Default + CoroutineName("Первый")
    val context2 = Dispatchers.IO + CoroutineName("Второй")

    val combined = context1 + context2

    println("Диспетчер: ${combined[CoroutineDispatcher]}")
    println("Имя: ${combined[CoroutineName]}")
}
// Вывод:
// Диспетчер: Dispatchers.IO
// Имя: CoroutineName(Второй)
```

**Комбинирование нескольких элементов**:

```kotlin
val handler = CoroutineExceptionHandler { _, e ->
    println("Ошибка: $e")
}

val fullContext =
    Dispatchers.IO +
    CoroutineName("ОбработчикДанных") +
    handler +
    Job()
```

**Порядок имеет значение**:

```kotlin
fun main() = runBlocking {
    // Последний диспетчер побеждает
    val context1 = Dispatchers.Default + Dispatchers.IO
    println(context1[CoroutineDispatcher]) // Dispatchers.IO

    // Последнее имя побеждает
    val context2 =
        CoroutineName("Первый") +
        CoroutineName("Второй") +
        CoroutineName("Третий")
    println(context2[CoroutineName]) // CoroutineName(Третий)
}
```

---

### Наследование контекста

**Дочерние корутины наследуют родительский контекст**:

```kotlin
fun main() = runBlocking {
    launch(Dispatchers.Default + CoroutineName("Родитель")) {
        println("Родитель:")
        println("  Поток: ${Thread.currentThread().name}")
        println("  Имя: ${coroutineContext[CoroutineName]}")

        // Потомок наследует диспетчер и имя
        launch {
            println("Потомок (унаследовано):")
            println("  Поток: ${Thread.currentThread().name}")
            println("  Имя: ${coroutineContext[CoroutineName]}")
        }

        // Потомок может переопределить
        launch(Dispatchers.IO + CoroutineName("Потомок")) {
            println("Потомок (переопределено):")
            println("  Поток: ${Thread.currentThread().name}")
            println("  Имя: ${coroutineContext[CoroutineName]}")
        }

        delay(100)
    }

    delay(200)
}
```

**Наследование Job особенное**:

```kotlin
fun main() = runBlocking {
    val parentJob = Job()

    launch(parentJob) {
        println("Дочерний job: ${coroutineContext[Job]}")
        println("Родительский job: ${coroutineContext[Job]?.parent}")
        println("Они одинаковые? ${coroutineContext[Job]?.parent == parentJob}")
    }

    delay(100)
}
// Потомок получает НОВЫЙ Job со ссылкой на parentJob как родителя
```

---

### Практические паттерны

#### Паттерн 1: Репозиторий с контекстом

```kotlin
class UserRepository(
    private val dispatcher: CoroutineDispatcher = Dispatchers.IO
) {
    private val repositoryContext =
        dispatcher +
        CoroutineName("UserRepository") +
        SupervisorJob()

    private val scope = CoroutineScope(repositoryContext)

    suspend fun fetchUser(id: String): User = withContext(dispatcher) {
        delay(1000)
        User(id, "Пользователь $id")
    }

    fun cleanup() {
        scope.cancel()
    }
}
```

#### Паттерн 2: Настраиваемый обработчик

```kotlin
class DataProcessor(
    dispatcher: CoroutineDispatcher = Dispatchers.Default,
    name: String = "ОбработчикДанных"
) {
    private val handler = CoroutineExceptionHandler { _, e ->
        println("[$name] Ошибка: $e")
    }

    private val context =
        dispatcher +
        CoroutineName(name) +
        handler +
        SupervisorJob()

    private val scope = CoroutineScope(context)
}
```

---

### Правила распространения контекста

#### Правило 1: Явный контекст переопределяет унаследованный

```kotlin
fun main() = runBlocking(Dispatchers.Default + CoroutineName("Родитель")) {
    // Потомок наследует Default диспетчер
    launch {
        println("Унаследовано: ${Thread.currentThread().name}")
    }

    // Потомок переопределяет на IO диспетчер
    launch(Dispatchers.IO) {
        println("Переопределено: ${Thread.currentThread().name}")
    }

    delay(100)
}
```

#### Правило 2: Job всегда новый

#### Правило 3: withContext временно переопределяет

```kotlin
suspend fun fetchData() = withContext(Dispatchers.IO) {
    println("Загрузка на: ${Thread.currentThread().name}")
    delay(1000)
    "Данные"
}

fun main() = runBlocking(Dispatchers.Default) {
    println("Main на: ${Thread.currentThread().name}")
    val data = fetchData() // Переключается на IO
    println("Обратно на: ${Thread.currentThread().name}") // Обратно на Default
}
```

---

### Распространенные анти-паттерны

#### ❌ Анти-паттерн 1: Игнорирование диспетчера

```kotlin
// Плохо: Блокирующий I/O на Default диспетчере
suspend fun loadUser() = withContext(Dispatchers.Default) {
    File("user.json").readText() // Блокирует поток!
}

// Хорошо: I/O на IO диспетчере
suspend fun loadUser() = withContext(Dispatchers.IO) {
    File("user.json").readText()
}
```

#### ❌ Анти-паттерн 2: GlobalScope

```kotlin
// Плохо: GlobalScope нарушает структурированный конкаренси
fun fetchData() {
    GlobalScope.launch {
        // Эта корутина живет вечно!
    }
}

// Хорошо: Используйте правильный scope
class Repository(private val scope: CoroutineScope) {
    fun fetchData() = scope.launch {
        // Правильно управляемый жизненный цикл
    }
}
```

---

### Соображения производительности

#### 1. Накладные расходы переключения контекста

```kotlin
// Дорого: Много переключений контекста
suspend fun processItems(items: List<Int>) {
    items.forEach { item ->
        withContext(Dispatchers.IO) { // Переключение для каждого элемента
            processItem(item)
        }
    }
}

// Лучше: Переключиться один раз
suspend fun processItems(items: List<Int>) = withContext(Dispatchers.IO) {
    items.forEach { item ->
        processItem(item)
    }
}
```

---

## Follow-ups

1. How does CoroutineContext.Element.Key work internally to ensure type safety?
2. What happens when you combine two Jobs using the + operator?
3. How do ThreadLocal values interact with CoroutineContext?
4. What is the performance difference between Dispatchers.Default and Dispatchers.IO?
5. How would you implement a custom CoroutineContext.Element for distributed tracing?
6. What are the thread safety guarantees of CoroutineContext operations?
7. How does context propagation work with Flow operators like flowOn()?

## References

- [Kotlin Coroutines Official Documentation](https://kotlinlang.org/docs/coroutines-guide.html)
- [CoroutineContext API Reference](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-coroutine-context/)
- [Roman Elizarov - Structured Concurrency](https://medium.com/@elizarov/structured-concurrency-722d765aa952)
- [Kotlin Dispatchers Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-dispatchers/)
- [Exception Handling in Coroutines](https://kotlinlang.org/docs/exception-handling.html)

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-job-object--programming-languages--medium]]
- [[q-coroutine-job-lifecycle--kotlin--medium]]
- Basic coroutine concepts

### Related (Same Level)
- [[q-coroutine-context-explained--kotlin--medium]]
- [[q-structured-concurrency--kotlin--hard]]
- [[q-coroutine-supervisorjob-use-cases--kotlin--medium]]

### Advanced (Harder)
- [[q-flow-context-preservation--kotlin--hard]]
- [[q-custom-coroutine-builders--kotlin--hard]]
- Advanced context propagation patterns
