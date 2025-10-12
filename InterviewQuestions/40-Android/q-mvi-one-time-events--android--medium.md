---
topic: android
tags:
  - android
  - mvi
  - architecture
  - state-management
  - events
difficulty: medium
status: draft
---

# MVI: Обработка одноразовых событий (One-time Events)

**English**: How to handle one-time events in MVI architecture?

## Answer (EN)
В MVI (Model-View-Intent) State должен быть immutable и содержать только UI состояние. Но некоторые события (navigation, toasts, snackbars) не должны сохраняться в State и повторяться при пересоздании экрана. Существует несколько паттернов для их обработки.

### Проблема

```kotlin
// - НЕПРАВИЛЬНО - событие в State
data class UiState(
    val isLoading: Boolean = false,
    val data: List<Item> = emptyList(),
    val showSuccessToast: Boolean = false  // Проблема!
)

// При пересоздании Activity toast покажется снова
```

### Решение 1: SharedFlow с replay = 0

Рекомендуемый подход для Kotlin Coroutines.

```kotlin
sealed class UiEvent {
    data class ShowToast(val message: String) : UiEvent()
    data class Navigate(val route: String) : UiEvent()
    data class ShowError(val error: String) : UiEvent()
}

data class UiState(
    val isLoading: Boolean = false,
    val data: List<Item> = emptyList()
    // Никаких одноразовых событий здесь!
)

@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    // SharedFlow для одноразовых событий
    private val _events = MutableSharedFlow<UiEvent>()
    val events: SharedFlow<UiEvent> = _events.asSharedFlow()

    fun loadUsers() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }

            repository.getUsers()
                .onSuccess { users ->
                    _uiState.update {
                        it.copy(isLoading = false, data = users)
                    }
                    // Одноразовое событие
                    _events.emit(UiEvent.ShowToast("Loaded ${users.size} users"))
                }
                .onFailure { error ->
                    _uiState.update { it.copy(isLoading = false) }
                    _events.emit(UiEvent.ShowError(error.message ?: "Unknown error"))
                }
        }
    }

    fun navigateToDetails(itemId: Int) {
        viewModelScope.launch {
            _events.emit(UiEvent.Navigate("details/$itemId"))
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

    // Подписка на события
    LaunchedEffect(Unit) {
        viewModel.events.collect { event ->
            when (event) {
                is UiEvent.ShowToast -> {
                    Toast.makeText(context, event.message, Toast.LENGTH_SHORT).show()
                }
                is UiEvent.ShowError -> {
                    // Показать error dialog
                }
                is UiEvent.Navigate -> {
                    // Навигация
                }
            }
        }
    }

    // UI на основе state
    when {
        uiState.isLoading -> LoadingScreen()
        else -> UserList(users = uiState.data)
    }
}
```

**В UI (Fragment/Activity)**:

```kotlin
class UserFragment : Fragment() {
    private val viewModel: UserViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Подписка на state
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    updateUI(state)
                }
            }
        }

        // Подписка на события
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.events.collect { event ->
                    handleEvent(event)
                }
            }
        }
    }

    private fun handleEvent(event: UiEvent) {
        when (event) {
            is UiEvent.ShowToast -> {
                Toast.makeText(requireContext(), event.message, Toast.LENGTH_SHORT).show()
            }
            is UiEvent.Navigate -> {
                findNavController().navigate(event.route)
            }
            is UiEvent.ShowError -> {
                Snackbar.make(requireView(), event.error, Snackbar.LENGTH_LONG).show()
            }
        }
    }
}
```

### Решение 2: Channel

Альтернатива SharedFlow - более простой API.

```kotlin
class UserViewModel : ViewModel() {
    private val _events = Channel<UiEvent>()
    val events = _events.receiveAsFlow()

    fun loadUsers() {
        viewModelScope.launch {
            try {
                val users = repository.getUsers()
                _events.send(UiEvent.ShowToast("Success"))
            } catch (e: Exception) {
                _events.send(UiEvent.ShowError(e.message ?: "Error"))
            }
        }
    }
}

// В UI - то же самое
LaunchedEffect(Unit) {
    viewModel.events.collect { event ->
        // Handle event
    }
}
```

### Решение 3: SingleLiveEvent (LiveData)

Для проектов на LiveData.

```kotlin
class SingleLiveEvent<T> : MutableLiveData<T>() {
    private val pending = AtomicBoolean(false)

    override fun observe(owner: LifecycleOwner, observer: Observer<in T>) {
        super.observe(owner) { t ->
            if (pending.compareAndSet(true, false)) {
                observer.onChanged(t)
            }
        }
    }

    override fun setValue(value: T?) {
        pending.set(true)
        super.setValue(value)
    }
}

// ViewModel
class UserViewModel : ViewModel() {
    private val _toastEvent = SingleLiveEvent<String>()
    val toastEvent: LiveData<String> = _toastEvent

    fun loadUsers() {
        viewModelScope.launch {
            try {
                val users = repository.getUsers()
                _toastEvent.value = "Loaded ${users.size} users"
            } catch (e: Exception) {
                _toastEvent.value = "Error: ${e.message}"
            }
        }
    }
}

// В Activity/Fragment
viewModel.toastEvent.observe(viewLifecycleOwner) { message ->
    Toast.makeText(requireContext(), message, Toast.LENGTH_SHORT).show()
}
```

### Решение 4: Consumed Event Wrapper

Для StateFlow - обертка с флагом "consumed".

```kotlin
data class Event<out T>(
    private val content: T,
    private val id: String = UUID.randomUUID().toString()
) {
    private var hasBeenHandled = false

    fun getContentIfNotHandled(): T? {
        return if (hasBeenHandled) {
            null
        } else {
            hasBeenHandled = true
            content
        }
    }

    fun peekContent(): T = content
}

// ViewModel
data class UiState(
    val isLoading: Boolean = false,
    val data: List<Item> = emptyList(),
    val toastEvent: Event<String>? = null
)

class UserViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadUsers() {
        viewModelScope.launch {
            try {
                val users = repository.getUsers()
                _uiState.update {
                    it.copy(
                        data = users,
                        toastEvent = Event("Loaded ${users.size} users")
                    )
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(toastEvent = Event("Error: ${e.message}"))
                }
            }
        }
    }
}

// В UI
LaunchedEffect(uiState.toastEvent) {
    uiState.toastEvent?.getContentIfNotHandled()?.let { message ->
        Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
    }
}
```

### Сравнение подходов

| Подход | Pros | Cons | Use Case |
|--------|------|------|----------|
| **SharedFlow** | - Идиоматично для Flow<br>- Replay control<br>- Multiple subscribers | WARNING: Чуть сложнее API | - Рекомендуется для Compose |
| **Channel** | - Простой API<br>- FIFO гарантия | WARNING: Только один subscriber | - Простые случаи |
| **SingleLiveEvent** | - Работает с LiveData<br>- Lifecycle-aware | - Устаревший подход<br>- Thread-safety issues | WARNING: Legacy проекты |
| **Event Wrapper** | - Все в одном State | - Boilerplate код<br>- Мутабельный hasBeenHandled | WARNING: Простые приложения |

### Best Practices

**1. Разделяйте State и Events**

```kotlin
// - ПРАВИЛЬНО
data class UiState(
    val data: List<Item>,        // Состояние
    val isLoading: Boolean        // Состояние
)

sealed class UiEvent {
    data class ShowToast(val msg: String) : UiEvent()  // Событие
    object NavigateBack : UiEvent()                     // Событие
}

// - НЕПРАВИЛЬНО - смешивание
data class UiState(
    val data: List<Item>,
    val isLoading: Boolean,
    val showToast: Boolean,        // Событие в State!
    val navigationRoute: String?   // Событие в State!
)
```

**2. Используйте правильный scope для подписки**

```kotlin
// - ПРАВИЛЬНО - repeatOnLifecycle
viewLifecycleOwner.lifecycleScope.launch {
    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.events.collect { event ->
            handleEvent(event)
        }
    }
}

// - НЕПРАВИЛЬНО - события могут потеряться
lifecycleScope.launch {
    viewModel.events.collect { event ->
        handleEvent(event)  // Не вызовется если Fragment в background
    }
}
```

**3. Тестируйте события**

```kotlin
@Test
fun `when load fails should emit error event`() = runTest {
    // Given
    val errorMessage = "Network error"
    coEvery { repository.getUsers() } throws Exception(errorMessage)

    val events = mutableListOf<UiEvent>()
    val job = launch {
        viewModel.events.collect { events.add(it) }
    }

    // When
    viewModel.loadUsers()

    // Then
    advanceUntilIdle()
    assertTrue(events.any { it is UiEvent.ShowError })

    job.cancel()
}
```

**English**: In MVI, handle one-time events (toasts, navigation) separately from State. Use **SharedFlow** with `replay = 0` (recommended for Compose), **Channel** for simpler cases, **SingleLiveEvent** for LiveData legacy projects, or **Event wrapper** with consumed flag. State should only contain persistent UI data. Events are ephemeral and consumed once. Collect events in `LaunchedEffect` (Compose) or `repeatOnLifecycle` (Views). Test events with `turbine` or manual collection.


---

## Related Questions

### Hub
- [[q-clean-architecture-android--android--hard]] - Clean Architecture principles

### Related (Medium)
- [[q-mvvm-pattern--android--medium]] - MVVM pattern explained
- [[q-mvvm-vs-mvp-differences--android--medium]] - MVVM vs MVP comparison
- [[q-what-is-viewmodel--android--medium]] - What is ViewModel
- [[q-why-is-viewmodel-needed-and-what-happens-in-it--android--medium]] - ViewModel purpose & internals
- [[q-until-what-point-does-viewmodel-guarantee-state-preservation--android--medium]] - ViewModel state preservation

### Advanced (Harder)
- [[q-mvi-architecture--android--hard]] - MVI architecture pattern
- [[q-mvi-handle-one-time-events--android--hard]] - MVI one-time event handling
- [[q-offline-first-architecture--android--hard]] - Offline-first architecture

