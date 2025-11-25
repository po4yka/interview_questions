---
id: kotlin-071
title: "select Expression with Channels / Выражение select с каналами"
aliases: ["select Expression with Channels", "Выражение select с каналами"]

# Classification
topic: kotlin
subtopics: [channels, coroutines]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Coroutines select Expression Guide

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-concurrency, c-kotlin, q-advanced-coroutine-patterns--kotlin--hard]

# Timestamps
created: 2025-10-12
updated: 2025-11-11

tags: [channels, coroutines, difficulty/hard, kotlin]
date created: Sunday, October 12th 2025, 3:43:53 pm
date modified: Tuesday, November 25th 2025, 8:53:49 pm
---

# Вопрос (RU)
> Что такое выражение `select` для каналов в Kotlin? Объясните, как мультиплексировать несколько каналов, обрабатывать таймауты с `onTimeout`, реализовать приоритетный выбор и продвинутые паттерны fan-in/fan-out.

# Question (EN)
> What is the select expression for channels in Kotlin? Explain how to multiplex multiple channels, handle timeout with `onTimeout`, implement priority selection, and advanced patterns like fan-in/fan-out.

---

## Ответ (RU)

Выражение `select` в `kotlinx.coroutines` позволяет одновременно ожидать несколько приостанавливаемых операций (отправка/получение из каналов, таймауты и др.) и продолжать выполнение по той ветке, которая первой становится доступна. Это основной механизм мультиплексирования каналов и построения сложных конкурентных паттернов поверх [[c-concurrency]] и [[c-kotlin]].

Важно: во всех примерах предполагается выполнение внутри `CoroutineScope` (например, `runBlocking`, `coroutineScope`, `runTest`), так как `launch`, `produce` и работа с каналами требуют явного скоупа и соблюдения структурированной конкуренции.

Также важно: обычный `select` не гарантирует честность или приоритет между ветками. При необходимости приоритета его нужно реализовывать явно (например, сначала пробовать `tryReceive` для высокоприоритетного канала).

### Базовый Select С Каналами

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import kotlinx.coroutines.selects.*

// Базовый выбор между двумя каналами
fun CoroutineScope.basicSelect() {
    val channel1 = Channel<String>()
    val channel2 = Channel<String>()

    launch {
        delay(100)
        channel1.send("from channel 1")
    }

    launch {
        delay(200)
        channel2.send("from channel 2")
    }

    launch {
        val result = select<String> {
            channel1.onReceive { value ->
                "Received $value"
            }
            channel2.onReceive { value ->
                "Received $value"
            }
        }
        println(result)
        // Скорее всего: Received from channel 1 (побеждает более быстрый)
    }
}

// Select с несколькими приёмами
fun CoroutineScope.multipleSelects() = launch {
    val channel1 = produce {
        repeat(5) {
            delay(100)
            send("Fast-$it")
        }
        close()
    }

    val channel2 = produce {
        repeat(5) {
            delay(200)
            send("Slow-$it")
        }
        close()
    }

    repeat(10) {
        select<Unit> {
            channel1.onReceiveCatching { result ->
                result.getOrNull()?.let { println("Got $it") }
            }
            channel2.onReceiveCatching { result ->
                result.getOrNull()?.let { println("Got $it") }
            }
        }
    }
}
```

### Операции Select

```kotlin
class SelectOperations {

    // onReceive: получение из канала
    fun CoroutineScope.onReceiveExample() = launch {
        val channel = Channel<Int>()

        launch {
            delay(100)
            channel.send(42)
            channel.close()
        }

        val result = select<Int> {
            channel.onReceive { value ->
                println("Received: $value")
                value * 2
            }
        }
        println("Result: $result") // 84
    }

    // onSend: отправка в канал, когда станет возможной
    fun CoroutineScope.onSendExample() = launch {
        val channel = Channel<String>(capacity = 1)

        launch {
            delay(100)
            channel.receive() // Освобождаем место
        }

        select<Unit> {
            channel.onSend("Hello") {
                println("Message sent successfully")
            }
        }
    }

    // onReceiveCatching: безопасное получение с проверкой закрытия
    fun CoroutineScope.onReceiveCatchingExample() = launch {
        val channel = Channel<Int>()

        launch {
            delay(100)
            channel.close()
        }

        select<Unit> {
            channel.onReceiveCatching { result ->
                if (result.isSuccess) {
                    println("Received: ${result.getOrNull()}")
                } else {
                    println("Channel closed")
                }
            }
        }
    }

    // onTimeout: обработка таймаута
    fun CoroutineScope.onTimeoutExample() = launch {
        val channel = Channel<String>()

        // Никто не шлёт в этот канал

        val result = select<String> {
            channel.onReceive { it }
            onTimeout(1000) {
                println("Timeout after 1 second")
                "timeout"
            }
        }
        println("Result: $result")
    }
}
```

### Fan-in: Несколько Источников, Один Потребитель

```kotlin
class FanInPattern {

    // Объединяем несколько каналов в один, пока хотя бы один открыт
    fun <T> CoroutineScope.fanIn(
        vararg channels: ReceiveChannel<T>
    ): ReceiveChannel<T> = produce {
        val open = channels.toMutableSet()

        while (open.isNotEmpty()) {
            select<Unit> {
                // ВАЖНО: не модифицировать 'open' напрямую внутри других веток select,
                // закрытые каналы удаляются после select по их состоянию.
                open.forEach { ch ->
                    ch.onReceiveCatching { result ->
                        val value = result.getOrNull()
                        if (value != null) {
                            send(value)
                        }
                        // Удаление откладывается до завершения итерации select.
                    }
                }
            }
            open.removeAll { it.isClosedForReceive }
        }
    }

    // Пример использования
    suspend fun example() = coroutineScope {
        val producer1 = produce {
            repeat(5) {
                delay(100)
                send("P1-$it")
            }
            close()
        }

        val producer2 = produce {
            repeat(5) {
                delay(150)
                send("P2-$it")
            }
            close()
        }

        val producer3 = produce {
            repeat(5) {
                delay(200)
                send("P3-$it")
            }
            close()
        }

        val merged = fanIn(producer1, producer2, producer3)

        for (value in merged) {
            println("Merged: $value")
        }
    }
}
```

### Fan-out: Один Источник, Несколько Потребителей

```kotlin
class FanOutPattern {

    // Распределяем задания между несколькими worker-ами
    suspend fun fanOutExample() = coroutineScope {
        val jobs = produce {
            repeat(20) {
                send("Job-$it")
            }
            close()
        }

        val workers = List(3) { workerId ->
            launch {
                for (job in jobs) {
                    println("Worker $workerId processing $job")
                    delay(100) // Имитируем работу
                }
            }
        }

        workers.joinAll()
    }

    // Продвинутый вариант: worker с приоритетом на основе select.
    // Завершение воркеров основано на закрытии обоих каналов.
    suspend fun selectBasedFanOut() = coroutineScope {
        val highPriority = Channel<String>()
        val lowPriority = Channel<String>()

        fun CoroutineScope.worker(id: Int) = launch {
            while (isActive) {
                select<Unit> {
                    highPriority.onReceiveCatching { result ->
                        val job = result.getOrNull()
                        if (job != null) {
                            println("Worker $id: HIGH priority $job")
                            delay(50)
                        } else if (result.isClosed && lowPriority.isClosedForReceive) {
                            cancel()
                        }
                    }
                    lowPriority.onReceiveCatching { result ->
                        val job = result.getOrNull()
                        if (job != null) {
                            println("Worker $id: LOW priority $job")
                            delay(100)
                        } else if (result.isClosed && highPriority.isClosedForReceive) {
                            cancel()
                        }
                    }
                }
            }
        }

        val workers = List(2) { worker(it) }

        launch {
            repeat(5) {
                highPriority.send("H-$it")
                delay(150)
            }
            highPriority.close()
        }

        launch {
            repeat(10) {
                lowPriority.send("L-$it")
                delay(50)
            }
            lowPriority.close()
        }

        workers.joinAll()
    }
}
```

### Приоритетный Выбор

```kotlin
class PrioritySelection {

    // Приоритет реализуется явной логикой: сначала пробуем highPriority.tryReceive(),
    // затем используем select для ожидания, не полагаясь на честность реализации select.
    suspend fun priorityWithCustomLogic() = coroutineScope {
        val highPriority = Channel<String>()
        val lowPriority = Channel<String>()

        launch {
            repeat(10) {
                highPriority.send("HIGH-$it")
                delay(100)
            }
            highPriority.close()
        }

        launch {
            repeat(10) {
                lowPriority.send("LOW-$it")
                delay(50)
            }
            lowPriority.close()
        }

        while (isActive) {
            val highResult = highPriority.tryReceive()
            if (highResult.isSuccess) {
                println("Processing: ${highResult.getOrNull()}")
                continue
            }

            if (highPriority.isClosedForReceive && lowPriority.isClosedForReceive) {
                break
            }

            select<Unit> {
                highPriority.onReceiveCatching { result ->
                    val v = result.getOrNull()
                    if (v != null) println("Processing: $v")
                }
                lowPriority.onReceiveCatching { result ->
                    val v = result.getOrNull()
                    if (v != null) println("Processing: $v")
                }
            }
        }
    }
}
```

### Паттерны С Таймаутами

```kotlin
class TimeoutPatterns {

    // Простой таймаут ожидания
    suspend fun simpleTimeout() {
        val channel = Channel<String>()

        val result = select<String?> {
            channel.onReceive { it }
            onTimeout(1000) {
                println("Timed out")
                null
            }
        }

        println("Result: $result")
    }

    // Таймаут с повторами
    suspend fun timeoutWithRetry() {
        val channel = Channel<String>()

        repeat(3) { attempt ->
            val result = select<String?> {
                channel.onReceive { it }
                onTimeout(1000) {
                    println("Attempt ${attempt + 1} timed out")
                    null
                }
            }

            if (result != null) {
                println("Got result: $result")
                return
            }
        }

        println("All attempts failed")
    }

    // Несколько каналов с общим таймаутом
    suspend fun multiChannelTimeout() = coroutineScope {
        val channel1 = Channel<String>()
        val channel2 = Channel<String>()

        launch {
            delay(2000)
            channel1.send("Slow response")
        }

        val result = select<String> {
            channel1.onReceive { it }
            channel2.onReceive { it }
            onTimeout(1000) {
                "Timeout - no response"
            }
        }

        println(result) // "Timeout - no response"
    }
}
```

### Продвинутые Паттерны

```kotlin
class AdvancedSelectPatterns {

    // Гонка нескольких операций: вернуть первый результат, остальные отменить
    suspend fun <T> raceAll(
        vararg operations: suspend () -> T
    ): T = coroutineScope {
        val result = CompletableDeferred<T>()

        operations.forEach { op ->
            launch {
                try {
                    val value = op()
                    result.complete(value)
                } catch (e: Throwable) {
                    if (!result.isCompleted) result.completeExceptionally(e)
                }
            }
        }

        try {
            result.await()
        } finally {
            cancel() // отменяем оставшиеся операции в этом scope
        }
    }

    // Batch с таймаутом: собрать до batchSize или до таймаута/закрытия.
    // Здесь таймаут считается относительно начала вызова, чтобы не превышать timeoutMs.
    suspend fun <T> batchWithTimeout(
        channel: ReceiveChannel<T>,
        batchSize: Int,
        timeoutMs: Long
    ): List<T> = coroutineScope {
        val batch = mutableListOf<T>()
        val start = System.currentTimeMillis()

        while (batch.size < batchSize) {
            val elapsed = System.currentTimeMillis() - start
            val remainingTimeout = timeoutMs - elapsed
            if (remainingTimeout <= 0) break

            val completed = select<Boolean> {
                channel.onReceiveCatching { result ->
                    val v = result.getOrNull()
                    if (v != null) {
                        batch.add(v)
                        false
                    } else {
                        true // канал закрыт
                    }
                }
                onTimeout(remainingTimeout) {
                    true // таймаут
                }
            }
            if (completed) break
        }

        batch
    }

    // Упрощённый circuit breaker (использует withTimeout, не select напрямую)
    class CircuitBreaker<T>(
        private val failureThreshold: Int,
        private val resetTimeoutMs: Long
    ) {
        private var failureCount = 0
        private var lastFailureTime = 0L
        private var state = State.CLOSED

        enum class State { CLOSED, OPEN, HALF_OPEN }

        suspend fun execute(
            operation: suspend () -> T
        ): T {
            when (state) {
                State.OPEN -> {
                    if (System.currentTimeMillis() - lastFailureTime > resetTimeoutMs) {
                        state = State.HALF_OPEN
                    } else {
                        throw CircuitBreakerOpenException()
                    }
                }
                State.HALF_OPEN, State.CLOSED -> {
                    // продолжаем
                }
            }

            return try {
                val result = withTimeout(5000) { operation() }
                if (state == State.HALF_OPEN) {
                    state = State.CLOSED
                    failureCount = 0
                }
                result
            } catch (e: Exception) {
                failureCount++
                lastFailureTime = System.currentTimeMillis()
                if (failureCount >= failureThreshold) {
                    state = State.OPEN
                }
                throw e
            }
        }

        class CircuitBreakerOpenException : Exception("Circuit breaker is open")
    }

    // Request coalescing (не основан на select напрямую, но часто используется вместе)
    class RequestCoalescer<K, V> {
        private val pending = mutableMapOf<K, CompletableDeferred<V>>()

        suspend fun request(
            key: K,
            fetcher: suspend (K) -> V
        ): V {
            pending[key]?.let { return it.await() }

            val deferred = CompletableDeferred<V>()
            pending[key] = deferred

            try {
                val result = fetcher(key)
                deferred.complete(result)
                return result
            } catch (e: Exception) {
                deferred.completeExceptionally(e)
                throw e
            } finally {
                pending.remove(key)
            }
        }
    }
}
```

### Реальный Пример: Агрегатор Данных Из Нескольких Источников

```kotlin
class DataAggregator {

    data class DataSource(val name: String, val priority: Int)
    data class Data(val source: String, val value: String, val timestamp: Long)

    suspend fun aggregateData(
        sources: List<DataSource>,
        timeoutMs: Long
    ): List<Data> = coroutineScope {
        val channels: Map<DataSource, ReceiveChannel<Data>> = sources.associateWith { source ->
            produce {
                delay(source.priority * 100L)
                send(Data(source.name, "data-${source.name}", System.currentTimeMillis()))
                close()
            }
        }

        val results = mutableListOf<Data>()
        val remaining = channels.keys.toMutableSet()
        val startTime = System.currentTimeMillis()

        while (remaining.isNotEmpty()) {
            val elapsed = System.currentTimeMillis() - startTime
            val left = timeoutMs - elapsed
            if (left <= 0) break

            select<Unit> {
                remaining.toList().forEach { source ->
                    val ch = channels.getValue(source)
                    ch.onReceiveCatching { result ->
                        val data = result.getOrNull()
                        if (data != null) {
                            results.add(data)
                            remaining.remove(source)
                        } else if (result.isClosed) {
                            remaining.remove(source)
                        }
                    }
                }

                onTimeout(left) {
                    println("Timeout reached, got ${results.size} results")
                }
            }
        }

        results.sortedByDescending { it.timestamp }
    }

    suspend fun example() {
        val sources = listOf(
            DataSource("API", 1),
            DataSource("Database", 2),
            DataSource("Cache", 0)
        )

        val data = aggregateData(sources, 500)
        data.forEach { println("${it.source}: ${it.value}") }
    }
}
```

### Тестирование Select-выражений

```kotlin
class SelectTests {

    @Test
    fun `test select chooses faster channel`() = runTest {
        val fast = Channel<String>()
        val slow = Channel<String>()

        launch {
            delay(100)
            fast.send("fast")
            fast.close()
        }

        launch {
            delay(500)
            slow.send("slow")
            slow.close()
        }

        val result = select<String> {
            fast.onReceive { it }
            slow.onReceive { it }
        }

        assertEquals("fast", result)
    }

    @Test
    fun `test select with timeout`() = runTest {
        val channel = Channel<String>()

        val result = select<String> {
            channel.onReceive { it }
            onTimeout(100) { "timeout" }
        }

        assertEquals("timeout", result)
    }

    @Test
    fun `test fan-in merges channels`() = runTest {
        val channel1 = produce {
            send("A"); send("B")
            close()
        }
        val channel2 = produce {
            send("1"); send("2")
            close()
        }

        val merged = mutableListOf<String>()

        repeat(4) {
            select<Unit> {
                channel1.onReceiveCatching { result ->
                    result.getOrNull()?.let { merged.add(it) }
                }
                channel2.onReceiveCatching { result ->
                    result.getOrNull()?.let { merged.add(it) }
                }
            }
        }

        assertEquals(4, merged.size)
        assertTrue(merged.containsAll(listOf("A", "B", "1", "2")))
    }
}
```

---

## Answer (EN)

The `select` expression in `kotlinx.coroutines` lets you wait on multiple suspending operations (sending/receiving on channels, timeouts, etc.) and resume with whichever becomes available first. It is the core primitive for multiplexing channels and building higher-level concurrency patterns on top of [[c-concurrency]] and [[c-kotlin]] coroutines.

Note: all examples assume they are executed inside a `CoroutineScope` (e.g. `runBlocking`, `coroutineScope`, `runTest`), because `launch`, `produce` and channel operations require an explicit scope and structured concurrency.

Also note: plain `select` does not guarantee fairness or priority between clauses. If you need priority, you must implement it explicitly (e.g. by probing high-priority channels with `tryReceive` first).

### Basic Select with Channels

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import kotlinx.coroutines.selects.*

// Basic select between two channels
fun CoroutineScope.basicSelect() {
    val channel1 = Channel<String>()
    val channel2 = Channel<String>()

    launch {
        delay(100)
        channel1.send("from channel 1")
    }

    launch {
        delay(200)
        channel2.send("from channel 2")
    }

    launch {
        val result = select<String> {
            channel1.onReceive { value ->
                "Received $value"
            }
            channel2.onReceive { value ->
                "Received $value"
            }
        }
        println(result)
        // Likely: Received from channel 1 (wins because it's faster)
    }
}

// Select with multiple receives
fun CoroutineScope.multipleSelects() = launch {
    val channel1 = produce {
        repeat(5) {
            delay(100)
            send("Fast-$it")
        }
        close()
    }

    val channel2 = produce {
        repeat(5) {
            delay(200)
            send("Slow-$it")
        }
        close()
    }

    repeat(10) {
        select<Unit> {
            channel1.onReceiveCatching { result ->
                result.getOrNull()?.let { println("Got $it") }
            }
            channel2.onReceiveCatching { result ->
                result.getOrNull()?.let { println("Got $it") }
            }
        }
    }
}
```

### Select Operations

```kotlin
class SelectOperations {

    // onReceive: Receive from channel
    fun CoroutineScope.onReceiveExample() = launch {
        val channel = Channel<Int>()

        launch {
            delay(100)
            channel.send(42)
            channel.close()
        }

        val result = select<Int> {
            channel.onReceive { value ->
                println("Received: $value")
                value * 2
            }
        }
        println("Result: $result") // 84
    }

    // onSend: Send to channel when possible
    fun CoroutineScope.onSendExample() = launch {
        val channel = Channel<String>(capacity = 1)

        launch {
            delay(100)
            channel.receive() // Free up space
        }

        select<Unit> {
            channel.onSend("Hello") {
                println("Message sent successfully")
            }
        }
    }

    // onReceiveCatching: Safe receive with close-awareness
    fun CoroutineScope.onReceiveCatchingExample() = launch {
        val channel = Channel<Int>()

        launch {
            delay(100)
            channel.close()
        }

        select<Unit> {
            channel.onReceiveCatching { result ->
                if (result.isSuccess) {
                    println("Received: ${result.getOrNull()}")
                } else {
                    println("Channel closed")
                }
            }
        }
    }

    // onTimeout: Timeout handling
    fun CoroutineScope.onTimeoutExample() = launch {
        val channel = Channel<String>()

        // No one sends to this channel

        val result = select<String> {
            channel.onReceive { it }
            onTimeout(1000) {
                println("Timeout after 1 second")
                "timeout"
            }
        }
        println("Result: $result")
    }
}
```

### Fan-in Pattern: Multiple Producers, Single Consumer

```kotlin
class FanInPattern {

    // Merge multiple channels into one as long as at least one is open.
    fun <T> CoroutineScope.fanIn(
        vararg channels: ReceiveChannel<T>
    ): ReceiveChannel<T> = produce {
        val open = channels.toMutableSet()

        while (open.isNotEmpty()) {
            select<Unit> {
                // IMPORTANT: do not structurally modify 'open' during iteration;
                // closed channels are pruned after select based on their state.
                open.forEach { ch ->
                    ch.onReceiveCatching { result ->
                        val value = result.getOrNull()
                        if (value != null) {
                            send(value)
                        }
                        // Removal is deferred until after this select iteration.
                    }
                }
            }
            open.removeAll { it.isClosedForReceive }
        }
    }

    // Usage example
    suspend fun example() = coroutineScope {
        val producer1 = produce {
            repeat(5) {
                delay(100)
                send("P1-$it")
            }
            close()
        }

        val producer2 = produce {
            repeat(5) {
                delay(150)
                send("P2-$it")
            }
            close()
        }

        val producer3 = produce {
            repeat(5) {
                delay(200)
                send("P3-$it")
            }
            close()
        }

        val merged = fanIn(producer1, producer2, producer3)

        for (value in merged) {
            println("Merged: $value")
        }
    }
}
```

### Fan-out Pattern: Single Producer, Multiple Consumers

```kotlin
class FanOutPattern {

    // Distribute work among multiple workers
    suspend fun fanOutExample() = coroutineScope {
        val jobs = produce {
            repeat(20) {
                send("Job-$it")
            }
            close()
        }

        val workers = List(3) { workerId ->
            launch {
                for (job in jobs) {
                    println("Worker $workerId processing $job")
                    delay(100) // Simulate work
                }
            }
        }

        workers.joinAll()
    }

    // Advanced: Worker with select-based priority.
    // Worker termination depends on both channels being closed.
    suspend fun selectBasedFanOut() = coroutineScope {
        val highPriority = Channel<String>()
        val lowPriority = Channel<String>()

        fun CoroutineScope.worker(id: Int) = launch {
            while (isActive) {
                select<Unit> {
                    highPriority.onReceiveCatching { result ->
                        val job = result.getOrNull()
                        if (job != null) {
                            println("Worker $id: HIGH priority $job")
                            delay(50)
                        } else if (result.isClosed && lowPriority.isClosedForReceive) {
                            cancel()
                        }
                    }
                    lowPriority.onReceiveCatching { result ->
                        val job = result.getOrNull()
                        if (job != null) {
                            println("Worker $id: LOW priority $job")
                            delay(100)
                        } else if (result.isClosed && highPriority.isClosedForReceive) {
                            cancel()
                        }
                    }
                }
            }
        }

        val workers = List(2) { worker(it) }

        launch {
            repeat(5) {
                highPriority.send("H-$it")
                delay(150)
            }
            highPriority.close()
        }

        launch {
            repeat(10) {
                lowPriority.send("L-$it")
                delay(50)
            }
            lowPriority.close()
        }

        workers.joinAll()
    }
}
```

### Priority Selection

```kotlin
class PrioritySelection {

    // Priority is implemented via explicit logic: first try highPriority.tryReceive(),
    // then use select without assuming fairness or priority guarantees.
    suspend fun priorityWithCustomLogic() = coroutineScope {
        val highPriority = Channel<String>()
        val lowPriority = Channel<String>()

        launch {
            repeat(10) {
                highPriority.send("HIGH-$it")
                delay(100)
            }
            highPriority.close()
        }

        launch {
            repeat(10) {
                lowPriority.send("LOW-$it")
                delay(50)
            }
            lowPriority.close()
        }

        while (isActive) {
            val highResult = highPriority.tryReceive()
            if (highResult.isSuccess) {
                println("Processing: ${highResult.getOrNull()}")
                continue
            }

            if (highPriority.isClosedForReceive && lowPriority.isClosedForReceive) {
                break
            }

            select<Unit> {
                highPriority.onReceiveCatching { result ->
                    val v = result.getOrNull()
                    if (v != null) println("Processing: $v")
                }
                lowPriority.onReceiveCatching { result ->
                    val v = result.getOrNull()
                    if (v != null) println("Processing: $v")
                }
            }
        }
    }
}
```

### Timeout Patterns

```kotlin
class TimeoutPatterns {

    // Simple timeout
    suspend fun simpleTimeout() {
        val channel = Channel<String>()

        val result = select<String?> {
            channel.onReceive { it }
            onTimeout(1000) {
                println("Timed out")
                null
            }
        }

        println("Result: $result")
    }

    // Timeout with retry
    suspend fun timeoutWithRetry() {
        val channel = Channel<String>()

        repeat(3) { attempt ->
            val result = select<String?> {
                channel.onReceive { it }
                onTimeout(1000) {
                    println("Attempt ${attempt + 1} timed out")
                    null
                }
            }

            if (result != null) {
                println("Got result: $result")
                return
            }
        }

        println("All attempts failed")
    }

    // Multiple channels with timeout
    suspend fun multiChannelTimeout() = coroutineScope {
        val channel1 = Channel<String>()
        val channel2 = Channel<String>()

        launch {
            delay(2000)
            channel1.send("Slow response")
        }

        val result = select<String> {
            channel1.onReceive { it }
            channel2.onReceive { it }
            onTimeout(1000) {
                "Timeout - no response"
            }
        }

        println(result) // "Timeout - no response"
    }
}
```

### Advanced Patterns

```kotlin
class AdvancedSelectPatterns {

    // Racing multiple operations: returns first result, cancels losers
    suspend fun <T> raceAll(
        vararg operations: suspend () -> T
    ): T = coroutineScope {
        val result = CompletableDeferred<T>()

        operations.forEach { op ->
            launch {
                try {
                    val value = op()
                    result.complete(value)
                } catch (e: Throwable) {
                    if (!result.isCompleted) result.completeExceptionally(e)
                }
            }
        }

        try {
            result.await()
        } finally {
            cancel() // cancel remaining operations in this scope
        }
    }

    // Batching with timeout: collect up to batchSize or until timeout/close.
    // Timeout is measured from the beginning so total wait does not exceed timeoutMs.
    suspend fun <T> batchWithTimeout(
        channel: ReceiveChannel<T>,
        batchSize: Int,
        timeoutMs: Long
    ): List<T> = coroutineScope {
        val batch = mutableListOf<T>()
        val start = System.currentTimeMillis()

        while (batch.size < batchSize) {
            val elapsed = System.currentTimeMillis() - start
            val remainingTimeout = timeoutMs - elapsed
            if (remainingTimeout <= 0) break

            val completed = select<Boolean> {
                channel.onReceiveCatching { result ->
                    val v = result.getOrNull()
                    if (v != null) {
                        batch.add(v)
                        false
                    } else {
                        true // channel closed
                    }
                }
                onTimeout(remainingTimeout) {
                    true // timeout
                }
            }
            if (completed) break
        }

        batch
    }

    // Circuit breaker pattern (simplified, uses withTimeout, not select directly)
    class CircuitBreaker<T>(
        private val failureThreshold: Int,
        private val resetTimeoutMs: Long
    ) {
        private var failureCount = 0
        private var lastFailureTime = 0L
        private var state = State.CLOSED

        enum class State { CLOSED, OPEN, HALF_OPEN }

        suspend fun execute(
            operation: suspend () -> T
        ): T {
            when (state) {
                State.OPEN -> {
                    if (System.currentTimeMillis() - lastFailureTime > resetTimeoutMs) {
                        state = State.HALF_OPEN
                    } else {
                        throw CircuitBreakerOpenException()
                    }
                }
                State.HALF_OPEN, State.CLOSED -> {
                    // proceed
                }
            }

            return try {
                val result = withTimeout(5000) { operation() }
                if (state == State.HALF_OPEN) {
                    state = State.CLOSED
                    failureCount = 0
                }
                result
            } catch (e: Exception) {
                failureCount++
                lastFailureTime = System.currentTimeMillis()
                if (failureCount >= failureThreshold) {
                    state = State.OPEN
                }
                throw e
            }
        }

        class CircuitBreakerOpenException : Exception("Circuit breaker is open")
    }

    // Request coalescing (not select-based but often combined in real systems)
    class RequestCoalescer<K, V> {
        private val pending = mutableMapOf<K, CompletableDeferred<V>>()

        suspend fun request(
            key: K,
            fetcher: suspend (K) -> V
        ): V {
            pending[key]?.let { return it.await() }

            val deferred = CompletableDeferred<V>()
            pending[key] = deferred

            try {
                val result = fetcher(key)
                deferred.complete(result)
                return result
            } catch (e: Exception) {
                deferred.completeExceptionally(e)
                throw e
            } finally {
                pending.remove(key)
            }
        }
    }
}
```

### Real-world Example: Multi-source Data Aggregator

```kotlin
class DataAggregator {

    data class DataSource(val name: String, val priority: Int)
    data class Data(val source: String, val value: String, val timestamp: Long)

    suspend fun aggregateData(
        sources: List<DataSource>,
        timeoutMs: Long
    ): List<Data> = coroutineScope {
        val channels: Map<DataSource, ReceiveChannel<Data>> = sources.associateWith { source ->
            produce {
                delay(source.priority * 100L)
                send(Data(source.name, "data-${source.name}", System.currentTimeMillis()))
                close()
            }
        }

        val results = mutableListOf<Data>()
        val remaining = channels.keys.toMutableSet()
        val startTime = System.currentTimeMillis()

        while (remaining.isNotEmpty()) {
            val elapsed = System.currentTimeMillis() - startTime
            val left = timeoutMs - elapsed
            if (left <= 0) break

            select<Unit> {
                remaining.toList().forEach { source ->
                    val ch = channels.getValue(source)
                    ch.onReceiveCatching { result ->
                        val data = result.getOrNull()
                        if (data != null) {
                            results.add(data)
                            remaining.remove(source)
                        } else if (result.isClosed) {
                            remaining.remove(source)
                        }
                    }
                }

                onTimeout(left) {
                    println("Timeout reached, got ${results.size} results")
                }
            }
        }

        results.sortedByDescending { it.timestamp }
    }

    suspend fun example() {
        val sources = listOf(
            DataSource("API", 1),
            DataSource("Database", 2),
            DataSource("Cache", 0)
        )

        val data = aggregateData(sources, 500)
        data.forEach { println("${it.source}: ${it.value}") }
    }
}
```

### Testing Select Expressions

```kotlin
class SelectTests {

    @Test
    fun `test select chooses faster channel`() = runTest {
        val fast = Channel<String>()
        val slow = Channel<String>()

        launch {
            delay(100)
            fast.send("fast")
            fast.close()
        }

        launch {
            delay(500)
            slow.send("slow")
            slow.close()
        }

        val result = select<String> {
            fast.onReceive { it }
            slow.onReceive { it }
        }

        assertEquals("fast", result)
    }

    @Test
    fun `test select with timeout`() = runTest {
        val channel = Channel<String>()

        val result = select<String> {
            channel.onReceive { it }
            onTimeout(100) { "timeout" }
        }

        assertEquals("timeout", result)
    }

    @Test
    fun `test fan-in merges channels`() = runTest {
        val channel1 = produce {
            send("A"); send("B")
            close()
        }
        val channel2 = produce {
            send("1"); send("2")
            close()
        }

        val merged = mutableListOf<String>()

        repeat(4) {
            select<Unit> {
                channel1.onReceiveCatching { result ->
                    result.getOrNull()?.let { merged.add(it) }
                }
                channel2.onReceiveCatching { result ->
                    result.getOrNull()?.let { merged.add(it) }
                }
            }
        }

        assertEquals(4, merged.size)
        assertTrue(merged.containsAll(listOf("A", "B", "1", "2")))
    }
}
```

---

## Дополнительные Вопросы (RU)

- Как `select` взаимодействует со структурированной конкуренцией и отменой, когда одна ветка завершилась, а другие ещё выполняются?
- В каких случаях вы предпочли бы использовать `select` вместо `Flow` или композиции `Deferred` для мультиплексирования результатов?
- Каковы компромиссы между fan-in/fan-out на базе `select` и использованием более высокоуровневых библиотек или фреймворков для конкуренции?

## Follow-ups

- How does `select` interact with structured concurrency and cancellation when one branch completes and others are still running?
- In which cases would you prefer `select` over `Flow` or `Deferred` composition APIs for multiplexing results?
- What are the trade-offs between using `select`-based fan-in/fan-out and higher-level libraries or frameworks for concurrency?

## Ссылки (RU)

- [[c-kotlin]]
- [[c-concurrency]]
- Официальное руководство по Kotlin Coroutines: раздел "Select expression"

## References

- [[c-kotlin]]
- [[c-concurrency]]
- Official Kotlin Coroutines guide: "Select expression" section

## Related Questions

- [[q-advanced-coroutine-patterns--kotlin--hard]]
