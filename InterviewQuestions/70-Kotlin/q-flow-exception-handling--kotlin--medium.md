---
id: 20251011-003
title: "Flow Exception Handling / Обработка исключений в Flow"
aliases: []

# Classification
topic: kotlin
subtopics: [flow, exceptions, error-handling, retry, catch]
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
related: [q-kotlin-flow-basics--kotlin--medium, q-coroutine-exception-handling--kotlin--medium]

# Timestamps
created: 2025-10-11
updated: 2025-10-11

tags: [kotlin, flow, exceptions, error-handling, retry, catch, difficulty/medium]
---
# Question (EN)
> How do you handle exceptions in Flows? Explain catch, retry, retryWhen operators. Implement exponential backoff retry strategy.

# Вопрос (RU)
> Как обрабатывать исключения в Flow? Объясните операторы catch, retry, retryWhen. Реализуйте стратегию повтора с экспоненциальной задержкой.

---

## Answer (EN)

Exception handling in Flows is crucial for building robust applications. Kotlin Flow provides several operators for handling errors gracefully.

### Exception Transparency Principle

Flow follows the **exception transparency** principle: exceptions can only be caught downstream, not upstream of where they occur.

```kotlin
// ❌ Wrong: catch cannot handle upstream exceptions
flow {
    emit(1)
    throw Exception("Error in flow")
}
.catch { /* This catches the exception */ }
.map { it * 2 } // If exception here, catch above won't handle it

// ✅ Correct: catch handles exceptions from upstream
flow {
    emit(1)
    throw Exception("Error in flow")
}
.map { it * 2 }
.catch { /* This catches exceptions from flow and map */ }
```

### The catch Operator

The `catch` operator intercepts exceptions from upstream and allows you to handle them.

#### Basic Usage

```kotlin
fun fetchUser(id: Int): Flow<User> = flow {
    if (id <= 0) {
        throw IllegalArgumentException("Invalid user ID")
    }
    val user = api.getUser(id)
    emit(user)
}

// Handle exception and provide default value
fetchUser(-1)
    .catch { exception ->
        println("Error: ${exception.message}")
        emit(User.DEFAULT) // Emit default value
    }
    .collect { user ->
        println("User: $user")
    }

/*
Output:
Error: Invalid user ID
User: User.DEFAULT
*/
```

#### Catch Properties

1. **Only catches upstream exceptions** - Does not catch exceptions in the collect block
2. **Can emit values** - Provide fallback data
3. **Can rethrow** - Propagate to outer handler
4. **Transparent** - Exception downstream continues to propagate

```kotlin
flow {
    emit(1)
    throw IOException("Network error")
}
.catch { e ->
    when (e) {
        is IOException -> emit(-1) // Provide fallback
        else -> throw e // Rethrow other exceptions
    }
}
.collect { value ->
    println("Received: $value")
    // Exception here NOT caught by catch above
}
```

### Real-world Example: Network Request with Fallback

```kotlin
data class Article(val id: Int, val title: String, val cached: Boolean = false)

class ArticleRepository(
    private val api: ArticleApi,
    private val cache: ArticleCache
) {
    fun getArticle(id: Int): Flow<Article> = flow {
        // Try to fetch from network
        val article = api.fetchArticle(id)
        emit(article)
    }
    .catch { exception ->
        println("Network failed: ${exception.message}, trying cache...")

        // Fallback to cache
        val cachedArticle = cache.get(id)
        if (cachedArticle != null) {
            emit(cachedArticle.copy(cached = true))
        } else {
            // No cache available, emit error state or rethrow
            throw ArticleNotFoundException("Article $id not found")
        }
    }
}

// Usage
suspend fun loadArticle() {
    repository.getArticle(123)
        .catch { e ->
            // Handle final error
            emit(Article(-1, "Failed to load", cached = false))
        }
        .collect { article ->
            if (article.cached) {
                showCachedIndicator()
            }
            displayArticle(article)
        }
}
```

### The retry Operator

The `retry` operator automatically retries the flow when an exception occurs.

#### Simple Retry

```kotlin
fun <T> Flow<T>.retry(
    retries: Long = Long.MAX_VALUE,
    predicate: suspend (cause: Throwable) -> Boolean = { true }
): Flow<T>
```

```kotlin
// Retry up to 3 times on any exception
flow {
    println("Attempting request...")
    val result = unstableNetworkCall()
    emit(result)
}
.retry(3)
.collect { println("Success: $it") }

/*
Output (if first 2 attempts fail):
Attempting request...
Attempting request...
Attempting request...
Success: data
*/
```

#### Conditional Retry

```kotlin
// Retry only for specific exceptions
flow {
    val result = api.fetchData()
    emit(result)
}
.retry(3) { exception ->
    // Only retry on network errors
    exception is IOException
}
.collect { data ->
    println("Data: $data")
}
```

#### Retry with Delay

```kotlin
// Simple retry with fixed delay
fun <T> Flow<T>.retryWithDelay(
    retries: Long,
    delayMillis: Long
): Flow<T> {
    var currentRetry = 0L
    return retry(retries) { cause ->
        if (currentRetry >= retries) {
            false
        } else {
            currentRetry++
            delay(delayMillis)
            true
        }
    }
}

// Usage
fetchDataFlow()
    .retryWithDelay(retries = 3, delayMillis = 1000)
    .collect { data -> processData(data) }
```

### The retryWhen Operator

The `retryWhen` operator provides more control over retry logic with access to attempt count and exception.

```kotlin
fun <T> Flow<T>.retryWhen(
    predicate: suspend FlowCollector<T>.(cause: Throwable, attempt: Long) -> Boolean
): Flow<T>
```

```kotlin
// Retry with increasing delay
flow {
    println("Attempt at ${System.currentTimeMillis()}")
    val result = unstableOperation()
    emit(result)
}
.retryWhen { cause, attempt ->
    if (attempt < 3 && cause is IOException) {
        delay(1000 * (attempt + 1)) // 1s, 2s, 3s
        println("Retrying after ${1000 * (attempt + 1)}ms")
        true
    } else {
        false
    }
}
.collect { println("Success: $it") }
```

### Exponential Backoff Implementation

Exponential backoff is a standard error-handling strategy where retry delays increase exponentially.

#### Complete Implementation

```kotlin
/**
 * Retries the flow with exponential backoff strategy.
 *
 * @param maxRetries Maximum number of retry attempts
 * @param initialDelayMs Initial delay in milliseconds
 * @param maxDelayMs Maximum delay in milliseconds
 * @param factor Exponential factor (typically 2.0)
 * @param jitter Add randomness to prevent thundering herd (0.0 to 1.0)
 * @param predicate Optional condition to determine if retry should occur
 */
fun <T> Flow<T>.retryWithExponentialBackoff(
    maxRetries: Int = 3,
    initialDelayMs: Long = 1000,
    maxDelayMs: Long = 32000,
    factor: Double = 2.0,
    jitter: Double = 0.1,
    predicate: (Throwable) -> Boolean = { true }
): Flow<T> = retryWhen { cause, attempt ->
    if (attempt >= maxRetries || !predicate(cause)) {
        false // Stop retrying
    } else {
        // Calculate exponential delay
        val exponentialDelay = (initialDelayMs * factor.pow(attempt.toInt())).toLong()
        val cappedDelay = exponentialDelay.coerceAtMost(maxDelayMs)

        // Add jitter to prevent thundering herd
        val jitterMs = (cappedDelay * jitter * Random.nextDouble()).toLong()
        val finalDelay = cappedDelay + jitterMs

        println("Retry attempt ${attempt + 1}/$maxRetries after ${finalDelay}ms due to: ${cause.message}")
        delay(finalDelay)
        true
    }
}

// Usage example
suspend fun fetchWithBackoff() {
    var attemptCount = 0

    flow {
        attemptCount++
        println("Attempt $attemptCount")

        if (attemptCount < 3) {
            throw IOException("Network unavailable")
        }

        emit("Success!")
    }
    .retryWithExponentialBackoff(
        maxRetries = 5,
        initialDelayMs = 1000,
        maxDelayMs = 30000,
        factor = 2.0,
        jitter = 0.1,
        predicate = { it is IOException } // Only retry network errors
    )
    .collect { result ->
        println("Result: $result")
    }
}

/*
Output:
Attempt 1
Retry attempt 1/5 after 1100ms due to: Network unavailable
Attempt 2
Retry attempt 2/5 after 2050ms due to: Network unavailable
Attempt 3
Result: Success!
*/
```

#### Why Use Jitter?

Jitter prevents the "thundering herd" problem where multiple clients retry simultaneously:

```kotlin
// Without jitter - all clients retry at same time
// Client 1: retry at 1000ms, 2000ms, 4000ms
// Client 2: retry at 1000ms, 2000ms, 4000ms
// Server gets slammed with simultaneous requests!

// With jitter - retries spread out
// Client 1: retry at 1050ms, 2150ms, 4200ms
// Client 2: retry at 1100ms, 1900ms, 3800ms
// Load distributed over time
```

### Advanced Pattern: Circuit Breaker

Circuit breaker pattern prevents cascading failures by stopping requests after consecutive failures.

```kotlin
class CircuitBreaker(
    private val failureThreshold: Int = 5,
    private val resetTimeoutMs: Long = 60000
) {
    private var failureCount = 0
    private var lastFailureTime = 0L
    private var state = State.CLOSED

    enum class State { CLOSED, OPEN, HALF_OPEN }

    suspend fun <T> execute(block: suspend () -> T): T {
        when (state) {
            State.OPEN -> {
                // Check if enough time passed to try again
                if (System.currentTimeMillis() - lastFailureTime > resetTimeoutMs) {
                    state = State.HALF_OPEN
                    println("Circuit breaker: HALF_OPEN")
                } else {
                    throw CircuitBreakerOpenException("Circuit breaker is OPEN")
                }
            }
            State.HALF_OPEN, State.CLOSED -> {
                // Allow request
            }
        }

        return try {
            val result = block()
            onSuccess()
            result
        } catch (e: Exception) {
            onFailure()
            throw e
        }
    }

    private fun onSuccess() {
        failureCount = 0
        state = State.CLOSED
    }

    private fun onFailure() {
        failureCount++
        lastFailureTime = System.currentTimeMillis()

        if (failureCount >= failureThreshold) {
            state = State.OPEN
            println("Circuit breaker: OPEN after $failureCount failures")
        }
    }
}

class CircuitBreakerOpenException(message: String) : Exception(message)

// Extension function for Flow
fun <T> Flow<T>.withCircuitBreaker(
    circuitBreaker: CircuitBreaker
): Flow<T> = flow {
    collect { value ->
        circuitBreaker.execute {
            emit(value)
        }
    }
}.catch { exception ->
    if (exception is CircuitBreakerOpenException) {
        println("Request blocked by circuit breaker")
        // Emit fallback or rethrow
    } else {
        throw exception
    }
}

// Usage
val circuitBreaker = CircuitBreaker(failureThreshold = 3, resetTimeoutMs = 10000)

suspend fun makeRequestWithCircuitBreaker() {
    flow {
        val result = api.fetchData()
        emit(result)
    }
    .withCircuitBreaker(circuitBreaker)
    .retryWithExponentialBackoff(maxRetries = 2)
    .catch { e ->
        println("Final error: ${e.message}")
        emit(emptyList()) // Fallback
    }
    .collect { data ->
        println("Data: $data")
    }
}
```

### Combining Error Handling Strategies

```kotlin
// Comprehensive error handling
fun <T> Flow<T>.withRobustErrorHandling(
    maxRetries: Int = 3,
    timeout: Duration = 30.seconds,
    fallback: T? = null
): Flow<T> = this
    .timeout(timeout) // Prevent hanging
    .retryWithExponentialBackoff(
        maxRetries = maxRetries,
        initialDelayMs = 1000,
        predicate = {
            // Retry transient errors only
            it is IOException || it is TimeoutCancellationException
        }
    )
    .catch { exception ->
        when (exception) {
            is TimeoutCancellationException -> {
                println("Request timed out")
                fallback?.let { emit(it) }
            }
            is IOException -> {
                println("Network error: ${exception.message}")
                fallback?.let { emit(it) }
            }
            else -> {
                // Non-recoverable error
                throw exception
            }
        }
    }

// Usage
suspend fun loadUserData(userId: Int) {
    userRepository.getUser(userId)
        .withRobustErrorHandling(
            maxRetries = 3,
            timeout = 10.seconds,
            fallback = User.GUEST
        )
        .collect { user ->
            displayUser(user)
        }
}
```

### Error Handling in StateFlow/SharedFlow

```kotlin
class UserViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState

    sealed class UiState {
        object Loading : UiState()
        data class Success(val user: User) : UiState()
        data class Error(val message: String) : UiState()
    }

    fun loadUser(userId: Int) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            userRepository.getUser(userId)
                .retryWithExponentialBackoff(maxRetries = 3)
                .catch { exception ->
                    _uiState.value = UiState.Error(
                        exception.message ?: "Unknown error"
                    )
                }
                .collect { user ->
                    _uiState.value = UiState.Success(user)
                }
        }
    }
}
```

### Best Practices

1. **Always use catch for critical flows**:
   ```kotlin
   // ❌ Unhandled exception crashes app
   flow { emit(api.getData()) }.collect()

   // ✅ Graceful error handling
   flow { emit(api.getData()) }
       .catch { emit(defaultData) }
       .collect()
   ```

2. **Place catch after all transformations**:
   ```kotlin
   // ✅ Catches all upstream exceptions
   flow { }
       .map { }
       .filter { }
       .catch { } // Handles all above
       .collect()
   ```

3. **Don't catch in collect block**:
   ```kotlin
   // ❌ Wrong: catch doesn't handle this
   .catch { }
   .collect { throw Exception() }

   // ✅ Correct: handle in onEach
   .onEach { if (invalid) throw Exception() }
   .catch { }
   .collect()
   ```

4. **Use retry for transient errors only**:
   ```kotlin
   .retry { exception ->
       exception is IOException ||
       exception is TimeoutException
   }
   ```

5. **Combine with timeout**:
   ```kotlin
   .timeout(30.seconds)
   .retryWithExponentialBackoff()
   .catch { }
   ```

### Common Pitfalls

1. **Catching exceptions in collect**:
   ```kotlin
   // ❌ catch operator won't handle this
   .catch { emit(default) }
   .collect { throw Exception() }

   // ✅ Use onEach instead
   .onEach { if (error) throw Exception() }
   .catch { emit(default) }
   .collect()
   ```

2. **Infinite retry**:
   ```kotlin
   // ❌ Will retry forever
   .retry { true }

   // ✅ Limit retries
   .retry(3) { it is IOException }
   ```

3. **Not considering error types**:
   ```kotlin
   // ❌ Retries even on auth errors
   .retry(5)

   // ✅ Only retry recoverable errors
   .retry(5) { it is IOException }
   ```

4. **Missing timeout**:
   ```kotlin
   // ❌ Can hang forever
   .retry(3)

   // ✅ Add timeout
   .timeout(30.seconds)
   .retry(3)
   ```

**English Summary**: Flow exception handling uses catch for handling upstream exceptions, retry for automatic retries, and retryWhen for conditional retry logic. Exponential backoff with jitter is the standard retry strategy. The catch operator only handles exceptions from upstream, not from the collect block. Combine error handling strategies with timeout and circuit breaker patterns for robust applications. Always provide fallback values or error states for UI flows.

## Ответ (RU)

Обработка исключений в Flow критична для построения надежных приложений. Kotlin Flow предоставляет несколько операторов для изящной обработки ошибок.

### Принцип прозрачности исключений

Flow следует принципу **прозрачности исключений**: исключения можно поймать только ниже по потоку, а не выше места их возникновения.

```kotlin
// ❌ Неправильно: catch не может обработать исключения выше по потоку
flow {
    emit(1)
    throw Exception("Ошибка")
}
.catch { /* Это ловит исключение */ }
.map { it * 2 } // Если исключение здесь, catch выше не обработает

// ✅ Правильно
flow { emit(1) }
.map { it * 2 }
.catch { /* Это ловит исключения из flow и map */ }
```

### Оператор catch

Оператор `catch` перехватывает исключения из upstream и позволяет их обработать.

#### Базовое использование

```kotlin
fun fetchUser(id: Int): Flow<User> = flow {
    if (id <= 0) {
        throw IllegalArgumentException("Неверный ID")
    }
    val user = api.getUser(id)
    emit(user)
}

// Обработка исключения с дефолтным значением
fetchUser(-1)
    .catch { exception ->
        println("Ошибка: ${exception.message}")
        emit(User.DEFAULT) // Испустить дефолтное значение
    }
    .collect { user ->
        println("Пользователь: $user")
    }
```

### Реальный пример: Сетевой запрос с fallback

```kotlin
class ArticleRepository(
    private val api: ArticleApi,
    private val cache: ArticleCache
) {
    fun getArticle(id: Int): Flow<Article> = flow {
        // Попытка загрузки из сети
        val article = api.fetchArticle(id)
        emit(article)
    }
    .catch { exception ->
        println("Сеть недоступна: ${exception.message}, проверяю кеш...")

        // Fallback на кеш
        val cachedArticle = cache.get(id)
        if (cachedArticle != null) {
            emit(cachedArticle.copy(cached = true))
        } else {
            throw ArticleNotFoundException("Статья $id не найдена")
        }
    }
}
```

### Оператор retry

Оператор `retry` автоматически повторяет поток при возникновении исключения.

#### Простой retry

```kotlin
// Повтор до 3 раз при любом исключении
flow {
    println("Попытка запроса...")
    val result = unstableNetworkCall()
    emit(result)
}
.retry(3)
.collect { println("Успех: $it") }
```

#### Условный retry

```kotlin
// Повтор только для конкретных исключений
flow {
    val result = api.fetchData()
    emit(result)
}
.retry(3) { exception ->
    // Повтор только при сетевых ошибках
    exception is IOException
}
.collect { data -> println("Данные: $data") }
```

### Оператор retryWhen

Оператор `retryWhen` предоставляет больше контроля с доступом к номеру попытки и исключению.

```kotlin
// Повтор с увеличивающейся задержкой
flow {
    println("Попытка")
    val result = unstableOperation()
    emit(result)
}
.retryWhen { cause, attempt ->
    if (attempt < 3 && cause is IOException) {
        delay(1000 * (attempt + 1)) // 1с, 2с, 3с
        println("Повтор через ${1000 * (attempt + 1)}мс")
        true
    } else {
        false
    }
}
.collect { println("Успех: $it") }
```

### Реализация экспоненциальной задержки

Экспоненциальная задержка - стандартная стратегия обработки ошибок, где задержки повтора растут экспоненциально.

```kotlin
/**
 * Повтор с экспоненциальной задержкой.
 *
 * @param maxRetries Максимальное количество повторов
 * @param initialDelayMs Начальная задержка в миллисекундах
 * @param maxDelayMs Максимальная задержка
 * @param factor Экспоненциальный коэффициент (обычно 2.0)
 * @param jitter Добавить случайность для предотвращения одновременных запросов
 */
fun <T> Flow<T>.retryWithExponentialBackoff(
    maxRetries: Int = 3,
    initialDelayMs: Long = 1000,
    maxDelayMs: Long = 32000,
    factor: Double = 2.0,
    jitter: Double = 0.1,
    predicate: (Throwable) -> Boolean = { true }
): Flow<T> = retryWhen { cause, attempt ->
    if (attempt >= maxRetries || !predicate(cause)) {
        false
    } else {
        val exponentialDelay = (initialDelayMs * factor.pow(attempt.toInt())).toLong()
        val cappedDelay = exponentialDelay.coerceAtMost(maxDelayMs)

        // Добавить jitter
        val jitterMs = (cappedDelay * jitter * Random.nextDouble()).toLong()
        val finalDelay = cappedDelay + jitterMs

        println("Повтор ${attempt + 1}/$maxRetries через ${finalDelay}мс")
        delay(finalDelay)
        true
    }
}

// Использование
fetchDataFlow()
    .retryWithExponentialBackoff(
        maxRetries = 5,
        initialDelayMs = 1000,
        predicate = { it is IOException }
    )
    .collect { result -> println("Результат: $result") }
```

#### Зачем нужен jitter?

Jitter предотвращает проблему "стада", когда все клиенты повторяют запросы одновременно:

```kotlin
// Без jitter - все клиенты повторяют одновременно
// Клиент 1: повтор в 1000мс, 2000мс, 4000мс
// Клиент 2: повтор в 1000мс, 2000мс, 4000мс
// Сервер получает шквал одновременных запросов!

// С jitter - повторы распределены
// Клиент 1: повтор в 1050мс, 2150мс, 4200мс
// Клиент 2: повтор в 1100мс, 1900мс, 3800мс
// Нагрузка распределена во времени
```

### Продвинутый паттерн: Circuit Breaker

```kotlin
class CircuitBreaker(
    private val failureThreshold: Int = 5,
    private val resetTimeoutMs: Long = 60000
) {
    private var failureCount = 0
    private var state = State.CLOSED

    enum class State { CLOSED, OPEN, HALF_OPEN }

    suspend fun <T> execute(block: suspend () -> T): T {
        when (state) {
            State.OPEN -> {
                if (System.currentTimeMillis() - lastFailureTime > resetTimeoutMs) {
                    state = State.HALF_OPEN
                } else {
                    throw CircuitBreakerOpenException("Circuit breaker открыт")
                }
            }
            else -> { /* Разрешить запрос */ }
        }

        return try {
            val result = block()
            onSuccess()
            result
        } catch (e: Exception) {
            onFailure()
            throw e
        }
    }
}
```

### Комбинирование стратегий обработки ошибок

```kotlin
// Комплексная обработка ошибок
fun <T> Flow<T>.withRobustErrorHandling(
    maxRetries: Int = 3,
    timeout: Duration = 30.seconds,
    fallback: T? = null
): Flow<T> = this
    .timeout(timeout) // Предотвратить зависание
    .retryWithExponentialBackoff(
        maxRetries = maxRetries,
        predicate = {
            it is IOException || it is TimeoutCancellationException
        }
    )
    .catch { exception ->
        when (exception) {
            is TimeoutCancellationException -> {
                fallback?.let { emit(it) }
            }
            is IOException -> {
                fallback?.let { emit(it) }
            }
            else -> throw exception
        }
    }
```

### Лучшие практики

1. **Всегда используйте catch для критичных потоков**:
   ```kotlin
   // ❌ Необработанное исключение крашит приложение
   flow { emit(api.getData()) }.collect()

   // ✅ Изящная обработка ошибок
   flow { emit(api.getData()) }
       .catch { emit(defaultData) }
       .collect()
   ```

2. **Размещайте catch после всех трансформаций**:
   ```kotlin
   flow { }
       .map { }
       .filter { }
       .catch { } // Обрабатывает все выше
       .collect()
   ```

3. **Используйте retry только для временных ошибок**:
   ```kotlin
   .retry { exception ->
       exception is IOException || exception is TimeoutException
   }
   ```

4. **Комбинируйте с timeout**:
   ```kotlin
   .timeout(30.seconds)
   .retryWithExponentialBackoff()
   .catch { }
   ```

### Распространенные ошибки

1. **Ловля исключений в collect**:
   ```kotlin
   // ❌ catch не обработает это
   .catch { emit(default) }
   .collect { throw Exception() }

   // ✅ Используйте onEach
   .onEach { if (error) throw Exception() }
   .catch { emit(default) }
   .collect()
   ```

2. **Бесконечный retry**:
   ```kotlin
   // ❌ Будет повторять вечно
   .retry { true }

   // ✅ Ограничьте повторы
   .retry(3) { it is IOException }
   ```

3. **Отсутствие timeout**:
   ```kotlin
   // ❌ Может зависнуть навсегда
   .retry(3)

   // ✅ Добавьте timeout
   .timeout(30.seconds).retry(3)
   ```

**Краткое содержание**: Обработка исключений в Flow использует catch для обработки upstream исключений, retry для автоматических повторов, и retryWhen для условной логики повтора. Экспоненциальная задержка с jitter - стандартная стратегия повтора. Оператор catch обрабатывает только исключения из upstream, не из блока collect. Комбинируйте стратегии обработки ошибок с timeout и circuit breaker для надежных приложений.

---

## References
- [Exception handling - Kotlin Flow](https://kotlinlang.org/docs/flow.html#exception-handling)
- [Flow error handling - Android Developers](https://developer.android.com/kotlin/flow#catch)
- [Exponential backoff - Wikipedia](https://en.wikipedia.org/wiki/Exponential_backoff)

## Related Questions

### Related (Medium)
- [[q-coroutine-exception-handling--kotlin--medium]] - Coroutines
- [[q-catch-operator-flow--kotlin--medium]] - Flow
- [[q-retry-operators-flow--kotlin--medium]] - Flow
- [[q-instant-search-flow-operators--kotlin--medium]] - Flow

### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
### Related (Medium)
- [[q-coroutine-exception-handling--kotlin--medium]] - Coroutines
- [[q-catch-operator-flow--kotlin--medium]] - Flow
- [[q-retry-operators-flow--kotlin--medium]] - Flow
- [[q-instant-search-flow-operators--kotlin--medium]] - Flow

### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
### Related (Medium)
- [[q-coroutine-exception-handling--kotlin--medium]] - Coroutines
- [[q-catch-operator-flow--kotlin--medium]] - Flow
- [[q-retry-operators-flow--kotlin--medium]] - Flow
- [[q-instant-search-flow-operators--kotlin--medium]] - Flow

### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines
### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction

### Related (Medium)
- [[q-hot-cold-flows--kotlin--medium]] - Hot vs Cold flows
- [[q-cold-vs-hot-flows--kotlin--medium]] - Cold vs Hot flows explained
- [[q-flow-vs-livedata-comparison--kotlin--medium]] - Flow vs LiveData
- [[q-channels-vs-flow--kotlin--medium]] - Channels vs Flow
- [[q-sharedflow-stateflow--kotlin--medium]] - SharedFlow vs StateFlow

### Advanced (Harder)
- [[q-flowon-operator-context-switching--kotlin--hard]] - flowOn & context switching
- [[q-flow-backpressure--kotlin--hard]] - Backpressure handling
- [[q-flow-backpressure-strategies--kotlin--hard]] - Backpressure strategies
