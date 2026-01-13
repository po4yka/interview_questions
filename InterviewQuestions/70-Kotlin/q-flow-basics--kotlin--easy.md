---
anki_cards:
- slug: q-flow-basics--kotlin--easy-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-flow-basics--kotlin--easy-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
## Answer (EN)

`Flow` is Kotlin's asynchronous stream API that represents a cold asynchronous data stream. It emits multiple values sequentially over time and is built on top of coroutines.

### What is Flow?

```kotlin
// Simple Flow example
fun simple(): Flow<Int> = flow {
    println("Flow started")
    for (i in 1..3) {
        delay(100)
        emit(i)
        println("Emitted $i")
    }
}

fun main() = runBlocking {
    println("Calling simple()")
    val flow = simple()
    println("Before collect")
    flow.collect { value ->
        println("Collected $value")
    }
}

// Output:
// Calling simple()
// Before collect
// Flow started
// Emitted 1
// Collected 1
// Emitted 2
// Collected 2
// Emitted 3
// Collected 3
```

**Key characteristics**:
1. **Asynchronous**: Works with coroutines.
2. **Sequential**: Emits values one at a time.
3. **Cold**: Doesn't start until collection begins.
4. **Suspending-friendly**: Can call `suspend` functions inside.

### Cold Vs Hot Streams

#### Cold Streams (`Flow`)

```kotlin
val coldFlow = flow {
    println("Flow started")
    emit(1)
    emit(2)
    emit(3)
}

// Nothing happens yet...

coldFlow.collect { println(it) }  // Starts execution
// Output: Flow started, 1, 2, 3

coldFlow.collect { println(it) }  // Starts again
// Output: Flow started, 1, 2, 3 (executes from beginning)
```

**Cold stream characteristics**:
- Starts on collection.
- Each collector gets independent execution.
- Values are computed on demand.
- Like `Sequence` but asynchronous.

#### Hot Streams (`SharedFlow` / `StateFlow`)

```kotlin
val hotFlow = MutableSharedFlow<Int>() // default replay = 0

launch {
    hotFlow.emit(1)
    hotFlow.emit(2)
}

// Collection starts later and, because replay = 0, will likely miss these values
hotFlow.collect { println(it) }
```

**Hot stream characteristics**:
- Emissions are produced in the producer's coroutine regardless of active collectors.
- Multiple collectors share the same stream of values.
- Conceptually similar to a multi-subscriber `Channel`, but exposed via `Flow` types like `SharedFlow` and `StateFlow`.

### Flow Builders

```kotlin
// 1. flow { } builder
val flow1 = flow {
    emit(1)
    emit(2)
}

// 2. flowOf - fixed set of values
val flow2 = flowOf(1, 2, 3, 4, 5)

// 3. asFlow - convert collection/sequence
val flow3 = (1..5).asFlow()
val flow4 = listOf(1, 2, 3).asFlow()

// 4. channelFlow - concurrent-safe cold Flow builder using channels internally
val flow5 = channelFlow {
    send(1)
    send(2)
    // remember to call awaitClose { ... } when using callbacks/resources
}
```

### Basic Operators

#### Terminal Operators (Trigger collection)

```kotlin
// collect - process each value
flow.collect { value ->
    println(value)
}

// toList - collect to list
val list = flow.toList()

// first - get first value
val first = flow.first()

// single - get single value (or throw)
val single = flow.single()

// reduce - combine values
val sum = flow.reduce { acc, value ->
    acc + value
}

// fold - reduce with initial value
val result = flow.fold(0) { acc, value ->
    acc + value
}
```

#### Intermediate Operators (Transform Flow)

```kotlin
// map - transform values
flow { emit(1); emit(2) }
    .map { it * 2 }
    .collect { println(it) }  // 2, 4

// filter - filter values
(1..10).asFlow()
    .filter { it % 2 == 0 }
    .collect { println(it) }  // 2, 4, 6, 8, 10

// transform - emit multiple values
(1..3).asFlow()
    .transform { value ->
        emit("Value: $value")
        emit("Squared: ${value * value}")
    }
    .collect { println(it) }

// take - limit emissions
(1..100).asFlow()
    .take(5)
    .collect { println(it) }  // 1, 2, 3, 4, 5

// drop - skip first n values
(1..10).asFlow()
    .drop(5)
    .collect { println(it) }  // 6, 7, 8, 9, 10
```

### Real-World Examples

#### Repository Pattern

```kotlin
class UserRepository(private val api: ApiService) {
    fun getUsers(): Flow<List<User>> = flow {
        val users = api.fetchUsers()
        emit(users)
    }

    fun observeUsers(): Flow<List<User>> = flow {
        while (true) {
            val users = api.fetchUsers()
            emit(users)
            delay(30_000) // Refresh every 30 seconds; loop stops when collection is cancelled
        }
    }
}

class UserViewModel(private val repository: UserRepository) : ViewModel() {
    val users: StateFlow<List<User>> = repository.getUsers()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )
}
```

#### Search with Debounce

```kotlin
class SearchViewModel : ViewModel() {
    private val _searchQuery = MutableStateFlow("")

    val searchResults: StateFlow<List<Result>> = _searchQuery
        .debounce(300)
        .filter { it.length >= 3 }
        .flatMapLatest { query ->
            searchRepository.search(query)
        }
        .catch { e -> emit(emptyList()) }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            initialValue = emptyList()
        )

    fun onSearchQueryChanged(query: String) {
        _searchQuery.value = query
    }
}
```

### When to Use Flow

#### Use Flow For:

```kotlin
// 1. Streaming data
fun observeDatabase(): Flow<List<Item>> = database.observeItems()

// 2. Multiple values over time
fun countDown(from: Int): Flow<Int> = flow {
    for (i in from downTo 0) {
        emit(i)
        delay(1000)
    }
}

// 3. Async transformations
fun processData(input: Flow<Data>): Flow<ProcessedData> =
    input.map { processAsync(it) }

// 4. Error handling with retry
fun loadWithRetry(): Flow<Data> = flow {
    emit(fetchData())
}.retry(3) { it is IOException }
```

#### Don't Use Flow For:

```kotlin
// Single value - use suspend function instead
suspend fun getUser(id: Int): User  // Better than Flow<User>

// Immediate values - use regular function
fun calculate(x: Int): Int  // Better than Flow<Int>

// Fire-and-forget - use launch
viewModelScope.launch { logEvent() }  // Use a coroutine, not Flow
```

### Best Practices

#### DO:
```kotlin
// Use Flow for streams
fun observeData(): Flow<Data> = callbackFlow {
    // Stream data from callbacks / listeners
    // ...
    awaitClose {
        // Clean up resources / unsubscribe from callbacks
    }
}

// Chain operators
flow.map { }
    .filter { }
    .distinctUntilChanged()
    .collect { }

// Handle exceptions
flow.catch { e ->
    emit(defaultValue)
}.collect { }

// Use flowOn for dispatchers
flow {
    emit(heavyWork())
}.flowOn(Dispatchers.Default)
```

#### DON'T:
```kotlin
// Avoid unbounded collection without considering the consumer lifecycle
class BadViewModel : ViewModel() {
    init {
        viewModelScope.launch {
            repository.data.collect { }
            // This collection started in init will live for the whole ViewModel lifetime,
            // even if the UI no longer needs these updates.
        }
    }
}

// Don't expose MutableStateFlow directly; expose it as StateFlow
private val _state = MutableStateFlow<State>(Initial)
val state: StateFlow<State> = _state

// Avoid Flow for a simple single-shot value
fun getUser(): Flow<User>  // Overkill in most cases
suspend fun getUser(): User  // Prefer this
```

---

## Дополнительные Вопросы (RU)

- Каковы ключевые отличия `Flow` от Java-подходов к асинхронности?
- Когда вы бы использовали `Flow` на практике?
- Какие распространённые ошибки при использовании `Flow` стоит избегать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Документация Kotlin Flow](https://kotlinlang.org/docs/flow.html)
- [Руководство по Kotlin Flow](https://developer.android.com/kotlin/flow)
- [Flow API Reference](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-flow/)

## References

- [Kotlin `Flow` Documentation](https://kotlinlang.org/docs/flow.html)
- [Kotlin `Flow` Guide](https://developer.android.com/kotlin/flow)
- [Flow API Reference](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-flow/)

## Связанные Вопросы (RU)

### Тот Же Уровень (Easy)
- [[q-flow-cold-flow-fundamentals--kotlin--easy]] - Основы холодных потоков

### Следующие Шаги (Medium)
- [[q-hot-cold-flows--kotlin--medium]] - Hot vs Cold Flows
- [[q-cold-vs-hot-flows--kotlin--medium]] - Объяснение Cold vs Hot Flows
- [[q-flow-vs-livedata-comparison--kotlin--medium]] - `Flow` vs `LiveData`
- [[q-channels-vs-flow--kotlin--medium]] - Каналы vs `Flow`

### Продвинутые (Harder)
- [[q-kotlin-flow-basics--kotlin--medium]] - Введение в `Flow`
- [[q-catch-operator-flow--kotlin--medium]] - Оператор catch в `Flow`
- [[q-flow-operators-map-filter--kotlin--medium]] - Операторы `Flow`

### Хаб
- [[q-kotlin-flow-basics--kotlin--medium]] - Комплексное введение в `Flow`

## Related Questions

### Same Level (Easy)
- [[q-flow-cold-flow-fundamentals--kotlin--easy]] - Cold flow fundamentals

### Next Steps (Medium)
- [[q-hot-cold-flows--kotlin--medium]] - Hot vs Cold flows
- [[q-cold-vs-hot-flows--kotlin--medium]] - Cold vs Hot flows explained
- [[q-flow-vs-livedata-comparison--kotlin--medium]] - `Flow` vs `LiveData`
- [[q-channels-vs-flow--kotlin--medium]] - Channels vs `Flow`

### Advanced (Harder)
- [[q-kotlin-flow-basics--kotlin--medium]] - `Flow`
- [[q-catch-operator-flow--kotlin--medium]] - `Flow`
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive `Flow` introduction

## MOC Links

- [[moc-kotlin]]
