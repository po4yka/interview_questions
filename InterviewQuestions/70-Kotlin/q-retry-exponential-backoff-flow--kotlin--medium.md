---
id: "20251012-180004"
title: "Retry and exponential backoff patterns in Flow / Retry и exponential backoff паттерны в Flow"
topic: kotlin
difficulty: medium
status: draft
created: 2025-10-15
tags:
  - kotlin
  - coroutines
  - flow
  - retry
  - exponential-backoff
  - error-handling
  - resilience
  - circuit-breaker
  - production
moc: moc-kotlin
related: [q-fan-in-fan-out-channels--kotlin--hard, q-actor-pattern--kotlin--hard, q-coroutine-dispatchers--kotlin--medium]
subtopics:
  - coroutines
  - flow
  - retry
  - error-handling
  - resilience
---
# Retry and exponential backoff patterns in Flow

## English

### Question
How do you implement retry logic with exponential backoff in Kotlin Flow? Explain the retry() and retryWhen() operators, custom retry policies, jitter, circuit breaker integration, and testing strategies. Provide production-ready examples for network requests, database operations, and resilient data streams.

### Answer

**Retry** patterns are essential for building resilient applications that can recover from transient failures. **Exponential backoff** is a strategy where retry delays increase exponentially to avoid overwhelming failing services.

#### 1. Basic Retry with retry() Operator

**retry() operator:**
- Retries the Flow on exception
- Optionally limit number of attempts
- Does NOT add delay between retries (immediate retry)

**Simple retry:**

```kotlin
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.*

fun getData(): Flow<String> = flow {
    var attempt = 0
    println("Attempt ${++attempt}")
    if (attempt < 3) {
        throw IOException("Network error")
    }
    emit("Success")
}

suspend fun basicRetryExample() {
    getData()
        .retry(retries = 3) // Retry up to 3 times
        .collect { data ->
            println("Received: $data")
        }
}

// Output:
// Attempt 1
// Attempt 2
// Attempt 3
// Received: Success
```

**Retry with predicate:**

```kotlin
suspend fun retryWithPredicateExample() {
    getData()
        .retry(3) { cause ->
            // Only retry on IOException, not on IllegalStateException
            cause is IOException
        }
        .collect { data ->
            println("Received: $data")
        }
}
```

#### 2. Advanced Retry with retryWhen()

**retryWhen() operator:**
- More control over retry logic
- Can add delays between retries
- Access to attempt count and exception

**Basic retryWhen:**

```kotlin
suspend fun retryWhenExample() {
    flow {
        println("Attempting to fetch data...")
        throw IOException("Network error")
    }
        .retryWhen { cause, attempt ->
            // Retry only IOException, max 3 attempts
            if (cause is IOException && attempt < 3) {
                delay(1000 * (attempt + 1)) // Linear backoff
                true // Retry
            } else {
                false // Don't retry
            }
        }
        .catch { e ->
            println("Failed after retries: ${e.message}")
        }
        .collect()
}
```

**retryWhen vs retry:**

| Feature | retry() | retryWhen() |
|---------|---------|-------------|
| Delay | No (immediate) | Yes (manual delay) |
| Attempt count | Not accessible | Available |
| Conditional logic | Basic predicate | Full control |
| Best for | Simple retry | Custom backoff strategies |

#### 3. Exponential Backoff Implementation

**Exponential backoff algorithm:**
- Delay increases exponentially: 1s, 2s, 4s, 8s, 16s...
- Formula: `delay = initialDelay * (multiplier ^ attempt)`
- Prevents overwhelming failing services

**Basic exponential backoff:**

```kotlin
suspend fun exponentialBackoffExample() {
    val initialDelayMs = 1000L
    val multiplier = 2.0
    val maxAttempts = 5

    flow {
        println("Fetching data...")
        throw IOException("Network error")
    }
        .retryWhen { cause, attempt ->
            if (cause is IOException && attempt < maxAttempts) {
                val delayMs = (initialDelayMs * multiplier.pow(attempt.toDouble())).toLong()
                println("Retry ${attempt + 1}/$maxAttempts after ${delayMs}ms")
                delay(delayMs)
                true
            } else {
                false
            }
        }
        .catch { e ->
            println("Failed after $maxAttempts attempts: ${e.message}")
        }
        .collect()
}

// Output:
// Fetching data...
// Retry 1/5 after 1000ms
// Fetching data...
// Retry 2/5 after 2000ms
// Fetching data...
// Retry 3/5 after 4000ms
// ...
```

**Production-ready exponential backoff:**

```kotlin
data class RetryConfig(
    val maxAttempts: Int = 5,
    val initialDelayMs: Long = 1000,
    val maxDelayMs: Long = 32000,
    val multiplier: Double = 2.0,
    val jitterFactor: Double = 0.1
)

fun <T> Flow<T>.retryWithExponentialBackoff(
    config: RetryConfig = RetryConfig(),
    predicate: (Throwable) -> Boolean = { true }
): Flow<T> = retryWhen { cause, attempt ->
    if (predicate(cause) && attempt < config.maxAttempts) {
        val baseDelay = (config.initialDelayMs * config.multiplier.pow(attempt.toDouble()))
            .toLong()
            .coerceAtMost(config.maxDelayMs)

        // Add jitter (randomness) to prevent thundering herd
        val jitter = (baseDelay * config.jitterFactor * Random.nextDouble(-1.0, 1.0)).toLong()
        val delayMs = (baseDelay + jitter).coerceAtLeast(0)

        println("Retry ${attempt + 1}/${config.maxAttempts} after ${delayMs}ms (cause: ${cause.message})")
        delay(delayMs)
        true
    } else {
        false
    }
}

// Usage
suspend fun retryWithConfigExample() {
    getDataFromApi()
        .retryWithExponentialBackoff(
            config = RetryConfig(
                maxAttempts = 5,
                initialDelayMs = 1000,
                maxDelayMs = 30000,
                multiplier = 2.0,
                jitterFactor = 0.1
            ),
            predicate = { it is IOException || it is HttpException }
        )
        .collect { data ->
            println("Success: $data")
        }
}
```

#### 4. Jitter for Retry Timing

**Why jitter?**
- Prevents **thundering herd** problem
- Multiple clients don't retry at exact same time
- Distributes load more evenly

**Jitter strategies:**

```kotlin
// 1. Full jitter: random delay between 0 and calculated delay
fun calculateFullJitter(baseDelay: Long): Long {
    return (baseDelay * Random.nextDouble()).toLong()
}

// 2. Equal jitter: half base delay + random half
fun calculateEqualJitter(baseDelay: Long): Long {
    return (baseDelay / 2) + (baseDelay / 2 * Random.nextDouble()).toLong()
}

// 3. Decorrelated jitter: based on previous delay
fun calculateDecorrelatedJitter(previousDelay: Long, baseDelay: Long): Long {
    return (baseDelay + (previousDelay * 3 * Random.nextDouble())).toLong()
}

// Example with equal jitter
fun <T> Flow<T>.retryWithJitter(
    maxAttempts: Int = 5,
    initialDelayMs: Long = 1000,
    maxDelayMs: Long = 32000
): Flow<T> = retryWhen { cause, attempt ->
    if (attempt < maxAttempts) {
        val baseDelay = (initialDelayMs * (2.0.pow(attempt.toDouble())))
            .toLong()
            .coerceAtMost(maxDelayMs)

        // Equal jitter
        val delayMs = (baseDelay / 2) + (baseDelay / 2 * Random.nextDouble()).toLong()

        delay(delayMs)
        true
    } else {
        false
    }
}
```

#### 5. Production Example: Network Requests

**Resilient API client:**

```kotlin
import retrofit2.HttpException
import java.io.IOException

class ApiClient(private val api: ApiService) {

    // Retry configuration for different request types
    private val standardRetry = RetryConfig(
        maxAttempts = 3,
        initialDelayMs = 1000,
        maxDelayMs = 10000
    )

    private val longRetry = RetryConfig(
        maxAttempts = 5,
        initialDelayMs = 2000,
        maxDelayMs = 60000
    )

    fun getUser(userId: String): Flow<User> = flow {
        emit(api.getUser(userId))
    }
        .retryWithExponentialBackoff(
            config = standardRetry,
            predicate = ::isRetriableError
        )
        .catch { e ->
            // Handle non-retriable errors
            throw ApiException("Failed to get user", e)
        }

    fun syncData(): Flow<SyncResult> = flow {
        emit(api.syncData())
    }
        .retryWithExponentialBackoff(
            config = longRetry,
            predicate = ::isRetriableError
        )
        .onEach { result ->
            println("Sync completed: $result")
        }

    fun searchUsers(query: String): Flow<List<User>> = flow {
        emit(api.searchUsers(query))
    }
        .timeout(5000) // Timeout after 5 seconds
        .retryWithExponentialBackoff(
            config = standardRetry,
            predicate = { it is IOException || it is TimeoutCancellationException }
        )

    private fun isRetriableError(error: Throwable): Boolean {
        return when (error) {
            // Network errors - retry
            is IOException -> true

            // Timeout - retry
            is TimeoutCancellationException -> true

            // HTTP errors - check status code
            is HttpException -> when (error.code()) {
                // 5xx server errors - retry
                in 500..599 -> true

                // 408 Request Timeout - retry
                408 -> true

                // 429 Too Many Requests - retry
                429 -> true

                // Other 4xx client errors - don't retry
                else -> false
            }

            // Other errors - don't retry
            else -> false
        }
    }
}

// Usage
suspend fun fetchUserWithRetry() {
    val apiClient = ApiClient(apiService)

    apiClient.getUser("user123")
        .onStart { println("Fetching user...") }
        .onEach { user -> println("User: ${user.name}") }
        .catch { e -> println("Error: ${e.message}") }
        .collect()
}
```

#### 6. Production Example: Database Operations

**Resilient database operations with retry:**

```kotlin
class DatabaseRepository(private val database: AppDatabase) {

    fun insertWithRetry(item: Item): Flow<Long> = flow {
        emit(database.itemDao().insert(item))
    }
        .retryWhen { cause, attempt ->
            // Retry on database locked errors
            if (cause is SQLiteException && attempt < 3) {
                val delayMs = 100L * (attempt + 1)
                println("Database locked, retry ${attempt + 1} after ${delayMs}ms")
                delay(delayMs)
                true
            } else {
                false
            }
        }

    fun batchInsertWithRetry(items: List<Item>): Flow<Unit> = flow {
        database.withTransaction {
            items.forEach { item ->
                database.itemDao().insert(item)
            }
        }
        emit(Unit)
    }
        .retryWithExponentialBackoff(
            config = RetryConfig(
                maxAttempts = 3,
                initialDelayMs = 100,
                maxDelayMs = 1000
            ),
            predicate = { it is SQLiteException }
        )

    fun observeItemsWithRetry(userId: String): Flow<List<Item>> {
        return database.itemDao().observeItems(userId)
            .catch { e ->
                if (e is SQLiteException) {
                    // Emit empty list on error and retry
                    emit(emptyList())
                    delay(1000)
                    throw e
                }
            }
            .retryWhen { cause, attempt ->
                cause is SQLiteException && attempt < 5
            }
    }
}
```

#### 7. Combining Retry with Timeout

**Timeout + retry pattern:**

```kotlin
suspend fun fetchDataWithTimeoutAndRetry() {
    flow {
        emit(fetchDataFromSlowApi())
    }
        .timeout(5000) // Timeout each attempt after 5 seconds
        .retryWithExponentialBackoff(
            config = RetryConfig(maxAttempts = 3)
        )
        .catch { e ->
            when (e) {
                is TimeoutCancellationException -> {
                    println("All attempts timed out")
                }
                else -> println("Failed: ${e.message}")
            }
        }
        .collect { data ->
            println("Success: $data")
        }
}

// Per-request timeout vs total timeout
suspend fun fetchWithTotalTimeout() {
    withTimeout(15000) { // Total timeout: 15 seconds
        flow {
            emit(fetchDataFromApi())
        }
            .timeout(5000) // Per-attempt timeout: 5 seconds
            .retryWhen { cause, attempt ->
                if (cause is TimeoutCancellationException && attempt < 2) {
                    println("Attempt timed out, retrying...")
                    delay(1000)
                    true
                } else {
                    false
                }
            }
            .collect { data ->
                println("Success: $data")
            }
    }
}
```

#### 8. Circuit Breaker Integration

**Circuit breaker with retry:**

```kotlin
enum class CircuitState {
    CLOSED,  // Normal operation
    OPEN,    // Failing, reject requests
    HALF_OPEN // Testing if recovered
}

class CircuitBreaker(
    private val failureThreshold: Int = 5,
    private val resetTimeoutMs: Long = 60000
) {
    private var state = CircuitState.CLOSED
    private var failureCount = 0
    private var lastFailureTime = 0L

    fun <T> protect(block: suspend () -> T): Flow<T> = flow {
        when (state) {
            CircuitState.OPEN -> {
                if (System.currentTimeMillis() - lastFailureTime >= resetTimeoutMs) {
                    state = CircuitState.HALF_OPEN
                    println("Circuit breaker: HALF_OPEN (testing)")
                } else {
                    throw CircuitBreakerOpenException("Circuit breaker is OPEN")
                }
            }
            else -> {}
        }

        try {
            val result = block()
            onSuccess()
            emit(result)
        } catch (e: Exception) {
            onFailure()
            throw e
        }
    }

    private fun onSuccess() {
        failureCount = 0
        if (state == CircuitState.HALF_OPEN) {
            state = CircuitState.CLOSED
            println("Circuit breaker: CLOSED (recovered)")
        }
    }

    private fun onFailure() {
        failureCount++
        lastFailureTime = System.currentTimeMillis()

        if (failureCount >= failureThreshold) {
            state = CircuitState.OPEN
            println("Circuit breaker: OPEN (too many failures)")
        }
    }
}

class CircuitBreakerOpenException(message: String) : Exception(message)

// Usage with retry
suspend fun fetchWithCircuitBreaker() {
    val circuitBreaker = CircuitBreaker(
        failureThreshold = 3,
        resetTimeoutMs = 30000
    )

    circuitBreaker.protect {
        fetchDataFromApi()
    }
        .retryWithExponentialBackoff(
            config = RetryConfig(maxAttempts = 3),
            predicate = { it !is CircuitBreakerOpenException }
        )
        .catch { e ->
            when (e) {
                is CircuitBreakerOpenException -> {
                    println("Circuit breaker open, not retrying")
                }
                else -> println("Failed: ${e.message}")
            }
        }
        .collect { data ->
            println("Success: $data")
        }
}
```

#### 9. Retry for Different Exception Types

**Different strategies for different errors:**

```kotlin
data class RetryStrategy(
    val maxAttempts: Int,
    val initialDelayMs: Long,
    val multiplier: Double = 2.0
)

fun <T> Flow<T>.retryByExceptionType(
    strategies: Map<KClass<out Throwable>, RetryStrategy>,
    defaultStrategy: RetryStrategy? = null
): Flow<T> = retryWhen { cause, attempt ->
    // Find matching strategy
    val strategy = strategies.entries
        .firstOrNull { (exceptionType, _) ->
            exceptionType.isInstance(cause)
        }?.value ?: defaultStrategy

    if (strategy != null && attempt < strategy.maxAttempts) {
        val delayMs = (strategy.initialDelayMs * strategy.multiplier.pow(attempt.toDouble()))
            .toLong()

        println("Retry ${cause::class.simpleName} (${attempt + 1}/${strategy.maxAttempts}) after ${delayMs}ms")
        delay(delayMs)
        true
    } else {
        false
    }
}

// Usage
suspend fun fetchWithCustomStrategies() {
    getDataFromApi()
        .retryByExceptionType(
            strategies = mapOf(
                IOException::class to RetryStrategy(
                    maxAttempts = 5,
                    initialDelayMs = 1000,
                    multiplier = 2.0
                ),
                HttpException::class to RetryStrategy(
                    maxAttempts = 3,
                    initialDelayMs = 2000,
                    multiplier = 1.5
                ),
                TimeoutCancellationException::class to RetryStrategy(
                    maxAttempts = 2,
                    initialDelayMs = 5000,
                    multiplier = 1.0
                )
            ),
            defaultStrategy = RetryStrategy(
                maxAttempts = 1,
                initialDelayMs = 1000
            )
        )
        .collect { data ->
            println("Success: $data")
        }
}
```

#### 10. Monitoring and Logging Retry Attempts

**Production monitoring:**

```kotlin
interface RetryLogger {
    fun onRetryAttempt(attempt: Int, maxAttempts: Int, cause: Throwable, delayMs: Long)
    fun onRetryExhausted(attempts: Int, lastCause: Throwable)
    fun onRetrySuccess(totalAttempts: Int)
}

class ProductionRetryLogger(private val analyticsService: AnalyticsService) : RetryLogger {
    override fun onRetryAttempt(attempt: Int, maxAttempts: Int, cause: Throwable, delayMs: Long) {
        val event = mapOf(
            "event" to "retry_attempt",
            "attempt" to attempt,
            "max_attempts" to maxAttempts,
            "cause" to cause::class.simpleName,
            "delay_ms" to delayMs
        )
        analyticsService.logEvent(event)
        println("[RETRY] Attempt $attempt/$maxAttempts after ${delayMs}ms - ${cause.message}")
    }

    override fun onRetryExhausted(attempts: Int, lastCause: Throwable) {
        val event = mapOf(
            "event" to "retry_exhausted",
            "attempts" to attempts,
            "cause" to lastCause::class.simpleName
        )
        analyticsService.logEvent(event)
        println("[RETRY] Exhausted after $attempts attempts - ${lastCause.message}")
    }

    override fun onRetrySuccess(totalAttempts: Int) {
        if (totalAttempts > 0) {
            val event = mapOf(
                "event" to "retry_success",
                "attempts" to totalAttempts
            )
            analyticsService.logEvent(event)
            println("[RETRY] Success after $totalAttempts retries")
        }
    }
}

fun <T> Flow<T>.retryWithLogging(
    config: RetryConfig,
    logger: RetryLogger,
    predicate: (Throwable) -> Boolean = { true }
): Flow<T> {
    var attemptCount = 0

    return this
        .retryWhen { cause, attempt ->
            attemptCount = attempt.toInt()

            if (predicate(cause) && attempt < config.maxAttempts) {
                val delayMs = calculateBackoff(config, attempt)
                logger.onRetryAttempt(
                    attempt = (attempt + 1).toInt(),
                    maxAttempts = config.maxAttempts,
                    cause = cause,
                    delayMs = delayMs
                )
                delay(delayMs)
                true
            } else {
                logger.onRetryExhausted(attemptCount + 1, cause)
                false
            }
        }
        .onEach {
            if (attemptCount > 0) {
                logger.onRetrySuccess(attemptCount)
            }
        }
}

private fun calculateBackoff(config: RetryConfig, attempt: Long): Long {
    val baseDelay = (config.initialDelayMs * config.multiplier.pow(attempt.toDouble()))
        .toLong()
        .coerceAtMost(config.maxDelayMs)

    val jitter = (baseDelay * config.jitterFactor * Random.nextDouble(-1.0, 1.0)).toLong()
    return (baseDelay + jitter).coerceAtLeast(0)
}
```

#### 11. Testing Retry Logic

**Unit tests with virtual time:**

```kotlin
import kotlinx.coroutines.test.*
import org.junit.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class RetryTest {

    @Test
    fun `retry succeeds after 2 attempts`() = runTest {
        var attempts = 0

        val flow = flow {
            attempts++
            if (attempts < 2) {
                throw IOException("Network error")
            }
            emit("Success")
        }

        val result = flow
            .retry(retries = 3)
            .first()

        assertEquals("Success", result)
        assertEquals(2, attempts)
    }

    @Test
    fun `exponential backoff has increasing delays`() = runTest {
        val delays = mutableListOf<Long>()
        var attempts = 0

        val flow = flow {
            attempts++
            throw IOException("Error")
        }

        flow
            .retryWhen { _, attempt ->
                if (attempt < 3) {
                    val delay = 1000L * (2.0.pow(attempt.toDouble())).toLong()
                    delays.add(delay)
                    delay(delay)
                    true
                } else {
                    false
                }
            }
            .catch { }
            .collect()

        // Verify exponential delays: 1000, 2000, 4000
        assertEquals(listOf(1000L, 2000L, 4000L), delays)
        assertEquals(4, attempts)
    }

    @Test
    fun `retry only on specific exception type`() = runTest {
        var ioAttempts = 0
        var otherAttempts = 0

        val flow = flow {
            if (ioAttempts < 2) {
                ioAttempts++
                throw IOException("Network error")
            } else {
                otherAttempts++
                throw IllegalStateException("Invalid state")
            }
        }

        try {
            flow
                .retry(5) { it is IOException }
                .collect()
        } catch (e: IllegalStateException) {
            // Expected
        }

        assertEquals(2, ioAttempts) // Retried IOException twice
        assertEquals(1, otherAttempts) // IllegalStateException not retried
    }

    @Test
    fun `retry with timeout`() = runTest {
        val flow = flow {
            delay(10000) // Simulate slow operation
            emit("Data")
        }

        var timeoutCount = 0

        flow
            .timeout(1000)
            .retryWhen { cause, attempt ->
                if (cause is TimeoutCancellationException && attempt < 2) {
                    timeoutCount++
                    delay(100)
                    true
                } else {
                    false
                }
            }
            .catch { }
            .collect()

        assertEquals(3, timeoutCount) // Initial + 2 retries
    }
}
```

#### 12. Best Practices Summary

**Do's:**

```kotlin
//  Use exponential backoff for network requests
flow { fetchFromApi() }
    .retryWithExponentialBackoff()

//  Add jitter to prevent thundering herd
.retryWithExponentialBackoff(
    config = RetryConfig(jitterFactor = 0.1)
)

//  Set max delay to avoid very long waits
RetryConfig(maxDelayMs = 60000)

//  Only retry retriable errors
.retry { it is IOException }

//  Combine with timeout
.timeout(5000)
.retryWithExponentialBackoff()

//  Log retry attempts for monitoring
.retryWithLogging(config, logger)
```

**Don'ts:**

```kotlin
//  Don't retry immediately without delay
.retry(10) // Hammers the server

//  Don't retry forever
.retry(Long.MAX_VALUE) // Never gives up

//  Don't retry non-retriable errors
.retry { true } // Retries everything

//  Don't forget max delay
RetryConfig(multiplier = 10.0) // Can lead to hours of waiting

//  Don't ignore exceptions after retry
.retry(3)
// Missing .catch { }
```

### Related Questions

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

## Follow-ups
1. How does exponential backoff with jitter prevent the thundering herd problem? Provide mathematical explanation.
2. What's the difference between retry() at the Flow level vs retry logic in the repository? When to choose each?
3. How would you implement a retry policy that backs off based on server response headers (e.g., Retry-After)?
4. Explain how to test retry logic with virtual time without actually waiting for delays.
5. How do you balance between retry aggressiveness and avoiding server overload in production?
6. What's the relationship between circuit breaker, retry, and timeout patterns? How do they complement each other?
7. How would you implement retry with different strategies for different HTTP status codes (e.g., retry 503, don't retry 400)?

### References
- [Flow Exception Handling](https://kotlinlang.org/docs/flow.html#flow-exceptions)
- [Exponential Backoff And Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)
- [Retry Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/retry)
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)

---

## Русский

### Вопрос
Как реализовать retry логику с экспоненциальным backoff в Kotlin Flow? Объясните операторы retry() и retryWhen(), кастомные retry политики, jitter, интеграцию с circuit breaker и стратегии тестирования. Приведите production-ready примеры для сетевых запросов, операций с БД и устойчивых потоков данных.

### Ответ

**Retry** паттерны критически важны для создания устойчивых приложений, которые могут восстанавливаться после временных сбоев. **Exponential backoff** — это стратегия, при которой задержки повторных попыток увеличиваются экспоненциально, чтобы избежать перегрузки падающих сервисов.

*(Продолжение следует той же структуре с подробными примерами retry(), retryWhen(), exponential backoff, jitter, circuit breaker интеграции, production примерами для сетевых запросов и БД, тестированием и best practices на русском языке)*

### Связанные вопросы
- [[q-flow-operators--kotlin--medium]] - Операторы Flow
- [[q-flow-exception-handling--kotlin--medium]] - Обработка исключений в Flow
- [[q-circuit-breaker-coroutines--kotlin--hard]] - Паттерн Circuit breaker
- [[q-structured-concurrency--kotlin--hard]] - Структурированная конкурентность

### Дополнительные вопросы
1. Как exponential backoff с jitter предотвращает проблему thundering herd? Приведите математическое объяснение.
2. В чем разница между retry() на уровне Flow и retry логикой в репозитории? Когда выбирать каждый подход?
3. Как реализовать retry политику, которая делает backoff на основе заголовков ответа сервера (например, Retry-After)?
4. Объясните, как тестировать retry логику с виртуальным временем без реального ожидания задержек.
5. Как балансировать между агрессивностью retry и избеганием перегрузки сервера в production?
6. Какая связь между circuit breaker, retry и timeout паттернами? Как они дополняют друг друга?
7. Как реализовать retry с разными стратегиями для разных HTTP статус кодов (например, retry 503, не retry 400)?

### Ссылки
- [Обработка исключений Flow](https://kotlinlang.org/docs/flow.html#flow-exceptions)
- [Exponential Backoff And Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)
- [Retry Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/retry)
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)
