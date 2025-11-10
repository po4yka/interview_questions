---
id: kotlin-114
title: "Channel Buffering Strategies / Стратегии буферизации каналов"
aliases: ["Channel Buffering Strategies", "Стратегии буферизации каналов"]

# Classification
topic: kotlin
subtopics:
  - channels
  - coroutines
  - buffering
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
related: [c-kotlin, c-coroutines, q-flow-backpressure--kotlin--hard]

# Timestamps
created: 2025-10-12
updated: 2025-11-09

tags: [buffering, channels, conflated, coroutines, difficulty/hard, kotlin, performance, rendezvous, unlimited]
---
# Вопрос (RU)
> Что такое стратегии буферизации каналов в Kotlin? Объясните каналы RENDEZVOUS, BUFFERED, UNLIMITED и CONFLATED и когда использовать каждый.

---

# Question (EN)
> What are channel buffering strategies in Kotlin? Explain RENDEZVOUS, BUFFERED, UNLIMITED, and CONFLATED channels and when to use each.

## Ответ (RU)

Стратегии буферизации каналов определяют, как каналы управляют потоком данных между производителями и потребителями. Kotlin предоставляет четыре основные стратегии с разными компромиссами производительности и памяти.

### Типы ёмкости канала

```kotlin
// Rendezvous (0 buffer)
val channel1 = Channel<Int>(Channel.RENDEZVOUS)
val channel2 = Channel<Int>(0)
val channel3 = Channel<Int>() // Default is BUFFERED with default capacity

// Buffered (specific size)
val channel4 = Channel<Int>(Channel.BUFFERED) // Default capacity (e.g. 64, configurable)
val channel5 = Channel<Int>(10) // Custom fixed size

// Unlimited
val channel6 = Channel<Int>(Channel.UNLIMITED)

// Conflated (size 1, drops old)
val channel7 = Channel<Int>(Channel.CONFLATED)
```

### RENDEZVOUS (Ёмкость = 0)

Каналы RENDEZVOUS не имеют буфера — отправка и получение должны встретиться:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

suspend fun rendezvousExample() = coroutineScope {
    val channel = Channel<Int>(Channel.RENDEZVOUS)

    launch {
        println("Sending 1...")
        channel.send(1) // Приостанавливается, пока не готов получатель
        println("Sent 1")

        println("Sending 2...")
        channel.send(2)
        println("Sent 2")

        channel.close()
    }

    launch {
        delay(1000) // Заставляем отправителя подождать
        println("Receiving...")
        println("Received: ${channel.receive()}")

        delay(1000)
        println("Received: ${channel.receive()}")
    }
}
```

**Характеристики:**
- Нулевая ёмкость буфера
- `send` приостанавливается до `receive`
- Гарантирует точную синхронизацию
- Нет потери данных
- Малое использование памяти
- Может приводить к взаимоблокировкам, если нет доступного получателя

### BUFFERED (Фиксированный размер)

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

    delay(1000) // Даём отправителю заполнить буфер
    launch {
        for (value in channel) {
            println("Received: $value")
            delay(500)
        }
    }
}
```

**Характеристики:**
- Фиксированный размер буфера
- `send` приостанавливается при полном буфере (`backpressure`)
- Позволяет обработку всплесков нагрузки
- Предсказуемое использование памяти
- Декуплирует скорости производителя и потребителя

**Буфер по умолчанию:**

```kotlin
// Системное свойство: kotlinx.coroutines.channels.defaultBuffer
// Реализация по умолчанию обычно 64, если не переопределено.

val channel = Channel<Int>(Channel.BUFFERED)
// Эквивалентно Channel<Int>(<defaultBuffer>)
```

### UNLIMITED (Бесконечный буфер)

```kotlin
suspend fun unlimitedExample() = coroutineScope {
    val channel = Channel<Int>(Channel.UNLIMITED)

    launch {
        repeat(1000) {
            channel.send(it) // Не приостанавливается из-за ёмкости
            println("Sent $it")
        }
        channel.close()
    }

    delay(2000)
    launch {
        var count = 0
        for (value in channel) {
            count++
        }
        println("Received $count items")
    }
}
```

**Характеристики:**
- Логически неограниченная ёмкость буфера (ограничена только доступной памятью)
- `send` не приостанавливается из-за размера; нет встроенного `backpressure`
- Высокий риск OutOfMemoryError и нагрузки на GC при медленном потребителе
- Использовать крайне осторожно и обычно только там, где допустимы потери/внешние лимиты

**Опасный пример:**

```kotlin
suspend fun dangerousUnlimited(scope: CoroutineScope) {
    val channel = Channel<ByteArray>(Channel.UNLIMITED)

    // Продюсер
    scope.launch {
        repeat(1_000_000) {
            channel.send(ByteArray(1024)) // 1KB, без backpressure
        }
        channel.close()
    }

    // Медленный потребитель
    for (data in channel) {
        delay(1) // Очень медленно
        // Память может сильно расти; риск OOM
    }
}
```

**Иллюстрация защищённого использования (концептуально):**

```kotlin
class RateLimitedChannel<T>(
    private val maxSize: Int = 10_000
) {
    private val channel = Channel<T>(Channel.UNLIMITED)
    private val size = java.util.concurrent.atomic.AtomicInteger(0)

    suspend fun send(element: T): Boolean {
        while (true) {
            val current = size.get()
            if (current >= maxSize) return false
            if (size.compareAndSet(current, current + 1)) {
                break
            }
        }
        return try {
            channel.send(element)
            true
        } catch (e: Throwable) {
            size.decrementAndGet()
            throw e
        }
    }

    suspend fun receive(): T {
        val element = channel.receive()
        size.decrementAndGet()
        return element
    }

    fun close() = channel.close()
}
```

### CONFLATED (Размер 1, сброс старых значений)

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

    delay(500)
    launch {
        for (value in channel) {
            println("Received: $value")
        }
    }
}
// На практике наблюдается только последнее доступное значение(я);
// многие промежуточные значения будут отброшены.
```

**Характеристики:**
- Эффективный размер буфера 1
- Перезаписывает предыдущее значение новым, промежуточные теряются
- `send` не приостанавливается из-за заполнения
- Важно только последнее значение
- Постоянное использование памяти

### Сравнение производительности

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import kotlin.system.measureTimeMillis

suspend fun benchmarkChannels() {
    val itemCount = 10_000

    val rendezvousTime = measureTimeMillis {
        testChannel(Channel.RENDEZVOUS, itemCount)
    }
    println("RENDEZVOUS: $rendezvousTime ms")

    val bufferedTime = measureTimeMillis {
        testChannel(64, itemCount)
    }
    println("BUFFERED(64): $bufferedTime ms")

    val unlimitedTime = measureTimeMillis {
        testChannel(Channel.UNLIMITED, itemCount)
    }
    println("UNLIMITED: $unlimitedTime ms")

    val conflatedTime = measureTimeMillis {
        testChannel(Channel.CONFLATED, itemCount)
    }
    println("CONFLATED: $conflatedTime ms")
}

suspend fun testChannel(capacity: Int, count: Int) = coroutineScope {
    val channel = Channel<Int>(capacity)

    val sender = launch {
        repeat(count) {
            channel.send(it)
        }
        channel.close()
    }

    val receiver = launch {
        for (value in channel) {
            // Потребление
        }
    }

    sender.join()
    receiver.join()
}
```

(Фактические времена зависят от окружения; UNLIMITED и CONFLATED часто быстрее за счёт меньшего количества приостановок/доставки меньшего числа элементов, но могут увеличивать нагрузку на память/GC.)

### Выбор стратегии буферизации

| Стратегия | Память | Скорость | Потеря данных | Случай использования |
|-----------|--------|----------|---------------|----------------------|
| RENDEZVOUS | Минимальная | Ниже (жёсткая синхронизация) | Никогда | Запрос-ответ, строгий порядок |
| BUFFERED | Предсказуемая | Выше (декуплинг) | Никогда | Очереди задач, пакетная обработка |
| UNLIMITED | Риск OOM | Высокая скорость отправки, но возможна деградация | Никогда (только рост задержки) | Логирование/метрики с внешними ограничителями или допустимым дропом |
| CONFLATED | Постоянная | Высокая (за счёт дропа промежуточных) | Да | Обновления UI, данные сенсоров, "важно только последнее" |

### Стратегии при переполнении буфера

```kotlin
import kotlinx.coroutines.channels.BufferOverflow

val channel = Channel<Int>(
    capacity = 10,
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)

// Доступные стратегии:
// BufferOverflow.SUSPEND (по умолчанию) - приостанавливать отправителя, когда буфер заполнен
// BufferOverflow.DROP_OLDEST - удалять самый старый элемент буфера
// BufferOverflow.DROP_LATEST - отбрасывать новый элемент
```

### Реальный пример: Event Bus

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

sealed class Event
data class UserEvent(val action: String) : Event()
data class SystemEvent(val message: String) : Event()

data class CriticalEvent(val message: String) : Event()

class EventBus {
    private val userEvents = Channel<UserEvent>(capacity = 100) // BUFFERED
    private val systemEvents = Channel<SystemEvent>(Channel.CONFLATED) // только последнее
    private val criticalEvents = Channel<CriticalEvent>(Channel.RENDEZVOUS) // строгая синхронизация

    suspend fun emitUserEvent(event: UserEvent) {
        userEvents.send(event)
    }

    suspend fun emitSystemEvent(event: SystemEvent) {
        systemEvents.send(event)
    }

    suspend fun emitCriticalEvent(event: CriticalEvent) {
        criticalEvents.send(event)
    }

    fun subscribeToUserEvents(): ReceiveChannel<UserEvent> = userEvents
    fun subscribeToSystemEvents(): ReceiveChannel<SystemEvent> = systemEvents
    fun subscribeToCriticalEvents(): ReceiveChannel<CriticalEvent> = criticalEvents
}
```

### Рекомендации (Best Practices)

#### Делайте:

```kotlin
// Используйте BUFFERED для большинства producer-consumer пайплайнов
val channel = Channel<Int>(capacity = 100)

// Используйте RENDEZVOUS, когда нужна строгая передача/синхронизация
val syncChannel = Channel<Int>(Channel.RENDEZVOUS)

// Используйте CONFLATED, когда важна только последняя версия состояния (например, UI)
val uiChannel = Channel<State>(Channel.CONFLATED)

// Наблюдайте состояние канала при отладке
println("Empty: ${channel.isEmpty}, closedForSend: ${channel.isClosedForSend}")

// Закрывайте каналы, когда продюсер закончил
channel.close()
```

#### Не делайте:

```kotlin
// Не используйте UNLIMITED без внешних лимитов/мониторинга
val unlimited = Channel<Int>(Channel.UNLIMITED)

// Не используйте CONFLATED для критичных данных, где важно каждое сообщение
val transactions = Channel<Transaction>(Channel.CONFLATED) // риск потери данных

// Не создавайте чрезмерное количество каналов без необходимости
repeat(10_000) {
    Channel<Int>() // оверхед и потенциальные утечки
}

// Не забывайте закрывать канал при понятной ответственности
val c = Channel<Int>()
// ... используем c
c.close()

// Не выбирайте экстремальные размеры буфера без измерений
val tinyBuffer = Channel<Int>(capacity = 1) // может вызывать лишнюю конкуренцию
val hugeBuffer = Channel<Int>(capacity = 1_000_000) // может тратить много памяти
```

### Учет памяти

```kotlin
// Приблизительная интуиция (конкретные значения зависят от реализации/JVM):
// RENDEZVOUS: только структуры синхронизации
// BUFFERED(n): O(n) памяти под очередь элементов
// UNLIMITED: растёт по мере необходимости; может занимать очень много памяти
// CONFLATED: O(1) — только один последний элемент
```

---

## Answer (EN)

Channel buffering strategies determine how channels handle the flow of data between producers and consumers. Kotlin provides four main strategies with different performance and memory trade-offs.

### Channel Capacity Types

```kotlin
// Rendezvous (0 buffer)
val channel1 = Channel<Int>(Channel.RENDEZVOUS)
val channel2 = Channel<Int>(0)
val channel3 = Channel<Int>() // Default is BUFFERED with default capacity

// Buffered (specific size)
val channel4 = Channel<Int>(Channel.BUFFERED) // Default capacity (e.g. 64, configurable)
val channel5 = Channel<Int>(10) // Custom fixed size

// Unlimited
val channel6 = Channel<Int>(Channel.UNLIMITED)

// Conflated (size 1, drops old)
val channel7 = Channel<Int>(Channel.CONFLATED)
```

### RENDEZVOUS (Capacity = 0)

**Rendezvous** channels have no buffer — send and receive must meet:

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
```

**Characteristics:**
- Zero buffer capacity
- send suspends until a receiver is ready
- Provides precise synchronization
- No data loss
- Lower memory usage
- Can cause deadlocks if no receiver is available

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
```

**Characteristics:**
- Fixed buffer size
- send suspends when the buffer is full (backpressure)
- Allows burst handling
- Predictable memory usage
- Decouples producer/consumer speeds

**Default buffer size:**

```kotlin
// System property: kotlinx.coroutines.channels.defaultBuffer
// Implementation default is typically 64 unless overridden.

val channel = Channel<Int>(Channel.BUFFERED)
// Equivalent to Channel<Int>(<defaultBuffer>)
```

### UNLIMITED (Infinite Buffer)

**Unlimited** channels never suspend due to buffer capacity:

```kotlin
suspend fun unlimitedExample() = coroutineScope {
    val channel = Channel<Int>(Channel.UNLIMITED)

    launch {
        repeat(1000) {
            channel.send(it) // Does not suspend because of capacity
            println("Sent $it")
        }
        channel.close()
    }

    delay(2000)
    launch {
        var count = 0
        for (value in channel) {
            count++
        }
        println("Received $count items")
    }
}
```

**Characteristics:**
- Logically unbounded buffer (limited only by available memory)
- send does not suspend due to size; there is no built-in backpressure
- High risk of OutOfMemoryError and GC pressure with slow consumers
- Use extremely carefully and usually only for cases like logging/telemetry where drops or external limits are acceptable

**Danger example:**

```kotlin
suspend fun dangerousUnlimited(scope: CoroutineScope) {
    val channel = Channel<ByteArray>(Channel.UNLIMITED)

    // Producer
    scope.launch {
        repeat(1_000_000) {
            channel.send(ByteArray(1024)) // 1KB each, no backpressure
        }
        channel.close()
    }

    // Slow consumer
    for (data in channel) {
        delay(1) // Very slow
        // Memory usage can grow dramatically; risk of OOM
    }
}
```

**Illustrative guarded usage (conceptual):**

```kotlin
class RateLimitedChannel<T>(
    private val maxSize: Int = 10_000
) {
    private val channel = Channel<T>(Channel.UNLIMITED)
    private val size = java.util.concurrent.atomic.AtomicInteger(0)

    suspend fun send(element: T): Boolean {
        while (true) {
            val current = size.get()
            if (current >= maxSize) return false
            if (size.compareAndSet(current, current + 1)) {
                break
            }
        }
        return try {
            channel.send(element)
            true
        } catch (e: Throwable) {
            size.decrementAndGet()
            throw e
        }
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

    delay(500)
    launch {
        for (value in channel) {
            println("Received: $value")
        }
    }
}
// In practice, only the latest available value(s) are observed; many intermediate values are dropped.
```

**Characteristics:**
- Effective buffer size of 1
- Overwrites the previous value with the new one; intermediate values are lost
- send does not suspend due to buffer being full
- Only the latest value matters
- Constant memory usage

### Performance Comparison

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*
import kotlin.system.measureTimeMillis

suspend fun benchmarkChannels() {
    val itemCount = 10_000

    val rendezvousTime = measureTimeMillis {
        testChannel(Channel.RENDEZVOUS, itemCount)
    }
    println("RENDEZVOUS: $rendezvousTime ms")

    val bufferedTime = measureTimeMillis {
        testChannel(64, itemCount)
    }
    println("BUFFERED(64): $bufferedTime ms")

    val unlimitedTime = measureTimeMillis {
        testChannel(Channel.UNLIMITED, itemCount)
    }
    println("UNLIMITED: $unlimitedTime ms")

    val conflatedTime = measureTimeMillis {
        testChannel(Channel.CONFLATED, itemCount)
    }
    println("CONFLATED: $conflatedTime ms")
}

suspend fun testChannel(capacity: Int, count: Int) = coroutineScope {
    val channel = Channel<Int>(capacity)

    val sender = launch {
        repeat(count) {
            channel.send(it)
        }
        channel.close()
    }

    val receiver = launch {
        for (value in channel) {
            // Consume
        }
    }

    sender.join()
    receiver.join()
}
```

(Note: actual timings depend on environment; UNLIMITED and CONFLATED are fast primarily because they avoid suspensions/deliver fewer elements, but may increase memory/GC costs.)

### Choosing Buffer Strategy

| Strategy | Memory | Speed | Data Loss | Use Case |
|----------|--------|-------|-----------|----------|
| RENDEZVOUS | Minimal | Lower (strict sync) | Never | Request-response, strict ordering |
| BUFFERED | Predictable | Higher (decoupled) | Never | Task queues, batch processing |
| UNLIMITED | Risk OOM | High send rate, but can hurt overall perf | Never (only delay) | Logging/metrics with external safeguards |
| CONFLATED | Constant | High (drops intermediates) | Yes | UI updates, sensor data, "latest only" semantics |

### Buffer Overflow Strategies

```kotlin
import kotlinx.coroutines.channels.BufferOverflow

val channel = Channel<Int>(
    capacity = 10,
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)

// Available strategies:
// BufferOverflow.SUSPEND (default) - suspend sender when full
// BufferOverflow.DROP_OLDEST - remove oldest buffered item
// BufferOverflow.DROP_LATEST - drop the new item
```

### Real-World Example: Event Bus

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.*

sealed class Event
data class UserEvent(val action: String) : Event()
data class SystemEvent(val message: String) : Event()

data class CriticalEvent(val message: String) : Event()

class EventBus {
    private val userEvents = Channel<UserEvent>(capacity = 100) // buffered
    private val systemEvents = Channel<SystemEvent>(Channel.CONFLATED) // latest only
    private val criticalEvents = Channel<CriticalEvent>(Channel.RENDEZVOUS) // strict sync

    suspend fun emitUserEvent(event: UserEvent) {
        userEvents.send(event)
    }

    suspend fun emitSystemEvent(event: SystemEvent) {
        systemEvents.send(event)
    }

    suspend fun emitCriticalEvent(event: CriticalEvent) {
        criticalEvents.send(event)
    }

    fun subscribeToUserEvents(): ReceiveChannel<UserEvent> = userEvents
    fun subscribeToSystemEvents(): ReceiveChannel<SystemEvent> = systemEvents
    fun subscribeToCriticalEvents(): ReceiveChannel<CriticalEvent> = criticalEvents
}
```

### Best Practices

#### DO:

```kotlin
// Use BUFFERED for most producer-consumer pipelines
val channel = Channel<Int>(capacity = 100)

// Use RENDEZVOUS when you need strict handoff/synchronization
val syncChannel = Channel<Int>(Channel.RENDEZVOUS)

// Use CONFLATED when only the latest state matters (e.g., UI)
val uiChannel = Channel<State>(Channel.CONFLATED)

// Observe emptiness/closedness when debugging channel state
println("Empty: ${channel.isEmpty}, closedForSend: ${channel.isClosedForSend}")

// Close channels when you are done producing
channel.close()
```

#### DON'T:

```kotlin
// Don't use UNLIMITED without external limits/monitoring
val unlimited = Channel<Int>(Channel.UNLIMITED)

// Don't use CONFLATED for data where every element is critical
val transactions = Channel<Transaction>(Channel.CONFLATED) // Risk of data loss

// Don't create excessive numbers of channels unnecessarily
repeat(10_000) {
    Channel<Int>() // Overhead and potential leaks
}

// Don't forget to close when ownership is clear
val c = Channel<Int>()
// ... use c
c.close()

// Don't choose extreme capacities without measurement
val tinyBuffer = Channel<Int>(capacity = 1) // May cause unnecessary contention
val hugeBuffer = Channel<Int>(capacity = 1_000_000) // May waste memory
```

### Memory Considerations

```kotlin
// Approximate intuition (real values depend on implementation/JVM):
// RENDEZVOUS: only synchronization structures
// BUFFERED(n): O(n) memory for queued elements
// UNLIMITED: grows as needed; can reach very large memory usage
// CONFLATED: O(1) — single latest element
```

---

## Follow-ups

- What are the key differences between this and Java concurrency primitives?
- When would you use each strategy in practice for real workloads?
- What are common pitfalls (deadlocks, leaks, unbounded growth) to avoid?

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
