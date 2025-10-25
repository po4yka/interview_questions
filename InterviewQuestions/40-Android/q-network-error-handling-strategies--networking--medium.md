---
id: 20251012-12271152
title: "Network Error Handling Strategies"
topic: networking
difficulty: medium
status: draft
moc: moc-android
related: [q-presenter-notify-view--android--medium, q-leakcanary-detection-mechanism--android--medium, q-how-to-change-number-of-columns-in-recyclerview-based-on-orientation--programming-languages--easy]
created: 2025-10-15
tags: [error-handling, strategy, architecture, ux, difficulty/medium]
---

# Question (EN)

> Design a comprehensive error handling strategy for network requests. Handle timeouts, no internet, 4xx/5xx errors differently with user-friendly messages.

# Вопрос (RU)

> Спроектируйте стратегию обработки сетевых ошибок. Обрабатывайте таймауты, отсутствие интернета, 4xx/5xx ошибки по-разному с понятными сообщениями пользователю.

---

## Answer (EN)

**Comprehensive error handling** is crucial for providing excellent user experience in Android apps. Users should understand what went wrong and what they can do about it. A well-designed error handling strategy differentiates between error types and provides appropriate responses for each.

### Error Classification

Different errors require different handling strategies:

```kotlin
sealed class NetworkError {
    // Client-side errors (user can potentially fix)
    data class NoInternet(
        val message: String = "No internet connection"
    ) : NetworkError()

    data class Timeout(
        val type: TimeoutType,
        val message: String = "Request timed out"
    ) : NetworkError() {
        enum class TimeoutType {
            CONNECTION,  // Failed to establish connection
            READ,        // Connection established but read timed out
            WRITE        // Connection established but write timed out
        }
    }

    // Server-side errors (4xx - client mistakes)
    sealed class ClientError : NetworkError() {
        data class BadRequest(
            val details: String? = null,
            val message: String = "Invalid request"
        ) : ClientError()

        data class Unauthorized(
            val message: String = "Authentication required"
        ) : ClientError()

        data class Forbidden(
            val message: String = "Access denied"
        ) : ClientError()

        data class NotFound(
            val resource: String? = null,
            val message: String = "Resource not found"
        ) : ClientError()

        data class Conflict(
            val details: String? = null,
            val message: String = "Request conflict"
        ) : ClientError()

        data class Validation(
            val errors: Map<String, List<String>>,
            val message: String = "Validation failed"
        ) : ClientError()

        data class TooManyRequests(
            val retryAfterSeconds: Long? = null,
            val message: String = "Too many requests"
        ) : ClientError()
    }

    // Server-side errors (5xx - server problems)
    sealed class ServerError : NetworkError() {
        data class InternalServerError(
            val message: String = "Server error occurred"
        ) : ServerError()

        data class ServiceUnavailable(
            val retryAfterSeconds: Long? = null,
            val message: String = "Service temporarily unavailable"
        ) : ServerError()

        data class GatewayTimeout(
            val message: String = "Gateway timeout"
        ) : ServerError()
    }

    // Parsing/serialization errors
    data class ParseError(
        val exception: Exception,
        val message: String = "Failed to parse response"
    ) : NetworkError()

    // SSL/TLS errors
    data class SSLError(
        val exception: Exception,
        val message: String = "Security error"
    ) : NetworkError()

    // Unexpected errors
    data class Unknown(
        val exception: Throwable,
        val message: String = "Unexpected error occurred"
    ) : NetworkError()
}

// Extension to check if error is retryable
val NetworkError.isRetryable: Boolean
    get() = when (this) {
        is NetworkError.Timeout -> true
        is NetworkError.ServerError.ServiceUnavailable -> true
        is NetworkError.ServerError.GatewayTimeout -> true
        is NetworkError.ClientError.TooManyRequests -> true
        is NetworkError.NoInternet -> true
        else -> false
    }

// Extension to get retry delay
val NetworkError.retryAfterMs: Long?
    get() = when (this) {
        is NetworkError.ClientError.TooManyRequests -> retryAfterSeconds?.times(1000)
        is NetworkError.ServerError.ServiceUnavailable -> retryAfterSeconds?.times(1000)
        else -> null
    }
```

### Error Mapper

Converts exceptions and HTTP codes to our error types:

```kotlin
class NetworkErrorMapper {

    fun mapError(throwable: Throwable): NetworkError {
        return when (throwable) {
            is UnknownHostException,
            is ConnectException -> NetworkError.NoInternet()

            is SocketTimeoutException -> {
                val type = when {
                    throwable.message?.contains("connect", ignoreCase = true) == true ->
                        NetworkError.Timeout.TimeoutType.CONNECTION
                    throwable.message?.contains("read", ignoreCase = true) == true ->
                        NetworkError.Timeout.TimeoutType.READ
                    else -> NetworkError.Timeout.TimeoutType.WRITE
                }
                NetworkError.Timeout(type)
            }

            is SSLException,
            is CertificateException -> NetworkError.SSLError(
                exception = throwable as Exception,
                message = "Security certificate error"
            )

            is JsonSyntaxException,
            is JsonParseException -> NetworkError.ParseError(
                exception = throwable as Exception,
                message = "Failed to parse server response"
            )

            is HttpException -> mapHttpError(throwable)

            else -> NetworkError.Unknown(
                exception = throwable,
                message = throwable.message ?: "Unknown error"
            )
        }
    }

    private fun mapHttpError(exception: HttpException): NetworkError {
        val code = exception.code()
        val errorBody = exception.response()?.errorBody()?.string()

        return when (code) {
            400 -> NetworkError.ClientError.BadRequest(
                details = errorBody,
                message = parseErrorMessage(errorBody) ?: "Invalid request"
            )

            401 -> NetworkError.ClientError.Unauthorized(
                message = parseErrorMessage(errorBody) ?: "Please log in"
            )

            403 -> NetworkError.ClientError.Forbidden(
                message = parseErrorMessage(errorBody) ?: "Access denied"
            )

            404 -> NetworkError.ClientError.NotFound(
                resource = extractResourceFromError(errorBody),
                message = parseErrorMessage(errorBody) ?: "Not found"
            )

            409 -> NetworkError.ClientError.Conflict(
                details = errorBody,
                message = parseErrorMessage(errorBody) ?: "Conflict occurred"
            )

            422 -> {
                val validationErrors = parseValidationErrors(errorBody)
                NetworkError.ClientError.Validation(
                    errors = validationErrors,
                    message = "Please check your input"
                )
            }

            429 -> {
                val retryAfter = exception.response()
                    ?.headers()
                    ?.get("Retry-After")
                    ?.toLongOrNull()

                NetworkError.ClientError.TooManyRequests(
                    retryAfterSeconds = retryAfter,
                    message = "Too many requests. Please try again later."
                )
            }

            500 -> NetworkError.ServerError.InternalServerError(
                message = "Server error. Please try again."
            )

            502 -> NetworkError.ServerError.GatewayTimeout(
                message = "Gateway error. Please try again."
            )

            503 -> {
                val retryAfter = exception.response()
                    ?.headers()
                    ?.get("Retry-After")
                    ?.toLongOrNull()

                NetworkError.ServerError.ServiceUnavailable(
                    retryAfterSeconds = retryAfter,
                    message = "Service temporarily unavailable"
                )
            }

            504 -> NetworkError.ServerError.GatewayTimeout(
                message = "Gateway timeout. Please try again."
            )

            else -> NetworkError.Unknown(
                exception = exception,
                message = "HTTP error: $code"
            )
        }
    }

    private fun parseErrorMessage(errorBody: String?): String? {
        if (errorBody == null) return null

        return try {
            // Try to parse standard error response
            val json = JSONObject(errorBody)
            json.optString("message")
                ?.takeIf { it.isNotEmpty() }
                ?: json.optString("error")?.takeIf { it.isNotEmpty() }
        } catch (e: Exception) {
            null
        }
    }

    private fun parseValidationErrors(errorBody: String?): Map<String, List<String>> {
        if (errorBody == null) return emptyMap()

        return try {
            val json = JSONObject(errorBody)
            val errors = json.optJSONObject("errors") ?: return emptyMap()

            errors.keys().asSequence()
                .associateWith { key ->
                    val errorsArray = errors.optJSONArray(key)
                    if (errorsArray != null) {
                        (0 until errorsArray.length()).map { errorsArray.getString(it) }
                    } else {
                        listOf(errors.optString(key))
                    }
                }
        } catch (e: Exception) {
            emptyMap()
        }
    }

    private fun extractResourceFromError(errorBody: String?): String? {
        if (errorBody == null) return null

        return try {
            val json = JSONObject(errorBody)
            json.optString("resource")?.takeIf { it.isNotEmpty() }
        } catch (e: Exception) {
            null
        }
    }
}
```

### Network Monitor

Monitors network connectivity in real-time:

```kotlin
@RequiresApi(Build.VERSION_CODES.N)
class NetworkMonitor @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE)
        as ConnectivityManager

    private val _isConnected = MutableStateFlow(isCurrentlyConnected())
    val isConnected: StateFlow<Boolean> = _isConnected.asStateFlow()

    private val networkCallback = object : ConnectivityManager.NetworkCallback() {
        override fun onAvailable(network: Network) {
            _isConnected.value = true
        }

        override fun onLost(network: Network) {
            _isConnected.value = false
        }

        override fun onCapabilitiesChanged(
            network: Network,
            networkCapabilities: NetworkCapabilities
        ) {
            val hasInternet = networkCapabilities.hasCapability(
                NetworkCapabilities.NET_CAPABILITY_INTERNET
            ) && networkCapabilities.hasCapability(
                NetworkCapabilities.NET_CAPABILITY_VALIDATED
            )
            _isConnected.value = hasInternet
        }
    }

    init {
        registerNetworkCallback()
    }

    private fun registerNetworkCallback() {
        val request = NetworkRequest.Builder()
            .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
            .addCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED)
            .build()

        connectivityManager.registerNetworkCallback(request, networkCallback)
    }

    fun unregister() {
        connectivityManager.unregisterNetworkCallback(networkCallback)
    }

    private fun isCurrentlyConnected(): Boolean {
        val network = connectivityManager.activeNetwork ?: return false
        val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false

        return capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET) &&
               capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED)
    }

    fun getConnectionType(): ConnectionType {
        val network = connectivityManager.activeNetwork ?: return ConnectionType.NONE
        val capabilities = connectivityManager.getNetworkCapabilities(network)
            ?: return ConnectionType.NONE

        return when {
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) ->
                ConnectionType.WIFI
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) ->
                ConnectionType.CELLULAR
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET) ->
                ConnectionType.ETHERNET
            else -> ConnectionType.OTHER
        }
    }

    enum class ConnectionType {
        WIFI, CELLULAR, ETHERNET, OTHER, NONE
    }
}
```

### Retry Strategy

Implements intelligent retry logic:

```kotlin
class RetryStrategy(
    private val maxAttempts: Int = 3,
    private val initialDelayMs: Long = 1000L,
    private val maxDelayMs: Long = 10000L,
    private val factor: Double = 2.0,
    private val jitterFactor: Double = 0.1
) {

    suspend fun <T> execute(
        operation: suspend (attempt: Int) -> Result<T, NetworkError>
    ): Result<T, NetworkError> {
        var currentAttempt = 0
        var lastError: NetworkError? = null

        while (currentAttempt < maxAttempts) {
            val result = operation(currentAttempt)

            when {
                result is Result.Success -> return result

                result is Result.Failure && !result.error.isRetryable -> {
                    return result
                }

                result is Result.Failure -> {
                    lastError = result.error
                    currentAttempt++

                    if (currentAttempt < maxAttempts) {
                        val delay = calculateDelay(currentAttempt, result.error)
                        delay(delay)
                    }
                }
            }
        }

        return Result.Failure(
            lastError ?: NetworkError.Unknown(
                exception = IllegalStateException("Max retries exceeded"),
                message = "Maximum retry attempts exceeded"
            )
        )
    }

    private fun calculateDelay(attempt: Int, error: NetworkError): Long {
        // Check if server specified retry-after
        error.retryAfterMs?.let { return it }

        // Calculate exponential backoff
        val exponentialDelay = (initialDelayMs * factor.pow(attempt - 1)).toLong()
        val delayWithCap = exponentialDelay.coerceAtMost(maxDelayMs)

        // Add jitter to prevent thundering herd
        val jitter = (delayWithCap * jitterFactor * Random.nextDouble()).toLong()

        return delayWithCap + jitter
    }
}

// Result type for operations
sealed class Result<out T, out E> {
    data class Success<T>(val value: T) : Result<T, Nothing>()
    data class Failure<E>(val error: E) : Result<Nothing, E>()

    val isSuccess: Boolean get() = this is Success
    val isFailure: Boolean get() = this is Failure

    inline fun onSuccess(action: (T) -> Unit): Result<T, E> {
        if (this is Success) action(value)
        return this
    }

    inline fun onFailure(action: (E) -> Unit): Result<T, E> {
        if (this is Failure) action(error)
        return this
    }
}
```

### Repository with Error Handling

Complete repository implementation with comprehensive error handling:

```kotlin
class UserRepository(
    private val apiService: ApiService,
    private val userDao: UserDao,
    private val networkMonitor: NetworkMonitor,
    private val errorMapper: NetworkErrorMapper,
    private val retryStrategy: RetryStrategy
) {

    // Simple fetch with error mapping
    suspend fun getUser(userId: String): Result<User, NetworkError> {
        return withContext(Dispatchers.IO) {
            // Check network first
            if (!networkMonitor.isConnected.value) {
                return@withContext Result.Failure(NetworkError.NoInternet())
            }

            try {
                val response = apiService.getUser(userId)
                if (response.isSuccessful && response.body() != null) {
                    Result.Success(response.body()!!)
                } else {
                    val error = errorMapper.mapError(
                        HttpException(response)
                    )
                    Result.Failure(error)
                }
            } catch (e: Exception) {
                val error = errorMapper.mapError(e)
                Result.Failure(error)
            }
        }
    }

    // Fetch with caching fallback
    suspend fun getUserWithCache(userId: String): Result<User, NetworkError> {
        return withContext(Dispatchers.IO) {
            val result = getUser(userId)

            // On success, update cache
            result.onSuccess { user ->
                userDao.insertUser(user)
            }

            // On error, try cache
            if (result is Result.Failure) {
                val cachedUser = userDao.getUserById(userId)
                if (cachedUser != null) {
                    return@withContext Result.Success(cachedUser)
                }
            }

            result
        }
    }

    // Fetch with automatic retry
    suspend fun getUserWithRetry(userId: String): Result<User, NetworkError> {
        return retryStrategy.execute { attempt ->
            Log.d("UserRepository", "Attempt $attempt to fetch user $userId")
            getUser(userId)
        }
    }

    // Create with validation error handling
    suspend fun createPost(
        userId: String,
        title: String,
        content: String
    ): Result<Post, NetworkError> {
        return withContext(Dispatchers.IO) {
            try {
                val request = CreatePostRequest(
                    userId = userId,
                    title = title,
                    content = content
                )

                val response = apiService.createPost(request)

                if (response.isSuccessful && response.body() != null) {
                    Result.Success(response.body()!!)
                } else {
                    val error = errorMapper.mapError(HttpException(response))
                    Result.Failure(error)
                }
            } catch (e: Exception) {
                val error = errorMapper.mapError(e)
                Result.Failure(error)
            }
        }
    }

    // Batch operation with partial failure handling
    suspend fun createPosts(
        posts: List<CreatePostRequest>
    ): BatchResult<Post, NetworkError> {
        return withContext(Dispatchers.IO) {
            val successes = mutableListOf<Post>()
            val failures = mutableListOf<Pair<CreatePostRequest, NetworkError>>()

            posts.forEach { request ->
                try {
                    val response = apiService.createPost(request)

                    if (response.isSuccessful && response.body() != null) {
                        successes.add(response.body()!!)
                    } else {
                        val error = errorMapper.mapError(HttpException(response))
                        failures.add(request to error)
                    }
                } catch (e: Exception) {
                    val error = errorMapper.mapError(e)
                    failures.add(request to error)
                }
            }

            BatchResult(successes, failures)
        }
    }
}

data class BatchResult<T, E>(
    val successes: List<T>,
    val failures: List<Pair<*, E>>
) {
    val hasFailures: Boolean get() = failures.isNotEmpty()
    val hasSuccesses: Boolean get() = successes.isNotEmpty()
    val isCompleteSuccess: Boolean get() = failures.isEmpty()
    val isCompleteFailure: Boolean get() = successes.isEmpty()
}
```

### ViewModel with Error State

```kotlin
class UserViewModel(
    private val userRepository: UserRepository,
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val userId: String = savedStateHandle["userId"]
        ?: throw IllegalArgumentException("userId required")

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    sealed class UiState {
        object Loading : UiState()

        data class Success(
            val user: User,
            val fromCache: Boolean = false
        ) : UiState()

        data class Error(
            val error: NetworkError,
            val canRetry: Boolean,
            val retryAfterMs: Long? = null
        ) : UiState()
    }

    init {
        loadUser()
    }

    fun loadUser() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            val result = userRepository.getUserWithRetry(userId)

            _uiState.value = when (result) {
                is Result.Success -> UiState.Success(result.value)

                is Result.Failure -> UiState.Error(
                    error = result.error,
                    canRetry = result.error.isRetryable,
                    retryAfterMs = result.error.retryAfterMs
                )
            }
        }
    }

    fun retry() {
        loadUser()
    }
}
```

### UI Layer with Compose

```kotlin
@Composable
fun UserScreen(
    viewModel: UserViewModel = viewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    Box(modifier = Modifier.fillMaxSize()) {
        when (val state = uiState) {
            is UserViewModel.UiState.Loading -> {
                LoadingContent()
            }

            is UserViewModel.UiState.Success -> {
                UserContent(user = state.user)

                if (state.fromCache) {
                    OfflineIndicator()
                }
            }

            is UserViewModel.UiState.Error -> {
                ErrorContent(
                    error = state.error,
                    canRetry = state.canRetry,
                    onRetry = { viewModel.retry() }
                )
            }
        }
    }
}

@Composable
private fun ErrorContent(
    error: NetworkError,
    canRetry: Boolean,
    onRetry: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        // Error icon based on type
        val (icon, iconTint) = when (error) {
            is NetworkError.NoInternet -> Icons.Default.WifiOff to Color.Gray
            is NetworkError.ClientError.Unauthorized -> Icons.Default.Lock to Color.Red
            is NetworkError.ClientError.NotFound -> Icons.Default.SearchOff to Color.Gray
            is NetworkError.ServerError -> Icons.Default.ErrorOutline to Color.Orange
            else -> Icons.Default.Error to Color.Red
        }

        Icon(
            imageVector = icon,
            contentDescription = null,
            modifier = Modifier.size(64.dp),
            tint = iconTint
        )

        Spacer(modifier = Modifier.height(16.dp))

        // Error message
        Text(
            text = error.toUserFriendlyMessage(),
            style = MaterialTheme.typography.titleMedium,
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(8.dp))

        // Additional details for specific errors
        when (error) {
            is NetworkError.ClientError.Validation -> {
                ValidationErrorDetails(errors = error.errors)
            }
            is NetworkError.ClientError.TooManyRequests -> {
                error.retryAfterSeconds?.let { seconds ->
                    Text(
                        text = "Please wait $seconds seconds before retrying",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
            else -> Unit
        }

        // Retry button
        if (canRetry) {
            Spacer(modifier = Modifier.height(16.dp))

            Button(onClick = onRetry) {
                Icon(Icons.Default.Refresh, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("Retry")
            }
        }

        // Navigation for specific errors
        when (error) {
            is NetworkError.ClientError.Unauthorized -> {
                Spacer(modifier = Modifier.height(8.dp))
                TextButton(onClick = { /* Navigate to login */ }) {
                    Text("Go to Login")
                }
            }
            is NetworkError.NoInternet -> {
                Spacer(modifier = Modifier.height(8.dp))
                TextButton(onClick = { /* Open settings */ }) {
                    Text("Check Network Settings")
                }
            }
            else -> Unit
        }
    }
}

@Composable
private fun ValidationErrorDetails(errors: Map<String, List<String>>) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "Please fix the following:",
                style = MaterialTheme.typography.titleSmall,
                color = MaterialTheme.colorScheme.error
            )

            Spacer(modifier = Modifier.height(8.dp))

            errors.forEach { (field, messages) ->
                Text(
                    text = "• ${field.capitalize()}: ${messages.joinToString()}",
                    style = MaterialTheme.typography.bodySmall
                )
            }
        }
    }
}

@Composable
private fun OfflineIndicator() {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        color = MaterialTheme.colorScheme.surfaceVariant
    ) {
        Row(
            modifier = Modifier.padding(8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = Icons.Default.WifiOff,
                contentDescription = null,
                modifier = Modifier.size(16.dp)
            )

            Spacer(modifier = Modifier.width(8.dp))

            Text(
                text = "Showing cached data",
                style = MaterialTheme.typography.bodySmall
            )
        }
    }
}

// Extension to convert errors to user-friendly messages
fun NetworkError.toUserFriendlyMessage(): String {
    return when (this) {
        is NetworkError.NoInternet ->
            "No internet connection. Please check your network."

        is NetworkError.Timeout ->
            "Request timed out. Please try again."

        is NetworkError.ClientError.Unauthorized ->
            "Please log in to continue."

        is NetworkError.ClientError.Forbidden ->
            "You don't have permission to access this resource."

        is NetworkError.ClientError.NotFound ->
            resource?.let { "The $it you're looking for doesn't exist." }
                ?: "Resource not found."

        is NetworkError.ClientError.Validation ->
            "Please check your input and try again."

        is NetworkError.ClientError.TooManyRequests ->
            "Too many requests. Please slow down."

        is NetworkError.ServerError.InternalServerError ->
            "A server error occurred. We're working on it."

        is NetworkError.ServerError.ServiceUnavailable ->
            "Service is temporarily unavailable. Please try again later."

        is NetworkError.ParseError ->
            "Failed to process server response."

        is NetworkError.SSLError ->
            "A security error occurred. Please check your connection."

        else -> message
    }
}
```

### Best Practices

1. **Classify Errors Properly**: Different errors need different handling

2. **Provide User-Friendly Messages**: Translate technical errors to user language

3. **Implement Retry Logic**: Automatic retry for transient failures

4. **Monitor Network State**: React to connectivity changes

5. **Cache for Offline**: Provide degraded service when offline

6. **Respect Server Guidance**: Honor Retry-After headers

7. **Add Jitter to Retries**: Prevent thundering herd problem

8. **Log Errors**: Track error patterns for debugging

9. **Handle Validation Errors**: Show field-specific errors

10. **Test Error Scenarios**: Test all error paths

### Common Pitfalls

1. **Generic Error Messages**: "Error occurred" tells users nothing

2. **No Retry Logic**: Making users manually retry everything

3. **Ignoring Network State**: Attempting requests when offline

4. **Infinite Retries**: Not limiting retry attempts

5. **No Exponential Backoff**: Overwhelming failing servers

6. **Not Closing Resources**: Memory leaks from error responses

7. **Swallowing Errors**: Silent failures confuse users

8. **No Offline Mode**: App unusable without internet

### Summary

Comprehensive error handling provides:

-   **Better UX**: Clear, actionable error messages
-   **Resilience**: Automatic retry for transient failures
-   **Offline Support**: Graceful degradation when offline
-   **Intelligence**: Different strategies for different errors
-   **Debugging**: Proper error logging and tracking
-   **Maintainability**: Centralized error handling logic

Master error handling to build robust, user-friendly Android applications.

---

## Ответ (RU)

**Комплексная обработка ошибок** критична для отличного пользовательского опыта в Android приложениях. Пользователи должны понимать, что пошло не так и что они могут с этим сделать. Хорошо спроектированная стратегия обработки ошибок различает типы ошибок и предоставляет соответствующие ответы для каждого.

### Классификация ошибок

```kotlin
sealed class NetworkError {
    // Клиентские ошибки (пользователь может исправить)
    data class NoInternet(
        val message: String = "Нет интернета"
    ) : NetworkError()

    data class Timeout(
        val type: TimeoutType,
        val message: String = "Превышено время ожидания"
    ) : NetworkError()

    // Ошибки сервера (4xx - ошибки клиента)
    sealed class ClientError : NetworkError() {
        data class BadRequest(
            val details: String? = null,
            val message: String = "Неверный запрос"
        ) : ClientError()

        data class Unauthorized(
            val message: String = "Требуется авторизация"
        ) : ClientError()

        data class Forbidden(
            val message: String = "Доступ запрещён"
        ) : ClientError()

        data class NotFound(
            val resource: String? = null,
            val message: String = "Ресурс не найден"
        ) : ClientError()

        data class Validation(
            val errors: Map<String, List<String>>,
            val message: String = "Ошибка валидации"
        ) : ClientError()

        data class TooManyRequests(
            val retryAfterSeconds: Long? = null,
            val message: String = "Слишком много запросов"
        ) : ClientError()
    }

    // Серверные ошибки (5xx)
    sealed class ServerError : NetworkError() {
        data class InternalServerError(
            val message: String = "Ошибка сервера"
        ) : ServerError()

        data class ServiceUnavailable(
            val retryAfterSeconds: Long? = null,
            val message: String = "Сервис недоступен"
        ) : ServerError()
    }

    data class ParseError(
        val exception: Exception,
        val message: String = "Ошибка парсинга"
    ) : NetworkError()

    data class Unknown(
        val exception: Throwable,
        val message: String = "Неизвестная ошибка"
    ) : NetworkError()
}

val NetworkError.isRetryable: Boolean
    get() = when (this) {
        is NetworkError.Timeout -> true
        is NetworkError.ServerError -> true
        is NetworkError.NoInternet -> true
        else -> false
    }
```

### Маппер ошибок

```kotlin
class NetworkErrorMapper {

    fun mapError(throwable: Throwable): NetworkError {
        return when (throwable) {
            is UnknownHostException,
            is ConnectException -> NetworkError.NoInternet()

            is SocketTimeoutException -> NetworkError.Timeout(
                type = NetworkError.Timeout.TimeoutType.CONNECTION
            )

            is HttpException -> mapHttpError(throwable)

            else -> NetworkError.Unknown(
                exception = throwable,
                message = throwable.message ?: "Неизвестная ошибка"
            )
        }
    }

    private fun mapHttpError(exception: HttpException): NetworkError {
        val code = exception.code()
        val errorBody = exception.response()?.errorBody()?.string()

        return when (code) {
            400 -> NetworkError.ClientError.BadRequest(details = errorBody)
            401 -> NetworkError.ClientError.Unauthorized()
            403 -> NetworkError.ClientError.Forbidden()
            404 -> NetworkError.ClientError.NotFound()
            422 -> NetworkError.ClientError.Validation(
                errors = parseValidationErrors(errorBody)
            )
            429 -> NetworkError.ClientError.TooManyRequests()
            500 -> NetworkError.ServerError.InternalServerError()
            503 -> NetworkError.ServerError.ServiceUnavailable()
            else -> NetworkError.Unknown(
                exception = exception,
                message = "HTTP ошибка: $code"
            )
        }
    }
}
```

### Монитор сети

```kotlin
class NetworkMonitor(context: Context) {
    private val cm = context.getSystemService(Context.CONNECTIVITY_SERVICE)
        as ConnectivityManager

    private val _isConnected = MutableStateFlow(isCurrentlyConnected())
    val isConnected: StateFlow<Boolean> = _isConnected.asStateFlow()

    private val callback = object : ConnectivityManager.NetworkCallback() {
        override fun onAvailable(network: Network) {
            _isConnected.value = true
        }

        override fun onLost(network: Network) {
            _isConnected.value = false
        }
    }

    init {
        val request = NetworkRequest.Builder()
            .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
            .build()

        cm.registerNetworkCallback(request, callback)
    }

    private fun isCurrentlyConnected(): Boolean {
        val network = cm.activeNetwork ?: return false
        val capabilities = cm.getNetworkCapabilities(network) ?: return false
        return capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
    }
}
```

### Стратегия повторов

```kotlin
class RetryStrategy(
    private val maxAttempts: Int = 3,
    private val initialDelayMs: Long = 1000L,
    private val factor: Double = 2.0
) {

    suspend fun <T> execute(
        operation: suspend (attempt: Int) -> Result<T>
    ): Result<T> {
        var currentAttempt = 0

        while (currentAttempt < maxAttempts) {
            val result = operation(currentAttempt)

            when {
                result is Result.Success -> return result

                result is Result.Failure && !result.error.isRetryable -> {
                    return result
                }

                result is Result.Failure -> {
                    currentAttempt++

                    if (currentAttempt < maxAttempts) {
                        val delay = calculateDelay(currentAttempt)
                        delay(delay)
                    }
                }
            }
        }

        return Result.Failure(NetworkError.Unknown(
            exception = IllegalStateException("Max retries"),
            message = "Превышено максимальное количество попыток"
        ))
    }

    private fun calculateDelay(attempt: Int): Long {
        return (initialDelayMs * factor.pow(attempt - 1)).toLong()
    }
}
```

### Repository с обработкой ошибок

```kotlin
class UserRepository(
    private val apiService: ApiService,
    private val networkMonitor: NetworkMonitor,
    private val errorMapper: NetworkErrorMapper,
    private val retryStrategy: RetryStrategy
) {

    suspend fun getUser(userId: String): Result<User> {
        if (!networkMonitor.isConnected.value) {
            return Result.Failure(NetworkError.NoInternet())
        }

        return try {
            val response = apiService.getUser(userId)
            if (response.isSuccessful && response.body() != null) {
                Result.Success(response.body()!!)
            } else {
                val error = errorMapper.mapError(HttpException(response))
                Result.Failure(error)
            }
        } catch (e: Exception) {
            val error = errorMapper.mapError(e)
            Result.Failure(error)
        }
    }

    suspend fun getUserWithRetry(userId: String): Result<User> {
        return retryStrategy.execute { attempt ->
            getUser(userId)
        }
    }
}
```

### ViewModel с состояниями ошибок

```kotlin
class UserViewModel(
    private val userRepository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    sealed class UiState {
        object Loading : UiState()
        data class Success(val user: User) : UiState()
        data class Error(
            val error: NetworkError,
            val canRetry: Boolean
        ) : UiState()
    }

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            when (val result = userRepository.getUserWithRetry(userId)) {
                is Result.Success -> {
                    _uiState.value = UiState.Success(result.value)
                }
                is Result.Failure -> {
                    _uiState.value = UiState.Error(
                        error = result.error,
                        canRetry = result.error.isRetryable
                    )
                }
            }
        }
    }
}
```

### Best Practices

1. **Классифицируйте ошибки**: Разные ошибки требуют разной обработки

2. **Понятные сообщения**: Переводите технические ошибки на язык пользователя

3. **Логика повторов**: Автоматические повторы для временных сбоев

4. **Мониторинг сети**: Реагируйте на изменения подключения

5. **Кеширование для оффлайна**: Деградация функциональности

6. **Уважайте указания сервера**: Соблюдайте Retry-After заголовки

7. **Jitter в повторах**: Предотвращайте thundering herd

8. **Логируйте ошибки**: Отслеживайте паттерны

9. **Тестируйте ошибки**: Тестируйте все пути ошибок

### Распространённые ошибки

1. **Общие сообщения**: "Произошла ошибка" ничего не говорит

2. **Нет логики повторов**: Пользователь вручную повторяет всё

3. **Игнорирование состояния сети**: Попытки запросов оффлайн

4. **Бесконечные повторы**: Не ограничивать попытки

5. **Нет экспоненциального увеличения**: Перегрузка падающих серверов

### Резюме

Комплексная обработка ошибок обеспечивает:

-   **Лучший UX**: Понятные, действенные сообщения
-   **Устойчивость**: Автоматические повторы
-   **Оффлайн поддержку**: Деградация без интернета
-   **Интеллект**: Разные стратегии для разных ошибок
-   **Отладку**: Правильное логирование
-   **Поддерживаемость**: Централизованная логика

---

## Related Questions

### Prerequisites (Easier)

-   [[q-graphql-vs-rest--networking--easy]] - Networking

### Related (Medium)

-   [[q-http-protocols-comparison--android--medium]] - Networking
-   [[q-kmm-ktor-networking--android--medium]] - Networking
-   [[q-retrofit-call-adapter-advanced--networking--medium]] - Networking
-   [[q-okhttp-interceptors-advanced--networking--medium]] - Networking
-   [[q-network-operations-android--android--medium]] - Networking

### Advanced (Harder)

-   [[q-data-sync-unstable-network--android--hard]] - Networking
-   [[q-network-request-deduplication--networking--hard]] - Networking
