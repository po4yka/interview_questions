---
id: kotlin-124
title: "Channels Basics and Types / Основы и типы каналов"
aliases: ["Channels Basics and Types, Основы и типы каналов"]

# Classification
topic: kotlin
subtopics: [buffered, channel-types, channels]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Coroutines Channel Guide

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-channel-buffering-strategies--kotlin--hard, q-channel-closing-completion--kotlin--medium, q-channel-flow-comparison--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [buffered, channel-types, channels, coroutines, difficulty/medium, kotlin, rendezvous]
---

# Question (EN)
> What are Channels in Kotlin coroutines? Explain different channel types (Rendezvous, Buffered, Unlimited, Conflated), their characteristics, and when to use each type.

# Вопрос (RU)
> Что такое каналы в корутинах Kotlin? Объясните различные типы каналов (Rendezvous, Buffered, Unlimited, Conflated), их характеристики и когда использовать каждый тип.

---

## Answer (EN)

Channels in Kotlin coroutines provide a way to transfer a stream of values between coroutines. They're similar to BlockingQueue but designed for coroutines with suspend functions instead of blocking operations.

### Core Concept: Communication Primitive

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

// Basic channel usage
suspend fun basicChannelExample() {
    val channel = Channel<Int>()

    launch {
        // Producer
        for (x in 1..5) {
            println("Sending $x")
            channel.send(x)
        }
        channel.close() // Signal completion
    }

    launch {
        // Consumer
        for (y in channel) {
            println("Received $y")
        }
        println("Channel closed")
    }
}

// Output (execution order may vary):
// Sending 1
// Received 1
// Sending 2
// Received 2
// ...
```

**Key characteristics**:
- **Hot stream**: Produces values regardless of consumers
- **Single value transfer**: Each sent value is received exactly once
- **Suspending operations**: send/receive suspend when necessary
- **Closeable**: Can be closed to signal completion

### Channel Types Comparison

```kotlin
// 1. RENDEZVOUS Channel (default, capacity = 0)
suspend fun rendezvousChannel() {
    val channel = Channel<Int>() // or Channel<Int>(Channel.RENDEZVOUS)

    launch {
        println("Sending 1...")
        channel.send(1) // Suspends until received
        println("1 was received")

        println("Sending 2...")
        channel.send(2) // Suspends until received
        println("2 was received")
    }

    delay(100) // Let sender try first

    println("Receiving...")
    println("Got: ${channel.receive()}")
    delay(100)
    println("Got: ${channel.receive()}")

    channel.close()
}

// Output:
// Sending 1...
// Receiving...
// Got: 1
// 1 was received
// Sending 2...
// Got: 2
// 2 was received

// 2. BUFFERED Channel (capacity = N)
suspend fun bufferedChannel() {
    val channel = Channel<Int>(capacity = 3)

    launch {
        for (i in 1..5) {
            println("Sending $i")
            channel.send(i)
            println("Sent $i")
        }
    }

    delay(500) // Let sender work

    for (i in channel) {
        println("Received $i")
        delay(100)
    }
}

// Output:
// Sending 1
// Sent 1
// Sending 2
// Sent 2
// Sending 3
// Sent 3
// Sending 4    <- Suspends here (buffer full)
// Received 1
// Sent 4       <- Resumes
// Sending 5    <- Suspends
// Received 2
// Sent 5
// ...

// 3. UNLIMITED Channel
suspend fun unlimitedChannel() {
    val channel = Channel<Int>(Channel.UNLIMITED)

    launch {
        for (i in 1..10000) {
            channel.send(i) // Never suspends
        }
        println("All sent!")
        channel.close()
    }

    delay(100) // Sender completes instantly

    var count = 0
    for (i in channel) {
        count++
    }
    println("Received $count items")
}

// Output:
// All sent!
// Received 10000 items

// 4. CONFLATED Channel (keeps only latest)
suspend fun conflatedChannel() {
    val channel = Channel<Int>(Channel.CONFLATED)

    launch {
        for (i in 1..10) {
            channel.send(i) // Never suspends, overwrites previous
            println("Sent $i")
        }
        channel.close()
    }

    delay(500) // Let all sends complete

    // Only latest value available
    println("Received: ${channel.receive()}")
    println("Is closed: ${channel.isClosedForReceive}")
}

// Output:
// Sent 1
// Sent 2
// ...
// Sent 10
// Received: 10
// Is closed: true
```

### Detailed Channel Type Characteristics

```kotlin
// Comprehensive comparison
class ChannelTypesDemo {

    // RENDEZVOUS: Direct handoff
    suspend fun rendezvousCharacteristics() {
        val channel = Channel<String>(Channel.RENDEZVOUS)

        println("=== Rendezvous Channel ===")
        println("Capacity: ${channel.capacity}") // 0

        launch {
            println("Producer: About to send")
            channel.send("Message") // Blocks until received
            println("Producer: Message received by consumer")
        }

        delay(100)
        println("Consumer: About to receive")
        val msg = channel.receive()
        println("Consumer: Got $msg")

        channel.close()
    }

    // BUFFERED: Fixed buffer
    suspend fun bufferedCharacteristics() {
        val channel = Channel<Int>(capacity = 2)

        println("\n=== Buffered Channel (capacity=2) ===")

        launch {
            repeat(4) { i ->
                val result = channel.trySend(i)
                println("trySend($i): ${result.isSuccess}")
            }
        }

        delay(100)

        // First 2 succeed (buffer), next 2 fail (full)
        // Output:
        // trySend(0): true
        // trySend(1): true
        // trySend(2): false
        // trySend(3): false

        channel.close()
    }

    // UNLIMITED: No blocking on send
    suspend fun unlimitedCharacteristics() {
        val channel = Channel<Int>(Channel.UNLIMITED)

        println("\n=== Unlimited Channel ===")
        println("Capacity: ${channel.capacity}") // Int.MAX_VALUE

        // Send millions without suspending
        repeat(1_000_000) {
            channel.send(it) // Never suspends
        }
        println("Sent 1 million items instantly!")

        channel.close()

        // Consume
        var count = 0
        for (item in channel) {
            count++
        }
        println("Received $count items")
    }

    // CONFLATED: Only latest value
    suspend fun conflatedCharacteristics() {
        val channel = Channel<Int>(Channel.CONFLATED)

        println("\n=== Conflated Channel ===")

        launch {
            repeat(5) { i ->
                channel.send(i)
                println("Sent $i (overwrites previous)")
                delay(10)
            }
            channel.close()
        }

        delay(100) // Let all sends complete

        // Only last value remains
        val value = channel.tryReceive().getOrNull()
        println("Received: $value") // 4

        val next = channel.tryReceive().getOrNull()
        println("Next: $next") // null (channel closed)
    }
}
```

### When to Use Each Type

```kotlin
// Use Case 1: RENDEZVOUS - Request-Response Pattern
class RequestResponseService {
    private val requestChannel = Channel<Request>()
    private val responseChannel = Channel<Response>()

    data class Request(val id: Int, val data: String)
    data class Response(val id: Int, val result: String)

    suspend fun handleRequests() {
        for (request in requestChannel) {
            // Process request
            val response = Response(request.id, "Processed: ${request.data}")
            responseChannel.send(response)
        }
    }

    suspend fun sendRequest(request: Request): Response {
        requestChannel.send(request) // Suspends until handler ready
        return responseChannel.receive() // Suspends until response ready
    }
}

// Use Case 2: BUFFERED - Smoothing Bursts
class EventProcessor {
    // Buffer handles burst of events without blocking producers
    private val eventChannel = Channel<Event>(capacity = 100)

    data class Event(val type: String, val data: Any)

    fun submitEvent(event: Event) {
        // Non-blocking if buffer not full
        eventChannel.trySend(event)
    }

    suspend fun processEvents() {
        for (event in eventChannel) {
            // Slow processing
            processEvent(event)
            delay(100)
        }
    }

    private suspend fun processEvent(event: Event) {
        println("Processing ${event.type}")
    }
}

// Use Case 3: UNLIMITED - Fire and Forget
class LoggingService {
    // Never block producers
    private val logChannel = Channel<LogEntry>(Channel.UNLIMITED)

    data class LogEntry(val level: String, val message: String, val timestamp: Long)

    fun log(level: String, message: String) {
        // Never suspends, never blocks
        logChannel.trySend(
            LogEntry(level, message, System.currentTimeMillis())
        )
    }

    suspend fun processLogs() {
        for (entry in logChannel) {
            writeToDisk(entry)
        }
    }

    private fun writeToDisk(entry: LogEntry) {
        // Slow I/O operation
    }
}

// Use Case 4: CONFLATED - UI State Updates
class TemperatureSensor {
    // Only care about latest reading
    private val temperatureChannel = Channel<Double>(Channel.CONFLATED)

    // Simulate sensor producing readings
    suspend fun startSensor() {
        while (true) {
            val temp = readTemperature()
            temperatureChannel.send(temp) // Overwrites old value
            delay(100) // Read every 100ms
        }
    }

    // UI updates with latest value
    suspend fun observeTemperature() {
        for (temp in temperatureChannel) {
            updateUI(temp)
            delay(1000) // UI updates every second
        }
    }

    private fun readTemperature(): Double = 20.0 + Math.random() * 10
    private fun updateUI(temp: Double) {
        println("Temperature: $temp°C")
    }
}
```

### Channel Operations and Error Handling

```kotlin
class ChannelOperations {

    // Safe operations with try/catch
    suspend fun safeChannelOperations() {
        val channel = Channel<Int>(capacity = 2)

        // Non-suspending operations
        val sendResult = channel.trySend(1)
        println("Send success: ${sendResult.isSuccess}")

        val receiveResult = channel.tryReceive()
        println("Received: ${receiveResult.getOrNull()}")

        // Handle closed channel
        channel.close()

        val afterClose = channel.trySend(2)
        println("Send after close: ${afterClose.isSuccess}") // false
        println("Closed for send: ${afterClose.isClosedForSend}") // true
    }

    // Producer-Consumer with proper cleanup
    suspend fun producerConsumerPattern() {
        val channel = Channel<Int>(capacity = 10)

        // Producer
        val producerJob = launch {
            try {
                for (i in 1..100) {
                    channel.send(i)
                }
            } catch (e: ClosedSendChannelException) {
                println("Channel closed while sending")
            } finally {
                channel.close()
                println("Producer finished")
            }
        }

        // Consumer
        val consumerJob = launch {
            try {
                for (item in channel) {
                    processItem(item)
                }
            } catch (e: ClosedReceiveChannelException) {
                println("Channel closed while receiving")
            } finally {
                println("Consumer finished")
            }
        }

        // Wait for completion
        joinAll(producerJob, consumerJob)
    }

    private suspend fun processItem(item: Int) {
        delay(10)
        println("Processed: $item")
    }

    // Multiple producers, single consumer
    suspend fun multipleProducers() {
        val channel = Channel<String>(capacity = 50)

        // Start 3 producers
        val producers = List(3) { producerId ->
            launch {
                repeat(10) { i ->
                    channel.send("Producer $producerId: Item $i")
                    delay(50)
                }
            }
        }

        // Single consumer
        launch {
            var count = 0
            for (msg in channel) {
                println(msg)
                count++
                if (count == 30) break // All items received
            }
            channel.cancel() // Stop producers
        }

        producers.joinAll()
    }
}
```

### Performance Considerations

```kotlin
class ChannelPerformance {

    // Rendezvous: Lowest throughput, lowest memory
    suspend fun measureRendezvous() {
        val channel = Channel<Int>()
        val startTime = System.currentTimeMillis()

        launch {
            repeat(10000) {
                channel.send(it)
            }
            channel.close()
        }

        var count = 0
        for (item in channel) {
            count++
        }

        val duration = System.currentTimeMillis() - startTime
        println("Rendezvous: $count items in $duration ms")
        // Typical: ~500-1000ms (lots of suspensions)
    }

    // Buffered: Balanced throughput and memory
    suspend fun measureBuffered() {
        val channel = Channel<Int>(capacity = 1000)
        val startTime = System.currentTimeMillis()

        launch {
            repeat(10000) {
                channel.send(it)
            }
            channel.close()
        }

        var count = 0
        for (item in channel) {
            count++
        }

        val duration = System.currentTimeMillis() - startTime
        println("Buffered: $count items in $duration ms")
        // Typical: ~100-200ms (fewer suspensions)
    }

    // Unlimited: Highest throughput, highest memory
    suspend fun measureUnlimited() {
        val channel = Channel<Int>(Channel.UNLIMITED)
        val startTime = System.currentTimeMillis()

        launch {
            repeat(10000) {
                channel.send(it)
            }
            channel.close()
        }

        delay(10) // Producer finishes almost instantly

        var count = 0
        for (item in channel) {
            count++
        }

        val duration = System.currentTimeMillis() - startTime
        println("Unlimited: $count items in $duration ms")
        // Typical: ~50-100ms (no suspensions, but memory usage)
    }

    // Conflated: Lowest memory, data loss
    suspend fun measureConflated() {
        val channel = Channel<Int>(Channel.CONFLATED)

        launch {
            repeat(10000) {
                channel.send(it)
            }
            channel.close()
        }

        delay(100) // Let all sends complete

        var count = 0
        for (item in channel) {
            println("Received: $item")
            count++
        }

        println("Conflated: $count items received out of 10000")
        // Typical: 1 item (only latest)
    }
}
```

### Common Patterns and Anti-patterns

```kotlin
class ChannelPatterns {

    //  GOOD: Close channel after sending
    suspend fun goodProducerPattern() {
        val channel = Channel<Int>()

        launch {
            try {
                for (i in 1..10) {
                    channel.send(i)
                }
            } finally {
                channel.close() // Always close
            }
        }

        for (item in channel) {
            println(item)
        }
    }

    //  BAD: Forgot to close channel
    suspend fun badProducerPattern() {
        val channel = Channel<Int>()

        launch {
            for (i in 1..10) {
                channel.send(i)
            }
            // Missing channel.close() - consumer hangs forever!
        }

        for (item in channel) { // Loops forever waiting
            println(item)
        }
    }

    //  GOOD: Choose appropriate capacity
    suspend fun goodCapacityChoice() {
        // UI updates: conflated (only latest matters)
        val uiUpdates = Channel<State>(Channel.CONFLATED)

        // Network requests: small buffer
        val requests = Channel<Request>(capacity = 10)

        // Logs: unlimited (never block)
        val logs = Channel<LogEntry>(Channel.UNLIMITED)
    }

    //  BAD: Wrong capacity choice
    suspend fun badCapacityChoice() {
        // UI updates with unlimited: memory leak!
        val uiUpdates = Channel<State>(Channel.UNLIMITED)
        // If UI is slow, millions of states accumulate

        // Critical requests with conflated: data loss!
        val requests = Channel<Request>(Channel.CONFLATED)
        // Lost requests if new ones arrive before processing
    }

    //  GOOD: Proper exception handling
    suspend fun goodExceptionHandling() {
        val channel = Channel<Int>()

        launch {
            try {
                repeat(10) {
                    channel.send(it)
                }
            } catch (e: CancellationException) {
                println("Producer cancelled")
                throw e // Re-throw cancellation
            } finally {
                channel.close()
            }
        }
    }
}
```

---

## Ответ (RU)

Каналы в корутинах Kotlin предоставляют способ передачи потока значений между корутинами. Они похожи на BlockingQueue, но разработаны для корутин с suspend-функциями вместо блокирующих операций.

### Основная Концепция: Примитив Коммуникации

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

// Базовое использование канала
suspend fun basicChannelExample() {
    val channel = Channel<Int>()

    launch {
        // Производитель
        for (x in 1..5) {
            println("Отправка $x")
            channel.send(x)
        }
        channel.close() // Сигнал завершения
    }

    launch {
        // Потребитель
        for (y in channel) {
            println("Получено $y")
        }
        println("Канал закрыт")
    }
}
```

**Ключевые характеристики**:
- **Горячий поток**: Производит значения независимо от потребителей
- **Однократная передача**: Каждое отправленное значение получается ровно один раз
- **Приостанавливаемые операции**: send/receive приостанавливаются при необходимости
- **Закрываемый**: Может быть закрыт для сигнала о завершении

### Сравнение Типов Каналов

```kotlin
// 1. RENDEZVOUS канал (по умолчанию, вместимость = 0)
suspend fun rendezvousChannel() {
    val channel = Channel<Int>() // или Channel<Int>(Channel.RENDEZVOUS)

    launch {
        println("Отправка 1...")
        channel.send(1) // Приостанавливается до получения
        println("1 было получено")

        println("Отправка 2...")
        channel.send(2) // Приостанавливается до получения
        println("2 было получено")
    }

    delay(100) // Даем отправителю попробовать первым

    println("Получение...")
    println("Получено: ${channel.receive()}")
    delay(100)
    println("Получено: ${channel.receive()}")

    channel.close()
}

// 2. BUFFERED канал (вместимость = N)
suspend fun bufferedChannel() {
    val channel = Channel<Int>(capacity = 3)

    launch {
        for (i in 1..5) {
            println("Отправка $i")
            channel.send(i)
            println("Отправлено $i")
        }
    }

    delay(500)

    for (i in channel) {
        println("Получено $i")
        delay(100)
    }
}

// 3. UNLIMITED канал
suspend fun unlimitedChannel() {
    val channel = Channel<Int>(Channel.UNLIMITED)

    launch {
        for (i in 1..10000) {
            channel.send(i) // Никогда не приостанавливается
        }
        println("Все отправлено!")
        channel.close()
    }

    delay(100)

    var count = 0
    for (i in channel) {
        count++
    }
    println("Получено $count элементов")
}

// 4. CONFLATED канал (хранит только последнее)
suspend fun conflatedChannel() {
    val channel = Channel<Int>(Channel.CONFLATED)

    launch {
        for (i in 1..10) {
            channel.send(i) // Не приостанавливается, перезаписывает предыдущее
            println("Отправлено $i")
        }
        channel.close()
    }

    delay(500)

    println("Получено: ${channel.receive()}")
}
```

### Когда Использовать Каждый Тип

**RENDEZVOUS**: Паттерн запрос-ответ, синхронная коммуникация
**BUFFERED**: Сглаживание всплесков, балансировка нагрузки
**UNLIMITED**: Fire-and-forget операции, логирование
**CONFLATED**: Обновления UI, показания датчиков (важно только последнее значение)

### Операции С Каналами

```kotlin
// Безопасные операции
val sendResult = channel.trySend(1)
val receiveResult = channel.tryReceive()

// Обработка закрытого канала
if (sendResult.isClosedForSend) {
    println("Канал закрыт для отправки")
}

// Правильное закрытие
try {
    for (i in 1..10) {
        channel.send(i)
    }
} finally {
    channel.close()
}
```

### Соображения Производительности

- **Rendezvous**: Низкая пропускная способность, минимум памяти
- **Buffered**: Баланс между производительностью и памятью
- **Unlimited**: Высокая пропускная способность, высокое использование памяти
- **Conflated**: Минимум памяти, возможна потеря данных

---

## Follow-up Questions (Следующие вопросы)

1. **How do you handle backpressure with channels?**
   - Buffer sizing strategies
   - Conflated channels for dropping old values
   - Custom flow control mechanisms

2. **What's the difference between Channel and Flow?**
   - Hot vs cold streams
   - Single vs multiple collectors
   - Backpressure handling

3. **How to implement fan-out and fan-in patterns?**
   - Multiple producers, single consumer
   - Single producer, multiple consumers
   - Load balancing between workers

4. **When should you use Channel instead of Flow?**
   - When you need hot stream behavior
   - When multiple coroutines produce values
   - When you need precise control over buffering

5. **How to test code using channels?**
   - Using TestScope
   - Mocking channel behavior
   - Testing producer-consumer patterns

---

## References (Ссылки)

### Official Documentation
- [Kotlin Coroutines Guide - Channels](https://kotlinlang.org/docs/channels.html)
- [Channel API Reference](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/-channel/)
- [Channel Capacity](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/-channel/-factory/)

### Learning Resources
- "Kotlin Coroutines" by Marcin Moskała - Chapter on Channels
- [Roman Elizarov's Medium Articles on Channels](https://medium.com/@elizarov)
- [Kotlin Coroutines Patterns](https://www.youtube.com/watch?v=BOHK_w09pVA)

### Related Topics
- Producer-Consumer Pattern
- Actor Model
- CSP (Communicating Sequential Processes)
- Flow Backpressure

---

## Related Questions (Связанные вопросы)

- [[q-channel-flow-comparison--kotlin--medium]] - Channel vs Flow comparison
- [[q-channel-closing-completion--kotlin--medium]] - Channel closing and completion
- [[q-channel-buffering-strategies--kotlin--hard]] - Advanced buffering strategies
- [[q-produce-actor-builders--kotlin--medium]] - produce and actor builders
- [[q-select-expression-channels--kotlin--hard]] - select expression with channels
