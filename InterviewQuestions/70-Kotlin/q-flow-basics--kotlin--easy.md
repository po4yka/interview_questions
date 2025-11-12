---
id: kotlin-104
title: "Flow Basics in Kotlin / Основы Flow в Kotlin"
aliases: ["Flow Basics in Kotlin", "Основы Flow в Kotlin"]

# Classification
topic: kotlin
subtopics: [coroutines, flow, cold-flow]
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
related: [c-flow, c-kotlin-coroutines-basics, q-flow-exception-handling--kotlin--medium, q-hot-cold-flows--kotlin--medium, q-sharedflow-stateflow--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-11-09

tags: [cold-flow, coroutines, difficulty/easy, flow, kotlin, reactive, streams]
---
# Вопрос (RU)
> Что такое Kotlin `Flow`? Объясните холодные vs горячие потоки, базовые операторы и когда использовать `Flow`.

# Question (EN)
> What is Kotlin `Flow`? Explain cold streams vs hot streams, basic operators, and when to use `Flow`.

## Ответ (RU)

`Flow` — это API асинхронных потоков в Kotlin, представляющее холодный асинхронный поток данных. Он излучает (emits) множество значений последовательно во времени и построен поверх корутин. См. также: [[c-flow]], [[c-coroutines]].

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
1. **Асинхронный**: Работает с корутинами.
2. **Последовательный**: Излучает значения по одному.
3. **Холодный**: Не запускается, пока не начнётся сбор (collect).
4. **Поддерживает приостановку**: Внутри можно вызывать `suspend`-функции.

### Холодные Vs Горячие Потоки

#### Холодные Потоки (`Flow`)

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
- Запускается при сборе.
- Каждый коллектор получает независимое выполнение.
- Значения вычисляются по требованию.
- Похож на `Sequence`, но асинхронный.

#### Горячие Потоки (`SharedFlow` / `StateFlow`)

```kotlin
val hotFlow = MutableSharedFlow<Int>() // по умолчанию replay = 0

launch {
    hotFlow.emit(1)
    hotFlow.emit(2)
}

// Коллекция начинается позже и из-за replay = 0, скорее всего пропустит эти значения
hotFlow.collect { println(it) }
```

**Характеристики горячего потока**:
- Значения излучаются в контексте продюсера независимо от наличия сборщиков.
- Несколько сборщиков разделяют один и тот же поток данных.
- Похож на многоподписочный канал (`Channel`), но с API `Flow` (такие как `SharedFlow`, `StateFlow`).

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

// 4. channelFlow - поток с использованием каналов для конкурентных операций
val flow5 = channelFlow {
    send(1)
    send(2)
    // не забывайте вызывать awaitClose { ... } при использовании колбэков/ресурсов
}
```

### Базовые Операторы

#### Терминальные Операторы (запускают сбор)

```kotlin
// collect - обработать каждое значение
flow.collect { value ->
    println(value)
}

// toList - собрать в список
val list = flow.toList()

// first - получить первое значение
val first = flow.first()

// single - получить единственное значение (или выбросить исключение)
val single = flow.single()

// reduce - комбинировать значения
val sum = flow.reduce { acc, value ->
    acc + value
}

// fold - reduce с начальным значением
val result = flow.fold(0) { acc, value ->
    acc + value
}
```

#### Промежуточные Операторы (трансформируют Flow)

```kotlin
// map - трансформировать значения
flow { emit(1); emit(2) }
    .map { it * 2 }
    .collect { println(it) }  // 2, 4

// filter - фильтровать значения
(1..10).asFlow()
    .filter { it % 2 == 0 }
    .collect { println(it) }  // 2, 4, 6, 8, 10

// transform - из одного входного значения эмитить несколько
(1..3).asFlow()
    .transform { value ->
        emit("Value: $value")
        emit("Squared: ${value * value}")
    }
    .collect { println(it) }

// take - ограничить эмиссии
(1..100).asFlow()
    .take(5)
    .collect { println(it) }  // 1, 2, 3, 4, 5

// drop - пропустить первые n значений
(1..10).asFlow()
    .drop(5)
    .collect { println(it) }  // 6, 7, 8, 9, 10
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
            delay(30_000) // Обновлять каждые 30 секунд; цикл прекратится при отмене коллекции
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

#### Поиск с Debounce

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

### Когда Использовать Flow

#### Использовать Flow для:

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

// 3. Асинхронные преобразования
fun processData(input: Flow<Data>): Flow<ProcessedData> =
    input.map { processAsync(it) }

// 4. Обработка ошибок с retry
fun loadWithRetry(): Flow<Data> = flow {
    emit(fetchData())
}.retry(3) { it is IOException }
```

#### Не использовать Flow для:

```kotlin
// Одно значение - использовать suspend-функцию
suspend fun getUser(id: Int): User  // Лучше, чем Flow<User>

// Немедленные значения - использовать обычную функцию
fun calculate(x: Int): Int  // Лучше, чем Flow<Int>

// Fire-and-forget - использовать launch
viewModelScope.launch { logEvent() }  // Использовать корутину, не Flow
```

### Лучшие Практики (RU)

#### ДЕЛАЙТЕ:
```kotlin
// Используйте Flow для потоков данных
fun observeData(): Flow<Data> = callbackFlow {
    // Стримим данные из колбеков / слушателей
    // ...
    awaitClose {
        // Освободить ресурсы/отписаться от колбеков
    }
}

// Стройте цепочки операторов
flow.map { }
    .filter { }
    .distinctUntilChanged()
    .collect { }

// Обрабатывайте исключения
flow.catch { e ->
    emit(defaultValue)
}.collect { }

// Используйте flowOn для выбора диспетчеров
flow {
    emit(heavyWork())
}.flowOn(Dispatchers.Default)
```

#### НЕ ДЕЛАЙТЕ:
```kotlin
// Избегайте бесконтрольной коллекции без учёта жизненного цикла потребителя
class BadViewModel : ViewModel() {
    init {
        viewModelScope.launch {
            repository.data.collect { }
            // Такой сбор, начатый в init, будет жить всё время жизни ViewModel,
            // даже если UI больше не нуждается в данных.
        }
    }
}

// Не публикуйте MutableStateFlow наружу; экспонируйте как StateFlow
private val _state = MutableStateFlow<State>(Initial)
val state: StateFlow<State> = _state

// Избегайте Flow для простых одноразовых значений
fun getUser(): Flow<User>  // Лишнее в большинстве случаев
suspend fun getUser(): User  // Предпочтительный вариант
```

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
- Conceptually similar to a multi-subscriber `Channel`, but exposed via Flow types like `SharedFlow` and `StateFlow`.

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

## Дополнительные вопросы (RU)

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

- [Kotlin Flow Documentation](https://kotlinlang.org/docs/flow.html)
- [Kotlin Flow Guide](https://developer.android.com/kotlin/flow)
- [Flow API Reference](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-flow/)

## Связанные вопросы (RU)

### Тот же уровень (Easy)
- [[q-flow-cold-flow-fundamentals--kotlin--easy]] - Основы холодных потоков

### Следующие шаги (Medium)
- [[q-hot-cold-flows--kotlin--medium]] - Hot vs Cold Flows
- [[q-cold-vs-hot-flows--kotlin--medium]] - Объяснение Cold vs Hot Flows
- [[q-flow-vs-livedata-comparison--kotlin--medium]] - `Flow` vs `LiveData`
- [[q-channels-vs-flow--kotlin--medium]] - Каналы vs `Flow`

### Продвинутые (Harder)
- [[q-kotlin-flow-basics--kotlin--medium]] - Введение в Flow
- [[q-catch-operator-flow--kotlin--medium]] - Оператор catch в Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Операторы Flow

### Хаб
- [[q-kotlin-flow-basics--kotlin--medium]] - Комплексное введение в Flow

## Related Questions

### Same Level (Easy)
- [[q-flow-cold-flow-fundamentals--kotlin--easy]] - Cold flow fundamentals

### Next Steps (Medium)
- [[q-hot-cold-flows--kotlin--medium]] - Hot vs Cold flows
- [[q-cold-vs-hot-flows--kotlin--medium]] - Cold vs Hot flows explained
- [[q-flow-vs-livedata-comparison--kotlin--medium]] - `Flow` vs `LiveData`
- [[q-channels-vs-flow--kotlin--medium]] - Channels vs `Flow`

### Advanced (Harder)
- [[q-kotlin-flow-basics--kotlin--medium]] - Flow
- [[q-catch-operator-flow--kotlin--medium]] - Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction

## MOC Links

- [[moc-kotlin]]
