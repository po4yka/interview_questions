---
id: kotlin-052
title: "Flow Exception Handling / Обработка исключений в Flow"
aliases: ["Flow Exception Handling", "Обработка исключений в Flow"]

# Classification
topic: kotlin
subtopics: [coroutines, error-handling, flow]
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
related: [c-flow, c-kotlin, q-catch-operator-flow--kotlin--medium, q-coroutine-exception-handling--kotlin--medium, q-kotlin-flow-basics--kotlin--medium]

# Timestamps
created: 2025-10-11
updated: 2025-11-09

tags: [catch, difficulty/medium, error-handling, exceptions, flow, kotlin, retry]
date created: Saturday, October 18th 2025, 3:12:22 pm
date modified: Tuesday, November 25th 2025, 8:53:51 pm
---
# Вопрос (RU)
> Как обрабатывать исключения в `Flow`? Объясните операторы catch, retry, retryWhen. Реализуйте стратегию повтора с экспоненциальной задержкой.

# Question (EN)
> How do you handle exceptions in `Flow`s? Explain catch, retry, retryWhen operators. Implement exponential backoff retry strategy.

## Ответ (RU)

Обработка исключений в `Flow` критична для построения надежных приложений. Kotlin `Flow` предоставляет несколько операторов для изящной обработки ошибок (см. также [[c-flow]]).

### Принцип Прозрачности Исключений

`Flow` следует принципу **прозрачности исключений**: оператор `catch` может перехватывать только исключения из upstream-части (выше по цепочке операторов) и не влияет на код ниже по потоку, где он сам расположен.

```kotlin
//  Неправильно: catch не перехватывает исключения ниже по потоку
flow {
    emit(1)
    throw Exception("Ошибка в flow")
}
.map { it * 2 }
.catch { /* Ловит исключения только из flow и map выше */ }
.collect { value ->
    // Исключение здесь не будет поймано catch выше
    println(value)
}

//  Правильно: catch размещен после всех операторов, чьи исключения нужно обработать
flow {
    emit(1)
    throw Exception("Ошибка в flow")
}
.map { it * 2 }
.catch { /* Это ловит исключения из flow и map */ }
.collect()
```

### Оператор Catch

Оператор `catch` перехватывает исключения из upstream и позволяет их обработать.

#### Базовое Использование

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

#### Свойства Catch

1. Перехватывает только исключения из upstream (не исключения внутри `collect`).
2. Может эмитить fallback-значения.
3. Может пробрасывать исключение дальше (rethrow) для внешних обработчиков.
4. Соблюдает прозрачность исключений: не скрывает несвязанные ошибки downstream.

```kotlin
flow {
    emit(1)
    throw IOException("Сетевая ошибка")
}
.catch { e ->
    when (e) {
        is IOException -> emit(-1) // Fallback
        else -> throw e // Проброс других исключений
    }
}
.collect { value ->
    println("Получено: $value")
    // Исключения здесь не ловятся catch выше
}
```

### Реальный Пример: Сетевой Запрос С Fallback

```kotlin
data class Article(val id: Int, val title: String, val cached: Boolean = false)

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

### Оператор Retry

Оператор `retry` автоматически перезапускает весь upstream-поток при возникновении исключения.

#### Простой Retry

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

#### Условный Retry

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

#### Помощник Retry С Фиксированной Задержкой

```kotlin
fun <T> Flow<T>.retryWithDelay(
    retries: Long,
    delayMillis: Long
): Flow<T> = retry(retries) { cause ->
    // Выполнять повтор только для временных ошибок
    if (cause is IOException) {
        delay(delayMillis)
        true
    } else {
        false
    }
}

// Использование
fetchDataFlow()
    .retryWithDelay(retries = 3, delayMillis = 1000)
    .collect { data -> processData(data) }
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

### Реализация Экспоненциальной Задержки

Экспоненциальная задержка — стандартная стратегия обработки ошибок, где задержки повтора растут экспоненциально.

```kotlin
import kotlin.math.pow
import kotlin.random.Random

/**
 * Повтор с экспоненциальной задержкой.
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

        // Добавить jitter (случайный сдвиг) для избежания "стада"
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

#### Зачем Нужен Jitter?

Jitter предотвращает проблему "стада", когда все клиенты повторяют запросы одновременно.

```kotlin
// Без jitter - все клиенты повторяют одновременно
// Клиент 1: повтор в 1000мс, 2000мс, 4000мс
// Клиент 2: повтор в 1000мс, 2000мс, 4000мс

// С jitter - повторы распределены
// Клиент 1: повтор в 1050мс, 2150мс, 4200мс
// Клиент 2: повтор в 1100мс, 1900мс, 3800мс
```

### Продвинутый Паттерн: Circuit Breaker

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
                if (System.currentTimeMillis() - lastFailureTime > resetTimeoutMs) {
                    state = State.HALF_OPEN
                } else {
                    throw CircuitBreakerOpenException("Circuit breaker открыт")
                }
            }
            State.HALF_OPEN, State.CLOSED -> {
                // Разрешить запрос
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
        }
    }
}

class CircuitBreakerOpenException(message: String) : Exception(message)
```

#### Использование Circuit Breaker С `Flow`

```kotlin
fun <T> Flow<T>.withCircuitBreaker(
    circuitBreaker: CircuitBreaker
): Flow<T> = flow {
    circuitBreaker.execute {
        // collect из исходного Flow внутри circuit breaker
        collect { value ->
            emit(value)
        }
    }
}.catch { exception ->
    if (exception is CircuitBreakerOpenException) {
        println("Запрос заблокирован circuit breaker")
        // Здесь можно эмитить fallback или пробросить дальше
    } else {
        throw exception
    }
}
```

### Комбинирование Стратегий Обработки Ошибок

```kotlin
// Комплексная обработка ошибок
fun <T> Flow<T>.withRobustErrorHandling(
    maxRetries: Int = 3,
    timeout: Duration = 30.seconds,
    fallback: T? = null
): Flow<T> = this
    .timeout(timeout)
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

### Обработка Ошибок В `StateFlow`/`SharedFlow`

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
                        exception.message ?: "Неизвестная ошибка"
                    )
                }
                .collect { user ->
                    _uiState.value = UiState.Success(user)
                }
        }
    }
}
```

### Лучшие Практики

1. **Для важных потоков явно обрабатывайте ошибки с помощью catch**:
   ```kotlin
   // Необработанное исключение отменит корутину
   flow { emit(api.getData()) }.collect()

   // Явная обработка ошибки
   flow { emit(api.getData()) }
       .catch { emit(defaultData) }
       .collect()
   ```

2. **Размещайте catch после всех трансформаций, которые хотите покрыть**:
   ```kotlin
   flow { }
       .map { }
       .filter { }
       .catch { }
       .collect()
   ```

3. **Не рассчитывайте, что catch обработает исключения в collect** (переносите броски в onEach/операторы выше, чтобы catch мог их перехватить):
   ```kotlin
   // Неверно: исключение в collect не поймается
   .catch { emit(default) }
   .collect { throw Exception() }

   // Верно: бросаем выше по цепочке
   .onEach { if (error) throw Exception() }
   .catch { emit(default) }
   .collect()
   ```

4. **Используйте retry только для временных ошибок**:
   ```kotlin
   .retry { exception ->
       exception is IOException || exception is TimeoutException
   }
   ```

5. **Комбинируйте с timeout**:
   ```kotlin
   .timeout(30.seconds)
   .retryWithExponentialBackoff()
   .catch { }
   ```

### Распространенные Ошибки

1. **Обработка исключений только внутри collect**:
   ```kotlin
   // catch не перехватит это исключение
   .catch { emit(default) }
   .collect { throw Exception() }

   // Нужно переносить в onEach
   .onEach { if (error) throw Exception() }
   .catch { emit(default) }
   .collect()
   ```

2. **Бесконечный retry без условий**:
   ```kotlin
   // Будет повторять бесконечно, даже для неустранимых ошибок
   .retry { true }

   // Ограничиваем и фильтруем по типу
   .retry(3) { it is IOException }
   ```

3. **Игнорирование типов ошибок**:
   ```kotlin
   // Повторяет в том числе на логических/авторизационных ошибках
   .retry(5)

   // Повторяем только для восстанавливаемых ошибок
   .retry(5) { it is IOException }
   ```

4. **Отсутствие timeout**:
   ```kotlin
   // Поток может "висеть" бесконечно
   .retry(3)

   // Добавляем timeout
   .timeout(30.seconds)
   .retry(3)
   ```

**Краткое содержание**: Обработка исключений в `Flow` использует `catch` для обработки upstream-исключений, `retry` для автоматических повторов и `retryWhen` для условной логики повтора. Экспоненциальная задержка с jitter — стандартная стратегия повтора. Оператор `catch` обрабатывает только исключения из upstream, а не из блока `collect`. Комбинируйте стратегии обработки ошибок с timeout и circuit breaker для надежных приложений. Для UI-потоков (например, `StateFlow`/`SharedFlow`) предоставляйте понятные состояния ошибок.

---

## Answer (EN)

Exception handling in `Flow`s is crucial for building robust applications. Kotlin `Flow` provides several operators for handling errors gracefully (see also [[c-flow]]).

### Exception Transparency Principle

`Flow` follows the **exception transparency** principle: the `catch` operator can only intercept exceptions from its upstream (operators before it in the chain) and does not affect code placed downstream of it.

```kotlin
//  Incorrect: catch does not handle exceptions thrown downstream in collect
flow {
    emit(1)
    throw Exception("Error in flow")
}
.map { it * 2 }
.catch { /* Catches exceptions from flow and map above */ }
.collect { value ->
    // Exception here will NOT be caught by catch above
    println(value)
}

//  Correct: place catch after all operators whose exceptions you want to handle
flow {
    emit(1)
    throw Exception("Error in flow")
}
.map { it * 2 }
.catch { /* This catches exceptions from flow and map */ }
.collect()
```

### The Catch Operator

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
```

#### Catch Properties

1. Only catches upstream exceptions (not exceptions from the `collect` block).
2. Can emit fallback values.
3. Can rethrow to propagate to outer handlers.
4. Respects exception transparency: it does not hide unrelated downstream errors.

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
    // Exceptions here are NOT caught by catch above
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
            throw ArticleNotFoundException("Article $id not found")
        }
    }
}
```

### The Retry Operator

The `retry` operator automatically restarts the upstream flow when an exception occurs.

```kotlin
fun <T> Flow<T>.retry(
    retries: Long = Long.MAX_VALUE,
    predicate: suspend (cause: Throwable) -> Boolean = { true }
): Flow<T>
```

#### Simple Retry

```kotlin
// Retry up to 3 times on any exception
flow {
    println("Attempting request...")
    val result = unstableNetworkCall()
    emit(result)
}
.retry(3)
.collect { println("Success: $it") }
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
// Simple retry with fixed delay for transient errors
fun <T> Flow<T>.retryWithDelay(
    retries: Long,
    delayMillis: Long
): Flow<T> = retry(retries) { cause ->
    if (cause is IOException) {
        delay(delayMillis)
        true
    } else {
        false
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

```kotlin
import kotlin.math.pow
import kotlin.random.Random

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
```

### Why Use Jitter?

Jitter prevents the "thundering herd" problem where multiple clients retry simultaneously:

```kotlin
// Without jitter - all clients retry at same time
// Client 1: retry at 1000ms, 2000ms, 4000ms
// Client 2: retry at 1000ms, 2000ms, 4000ms

// With jitter - retries spread out
// Client 1: retry at 1050ms, 2150ms, 4200ms
// Client 2: retry at 1100ms, 1900ms, 3800ms
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
    circuitBreaker.execute {
        // Collect from the original Flow inside the circuit breaker
        collect { value ->
            emit(value)
        }
    }
}.catch { exception ->
    if (exception is CircuitBreakerOpenException) {
        println("Request blocked by circuit breaker")
        // Emit fallback or rethrow as needed
    } else {
        throw exception
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
```

### Error Handling in `StateFlow`/`SharedFlow`

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

1. Always handle errors explicitly for critical flows:
   ```kotlin
   //  Unhandled exception cancels the coroutine (may crash app in top-level scope)
   flow { emit(api.getData()) }.collect()

   //  Graceful error handling
   flow { emit(api.getData()) }
       .catch { emit(defaultData) }
       .collect()
   ```

2. Place `catch` after all transformations you want to cover:
   ```kotlin
   flow { }
       .map { }
       .filter { }
       .catch { } // Handles all above
       .collect()
   ```

3. Don't expect `catch` to handle exceptions in `collect`:
   ```kotlin
   //  Wrong: catch doesn't handle this
   .catch { emit(default) }
   .collect { throw Exception() }

   //  Correct: handle in onEach so catch can see it
   .onEach { if (error) throw Exception() }
   .catch { emit(default) }
   .collect()
   ```

4. Use `retry` only for transient errors:
   ```kotlin
   .retry { exception ->
       exception is IOException ||
       exception is TimeoutException
   }
   ```

5. Combine with `timeout`:
   ```kotlin
   .timeout(30.seconds)
   .retryWithExponentialBackoff()
   .catch { }
   ```

### Common Pitfalls

1. Catching exceptions only inside `collect`:
   ```kotlin
   //  catch operator won't handle this
   .catch { emit(default) }
   .collect { throw Exception() }

   //  Use onEach instead
   .onEach { if (error) throw Exception() }
   .catch { emit(default) }
   .collect()
   ```

2. Infinite `retry`:
   ```kotlin
   //  Will retry forever, even on non-recoverable errors
   .retry { true }

   //  Limit retries and filter by error type
   .retry(3) { it is IOException }
   ```

3. Not considering error types:
   ```kotlin
   //  Retries on all errors, including auth/business logic
   .retry(5)

   //  Only retry recoverable errors
   .retry(5) { it is IOException }
   ```

4. Missing `timeout`:
   ```kotlin
   //  Can hang forever
   .retry(3)

   //  Add timeout
   .timeout(30.seconds)
   .retry(3)
   ```

**English Summary**: Flow exception handling uses `catch` for handling upstream exceptions, `retry` for automatic retries, and `retryWhen` for conditional retry logic. Exponential backoff with jitter is a standard retry strategy. The `catch` operator only handles exceptions from upstream, not from the `collect` block. Combine error handling strategies with `timeout` and circuit breaker patterns for robust applications. Provide fallback values or error states for UI flows (e.g., `StateFlow`/`SharedFlow`) where appropriate.

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

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

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive Flow introduction
