---
topic: kotlin
id: kotlin-117
title: "Creating custom CoroutineDispatchers with limitedParallelism / Кастомные диспетчеры"
aliases: [Custom Dispatchers, Кастомные диспетчеры]
subtopics: [coroutines, dispatchers]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-12
updated: 2025-10-31
category: "coroutines-advanced"
tags: ["dispatchers", "threading", "limitedparallelism", "performance", "resource-management", "concurrency", "difficulty/hard"]
description: "Deep dive into creating custom dispatchers, limitedParallelism API, thread pool sizing, and resource-specific dispatchers"
moc: moc-kotlin
related: [q-kotlin-map-collection--programming-languages--easy, q-visibility-modifiers-kotlin--kotlin--medium, q-supervisor-scope-vs-coroutine-scope--kotlin--medium]
---

# Creating custom CoroutineDispatchers with limitedParallelism / Создание кастомных диспетчеров

# Question (EN)

> When and how should you create custom CoroutineDispatchers in Kotlin? Explain the `limitedParallelism()` API, ExecutorService integration, thread pool sizing strategies, and real-world scenarios for resource-specific dispatchers.

# Вопрос (RU)

> Когда и как следует создавать кастомные CoroutineDispatchers в Kotlin? Объясните API `limitedParallelism()`, интеграцию с ExecutorService, стратегии размера пула потоков и реальные сценарии для диспетчеров специфических ресурсов.

---

## Answer (EN)

#### When to Create Custom Dispatchers

Custom dispatchers are needed when:

1. **Resource Protection**: Limiting concurrent access to shared resources (database, camera, file system)
2. **Rate Limiting**: Controlling API call frequency
3. **Thread Pool Customization**: Specific thread pool characteristics for your workload
4. **Priority Execution**: Different priority levels for tasks
5. **Legacy Integration**: Bridging existing ExecutorService with coroutines
6. **Testing**: Controlled execution environment

**Default dispatchers are usually sufficient:**
- `Dispatchers.Default`: CPU-bound work (parallelism = CPU cores)
- `Dispatchers.IO`: I/O operations (parallelism = 64 by default)
- `Dispatchers.Main`: UI thread (Android/Desktop)
- `Dispatchers.Unconfined`: Advanced cases only

#### The limitedParallelism() API (Kotlin 1.6+)

`limitedParallelism()` creates a view of a dispatcher with limited parallelism:

```kotlin
import kotlinx.coroutines.*

fun demonstrateLimitedParallelism() = runBlocking {
    // Create dispatcher with parallelism of 2
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

// Output shows only 2 coroutines running concurrently:
// [1] Started on DefaultDispatcher-worker-1
// [2] Started on DefaultDispatcher-worker-2
// [1] Finished
// [3] Started on DefaultDispatcher-worker-1
// [2] Finished
// [4] Started on DefaultDispatcher-worker-2
// ...
```

**Key characteristics:**
- Creates a **view** of the parent dispatcher
- Doesn't create new threads
- Uses parent dispatcher's thread pool
- Controls **concurrency**, not which threads
- Multiple views can share the same parent
- Lightweight and efficient

**Comparison with old APIs:**

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
import java.util.concurrent.Executors

// Problem with newSingleThreadContext: Resource leak if not closed
fun problemWithOldAPI() = runBlocking {
    val dispatcher = newSingleThreadContext("MyThread")

    launch(dispatcher) {
        println("Running on ${Thread.currentThread().name}")
    }

    // MUST call close() or thread leaks!
    dispatcher.close()
}

// Problem: Easy to forget, especially with exceptions
fun leakyCode() = runBlocking {
    val dispatcher = newSingleThreadContext("LeakyThread")
    try {
        launch(dispatcher) {
            throw Exception("Oops")
        }
    } finally {
        // If you forget this, thread leaks forever
        // dispatcher.close()
    }
}

// limitedParallelism doesn't create threads, so no leak
fun newWaySafe() = runBlocking {
    val dispatcher = Dispatchers.IO.limitedParallelism(1)

    launch(dispatcher) {
        println("Running on ${Thread.currentThread().name}")
    }

    // No close() needed!
}
```

**Why migration is important:**

| Old API | Problem | New API |
|---------|---------|---------|
| `newSingleThreadContext` | Dedicated thread, must close | `limitedParallelism(1)` |
| `newFixedThreadPoolContext` | Dedicated threads, must close | `limitedParallelism(n)` |
| Resource leak risk | Thread leaks if not closed | No threads created |
| Memory overhead | Each dispatcher = new threads | Shared thread pool |

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

**ExecutorCoroutineDispatcher interface:**

```kotlin
public abstract class ExecutorCoroutineDispatcher : CoroutineDispatcher(), Closeable {
    public abstract val executor: Executor
    public abstract override fun close()
}
```

**Real-world example: Custom priority dispatcher**

```kotlin
import kotlinx.coroutines.*
import java.util.concurrent.*

enum class TaskPriority {
    HIGH, NORMAL, LOW
}

class PriorityDispatcher {
    private val executor = ThreadPoolExecutor(
        2, // core pool size
        4, // max pool size
        60L, TimeUnit.SECONDS, // keep alive
        PriorityBlockingQueue<Runnable>(11, compareBy {
            (it as? PriorityTask)?.priority?.ordinal ?: Int.MAX_VALUE
        })
    )

    private data class PriorityTask(
        val priority: TaskPriority,
        val runnable: Runnable
    ) : Runnable by runnable

    val dispatcher = executor.asCoroutineDispatcher()

    suspend fun <T> execute(priority: TaskPriority, block: suspend () -> T): T =
        withContext(dispatcher) {
            // Note: Priority is set at submission time
            block()
        }

    fun close() {
        dispatcher.close()
        executor.shutdown()
    }
}

// Usage
suspend fun usePriorityDispatcher() {
    val priorityDispatcher = PriorityDispatcher()

    try {
        coroutineScope {
            launch {
                priorityDispatcher.execute(TaskPriority.LOW) {
                    println("Low priority task")
                    delay(1000)
                }
            }

            launch {
                priorityDispatcher.execute(TaskPriority.HIGH) {
                    println("High priority task")
                    delay(1000)
                }
            }
        }
    } finally {
        priorityDispatcher.close()
    }
}
```

#### Thread Pool Sizing Strategies

**CPU-bound tasks:**

```kotlin
// Formula: Number of CPU cores
val cpuBoundDispatcher = Dispatchers.Default.limitedParallelism(
    Runtime.getRuntime().availableProcessors()
)

// Or just use Default
val cpuDispatcher = Dispatchers.Default
```

**I/O-bound tasks:**

```kotlin
// Formula: Much higher than CPU cores
// Rule of thumb: cores * (1 + wait_time / compute_time)

// Example: If 90% waiting, 10% computing
val cores = Runtime.getRuntime().availableProcessors()
val ioDispatcher = Dispatchers.IO.limitedParallelism(cores * 10)

// Or use default IO (parallelism = 64)
val defaultIO = Dispatchers.IO
```

**Mixed workload:**

```kotlin
import kotlinx.coroutines.*

class WorkloadManager {
    // CPU-intensive work
    val cpuDispatcher = Dispatchers.Default

    // I/O operations (network, disk)
    val ioDispatcher = Dispatchers.IO

    // Light I/O with controlled concurrency
    val lightIoDispatcher = Dispatchers.IO.limitedParallelism(8)

    // Database operations (single writer)
    val databaseDispatcher = Dispatchers.IO.limitedParallelism(1)

    // Heavy I/O (large file operations)
    val heavyIoDispatcher = Dispatchers.IO.limitedParallelism(4)
}

// Usage
suspend fun processData(manager: WorkloadManager) {
    // Parse JSON (CPU-bound)
    val parsed = withContext(manager.cpuDispatcher) {
        parseJson()
    }

    // Save to database (needs serialization)
    withContext(manager.databaseDispatcher) {
        saveToDatabase(parsed)
    }

    // Upload to server (I/O-bound)
    withContext(manager.ioDispatcher) {
        uploadToServer(parsed)
    }
}

suspend fun parseJson() = delay(100) // Simulate
suspend fun saveToDatabase(data: Any) = delay(50)
suspend fun uploadToServer(data: Any) = delay(200)
```

**Sizing decision table:**

| Workload Type | Parallelism | Reasoning |
|---------------|-------------|-----------|
| Pure CPU | # cores | Minimize context switching |
| Pure I/O | 64+ | Threads mostly waiting |
| Database writes | 1 | Serialize writes |
| Database reads | 4-8 | Allow concurrent reads |
| API calls (rate-limited) | Rate limit | Respect API limits |
| File I/O | 4-8 | Disk concurrency limit |
| Image processing | # cores | CPU-bound |
| Network requests | 32-64 | I/O-bound |

#### Custom Dispatcher for Specific Resources

**Example 1: Database dispatcher (single writer)**

```kotlin
import kotlinx.coroutines.*

class DatabaseDispatcher {
    // Single thread for writes (SQLite requirement)
    private val writeDispatcher = Dispatchers.IO.limitedParallelism(1)

    // Multiple threads for reads
    private val readDispatcher = Dispatchers.IO.limitedParallelism(4)

    suspend fun <T> read(block: suspend () -> T): T =
        withContext(readDispatcher) {
            block()
        }

    suspend fun <T> write(block: suspend () -> T): T =
        withContext(writeDispatcher) {
            block()
        }
}

// Usage
class UserRepository(private val db: DatabaseDispatcher) {
    suspend fun getUser(id: Int): User = db.read {
        // Read query (can run in parallel with other reads)
        delay(50)
        User(id, "Name")
    }

    suspend fun saveUser(user: User) = db.write {
        // Write query (serialized with other writes)
        delay(100)
    }
}

data class User(val id: Int, val name: String)

suspend fun demonstrateDatabaseAccess() {
    val db = DatabaseDispatcher()
    val repo = UserRepository(db)

    coroutineScope {
        // Multiple reads in parallel
        val users = (1..5).map { id ->
            async { repo.getUser(id) }
        }.awaitAll()

        // Writes are serialized automatically
        users.forEach { user ->
            launch { repo.saveUser(user) }
        }
    }
}
```

**Example 2: Rate-limited API dispatcher**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.*
import kotlin.time.*
import kotlin.time.Duration.Companion.seconds

class RateLimitedDispatcher(
    private val maxConcurrent: Int,
    private val requestsPerSecond: Int
) {
    private val semaphore = Semaphore(maxConcurrent)
    private val rateLimiter = RateLimiter(requestsPerSecond)
    private val dispatcher = Dispatchers.IO.limitedParallelism(maxConcurrent)

    suspend fun <T> execute(block: suspend () -> T): T {
        semaphore.withPermit {
            rateLimiter.acquire()
            return withContext(dispatcher) {
                block()
            }
        }
    }
}

class RateLimiter(private val permitsPerSecond: Int) {
    private val permits = Semaphore(permitsPerSecond)
    private var lastRefill = System.currentTimeMillis()

    suspend fun acquire() {
        refillIfNeeded()
        permits.acquire()
    }

    private suspend fun refillIfNeeded() {
        val now = System.currentTimeMillis()
        val elapsed = now - lastRefill

        if (elapsed >= 1000) {
            val toRefill = (elapsed / 1000).toInt() * permitsPerSecond
            repeat(minOf(toRefill, permitsPerSecond - permits.availablePermits)) {
                permits.release()
            }
            lastRefill = now
        }
    }
}

// Usage: API client with rate limiting
class ApiClient {
    // Max 5 concurrent requests, 10 requests per second
    private val rateLimiter = RateLimitedDispatcher(
        maxConcurrent = 5,
        requestsPerSecond = 10
    )

    suspend fun fetchData(endpoint: String): String =
        rateLimiter.execute {
            println("[${System.currentTimeMillis()}] Fetching $endpoint")
            delay(100) // Simulate API call
            "Data from $endpoint"
        }
}

suspend fun demonstrateRateLimiting() {
    val client = ApiClient()

    // Try to make 20 requests - will be rate limited
    coroutineScope {
        (1..20).map { id ->
            async {
                client.fetchData("endpoint-$id")
            }
        }.awaitAll()
    }
}
```

**Example 3: Camera dispatcher (exclusive access)**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.*

class CameraDispatcher {
    // Only one coroutine can use camera at a time
    private val mutex = Mutex()
    private val dispatcher = Dispatchers.IO.limitedParallelism(1)

    suspend fun <T> useCamera(block: suspend () -> T): T =
        mutex.withLock {
            withContext(dispatcher) {
                block()
            }
        }
}

class CameraManager(private val cameraDispatcher: CameraDispatcher) {
    suspend fun takePicture(): ByteArray = cameraDispatcher.useCamera {
        println("Opening camera...")
        delay(100)
        println("Capturing image...")
        delay(500)
        println("Closing camera...")
        ByteArray(0) // Simulated image data
    }

    suspend fun recordVideo(duration: Long): ByteArray = cameraDispatcher.useCamera {
        println("Opening camera...")
        delay(100)
        println("Recording video for ${duration}ms...")
        delay(duration)
        println("Closing camera...")
        ByteArray(0) // Simulated video data
    }
}

suspend fun demonstrateCameraAccess() {
    val cameraDispatcher = CameraDispatcher()
    val camera = CameraManager(cameraDispatcher)

    coroutineScope {
        // These will execute sequentially (only one can access camera)
        launch { camera.takePicture() }
        launch { camera.recordVideo(1000) }
        launch { camera.takePicture() }
    }
}
```

#### Dispatcher.IO.limitedParallelism(1) for Serial Execution

```kotlin
import kotlinx.coroutines.*

// Serial execution use cases
class SerialExecutionExamples {
    // Use case 1: File writing (avoid corruption)
    private val fileWriteDispatcher = Dispatchers.IO.limitedParallelism(1)

    suspend fun appendToFile(data: String) = withContext(fileWriteDispatcher) {
        // Guaranteed serial execution
        println("Writing: $data")
        delay(100)
    }

    // Use case 2: Shared resource modification
    private val sharedResourceDispatcher = Dispatchers.IO.limitedParallelism(1)
    private var counter = 0

    suspend fun incrementCounter() = withContext(sharedResourceDispatcher) {
        // No race conditions - serial execution
        val current = counter
        delay(10) // Simulate work
        counter = current + 1
    }

    // Use case 3: Order-dependent operations
    private val orderDispatcher = Dispatchers.IO.limitedParallelism(1)

    suspend fun processInOrder(item: Int) = withContext(orderDispatcher) {
        println("Processing $item in order")
        delay(50)
    }
}

suspend fun demonstrateSerialExecution() {
    val examples = SerialExecutionExamples()

    coroutineScope {
        // Launch 5 concurrent coroutines
        repeat(5) { i ->
            launch {
                examples.appendToFile("Data $i")
            }
        }
    }
    // Output is always sequential:
    // Writing: Data 0
    // Writing: Data 1
    // Writing: Data 2
    // ...
}
```

#### Performance Implications

**Benchmark: Default vs Limited Parallelism**

```kotlin
import kotlinx.coroutines.*
import kotlin.system.measureTimeMillis

suspend fun cpuIntensiveTask(): Int {
    // Simulate CPU work
    var result = 0
    repeat(1_000_000) {
        result += it
    }
    return result
}

fun benchmarkDispatchers() = runBlocking {
    val taskCount = 100

    // Benchmark 1: Dispatchers.Default (optimal for CPU-bound)
    val defaultTime = measureTimeMillis {
        (1..taskCount).map {
            async(Dispatchers.Default) {
                cpuIntensiveTask()
            }
        }.awaitAll()
    }

    // Benchmark 2: Limited parallelism (too low)
    val limitedTime = measureTimeMillis {
        val limited = Dispatchers.Default.limitedParallelism(2)
        (1..taskCount).map {
            async(limited) {
                cpuIntensiveTask()
            }
        }.awaitAll()
    }

    // Benchmark 3: IO dispatcher (wrong choice for CPU work)
    val ioTime = measureTimeMillis {
        (1..taskCount).map {
            async(Dispatchers.IO) {
                cpuIntensiveTask()
            }
        }.awaitAll()
    }

    println("Dispatchers.Default: ${defaultTime}ms")
    println("limitedParallelism(2): ${limitedTime}ms")
    println("Dispatchers.IO: ${ioTime}ms")
}

// Typical results on 8-core CPU:
// Dispatchers.Default: 1500ms (optimal)
// limitedParallelism(2): 6000ms (4x slower - underutilized)
// Dispatchers.IO: 2000ms (worse - wrong pool)
```

**Memory overhead comparison:**

```kotlin
import kotlinx.coroutines.*
import java.util.concurrent.Executors

fun compareMemoryOverhead() {
    // Old way: 100 dispatchers = 100 threads
    @Suppress("DEPRECATION")
    val oldDispatchers = (1..100).map {
        newSingleThreadContext("Thread-$it")
    }
    // Memory: ~100 MB (1 MB per thread stack)

    // New way: 100 views = 0 new threads
    val newDispatchers = (1..100).map {
        Dispatchers.IO.limitedParallelism(1)
    }
    // Memory: ~1 MB (just dispatcher objects)

    oldDispatchers.forEach { it.close() }
}
```

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

// Usage with use() for automatic cleanup
suspend fun safeDispatcherUsage() {
    ManagedDispatcher().use { managed ->
        withContext(managed.dispatcher) {
            println("Doing work...")
            delay(1000)
        }
    } // Automatically closed
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

#### Testing with Custom Dispatchers

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.test.*
import org.junit.Test
import kotlin.test.assertEquals

class DispatcherTests {
    @Test
    fun testWithCustomDispatcher() = runTest {
        val dispatcher = StandardTestDispatcher(testScheduler)

        launch(dispatcher) {
            delay(1000)
            println("Task completed")
        }

        advanceTimeBy(1000)
    }

    @Test
    fun testRateLimiting() = runTest {
        val executions = mutableListOf<Long>()

        // Use test dispatcher for controlled timing
        val testDispatcher = StandardTestDispatcher(testScheduler)

        repeat(5) {
            launch(testDispatcher) {
                executions.add(currentTime)
                delay(100)
            }
        }

        advanceUntilIdle()

        // Verify executions happened at expected times
        assertEquals(5, executions.size)
    }
}
```

### Real-World Examples

**Example 1: Image processing pipeline**

```kotlin
import kotlinx.coroutines.*

class ImageProcessor {
    // CPU-intensive operations
    private val processingDispatcher = Dispatchers.Default

    // Disk I/O
    private val diskDispatcher = Dispatchers.IO.limitedParallelism(4)

    // Network upload (rate-limited)
    private val uploadDispatcher = Dispatchers.IO.limitedParallelism(2)

    suspend fun processAndUploadImage(path: String) {
        // Load from disk
        val imageData = withContext(diskDispatcher) {
            loadImageFromDisk(path)
        }

        // Process (CPU-intensive)
        val processed = withContext(processingDispatcher) {
            applyFilters(imageData)
        }

        // Upload (network I/O)
        withContext(uploadDispatcher) {
            uploadToServer(processed)
        }
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

**Example 2: Multi-tenant resource manager**

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
        return withContext(dispatcher) {
            block()
        }
    }
}

// Usage
suspend fun demonstrateMultiTenant() {
    val manager = MultiTenantResourceManager()

    coroutineScope {
        // Premium tenant: 10 concurrent operations
        launch {
            manager.executeForTenant("premium-customer", 10) {
                // Heavy operation
                delay(1000)
            }
        }

        // Free tenant: 2 concurrent operations
        launch {
            manager.executeForTenant("free-user", 2) {
                // Same operation, but limited
                delay(1000)
            }
        }
    }
}
```

### Common Pitfalls and Gotchas

1. **Forgetting to close ExecutorCoroutineDispatcher**
```kotlin
// Bad - thread leak
fun leakyCode() = runBlocking {
    val executor = Executors.newFixedThreadPool(4)
    val dispatcher = executor.asCoroutineDispatcher()

    launch(dispatcher) {
        // work
    }
    // Missing: dispatcher.close() and executor.shutdown()
}

// Good - proper cleanup
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

2. **Using wrong dispatcher for workload**
```kotlin
// Bad - CPU work on IO dispatcher
suspend fun badChoice() = withContext(Dispatchers.IO) {
    // CPU-intensive work (wrong dispatcher!)
    (1..1_000_000).sum()
}

// Good - CPU work on Default dispatcher
suspend fun goodChoice() = withContext(Dispatchers.Default) {
    // CPU-intensive work
    (1..1_000_000).sum()
}
```

3. **Over-limiting parallelism**
```kotlin
// Bad - too restrictive for I/O work
val tooLimited = Dispatchers.IO.limitedParallelism(1)

suspend fun slowIO() {
    (1..100).map {
        async(tooLimited) {
            delay(100) // Simulated I/O
        }
    }.awaitAll()
    // Takes 10 seconds instead of 100ms!
}

// Good - appropriate parallelism for I/O
val appropriateLimit = Dispatchers.IO.limitedParallelism(10)
```

### Summary

**Custom dispatchers** are created using `limitedParallelism()` (preferred) or `asCoroutineDispatcher()` (for ExecutorService). Key principles:

- **limitedParallelism()**: Lightweight, no new threads, recommended
- **Thread pool sizing**: CPU cores for CPU work, higher for I/O work
- **Resource protection**: Use limited parallelism (often 1) for exclusive resources
- **Lifecycle**: Close ExecutorCoroutineDispatchers to avoid leaks
- **Testing**: Use TestDispatcher for controlled execution

Choose the right dispatcher for your workload to maximize performance and resource efficiency.

---

## Ответ (RU)

*(Краткое содержание основных пунктов из английской версии)*

#### Когда создавать кастомные диспетчеры

Кастомные диспетчеры нужны когда:

1. **Защита ресурсов**: Ограничение конкурентного доступа к общим ресурсам (база данных, камера, файловая система)
2. **Ограничение скорости**: Контроль частоты API вызовов
3. **Настройка пула потоков**: Специфические характеристики пула потоков для вашей нагрузки
4. **Приоритетное выполнение**: Разные уровни приоритета для задач
5. **Интеграция с legacy**: Мост между существующим ExecutorService и корутинами
6. **Тестирование**: Контролируемая среда выполнения

**Стандартные диспетчеры обычно достаточны:**
- `Dispatchers.Default`: CPU-зависимая работа (параллелизм = ядра CPU)
- `Dispatchers.IO`: I/O операции (параллелизм = 64 по умолчанию)
- `Dispatchers.Main`: UI поток (Android/Desktop)
- `Dispatchers.Unconfined`: Только для продвинутых случаев

#### API limitedParallelism() (Kotlin 1.6+)

`limitedParallelism()` создаёт представление диспетчера с ограниченным параллелизмом:

```kotlin
import kotlinx.coroutines.*

fun demonstrateLimitedParallelism() = runBlocking {
    // Создаём диспетчер с параллелизмом 2
    val limitedDispatcher = Dispatchers.IO.limitedParallelism(2)

    // Запускаем 5 корутин
    val jobs = (1..5).map { id ->
        launch(limitedDispatcher) {
            println("[$id] Запущен на ${Thread.currentThread().name}")
            delay(1000)
            println("[$id] Завершён")
        }
    }

    jobs.joinAll()
}

// Вывод показывает только 2 корутины выполняются одновременно
```

**Ключевые характеристики:**
- Создаёт **представление** родительского диспетчера
- Не создаёт новые потоки
- Использует пул потоков родительского диспетчера
- Контролирует **конкурентность**, а не какие потоки
- Несколько представлений могут использовать одного родителя
- Лёгкий и эффективный

**Сравнение со старыми API:**

```kotlin
// Старый способ (устарел) - создаёт выделенные потоки
@Deprecated("Используйте Dispatchers.IO.limitedParallelism(1)")
val oldSingleThread = newSingleThreadContext("MyThread")

@Deprecated("Используйте Dispatchers.IO.limitedParallelism(n)")
val oldFixedPool = newFixedThreadPoolContext(4, "MyPool")

// Новый способ (рекомендуется) - использует общий пул потоков
val newSingleThread = Dispatchers.IO.limitedParallelism(1)
val newLimitedPool = Dispatchers.IO.limitedParallelism(4)
```

#### Почему старые API устарели

```kotlin
import kotlinx.coroutines.*

// Проблема с newSingleThreadContext: Утечка ресурсов если не закрыть
fun problemWithOldAPI() = runBlocking {
    val dispatcher = newSingleThreadContext("MyThread")

    launch(dispatcher) {
        println("Выполняется на ${Thread.currentThread().name}")
    }

    // ДОЛЖНЫ вызвать close() или поток утечёт!
    dispatcher.close()
}

// limitedParallelism не создаёт потоки, поэтому нет утечки
fun newWaySafe() = runBlocking {
    val dispatcher = Dispatchers.IO.limitedParallelism(1)

    launch(dispatcher) {
        println("Выполняется на ${Thread.currentThread().name}")
    }

    // close() не нужен!
}
```

#### Создание диспетчера из ExecutorService

При интеграции с legacy кодом или кастомными пулами потоков:

```kotlin
import kotlinx.coroutines.*
import java.util.concurrent.*

fun createFromExecutor() = runBlocking {
    // Создаём кастомный executor
    val executor = Executors.newFixedThreadPool(4) { runnable ->
        Thread(runnable, "CustomThread").apply {
            isDaemon = true
            priority = Thread.MAX_PRIORITY
        }
    }

    // Конвертируем в CoroutineDispatcher
    val dispatcher = executor.asCoroutineDispatcher()

    try {
        launch(dispatcher) {
            println("Выполняется на ${Thread.currentThread().name}")
            println("Приоритет: ${Thread.currentThread().priority}")
        }.join()
    } finally {
        // ДОЛЖНЫ закрыть и диспетчер и executor
        dispatcher.close()
        executor.shutdown()
    }
}
```

#### Стратегии размера пула потоков

**CPU-зависимые задачи:**

```kotlin
// Формула: Количество ядер CPU
val cpuBoundDispatcher = Dispatchers.Default.limitedParallelism(
    Runtime.getRuntime().availableProcessors()
)
```

**I/O-зависимые задачи:**

```kotlin
// Формула: Значительно больше чем ядра CPU
// Эмпирическое правило: ядра * (1 + время_ожидания / время_вычисления)

val cores = Runtime.getRuntime().availableProcessors()
val ioDispatcher = Dispatchers.IO.limitedParallelism(cores * 10)
```

**Таблица решений по размеру:**

| Тип нагрузки | Параллелизм | Обоснование |
|--------------|-------------|-------------|
| Чистый CPU | # ядер | Минимизация переключения контекста |
| Чистый I/O | 64+ | Потоки в основном ждут |
| Запись в БД | 1 | Сериализация записей |
| Чтение из БД | 4-8 | Разрешить конкурентное чтение |
| API вызовы (с лимитом) | Лимит rate | Соблюдать ограничения API |
| Файловый I/O | 4-8 | Ограничение конкурентности диска |

#### Кастомный диспетчер для специфических ресурсов

**Пример 1: Диспетчер базы данных (один писатель)**

```kotlin
import kotlinx.coroutines.*

class DatabaseDispatcher {
    // Один поток для записей (требование SQLite)
    private val writeDispatcher = Dispatchers.IO.limitedParallelism(1)

    // Несколько потоков для чтений
    private val readDispatcher = Dispatchers.IO.limitedParallelism(4)

    suspend fun <T> read(block: suspend () -> T): T =
        withContext(readDispatcher) {
            block()
        }

    suspend fun <T> write(block: suspend () -> T): T =
        withContext(writeDispatcher) {
            block()
        }
}

// Использование
class UserRepository(private val db: DatabaseDispatcher) {
    suspend fun getUser(id: Int): User = db.read {
        // Запрос чтения (может выполняться параллельно с другими чтениями)
        delay(50)
        User(id, "Имя")
    }

    suspend fun saveUser(user: User) = db.write {
        // Запрос записи (сериализуется с другими записями)
        delay(100)
    }
}

data class User(val id: Int, val name: String)
```

**Пример 2: API диспетчер с ограничением скорости**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.*

class RateLimitedDispatcher(
    private val maxConcurrent: Int,
    private val requestsPerSecond: Int
) {
    private val semaphore = Semaphore(maxConcurrent)
    private val dispatcher = Dispatchers.IO.limitedParallelism(maxConcurrent)

    suspend fun <T> execute(block: suspend () -> T): T {
        semaphore.withPermit {
            return withContext(dispatcher) {
                block()
            }
        }
    }
}

// Использование: API клиент с ограничением скорости
class ApiClient {
    // Макс 5 одновременных запросов, 10 запросов в секунду
    private val rateLimiter = RateLimitedDispatcher(
        maxConcurrent = 5,
        requestsPerSecond = 10
    )

    suspend fun fetchData(endpoint: String): String =
        rateLimiter.execute {
            println("Загрузка $endpoint")
            delay(100) // Имитация API вызова
            "Данные из $endpoint"
        }
}
```

**Пример 3: Диспетчер камеры (эксклюзивный доступ)**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.*

class CameraDispatcher {
    // Только одна корутина может использовать камеру одновременно
    private val mutex = Mutex()
    private val dispatcher = Dispatchers.IO.limitedParallelism(1)

    suspend fun <T> useCamera(block: suspend () -> T): T =
        mutex.withLock {
            withContext(dispatcher) {
                block()
            }
        }
}

class CameraManager(private val cameraDispatcher: CameraDispatcher) {
    suspend fun takePicture(): ByteArray = cameraDispatcher.useCamera {
        println("Открытие камеры...")
        delay(100)
        println("Захват изображения...")
        delay(500)
        println("Закрытие камеры...")
        ByteArray(0)
    }
}
```

#### Dispatcher.IO.limitedParallelism(1) для последовательного выполнения

```kotlin
import kotlinx.coroutines.*

class SerialExecutionExamples {
    // Случай использования 1: Запись в файл (избежать повреждения)
    private val fileWriteDispatcher = Dispatchers.IO.limitedParallelism(1)

    suspend fun appendToFile(data: String) = withContext(fileWriteDispatcher) {
        // Гарантированное последовательное выполнение
        println("Запись: $data")
        delay(100)
    }

    // Случай использования 2: Модификация общего ресурса
    private val sharedResourceDispatcher = Dispatchers.IO.limitedParallelism(1)
    private var counter = 0

    suspend fun incrementCounter() = withContext(sharedResourceDispatcher) {
        // Нет гонок - последовательное выполнение
        val current = counter
        delay(10)
        counter = current + 1
    }
}
```

#### Управление жизненным циклом

```kotlin
import kotlinx.coroutines.*
import java.util.concurrent.Executors

class ManagedDispatcher : AutoCloseable {
    private val executor = Executors.newFixedThreadPool(4)
    val dispatcher = executor.asCoroutineDispatcher()

    override fun close() {
        println("Закрытие диспетчера...")
        dispatcher.close()
        executor.shutdown()
        if (!executor.awaitTermination(5, java.util.concurrent.TimeUnit.SECONDS)) {
            executor.shutdownNow()
        }
    }
}

// Использование с use() для автоматической очистки
suspend fun safeDispatcherUsage() {
    ManagedDispatcher().use { managed ->
        withContext(managed.dispatcher) {
            println("Выполнение работы...")
            delay(1000)
        }
    } // Автоматически закрыт
}
```

### Типичные ошибки

1. **Забыть закрыть ExecutorCoroutineDispatcher**
```kotlin
// Плохо - утечка потоков
fun leakyCode() = runBlocking {
    val executor = Executors.newFixedThreadPool(4)
    val dispatcher = executor.asCoroutineDispatcher()

    launch(dispatcher) {
        // работа
    }
    // Отсутствует: dispatcher.close() и executor.shutdown()
}
```

2. **Использование неправильного диспетчера для нагрузки**
```kotlin
// Плохо - CPU работа на IO диспетчере
suspend fun badChoice() = withContext(Dispatchers.IO) {
    // CPU-интенсивная работа (неправильный диспетчер!)
    (1..1_000_000).sum()
}

// Хорошо - CPU работа на Default диспетчере
suspend fun goodChoice() = withContext(Dispatchers.Default) {
    // CPU-интенсивная работа
    (1..1_000_000).sum()
}
```

### Резюме

**Кастомные диспетчеры** создаются используя `limitedParallelism()` (предпочтительно) или `asCoroutineDispatcher()` (для ExecutorService). Ключевые принципы:

- **limitedParallelism()**: Лёгкий, не создаёт новые потоки, рекомендуется
- **Размер пула потоков**: Ядра CPU для CPU работы, выше для I/O работы
- **Защита ресурсов**: Используйте ограниченный параллелизм (часто 1) для эксклюзивных ресурсов
- **Жизненный цикл**: Закрывайте ExecutorCoroutineDispatchers чтобы избежать утечек
- **Тестирование**: Используйте TestDispatcher для контролируемого выполнения

---

## Follow-ups

1. How does `limitedParallelism()` internally implement concurrency limiting without creating new threads? What synchronization primitives does it use?

2. Explain the trade-offs between using a single dispatcher with high parallelism vs multiple dispatchers with limited parallelism for different workload types.

3. How would you implement a custom dispatcher that supports dynamic parallelism adjustment based on system load?

4. What are the implications of using `Dispatchers.IO.limitedParallelism(1)` vs `Mutex` for serializing access to a shared resource?

5. How can you monitor and debug dispatcher usage in production? What metrics should you track?

6. Explain how `limitedParallelism()` interacts with `CoroutineStart.LAZY`. Does the parallelism limit apply before or after the coroutine starts?

7. How would you design a dispatcher pool that automatically scales based on queue depth and response time SLAs?

## References

- [Kotlin Coroutines Guide - Coroutine Context and Dispatchers](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)
- [limitedParallelism Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-coroutine-dispatcher/limited-parallelism.html)
- [ExecutorCoroutineDispatcher API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-executor-coroutine-dispatcher/)
- [Roman Elizarov - Explicit Concurrency](https://medium.com/@elizarov/explicit-concurrency-67a8e8fd9b25)
- [Dispatchers Migration Guide](https://github.com/Kotlin/kotlinx.coroutines/blob/master/docs/topics/migration.md)

## Related Questions

- [[q-deferred-async-patterns--kotlin--medium]] - Using async with custom dispatchers
- [[q-flowon-operator-context-switching--kotlin--hard]] - Context switching in flows
- [[q-testing-coroutine-timing-control--kotlin--medium]] - Testing with custom dispatchers
- [[q-coroutine-memory-leak-detection--kotlin--hard]] - Dispatcher lifecycle and leaks
- [[q-channel-buffer-strategies-comparison--kotlin--hard]] - Channel dispatchers

## Tags
#kotlin #coroutines #dispatchers #threading #performance #limitedparallelism #custom-dispatchers #resource-management

