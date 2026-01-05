---
id: kotlin-103
title: "Flow Operators in Kotlin / Операторы Flow в Kotlin"
aliases: ["Flow Operators in Kotlin", "Операторы Flow в Kotlin"]

# Classification
topic: kotlin
subtopics: [combining, filtering, flow]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Created for vault completeness

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-flow, q-flow-backpressure-strategies--kotlin--hard, q-flow-operators-deep-dive--kotlin--hard, q-instant-search-flow-operators--kotlin--medium, q-stateflow-sharedflow-differences--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-11-09

tags: [combining, difficulty/medium, filtering, flow, kotlin, operators, transformation]
---
# Вопрос (RU)
> Что такое операторы `Flow` в Kotlin? Объясните категории: трансформации (`map`, `flatMap`), фильтрации (`filter`, `distinctUntilChanged`), комбинирования (`zip`, `combine`) и терминальные операторы (`collect`, `toList`). Приведите практические примеры.

---

# Question (EN)
> What are `Flow` operators in Kotlin? Explain categories: transformation (`map`, `flatMap`), filtering (`filter`, `distinctUntilChanged`), combining (`zip`, `combine`), and collection (`collect`, `toList`). Provide practical examples.

## Ответ (RU)

Операторы `Flow` — это функции-расширения, которые трансформируют, фильтруют, комбинируют или собирают потоки `Flow`. Они позволяют строить сложные реактивные конвейеры данных декларативным способом.

### Обзор Категорий Операторов

```kotlin
// Пример конвейера Flow
flow {
    emit(1)
    emit(2)
    emit(3)
}
    .map { it * 2 }           // Трансформация
    .filter { it > 2 }        // Фильтрация
    .collect { println(it) }  // Терминальный оператор
```

### 1. Операторы Трансформации

#### Map — Трансформация Каждого Элемента

```kotlin
flow {
    emit(1)
    emit(2)
    emit(3)
}.map { value ->
    value * 2
}.collect { println(it) }
// Вывод: 2, 4, 6

// Практический пример: трансформация ответа API
data class User(val id: Int, val name: String)
data class UserUI(val displayName: String, val initial: Char)

fun getUsersFlow(): Flow<User> = flow {
    emit(User(1, "Alice"))
    emit(User(2, "Bob"))
    emit(User(3, "Charlie"))
}

fun displayUsers() = runBlocking {
    getUsersFlow()
        .map { user ->
            UserUI(
                displayName = user.name,
                initial = user.name.first()
            )
        }
        .collect { userUI ->
            println("${userUI.initial}: ${userUI.displayName}")
        }
}
```

#### Transform — Гибкая Трансформация

```kotlin
flow {
    emit(1)
    emit(2)
    emit(3)
}.transform { value ->
    emit("Start: $value")
    emit("Processing: $value")
    emit("End: $value")
}.collect { println(it) }
```

#### flatMapConcat — Последовательное Выравнивание

```kotlin
flow {
    emit(1)
    emit(2)
    emit(3)
}.flatMapConcat { value ->
    flow {
        emit("$value-a")
        delay(100)
        emit("$value-b")
    }
}.collect { println(it) }
// Вывод: 1-a, 1-b, 2-a, 2-b, 3-a, 3-b (строго по порядку)
```

#### flatMapMerge — Конкурентное Выравнивание

```kotlin
flow {
    emit(1)
    emit(2)
    emit(3)
}.flatMapMerge(concurrency = 2) { value ->
    flow {
        delay(100)
        emit("Result: $value")
    }
}.collect { println(it) }
// Результаты могут приходить в любом порядке
```

#### flatMapLatest — Отмена Предыдущего При Новой Эмиссии

```kotlin
flow {
    emit("kot")
    delay(100)
    emit("kotl")
    delay(100)
    emit("kotlin")
    delay(500)
}.flatMapLatest { query ->
    flow {
        delay(200)
        emit("Результат поиска: $query")
    }
}.collect { println(it) }
// Вывод: "Результат поиска: kotlin" (завершается только последний запрос)
```

### 2. Операторы Фильтрации

#### Filter — Оставить Элементы По Условию

```kotlin
flow {
    (1..10).forEach { emit(it) }
}.filter { value ->
    value % 2 == 0  // оставить чётные числа
}.collect { println(it) }
// Вывод: 2, 4, 6, 8, 10
```

#### distinctUntilChanged — Исключить Последовательные Дубликаты

```kotlin
flow {
    emit(1)
    emit(1)
    emit(2)
    emit(2)
    emit(1)
}.distinctUntilChanged()
    .collect { println(it) }
// Вывод: 1, 2, 1

// Практический пример: избежать лишних обновлений UI
class LocationViewModel : ViewModel() {
    private val _location = MutableStateFlow<Location?>(null)

    val location: StateFlow<Location?> = _location
        .distinctUntilChanged { old, new ->
            // Считать локации одинаковыми, если они в пределах 10 метров
            if (old == null || new == null) false
            else old.distanceTo(new) < 10f
        }
        .stateIn(
            viewModelScope,
            SharingStarted.WhileSubscribed(5000),
            null
        )
}
```

#### distinctUntilChangedBy — Сравнение По Свойству

```kotlin
data class User(val id: Int, val name: String, val online: Boolean)

flow {
    emit(User(1, "Alice", true))
    emit(User(1, "Alice", true))
    emit(User(1, "Alice", false))
    emit(User(2, "Bob", true))
}.distinctUntilChangedBy { it.id }
    .collect { println(it) }
// Вывод: User(1, Alice, true), User(2, Bob, true)
```

#### Take / Drop / Debounce / Sample (кратко)

```kotlin
flow { repeat(100) { emit(it) } }
    .take(5)
    .collect { println(it) }
// 0,1,2,3,4

flow { repeat(10) { emit(it) } }
    .drop(5)
    .collect { println(it) }
// 5..9

flow {
    emit("a"); delay(100)
    emit("b"); delay(100)
    emit("c"); delay(500)
    emit("d")
}.debounce(300)
    .collect { println(it) }
// "c", "d"

flow {
    repeat(100) { emit(it); delay(50) }
}.sample(200)
    .collect { println(it) }
```

### 3. Операторы Комбинирования

#### Zip — Комбинировать Соответствующие Элементы

```kotlin
val numbers = flowOf(1, 2, 3)
val letters = flowOf("A", "B", "C", "D")

numbers.zip(letters) { num, letter ->
    "$num$letter"
}.collect { println(it) }
// Вывод: 1A, 2B, 3C (останавливается, когда завершается самый короткий поток)
```

#### Combine — Комбинировать Последние Значения

```kotlin
val numbers = flow {
    emit(1)
    delay(100)
    emit(2)
    delay(100)
    emit(3)
}

val letters = flow {
    emit("A")
    delay(150)
    emit("B")
    delay(150)
    emit("C")
}

numbers.combine(letters) { num, letter ->
    "$num$letter"
}.collect { println(it) }
```

// Практический пример: валидация формы
```kotlin
class FormViewModel : ViewModel() {
    private val _email = MutableStateFlow("")
    private val _password = MutableStateFlow("")

    val isFormValid: StateFlow<Boolean> = combine(
        _email,
        _password
    ) { email, password ->
        email.contains("@") && password.length >= 8
    }.stateIn(
        viewModelScope,
        SharingStarted.WhileSubscribed(5000),
        false
    )
}
```

#### Merge — Объединить Несколько Потоков

```kotlin
val flow1 = flow {
    emit("Flow1: A")
    delay(100)
    emit("Flow1: B")
}

val flow2 = flow {
    emit("Flow2: X")
    delay(150)
    emit("Flow2: Y")
}

merge(flow1, flow2).collect { println(it) }
```

### 4. Обработка Исключений

#### Catch — Обработка Исключений Выше По Цепочке

```kotlin
flow {
    emit(1)
    throw RuntimeException("Ошибка!")
    emit(2)
}.catch { exception ->
    println("Поймано: ${exception.message}")
    emit(-1)
}.collect { println("Получено: $it") }
```

#### Retry / retryWhen — Повтор При Ошибке

```kotlin
flow {
    emit(api.fetchData())
}.retry(3) { exception ->
    exception is IOException
}.collect { data ->
    updateUI(data)
}
```

```kotlin
flow {
    emit(api.fetchData())
}.retryWhen { cause, attempt ->
    if (cause is IOException && attempt < 3) {
        delay(1000 * (attempt + 1))
        true
    } else {
        false
    }
}.collect { data -> updateUI(data) }
```

### 5. Утилитарные Операторы

#### onEach / onStart / onCompletion

```kotlin
flow {
    emit(1)
    emit(2)
}.onStart {
    println("Старт")
    emit(0)
}.onEach { value ->
    println("Обработка: $value")
}.onCompletion { cause ->
    println(if (cause == null) "Завершено" else "С ошибкой: $cause")
}.collect()
```

### 6. Терминальные Операторы

#### Collect / toList / toSet / First / Single / Reduce / Fold

```kotlin
val list = flow {
    emit(1)
    emit(2)
    emit(3)
}.toList()

val set = flow {
    emit(1)
    emit(2)
    emit(2)
    emit(3)
}.toSet()

val first = flowOf(1, 2, 3).first()

val single = flowOf(1).single()

val sum = flowOf(1, 2, 3, 4).reduce { acc, v -> acc + v }

val folded = flowOf(1, 2, 3).fold(0) { acc, v -> acc + v }
```

### 7. Буферизация

#### Buffer — Ослабление Связки Между Продюсером И Потребителем

```kotlin
flow {
    repeat(5) {
        emit(it)
        delay(100)
    }
}.buffer(capacity = 3)
    .collect { value ->
        delay(300)
        println(value)
    }
```

#### Conflate — Оставлять Только Последние Значения

```kotlin
flow {
    repeat(10) {
        emit(it)
        delay(100)
    }
}.conflate()
    .collect { value ->
        delay(500)
        println(value)
    }
// Пропускает часть промежуточных значений, обрабатывает только актуальные
```

### Реальный Пример: Поиск С Использованием Операторов

```kotlin
class SearchViewModel(
    private val searchRepository: SearchRepository
) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")
    private val _selectedFilters = MutableStateFlow(emptySet<String>())

    val searchResults: StateFlow<SearchUiState> = combine(
        _searchQuery,
        _selectedFilters
    ) { query, filters ->
        Pair(query, filters)
    }
        .debounce(300)
        .distinctUntilChanged()
        .filter { (query, _) -> query.length >= 3 }
        .flatMapLatest { (query, filters) ->
            searchRepository.search(query, filters)
                .map { results -> SearchUiState.Success(results) as SearchUiState }
                .onStart { emit(SearchUiState.Loading) }
                .catch { exception ->
                    emit(SearchUiState.Error(exception.message ?: "Unknown error"))
                }
        }
        .stateIn(
            viewModelScope,
            SharingStarted.WhileSubscribed(5000),
            SearchUiState.Empty
        )

    fun updateQuery(query: String) {
        _searchQuery.value = query
    }

    fun toggleFilter(filter: String) {
        _selectedFilters.update { current ->
            if (filter in current) current - filter else current + filter
        }
    }
}

sealed class SearchUiState {
    object Empty : SearchUiState()
    object Loading : SearchUiState()
    data class Success(val results: List<SearchResult>) : SearchUiState()
    data class Error(val message: String) : SearchUiState()
}
```

### Лучшие Практики Построения Цепочек Операторов

```kotlin
// Хорошо: понятный, читаемый конвейер
fun processData(input: Flow<RawData>): Flow<ProcessedData> =
    input
        .filter { it.isValid() }
        .map { it.normalize() }
        .distinctUntilChanged()
        .catch { emit(ProcessedData.empty()) }

// Плохо: слишком сложная, трудная для тестирования цепочка
fun processData(input: Flow<RawData>): Flow<ProcessedData> =
    input.filter { data ->
        data.value > 0 && data.timestamp > System.currentTimeMillis() - 1000
    }.map { data ->
        ProcessedData(
            id = data.id,
            value = data.value * 2.5,
            computed = heavyComputation(data)
        )
    }.distinctUntilChanged { old, new ->
        old.id == new.id && abs(old.value - new.value) < 0.01
    }
```

### Типовые Паттерны

#### Паттерн 1: Загрузка-обновление-ошибка (Load-Refresh-Error)

```kotlin
fun loadDataWithRefresh(): Flow<DataState> = flow {
    emit(DataState.Loading)
    val data = fetchData()
    emit(DataState.Success(data))
}
    .catch { exception ->
        emit(DataState.Error(exception.message))
    }
```

#### Паттерн 2: Бесконечный Скролл (Infinite Scroll)

```kotlin
fun infiniteScroll(
    loadMore: () -> Flow<List<Item>>
): Flow<List<Item>> = flow {
    var allItems = emptyList<Item>()

    while (true) {
        val newItems = loadMore().first()
        if (newItems.isEmpty()) break

        allItems = allItems + newItems
        emit(allItems)
    }
}
```

#### Паттерн 3: Offline-first

```kotlin
fun fetchDataOfflineFirst(): Flow<Data> = flow {
    val cached = cache.getData()
    if (cached != null) emit(cached)

    try {
        val fresh = api.fetchData()
        cache.saveData(fresh)
        emit(fresh)
    } catch (e: IOException) {
        if (cached == null) throw e
    }
}
```

### Дополнительные Вопросы (RU)

- В чем ключевые отличия `Flow` от подхода в Java (Rx/Streams)?
- Когда вы бы использовали эти операторы на практике?
- Каковы распространенные ошибки и подводные камни при работе с операторами `Flow`?

### Ссылки (RU)

- [Операторы Flow — документация Kotlin](https://kotlinlang.org/docs/flow.html#flow-operators)
- [Flow API Reference](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/)
- [Kotlin Flow Guide](https://developer.android.com/kotlin/flow)
- См. также: [[c-flow]]

### Связанные Вопросы (RU)

- [[q-instant-search-flow-operators--kotlin--medium]]
- [[q-flow-operators-map-filter--kotlin--medium]]
- [[q-retry-operators-flow--kotlin--medium]]
- [[q-testing-flow-operators--kotlin--hard]]
- [[q-flow-operators-deep-dive--kotlin--hard]]
- [[q-flow-backpressure-strategies--kotlin--hard]]
- [[q-kotlin-flow-basics--kotlin--medium]]

## Answer (EN)

Flow operators are extension functions that transform, filter, combine, or collect `Flow` streams. They enable building complex reactive data pipelines in a declarative way, similar to sequence and collection operations.

### Operator Categories Overview

```kotlin
// Flow pipeline example
flow {
    emit(1)
    emit(2)
    emit(3)
}
    .map { it * 2 }           // Transform
    .filter { it > 2 }        // Filter
    .collect { println(it) }  // Terminal operator
```

### 1. Transformation Operators

#### Map — Transform Each Element

```kotlin
flow {
    emit(1)
    emit(2)
    emit(3)
}.map { value ->
    value * 2
}.collect { println(it) }
// Output: 2, 4, 6

// Practical example: Transform API response
data class User(val id: Int, val name: String)
data class UserUI(val displayName: String, val initial: Char)

fun getUsersFlow(): Flow<User> = flow {
    emit(User(1, "Alice"))
    emit(User(2, "Bob"))
    emit(User(3, "Charlie"))
}

fun displayUsers() = runBlocking {
    getUsersFlow()
        .map { user ->
            UserUI(
                displayName = user.name,
                initial = user.name.first()
            )
        }
        .collect { userUI ->
            println("${userUI.initial}: ${userUI.displayName}")
        }
}
```

#### Transform — Flexible Transformation

```kotlin
flow {
    emit(1)
    emit(2)
    emit(3)
}.transform { value ->
    emit("Start: $value")
    emit("Processing: $value")
    emit("End: $value")
}.collect { println(it) }
```

#### flatMapConcat — Sequential Flattening

```kotlin
flow {
    emit(1)
    emit(2)
    emit(3)
}.flatMapConcat { value ->
    flow {
        emit("$value-a")
        delay(100)
        emit("$value-b")
    }
}.collect { println(it) }
// Output: 1-a, 1-b, 2-a, 2-b, 3-a, 3-b (sequential)
```

#### flatMapMerge — Concurrent Flattening

```kotlin
flow {
    emit(1)
    emit(2)
    emit(3)
}.flatMapMerge(concurrency = 2) { value ->
    flow {
        delay(100)
        emit("Result: $value")
    }
}.collect { println(it) }
// Results may arrive in any order
```

#### flatMapLatest — Cancel Previous on New Emission

```kotlin
flow {
    emit("kot")
    delay(100)
    emit("kotl")
    delay(100)
    emit("kotlin")
    delay(500)
}.flatMapLatest { query ->
    flow {
        delay(200)
        emit("Search result for: $query")
    }
}.collect { println(it) }
// Output: "Search result for: kotlin" (only last completes)
```

### 2. Filtering Operators

#### Filter — Keep Elements Matching Predicate

```kotlin
flow {
    (1..10).forEach { emit(it) }
}.filter { value ->
    value % 2 == 0
}.collect { println(it) }
// Output: 2, 4, 6, 8, 10
```

#### distinctUntilChanged — Eliminate Consecutive Duplicates

```kotlin
flow {
    emit(1)
    emit(1)
    emit(2)
    emit(2)
    emit(2)
    emit(1)
}.distinctUntilChanged()
    .collect { println(it) }
// Output: 1, 2, 1

// Practical: Avoid redundant UI updates
class LocationViewModel : ViewModel() {
    private val _location = MutableStateFlow<Location?>(null)

    val location: StateFlow<Location?> = _location
        .distinctUntilChanged { old, new ->
            // Consider locations same if within 10 meters
            if (old == null || new == null) false
            else old.distanceTo(new) < 10f
        }
        .stateIn(
            viewModelScope,
            SharingStarted.WhileSubscribed(5000),
            null
        )
}
```

#### distinctUntilChangedBy — Compare by Specific Property

```kotlin
data class User(val id: Int, val name: String, val online: Boolean)

flow {
    emit(User(1, "Alice", true))
    emit(User(1, "Alice", true))   // Duplicate by id
    emit(User(1, "Alice", false))  // Different online status
    emit(User(2, "Bob", true))
}.distinctUntilChangedBy { it.id }
    .collect { println(it) }
// Emits: User(1, Alice, true), User(2, Bob, true)
```

#### Take / Drop / Debounce / Sample

```kotlin
flow { repeat(100) { emit(it) } }
    .take(5)
    .collect { println(it) }

flow { repeat(10) { emit(it) } }
    .drop(5)
    .collect { println(it) }

flow {
    emit("a"); delay(100)
    emit("b"); delay(100)
    emit("c"); delay(500)
    emit("d")
}.debounce(300)
    .collect { println(it) }

flow {
    repeat(100) { emit(it); delay(50) }
}.sample(200)
    .collect { println(it) }
```

### 3. Combining Operators

#### Zip — Combine Corresponding Elements

```kotlin
val numbers = flowOf(1, 2, 3)
val letters = flowOf("A", "B", "C", "D")

numbers.zip(letters) { num, letter ->
    "$num$letter"
}.collect { println(it) }
// Output: 1A, 2B, 3C (stops when shortest completes)
```

#### Combine — Combine Latest Values

```kotlin
val numbers = flow {
    emit(1)
    delay(100)
    emit(2)
    delay(100)
    emit(3)
}

val letters = flow {
    emit("A")
    delay(150)
    emit("B")
    delay(150)
    emit("C")
}

numbers.combine(letters) { num, letter ->
    "$num$letter"
}.collect { println(it) }
```

// Practical: Form validation
```kotlin
class FormViewModel : ViewModel() {
    private val _email = MutableStateFlow("")
    private val _password = MutableStateFlow("")

    val isFormValid: StateFlow<Boolean> = combine(
        _email,
        _password
    ) { email, password ->
        email.contains("@") && password.length >= 8
    }.stateIn(
        viewModelScope,
        SharingStarted.WhileSubscribed(5000),
        false
    )
}
```

#### Merge — Merge Multiple Flows

```kotlin
val flow1 = flow {
    emit("Flow1: A")
    delay(100)
    emit("Flow1: B")
}

val flow2 = flow {
    emit("Flow2: X")
    delay(150)
    emit("Flow2: Y")
}

merge(flow1, flow2).collect { println(it) }
```

### 4. Exception Handling Operators

#### Catch — Handle Upstream Exceptions

```kotlin
flow {
    emit(1)
    emit(2)
    throw RuntimeException("Error!")
}.catch { exception ->
    println("Caught: ${exception.message}")
    emit(-1)  // Emit fallback value
}.collect { println("Received: $it") }
```

#### Retry / retryWhen — Retry on Failure

```kotlin
var attempts = 0
flow {
    attempts++
    if (attempts < 3) throw IOException("Network error")
    emit("Success")
}.retry(3) { exception ->
    exception is IOException
}.collect { println(it) }
```

```kotlin
flow {
    emit(api.fetchData())
}.retryWhen { cause, attempt ->
    if (cause is IOException && attempt < 3) {
        delay(1000 * (attempt + 1))
        true
    } else {
        false
    }
}.collect { data -> updateUI(data) }
```

### 5. Utility Operators

#### onEach — Perform Action on Each Element

```kotlin
flow {
    emit(1)
    emit(2)
    emit(3)
}.onEach { value ->
    println("Processing: $value")
}.collect { value ->
    println("Collected: $value")
}
```

#### onStart — Execute before `Flow` Starts

```kotlin
fun loadDataWithLoading(): Flow<UiState> =
    flow {
        val data = fetchData()
        emit(UiState.Success(data))
    }
        .onStart { emit(UiState.Loading) }
        .catch { exception ->
            emit(UiState.Error(exception.message))
        }
```

#### onCompletion — Execute when `Flow` Completes

```kotlin
flow {
    emit(1)
    emit(2)
    emit(3)
}.onCompletion { exception ->
    if (exception == null) {
        println("Completed successfully")
    } else {
        println("Completed with error: $exception")
    }
}.collect { println(it) }
```

### 6. Terminal Operators

#### Collect / toList / toSet / First / Single / Reduce / Fold

```kotlin
val list = flow {
    emit(1)
    emit(2)
    emit(3)
}.toList()

val set = flow {
    emit(1)
    emit(2)
    emit(2)
    emit(3)
}.toSet()

val first = flowOf(1, 2, 3).first()

val single = flowOf(1).single()

val sum = flowOf(1, 2, 3, 4).reduce { acc, v -> acc + v }

val folded = flowOf(1, 2, 3).fold(0) { acc, v -> acc + v }
```

### 7. Buffering Operators

#### Buffer — Allow Concurrent Production and Consumption

```kotlin
flow {
    repeat(5) {
        emit(it)
        delay(100)
    }
}.buffer(capacity = 3)
    .collect { value ->
        delay(300)
        println(value)
    }
```

#### Conflate — Keep Only Latest

```kotlin
flow {
    repeat(10) {
        emit(it)
        delay(100)
    }
}.conflate()
    .collect { value ->
        delay(500)
        println(value)
    }
// Skips intermediate values, processes only latest
```

### Real-World Example: Search with Operators

```kotlin
class SearchViewModel(
    private val searchRepository: SearchRepository
) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")
    private val _selectedFilters = MutableStateFlow(emptySet<String>())

    val searchResults: StateFlow<SearchUiState> = combine(
        _searchQuery,
        _selectedFilters
    ) { query, filters ->
        Pair(query, filters)
    }
        .debounce(300)
        .distinctUntilChanged()
        .filter { (query, _) -> query.length >= 3 }
        .flatMapLatest { (query, filters) ->
            searchRepository.search(query, filters)
                .map { results -> SearchUiState.Success(results) as SearchUiState }
                .onStart { emit(SearchUiState.Loading) }
                .catch { exception ->
                    emit(SearchUiState.Error(exception.message ?: "Unknown error"))
                }
        }
        .stateIn(
            viewModelScope,
            SharingStarted.WhileSubscribed(5000),
            SearchUiState.Empty
        )

    fun updateQuery(query: String) {
        _searchQuery.value = query
    }

    fun toggleFilter(filter: String) {
        _selectedFilters.update { current ->
            if (filter in current) current - filter else current + filter
        }
    }
}

sealed class SearchUiState {
    object Empty : SearchUiState()
    object Loading : SearchUiState()
    data class Success(val results: List<SearchResult>) : SearchUiState()
    data class Error(val message: String) : SearchUiState()
}
```

### Operator Chaining Best Practices

```kotlin
// Good: Clear, readable pipeline
fun processData(input: Flow<RawData>): Flow<ProcessedData> =
    input
        .filter { it.isValid() }
        .map { it.normalize() }
        .distinctUntilChanged()
        .catch { emit(ProcessedData.empty()) }

// Bad: Too complex, hard to test
fun processData(input: Flow<RawData>): Flow<ProcessedData> =
    input.filter { data ->
        data.value > 0 && data.timestamp > System.currentTimeMillis() - 1000
    }.map { data ->
        ProcessedData(
            id = data.id,
            value = data.value * 2.5,
            computed = heavyComputation(data)
        )
    }.distinctUntilChanged { old, new ->
        old.id == new.id && abs(old.value - new.value) < 0.01
    }
```

### Common Patterns

#### Pattern 1: Load-Refresh-Error

```kotlin
fun loadDataWithRefresh(): Flow<DataState> = flow {
    emit(DataState.Loading)
    val data = fetchData()
    emit(DataState.Success(data))
}
    .catch { exception ->
        emit(DataState.Error(exception.message))
    }
```

#### Pattern 2: Infinite Scroll

```kotlin
fun infiniteScroll(
    loadMore: () -> Flow<List<Item>>
): Flow<List<Item>> = flow {
    var allItems = emptyList<Item>()

    while (true) {
        val newItems = loadMore().first()
        if (newItems.isEmpty()) break

        allItems = allItems + newItems
        emit(allItems)
    }
}
```

#### Pattern 3: Offline-First

```kotlin
fun fetchDataOfflineFirst(): Flow<Data> = flow {
    val cached = cache.getData()
    if (cached != null) emit(cached)

    try {
        val fresh = api.fetchData()
        cache.saveData(fresh)
        emit(fresh)
    } catch (e: IOException) {
        if (cached == null) throw e
    }
}
```

## Follow-ups

- What are the key differences between `Flow` and Java (Rx/Streams)?
- When would you use these operators in practice?
- What are common pitfalls to avoid when chaining `Flow` operators?

## References
- [Flow Operators - Kotlin Documentation](https://kotlinlang.org/docs/flow.html#flow-operators)
- [Flow API Reference](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/)
- [Kotlin Flow Guide](https://developer.android.com/kotlin/flow)
- See also: [[c-flow]]

## Related Questions

- [[q-instant-search-flow-operators--kotlin--medium]]
- [[q-flow-operators-map-filter--kotlin--medium]]
- [[q-retry-operators-flow--kotlin--medium]]
- [[q-testing-flow-operators--kotlin--hard]]
- [[q-flow-operators-deep-dive--kotlin--hard]]
- [[q-flow-backpressure-strategies--kotlin--hard]]
- [[q-kotlin-flow-basics--kotlin--medium]]
