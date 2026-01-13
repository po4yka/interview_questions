---
---
---\
id: kotlin-044
title: "Retry and RetryWhen operators in Flow / Операторы Retry и RetryWhen во `Flow`"
aliases: ["Retry and RetryWhen operators in Flow", "Операторы Retry и RetryWhen во Flow"]

# Classification
topic: kotlin
subtopics: [error-handling, flow]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: "https://github.com/amitshekhariitbhu/android-interview-questions"
source_note: Amit Shekhar Android Interview Questions repository - MEDIUM priority

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-flow, q-race-conditions-coroutines--kotlin--hard, q-suspend-functions-basics--kotlin--easy]

# Timestamps
created: 2025-10-06
updated: 2025-11-09

tags: [difficulty/medium, error-handling, flow, kotlin, operators, retry]
---\
# Вопрос (RU)
> Что такое операторы `retry` и `retryWhen` в Kotlin `Flow`? Как они работают?

---

# Question (EN)
> What are `retry` and `retryWhen` operators in Kotlin `Flow`? How do they work?

## Ответ (RU)

**`retry` и `retryWhen`** — операторы `Flow`, которые автоматически повторно запускают flow при возникновении исключения, реализуя устойчивую обработку ошибок.

### Retry - Простая Логика Повтора

**Базовый retry с подсчетом попыток:**

```kotlin
flow {
    emit(fetchDataFromNetwork())
}
.retry(retries = 3) { cause ->
    cause is IOException  // Повторять только при сетевых ошибках
}
.collect { data ->
    println("Data: $data")
}
```

#### Сигнатура `retry`

```kotlin
fun <T> Flow<T>.retry(
    retries: Long = Long.MAX_VALUE,
    predicate: suspend (cause: Throwable) -> Boolean = { true }
): Flow<T>
```

**Характеристики:**
- **Повторяет немедленно** после сбоя (если в предикате не используется `delay`).
- **Количество повторов управляемо:** `retries` — максимальное число повторных попыток (по умолчанию `Long.MAX_VALUE`, т.е. практически бесконечно относительно количества ретраев; исходная попытка в это число не входит).
- **Предикат** определяет, при каких исключениях выполнять повтор.
- **Просто** — хорошо для базовой логики повтора.

### Реальные Примеры Использования Retry

**Пример 1: Сетевой запрос с повтором**

```kotlin
class UserRepository {
    fun getUser(id: String): Flow<User> = flow {
        val user = api.fetchUser(id)  // Может выбросить IOException
        emit(user)
    }
    .retry(3) { exception ->
        // Повторяем только при сетевых ошибках, не при ошибках аутентификации
        exception is IOException && exception !is UnauthorizedException
    }
}
```

**Пример 2: Практически бесконечный повтор для критичных операций**

```kotlin
class ConfigRepository {
    fun getRemoteConfig(): Flow<Config> = flow {
        val config = api.fetchConfig()
        emit(config)
    }
    .retry { exception ->  // Практически бесконечные повторы ретраев
        exception is IOException
    }
}
```

**Пример 3: Повтор с логированием**

```kotlin
fun loadData(): Flow<Data> = flow {
    emit(api.getData())
}
.retry(5) { exception ->
    Log.e("DataRepo", "Failed to load data", exception)
    exception is IOException
}
```

### retryWhen - Продвинутая Логика Повтора

**`retryWhen` предоставляет контроль над временем и поведением повтора.**

```kotlin
fun <T> Flow<T>.retryWhen(
    predicate: suspend FlowCollector<T>.(cause: Throwable, attempt: Long) -> Boolean
): Flow<T>
```

**Особенности:**
- Параметр **`attempt`** — номер попытки повтора (начинается с 0 для первого ретрая).
- Можно реализовать **кастомные задержки** (экспоненциальная, линейная и т.п.).
- **Сложные условия** повтора по типам ошибок и числу попыток.
- Есть доступ к **FlowCollector** — можно эмитить состояния (например, прогресс) между попытками.

### Примеры retryWhen

**Пример 1: Экспоненциальная задержка**

```kotlin
class ApiRepository {
    fun fetchData(): Flow<Data> = flow {
        emit(api.getData())
    }
    .retryWhen { cause, attempt ->
        if (cause is IOException && attempt < 5) {
            val delayMs = 1000 * (2.0.pow(attempt.toInt())).toLong()  // 1s, 2s, 4s, 8s, 16s
            delay(delayMs)
            true  // Повторить
        } else {
            false  // Не повторять
        }
    }
}
```

**Пример 2: Линейная задержка с jitter**

```kotlin
fun loadUserData(): Flow<User> = flow {
    emit(api.getUser())
}
.retryWhen { cause, attempt ->
    when {
        cause !is IOException -> false  // Не повторять не-сетевые ошибки
        attempt >= 3 -> false  // Максимум 3 повтора
        else -> {
            // Линейная задержка: 1s, 2s, 3s + случайный jitter
            val baseDelay = (attempt + 1) * 1000
            val jitter = Random.nextInt(0, 500)
            delay(baseDelay + jitter)
            true
        }
    }
}
```

**Пример 3: Повтор с разными стратегиями по типу ошибки**

```kotlin
fun syncData(): Flow<SyncResult> = flow {
    emit(api.sync())
}
.retryWhen { cause, attempt ->
    when (cause) {
        is RateLimitException -> {
            // Ждать сброса rate limit
            delay(cause.retryAfterMs)
            attempt < 10
        }
        is ServerErrorException -> {
            // Экспоненциальная задержка для ошибок сервера
            delay(1000 * (2.0.pow(attempt.toInt())).toLong())
            attempt < 5
        }
        is NetworkException -> {
            // Быстрый повтор для сетевых ошибок
            delay(500)
            attempt < 3
        }
        else -> false  // Не повторять другие ошибки
    }
}
```

### Сравнение: Retry Vs retryWhen

| Функция | retry | retryWhen |
|---------|-------|-----------|
| **Задержка** | Нет задержки по умолчанию (немедленно) | Кастомная задержка (экспоненциальная и т.п.) |
| **Счетчик попыток** | Нет доступа к номеру попытки | Доступен параметр `attempt` |
| **Сложность** | Простой | Более гибкий |
| **Применение** | Базовый повтор | Продвинутые стратегии повтора |

### Продвинутые Паттерны

**Паттерн 1: Повтор с таймаутом**

```kotlin
fun loadData(): Flow<Data> = flow {
    emit(api.getData())
}
.timeout(10.seconds)  // Таймаут для каждой попытки эмита
.retryWhen { cause, attempt ->
    if (attempt < 3 && (cause is IOException || cause is TimeoutCancellationException)) {
        delay(2000)
        true
    } else {
        false
    }
}
```

**Паттерн 2: Повтор с fallback**

```kotlin
fun getUserData(): Flow<User> = flow {
    // Пробуем удаленный сначала
    emit(remoteApi.getUser())
}
.retryWhen { cause, attempt ->
    if (attempt < 2 && cause is IOException) {
        delay(1000)
        true
    } else {
        false
    }
}
.catch { exception ->
    // Fallback к кэшированным данным
    localCache.getUser()?.let { emit(it) } ?: throw exception
}
```

**Паттерн 3: Повтор с обновлением прогресса**

```kotlin
sealed class LoadState<out T> {
    data class Success<T>(val data: T) : LoadState<T>()
    data class Retrying(val attempt: Int) : LoadState<Nothing>()
    data class Error(val exception: Throwable) : LoadState<Nothing>()
}

fun loadWithRetry(): Flow<LoadState<Data>> = flow {
    try {
        val data = api.getData()
        emit(LoadState.Success(data))
    } catch (e: Exception) {
        throw e  // Будет обработано retryWhen
    }
}
.retryWhen { cause, attempt ->
    if (cause is IOException && attempt < 3) {
        emit(LoadState.Retrying(attempt.toInt() + 1))
        delay(1000 * (attempt + 1))
        true
    } else {
        emit(LoadState.Error(cause))
        false
    }
}
```

**Паттерн 4: Условный повтор на основе ответа**

```kotlin
sealed class ApiException(message: String) : Exception(message) {
    class RateLimited(val retryAfterSeconds: Long) : ApiException("Rate limited")
    class ServerError : ApiException("Server error")
    class ClientError(message: String) : ApiException(message)
}

fun makeApiCall(): Flow<Response> = flow {
    val response = api.call()
    when (response.code) {
        200 -> emit(response)
        429 -> throw ApiException.RateLimited(response.retryAfter)
        in 500..599 -> throw ApiException.ServerError()
        else -> throw ApiException.ClientError("Client error")
    }
}
.retryWhen { cause, attempt ->
    when (cause) {
        is ApiException.RateLimited -> {
            delay(cause.retryAfterSeconds * 1000)
            true
        }
        is ApiException.ServerError -> {
            if (attempt < 3) {
                delay(2000)
                true
            } else false
        }
        else -> false  // Не повторять client errors
    }
}
```

### Интеграция С `ViewModel`

```kotlin
class ProductViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    init {
        loadProducts()
    }

    private fun loadProducts() {
        viewModelScope.launch {
            repository.getProducts()
                .retryWhen { cause, attempt ->
                    if (cause is IOException && attempt < 3) {
                        _uiState.value = UiState.Retrying(attempt.toInt() + 1)
                        delay(1000 * (attempt + 1))
                        true
                    } else {
                        false
                    }
                }
                .catch { exception ->
                    _uiState.value = UiState.Error(exception.message ?: "Unknown error")
                }
                .collect { products ->
                    _uiState.value = UiState.Success(products)
                }
        }
    }
}
```

```kotlin
sealed class UiState {
    object Loading : UiState()
    data class Retrying(val attempt: Int) : UiState()
    data class Success(val products: List<Product>) : UiState()
    data class Error(val message: String) : UiState()
}
```

### Тестирование Логики Повтора

```kotlin
@Test
fun `retry должен повторять 3 раза при IOException`() = runTest {
    var attempts = 0
    val flow = flow {
        attempts++
        if (attempts < 4) {
            throw IOException("Network error")
        }
        emit("Success")
    }
    .retry(3) { it is IOException }

    val result = flow.first()

    assertEquals("Success", result)
    assertEquals(4, attempts)  // Первая попытка + 3 ретрая
}
```

### Лучшие Практики

**1. Всегда используйте предикат для фильтрации исключений**

```kotlin
// - ХОРОШО - Только сетевые ошибки
.retry(3) { it is IOException }

// - ПЛОХО - Повторяет все исключения
.retry(3)
```

**2. Реализуйте экспоненциальную задержку для retryWhen**

```kotlin
// - ХОРОШО - Экспоненциальная задержка
.retryWhen { cause, attempt ->
    if (attempt < 5) {
        delay(1000 * (2.0.pow(attempt.toInt())).toLong())
        true
    } else false
}

// - ПЛОХО - Без задержки, перегружает сервер
.retryWhen { _, attempt ->
    attempt < 5
}
```

**3. Устанавливайте максимальное количество попыток**

```kotlin
// - ХОРОШО - Ограниченные повторы
.retry(3) { it is IOException }

// - ПЛОХО - Бесконечные повторы могут вызвать проблемы
.retry { it is IOException }
```

**4. Логируйте попытки повтора**

```kotlin
.retryWhen { cause, attempt ->
    Log.w("API", "Retry attempt $attempt for ${cause.message}")
    if (attempt < 3) {
        delay(1000)
        true
    } else false
}
```

**Краткое содержание**: `retry` немедленно повторяет `Flow` при исключении (количество ретраев задается параметром `retries`, по умолчанию практически бесконечно относительно числа ретраев; используйте предикат для фильтрации ошибок). `retryWhen` предоставляет продвинутый контроль (доступ к номеру попытки ретрая, кастомные задержки, разные стратегии по типу ошибки, возможность эмитить промежуточные состояния). Используйте `retry` для простой логики повтора, `retryWhen` — для экспоненциальной задержки, разных стратегий и обновления прогресса. Всегда фильтруйте исключения, добавляйте задержки при сетевых ретраях и устанавливайте максимальное число попыток. См. также [[c-flow]] для базовых концепций.

---

## Answer (EN)

**`retry` and `retryWhen`** are `Flow` operators that automatically re-execute a `Flow` when it encounters an exception, implementing resilient error handling.

### Retry - Simple Retry Logic

**Basic retry with count:**

```kotlin
flow {
    emit(fetchDataFromNetwork())
}
.retry(retries = 3) { cause ->
    cause is IOException  // Only retry on network errors
}
.collect { data ->
    println("Data: $data")
}
```

### Retry Signature

```kotlin
fun <T> Flow<T>.retry(
    retries: Long = Long.MAX_VALUE,
    predicate: suspend (cause: Throwable) -> Boolean = { true }
): Flow<T>
```

**Characteristics:**
- **Retries immediately** after failure by default (unless you call `delay` inside the predicate).
- **Retry count is controlled**: `retries` is the maximum number of retry attempts (default `Long.MAX_VALUE`, i.e., effectively infinite in terms of retries; the initial attempt is not counted).
- **Predicate** determines which exceptions to retry on.
- **Simple** - good for basic retry logic.

### Real-World Retry Examples

**Example 1: Network `Request` with Retry**

```kotlin
class UserRepository {
    fun getUser(id: String): Flow<User> = flow {
        val user = api.fetchUser(id)  // May throw IOException
        emit(user)
    }
    .retry(3) { exception ->
        // Retry only on network errors, not on auth errors
        exception is IOException && exception !is UnauthorizedException
    }
}
```

**Example 2: Infinite Retry for Critical Operations**

```kotlin
class ConfigRepository {
    fun getRemoteConfig(): Flow<Config> = flow {
        val config = api.fetchConfig()
        emit(config)
    }
    .retry { exception ->  // Effectively infinite retries (for retries themselves)
        exception is IOException
    }
}
```

**Example 3: Retry with Logging**

```kotlin
fun loadData(): Flow<Data> = flow {
    emit(api.getData())
}
.retry(5) { exception ->
    Log.e("DataRepo", "Failed to load data", exception)
    exception is IOException
}
```

### retryWhen - Advanced Retry Logic

**`retryWhen` provides control over retry timing and behavior.**

```kotlin
fun <T> Flow<T>.retryWhen(
    predicate: suspend FlowCollector<T>.(cause: Throwable, attempt: Long) -> Boolean
): Flow<T>
```

**Key features:**
- **`attempt` parameter** - retry attempt number (0-based, for retries only).
- **Custom delay** - implement exponential/linear backoff.
- **Conditional logic** - complex retry conditions per error type and attempt.
- **Access to FlowCollector** - can emit values (e.g., progress) between attempts.

### retryWhen Examples

**Example 1: Exponential Backoff**

```kotlin
class ApiRepository {
    fun fetchData(): Flow<Data> = flow {
        emit(api.getData())
    }
    .retryWhen { cause, attempt ->
        if (cause is IOException && attempt < 5) {
            val delayMs = 1000 * (2.0.pow(attempt.toInt())).toLong()  // 1s, 2s, 4s, 8s, 16s
            delay(delayMs)
            true  // Retry
        } else {
            false  // Don't retry
        }
    }
}
```

**Example 2: Linear Backoff with Jitter**

```kotlin
fun loadUserData(): Flow<User> = flow {
    emit(api.getUser())
}
.retryWhen { cause, attempt ->
    when {
        cause !is IOException -> false  // Don't retry non-network errors
        attempt >= 3 -> false  // Max 3 retries
        else -> {
            // Linear backoff: 1s, 2s, 3s + random jitter
            val baseDelay = (attempt + 1) * 1000
            val jitter = Random.nextInt(0, 500)
            delay(baseDelay + jitter)
            true
        }
    }
}
```

**Example 3: Retry with Different Strategies by Error Type**

```kotlin
fun syncData(): Flow<SyncResult> = flow {
    emit(api.sync())
}
.retryWhen { cause, attempt ->
    when (cause) {
        is RateLimitException -> {
            // Wait for rate limit to reset
            delay(cause.retryAfterMs)
            attempt < 10
        }
        is ServerErrorException -> {
            // Exponential backoff for server errors
            delay(1000 * (2.0.pow(attempt.toInt())).toLong())
            attempt < 5
        }
        is NetworkException -> {
            // Quick retry for network errors
            delay(500)
            attempt < 3
        }
        else -> false  // Don't retry other errors
    }
}
```

### Comparison: Retry Vs retryWhen

| Feature | retry | retryWhen |
|---------|-------|-----------|
| **Delay** | No delay by default (immediate) | Custom delay (exponential backoff, etc.) |
| **Attempt count** | No attempt index provided | Attempt index available as `attempt` |
| **Complexity** | Simple | More flexible |
| **Use case** | Basic retry | Advanced retry strategies |

### Advanced Patterns

**Pattern 1: Retry with Timeout**

```kotlin
fun loadData(): Flow<Data> = flow {
    emit(api.getData())
}
.timeout(10.seconds)  // Timeout each emission attempt
.retryWhen { cause, attempt ->
    if (attempt < 3 && (cause is IOException || cause is TimeoutCancellationException)) {
        delay(2000)
        true
    } else {
        false
    }
}
```

**Pattern 2: Retry with Fallback**

```kotlin
fun getUserData(): Flow<User> = flow {
    // Try remote first
    emit(remoteApi.getUser())
}
.retryWhen { cause, attempt ->
    if (attempt < 2 && cause is IOException) {
        delay(1000)
        true
    } else {
        false
    }
}
.catch { exception ->
    // Fallback to cached data
    localCache.getUser()?.let { emit(it) } ?: throw exception
}
```

**Pattern 3: Retry with Progress Updates**

```kotlin
sealed class LoadState<out T> {
    data class Success<T>(val data: T) : LoadState<T>()
    data class Retrying(val attempt: Int) : LoadState<Nothing>()
    data class Error(val exception: Throwable) : LoadState<Nothing>()
}

fun loadWithRetry(): Flow<LoadState<Data>> = flow {
    try {
        val data = api.getData()
        emit(LoadState.Success(data))
    } catch (e: Exception) {
        throw e  // Will be handled by retryWhen
    }
}
.retryWhen { cause, attempt ->
    if (cause is IOException && attempt < 3) {
        emit(LoadState.Retrying(attempt.toInt() + 1))
        delay(1000 * (attempt + 1))
        true
    } else {
        emit(LoadState.Error(cause))
        false
    }
}
```

**Pattern 4: Conditional Retry Based on `Response`**

```kotlin
sealed class ApiException(message: String) : Exception(message) {
    class RateLimited(val retryAfterSeconds: Long) : ApiException("Rate limited")
    class ServerError : ApiException("Server error")
    class ClientError(message: String) : ApiException(message)
}

fun makeApiCall(): Flow<Response> = flow {
    val response = api.call()
    when (response.code) {
        200 -> emit(response)
        429 -> throw ApiException.RateLimited(response.retryAfter)
        in 500..599 -> throw ApiException.ServerError()
        else -> throw ApiException.ClientError("Client error")
    }
}
.retryWhen { cause, attempt ->
    when (cause) {
        is ApiException.RateLimited -> {
            delay(cause.retryAfterSeconds * 1000)
            true
        }
        is ApiException.ServerError -> {
            if (attempt < 3) {
                delay(2000)
                true
            } else false
        }
        else -> false  // Don't retry client errors
    }
}
```

### ViewModel Integration

```kotlin
class ProductViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    init {
        loadProducts()
    }

    private fun loadProducts() {
        viewModelScope.launch {
            repository.getProducts()
                .retryWhen { cause, attempt ->
                    if (cause is IOException && attempt < 3) {
                        _uiState.value = UiState.Retrying(attempt.toInt() + 1)
                        delay(1000 * (attempt + 1))
                        true
                    } else {
                        false
                    }
                }
                .catch { exception ->
                    _uiState.value = UiState.Error(exception.message ?: "Unknown error")
                }
                .collect { products ->
                    _uiState.value = UiState.Success(products)
                }
        }
    }
}

sealed class UiState {
    object Loading : UiState()
    data class Retrying(val attempt: Int) : UiState()
    data class Success(val products: List<Product>) : UiState()
    data class Error(val message: String) : UiState()
}
```

### Testing Retry Logic

```kotlin
@Test
fun `retry should retry 3 times on IOException`() = runTest {
    var attempts = 0
    val flow = flow {
        attempts++
        if (attempts < 4) {
            throw IOException("Network error")
        }
        emit("Success")
    }
    .retry(3) { it is IOException }

    val result = flow.first()

    assertEquals("Success", result)
    assertEquals(4, attempts)  // Initial attempt + 3 retries
}
```

### Best Practices

**1. Always use predicate to filter exceptions**

```kotlin
// - GOOD - Only retry network errors
.retry(3) { it is IOException }

// - BAD - Retries all exceptions
.retry(3)
```

**2. Implement exponential backoff for retryWhen**

```kotlin
// - GOOD - Exponential backoff
.retryWhen { cause, attempt ->
    if (attempt < 5) {
        delay(1000 * (2.0.pow(attempt.toInt())).toLong())
        true
    } else false
}

// - BAD - No delay, hammers server
.retryWhen { _, attempt ->
    attempt < 5
}
```

**3. `Set` maximum retry attempts**

```kotlin
// - GOOD - Limited retries
.retry(3) { it is IOException }

// - BAD - Infinite retries can cause issues
.retry { it is IOException }
```

**4. Log retry attempts**

```kotlin
.retryWhen { cause, attempt ->
    Log.w("API", "Retry attempt $attempt for ${cause.message}")
    if (attempt < 3) {
        delay(1000)
        true
    } else false
}
```

**English Summary**: `retry` immediately retries the `Flow` on exception (number of retries controlled by `retries`, default effectively infinite for retries; use predicate to filter which errors are retried). `retryWhen` provides advanced control (attempt number, custom delays, different strategies per error type, ability to emit progress states). Use `retry` for simple retry logic; use `retryWhen` for exponential backoff, differentiated strategies, and progress updates. Always filter exceptions, add delays for network retries, and set maximum attempts. See also [[c-flow]] for foundational concepts.

## Дополнительные Вопросы (RU)

- В чем ключевые отличия этих операторов от подходов в Java?
- Когда вы бы применили эти операторы на практике?
- Каких распространенных ошибок при использовании повтора следует избегать?

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)

- [Обработка ошибок во `Flow` - документация Kotlin](https://kotlinlang.org/docs/flow.html#exception-handling)
- [Операторы Retry](https://elizarov.medium.com/kotlin-flows-and-coroutines-256260fb3bdb)

## References

- [Flow Error Handling - Kotlin Documentation](https://kotlinlang.org/docs/flow.html#exception-handling)
- [Retry Operators](https://elizarov.medium.com/kotlin-flows-and-coroutines-256260fb3bdb)

## Связанные Вопросы (RU)

### Средний Уровень
- [[q-instant-search-flow-operators--kotlin--medium]] - `Flow`
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-flow-operators--kotlin--medium]] - `Flow`
- [[q-catch-operator-flow--kotlin--medium]] - `Flow`

### Продвинутый Уровень
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-operators-deep-dive--kotlin--hard]] - `Flow`
- [[q-flow-backpressure-strategies--kotlin--hard]] - `Flow`

### Хаб
- [[q-kotlin-flow-basics--kotlin--medium]] - Введение в `Flow`

## Related Questions

### Related (Medium)
- [[q-instant-search-flow-operators--kotlin--medium]] - `Flow`
- [[q-flow-operators-map-filter--kotlin--medium]] - Coroutines
- [[q-flow-operators--kotlin--medium]] - `Flow`
- [[q-catch-operator-flow--kotlin--medium]] - `Flow`

### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
- [[q-flow-operators-deep-dive--kotlin--hard]] - `Flow`
- [[q-flow-backpressure-strategies--kotlin--hard]] - `Flow`

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive `Flow` introduction
