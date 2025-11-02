---
id: kotlin-103
title: "Flow Operators in Kotlin / Операторы Flow в Kotlin"
aliases: []

# Classification
topic: kotlin
subtopics: [combining, filtering, flow, operators, transformation]
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
related: [q-flow-backpressure-strategies--kotlin--hard, q-flow-operators-deep-dive--kotlin--hard, q-instant-search-flow-operators--kotlin--medium, q-stateflow-sharedflow-differences--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [combining, difficulty/medium, filtering, flow, kotlin, operators, transformation]
date created: Sunday, October 12th 2025, 2:10:07 pm
date modified: Saturday, November 1st 2025, 5:43:26 pm
---

# Question (EN)
> What are Flow operators in Kotlin? Explain categories: transformation (map, flatMap), filtering (filter, distinctUntilChanged), combining (zip, combine), and collection (collect, toList). Provide practical examples.

# Вопрос (RU)
> Что такое операторы Flow в Kotlin? Объясните категории: трансформация (map, flatMap), фильтрация (filter, distinctUntilChanged), комбинирование (zip, combine) и коллекция (collect, toList). Приведите практические примеры.

---

## Answer (EN)

Flow operators are extension functions that transform, filter, combine, or collect Flow streams. They enable building complex reactive data pipelines in a declarative way, similar to sequence and collection operations.

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

#### Map - Transform Each Element

```kotlin
// Basic map
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
    // Simulate API call
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

#### Transform - Flexible Transformation

Can emit multiple values or skip values:

```kotlin
flow {
    emit(1)
    emit(2)
    emit(3)
}.transform { value ->
    emit("Start: $value")      // Emit multiple times
    emit("Processing: $value")
    emit("End: $value")
}.collect { println(it) }

// Practical: Add loading states
fun loadDataWithStates(): Flow<DataState> = flow {
    emit(DataState.Loading)
    val data = fetchData()
    emit(DataState.Success(data))
}.transform { state ->
    emit(state)
    if (state is DataState.Success) {
        emit(DataState.Complete)  // Add completion state
    }
}
```

#### flatMapConcat - Sequential Flattening

```kotlin
// Basic example
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

// Practical: Sequential API calls
fun fetchUserDetails(userId: Int): Flow<UserDetail> = flow {
    delay(100)
    emit(UserDetail(userId, "Detail for user $userId"))
}

fun fetchAllUserDetails(userIds: List<Int>): Flow<UserDetail> =
    userIds.asFlow()
        .flatMapConcat { userId ->
            fetchUserDetails(userId)
        }
```

#### flatMapMerge - Concurrent Flattening

```kotlin
// Processes multiple flows concurrently
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

// Practical: Parallel network requests
fun fetchUserData(userId: Int): Flow<UserData> = flow {
    delay((50..150).random().toLong())
    emit(UserData(userId, "Data for $userId"))
}

fun fetchMultipleUsers(userIds: List<Int>): Flow<UserData> =
    userIds.asFlow()
        .flatMapMerge(concurrency = 5) { userId ->
            fetchUserData(userId)
        }
```

#### flatMapLatest - Cancel Previous on New Emission

```kotlin
// Cancels previous inner flow when new value emitted
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

// Practical: Search with autocomplete
@Composable
fun SearchScreen(viewModel: SearchViewModel) {
    var query by remember { mutableStateOf("") }

    val searchResults by viewModel.searchFlow(query)
        .flatMapLatest { q ->
            if (q.length >= 3) {
                searchRepository.search(q)
            } else {
                flowOf(emptyList())
            }
        }
        .collectAsState(initial = emptyList())

    SearchBar(query = query, onQueryChange = { query = it })
    ResultsList(results = searchResults)
}
```

### 2. Filtering Operators

#### Filter - Keep Elements Matching Predicate

```kotlin
flow {
    (1..10).forEach { emit(it) }
}.filter { value ->
    value % 2 == 0  // Keep even numbers
}.collect { println(it) }
// Output: 2, 4, 6, 8, 10

// Practical: Filter valid data
data class FormInput(val email: String, val age: Int)

fun validateInputs(inputs: Flow<FormInput>): Flow<FormInput> =
    inputs.filter { input ->
        input.email.contains("@") && input.age >= 18
    }
```

#### distinctUntilChanged - Eliminate Consecutive Duplicates

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
            old?.distanceTo(new) ?: Float.MAX_VALUE < 10f
        }
        .stateIn(
            viewModelScope,
            SharingStarted.WhileSubscribed(5000),
            null
        )
}
```

#### distinctUntilChangedBy - Compare by Specific Property

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

#### Take - Take First N Elements

```kotlin
flow {
    repeat(100) { emit(it) }
}.take(5)
    .collect { println(it) }
// Output: 0, 1, 2, 3, 4

// Practical: Limit results
fun searchWithLimit(query: String): Flow<SearchResult> =
    searchRepository.search(query)
        .take(10)  // Maximum 10 results
```

#### Drop - Skip First N Elements

```kotlin
flow {
    repeat(10) { emit(it) }
}.drop(5)
    .collect { println(it) }
// Output: 5, 6, 7, 8, 9

// Practical: Pagination
fun loadPage(pageNumber: Int, pageSize: Int): Flow<Item> =
    allItemsFlow()
        .drop(pageNumber * pageSize)
        .take(pageSize)
```

#### Debounce - Emit only after Quiet Period

```kotlin
flow {
    emit("a")
    delay(100)
    emit("b")
    delay(100)
    emit("c")
    delay(500)  // Quiet period
    emit("d")
}.debounce(300)
    .collect { println(it) }
// Output: "c", "d"

// Practical: Search input debouncing
class SearchViewModel : ViewModel() {
    private val _searchQuery = MutableStateFlow("")

    val searchResults: StateFlow<List<Result>> = _searchQuery
        .debounce(300)  // Wait 300ms after user stops typing
        .filter { it.length >= 3 }
        .flatMapLatest { query ->
            searchRepository.search(query)
        }
        .stateIn(
            viewModelScope,
            SharingStarted.WhileSubscribed(5000),
            emptyList()
        )

    fun updateQuery(query: String) {
        _searchQuery.value = query
    }
}
```

#### Sample - Emit at Fixed Intervals

```kotlin
flow {
    repeat(100) {
        emit(it)
        delay(50)
    }
}.sample(200)  // Sample every 200ms
    .collect { println(it) }
// Emits approximately every 200ms

// Practical: Throttle sensor data
fun sampleSensorData(): Flow<SensorReading> =
    sensorFlow()
        .sample(100)  // Maximum 10 readings per second
```

### 3. Combining Operators

#### Zip - Combine Corresponding Elements

```kotlin
val numbers = flowOf(1, 2, 3)
val letters = flowOf("A", "B", "C", "D")

numbers.zip(letters) { num, letter ->
    "$num$letter"
}.collect { println(it) }
// Output: 1A, 2B, 3C (stops when shortest completes)

// Practical: Combine multiple API calls
suspend fun loadUserProfile(userId: Int) {
    val userFlow = fetchUser(userId)
    val postsFlow = fetchUserPosts(userId)
    val followersFlow = fetchFollowers(userId)

    userFlow.zip(postsFlow) { user, posts ->
        Pair(user, posts)
    }.zip(followersFlow) { (user, posts), followers ->
        UserProfile(user, posts, followers)
    }.collect { profile ->
        updateUI(profile)
    }
}
```

#### Combine - Combine Latest Values

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
// Output: 1A, 2A, 2B, 3B, 3C (all combinations)

// Practical: Form validation
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

#### Merge - Merge Multiple Flows

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
// Output: Flow1: A, Flow2: X, Flow1: B, Flow2: Y

// Practical: Multiple data sources
fun observeAllNotifications(): Flow<Notification> = merge(
    pushNotificationFlow(),
    localNotificationFlow(),
    systemNotificationFlow()
)
```

### 4. Exception Handling Operators

#### Catch - Handle upstream Exceptions

```kotlin
flow {
    emit(1)
    emit(2)
    throw RuntimeException("Error!")
    emit(3)
}.catch { exception ->
    println("Caught: ${exception.message}")
    emit(-1)  // Emit fallback value
}.collect { println("Received: $it") }
// Output: Received: 1, Received: 2, Caught: Error!, Received: -1

// Practical: API error handling
fun fetchDataSafely(): Flow<Data> =
    flow {
        val result = api.fetchData()
        emit(result)
    }.catch { exception ->
        when (exception) {
            is IOException -> {
                // Network error - emit cached data
                emit(cache.getData())
            }
            is HttpException -> {
                // HTTP error - emit error state
                emit(Data.Error(exception.code()))
            }
            else -> throw exception
        }
    }
```

#### Retry - Retry on Failure

```kotlin
var attempts = 0
flow {
    attempts++
    println("Attempt $attempts")
    if (attempts < 3) {
        throw IOException("Network error")
    }
    emit("Success")
}.retry(3) { exception ->
    exception is IOException
}.collect { println(it) }
// Retries 3 times on IOException

// Practical: Retry with exponential backoff
fun fetchWithRetry(): Flow<Data> = flow {
    val result = api.fetchData()
    emit(result)
}.retry(3) { exception ->
    if (exception is IOException) {
        delay(1000)  // Wait before retry
        true
    } else {
        false
    }
}
```

#### retryWhen - Custom Retry Logic

```kotlin
flow {
    emit(api.fetchData())
}.retryWhen { cause, attempt ->
    if (cause is IOException && attempt < 3) {
        delay(1000 * (attempt + 1))  // Exponential backoff
        true
    } else {
        false
    }
}.collect { data ->
    updateUI(data)
}
```

### 5. Utility Operators

#### onEach - Perform Action on Each Element

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

// Practical: Logging
fun fetchDataWithLogging(): Flow<Data> =
    flow { emit(api.fetchData()) }
        .onEach { data ->
            logger.log("Received data: $data")
        }
```

#### onStart - Execute before Flow Starts

```kotlin
flow {
    emit(1)
    emit(2)
}.onStart {
    println("Starting flow")
    emit(0)  // Can emit initial value
}.collect { println(it) }
// Output: Starting flow, 0, 1, 2

// Practical: Show loading state
fun loadDataWithLoading(): Flow<UiState> =
    flow {
        val data = fetchData()
        emit(UiState.Success(data))
    }
    .onStart {
        emit(UiState.Loading)
    }
    .catch { exception ->
        emit(UiState.Error(exception.message))
    }
```

#### onCompletion - Execute when Flow Completes

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

// Practical: Hide loading indicator
fun loadDataWithLoadingState(): Flow<Data> =
    dataSource.fetchData()
        .onStart { showLoading() }
        .onCompletion { hideLoading() }
```

### 6. Terminal Operators

#### Collect - Consume Flow

```kotlin
flow {
    emit(1)
    emit(2)
    emit(3)
}.collect { value ->
    println(value)
}
```

#### toList - Collect to List

```kotlin
val list = flow {
    emit(1)
    emit(2)
    emit(3)
}.toList()

println(list)  // [1, 2, 3]
```

#### toSet - Collect to Set

```kotlin
val set = flow {
    emit(1)
    emit(2)
    emit(2)
    emit(3)
}.toSet()

println(set)  // [1, 2, 3]
```

#### First - Get First Element

```kotlin
val first = flow {
    emit(1)
    emit(2)
    emit(3)
}.first()

println(first)  // 1

// With predicate
val firstEven = flow {
    emit(1)
    emit(2)
    emit(3)
    emit(4)
}.first { it % 2 == 0 }

println(firstEven)  // 2
```

#### Single - Ensure Single Element

```kotlin
try {
    val single = flow {
        emit(1)
    }.single()
    println(single)  // 1
} catch (e: IllegalStateException) {
    // Throws if more than one element
}
```

#### Reduce - Accumulate Values

```kotlin
val sum = flow {
    emit(1)
    emit(2)
    emit(3)
    emit(4)
}.reduce { accumulator, value ->
    accumulator + value
}

println(sum)  // 10

// Practical: Calculate total
suspend fun calculateTotal(items: Flow<CartItem>): Double =
    items.reduce { total, item ->
        total + (item.price * item.quantity)
    }
```

#### Fold - Accumulate with Initial Value

```kotlin
val sum = flow {
    emit(1)
    emit(2)
    emit(3)
}.fold(0) { accumulator, value ->
    accumulator + value
}

println(sum)  // 6

// Practical: Build complex object
suspend fun buildReport(events: Flow<Event>): Report =
    events.fold(Report.empty()) { report, event ->
        report.addEvent(event)
    }
```

### 7. Buffering Operators

#### Buffer - Allow Concurrent Collection

```kotlin
flow {
    repeat(5) {
        emit(it)
        delay(100)  // Slow producer
    }
}.buffer(capacity = 3)
    .collect { value ->
        delay(300)  // Slow collector
        println(value)
    }
// Buffer allows producer to continue while collector processes
```

#### Conflate - Keep only Latest

```kotlin
flow {
    repeat(10) {
        emit(it)
        delay(100)
    }
}.conflate()
    .collect { value ->
        delay(500)  // Very slow collector
        println(value)
    }
// Skips intermediate values, processes only latest
```

### Real-World Example: Search with All Operators

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
        .debounce(300)  // Wait for user to stop typing
        .distinctUntilChanged()  // Avoid duplicate searches
        .filter { (query, _) -> query.length >= 3 }  // Minimum 3 chars
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
            if (filter in current) current - filter
            else current + filter
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
//  Good: Clear, readable pipeline
fun processData(input: Flow<RawData>): Flow<ProcessedData> =
    input
        .filter { it.isValid() }
        .map { it.normalize() }
        .distinctUntilChanged()
        .catch { emit(ProcessedData.empty()) }

//  Bad: Too complex, hard to test
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
    .onCompletion { exception ->
        if (exception == null) {
            delay(30000)  // Refresh after 30 seconds
            // Can trigger refresh
        }
    }
```

#### Pattern 2: Infinite Scroll

```kotlin
fun infiniteScroll(
    loadMore: () -> Flow<List<Item>>
): Flow<List<Item>> = flow {
    var allItems = emptyList<Item>()
    var page = 0

    while (true) {
        val newItems = loadMore().first()
        if (newItems.isEmpty()) break

        allItems = allItems + newItems
        emit(allItems)
        page++
    }
}
```

#### Pattern 3: Offline-First

```kotlin
fun fetchDataOfflineFirst(): Flow<Data> = flow {
    // Emit cached data first
    val cached = cache.getData()
    if (cached != null) {
        emit(cached)
    }

    // Then fetch from network
    try {
        val fresh = api.fetchData()
        cache.saveData(fresh)
        emit(fresh)
    } catch (e: IOException) {
        if (cached == null) throw e
    }
}
```

---

## Ответ (RU)

Операторы Flow - это функции расширения, которые трансформируют, фильтруют, комбинируют или собирают потоки Flow. Они позволяют строить сложные реактивные конвейеры данных декларативным способом.

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

#### Map - Трансформация Каждого Элемента

```kotlin
flow {
    emit(1)
    emit(2)
    emit(3)
}.map { value ->
    value * 2
}.collect { println(it) }
// Вывод: 2, 4, 6

// Практический пример: Трансформация ответа API
data class User(val id: Int, val name: String)
data class UserUI(val displayName: String, val initial: Char)

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

#### flatMapConcat - Последовательное Выравнивание

```kotlin
// Базовый пример
flow {
    emit(1)
    emit(2)
}.flatMapConcat { value ->
    flow {
        emit("$value-a")
        emit("$value-b")
    }
}.collect { println(it) }
// Вывод: 1-a, 1-b, 2-a, 2-b (последовательно)
```

#### flatMapLatest - Отмена Предыдущего При Новой Эмиссии

```kotlin
// Практический пример: Поиск с автодополнением
flow {
    emit("kot")
    delay(100)
    emit("kotlin")
    delay(500)
}.flatMapLatest { query ->
    flow {
        delay(200)
        emit("Результат поиска: $query")
    }
}.collect { println(it) }
// Вывод: "Результат поиска: kotlin" (только последний завершается)
```

### 2. Операторы Фильтрации

#### Filter - Оставить Элементы По Условию

```kotlin
flow {
    (1..10).forEach { emit(it) }
}.filter { value ->
    value % 2 == 0  // Оставить четные числа
}.collect { println(it) }
// Вывод: 2, 4, 6, 8, 10
```

#### distinctUntilChanged - Исключить Последовательные Дубликаты

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

// Практический пример: Избежать избыточных обновлений UI
class LocationViewModel : ViewModel() {
    val location: StateFlow<Location?> = _location
        .distinctUntilChanged { old, new ->
            // Считать локации одинаковыми если в пределах 10 метров
            old?.distanceTo(new) ?: Float.MAX_VALUE < 10f
        }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), null)
}
```

#### Debounce - Эмиссия Только После Периода Тишины

```kotlin
// Практический пример: Debouncing ввода поиска
class SearchViewModel : ViewModel() {
    private val _searchQuery = MutableStateFlow("")

    val searchResults: StateFlow<List<Result>> = _searchQuery
        .debounce(300)  // Ждать 300мс после того как пользователь перестал печатать
        .filter { it.length >= 3 }
        .flatMapLatest { query ->
            searchRepository.search(query)
        }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())
}
```

### 3. Операторы Комбинирования

#### Zip - Комбинировать Соответствующие Элементы

```kotlin
val numbers = flowOf(1, 2, 3)
val letters = flowOf("A", "B", "C")

numbers.zip(letters) { num, letter ->
    "$num$letter"
}.collect { println(it) }
// Вывод: 1A, 2B, 3C
```

#### Combine - Комбинировать Последние Значения

```kotlin
// Практический пример: Валидация формы
class FormViewModel : ViewModel() {
    private val _email = MutableStateFlow("")
    private val _password = MutableStateFlow("")

    val isFormValid: StateFlow<Boolean> = combine(
        _email,
        _password
    ) { email, password ->
        email.contains("@") && password.length >= 8
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), false)
}
```

### 4. Обработка Исключений

#### Catch - Обработка Исключений

```kotlin
flow {
    emit(1)
    throw RuntimeException("Ошибка!")
    emit(2)
}.catch { exception ->
    println("Поймано: ${exception.message}")
    emit(-1)  // Эмиссия резервного значения
}.collect { println("Получено: $it") }

// Практический пример: Обработка ошибок API
fun fetchDataSafely(): Flow<Data> =
    flow {
        val result = api.fetchData()
        emit(result)
    }.catch { exception ->
        when (exception) {
            is IOException -> emit(cache.getData())
            else -> throw exception
        }
    }
```

#### Retry - Повтор При Ошибке

```kotlin
flow {
    emit(api.fetchData())
}.retry(3) { exception ->
    exception is IOException
}.collect { data ->
    updateUI(data)
}
```

### 5. Утилитарные Операторы

#### onEach - Выполнить Действие На Каждом Элементе

```kotlin
flow {
    emit(1)
    emit(2)
}.onEach { value ->
    println("Обработка: $value")
}.collect { value ->
    println("Собрано: $value")
}
```

#### onStart - Выполнить Перед Началом Потока

```kotlin
// Практический пример: Показать состояние загрузки
fun loadDataWithLoading(): Flow<UiState> =
    flow {
        val data = fetchData()
        emit(UiState.Success(data))
    }
    .onStart {
        emit(UiState.Loading)
    }
```

### 6. Терминальные Операторы

#### Collect - Потребление Потока

```kotlin
flow {
    emit(1)
    emit(2)
}.collect { value ->
    println(value)
}
```

#### toList - Собрать В Список

```kotlin
val list = flow {
    emit(1)
    emit(2)
    emit(3)
}.toList()

println(list)  // [1, 2, 3]
```

#### First - Получить Первый Элемент

```kotlin
val first = flow {
    emit(1)
    emit(2)
}.first()

println(first)  // 1
```

### Реальный Пример: Поиск Со Всеми Операторами

```kotlin
class SearchViewModel(
    private val searchRepository: SearchRepository
) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")

    val searchResults: StateFlow<SearchUiState> = _searchQuery
        .debounce(300)  // Ждать остановки печати
        .distinctUntilChanged()  // Избежать дубликатов
        .filter { it.length >= 3 }  // Минимум 3 символа
        .flatMapLatest { query ->
            searchRepository.search(query)
                .map { results -> SearchUiState.Success(results) as SearchUiState }
                .onStart { emit(SearchUiState.Loading) }
                .catch { exception ->
                    emit(SearchUiState.Error(exception.message ?: "Неизвестная ошибка"))
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
}
```

### Лучшие Практики

```kotlin
//  Хорошо: Ясный, читаемый конвейер
fun processData(input: Flow<RawData>): Flow<ProcessedData> =
    input
        .filter { it.isValid() }
        .map { it.normalize() }
        .distinctUntilChanged()
        .catch { emit(ProcessedData.empty()) }

//  Плохо: Слишком сложно, трудно тестировать
fun processData(input: Flow<RawData>): Flow<ProcessedData> =
    input.filter { data ->
        data.value > 0 && data.timestamp > System.currentTimeMillis() - 1000
    }.map { /* сложная логика */ }
```

---

## Related Questions

### Related (Medium)
- [[q-instant-search-flow-operators--kotlin--medium]] - Flow
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-retry-operators-flow--kotlin--medium]] - Flow
-  - Flow

### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-operators-deep-dive--kotlin--hard]] - Flow
- [[q-flow-backpressure-strategies--kotlin--hard]] - Flow

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction

## References
- [Flow Operators - Kotlin Documentation](https://kotlinlang.org/docs/flow.html#flow-operators)
- [Flow API Reference](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/)
- [Kotlin Flow Guide](https://developer.android.com/kotlin/flow)
