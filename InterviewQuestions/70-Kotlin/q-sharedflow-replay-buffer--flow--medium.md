---
id: kotlin-flow-010
title: SharedFlow Replay and Buffer Configuration / Настройка replay и buffer в SharedFlow
aliases:
- SharedFlow Replay Buffer
- SharedFlow Configuration
- MutableSharedFlow Setup
topic: kotlin
subtopics:
- coroutines
- flow
- sharedflow
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
source: internal
status: draft
moc: moc-kotlin
related:
- c-kotlin
- c-flow
- q-stateflow-vs-sharedflow--flow--medium
created: 2026-01-23
updated: 2026-01-23
tags:
- coroutines
- difficulty/medium
- flow
- kotlin
- sharedflow
- buffer
anki_cards:
- slug: kotlin-flow-010-0-en
  language: en
  anki_id: 1769344155540
  synced_at: '2026-01-25T16:29:15.592071'
- slug: kotlin-flow-010-0-ru
  language: ru
  anki_id: 1769344155590
  synced_at: '2026-01-25T16:29:15.593873'
---
# Vopros (RU)
> Как настроить `SharedFlow` с replay и buffer? Объясните параметры конфигурации.

---

# Question (EN)
> How to configure `SharedFlow` with replay and buffer? Explain the configuration parameters.

## Otvet (RU)

### Параметры MutableSharedFlow

```kotlin
MutableSharedFlow<T>(
    replay: Int = 0,           // Сколько последних значений получит новый подписчик
    extraBufferCapacity: Int = 0,  // Дополнительная ёмкость буфера
    onBufferOverflow: BufferOverflow = BufferOverflow.SUSPEND  // Что делать при переполнении
)
```

### Параметр replay

`replay` определяет сколько последних эмиссий получит новый подписчик:

```kotlin
// replay = 0 (по умолчанию) - новые подписчики не получают прошлые значения
val eventsFlow = MutableSharedFlow<Event>(replay = 0)

eventsFlow.emit(Event.UserLoggedIn)  // Эмитируем до подписки
eventsFlow.emit(Event.DataLoaded)

// Подписчик подключается ПОСЛЕ эмиссий
eventsFlow.collect { event ->
    // Не получит UserLoggedIn и DataLoaded
    // Получит только будущие события
}

// replay = 1 - новый подписчик получит последнее значение
val statusFlow = MutableSharedFlow<Status>(replay = 1)

statusFlow.emit(Status.Online)
statusFlow.emit(Status.Busy)  // Последнее значение

statusFlow.collect { status ->
    // Сразу получит Status.Busy
    // Затем будущие значения
}

// replay = 3 - новый подписчик получит до 3 последних значений
val notificationsFlow = MutableSharedFlow<Notification>(replay = 3)

notificationsFlow.emit(Notification(1))
notificationsFlow.emit(Notification(2))
notificationsFlow.emit(Notification(3))
notificationsFlow.emit(Notification(4))
notificationsFlow.emit(Notification(5))

notificationsFlow.collect { notification ->
    // Получит Notification(3), Notification(4), Notification(5)
    // Notification(1) и Notification(2) уже вне replay cache
}
```

### Параметр extraBufferCapacity

`extraBufferCapacity` - дополнительный буфер для эмиссий когда подписчики не успевают обрабатывать:

```kotlin
// Без буфера - emit() будет suspend пока подписчик не обработает
val slowFlow = MutableSharedFlow<Int>(
    replay = 0,
    extraBufferCapacity = 0  // Нет буфера
)

// С буфером - emit() не блокируется пока буфер не заполнен
val bufferedFlow = MutableSharedFlow<Int>(
    replay = 0,
    extraBufferCapacity = 64  // Буфер на 64 элемента
)

// Общая ёмкость = replay + extraBufferCapacity
val configuredFlow = MutableSharedFlow<Int>(
    replay = 1,               // 1 для replay
    extraBufferCapacity = 10  // + 10 дополнительно
    // Итого буфер на 11 элементов
)
```

### Параметр onBufferOverflow

Что делать когда буфер заполнен:

```kotlin
// SUSPEND (по умолчанию) - emit() приостанавливается
val suspendingFlow = MutableSharedFlow<Int>(
    extraBufferCapacity = 10,
    onBufferOverflow = BufferOverflow.SUSPEND
)

// DROP_OLDEST - отбрасывает старейшее значение
val dropOldestFlow = MutableSharedFlow<Int>(
    extraBufferCapacity = 10,
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)

// DROP_LATEST - отбрасывает новое значение (не эмитится)
val dropLatestFlow = MutableSharedFlow<Int>(
    extraBufferCapacity = 10,
    onBufferOverflow = BufferOverflow.DROP_LATEST
)
```

### Практические Конфигурации

#### События навигации (fire-and-forget)

```kotlin
// replay = 0: новый экран не должен получить старые навигационные события
// extraBufferCapacity = 1: позволяет emit() без suspend
private val _navigation = MutableSharedFlow<NavigationEvent>(
    replay = 0,
    extraBufferCapacity = 1,
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)
```

#### Сообщения/уведомления с историей

```kotlin
// replay = 10: показать последние 10 сообщений новому подписчику
private val _messages = MutableSharedFlow<Message>(
    replay = 10,
    extraBufferCapacity = 20,
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)
```

#### Быстрые события (сенсоры, ввод)

```kotlin
// Высокочастотные данные - отбрасываем старые если не успеваем
private val _sensorData = MutableSharedFlow<SensorReading>(
    replay = 1,  // Текущее значение для новых подписчиков
    extraBufferCapacity = 100,
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)
```

#### Критичные события (не терять)

```kotlin
// Важные события - suspend если буфер заполнен
private val _analyticsEvents = MutableSharedFlow<AnalyticsEvent>(
    replay = 0,
    extraBufferCapacity = 1000,
    onBufferOverflow = BufferOverflow.SUSPEND  // Не терять события
)
```

### tryEmit vs emit

```kotlin
val sharedFlow = MutableSharedFlow<Int>(
    extraBufferCapacity = 1,
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)

// emit() - suspend функция, ждёт если буфер полон и overflow = SUSPEND
viewModelScope.launch {
    sharedFlow.emit(1)  // Может приостановиться
}

// tryEmit() - non-suspend, возвращает Boolean
val emitted = sharedFlow.tryEmit(1)  // true если успешно, false если буфер полон

// tryEmit() полезен:
// 1. В callback-ах где нельзя suspend
// 2. Когда можно потерять значение
// 3. Для fire-and-forget событий
fun onClick() {
    _events.tryEmit(ClickEvent)  // Не блокирует UI thread
}
```

### Просмотр Replay Cache

```kotlin
val sharedFlow = MutableSharedFlow<Int>(replay = 3)

sharedFlow.emit(1)
sharedFlow.emit(2)
sharedFlow.emit(3)

// Получить replay cache без подписки
val replayCache: List<Int> = sharedFlow.replayCache
// [1, 2, 3]

// Очистить replay cache
sharedFlow.resetReplayCache()
```

### StateFlow vs SharedFlow с replay = 1

```kotlin
// StateFlow
val stateFlow = MutableStateFlow(0)
// - Всегда имеет значение (.value)
// - Требует начальное значение
// - distinctUntilChanged встроено
// - Нельзя настроить overflow

// SharedFlow с replay = 1
val sharedFlow = MutableSharedFlow<Int>(replay = 1)
// - Нет .value (нужно подписаться или читать replayCache)
// - Не требует начальное значение
// - Эмитит все значения (включая дубликаты)
// - Настраиваемый overflow

// Выбор:
// StateFlow - для состояния (UI state)
// SharedFlow - для событий или когда нужна кастомная логика
```

### Подписчики и Буфер

```kotlin
val flow = MutableSharedFlow<Int>(
    replay = 0,
    extraBufferCapacity = 2
)

// Сценарий: медленный подписчик
launch {
    flow.collect { value ->
        delay(1000)  // Медленная обработка
        println("Slow: $value")
    }
}

// Быстрые эмиссии
flow.emit(1)  // В буфер
flow.emit(2)  // В буфер
flow.emit(3)  // Буфер полон -> suspend (или drop по настройке)

// С DROP_OLDEST:
// emit(3) отбросит значение 1, подписчик получит 2, 3
```

---

## Answer (EN)

### MutableSharedFlow Parameters

```kotlin
MutableSharedFlow<T>(
    replay: Int = 0,           // How many recent values new subscriber gets
    extraBufferCapacity: Int = 0,  // Additional buffer capacity
    onBufferOverflow: BufferOverflow = BufferOverflow.SUSPEND  // What to do on overflow
)
```

### replay Parameter

`replay` determines how many recent emissions a new subscriber receives:

```kotlin
// replay = 0 (default) - new subscribers don't get past values
val eventsFlow = MutableSharedFlow<Event>(replay = 0)

eventsFlow.emit(Event.UserLoggedIn)  // Emit before subscription
eventsFlow.emit(Event.DataLoaded)

// Subscriber connects AFTER emissions
eventsFlow.collect { event ->
    // Won't get UserLoggedIn and DataLoaded
    // Only gets future events
}

// replay = 1 - new subscriber gets last value
val statusFlow = MutableSharedFlow<Status>(replay = 1)

statusFlow.emit(Status.Online)
statusFlow.emit(Status.Busy)  // Last value

statusFlow.collect { status ->
    // Immediately gets Status.Busy
    // Then future values
}

// replay = 3 - new subscriber gets up to 3 last values
val notificationsFlow = MutableSharedFlow<Notification>(replay = 3)

notificationsFlow.emit(Notification(1))
notificationsFlow.emit(Notification(2))
notificationsFlow.emit(Notification(3))
notificationsFlow.emit(Notification(4))
notificationsFlow.emit(Notification(5))

notificationsFlow.collect { notification ->
    // Gets Notification(3), Notification(4), Notification(5)
    // Notification(1) and Notification(2) are out of replay cache
}
```

### extraBufferCapacity Parameter

`extraBufferCapacity` - additional buffer for emissions when subscribers can't keep up:

```kotlin
// No buffer - emit() will suspend until subscriber processes
val slowFlow = MutableSharedFlow<Int>(
    replay = 0,
    extraBufferCapacity = 0  // No buffer
)

// With buffer - emit() doesn't block until buffer is full
val bufferedFlow = MutableSharedFlow<Int>(
    replay = 0,
    extraBufferCapacity = 64  // Buffer for 64 elements
)

// Total capacity = replay + extraBufferCapacity
val configuredFlow = MutableSharedFlow<Int>(
    replay = 1,               // 1 for replay
    extraBufferCapacity = 10  // + 10 additional
    // Total buffer for 11 elements
)
```

### onBufferOverflow Parameter

What to do when buffer is full:

```kotlin
// SUSPEND (default) - emit() suspends
val suspendingFlow = MutableSharedFlow<Int>(
    extraBufferCapacity = 10,
    onBufferOverflow = BufferOverflow.SUSPEND
)

// DROP_OLDEST - drops oldest value
val dropOldestFlow = MutableSharedFlow<Int>(
    extraBufferCapacity = 10,
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)

// DROP_LATEST - drops new value (not emitted)
val dropLatestFlow = MutableSharedFlow<Int>(
    extraBufferCapacity = 10,
    onBufferOverflow = BufferOverflow.DROP_LATEST
)
```

### Practical Configurations

#### Navigation events (fire-and-forget)

```kotlin
// replay = 0: new screen shouldn't get old navigation events
// extraBufferCapacity = 1: allows emit() without suspend
private val _navigation = MutableSharedFlow<NavigationEvent>(
    replay = 0,
    extraBufferCapacity = 1,
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)
```

#### Messages/notifications with history

```kotlin
// replay = 10: show last 10 messages to new subscriber
private val _messages = MutableSharedFlow<Message>(
    replay = 10,
    extraBufferCapacity = 20,
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)
```

#### Fast events (sensors, input)

```kotlin
// High-frequency data - drop old if can't keep up
private val _sensorData = MutableSharedFlow<SensorReading>(
    replay = 1,  // Current value for new subscribers
    extraBufferCapacity = 100,
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)
```

#### Critical events (don't lose)

```kotlin
// Important events - suspend if buffer full
private val _analyticsEvents = MutableSharedFlow<AnalyticsEvent>(
    replay = 0,
    extraBufferCapacity = 1000,
    onBufferOverflow = BufferOverflow.SUSPEND  // Don't lose events
)
```

### tryEmit vs emit

```kotlin
val sharedFlow = MutableSharedFlow<Int>(
    extraBufferCapacity = 1,
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)

// emit() - suspend function, waits if buffer full and overflow = SUSPEND
viewModelScope.launch {
    sharedFlow.emit(1)  // May suspend
}

// tryEmit() - non-suspend, returns Boolean
val emitted = sharedFlow.tryEmit(1)  // true if successful, false if buffer full

// tryEmit() is useful:
// 1. In callbacks where can't suspend
// 2. When value can be lost
// 3. For fire-and-forget events
fun onClick() {
    _events.tryEmit(ClickEvent)  // Doesn't block UI thread
}
```

### Inspecting Replay Cache

```kotlin
val sharedFlow = MutableSharedFlow<Int>(replay = 3)

sharedFlow.emit(1)
sharedFlow.emit(2)
sharedFlow.emit(3)

// Get replay cache without subscribing
val replayCache: List<Int> = sharedFlow.replayCache
// [1, 2, 3]

// Clear replay cache
sharedFlow.resetReplayCache()
```

### StateFlow vs SharedFlow with replay = 1

```kotlin
// StateFlow
val stateFlow = MutableStateFlow(0)
// - Always has value (.value)
// - Requires initial value
// - distinctUntilChanged built-in
// - Cannot configure overflow

// SharedFlow with replay = 1
val sharedFlow = MutableSharedFlow<Int>(replay = 1)
// - No .value (need to subscribe or read replayCache)
// - Doesn't require initial value
// - Emits all values (including duplicates)
// - Configurable overflow

// Choice:
// StateFlow - for state (UI state)
// SharedFlow - for events or when need custom logic
```

### Subscribers and Buffer

```kotlin
val flow = MutableSharedFlow<Int>(
    replay = 0,
    extraBufferCapacity = 2
)

// Scenario: slow subscriber
launch {
    flow.collect { value ->
        delay(1000)  // Slow processing
        println("Slow: $value")
    }
}

// Fast emissions
flow.emit(1)  // To buffer
flow.emit(2)  // To buffer
flow.emit(3)  // Buffer full -> suspend (or drop based on config)

// With DROP_OLDEST:
// emit(3) drops value 1, subscriber gets 2, 3
```

---

## Dopolnitelnye Voprosy (RU)

1. Как выбрать правильный размер буфера для высоконагруженных сценариев?
2. Когда использовать `DROP_OLDEST` vs `DROP_LATEST`?
3. Как мониторить заполненность буфера SharedFlow?
4. Какие проблемы могут возникнуть при большом replay cache?
5. Как тестировать SharedFlow с различными конфигурациями буфера?

---

## Follow-ups

1. How to choose the right buffer size for high-load scenarios?
2. When to use `DROP_OLDEST` vs `DROP_LATEST`?
3. How to monitor SharedFlow buffer fullness?
4. What problems can arise with large replay cache?
5. How to test SharedFlow with different buffer configurations?

---

## Ssylki (RU)

- [[c-kotlin]]
- [[c-flow]]
- [SharedFlow Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/)
- [MutableSharedFlow](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-mutable-shared-flow/)

---

## References

- [[c-kotlin]]
- [[c-flow]]
- [SharedFlow Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/)
- [MutableSharedFlow](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-mutable-shared-flow/)

---

## Svyazannye Voprosy (RU)

### Sredniy Uroven
- [[q-stateflow-vs-sharedflow--flow--medium]]
- [[q-sharedflow-replay-buffer-config--kotlin--medium]]
- [[q-backpressure-in-kotlin-flow--kotlin--medium]]

---

## Related Questions

### Related (Medium)
- [[q-stateflow-vs-sharedflow--flow--medium]] - StateFlow vs SharedFlow
- [[q-sharedflow-replay-buffer-config--kotlin--medium]] - SharedFlow configuration details
- [[q-backpressure-in-kotlin-flow--kotlin--medium]] - Backpressure handling
