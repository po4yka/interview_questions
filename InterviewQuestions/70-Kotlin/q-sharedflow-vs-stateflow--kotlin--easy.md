---
'---id': lang-019
title: SharedFlow Vs StateFlow / SharedFlow против StateFlow
aliases:
- SharedFlow Vs StateFlow
- SharedFlow против StateFlow
topic: kotlin
subtopics:
- coroutines
- flow
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-concurrency
- c-stateflow
created: 2025-10-15
updated: 2025-11-11
tags:
- coroutines
- difficulty/easy
- flow
- kotlin
- sharedflow
- stateflow
anki_cards:
- slug: q-sharedflow-vs-stateflow--kotlin--easy-0-en
  language: en
  anki_id: 1768326288007
  synced_at: '2026-01-23T17:03:51.250964'
- slug: q-sharedflow-vs-stateflow--kotlin--easy-0-ru
  language: ru
  anki_id: 1768326288032
  synced_at: '2026-01-23T17:03:51.252808'
---
# Вопрос (RU)
> Какие различия между `SharedFlow` и `StateFlow`?

# Question (EN)
> What are the differences between `SharedFlow` and `StateFlow`?

## Ответ (RU)

`SharedFlow` — это горячий поток, который передаёт значения нескольким подписчикам и может буферизировать/реплеить их (без жёстких гарантий "реального времени" — доставка зависит от планирования корутин).

`StateFlow` — это специализированный `SharedFlow`, который всегда хранит ровно одно последнее значение, сразу отдаёт его новым подписчикам и эмитит новое только если оно отличается от текущего по `equals`, то есть повторная установка того же значения не приведёт к новому эмиту.

### Сравнение Ключевых Характеристик

| Характеристика | `SharedFlow` | `StateFlow` |
|----------------|------------|-----------|
| Тип | Горячий `Flow` | Горячий `Flow` (специализированный `SharedFlow`) |
| Начальное значение | Необязательно | Обязательно |
| Хранение значений | Может буферизировать несколько значений | Всегда хранит ровно одно текущее значение |
| Реплей | Настраиваемый (от 0 до n) | Всегда реплеит 1 (текущее значение) |
| Конфлуация | Настраиваемая | Всегда конфлюирует до последнего значения |
| Уникальность значений | Может эмитить дубликаты | Пропускает эмит, если новое значение == текущему (по equals) |
| Основной кейс | События, широковещательные уведомления, потоки событий | Управление состоянием (всегда доступное текущее состояние) |

### Пример SharedFlow

```kotlin
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.collect

class EventBus {
    // MutableSharedFlow без реплея и дополнительного буфера
    private val _events = MutableSharedFlow<String>(replay = 0)
    val events: SharedFlow<String> = _events.asSharedFlow()

    suspend fun sendEvent(event: String) {
        _events.emit(event)
    }
}

fun main() = runBlocking {
    val eventBus = EventBus()

    // Первый подписчик
    launch {
        eventBus.events.collect { event ->
            println("Subscriber 1: $event")
        }
    }

    // Второй подписчик
    launch {
        eventBus.events.collect { event ->
            println("Subscriber 2: $event")
        }
    }

    delay(100)
    eventBus.sendEvent("Event 1")
    eventBus.sendEvent("Event 2")
    delay(100)

    // Третий подписчик (подключается поздно, c replay=0 не получит старые события)
    launch {
        eventBus.events.collect { event ->
            println("Subscriber 3 (late): $event")
        }
    }

    delay(100)
    eventBus.sendEvent("Event 3")
    delay(100)
}

// Возможный вывод:
// Subscriber 1: Event 1
// Subscriber 2: Event 1
// Subscriber 1: Event 2
// Subscriber 2: Event 2
// Subscriber 1: Event 3
// Subscriber 2: Event 3
// Subscriber 3 (late): Event 3
```

### Пример StateFlow

```kotlin
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.launch
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.flow.collect

data class UiState(val count: Int, val isLoading: Boolean)

class CounterViewModel {
    private val _uiState = MutableStateFlow(UiState(count = 0, isLoading = false))
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun increment() {
        _uiState.update { currentState ->
            currentState.copy(count = currentState.count + 1)
        }
    }

    fun setLoading(loading: Boolean) {
        _uiState.update { it.copy(isLoading = loading) }
    }
}

fun main() = runBlocking {
    val viewModel = CounterViewModel()

    // Подписчик 1 (сразу получает первое значение)
    launch {
        viewModel.uiState.collect { state ->
            println("Subscriber 1: count=${state.count}, loading=${state.isLoading}")
        }
    }

    delay(100)
    viewModel.increment()
    viewModel.increment()
    viewModel.setLoading(true)

    delay(100)

    // Подписчик 2 (подключается позже и сразу получает актуальное состояние)
    launch {
        viewModel.uiState.collect { state ->
            println("Subscriber 2 (late): count=${state.count}, loading=${state.isLoading}")
        }
    }

    delay(100)
}

// Вывод:
// Subscriber 1: count=0, loading=false
// Subscriber 1: count=1, loading=false
// Subscriber 1: count=2, loading=false
// Subscriber 1: count=2, loading=true
// Subscriber 2 (late): count=2, loading=true
```

### SharedFlow С Реплей-буфером

```kotlin
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.collect

class NotificationService {
    // Реплеим последние 3 события для новых подписчиков
    private val _notifications = MutableSharedFlow<String>(
        replay = 3,
        extraBufferCapacity = 10
    )
    val notifications: SharedFlow<String> = _notifications.asSharedFlow()

    suspend fun notify(message: String) {
        _notifications.emit(message)
    }
}

fun main() = runBlocking {
    val service = NotificationService()

    // Отправляем уведомления до появления подписчиков
    service.notify("Notification 1")
    service.notify("Notification 2")
    service.notify("Notification 3")
    service.notify("Notification 4")

    delay(100)

    // Новый подписчик получает последние 3 уведомления
    launch {
        service.notifications.collect { notification ->
            println("Late subscriber: $notification")
        }
    }

    delay(100)
}

// Вывод:
// Late subscriber: Notification 2
// Late subscriber: Notification 3
// Late subscriber: Notification 4
```

### StateFlow: Только Различные Значения

```kotlin
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.launch
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.collect

fun main() = runBlocking {
    val state = MutableStateFlow("Initial")

    launch {
        state.collect { value ->
            println("Collected: $value")
        }
    }

    delay(100)
    state.value = "Updated"
    state.value = "Updated"  // То же значение -> не эмитится
    state.value = "Updated"  // То же значение -> не эмитится
    state.value = "Different"
    state.value = "Different"  // То же значение -> не эмитится

    delay(100)
}

// Вывод:
// Collected: Initial
// Collected: Updated
// Collected: Different
```

### Когда Использовать SharedFlow

```kotlin
// Используйте SharedFlow для:

// 1. Широковещательной отправки событий (клики, навигация)
class NavigationEvents {
    private val _navEvents = MutableSharedFlow<NavigationDestination>()
    val navEvents = _navEvents.asSharedFlow()

    suspend fun navigateTo(destination: NavigationDestination) {
        _navEvents.emit(destination)
    }
}

// 2. Одноразовых событий (тосты, снекбары)
class MessageEvents {
    private val _messages = MutableSharedFlow<String>()
    val messages = _messages.asSharedFlow()

    suspend fun showMessage(msg: String) {
        _messages.emit(msg)
    }
}

// 3. Частых эмиссий подряд
import kotlinx.coroutines.channels.BufferOverflow

class SearchQuery {
    private val _searchEvents = MutableSharedFlow<String>(
        replay = 0,
        extraBufferCapacity = 64,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val searchEvents = _searchEvents.asSharedFlow()

    fun onSearchTextChanged(query: String) {
        _searchEvents.tryEmit(query)
    }
}
```

### Когда Использовать StateFlow

```kotlin
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

// Используйте StateFlow для:

// 1. Управления UI-состоянием
class ScreenViewModel {
    private val _screenState = MutableStateFlow<ScreenState>(ScreenState.Loading)
    val screenState: StateFlow<ScreenState> = _screenState.asStateFlow()

    fun loadData(data: Data) {
        _screenState.value = ScreenState.Success(data)
    }
}

// 2. Конфигурации/настроек
class ThemeManager {
    private val _isDarkMode = MutableStateFlow(false)
    val isDarkMode: StateFlow<Boolean> = _isDarkMode.asStateFlow()

    fun toggleTheme() {
        _isDarkMode.value = !_isDarkMode.value
    }
}

// 3. Данных, у которых всегда должно быть актуальное значение
class UserRepository {
    private val _currentUser = MutableStateFlow<User?>(null)
    val currentUser: StateFlow<User?> = _currentUser.asStateFlow()

    fun setUser(user: User?) {
        _currentUser.value = user
    }
}
```

### Стратегии Буфера SharedFlow

```kotlin
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.channels.BufferOverflow

// Разные стратегии переполнения буфера
val sharedFlow1 = MutableSharedFlow<Int>(
    replay = 0,
    extraBufferCapacity = 5,
    onBufferOverflow = BufferOverflow.SUSPEND  // По умолчанию: suspend эмиттера
)

val sharedFlow2 = MutableSharedFlow<Int>(
    replay = 0,
    extraBufferCapacity = 5,
    onBufferOverflow = BufferOverflow.DROP_OLDEST  // Отбрасывать самые старые значения из дополнительного буфера (сохраняя replay)
)

val sharedFlow3 = MutableSharedFlow<Int>(
    replay = 0,
    extraBufferCapacity = 5,
    onBufferOverflow = BufferOverflow.DROP_LATEST  // Отбрасывать новые значения при полном буфере
)
```

### Конвертация Между StateFlow И SharedFlow

```kotlin
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.SharingStarted

// StateFlow — специализированный SharedFlow (реализует SharedFlow с ограничениями)
val stateFlow: StateFlow<Int> = MutableStateFlow(0)
val asShared: SharedFlow<Int> = stateFlow  // Допустимо: upcast к SharedFlow

// Создание StateFlow из SharedFlow/Flow с помощью stateIn: оборачиваем исходный Flow
val sharedFlow = MutableSharedFlow<Int>(replay = 1)
val converted: StateFlow<Int> = sharedFlow.stateIn(
    scope = CoroutineScope(Dispatchers.Default),
    started = SharingStarted.Eagerly,
    initialValue = 0
)
```

### Производительность

```kotlin
// StateFlow эффективен для состояния:
// - Всегда имеет текущее значение (коллекторы сразу получают последнее)
// - Конфлюирует до последнего значения (пропускает emission при new == current)
// - Подходит как контейнер наблюдаемого состояния

// SharedFlow более гибкий:
// - Может буферизировать несколько значений
// - Может эмитить дубликаты
// - Настраиваемый реплей и стратегия буфера
// - Лучше подходит для событий и широковещательных сценариев
```

## Answer (EN)

`SharedFlow` is a hot stream that delivers values to multiple subscribers and can buffer/replay them (without strict real-time guarantees; delivery depends on coroutine scheduling).

`StateFlow` is a specialized `SharedFlow` that always holds exactly one latest value and replays it to new subscribers; a new value is emitted to collectors only when it is different from the current one (by equals), so setting the same value again does not trigger a new emission.

### Key Characteristics Comparison

| Feature | `SharedFlow` | `StateFlow` |
|---------|------------|-----------|
| Type | Hot `Flow` | Hot `Flow` (specialized `SharedFlow`) |
| Initial Value | Optional | Required |
| Value Storage | Can buffer multiple values | Always stores exactly one value |
| Replay | Configurable (0 to n) | Always replays 1 (the current value) |
| Conflation | Configurable | Always conflated to the latest value |
| Distinct Values | Can emit duplicates (no automatic distinct) | Skips emission when new value == current value (by equals) |
| Use Case | Events, broadcasts, multiple emissions | State management (always-available current state) |

### SharedFlow Example

```kotlin
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.collect

class EventBus {
    // MutableSharedFlow with no replay, no extra buffer
    private val _events = MutableSharedFlow<String>(replay = 0)
    val events: SharedFlow<String> = _events.asSharedFlow()

    suspend fun sendEvent(event: String) {
        _events.emit(event)
    }
}

fun main() = runBlocking {
    val eventBus = EventBus()

    // First subscriber
    launch {
        eventBus.events.collect { event ->
            println("Subscriber 1: $event")
        }
    }

    // Second subscriber
    launch {
        eventBus.events.collect { event ->
            println("Subscriber 2: $event")
        }
    }

    delay(100)
    eventBus.sendEvent("Event 1")
    eventBus.sendEvent("Event 2")
    delay(100)

    // Third subscriber (joins late, won't receive previous events with replay=0)
    launch {
        eventBus.events.collect { event ->
            println("Subscriber 3 (late): $event")
        }
    }

    delay(100)
    eventBus.sendEvent("Event 3")
    delay(100)
}

// Possible output:
// Subscriber 1: Event 1
// Subscriber 2: Event 1
// Subscriber 1: Event 2
// Subscriber 2: Event 2
// Subscriber 1: Event 3
// Subscriber 2: Event 3
// Subscriber 3 (late): Event 3
```

### StateFlow Example

```kotlin
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.launch
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.flow.collect

data class UiState(val count: Int, val isLoading: Boolean)

class CounterViewModel {
    private val _uiState = MutableStateFlow(UiState(count = 0, isLoading = false))
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun increment() {
        _uiState.update { currentState ->
            currentState.copy(count = currentState.count + 1)
        }
    }

    fun setLoading(loading: Boolean) {
        _uiState.update { it.copy(isLoading = loading) }
    }
}

fun main() = runBlocking {
    val viewModel = CounterViewModel()

    // Subscriber 1 (collects immediately; first value is delivered right away)
    launch {
        viewModel.uiState.collect { state ->
            println("Subscriber 1: count=${state.count}, loading=${state.isLoading}")
        }
    }

    delay(100)
    viewModel.increment()
    viewModel.increment()
    viewModel.setLoading(true)

    delay(100)

    // Subscriber 2 (joins late, immediately receives current state)
    launch {
        viewModel.uiState.collect { state ->
            println("Subscriber 2 (late): count=${state.count}, loading=${state.isLoading}")
        }
    }

    delay(100)
}

// Output:
// Subscriber 1: count=0, loading=false
// Subscriber 1: count=1, loading=false
// Subscriber 1: count=2, loading=false
// Subscriber 1: count=2, loading=true
// Subscriber 2 (late): count=2, loading=true
```

### SharedFlow with Replay Buffer

```kotlin
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.collect

class NotificationService {
    // Replay last 3 events to new subscribers
    private val _notifications = MutableSharedFlow<String>(
        replay = 3,
        extraBufferCapacity = 10
    )
    val notifications: SharedFlow<String> = _notifications.asSharedFlow()

    suspend fun notify(message: String) {
        _notifications.emit(message)
    }
}

fun main() = runBlocking {
    val service = NotificationService()

    // Send notifications before any subscriber
    service.notify("Notification 1")
    service.notify("Notification 2")
    service.notify("Notification 3")
    service.notify("Notification 4")

    delay(100)

    // New subscriber receives last 3 notifications
    launch {
        service.notifications.collect { notification ->
            println("Late subscriber: $notification")
        }
    }

    delay(100)
}

// Output:
// Late subscriber: Notification 2
// Late subscriber: Notification 3
// Late subscriber: Notification 4
```

### StateFlow Distinct Values Only

```kotlin
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.launch
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.collect

fun main() = runBlocking {
    val state = MutableStateFlow("Initial")

    launch {
        state.collect { value ->
            println("Collected: $value")
        }
    }

    delay(100)
    state.value = "Updated"
    state.value = "Updated"  // Same as current -> won't emit
    state.value = "Updated"  // Same as current -> won't emit
    state.value = "Different"
    state.value = "Different"  // Same as current -> won't emit

    delay(100)
}

// Output:
// Collected: Initial
// Collected: Updated
// Collected: Different
```

### When to Use SharedFlow

```kotlin
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.channels.BufferOverflow

// Use SharedFlow for:

// 1. Event broadcasting (button clicks, navigation)
class NavigationEvents {
    private val _navEvents = MutableSharedFlow<NavigationDestination>()
    val navEvents = _navEvents.asSharedFlow()

    suspend fun navigateTo(destination: NavigationDestination) {
        _navEvents.emit(destination)
    }
}

// 2. One-time events (toasts, snackbars)
class MessageEvents {
    private val _messages = MutableSharedFlow<String>()
    val messages = _messages.asSharedFlow()

    suspend fun showMessage(msg: String) {
        _messages.emit(msg)
    }
}

// 3. Multiple emissions in quick succession
class SearchQuery {
    private val _searchEvents = MutableSharedFlow<String>(
        replay = 0,
        extraBufferCapacity = 64,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val searchEvents = _searchEvents.asSharedFlow()

    fun onSearchTextChanged(query: String) {
        _searchEvents.tryEmit(query)
    }
}
```

### When to Use StateFlow

```kotlin
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

// Use StateFlow for:

// 1. UI State management
class ScreenViewModel {
    private val _screenState = MutableStateFlow<ScreenState>(ScreenState.Loading)
    val screenState: StateFlow<ScreenState> = _screenState.asStateFlow()

    fun loadData(data: Data) {
        _screenState.value = ScreenState.Success(data)
    }
}

// 2. Configuration/Settings
class ThemeManager {
    private val _isDarkMode = MutableStateFlow(false)
    val isDarkMode: StateFlow<Boolean> = _isDarkMode.asStateFlow()

    fun toggleTheme() {
        _isDarkMode.value = !_isDarkMode.value
    }
}

// 3. Data that always has a "current" value
class UserRepository {
    private val _currentUser = MutableStateFlow<User?>(null)
    val currentUser: StateFlow<User?> = _currentUser.asStateFlow()

    fun setUser(user: User?) {
        _currentUser.value = user
    }
}
```

### SharedFlow Buffer Strategies

```kotlin
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.channels.BufferOverflow

// Different buffer overflow strategies
val sharedFlow1 = MutableSharedFlow<Int>(
    replay = 0,
    extraBufferCapacity = 5,
    onBufferOverflow = BufferOverflow.SUSPEND  // Default: suspend emitter
)

val sharedFlow2 = MutableSharedFlow<Int>(
    replay = 0,
    extraBufferCapacity = 5,
    onBufferOverflow = BufferOverflow.DROP_OLDEST  // Drop oldest values from extra buffer (while preserving replay)
)

val sharedFlow3 = MutableSharedFlow<Int>(
    replay = 0,
    extraBufferCapacity = 5,
    onBufferOverflow = BufferOverflow.DROP_LATEST  // Drop newest values when buffer is full
)
```

### Converting Between StateFlow and SharedFlow

```kotlin
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.SharingStarted

// StateFlow IS a specialized SharedFlow (it implements SharedFlow with constraints)
val stateFlow: StateFlow<Int> = MutableStateFlow(0)
val asShared: SharedFlow<Int> = stateFlow  // Valid: upcast to SharedFlow

// Creating a StateFlow from a SharedFlow/Flow using stateIn: wrapping the source Flow
val sharedFlow = MutableSharedFlow<Int>(replay = 1)
val converted: StateFlow<Int> = sharedFlow.stateIn(
    scope = CoroutineScope(Dispatchers.Default),
    started = SharingStarted.Eagerly,
    initialValue = 0
)
```

### Performance Considerations

```kotlin
// StateFlow is efficient for state:
// - Always has current value (collectors immediately receive the latest on start)
// - Conflates to the latest value (skips emission when new == current)
// - Suited for observable state containers

// SharedFlow is more flexible:
// - Can buffer multiple values
// - Can emit duplicates
// - Configurable replay and buffer strategy
// - Better for events and broadcast-style use cases
```

---

## Дополнительные Вопросы (RU)

- В чем ключевые отличия этого подхода от Java-подходов к реактивности/наблюдаемости?
- Когда вы бы использовали эти примитивы на практике?
- Какие распространенные подводные камни при использовании `SharedFlow` и `StateFlow`?

## Follow-ups

- What are the key differences between this and Java approaches to reactivity/observability?
- When would you use these primitives in practice?
- What are common pitfalls when using `SharedFlow` and `StateFlow`?

## Ссылки (RU)

- [Документация Kotlin]("https://kotlinlang.org/docs/home.html")
- [[c-concurrency]]
## References

- [Kotlin Documentation]("https://kotlinlang.org/docs/home.html")
- [[c-concurrency]]
## Связанные Вопросы (RU)

- [[q-launch-vs-async-error-handling--kotlin--medium]]

## Related Questions

- [[q-launch-vs-async-error-handling--kotlin--medium]]
