---
id: kotlin-104
title: "Flow Basics in Kotlin / Основы Flow в Kotlin"
aliases: ["Flow Basics in Kotlin, Основы Flow в Kotlin"]

# Classification
topic: kotlin
subtopics: [cold-flow, coroutines, flow]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Introduction to Kotlin Flow

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-flow-exception-handling--kotlin--medium, q-hot-cold-flows--kotlin--medium, q-sharedflow-stateflow--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [cold-flow, coroutines, difficulty/easy, flow, kotlin, reactive, streams]
---
# Вопрос (RU)
> Что такое Kotlin Flow? Объясните холодные vs горячие потоки, базовые операторы и когда использовать Flow.

---

# Question (EN)
> What is Kotlin Flow? Explain cold streams vs hot streams, basic operators, and when to use Flow.

## Ответ (RU)

**Flow** — библиотека асинхронных потоков Kotlin, представляющая холодный асинхронный поток данных. Он излучает множество значений последовательно во времени и построен поверх корутин.

### Что Такое Flow?

```kotlin
// Простой пример Flow
fun simple(): Flow<Int> = flow {
    println("Flow запущен")
    for (i in 1..3) {
        delay(100)
        emit(i)
        println("Излучено $i")
    }
}

fun main() = runBlocking {
    println("Вызов simple()")
    val flow = simple()
    println("Перед collect")
    flow.collect { value ->
        println("Собрано $value")
    }
}
```

**Ключевые характеристики**:
1. **Асинхронный**: Работает с корутинами
2. **Последовательный**: Излучает значения по одному
3. **Холодный**: Не запускается пока не собран
4. **Suspending**: Может использовать suspend функции

### Холодные Vs Горячие Потоки

#### Холодные Потоки (Flow)

```kotlin
val coldFlow = flow {
    println("Flow запущен")
    emit(1)
    emit(2)
    emit(3)
}

// Ничего не происходит...

coldFlow.collect { println(it) }  // Запускает выполнение
// Вывод: Flow запущен, 1, 2, 3

coldFlow.collect { println(it) }  // Запускает снова
// Вывод: Flow запущен, 1, 2, 3 (выполняется с начала)
```

**Характеристики холодного потока**:
- Запускается при сборке
- Каждый коллектор получает независимое выполнение
- Значения вычисляются по требованию
- Как `Sequence`, но асинхронный

### Билдеры Flow

```kotlin
// 1. Билдер flow { }
val flow1 = flow {
    emit(1)
    emit(2)
}

// 2. flowOf - фиксированный набор значений
val flow2 = flowOf(1, 2, 3, 4, 5)

// 3. asFlow - конвертировать коллекцию/последовательность
val flow3 = (1..5).asFlow()
val flow4 = listOf(1, 2, 3).asFlow()
```

### Базовые Операторы

#### Терминальные Операторы (Запускают сборку)

```kotlin
// collect - обработать каждое значение
flow.collect { value ->
    println(value)
}

// toList - собрать в список
val list = flow.toList()

// first - получить первое значение
val first = flow.first()

// reduce - комбинировать значения
val sum = flow.reduce { acc, value ->
    acc + value
}
```

#### Промежуточные Операторы (Трансформируют Flow)

```kotlin
// map - трансформировать значения
flow { emit(1); emit(2) }
    .map { it * 2 }
    .collect { println(it) }  // 2, 4

// filter - фильтровать значения
(1..10).asFlow()
    .filter { it % 2 == 0 }
    .collect { println(it) }  // 2, 4, 6, 8, 10

// take - ограничить эмиссии
(1..100).asFlow()
    .take(5)
    .collect { println(it) }  // 1, 2, 3, 4, 5
```

### Реальные Примеры

#### Паттерн Repository

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
            delay(30_000) // Обновлять каждые 30 секунд
        }
    }
}
```

### Когда Использовать Flow

#### Использовать Flow Для:

```kotlin
// 1. Потоковые данные
fun observeDatabase(): Flow<List<Item>> = database.observeItems()

// 2. Множественные значения во времени
fun countDown(from: Int): Flow<Int> = flow {
    for (i in from downTo 0) {
        emit(i)
        delay(1000)
    }
}
```

#### Не Использовать Flow Для:

```kotlin
// Одно значение - использовать suspend функцию
suspend fun getUser(id: Int): User  // Лучше чем Flow<User>

// Немедленные значения - использовать обычную функцию
fun calculate(x: Int): Int  // Лучше чем Flow<Int>
```

---

## Answer (EN)

**Flow** is Kotlin's asynchronous stream library that represents a cold asynchronous data stream. It emits multiple values sequentially over time and is built on top of coroutines.

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
1. **Asynchronous**: Works with coroutines
2. **Sequential**: Emits values one at a time
3. **Cold**: Doesn't start until collected
4. **Suspending**: Can use suspend functions

### Cold Vs Hot Streams

#### Cold Streams (Flow)

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
- Starts on collection
- Each collector gets independent execution
- Values computed on demand
- Like `Sequence` but asynchronous

#### Hot Streams (SharedFlow/StateFlow)

```kotlin
val hotFlow = MutableSharedFlow<Int>()

launch {
    hotFlow.emit(1)
    hotFlow.emit(2)
}

// Collection starts later, might miss values
hotFlow.collect { println(it) }
```

**Hot stream characteristics**:
- Always active
- Values emitted regardless of collectors
- Multiple collectors share same stream
- Like `Channel` but multiple receivers

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

// 4. channelFlow - hot Flow
val flow5 = channelFlow {
    send(1)
    send(2)
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
            delay(30_000) // Refresh every 30 seconds
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

// 4. Error handling
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
viewModelScope.launch { logEvent() }  // Not Flow
```

### Best Practices

#### DO:
```kotlin
// Use Flow for streams
fun observeData(): Flow<Data> = callbackFlow {
    // Stream data
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
// Don't collect in viewmodel
class BadViewModel : ViewModel() {
    init {
        repository.data.collect { }  //  No scope
    }
}

// Don't expose MutableStateFlow
val state = MutableStateFlow<State>()  //  Mutable

// Use regular function for single values
fun getUser(): Flow<User>  //  Overkill
suspend fun getUser(): User  //  Better
```

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Flow Documentation](https://kotlinlang.org/docs/flow.html)
- [Kotlin Flow Guide](https://developer.android.com/kotlin/flow)
- [Flow API Reference](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-flow/)

## Related Questions

### Same Level (Easy)
- [[q-flow-cold-flow-fundamentals--kotlin--easy]] - Cold flow fundamentals

### Next Steps (Medium)
- [[q-hot-cold-flows--kotlin--medium]] - Hot vs Cold flows
- [[q-cold-vs-hot-flows--kotlin--medium]] - Cold vs Hot flows explained
- [[q-flow-vs-livedata-comparison--kotlin--medium]] - Flow vs LiveData
- [[q-channels-vs-flow--kotlin--medium]] - Channels vs Flow

### Advanced (Harder)
- [[q-kotlin-flow-basics--kotlin--medium]] - Flow
- [[q-catch-operator-flow--kotlin--medium]] - Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction

## MOC Links

- [[moc-kotlin]]
