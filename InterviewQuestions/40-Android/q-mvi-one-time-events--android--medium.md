---
id: android-159
title: "MVI One-Time Events / Одноразовые события в MVI"
aliases: ["MVI One-Time Events", "One-time events in MVI", "SharedFlow для событий", "Одноразовые события в MVI"]
topic: android
subtopics: [architecture-mvi]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-lifecycle, c-viewmodel, q-mvi-architecture--android--hard]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/architecture-mvi, architecture, difficulty/medium, events, mvi]

---
# Вопрос (RU)

> Как обработать одноразовые события (one-time events) в MVI архитектуре?

# Question (EN)

> How to handle one-time events in MVI architecture?

---

## Ответ (RU)

В MVI State должен быть immutable и содержать только постоянные UI данные. Одноразовые события (navigation, toasts, snackbars) обрабатываются отдельно через **`SharedFlow`** с `replay = 0` или **Channel**.

**Проблема**: хранение событий в State приводит к их повторному срабатыванию при пересоздании экрана.

```kotlin
// ❌ Неправильно - событие в State
data class UiState(
    val isLoading: Boolean = false,
    val showSuccessToast: Boolean = false  // При повороте toast покажется снова
)
```

**Решение 1: `SharedFlow` (рекомендуется для Compose)**

```kotlin
sealed class UiEvent {
    data class ShowToast(val message: String) : UiEvent()
    data class ShowError(val message: String) : UiEvent()
    data class Navigate(val route: String) : UiEvent()
}

data class UiState(
    val isLoading: Boolean = false,
    val data: List<Item> = emptyList()
    // ✅ Никаких одноразовых событий
)

class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    // ✅ SharedFlow для событий c явным replay = 0
    private val _events = MutableSharedFlow<UiEvent>(replay = 0)
    val events: SharedFlow<UiEvent> = _events.asSharedFlow()

    fun loadUsers() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            repository.getUsers()
                .onSuccess { users ->
                    _uiState.update { it.copy(isLoading = false, data = users) }
                    _events.emit(UiEvent.ShowToast("Loaded ${users.size} users"))
                }
                .onFailure { error ->
                    _uiState.update { it.copy(isLoading = false) }
                    _events.emit(UiEvent.ShowError(error.message ?: "Error"))
                }
        }
    }
}
```

**В UI (Compose)**:

```kotlin
@Composable
fun UserScreen(viewModel: UserViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsState()
    val context = LocalContext.current

    // ✅ LaunchedEffect для событий
    LaunchedEffect(viewModel) {
        viewModel.events.collect { event ->
            when (event) {
                is UiEvent.ShowToast -> {
                    Toast.makeText(context, event.message, Toast.LENGTH_SHORT).show()
                }
                is UiEvent.ShowError -> {
                    Toast.makeText(context, event.message, Toast.LENGTH_SHORT).show()
                }
                is UiEvent.Navigate -> { /* Навигация */ }
            }
        }
    }

    if (uiState.isLoading) LoadingScreen() else UserList(uiState.data)
}
```

**В UI (Views)**:

```kotlin
class UserFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // ✅ repeatOnLifecycle для событий
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.events.collect { event -> handleEvent(event) }
            }
        }
    }
}
```

**Решение 2: Channel (проще и надёжнее для одного потребителя)**

```kotlin
class UserViewModel : ViewModel() {
    private val _events = Channel<UiEvent>()
    val events = _events.receiveAsFlow()

    fun loadUsers() {
        viewModelScope.launch {
            _events.send(UiEvent.ShowToast("Success"))
        }
    }
}
```

> Channel по своей природе соответствует "горячему" потоку одноразовых событий и предполагает одного потребителя: при нескольких коллекторах события будут разделяться между ними, поэтому его стоит использовать там, где есть один предсказуемый подписчик.

**Сравнение подходов**:

| Подход | Плюсы | Минусы | Use Case |
|--------|-------|--------|----------|
| **`SharedFlow`** | Множественные подписчики, контроль replay | Чуть сложнее API | Compose, современные проекты |
| **Channel** | Простой API, FIFO гарантии, хорошо подходит для одного потребителя | События распределяются между несколькими коллекторами, не подходит для широковещательных событий | Простые случаи с одним подписчиком |

**Best Practices**:

1. **Разделяйте State и Events**: State - постоянные данные, Events - одноразовые действия.
2. **Правильный scope**: используйте `LaunchedEffect` с стабильным ключом (например, `viewModel`) в Compose и `repeatOnLifecycle` во `View`-D для безопасного сбора событий.
3. **Тестируйте события**: собирайте их в список из `SharedFlow`/`Channel` и проверяйте наличие ожидаемых событий.

```kotlin
@Test
fun `loadUsers failure emits error event`() = runTest {
    coEvery { repository.getUsers() } throws Exception("Error")

    val events = mutableListOf<UiEvent>()
    val job = launch { viewModel.events.collect { events.add(it) } }

    viewModel.loadUsers()
    advanceUntilIdle()

    assertTrue(events.any { it is UiEvent.ShowError })
    job.cancel()
}
```

## Answer (EN)

In MVI, State should be immutable and contain only persistent UI data. One-time events (navigation, toasts, snackbars) should be handled separately via **`SharedFlow`** with `replay = 0` or a **Channel**.

**Problem**: storing events in State causes them to re-trigger on screen recreation.

```kotlin
// ❌ Wrong - event in State
data class UiState(
    val isLoading: Boolean = false,
    val showSuccessToast: Boolean = false  // Toast shows again on rotation
)
```

**Solution 1: `SharedFlow` (recommended for Compose)**

```kotlin
sealed class UiEvent {
    data class ShowToast(val message: String) : UiEvent()
    data class ShowError(val message: String) : UiEvent()
    data class Navigate(val route: String) : UiEvent()
}

data class UiState(
    val isLoading: Boolean = false,
    val data: List<Item> = emptyList()
    // ✅ No one-time events
)

class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    // ✅ SharedFlow for events with explicit replay = 0
    private val _events = MutableSharedFlow<UiEvent>(replay = 0)
    val events: SharedFlow<UiEvent> = _events.asSharedFlow()

    fun loadUsers() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            repository.getUsers()
                .onSuccess { users ->
                    _uiState.update { it.copy(isLoading = false, data = users) }
                    _events.emit(UiEvent.ShowToast("Loaded ${users.size} users"))
                }
                .onFailure { error ->
                    _uiState.update { it.copy(isLoading = false) }
                    _events.emit(UiEvent.ShowError(error.message ?: "Error"))
                }
        }
    }
}
```

**In UI (Compose)**:

```kotlin
@Composable
fun UserScreen(viewModel: UserViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsState()
    val context = LocalContext.current

    // ✅ LaunchedEffect for events
    LaunchedEffect(viewModel) {
        viewModel.events.collect { event ->
            when (event) {
                is UiEvent.ShowToast -> {
                    Toast.makeText(context, event.message, Toast.LENGTH_SHORT).show()
                }
                is UiEvent.ShowError -> {
                    Toast.makeText(context, event.message, Toast.LENGTH_SHORT).show()
                }
                is UiEvent.Navigate -> { /* Navigation */ }
            }
        }
    }

    if (uiState.isLoading) LoadingScreen() else UserList(uiState.data)
}
```

**In UI (Views)**:

```kotlin
class UserFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // ✅ repeatOnLifecycle for events
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.events.collect { event -> handleEvent(event) }
            }
        }
    }
}
```

**Solution 2: Channel (simpler and more reliable for a single consumer)**

```kotlin
class UserViewModel : ViewModel() {
    private val _events = Channel<UiEvent>()
    val events = _events.receiveAsFlow()

    fun loadUsers() {
        viewModelScope.launch {
            _events.send(UiEvent.ShowToast("Success"))
        }
    }
}
```

> A Channel naturally models a "hot" stream of one-time events with a single consumer: with multiple collectors, events are distributed between them, so it should be used where you have one predictable subscriber.

**Comparison**:

| Approach | Pros | Cons | Use Case |
|----------|------|------|----------|
| **`SharedFlow`** | Multiple subscribers, replay control | Slightly more complex API | Compose, modern projects |
| **Channel** | Simple API, FIFO guarantees, good for a single consumer | Events are distributed between multiple collectors, not suitable for broadcast-style events | Simple cases with a single subscriber |

**Best Practices**:

1. **Separate State and Events**: State = persistent data, Events = one-time actions.
2. **Correct scope**: use `LaunchedEffect` with a stable key (e.g. `viewModel`) in Compose and `repeatOnLifecycle` in Views for safe event collection.
3. **Test events**: collect from `SharedFlow`/`Channel` into a list and assert expected events.

```kotlin
@Test
fun `loadUsers failure emits error event`() = runTest {
    coEvery { repository.getUsers() } throws Exception("Error")

    val events = mutableListOf<UiEvent>()
    val job = launch { viewModel.events.collect { events.add(it) } }

    viewModel.loadUsers()
    advanceUntilIdle()

    assertTrue(events.any { it is UiEvent.ShowError })
    job.cancel()
}
```

---

## Follow-ups

- How to handle events when multiple subscribers are needed?
- What happens to events emitted before UI subscribes?
- How to test `SharedFlow` vs Channel in ViewModels?
- When to use `extraBufferCapacity` in `SharedFlow`?
- How to prevent event loss during configuration changes?

## References

- [[c-viewmodel]] - `ViewModel` fundamentals
- [[c-lifecycle]] - Android Lifecycle

## Related Questions

### Prerequisites

- [[q-what-is-viewmodel--android--medium]] - `ViewModel` basics
- [[q-channel-flow-comparison--kotlin--medium]] - Channel vs `Flow` comparison

### Related

- [[q-mvvm-vs-mvp-differences--android--medium]] - MVVM vs MVP comparison
- [[q-stateflow-flow-sharedflow-livedata--android--medium]] - `StateFlow` vs `SharedFlow` vs `LiveData`

### Advanced

- [[q-mvi-architecture--android--hard]] - Full MVI architecture
- [[q-offline-first-architecture--android--hard]] - Offline-first architecture
