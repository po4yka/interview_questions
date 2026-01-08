---\
id: kotlin-133
title: "Advanced Coroutine Patterns / Продвинутые паттерны корутин"
aliases: ["Advanced Coroutine Patterns", "Продвинутые паттерны корутин"]

# Classification
topic: kotlin
subtopics: [coroutines, pipeline, producer-consumer]
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
related: [c-coroutines, c-kotlin, q-actor-pattern--kotlin--hard]

# Timestamps
created: 2025-10-12
updated: 2025-11-10

tags: [coroutines, difficulty/hard, kotlin, mutex, patterns, pipeline, producer-consumer, semaphore]
---\
# Вопрос (RU)
> Что такое продвинутые паттерны корутин в Kotlin? Объясните паттерн pipeline, producer-consumer с несколькими стадиями, пулинг ресурсов с Mutex/Semaphore, кастомные scope builders и паттерны rate limiting.

---

# Question (EN)
> What are advanced coroutine patterns in Kotlin? Explain pipeline pattern, producer-consumer with multiple stages, resource pooling with Mutex/Semaphore, custom scope builders, and rate limiting patterns.

## Ответ (RU)

Продвинутые паттерны корутин позволяют решать сложные задачи конкурентного и асинхронного программирования, сохраняя при этом читаемость, безопасность и принципы структурированной конкуренции.

Ниже приведены ключевые паттерны с примерами, концептуально согласованные с EN-версией.

### Паттерн Pipeline

Паттерн pipeline связывает несколько стадий обработки, где каждая стадия:
- читает данные из предыдущего канала,
- обрабатывает их,
- отправляет результат в следующий канал.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

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

fun CoroutineScope.toStringChannel(numbers: ReceiveChannel<Int>) = produce {
    for (x in numbers) {
        send("Number: $x")
    }
}

suspend fun pipelineExample() = coroutineScope {
    val numbers = produceNumbers()
    val squares = square(numbers)
    val strings = toStringChannel(squares)

    repeat(5) {
        println(strings.receive())
    }

    coroutineContext.cancelChildren() // корректно завершаем pipeline и освобождаем ресурсы
}
```

Ключевые моменты:
- использовать `CoroutineScope.produce` и `ReceiveChannel` для композиции стадий;
- обязательно отменять/закрывать каналы, когда результат больше не нужен, чтобы избежать утечек;
- стадии должны уважать отмену (`for (x in channel)` корректно завершится после `cancel`).

### Producer-Consumer С Несколькими Стадиями

Многостадийный producer-consumer — это частный случай pipeline, где между стадиями могут быть несколько воркеров.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

data class RawData(val id: Int, val content: String)
data class ProcessedData(val id: Int, val processed: String, val timestamp: Long)
data class EnrichedData(val id: Int, val final: String, val metadata: Map<String, Any>)

class DataPipeline(private val scope: CoroutineScope) {

    // Stage 1: источник сырых данных
    private fun produceRawData(count: Int) = scope.produce {
        repeat(count) { i ->
            delay(50)
            send(RawData(i, "raw_$i"))
        }
        // produce автоматически закроет канал по завершении блока
    }

    // Stage 2: обработка с несколькими воркерами
    private fun processData(
        rawChannel: ReceiveChannel<RawData>,
        workers: Int = 3
    ): ReceiveChannel<ProcessedData> {
        val out = Channel<ProcessedData>()

        repeat(workers) { workerId ->
            scope.launch {
                for (raw in rawChannel) {
                    delay(100)
                    val processed = ProcessedData(
                        id = raw.id,
                        processed = raw.content.uppercase(),
                        timestamp = System.currentTimeMillis()
                    )
                    out.send(processed)
                    println("Worker $workerId processed item ${raw.id}")
                }
            }
        }

        scope.launch {
            // Пример корректного закрытия out после завершения всех воркеров
            // и исчерпания rawChannel.
            // Здесь можно использовать join на запущенных job'ах.
            // Для краткости оставлено как комментарий, так как точная
            // реализация зависит от требований.
        }

        return out
    }

    // Stage 3: обогащение
    private fun enrichData(
        processedChannel: ReceiveChannel<ProcessedData>
    ) = scope.produce {
        for (processed in processedChannel) {
            delay(80)
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

    // Stage 4: сохранение батчами (упрощённый пример)
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
        if (batch.isNotEmpty()) {
            saveBatch(batch)
        }
    }

    private suspend fun saveBatch(items: List<EnrichedData>) {
        delay(100)
        println("Saved batch of ${items.size} items: ${items.map { it.id }}")
    }

    suspend fun execute(count: Int) {
        val raw = produceRawData(count)
        val processed = processData(raw, workers = 3)
        val enriched = enrichData(processed)
        saveToDatabase(enriched, batchSize = 5)
    }
}
```

Идея: использовать каналы для связывания стадий и `launch` для параллельных воркеров. Для production-кода важно корректно закрывать `out` и не допускать зависания потребителей.

### Пулинг Ресурсов С Semaphore

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit

class DatabaseConnection(val id: Int) {
    suspend fun query(sql: String): List<String> {
        delay(100)
        return listOf("Result from connection $id")
    }
}

class ConnectionPool(private val size: Int) {
    private val connections = List(size) { DatabaseConnection(it) }
    private val semaphore = Semaphore(size)
    private val available = ArrayDeque(connections)

    suspend fun <T> withConnection(block: suspend (DatabaseConnection) -> T): T =
        semaphore.withPermit {
            val connection = synchronized(available) {
                require(available.isNotEmpty())
                available.removeFirst()
            }
            try {
                block(connection)
            } finally {
                synchronized(available) {
                    available.addLast(connection)
                }
            }
        }
}
```

Идея: `Semaphore` ограничивает одновременное количество пользователей ресурса; очередь ресурсов защищена синхронизацией (в реальных приложениях обычно используют неблокирующие структуры или отдельный мьютекс).

### Пулинг Ресурсов С Mutex

```kotlin
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

class ResourceManager<T>(
    private val create: () -> T,
    private val destroy: (T) -> Unit = {}
) {
    private val resources = mutableListOf<T>()
    private val mutex = Mutex()

    suspend fun acquire(): T = mutex.withLock {
        if (resources.isEmpty()) create() else resources.removeAt(0)
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
```

Mutex защищает структуру данных пула; `Semaphore` ограничивает конкуренцию по числу пользователей.

### Rate Limiting (ограничение частоты)

Упрощённый token-bucket через `Semaphore` (для демонстрации, без гарантии строгой структурированной конкуренции):

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Semaphore
import kotlin.time.Duration

class RateLimiter(
    private val maxRequests: Int,
    private val window: Duration,
    private val scope: CoroutineScope
) {
    private val semaphore = Semaphore(maxRequests)

    suspend fun <T> execute(block: suspend () -> T): T {
        semaphore.acquire()

        // Планируем возврат токена через окно; важно, чтобы переданный scope
        // имел корректный жизненный цикл, иначе возможны утечки.
        scope.launch {
            delay(window)
            semaphore.release()
        }

        return block()
    }
}
```

Замечание: в продакшене важно выбирать scope так, чтобы фоновые задачки на release
не терялись при отмене/завершении, и учитывать, что при ошибках `block` токен
всё равно будет возвращён по таймеру.

Скользящее окно через `Mutex`:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

class SlidingWindowRateLimiter(
    private val maxRequests: Int,
    private val windowMillis: Long
) {
    private val timestamps = mutableListOf<Long>()
    private val mutex = Mutex()

    suspend fun tryAcquire(): Boolean = mutex.withLock {
        val now = System.currentTimeMillis()
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
```

### Кастомные Scope Builders

```kotlin
import kotlinx.coroutines.*

suspend fun <T> retryScope(
    times: Int = 3,
    delayMillis: Long = 1000,
    block: suspend CoroutineScope.() -> T
): T {
    require(times >= 1)
    repeat(times - 1) { attempt ->
        try {
            return coroutineScope { block() }
        } catch (e: Exception) {
            if (e is CancellationException) throw e
            println("Attempt ${attempt + 1} failed: ${e.message}")
            delay(delayMillis * (attempt + 1))
        }
    }
    return coroutineScope { block() }
}
```

Обертка с таймаутом:

```kotlin
import kotlinx.coroutines.*

suspend fun <T> timeoutScope(
    timeoutMillis: Long,
    onTimeout: () -> T,
    block: suspend CoroutineScope.() -> T
): T {
    return try {
        withTimeout(timeoutMillis) { block() }
    } catch (e: TimeoutCancellationException) {
        println("Operation timed out after ${timeoutMillis}ms")
        onTimeout()
    }
}
```

Параллельная обработка с ограничением конкуренции:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit

suspend fun <T, R> List<T>.parallelMap(
    concurrency: Int = 10,
    transform: suspend (T) -> R
): List<R> = coroutineScope {
    val semaphore = Semaphore(concurrency)
    map { item ->
        async {
            semaphore.withPermit {
                transform(item)
            }
        }
    }.awaitAll()
}
```

Ключевая идея: инкапсулировать повтор, таймаут, параллелизм и др. в переиспользуемые билдеры, сохраняя структурированную конкуренцию.

### Circuit Breaker (предохранитель)

```kotlin
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

sealed class CircuitState {
    object Closed : CircuitState()
    data class Open(val openedAt: Long) : CircuitState()
    object HalfOpen : CircuitState()
}

class CircuitBreaker(
    private val failureThreshold: Int = 5,
    private val timeoutMillis: Long = 60000
) {
    private var state: CircuitState = CircuitState.Closed
    private var failureCount = 0
    private val mutex = Mutex()

    suspend fun <T> execute(block: suspend () -> T): T {
        // Быстрая проверка состояния + обновление под мьютексом.
        return when (val currentState = mutex.withLock { state }) {
            is CircuitState.Closed -> runClosed(block)
            is CircuitState.Open -> runOpen(currentState, block)
            is CircuitState.HalfOpen -> runHalfOpen(block)
        }
    }

    private suspend fun <T> runClosed(block: suspend () -> T): T =
        try {
            val result = block()
            mutex.withLock { failureCount = 0 }
            result
        } catch (e: Exception) {
            mutex.withLock {
                if (++failureCount >= failureThreshold) {
                    state = CircuitState.Open(System.currentTimeMillis())
                    println("Circuit opened")
                }
            }
            throw e
        }

    private suspend fun <T> runOpen(current: CircuitState.Open, block: suspend () -> T): T {
        val now = System.currentTimeMillis()
        return if (now - current.openedAt >= timeoutMillis) {
            mutex.withLock { state = CircuitState.HalfOpen }
            runHalfOpen(block)
        } else {
            throw Exception("Circuit is open, request rejected")
        }
    }

    private suspend fun <T> runHalfOpen(block: suspend () -> T): T =
        try {
            val result = block()
            mutex.withLock {
                state = CircuitState.Closed
                failureCount = 0
                println("Circuit closed")
            }
            result
        } catch (e: Exception) {
            mutex.withLock {
                state = CircuitState.Open(System.currentTimeMillis())
                println("Circuit reopened")
            }
            throw e
        }
}
```

Комментарий: здесь только операции над состоянием защищены `Mutex`, выполнение `block` не держит мьютекс и не блокирует конкуренцию.

### Bulkhead Pattern (отсекание)

```kotlin
import kotlinx.coroutines.sync.Semaphore
import java.util.concurrent.atomic.AtomicInteger

class Bulkhead(private val maxConcurrent: Int) {
    private val semaphore = Semaphore(maxConcurrent)
    private val activeCount = AtomicInteger(0)
    private val rejectedCount = AtomicInteger(0)

    suspend fun <T> execute(block: suspend () -> T): T {
        if (!semaphore.tryAcquire()) {
            rejectedCount.incrementAndGet()
            throw Exception("Bulkhead full, request rejected")
        }
        activeCount.incrementAndGet()
        return try {
            block()
        } finally {
            activeCount.decrementAndGet()
            semaphore.release()
        }
    }

    fun getMetrics() = "Active: ${activeCount.get()}, Rejected: ${rejectedCount.get()}"
}
```

Идея: разделять ресурсы по типам нагрузки и ограничивать конкуренцию для каждой группы отдельно (часто с немедленным отказом) — пример демонстрационный.

### Лучшие Практики (RU)

#### ДЕЛАТЬ:

```kotlin
// Использовать pipeline для последовательных стадий
val stage1 = produceData()
val stage2 = transformData(stage1)
val stage3 = saveData(stage2)

// Использовать Semaphore для ограничения параллелизма
val semaphore = Semaphore(10)
semaphore.withPermit { /* operation */ }

// Использовать кастомные scope builders для повторяемых шаблонов
suspend fun <T> retryScope(times: Int, block: suspend () -> T): T

// Использовать circuit breaker для отказоустойчивости
val circuit = CircuitBreaker()
circuit.execute { apiCall() }
```

#### НЕ ДЕЛАТЬ:

```kotlin
// Не создавать неограниченные каналы без необходимости
val channel = Channel<Int>(Channel.UNLIMITED)  // Может вызвать OOM

// Не игнорировать отмену
try {
    operation()
} catch (e: Exception) {
    // Не гасите CancellationException без повторного выброса
}

// Не забывать закрывать/отменять каналы
val channel = produce { /* ... */ }
// После использования — channel.cancel() / close()

// Не блокировать потоки внутри корутин
GlobalScope.launch {
    Thread.sleep(1000)  // Плохо! Используйте delay()
}
```

---

## Answer (EN)

Advanced coroutine patterns enable sophisticated concurrent and asynchronous programming while preserving clarity, safety, and structured concurrency principles.

Below are key patterns with examples.

### Pipeline Pattern

The pipeline pattern chains multiple processing stages, where each stage:
- consumes from the previous channel,
- transforms data,
- produces to the next channel.

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

fun CoroutineScope.toStringChannel(numbers: ReceiveChannel<Int>) = produce {
    for (x in numbers) {
        send("Number: $x")
    }
}

suspend fun pipelineExample() = coroutineScope {
    val numbers = produceNumbers()
    val squares = square(numbers)
    val strings = toStringChannel(squares)

    repeat(5) {
        println(strings.receive())
    }

    coroutineContext.cancelChildren() // cancel the pipeline and free resources when done
}
```

Key points:
- use `produce`/`ReceiveChannel` to compose stages;
- always cancel/close channels when you no longer need results to avoid leaks;
- stages should be cancellation-cooperative (`for (x in channel)` terminates on cancel).

### Producer-Consumer with Multiple Stages

A multi-stage producer-consumer setup is a specialized pipeline where some stages have multiple workers.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

data class RawData(val id: Int, val content: String)
data class ProcessedData(val id: Int, val processed: String, val timestamp: Long)
data class EnrichedData(val id: Int, val final: String, val metadata: Map<String, Any>)

class DataPipeline(private val scope: CoroutineScope) {

    // Stage 1: raw data source
    private fun produceRawData(count: Int) = scope.produce {
        repeat(count) { i ->
            delay(50)
            send(RawData(i, "raw_$i"))
        }
        // produce will close the channel when this block completes
    }

    // Stage 2: processing with multiple workers
    private fun processData(
        rawChannel: ReceiveChannel<RawData>,
        workers: Int = 3
    ): ReceiveChannel<ProcessedData> {
        val out = Channel<ProcessedData>()

        repeat(workers) { workerId ->
            scope.launch {
                for (raw in rawChannel) {
                    delay(100)
                    val processed = ProcessedData(
                        id = raw.id,
                        processed = raw.content.uppercase(),
                        timestamp = System.currentTimeMillis()
                    )
                    out.send(processed)
                    println("Worker $workerId processed item ${raw.id}")
                }
            }
        }

        scope.launch {
            // Here you would typically await worker completion and then close `out`.
            // Kept as a comment because the exact coordination depends on requirements.
        }

        return out
    }

    // Stage 3: enrichment
    private fun enrichData(
        processedChannel: ReceiveChannel<ProcessedData>
    ) = scope.produce {
        for (processed in processedChannel) {
            delay(80)
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

    // Stage 4: batched persistence (simplified)
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
        if (batch.isNotEmpty()) {
            saveBatch(batch)
        }
    }

    private suspend fun saveBatch(items: List<EnrichedData>) {
        delay(100)
        println("Saved batch of ${items.size} items: ${items.map { it.id }}")
    }

    suspend fun execute(count: Int) {
        val raw = produceRawData(count)
        val processed = processData(raw, workers = 3)
        val enriched = enrichData(processed)
        saveToDatabase(enriched, batchSize = 5)
    }
}
```

Idea: use channels to connect stages and `launch` for parallel workers. For production code, ensure `out` is closed correctly to avoid consumers hanging.

### Resource Pooling with Semaphore

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit

class DatabaseConnection(val id: Int) {
    suspend fun query(sql: String): List<String> {
        delay(100)
        return listOf("Result from connection $id")
    }
}

class ConnectionPool(private val size: Int) {
    private val connections = List(size) { DatabaseConnection(it) }
    private val semaphore = Semaphore(size)
    private val available = ArrayDeque(connections)

    suspend fun <T> withConnection(block: suspend (DatabaseConnection) -> T): T =
        semaphore.withPermit {
            val connection = synchronized(available) {
                require(available.isNotEmpty())
                available.removeFirst()
            }
            try {
                block(connection)
            } finally {
                synchronized(available) {
                    available.addLast(connection)
                }
            }
        }
}
```

Key ideas:
- `Semaphore` bounds concurrent usage;
- the shared queue is protected via synchronization (in real systems, prefer non-blocking or coroutine-friendly primitives);
- `withPermit` guarantees permit release.

### Resource Pooling with Mutex

```kotlin
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

class ResourceManager<T>(
    private val create: () -> T,
    private val destroy: (T) -> Unit = {}
) {
    private val resources = mutableListOf<T>()
    private val mutex = Mutex()

    suspend fun acquire(): T = mutex.withLock {
        if (resources.isEmpty()) create() else resources.removeAt(0)
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
```

### Rate Limiting Pattern

Simple token-bucket-style limiter using `Semaphore` (demo-level; scope lifecycle and cancellation must be handled with care):

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Semaphore
import kotlin.time.Duration

class RateLimiter(
    private val maxRequests: Int,
    private val window: Duration,
    private val scope: CoroutineScope
) {
    private val semaphore = Semaphore(maxRequests)

    suspend fun <T> execute(block: suspend () -> T): T {
        semaphore.acquire()

        // Schedule permit release after the window using caller-provided scope.
        // Ensure this scope lives long enough and handles cancellation properly.
        scope.launch {
            delay(window)
            semaphore.release()
        }

        return block()
    }
}
```

A sliding-window limiter using `Mutex`:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

class SlidingWindowRateLimiter(
    private val maxRequests: Int,
    private val windowMillis: Long
) {
    private val timestamps = mutableListOf<Long>()
    private val mutex = Mutex()

    suspend fun tryAcquire(): Boolean = mutex.withLock {
        val now = System.currentTimeMillis()
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
```

Note: using an injected scope and proper cancellation handling is important for production-grade implementations.

### Custom Scope Builders

```kotlin
import kotlinx.coroutines.*

suspend fun <T> retryScope(
    times: Int = 3,
    delayMillis: Long = 1000,
    block: suspend CoroutineScope.() -> T
): T {
    require(times >= 1)
    repeat(times - 1) { attempt ->
        try {
            return coroutineScope { block() }
        } catch (e: Exception) {
            if (e is CancellationException) throw e
            println("Attempt ${attempt + 1} failed: ${e.message}")
            delay(delayMillis * (attempt + 1))
        }
    }
    return coroutineScope { block() }
}
```

Timeout wrapper:

```kotlin
import kotlinx.coroutines.*

suspend fun <T> timeoutScope(
    timeoutMillis: Long,
    onTimeout: () -> T,
    block: suspend CoroutineScope.() -> T
): T {
    return try {
        withTimeout(timeoutMillis) { block() }
    } catch (e: TimeoutCancellationException) {
        println("Operation timed out after ${timeoutMillis}ms")
        onTimeout()
    }
}
```

Parallel map with bounded concurrency:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit

suspend fun <T, R> List<T>.parallelMap(
    concurrency: Int = 10,
    transform: suspend (T) -> R
): List<R> = coroutineScope {
    val semaphore = Semaphore(concurrency)
    map { item ->
        async {
            semaphore.withPermit {
                transform(item)
            }
        }
    }.awaitAll()
}
```

### Circuit Breaker Pattern

```kotlin
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

sealed class CircuitState {
    object Closed : CircuitState()
    data class Open(val openedAt: Long) : CircuitState()
    object HalfOpen : CircuitState()
}

class CircuitBreaker(
    private val failureThreshold: Int = 5,
    private val timeoutMillis: Long = 60000
) {
    private var state: CircuitState = CircuitState.Closed
    private var failureCount = 0
    private val mutex = Mutex()

    suspend fun <T> execute(block: suspend () -> T): T {
        return when (val currentState = mutex.withLock { state }) {
            is CircuitState.Closed -> runClosed(block)
            is CircuitState.Open -> runOpen(currentState, block)
            is CircuitState.HalfOpen -> runHalfOpen(block)
        }
    }

    private suspend fun <T> runClosed(block: suspend () -> T): T =
        try {
            val result = block()
            mutex.withLock { failureCount = 0 }
            result
        } catch (e: Exception) {
            mutex.withLock {
                if (++failureCount >= failureThreshold) {
                    state = CircuitState.Open(System.currentTimeMillis())
                    println("Circuit opened")
                }
            }
            throw e
        }

    private suspend fun <T> runOpen(current: CircuitState.Open, block: suspend () -> T): T {
        val now = System.currentTimeMillis()
        return if (now - current.openedAt >= timeoutMillis) {
            mutex.withLock { state = CircuitState.HalfOpen }
            runHalfOpen(block)
        } else {
            throw Exception("Circuit is open, request rejected")
        }
    }

    private suspend fun <T> runHalfOpen(block: suspend () -> T): T =
        try {
            val result = block()
            mutex.withLock {
                state = CircuitState.Closed
                failureCount = 0
                println("Circuit closed")
            }
            result
        } catch (e: Exception) {
            mutex.withLock {
                state = CircuitState.Open(System.currentTimeMillis())
                println("Circuit reopened")
            }
            throw e
        }
}
```

Key idea: only protect state transitions with `Mutex`; do not hold it while executing `block`.

### Bulkhead Pattern

```kotlin
import kotlinx.coroutines.sync.Semaphore
import java.util.concurrent.atomic.AtomicInteger

class Bulkhead(private val maxConcurrent: Int) {
    private val semaphore = Semaphore(maxConcurrent)
    private val activeCount = AtomicInteger(0)
    private val rejectedCount = AtomicInteger(0)

    suspend fun <T> execute(block: suspend () -> T): T {
        if (!semaphore.tryAcquire()) {
            rejectedCount.incrementAndGet()
            throw Exception("Bulkhead full, request rejected")
        }
        activeCount.incrementAndGet()
        return try {
            block()
        } finally {
            activeCount.decrementAndGet()
            semaphore.release()
        }
    }

    fun getMetrics() = "Active: ${activeCount.get()}, Rejected: ${rejectedCount.get()}"
}
```

### Best Practices (EN)

#### DO:

```kotlin
// Use pipeline for sequential stages
val stage1 = produceData()
val stage2 = transformData(stage1)
val stage3 = saveData(stage2)

// Use Semaphore for resource limits
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
// Don't create unbounded channels without a clear reason
val channel = Channel<Int>(Channel.UNLIMITED)  // Can cause OOM

// Don't swallow CancellationException
try {
    operation()
} catch (e: Exception) {
    // Re-throw CancellationException if caught
}

// Don't forget to close or cancel channels
val channel = produce { /* ... */ }
// Cancel/close when done

// Don't block threads in coroutines
GlobalScope.launch {
    Thread.sleep(1000)  // Bad! Use delay()
}
```

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use these patterns in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Coroutines Guide](https://kotlinlang.org/docs/coroutines-guide.html)
- [Channels Documentation](https://kotlinlang.org/docs/channels.html)
- [Shared Mutable State and Concurrency](https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html)
- [Coroutine `Context` and Dispatchers](https://kotlinlang.org/docs/coroutine-context-and-dispatchers.html)

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

## Concept Links

- [[c-kotlin]]
- [[c-coroutines]]
