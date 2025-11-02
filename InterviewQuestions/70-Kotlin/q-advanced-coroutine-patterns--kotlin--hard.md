---
id: kotlin-133
title: "Advanced Coroutine Patterns / Продвинутые паттерны корутин"
aliases: []

# Classification
topic: kotlin
subtopics:
  - coroutines
  - patterns
  - pipeline
  - producer-consumer
  - resource-pooling
question_kind: theory
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive guide on advanced Kotlin Coroutine patterns

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-actor-pattern--kotlin--hard, q-fan-in-fan-out--kotlin--hard, q-structured-concurrency--kotlin--hard]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [kotlin, coroutines, patterns, pipeline, producer-consumer, semaphore, mutex, difficulty/hard]
---
# Question (EN)
> What are advanced coroutine patterns in Kotlin? Explain pipeline pattern, producer-consumer with multiple stages, resource pooling with Mutex/Semaphore, custom scope builders, and rate limiting patterns.

# Вопрос (RU)
> Что такое продвинутые паттерны корутин в Kotlin? Объясните паттерн pipeline, producer-consumer с несколькими стадиями, пулинг ресурсов с Mutex/Semaphore, кастомные scope builders и паттерны rate limiting.

---

## Answer (EN)

Advanced coroutine patterns enable sophisticated concurrent programming scenarios while maintaining code clarity and safety. These patterns build upon basic coroutine concepts to solve complex real-world problems.

### Pipeline Pattern

The pipeline pattern chains multiple processing stages where each stage consumes from the previous and produces for the next.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

// Pipeline: numbers -> squares -> strings
fun CoroutineScope.produceNumbers() = produce {
    var x = 1
    while (true) {
        send(x++)
        delay(100)
    }
}

fun CoroutineScope.square(numbers: ReceiveChannel<Int>) = produce {
    for (x in numbers) {
        send(x * x)
    }
}

fun CoroutineScope.toString(numbers: ReceiveChannel<Int>) = produce {
    for (x in numbers) {
        send("Number: $x")
    }
}

suspend fun main() = coroutineScope {
    val numbers = produceNumbers()
    val squares = square(numbers)
    val strings = toString(squares)

    repeat(5) {
        println(strings.receive())
    }

    coroutineContext.cancelChildren()
}
```

**Real-world pipeline: Image processing**

```kotlin
data class Image(val id: Int, val data: ByteArray, val metadata: Map<String, String> = emptyMap())

// Stage 1: Load images from disk
fun CoroutineScope.loadImages(paths: List<String>) = produce {
    for ((index, path) in paths.withIndex()) {
        delay(50) // Simulate I/O
        val data = ByteArray(1024) // Simulate loaded data
        send(Image(index, data))
    }
}

// Stage 2: Resize images
fun CoroutineScope.resizeImages(
    images: ReceiveChannel<Image>,
    targetSize: Int
) = produce {
    for (image in images) {
        delay(100) // Simulate resizing
        val resized = image.copy(
            data = image.data.copyOf(targetSize),
            metadata = image.metadata + ("size" to "$targetSize")
        )
        send(resized)
    }
}

// Stage 3: Apply filters
fun CoroutineScope.applyFilters(images: ReceiveChannel<Image>) = produce {
    for (image in images) {
        delay(80) // Simulate filter processing
        val filtered = image.copy(
            metadata = image.metadata + ("filtered" to "true")
        )
        send(filtered)
    }
}

// Stage 4: Save to disk
suspend fun saveImages(images: ReceiveChannel<Image>, outputDir: String) {
    for (image in images) {
        delay(50) // Simulate disk I/O
        println("Saved image ${image.id} to $outputDir with metadata: ${image.metadata}")
    }
}

// Usage
suspend fun main() = coroutineScope {
    val paths = List(10) { "image_$it.jpg" }

    val loaded = loadImages(paths)
    val resized = resizeImages(loaded, 800)
    val filtered = applyFilters(resized)

    saveImages(filtered, "/output")
}
```

### Producer-Consumer with Multiple Stages

```kotlin
// Multi-stage producer-consumer for data processing

data class RawData(val id: Int, val content: String)
data class ProcessedData(val id: Int, val processed: String, val timestamp: Long)
data class EnrichedData(val id: Int, val final: String, val metadata: Map<String, Any>)

class DataPipeline(private val scope: CoroutineScope) {

    // Stage 1: Fetch raw data
    private fun produceRawData(count: Int) = scope.produce {
        repeat(count) { i ->
            delay(50)
            send(RawData(i, "raw_$i"))
        }
    }

    // Stage 2: Process data (multiple workers)
    private fun processData(
        rawChannel: ReceiveChannel<RawData>,
        workers: Int = 3
    ) = scope.produce {
        repeat(workers) { workerId ->
            launch {
                for (raw in rawChannel) {
                    delay(100) // Simulate processing
                    val processed = ProcessedData(
                        id = raw.id,
                        processed = raw.content.uppercase(),
                        timestamp = System.currentTimeMillis()
                    )
                    send(processed)
                    println("Worker $workerId processed item ${raw.id}")
                }
            }
        }
    }

    // Stage 3: Enrich data
    private fun enrichData(
        processedChannel: ReceiveChannel<ProcessedData>
    ) = scope.produce {
        for (processed in processedChannel) {
            delay(80) // Simulate enrichment
            val enriched = EnrichedData(
                id = processed.id,
                final = "${processed.processed}_enriched",
                metadata = mapOf(
                    "timestamp" to processed.timestamp,
                    "enriched_at" to System.currentTimeMillis()
                )
            )
            send(enriched)
        }
    }

    // Stage 4: Save to database (batch processing)
    private suspend fun saveToDatabase(
        enrichedChannel: ReceiveChannel<EnrichedData>,
        batchSize: Int = 5
    ) {
        val batch = mutableListOf<EnrichedData>()

        for (enriched in enrichedChannel) {
            batch.add(enriched)

            if (batch.size >= batchSize) {
                saveBatch(batch.toList())
                batch.clear()
            }
        }

        // Save remaining items
        if (batch.isNotEmpty()) {
            saveBatch(batch)
        }
    }

    private suspend fun saveBatch(items: List<EnrichedData>) {
        delay(100) // Simulate database write
        println("Saved batch of ${items.size} items: ${items.map { it.id }}")
    }

    suspend fun execute(count: Int) {
        val raw = produceRawData(count)
        val processed = processData(raw, workers = 3)
        val enriched = enrichData(processed)
        saveToDatabase(enriched, batchSize = 5)
    }
}

// Usage
suspend fun main() = coroutineScope {
    val pipeline = DataPipeline(this)
    pipeline.execute(20)
}
```

### Resource Pooling with Semaphore

```kotlin
import kotlinx.coroutines.sync.Semaphore

// Database connection pool
class DatabaseConnection(val id: Int) {
    suspend fun query(sql: String): List<String> {
        delay(100) // Simulate query
        return listOf("Result from connection $id")
    }
}

class ConnectionPool(private val size: Int) {
    private val connections = List(size) { DatabaseConnection(it) }
    private val semaphore = Semaphore(size)
    private val available = ArrayDeque(connections)

    suspend fun <T> withConnection(block: suspend (DatabaseConnection) -> T): T {
        semaphore.acquire()
        val connection = synchronized(available) {
            available.removeFirst()
        }

        return try {
            block(connection)
        } finally {
            synchronized(available) {
                available.addLast(connection)
            }
            semaphore.release()
        }
    }
}

// Usage
suspend fun main() = coroutineScope {
    val pool = ConnectionPool(size = 3)

    // Launch 10 concurrent queries
    val jobs = List(10) { i ->
        async {
            pool.withConnection { conn ->
                println("Query $i using connection ${conn.id}")
                conn.query("SELECT * FROM users WHERE id = $i")
            }
        }
    }

    jobs.awaitAll().forEach { println(it) }
}
```

**Advanced resource pool with metrics**

```kotlin
class AdvancedConnectionPool(private val size: Int) {
    private val connections = List(size) { DatabaseConnection(it) }
    private val semaphore = Semaphore(size)
    private val available = ArrayDeque(connections)

    // Metrics
    private var totalAcquisitions = 0
    private var totalWaitTime = 0L
    private val activeBorrows = mutableMapOf<Int, Long>()

    suspend fun <T> withConnection(block: suspend (DatabaseConnection) -> T): T {
        val startWait = System.currentTimeMillis()
        semaphore.acquire()
        val waitTime = System.currentTimeMillis() - startWait

        val connection = synchronized(available) {
            totalAcquisitions++
            totalWaitTime += waitTime
            val conn = available.removeFirst()
            activeBorrows[conn.id] = System.currentTimeMillis()
            conn
        }

        println("Acquired connection ${connection.id} after waiting ${waitTime}ms")

        return try {
            block(connection)
        } finally {
            synchronized(available) {
                activeBorrows.remove(connection.id)
                available.addLast(connection)
            }
            semaphore.release()
        }
    }

    fun getMetrics(): PoolMetrics {
        synchronized(available) {
            return PoolMetrics(
                totalSize = size,
                available = available.size,
                inUse = size - available.size,
                totalAcquisitions = totalAcquisitions,
                averageWaitTime = if (totalAcquisitions > 0) totalWaitTime / totalAcquisitions else 0
            )
        }
    }
}

data class PoolMetrics(
    val totalSize: Int,
    val available: Int,
    val inUse: Int,
    val totalAcquisitions: Int,
    val averageWaitTime: Long
)
```

### Resource Pooling with Mutex

```kotlin
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

// Thread-safe resource manager
class ResourceManager<T>(
    private val create: () -> T,
    private val destroy: (T) -> Unit = {}
) {
    private val resources = mutableListOf<T>()
    private val mutex = Mutex()

    suspend fun acquire(): T = mutex.withLock {
        if (resources.isEmpty()) {
            create()
        } else {
            resources.removeAt(0)
        }
    }

    suspend fun release(resource: T) = mutex.withLock {
        resources.add(resource)
    }

    suspend fun <R> withResource(block: suspend (T) -> R): R {
        val resource = acquire()
        return try {
            block(resource)
        } finally {
            release(resource)
        }
    }

    suspend fun clear() = mutex.withLock {
        resources.forEach { destroy(it) }
        resources.clear()
    }
}

// Usage: HTTP client pool
data class HttpClient(val id: Int)

suspend fun main() = coroutineScope {
    val clientPool = ResourceManager(
        create = { HttpClient((0..1000).random()) },
        destroy = { println("Destroying client ${it.id}") }
    )

    val jobs = List(5) { i ->
        async {
            clientPool.withResource { client ->
                println("Request $i using client ${client.id}")
                delay(100)
                "Response $i"
            }
        }
    }

    jobs.awaitAll().forEach { println(it) }
    clientPool.clear()
}
```

### Rate Limiting Pattern

```kotlin
import kotlinx.coroutines.sync.Semaphore
import kotlin.time.Duration
import kotlin.time.Duration.Companion.seconds

// Token bucket rate limiter
class RateLimiter(
    private val maxRequests: Int,
    private val window: Duration
) {
    private val semaphore = Semaphore(maxRequests)

    suspend fun <T> execute(block: suspend () -> T): T {
        semaphore.acquire()

        // Release permit after window duration
        CoroutineScope(Dispatchers.Default).launch {
            delay(window)
            semaphore.release()
        }

        return block()
    }
}

// Usage
suspend fun main() = coroutineScope {
    val rateLimiter = RateLimiter(maxRequests = 3, window = 1.seconds)

    val jobs = List(10) { i ->
        async {
            val start = System.currentTimeMillis()
            rateLimiter.execute {
                val elapsed = System.currentTimeMillis() - start
                println("Request $i executed after ${elapsed}ms")
                delay(100)
            }
        }
    }

    jobs.awaitAll()
}
```

**Advanced rate limiter with sliding window**

```kotlin
class SlidingWindowRateLimiter(
    private val maxRequests: Int,
    private val windowMillis: Long
) {
    private val timestamps = mutableListOf<Long>()
    private val mutex = Mutex()

    suspend fun tryAcquire(): Boolean = mutex.withLock {
        val now = System.currentTimeMillis()

        // Remove old timestamps outside the window
        timestamps.removeIf { it < now - windowMillis }

        if (timestamps.size < maxRequests) {
            timestamps.add(now)
            true
        } else {
            false
        }
    }

    suspend fun acquire() {
        while (!tryAcquire()) {
            delay(10)
        }
    }

    suspend fun <T> execute(block: suspend () -> T): T {
        acquire()
        return block()
    }
}

// Usage
suspend fun main() = coroutineScope {
    val rateLimiter = SlidingWindowRateLimiter(
        maxRequests = 5,
        windowMillis = 1000
    )

    repeat(10) { i ->
        launch {
            val allowed = rateLimiter.tryAcquire()
            println("Request $i: ${if (allowed) "ALLOWED" else "DENIED"}")
        }
    }

    delay(1100) // Wait for window to pass

    repeat(5) { i ->
        launch {
            val allowed = rateLimiter.tryAcquire()
            println("Request ${i + 10}: ${if (allowed) "ALLOWED" else "DENIED"}")
        }
    }
}
```

### Custom Scope Builders

```kotlin
// Custom scope for retry logic
suspend fun <T> retryScope(
    times: Int = 3,
    delayMillis: Long = 1000,
    block: suspend CoroutineScope.() -> T
): T {
    repeat(times - 1) { attempt ->
        try {
            return coroutineScope { block() }
        } catch (e: Exception) {
            println("Attempt ${attempt + 1} failed: ${e.message}")
            delay(delayMillis * (attempt + 1))
        }
    }

    // Last attempt - throw exception if fails
    return coroutineScope { block() }
}

// Usage
suspend fun main() {
    try {
        retryScope(times = 3, delayMillis = 500) {
            println("Attempting operation...")
            if (Random.nextBoolean()) {
                throw Exception("Random failure")
            }
            "Success"
        }
    } catch (e: Exception) {
        println("All attempts failed")
    }
}
```

**Custom timeout scope**

```kotlin
suspend fun <T> timeoutScope(
    timeoutMillis: Long,
    onTimeout: () -> T,
    block: suspend CoroutineScope.() -> T
): T {
    return try {
        withTimeout(timeoutMillis) {
            block()
        }
    } catch (e: TimeoutCancellationException) {
        println("Operation timed out after ${timeoutMillis}ms")
        onTimeout()
    }
}

// Usage
suspend fun main() {
    val result = timeoutScope(
        timeoutMillis = 1000,
        onTimeout = { "Default value" }
    ) {
        delay(2000)
        "Completed"
    }

    println("Result: $result")  // "Default value"
}
```

**Custom parallel scope**

```kotlin
suspend fun <T, R> List<T>.parallelMap(
    concurrency: Int = 10,
    transform: suspend (T) -> R
): List<R> = coroutineScope {
    val semaphore = Semaphore(concurrency)

    map { item ->
        async {
            semaphore.acquire()
            try {
                transform(item)
            } finally {
                semaphore.release()
            }
        }
    }.awaitAll()
}

// Usage
suspend fun main() {
    val numbers = (1..100).toList()

    val results = numbers.parallelMap(concurrency = 5) { number ->
        delay(100)
        number * 2
    }

    println("Processed ${results.size} items")
}
```

### Circuit Breaker Pattern

```kotlin
sealed class CircuitState {
    object Closed : CircuitState()
    data class Open(val openedAt: Long) : CircuitState()
    object HalfOpen : CircuitState()
}

class CircuitBreaker(
    private val failureThreshold: Int = 5,
    private val timeoutMillis: Long = 60000,
    private val halfOpenTimeout: Long = 5000
) {
    private var state: CircuitState = CircuitState.Closed
    private var failureCount = 0
    private val mutex = Mutex()

    suspend fun <T> execute(block: suspend () -> T): T = mutex.withLock {
        when (val currentState = state) {
            is CircuitState.Closed -> {
                try {
                    val result = block()
                    failureCount = 0
                    result
                } catch (e: Exception) {
                    failureCount++
                    if (failureCount >= failureThreshold) {
                        state = CircuitState.Open(System.currentTimeMillis())
                        println("Circuit opened due to failures")
                    }
                    throw e
                }
            }

            is CircuitState.Open -> {
                val elapsed = System.currentTimeMillis() - currentState.openedAt
                if (elapsed >= timeoutMillis) {
                    state = CircuitState.HalfOpen
                    println("Circuit half-open, testing...")
                    execute(block)
                } else {
                    throw Exception("Circuit is open, request rejected")
                }
            }

            is CircuitState.HalfOpen -> {
                try {
                    val result = block()
                    state = CircuitState.Closed
                    failureCount = 0
                    println("Circuit closed, service recovered")
                    result
                } catch (e: Exception) {
                    state = CircuitState.Open(System.currentTimeMillis())
                    println("Circuit reopened, service still failing")
                    throw e
                }
            }
        }
    }
}

// Usage
suspend fun main() = coroutineScope {
    val circuit = CircuitBreaker(failureThreshold = 3, timeoutMillis = 2000)

    repeat(10) { i ->
        launch {
            delay(i * 100L)
            try {
                circuit.execute {
                    if (i < 5) throw Exception("Service failure")
                    "Success"
                }
                println("Request $i: SUCCESS")
            } catch (e: Exception) {
                println("Request $i: FAILED - ${e.message}")
            }
        }
    }
}
```

### Bulkhead Pattern

```kotlin
// Isolate resources between different operations
class Bulkhead(private val maxConcurrent: Int) {
    private val semaphore = Semaphore(maxConcurrent)
    private var activeCount = 0
    private var rejectedCount = 0

    suspend fun <T> execute(block: suspend () -> T): T {
        if (!semaphore.tryAcquire()) {
            rejectedCount++
            throw Exception("Bulkhead full, request rejected")
        }

        activeCount++
        return try {
            block()
        } finally {
            activeCount--
            semaphore.release()
        }
    }

    fun getMetrics() = "Active: $activeCount, Rejected: $rejectedCount"
}

class BulkheadManager {
    private val readBulkhead = Bulkhead(maxConcurrent = 10)
    private val writeBulkhead = Bulkhead(maxConcurrent = 5)
    private val heavyBulkhead = Bulkhead(maxConcurrent = 2)

    suspend fun readOperation() = readBulkhead.execute {
        delay(100)
        "Read result"
    }

    suspend fun writeOperation() = writeBulkhead.execute {
        delay(200)
        "Write result"
    }

    suspend fun heavyOperation() = heavyBulkhead.execute {
        delay(1000)
        "Heavy result"
    }

    fun getMetrics() = """
        Read: ${readBulkhead.getMetrics()}
        Write: ${writeBulkhead.getMetrics()}
        Heavy: ${heavyBulkhead.getMetrics()}
    """.trimIndent()
}

// Usage
suspend fun main() = coroutineScope {
    val manager = BulkheadManager()

    // Launch many operations
    val jobs = List(30) { i ->
        async {
            try {
                when (i % 3) {
                    0 -> manager.readOperation()
                    1 -> manager.writeOperation()
                    else -> manager.heavyOperation()
                }
            } catch (e: Exception) {
                "REJECTED"
            }
        }
    }

    jobs.awaitAll()
    println(manager.getMetrics())
}
```

### Best Practices

#### DO:

```kotlin
// Use pipeline for sequential stages
val stage1 = produceData()
val stage2 = transformData(stage1)
val stage3 = saveData(stage2)

// Use semaphore for resource limits
val semaphore = Semaphore(10)
semaphore.withPermit { /* operation */ }

// Use custom scopes for reusable patterns
suspend fun <T> retryScope(times: Int, block: suspend () -> T): T

// Use circuit breaker for fault tolerance
val circuit = CircuitBreaker()
circuit.execute { apiCall() }
```

#### DON'T:

```kotlin
// Don't create unbounded channels
val channel = Channel<Int>(Channel.UNLIMITED)  // Can cause OOM

// Don't ignore cancellation
try {
    operation()
} catch (e: Exception) {
    // Don't catch CancellationException!
}

// Don't forget to close channels
val channel = produce { /* ... */ }
// Always close or cancel when done

// Don't block in coroutines
GlobalScope.launch {
    Thread.sleep(1000)  // Bad! Use delay()
}
```

---

## Ответ (RU)

Продвинутые паттерны корутин позволяют решать сложные задачи параллельного программирования, сохраняя при этом чистоту и безопасность кода.

### Паттерн Pipeline

Паттерн pipeline связывает несколько стадий обработки, где каждая стадия потребляет из предыдущей и производит для следующей.

```kotlin
// Pipeline: числа -> квадраты -> строки
fun CoroutineScope.produceNumbers() = produce {
    var x = 1
    while (true) {
        send(x++)
        delay(100)
    }
}

fun CoroutineScope.square(numbers: ReceiveChannel<Int>) = produce {
    for (x in numbers) {
        send(x * x)
    }
}
```

### Пулинг ресурсов с Semaphore

```kotlin
class ConnectionPool(private val size: Int) {
    private val connections = List(size) { DatabaseConnection(it) }
    private val semaphore = Semaphore(size)

    suspend fun <T> withConnection(block: suspend (DatabaseConnection) -> T): T {
        semaphore.acquire()
        val connection = getConnection()

        return try {
            block(connection)
        } finally {
            releaseConnection(connection)
            semaphore.release()
        }
    }
}
```

### Rate Limiting

```kotlin
class RateLimiter(
    private val maxRequests: Int,
    private val window: Duration
) {
    private val semaphore = Semaphore(maxRequests)

    suspend fun <T> execute(block: suspend () -> T): T {
        semaphore.acquire()

        CoroutineScope(Dispatchers.Default).launch {
            delay(window)
            semaphore.release()
        }

        return block()
    }
}
```

### Лучшие практики

#### ДЕЛАТЬ:

```kotlin
// Использовать pipeline для последовательных стадий
val stage1 = produceData()
val stage2 = transformData(stage1)

// Использовать semaphore для ограничения ресурсов
val semaphore = Semaphore(10)

// Использовать кастомные скоупы для переиспользуемых паттернов
suspend fun <T> retryScope(times: Int, block: suspend () -> T): T
```

#### НЕ ДЕЛАТЬ:

```kotlin
// Не создавать неограниченные каналы
val channel = Channel<Int>(Channel.UNLIMITED)  // Может вызвать OOM

// Не блокировать в корутинах
GlobalScope.launch {
    Thread.sleep(1000)  // Плохо! Используйте delay()
}
```

---

## References

- [Kotlin Coroutines Guide](https://kotlinlang.org/docs/coroutines-guide.html)
- [Channels Documentation](https://kotlinlang.org/docs/channels.html)
- [Shared Mutable State and Concurrency](https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html)
- [Coroutine Context and Dispatchers](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)

## Related Questions

### Related (Hard)
- [[q-coroutine-profiling--kotlin--hard]] - Coroutines
- [[q-coroutine-performance-optimization--kotlin--hard]] - Coroutines
- [[q-coroutine-memory-leaks--kotlin--hard]] - Coroutines
- [[q-flow-performance--kotlin--hard]] - Coroutines

### Prerequisites (Easier)
- [[q-flow-combining-zip-combine--kotlin--medium]] - Coroutines
- [[q-what-is-coroutine--kotlin--easy]] - Coroutines
- [[q-coroutine-builders-basics--kotlin--easy]] - Coroutines

### Hub
- [[q-kotlin-coroutines-introduction--kotlin--medium]] - Comprehensive coroutines introduction

## MOC Links

- [[moc-kotlin]]
