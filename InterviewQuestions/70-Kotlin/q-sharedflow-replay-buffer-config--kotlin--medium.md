---
id: kotlin-080
title: "SharedFlow replay cache and buffer configuration / SharedFlow replay cache и конфигурация буфера"
aliases: [Hot Flow, Replay Buffer, SharedFlow, SharedFlow Configuration]
topic: kotlin
subtopics: [coroutines, flow]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-channels-vs-flow--kotlin--medium, q-data-class-purpose--kotlin--easy, q-kotlin-any-class-methods--programming-languages--medium]
created: 2025-10-12
updated: 2025-10-31
tags: [backpressure, buffer, configuration, coroutines, difficulty/medium, flow, hot-flow, kotlin, replay, sharedflow]
contributors: []
date created: Friday, October 31st 2025, 6:30:54 pm
date modified: Saturday, November 1st 2025, 5:43:23 pm
---

# SharedFlow Replay Cache and Buffer Configuration / SharedFlow Replay Cache И Конфигурация Буфера

## English Version

### Question
How do you configure SharedFlow's replay cache and buffer? Explain the `replay`, `extraBufferCapacity`, and `onBufferOverflow` parameters, their interactions, and real-world usage scenarios with performance considerations.

### Answer

#### Understanding SharedFlow

`SharedFlow` is a **hot flow** that emits values to all active collectors. Unlike cold flows, it doesn't restart for each collector. Key characteristics:

- **Hot**: Emits regardless of collectors
- **Broadcast**: All collectors receive the same values
- **Configurable**: Replay, buffer, and overflow behavior
- **State-sharing**: Can be used for events or state

#### MutableSharedFlow Constructor Parameters

```kotlin
public fun <T> MutableSharedFlow(
    replay: Int = 0,
    extraBufferCapacity: Int = 0,
    onBufferOverflow: BufferOverflow = BufferOverflow.SUSPEND
): MutableSharedFlow<T>
```

**Three key parameters:**

1. **replay**: Number of values to cache for late subscribers
2. **extraBufferCapacity**: Additional buffer beyond replay
3. **onBufferOverflow**: What happens when buffer is full

#### The Replay Parameter

The `replay` parameter specifies how many **most recent values** are cached and replayed to new collectors:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun demonstrateReplay() = runBlocking {
    // replay = 2: Cache last 2 values
    val flow = MutableSharedFlow<Int>(replay = 2)

    // Emit 3 values (no collectors yet)
    flow.emit(1)
    flow.emit(2)
    flow.emit(3)

    // New collector receives last 2 values (2, 3)
    launch {
        flow.collect { value ->
            println("Collector 1: $value")
        }
    }
    // Output:
    // Collector 1: 2
    // Collector 1: 3

    delay(100)

    // Emit another value
    flow.emit(4)
    // Output:
    // Collector 1: 4

    // New collector receives last 2 values (3, 4)
    launch {
        flow.collect { value ->
            println("Collector 2: $value")
        }
    }
    // Output:
    // Collector 2: 3
    // Collector 2: 4

    delay(100)
}
```

**Replay behavior:**

| replay value | Behavior | Use case |
|--------------|----------|----------|
| 0 | No replay, late subscribers miss past values | Events |
| 1 | Replay last value (like StateFlow) | Latest state |
| N | Replay last N values | Recent history |
| Int.MAX_VALUE | Replay all values (unbounded) | Complete history (risk!) |

**Accessing replay cache:**

```kotlin
import kotlinx.coroutines.flow.*

fun accessReplayCache() {
    val flow = MutableSharedFlow<String>(replay = 3)

    // Emit some values
    runBlocking {
        flow.emit("A")
        flow.emit("B")
        flow.emit("C")
    }

    // Access cached values without collecting
    val cached: List<String> = flow.replayCache
    println("Cached: $cached") // [A, B, C]
}
```

#### The extraBufferCapacity Parameter

`extraBufferCapacity` adds buffer space **beyond** the replay cache for **slow collectors**:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun demonstrateExtraBuffer() = runBlocking {
    // replay = 0, but buffer = 2 for slow collectors
    val flow = MutableSharedFlow<Int>(
        replay = 0,
        extraBufferCapacity = 2
    )

    // Fast emitter
    launch {
        repeat(5) {
            println("Emitting $it")
            flow.emit(it)
            delay(10)
        }
    }

    // Slow collector (takes 100ms per value)
    launch {
        delay(50) // Start late
        flow.collect { value ->
            println("Collecting $value")
            delay(100) // Slow processing
        }
    }

    delay(1000)
}

// Output explanation:
// Emitter is fast (10ms), collector is slow (100ms)
// Buffer holds 2 values while collector processes
// Without buffer, emitter would suspend waiting for collector
```

**Total buffer capacity:**

```
Total capacity = replay + extraBufferCapacity
```

**Example:**
```kotlin
val flow = MutableSharedFlow<Int>(
    replay = 2,           // 2 slots for replay
    extraBufferCapacity = 3  // 3 additional slots
)
// Total: 5 buffered values
```

#### The onBufferOverflow Parameter

When total buffer is full, `onBufferOverflow` determines what happens:

```kotlin
enum class BufferOverflow {
    SUSPEND,    // Suspend emitter (backpressure)
    DROP_OLDEST, // Drop oldest value, add new
    DROP_LATEST  // Drop new value, keep existing
}
```

**1. BufferOverflow.SUSPEND (default)**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun demonstrateSuspend() = runBlocking {
    val flow = MutableSharedFlow<Int>(
        replay = 0,
        extraBufferCapacity = 2,
        onBufferOverflow = BufferOverflow.SUSPEND // Default
    )

    // Slow collector
    launch {
        flow.collect { value ->
            println("Collected: $value")
            delay(200) // Slow
        }
    }

    // Fast emitter
    launch {
        repeat(5) { i ->
            println("Emitting $i at ${System.currentTimeMillis()}")
            flow.emit(i) // Will suspend when buffer full
            println("Emitted $i")
        }
    }

    delay(2000)
}

// Output shows emitter suspending when buffer (2) is full
// Provides backpressure
```

**2. BufferOverflow.DROP_OLDEST**

```kotlin
fun demonstrateDropOldest() = runBlocking {
    val flow = MutableSharedFlow<Int>(
        replay = 1,
        extraBufferCapacity = 2,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )

    // No collector, just emit
    repeat(5) {
        println("Emitting $it")
        flow.emit(it) // Never suspends
    }

    println("Replay cache: ${flow.replayCache}")
    // Output: [4] (only most recent value)

    // Collector receives only last value
    flow.take(1).collect { println("Collected: $it") }
    // Output: Collected: 4
}
```

**3. BufferOverflow.DROP_LATEST**

```kotlin
fun demonstrateDropLatest() = runBlocking {
    val flow = MutableSharedFlow<Int>(
        replay = 1,
        extraBufferCapacity = 2,
        onBufferOverflow = BufferOverflow.DROP_LATEST
    )

    // Emit values
    flow.emit(1)
    flow.emit(2)
    flow.emit(3)
    flow.emit(4) // Buffer full, drops 4
    flow.emit(5) // Buffer full, drops 5

    println("Replay cache: ${flow.replayCache}")
    // Output: [3] (new values were dropped)
}
```

**Comparison table:**

| Strategy | Behavior | Use case | Emitter blocks? |
|----------|----------|----------|-----------------|
| SUSPEND | Wait for space | Critical data | Yes |
| DROP_OLDEST | Remove oldest | Latest state matters | No |
| DROP_LATEST | Ignore new | First events matter | No |

#### How Replay and Buffer Work Together

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun demonstrateReplayAndBuffer() = runBlocking {
    val flow = MutableSharedFlow<String>(
        replay = 2,            // Keep last 2 for new collectors
        extraBufferCapacity = 3,  // 3 additional buffer slots
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )

    // Emit 10 values (no collectors)
    repeat(10) {
        flow.emit("Value-$it")
    }

    println("Replay cache: ${flow.replayCache}")
    // Output: [Value-8, Value-9]
    // Only last 2 values kept (replay = 2)

    // New collector gets replayed values
    launch {
        flow.take(2).collect { value ->
            println("Collected: $value")
        }
    }
    // Output:
    // Collected: Value-8
    // Collected: Value-9

    delay(100)
}
```

**Visualization:**

```
Configuration: replay=2, extraBufferCapacity=3, onBufferOverflow=DROP_OLDEST

[Replay Cache (2)] [Extra Buffer (3)]
    Slot 1             Slot 3
    Slot 2             Slot 4
                      Slot 5

Total capacity: 5

When full and new value arrives:
- DROP_OLDEST: Remove Slot 1, add to end
- DROP_LATEST: Ignore new value
- SUSPEND: Wait until space available
```

#### Real-World Examples

**Example 1: Event bus (no replay)**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

sealed class AppEvent {
    data class UserLoggedIn(val userId: String) : AppEvent()
    data class UserLoggedOut(val userId: String) : AppEvent()
    data class NetworkError(val error: String) : AppEvent()
}

class EventBus {
    // Events: no replay, subscribers only get future events
    private val _events = MutableSharedFlow<AppEvent>(
        replay = 0,
        extraBufferCapacity = 10,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val events: SharedFlow<AppEvent> = _events

    suspend fun post(event: AppEvent) {
        _events.emit(event)
    }
}

// Usage
suspend fun demonstrateEventBus() {
    val eventBus = EventBus()

    // Subscriber 1
    val job1 = CoroutineScope(Dispatchers.Default).launch {
        eventBus.events.collect { event ->
            println("Subscriber 1: $event")
        }
    }

    // Subscriber 2 (starts later)
    val job2 = CoroutineScope(Dispatchers.Default).launch {
        delay(100) // Starts late, misses early events
        eventBus.events.collect { event ->
            println("Subscriber 2: $event")
        }
    }

    // Post events
    eventBus.post(AppEvent.UserLoggedIn("user1"))
    delay(50)
    eventBus.post(AppEvent.UserLoggedIn("user2"))
    delay(100)
    eventBus.post(AppEvent.NetworkError("timeout"))

    delay(200)
    job1.cancel()
    job2.cancel()
}
```

**Example 2: UI state with latest value (like StateFlow)**

```kotlin
import kotlinx.coroutines.flow.*

data class UiState(
    val isLoading: Boolean = false,
    val data: String? = null,
    val error: String? = null
)

class ViewModel {
    // replay = 1: New collectors get current state
    private val _uiState = MutableSharedFlow<UiState>(
        replay = 1,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val uiState: SharedFlow<UiState> = _uiState

    init {
        // Must emit initial value
        runBlocking {
            _uiState.emit(UiState())
        }
    }

    suspend fun loadData() {
        _uiState.emit(UiState(isLoading = true))

        delay(1000) // Simulate network call

        _uiState.emit(UiState(
            isLoading = false,
            data = "Loaded data"
        ))
    }
}

// Note: StateFlow is better for this use case!
// StateFlow = SharedFlow(replay=1, onBufferOverflow=DROP_OLDEST) + initial value
```

**Example 3: Recent notifications (replay last N)**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

data class Notification(
    val id: String,
    val title: String,
    val message: String,
    val timestamp: Long = System.currentTimeMillis()
)

class NotificationManager {
    // Keep last 5 notifications for new observers
    private val _notifications = MutableSharedFlow<Notification>(
        replay = 5,
        extraBufferCapacity = 10,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val notifications: SharedFlow<Notification> = _notifications

    suspend fun notify(notification: Notification) {
        _notifications.emit(notification)
    }

    fun getRecentNotifications(): List<Notification> {
        return _notifications.replayCache
    }
}

// Usage
suspend fun demonstrateNotifications() {
    val manager = NotificationManager()

    // Send some notifications
    repeat(10) { i ->
        manager.notify(Notification(
            id = "notif-$i",
            title = "Notification $i",
            message = "Message $i"
        ))
        delay(50)
    }

    // New observer gets last 5
    manager.notifications.take(5).collect { notif ->
        println("Received: ${notif.title}")
    }
    // Output: Notification 5, 6, 7, 8, 9
}
```

**Example 4: Multi-subscriber scenario with buffering**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

class DataPublisher {
    private val _data = MutableSharedFlow<Int>(
        replay = 1,
        extraBufferCapacity = 32,
        onBufferOverflow = BufferOverflow.SUSPEND // Backpressure
    )
    val data: SharedFlow<Int> = _data

    suspend fun publish() {
        repeat(100) { i ->
            _data.emit(i)
            delay(10)
        }
    }
}

suspend fun demonstrateMultiSubscriber() = coroutineScope {
    val publisher = DataPublisher()

    // Fast consumer
    launch {
        publisher.data.collect { value ->
            println("Fast: $value")
            // No delay - keeps up
        }
    }

    // Slow consumer
    launch {
        publisher.data.collect { value ->
            println("Slow: $value")
            delay(50) // Can't keep up
        }
    }

    // Medium consumer
    launch {
        delay(200) // Starts late
        publisher.data.collect { value ->
            println("Late: $value")
            delay(20)
        }
    }

    launch { publisher.publish() }

    delay(2000)
}
// Buffer allows slow consumers to lag without blocking fast ones
// (up to buffer limit)
```

#### Late Subscriber Behavior

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun demonstrateLateSubscriber() = runBlocking {
    val flow = MutableSharedFlow<Int>(replay = 3)

    // Emit values before any collector
    launch {
        repeat(10) {
            println("Emitting $it")
            flow.emit(it)
            delay(50)
        }
    }

    delay(250) // Let some emissions happen

    // Late subscriber receives replay cache
    launch {
        println("Late subscriber starting...")
        flow.collect { value ->
            println("Late subscriber received: $value")
        }
    }

    delay(1000)
}

// Output:
// Emitting 0
// Emitting 1
// Emitting 2
// Emitting 3
// Emitting 4
// Late subscriber starting...
// Late subscriber received: 2  <- Replay cache starts here
// Late subscriber received: 3
// Late subscriber received: 4
// Emitting 5
// Late subscriber received: 5  <- Then receives new emissions
```

#### Performance Implications

**Memory usage:**

```kotlin
import kotlinx.coroutines.flow.*

// Scenario 1: High memory usage
val highMemory = MutableSharedFlow<LargeObject>(
    replay = 1000,  // Keeps 1000 objects in memory!
    extraBufferCapacity = 1000  // Plus 1000 more
)
// Memory: ~2000 * sizeof(LargeObject)

// Scenario 2: Low memory usage
val lowMemory = MutableSharedFlow<LargeObject>(
    replay = 1,  // Only 1 object
    extraBufferCapacity = 0
)
// Memory: ~1 * sizeof(LargeObject)

data class LargeObject(val data: ByteArray)
```

**CPU impact of replay:**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlin.system.measureTimeMillis

suspend fun benchmarkReplay() {
    // Benchmark replay cache replay
    val flow = MutableSharedFlow<Int>(replay = 1000)

    // Fill replay cache
    repeat(1000) { flow.emit(it) }

    // Measure time for new collector to receive replay
    val time = measureTimeMillis {
        flow.take(1000).collect { }
    }

    println("Replay of 1000 values took: ${time}ms")
    // Very fast - replay is immediate, no suspension
}
```

**Buffer overflow performance:**

```kotlin
suspend fun benchmarkOverflow() = coroutineScope {
    // SUSPEND: Slowest for emitter, guarantees delivery
    val suspendFlow = MutableSharedFlow<Int>(
        extraBufferCapacity = 10,
        onBufferOverflow = BufferOverflow.SUSPEND
    )

    // DROP_OLDEST: Fastest for emitter, may lose data
    val dropFlow = MutableSharedFlow<Int>(
        extraBufferCapacity = 10,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )

    // Benchmark SUSPEND
    val suspendTime = measureTimeMillis {
        launch {
            suspendFlow.collect { delay(100) } // Slow
        }
        repeat(100) { suspendFlow.emit(it) }
    }

    // Benchmark DROP_OLDEST
    val dropTime = measureTimeMillis {
        launch {
            dropFlow.collect { delay(100) } // Slow
        }
        repeat(100) { dropFlow.emit(it) }
    }

    println("SUSPEND: ${suspendTime}ms")  // ~10000ms (blocks on slow collector)
    println("DROP_OLDEST: ${dropTime}ms") // ~10ms (never blocks)
}
```

#### When to Use Replay Vs StateFlow

**Use StateFlow when:**
- Representing **state** (not events)
- Need exactly **one current value**
- Need **conflated behavior** (always latest)
- Want simpler API (`.value` property)

**Use SharedFlow with replay when:**
- Need more than 1 replayed value
- Need events (can be zero replay)
- Need control over buffer overflow
- Need to distinguish "no value" from "null value"

```kotlin
import kotlinx.coroutines.flow.*

// StateFlow: State (always has value)
val stateFlow = MutableStateFlow("initial")
stateFlow.value = "updated" // Direct access

// SharedFlow: Events or state with more control
val sharedFlow = MutableSharedFlow<String?>(replay = 1)
// No .value property, must emit
```

**Equivalence:**

```kotlin
// These are functionally similar:
val stateFlow = MutableStateFlow("initial")

val sharedFlow = MutableSharedFlow<String>(
    replay = 1,
    onBufferOverflow = BufferOverflow.DROP_OLDEST
).apply {
    tryEmit("initial") // Must emit initial value
}
```

#### Testing SharedFlow Configurations

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.test.*
import org.junit.Test
import kotlin.test.assertEquals

class SharedFlowTests {
    @Test
    fun testReplayCache() = runTest {
        val flow = MutableSharedFlow<Int>(replay = 3)

        flow.emit(1)
        flow.emit(2)
        flow.emit(3)

        assertEquals(listOf(1, 2, 3), flow.replayCache)

        flow.emit(4)
        assertEquals(listOf(2, 3, 4), flow.replayCache)
    }

    @Test
    fun testLateSubscriber() = runTest {
        val flow = MutableSharedFlow<Int>(replay = 2)

        flow.emit(1)
        flow.emit(2)
        flow.emit(3)

        val collected = mutableListOf<Int>()
        val job = launch {
            flow.take(3).collect { collected.add(it) }
        }

        job.join()
        assertEquals(listOf(2, 3), collected.take(2)) // Replay
    }

    @Test
    fun testBufferOverflowSuspend() = runTest {
        val flow = MutableSharedFlow<Int>(
            extraBufferCapacity = 2,
            onBufferOverflow = BufferOverflow.SUSPEND
        )

        var emitCount = 0

        // Slow collector
        launch {
            flow.collect {
                delay(100)
            }
        }

        // Fast emitter
        launch {
            repeat(10) {
                flow.emit(it)
                emitCount++
            }
        }

        advanceTimeBy(150)
        // Emitter suspended after filling buffer
        assert(emitCount < 10)
    }

    @Test
    fun testBufferOverflowDrop() = runTest {
        val flow = MutableSharedFlow<Int>(
            replay = 1,
            extraBufferCapacity = 2,
            onBufferOverflow = BufferOverflow.DROP_OLDEST
        )

        // Emit many values quickly
        repeat(10) { flow.emit(it) }

        // Only most recent in cache
        assertEquals(listOf(9), flow.replayCache)
    }
}
```

### Common Pitfalls

1. **Forgetting that SharedFlow is hot**
```kotlin
// Bad: Creates flow but no collectors, emissions lost
val flow = MutableSharedFlow<Int>(replay = 0)
launch { flow.emit(42) } // Lost if no collectors!

// Good: Either use replay or ensure collectors
val flow2 = MutableSharedFlow<Int>(replay = 1)
launch { flow2.emit(42) } // Cached for late collectors
```

2. **Using huge replay values**
```kotlin
// Bad: Memory leak risk
val flow = MutableSharedFlow<LargeData>(
    replay = Int.MAX_VALUE // Keeps ALL values forever!
)

// Good: Reasonable replay
val flow2 = MutableSharedFlow<LargeData>(
    replay = 10 // Keep last 10 only
)
```

3. **Wrong overflow strategy**
```kotlin
// Bad: Using DROP for critical data
val criticalData = MutableSharedFlow<Transaction>(
    onBufferOverflow = BufferOverflow.DROP_OLDEST // Can lose transactions!
)

// Good: Use SUSPEND for critical data
val criticalData2 = MutableSharedFlow<Transaction>(
    extraBufferCapacity = 100,
    onBufferOverflow = BufferOverflow.SUSPEND // Backpressure
)
```

### Summary

**SharedFlow configuration** requires understanding three parameters:

- **replay**: How many values new collectors receive (0 = events, 1 = state, N = history)
- **extraBufferCapacity**: Buffer for slow collectors (0 = no buffer, N = N slots)
- **onBufferOverflow**: What happens when full (SUSPEND = backpressure, DROP_OLDEST = latest wins, DROP_LATEST = keep old)

**Total capacity** = replay + extraBufferCapacity

Choose configuration based on use case:
- **Events**: replay=0, DROP_OLDEST
- **State**: replay=1, DROP_OLDEST (or use StateFlow)
- **History**: replay=N, consider memory
- **Critical data**: SUSPEND for backpressure

---

## Russian Version / Русская Версия

### Вопрос
Как настроить replay cache и buffer в SharedFlow? Объясните параметры `replay`, `extraBufferCapacity` и `onBufferOverflow`, их взаимодействие и реальные сценарии использования с учётом производительности.

### Ответ

#### Понимание SharedFlow

`SharedFlow` - это **горячий поток**, который эмитит значения всем активным коллекторам. В отличие от холодных потоков, он не перезапускается для каждого коллектора.

**Ключевые характеристики:**
- **Горячий**: Эмитит независимо от коллекторов
- **Широковещательный**: Все коллекторы получают одни и те же значения
- **Настраиваемый**: Replay, buffer и поведение при переполнении
- **Разделение состояния**: Может использоваться для событий или состояния

#### Параметры Конструктора MutableSharedFlow

```kotlin
public fun <T> MutableSharedFlow(
    replay: Int = 0,
    extraBufferCapacity: Int = 0,
    onBufferOverflow: BufferOverflow = BufferOverflow.SUSPEND
): MutableSharedFlow<T>
```

**Три ключевых параметра:**

1. **replay**: Количество значений для кеширования для поздних подписчиков
2. **extraBufferCapacity**: Дополнительный буфер помимо replay
3. **onBufferOverflow**: Что происходит когда буфер заполнен

#### Параметр Replay

Параметр `replay` указывает сколько **последних значений** кешируются и воспроизводятся для новых коллекторов:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun demonstrateReplay() = runBlocking {
    // replay = 2: Кешировать последние 2 значения
    val flow = MutableSharedFlow<Int>(replay = 2)

    // Эмитим 3 значения (коллекторов ещё нет)
    flow.emit(1)
    flow.emit(2)
    flow.emit(3)

    // Новый коллектор получает последние 2 значения (2, 3)
    launch {
        flow.collect { value ->
            println("Коллектор 1: $value")
        }
    }
    // Вывод:
    // Коллектор 1: 2
    // Коллектор 1: 3

    delay(100)
}
```

**Поведение replay:**

| Значение replay | Поведение | Случай использования |
|-----------------|-----------|----------------------|
| 0 | Нет replay, поздние подписчики пропускают прошлые значения | События |
| 1 | Replay последнего значения (как StateFlow) | Последнее состояние |
| N | Replay последних N значений | Недавняя история |

**Доступ к replay cache:**

```kotlin
import kotlinx.coroutines.flow.*

fun accessReplayCache() {
    val flow = MutableSharedFlow<String>(replay = 3)

    runBlocking {
        flow.emit("A")
        flow.emit("B")
        flow.emit("C")
    }

    // Доступ к кешированным значениям без сбора
    val cached: List<String> = flow.replayCache
    println("Кешировано: $cached") // [A, B, C]
}
```

#### Параметр extraBufferCapacity

`extraBufferCapacity` добавляет буферное пространство **помимо** replay cache для **медленных коллекторов**:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun demonstrateExtraBuffer() = runBlocking {
    // replay = 0, но buffer = 2 для медленных коллекторов
    val flow = MutableSharedFlow<Int>(
        replay = 0,
        extraBufferCapacity = 2
    )

    // Быстрый эмиттер
    launch {
        repeat(5) {
            println("Эмитим $it")
            flow.emit(it)
            delay(10)
        }
    }

    // Медленный коллектор (обрабатывает 100мс на значение)
    launch {
        delay(50) // Начинает поздно
        flow.collect { value ->
            println("Собираем $value")
            delay(100) // Медленная обработка
        }
    }

    delay(1000)
}
```

**Общая ёмкость буфера:**

```
Общая ёмкость = replay + extraBufferCapacity
```

#### Параметр onBufferOverflow

Когда общий буфер заполнен, `onBufferOverflow` определяет что происходит:

```kotlin
enum class BufferOverflow {
    SUSPEND,    // Приостановить эмиттер (обратное давление)
    DROP_OLDEST, // Удалить самое старое значение, добавить новое
    DROP_LATEST  // Удалить новое значение, сохранить существующие
}
```

**1. BufferOverflow.SUSPEND (по умолчанию)**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun demonstrateSuspend() = runBlocking {
    val flow = MutableSharedFlow<Int>(
        replay = 0,
        extraBufferCapacity = 2,
        onBufferOverflow = BufferOverflow.SUSPEND
    )

    // Медленный коллектор
    launch {
        flow.collect { value ->
            println("Собрано: $value")
            delay(200) // Медленно
        }
    }

    // Быстрый эмиттер
    launch {
        repeat(5) { i ->
            println("Эмитим $i")
            flow.emit(i) // Приостановится когда буфер заполнен
        }
    }

    delay(2000)
}
// Обеспечивает обратное давление
```

**2. BufferOverflow.DROP_OLDEST**

```kotlin
fun demonstrateDropOldest() = runBlocking {
    val flow = MutableSharedFlow<Int>(
        replay = 1,
        extraBufferCapacity = 2,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )

    // Без коллектора, просто эмитим
    repeat(5) {
        println("Эмитим $it")
        flow.emit(it) // Никогда не приостанавливается
    }

    println("Replay cache: ${flow.replayCache}")
    // Вывод: [4] (только самое последнее значение)
}
```

**3. BufferOverflow.DROP_LATEST**

```kotlin
fun demonstrateDropLatest() = runBlocking {
    val flow = MutableSharedFlow<Int>(
        replay = 1,
        extraBufferCapacity = 2,
        onBufferOverflow = BufferOverflow.DROP_LATEST
    )

    flow.emit(1)
    flow.emit(2)
    flow.emit(3)
    flow.emit(4) // Буфер полон, удаляет 4
    flow.emit(5) // Буфер полон, удаляет 5

    println("Replay cache: ${flow.replayCache}")
    // Вывод: [3] (новые значения удалены)
}
```

**Таблица сравнения:**

| Стратегия | Поведение | Случай использования | Эмиттер блокируется? |
|-----------|-----------|----------------------|----------------------|
| SUSPEND | Ждать места | Критичные данные | Да |
| DROP_OLDEST | Удалить старейшее | Важно последнее состояние | Нет |
| DROP_LATEST | Игнорировать новое | Важны первые события | Нет |

#### Примеры Из Реального Мира

**Пример 1: Шина событий (без replay)**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

sealed class AppEvent {
    data class UserLoggedIn(val userId: String) : AppEvent()
    data class UserLoggedOut(val userId: String) : AppEvent()
    data class NetworkError(val error: String) : AppEvent()
}

class EventBus {
    // События: без replay, подписчики получают только будущие события
    private val _events = MutableSharedFlow<AppEvent>(
        replay = 0,
        extraBufferCapacity = 10,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val events: SharedFlow<AppEvent> = _events

    suspend fun post(event: AppEvent) {
        _events.emit(event)
    }
}
```

**Пример 2: UI состояние с последним значением (как StateFlow)**

```kotlin
import kotlinx.coroutines.flow.*

data class UiState(
    val isLoading: Boolean = false,
    val data: String? = null,
    val error: String? = null
)

class ViewModel {
    // replay = 1: Новые коллекторы получают текущее состояние
    private val _uiState = MutableSharedFlow<UiState>(
        replay = 1,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val uiState: SharedFlow<UiState> = _uiState

    init {
        // Должны эмитить начальное значение
        runBlocking {
            _uiState.emit(UiState())
        }
    }

    suspend fun loadData() {
        _uiState.emit(UiState(isLoading = true))
        delay(1000)
        _uiState.emit(UiState(isLoading = false, data = "Загруженные данные"))
    }
}

// Примечание: StateFlow лучше для этого случая!
```

**Пример 3: Последние уведомления (replay последних N)**

```kotlin
import kotlinx.coroutines.flow.*

data class Notification(
    val id: String,
    val title: String,
    val message: String
)

class NotificationManager {
    // Хранить последние 5 уведомлений для новых наблюдателей
    private val _notifications = MutableSharedFlow<Notification>(
        replay = 5,
        extraBufferCapacity = 10,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val notifications: SharedFlow<Notification> = _notifications

    suspend fun notify(notification: Notification) {
        _notifications.emit(notification)
    }

    fun getRecentNotifications(): List<Notification> {
        return _notifications.replayCache
    }
}
```

#### Последствия Для Производительности

**Использование памяти:**

```kotlin
// Сценарий 1: Высокое использование памяти
val highMemory = MutableSharedFlow<LargeObject>(
    replay = 1000,  // Хранит 1000 объектов в памяти!
    extraBufferCapacity = 1000
)

// Сценарий 2: Низкое использование памяти
val lowMemory = MutableSharedFlow<LargeObject>(
    replay = 1,
    extraBufferCapacity = 0
)
```

#### Когда Использовать Replay Vs StateFlow

**Использовать StateFlow когда:**
- Представляете **состояние** (не события)
- Нужно ровно **одно текущее значение**
- Нужно **conflated поведение** (всегда последнее)
- Хотите более простой API (свойство `.value`)

**Использовать SharedFlow с replay когда:**
- Нужно больше 1 воспроизводимого значения
- Нужны события (может быть нулевой replay)
- Нужен контроль над переполнением буфера
- Нужно различать "нет значения" от "null значение"

### Резюме

**Конфигурация SharedFlow** требует понимания трёх параметров:

- **replay**: Сколько значений получают новые коллекторы
- **extraBufferCapacity**: Буфер для медленных коллекторов
- **onBufferOverflow**: Что происходит при заполнении

**Общая ёмкость** = replay + extraBufferCapacity

Выбирайте конфигурацию на основе случая использования:
- **События**: replay=0, DROP_OLDEST
- **Состояние**: replay=1, DROP_OLDEST (или используйте StateFlow)
- **История**: replay=N, учитывайте память
- **Критичные данные**: SUSPEND для обратного давления

---

## Follow-ups

1. How does SharedFlow's replay cache interact with Flow operators like `distinctUntilChanged()` or `filter()`? Are replay values subject to these transformations?

2. What happens to the replay cache when a SharedFlow is collected with `take(n)` where n < replay size? Does it affect other collectors?

3. How would you implement a custom buffer overflow strategy beyond the three provided options (SUSPEND, DROP_OLDEST, DROP_LATEST)?

4. Explain the thread-safety guarantees of SharedFlow when multiple coroutines call `emit()` concurrently.

5. How does SharedFlow's performance compare to BroadcastChannel (deprecated)? What improvements were made?

6. Can you explain the memory implications of using `replay = Int.MAX_VALUE`? How would you implement a size-limited history buffer?

7. How would you implement a "sticky" event bus where certain events replay indefinitely while others don't?

## References

- [Kotlin SharedFlow Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/)
- [MutableSharedFlow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-mutable-shared-flow/)
- [BufferOverflow Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/-buffer-overflow/)
- [Roman Elizarov - SharedFlow and StateFlow](https://elizarov.medium.com/shared-flows-broadcast-channels-899b675e805c)
- [Kotlin Flow Guide](https://kotlinlang.org/docs/flow.html)

## Related Questions

### Related ("medium")
- [[q-testing-stateflow-sharedflow--kotlin--medium]] - Coroutines
- [[q-stateflow-sharedflow-android--kotlin--medium]] - Coroutines
- [[q-stateflow-sharedflow-differences--kotlin--medium]] - Stateflow
- [[q-sharedflow-stateflow--kotlin--medium]] - Flow

### Related (Medium)
- [[q-hot-cold-flows--kotlin--medium]] - Hot vs Cold flows
- [[q-cold-vs-hot-flows--kotlin--medium]] - Cold vs Hot flows explained
- [[q-flow-vs-livedata-comparison--kotlin--medium]] - Flow vs LiveData
- [[q-channels-vs-flow--kotlin--medium]] - Channels vs Flow
- [[q-sharedflow-stateflow--kotlin--medium]] - SharedFlow vs StateFlow

### Advanced (Harder)
- [[q-channel-pipelines--kotlin--hard]] - Channels
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction

## Tags
#kotlin #coroutines #sharedflow #replay #buffer #backpressure #hot-flow #stateflow

