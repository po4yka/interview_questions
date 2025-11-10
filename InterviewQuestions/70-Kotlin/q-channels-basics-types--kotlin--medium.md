---
id: kotlin-124
title: "Channels Basics and Types / Основы и типы каналов"
aliases: ["Channels Basics and Types", "Основы и типы каналов"]

# Classification
topic: kotlin
subtopics: [channels, c-kotlin-coroutines-basics, c-coroutines]
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
related: [c-kotlin, c-coroutines, q-channel-buffering-strategies--kotlin--hard]

# Timestamps
created: 2025-10-12
updated: 2025-11-09

tags: [buffered, channel-types, channels, coroutines, difficulty/medium, kotlin, rendezvous]
---

# Вопрос (RU)
> Что такое каналы в корутинах Kotlin? Объясните различные типы каналов (Rendezvous, Buffered, Unlimited, Conflated), их характеристики и когда использовать каждый тип.

# Question (EN)
> What are Channels in Kotlin coroutines? Explain different channel types (Rendezvous, Buffered, Unlimited, Conflated), their characteristics, and when to use each type.

---

## Ответ (RU)

Каналы в корутинах Kotlin предоставляют способ передачи потока значений между корутинами. Они похожи на `BlockingQueue`, но разработаны для корутин с `suspend`-функциями вместо блокирующих операций.

Сам канал — это примитив коммуникации/буфера, он сам по себе не генерирует значения. "Горячесть" или "холодность" источника определяется тем, как устроены продюсеры, а не типом канала.

### Основная Концепция: Примитив Коммуникации

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

// Базовое использование канала
suspend fun basicChannelExample() = coroutineScope {
    val channel = Channel<Int>()

    // Производитель
    launch {
        for (x in 1..5) {
            println("Отправка $x")
            channel.send(x)
        }
        channel.close() // Сигнал завершения
    }

    // Потребитель
    launch {
        for (y in channel) {
            println("Получено $y")
        }
        println("Канал закрыт")
    }
}
```

**Ключевые характеристики**:
- **Примитив для очереди между корутинами**: Пригоден для асинхронного обмена.
- **Однократная доставка**: Каждый отправленный элемент может быть получен не более одного раза.
- **Приостанавливаемые операции**: `send`/`receive` приостанавливаются, если канал не готов (нет места / нет элементов).
- **Закрываемый**: Канал можно закрыть для сигнала завершения; буферизированные элементы всё ещё можно дочитать.

### Сравнение Типов Каналов

```kotlin
// 1. RENDEZVOUS канал (по умолчанию, capacity = 0)
suspend fun rendezvousChannel() = coroutineScope {
    val channel = Channel<Int>() // или Channel<Int>(Channel.RENDEZVOUS)

    launch {
        println("Отправка 1...")
        channel.send(1) // Приостановка до получения
        println("1 было получено")

        println("Отправка 2...")
        channel.send(2) // Приостановка до получения
        println("2 было получено")
    }

    delay(100)

    println("Получение...")
    println("Получено: ${channel.receive()}")
    delay(100)
    println("Получено: ${channel.receive()}")

    channel.close()
}

// 2. BUFFERED канал (capacity = N)
suspend fun bufferedChannel() = coroutineScope {
    val channel = Channel<Int>(capacity = 3)

    launch {
        for (i in 1..5) {
            println("Отправка $i")
            channel.send(i) // Приостанавливается только при заполненном буфере и отсутствии получателя
            println("Отправлено $i")
        }
        channel.close()
    }

    delay(500)

    for (i in channel) {
        println("Получено $i")
        delay(100)
    }
}

// 3. UNLIMITED канал
suspend fun unlimitedChannel() = coroutineScope {
    val channel = Channel<Int>(Channel.UNLIMITED)

    launch {
        for (i in 1..10000) {
            channel.send(i) // Не приостанавливается из-за лимита буфера, но возможны ошибки при закрытом/отменённом канале
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

// 4. CONFLATED канал (хранит только последнее значение)
suspend fun conflatedChannel() = coroutineScope {
    val channel = Channel<Int>(Channel.CONFLATED)

    launch {
        for (i in 1..10) {
            channel.send(i) // Новое значение перезаписывает предыдущее в буфере
            println("Отправлено $i")
        }
        channel.close()
    }

    delay(500)

    // Получатель увидит последнее не прочитанное значение
    if (!channel.isEmpty) {
        println("Получено: ${channel.receive()}")
    }
    println("Канал закрыт для чтения: ${channel.isClosedForReceive}")
}
```

### Подробные Характеристики Типов Каналов

```kotlin
class ChannelTypesDemoRu {

    // RENDEZVOUS: прямой обмен
    suspend fun rendezvousCharacteristics() = coroutineScope {
        val channel = Channel<String>(Channel.RENDEZVOUS)

        println("=== Rendezvous канал ===")
        println("Вместимость: ${channel.capacity}")

        launch {
            println("Продюсер: пытается отправить")
            channel.send("Сообщение") // Приостановка до получения
            println("Продюсер: сообщение получено потребителем")
        }

        delay(100)
        println("Потребитель: пытается получить")
        val msg = channel.receive()
        println("Потребитель: получил $msg")

        channel.close()
    }

    // BUFFERED: фиксированный буфер
    suspend fun bufferedCharacteristics() = coroutineScope {
        val channel = Channel<Int>(capacity = 2)

        println("\n=== Buffered канал (capacity=2) ===")

        launch {
            repeat(4) { i ->
                val result = channel.trySend(i)
                println("trySend($i): ${result.isSuccess}")
            }
            channel.close()
        }

        delay(100)
        // Первые 2 успешны (буфер), следующие 2 неуспешны (буфер полон)
    }

    // UNLIMITED: без обратного давления по capacity
    suspend fun unlimitedCharacteristics() = coroutineScope {
        val channel = Channel<Int>(Channel.UNLIMITED)

        println("\n=== Unlimited канал ===")
        println("Вместимость: ${channel.capacity}")

        launch {
            repeat(1_000_000) {
                channel.send(it)
            }
            channel.close()
        }

        var count = 0
        for (item in channel) {
            count++
        }
        println("Получено $count элементов")
    }

    // CONFLATED: хранится только последнее значение
    suspend fun conflatedCharacteristics() = coroutineScope {
        val channel = Channel<Int>(Channel.CONFLATED)

        println("\n=== Conflated канал ===")

        launch {
            repeat(5) { i ->
                channel.send(i)
                println("Отправлено $i (перезаписывает предыдущее)")
                delay(10)
            }
            channel.close()
        }

        delay(100)

        val value = channel.tryReceive().getOrNull()
        println("Получено: $value")

        val next = channel.tryReceive().getOrNull()
        println("Следующее: $next")
    }
}
```

### Когда Использовать Каждый Тип (с примерами)

```kotlin
// Пример 1: RENDEZVOUS — запрос-ответ
class RequestResponseServiceRu {
    private val requestChannel = Channel<Request>()
    private val responseChannel = Channel<Response>()

    data class Request(val id: Int, val data: String)
    data class Response(val id: Int, val result: String)

    suspend fun handleRequests() = coroutineScope {
        for (request in requestChannel) {
            val response = Response(request.id, "Обработано: ${request.data}")
            responseChannel.send(response)
        }
    }

    suspend fun sendRequest(request: Request): Response {
        requestChannel.send(request)
        return responseChannel.receive()
    }
}

// Пример 2: BUFFERED — сглаживание всплесков
class EventProcessorRu {
    private val eventChannel = Channel<Event>(capacity = 100)

    data class Event(val type: String, val data: Any)

    fun submitEvent(event: Event) {
        eventChannel.trySend(event)
    }

    suspend fun processEvents() {
        for (event in eventChannel) {
            processEvent(event)
            delay(100)
        }
    }

    private suspend fun processEvent(event: Event) {
        println("Обработка ${event.type}")
    }
}

// Пример 3: UNLIMITED — fire-and-forget (с осторожностью)
class LoggingServiceRu {
    private val logChannel = Channel<LogEntry>(Channel.UNLIMITED)

    data class LogEntry(val level: String, val message: String, val timestamp: Long)

    fun log(level: String, message: String) {
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
        // Медленная I/O операция
    }
}

// Пример 4: CONFLATED — обновления UI
class TemperatureSensorRu {
    private val temperatureChannel = Channel<Double>(Channel.CONFLATED)

    suspend fun startSensor() = coroutineScope {
        launch {
            while (isActive) {
                val temp = readTemperature()
                temperatureChannel.send(temp)
                delay(100)
            }
        }
    }

    suspend fun observeTemperature() {
        for (temp in temperatureChannel) {
            updateUI(temp)
            delay(1000)
        }
    }

    private fun readTemperature(): Double = 20.0 + Math.random() * 10

    private fun updateUI(temp: Double) {
        println("Температура: $temp°C")
    }
}
```

### Операции с Каналами и Обработка Ошибок

```kotlin
class ChannelOperationsRu {

    // Безопасные операции с trySend/tryReceive
    suspend fun safeChannelOperations() {
        val channel = Channel<Int>(capacity = 2)

        val sendResult = channel.trySend(1)
        println("Отправка успешна: ${sendResult.isSuccess}")

        val receiveResult = channel.tryReceive()
        println("Получено: ${receiveResult.getOrNull()}")

        channel.close()

        val afterClose = channel.trySend(2)
        println("Отправка после закрытия успешна: ${afterClose.isSuccess}")
        println("Канал закрыт для отправки: ${channel.isClosedForSend}")
    }

    // Продюсер-потребитель с корректным завершением
    suspend fun producerConsumerPattern() = coroutineScope {
        val channel = Channel<Int>(capacity = 10)

        val producerJob = launch {
            try {
                for (i in 1..100) {
                    channel.send(i)
                }
            } catch (e: ClosedSendChannelException) {
                println("Канал закрыт во время отправки")
            } finally {
                channel.close()
                println("Продюсер завершил работу")
            }
        }

        val consumerJob = launch {
            try {
                for (item in channel) {
                    processItem(item)
                }
            } catch (e: ClosedReceiveChannelException) {
                println("Канал закрыт во время получения")
            } finally {
                println("Потребитель завершил работу")
            }
        }

        joinAll(producerJob, consumerJob)
    }

    private suspend fun processItem(item: Int) {
        delay(10)
        println("Обработано: $item")
    }

    // Несколько продюсеров, один потребитель
    suspend fun multipleProducers() = coroutineScope {
        val channel = Channel<String>(capacity = 50)

        val producers = List(3) { producerId ->
            launch {
                repeat(10) { i ->
                    channel.send("Продюсер $producerId: Элемент $i")
                    delay(50)
                }
            }
        }

        val consumer = launch {
            var count = 0
            for (msg in channel) {
                println(msg)
                count++
                if (count == 30) break
            }
            channel.cancel()
        }

        producers.forEach { it.join() }
        consumer.join()
    }
}
```

### Соображения Производительности (с кодом)

```kotlin
class ChannelPerformanceRu {

    // Rendezvous: больше приостановок, меньше память
    suspend fun measureRendezvous() = coroutineScope {
        val channel = Channel<Int>()
        val startTime = System.currentTimeMillis()

        launch {
            repeat(10_000) {
                channel.send(it)
            }
            channel.close()
        }

        var count = 0
        for (item in channel) {
            count++
        }

        val duration = System.currentTimeMillis() - startTime
        println("Rendezvous: $count элементов за $duration мс")
    }

    // Buffered: выше пропускная способность, ограниченная память
    suspend fun measureBuffered() = coroutineScope {
        val channel = Channel<Int>(capacity = 1_000)
        val startTime = System.currentTimeMillis()

        launch {
            repeat(10_000) {
                channel.send(it)
            }
            channel.close()
        }

        var count = 0
        for (item in channel) {
            count++
        }

        val duration = System.currentTimeMillis() - startTime
        println("Buffered: $count элементов за $duration мс")
    }

    // Unlimited: без обратного давления, риск памяти
    suspend fun measureUnlimited() = coroutineScope {
        val channel = Channel<Int>(Channel.UNLIMITED)
        val startTime = System.currentTimeMillis()

        launch {
            repeat(10_000) {
                channel.send(it)
            }
            channel.close()
        }

        var count = 0
        for (item in channel) {
            count++
        }

        val duration = System.currentTimeMillis() - startTime
        println("Unlimited: $count элементов за $duration мс")
    }

    // Conflated: только последнее значение, потеря промежуточных
    suspend fun measureConflated() = coroutineScope {
        val channel = Channel<Int>(Channel.CONFLATED)

        launch {
            repeat(10_000) {
                channel.send(it)
            }
            channel.close()
        }

        var count = 0
        for (item in channel) {
            println("Получено: $item")
            count++
        }

        println("Conflated: получено $count элементов из 10000 (обычно мало, часто 1)")
    }
}
```

### Распространённые Паттерны и Антипаттерны

```kotlin
class ChannelPatternsRu {

    // ХОРОШО: закрывать канал после отправки
    suspend fun goodProducerPattern() = coroutineScope {
        val channel = Channel<Int>()

        launch {
            try {
                for (i in 1..10) {
                    channel.send(i)
                }
            } finally {
                channel.close()
            }
        }

        for (item in channel) {
            println(item)
        }
    }

    // ПЛОХО: забыть закрыть канал (потребитель может зависнуть)
    suspend fun badProducerPattern() = coroutineScope {
        val channel = Channel<Int>()

        launch {
            for (i in 1..10) {
                channel.send(i)
            }
            // Нет channel.close()
        }

        for (item in channel) {
            println(item)
        }
    }

    // ХОРОШО: выбирать подходящую вместимость
    suspend fun goodCapacityChoice() {
        val uiUpdates = Channel<State>(Channel.CONFLATED)
        val requests = Channel<Request>(capacity = 10)
        val logs = Channel<LogEntry>(Channel.UNLIMITED)
    }

    // ПЛОХО: неправильный выбор вместимости
    suspend fun badCapacityChoice() {
        val uiUpdates = Channel<State>(Channel.UNLIMITED)
        val requests = Channel<Request>(Channel.CONFLATED)
    }

    // ХОРОШО: корректная обработка исключений
    suspend fun goodExceptionHandling() = coroutineScope {
        val channel = Channel<Int>()

        launch {
            try {
                repeat(10) {
                    channel.send(it)
                }
            } catch (e: CancellationException) {
                println("Продюсер отменён")
                throw e
            } finally {
                channel.close()
            }
        }
    }
}
```

---

## Answer (EN)

Channels in Kotlin coroutines provide a way to transfer a stream of values between coroutines. They're similar to `BlockingQueue` but designed for coroutines with `suspend` functions instead of blocking operations.

A channel itself is a communication/buffering primitive; it does not produce values on its own. Whether the overall data source behaves "hot" (producing regardless of observers) or "cold" depends on how producer coroutines are implemented.

### Core Concept: Communication Primitive

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

// Basic channel usage
suspend fun basicChannelExample() = coroutineScope {
    val channel = Channel<Int>()

    // Producer
    launch {
        for (x in 1..5) {
            println("Sending $x")
            channel.send(x)
        }
        channel.close() // Signal completion
    }

    // Consumer
    launch {
        for (y in channel) {
            println("Received $y")
        }
        println("Channel closed")
    }
}
```

**Key characteristics**:
- **Coroutine-friendly queue**: A suspendable primitive for communication between coroutines.
- **Single delivery**: Each sent element is received at most once.
- **Suspending operations**: `send`/`receive` suspend when the channel is not ready (e.g., no buffer / no elements).
- **Closeable**: Can be closed to signal completion; remaining buffered elements can still be received.

### Channel Types Comparison

```kotlin
// 1. RENDEZVOUS Channel (default, capacity = 0)
suspend fun rendezvousChannel() = coroutineScope {
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

// 2. BUFFERED Channel (capacity = N)
suspend fun bufferedChannel() = coroutineScope {
    val channel = Channel<Int>(capacity = 3)

    launch {
        for (i in 1..5) {
            println("Sending $i")
            channel.send(i) // Suspends only when buffer is full and no receiver
            println("Sent $i")
        }
        channel.close()
    }

    delay(500) // Let sender work

    for (i in channel) {
        println("Received $i")
        delay(100)
    }
}

// 3. UNLIMITED Channel
suspend fun unlimitedChannel() = coroutineScope {
    val channel = Channel<Int>(Channel.UNLIMITED)

    launch {
        for (i in 1..10000) {
            channel.send(i) // Does not suspend due to buffer limit; may still fail if channel closed/cancelled
        }
        println("All sent!")
        channel.close()
    }

    delay(100)

    var count = 0
    for (i in channel) {
        count++
    }
    println("Received $count items")
}

// 4. CONFLATED Channel (keeps only latest)
suspend fun conflatedChannel() = coroutineScope {
    val channel = Channel<Int>(Channel.CONFLATED)

    launch {
        for (i in 1..10) {
            channel.send(i) // Does not suspend due to buffer limit; overwrites previous buffered value
            println("Sent $i")
        }
        channel.close()
    }

    delay(500) // Let all sends complete

    // Receiving gets the latest value that was not yet received.
    if (!channel.isEmpty) {
        println("Received: ${channel.receive()}")
    }
    println("Is closed for receive: ${channel.isClosedForReceive}")
}
```

### Detailed Channel Type Characteristics

```kotlin
// Comprehensive comparison
class ChannelTypesDemo {

    // RENDEZVOUS: Direct handoff
    suspend fun rendezvousCharacteristics() = coroutineScope {
        val channel = Channel<String>(Channel.RENDEZVOUS)

        println("=== Rendezvous Channel ===")
        println("Capacity: ${channel.capacity}") // 0

        launch {
            println("Producer: About to send")
            channel.send("Message") // Suspends until received
            println("Producer: Message received by consumer")
        }

        delay(100)
        println("Consumer: About to receive")
        val msg = channel.receive()
        println("Consumer: Got $msg")

        channel.close()
    }

    // BUFFERED: Fixed buffer
    suspend fun bufferedCharacteristics() = coroutineScope {
        val channel = Channel<Int>(capacity = 2)

        println("\n=== Buffered Channel (capacity=2) ===")

        launch {
            repeat(4) { i ->
                val result = channel.trySend(i)
                println("trySend($i): ${result.isSuccess}")
            }
            channel.close()
        }

        delay(100)

        // First 2 succeed (buffer), next 2 fail (buffer full)
        // Output:
        // trySend(0): true
        // trySend(1): true
        // trySend(2): false
        // trySend(3): false
    }

    // UNLIMITED: No backpressure from capacity
    suspend fun unlimitedCharacteristics() = coroutineScope {
        val channel = Channel<Int>(Channel.UNLIMITED)

        println("\n=== Unlimited Channel ===")
        println("Capacity: ${channel.capacity}") // Int.MAX_VALUE (effectively unbounded)

        launch {
            repeat(1_000_000) {
                channel.send(it) // Does not suspend due to capacity, but can still fail if channel closed/cancelled
            }
            channel.close()
        }

        var count = 0
        for (item in channel) {
            count++
        }
        println("Received $count items")
    }

    // CONFLATED: Only latest value retained
    suspend fun conflatedCharacteristics() = coroutineScope {
        val channel = Channel<Int>(Channel.CONFLATED)

        println("\n=== Conflated Channel ===")

        launch {
            repeat(5) { i ->
                channel.send(i) // Overwrites previous buffered value
                println("Sent $i (overwrites previous)")
                delay(10)
            }
            channel.close()
        }

        delay(100) // Let all sends complete

        val value = channel.tryReceive().getOrNull()
        println("Received: $value") // Typically 4 (the latest)

        val next = channel.tryReceive().getOrNull()
        println("Next: $next") // null (no more elements; channel is closed)
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

    suspend fun handleRequests() = coroutineScope {
        for (request in requestChannel) {
            // Process request
            val response = Response(request.id, "Processed: ${request.data}")
            responseChannel.send(response)
        }
    }

    suspend fun sendRequest(request: Request): Response {
        requestChannel.send(request) // May suspend until handler ready
        return responseChannel.receive() // Suspends until response ready
    }
}

// Use Case 2: BUFFERED - Smoothing Bursts
class EventProcessor {
    // Buffer handles bursts of events without immediately blocking producers
    private val eventChannel = Channel<Event>(capacity = 100)

    data class Event(val type: String, val data: Any)

    fun submitEvent(event: Event) {
        // Non-suspending if buffer not full
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

// Use Case 3: UNLIMITED - Fire and Forget (with caution)
class LoggingService {
    // Avoids blocking producers due to buffer capacity; risk of high memory usage under load
    private val logChannel = Channel<LogEntry>(Channel.UNLIMITED)

    data class LogEntry(val level: String, val message: String, val timestamp: Long)

    fun log(level: String, message: String) {
        // Non-suspending with respect to capacity; may fail if channel closed/cancelled
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
    // Only care about the latest reading
    private val temperatureChannel = Channel<Double>(Channel.CONFLATED)

    // Simulate sensor producing readings
    suspend fun startSensor() = coroutineScope {
        launch {
            while (isActive) {
                val temp = readTemperature()
                temperatureChannel.send(temp) // Overwrites old buffered value
                delay(100) // Read every 100ms
            }
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

    // Safe operations with try/catch and trySend/tryReceive
    suspend fun safeChannelOperations() {
        val channel = Channel<Int>(capacity = 2)

        // Non-suspending send/receive attempts
        val sendResult = channel.trySend(1)
        println("Send success: ${sendResult.isSuccess}")

        val receiveResult = channel.tryReceive()
        println("Received: ${receiveResult.getOrNull()}")

        // Close channel
        channel.close()

        val afterClose = channel.trySend(2)
        println("Send after close success: ${afterClose.isSuccess}") // false
        println("Channel closed for send: ${channel.isClosedForSend}") // true
    }

    // Producer-Consumer with proper cleanup
    suspend fun producerConsumerPattern() = coroutineScope {
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
    suspend fun multipleProducers() = coroutineScope {
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
        val consumer = launch {
            var count = 0
            for (msg in channel) {
                println(msg)
                count++
                if (count == 30) break // All items received
            }
            channel.cancel() // Cancel the channel and wake up senders
        }

        producers.forEach { it.join() }
        consumer.join()
    }
}
```

### Performance Considerations

```kotlin
class ChannelPerformance {

    // Rendezvous: More suspensions, lower throughput, minimal memory
    suspend fun measureRendezvous() = coroutineScope {
        val channel = Channel<Int>()
        val startTime = System.currentTimeMillis()

        launch {
            repeat(10_000) {
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
    }

    // Buffered: Fewer suspensions, better throughput, bounded memory
    suspend fun measureBuffered() = coroutineScope {
        val channel = Channel<Int>(capacity = 1_000)
        val startTime = System.currentTimeMillis()

        launch {
            repeat(10_000) {
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
    }

    // Unlimited: No backpressure from capacity; risk of higher memory usage
    suspend fun measureUnlimited() = coroutineScope {
        val channel = Channel<Int>(Channel.UNLIMITED)
        val startTime = System.currentTimeMillis()

        launch {
            repeat(10_000) {
                channel.send(it)
            }
            channel.close()
        }

        var count = 0
        for (item in channel) {
            count++
        }

        val duration = System.currentTimeMillis() - startTime
        println("Unlimited: $count items in $duration ms")
    }

    // Conflated: Keeps only the most recent value; may lose intermediate data
    suspend fun measureConflated() = coroutineScope {
        val channel = Channel<Int>(Channel.CONFLATED)

        launch {
            repeat(10_000) {
                channel.send(it)
            }
            channel.close()
        }

        var count = 0
        for (item in channel) {
            println("Received: $item")
            count++
        }

        println("Conflated: $count items received out of 10000 (typically small, often 1)")
    }
}
```

### Common Patterns and Anti-patterns

```kotlin
class ChannelPatterns {

    // GOOD: Close channel after sending
    suspend fun goodProducerPattern() = coroutineScope {
        val channel = Channel<Int>()

        launch {
            try {
                for (i in 1..10) {
                    channel.send(i)
                }
            } finally {
                channel.close() // Always close when producer is done
            }
        }

        for (item in channel) {
            println(item)
        }
    }

    // BAD: Forgot to close channel (consumer may hang)
    suspend fun badProducerPattern() = coroutineScope {
        val channel = Channel<Int>()

        launch {
            for (i in 1..10) {
                channel.send(i)
            }
            // Missing channel.close() - consumer loop will keep waiting
        }

        for (item in channel) { // Suspends waiting for more until channel is closed/cancelled
            println(item)
        }
    }

    // GOOD: Choose appropriate capacity
    suspend fun goodCapacityChoice() {
        // UI updates: conflated (only latest matters)
        val uiUpdates = Channel<State>(Channel.CONFLATED)

        // Network requests: bounded buffer
        val requests = Channel<Request>(capacity = 10)

        // Logs: larger/unlimited buffer (with monitoring)
        val logs = Channel<LogEntry>(Channel.UNLIMITED)
    }

    // BAD: Wrong capacity choice
    suspend fun badCapacityChoice() {
        // UI updates with unlimited: risk of high memory usage
        val uiUpdates = Channel<State>(Channel.UNLIMITED)

        // Critical requests with conflated: data loss risk
        val requests = Channel<Request>(Channel.CONFLATED)
    }

    // GOOD: Proper exception handling
    suspend fun goodExceptionHandling() = coroutineScope {
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

## Follow-ups

1. How do you handle backpressure with channels?
   - Buffer sizing strategies
   - Conflated channels for dropping old values
   - Custom flow control mechanisms

2. What's the difference between `Channel` and `Flow`?
   - Hot vs cold streams
   - Single vs multiple collectors
   - Backpressure handling

3. How to implement fan-out and fan-in patterns?
   - Multiple producers, single consumer
   - Single producer, multiple consumers
   - Load balancing between workers

4. When should you use `Channel` instead of `Flow`?
   - When you need hot stream behavior
   - When multiple coroutines produce values
   - When you need precise control over buffering

5. How to test code using channels?
   - Using `TestScope`
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
- [[c-coroutines]]
- Producer-Consumer Pattern
- Actor Model
- CSP (Communicating Sequential Processes)
- `Flow` backpressure

---

## Related Questions (Связанные вопросы)

- [[q-channel-flow-comparison--kotlin--medium]] - Channel vs Flow comparison
- [[q-channel-closing-completion--kotlin--medium]] - Channel closing and completion
- [[q-channel-buffering-strategies--kotlin--hard]] - Advanced buffering strategies
- [[q-produce-actor-builders--kotlin--medium]] - produce and actor builders
- [[q-select-expression-channels--kotlin--hard]] - select expression with channels
