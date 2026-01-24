---
anki_cards:
- slug: q-stateflow-sharedflow-android--kotlin--medium-0-en
  language: en
  anki_id: 1768326284005
  synced_at: '2026-01-23T17:03:50.832895'
- slug: q-stateflow-sharedflow-android--kotlin--medium-0-ru
  language: ru
  anki_id: 1768326284030
  synced_at: '2026-01-23T17:03:50.834290'
---
# Question (EN)
> How to use `StateFlow` and `SharedFlow` in Android? Explain the difference, replay cache, when to use each, and patterns for `ViewModel`s.

## Ответ (RU)

`StateFlow` и `SharedFlow` — это горячие типы `Flow`, предназначенные для обмена состоянием и событиями между компонентами в Android приложениях.

### StateFlow: Управление Состоянием

```kotlin
class UserViewModel : ViewModel() {
    // StateFlow для состояния UI
    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    data class UiState(
        val user: User? = null,
        val isLoading: Boolean = false,
        val error: String? = null
    )

    data class User(val id: String, val name: String)

    fun loadUser(id: String) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            try {
                val user = fetchUser(id)
                _uiState.value = UiState(user = user, isLoading = false)
            } catch (e: Exception) {
                _uiState.value = UiState(error = e.message, isLoading = false)
            }
        }
    }

    private suspend fun fetchUser(id: String): User {
        delay(1000)
        return User(id, "User $id")
    }
}
```

### SharedFlow: События

```kotlin
class EventViewModel : ViewModel() {
    // SharedFlow для одноразовых событий (по умолчанию replay = 0, без буфера —
    // коллектор должен быть активен в момент эмиссии, иначе событие потеряется)
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()

    sealed class Event {
        data class ShowToast(val message: String) : Event()
        object NavigateBack : Event()
    }

    fun saveData() {
        viewModelScope.launch {
            try {
                repository.save()
                _events.emit(Event.ShowToast("Saved!"))
            } catch (e: Exception) {
                _events.emit(Event.ShowToast("Error: ${e.message}"))
            }
        }
    }

    private val repository = Repository()
    class Repository {
        suspend fun save() {}
    }
}
```

### Ключевые Различия

```kotlin
/**
 * StateFlow vs SharedFlow
 *
 * StateFlow:
 * - Всегда имеет текущее значение
 * - Встроенный replay = 1 (последнее значение всегда доступно новым коллекторам)
 * - Эмиттирует только последнее установленное значение (промежуточные значения
 *   могут быть пропущены для медленных коллекторах)
 * - Для управления СОСТОЯНИЕМ (UI state, необходимые для восстановления значения)
 *
 * SharedFlow:
 * - Может не иметь значения по умолчанию
 * - Настраиваемый replay (сколько последних значений получат новые коллектора)
 * - Дополнительная емкость буфера и onBufferOverflow позволяют настраивать,
 *   сколько значений хранится; по умолчанию replay = 0 и нет буфера
 * - Для СОБЫТИЙ и потоков, где важно доставить последовательность значений,
 *   при необходимости настраивая replay/буфер
 */

class ComparisonExample : ViewModel() {
    // StateFlow: Текущее состояние экрана
    private val _screenState = MutableStateFlow(ScreenState.Loading)
    val screenState = _screenState.asStateFlow()

    // SharedFlow: Одноразовые события навигации
    // (обычно используют replay = 0 для "одноразовости")
    private val _navigationEvents = MutableSharedFlow<Navigation>(replay = 0)
    val navigationEvents = _navigationEvents.asSharedFlow()

    sealed class ScreenState {
        object Loading : ScreenState()
        data class Content(val data: String) : ScreenState()
    }

    sealed class Navigation {
        object GoBack : Navigation()
        data class GoToDetails(val id: String) : Navigation()
    }
}
```

### Когда Использовать Каждый

```kotlin
// StateFlow: Для состояния, которое должен стабильно отображать UI
class GoodStateUsage : ViewModel() {
    private val _isLoggedIn = MutableStateFlow(false)
    val isLoggedIn = _isLoggedIn.asStateFlow()

    private val _userName = MutableStateFlow<String?>(null)
    val userName = _userName.asStateFlow()
}

// SharedFlow: Для событий (навигация, сообщения), где подходящий выбор
// параметров (replay/буфер) предотвращает потерю нужных событий
class GoodEventUsage : ViewModel() {
    private val _snackbarMessages = MutableSharedFlow<String>(replay = 0)
    val snackbarMessages = _snackbarMessages.asSharedFlow()

    private val _navigationCommands = MutableSharedFlow<NavCommand>(replay = 0)
    val navigationCommands = _navigationCommands.asSharedFlow()

    sealed class NavCommand {
        object Back : NavCommand()
    }
}
```

---

## Answer (EN)

`StateFlow` and `SharedFlow` are hot `Flow` types designed for sharing state and events between components in Android applications.

### StateFlow: State Management

```kotlin
class UserViewModel : ViewModel() {
    // StateFlow for UI state
    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    data class UiState(
        val user: User? = null,
        val isLoading: Boolean = false,
        val error: String? = null
    )

    data class User(val id: String, val name: String)

    fun loadUser(id: String) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            try {
                val user = fetchUser(id)
                _uiState.value = UiState(user = user, isLoading = false)
            } catch (e: Exception) {
                _uiState.value = UiState(error = e.message, isLoading = false)
            }
        }
    }

    private suspend fun fetchUser(id: String): User {
        delay(1000)
        return User(id, "User $id")
    }
}
```

### SharedFlow: Events

```kotlin
class EventViewModel : ViewModel() {
    // SharedFlow for one-time events (by default replay = 0 and no extra buffer,
    // so collectors must be active at emission time or the event is lost)
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()

    sealed class Event {
        data class ShowToast(val message: String) : Event()
        object NavigateBack : Event()
    }

    fun saveData() {
        viewModelScope.launch {
            try {
                repository.save()
                _events.emit(Event.ShowToast("Saved!"))
            } catch (e: Exception) {
                _events.emit(Event.ShowToast("Error: ${e.message}"))
            }
        }
    }

    private val repository = Repository()
    class Repository {
        suspend fun save() {}
    }
}
```

### Key Differences

```kotlin
/**
 * StateFlow vs SharedFlow
 *
 * StateFlow:
 * - Always has a current value
 * - Built-in replay = 1 (latest value is always delivered to new collectors)
 * - Effectively emits only the latest set value (intermediate values may be
 *   skipped for slow collectors)
 * - For STATE management (UI state, values that must be restorable)
 *
 * SharedFlow:
 * - May have no value by default
 * - Configurable replay (how many recent values new collectors get)
 * - Extra buffer capacity and onBufferOverflow control how many values are kept;
 *   by default replay = 0 and no buffer
 * - For EVENTS and streams where delivering a sequence of values matters,
 *   using appropriate replay/buffer configuration
 */

class ComparisonExample : ViewModel() {
    // StateFlow: Current screen state
    private val _screenState = MutableStateFlow(ScreenState.Loading)
    val screenState = _screenState.asStateFlow()

    // SharedFlow: One-time navigation events
    // (commonly configured with replay = 0 for "one-off" semantics)
    private val _navigationEvents = MutableSharedFlow<Navigation>(replay = 0)
    val navigationEvents = _navigationEvents.asSharedFlow()

    sealed class ScreenState {
        object Loading : ScreenState()
        data class Content(val data: String) : ScreenState()
    }

    sealed class Navigation {
        object GoBack : Navigation()
        data class GoToDetails(val id: String) : Navigation()
    }
}
```

### When to Use Each

```kotlin
// StateFlow: For state that UI must consistently reflect
class GoodStateUsage : ViewModel() {
    private val _isLoggedIn = MutableStateFlow(false)
    val isLoggedIn = _isLoggedIn.asStateFlow()

    private val _userName = MutableStateFlow<String?>(null)
    val userName = _userName.asStateFlow()
}

// SharedFlow: For events (navigation, messages); choose replay/buffer so that
// you don't lose important events unintentionally
class GoodEventUsage : ViewModel() {
    private val _snackbarMessages = MutableSharedFlow<String>(replay = 0)
    val snackbarMessages = _snackbarMessages.asSharedFlow()

    private val _navigationCommands = MutableSharedFlow<NavCommand>(replay = 0)
    val navigationCommands = _navigationCommands.asSharedFlow()

    sealed class NavCommand {
        object Back : NavCommand()
    }
}
```

---

## Follow-ups

1. How would you collect `StateFlow` in an `Activity` or `Fragment` using lifecycle-aware scopes (e.g., `repeatOnLifecycle`), and what are the common pitfalls such as leaks or missed emissions?
2. How does the replay cache in `SharedFlow` work in practice, and how would you configure `replay` and buffer capacity differently for one-off UI events versus continuous data streams?
3. Compare `StateFlow` and `LiveData` for UI state management in Android, considering cancellation, backpressure, and testing. When would you choose one over the other?
4. How do you test `StateFlow` and `SharedFlow` in unit tests, including controlling coroutine dispatchers, using `Turbine` or similar libraries, and asserting emissions order?
5. How would you migrate an existing `LiveData`-based `ViewModel` to use `StateFlow`/`SharedFlow` while keeping the UI compatible during the transition period?

---

## References

- [StateFlow Documentation](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow)
- [[c-kotlin]]
- [[c-flow]]

---

## Related Questions

### Related (Medium)
- [[q-testing-stateflow-sharedflow--kotlin--medium]] - Coroutines
- [[q-stateflow-sharedflow-differences--kotlin--medium]] - Stateflow
- [[q-sharedflow-stateflow--kotlin--medium]] - `Flow`
- [[q-sharedflow-replay-buffer-config--kotlin--medium]] - Coroutines

### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive `Flow` introduction
