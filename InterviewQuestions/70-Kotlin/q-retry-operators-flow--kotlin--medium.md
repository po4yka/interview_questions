---
id: 20251006-004
title: "Retry and RetryWhen operators in Flow / Операторы Retry и RetryWhen во Flow"
aliases: []

# Classification
topic: kotlin
subtopics: [flow, retry, error-handling, operators]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/amitshekhariitbhu/android-interview-questions
source_note: Amit Shekhar Android Interview Questions repository - MEDIUM priority

# Workflow & relations
status: draft
moc: moc-kotlin
related: []

# Timestamps
created: 2025-10-06
updated: 2025-10-06

tags: [kotlin, flow, retry, error-handling, operators, difficulty/medium]
---

# Question (EN)
> What are Retry and RetryWhen operators in Kotlin Flow? How do they work?

# Вопрос (RU)
> Что такое операторы Retry и RetryWhen в Kotlin Flow? Как они работают?

---

## Answer (EN)

**`retry` and `retryWhen`** are Flow operators that automatically re-execute a flow when it encounters an exception, implementing resilient error handling.

### retry - Simple Retry Logic

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

**Characteristics:**
- **Retries immediately** after failure
- **Fixed number of retries** (or infinite if not specified)
- **Predicate** determines which exceptions to retry
- **Simple** - good for basic retry logic

### retry Signature

```kotlin
fun <T> Flow<T>.retry(
    retries: Long = Long.MAX_VALUE,
    predicate: suspend (cause: Throwable) -> Boolean = { true }
): Flow<T>
```

### Real-World retry Examples

**Example 1: Network Request with Retry**

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
    .retry() { exception ->  // Retry indefinitely
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
- **`attempt` parameter** - retry attempt number (0-indexed)
- **Custom delay** - implement exponential backoff
- **Conditional logic** - complex retry conditions
- **Access to FlowCollector** - can emit values during retry

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

### Comparison: retry vs retryWhen

| Feature | retry | retryWhen |
|---------|-------|-----------|
| **Delay** | No delay (immediate) | Custom delay (exponential backoff, etc.) |
| **Attempt count** | Not available | Available as parameter |
| **Complexity** | Simple | More flexible |
| **Use case** | Basic retry | Advanced retry strategies |

### Advanced Patterns

**Pattern 1: Retry with Timeout**

```kotlin
fun loadData(): Flow<Data> = flow {
    emit(api.getData())
}
.timeout(10.seconds)  // Timeout each attempt
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
        throw e  // Will be caught by retryWhen
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

**Pattern 4: Conditional Retry Based on Response**

```kotlin
sealed class ApiException(message: String) : Exception(message) {
    class RateLimited(val retryAfterSeconds: Long) : ApiException("Rate limited")
    class ServerError : ApiException("Server error")
    class ClientError : ApiException("Client error")
}

fun makeApiCall(): Flow<Response> = flow {
    val response = api.call()
    when (response.code) {
        200 -> emit(response)
        429 -> throw ApiException.RateLimited(response.retryAfter)
        in 500..599 -> throw ApiException.ServerError()
        else -> throw ApiException.ClientError()
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
    assertEquals(4, attempts)  // Initial + 3 retries
}

@Test
fun `retryWhen should apply exponential backoff`() = runTest {
    val delays = mutableListOf<Long>()
    val startTime = currentTime

    flow {
        if (delays.size < 3) {
            delays.add(currentTime - startTime)
            throw IOException()
        }
        emit("Success")
    }
    .retryWhen { cause, attempt ->
        if (cause is IOException && attempt < 3) {
            delay(1000 * (2.0.pow(attempt.toInt())).toLong())
            true
        } else false
    }
    .first()

    // Verify exponential delays: ~0ms, ~1000ms, ~2000ms
    assertTrue(delays[1] in 900..1100)
    assertTrue(delays[2] in 2900..3100)
}
```

### Best Practices

**1. Always use predicate to filter exceptions**

```kotlin
// ✅ GOOD - Only retry network errors
.retry(3) { it is IOException }

// ❌ BAD - Retries all exceptions
.retry(3)
```

**2. Implement exponential backoff for retryWhen**

```kotlin
// ✅ GOOD - Exponential backoff
.retryWhen { cause, attempt ->
    if (attempt < 5) {
        delay(1000 * (2.0.pow(attempt.toInt())).toLong())
        true
    } else false
}

// ❌ BAD - No delay, hammers server
.retryWhen { cause, attempt ->
    attempt < 5
}
```

**3. Set maximum retry attempts**

```kotlin
// ✅ GOOD - Limited retries
.retry(3) { it is IOException }

// ❌ BAD - Infinite retries can cause issues
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

**English Summary**: `retry` immediately retries flow on exception (fixed count, predicate filter). `retryWhen` provides advanced control (access to attempt number, custom delays, exponential backoff). Use `retry` for simple retry logic. Use `retryWhen` for exponential backoff, different strategies per error type, progress updates. Always filter exceptions, implement delays, set max attempts. Common patterns: exponential backoff, linear backoff with jitter, retry with timeout/fallback.

## Ответ (RU)

**`retry` и `retryWhen`** — операторы Flow, которые автоматически пере-выполняют flow при возникновении исключения, реализуя устойчивую обработку ошибок.

### retry - Простая логика повтора

**Базовый retry с подсчетом:**

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

**Характеристики:**
- **Повторяет немедленно** после сбоя
- **Фиксированное количество повторов** (или бесконечно если не указано)
- **Предикат** определяет какие исключения повторять
- **Просто** - хорошо для базовой логики повтора

### retryWhen - Продвинутая логика повтора

**`retryWhen` предоставляет контроль над временем и поведением повтора.**

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

### Сравнение: retry vs retryWhen

| Функция | retry | retryWhen |
|---------|-------|-----------|
| **Задержка** | Нет задержки (немедленно) | Кастомная задержка (экспоненциальная задержка и т.д.) |
| **Счетчик попыток** | Недоступен | Доступен как параметр |
| **Сложность** | Простой | Более гибкий |
| **Применение** | Базовый повтор | Продвинутые стратегии повтора |

### Продвинутые паттерны

**Паттерн 1: Повтор с таймаутом**

```kotlin
fun loadData(): Flow<Data> = flow {
    emit(api.getData())
}
.timeout(10.seconds)  // Таймаут для каждой попытки
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

### Интеграция с ViewModel

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

### Лучшие практики

**1. Всегда используйте предикат для фильтрации исключений**

```kotlin
// ✅ ХОРОШО - Только сетевые ошибки
.retry(3) { it is IOException }

// ❌ ПЛОХО - Повторяет все исключения
.retry(3)
```

**2. Реализуйте экспоненциальную задержку для retryWhen**

```kotlin
// ✅ ХОРОШО - Экспоненциальная задержка
.retryWhen { cause, attempt ->
    if (attempt < 5) {
        delay(1000 * (2.0.pow(attempt.toInt())).toLong())
        true
    } else false
}
```

**3. Устанавливайте максимальное количество попыток**

```kotlin
// ✅ ХОРОШО - Ограниченные повторы
.retry(3) { it is IOException }

// ❌ ПЛОХО - Бесконечные повторы могут вызвать проблемы
.retry { it is IOException }
```

**Краткое содержание**: `retry` немедленно повторяет flow при исключении (фиксированное количество, фильтр предиката). `retryWhen` предоставляет продвинутый контроль (доступ к номеру попытки, кастомные задержки, экспоненциальная задержка). Используйте `retry` для простой логики повтора. Используйте `retryWhen` для экспоненциальной задержки, разных стратегий по типу ошибки, обновлений прогресса. Всегда фильтруйте исключения, реализуйте задержки, устанавливайте макс. попытки.

---

## References
- [Flow Error Handling - Kotlin Documentation](https://kotlinlang.org/docs/flow.html#exception-handling)
- [Retry Operators](https://elizarov.medium.com/kotlin-flows-and-coroutines-256260fb3bdb)

## Related Questions
- [[q-flow-error-handling--kotlin--medium]]
- [[q-catch-operator-flow--kotlin--medium]]
