---
anki_cards:
- slug: q-cold-vs-hot-flows--kotlin--medium-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-cold-vs-hot-flows--kotlin--medium-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
---id: kotlin-059
title: "Cold vs Hot Flows / Холодные и горячие потоки"
aliases: ["Cold vs Hot Flows", "Холодные и горячие потоки"]
topic: kotlin
subtopics: [flow]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
source: internal
source_note: Phase 1 Coroutines & Flow Advanced Questions
status: draft
moc: moc-kotlin
related: [c-concurrency, c-stateflow, q-kotlin-flow-basics--kotlin--medium, q-stateflow-sharedflow-differences--kotlin--medium]
created: 2025-10-11
updated: 2025-11-11
tags: [cold-flows, difficulty/medium, flow, hot-flows, kotlin, shareIn, stateIn]

---
# Вопрос (RU)
> Объясните холодные и горячие потоки. Как `shareIn` и `stateIn` конвертируют холодные в горячие? Как правильно настроить параметры `replay` и `started`?

# Question (EN)
> Explain cold vs hot flows. How do `shareIn` and `stateIn` convert cold to hot? Configure `replay` and `started` parameters properly.

---

## Ответ (RU)

Понимание холодных и горячих потоков фундаментально для построения эффективных и ресурс-эффективных реактивных приложений с Kotlin `Flow` и корутинами (`Coroutine`, [[c-concurrency]]).

### Холодные Потоки

**Холодные потоки** запускают свой upstream при начале коллекции. Каждый коллектор независимо запускает код билдера потока.

#### Ключевые Характеристики

1. **Ленивые** - Начинают выполнение только при сборе
2. **Unicast по умолчанию** - Каждый коллектор получает свой независимый поток выполнения
3. **Нет общего состояния** - Множественные коллекторы не делят одно и то же выполнение
4. **Свежие данные** - Каждый коллектор запускает новое выполнение upstream

#### Пример: Поведение Холодного Потока

```kotlin
fun createColdFlow(): Flow<Int> = flow {
    println("Flow started at ${'$'}{System.currentTimeMillis()}")
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
Ключевой момент: каждый коллектор запускает собственное выполнение.
Вы увидите "Flow started" дважды, в разные моменты времени.
*/
```

#### Реальные Примеры Холодных Потоков

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

// Чтение файла - каждый коллектор читает файл с начала
fun readLogFile(): Flow<String> = flow {
    File("logs.txt").forEachLine { line ->
        emit(line)
    }
}
```

### Горячие Потоки

**Горячие потоки** продолжают испускать значения независимо от того, кто и когда на них подписывается. Коллекторы разделяют одно и то же исполнение или состояние.

#### Ключевые Характеристики

1. **Не зависят от коллектора** - Могут испускать значения, даже когда подписчиков нет (в зависимости от реализации/стратегии)
2. **Multicast** - Несколько коллекторов получают одно и то же последовательное исполнение
3. **Общее состояние/исполнение** - Один upstream разделяется между всеми подписчиками
4. **Могут пропустить значения** - Подписчики получают только значения, испущенные после подписки (за исключением того, что покрывает `replay`)

### Встроенные Горячие Потоки

```kotlin
// `StateFlow` - всегда хранит текущее значение
val stateFlow = MutableStateFlow(0)

// `SharedFlow` - настраиваемый горячий поток
val sharedFlow = MutableSharedFlow<Int>(
    replay = 0,
    extraBufferCapacity = 0,
    onBufferOverflow = BufferOverflow.SUSPEND
)
```

### Конвертация Холодного В Горячий: `shareIn()`

Оператор `shareIn` конвертирует холодный поток в горячий `SharedFlow`, запуская общий корутин, который коллекционирует исходный `Flow` и шарит значения.

```kotlin
fun <T> Flow<T>.shareIn(
    scope: CoroutineScope,
    started: SharingStarted,
    replay: Int = 0
): SharedFlow<T>
```

#### Объяснение Параметров

**1. scope** - `CoroutineScope`, контролирующий время жизни шарящего корутина.

**2. replay** - Количество значений для повтора новым подписчикам:
- `0` - Нет повтора, новые коллекторы получают только будущие значения
- `1` - Повтор последнего значения (поведение, похожее на `StateFlow`)
- `n` - Повтор последних `n` значений

**3. started** - Когда запускать/останавливать общий сбор исходного потока.

| Стратегия | Поведение | Применение |
|-----------|-----------|------------|
| **Eagerly** | Сбор стартует сразу и не останавливается до отмены `scope` | Фоновые сервисы, постоянные потоки |
| **Lazily** | Старт при первом подписчике и без авто-остановки | Кешированные/инициализационные данные в рамках `scope` |
| **WhileSubscribed** | Старт при появлении первого подписчика, остановка с таймаутом после ухода последнего | Наиболее часто для UI, ресурс-эффективно |

#### Примеры `shareIn`

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

    // Разделение показаний датчика
    val temperature: SharedFlow<Float> = temperatureReadings
        .shareIn(
            scope = scope,
            started = SharingStarted.Eagerly,
            replay = 1 // Новые подписчики получают последнюю температуру
        )

    private fun readTemperature(): Float {
        println("Reading temperature sensor...")
        return (20..30).random().toFloat()
    }
}

// Множественные коллекторы разделяют одно чтение в секунду
```

```kotlin
// Пример: Сетевые данные с WhileSubscribed
class NewsRepository(private val scope: CoroutineScope) {
    private val newsUpdates = flow {
        while (true) {
            val news = fetchNewsFromNetwork()
            emit(news)
            delay(60_000)
        }
    }

    val latestNews: SharedFlow<List<Article>> = newsUpdates
        .shareIn(
            scope = scope,
            started = SharingStarted.WhileSubscribed(5000), // Остановка через 5с после последнего подписчика
            replay = 1
        )
}
```

#### Конфигурация `WhileSubscribed`

```kotlin
SharingStarted.WhileSubscribed(
    stopTimeoutMillis: Long = 0,
    replayExpirationMillis: Long = Long.MAX_VALUE
)
```

**stopTimeoutMillis** - Как долго держать сбор активным после ухода последнего подписчика:
- `0` - Остановить сразу
- `5000` - 5 секунд (удобно для поворота экрана)

**replayExpirationMillis** - Как долго кеш `replay` остаётся доступен без подписчиков:
- `Long.MAX_VALUE` (по умолчанию) - не очищать автоматически
- другое значение - очистка после заданной паузы

```kotlin
// Пример: ViewModel с WhileSubscribed
class MyViewModel : ViewModel() {
    val uiState = repository.dataFlow
        .shareIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            replay = 1
        )
}
```

### Конвертация Холодного В Горячий: `stateIn()`

Оператор `stateIn` конвертирует холодный поток в горячий `StateFlow`, который всегда имеет текущее значение и ведёт себя как "горячий" источник состояния.

```kotlin
fun <T> Flow<T>.stateIn(
    scope: CoroutineScope,
    started: SharingStarted,
    initialValue: T
): StateFlow<T>
```

#### Ключевые Отличия От `shareIn`

| Характеристика | `shareIn` | `stateIn` |
|----------------|-----------|-----------|
| **Тип результата** | `SharedFlow` | `StateFlow` |
| **Начальное значение** | Через `replay` (необязательно) | Обязательно `initialValue` |
| **Всегда есть значение** | Нет | Да |
| **Конфляция** | Настраивается | Всегда хранит только последнее |
| **Использование** | Потоки событий/несколько значений | Держатель текущего состояния |

#### Примеры `stateIn`

```kotlin
// Пример 1: Состояние аутентификации
class AuthRepository(private val scope: CoroutineScope) {
    private val authChanges: Flow<Boolean> = flow {
        while (true) {
            emit(checkAuthStatus())
            delay(5000)
        }
    }

    val isAuthenticated: StateFlow<Boolean> = authChanges
        .stateIn(
            scope = scope,
            started = SharingStarted.Eagerly,
            initialValue = false // Состояние по умолчанию
        )
}

// Всегда есть текущее состояние
println("Текущее состояние: ${'$'}{authRepository.isAuthenticated.value}")
```

```kotlin
// Пример 2: Результаты поиска с debounce и фильтрацией
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
            initialValue = emptyList()
        )
}
```

```kotlin
// Пример 3: Сложное UI-состояние из нескольких потоков

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
            initialValue = UiState() // Значение по умолчанию
        )
}
```

### Таблица Сравнения: Холодные Vs Горячие Потоки

| Аспект | Холодный поток | Горячий поток |
|--------|----------------|---------------|
| **Активация** | При сборе | Активен независимо от конкретного коллектора (в рамках стратегии) |
| **Выполнение** | На коллектор | Общее выполнение |
| **Источник данных** | Свежий для каждого | Общий источник |
| **Использование ресурсов** | Множественные выполнения | Единое выполнение на `scope`/шару |
| **Пропуск значений** | Как правило, нет: каждый сбор с начала | Возможны пропуски; `replay` частично компенсирует |
| **Состояние** | Нет встроенного состояния | Может хранить состояние (например, `StateFlow`) |
| **Примеры типов** | `flow { }`, `flowOf()` | `StateFlow`, `SharedFlow` |

### Соображения Производительности

```kotlin
// Плохо: каждый коллектор триггерит API вызов
class BadRepository {
    fun getUsers(): Flow<List<User>> = flow {
        emit(api.getUsers())
    }
}

// Во ViewModel несколько подписчиков => несколько сетевых запросов
val usersFlow1 = repository.getUsers()
val usersFlow2 = repository.getUsers()

// Хорошо: шарим выполнение в рамках scope
class GoodRepository(scope: CoroutineScope) {
    val users: StateFlow<List<User>> = flow {
        emit(api.getUsers()) // Вызывается один раз за жизненный цикл шаринга
    }
        .stateIn(
            scope = scope,
            started = SharingStarted.Lazily,
            initialValue = emptyList()
        )
}

// Во ViewModel оба используют одно и то же состояние
val users1 = repository.users
val users2 = repository.users
```

### Лучшие Практики

1. **Используйте холодные потоки для**:
   - Одноразовых операций (один API вызов)
   - Когда каждому подписчику нужно независимое выполнение
   - Простых ленивых трансформаций и репозиторных API

2. **Используйте горячие потоки (`shareIn`/`stateIn`) для**:
   - Дорогих операций, результаты которых нужно шарить
   - Множественных подписчиков одного и того же источника данных
   - Фоновых/непрерывных потоков данных
   - Управления состоянием UI и кеширования в рамках `scope`

3. **Выбор стратегии `started`**:
   ```kotlin
   // Поток, похожий на сервис, всегда активен в рамках scope
   .shareIn(scope, SharingStarted.Eagerly, replay = 1)

   // Ленивое начало без авто-остановки
   .stateIn(scope, SharingStarted.Lazily, initialValue)

   // UI-обновления, которые останавливаются, когда нет подписчиков
   .stateIn(scope, SharingStarted.WhileSubscribed(5000), initialValue)
   ```

4. **Правильная конфигурация `replay`**:
   ```kotlin
   // Без повторов — одноразовые события
   .shareIn(scope, started, replay = 0)

   // Повтор последнего — распространено для UI-состояния
   .shareIn(scope, started, replay = 1)

   // Несколько значений — следите за памятью
   .shareIn(scope, started, replay = 100)
   ```

### Распространенные Ошибки

1. **Неиспользование горячих потоков для дорогих операций**:
   ```kotlin
   // Каждый сбор запускает новый сетевой вызов
   val data: Flow<List<Item>> = flow { emit(api.fetchData()) }

   // Правильно: расшарить результат в рамках scope
   val sharedData: StateFlow<List<Item>> = flow { emit(api.fetchData()) }
       .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())
   ```

2. **Использование `Eagerly`, когда лучше `WhileSubscribed`**:
   ```kotlin
   // Поток активен даже без подписчиков
   .shareIn(scope, SharingStarted.Eagerly, 1)

   // Экономия ресурсов: активен только при наличии подписчиков
   .shareIn(scope, SharingStarted.WhileSubscribed(5000), 1)
   ```

3. **Забывают про `initialValue` в `stateIn`**:
   ```kotlin
   // Неверно: отсутствует начальное значение (ошибка компиляции)
   // .stateIn(scope, SharingStarted.Lazily)

   // Верно: задать подходящее значение по умолчанию
   .stateIn(scope, SharingStarted.Lazily, emptyList())
   ```

4. **Утечки памяти / неверный жизненный цикл из-за `scope`**:
   ```kotlin
   // Поток может жить дольше, чем нужно
   .shareIn(GlobalScope, SharingStarted.Eagerly, 1)

   // Верно: привязать к жизненному циклу (например, ViewModel)
   .shareIn(viewModelScope, SharingStarted.WhileSubscribed(5000), 1)
   ```

**Краткое резюме (RU)**: Холодные потоки выполняются независимо для каждого коллектора; горячие потоки разделяют единое выполнение или состояние между несколькими коллекторами и могут эмитить значения независимо от подписчиков (в зависимости от стратегии). Используйте `shareIn()` для конвертации `Flow` в `SharedFlow` с настраиваемыми `replay` и стратегиями запуска. Используйте `stateIn()` для получения `StateFlow` как держателя текущего состояния. Предпочитайте `WhileSubscribed` для UI, `Lazily` для одноразовой инициализации в `scope`, `Eagerly` для всегда-активных сервисов.

---

## Answer (EN)

Understanding cold vs hot flows is fundamental to building efficient reactive applications with Kotlin `Flow`. The distinction affects performance, resource usage, and data sharing patterns.

### Cold Flows

**Cold flows** start their upstream when collected. Each collector independently triggers the flow builder code.

#### Key Characteristics

1. **Lazy** - Start executing only when collected
2. **Unicast by default** - Each collector gets its own independent execution
3. **No shared upstream state** - Multiple collectors don't share a single execution
4. **Fresh data** - Each collector triggers a new upstream run

#### Example: Cold Flow Behavior

```kotlin
fun createColdFlow(): Flow<Int> = flow {
    println("Flow started at ${'$'}{System.currentTimeMillis()}")
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
Key point: each collector triggers its own execution.
You'll see "Flow started" printed twice at different times.
*/
```

#### Real-world Cold Flow Examples

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

// File reading - each collector reads file from beginning
fun readLogFile(): Flow<String> = flow {
    File("logs.txt").forEachLine { line ->
        emit(line)
    }
}
```

### Hot Flows

**Hot flows** produce values independently of any particular collector. Multiple collectors observe a shared execution or shared state, and may miss values emitted before they start collecting (except for what is covered by `replay`).

#### Key Characteristics

1. **Independent from individual collectors** - Can keep emitting even with zero subscribers, depending on implementation/`SharingStarted`
2. **Multicast** - Multiple collectors observe the same logical stream
3. **Shared state/execution** - Single upstream shared among collectors
4. **May miss values** - Collectors receive values emitted after subscription (plus any replayed ones)

#### Built-in Hot Flows

```kotlin
// `StateFlow` - always holds a current value
val stateFlow = MutableStateFlow(0)

// `SharedFlow` - configurable hot flow
val sharedFlow = MutableSharedFlow<Int>(
    replay = 0,
    extraBufferCapacity = 0,
    onBufferOverflow = BufferOverflow.SUSPEND
)
```

### Converting Cold to Hot: `shareIn()`

The `shareIn` operator converts a cold `Flow` into a hot `SharedFlow` by launching a single collector in the given scope and multicasting emissions.

```kotlin
fun <T> Flow<T>.shareIn(
    scope: CoroutineScope,
    started: SharingStarted,
    replay: Int = 0
): SharedFlow<T>
```

#### Parameters Explained

**1. scope** - `CoroutineScope` that controls the lifetime of the sharing coroutine.

**2. replay** - Number of values to replay to new subscribers:
- `0` - No replay, new collectors only get future values
- `1` - Replay last value (`StateFlow`-like behavior)
- `n` - Replay last `n` values

**3. started** - When to start/stop collecting the upstream `Flow`.

| Strategy | Behavior | Use Case |
|----------|----------|----------|
| **Eagerly** | Start immediately and keep running until scope is cancelled | Background services, always-on streams |
| **Lazily** | Start on first subscriber and never stop automatically | Cached data, one-time initialization in a scope |
| **WhileSubscribed** | Start when first subscriber appears; stop after timeout when last leaves | Most common for UI, resource-efficient |

#### `shareIn` Examples

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

    // Share sensor readings
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
}
```

#### WhileSubscribed Configuration

```kotlin
SharingStarted.WhileSubscribed(
    stopTimeoutMillis: Long = 0,
    replayExpirationMillis: Long = Long.MAX_VALUE
)
```

**stopTimeoutMillis** - How long to keep collecting after the last subscriber:
- `0` - Stop immediately
- `5000` - Keep active for 5 seconds (good for configuration changes)

**replayExpirationMillis** - How long replay cache stays valid without subscribers:
- `Long.MAX_VALUE` - Never expire (default)
- Custom value - Clear cache after period with no subscribers

```kotlin
// Android ViewModel example - survive configuration changes within timeout
class MyViewModel : ViewModel() {
    val uiState = repository.dataFlow
        .shareIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            replay = 1
        )
}
```

### Converting Cold to Hot: `stateIn()`

The `stateIn` operator converts a cold `Flow` into a hot `StateFlow` that always has a current value and shares a single collection.

```kotlin
fun <T> Flow<T>.stateIn(
    scope: CoroutineScope,
    started: SharingStarted,
    initialValue: T
): StateFlow<T>
```

#### Key Differences from `shareIn`

| Feature | `shareIn` | `stateIn` |
|---------|-----------|-----------|
| **Return type** | `SharedFlow` | `StateFlow` |
| **Initial value** | Optional via `replay` | Required |
| **Always has value** | No | Yes |
| **Conflation** | Configurable | Always conflates to latest |
| **Use case** | Event/multi-value streams | Current state holder |

#### `stateIn` Examples

```kotlin
// Example 1: User authentication state
class AuthRepository(private val scope: CoroutineScope) {
    private val authChanges = flow {
        while (true) {
            val isAuthenticated = checkAuthStatus()
            emit(isAuthenticated)
            delay(5000)
        }
    }

    val isAuthenticated: StateFlow<Boolean> = authChanges
        .stateIn(
            scope = scope,
            started = SharingStarted.Eagerly, // Start immediately in this scope
            initialValue = false // Default state
        )
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

### Comparison Table: Cold Vs Hot Flows

| Aspect | Cold `Flow` | Hot `Flow` |
|--------|-----------|----------|
| **Activation** | On collection | Active independently of individual collectors (per strategy) |
| **Execution** | Per collector | Shared execution |
| **Data source** | Fresh per collector | Shared data source |
| **Resource usage** | Multiple executions | Single execution per sharing lifecycle |
| **Missed values** | Typically no (starts from beginning) | Possible (unless covered by `replay`) |
| **State** | No inherent state | Can hold state (e.g., `StateFlow`) |
| **Example types** | `flow { }`, `flowOf()` | `StateFlow`, `SharedFlow` |

### Performance Considerations

```kotlin
// Bad: Each collector triggers an API call (per execution of this flow)
class BadRepository {
    fun getUsers(): Flow<List<User>> = flow {
        emit(api.getUsers())
    }
}

// In ViewModel, separate calls cause multiple network requests
val usersFlow1 = repository.getUsers()
val usersFlow2 = repository.getUsers()

// Better: Share within a scope so collectors reuse the same execution
class GoodRepository(scope: CoroutineScope) {
    val users: StateFlow<List<User>> = flow {
        emit(api.getUsers()) // Executed once per sharing lifecycle
    }
        .stateIn(
            scope = scope,
            started = SharingStarted.Lazily, // Start on first subscriber
            initialValue = emptyList()
        )
}

// In ViewModel
val users1 = repository.users // Same shared data
val users2 = repository.users
```

### Best Practices

1. **Use cold flows for**:
   - One-time operations (single API call)
   - When each subscriber needs an independent execution
   - Simple transformations and repository APIs that remain lazy

2. **Use hot flows (`shareIn`/`stateIn`) for**:
   - Expensive operations that should be shared
   - Multiple subscribers observing same data
   - Background/continuous data streams
   - UI state management and caching within a scope

3. **Choose `started` strategy**:
   ```kotlin
   // Background service-like streams
   .shareIn(scope, SharingStarted.Eagerly, replay = 1)

   // Lazy initialization within scope (no auto-stop)
   .stateIn(scope, SharingStarted.Lazily, initialValue)

   // UI updates that stop when not observed
   .stateIn(scope, SharingStarted.WhileSubscribed(5000), initialValue)
   ```

4. **Configure `replay` appropriately**:
   ```kotlin
   // No replay - fire-and-forget events
   .shareIn(scope, started, replay = 0)

   // Replay latest - common for UI state-ish data
   .shareIn(scope, started, replay = 1)

   // Multiple values - be mindful of memory
   .shareIn(scope, started, replay = 100)
   ```

### Common Pitfalls

1. **Not using hot flows for expensive operations**:
   ```kotlin
   // Each collection triggers a new network call
   val data: Flow<List<Item>> = flow { emit(api.fetchData()) }

   // Share result within ViewModel scope across collectors
   val sharedData: StateFlow<List<Item>> = flow { emit(api.fetchData()) }
       .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())
   ```

2. **Using `Eagerly` when `WhileSubscribed` is better**:
   ```kotlin
   // Flow active even when nobody is observing
   .shareIn(scope, SharingStarted.Eagerly, 1)

   // Flow stops when no subscribers (saves resources)
   .shareIn(scope, SharingStarted.WhileSubscribed(5000), 1)
   ```

3. **Forgetting initial value with `stateIn`**:
   ```kotlin
   // Compilation error - missing initial value
   // .stateIn(scope, SharingStarted.Lazily)

   // Correct: provide appropriate default
   .stateIn(scope, SharingStarted.Lazily, emptyList())
   ```

4. **Memory leaks / unexpected lifetime with wrong scope**:
   ```kotlin
   // May run longer than intended
   .shareIn(GlobalScope, SharingStarted.Eagerly, 1)

   // Correct: tie to lifecycle (e.g., ViewModel)
   .shareIn(viewModelScope, SharingStarted.WhileSubscribed(5000), 1)
   ```

**English Summary**: Cold flows execute independently for each collector; hot flows share a single execution or state among multiple collectors and may emit regardless of who is collecting, depending on the strategy. Use `shareIn()` to convert a cold `Flow` into a `SharedFlow` with configurable `replay` and starting behavior. Use `stateIn()` to convert into a `StateFlow` when you need a state holder with a current value. Prefer `WhileSubscribed` for UI, `Lazily` for one-time initialization that stays active within scope, and `Eagerly` for always-on services.

## Дополнительные Вопросы (RU)

- В чем ключевые отличия этого подхода от Java без `Flow`/горячих потоков?
- Когда бы вы использовали это на практике?
- Как избежать распространенных ошибок при использовании `shareIn` и `stateIn`?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [`StateFlow` и `SharedFlow` - Android Developers](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow)
- [Холодные и горячие потоки - Документация Kotlin](https://kotlinlang.org/docs/flow.html#flows-are-cold)
- [Операторы `shareIn` и `stateIn` - Kotlinx Coroutines](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/)

## References

- [`StateFlow` and `SharedFlow` - Android Developers](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow)
- [Cold flows, hot flows - Kotlin Documentation](https://kotlinlang.org/docs/flow.html#flows-are-cold)
- [shareIn and stateIn operators - Kotlinx Coroutines](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/)

## Связанные Вопросы (RU)

### Похожие (Medium)
- [[q-hot-cold-flows--kotlin--medium]]
- [[q-sharedin-statein--kotlin--medium]]
- [[q-stateflow-sharedflow-differences--kotlin--medium]]
- [[q-flow-cold-flow-fundamentals--kotlin--easy]]

### Продвинутые (Harder)
- [[q-testing-flow-operators--kotlin--hard]]

### Хаб
- [[q-kotlin-flow-basics--kotlin--medium]]

## Related Questions

### Related (Medium)
- [[q-hot-cold-flows--kotlin--medium]]
- [[q-sharedin-statein--kotlin--medium]]
- [[q-stateflow-sharedflow-differences--kotlin--medium]]
- [[q-flow-cold-flow-fundamentals--kotlin--easy]]

### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]]

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]]
