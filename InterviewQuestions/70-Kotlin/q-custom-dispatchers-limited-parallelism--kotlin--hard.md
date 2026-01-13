---
---
id: kotlin-117
title: "Creating custom CoroutineDispatchers with limitedParallelism / Создание пользовательских CoroutineDispatchers с limitedParallelism"
aliases: ["Custom Dispatchers", "limitedParallelism"]
topic: kotlin
subtopics: [coroutines, dispatchers]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en]
status: draft
created: 2025-10-12
updated: 2025-10-31
category: "coroutines-advanced"
tags: ["concurrency", "difficulty/hard", "dispatchers", "limitedparallelism", "performance", "resource-management", "threading"]
description: "Deep dive into creating custom dispatchers, limitedParallelism API, thread pool sizing, and resource-specific dispatchers"
moc: moc-kotlin
related: [q-supervisor-scope-vs-coroutine-scope--kotlin--medium, q-visibility-modifiers-kotlin--kotlin--medium]
---\
# Вопрос (RU)

Когда и как следует создавать пользовательские CoroutineDispatchers в Kotlin? Объясните API `limitedParallelism()`, интеграцию с ExecutorService, стратегии определения размера пула потоков и реальные сценарии для dispatcher-ов специфичных ресурсов.

# Question (EN)

When and how should you create custom CoroutineDispatchers in Kotlin? Explain the `limitedParallelism()` API, ExecutorService integration, thread pool sizing strategies, and real-world scenarios for resource-specific dispatchers.

---

## Ответ (RU)

Ниже приведено подробное объяснение создания пользовательских dispatcher-ов, включая API limitedParallelism, интеграцию с ExecutorService и стратегии определения размера пула потоков.

## Answer (EN)

#### When to Create Custom Dispatchers

Custom dispatchers are needed when:

1. **Resource Protection**: Limiting concurrent access to shared resources (database, camera, file system)
2. **Concurrency Limiting / Rate Limiting Integration**: Controlling how many operations run at once and coordinating with external rate limits
3. **`Thread` Pool Customization**: Specific thread pool characteristics for your workload
4. **Priority Execution**: Different priority levels for certain classes of work
5. **Legacy Integration**: Bridging existing ExecutorService or thread pools with coroutines
6. **Testing**: Providing a controlled execution environment

**Default dispatchers are usually sufficient (and should be preferred by default):**
- `Dispatchers.Default`: CPU-bound work (parallelism tuned to available CPU cores)
- `Dispatchers.IO`: I/O operations (a shared pool with a higher upper bound of threads, typically up to 64 by default; implementations may evolve)
- `Dispatchers.Main`: UI thread (Android/Desktop)
- `Dispatchers.Unconfined`: Advanced/low-level cases only

#### The limitedParallelism() API (kotlinx.coroutines 1.6+)

`limitedParallelism()` creates a view of a dispatcher with a bounded level of concurrency for tasks dispatched through that view:

```kotlin
import kotlinx.coroutines.*

fun demonstrateLimitedParallelism() = runBlocking {
    // Create dispatcher with parallelism of 2 for coroutines using this view
    val limitedDispatcher = Dispatchers.IO.limitedParallelism(2)

    // Launch 5 coroutines
    val jobs = (1..5).map { id ->
        launch(limitedDispatcher) {
            println("[$id] Started on ${Thread.currentThread().name}")
            delay(1000)
            println("[$id] Finished")
        }
    }

    jobs.joinAll()
}

// Effect: at most 2 coroutines using limitedDispatcher execute concurrently,
// even though they run on the shared IO thread pool.
```

Key characteristics:
- Creates a lightweight view of the parent dispatcher
- Does not create new threads
- Uses the parent dispatcher's thread pool
- Limits concurrency of coroutines dispatched through this view (how many run at once), not specific threads
- Multiple limited views can share the same parent
- Safe to create many such views; no lifecycle management required

Comparison with old APIs:

```kotlin
// Old way (deprecated) - creates dedicated threads
@Deprecated("Use Dispatchers.IO.limitedParallelism(1)")
val oldSingleThread = newSingleThreadContext("MyThread")

@Deprecated("Use Dispatchers.IO.limitedParallelism(n)")
val oldFixedPool = newFixedThreadPoolContext(4, "MyPool")

// New way (recommended) - uses shared thread pool
val newSingleThread = Dispatchers.IO.limitedParallelism(1)
val newLimitedPool = Dispatchers.IO.limitedParallelism(4)
```

#### Why Old APIs Are Deprecated

```kotlin
import kotlinx.coroutines.*

// Problem with newSingleThreadContext: Resource leak if not closed
fun problemWithOldAPI() = runBlocking {
    val dispatcher = newSingleThreadContext("MyThread")

    launch(dispatcher) {
        println("Running on ${Thread.currentThread().name}")
    }

    // MUST call close() or the thread leaks!
    dispatcher.close()
}

// limitedParallelism does not create its own threads, so no explicit close()
fun newWaySafe() = runBlocking {
    val dispatcher = Dispatchers.IO.limitedParallelism(1)

    launch(dispatcher) {
        println("Running on ${Thread.currentThread().name}")
    }

    // No close() needed
}
```

Migration considerations:

- `newSingleThreadContext` / `newFixedThreadPoolContext` allocate dedicated threads and must be closed.
- `limitedParallelism(n)` reuses an existing pool, avoids extra threads, and has no close requirement.
- Prefer `limitedParallelism()` and `Dispatchers.IO`/`Dispatchers.Default` unless you truly need a dedicated pool.

#### Creating Dispatcher from ExecutorService

When integrating with legacy code or custom thread pools:

```kotlin
import kotlinx.coroutines.*
import java.util.concurrent.*

fun createFromExecutor() = runBlocking {
    // Create custom executor
    val executor = Executors.newFixedThreadPool(4) { runnable ->
        Thread(runnable, "CustomThread").apply {
            isDaemon = true
            priority = Thread.MAX_PRIORITY
        }
    }

    // Convert to CoroutineDispatcher
    val dispatcher = executor.asCoroutineDispatcher()

    try {
        launch(dispatcher) {
            println("Running on ${Thread.currentThread().name}")
            println("Priority: ${Thread.currentThread().priority}")
        }.join()
    } finally {
        // MUST close both dispatcher and executor
        dispatcher.close()
        executor.shutdown()
    }
}
```

Note: `ExecutorCoroutineDispatcher` exposes its underlying `Executor` and must be closed to avoid thread leaks.

#### Thread Pool Sizing Strategies

Heuristics (not strict rules):

CPU-bound tasks:

```kotlin
// Approx: number of CPU cores
val cpuBoundDispatcher = Dispatchers.Default.limitedParallelism(
    Runtime.getRuntime().availableProcessors()
)

// Often just using Dispatchers.Default is sufficient
val cpuDispatcher = Dispatchers.Default
```

I/O-bound tasks:

```kotlin
// Heuristic: higher than CPU cores because tasks spend time waiting
// Rule of thumb: cores * (1 + wait_time / compute_time)

val cores = Runtime.getRuntime().availableProcessors()
val ioDispatcher = Dispatchers.IO.limitedParallelism(cores * 10)

// Or rely on the default Dispatchers.IO configuration
val defaultIO = Dispatchers.IO
```

Mixed workloads:

```kotlin
import kotlinx.coroutines.*

class WorkloadManager {
    // CPU-intensive work
    val cpuDispatcher = Dispatchers.Default

    // I/O operations (network, disk)
    val ioDispatcher = Dispatchers.IO

    // Light I/O with controlled concurrency
    val lightIoDispatcher = Dispatchers.IO.limitedParallelism(8)

    // Database operations (e.g., single-writer SQLite)
    val databaseDispatcher = Dispatchers.IO.limitedParallelism(1)
}
```

Sizing decision table (heuristic):

| Workload Type | Parallelism (typical) | Reasoning |
|---------------|-----------------------|-----------|
| Pure CPU | # cores | Keep cores busy, avoid oversubscription |
| Pure I/O | up to ~64 | Threads mostly waiting; depends on env |
| Single-writer DB (SQLite/Room style) | 1 | Enforce serialization of writes |
| DB reads | 4-8 | Allow concurrent reads (respect DB limits) |
| API calls (rate-limited) | per API limits | Respect external constraints |
| File I/O | 4-8 | Avoid overloading disk |
| Image processing | # cores | CPU-bound |
| Network requests | tens (32-64) | Latency-bound; tune per system |

#### Custom Dispatcher for Specific Resources

Example 1: `Database` dispatcher (single writer pattern)

```kotlin
import kotlinx.coroutines.*

class DatabaseDispatcher {
    // Single-writer pattern (e.g., SQLite based storage)
    private val writeDispatcher = Dispatchers.IO.limitedParallelism(1)

    // Concurrent reads
    private val readDispatcher = Dispatchers.IO.limitedParallelism(4)

    suspend fun <T> read(block: suspend () -> T): T =
        withContext(readDispatcher) { block() }

    suspend fun <T> write(block: suspend () -> T): T =
        withContext(writeDispatcher) { block() }
}

class UserRepository(private val db: DatabaseDispatcher) {
    suspend fun getUser(id: Int): User = db.read {
        delay(50) // Simulate read
        User(id, "Name")
    }

    suspend fun saveUser(user: User) = db.write {
        delay(100) // Simulate write
    }
}

data class User(val id: Int, val name: String)
```

Example 2: Concurrency-limited API dispatcher (no custom rate algorithm)

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.*

class ConcurrentLimitedDispatcher(
    private val maxConcurrent: Int
) {
    private val semaphore = Semaphore(maxConcurrent)
    private val dispatcher = Dispatchers.IO.limitedParallelism(maxConcurrent)

    suspend fun <T> execute(block: suspend () -> T): T =
        semaphore.withPermit {
            withContext(dispatcher) { block() }
        }
}

class ApiClient {
    private val concurrentLimiter = ConcurrentLimitedDispatcher(maxConcurrent = 5)

    suspend fun fetchData(endpoint: String): String =
        concurrentLimiter.execute {
            println("Fetching $endpoint")
            delay(100)
            "Data from $endpoint"
        }
}
```

Example 3: Camera dispatcher (exclusive access)

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.*

class CameraDispatcher {
    private val mutex = Mutex()
    private val dispatcher = Dispatchers.IO.limitedParallelism(1)

    suspend fun <T> useCamera(block: suspend () -> T): T =
        mutex.withLock {
            withContext(dispatcher) { block() }
        }
}

class CameraManager(private val cameraDispatcher: CameraDispatcher) {
    suspend fun takePicture(): ByteArray = cameraDispatcher.useCamera {
        println("Opening camera...")
        delay(100)
        println("Capturing image...")
        delay(500)
        println("Closing camera...")
        ByteArray(0)
    }

    suspend fun recordVideo(duration: Long): ByteArray = cameraDispatcher.useCamera {
        println("Opening camera...")
        delay(100)
        println("Recording video for ${duration}ms...")
        delay(duration)
        println("Closing camera...")
        ByteArray(0)
    }
}
```

Note: `Dispatchers.IO.limitedParallelism(1)` provides serial execution for tasks dispatched via that view; a `Mutex` expresses mutual exclusion in code. They can be combined as above for both structured access and predictable execution context.

#### Dispatcher.IO.limitedParallelism(1) For Serial Execution

```kotlin
import kotlinx.coroutines.*

class SerialExecutionExamples {
    // Use case 1: File writing (avoid corruption)
    private val fileWriteDispatcher = Dispatchers.IO.limitedParallelism(1)

    suspend fun appendToFile(data: String) = withContext(fileWriteDispatcher) {
        println("Writing: $data")
        delay(100)
    }

    // Use case 2: Shared resource modification
    private val sharedResourceDispatcher = Dispatchers.IO.limitedParallelism(1)
    private var counter = 0

    suspend fun incrementCounter() = withContext(sharedResourceDispatcher) {
        val current = counter
        delay(10)
        counter = current + 1
    }
}
```

#### Performance Implications (Illustrative)

```kotlin
import kotlinx.coroutines.*
import kotlin.system.measureTimeMillis

suspend fun cpuIntensiveTask(): Int {
    var result = 0
    repeat(1_000_000) { result += it }
    return result
}

fun benchmarkDispatchers() = runBlocking {
    val taskCount = 100

    val defaultTime = measureTimeMillis {
        (1..taskCount).map {
            async(Dispatchers.Default) { cpuIntensiveTask() }
        }.awaitAll()
    }

    val limitedTime = measureTimeMillis {
        val limited = Dispatchers.Default.limitedParallelism(2)
        (1..taskCount).map {
            async(limited) { cpuIntensiveTask() }
        }.awaitAll()
    }

    val ioTime = measureTimeMillis {
        (1..taskCount).map {
            async(Dispatchers.IO) { cpuIntensiveTask() }
        }.awaitAll()
    }

    println("Dispatchers.Default: ${defaultTime}ms")
    println("limitedParallelism(2): ${limitedTime}ms")
    println("Dispatchers.IO: ${ioTime}ms")
}
```

Interpretation:
- Default is tuned for CPU-bound workloads.
- Too-low `limitedParallelism` underutilizes CPU.
- Using IO for CPU work may hurt performance; prefer Default.

#### Lifecycle Management

```kotlin
import kotlinx.coroutines.*
import java.util.concurrent.Executors

class ManagedDispatcher : AutoCloseable {
    private val executor = Executors.newFixedThreadPool(4)
    val dispatcher = executor.asCoroutineDispatcher()

    override fun close() {
        println("Closing dispatcher...")
        dispatcher.close()
        executor.shutdown()
        if (!executor.awaitTermination(5, java.util.concurrent.TimeUnit.SECONDS)) {
            executor.shutdownNow()
        }
    }
}

suspend fun safeDispatcherUsage() {
    ManagedDispatcher().use { managed ->
        withContext(managed.dispatcher) {
            println("Doing work...")
            delay(1000)
        }
    }
}

// Android ViewModel example
class MyViewModel : ViewModel() {
    private val executor = Executors.newFixedThreadPool(2)
    private val customDispatcher = executor.asCoroutineDispatcher()

    fun doWork() {
        viewModelScope.launch(customDispatcher) {
            // Work...
        }
    }

    override fun onCleared() {
        super.onCleared()
        customDispatcher.close()
        executor.shutdown()
    }
}
```

Note: `awaitTermination` is blocking; use it only from appropriate contexts (e.g., not on main/UI thread).

#### Testing with Custom Dispatchers

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import kotlin.test.Test
import kotlin.test.assertEquals

class DispatcherTests {
    @Test
    fun testWithCustomDispatcher() = runTest {
        val dispatcher = StandardTestDispatcher(testScheduler)

        launch(dispatcher) {
            delay(1000)
            println("Task completed")
        }

        // Advance virtual time so the coroutine can complete
        advanceTimeBy(1000)
    }

    @Test
    fun testConcurrentExecutionCount() = runTest {
        val limited = Dispatchers.Default.limitedParallelism(2)
        var maxConcurrent = 0
        var current = 0

        val jobs = (1..10).map {
            launch(limited) {
                synchronized(this@testConcurrentExecutionCount) {
                    current++
                    if (current > maxConcurrent) maxConcurrent = current
                }
                delay(100)
                synchronized(this@testConcurrentExecutionCount) {
                    current--
                }
            }
        }

        jobs.joinAll()
        // Ensure parallelism limit was respected (best-effort illustrative check)
        assertEquals(2, maxConcurrent)
    }
}
```

### Real-World Examples

Example 1: Image processing pipeline

```kotlin
import kotlinx.coroutines.*

class ImageProcessor {
    private val processingDispatcher = Dispatchers.Default
    private val diskDispatcher = Dispatchers.IO.limitedParallelism(4)
    private val uploadDispatcher = Dispatchers.IO.limitedParallelism(2)

    suspend fun processAndUploadImage(path: String) {
        val imageData = withContext(diskDispatcher) { loadImageFromDisk(path) }
        val processed = withContext(processingDispatcher) { applyFilters(imageData) }
        withContext(uploadDispatcher) { uploadToServer(processed) }
    }

    private suspend fun loadImageFromDisk(path: String): ByteArray {
        delay(100)
        return ByteArray(0)
    }

    private suspend fun applyFilters(data: ByteArray): ByteArray {
        delay(200)
        return data
    }

    private suspend fun uploadToServer(data: ByteArray) {
        delay(300)
    }
}
```

Example 2: Multi-tenant resource manager

```kotlin
import kotlinx.coroutines.*

class MultiTenantResourceManager {
    private val dispatchers = mutableMapOf<String, CoroutineDispatcher>()

    fun getDispatcher(tenantId: String, maxParallelism: Int): CoroutineDispatcher {
        return dispatchers.getOrPut(tenantId) {
            Dispatchers.IO.limitedParallelism(maxParallelism)
        }
    }

    suspend fun <T> executeForTenant(
        tenantId: String,
        maxParallelism: Int,
        block: suspend () -> T
    ): T {
        val dispatcher = getDispatcher(tenantId, maxParallelism)
        return withContext(dispatcher) { block() }
    }
}

suspend fun demonstrateMultiTenant() {
    val manager = MultiTenantResourceManager()

    coroutineScope {
        launch {
            manager.executeForTenant("premium-customer", 10) {
                delay(1000)
            }
        }

        launch {
            manager.executeForTenant("free-user", 2) {
                delay(1000)
            }
        }
    }
}
```

Note: Each tenant gets its own limited view, but all share the underlying IO pool. Limits are per-view, not hard per-tenant CPU isolation.

### Common Pitfalls and Gotchas

1. Forgetting to close ExecutorCoroutineDispatcher

```kotlin
fun leakyCode() = runBlocking {
    val executor = Executors.newFixedThreadPool(4)
    val dispatcher = executor.asCoroutineDispatcher()

    launch(dispatcher) {
        // work
    }
    // Missing: dispatcher.close() and executor.shutdown()
}

fun properCode() = runBlocking {
    val executor = Executors.newFixedThreadPool(4)
    val dispatcher = executor.asCoroutineDispatcher()

    try {
        launch(dispatcher) {
            // work
        }.join()
    } finally {
        dispatcher.close()
        executor.shutdown()
    }
}
```

1. Using wrong dispatcher for workload

```kotlin
// Bad - CPU work on IO dispatcher
suspend fun badChoice() = withContext(Dispatchers.IO) {
    (1..1_000_000).sum()
}

// Good - CPU work on Default dispatcher
suspend fun goodChoice() = withContext(Dispatchers.Default) {
    (1..1_000_000).sum()
}
```

1. Over-limiting parallelism

```kotlin
val tooLimited = Dispatchers.IO.limitedParallelism(1)

suspend fun slowIO() {
    (1..100).map {
        async(tooLimited) {
            delay(100)
        }
    }.awaitAll()
    // This takes ~10 seconds instead of ~100ms due to unnecessary serialization
}

val appropriateLimit = Dispatchers.IO.limitedParallelism(10)
```

### Summary

Custom dispatchers are typically created using `limitedParallelism()` (preferred) or `asCoroutineDispatcher()` (when integrating with an `ExecutorService`). Key principles:

- `limitedParallelism()` is lightweight, reuses existing pools, and is the recommended way to bound concurrency.
- Size concurrency limits based on workload type: cores for CPU-bound, higher (heuristic) for I/O-bound.
- Use limited views or synchronization (e.g., `Mutex`) to protect exclusive resources.
- Always close `ExecutorCoroutineDispatcher` wrappers (and underlying executors) to avoid leaks.
- In tests, use `TestDispatcher` and `runTest` for deterministic, controllable execution.

---

## Follow-ups

1. How does `limitedParallelism()` internally implement concurrency limiting without creating new threads?
2. Trade-offs between using a single dispatcher with high parallelism vs multiple limited views for different workloads.
3. How to design a dispatcher or wrapper with dynamic parallelism adjustment based on load.
4. `Dispatchers.IO.limitedParallelism(1)` vs `Mutex` for serializing access to a shared resource.
5. Monitoring and debugging dispatcher usage in production (queue lengths, active coroutines, throughput, latencies).
6. `limitedParallelism()` interaction with `CoroutineStart.LAZY` and when limits are applied.
7. Designing a scalable dispatcher pool based on queue depth and SLOs.

## References

- [Kotlin Coroutines Guide - `Coroutine` `Context` and Dispatchers](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)
- [limitedParallelism Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-coroutine-dispatcher/limited-parallelism.html)
- [ExecutorCoroutineDispatcher API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-executor-coroutine-dispatcher/)
- [Roman Elizarov - Explicit Concurrency](https://medium.com/@elizarov/explicit-concurrency-67a8e8fd9b25)
- [Dispatchers Migration Guide](https://github.com/Kotlin/kotlinx.coroutines/blob/master/docs/topics/migration.md)

## Related Questions

- [[q-deferred-async-patterns--kotlin--medium]]
- [[q-flowon-operator-context-switching--kotlin--hard]]
- [[q-testing-coroutine-timing-control--kotlin--medium]]
- [[q-coroutine-memory-leak-detection--kotlin--hard]]
- [[q-channel-buffer-strategies-comparison--kotlin--hard]]

## Tags
#kotlin #coroutines #dispatchers #threading #performance #limitedparallelism #custom-dispatchers #resource-management
