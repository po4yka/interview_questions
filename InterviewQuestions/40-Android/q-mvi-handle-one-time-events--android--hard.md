---
id: android-431
title: MVI Handle One Time Events / Обработка одноразовых событий в MVI
aliases: [Event Wrapper, MVI One-Time Events, SingleLiveEvent, Обработка событий MVI, Одноразовые события]
topic: android
subtopics:
  - architecture-mvi
  - coroutines
  - flow
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-coroutines
  - c-flow
  - q-dagger-build-time-optimization--android--medium
  - q-mvi-architecture--android--hard
  - q-mvi-one-time-events--android--medium
  - q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium
created: 2025-10-15
updated: 2025-10-30
tags: [android/architecture-mvi, android/coroutines, android/flow, architecture-mvi, difficulty/hard, sharedflow, stateflow, viewmodel]

date created: Saturday, November 1st 2025, 12:46:59 pm
date modified: Tuesday, November 25th 2025, 8:53:58 pm
---
# Вопрос (RU)
> Как в MVI-архитектуре правильно обрабатывать одноразовые события (one-time events), которые не должны храниться в State и пересылаться при пересоздании экрана?

# Question (EN)
> How to properly handle one-time events in MVI architecture that should not be stored in State and re-delivered on screen recreation?

---

## Ответ (RU)

В MVI существует фундаментальное противоречие: State должен быть воспроизводимым и переживать configuration changes, но события (навигация, toast, snackbar) должны показываться только один раз. Существует несколько паттернов решения этой проблемы.

### 1. `SharedFlow` С Replay = 0 (Рекомендуемый подход)

✅ **Best Practice** - чистое reactive-решение для одноразовых событий:

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
- `replay = 0` — новые подписчики не получают старые события
- `extraBufferCapacity` — буфер для событий при временном отсутствии активных подписчиков (если буфер заполнен, при выбранной политике события могут быть отброшены)
- `BufferOverflow.DROP_OLDEST` — при переполнении удаляет старейшие события

### 2. Канал (Channel) Для Буферизации И Управляемой Доставки

✅ **Для более критичных событий** — позволяет буферизовать события, пока есть потребитель, но не является абсолютной «гарантией доставки» в любых условиях.

```kotlin
class MyViewModel : ViewModel() {
    private val _events = Channel<Event>(Channel.BUFFERED)
    val events = _events.receiveAsFlow()

    fun performAction() {
        // trySend не приостанавливает, но может вернуть failure при невозможности записи
        _events.trySend(Event.ShowError("Failed"))
    }
}

// View
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.events.collect { event ->
            handleEvent(event)
        }
    }
}
```

**Важно**:
- `Channel.BUFFERED` создаёт буфер, поэтому события не теряются, пока есть место в буфере и пока потребитель (`View`) возобновляет сбор.
- Однако при полном буфере, ошибках или отсутствии потребителей навсегда «гарантии» нет — архитектуру всё равно нужно проектировать с учётом возможной потери некритичных событий.

### 3. EventWrapper Для `StateFlow`

❌ **Legacy-подход** — используется, если нужна совместимость с `LiveData`/`StateFlow` и уже есть существующий код:

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

**Недостатки**: mutable state внутри, сложное тестирование, риск неправильного использования, смешение постоянного `State` и одноразовых событий.

### 4. Разделение State И Effects

✅ **Архитектурный подход** — явное разделение долгоживущего состояния и одноразовых эффектов:

```kotlin
data class UiState(val data: String, val isLoading: Boolean)
sealed interface Effect {
    data class ShowToast(val message: String) : Effect
    data class Navigate(val route: String) : Effect
}

class MyViewModel : ViewModel() {
    private val _state = MutableStateFlow(UiState(data = "", isLoading = false))
    val state = _state.asStateFlow()

    private val _effects = MutableSharedFlow<Effect>(
        replay = 0,
        extraBufferCapacity = 1,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val effects = _effects.asSharedFlow()

    fun onAction() {
        // обновляем state
        _state.update { it.copy(isLoading = true) }
        // эмитим одноразовый эффект
        viewModelScope.launch {
            _effects.emit(Effect.ShowToast("Loaded"))
        }
    }
}
```

---

### Edge Cases Для HARD Уровня

**1. Потеря событий при быстрой ротации**:

```kotlin
// ❌ Проблема: события могут теряться при отмене корутины при смене lifecycle state
lifecycleScope.launch {
    viewModel.events.collect { ... }
}

// ✅ Решение: repeatOnLifecycle гарантирует пере-запуск коллекции при возвращении в STARTED
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.events.collect { ... }
    }
}
```

**2. Race condition при emit во время пересоздания**:

```kotlin
// Используем extraBufferCapacity для буферизации краткоживущих событий
MutableSharedFlow<Event>(
    replay = 0,
    extraBufferCapacity = 64,  // достаточный буфер для всплесков
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)
```

**3. Memory leaks при долгоживущих событиях**:

```kotlin
// ❌ Потенциальная утечка — события держат ссылки на большие объекты
sealed class Event {
    data class ShowImage(val bitmap: Bitmap) : Event
}

// ✅ Решение — передавать только ID, данные получать из Repository/кеша
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
| Обычные события (toast, snackbar) | `SharedFlow` (replay=0) | Простота, потеря некритична |
| Более критичные события (ошибка, важный диалог) | Channel/`SharedFlow` с буфером | Буферизация и явный контроль поведения при переполнении |
| Совместимость с `LiveData`/legacy | EventWrapper | Постепенная миграция, но не рекомендуется для нового кода |
| Сложная бизнес-логика | State + Effects разделение | Чистая архитектура, явные одноразовые эффекты |

---

## Answer (EN)

In MVI, there's a fundamental tension: State should be reproducible and survive configuration changes, while events (navigation, toast, snackbar) must be delivered only once. Several patterns are used to solve this.

### 1. `SharedFlow` With Replay = 0 (Recommended)

✅ **Best Practice** — a pure reactive solution for one-time events:

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

**Key parameters**:
- `replay = 0` — new subscribers don't receive past events
- `extraBufferCapacity` — buffer for events while there are no active subscribers (with the configured `onBufferOverflow`, events may still be dropped)
- `BufferOverflow.DROP_OLDEST` — drops oldest events when the buffer is full

### 2. Channel for Buffered and Controlled Delivery

✅ **For more critical events** — allows buffering and explicit back-pressure handling, but is not an absolute "guaranteed delivery" mechanism.

```kotlin
class MyViewModel : ViewModel() {
    private val _events = Channel<Event>(Channel.BUFFERED)
    val events = _events.receiveAsFlow()

    fun performAction() {
        // trySend is non-suspending and may fail if the buffer is full
        _events.trySend(Event.ShowError("Failed"))
    }
}

// View
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.events.collect { event ->
            handleEvent(event)
        }
    }
}
```

**Notes**:
- With `Channel.BUFFERED`, events are kept while there is buffer space and a consumer eventually collects them.
- If the buffer is full or no consumer collects, events can be dropped or `trySend` can fail — you must design for potential loss or handle failures explicitly.

### 3. EventWrapper for `StateFlow`

❌ **Legacy approach** — use only when interoperating with existing `LiveData`/`StateFlow` patterns:

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

**Drawbacks**: mutable state inside, harder to test, mixes persistent state with one-time events.

### 4. Separation of State and Effects

✅ **Architectural approach** — separate long-lived state from one-time effects:

```kotlin
data class UiState(val data: String, val isLoading: Boolean)
sealed interface Effect {
    data class ShowToast(val message: String) : Effect
    data class Navigate(val route: String) : Effect
}

class MyViewModel : ViewModel() {
    private val _state = MutableStateFlow(UiState(data = "", isLoading = false))
    val state = _state.asStateFlow()

    private val _effects = MutableSharedFlow<Effect>(
        replay = 0,
        extraBufferCapacity = 1,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val effects = _effects.asSharedFlow()

    fun onAction() {
        _state.update { it.copy(isLoading = true) }
        viewModelScope.launch {
            _effects.emit(Effect.ShowToast("Loaded"))
        }
    }
}
```

---

### Edge Cases for HARD Level

**1. Event loss during rapid rotation**:

```kotlin
// ❌ Problem: collection tied to a single lifecycleScope.launch can be cancelled on state change
lifecycleScope.launch {
    viewModel.events.collect { ... }
}

// ✅ Solution: repeatOnLifecycle restarts collection when returning to STARTED
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.events.collect { ... }
    }
}
```

**2. Race condition during recreation**:

```kotlin
// Use extraBufferCapacity to absorb short spikes while collectors restart
MutableSharedFlow<Event>(
    replay = 0,
    extraBufferCapacity = 64,
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)
```

**3. Memory leaks with long-lived events**:

```kotlin
// ❌ Potential leak — events hold strong references to large objects
sealed class Event {
    data class ShowImage(val bitmap: Bitmap) : Event
}

// ✅ Solution — pass only IDs, resolve data via Repository/cache
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
|----------|---------|--------|
| Regular events (toast, snackbar) | `SharedFlow` (replay=0) | Simple; loss is acceptable |
| More critical events (errors, important dialogs) | Channel/`SharedFlow` with buffer | Buffering plus explicit handling of overflow/loss |
| `LiveData`/legacy compatibility | EventWrapper | Helps migration; not recommended for new designs |
| Complex business logic | State + Effects separation | Clean, explicit one-time effects handling |

---

## Дополнительные Вопросы (RU)

1. В чем разница между `replay` и `extraBufferCapacity` в `SharedFlow` и когда использовать каждый из них?
2. Что произойдет, если эмитить событие при `replay = 0` и `extraBufferCapacity = 0`, когда нет активных коллекторов?
3. Как реализовать систему приоритетов событий, где критичные события вытесняют некритичные?
4. Как различаются характеристики потокобезопасности и поведения при использовании `Channel.CONFLATED` и `Channel.BUFFERED` для одноразовых событий?
5. Как спроектировать систему событий, поддерживающую отмену/rollback событий (например, undo для навигации)?

## Follow-ups

1. How does `extraBufferCapacity` differ from `replay` in `SharedFlow`, and when would you use each?
2. What happens if you emit an event while no collectors are active with `replay = 0` and `extraBufferCapacity = 0`?
3. How would you implement an event priority system where critical events override non-critical ones?
4. What are the threading and delivery implications of using `Channel.CONFLATED` vs `Channel.BUFFERED` for events?
5. How would you design an event system that supports event cancellation/rollback (e.g., undo navigation)?

## Ссылки (RU)

- [[q-mvi-architecture--android--hard]] — основы архитектуры MVI
- [[q-stateflow-flow-sharedflow-livedata--android--medium]] — сравнение типов `Flow`
- [[q-sharedflow-stateflow--kotlin--medium]] — `SharedFlow` vs `StateFlow`
- "https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/"
- "https://developer.android.com/topic/libraries/architecture/coroutines"

## References

- [[q-mvi-architecture--android--hard]] - MVI architecture fundamentals
- [[q-stateflow-flow-sharedflow-livedata--android--medium]] - `Flow` types comparison
- [[q-sharedflow-stateflow--kotlin--medium]] - `SharedFlow` vs `StateFlow`
- "https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/"
- "https://developer.android.com/topic/libraries/architecture/coroutines"

## Связанные Вопросы (RU)

### Предварительные Знания / Концепции

- [[c-flow]]
- [[c-coroutines]]

### Предварительные Вопросы (Medium)

- [[q-mvi-one-time-events--android--medium]] — базовая обработка одноразовых событий
- [[q-stateflow-flow-sharedflow-livedata--android--medium]] — обзор типов `Flow`

### Связанные (Hard)

- [[q-mvi-architecture--android--hard]] — глубокое погружение в архитектуру MVI

## Related Questions

### Prerequisites / Concepts

- [[c-flow]]
- [[c-coroutines]]

### Prerequisites (Medium)

- [[q-mvi-one-time-events--android--medium]] - Basic one-time events handling
- [[q-stateflow-flow-sharedflow-livedata--android--medium]] - `Flow` types overview

### Related (Hard)

- [[q-mvi-architecture--android--hard]] - MVI architecture deep dive
