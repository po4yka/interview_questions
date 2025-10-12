---
id: "20251012-150004"
title: "Comparison of all coroutine builders: launch, async, runBlocking, withContext, coroutineScope, supervisorScope"
description: "Comprehensive comparison of Kotlin coroutine builders covering return types, blocking vs suspending behavior, use cases, and performance implications"
tags: ["kotlin", "coroutines", "builders", "launch", "async", "runblocking", "difficulty/medium"]
topic: "kotlin"
subtopics: ["coroutines", "builders", "launch", "async", "runblocking"]
moc: "moc-kotlin"
status: "draft"
date_created: "2025-10-12"
date_updated: "2025-10-12"
---

# Comparison of all coroutine builders: launch, async, runBlocking, withContext, coroutineScope, supervisorScope

## English

### Problem Statement

Kotlin provides several coroutine builders (launch, async, runBlocking, withContext, coroutineScope, supervisorScope), each with different characteristics and use cases. Understanding the differences in return types, blocking behavior, exception handling, and appropriate usage scenarios is crucial for writing effective coroutine code.

### Solution

Let's comprehensively compare all coroutine builders across multiple dimensions.

#### Quick Reference Table

| Builder | Returns | Suspending | Blocking | Exception Handling | Use Case |
|---------|---------|------------|----------|-------------------|----------|
| `launch` | `Job` | No | No | Propagates to parent | Fire-and-forget operations |
| `async` | `Deferred<T>` | No | No | Exception on await() | Concurrent computations with results |
| `runBlocking` | `T` | No | Yes | Throws exception | Bridging blocking/suspending code |
| `withContext` | `T` | Yes | No | Throws exception | Switching dispatcher, sequential operations |
| `coroutineScope` | `T` | Yes | No | Throws exception | Creating child scope, structured concurrency |
| `supervisorScope` | `T` | Yes | No | Throws if scope fails | Independent child operations |

#### launch - Fire and Forget

```kotlin
import kotlinx.coroutines.*

fun launchExamples() = runBlocking {
    println("=== launch ===")

    // Returns Job immediately
    val job: Job = launch {
        delay(1000)
        println("launch completed")
    }

    println("launch returned immediately")

    // Does not suspend parent automatically
    // Must explicitly join if waiting is needed
    job.join()

    // Use case 1: Fire-and-forget operations
    launch {
        updateAnalytics()
    }

    launch {
        logEvent()
    }

    // Use case 2: Parallel independent operations
    val job1 = launch { downloadFile1() }
    val job2 = launch { downloadFile2() }
    val job3 = launch { downloadFile3() }

    joinAll(job1, job2, job3)

    // Use case 3: Background work with lifecycle
    val backgroundJob = launch {
        while (isActive) {
            doPeriodicWork()
            delay(1000)
        }
    }

    delay(5000)
    backgroundJob.cancel()
}

suspend fun updateAnalytics() { delay(100) }
suspend fun logEvent() { delay(100) }
suspend fun downloadFile1() { delay(500) }
suspend fun downloadFile2() { delay(500) }
suspend fun downloadFile3() { delay(500) }
suspend fun doPeriodicWork() { println("Working...") }
```

#### async - Concurrent Computations

```kotlin
import kotlinx.coroutines.*

fun asyncExamples() = runBlocking {
    println("=== async ===")

    // Returns Deferred<T> immediately
    val deferred: Deferred<String> = async {
        delay(1000)
        "async result"
    }

    println("async returned immediately")

    // Suspends when calling await()
    val result = deferred.await()
    println("Result: $result")

    // Use case 1: Parallel computations with results
    val time1 = measureTimeMillis {
        val result1 = async { computeValue1() }
        val result2 = async { computeValue2() }
        val result3 = async { computeValue3() }

        val sum = result1.await() + result2.await() + result3.await()
        println("Sum: $sum")
    }
    println("Parallel async: $time1 ms")

    // Use case 2: Multiple independent API calls
    val users = async { fetchUsers() }
    val posts = async { fetchPosts() }
    val comments = async { fetchComments() }

    val allData = Triple(
        users.await(),
        posts.await(),
        comments.await()
    )

    // Use case 3: Race condition (first to complete)
    val fastest = select<String> {
        async { slowOperation() }.onAwait { "Slow: $it" }
        async { fastOperation() }.onAwait { "Fast: $it" }
    }
    println("Fastest: $fastest")
}

suspend fun computeValue1(): Int {
    delay(500)
    return 10
}

suspend fun computeValue2(): Int {
    delay(500)
    return 20
}

suspend fun computeValue3(): Int {
    delay(500)
    return 30
}

suspend fun fetchUsers(): List<String> {
    delay(300)
    return listOf("User1", "User2")
}

suspend fun fetchPosts(): List<String> {
    delay(400)
    return listOf("Post1", "Post2")
}

suspend fun fetchComments(): List<String> {
    delay(200)
    return listOf("Comment1", "Comment2")
}

suspend fun slowOperation(): String {
    delay(2000)
    return "slow"
}

suspend fun fastOperation(): String {
    delay(500)
    return "fast"
}
```

#### runBlocking - Blocking Bridge

```kotlin
import kotlinx.coroutines.*

fun runBlockingExamples() {
    println("=== runBlocking ===")

    // Blocks the current thread
    val result = runBlocking {
        delay(1000)
        "runBlocking result"
    }
    println("Result: $result")

    // Use case 1: main function
    fun main() = runBlocking {
        launch {
            delay(1000)
            println("World!")
        }
        println("Hello,")
    }

    // Use case 2: Unit tests
    @Test
    fun testCoroutine() = runBlocking {
        val result = async {
            delay(100)
            42
        }
        assertEquals(42, result.await())
    }

    // Use case 3: Bridging blocking and suspending code
    fun blockingFunction(): String = runBlocking {
        suspendingFunction()
    }

    // AVOID in production: Blocks thread
    // Bad example
    fun badExample() {
        runBlocking {
            // This blocks the calling thread!
            delay(10000)
        }
    }

    // Use case 4: Simple scripts
    fun simpleScript() = runBlocking {
        val data = fetchData()
        processData(data)
        saveData(data)
    }
}

suspend fun suspendingFunction(): String {
    delay(100)
    return "result"
}

suspend fun fetchData(): String {
    delay(100)
    return "data"
}

suspend fun processData(data: String) {
    delay(100)
}

suspend fun saveData(data: String) {
    delay(100)
}

annotation class Test
fun assertEquals(expected: Int, actual: Int) {}
```

#### withContext - Dispatcher Switching

```kotlin
import kotlinx.coroutines.*

fun withContextExamples() = runBlocking {
    println("=== withContext ===")

    // Suspends and returns result
    val result: String = withContext(Dispatchers.IO) {
        delay(1000)
        "withContext result"
    }
    println("Result: $result")

    // Use case 1: I/O operations
    suspend fun loadUser(id: String): User = withContext(Dispatchers.IO) {
        // Database or network call
        delay(500)
        User(id, "John")
    }

    // Use case 2: CPU-intensive operations
    suspend fun processImage(image: ByteArray): ByteArray =
        withContext(Dispatchers.Default) {
            // Complex image processing
            delay(1000)
            image
        }

    // Use case 3: Sequential operations with dispatcher switching
    suspend fun loadAndProcess(id: String): ProcessedUser {
        val user = withContext(Dispatchers.IO) {
            loadUserFromDb(id)
        }

        val processed = withContext(Dispatchers.Default) {
            processUser(user)
        }

        withContext(Dispatchers.IO) {
            saveProcessedUser(processed)
        }

        return processed
    }

    // Use case 4: Context modification
    withContext(CoroutineName("MyCoroutine")) {
        println("Name: ${coroutineContext[CoroutineName]}")
    }

    // Better than async + await for single operations
    // Less overhead
    val data1 = withContext(Dispatchers.IO) { fetchData1() }
    val data2 = withContext(Dispatchers.IO) { fetchData2() }
}

data class User(val id: String, val name: String)
data class ProcessedUser(val id: String, val name: String, val processed: Boolean = true)

suspend fun loadUserFromDb(id: String): User {
    delay(300)
    return User(id, "User $id")
}

suspend fun processUser(user: User): ProcessedUser {
    delay(200)
    return ProcessedUser(user.id, user.name.uppercase())
}

suspend fun saveProcessedUser(user: ProcessedUser) {
    delay(100)
}

suspend fun fetchData1(): String {
    delay(300)
    return "data1"
}

suspend fun fetchData2(): String {
    delay(300)
    return "data2"
}
```

#### coroutineScope - Structured Concurrency

```kotlin
import kotlinx.coroutines.*

fun coroutineScopeExamples() = runBlocking {
    println("=== coroutineScope ===")

    // Suspends until all children complete
    val result = coroutineScope {
        val deferred1 = async { computeValue1() }
        val deferred2 = async { computeValue2() }

        deferred1.await() + deferred2.await()
    }
    println("Result: $result")

    // Use case 1: Creating parallel operations within suspend function
    suspend fun loadUserData(userId: String): UserData = coroutineScope {
        val user = async { loadUser(userId) }
        val posts = async { loadPosts(userId) }
        val friends = async { loadFriends(userId) }

        UserData(user.await(), posts.await(), friends.await())
    }

    // Use case 2: Ensuring all children complete
    suspend fun processAllItems(items: List<String>) = coroutineScope {
        items.map { item ->
            async { processItem(item) }
        }.awaitAll()
    }

    // Use case 3: Exception handling
    try {
        coroutineScope {
            launch {
                delay(500)
                throw RuntimeException("Child failed")
            }

            launch {
                delay(1000)
                println("This never executes")
            }
        }
    } catch (e: RuntimeException) {
        println("Caught exception: ${e.message}")
    }

    // Use case 4: Cancellation propagation
    suspend fun cancellableOperation() = coroutineScope {
        launch {
            repeat(5) {
                println("Working $it")
                delay(500)
            }
        }
        // Scope waits for all children
    }

    // Comparison with launch
    launch {
        // Parent doesn't wait
        async { delay(1000) }
        println("Parent continues")
    }

    coroutineScope {
        // Parent waits for child
        async { delay(1000) }
        println("After child completes")
    }

    delay(2000)
}

data class UserData(
    val user: User,
    val posts: List<String>,
    val friends: List<String>
)

suspend fun loadUser(userId: String): User {
    delay(300)
    return User(userId, "User $userId")
}

suspend fun loadPosts(userId: String): List<String> {
    delay(400)
    return listOf("Post1", "Post2")
}

suspend fun loadFriends(userId: String): List<String> {
    delay(200)
    return listOf("Friend1", "Friend2")
}

suspend fun processItem(item: String): String {
    delay(100)
    return "processed: $item"
}
```

#### supervisorScope - Independent Children

```kotlin
import kotlinx.coroutines.*

fun supervisorScopeExamples() = runBlocking {
    println("=== supervisorScope ===")

    // Children fail independently
    supervisorScope {
        launch {
            delay(500)
            println("Child 1 completed")
        }

        launch {
            delay(200)
            throw RuntimeException("Child 2 failed")
        }

        launch {
            delay(1000)
            println("Child 3 completed") // Still executes
        }

        delay(1500)
    }

    // Use case 1: Loading independent dashboard widgets
    suspend fun loadDashboard(): Dashboard = supervisorScope {
        val weather = async {
            try {
                loadWeatherWidget()
            } catch (e: Exception) {
                null // Widget failed, return null
            }
        }

        val news = async {
            try {
                loadNewsWidget()
            } catch (e: Exception) {
                null
            }
        }

        val stocks = async {
            try {
                loadStocksWidget()
            } catch (e: Exception) {
                null
            }
        }

        Dashboard(weather.await(), news.await(), stocks.await())
    }

    // Use case 2: Partial results collection
    suspend fun fetchPartialResults(): List<String> = supervisorScope {
        val jobs = List(5) { index ->
            async {
                if (index == 2) throw Exception("Failed")
                "Result $index"
            }
        }

        jobs.mapNotNull { job ->
            try {
                job.await()
            } catch (e: Exception) {
                null
            }
        }
    }

    // Use case 3: Independent background tasks
    suspend fun startBackgroundTasks() = supervisorScope {
        launch {
            try {
                syncUsers()
            } catch (e: Exception) {
                logError("User sync failed", e)
            }
        }

        launch {
            try {
                syncPosts()
            } catch (e: Exception) {
                logError("Post sync failed", e)
            }
        }

        delay(5000) // Let tasks run
    }
}

data class Dashboard(
    val weather: String?,
    val news: String?,
    val stocks: String?
)

suspend fun loadWeatherWidget(): String {
    delay(300)
    return "Sunny, 72°F"
}

suspend fun loadNewsWidget(): String {
    delay(400)
    throw Exception("News service unavailable")
}

suspend fun loadStocksWidget(): String {
    delay(200)
    return "AAPL: $150"
}

suspend fun syncUsers() {
    delay(500)
    println("Users synced")
}

suspend fun syncPosts() {
    delay(400)
    throw Exception("Post sync failed")
}

fun logError(message: String, error: Exception) {
    println("ERROR: $message - ${error.message}")
}
```

#### Comprehensive Comparison Examples

```kotlin
import kotlinx.coroutines.*

fun comprehensiveComparison() = runBlocking {
    println("=== Return Types ===")

    val job: Job = launch { delay(100) }
    val deferred: Deferred<String> = async { "result" }
    val blockingResult: String = runBlocking { "result" }
    val contextResult: String = withContext(Dispatchers.Default) { "result" }
    val scopeResult: String = coroutineScope { "result" }
    val supervisorResult: String = supervisorScope { "result" }

    println("\n=== Blocking Behavior ===")

    // runBlocking: blocks thread
    println("Before runBlocking")
    runBlocking {
        delay(1000)
        println("Inside runBlocking")
    }
    println("After runBlocking (thread was blocked)")

    // Others: don't block thread
    println("Before launch")
    val launchJob = launch {
        delay(1000)
        println("Inside launch")
    }
    println("After launch (thread not blocked)")
    launchJob.join()

    println("\n=== Exception Handling ===")

    // launch: propagates to parent
    val exceptionHandler = CoroutineExceptionHandler { _, e ->
        println("Caught in handler: ${e.message}")
    }

    CoroutineScope(Dispatchers.Default + exceptionHandler).launch {
        throw RuntimeException("launch exception")
    }

    // async: exception on await
    try {
        async {
            throw RuntimeException("async exception")
        }.await()
    } catch (e: RuntimeException) {
        println("Caught on await: ${e.message}")
    }

    // withContext: throws immediately
    try {
        withContext(Dispatchers.Default) {
            throw RuntimeException("withContext exception")
        }
    } catch (e: RuntimeException) {
        println("Caught from withContext: ${e.message}")
    }

    // coroutineScope: cancels all children and throws
    try {
        coroutineScope {
            launch {
                throw RuntimeException("coroutineScope exception")
            }
            delay(1000)
        }
    } catch (e: RuntimeException) {
        println("Caught from coroutineScope: ${e.message}")
    }

    // supervisorScope: continues despite child failure
    supervisorScope {
        launch {
            throw RuntimeException("supervisorScope exception")
        }
        delay(500)
        println("supervisorScope continues")
    }

    println("\n=== Use Case: Parallel vs Sequential ===")

    // Parallel with async
    val parallelTime = measureTimeMillis {
        coroutineScope {
            val a = async { delay(1000); 1 }
            val b = async { delay(1000); 2 }
            println("Sum: ${a.await() + b.await()}")
        }
    }
    println("Parallel: $parallelTime ms")

    // Sequential with withContext
    val sequentialTime = measureTimeMillis {
        val a = withContext(Dispatchers.Default) { delay(1000); 1 }
        val b = withContext(Dispatchers.Default) { delay(1000); 2 }
        println("Sum: ${a + b}")
    }
    println("Sequential: $sequentialTime ms")

    delay(2000)
}
```

#### Performance Comparison

```kotlin
import kotlinx.coroutines.*

fun performanceComparison() = runBlocking {
    println("=== Performance Comparison ===")

    val iterations = 10000

    // launch overhead
    val launchTime = measureTimeMillis {
        val jobs = List(iterations) {
            launch { }
        }
        jobs.forEach { it.join() }
    }
    println("launch x$iterations: $launchTime ms")

    // async overhead
    val asyncTime = measureTimeMillis {
        val deferreds = List(iterations) {
            async { 42 }
        }
        deferreds.forEach { it.await() }
    }
    println("async x$iterations: $asyncTime ms")

    // withContext overhead
    val withContextTime = measureTimeMillis {
        repeat(iterations) {
            withContext(Dispatchers.Default) { 42 }
        }
    }
    println("withContext x$iterations: $withContextTime ms")

    // coroutineScope overhead
    val coroutineScopeTime = measureTimeMillis {
        repeat(iterations) {
            coroutineScope { 42 }
        }
    }
    println("coroutineScope x$iterations: $coroutineScopeTime ms")

    println("\n=== Memory Allocation ===")

    // launch: allocates Job
    // async: allocates Deferred + result storage
    // withContext: minimal allocation
    // coroutineScope: minimal allocation
}
```

### Decision Matrix

```kotlin
// Use launch when:
// - Fire-and-forget operation
// - Don't need result
// - Want to start coroutine without waiting
launch { updateCache() }

// Use async when:
// - Need result from concurrent operation
// - Want to parallelize multiple operations
// - Can wait for result later
val result = async { fetchData() }.await()

// Use runBlocking when:
// - In main function
// - In unit tests
// - Bridging blocking and suspending code
// - NEVER in production coroutines
fun main() = runBlocking { }

// Use withContext when:
// - Need to switch dispatcher
// - Sequential operation with result
// - More efficient than async + await
val data = withContext(Dispatchers.IO) { loadFromDb() }

// Use coroutineScope when:
// - Creating structured concurrency
// - Need all children to complete
// - Want exception to cancel all siblings
suspend fun loadAll() = coroutineScope {
    // all children must succeed
}

// Use supervisorScope when:
// - Children should fail independently
// - Want partial results
// - Some operations can fail without affecting others
suspend fun loadPartial() = supervisorScope {
    // children fail independently
}
```

### Best Practices

1. **Choose the right builder for the job**
2. **Avoid runBlocking in production code**
3. **Use withContext over async + await for single operations**
4. **Use coroutineScope for structured concurrency**
5. **Use supervisorScope for independent operations**

---

## Русский

### Описание проблемы

Kotlin предоставляет несколько строителей корутин (launch, async, runBlocking, withContext, coroutineScope, supervisorScope), каждый с различными характеристиками и случаями использования. Понимание различий в типах возврата, блокирующем поведении, обработке исключений и соответствующих сценариях использования критически важно для написания эффективного кода корутин.

[Полный перевод...]

---

## Follow-up Questions

1. When would you use `async` over `withContext` despite the overhead?
2. Can you nest different coroutine builders, and what are the implications?
3. How does cancellation behave differently across these builders?
4. What's the memory footprint difference between these builders?
5. Can you use `runBlocking` inside a coroutine, and should you?
6. How do these builders interact with CoroutineContext?
7. What happens if you call `await()` on multiple `Deferred` in different orders?
8. How do exception handlers work differently with each builder?

## References

- [Kotlin Coroutines Guide](https://kotlinlang.org/docs/coroutines-guide.html)
- [Coroutine Builders - API Reference](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/)
- [Roman Elizarov - Structured Concurrency](https://medium.com/@elizarov/structured-concurrency-722d765aa952)
- [Kotlin Coroutines Best Practices](https://developer.android.com/kotlin/coroutines/coroutines-best-practices)

## Related Questions

- [[q-coroutine-job-lifecycle--kotlin--medium]]
- [[q-withcontext-use-cases--kotlin--medium]]
- [[q-coroutine-supervisorjob-use-cases--kotlin--medium]]
- [[q-structured-concurrency--kotlin--hard]]
- [[q-coroutine-dispatchers--kotlin--medium]]
