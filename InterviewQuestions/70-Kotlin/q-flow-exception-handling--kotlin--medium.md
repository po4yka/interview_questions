---
anki_cards:
- slug: q-flow-exception-handling--kotlin--medium-0-en
  language: en
  anki_id: 1768326283655
  synced_at: '2026-01-23T17:03:50.806990'
- slug: q-flow-exception-handling--kotlin--medium-0-ru
  language: ru
  anki_id: 1768326283682
  synced_at: '2026-01-23T17:03:50.808719'
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

**English Summary**: `Flow` exception handling uses `catch` for handling upstream exceptions, `retry` for automatic retries, and `retryWhen` for conditional retry logic. Exponential backoff with jitter is a standard retry strategy. The `catch` operator only handles exceptions from upstream, not from the `collect` block. Combine error handling strategies with `timeout` and circuit breaker patterns for robust applications. Provide fallback values or error states for UI flows (e.g., `StateFlow`/`SharedFlow`) where appropriate.

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
- [[q-catch-operator-flow--kotlin--medium]] - `Flow`
- [[q-retry-operators-flow--kotlin--medium]] - `Flow`
- [[q-instant-search-flow-operators--kotlin--medium]] - `Flow`

### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive `Flow` introduction
