---
id: kotlin-111
title: "SharedFlow vs StateFlow / SharedFlow против StateFlow"
aliases: []

# Classification
topic: kotlin
subtopics:
  - flow
  - hot-flow
  - sharedflow
  - state-management
  - stateflow
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive comparison of SharedFlow and StateFlow

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-flow-basics--kotlin--easy, q-hot-cold-flows--kotlin--medium, q-stateflow-sharedflow-differences--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-31

tags: [coroutines, difficulty/medium, flow, hot-flow, kotlin, sharedflow, state-management, stateflow]
date created: Saturday, November 1st 2025, 9:25:31 am
date modified: Saturday, November 1st 2025, 5:43:23 pm
---

# Question (EN)
> What's the difference between SharedFlow and StateFlow? When should you use each?

# Вопрос (RU)
> В чём разница между SharedFlow и StateFlow? Когда использовать каждый из них?

---

## Answer (EN)

**SharedFlow** and **StateFlow** are hot Flow implementations designed for sharing state and events among multiple collectors. While both are hot flows that emit values to all active collectors, they serve different purposes and have distinct characteristics.

### Key Differences

| Aspect | StateFlow | SharedFlow |
|--------|-----------|------------|
| **Purpose** | State holder | Event broadcaster |
| **Initial Value** | Required | Optional |
| **Replay** | Always 1 | Configurable (0+) |
| **Conflation** | Always conflated | Configurable |
| **Distinct Values** | Only distinct | All values |
| **Use Case** | UI state, config | Events, notifications |

### StateFlow: State Holder

StateFlow is specifically designed for representing state that always has a value:

```kotlin
interface StateFlow<out T> : SharedFlow<T> {
    val value: T  // Always has a current value
}

// Creating StateFlow
val _state = MutableStateFlow<Int>(0)  // Initial value required
val state: StateFlow<Int> = _state.asStateFlow()

// Reading current value
println(_state.value)  // Direct access

// Updating value
_state.value = 1
_state.update { it + 1 }  // Atomic update
```

**StateFlow Characteristics**:
1. **Always has a value** - Must provide initial value
2. **Replay = 1** - New collectors immediately receive current value
3. **Conflated** - Only latest value matters
4. **Distinct values only** - Doesn't emit if new value equals current
5. **Never completes** - Remains active until scope cancelled

### SharedFlow: Event Broadcaster

SharedFlow is a general-purpose hot flow for broadcasting values:

```kotlin
// Creating SharedFlow
val _events = MutableSharedFlow<Event>()  // No initial value
val events: SharedFlow<Event> = _events.asSharedFlow()

// Emitting values
_events.emit(Event.UserLoggedIn)
_events.tryEmit(Event.DataLoaded)  // Non-suspending

// Configurable SharedFlow
val _results = MutableSharedFlow<Result>(
    replay = 2,        // Cache last 2 values
    extraBufferCapacity = 5,  // Additional buffer
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)
```

**SharedFlow Characteristics**:
1. **No initial value required** - Can be empty
2. **Configurable replay** - 0 to unlimited
3. **No conflation by default** - All values emitted
4. **Emits all values** - Including duplicates
5. **Can complete** - Via flow operators

### Real-World Example: ViewModel

```kotlin
class UserViewModel : ViewModel() {
    // StateFlow for state
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    // SharedFlow for events
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()

    fun loadUser(id: Int) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            try {
                val user = repository.getUser(id)
                _uiState.value = UiState.Success(user)
                _events.emit(Event.ShowToast("User loaded"))
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message)
                _events.emit(Event.ShowError(e.message))
            }
        }
    }
}

// UI observing both
class UserActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Collect state - always receives current value
        lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                when (state) {
                    is UiState.Loading -> showLoading()
                    is UiState.Success -> showUser(state.user)
                    is UiState.Error -> showError(state.message)
                }
            }
        }

        // Collect events - only new events
        lifecycleScope.launch {
            viewModel.events.collect { event ->
                when (event) {
                    is Event.ShowToast -> Toast.makeText(this@UserActivity, event.message, Toast.LENGTH_SHORT).show()
                    is Event.ShowError -> showErrorDialog(event.message)
                }
            }
        }
    }
}
```

### StateFlow Deep Dive

#### Creating StateFlow

```kotlin
// MutableStateFlow with initial value
val state1 = MutableStateFlow<String>("initial")

// From regular Flow (needs initial value)
val flow = flowOf(1, 2, 3)
val state2 = flow.stateIn(
    scope = viewModelScope,
    started = SharingStarted.WhileSubscribed(5000),
    initialValue = 0
)
```

#### StateFlow Updates

```kotlin
class CounterViewModel : ViewModel() {
    private val _counter = MutableStateFlow(0)
    val counter: StateFlow<Int> = _counter.asStateFlow()

    // Direct assignment
    fun increment() {
        _counter.value = _counter.value + 1
    }

    // Atomic update (thread-safe)
    fun incrementAtomic() {
        _counter.update { it + 1 }
    }

    // Update and get (atomic)
    fun incrementAndGet(): Int {
        return _counter.updateAndGet { it + 1 }
    }

    // Conditional update
    fun reset() {
        _counter.compareAndSet(expect = _counter.value, update = 0)
    }
}
```

#### StateFlow Conflation

```kotlin
// StateFlow is always conflated
viewModelScope.launch {
    _state.value = 1
    _state.value = 2
    _state.value = 3
    // Collector might only see: 3 (intermediate values skipped)
}

// Use SharedFlow if all values are important
val _allValues = MutableSharedFlow<Int>()
viewModelScope.launch {
    _allValues.emit(1)
    _allValues.emit(2)
    _allValues.emit(3)
    // Collector sees: 1, 2, 3 (all values)
}
```

#### StateFlow Distinct Values

```kotlin
val state = MutableStateFlow("A")

viewModelScope.launch {
    state.value = "B"  // Emitted
    state.value = "B"  // NOT emitted (same value)
    state.value = "C"  // Emitted
    state.value = "C"  // NOT emitted (same value)
}

// Collector receives: "A" (initial), "B", "C"
```

### SharedFlow Deep Dive

#### Creating SharedFlow

```kotlin
// Default: no replay, no buffer
val shared1 = MutableSharedFlow<String>()

// With replay
val shared2 = MutableSharedFlow<String>(
    replay = 5  // Cache last 5 values for new collectors
)

// With buffer
val shared3 = MutableSharedFlow<String>(
    replay = 1,
    extraBufferCapacity = 10,  // Buffer for slow collectors
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)

// From regular Flow
val flow = flowOf(1, 2, 3)
val shared4 = flow.shareIn(
    scope = viewModelScope,
    started = SharingStarted.WhileSubscribed(),
    replay = 1
)
```

#### SharedFlow Replay

```kotlin
class EventBus {
    private val _events = MutableSharedFlow<Event>(
        replay = 3  // Cache last 3 events
    )
    val events: SharedFlow<Event> = _events.asSharedFlow()

    suspend fun post(event: Event) {
        _events.emit(event)
    }
}

val bus = EventBus()

// Emit some events
bus.post(Event.A)
bus.post(Event.B)
bus.post(Event.C)

// New collector receives last 3 events immediately
bus.events.collect { event ->
    // Receives: Event.A, Event.B, Event.C, then waits for new events
    println(event)
}
```

#### SharedFlow Buffer Strategies

```kotlin
// DROP_OLDEST: Remove oldest when buffer full
val dropOldest = MutableSharedFlow<Int>(
    replay = 0,
    extraBufferCapacity = 5,
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)

// DROP_LATEST: Drop newest when buffer full
val dropLatest = MutableSharedFlow<Int>(
    replay = 0,
    extraBufferCapacity = 5,
    onBufferOverflow = BufferOverflow.DROP_LATEST
)

// SUSPEND: Suspend emitter when buffer full (backpressure)
val suspend = MutableSharedFlow<Int>(
    replay = 0,
    extraBufferCapacity = 5,
    onBufferOverflow = BufferOverflow.SUSPEND
)
```

### When to Use StateFlow

#### Use StateFlow For:

```kotlin
// 1. UI State
class ProductsViewModel : ViewModel() {
    private val _products = MutableStateFlow<List<Product>>(emptyList())
    val products: StateFlow<List<Product>> = _products.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()
}

// 2. Configuration
class AppConfig {
    private val _theme = MutableStateFlow(Theme.LIGHT)
    val theme: StateFlow<Theme> = _theme.asStateFlow()

    private val _language = MutableStateFlow(Language.EN)
    val language: StateFlow<Language> = _language.asStateFlow()
}

// 3. User Session
class SessionManager {
    private val _currentUser = MutableStateFlow<User?>(null)
    val currentUser: StateFlow<User?> = _currentUser.asStateFlow()

    private val _isLoggedIn = MutableStateFlow(false)
    val isLoggedIn: StateFlow<Boolean> = _isLoggedIn.asStateFlow()
}

// 4. Data Cache
class Repository {
    private val _cachedData = MutableStateFlow<Data?>(null)
    val cachedData: StateFlow<Data?> = _cachedData.asStateFlow()
}
```

### When to Use SharedFlow

#### Use SharedFlow For:

```kotlin
// 1. One-time Events
class LoginViewModel : ViewModel() {
    private val _navigationEvents = MutableSharedFlow<NavigationEvent>()
    val navigationEvents: SharedFlow<NavigationEvent> = _navigationEvents.asSharedFlow()

    fun onLoginSuccess() {
        viewModelScope.launch {
            _navigationEvents.emit(NavigationEvent.NavigateToHome)
        }
    }
}

// 2. Notifications
class NotificationManager {
    private val _notifications = MutableSharedFlow<Notification>(replay = 5)
    val notifications: SharedFlow<Notification> = _notifications.asSharedFlow()

    suspend fun notify(message: String) {
        _notifications.emit(Notification(message, System.currentTimeMillis()))
    }
}

// 3. Multiple Distinct Values Matter
class SearchViewModel : ViewModel() {
    private val _searchResults = MutableSharedFlow<List<Result>>()
    val searchResults: SharedFlow<List<Result>> = _searchResults.asSharedFlow()

    fun search(query: String) {
        viewModelScope.launch {
            // All results emitted, even if same list
            _searchResults.emit(performSearch(query))
        }
    }
}

// 4. Event Bus
class EventBus {
    private val _events = MutableSharedFlow<AppEvent>(
        replay = 10,
        extraBufferCapacity = 20,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val events: SharedFlow<AppEvent> = _events.asSharedFlow()

    suspend fun post(event: AppEvent) {
        _events.emit(event)
    }
}
```

### StateFlow Vs SharedFlow: Detailed Comparison

#### Initialization

```kotlin
// StateFlow: Must have initial value
val state = MutableStateFlow<String>("initial")  //
// val state = MutableStateFlow<String>()        //  Error

// SharedFlow: No initial value required
val shared = MutableSharedFlow<String>()         //
val shared2 = MutableSharedFlow<String?>(replay = 1).apply {
    tryEmit(null)  // Can set initial value if needed
}
```

#### Value Access

```kotlin
// StateFlow: Direct value access
val state = MutableStateFlow(10)
println(state.value)  // 10
state.value = 20      // Direct assignment

// SharedFlow: No value property
val shared = MutableSharedFlow<Int>()
// println(shared.value)  //  Error: no value property
```

#### Collecting

```kotlin
// StateFlow: Immediately emits current value
val state = MutableStateFlow("current")
state.collect { value ->
    // Immediately receives: "current"
    println(value)
}

// SharedFlow (no replay): Only receives new values
val shared = MutableSharedFlow<String>()
shared.collect { value ->
    // Waits for first emit()
    println(value)
}

// SharedFlow (with replay): Receives cached values
val sharedWithReplay = MutableSharedFlow<String>(replay = 1)
sharedWithReplay.emit("cached")
sharedWithReplay.collect { value ->
    // Immediately receives: "cached"
    println(value)
}
```

### Advanced Patterns

#### Converting Between StateFlow and SharedFlow

```kotlin
// SharedFlow to StateFlow
val sharedFlow = MutableSharedFlow<Int>(replay = 1).apply { tryEmit(0) }
val stateFlow = sharedFlow
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.Eagerly,
        initialValue = 0
    )

// StateFlow to SharedFlow (already is!)
val stateFlow = MutableStateFlow(0)
val sharedFlow: SharedFlow<Int> = stateFlow  // StateFlow is SharedFlow
```

#### Combining Multiple Flows

```kotlin
class CombinedViewModel : ViewModel() {
    private val _isLoading = MutableStateFlow(false)
    private val _error = MutableStateFlow<String?>(null)
    private val _data = MutableStateFlow<Data?>(null)

    val uiState: StateFlow<UiState> = combine(
        _isLoading,
        _error,
        _data
    ) { isLoading, error, data ->
        when {
            isLoading -> UiState.Loading
            error != null -> UiState.Error(error)
            data != null -> UiState.Success(data)
            else -> UiState.Empty
        }
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = UiState.Empty
    )
}
```

#### Channel-backed SharedFlow

```kotlin
class EventManager {
    private val eventChannel = Channel<Event>(Channel.UNLIMITED)

    val events: SharedFlow<Event> = eventChannel.receiveAsFlow()
        .shareIn(
            scope = GlobalScope,  // Or appropriate scope
            started = SharingStarted.Eagerly,
            replay = 0
        )

    fun sendEvent(event: Event) {
        eventChannel.trySend(event)
    }
}
```

### Best Practices

#### DO:
```kotlin
// Use StateFlow for state
class GoodViewModel : ViewModel() {
    private val _state = MutableStateFlow<UiState>(UiState.Initial)
    val state: StateFlow<UiState> = _state.asStateFlow()
}

// Use SharedFlow for events
class GoodViewModel : ViewModel() {
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()
}

// Expose read-only versions
class GoodViewModel : ViewModel() {
    private val _data = MutableStateFlow<Data?>(null)
    val data: StateFlow<Data?> = _data.asStateFlow()  // Read-only
}

// Use appropriate replay for SharedFlow
val notifications = MutableSharedFlow<String>(
    replay = 5,  // Keep last 5 for new subscribers
    extraBufferCapacity = 10
)
```

#### DON'T:
```kotlin
// Don't expose mutable versions
class BadViewModel : ViewModel() {
    val state = MutableStateFlow<UiState>(UiState.Initial)  //  Bad
}

// Don't use SharedFlow for state
class BadViewModel : ViewModel() {
    private val _isLoading = MutableSharedFlow<Boolean>()  //  Use StateFlow
}

// Don't use StateFlow for events
class BadViewModel : ViewModel() {
    private val _events = MutableStateFlow<Event?>(null)  //  Use SharedFlow
}

// Don't forget initial value for StateFlow
// val state = MutableStateFlow<String>()  //  Error
```

### Performance Considerations

```kotlin
// StateFlow: Best for state (conflated, distinct)
val state = MutableStateFlow(0)
repeat(1000) {
    state.value = it
}
// Collector only sees latest value

// SharedFlow: All emissions reach collectors
val shared = MutableSharedFlow<Int>()
repeat(1000) {
    shared.emit(it)
}
// Collector receives all 1000 values (if buffer allows)
```

---

## Ответ (RU)

**SharedFlow** и **StateFlow** — горячие реализации Flow, предназначенные для разделения состояния и событий между несколькими коллекторами. Хотя оба являются горячими потоками, излучающими значения всем активным коллекторам, они служат разным целям и имеют разные характеристики.

### Ключевые Различия

| Аспект | StateFlow | SharedFlow |
|--------|-----------|------------|
| **Назначение** | Хранитель состояния | Вещатель событий |
| **Начальное значение** | Обязательно | Опционально |
| **Replay** | Всегда 1 | Настраиваемый (0+) |
| **Conflation** | Всегда conflated | Настраиваемый |
| **Различные значения** | Только различные | Все значения |
| **Случай использования** | UI состояние, конфигурация | События, уведомления |

### StateFlow: Хранитель Состояния

StateFlow специально разработан для представления состояния, которое всегда имеет значение:

```kotlin
interface StateFlow<out T> : SharedFlow<T> {
    val value: T  // Всегда имеет текущее значение
}

// Создание StateFlow
val _state = MutableStateFlow<Int>(0)  // Начальное значение обязательно
val state: StateFlow<Int> = _state.asStateFlow()

// Чтение текущего значения
println(_state.value)  // Прямой доступ

// Обновление значения
_state.value = 1
_state.update { it + 1 }  // Атомарное обновление
```

**Характеристики StateFlow**:
1. **Всегда имеет значение** - Необходимо предоставить начальное значение
2. **Replay = 1** - Новые коллекторы сразу получают текущее значение
3. **Conflated** - Важно только последнее значение
4. **Только различные значения** - Не излучает если новое значение равно текущему
5. **Никогда не завершается** - Остаётся активным пока scope не отменён

### SharedFlow: Вещатель Событий

SharedFlow — универсальный горячий поток для вещания значений:

```kotlin
// Создание SharedFlow
val _events = MutableSharedFlow<Event>()  // Начальное значение не нужно
val events: SharedFlow<Event> = _events.asSharedFlow()

// Излучение значений
_events.emit(Event.UserLoggedIn)
_events.tryEmit(Event.DataLoaded)  // Не suspend

// Настраиваемый SharedFlow
val _results = MutableSharedFlow<Result>(
    replay = 2,        // Кешировать последние 2 значения
    extraBufferCapacity = 5,  // Дополнительный буфер
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)
```

**Характеристики SharedFlow**:
1. **Начальное значение не требуется** - Может быть пустым
2. **Настраиваемый replay** - От 0 до безлимит
3. **Без conflation по умолчанию** - Излучаются все значения
4. **Излучает все значения** - Включая дубликаты
5. **Может завершиться** - Через операторы flow

### Реальный Пример: ViewModel

```kotlin
class UserViewModel : ViewModel() {
    // StateFlow для состояния
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    // SharedFlow для событий
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()

    fun loadUser(id: Int) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            try {
                val user = repository.getUser(id)
                _uiState.value = UiState.Success(user)
                _events.emit(Event.ShowToast("Пользователь загружен"))
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message)
                _events.emit(Event.ShowError(e.message))
            }
        }
    }
}
```

### Когда Использовать StateFlow

#### Использовать StateFlow Для:

```kotlin
// 1. Состояние UI
class ProductsViewModel : ViewModel() {
    private val _products = MutableStateFlow<List<Product>>(emptyList())
    val products: StateFlow<List<Product>> = _products.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()
}

// 2. Конфигурация
class AppConfig {
    private val _theme = MutableStateFlow(Theme.LIGHT)
    val theme: StateFlow<Theme> = _theme.asStateFlow()
}

// 3. Пользовательская сессия
class SessionManager {
    private val _currentUser = MutableStateFlow<User?>(null)
    val currentUser: StateFlow<User?> = _currentUser.asStateFlow()
}
```

### Когда Использовать SharedFlow

#### Использовать SharedFlow Для:

```kotlin
// 1. Одноразовые события
class LoginViewModel : ViewModel() {
    private val _navigationEvents = MutableSharedFlow<NavigationEvent>()
    val navigationEvents: SharedFlow<NavigationEvent> = _navigationEvents.asSharedFlow()

    fun onLoginSuccess() {
        viewModelScope.launch {
            _navigationEvents.emit(NavigationEvent.NavigateToHome)
        }
    }
}

// 2. Уведомления
class NotificationManager {
    private val _notifications = MutableSharedFlow<Notification>(replay = 5)
    val notifications: SharedFlow<Notification> = _notifications.asSharedFlow()

    suspend fun notify(message: String) {
        _notifications.emit(Notification(message, System.currentTimeMillis()))
    }
}

// 3. Event Bus
class EventBus {
    private val _events = MutableSharedFlow<AppEvent>(
        replay = 10,
        extraBufferCapacity = 20,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val events: SharedFlow<AppEvent> = _events.asSharedFlow()

    suspend fun post(event: AppEvent) {
        _events.emit(event)
    }
}
```

### Лучшие Практики

#### ДЕЛАТЬ:
```kotlin
// Использовать StateFlow для состояния
class GoodViewModel : ViewModel() {
    private val _state = MutableStateFlow<UiState>(UiState.Initial)
    val state: StateFlow<UiState> = _state.asStateFlow()
}

// Использовать SharedFlow для событий
class GoodViewModel : ViewModel() {
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()
}

// Выставлять read-only версии
class GoodViewModel : ViewModel() {
    private val _data = MutableStateFlow<Data?>(null)
    val data: StateFlow<Data?> = _data.asStateFlow()  // Только для чтения
}
```

#### НЕ ДЕЛАТЬ:
```kotlin
// Не выставлять изменяемые версии
class BadViewModel : ViewModel() {
    val state = MutableStateFlow<UiState>(UiState.Initial)  //  Плохо
}

// Не использовать SharedFlow для состояния
class BadViewModel : ViewModel() {
    private val _isLoading = MutableSharedFlow<Boolean>()  //  Использовать StateFlow
}

// Не использовать StateFlow для событий
class BadViewModel : ViewModel() {
    private val _events = MutableStateFlow<Event?>(null)  //  Использовать SharedFlow
}
```

---

## References

- [Kotlin SharedFlow Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/)
- [Kotlin StateFlow Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/)
- [StateFlow and SharedFlow Guide](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow)

## Related Questions

### Related (Medium)
- [[q-testing-stateflow-sharedflow--kotlin--medium]] - Coroutines
- [[q-stateflow-sharedflow-android--kotlin--medium]] - Coroutines
- [[q-stateflow-sharedflow-differences--kotlin--medium]] - Stateflow
- [[q-sharedflow-replay-buffer-config--kotlin--medium]] - Coroutines

### Advanced (Harder)
- [[q-actor-pattern--kotlin--hard]] - Coroutines
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction

## MOC Links

- [[moc-kotlin]]
