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
related: [c-flow, c-kotlin, q-channels-vs-flow--kotlin--medium]
created: 2025-10-12
updated: 2025-11-09
tags: [backpressure, buffer, configuration, coroutines, difficulty/medium, flow, hot-flow, kotlin, replay, sharedflow]
contributors: []

date created: Friday, October 31st 2025, 6:30:54 pm
date modified: Tuesday, November 25th 2025, 8:53:49 pm
---

# Вопрос (RU)
> Как настроить replay cache и buffer в `SharedFlow`? Объясните параметры `replay`, `extraBufferCapacity` и `onBufferOverflow`, их взаимодействие и реальные сценарии использования с учётом производительности.

# Question (EN)
> How do you configure `SharedFlow`'s replay cache and buffer? Explain the `replay`, `extraBufferCapacity`, and `onBufferOverflow` parameters, their interactions, and real-world usage scenarios with performance considerations.

## Ответ (RU)

#### Понимание `SharedFlow`

`SharedFlow` — это **горячий поток**, который эмитит значения всем активным коллекторам. В отличие от холодных потоков, он не перезапускается для каждого коллектора.

**Ключевые характеристики:**
- **Горячий**: Эмитит независимо от наличия коллекторов
- **Широковещательный**: Все коллектора получают одни и те же значения
- **Настраиваемый**: `replay`, буфер и поведение при переполнении
- **Разделение состояния**: Может использоваться и для событий, и для состояния

#### Параметры Конструктора `MutableSharedFlow`

```kotlin
public fun <T> MutableSharedFlow(
    replay: Int = 0,
    extraBufferCapacity: Int = 0,
    onBufferOverflow: BufferOverflow = BufferOverflow.SUSPEND
): MutableSharedFlow<T>
```

**Три ключевых параметра:**

1. `replay`: Количество значений, кешируемых для поздних подписчиков
2. `extraBufferCapacity`: Дополнительные слоты буфера помимо `replay`
3. `onBufferOverflow`: Что происходит, когда общий буфер заполнен (`replay + extraBufferCapacity`)

#### Параметр `replay`

Параметр `replay` задаёт, сколько **последних значений** кешируется и воспроизводится новым коллекторам:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun demonstrateReplayRu() = runBlocking {
    // replay = 2: кешируем последние 2 значения
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
    // Один из возможных выводов:
    // Коллектор 1: 2
    // Коллектор 1: 3

    delay(100)

    // Эмитим ещё одно значение
    flow.emit(4)
    // Коллектор 1 также получит 4

    // Новый коллектор получает последние 2 значения (3, 4)
    launch {
        flow.collect { value ->
            println("Коллектор 2: $value")
        }
    }
    // Один из возможных выводов (для второго коллектора):
    // Коллектор 2: 3
    // Коллектор 2: 4

    delay(100)
}
```

**Поведение `replay`:**

| Значение replay | Поведение | Сценарий использования |
|-----------------|-----------|------------------------|
| 0 | Нет replay, поздние подписчики не видят прошлые значения | События |
| 1 | Повторяется последнее значение (похоже на `StateFlow`) | Текущее состояние |
| N | Повторяются последние N значений | Недавняя история |

(Очень большие значения `replay`, например `Int.MAX_VALUE`, почти всегда нецелесообразны из-за памяти.)

**Доступ к replay cache:**

```kotlin
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.runBlocking

fun accessReplayCacheRu() = runBlocking {
    val flow = MutableSharedFlow<String>(replay = 3)

    flow.emit("A")
    flow.emit("B")
    flow.emit("C")

    val cached: List<String> = flow.replayCache
    println("Кешировано: $cached") // [A, B, C]
}
```

#### Параметр `extraBufferCapacity`

`extraBufferCapacity` добавляет буферное пространство **сверх** `replay` для поддержки **медленных коллекторов**:

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun demonstrateExtraBufferRu() = runBlocking {
    // replay = 0, но есть extraBufferCapacity = 2 для медленного коллектора
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

    // Медленный коллектор
    launch {
        delay(50) // начинает позже
        flow.collect { value ->
            println("Собираем $value")
            delay(100)
        }
    }

    delay(1000)
}

// Общая идея: эмиттер может немного "убегать вперёд", не блокируясь сразу.
```

**Общая ёмкость буфера:**

```
Общая ёмкость = replay + extraBufferCapacity
```

#### Параметр `onBufferOverflow`

Когда общий буфер (`replay + extraBufferCapacity`) заполнен, `onBufferOverflow` определяет поведение при попытке эмитировать новое значение:

```kotlin
enum class BufferOverflow {
    SUSPEND,     // Приостановить эмиттера (backpressure)
    DROP_OLDEST, // Удалить самое старое значение и добавить новое
    DROP_LATEST  // Отбросить новое значение, сохранить существующие
}
```

Важно: политика применяется только если буфер уже заполнен; до этого все значения записываются без потерь.

**1. `BufferOverflow.SUSPEND` (по умолчанию)**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun demonstrateSuspendRu() = runBlocking {
    val flow = MutableSharedFlow<Int>(
        replay = 0,
        extraBufferCapacity = 2,
        onBufferOverflow = BufferOverflow.SUSPEND
    )

    // Медленный коллектор
    launch {
        flow.collect { value ->
            println("Собрано: $value")
            delay(200)
        }
    }

    // Быстрый эмиттер
    launch {
        repeat(5) { i ->
            println("Эмитим $i")
            flow.emit(i) // при заполнении буфера будет приостановлен, пока не появится место
        }
    }

    delay(2000)
}

// Обеспечивает обратное давление: эмиттер не может бесконечно опережать потребителя.
```

**2. `BufferOverflow.DROP_OLDEST`**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun demonstrateDropOldestRu() = runBlocking {
    val flow = MutableSharedFlow<Int>(
        replay = 1,
        extraBufferCapacity = 2,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )

    // Общая ёмкость буфера = 3; первые 3 значения будут сохранены полностью.
    repeat(5) {
        println("Эмитим $it")
        flow.emit(it)
    }

    println("Replay cache: ${flow.replayCache}")
    // При такой конфигурации и отсутствии коллекторов в конце останется одно последнее значение,
    // так как replay = 1 хранит только последний элемент.
    // DROP_OLDEST влияет на то, какие значения попадут в буфер при переполнении,
    // но не увеличивает размер replay-кеша.
}
```

**3. `BufferOverflow.DROP_LATEST`**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun demonstrateDropLatestRu() = runBlocking {
    val flow = MutableSharedFlow<Int>(
        replay = 1,
        extraBufferCapacity = 2,
        onBufferOverflow = BufferOverflow.DROP_LATEST
    )

    // Общая ёмкость = 3. Первые 3 значения будут сохранены; дальнейшие,
    // при заполненном буфере, могут быть отброшены согласно DROP_LATEST.
    flow.emit(1)
    flow.emit(2)
    flow.emit(3)
    flow.emit(4) // может быть отброшено, если буфер полон
    flow.emit(5) // аналогично

    println("Replay cache: ${flow.replayCache}")
    // Здесь replayCache гарантированно содержит только один элемент (из-за replay = 1),
    // но конкретное значение зависит от того, какие значения были отброшены
    // в момент переполнения. Не следует полагаться на это как на детерминированный сценарий
    // без учёта временных характеристик.
}
```

**Сравнение стратегий:**

| Стратегия | Поведение | Сценарий использования | Эмиттер блокируется? |
|-----------|-----------|------------------------|----------------------|
| SUSPEND | Ждёт освобождения места | Критичные данные | Да |
| DROP_OLDEST | Удаляет старейшее значение при полном буфере | Важно последнее состояние | Нет |
| DROP_LATEST | Отбрасывает новое значение при полном буфере | Важны ранние события | Нет |

#### Совместная Работа `replay` И Буфера

Общий размер буфера — это `replay + extraBufferCapacity`, а выбранная стратегия `onBufferOverflow` определяет, что делать при переполнении. При этом:
- `replay` задаёт, сколько последних значений гарантированно доступны новым коллекторам.
- `extraBufferCapacity` влияет на то, сколько значений может быть "в пути" для текущих коллекторов.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun demonstrateReplayAndBufferRu() = runBlocking {
    val flow = MutableSharedFlow<String>(
        replay = 2,
        extraBufferCapacity = 3,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )

    repeat(10) {
        flow.emit("Value-$it")
    }

    println("Replay cache: ${flow.replayCache}")
    // Ожидаемо для этой конфигурации: в replayCache два последних значения (Value-8, Value-9),
    // так как replay = 2.

    launch {
        flow.take(2).collect { value ->
            println("Collected: $value")
        }
    }

    delay(100)
}
```

#### Визуализация Расположения replay/buffer

```
Конфигурация: replay=2, extraBufferCapacity=3, onBufferOverflow=DROP_OLDEST

[Replay Cache (2)] [Extra Buffer (3)]
    Slot 1             Slot 3
    Slot 2             Slot 4
                      Slot 5

Общая ёмкость: 5

При переполнении и поступлении нового значения:
- DROP_OLDEST: удалить самый старый элемент и добавить новый
- DROP_LATEST: проигнорировать новое значение
- SUSPEND: приостановить эмиттера до появления свободного места
```

#### Поведение Для Поздних Подписчиков

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun demonstrateLateSubscriberRu() = runBlocking {
    val flow = MutableSharedFlow<Int>(replay = 3)

    launch {
        repeat(10) {
            println("Эмитим $it")
            flow.emit(it)
            delay(50)
        }
    }

    delay(250)

    launch {
        println("Поздний подписчик начинает...")
        flow.collect { value ->
            println("Поздний подписчик получил: $value")
        }
    }

    delay(1000)
}

// Поздний подписчик сначала получает последние 3 значения на момент подписки,
// затем — новые эмиссии.
```

#### Примеры Из Реального Мира

**Пример 1: Шина событий (без replay) с несколькими подписчиками**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

sealed class AppEvent {
    data class UserLoggedIn(val userId: String) : AppEvent()
    data class UserLoggedOut(val userId: String) : AppEvent()
    data class NetworkError(val error: String) : AppEvent()
}

class EventBusRu {
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

suspend fun demonstrateEventBusRu() = coroutineScope {
    val eventBus = EventBusRu()

    // Подписчик 1
    val job1 = launch {
        eventBus.events.collect { event ->
            println("Подписчик 1: $event")
        }
    }

    // Подписчик 2 (начинает позже и пропускает ранние события)
    val job2 = launch {
        delay(100)
        eventBus.events.collect { event ->
            println("Подписчик 2: $event")
        }
    }

    // Публикуем события
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

**Пример 2: UI-состояние с последним значением (как `StateFlow`)**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

data class UiStateRu(
    val isLoading: Boolean = false,
    val data: String? = null,
    val error: String? = null
)

class ViewModelRu {
    // replay = 1: новые коллектора сразу получают текущее состояние
    private val _uiState = MutableSharedFlow<UiStateRu>(
        replay = 1,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val uiState: SharedFlow<UiStateRu> = _uiState

    init {
        // В реальном коде лучше использовать viewModelScope; runBlocking здесь только для примера.
        runBlocking {
            _uiState.emit(UiStateRu())
        }
    }

    suspend fun loadData() {
        _uiState.emit(UiStateRu(isLoading = true))
        delay(1000)
        _uiState.emit(UiStateRu(isLoading = false, data = "Загруженные данные"))
    }
}

// Для такого сценария обычно лучше подходит `StateFlow`.
```

**Пример 3: Последние уведомления (replay последних N)**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

data class NotificationRu(
    val id: String,
    val title: String,
    val message: String,
    val timestamp: Long = System.currentTimeMillis()
)

class NotificationManagerRu {
    // Храним последние 5 уведомлений для новых наблюдателей
    private val _notifications = MutableSharedFlow<NotificationRu>(
        replay = 5,
        extraBufferCapacity = 10,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val notifications: SharedFlow<NotificationRu> = _notifications

    suspend fun notify(notification: NotificationRu) {
        _notifications.emit(notification)
    }

    fun getRecentNotifications(): List<NotificationRu> = _notifications.replayCache
}

suspend fun demonstrateNotificationsRu() = coroutineScope {
    val manager = NotificationManagerRu()

    // Эмитим несколько уведомлений
    repeat(10) { i ->
        manager.notify(
            NotificationRu(
                id = "notif-$i",
                title = "Уведомление $i",
                message = "Сообщение $i"
            )
        )
        delay(50)
    }

    // Новый наблюдатель получает последние 5
    manager.notifications.take(5).collect { notif ->
        println("Получено: ${notif.title}")
    }
}
```

**Пример 4: Мульти-подписчики с буферизацией**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

class DataPublisherRu {
    private val _data = MutableSharedFlow<Int>(
        replay = 1,
        extraBufferCapacity = 32,
        onBufferOverflow = BufferOverflow.SUSPEND
    )
    val data: SharedFlow<Int> = _data

    suspend fun publish() {
        repeat(100) { i ->
            _data.emit(i)
            delay(10)
        }
    }
}

suspend fun demonstrateMultiSubscriberRu() = coroutineScope {
    val publisher = DataPublisherRu()

    // Быстрый потребитель
    launch {
        publisher.data.collect { value ->
            println("Fast: $value")
        }
    }

    // Медленный потребитель
    launch {
        publisher.data.collect { value ->
            println("Slow: $value")
            delay(50)
        }
    }

    // Поздний потребитель (использует replay/buffer)
    launch {
        delay(200)
        publisher.data.collect { value ->
            println("Late: $value")
            delay(20)
        }
    }

    launch { publisher.publish() }

    delay(2000)
}
```

#### Последствия Для Производительности

Основные выводы:
- Чем больше `replay` и `extraBufferCapacity`, тем выше потребление памяти.
- `SUSPEND` может замедлить эмиттера (backpressure), но сохраняет данные.
- DROP-стратегии (`DROP_OLDEST`, `DROP_LATEST`) разгружают эмиттера ценой потери событий.

```kotlin
import kotlinx.coroutines.flow.*

data class LargeObjectRu(val data: ByteArray)

// Сценарий с высоким потреблением памяти
val highMemoryRu = MutableSharedFlow<LargeObjectRu>(
    replay = 1000,
    extraBufferCapacity = 1000
)

// Более экономичный сценарий
val lowMemoryRu = MutableSharedFlow<LargeObjectRu>(
    replay = 1,
    extraBufferCapacity = 0
)
```

**Тестирование конфигураций `SharedFlow` (RU)**

Ниже — примерные тесты, иллюстрирующие поведение. Они демонстрационные; при использовании `runTest` и `delay` важно правильно учитывать виртуальное время тестового диспетчера.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.test.*
import org.junit.Test
import kotlin.test.assertEquals

class SharedFlowTestsRu {
    @Test
    fun testReplayCacheRu() = runTest {
        val flow = MutableSharedFlow<Int>(replay = 3)

        flow.emit(1)
        flow.emit(2)
        flow.emit(3)

        assertEquals(listOf(1, 2, 3), flow.replayCache)

        flow.emit(4)
        assertEquals(listOf(2, 3, 4), flow.replayCache)
    }

    @Test
    fun testLateSubscriberRu() = runTest {
        val flow = MutableSharedFlow<Int>(replay = 2)

        flow.emit(1)
        flow.emit(2)
        flow.emit(3)

        val collected = mutableListOf<Int>()
        flow.take(3).collect { collected.add(it) }

        // Первые два значения в collected приходят из replay: (2, 3)
        assertEquals(listOf(2, 3), collected.take(2))
    }

    @Test
    fun testBufferOverflowSuspendRu() = runTest {
        val flow = MutableSharedFlow<Int>(
            extraBufferCapacity = 2,
            onBufferOverflow = BufferOverflow.SUSPEND
        )

        var emitCount = 0

        // Медленный коллектор (используем виртуальное время тестового диспетчера)
        launch {
            flow.collect {
                delay(100)
            }
        }

        val emitter = launch {
            repeat(10) {
                flow.emit(it)
                emitCount++
            }
        }

        advanceTimeBy(150)

        // Консервативная проверка: предполагаем, что при SUSPEND эмиттер не смог мгновенно отправить все 10 значений
        assert(emitCount < 10)

        emitter.cancel()
    }

    @Test
    fun testBufferOverflowDropRu() = runTest {
        val flow = MutableSharedFlow<Int>(
            replay = 1,
            extraBufferCapacity = 2,
            onBufferOverflow = BufferOverflow.DROP_OLDEST
        )

        repeat(10) { flow.emit(it) }

        // replay = 1 гарантирует, что останется только последнее значение,
        // DROP_OLDEST влияет только на то, какие значения будут отброшены по пути.
        assertEquals(listOf(9), flow.replayCache)
    }
}
```

**Детализированные бенчмарки (RU)**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*
import kotlin.system.measureTimeMillis

suspend fun benchmarkReplayRu() {
    val flow = MutableSharedFlow<Int>(replay = 1000)

    repeat(1000) { flow.emit(it) }

    val time = measureTimeMillis {
        flow.take(1000).collect { }
    }

    println("Replay 1000 значений занял: ${time}ms")
}

suspend fun benchmarkOverflowRu() = coroutineScope {
    val suspendFlow = MutableSharedFlow<Int>(
        extraBufferCapacity = 10,
        onBufferOverflow = BufferOverflow.SUSPEND
    )

    val dropFlow = MutableSharedFlow<Int>(
        extraBufferCapacity = 10,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )

    val suspendTime = measureTimeMillis {
        launch {
            suspendFlow.collect { delay(100) }
        }
        repeat(100) { suspendFlow.emit(it) }
    }

    val dropTime = measureTimeMillis {
        launch {
            dropFlow.collect { delay(100) }
        }
        repeat(100) { dropFlow.emit(it) }
    }

    println("SUSPEND: ${suspendTime}ms")
    println("DROP_OLDEST: ${dropTime}ms")
}
```

#### Когда Использовать `replay` Vs `StateFlow`

**`StateFlow` стоит использовать, когда:**
- Представляется **состояние**, а не события
- Нужен один «текущий снимок»
- Нужна семантика "всегда последнее" (conflated)
- Удобно иметь свойство `.value`

**`SharedFlow` с `replay` стоит использовать, когда:**
- Нужно более одного воспроизводимого значения
- Нужны event-паттерны (с `replay = 0` или малым значением)
- Важно контролировать переполнение буфера
- Нужно различать "нет значения" и `null`

### Резюме (RU)

Конфигурация `SharedFlow` опирается на три параметра:

- `replay`: Сколько значений получают новые коллектора (0 = только будущие события, 1 = текущее состояние, N = история)
- `extraBufferCapacity`: Дополнительный буфер для медленных потребителей
- `onBufferOverflow`: Стратегия при переполнении (`SUSPEND`, `DROP_OLDEST`, `DROP_LATEST`)

**Общая ёмкость** = `replay + extraBufferCapacity`.

Типичные конфигурации:
- События: `replay = 0`, `DROP_OLDEST`
- Состояние: `replay = 1`, `DROP_OLDEST` (или `StateFlow`)
- История: `replay = N`, с контролем памяти
- Критичные данные: `SUSPEND` + разумный буфер

## Answer (EN)

### Understanding `SharedFlow`

`SharedFlow` is a hot flow that emits values to all active collectors. Unlike cold flows, it doesn't restart for each collector.

Key characteristics:
- Hot: Emits regardless of collectors
- Broadcast: All collectors receive the same values
- Configurable: `replay`, buffer, and overflow behavior
- State-sharing: Can be used for events or state

### `MutableSharedFlow` Constructor Parameters

```kotlin
public fun <T> MutableSharedFlow(
    replay: Int = 0,
    extraBufferCapacity: Int = 0,
    onBufferOverflow: BufferOverflow = BufferOverflow.SUSPEND
): MutableSharedFlow<T>
```

- `replay`: Number of values to cache for late subscribers
- `extraBufferCapacity`: Additional buffer beyond `replay`
- `onBufferOverflow`: What happens when total buffer (`replay + extraBufferCapacity`) is full

### The `replay` Parameter

The `replay` parameter specifies how many most recent values are cached and replayed to new collectors.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun demonstrateReplay() = runBlocking {
    val flow = MutableSharedFlow<Int>(replay = 2)

    flow.emit(1)
    flow.emit(2)
    flow.emit(3)

    launch {
        flow.collect { value ->
            println("Collector 1: $value")
        }
    }

    // One possible output:
    // Collector 1: 2
    // Collector 1: 3

    delay(100)
    flow.emit(4)

    // Collector 1 will also receive 4

    launch {
        flow.collect { value ->
            println("Collector 2: $value")
        }
    }

    // One possible output for collector 2:
    // Collector 2: 3
    // Collector 2: 4

    delay(100)
}
```

Replay behavior examples:
- `replay = 0`: Events only, no history
- `replay = 1`: Last value only (similar to `StateFlow`)
- `replay = N`: Last N values (history)

Very large `replay` values like `Int.MAX_VALUE` are usually impractical due to memory.

```kotlin
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.runBlocking

fun accessReplayCache() = runBlocking {
    val flow = MutableSharedFlow<String>(replay = 3)
    flow.emit("A")
    flow.emit("B")
    flow.emit("C")
    val cached: List<String> = flow.replayCache
    println("Cached: $cached") // [A, B, C]
}
```

### The `extraBufferCapacity` Parameter

`extraBufferCapacity` adds buffer space beyond `replay` for slow collectors.

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun demonstrateExtraBuffer() = runBlocking {
    val flow = MutableSharedFlow<Int>(
        replay = 0,
        extraBufferCapacity = 2
    )

    launch {
        repeat(5) {
            println("Emitting $it")
            flow.emit(it)
            delay(10)
        }
    }

    launch {
        delay(50)
        flow.collect { value ->
            println("Collecting $value")
            delay(100)
        }
    }

    delay(1000)
}
```

Total capacity = `replay + extraBufferCapacity`.

### The `onBufferOverflow` Parameter

When total buffer (`replay + extraBufferCapacity`) is full, `onBufferOverflow` controls behavior for new emissions.

```kotlin
enum class BufferOverflow {
    SUSPEND,
    DROP_OLDEST,
    DROP_LATEST
}
```

- `SUSPEND`: Backpressure, emitter suspends until space is available
- `DROP_OLDEST`: Drop oldest buffered value and append new value
- `DROP_LATEST`: Drop the new value, keep existing buffer

Note: the strategy applies only when the buffer is already full.

Example: `SUSPEND`:

```kotlin
fun demonstrateSuspend() = runBlocking {
    val flow = MutableSharedFlow<Int>(
        replay = 0,
        extraBufferCapacity = 2,
        onBufferOverflow = BufferOverflow.SUSPEND
    )

    launch {
        flow.collect { value ->
            println("Collected: $value")
            delay(200)
        }
    }

    launch {
        repeat(5) { i ->
            println("Emitting $i at ${System.currentTimeMillis()}")
            flow.emit(i) // suspends when buffer is full
            println("Emitted $i")
        }
    }

    delay(2000)
}
```

Example: `DROP_OLDEST`:

```kotlin
fun demonstrateDropOldest() = runBlocking {
    val flow = MutableSharedFlow<Int>(
        replay = 1,
        extraBufferCapacity = 2,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )

    // Total capacity = 3. First 3 emissions fit; subsequent emissions cause
    // the oldest buffered value to be dropped.
    repeat(5) {
        println("Emitting $it")
        flow.emit(it)
    }

    println("Replay cache: ${flow.replayCache}")
    // With replay = 1, only the last value is kept in replayCache.
    // DROP_OLDEST controls which values are dropped on overflow,
    // but does not change replay size.
}
```

Example: `DROP_LATEST`:

```kotlin
fun demonstrateDropLatest() = runBlocking {
    val flow = MutableSharedFlow<Int>(
        replay = 1,
        extraBufferCapacity = 2,
        onBufferOverflow = BufferOverflow.DROP_LATEST
    )

    // Total capacity = 3. The first 3 emissions are stored; further emissions
    // when full may be dropped according to DROP_LATEST.
    flow.emit(1)
    flow.emit(2)
    flow.emit(3)
    flow.emit(4) // may be dropped if buffer is full
    flow.emit(5) // may also be dropped

    println("Replay cache: ${flow.replayCache}")
    // replayCache will contain exactly one value (because replay = 1),
    // but which one depends on overflow timing; don't rely on this pattern
    // as a deterministic example without controlled scheduling.
}
```

### How Replay and Buffer Work Together

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun demonstrateReplayAndBuffer() = runBlocking {
    val flow = MutableSharedFlow<String>(
        replay = 2,
        extraBufferCapacity = 3,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )

    repeat(10) {
        flow.emit("Value-$it")
    }

    println("Replay cache: ${flow.replayCache}")
    // With replay = 2, replayCache will contain the last two values, e.g. [Value-8, Value-9].

    launch {
        flow.take(2).collect { value ->
            println("Collected: $value")
        }
    }

    delay(100)
}
```

### Visualization

```
Configuration: replay=2, extraBufferCapacity=3, onBufferOverflow=DROP_OLDEST

[Replay Cache (2)] [Extra Buffer (3)]
    Slot 1             Slot 3
    Slot 2             Slot 4
                      Slot 5

Total capacity: 5

When full and new value arrives:
- DROP_OLDEST: Remove oldest buffered element, append new
- DROP_LATEST: Ignore new value
- SUSPEND: Suspend emitter until space available
```

### Real-World Examples

Example 1: Event bus (no replay) with multiple subscribers:

```kotlin
class EventBus {
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

suspend fun demonstrateEventBus() = coroutineScope {
    val eventBus = EventBus()

    val job1 = launch {
        eventBus.events.collect { event ->
            println("Subscriber 1: $event")
        }
    }

    val job2 = launch {
        delay(100)
        eventBus.events.collect { event ->
            println("Subscriber 2: $event")
        }
    }

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

Example 2: UI state with latest value (like `StateFlow`):

```kotlin
data class UiState(
    val isLoading: Boolean = false,
    val data: String? = null,
    val error: String? = null
)

class ViewModel {
    private val _uiState = MutableSharedFlow<UiState>(
        replay = 1,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val uiState: SharedFlow<UiState> = _uiState

    init {
        // In real apps prefer a proper scope; runBlocking only for illustration.
        runBlocking {
            _uiState.emit(UiState())
        }
    }

    suspend fun loadData() {
        _uiState.emit(UiState(isLoading = true))
        delay(1000)
        _uiState.emit(UiState(isLoading = false, data = "Loaded data"))
    }
}

// Note: `StateFlow` is usually better for this use case.
```

Example 3: Recent notifications (replay last N):

```kotlin
data class Notification(
    val id: String,
    val title: String,
    val message: String,
    val timestamp: Long = System.currentTimeMillis()
)

class NotificationManager {
    private val _notifications = MutableSharedFlow<Notification>(
        replay = 5,
        extraBufferCapacity = 10,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val notifications: SharedFlow<Notification> = _notifications

    suspend fun notify(notification: Notification) {
        _notifications.emit(notification)
    }

    fun getRecentNotifications(): List<Notification> = _notifications.replayCache
}
```

Example 4: Multi-subscriber scenario with buffering:

```kotlin
class DataPublisher {
    private val _data = MutableSharedFlow<Int>(
        replay = 1,
        extraBufferCapacity = 32,
        onBufferOverflow = BufferOverflow.SUSPEND
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

    launch {
        publisher.data.collect { value ->
            println("Fast: $value")
        }
    }

    launch {
        publisher.data.collect { value ->
            println("Slow: $value")
            delay(50)
        }
    }

    launch {
        delay(200)
        publisher.data.collect { value ->
            println("Late: $value")
            delay(20)
        }
    }

    launch { publisher.publish() }

    delay(2000)
}
```

### Late Subscriber Behavior

```kotlin
fun demonstrateLateSubscriber() = runBlocking {
    val flow = MutableSharedFlow<Int>(replay = 3)

    launch {
        repeat(10) {
            println("Emitting $it")
            flow.emit(it)
            delay(50)
        }
    }

    delay(250)

    launch {
        println("Late subscriber starting...")
        flow.collect { value ->
            println("Late subscriber received: $value")
        }
    }

    delay(1000)
}

// Late subscriber first receives last 3 values from replay, then new emissions.
```

### Performance Implications

Memory usage:

```kotlin
data class LargeObject(val data: ByteArray)

val highMemory = MutableSharedFlow<LargeObject>(
    replay = 1000,
    extraBufferCapacity = 1000
)

val lowMemory = MutableSharedFlow<LargeObject>(
    replay = 1,
    extraBufferCapacity = 0
)
```

Replay benchmark:

```kotlin
suspend fun benchmarkReplay() {
    val flow = MutableSharedFlow<Int>(replay = 1000)

    repeat(1000) { flow.emit(it) }

    val time = measureTimeMillis {
        flow.take(1000).collect { }
    }

    println("Replay of 1000 values took: ${time}ms")
}
```

Overflow benchmark:

```kotlin
suspend fun benchmarkOverflow() = coroutineScope {
    val suspendFlow = MutableSharedFlow<Int>(
        extraBufferCapacity = 10,
        onBufferOverflow = BufferOverflow.SUSPEND
    )

    val dropFlow = MutableSharedFlow<Int>(
        extraBufferCapacity = 10,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )

    val suspendTime = measureTimeMillis {
        launch {
            suspendFlow.collect { delay(100) }
        }
        repeat(100) { suspendFlow.emit(it) }
    }

    val dropTime = measureTimeMillis {
        launch {
            dropFlow.collect { delay(100) }
        }
        repeat(100) { dropFlow.emit(it) }
    }

    println("SUSPEND: ${suspendTime}ms")
    println("DROP_OLDEST: ${dropTime}ms")
}
```

### When to Use Replay Vs `StateFlow`

Use `StateFlow` when:
- Representing state, not events
- You need exactly one current value
- You want conflated "latest only" behavior
- You need `.value` API

Use `SharedFlow` with `replay` when:
- You need more than one replayed value
- You need event-style patterns (`replay = 0` or small)
- You need explicit buffer overflow control
- You need to distinguish "no value" from `null`

```kotlin
val stateFlow = MutableStateFlow("initial")

val sharedFlow = MutableSharedFlow<String>(
    replay = 1,
    onBufferOverflow = BufferOverflow.DROP_OLDEST
).apply {
    tryEmit("initial")
}
```

### Testing `SharedFlow` Configurations

```kotlin
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
        flow.take(3).collect { collected.add(it) }

        // First two values come from replay: (2, 3)
        assertEquals(listOf(2, 3), collected.take(2))
    }

    @Test
    fun testBufferOverflowSuspend() = runTest {
        val flow = MutableSharedFlow<Int>(
            extraBufferCapacity = 2,
            onBufferOverflow = BufferOverflow.SUSPEND
        )

        var emitCount = 0

        launch {
            flow.collect {
                delay(100)
            }
        }

        val emitter = launch {
            repeat(10) {
                flow.emit(it)
                emitCount++
            }
        }

        advanceTimeBy(150)

        // Conservative: with SUSPEND, emitter should not be able to emit all 10 immediately
        assert(emitCount < 10)

        emitter.cancel()
    }

    @Test
    fun testBufferOverflowDrop() = runTest {
        val flow = MutableSharedFlow<Int>(
            replay = 1,
            extraBufferCapacity = 2,
            onBufferOverflow = BufferOverflow.DROP_OLDEST
        )

        repeat(10) { flow.emit(it) }

        // replay = 1 ensures only the last value is retained in replayCache.
        assertEquals(listOf(9), flow.replayCache)
    }
}
```

### Summary

`SharedFlow` configuration centers on:
- `replay`: how many values new collectors receive
- `extraBufferCapacity`: additional buffer for slow collectors
- `onBufferOverflow`: strategy when buffer is full

Total capacity = `replay + extraBufferCapacity`.

Choose based on use case:
- Events: `replay = 0`, `DROP_OLDEST`
- State: `replay = 1`, `DROP_OLDEST` or `StateFlow`
- History: `replay = N`, consider memory
- Critical data: `SUSPEND` with reasonable capacity

## Дополнительные Вопросы (RU)

1. Как `replay`-кеш `SharedFlow` взаимодействует с операторами `Flow` вроде `distinctUntilChanged()` или `filter()`? Применяются ли эти трансформации к переигрываемым значениям?
2. Что происходит с `replay`-кешем при коллекции `SharedFlow` с `take(n)`, где `n` < размера `replay`? Влияет ли это на других коллекторов?
3. Как бы вы реализовали кастомную стратегию переполнения буфера помимо `SUSPEND`, `DROP_OLDEST`, `DROP_LATEST`?
4. Объясните гарантии потокобезопасности `SharedFlow` при одновременных вызовах `emit()` из нескольких корутин.
5. Как производительность `SharedFlow` сравнивается с устаревшим `BroadcastChannel` и какие улучшения были внесены?
6. Каковы последствия по памяти при использовании `replay = Int.MAX_VALUE` и как реализовать буфер истории с ограниченным размером?
7. Как реализовать "липкий" event bus, где некоторые события воспроизводятся бесконечно, а другие — нет?

## Follow-ups

1. How does `SharedFlow`'s replay cache interact with `Flow` operators like `distinctUntilChanged()` or `filter()`? Are replay values subject to these transformations?
2. What happens to the replay cache when a `SharedFlow` is collected with `take(n)` where `n` < `replay` size? Does it affect other collectors?
3. How would you implement a custom buffer overflow strategy beyond `SUSPEND`, `DROP_OLDEST`, `DROP_LATEST`?
4. Explain the thread-safety guarantees of `SharedFlow` when multiple coroutines call `emit()` concurrently.
5. How does `SharedFlow`'s performance compare to deprecated `BroadcastChannel`? What improvements were made?
6. What are the memory implications of using `replay = Int.MAX_VALUE`? How would you implement a size-limited history buffer?
7. How would you implement a "sticky" event bus where certain events replay indefinitely while others don't?

## Ссылки (RU)

- Официальная документация `SharedFlow`: https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/
- API `MutableSharedFlow`: https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-mutable-shared-flow/
- Документация `BufferOverflow`: https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/-buffer-overflow/
- Статья Roman Elizarov о `SharedFlow` и `StateFlow`: https://elizarov.medium.com/shared-flows-broadcast-channels-899b675e805c
- Гайд по `Flow`: https://kotlinlang.org/docs/flow.html
- [[c-kotlin]]
- [[c-flow]]

## References

- Kotlin `SharedFlow` Documentation: https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/
- MutableSharedFlow API: https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-mutable-shared-flow/
- BufferOverflow Documentation: https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.channels/-buffer-overflow/
- Roman Elizarov - `SharedFlow` and `StateFlow`: https://elizarov.medium.com/shared-flows-broadcast-channels-899b675e805c
- Kotlin `Flow` Guide: https://kotlinlang.org/docs/flow.html
- [[c-kotlin]]
- [[c-flow]]

## Связанные Вопросы (RU)

- [[q-testing-stateflow-sharedflow--kotlin--medium]]
- [[q-stateflow-sharedflow-android--kotlin--medium]]
- [[q-stateflow-sharedflow-differences--kotlin--medium]]
- [[q-sharedflow-stateflow--kotlin--medium]]
- [[q-hot-cold-flows--kotlin--medium]]
- [[q-cold-vs-hot-flows--kotlin--medium]]
- [[q-flow-vs-livedata-comparison--kotlin--medium]]
- [[q-channels-vs-flow--kotlin--medium]]
- [[q-channel-pipelines--kotlin--hard]]
- [[q-testing-flow-operators--kotlin--hard]]
- [[q-kotlin-flow-basics--kotlin--medium]]

## Related Questions

- [[q-testing-stateflow-sharedflow--kotlin--medium]]
- [[q-stateflow-sharedflow-android--kotlin--medium]]
- [[q-stateflow-sharedflow-differences--kotlin--medium]]
- [[q-sharedflow-stateflow--kotlin--medium]]
- [[q-hot-cold-flows--kotlin--medium]]
- [[q-cold-vs-hot-flows--kotlin--medium]]
- [[q-flow-vs-livedata-comparison--kotlin--medium]]
- [[q-channels-vs-flow--kotlin--medium]]
- [[q-channel-pipelines--kotlin--hard]]
- [[q-testing-flow-operators--kotlin--hard]]
- [[q-kotlin-flow-basics--kotlin--medium]]
