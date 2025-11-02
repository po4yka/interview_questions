---
id: net-003
title: Network Error Handling Strategies / Стратегии обработки сетевых ошибок
aliases: [Network Error Handling Strategies, Стратегии обработки сетевых ошибок]
topic: networking
subtopics: [error-handling, http, resilience]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-leakcanary-detection-mechanism--android--medium, q-presenter-notify-view--android--medium]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [architecture, difficulty/medium, error-handling, strategy, ux]
date created: Monday, October 27th 2025, 4:02:02 pm
date modified: Saturday, November 1st 2025, 5:44:10 pm
---

# Вопрос (RU)

> Спроектируйте стратегию обработки сетевых ошибок. Обрабатывайте таймауты, отсутствие интернета, 4xx/5xx ошибки по-разному с понятными сообщениями пользователю.

# Question (EN)

> Design a comprehensive error handling strategy for network requests. Handle timeouts, no internet, 4xx/5xx errors differently with user-friendly messages.

---

## Ответ (RU)

**Комплексная обработка ошибок** критична для хорошего UX. Пользователи должны понимать проблему и знать, что делать. Стратегия включает классификацию ошибок, интеллектуальные повторы и понятные сообщения.

### Классификация Ошибок

Sealed class hierarchy для типизации ошибок:

```kotlin
sealed class NetworkError {
    // ✅ Клиентские ошибки - пользователь может исправить
    data class NoInternet(val message: String = "Нет подключения") : NetworkError()
    data class Timeout(val type: TimeoutType) : NetworkError()

    // ✅ 4xx - ошибки клиента
    sealed class ClientError : NetworkError() {
        data class Unauthorized(val message: String = "Требуется авторизация") : ClientError()
        data class NotFound(val resource: String? = null) : ClientError()
        data class Validation(val errors: Map<String, List<String>>) : ClientError()
    }

    // ✅ 5xx - ошибки сервера
    sealed class ServerError : NetworkError() {
        data class InternalServerError(val message: String = "Ошибка сервера") : ServerError()
        data class ServiceUnavailable(val retryAfterSeconds: Long? = null) : ServerError()
    }

    data class Unknown(val exception: Throwable) : NetworkError()
}

// ✅ Extension для определения, можно ли повторить запрос
val NetworkError.isRetryable: Boolean
    get() = when (this) {
        is NetworkError.Timeout,
        is NetworkError.ServerError,
        is NetworkError.NoInternet -> true
        else -> false
    }
```

### Маппинг Исключений

Конвертация исключений и HTTP кодов:

```kotlin
class NetworkErrorMapper {
    fun mapError(throwable: Throwable): NetworkError {
        return when (throwable) {
            // ✅ Сетевые проблемы
            is UnknownHostException,
            is ConnectException -> NetworkError.NoInternet()

            // ✅ Таймауты
            is SocketTimeoutException -> NetworkError.Timeout(
                type = determineTimeoutType(throwable)
            )

            // ✅ HTTP ошибки
            is HttpException -> mapHttpError(throwable)

            // ❌ Не глотать неизвестные ошибки молча
            else -> NetworkError.Unknown(throwable)
        }
    }

    private fun mapHttpError(exception: HttpException): NetworkError {
        return when (exception.code()) {
            401 -> NetworkError.ClientError.Unauthorized()
            404 -> NetworkError.ClientError.NotFound()
            422 -> NetworkError.ClientError.Validation(
                errors = parseValidationErrors(exception)
            )
            500 -> NetworkError.ServerError.InternalServerError()
            503 -> NetworkError.ServerError.ServiceUnavailable(
                retryAfterSeconds = parseRetryAfter(exception)
            )
            else -> NetworkError.Unknown(exception)
        }
    }
}
```

### Стратегия Повторов

Exponential backoff с jitter:

```kotlin
class RetryStrategy(
    private val maxAttempts: Int = 3,
    private val initialDelayMs: Long = 1000L,
    private val factor: Double = 2.0,
    private val jitterFactor: Double = 0.1
) {
    suspend fun <T> execute(
        operation: suspend () -> Result<T, NetworkError>
    ): Result<T, NetworkError> {
        var attempt = 0

        while (attempt < maxAttempts) {
            val result = operation()

            when {
                result is Result.Success -> return result
                // ✅ Не повторять невосстанавливаемые ошибки
                result is Result.Failure && !result.error.isRetryable -> return result
                // ✅ Повторить с задержкой
                result is Result.Failure -> {
                    attempt++
                    if (attempt < maxAttempts) {
                        delay(calculateDelay(attempt, result.error))
                    }
                }
            }
        }

        return Result.Failure(NetworkError.Unknown(
            IllegalStateException("Max retries exceeded")
        ))
    }

    private fun calculateDelay(attempt: Int, error: NetworkError): Long {
        // ✅ Уважаем Retry-After header
        error.retryAfterMs?.let { return it }

        // ✅ Exponential backoff с jitter для предотвращения thundering herd
        val exponential = (initialDelayMs * factor.pow(attempt - 1)).toLong()
        val jitter = (exponential * jitterFactor * Random.nextDouble()).toLong()
        return exponential + jitter
    }
}
```

### Repository С Обработкой

Централизованная обработка в data layer:

```kotlin
class UserRepository(
    private val apiService: ApiService,
    private val networkMonitor: NetworkMonitor,
    private val errorMapper: NetworkErrorMapper,
    private val retryStrategy: RetryStrategy
) {
    suspend fun getUser(userId: String): Result<User, NetworkError> {
        // ✅ Проверяем сеть перед запросом
        if (!networkMonitor.isConnected.value) {
            return Result.Failure(NetworkError.NoInternet())
        }

        return try {
            val response = apiService.getUser(userId)
            if (response.isSuccessful && response.body() != null) {
                Result.Success(response.body()!!)
            } else {
                Result.Failure(errorMapper.mapError(HttpException(response)))
            }
        } catch (e: Exception) {
            Result.Failure(errorMapper.mapError(e))
        }
    }

    // ✅ Автоматические повторы для временных сбоев
    suspend fun getUserWithRetry(userId: String): Result<User, NetworkError> {
        return retryStrategy.execute { getUser(userId) }
    }
}
```

### UI С Обработкой Ошибок

ViewModel и Compose UI:

```kotlin
class UserViewModel(
    private val userRepository: UserRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    sealed class UiState {
        object Loading : UiState()
        data class Success(val user: User) : UiState()
        data class Error(val error: NetworkError, val canRetry: Boolean) : UiState()
    }

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            when (val result = userRepository.getUserWithRetry(userId)) {
                is Result.Success -> _uiState.value = UiState.Success(result.value)
                is Result.Failure -> _uiState.value = UiState.Error(
                    error = result.error,
                    canRetry = result.error.isRetryable
                )
            }
        }
    }
}

@Composable
fun ErrorContent(error: NetworkError, canRetry: Boolean, onRetry: () -> Unit) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        // ✅ Иконка зависит от типа ошибки
        val icon = when (error) {
            is NetworkError.NoInternet -> Icons.Default.WifiOff
            is NetworkError.ClientError.Unauthorized -> Icons.Default.Lock
            is NetworkError.ServerError -> Icons.Default.ErrorOutline
            else -> Icons.Default.Error
        }

        Icon(imageVector = icon, contentDescription = null, modifier = Modifier.size(64.dp))

        // ✅ Понятное сообщение для пользователя
        Text(text = error.toUserFriendlyMessage())

        // ✅ Кнопка повтора только для recoverable ошибок
        if (canRetry) {
            Button(onClick = onRetry) {
                Text("Повторить")
            }
        }
    }
}

// ✅ Конвертация технических ошибок в понятные сообщения
fun NetworkError.toUserFriendlyMessage(): String {
    return when (this) {
        is NetworkError.NoInternet -> "Нет интернета. Проверьте подключение."
        is NetworkError.Timeout -> "Превышено время ожидания. Попробуйте позже."
        is NetworkError.ClientError.Unauthorized -> "Войдите в систему."
        is NetworkError.ClientError.NotFound -> "Ресурс не найден."
        is NetworkError.ServerError -> "Ошибка сервера. Попробуйте позже."
        else -> "Произошла ошибка."
    }
}
```

### Best Practices

1. **Классифицируйте ошибки** - разные типы требуют разной обработки
2. **Понятные сообщения** - переводите технические ошибки на язык пользователя
3. **Интеллектуальные повторы** - exponential backoff с jitter
4. **Уважайте сервер** - соблюдайте Retry-After headers
5. **Не повторяйте бессмысленно** - 401/404 не нужно ретраить
6. **Мониторьте сеть** - проверяйте подключение перед запросами
7. **Кешируйте** - graceful degradation при отсутствии сети

---

## Answer (EN)

**Comprehensive error handling** is critical for good UX. Users must understand the problem and know what to do. The strategy includes error classification, intelligent retries, and user-friendly messages.

### Error Classification

Sealed class hierarchy for type-safe errors:

```kotlin
sealed class NetworkError {
    // ✅ Client-side errors - user can potentially fix
    data class NoInternet(val message: String = "No connection") : NetworkError()
    data class Timeout(val type: TimeoutType) : NetworkError()

    // ✅ 4xx - client mistakes
    sealed class ClientError : NetworkError() {
        data class Unauthorized(val message: String = "Auth required") : ClientError()
        data class NotFound(val resource: String? = null) : ClientError()
        data class Validation(val errors: Map<String, List<String>>) : ClientError()
    }

    // ✅ 5xx - server problems
    sealed class ServerError : NetworkError() {
        data class InternalServerError(val message: String = "Server error") : ServerError()
        data class ServiceUnavailable(val retryAfterSeconds: Long? = null) : ServerError()
    }

    data class Unknown(val exception: Throwable) : NetworkError()
}

// ✅ Extension to check if error is retryable
val NetworkError.isRetryable: Boolean
    get() = when (this) {
        is NetworkError.Timeout,
        is NetworkError.ServerError,
        is NetworkError.NoInternet -> true
        else -> false
    }
```

### Exception Mapping

Convert exceptions and HTTP codes:

```kotlin
class NetworkErrorMapper {
    fun mapError(throwable: Throwable): NetworkError {
        return when (throwable) {
            // ✅ Network connectivity issues
            is UnknownHostException,
            is ConnectException -> NetworkError.NoInternet()

            // ✅ Timeouts
            is SocketTimeoutException -> NetworkError.Timeout(
                type = determineTimeoutType(throwable)
            )

            // ✅ HTTP errors
            is HttpException -> mapHttpError(throwable)

            // ❌ Don't silently swallow unknown errors
            else -> NetworkError.Unknown(throwable)
        }
    }

    private fun mapHttpError(exception: HttpException): NetworkError {
        return when (exception.code()) {
            401 -> NetworkError.ClientError.Unauthorized()
            404 -> NetworkError.ClientError.NotFound()
            422 -> NetworkError.ClientError.Validation(
                errors = parseValidationErrors(exception)
            )
            500 -> NetworkError.ServerError.InternalServerError()
            503 -> NetworkError.ServerError.ServiceUnavailable(
                retryAfterSeconds = parseRetryAfter(exception)
            )
            else -> NetworkError.Unknown(exception)
        }
    }
}
```

### Retry Strategy

Exponential backoff with jitter:

```kotlin
class RetryStrategy(
    private val maxAttempts: Int = 3,
    private val initialDelayMs: Long = 1000L,
    private val factor: Double = 2.0,
    private val jitterFactor: Double = 0.1
) {
    suspend fun <T> execute(
        operation: suspend () -> Result<T, NetworkError>
    ): Result<T, NetworkError> {
        var attempt = 0

        while (attempt < maxAttempts) {
            val result = operation()

            when {
                result is Result.Success -> return result
                // ✅ Don't retry unrecoverable errors
                result is Result.Failure && !result.error.isRetryable -> return result
                // ✅ Retry with delay
                result is Result.Failure -> {
                    attempt++
                    if (attempt < maxAttempts) {
                        delay(calculateDelay(attempt, result.error))
                    }
                }
            }
        }

        return Result.Failure(NetworkError.Unknown(
            IllegalStateException("Max retries exceeded")
        ))
    }

    private fun calculateDelay(attempt: Int, error: NetworkError): Long {
        // ✅ Respect Retry-After header
        error.retryAfterMs?.let { return it }

        // ✅ Exponential backoff with jitter to prevent thundering herd
        val exponential = (initialDelayMs * factor.pow(attempt - 1)).toLong()
        val jitter = (exponential * jitterFactor * Random.nextDouble()).toLong()
        return exponential + jitter
    }
}
```

### Repository with Error Handling

Centralized error handling in data layer:

```kotlin
class UserRepository(
    private val apiService: ApiService,
    private val networkMonitor: NetworkMonitor,
    private val errorMapper: NetworkErrorMapper,
    private val retryStrategy: RetryStrategy
) {
    suspend fun getUser(userId: String): Result<User, NetworkError> {
        // ✅ Check network before making request
        if (!networkMonitor.isConnected.value) {
            return Result.Failure(NetworkError.NoInternet())
        }

        return try {
            val response = apiService.getUser(userId)
            if (response.isSuccessful && response.body() != null) {
                Result.Success(response.body()!!)
            } else {
                Result.Failure(errorMapper.mapError(HttpException(response)))
            }
        } catch (e: Exception) {
            Result.Failure(errorMapper.mapError(e))
        }
    }

    // ✅ Automatic retries for transient failures
    suspend fun getUserWithRetry(userId: String): Result<User, NetworkError> {
        return retryStrategy.execute { getUser(userId) }
    }
}
```

### UI with Error Handling

ViewModel and Compose UI:

```kotlin
class UserViewModel(
    private val userRepository: UserRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    sealed class UiState {
        object Loading : UiState()
        data class Success(val user: User) : UiState()
        data class Error(val error: NetworkError, val canRetry: Boolean) : UiState()
    }

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            when (val result = userRepository.getUserWithRetry(userId)) {
                is Result.Success -> _uiState.value = UiState.Success(result.value)
                is Result.Failure -> _uiState.value = UiState.Error(
                    error = result.error,
                    canRetry = result.error.isRetryable
                )
            }
        }
    }
}

@Composable
fun ErrorContent(error: NetworkError, canRetry: Boolean, onRetry: () -> Unit) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        // ✅ Icon depends on error type
        val icon = when (error) {
            is NetworkError.NoInternet -> Icons.Default.WifiOff
            is NetworkError.ClientError.Unauthorized -> Icons.Default.Lock
            is NetworkError.ServerError -> Icons.Default.ErrorOutline
            else -> Icons.Default.Error
        }

        Icon(imageVector = icon, contentDescription = null, modifier = Modifier.size(64.dp))

        // ✅ User-friendly message
        Text(text = error.toUserFriendlyMessage())

        // ✅ Retry button only for recoverable errors
        if (canRetry) {
            Button(onClick = onRetry) {
                Text("Retry")
            }
        }
    }
}

// ✅ Convert technical errors to user-friendly messages
fun NetworkError.toUserFriendlyMessage(): String {
    return when (this) {
        is NetworkError.NoInternet -> "No internet. Check your connection."
        is NetworkError.Timeout -> "Request timed out. Please try later."
        is NetworkError.ClientError.Unauthorized -> "Please log in."
        is NetworkError.ClientError.NotFound -> "Resource not found."
        is NetworkError.ServerError -> "Server error. Try again later."
        else -> "An error occurred."
    }
}
```

### Best Practices

1. **Classify errors** - different types require different handling
2. **User-friendly messages** - translate technical errors to user language
3. **Intelligent retries** - exponential backoff with jitter
4. **Respect server** - honor Retry-After headers
5. **Don't retry blindly** - 401/404 shouldn't be retried
6. **Monitor network** - check connectivity before requests
7. **Cache** - graceful degradation when offline

---

## Follow-ups

- How to implement circuit breaker pattern for failing endpoints?
- When should you fallback to cached data vs showing error?
- How to handle partial batch operation failures?
- How to implement request deduplication for identical concurrent requests?
- How to test error handling scenarios systematically?

## References

- https://developer.android.com/training/basics/network-ops/reading-network-state
- https://kotlinlang.org/docs/sealed-classes.html
- https://square.github.io/retrofit/

## Related Questions

### Prerequisites (Easier)

- [[q-graphql-vs-rest--networking--easy]] - Networking basics

### Related (Medium)

- [[q-http-protocols-comparison--android--medium]] - HTTP protocol comparison
- [[q-kmm-ktor-networking--android--medium]] - Ktor networking
- [[q-network-operations-android--android--medium]] - Network operations

### Advanced (Harder)

- [[q-data-sync-unstable-network--android--hard]] - Data sync strategies
- [[q-network-request-deduplication--networking--hard]] - Request deduplication
