---
id: android-431
title: "MVI Handle One Time Events / Обработка одноразовых событий в MVI"
aliases: [Event Wrapper, MVI One-Time Events, SingleLiveEvent, Обработка событий MVI, Одноразовые события]

# Classification
topic: android
subtopics: [architecture-mvi, coroutines, flow, ui-state]
question_kind: android
difficulty: hard

# Language
original_language: ru
language_tags: [en, ru]

# Workflow
status: draft

# Links
moc: moc-android
related: [q-mvi-architecture--android--hard, q-mvi-one-time-events--android--medium, q-sharedflow-stateflow--kotlin--medium, q-stateflow-flow-sharedflow-livedata--android--medium]

# Timestamps
created: 2025-10-15
updated: 2025-10-30

# Tags
tags: [android/architecture-mvi, android/coroutines, android/flow, android/ui-state, architecture-mvi, difficulty/hard, sharedflow, stateflow, viewmodel]
date created: Saturday, November 1st 2025, 12:46:59 pm
date modified: Saturday, November 1st 2025, 5:43:33 pm
---

# Вопрос (RU)
> Как в MVI-архитектуре правильно обрабатывать одноразовые события (one-time events), которые не должны храниться в State и пересылаться при пересоздании экрана?

# Question (EN)
> How to properly handle one-time events in MVI architecture that should not be stored in State and re-delivered on screen recreation?

---

## Ответ (RU)

В MVI существует фундаментальное противоречие: State должен быть воспроизводимым и surviv configuration changes, но события (навигация, toast, snackbar) должны показываться только один раз. Существует несколько паттернов решения этой проблемы.

### 1. SharedFlow С Replay = 0 (Рекомендуемый подход)

✅ **Best Practice** - чистое reactive решение для событий:

```kotlin
class MyViewModel : ViewModel() {
    private val _events = MutableSharedFlow<Event>(
        replay = 0,
        extraBufferCapacity = 1,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val events: SharedFlow<Event> = _events.asSharedFlow()

    fun performAction() {
        viewModelScope.launch {
            _events.emit(Event.ShowToast("Success"))
        }
    }
}

// View
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.events.collect { event ->
            when (event) {
                is Event.ShowToast -> showToast(event.message)
                is Event.Navigate -> navigate(event.route)
            }
        }
    }
}
```

**Ключевые параметры**:
- `replay = 0` - новые подписчики не получают старые события
- `extraBufferCapacity = 1` - буфер для событий при отсутствии активных подписчиков
- `BufferOverflow.DROP_OLDEST` - при переполнении удаляет старейшие события

### 2. Канал (Channel) Для Гарантированной Доставки

✅ **Для критичных событий** - гарантирует доставку:

```kotlin
class MyViewModel : ViewModel() {
    private val _events = Channel<Event>(Channel.BUFFERED)
    val events = _events.receiveAsFlow()

    fun performAction() {
        _events.trySend(Event.ShowError("Failed"))
    }
}

// View собирает события из канала
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.events.collect { event ->
            handleEvent(event)
        }
    }
}
```

**Гарантии**: события не теряются даже если View временно неактивна.

### 3. EventWrapper Для StateFlow

❌ **Legacy подход** - используется, если нужна совместимость с StateFlow:

```kotlin
data class Event<out T>(private val content: T) {
    private var hasBeenHandled = false

    fun getContentIfNotHandled(): T? {
        return if (!hasBeenHandled) {
            hasBeenHandled = true
            content
        } else null
    }
}

data class UiState(
    val data: String,
    val event: Event<String>? = null
)
```

**Недостатки**: mutable state в immutable объекте, сложное тестирование.

### 4. Разделение State И Effects

✅ **Архитектурный подход** - разделение ответственности:

```kotlin
data class UiState(val data: String, val isLoading: Boolean)
sealed interface Effect {
    data class ShowToast(val message: String) : Effect
    data class Navigate(val route: String) : Effect
}

class MyViewModel : ViewModel() {
    private val _state = MutableStateFlow(UiState())
    val state = _state.asStateFlow()

    private val _effects = MutableSharedFlow<Effect>()
    val effects = _effects.asSharedFlow()
}
```

### Edge Cases Для HARD Уровня

**1. Потеря событий при быстрой ротации**:
```kotlin
// ❌ Проблема: события могут теряться
lifecycleScope.launch {
    viewModel.events.collect { ... }
}

// ✅ Решение: repeatOnLifecycle
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.events.collect { ... }
    }
}
```

**2. Race condition при emit во время пересоздания**:
```kotlin
// Используем extraBufferCapacity для буферизации
MutableSharedFlow<Event>(
    replay = 0,
    extraBufferCapacity = 64,  // достаточный буфер
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)
```

**3. Memory leaks при долгоживущих событиях**:
```kotlin
// ❌ Утечка - события держат ссылки на большие объекты
sealed class Event {
    data class ShowImage(val bitmap: Bitmap) : Event
}

// ✅ Решение - передавать только ID, данные получать из Repository
sealed class Event {
    data class ShowImage(val imageId: String) : Event
}
```

**4. Тестирование событий**:
```kotlin
@Test
fun `event emitted once`() = runTest {
    val events = mutableListOf<Event>()
    val job = launch(UnconfinedTestDispatcher()) {
        viewModel.events.take(1).toList(events)
    }

    viewModel.performAction()
    advanceUntilIdle()

    assertEquals(1, events.size)
    job.cancel()
}
```

### Рекомендации По Выбору Подхода

| Сценарий | Решение | Причина |
|----------|---------|---------|
| Обычные события (toast, snackbar) | SharedFlow (replay=0) | Простота, потеря некритична |
| Критичные события (оплата, навигация) | Channel | Гарантия доставки |
| Совместимость с LiveData | EventWrapper | Миграция legacy кода |
| Сложная бизнес-логика | State + Effects разделение | Чистая архитектура |

## Answer (EN)

In MVI, there's a fundamental contradiction: State should be reproducible and survive configuration changes, but events (navigation, toast, snackbar) should be shown only once. Several patterns exist to solve this problem.

### 1. SharedFlow with Replay = 0 (Recommended)

✅ **Best Practice** - pure reactive solution for events:

```kotlin
class MyViewModel : ViewModel() {
    private val _events = MutableSharedFlow<Event>(
        replay = 0,
        extraBufferCapacity = 1,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val events: SharedFlow<Event> = _events.asSharedFlow()

    fun performAction() {
        viewModelScope.launch {
            _events.emit(Event.ShowToast("Success"))
        }
    }
}
```

**Key parameters**:
- `replay = 0` - new subscribers don't receive old events
- `extraBufferCapacity = 1` - buffer for events when no active subscribers
- `BufferOverflow.DROP_OLDEST` - drops oldest events on overflow

### 2. Channel for Guaranteed Delivery

✅ **For critical events** - guarantees delivery:

```kotlin
class MyViewModel : ViewModel() {
    private val _events = Channel<Event>(Channel.BUFFERED)
    val events = _events.receiveAsFlow()
}
```

**Guarantees**: events not lost even if View temporarily inactive.

### 3. EventWrapper for StateFlow

❌ **Legacy approach** - use only for StateFlow compatibility:

```kotlin
data class Event<out T>(private val content: T) {
    private var hasBeenHandled = false

    fun getContentIfNotHandled(): T? {
        return if (!hasBeenHandled) {
            hasBeenHandled = true
            content
        } else null
    }
}
```

**Drawbacks**: mutable state in immutable object, difficult testing.

### 4. Separation of State and Effects

✅ **Architectural approach** - separation of concerns:

```kotlin
data class UiState(val data: String, val isLoading: Boolean)
sealed interface Effect {
    data class ShowToast(val message: String) : Effect
    data class Navigate(val route: String) : Effect
}
```

### Edge Cases for HARD Level

**1. Event loss during rapid rotation**:
```kotlin
// ✅ Solution: use repeatOnLifecycle
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.events.collect { ... }
    }
}
```

**2. Race condition during recreation**:
```kotlin
MutableSharedFlow<Event>(
    replay = 0,
    extraBufferCapacity = 64,  // sufficient buffer
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)
```

**3. Memory leaks with long-lived events**:
```kotlin
// ✅ Solution - pass only IDs, fetch data from Repository
sealed class Event {
    data class ShowImage(val imageId: String) : Event
}
```

**4. Testing events**:
```kotlin
@Test
fun `event emitted once`() = runTest {
    val events = mutableListOf<Event>()
    val job = launch(UnconfinedTestDispatcher()) {
        viewModel.events.take(1).toList(events)
    }

    viewModel.performAction()
    advanceUntilIdle()

    assertEquals(1, events.size)
    job.cancel()
}
```

### Selection Guidelines

| Scenario | Solution | Reason |
|----------|---------|---------|
| Regular events (toast, snackbar) | SharedFlow (replay=0) | Simple, loss non-critical |
| Critical events (payment, navigation) | Channel | Delivery guarantee |
| LiveData compatibility | EventWrapper | Legacy code migration |
| Complex business logic | State + Effects separation | Clean architecture |

---

## Follow-ups

1. How does `extraBufferCapacity` differ from `replay` in SharedFlow, and when would you use each?
2. What happens if you emit an event while no collectors are active with `replay = 0` and `extraBufferCapacity = 0`?
3. How would you implement event priority system where critical events override non-critical ones?
4. What are the threading implications of using `Channel.CONFLATED` vs `Channel.BUFFERED` for events?
5. How would you design event system that supports event cancellation/rollback (e.g., undo navigation)?

## References

- [[q-mvi-architecture--android--hard]] - MVI architecture fundamentals
- [[q-stateflow-flow-sharedflow-livedata--android--medium]] - Flow types comparison
- [[q-sharedflow-stateflow--kotlin--medium]] - SharedFlow vs StateFlow
- [Kotlin Flow Documentation - SharedFlow](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/)
- [Android Lifecycle - repeatOnLifecycle](https://developer.android.com/topic/libraries/architecture/coroutines)

## Related Questions

### Prerequisites (Medium)
- [[q-mvi-one-time-events--android--medium]] - Basic one-time events handling
- [[q-stateflow-flow-sharedflow-livedata--android--medium]] - Flow types overview
- [[q-stateflow-sharedflow-android--kotlin--medium]] - StateFlow vs SharedFlow usage

### Related (Hard)
- [[q-mvi-architecture--android--hard]] - MVI architecture deep dive
- [[q-clean-architecture-android--android--hard]] - Clean Architecture patterns
- [[q-offline-first-architecture--android--hard]] - Offline-first state management

### Advanced Topics
- [[q-testing-stateflow-sharedflow--kotlin--medium]] - Testing Flow-based events
- [[q-sharedflow-replay-buffer-config--kotlin--medium]] - SharedFlow configuration
