---
id: 20251011-002
title: "Cold vs Hot Flows / Холодные и горячие потоки"
aliases: []

# Classification
topic: kotlin
subtopics: [flow, hot-flows, cold-flows, shareIn, stateIn]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Phase 1 Coroutines & Flow Advanced Questions

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-stateflow-sharedflow-differences--kotlin--medium, q-kotlin-flow-basics--kotlin--medium]

# Timestamps
created: 2025-10-11
updated: 2025-10-11

tags: [kotlin, flow, hot-flows, cold-flows, shareIn, stateIn, difficulty/medium]
---
# Question (EN)
> Explain cold vs hot flows. How do shareIn and stateIn convert cold to hot? Configure replay and started parameters properly.

# Вопрос (RU)
> Объясните холодные и горячие потоки. Как shareIn и stateIn конвертируют холодные в горячие? Правильно настройте параметры replay и started.

---

## Answer (EN)

Understanding cold vs hot flows is fundamental to building efficient reactive applications with Kotlin Flow. The distinction affects performance, resource management, and data sharing patterns.

### Cold Flows

**Cold flows** are flows that are activated when collected. Each collector triggers the flow builder code independently.

#### Key Characteristics

1. **Lazy** - Only start executing when collected
2. **Unicast** - Each collector gets its own independent flow
3. **No shared state** - Multiple collectors don't share data
4. **Fresh data** - Each collector triggers new execution

#### Example: Cold Flow Behavior

```kotlin
fun createColdFlow(): Flow<Int> = flow {
    println("Flow started at ${System.currentTimeMillis()}")
    repeat(3) { i ->
        delay(1000)
        emit(i)
        println("Emitted: $i")
    }
    println("Flow completed")
}

fun main() = runBlocking {
    val coldFlow = createColdFlow()

    println("Starting first collector")
    launch {
        coldFlow.collect { value ->
            println("Collector 1 received: $value")
        }
    }

    delay(2500)

    println("Starting second collector")
    launch {
        coldFlow.collect { value ->
            println("Collector 2 received: $value")
        }
    }

    delay(5000)
}

/*
Output:
Starting first collector
Flow started at 1000
Emitted: 0
Collector 1 received: 0
Emitted: 1
Collector 1 received: 1
Starting second collector
Flow started at 3500  // NEW flow execution!
Emitted: 2
Collector 1 received: 2
Flow completed
Emitted: 0
Collector 2 received: 0
Emitted: 1
Collector 2 received: 1
Emitted: 2
Collector 2 received: 2
Flow completed
*/
```

**Each collector triggers independent execution** - the flow builder code runs twice.

#### Real-world cold flow examples

```kotlin
// Database query - each collector executes query
fun getUserFlow(userId: Int): Flow<User> = flow {
    val user = database.getUser(userId) // Fresh query each time
    emit(user)
}

// Network request - each collector makes new request
fun fetchArticles(): Flow<List<Article>> = flow {
    val response = api.getArticles() // New network call each time
    emit(response)
}

// File reading - each collector reads file
fun readLogFile(): Flow<String> = flow {
    File("logs.txt").forEachLine { line ->
        emit(line) // Read from beginning each time
    }
}
```

### Hot Flows

**Hot flows** are always active and emit values regardless of whether there are collectors. Multiple collectors share the same flow execution.

#### Key Characteristics

1. **Eager** - Active even without collectors
2. **Multicast** - All collectors receive same emissions
3. **Shared state** - Single execution shared by all
4. **May miss values** - Collectors only receive values emitted after subscription

#### Built-in Hot Flows

```kotlin
// StateFlow - always has a value
val stateFlow = MutableStateFlow(0)

// SharedFlow - configurable hot flow
val sharedFlow = MutableSharedFlow<Int>(
    replay = 0,
    extraBufferCapacity = 0,
    onBufferOverflow = BufferOverflow.SUSPEND
)
```

### Converting Cold to Hot: shareIn()

The `shareIn` operator converts a cold flow into a hot SharedFlow.

```kotlin
fun <T> Flow<T>.shareIn(
    scope: CoroutineScope,
    started: SharingStarted,
    replay: Int = 0
): SharedFlow<T>
```

#### Parameters Explained

**1. scope** - CoroutineScope that controls the sharing coroutine lifetime

**2. replay** - Number of values to replay to new subscribers
- `0` - No replay, new collectors only get future values
- `1` - Replay last value (like StateFlow behavior)
- `n` - Replay last n values

**3. started** - When to start/stop the upstream flow

| Strategy | Behavior | Use Case |
|----------|----------|----------|
| **Eagerly** | Starts immediately, never stops | Background services, always-on streams |
| **Lazily** | Starts on first subscriber, never stops | Cached data, single initialization |
| **WhileSubscribed** | Starts/stops based on subscribers | Most common, resource efficient |

#### shareIn Examples

```kotlin
// Example 1: Temperature sensor data
class TemperatureSensor(scope: CoroutineScope) {
    private val temperatureReadings = flow {
        while (true) {
            val temp = readTemperature() // Expensive sensor read
            emit(temp)
            delay(1000)
        }
    }

    // Share sensor readings - start eagerly, never stop
    val temperature: SharedFlow<Float> = temperatureReadings
        .shareIn(
            scope = scope,
            started = SharingStarted.Eagerly,
            replay = 1 // New subscribers get latest temperature
        )

    private fun readTemperature(): Float {
        println("Reading temperature sensor...")
        return (20..30).random().toFloat()
    }
}

// Usage - multiple collectors share same sensor readings
fun main() = runBlocking {
    val sensor = TemperatureSensor(this)

    // Collector 1
    launch {
        sensor.temperature.collect { temp ->
            println("Display 1: $temp°C")
        }
    }

    delay(2000)

    // Collector 2 - gets latest value immediately due to replay=1
    launch {
        sensor.temperature.collect { temp ->
            println("Display 2: $temp°C")
        }
    }

    delay(5000)
}
/*
Output (sensor read only once per second):
Reading temperature sensor...
Display 1: 24°C
Reading temperature sensor...
Display 1: 27°C
Display 2: 27°C  // Gets replayed value immediately
Reading temperature sensor...
Display 1: 22°C
Display 2: 22°C  // Both share same reading
*/
```

```kotlin
// Example 2: Network data with WhileSubscribed
class NewsRepository(private val scope: CoroutineScope) {
    private val newsUpdates = flow {
        while (true) {
            val news = fetchNewsFromNetwork()
            emit(news)
            delay(60_000) // Refresh every minute
        }
    }

    val latestNews: SharedFlow<List<Article>> = newsUpdates
        .shareIn(
            scope = scope,
            started = SharingStarted.WhileSubscribed(5000), // Stop 5s after last subscriber
            replay = 1 // New subscribers get latest news
        )

    private suspend fun fetchNewsFromNetwork(): List<Article> {
        println("Fetching news from network...")
        delay(1000)
        return listOf(Article("Breaking news"))
    }
}

// Usage
fun main() = runBlocking {
    val repo = NewsRepository(this)

    // First subscriber - starts flow
    val job1 = launch {
        repo.latestNews.collect { news ->
            println("UI 1: ${news.size} articles")
        }
    }

    delay(3000)
    job1.cancel() // Last subscriber stopped

    // Flow continues for 5 more seconds (stopTimeout)
    delay(3000) // Still running

    // New subscriber within stopTimeout - flow still active
    launch {
        repo.latestNews.collect { news ->
            println("UI 2: ${news.size} articles")
        }
    }

    delay(10000)
}
```

#### WhileSubscribed Configuration

```kotlin
SharingStarted.WhileSubscribed(
    stopTimeoutMillis: Long = 0,
    replayExpirationMillis: Long = Long.MAX_VALUE
)
```

**stopTimeoutMillis** - How long to keep flow active after last subscriber
- `0` - Stop immediately when last subscriber cancels
- `5000` - Keep active for 5 seconds (good for screen rotations)
- Prevents restart if user quickly navigates back

**replayExpirationMillis** - How long replay cache remains valid
- `Long.MAX_VALUE` - Never expire (default)
- Custom value - Clear cache after period of no subscribers

```kotlin
// Android ViewModel example - survive configuration changes
class MyViewModel : ViewModel() {
    val uiState = repository.dataFlow
        .shareIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000), // Survive rotation
            replay = 1
        )
}
```

### Converting Cold to Hot: stateIn()

The `stateIn` operator converts a cold flow into a hot StateFlow.

```kotlin
fun <T> Flow<T>.stateIn(
    scope: CoroutineScope,
    started: SharingStarted,
    initialValue: T
): StateFlow<T>
```

#### Key Differences from shareIn

| Feature | shareIn | stateIn |
|---------|---------|---------|
| **Return type** | SharedFlow | StateFlow |
| **Initial value** | Optional (replay) | Required |
| **Always has value** | No | Yes |
| **Conflation** | Configurable | Always conflates |
| **Use case** | Events, multiple values | Current state |

#### stateIn Examples

```kotlin
// Example 1: User authentication state
class AuthRepository(private val scope: CoroutineScope) {
    private val authChanges = flow {
        // Listen to auth state changes
        while (true) {
            val isAuthenticated = checkAuthStatus()
            emit(isAuthenticated)
            delay(5000)
        }
    }

    val isAuthenticated: StateFlow<Boolean> = authChanges
        .stateIn(
            scope = scope,
            started = SharingStarted.Eagerly, // Start immediately
            initialValue = false // Default state
        )
}

// Usage - always has current auth state
fun main() = runBlocking {
    val auth = AuthRepository(this)

    println("Current state: ${auth.isAuthenticated.value}") // Immediate access

    launch {
        auth.isAuthenticated.collect { authenticated ->
            println("Auth state: $authenticated")
        }
    }

    delay(10000)
}
```

```kotlin
// Example 2: Search results with debounce
class SearchViewModel : ViewModel() {
    private val _searchQuery = MutableStateFlow("")

    val searchResults: StateFlow<List<SearchResult>> = _searchQuery
        .debounce(300)
        .filter { it.length >= 3 }
        .distinctUntilChanged()
        .flatMapLatest { query ->
            searchRepository.search(query)
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList() // Show empty while loading
        )

    fun onSearchQueryChanged(query: String) {
        _searchQuery.value = query
    }
}

// UI can access current value synchronously
fun updateUI(viewModel: SearchViewModel) {
    val currentResults = viewModel.searchResults.value // No suspend needed
    println("Current results: ${currentResults.size}")
}
```

```kotlin
// Example 3: Complex UI state
data class UiState(
    val isLoading: Boolean = false,
    val data: List<Item> = emptyList(),
    val error: String? = null
)

class DataViewModel : ViewModel() {
    val uiState: StateFlow<UiState> = combine(
        loadingFlow,
        dataFlow,
        errorFlow
    ) { isLoading, data, error ->
        UiState(isLoading, data, error)
    }
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = UiState() // Default state
    )
}
```

### Comparison Table: Cold vs Hot Flows

| Aspect | Cold Flow | Hot Flow |
|--------|-----------|----------|
| **Activation** | On collection | Always/Conditionally active |
| **Execution** | Per collector | Shared execution |
| **Data source** | Fresh per collector | Shared data source |
| **Resource usage** | Multiple executions | Single execution |
| **Missed values** | No (starts from beginning) | Yes (joins in progress) |
| **State** | No state | Can have state (StateFlow) |
| **Example types** | `flow { }`, `flowOf()` | `StateFlow`, `SharedFlow` |

### Performance Considerations

```kotlin
// ❌ Bad: Multiple collectors each make network call
class BadRepository {
    fun getUsers(): Flow<List<User>> = flow {
        emit(api.getUsers()) // Called per collector!
    }
}

// In ViewModel
val users1 = repository.getUsers()
val users2 = repository.getUsers() // Another network call!

// ✅ Good: Share single network call
class GoodRepository(scope: CoroutineScope) {
    val users: StateFlow<List<User>> = flow {
        emit(api.getUsers()) // Called once
    }
    .stateIn(
        scope = scope,
        started = SharingStarted.Lazily, // Start on first subscriber
        initialValue = emptyList()
    )
}

// In ViewModel
val users1 = repository.users // Same data
val users2 = repository.users // No extra call
```

### Best Practices

1. **Use cold flows for**:
   - One-time operations (single API call)
   - Per-subscriber fresh data needed
   - Simple transformations
   - Room database queries (already optimized)

2. **Use hot flows (shareIn/stateIn) for**:
   - Expensive operations (network, sensors)
   - Multiple subscribers
   - Background data streams
   - UI state management
   - Caching

3. **Choose started strategy**:
   ```kotlin
   // Background service - always active
   .shareIn(scope, SharingStarted.Eagerly, replay = 1)

   // Lazy initialization - start once
   .stateIn(scope, SharingStarted.Lazily, initialValue)

   // UI updates - efficient resource usage
   .stateIn(scope, SharingStarted.WhileSubscribed(5000), initialValue)
   ```

4. **Configure replay appropriately**:
   ```kotlin
   // No replay - events only
   .shareIn(scope, started, replay = 0)

   // Replay latest - most common
   .shareIn(scope, started, replay = 1)

   // Multiple values - careful with memory
   .shareIn(scope, started, replay = 100) // 100 items in memory!
   ```

### Common Pitfalls

1. **Not using hot flows for expensive operations**:
   ```kotlin
   // ❌ Each screen rotation makes new network call
   val data = flow { emit(api.fetchData()) }

   // ✅ Network call survives rotation
   val data = flow { emit(api.fetchData()) }
       .stateIn(viewModelScope, WhileSubscribed(5000), emptyList())
   ```

2. **Using Eagerly when WhileSubscribed is better**:
   ```kotlin
   // ❌ Flow active even when app in background
   .shareIn(scope, SharingStarted.Eagerly, 1)

   // ✅ Flow stops when no subscribers (saves resources)
   .shareIn(scope, SharingStarted.WhileSubscribed(5000), 1)
   ```

3. **Forgetting initial value with stateIn**:
   ```kotlin
   // ❌ Compilation error - no initial value
   .stateIn(scope, SharingStarted.Lazily)

   // ✅ Provide appropriate default
   .stateIn(scope, SharingStarted.Lazily, emptyList())
   ```

4. **Memory leaks with wrong scope**:
   ```kotlin
   // ❌ Flow never stops - GlobalScope leaks
   .shareIn(GlobalScope, SharingStarted.Eagerly, 1)

   // ✅ Flow lifecycle tied to ViewModel
   .shareIn(viewModelScope, SharingStarted.WhileSubscribed(5000), 1)
   ```

**English Summary**: Cold flows execute independently for each collector, while hot flows share a single execution among multiple collectors. Use shareIn() to convert cold to hot SharedFlow with configurable replay and started strategies. Use stateIn() to convert to StateFlow when you need a state holder with a current value. Choose WhileSubscribed for UI, Lazily for one-time initialization, and Eagerly for always-on services. Hot flows are essential for sharing expensive operations like network calls and sensor data.

## Ответ (RU)

Понимание холодных и горячих потоков фундаментально для построения эффективных реактивных приложений с Kotlin Flow.

### Холодные потоки

**Холодные потоки** активируются при сборе. Каждый коллектор независимо запускает код билдера потока.

#### Ключевые характеристики

1. **Ленивые** - Начинают выполнение только при сборе
2. **Unicast** - Каждый коллектор получает свой независимый поток
3. **Нет общего состояния** - Множественные коллекторы не делят данные
4. **Свежие данные** - Каждый коллектор запускает новое выполнение

#### Пример: Поведение холодного потока

```kotlin
fun createColdFlow(): Flow<Int> = flow {
    println("Поток запущен")
    repeat(3) { i ->
        delay(1000)
        emit(i)
        println("Испущено: $i")
    }
    println("Поток завершен")
}

// Каждый коллектор запускает независимое выполнение
coldFlow.collect { println("Коллектор 1: $it") }
coldFlow.collect { println("Коллектор 2: $it") }
// Код билдера выполняется дважды!
```

#### Реальные примеры холодных потоков

```kotlin
// Запрос к БД - каждый коллектор выполняет запрос
fun getUserFlow(userId: Int): Flow<User> = flow {
    val user = database.getUser(userId) // Свежий запрос каждый раз
    emit(user)
}

// Сетевой запрос - каждый коллектор делает новый запрос
fun fetchArticles(): Flow<List<Article>> = flow {
    val response = api.getArticles() // Новый сетевой вызов каждый раз
    emit(response)
}
```

### Горячие потоки

**Горячие потоки** всегда активны и испускают значения независимо от наличия коллекторов.

#### Ключевые характеристики

1. **Активные** - Работают даже без коллекторов
2. **Multicast** - Все коллекторы получают одинаковые испускания
3. **Общее состояние** - Единое выполнение для всех
4. **Могут пропустить значения** - Коллекторы получают только значения после подписки

### Конвертация холодного в горячий: shareIn()

Оператор `shareIn` конвертирует холодный поток в горячий SharedFlow.

```kotlin
fun <T> Flow<T>.shareIn(
    scope: CoroutineScope,
    started: SharingStarted,
    replay: Int = 0
): SharedFlow<T>
```

#### Объяснение параметров

**1. scope** - CoroutineScope, контролирующий время жизни

**2. replay** - Количество значений для повтора новым подписчикам
- `0` - Нет повтора, новые коллекторы получают только будущие значения
- `1` - Повтор последнего значения (как StateFlow)
- `n` - Повтор последних n значений

**3. started** - Когда запускать/останавливать поток

| Стратегия | Поведение | Применение |
|-----------|-----------|------------|
| **Eagerly** | Запускается сразу, никогда не останавливается | Фоновые сервисы |
| **Lazily** | Запускается при первом подписчике | Кешированные данные |
| **WhileSubscribed** | Запуск/остановка по подписчикам | Наиболее частый, эффективный |

#### Примеры shareIn

```kotlin
// Пример: Данные температурного датчика
class TemperatureSensor(scope: CoroutineScope) {
    private val temperatureReadings = flow {
        while (true) {
            val temp = readTemperature() // Дорогое чтение датчика
            emit(temp)
            delay(1000)
        }
    }

    // Разделение показаний датчика - запуск немедленный
    val temperature: SharedFlow<Float> = temperatureReadings
        .shareIn(
            scope = scope,
            started = SharingStarted.Eagerly,
            replay = 1 // Новые подписчики получают последнюю температуру
        )
}

// Использование - множественные коллекторы разделяют чтения датчика
// Датчик читается только раз в секунду для всех!
```

```kotlin
// Пример: Сетевые данные с WhileSubscribed
class NewsRepository(private val scope: CoroutineScope) {
    val latestNews: SharedFlow<List<Article>> = flow {
        while (true) {
            val news = fetchNewsFromNetwork()
            emit(news)
            delay(60_000)
        }
    }
    .shareIn(
        scope = scope,
        started = SharingStarted.WhileSubscribed(5000), // Остановка через 5с
        replay = 1
    )
}
```

#### Конфигурация WhileSubscribed

```kotlin
SharingStarted.WhileSubscribed(
    stopTimeoutMillis: Long = 0,
    replayExpirationMillis: Long = Long.MAX_VALUE
)
```

**stopTimeoutMillis** - Как долго держать поток активным после последнего подписчика
- `0` - Остановить сразу
- `5000` - 5 секунд (хорошо для поворота экрана)

### Конвертация холодного в горячий: stateIn()

Оператор `stateIn` конвертирует холодный поток в горячий StateFlow.

```kotlin
fun <T> Flow<T>.stateIn(
    scope: CoroutineScope,
    started: SharingStarted,
    initialValue: T
): StateFlow<T>
```

#### Примеры stateIn

```kotlin
// Пример: Состояние аутентификации
class AuthRepository(private val scope: CoroutineScope) {
    val isAuthenticated: StateFlow<Boolean> = authChanges
        .stateIn(
            scope = scope,
            started = SharingStarted.Eagerly,
            initialValue = false // Состояние по умолчанию
        )
}

// Использование - всегда имеет текущее состояние
println("Текущее состояние: ${auth.isAuthenticated.value}") // Немедленный доступ
```

```kotlin
// Пример: Результаты поиска
class SearchViewModel : ViewModel() {
    val searchResults: StateFlow<List<SearchResult>> = _searchQuery
        .debounce(300)
        .distinctUntilChanged()
        .flatMapLatest { query ->
            searchRepository.search(query)
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )
}
```

### Таблица сравнения

| Аспект | Холодный поток | Горячий поток |
|--------|----------------|---------------|
| **Активация** | При сборе | Всегда/Условно |
| **Выполнение** | На коллектор | Общее выполнение |
| **Источник данных** | Свежий для каждого | Общий источник |
| **Использование ресурсов** | Множественные выполнения | Единое выполнение |
| **Пропуск значений** | Нет | Да |

### Лучшие практики

1. **Используйте холодные потоки для**:
   - Одноразовых операций
   - Свежих данных для каждого подписчика
   - Простых трансформаций

2. **Используйте горячие потоки для**:
   - Дорогих операций (сеть, датчики)
   - Множественных подписчиков
   - Управления состоянием UI
   - Кеширования

3. **Выбирайте стратегию started**:
   ```kotlin
   // Фоновый сервис
   .shareIn(scope, SharingStarted.Eagerly, replay = 1)

   // UI обновления
   .stateIn(scope, SharingStarted.WhileSubscribed(5000), initialValue)
   ```

### Распространенные ошибки

1. **Не использование горячих потоков для дорогих операций**:
   ```kotlin
   // ❌ Каждый поворот - новый сетевой вызов
   val data = flow { emit(api.fetchData()) }

   // ✅ Сетевой вызов переживает поворот
   val data = flow { emit(api.fetchData()) }
       .stateIn(viewModelScope, WhileSubscribed(5000), emptyList())
   ```

2. **Утечки памяти с неправильным scope**:
   ```kotlin
   // ❌ Поток никогда не останавливается
   .shareIn(GlobalScope, SharingStarted.Eagerly, 1)

   // ✅ Жизненный цикл привязан к ViewModel
   .shareIn(viewModelScope, SharingStarted.WhileSubscribed(5000), 1)
   ```

**Краткое содержание**: Холодные потоки выполняются независимо для каждого коллектора, горячие потоки разделяют единое выполнение между множественными коллекторами. Используйте shareIn() для конвертации в SharedFlow с настраиваемым replay и стратегиями запуска. Используйте stateIn() для конвертации в StateFlow когда нужен держатель состояния с текущим значением. Выбирайте WhileSubscribed для UI, Lazily для одноразовой инициализации, Eagerly для всегда активных сервисов.

---

## References
- [StateFlow and SharedFlow - Android Developers](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow)
- [Cold flows, hot flows - Kotlin Documentation](https://kotlinlang.org/docs/flow.html#flows-are-cold)
- [shareIn and stateIn operators - Kotlin Blog](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/)

## Related Questions

### Related (Medium)
- [[q-hot-cold-flows--kotlin--medium]] - Coroutines
- [[q-sharedin-statein--kotlin--medium]] - Coroutines
- [[q-stateflow-sharedflow-differences--kotlin--medium]] - Stateflow
- [[q-flow-cold-flow-fundamentals--kotlin--easy]] - Coroutines

### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction

### Related (Medium)
- [[q-hot-cold-flows--kotlin--medium]] - Hot vs Cold flows
- [[q-flow-vs-livedata-comparison--kotlin--medium]] - Flow vs LiveData
- [[q-channels-vs-flow--kotlin--medium]] - Channels vs Flow
- [[q-sharedflow-stateflow--kotlin--medium]] - SharedFlow vs StateFlow
- [[q-stateflow-sharedflow-differences--kotlin--medium]] - StateFlow & SharedFlow differences

### Advanced (Harder)
- [[q-flowon-operator-context-switching--kotlin--hard]] - flowOn & context switching
- [[q-flow-backpressure--kotlin--hard]] - Backpressure handling
- [[q-flow-backpressure-strategies--kotlin--hard]] - Backpressure strategies
