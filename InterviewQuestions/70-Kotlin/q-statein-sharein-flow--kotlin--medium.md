---id: kotlin-041
title: "stateIn and shareIn operators in Flow / Операторы stateIn и shareIn во Flow"
aliases: ["stateIn and shareIn operators in Flow", "Операторы stateIn и shareIn во Flow"]
topic: kotlin
subtopics: [coroutines, flow, hot-flow]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository - MEDIUM priority
status: draft
moc: moc-kotlin
related: [c-flow, c-kotlin, c-stateflow, q-kotlin-type-aliases-inline--kotlin--medium, q-parallel-network-calls-coroutines--kotlin--medium, q-retry-exponential-backoff-flow--kotlin--medium]
created: 2025-10-06
updated: 2025-11-11
tags: [coroutines, difficulty/medium, flow, hot-flow, kotlin, sharein, statein]

---
# Вопрос (RU)
> Что такое операторы `stateIn` и `shareIn` в Kotlin `Flow`? Когда использовать каждый?

---

# Question (EN)
> What are `stateIn` and `shareIn` operators in Kotlin `Flow`? When to use each?

## Ответ (RU)

**`stateIn` и `shareIn`** — операторы, которые конвертируют **холодный `Flow`** в **горячий `Flow`** (`StateFlow` / `SharedFlow`), позволяя нескольким коллекторам делить один upstream `Flow`.

### Cold `Flow` Vs Hot `Flow`

**Cold `Flow`**: Каждый коллектор запускает независимое выполнение.

```kotlin
val coldFlow = flow {
    println("Cold flow started")
    emit(1)
    emit(2)
}

// Каждый collect запускает новое выполнение
coldFlow.collect { println("Collector 1: $it") }  // Печатает "Cold flow started"
coldFlow.collect { println("Collector 2: $it") }  // Печатает "Cold flow started" снова
```

**Hot `Flow`**: Одно выполнение разделяется между коллекторами (подписчики получают значения только если активны во время эмиссии).

```kotlin
val hotFlow = flow {
    println("Hot flow started")
    emit(1)
    emit(2)
}.shareIn(scope, SharingStarted.Lazily)

// Если несколько коллектора подписаны одновременно, они разделяют одно выполнение
scope.launch {
    hotFlow.collect { println("Collector 1: $it") }
}
scope.launch {
    hotFlow.collect { println("Collector 2: $it") }
}
// "Hot flow started" печатается один раз для общего upstream
```

### `stateIn` — Конвертация В `StateFlow`

**`stateIn`** создаёт `StateFlow`, который всегда имеет текущее значение и воспроизводит последнее значение новым коллекторам.

```kotlin
class UserViewModel : ViewModel() {
    // Cold flow из репозитория
    private val userFlow: Flow<User> = repository.getUserFlow()

    // Конвертация в `StateFlow` с начальным значением
    val user: StateFlow<User> = userFlow
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = User.Empty
        )
}
```

**Параметры:**

1. **`scope`**: `CoroutineScope` для `Flow`
2. **`started`**: когда запускать/останавливать upstream `Flow`
3. **`initialValue`**: начальное значение до первой эмиссии

### `stateIn` — Стратегии `SharingStarted`

```kotlin
// 1. WhileSubscribed — старт при первом подписчике, стоп после ухода последнего (с таймаутом)
val state1 = flow.stateIn(
    scope = viewModelScope,
    started = SharingStarted.WhileSubscribed(5000),  // таймаут 5с
    initialValue = initialValue
)

// 2. Eagerly — запускается сразу, никогда не останавливается
val state2 = flow.stateIn(
    scope = viewModelScope,
    started = SharingStarted.Eagerly,
    initialValue = initialValue
)

// 3. Lazily — запускается при первом подписчике, никогда не останавливается
val state3 = flow.stateIn(
    scope = viewModelScope,
    started = SharingStarted.Lazily,
    initialValue = initialValue
)
```

### `shareIn` — Конвертация В `SharedFlow`

**`shareIn`** создаёт `SharedFlow`, который может воспроизводить несколько значений и не требует начального значения.

```kotlin
class EventViewModel : ViewModel() {
    private val eventsFlow: Flow<Event> = repository.getEvents()

    // Конвертация в `SharedFlow`
    val events: SharedFlow<Event> = eventsFlow
        .shareIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            replay = 0  // Нет воспроизведения
        )
}
```

**Параметры:**

1. **`scope`**: `CoroutineScope` для `Flow`
2. **`started`**: когда запускать/останавливать
3. **`replay`**: количество значений для воспроизведения новым коллекторам

### Сравнение: `stateIn` Vs `shareIn`

| Функция | `stateIn` (`StateFlow`) | `shareIn` (`SharedFlow`) |
|--------|-------------------------|--------------------------|
| **Начальное значение** | Обязательно | Не требуется |
| **Текущее значение** | Есть `.value` | Нет `.value` |
| **Воспроизведение** | Всегда 1 (последнее) | Настраиваемое (0, 1, n) |
| **Конфлюация** | Хранит только последнее значение (быстрые эмиссии могут сливаться) | Может буферизовать или отбрасывать |
| **Применение** | Текущее состояние/данные | События, несколько последних значений |

### Когда Использовать `stateIn`

**1. Представление текущего состояния**

```kotlin
class ProductViewModel : ViewModel() {
    val product: StateFlow<Product> = repository
        .getProductFlow(productId)
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = Product.Loading
        )
}

@Composable
fun ProductScreen(viewModel: ProductViewModel) {
    val product by viewModel.product.collectAsState()

    when (product) {
        is Product.Loading -> LoadingView()
        is Product.Success -> ProductDetails(product)
        is Product.Error -> ErrorView()
    }
}
```

**2. Кэширование результатов сети/БД**

```kotlin
class UserRepository {
    val currentUser: StateFlow<User?> = flow {
        // Эмитим кэшированное значение сначала
        userDao.getUser()?.let { emit(it) }

        // Загружаем свежие данные
        val freshUser = userApi.getCurrentUser()
        userDao.saveUser(freshUser)
        emit(freshUser)
    }
    .stateIn(
        scope = repositoryScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = null
    )
}
```

**3. Комбинация нескольких источников**

```kotlin
class DashboardViewModel : ViewModel() {
    private val userFlow = repository.getUserFlow()
    private val settingsFlow = repository.getSettingsFlow()

    val dashboardState: StateFlow<DashboardState> = combine(
        userFlow,
        settingsFlow
    ) { user, settings ->
        DashboardState(user = user, settings = settings)
    }
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = DashboardState.Loading
    )
}
```

### Когда Использовать `shareIn`

**1. Широковещание значений из холодного источника нескольким подписчикам**

```kotlin
class OrderViewModel : ViewModel() {
    private val orderEventsFlow: Flow<OrderEvent> = repository.observeOrderEvents()

    val orderEvents: SharedFlow<OrderEvent> = orderEventsFlow
        .shareIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            replay = 0  // События не должны воспроизводиться
        )

    fun refresh() {
        viewModelScope.launch {
            // Триггеры в репозитории, влияющие на orderEventsFlow
        }
    }
}
```

**2. Несколько недавних значений**

```kotlin
class ChatViewModel : ViewModel() {
    val recentMessages: SharedFlow<Message> = repository
        .getMessagesFlow()
        .shareIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            replay = 10  // Показать последние 10 сообщений новым подписчикам
        )
}
```

**3. Широковещание одному источнику для нескольких коллекторов**

```kotlin
class LocationService {
    private val locationUpdates: Flow<Location> = callbackFlow {
        // Обновления локации из GPS
        val callback = object : LocationCallback() {
            override fun onLocationResult(result: LocationResult) {
                trySend(result.lastLocation)
            }
        }
        fusedLocationClient.requestLocationUpdates(request, callback, Looper.getMainLooper())
        awaitClose { fusedLocationClient.removeLocationUpdates(callback) }
    }

    // Деляем один поток GPS-данных между несколькими наблюдателями
    val sharedLocation: SharedFlow<Location> = locationUpdates
        .shareIn(
            scope = serviceScope,
            started = SharingStarted.WhileSubscribed(),
            replay = 1  // Новый коллектор получает последнюю известную локацию
        )
}
```

### Стратегии `SharingStarted`

**1. WhileSubscribed(stopTimeoutMillis)**

```kotlin
// Останавливается через 5с после ухода последнего коллектора, перезапускается при новом
SharingStarted.WhileSubscribed(5000)

val products = repository.getProducts()
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = emptyList()
    )
```

**2. Eagerly**

```kotlin
// Старт сразу при создании, никогда не останавливается
SharingStarted.Eagerly

val userSession = authRepository.getSessionFlow()
    .stateIn(
        scope = appScope,
        started = SharingStarted.Eagerly,
        initialValue = Session.None
    )
```

**3. Lazily**

```kotlin
// Старт при первом подписчике, никогда не останавливается
SharingStarted.Lazily

val expensiveData = computeExpensiveData()
    .shareIn(
        scope = viewModelScope,
        started = SharingStarted.Lazily,
        replay = 1
    )
```

### Реальный Пример: Экран Поиска

```kotlin
class SearchViewModel : ViewModel() {
    private val searchQuery = MutableStateFlow("")

    // Используем stateIn для результатов поиска (состояние)
    val searchResults: StateFlow<List<Product>> = searchQuery
        .debounce(300)
        .filter { it.length >= 2 }
        .distinctUntilChanged()
        .flatMapLatest { query ->
            repository.search(query)
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    // Используем SharedFlow для одноразовых событий поиска
    private val _searchEvents = MutableSharedFlow<SearchEvent>()
    val searchEvents: SharedFlow<SearchEvent> = _searchEvents.asSharedFlow()

    fun updateQuery(query: String) {
        searchQuery.value = query
        viewModelScope.launch {
            _searchEvents.emit(SearchEvent.QueryChanged(query))
        }
    }

    fun selectProduct(product: Product) {
        viewModelScope.launch {
            _searchEvents.emit(SearchEvent.ProductSelected(product.id))
        }
    }
}

sealed class SearchEvent {
    data class QueryChanged(val query: String) : SearchEvent()
    data class ProductSelected(val productId: String) : SearchEvent()
}
```

### Производительность

- `StateFlow` эффективно ведёт себя как конфлюирующий поток: он хранит только последнее значение, поэтому медленный коллектор может пропустить промежуточные эмиссии и видеть только актуальное значение.

```kotlin
val ticker = flow {
    var i = 0
    while (true) {
        emit(i++)
        delay(10)
    }
}
.stateIn(
    scope = viewModelScope,
    started = SharingStarted.Lazily,
    initialValue = 0
)

// Коллектор увидит только часть значений
ticker.collect { value ->
    println(value)
    delay(50)
}
```

- `shareIn` по умолчанию использует буфер, который можно настраивать (например, через оператор `buffer()` до `shareIn`), и в зависимости от конфигурации значения могут буферизоваться или отбрасываться.

```kotlin
val events = eventFlow
    .shareIn(
        scope = viewModelScope,
        started = SharingStarted.Lazily,
        replay = 0
    )
```

### Общие Паттерны

**Паттерн 1: Один `StateFlow` на состояние экрана**

```kotlin
class ScreenViewModel : ViewModel() {
    val uiState: StateFlow<UiState> = combine(
        dataFlow1,
        dataFlow2,
        dataFlow3
    ) { data1, data2, data3 ->
        UiState(data1, data2, data3)
    }
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = UiState.Loading
    )
}
```

**Паттерн 2: `SharedFlow` для событий, `StateFlow` для состояния**

```kotlin
class ExampleViewModel : ViewModel() {
    // State — текущее состояние данных
    val state: StateFlow<State> = dataFlow
        .stateIn(scope = viewModelScope, started = SharingStarted.WhileSubscribed(5000), initialValue = State.Loading)

    // Events — одноразовые действия
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()
}
```

**Краткое резюме (RU)**: `stateIn` конвертирует холодный `Flow` в `StateFlow` (всегда есть текущее значение, последнее воспроизводится новым коллекторам). `shareIn` конвертирует холодный `Flow` в `SharedFlow` (настраиваемое воспроизведение, начальное значение не требуется). Используйте `stateIn` для состояния и кэширования, `shareIn` — для событий и широковещания из холодных источников, в том числе когда нужно хранить несколько последних значений и расшаривать поток между множеством коллекторов, с учётом стратегий `SharingStarted` и особенностей производительности.

---

## Answer (EN)

**`stateIn` and `shareIn`** are operators that convert a **cold `Flow`** into a **hot `Flow`** (`StateFlow` / `SharedFlow`), allowing multiple collectors to share the same upstream `Flow`.

### Cold `Flow` Vs Hot `Flow`

**Cold `Flow`**: Each collector triggers independent execution.

```kotlin
val coldFlow = flow {
    println("Cold flow started")
    emit(1)
    emit(2)
}

// Each collect triggers new execution
coldFlow.collect { println("Collector 1: $it") }  // Prints "Cold flow started"
coldFlow.collect { println("Collector 2: $it") }  // Prints "Cold flow started" again
```

**Hot `Flow`**: Single execution shared among collectors (collectors receive values only while active during emission).

```kotlin
val hotFlow = flow {
    println("Hot flow started")
    emit(1)
    emit(2)
}.shareIn(scope, SharingStarted.Lazily)

// If multiple collectors are active concurrently, they share the same upstream execution
scope.launch {
    hotFlow.collect { println("Collector 1: $it") }
}
scope.launch {
    hotFlow.collect { println("Collector 2: $it") }
}
// "Hot flow started" is printed once for the shared upstream
```

### `stateIn` - Convert to `StateFlow`

**`stateIn`** creates a `StateFlow` that always has a current value and replays the latest value to new collectors.

```kotlin
class UserViewModel : ViewModel() {
    // Cold flow from repository
    private val userFlow: Flow<User> = repository.getUserFlow()

    // Convert to `StateFlow` with initial value
    val user: StateFlow<User> = userFlow
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = User.Empty
        )
}
```

**Parameters:**

1. **`scope`**: `CoroutineScope` for the `Flow`
2. **`started`**: When to start/stop the upstream `Flow`
3. **`initialValue`**: Initial value before first emission

### `stateIn` Sharing Strategies

```kotlin
// 1. WhileSubscribed - Start when first subscriber, stop after last leaves (with timeout)
val state1 = flow.stateIn(
    scope = viewModelScope,
    started = SharingStarted.WhileSubscribed(5000),  // 5s timeout
    initialValue = initialValue
)

// 2. Eagerly - Start immediately, never stop
val state2 = flow.stateIn(
    scope = viewModelScope,
    started = SharingStarted.Eagerly,
    initialValue = initialValue
)

// 3. Lazily - Start when first subscriber, never stop
val state3 = flow.stateIn(
    scope = viewModelScope,
    started = SharingStarted.Lazily,
    initialValue = initialValue
)
```

### `shareIn` - Convert to `SharedFlow`

**`shareIn`** creates a `SharedFlow` that can replay multiple values and doesn't require an initial value.

```kotlin
class EventViewModel : ViewModel() {
    private val eventsFlow: Flow<Event> = repository.getEvents()

    // Convert to `SharedFlow`
    val events: SharedFlow<Event> = eventsFlow
        .shareIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            replay = 0  // No replay
        )
}
```

**Parameters:**

1. **`scope`**: `CoroutineScope` for the `Flow`
2. **`started`**: When to start/stop
3. **`replay`**: Number of values to replay to new collectors

### Comparison: `stateIn` Vs `shareIn`

| Feature | `stateIn` (`StateFlow`) | `shareIn` (`SharedFlow`) |
|---------|------------------------|--------------------------|
| **Initial value** | Required | Not required |
| **Current value** | Always has `.value` | No `.value` property |
| **Replay** | Always replays 1 (latest) | Configurable (0, 1, n) |
| **Conflation** | Holds only the latest value (fast emissions may be "merged") | Can buffer or drop |
| **Use case** | Current state/data | Events, multiple recent values, broadcasting |

### When to Use `stateIn`

**1. Representing Current State**

```kotlin
class ProductViewModel : ViewModel() {
    val product: StateFlow<Product> = repository
        .getProductFlow(productId)
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = Product.Loading
        )
}

@Composable
fun ProductScreen(viewModel: ProductViewModel) {
    val product by viewModel.product.collectAsState()

    when (product) {
        is Product.Loading -> LoadingView()
        is Product.Success -> ProductDetails(product)
        is Product.Error -> ErrorView()
    }
}
```

**2. Caching Network/Database Results**

```kotlin
class UserRepository {
    private val userApi: UserApi
    private val userDao: UserDao

    val currentUser: StateFlow<User?> = flow {
        // Emit cached value first
        userDao.getUser()?.let { emit(it) }

        // Fetch fresh data
        val freshUser = userApi.getCurrentUser()
        userDao.saveUser(freshUser)
        emit(freshUser)
    }
    .stateIn(
        scope = repositoryScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = null
    )
}
```

**3. Combining Multiple Sources**

```kotlin
class DashboardViewModel : ViewModel() {
    private val userFlow = repository.getUserFlow()
    private val settingsFlow = repository.getSettingsFlow()

    val dashboardState: StateFlow<DashboardState> = combine(
        userFlow,
        settingsFlow
    ) { user, settings ->
        DashboardState(user = user, settings = settings)
    }
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = DashboardState.Loading
    )
}
```

### When to Use `shareIn`

**1. Broadcasting values from a cold source to multiple collectors**

```kotlin
class OrderViewModel : ViewModel() {
    private val orderEventsFlow: Flow<OrderEvent> = repository.observeOrderEvents()

    val orderEvents: SharedFlow<OrderEvent> = orderEventsFlow
        .shareIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            replay = 0  // Events should not be replayed
        )

    fun refresh() {
        viewModelScope.launch {
            // triggers in repository that affect orderEventsFlow
        }
    }
}
```

**2. Multiple Recent Values**

```kotlin
class ChatViewModel : ViewModel() {
    val recentMessages: SharedFlow<Message> = repository
        .getMessagesFlow()
        .shareIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            replay = 10  // Show last 10 messages to new subscribers
        )
}
```

**3. Broadcasting to Multiple Collectors**

```kotlin
class LocationService {
    private val locationUpdates: Flow<Location> = callbackFlow {
        // Location updates from GPS
        val callback = object : LocationCallback() {
            override fun onLocationResult(result: LocationResult) {
                trySend(result.lastLocation)
            }
        }
        fusedLocationClient.requestLocationUpdates(request, callback, Looper.getMainLooper())
        awaitClose { fusedLocationClient.removeLocationUpdates(callback) }
    }

    // Share single GPS stream to multiple observers
    val sharedLocation: SharedFlow<Location> = locationUpdates
        .shareIn(
            scope = serviceScope,
            started = SharingStarted.WhileSubscribed(),
            replay = 1  // New collectors get last known location
        )
}
```

### `SharingStarted` Strategies

**1. WhileSubscribed(stopTimeoutMillis)**

```kotlin
// Stops 5s after last collector leaves, restarts when new collector arrives
SharingStarted.WhileSubscribed(5000)

val products = repository.getProducts()
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = emptyList()
    )
```

**2. Eagerly**

```kotlin
// Starts immediately when created, never stops
SharingStarted.Eagerly

val userSession = authRepository.getSessionFlow()
    .stateIn(
        scope = appScope,
        started = SharingStarted.Eagerly,
        initialValue = Session.None
    )
```

**3. Lazily**

```kotlin
// Starts when first collector subscribes, never stops
SharingStarted.Lazily

val expensiveData = computeExpensiveData()
    .shareIn(
        scope = viewModelScope,
        started = SharingStarted.Lazily,
        replay = 1
    )
```

### Real-World Example: Search Screen

```kotlin
class SearchViewModel : ViewModel() {
    private val searchQuery = MutableStateFlow("")

    // Use stateIn for search results (state)
    val searchResults: StateFlow<List<Product>> = searchQuery
        .debounce(300)
        .filter { it.length >= 2 }
        .distinctUntilChanged()
        .flatMapLatest { query ->
            repository.search(query)
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    // Use SharedFlow for one-time search events
    private val _searchEvents = MutableSharedFlow<SearchEvent>()
    val searchEvents: SharedFlow<SearchEvent> = _searchEvents.asSharedFlow()

    fun updateQuery(query: String) {
        searchQuery.value = query
        viewModelScope.launch {
            _searchEvents.emit(SearchEvent.QueryChanged(query))
        }
    }

    fun selectProduct(product: Product) {
        viewModelScope.launch {
            _searchEvents.emit(SearchEvent.ProductSelected(product.id))
        }
    }
}

sealed class SearchEvent {
    data class QueryChanged(val query: String) : SearchEvent()
    data class ProductSelected(val productId: String) : SearchEvent()
}
```

### Performance Considerations

**`StateFlow` appears to conflate rapid updates:** because it always holds a single latest value, a slow collector may observe only some values.

```kotlin
val ticker = flow {
    var i = 0
    while (true) {
        emit(i++)
        delay(10)  // Very fast emissions
    }
}
.stateIn(
    scope = viewModelScope,
    started = SharingStarted.Lazily,
    initialValue = 0
)

// Collector sees only some values (latest at collection time)
ticker.collect { value ->
    println(value)  // e.g., 0, 5, 10, 20... (not all values)
    delay(50)
}
```

**`shareIn` can buffer or drop:**

```kotlin
val events = eventFlow
    .shareIn(
        scope = viewModelScope,
        started = SharingStarted.Lazily,
        replay = 0
    )
// Uses default buffer (can be configured with buffer() operator before shareIn)
```

### Common Patterns

**Pattern 1: One `StateFlow` per screen state**

```kotlin
class ScreenViewModel : ViewModel() {
    val uiState: StateFlow<UiState> = combine(
        dataFlow1,
        dataFlow2,
        dataFlow3
    ) { data1, data2, data3 ->
        UiState(data1, data2, data3)
    }
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = UiState.Loading
    )
}
```

**Pattern 2: `SharedFlow` for events, `StateFlow` for state**

```kotlin
class ViewModel : ViewModel() {
    // State - current data
    val state: StateFlow<State> = dataFlow
        .stateIn(scope = viewModelScope, started = SharingStarted.WhileSubscribed(5000), initialValue = State.Loading)

    // Events - one-time actions
    private val _events = MutableSharedFlow<Event>()
    val events: SharedFlow<Event> = _events.asSharedFlow()
}
```

**English Summary**: `stateIn` converts a cold `Flow` to a `StateFlow` (always has current value, replays latest to new collectors). `shareIn` converts a cold `Flow` to a `SharedFlow` (configurable replay, no initial value required). Use `stateIn` for state/data that has current value, caching, combining sources. Use `shareIn` for events and broadcasting from cold sources, multiple recent values, broadcasting to many collectors. `SharingStarted` strategies: `WhileSubscribed` (stops after timeout), `Eagerly` (never stops), `Lazily` (starts on first subscriber). `StateFlow` effectively conflates by keeping only the latest value; `SharedFlow` can buffer or drop depending on configuration.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References
- [`StateFlow` and `SharedFlow` - Kotlin Documentation](https://kotlinlang.org/docs/flow.html#stateflow-and-sharedflow)
- [`SharedFlow` vs `StateFlow`](https://elizarov.medium.com/shared-flows-broadcast-channels-899b675e805c)
- See also: [[c-kotlin]], [[c-flow]]

## Related Questions

- [[q-sharedflow-vs-stateflow--kotlin--easy]]