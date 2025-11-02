---
id: kotlin-071
title: "select Expression with Channels / Выражение select с каналами"
aliases: []

# Classification
topic: kotlin
subtopics: [advanced, channels, coroutines, multiplexing, select]
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
related: [q-advanced-coroutine-patterns--kotlin--hard, q-channels-basics-types--kotlin--medium, q-produce-actor-builders--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [advanced, channels, coroutines, difficulty/hard, kotlin, multiplexing, select]
date created: Sunday, October 12th 2025, 3:43:53 pm
date modified: Saturday, November 1st 2025, 5:43:23 pm
---

# Question (EN)
> What is the select expression for channels? Explain how to multiplex multiple channels, handle timeout with onTimeout, implement priority selection, and advanced patterns like fan-in/fan-out.

# Вопрос (RU)
> Что такое выражение select для каналов? Объясните как мультиплексировать несколько каналов, обрабатывать таймауты с onTimeout, реализовать приоритетный выбор и продвинутые паттерны fan-in/fan-out.

---

## Answer (EN)

The `select` expression allows you to wait on multiple suspending operations simultaneously and process whichever completes first. It's especially powerful with channels for implementing complex concurrency patterns.

### Basic Select with Channels

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import kotlinx.coroutines.selects.*

// Basic select between two channels
suspend fun basicSelect() {
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

    select<Unit> {
        channel1.onReceive { value ->
            println("Received $value")
        }
        channel2.onReceive { value ->
            println("Received $value")
        }
    }
    // Output: Received from channel 1 (wins because it's faster)
}

// Select with multiple receives
suspend fun multipleSelects() {
    val channel1 = produce {
        repeat(5) {
            delay(100)
            send("Fast-$it")
        }
    }

    val channel2 = produce {
        repeat(5) {
            delay(200)
            send("Slow-$it")
        }
    }

    repeat(10) {
        select<Unit> {
            channel1.onReceive { value ->
                println("Got $value")
            }
            channel2.onReceive { value ->
                println("Got $value")
            }
        }
    }
}
```

### Select Operations

```kotlin
class SelectOperations {

    // onReceive: Receive from channel
    suspend fun onReceiveExample() {
        val channel = Channel<Int>()

        launch {
            delay(100)
            channel.send(42)
        }

        val result = select<Int> {
            channel.onReceive { value ->
                println("Received: $value")
                value * 2
            }
        }
        println("Result: $result") // 84
    }

    // onSend: Send to channel
    suspend fun onSendExample() {
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

    // onReceiveCatching: Safe receive with result
    suspend fun onReceiveCatchingExample() {
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
    suspend fun onTimeoutExample() {
        val channel = Channel<String>()

        // No one sends to channel

        select<String> {
            channel.onReceive { it }
            onTimeout(1000) {
                println("Timeout after 1 second")
                "timeout"
            }
        }
    }
}
```

### Fan-in Pattern: Multiple Producers, Single Consumer

```kotlin
class FanInPattern {

    // Merge multiple channels into one
    fun <T> CoroutineScope.fanIn(
        vararg channels: ReceiveChannel<T>
    ): ReceiveChannel<T> = produce {
        repeat(channels.sumOf { it.count() }) {
            select<Unit> {
                channels.forEach { channel ->
                    channel.onReceiveCatching { result ->
                        result.getOrNull()?.let { send(it) }
                    }
                }
            }
        }
    }

    // Alternative implementation
    fun <T> CoroutineScope.fanInSimple(
        vararg channels: ReceiveChannel<T>
    ): ReceiveChannel<T> = produce {
        val remaining = channels.toMutableList()

        while (remaining.isNotEmpty()) {
            select<Unit> {
                remaining.forEach { channel ->
                    channel.onReceiveCatching { result ->
                        if (result.isSuccess) {
                            send(result.getOrThrow())
                        } else {
                            remaining.remove(channel)
                        }
                    }
                }
            }
        }
    }

    // Usage example
    suspend fun example() = coroutineScope {
        val producer1 = produce {
            repeat(5) {
                delay(100)
                send("P1-$it")
            }
        }

        val producer2 = produce {
            repeat(5) {
                delay(150)
                send("P2-$it")
            }
        }

        val producer3 = produce {
            repeat(5) {
                delay(200)
                send("P3-$it")
            }
        }

        val merged = fanInSimple(producer1, producer2, producer3)

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
        }

        // Create multiple workers
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

    // Advanced: Worker with select
    suspend fun selectBasedFanOut() = coroutineScope {
        val highPriority = Channel<String>()
        val lowPriority = Channel<String>()

        // Worker that prioritizes high priority jobs
        fun CoroutineScope.worker(id: Int) = launch {
            while (isActive) {
                select<Unit> {
                    highPriority.onReceive { job ->
                        println("Worker $id: HIGH priority $job")
                        delay(50)
                    }
                    lowPriority.onReceive { job ->
                        println("Worker $id: LOW priority $job")
                        delay(100)
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

        delay(2000)
        workers.forEach { it.cancel() }
    }
}
```

### Priority Selection

```kotlin
class PrioritySelection {

    // Priority using selectUnbiased is NOT guaranteed
    // Better approach: Custom priority logic
    suspend fun priorityWithCustomLogic() = coroutineScope {
        val highPriority = Channel<String>()
        val lowPriority = Channel<String>()

        launch {
            repeat(10) { highPriority.send("HIGH-$it"); delay(100) }
            highPriority.close()
        }

        launch {
            repeat(10) { lowPriority.send("LOW-$it"); delay(50) }
            lowPriority.close()
        }

        while (isActive) {
            // Check high priority first
            val highResult = highPriority.tryReceive()
            if (highResult.isSuccess) {
                println("Processing: ${highResult.getOrNull()}")
                continue
            }

            // If no high priority, select between both
            select<Unit> {
                highPriority.onReceiveCatching { result ->
                    result.getOrNull()?.let { println("Processing: $it") }
                        ?: run { cancel() }
                }
                lowPriority.onReceiveCatching { result ->
                    result.getOrNull()?.let { println("Processing: $it") }
                        ?: if (highPriority.isClosedForReceive) cancel()
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

    // Racing multiple operations
    suspend fun <T> raceAll(
        vararg operations: suspend () -> T
    ): T = coroutineScope {
        val results = Channel<T>()

        operations.forEach { op ->
            launch {
                results.send(op())
            }
        }

        results.receive().also {
            coroutineContext.cancel() // Cancel remaining
        }
    }

    // Batching with timeout
    suspend fun <T> batchWithTimeout(
        channel: ReceiveChannel<T>,
        batchSize: Int,
        timeoutMs: Long
    ): List<T> = coroutineScope {
        val batch = mutableListOf<T>()

        while (batch.size < batchSize) {
            select<Unit> {
                channel.onReceiveCatching { result ->
                    result.getOrNull()?.let { batch.add(it) }
                        ?: return@coroutineScope batch
                }
                onTimeout(timeoutMs) {
                    return@coroutineScope batch
                }
            }
        }

        batch
    }

    // Circuit breaker pattern
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
                State.HALF_OPEN -> {}
                State.CLOSED -> {}
            }

            return try {
                val result = withTimeout(5000) {
                    operation()
                }
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

    // Request coalescing
    class RequestCoalescer<K, V> {
        private val pending = mutableMapOf<K, CompletableDeferred<V>>()

        suspend fun request(
            key: K,
            fetcher: suspend (K) -> V
        ): V {
            val existing = pending[key]
            if (existing != null) {
                return existing.await()
            }

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
        val channels = sources.map { source ->
            source to produce {
                // Simulate data fetching
                delay(source.priority * 100L)
                send(Data(source.name, "data-${source.name}", System.currentTimeMillis()))
            }
        }.toMap()

        val results = mutableListOf<Data>()
        val remaining = channels.keys.toMutableSet()

        val startTime = System.currentTimeMillis()

        while (remaining.isNotEmpty()) {
            val elapsed = System.currentTimeMillis() - startTime
            if (elapsed >= timeoutMs) break

            select<Unit> {
                remaining.forEach { source ->
                    channels[source]?.onReceiveCatching { result ->
                        if (result.isSuccess) {
                            results.add(result.getOrThrow())
                            remaining.remove(source)
                        }
                    }
                }

                onTimeout(timeoutMs - elapsed) {
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
        }

        launch {
            delay(500)
            slow.send("slow")
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
        val channel1 = produce { send("A"); send("B") }
        val channel2 = produce { send("1"); send("2") }

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

## Ответ (RU)

Выражение `select` позволяет ожидать несколько приостанавливаемых операций одновременно и обрабатывать ту, которая завершится первой.

### Основные Операции Select

```kotlin
// Выбор между каналами
select<Unit> {
    channel1.onReceive { value -> /* обработка */ }
    channel2.onReceive { value -> /* обработка */ }
}

// С таймаутом
select<String> {
    channel.onReceive { it }
    onTimeout(1000) { "timeout" }
}
```

### Паттерны

**Fan-in**: Объединение нескольких каналов в один
**Fan-out**: Распределение работы между несколькими потребителями
**Priority**: Приоритизация каналов
**Timeout**: Обработка таймаутов

---

## Follow-up Questions (Следующие вопросы)

1. **How does select differ from async/await?**
2. **Can select be used with Deferred values?**
3. **How to implement fair selection between channels?**
4. **What are performance implications of select?**
5. **How to test complex select scenarios?**

---

## References (Ссылки)

### Official Documentation
- [select Expression](https://kotlinlang.org/docs/select-expression.html)
- [Channel select](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/)

### Learning Resources
- "Kotlin Coroutines" by Marcin Moskała - select Expression

---

## Related Questions (Связанные вопросы)

- [[q-channels-basics-types--kotlin--medium]] - Channel fundamentals
- [[q-produce-actor-builders--kotlin--medium]] - Channel builders
- [[q-advanced-coroutine-patterns--kotlin--hard]] - Advanced patterns
- [[q-fan-in-fan-out--kotlin--hard]] - Fan-in/Fan-out patterns
