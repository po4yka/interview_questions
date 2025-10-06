---
id: 20251006-002
title: "stateIn and shareIn operators in Flow / Операторы stateIn и shareIn во Flow"
aliases: []

# Classification
topic: kotlin
subtopics: [flow, coroutines, statein, sharein, hot-flow]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository - MEDIUM priority

# Workflow & relations
status: draft
moc: moc-kotlin
related: []

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [kotlin, flow, coroutines, statein, sharein, hot-flow, difficulty/medium]
---

# Question (EN)
> What are stateIn and shareIn operators in Kotlin Flow? When to use each?

# Вопрос (RU)
> Что такое операторы stateIn и shareIn в Kotlin Flow? Когда использовать каждый?

---

## Answer (EN)

**`stateIn` and `shareIn`** are operators that convert **cold Flow** into **hot Flow** (StateFlow/SharedFlow), allowing multiple collectors to share the same upstream flow.

### Cold Flow vs Hot Flow

**Cold Flow**: Each collector triggers independent execution

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

**Hot Flow**: Single execution shared among collectors

```kotlin
val hotFlow = flow {
    println("Hot flow started")
    emit(1)
    emit(2)
}.shareIn(scope, SharingStarted.Lazily)

// Single execution, both collectors share it
hotFlow.collect { println("Collector 1: $it") }
hotFlow.collect { println("Collector 2: $it") }  // "Hot flow started" printed only once
```

### stateIn - Convert to StateFlow

**`stateIn`** creates a **StateFlow** that always has a current value and replays the latest value to new collectors.

```kotlin
class UserViewModel : ViewModel() {
    // Cold flow from repository
    private val userFlow: Flow<User> = repository.getUserFlow()

    // Convert to StateFlow with initial value
    val user: StateFlow<User> = userFlow
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = User.Empty
        )
}
```

**Parameters:**

1. **`scope`**: CoroutineScope for the flow
2. **`started`**: When to start/stop the upstream flow
3. **`initialValue`**: Initial value before first emission

### stateIn Sharing Strategies

```kotlin
// 1. WhileSubscribed - Start when first subscriber, stop after last leaves
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

### shareIn - Convert to SharedFlow

**`shareIn`** creates a **SharedFlow** that can replay multiple values and doesn't require an initial value.

```kotlin
class EventViewModel : ViewModel() {
    private val eventsFlow: Flow<Event> = repository.getEvents()

    // Convert to SharedFlow
    val events: SharedFlow<Event> = eventsFlow
        .shareIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            replay = 0  // No replay
        )
}
```

**Parameters:**

1. **`scope`**: CoroutineScope for the flow
2. **`started`**: When to start/stop
3. **`replay`**: Number of values to replay to new collectors

### Comparison: stateIn vs shareIn

| Feature | stateIn (StateFlow) | shareIn (SharedFlow) |
|---------|-------------------|---------------------|
| **Initial value** | Required | Not required |
| **Current value** | Always has `.value` | No `.value` property |
| **Replay** | Always replays 1 (latest) | Configurable (0, 1, n) |
| **Conflation** | Conflates values | Can buffer or drop |
| **Use case** | Current state/data | Events, multiple values |

### When to Use stateIn

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

// UI can access current value
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

### When to Use shareIn

**1. One-Time Events**

```kotlin
class OrderViewModel : ViewModel() {
    private val _orderEvents = MutableSharedFlow<OrderEvent>()

    val orderEvents: SharedFlow<OrderEvent> = _orderEvents
        .shareIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            replay = 0  // Events should not be replayed
        )

    fun placeOrder(order: Order) {
        viewModelScope.launch {
            _orderEvents.emit(OrderEvent.OrderPlaced(order.id))
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

### SharingStarted Strategies

**1. WhileSubscribed(stopTimeoutMillis)**

```kotlin
// Stops 5s after last collector leaves, restarts when new collector arrives
SharingStarted.WhileSubscribed(5000)

// Use case: Save resources, allow state to reset
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

// Use case: Critical data needed immediately
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

// Use case: Expensive operations that should run once
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

    // Use shareIn for search events (one-time events)
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

**stateIn automatically conflates rapid updates:**

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

// Collector only sees some values (conflated)
ticker.collect { value ->
    println(value)  // 0, 5, 10, 20... (not all values)
    delay(50)
}
```

**shareIn can buffer or drop:**

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

**Pattern 1: One StateFlow per screen state**

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

**Pattern 2: SharedFlow for events, StateFlow for state**

```kotlin
class ViewModel : ViewModel() {
    // State - current data
    val state: StateFlow<State> = dataFlow
        .stateIn(scope, started, initialValue)

    // Events - one-time actions
    private val _events = MutableSharedFlow<Event>()
    val events = _events.asSharedFlow()
}
```

**English Summary**: `stateIn` converts cold Flow to StateFlow (always has current value, replays latest to new collectors). `shareIn` converts to SharedFlow (configurable replay, no initial value required). Use `stateIn` for: state/data that has current value, caching, combining sources. Use `shareIn` for: events, multiple recent values, broadcasting. SharingStarted strategies: `WhileSubscribed` (stops after timeout), `Eagerly` (never stops), `Lazily` (starts on first subscriber). StateFlow conflates, SharedFlow can buffer.

## Ответ (RU)

**`stateIn` и `shareIn`** — операторы, которые конвертируют **холодный Flow** в **горячий Flow** (StateFlow/SharedFlow), позволяя нескольким коллекторам делить один upstream flow.

### Cold Flow vs Hot Flow

**Cold Flow**: Каждый коллектор запускает независимое выполнение

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

**Hot Flow**: Одно выполнение разделяется между коллекторами

```kotlin
val hotFlow = flow {
    println("Hot flow started")
    emit(1)
    emit(2)
}.shareIn(scope, SharingStarted.Lazily)

// Одно выполнение, оба коллектора его разделяют
hotFlow.collect { println("Collector 1: $it") }
hotFlow.collect { println("Collector 2: $it") }  // "Hot flow started" печатается только раз
```

### stateIn - Конвертация в StateFlow

**`stateIn`** создаёт **StateFlow**, который всегда имеет текущее значение и воспроизводит последнее значение новым коллекторам.

```kotlin
class UserViewModel : ViewModel() {
    // Cold flow из репозитория
    private val userFlow: Flow<User> = repository.getUserFlow()

    // Конвертация в StateFlow с начальным значением
    val user: StateFlow<User> = userFlow
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = User.Empty
        )
}
```

**Параметры:**

1. **`scope`**: CoroutineScope для flow
2. **`started`**: Когда запускать/останавливать upstream flow
3. **`initialValue`**: Начальное значение до первой эмиссии

### shareIn - Конвертация в SharedFlow

**`shareIn`** создаёт **SharedFlow**, который может воспроизводить несколько значений и не требует начального значения.

```kotlin
class EventViewModel : ViewModel() {
    private val eventsFlow: Flow<Event> = repository.getEvents()

    // Конвертация в SharedFlow
    val events: SharedFlow<Event> = eventsFlow
        .shareIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            replay = 0  // Нет воспроизведения
        )
}
```

### Сравнение: stateIn vs shareIn

| Функция | stateIn (StateFlow) | shareIn (SharedFlow) |
|---------|-------------------|---------------------|
| **Начальное значение** | Обязательно | Не требуется |
| **Текущее значение** | Всегда есть `.value` | Нет `.value` |
| **Воспроизведение** | Всегда 1 (последнее) | Настраиваемое (0, 1, n) |
| **Конфляция** | Конфлирует значения | Может буферизовать или отбрасывать |
| **Применение** | Текущее состояние/данные | События, множественные значения |

### Когда использовать stateIn

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

### Когда использовать shareIn

**1. Одноразовые события**

```kotlin
class OrderViewModel : ViewModel() {
    private val _orderEvents = MutableSharedFlow<OrderEvent>()

    val orderEvents: SharedFlow<OrderEvent> = _orderEvents
        .shareIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            replay = 0  // События не должны воспроизводиться
        )
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

### Стратегии SharingStarted

**1. WhileSubscribed(stopTimeoutMillis)** - Останавливается через N мс после ухода последнего коллектора

**2. Eagerly** - Запускается немедленно при создании, никогда не останавливается

**3. Lazily** - Запускается при первом подписчике, никогда не останавливается

### Пример: Экран поиска

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

    // Используем shareIn для событий поиска (одноразовые события)
    private val _searchEvents = MutableSharedFlow<SearchEvent>()
    val searchEvents: SharedFlow<SearchEvent> = _searchEvents.asSharedFlow()

    fun updateQuery(query: String) {
        searchQuery.value = query
    }
}
```

**Краткое содержание**: `stateIn` конвертирует холодный Flow в StateFlow (всегда имеет текущее значение, воспроизводит последнее новым коллекторам). `shareIn` конвертирует в SharedFlow (настраиваемое воспроизведение, не требует начального значения). Используйте `stateIn` для: состояния/данных с текущим значением, кэширования, комбинирования источников. Используйте `shareIn` для: событий, нескольких недавних значений, вещания. Стратегии SharingStarted: `WhileSubscribed` (останавливается после таймаута), `Eagerly` (никогда не останавливается), `Lazily` (запускается на первом подписчике).

---

## References
- [StateFlow and SharedFlow - Kotlin Documentation](https://kotlinlang.org/docs/flow.html#stateflow-and-sharedflow)
- [SharedFlow vs StateFlow](https://elizarov.medium.com/shared-flows-broadcast-channels-899b675e805c)

## Related Questions
- [[q-stateflow-sharedflow--kotlin--medium]]
- [[q-cold-hot-flow--kotlin--medium]]
