---
id: 20251012-144928
title: "Catch Operator in Kotlin Flow / Оператор catch в Kotlin Flow"
aliases: []

# Classification
topic: kotlin
subtopics: [flow, catch, exception-handling, error-handling, coroutines]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Deep dive into catch operator in Kotlin Flow

# Workflow & relations
status: draft
moc: moc-kotlin
related: [q-flow-exception-handling--kotlin--medium, q-flow-basics--kotlin--easy, q-retry-operators-flow--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-10-12

tags: [kotlin, flow, catch, exception-handling, error-handling, coroutines, difficulty/medium]
---

# Question (EN)
> How does the catch operator work in Kotlin Flow? What is exception transparency and where should catch be placed?

# Вопрос (RU)
> Как работает оператор catch в Kotlin Flow? Что такое прозрачность исключений и где размещать catch?

---

## Answer (EN)

The `catch` operator in Kotlin Flow is a declarative way to handle exceptions that occur upstream in the flow. It implements the principle of **exception transparency**, meaning exceptions flow downstream just like regular values.

### Basic Catch Usage

```kotlin
flow {
    emit(1)
    emit(2)
    throw RuntimeException("Error!")
    emit(3)  // Never reached
}.catch { exception ->
    println("Caught: ${exception.message}")
    emit(-1)  // Emit recovery value
}.collect { value ->
    println("Collected: $value")
}

// Output:
// Collected: 1
// Collected: 2
// Caught: Error!
// Collected: -1
```

### Exception Transparency

Exception transparency is a key principle: exceptions are treated like data and flow downstream:

```kotlin
// Without catch: exception propagates to collector
flow {
    emit(1)
    throw RuntimeException("Error")
}.collect { value ->  // Exception thrown here
    println(value)
}

// With catch: exception caught and handled
flow {
    emit(1)
    throw RuntimeException("Error")
}.catch { e ->
    println("Handled: ${e.message}")
}.collect { value ->
    println(value)
}
```

### Catch Only Catches Upstream Exceptions

This is crucial: `catch` only catches exceptions from upstream operators, NOT from downstream:

```kotlin
// Catch DOES catch this (upstream)
flow {
    throw RuntimeException("Upstream error")
}.catch { e ->
    println("Caught: ${e.message}")  //  Catches this
}.collect { value ->
    println(value)
}

// Catch DOES NOT catch this (downstream)
flow {
    emit(1)
}.catch { e ->
    println("Caught: ${e.message}")  //  Does NOT catch this
}.collect { value ->
    throw RuntimeException("Downstream error")  // Propagates to caller
}
```

### Where to Place Catch

```kotlin
class UserRepository {
    fun getUsers(): Flow<List<User>> = flow {
        val users = api.fetchUsers()  // May throw
        emit(users)
    }.catch { e ->
        // Catch network/API errors
        logger.error("Failed to fetch users", e)
        emit(emptyList())  // Emit empty list as fallback
    }
}

// In ViewModel
class UserViewModel : ViewModel() {
    val users: StateFlow<Result<List<User>>> = repository.getUsers()
        .map { users -> Result.Success(users) }
        .catch { e ->
            // Catch mapping errors
            emit(Result.Error(e.message ?: "Unknown error"))
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = Result.Loading
        )
}
```

### Catch and Emit

You can emit recovery values in catch block:

```kotlin
fun loadData(): Flow<Data> = flow {
    val data = fetchDataFromNetwork()
    emit(data)
}.catch { exception ->
    when (exception) {
        is IOException -> {
            // Network error: emit cached data
            val cached = loadFromCache()
            if (cached != null) {
                emit(cached)
            } else {
                throw exception  // Re-throw if no cache
            }
        }
        is HttpException -> {
            // Server error: emit default data
            emit(Data.default())
        }
        else -> throw exception  // Re-throw unknown exceptions
    }
}
```

### Catch vs Try-Catch

```kotlin
// Try-catch in flow builder (imperative)
flow {
    try {
        val data = api.fetchData()
        emit(data)
    } catch (e: Exception) {
        emit(Data.default())
    }
}

// Catch operator (declarative, preferred)
flow {
    val data = api.fetchData()
    emit(data)
}.catch { e ->
    emit(Data.default())
}
```

**Differences**:
1. **Scope**: try-catch is local, catch operator affects entire upstream chain
2. **Composability**: catch operator can be composed with other operators
3. **Clarity**: catch operator makes error handling explicit in flow pipeline
4. **Exception transparency**: catch operator follows Flow's exception transparency principle

### Multiple Catch Operators

```kotlin
flow {
    emit(fetchFromNetwork())
}.catch { e ->
    // Catch network errors
    logger.warn("Network error, trying cache", e)
    emit(loadFromCache())
}.map { data ->
    processData(data)  // May throw
}.catch { e ->
    // Catch processing errors
    logger.error("Processing error", e)
    emit(Data.default())
}.collect { data ->
    updateUI(data)
}
```

### Catch with Flow Operators

```kotlin
fun searchUsers(query: String): Flow<List<User>> = flow {
    emit(api.search(query))
}.retry(3) { exception ->
    // Retry network errors
    exception is IOException
}.catch { exception ->
    // After retries failed, handle error
    when (exception) {
        is IOException -> emit(emptyList())
        is HttpException -> {
            if (exception.code() == 404) {
                emit(emptyList())
            } else {
                throw exception
            }
        }
        else -> throw exception
    }
}
```

### Real-World Example: ViewModel

```kotlin
class ProductViewModel : ViewModel() {
    private val _products = MutableStateFlow<UiState<List<Product>>>(UiState.Loading)
    val products: StateFlow<UiState<List<Product>>> = _products

    fun loadProducts() {
        viewModelScope.launch {
            repository.getProducts()
                .onStart {
                    _products.value = UiState.Loading
                }
                .map { products ->
                    UiState.Success(products) as UiState<List<Product>>
                }
                .catch { exception ->
                    _products.value = UiState.Error(
                        exception.message ?: "Unknown error"
                    )
                }
                .collect { state ->
                    _products.value = state
                }
        }
    }
}

sealed class UiState<out T> {
    object Loading : UiState<Nothing>()
    data class Success<T>(val data: T) : UiState<T>()
    data class Error(val message: String) : UiState<Nothing>()
}
```

### Catch with StateFlow/SharedFlow

```kotlin
class DataRepository {
    private val _data = MutableStateFlow<Result<Data>>(Result.Loading)
    val data: StateFlow<Result<Data>> = _data

    fun startMonitoring() {
        dataSource.observe()
            .map { data -> Result.Success(data) as Result<Data> }
            .catch { e ->
                emit(Result.Error(e.message ?: "Error"))
            }
            .onEach { result ->
                _data.value = result
            }
            .launchIn(coroutineScope)
    }
}
```

### Catch and Re-throw

```kotlin
fun loadUser(id: Int): Flow<User> = flow {
    emit(api.getUser(id))
}.catch { exception ->
    logger.error("Failed to load user $id", exception)

    when (exception) {
        is IOException -> {
            // Try cache, then re-throw if not found
            val cached = cache.getUser(id)
            if (cached != null) {
                emit(cached)
            } else {
                throw exception
            }
        }
        is AuthException -> {
            // Don't handle auth errors here
            throw exception
        }
        else -> {
            // Wrap unknown errors
            throw DataException("Failed to load user", exception)
        }
    }
}
```

### Catch Nullability

```kotlin
// Catch can emit null if flow type is nullable
fun loadData(): Flow<Data?> = flow {
    emit(api.fetchData())
}.catch { e ->
    logger.error("Failed to load data", e)
    emit(null)  // OK: Flow<Data?> allows null
}

// Cannot emit null for non-nullable flow
fun loadData(): Flow<Data> = flow {
    emit(api.fetchData())
}.catch { e ->
    // emit(null)  // Error: Type mismatch
    emit(Data.default())  // Must emit Data
}
```

### Best Practices

#### DO:
```kotlin
// Use catch for upstream errors
flow {
    emit(fetchData())
}.catch { e ->
    emit(defaultData())
}.collect { data ->
    process(data)
}

// Place catch after operations that may throw
flow {
    emit(1)
}.map { value ->
    riskyOperation(value)
}.catch { e ->
    emit(fallbackValue())
}

// Use specific exception types
.catch { exception ->
    when (exception) {
        is IOException -> handleNetworkError()
        is HttpException -> handleServerError()
        else -> throw exception
    }
}

// Log errors in catch
.catch { exception ->
    logger.error("Operation failed", exception)
    emit(fallback())
}

// Combine catch with retry
flow {
    emit(fetchData())
}.retry(3) { it is IOException }
.catch { e ->
    emit(cachedData())
}
```

#### DON'T:
```kotlin
// Don't use catch for downstream errors
flow {
    emit(1)
}.catch { e ->
    // Won't catch errors in collect!
}.collect { value ->
    throw Exception()  // Not caught
}

// Don't catch without handling
.catch { e ->
    // Do something!
}

// Don't swallow exceptions silently
.catch { e ->
    // Silent failure - bad practice
}

// Don't use when try-catch in builder is clearer
flow {
    // Complex logic with multiple try-catch
    // might be clearer than multiple catch operators
}
```

### Common Patterns

#### Fallback Chain

```kotlin
fun loadUser(id: Int): Flow<User> = flow {
    // Try network
    emit(api.getUser(id))
}.catch { e1 ->
    logger.warn("Network failed, trying cache", e1)
    flow {
        // Try cache
        val cached = cache.getUser(id)
        if (cached != null) {
            emit(cached)
        } else {
            throw CacheException("Not in cache")
        }
    }.catch { e2 ->
        // Try default
        logger.error("Cache failed, using default", e2)
        emit(User.default())
    }.collect { user ->
        emit(user)
    }
}
```

#### Error Transformation

```kotlin
fun loadProducts(): Flow<Result<List<Product>>> = flow {
    emit(api.getProducts())
}.map { products ->
    Result.Success(products)
}.catch { exception ->
    val errorResult = when (exception) {
        is IOException -> Result.Error.Network(exception.message)
        is HttpException -> Result.Error.Server(exception.code())
        else -> Result.Error.Unknown(exception.message)
    }
    emit(errorResult)
}
```

#### Conditional Recovery

```kotlin
fun fetchData(useCache: Boolean): Flow<Data> = flow {
    emit(api.fetchData())
}.catch { exception ->
    if (useCache && exception is IOException) {
        val cached = cache.getData()
        if (cached != null) {
            emit(cached)
        } else {
            throw exception
        }
    } else {
        throw exception
    }
}
```

### Advanced: Catch with Context

```kotlin
class DataService(
    private val api: ApiService,
    private val cache: CacheService,
    private val logger: Logger
) {
    fun getData(): Flow<Data> = flow {
        emit(api.fetchData())
    }.catch { exception ->
        logger.error("API call failed", exception)

        // Try cache
        try {
            val cached = cache.getData()
            if (cached != null) {
                logger.info("Using cached data")
                emit(cached)
            } else {
                logger.warn("No cached data available")
                throw exception
            }
        } catch (cacheException: Exception) {
            logger.error("Cache access failed", cacheException)
            throw exception  // Re-throw original exception
        }
    }.flowOn(Dispatchers.IO)
}
```

---

## Ответ (RU)

Оператор `catch` в Kotlin Flow — декларативный способ обработки исключений, возникающих выше по цепочке flow. Он реализует принцип **прозрачности исключений**, означающий, что исключения текут вниз по потоку так же, как обычные значения.

### Базовое использование Catch

```kotlin
flow {
    emit(1)
    emit(2)
    throw RuntimeException("Ошибка!")
    emit(3)  // Никогда не достигается
}.catch { exception ->
    println("Поймано: ${exception.message}")
    emit(-1)  // Излучить значение восстановления
}.collect { value ->
    println("Собрано: $value")
}

// Вывод:
// Собрано: 1
// Собрано: 2
// Поймано: Ошибка!
// Собрано: -1
```

### Прозрачность исключений

Прозрачность исключений — ключевой принцип: исключения обрабатываются как данные и текут вниз:

```kotlin
// Без catch: исключение распространяется на коллектор
flow {
    emit(1)
    throw RuntimeException("Ошибка")
}.collect { value ->  // Исключение выбрасывается здесь
    println(value)
}

// С catch: исключение поймано и обработано
flow {
    emit(1)
    throw RuntimeException("Ошибка")
}.catch { e ->
    println("Обработано: ${e.message}")
}.collect { value ->
    println(value)
}
```

### Catch ловит только upstream исключения

Это критически важно: `catch` ловит только исключения из операторов выше по потоку, НЕ из нижестоящих:

```kotlin
// Catch ЛОВИТ это (upstream)
flow {
    throw RuntimeException("Ошибка upstream")
}.catch { e ->
    println("Поймано: ${e.message}")  //  Ловит это
}.collect { value ->
    println(value)
}

// Catch НЕ ЛОВИТ это (downstream)
flow {
    emit(1)
}.catch { e ->
    println("Поймано: ${e.message}")  //  НЕ ловит это
}.collect { value ->
    throw RuntimeException("Ошибка downstream")  // Распространяется на вызывающего
}
```

### Где размещать Catch

```kotlin
class UserRepository {
    fun getUsers(): Flow<List<User>> = flow {
        val users = api.fetchUsers()  // Может выбросить исключение
        emit(users)
    }.catch { e ->
        // Ловить сетевые/API ошибки
        logger.error("Не удалось загрузить пользователей", e)
        emit(emptyList())  // Излучить пустой список как fallback
    }
}

// В ViewModel
class UserViewModel : ViewModel() {
    val users: StateFlow<Result<List<User>>> = repository.getUsers()
        .map { users -> Result.Success(users) }
        .catch { e ->
            // Ловить ошибки mapping
            emit(Result.Error(e.message ?: "Неизвестная ошибка"))
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = Result.Loading
        )
}
```

### Catch и Emit

Вы можете излучать значения восстановления в блоке catch:

```kotlin
fun loadData(): Flow<Data> = flow {
    val data = fetchDataFromNetwork()
    emit(data)
}.catch { exception ->
    when (exception) {
        is IOException -> {
            // Сетевая ошибка: излучить кешированные данные
            val cached = loadFromCache()
            if (cached != null) {
                emit(cached)
            } else {
                throw exception  // Перевыбросить если нет кеша
            }
        }
        is HttpException -> {
            // Ошибка сервера: излучить данные по умолчанию
            emit(Data.default())
        }
        else -> throw exception  // Перевыбросить неизвестные исключения
    }
}
```

### Catch vs Try-Catch

```kotlin
// Try-catch в билдере flow (императивный)
flow {
    try {
        val data = api.fetchData()
        emit(data)
    } catch (e: Exception) {
        emit(Data.default())
    }
}

// Оператор Catch (декларативный, предпочтительный)
flow {
    val data = api.fetchData()
    emit(data)
}.catch { e ->
    emit(Data.default())
}
```

**Различия**:
1. **Область**: try-catch локальный, оператор catch влияет на всю upstream цепочку
2. **Композируемость**: оператор catch может быть скомпонован с другими операторами
3. **Ясность**: оператор catch делает обработку ошибок явной в pipeline
4. **Прозрачность исключений**: оператор catch следует принципу прозрачности исключений Flow

### Лучшие практики

#### ДЕЛАТЬ:
```kotlin
// Использовать catch для upstream ошибок
flow {
    emit(fetchData())
}.catch { e ->
    emit(defaultData())
}.collect { data ->
    process(data)
}

// Размещать catch после операций которые могут выбросить исключение
flow {
    emit(1)
}.map { value ->
    riskyOperation(value)
}.catch { e ->
    emit(fallbackValue())
}

// Логировать ошибки в catch
.catch { exception ->
    logger.error("Операция не удалась", exception)
    emit(fallback())
}

// Комбинировать catch с retry
flow {
    emit(fetchData())
}.retry(3) { it is IOException }
.catch { e ->
    emit(cachedData())
}
```

#### НЕ ДЕЛАТЬ:
```kotlin
// Не использовать catch для downstream ошибок
flow {
    emit(1)
}.catch { e ->
    // Не поймает ошибки в collect!
}.collect { value ->
    throw Exception()  // Не поймано
}

// Не глотать исключения молча
.catch { e ->
    // Молчаливый провал - плохая практика
}
```

---

## References

- [Kotlin Flow Exception Transparency](https://kotlinlang.org/docs/flow.html#exception-transparency)
- [Flow Catch Operator](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/catch.html)
- [Exception Handling in Flow](https://developer.android.com/kotlin/flow#exceptions)

## Related Questions

### Prerequisites (Easier)
- [[q-flow-basics--kotlin--easy]] - Flow
### Related (Medium)
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-flow-exception-handling--kotlin--medium]] - Flow
- [[q-channel-flow-comparison--kotlin--medium]] - Coroutines
- [[q-flow-cold-flow-fundamentals--kotlin--easy]] - Coroutines
- [[q-hot-cold-flows--kotlin--medium]] - Hot vs Cold flows
- [[q-cold-vs-hot-flows--kotlin--medium]] - Cold vs Hot flows explained
- [[q-flow-vs-livedata-comparison--kotlin--medium]] - Flow vs LiveData
- [[q-channels-vs-flow--kotlin--medium]] - Channels vs Flow
- [[q-sharedflow-stateflow--kotlin--medium]] - SharedFlow vs StateFlow
### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-backpressure--kotlin--hard]] - Flow
- [[q-flowon-operator-context-switching--kotlin--hard]] - flowOn & context switching
- [[q-flow-backpressure--kotlin--hard]] - Backpressure handling
- [[q-flow-backpressure-strategies--kotlin--hard]] - Backpressure strategies
### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction

## MOC Links

- [[moc-kotlin]]
