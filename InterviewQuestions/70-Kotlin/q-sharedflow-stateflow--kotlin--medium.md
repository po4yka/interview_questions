---
---
---\
id: kotlin-111
title: "SharedFlow vs StateFlow / SharedFlow против StateFlow"
aliases: ["SharedFlow vs StateFlow", "SharedFlow против StateFlow"]

# Classification
topic: kotlin
subtopics: [flow, sharedflow, stateflow]
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
related: [c-flow, c-kotlin, q-flow-basics--kotlin--easy]

# Timestamps
created: 2025-10-12
updated: 2025-11-09

tags: [coroutines, difficulty/medium, flow, hot-flow, kotlin, sharedflow, state-management, stateflow]
---\
# Вопрос (RU)
> В чём разница между `SharedFlow` и `StateFlow`? Когда использовать каждый из них?

---

# Question (EN)
> What's the difference between `SharedFlow` and `StateFlow`? When should you use each?

## Ответ (RU)

**`SharedFlow`** и **`StateFlow`** — горячие реализации `Flow`, предназначенные для разделения состояния и событий между несколькими коллекторами. Хотя оба являются горячими потоками, излучающими значения всем активным коллекторам, они служат разным целям и имеют разные характеристики.

### Ключевые Различия

| Аспект | `StateFlow` | `SharedFlow` |
|--------|-------------|--------------|
| **Назначение** | Хранитель состояния | Вещатель событий / универсальный шейред-поток |
| **Начальное значение** | Обязательно | Опционально |
| **Replay** | Всегда 1 | Настраиваемый (0+) |
| **Conflation** | Всегда conflated | Настраиваемый |
| **Различные значения** | Только различные | Все значения |
| **Случай использования** | UI состояние, конфигурация | События, уведомления, стримы данных |

### `StateFlow`: Хранитель Состояния

`StateFlow` специально разработан для представления состояния, которое всегда имеет актуальное значение:

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

**Характеристики `StateFlow`**:
1. **Всегда имеет значение** — необходимо предоставить начальное значение.
2. **Replay = 1** — новые коллекторы сразу получают текущее значение.
3. **Conflated** — важно только последнее значение, медленные коллекторы могут пропускать промежуточные.
4. **Только различные значения** — не излучает, если новое значение равно текущему (`==`).
5. **Обычно не завершается самостоятельно** — в типичных сценариях (например, в `ViewModel`) остаётся активным, пока не отменён scope или не завершится источник; как `Flow` теоретически может завершиться при завершении апстрима.

### Глубокое Погружение В `StateFlow`

#### Создание `StateFlow`

```kotlin
// MutableStateFlow с начальным значением
val state1 = MutableStateFlow<String>("initial")

// Из обычного Flow (нужно начальное значение)
val flow = flowOf(1, 2, 3)
val state2 = flow.stateIn(
    scope = viewModelScope,
    started = SharingStarted.WhileSubscribed(5000),
    initialValue = 0
)
```

#### Обновление `StateFlow`

```kotlin
class CounterViewModel : ViewModel() {
    private val _counter = MutableStateFlow(0)
    val counter: StateFlow<Int> = _counter.asStateFlow()

    // Прямое присвоение
    fun increment() {
        _counter.value = _counter.value + 1
    }

    // Атомарное обновление (потокобезопасно)
    fun incrementAtomic() {
        _counter.update { it + 1 }
    }

    // Атомарное обновление с возвратом результата
    fun incrementAndGet(): Int {
        return _counter.updateAndGet { it + 1 }
    }

    // Условное обновление (успешно, только если значение не изменилось конкурентно)
    fun reset() {
        _counter.compareAndSet(expect = _counter.value, update = 0)
    }
}
```

#### Conflation В `StateFlow`

```kotlin
// StateFlow всегда conflated
viewModelScope.launch {
    _state.value = 1
    _state.value = 2
    _state.value = 3
    // Медленный коллектор может увидеть только 3 (промежуточные пропущены)
}

// Используйте SharedFlow, если важны все значения
val _allValues = MutableSharedFlow<Int>()
viewModelScope.launch {
    _allValues.emit(1)
    _allValues.emit(2)
    _allValues.emit(3)
    // Коллектор может получить 1, 2, 3 (с учётом настроек буфера/overflow)
}
```

#### Только Различные Значения В `StateFlow`

```kotlin
val state = MutableStateFlow("A")

viewModelScope.launch {
    state.value = "B"  // Эмитируется
    state.value = "B"  // НЕ эмитируется (то же значение)
    state.value = "C"  // Эмитируется
    state.value = "C"  // НЕ эмитируется
}

// Коллектор получит: "A" (начальное), "B", "C"
```

### `SharedFlow`: Вещатель Событий

`SharedFlow` — универсальный горячий поток для вещания значений:

```kotlin
// Создание SharedFlow
val _events = MutableSharedFlow<Event>()  // Начальное значение не нужно
val events: SharedFlow<Event> = _events.asSharedFlow()

// Излучение значений
_events.emit(Event.UserLoggedIn)
_events.tryEmit(Event.DataLoaded)  // Не suspend

// Настраиваемый SharedFlow
val _results = MutableSharedFlow<Result>(
    replay = 2,              // Кешировать последние 2 значения для новых коллекторов
    extraBufferCapacity = 5, // Дополнительный буфер
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)
```

**Характеристики `SharedFlow`**:
1. **Начальное значение не требуется** — может быть пустым.
2. **Настраиваемый replay** — от 0 до безлимит; новые коллекторы получают последние `replay` значений.
3. **Без conflation по умолчанию** — по умолчанию старается доставить все значения (с учётом настроек буфера).
4. **Излучает все значения** — включая дубликаты.
5. **Сам по себе не завершается** — но можно строить поверх него `Flow`, который завершается (`take`, `first` и т.п.).

### Глубокое Погружение В `SharedFlow`

#### Создание `SharedFlow`

```kotlin
// По умолчанию: без replay и extraBuffer
val shared1 = MutableSharedFlow<String>()

// С replay
val shared2 = MutableSharedFlow<String>(
    replay = 5  // Хранить последние 5 значений для новых коллекторов
)

// С буфером и политикой переполнения
val shared3 = MutableSharedFlow<String>(
    replay = 1,
    extraBufferCapacity = 10,
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)

// Из обычного Flow
val flow = flowOf(1, 2, 3)
val shared4 = flow.shareIn(
    scope = viewModelScope,
    started = SharingStarted.WhileSubscribed(),
    replay = 1
)
```

#### Replay В `SharedFlow`

```kotlin
class EventBus {
    private val _events = MutableSharedFlow<Event>(
        replay = 3  // Кэш до 3 последних событий для новых подписчиков
    )
    val events: SharedFlow<Event> = _events.asSharedFlow()

    suspend fun post(event: Event) {
        _events.emit(event)
    }
}

val bus = EventBus()

// Эмитим события
bus.post(Event.A)
bus.post(Event.B)
bus.post(Event.C)

// Новый коллектор сразу получит до 3 последних событий (здесь: A, B, C), затем новые
bus.events.collect { event ->
    println(event)
}
```

#### Стратегии Буфера В `SharedFlow`

```kotlin
// DROP_OLDEST: удалять старые при переполнении буфера (replay + extra)
val dropOldest = MutableSharedFlow<Int>(
    replay = 0,
    extraBufferCapacity = 5,
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)

// DROP_LATEST: отбрасывать новые при полном буфере
val dropLatest = MutableSharedFlow<Int>(
    replay = 0,
    extraBufferCapacity = 5,
    onBufferOverflow = BufferOverflow.DROP_LATEST
)

// SUSPEND: блокировать эмиттера при полном буфере
val suspend = MutableSharedFlow<Int>(
    replay = 0,
    extraBufferCapacity = 5,
    onBufferOverflow = BufferOverflow.SUSPEND
)
```

### Реальный Пример: `ViewModel`

```kotlin
class UserViewModel : ViewModel() {
    // StateFlow для состояния
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    // SharedFlow для одноразовых событий UI
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

// UI, наблюдающий и за состоянием, и за событиями
class UserActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Коллектим состояние — сразу получаем текущее значение
        lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                when (state) {
                    is UiState.Loading -> showLoading()
                    is UiState.Success -> showUser(state.user)
                    is UiState.Error -> showError(state.message)
                }
            }
        }

        // Коллектим события — получаем новые по мере прихода
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

### Когда Использовать `StateFlow`

#### Использовать `StateFlow` Для:

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

    private val _language = MutableStateFlow(Language.EN)
    val language: StateFlow<Language> = _language.asStateFlow()
}

// 3. Пользовательская сессия
class SessionManager {
    private val _currentUser = MutableStateFlow<User?>(null)
    val currentUser: StateFlow<User?> = _currentUser.asStateFlow()

    private val _isLoggedIn = MutableStateFlow(false)
    val isLoggedIn: StateFlow<Boolean> = _isLoggedIn.asStateFlow()
}

// 4. Кэшированные данные
class Repository {
    private val _cachedData = MutableStateFlow<Data?>(null)
    val cachedData: StateFlow<Data?> = _cachedData.asStateFlow()
}
```

### Когда Использовать `SharedFlow`

#### Использовать `SharedFlow` Для:

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

// 3. Несколько значений важны
class SearchViewModel : ViewModel() {
    private val _searchResults = MutableSharedFlow<List<Result>>()
    val searchResults: SharedFlow<List<Result>> = _searchResults.asSharedFlow()

    fun search(query: String) {
        viewModelScope.launch {
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

### Подробное Сравнение: `StateFlow` Vs `SharedFlow`

#### Инициализация

```kotlin
// StateFlow: нужно начальное значение
val state = MutableStateFlow<String>("initial")
// val state = MutableStateFlow<String>()        // Ошибка: нет конструктора без аргументов

// SharedFlow: начальное значение не требуется
val shared = MutableSharedFlow<String>()
val shared2 = MutableSharedFlow<String?>(replay = 1).apply {
    tryEmit(null)  // Можно дать "начальное" значение при необходимости
}
```

#### Доступ К Значению

```kotlin
// StateFlow: прямой доступ к value
val state = MutableStateFlow(10)
println(state.value)  // 10
state.value = 20      // Прямое присвоение

// SharedFlow: нет свойства value
val shared = MutableSharedFlow<Int>()
// println(shared.value)  // Ошибка: нет value
```

#### Коллекция

```kotlin
// StateFlow: сразу эмитирует текущее значение
val state = MutableStateFlow("current")
state.collect { value ->
    // Сначала "current", затем обновления
    println(value)
}

// SharedFlow (без replay): только новые значения после старта коллекции
val shared = MutableSharedFlow<String>()
shared.collect { value ->
    println(value)
}

// SharedFlow (с replay): сначала кэш, потом новые
val sharedWithReplay = MutableSharedFlow<String>(replay = 1)
sharedWithReplay.emit("cached")
sharedWithReplay.collect { value ->
    // Сразу "cached", затем новые
    println(value)
}
```

### Продвинутые Паттерны

#### Конвертация Между `StateFlow` И `SharedFlow`

```kotlin
// SharedFlow -> StateFlow
val sharedFlow = MutableSharedFlow<Int>(replay = 1).apply { tryEmit(0) }
val stateFlow = sharedFlow.stateIn(
    scope = viewModelScope,
    started = SharingStarted.Eagerly,
    initialValue = 0
)

// StateFlow -> SharedFlow (`StateFlow` является подтипом `SharedFlow`)
val stateFlowSrc = MutableStateFlow(0)
val sharedFlowView: SharedFlow<Int> = stateFlowSrc
```

#### Комбинирование Нескольких Flow

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

#### `SharedFlow` На Базе Channel

```kotlin
class EventManager {
    private val eventChannel = Channel<Event>(Channel.UNLIMITED)

    val events: SharedFlow<Event> = eventChannel
        .receiveAsFlow()
        .shareIn(
            scope = GlobalScope,  // В реальном коде используйте структурированный scope
            started = SharingStarted.Eagerly,
            replay = 0
        )

    fun sendEvent(event: Event) {
        eventChannel.trySend(event)
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

// Использовать SharedFlow для событий (особенно одноразовых)
class GoodViewModel : ViewModel() {
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()
}

// Выставлять только read-only версии
class GoodViewModel : ViewModel() {
    private val _data = MutableStateFlow<Data?>(null)
    val data: StateFlow<Data?> = _data.asStateFlow()
}

// Настраивать replay/buffer для SharedFlow под задачу
val notifications = MutableSharedFlow<String>(
    replay = 5,
    extraBufferCapacity = 10
)
```

#### НЕ ДЕЛАТЬ:

```kotlin
// Не выставлять изменяемые версии наружу
class BadViewModel : ViewModel() {
    val state = MutableStateFlow<UiState>(UiState.Initial)  // Плохо: наружу торчит mutable
}

// Не использовать SharedFlow как основной механизм хранения долгоживущего состояния без необходимости
class BadViewModel : ViewModel() {
    private val _isLoading = MutableSharedFlow<Boolean>()  // Для флагов лучше StateFlow
}

// Не использовать StateFlow для одноразовых событий, которые не должны повторяться новым подписчикам
class BadViewModel : ViewModel() {
    private val _events = MutableStateFlow<Event?>(null)  // Для одноразовых лучше SharedFlow
}

// Не забывать начальное значение для StateFlow
// val state = MutableStateFlow<String>()  // Ошибка: требуется initialValue
```

### Производительность

```kotlin
// StateFlow: оптимален для состояния (conflated, distinct)
val state = MutableStateFlow(0)
repeat(1000) {
    state.value = it
}
// Коллектору важно только последнее значение

// SharedFlow: потенциально доставляет каждую эмиссию
val shared = MutableSharedFlow<Int>()
repeat(1000) {
    shared.emit(it)
}
// Коллектор может получить все 1000 значений (зависит от настроек буфера)
```

---

## Answer (EN)

**`SharedFlow`** and **`StateFlow`** are hot `Flow` implementations designed for sharing state and events among multiple collectors. While both are hot flows that emit values to all active collectors, they serve different purposes and have distinct characteristics.

### Key Differences

| Aspect | `StateFlow` | `SharedFlow` |
|--------|-------------|--------------|
| **Purpose** | State holder | Event broadcaster / general shared stream |
| **Initial Value** | Required | Optional |
| **Replay** | Always 1 | Configurable (0+) |
| **Conflation** | Always conflated | Configurable |
| **Distinct Values** | Only distinct | All values |
| **Use Case** | UI state, config | Events, notifications, data streams |

### StateFlow: State Holder

`StateFlow` is specifically designed for representing state that always has a current value:

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

**`StateFlow` Characteristics**:
1. **Always has a value** — must provide an initial value.
2. **Replay = 1** — new collectors immediately receive the current value.
3. **Conflated** — only the latest value matters; slow collectors may skip intermediate updates.
4. **Distinct values only** — does not emit if the new value is equal (`==`) to the current one.
5. **Typically does not complete on its own** — in common usage (e.g., in a `ViewModel`) it stays active until the scope is cancelled or its upstream completes; as a `Flow` it can technically complete if its source completes.

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
    // A slow collector may observe only: 3 (intermediate values skipped)
}

// Use SharedFlow if all values are important
val _allValues = MutableSharedFlow<Int>()
viewModelScope.launch {
    _allValues.emit(1)
    _allValues.emit(2)
    _allValues.emit(3)
    // A collector can observe: 1, 2, 3 (subject to buffer/overflow configuration)
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

### SharedFlow: Event Broadcaster

`SharedFlow` is a general-purpose hot flow for broadcasting values:

```kotlin
// Creating SharedFlow
val _events = MutableSharedFlow<Event>()  // No initial value
val events: SharedFlow<Event> = _events.asSharedFlow()

// Emitting values
_events.emit(Event.UserLoggedIn)
_events.tryEmit(Event.DataLoaded)  // Non-suspending

// Configurable SharedFlow
val _results = MutableSharedFlow<Result>(
    replay = 2,              // Cache last 2 values for new collectors
    extraBufferCapacity = 5, // Additional buffer
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)
```

**`SharedFlow` Characteristics**:
1. **No initial value required** — can start empty.
2. **Configurable replay** — from 0 to unlimited; new collectors receive up to `replay` most recent values.
3. **No conflation by default** — by default attempts to deliver all values, subject to buffer/overflow settings.
4. **Emits all values** — including duplicates.
5. **MutableSharedFlow itself does not complete** — but you can build derived flows on top (e.g., using `take`, `first`) that do complete.

### SharedFlow Deep Dive

#### Creating SharedFlow

```kotlin
// Default: no replay, no extra buffer
val shared1 = MutableSharedFlow<String>()

// With replay
val shared2 = MutableSharedFlow<String>(
    replay = 5  // Cache last 5 values for new collectors
)

// With buffer and overflow policy
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
        replay = 3  // Cache up to the last 3 events for new collectors
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

// New collector receives the last up to 3 events immediately, then waits for new events
bus.events.collect { event ->
    println(event)
}
```

#### SharedFlow Buffer Strategies

```kotlin
// DROP_OLDEST: Remove oldest when buffer (replay + extra capacity) is full
val dropOldest = MutableSharedFlow<Int>(
    replay = 0,
    extraBufferCapacity = 5,
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)

// DROP_LATEST: Drop newest when buffer is full
val dropLatest = MutableSharedFlow<Int>(
    replay = 0,
    extraBufferCapacity = 5,
    onBufferOverflow = BufferOverflow.DROP_LATEST
)

// SUSPEND: Suspend emitter when buffer is full (backpressure-like behavior)
val suspend = MutableSharedFlow<Int>(
    replay = 0,
    extraBufferCapacity = 5,
    onBufferOverflow = BufferOverflow.SUSPEND
)
```

### Real-World Example: ViewModel

```kotlin
class UserViewModel : ViewModel() {
    // StateFlow for state
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    // SharedFlow for one-off UI events
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

        // Collect state - always receives current value first
        lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                when (state) {
                    is UiState.Loading -> showLoading()
                    is UiState.Success -> showUser(state.user)
                    is UiState.Error -> showError(state.message)
                }
            }
        }

        // Collect events - receives new events as they come
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
val state = MutableStateFlow<String>("initial")
// val state = MutableStateFlow<String>()        //  Error: no-arg constructor doesn't exist

// SharedFlow: No initial value required
val shared = MutableSharedFlow<String>()
val shared2 = MutableSharedFlow<String?>(replay = 1).apply {
    tryEmit(null)  // Can provide an initial-like value if needed
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
    // Immediately receives: "current" first, then updates
    println(value)
}

// SharedFlow (no replay): Only receives new values after collection starts
val shared = MutableSharedFlow<String>()
shared.collect { value ->
    println(value)
}

// SharedFlow (with replay): Receives cached values
val sharedWithReplay = MutableSharedFlow<String>(replay = 1)
sharedWithReplay.emit("cached")
sharedWithReplay.collect { value ->
    // Immediately receives: "cached" (the last replayed value), then new ones
    println(value)
}
```

### Advanced Patterns

#### Converting Between StateFlow and SharedFlow

```kotlin
// SharedFlow to StateFlow
val sharedFlow = MutableSharedFlow<Int>(replay = 1).apply { tryEmit(0) }
val stateFlow = sharedFlow.stateIn(
    scope = viewModelScope,
    started = SharingStarted.Eagerly,
    initialValue = 0
)

// StateFlow to SharedFlow (StateFlow is a subtype of SharedFlow)
val stateFlowSrc = MutableStateFlow(0)
val sharedFlowView: SharedFlow<Int> = stateFlowSrc
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

    val events: SharedFlow<Event> = eventChannel
        .receiveAsFlow()
        .shareIn(
            scope = GlobalScope,  // Prefer a structured scope in real code
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

// Use SharedFlow for events (especially one-time)
class GoodViewModel : ViewModel() {
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()
}

// Expose read-only versions
class GoodViewModel : ViewModel() {
    private val _data = MutableStateFlow<Data?>(null)
    val data: StateFlow<Data?> = _data.asStateFlow()  // Read-only
}

// Use appropriate replay/buffer for SharedFlow
val notifications = MutableSharedFlow<String>(
    replay = 5,  // Keep last 5 for new subscribers
    extraBufferCapacity = 10
)
```

#### DON'T:

```kotlin
// Don't expose mutable versions
class BadViewModel : ViewModel() {
    val state = MutableStateFlow<UiState>(UiState.Initial)  //  Bad: mutable exposed
}

// Avoid using SharedFlow as long-lived state holder when StateFlow models it better
class BadViewModel : ViewModel() {
    private val _isLoading = MutableSharedFlow<Boolean>()  //  Prefer StateFlow for such flags
}

// Avoid using StateFlow for one-off events that should not be replayed to new collectors
class BadViewModel : ViewModel() {
    private val _events = MutableStateFlow<Event?>(null)  //  Prefer SharedFlow for one-off events
}

// Don't forget initial value for StateFlow
// val state = MutableStateFlow<String>()  //  Error: requires initial value
```

### Performance Considerations

```kotlin
// StateFlow: Best for state (conflated, distinct)
val state = MutableStateFlow(0)
repeat(1000) {
    state.value = it
}
// Collector effectively cares about the latest value

// SharedFlow: Potentially delivers every emission to collectors
val shared = MutableSharedFlow<Int>()
repeat(1000) {
    shared.emit(it)
}
// A collector can receive all 1000 values (subject to buffer/overflow configuration)
```

---

## Дополнительные Вопросы (RU)

- В чём отличие от аналогичных механизмов в Java или RxJava?
- Когда вы бы применили `StateFlow` или `SharedFlow` на практике?
- Какие распространённые ошибки при использовании `StateFlow` и `SharedFlow`?

## Follow-ups

- What are the key differences between this and Java/RxJava approaches?
- When would you use `StateFlow` or `SharedFlow` in real projects?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [[c-kotlin]]
- [[c-flow]]
- Kotlin `SharedFlow` Documentation: https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/
- Kotlin `StateFlow` Documentation: https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/
- `StateFlow` and `SharedFlow` Guide (Android): https://developer.android.com/kotlin/flow/stateflow-and-sharedflow

## References

- [Kotlin `SharedFlow` Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/)
- [Kotlin `StateFlow` Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/)
- [StateFlow and `SharedFlow` Guide](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow)

## Связанные Вопросы (RU)

### Средний Уровень
- [[q-testing-stateflow-sharedflow--kotlin--medium]]
- [[q-stateflow-sharedflow-android--kotlin--medium]]
- [[q-stateflow-sharedflow-differences--kotlin--medium]]
- [[q-sharedflow-replay-buffer-config--kotlin--medium]]

### Продвинутый Уровень
- [[q-actor-pattern--kotlin--hard]]
- [[q-testing-flow-operators--kotlin--hard]]

### Хаб
- [[q-kotlin-flow-basics--kotlin--medium]]

## Related Questions

### Related (Medium)
- [[q-testing-stateflow-sharedflow--kotlin--medium]]
- [[q-stateflow-sharedflow-android--kotlin--medium]]
- [[q-stateflow-sharedflow-differences--kotlin--medium]]
- [[q-sharedflow-replay-buffer-config--kotlin--medium]]

### Advanced (Harder)
- [[q-actor-pattern--kotlin--hard]]
- [[q-testing-flow-operators--kotlin--hard]]

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]]

## MOC Связи (RU)

- [[moc-kotlin]]

## MOC Links

- [[moc-kotlin]]
