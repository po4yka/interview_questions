---
id: kotlin-114
title: "Channel Buffering Strategies / Стратегии буферизации каналов"
aliases: ["Channel Buffering Strategies, Стратегии буферизации каналов"]

# Classification
topic: kotlin
subtopics:
  - buffering
  - channels
  - conflated
  - coroutines
  - rendezvous
question_kind: theory
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive guide on Channel buffering strategies

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-actor-pattern--kotlin--hard, q-fan-in-fan-out--kotlin--hard, q-flow-backpressure--kotlin--hard]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [buffering, channels, conflated, coroutines, difficulty/hard, kotlin, performance, rendezvous, unlimited]
---
# Вопрос (RU)
> Что такое стратегии буферизации каналов в Kotlin? Объясните каналы RENDEZVOUS, BUFFERED, UNLIMITED и CONFLATED и когда использовать каждый.

---

# Question (EN)
> What are channel buffering strategies in Kotlin? Explain RENDEZVOUS, BUFFERED, UNLIMITED, and CONFLATED channels and when to use each.

## Ответ (RU)

Стратегии буферизации каналов определяют как каналы управляют потоком данных между производителями и потребителями. Kotlin предоставляет четыре основные стратегии с разными компромиссами производительности и памяти.

### RENDEZVOUS (Ёмкость = 0)

Каналы **Rendezvous** не имеют буфера - отправка и получение должны встретиться:

```kotlin
val channel = Channel<Int>(Channel.RENDEZVOUS)

launch {
    channel.send(1) // Приостанавливается пока не готов получатель
}

launch {
    val value = channel.receive() // Встречается с отправителем
}
```

**Характеристики:**
- Нулевая ёмкость буфера
- Send приостанавливается до receive
- Гарантирует синхронизацию
- Нет потери данных
- Меньшее использование памяти

### BUFFERED (Фиксированный размер)

```kotlin
val channel = Channel<Int>(capacity = 10)

// Send приостанавливается когда буфер полон
repeat(15) {
    channel.send(it) // Первые 10 отправятся сразу
}
```

**Характеристики:**
- Фиксированный размер буфера
- Send приостанавливается при полном буфере
- Позволяет обработку всплесков
- Предсказуемое использование памяти

### UNLIMITED (Бесконечный буфер)

```kotlin
val channel = Channel<Int>(Channel.UNLIMITED)

// Send НИКОГДА не приостанавливается
repeat(1_000_000) {
    channel.send(it) // Все отправляется сразу!
}
// Риск OutOfMemoryError!
```

**Характеристики:**
- Неограниченная ёмкость буфера
- Send никогда не приостанавливается
- Риск OutOfMemoryError
- Максимальная пропускная способность
- Использовать с крайней осторожностью

### CONFLATED (Размер 1, Сбрасывает старое)

```kotlin
val channel = Channel<Int>(Channel.CONFLATED)

repeat(10) {
    channel.send(it) // Перезаписывает предыдущее значение
}

val latest = channel.receive() // Получит только 9
```

**Характеристики:**
- Размер буфера 1
- Перезаписывает старое значение новым
- Send никогда не приостанавливается
- Важно только последнее значение
- Постоянное использование памяти

### Выбор Стратегии Буферизации

| Стратегия | Память | Скорость | Потеря данных | Случай использования |
|-----------|--------|----------|---------------|---------------------|
| RENDEZVOUS | Минимальная | Медленно | Никогда | Запрос-ответ, строгий порядок |
| BUFFERED | Предсказуемая | Быстро | Никогда | Очереди задач, пакетная обработка |
| UNLIMITED | Риск OOM | Быстрейшая | Никогда | Логирование (с осторожностью) |
| CONFLATED | Постоянная | Быстро | Да | Обновления UI, данные сенсоров |

---

## Answer (EN)

Channel buffering strategies determine how channels handle the flow of data between producers and consumers. Kotlin provides four main strategies with different performance and memory trade-offs.

### Channel Capacity Types

```kotlin
// Rendezvous (0 buffer)
val channel1 = Channel<Int>(Channel.RENDEZVOUS)
val channel2 = Channel<Int>(0)
val channel3 = Channel<Int>() // Default

// Buffered (specific size)
val channel4 = Channel<Int>(Channel.BUFFERED) // Default 64
val channel5 = Channel<Int>(10) // Custom size

// Unlimited
val channel6 = Channel<Int>(Channel.UNLIMITED)

// Conflated (size 1, drops old)
val channel7 = Channel<Int>(Channel.CONFLATED)
```

### RENDEZVOUS (Capacity = 0)

**Rendezvous** channels have no buffer - send and receive must meet:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

suspend fun rendezvousExample() = coroutineScope {
    val channel = Channel<Int>(Channel.RENDEZVOUS)

    launch {
        println("Sending 1...")
        channel.send(1) // Suspends until receiver ready
        println("Sent 1")

        println("Sending 2...")
        channel.send(2)
        println("Sent 2")

        channel.close()
    }

    launch {
        delay(1000) // Make sender wait
        println("Receiving...")
        println("Received: ${channel.receive()}")

        delay(1000)
        println("Received: ${channel.receive()}")
    }
}

// Output:
// Sending 1...
// (1 second pause)
// Receiving...
// Sent 1
// Received: 1
// Sending 2...
// (1 second pause)
// Sent 2
// Received: 2
```

**Characteristics:**
- Zero buffer capacity
- Send suspends until receive
- Guarantees synchronization
- No data loss
- Lower memory usage
- Can cause deadlocks if not careful

**Use cases:**
```kotlin
// Request-response pattern
suspend fun requestResponse() = coroutineScope {
    val requests = Channel<String>(Channel.RENDEZVOUS)
    val responses = Channel<String>(Channel.RENDEZVOUS)

    // Server
    launch {
        for (request in requests) {
            val response = processRequest(request)
            responses.send(response) // Waits for client to receive
        }
    }

    // Client
    launch {
        requests.send("GET /users")
        val response = responses.receive()
        println("Response: $response")
    }
}

suspend fun processRequest(req: String) = "Processed: $req"
```

### BUFFERED (Fixed Size)

**Buffered** channels have a fixed buffer size:

```kotlin
suspend fun bufferedExample() = coroutineScope {
    val channel = Channel<Int>(capacity = 3)

    launch {
        repeat(5) {
            println("Sending $it")
            channel.send(it)
            println("Sent $it")
        }
        channel.close()
    }

    delay(1000) // Let sender fill buffer
    launch {
        for (value in channel) {
            println("Received: $value")
            delay(500)
        }
    }
}

// Output:
// Sending 0
// Sent 0
// Sending 1
// Sent 1
// Sending 2
// Sent 2
// Sending 3 (suspends - buffer full)
// (1 second pause)
// Received: 0
// Sent 3 (buffer has space)
// Sending 4 (suspends again)
// Received: 1
// Sent 4
// Received: 2
// Received: 3
// Received: 4
```

**Characteristics:**
- Fixed buffer size
- Send suspends when buffer full
- Allows burst handling
- Predictable memory usage
- Decouples producer/consumer speeds

**Default buffer size:**
```kotlin
// System property: kotlinx.coroutines.channels.defaultBuffer
// Default value: 64

val channel = Channel<Int>(Channel.BUFFERED)
// Equivalent to Channel<Int>(64)
```

**Real-world example: Task queue**

```kotlin
class TaskProcessor(private val bufferSize: Int = 100) {
    private val taskChannel = Channel<Task>(capacity = bufferSize)

    suspend fun submitTask(task: Task): Boolean {
        return taskChannel.trySend(task).isSuccess
    }

    fun startProcessing(scope: CoroutineScope, workers: Int = 3) {
        repeat(workers) { workerId ->
            scope.launch {
                for (task in taskChannel) {
                    processTask(workerId, task)
                }
            }
        }
    }

    private suspend fun processTask(workerId: Int, task: Task) {
        println("Worker $workerId processing ${task.id}")
        delay(100)
    }

    fun close() = taskChannel.close()
}

data class Task(val id: Int, val data: String)

suspend fun main() = coroutineScope {
    val processor = TaskProcessor(bufferSize = 10)
    processor.startProcessing(this, workers = 3)

    // Submit tasks
    repeat(30) { i ->
        launch {
            val success = processor.submitTask(Task(i, "data_$i"))
            if (!success) println("Task $i rejected - buffer full")
        }
    }

    delay(2000)
    processor.close()
}
```

### UNLIMITED (Infinite Buffer)

**Unlimited** channels never suspend on send:

```kotlin
suspend fun unlimitedExample() = coroutineScope {
    val channel = Channel<Int>(Channel.UNLIMITED)

    launch {
        repeat(1000) {
            channel.send(it) // Never suspends!
            println("Sent $it")
        }
        channel.close()
    }

    delay(2000) // Sender finishes immediately
    launch {
        var count = 0
        for (value in channel) {
            count++
        }
        println("Received $count items")
    }
}

// Output:
// Sent 0
// Sent 1
// ...
// Sent 999
// (all sent immediately)
// Received 1000 items
```

**Characteristics:**
- Unlimited buffer capacity
- Send never suspends
- Risk of OutOfMemoryError
- Maximum throughput
- Use with extreme caution

**Danger example:**

```kotlin
suspend fun dangerousUnlimited() {
    val channel = Channel<ByteArray>(Channel.UNLIMITED)

    // Producer creates 1GB of data
    launch {
        repeat(1_000_000) {
            channel.send(ByteArray(1024)) // 1KB per item
            // Sends immediately, no backpressure!
        }
    }

    // Slow consumer
    for (data in channel) {
        delay(1) // Very slow
        // Memory fills up: OutOfMemoryError!
    }
}
```

**Safe usage with limits:**

```kotlin
class RateLimitedChannel<T>(
    private val maxSize: Int = 10000
) {
    private val channel = Channel<T>(Channel.UNLIMITED)
    private val size = AtomicInteger(0)

    suspend fun send(element: T): Boolean {
        if (size.get() >= maxSize) {
            return false // Reject when limit reached
        }
        channel.send(element)
        size.incrementAndGet()
        return true
    }

    suspend fun receive(): T {
        val element = channel.receive()
        size.decrementAndGet()
        return element
    }

    fun close() = channel.close()
}
```

### CONFLATED (Size 1, Drop Old)

**Conflated** channels keep only the latest value:

```kotlin
suspend fun conflatedExample() = coroutineScope {
    val channel = Channel<Int>(Channel.CONFLATED)

    launch {
        repeat(10) {
            channel.send(it)
            println("Sent $it")
            delay(50)
        }
        channel.close()
    }

    delay(500) // Let sender send multiple values
    launch {
        for (value in channel) {
            println("Received: $value")
        }
    }
}

// Output:
// Sent 0
// Sent 1
// Sent 2
// ...
// Sent 9
// Received: 9 (only latest value!)
```

**Characteristics:**
- Buffer size of 1
- Overwrites old value with new
- Send never suspends
- Only latest value matters
- Constant memory usage

**Real-world example: Sensor data**

```kotlin
data class SensorReading(val value: Double, val timestamp: Long)

class SensorMonitor {
    private val readings = Channel<SensorReading>(Channel.CONFLATED)

    fun startSensor(scope: CoroutineScope) {
        scope.launch {
            while (true) {
                val reading = SensorReading(
                    value = Random.nextDouble(),
                    timestamp = System.currentTimeMillis()
                )
                readings.send(reading) // Always succeeds, drops old
                delay(10) // Fast sensor: 100 readings/second
            }
        }
    }

    suspend fun getLatestReading(): SensorReading {
        return readings.receive()
    }
}

// Consumer always gets latest reading, even if slow
suspend fun main() = coroutineScope {
    val monitor = SensorMonitor()
    monitor.startSensor(this)

    repeat(5) {
        delay(200) // Slow consumer: 5 readings/second
        val reading = monitor.getLatestReading()
        println("Latest: ${reading.value} at ${reading.timestamp}")
        // Skipped intermediate readings automatically
    }
}
```

### Performance Comparison

```kotlin
import kotlin.system.measureTimeMillis

suspend fun benchmarkChannels() {
    val itemCount = 10000

    // RENDEZVOUS
    val rendezvousTime = measureTimeMillis {
        testChannel(Channel.RENDEZVOUS, itemCount)
    }
    println("RENDEZVOUS: $rendezvousTime ms")

    // BUFFERED
    val bufferedTime = measureTimeMillis {
        testChannel(64, itemCount)
    }
    println("BUFFERED(64): $bufferedTime ms")

    // UNLIMITED
    val unlimitedTime = measureTimeMillis {
        testChannel(Channel.UNLIMITED, itemCount)
    }
    println("UNLIMITED: $unlimitedTime ms")

    // CONFLATED
    val conflatedTime = measureTimeMillis {
        testChannel(Channel.CONFLATED, itemCount)
    }
    println("CONFLATED: $conflatedTime ms")
}

suspend fun testChannel(capacity: Int, count: Int) = coroutineScope {
    val channel = Channel<Int>(capacity)

    launch {
        repeat(count) {
            channel.send(it)
        }
        channel.close()
    }

    launch {
        for (value in channel) {
            // Consume
        }
    }
}

// Typical results:
// RENDEZVOUS: 150ms (slowest - synchronization overhead)
// BUFFERED(64): 50ms (good balance)
// UNLIMITED: 20ms (fastest - no backpressure)
// CONFLATED: 25ms (fast - drops values)
```

### Choosing Buffer Strategy

| Strategy | Memory | Speed | Data Loss | Use Case |
|----------|--------|-------|-----------|----------|
| RENDEZVOUS | Minimal | Slow | Never | Request-response, strict ordering |
| BUFFERED | Predictable | Fast | Never | Task queues, batch processing |
| UNLIMITED | Risk OOM | Fastest | Never | Logging, event collection (with care) |
| CONFLATED | Constant | Fast | Yes | UI updates, sensor data, latest-only |

### Buffer Overflow Strategies

```kotlin
// Channel with overflow handling
val channel = Channel<Int>(
    capacity = 10,
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)

// Available strategies:
// BufferOverflow.SUSPEND (default) - suspend sender
// BufferOverflow.DROP_OLDEST - remove oldest item
// BufferOverflow.DROP_LATEST - drop new item
```

**Custom overflow handling:**

```kotlin
class SmartChannel<T>(
    capacity: Int,
    private val onDrop: (T) -> Unit = {}
) {
    private val channel = Channel<T>(capacity)
    private val buffer = ArrayDeque<T>()
    private val mutex = Mutex()

    suspend fun send(element: T) {
        mutex.withLock {
            if (channel.trySend(element).isSuccess) {
                return
            }

            // Buffer full - custom logic
            if (buffer.size >= capacity) {
                val dropped = buffer.removeFirst()
                onDrop(dropped)
            }
            buffer.addLast(element)
        }
    }

    suspend fun receive(): T = channel.receive()
}

// Usage
val smartChannel = SmartChannel<Int>(capacity = 5) { dropped ->
    println("Dropped value: $dropped")
}
```

### Real-World Example: Event Bus

```kotlin
sealed class Event
data class UserEvent(val action: String) : Event()
data class SystemEvent(val message: String) : Event()

class EventBus {
    // Different strategies for different event types
    private val userEvents = Channel<UserEvent>(capacity = 100)
    private val systemEvents = Channel<SystemEvent>(Channel.CONFLATED)
    private val criticalEvents = Channel<Event>(Channel.RENDEZVOUS)

    suspend fun emitUserEvent(event: UserEvent) {
        userEvents.send(event) // Buffered - important events
    }

    suspend fun emitSystemEvent(event: SystemEvent) {
        systemEvents.send(event) // Conflated - only latest matters
    }

    suspend fun emitCriticalEvent(event: Event) {
        criticalEvents.send(event) // Rendezvous - must be processed
    }

    fun subscribeToUserEvents(): ReceiveChannel<UserEvent> = userEvents
    fun subscribeToSystemEvents(): ReceiveChannel<SystemEvent> = systemEvents
    fun subscribeToCriticalEvents(): ReceiveChannel<Event> = criticalEvents
}

// Usage
suspend fun main() = coroutineScope {
    val bus = EventBus()

    // User event consumer (processes all)
    launch {
        for (event in bus.subscribeToUserEvents()) {
            println("User: ${event.action}")
        }
    }

    // System event consumer (only latest)
    launch {
        for (event in bus.subscribeToSystemEvents()) {
            println("System: ${event.message}")
        }
    }

    // Critical event consumer (immediate processing)
    launch {
        for (event in bus.subscribeToCriticalEvents()) {
            println("Critical: $event")
            // Block sender until processed
        }
    }

    // Emit events
    bus.emitUserEvent(UserEvent("login"))
    bus.emitSystemEvent(SystemEvent("status: ok"))
    bus.emitCriticalEvent(SystemEvent("ALERT"))
}
```

### Best Practices

#### DO:

```kotlin
// Use BUFFERED for most cases
val channel = Channel<Int>(capacity = 100)

// Use RENDEZVOUS for synchronization
val syncChannel = Channel<Int>(Channel.RENDEZVOUS)

// Use CONFLATED for UI updates
val uiChannel = Channel<State>(Channel.CONFLATED)

// Monitor channel usage
val channel = Channel<Int>(capacity = 100)
println("Size: ${channel.isEmpty}/${channel.isClosedForSend}")

// Close channels properly
channel.close()
```

#### DON'T:

```kotlin
// Don't use UNLIMITED without limits
val channel = Channel<Int>(Channel.UNLIMITED) // Dangerous!

// Don't use CONFLATED for important data
val transactions = Channel<Transaction>(Channel.CONFLATED) // Data loss!

// Don't create too many channels
repeat(10000) {
    Channel<Int>() // Memory waste
}

// Don't forget to close
val channel = Channel<Int>()
// Use channel...
// Forgot channel.close() - leak!

// Don't use wrong capacity
val tinyBuffer = Channel<Int>(capacity = 1) // Too small
val hugeBuffer = Channel<Int>(capacity = 1000000) // Too large
```

### Memory Considerations

```kotlin
// Memory usage per strategy (approximate)

// RENDEZVOUS: ~100 bytes
// No buffer, just synchronization

// BUFFERED(64): ~64 * (item size + overhead)
// For Int: ~64 * 16 = 1KB

// UNLIMITED: Unbounded
// Can grow to GBs!

// CONFLATED: ~1 * (item size + overhead)
// For Int: ~16 bytes
```

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Channels](https://kotlinlang.org/docs/channels.html)
- [Channel Capacity](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/-channel/)
- [Buffering Strategies](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/-buffer-overflow/)

## Related Questions

- [[q-flow-backpressure--kotlin--hard]]
- [[q-actor-pattern--kotlin--hard]]
- [[q-fan-in-fan-out--kotlin--hard]]
- [[q-advanced-coroutine-patterns--kotlin--hard]]

## MOC Links

- [[moc-kotlin]]
