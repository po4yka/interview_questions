---
id: lang-019
title: "SharedFlow Vs StateFlow / SharedFlow против StateFlow"
aliases: [SharedFlow Vs StateFlow, SharedFlow против StateFlow]
topic: programming-languages
subtopics: [coroutines, flow, reactive-programming]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-class-composition--oop--medium, q-launch-vs-async-error-handling--programming-languages--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [coroutines, difficulty/easy, flow, kotlin, programming-languages, sharedflow, stateflow]
date created: Saturday, October 4th 2025, 10:40:14 am
date modified: Saturday, November 1st 2025, 5:43:23 pm
---

# SharedFlow Vs StateFlow Differences

# Question (EN)
> What are the differences between SharedFlow and StateFlow?

# Вопрос (RU)
> Какие различия между SharedFlow и StateFlow?

---

## Answer (EN)

**SharedFlow** is a hot stream that transmits data to multiple subscribers in real-time and can buffer values.

**StateFlow** is a stream that always stores one last value and sends it to subscribers only when the state changes.

### Key Characteristics Comparison

| Feature | SharedFlow | StateFlow |
|---------|------------|-----------|
| **Type** | Hot Flow | Hot Flow (specialized SharedFlow) |
| **Initial Value** | Optional | Required |
| **Value Storage** | Can buffer multiple values | Always stores exactly one value |
| **Replay** | Configurable (0 to n) | Always replays 1 (the current value) |
| **Conflation** | Configurable | Always conflated |
| **Distinct Values** | Can emit duplicates | Only emits distinct values |
| **Use Case** | Events, multiple emissions | State management |

### SharedFlow Example

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

class EventBus {
    // MutableSharedFlow with no replay, no buffer
    private val _events = MutableSharedFlow<String>()
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

// Output:
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

    // Subscriber 1 (collects immediately)
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
// Subscriber 2 (late): count=2, loading=true  // Immediately gets current state
```

### SharedFlow with Replay Buffer

```kotlin
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
fun main() = runBlocking {
    val state = MutableStateFlow("Initial")

    launch {
        state.collect { value ->
            println("Collected: $value")
        }
    }

    delay(100)
    state.value = "Updated"
    state.value = "Updated"  // Duplicate - won't emit
    state.value = "Updated"  // Duplicate - won't emit
    state.value = "Different"
    state.value = "Different"  // Duplicate - won't emit

    delay(100)
}

// Output:
// Collected: Initial
// Collected: Updated
// Collected: Different
```

### When to Use SharedFlow

```kotlin
// - Use SharedFlow for:

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
// - Use StateFlow for:

// 1. UI State management
class ScreenViewModel {
    private val _screenState = MutableStateFlow(ScreenState.Loading)
    val screenState: StateFlow<ScreenState> = _screenState.asStateFlow()

    fun loadData() {
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

    fun setUser(user: User) {
        _currentUser.value = user
    }
}
```

### SharedFlow Buffer Strategies

```kotlin
// Different buffer overflow strategies
val sharedFlow1 = MutableSharedFlow<Int>(
    replay = 0,
    extraBufferCapacity = 5,
    onBufferOverflow = BufferOverflow.SUSPEND  // Default: suspend emitter
)

val sharedFlow2 = MutableSharedFlow<Int>(
    replay = 0,
    extraBufferCapacity = 5,
    onBufferOverflow = BufferOverflow.DROP_OLDEST  // Drop oldest value
)

val sharedFlow3 = MutableSharedFlow<Int>(
    replay = 0,
    extraBufferCapacity = 5,
    onBufferOverflow = BufferOverflow.DROP_LATEST  // Drop newest value
)
```

### Converting Between StateFlow and SharedFlow

```kotlin
// StateFlow IS a SharedFlow (with specific constraints)
val stateFlow: StateFlow<Int> = MutableStateFlow(0)
val asShared: SharedFlow<Int> = stateFlow  // Valid conversion

// Convert SharedFlow to StateFlow (requires initial value)
val sharedFlow = MutableSharedFlow<Int>(replay = 1)
val converted: StateFlow<Int> = sharedFlow.stateIn(
    scope = CoroutineScope(Dispatchers.Default),
    started = SharingStarted.Eagerly,
    initialValue = 0
)
```

### Performance Considerations

```kotlin
// StateFlow is more efficient for state
// - Automatically conflates (skips intermediate values)
// - Always has current value (no suspend on collect)
// - Lower memory footprint

// SharedFlow is more flexible
// - Can buffer multiple values
// - Can emit duplicates
// - Configurable replay
// - Better for events
```

---

## Ответ (RU)

SharedFlow — это горячий поток, который передаёт данные нескольким подписчикам в реальном времени и может буферизировать значения. StateFlow — поток, который всегда хранит одно последнее значение и отправляет его подписчикам только при изменении состояния.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

- [[q-launch-vs-async-error-handling--programming-languages--medium]]
- [[q-class-composition--oop--medium]]
-
