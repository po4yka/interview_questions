---
tags:
  - Android
  - Kotlin
  - KMM
  - Ktor
  - Networking
difficulty: medium
status: draft
---

# Ktor Client for Multiplatform Networking

# Question (EN)
> 
Explain how to use Ktor client for multiplatform networking in KMM projects. How do you configure platform-specific engines, handle authentication, implement retry logic, and manage network errors across Android and iOS?

## Answer (EN)
Ktor is the recommended HTTP client for Kotlin Multiplatform, providing a unified API with platform-optimized engines (OkHttp for Android, NSURLSession for iOS) and comprehensive plugin support for modern networking requirements.

#### Ktor Setup and Configuration

**1. Dependencies**
```kotlin
// shared/build.gradle.kts
kotlin {
    sourceSets {
        val commonMain by getting {
            dependencies {
                // Ktor core
                implementation("io.ktor:ktor-client-core:2.3.7")

                // Serialization
                implementation("io.ktor:ktor-client-content-negotiation:2.3.7")
                implementation("io.ktor:ktor-serialization-kotlinx-json:2.3.7")

                // Logging
                implementation("io.ktor:ktor-client-logging:2.3.7")

                // Auth
                implementation("io.ktor:ktor-client-auth:2.3.7")

                // Additional features
                implementation("io.ktor:ktor-client-encoding:2.3.7")
            }
        }

        val androidMain by getting {
            dependencies {
                // Android engine (OkHttp)
                implementation("io.ktor:ktor-client-android:2.3.7")
            }
        }

        val iosMain by getting {
            dependencies {
                // iOS engine (NSURLSession)
                implementation("io.ktor:ktor-client-darwin:2.3.7")
            }
        }
    }
}
```

**2. Basic Client Configuration**
```kotlin
// commonMain/network/HttpClientFactory.kt
object HttpClientFactory {
    fun create(
        baseUrl: String,
        enableLogging: Boolean = true
    ): HttpClient {
        return HttpClient {
            // Base URL configuration
            defaultRequest {
                url(baseUrl)
                contentType(ContentType.Application.Json)

                // Common headers
                header("X-App-Version", BuildConfig.VERSION_NAME)
                header("X-Platform", getPlatform().name)
            }

            // JSON serialization
            install(ContentNegotiation) {
                json(Json {
                    prettyPrint = true
                    isLenient = true
                    ignoreUnknownKeys = true
                    explicitNulls = false
                })
            }

            // Logging
            if (enableLogging) {
                install(Logging) {
                    logger = object : Logger {
                        override fun log(message: String) {
                            co.touchlab.kermit.Logger.d { message }
                        }
                    }
                    level = if (isDebug()) {
                        LogLevel.ALL
                    } else {
                        LogLevel.NONE
                    }
                }
            }

            // Timeout configuration
            install(HttpTimeout) {
                requestTimeoutMillis = 30_000
                connectTimeoutMillis = 15_000
                socketTimeoutMillis = 15_000
            }

            // Response validation
            expectSuccess = true

            // Platform-specific configuration
            engine {
                configurePlatformEngine()
            }
        }
    }
}

// Platform-specific engine configuration
expect fun HttpClientConfig<*>.configurePlatformEngine()

// androidMain
actual fun HttpClientConfig<*>.configurePlatformEngine() {
    // Android (OkHttp) specific configuration
    engine {
        if (this is AndroidEngineConfig) {
            connectTimeout = 15_000
            socketTimeout = 15_000

            // Proxy configuration
            proxy = ProxyBuilder.http("http://proxy.example.com:8080")
        }
    }
}

// iosMain
actual fun HttpClientConfig<*>.configurePlatformEngine() {
    // iOS (NSURLSession) specific configuration
    engine {
        if (this is DarwinClientEngineConfig) {
            configureRequest {
                setAllowsCellularAccess(true)
            }
        }
    }
}
```

#### Authentication

**1. Bearer Token Authentication**
```kotlin
// commonMain/network/AuthenticatedHttpClient.kt
class AuthenticatedHttpClient(
    private val tokenProvider: TokenProvider
) {
    val client = HttpClient {
        defaultRequest {
            url("https://api.example.com/")
            contentType(ContentType.Application.Json)
        }

        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
                explicitNulls = false
            })
        }

        // Authentication plugin
        install(Auth) {
            bearer {
                loadTokens {
                    // Load tokens from storage
                    val token = tokenProvider.getAccessToken()
                    val refreshToken = tokenProvider.getRefreshToken()

                    BearerTokens(
                        accessToken = token ?: "",
                        refreshToken = refreshToken ?: ""
                    )
                }

                refreshTokens {
                    // Refresh token logic
                    val refreshToken = tokenProvider.getRefreshToken()

                    if (refreshToken == null) {
                        // No refresh token, user needs to re-login
                        return@refreshTokens null
                    }

                    try {
                        // Call refresh endpoint
                        val response = client.post("auth/refresh") {
                            markAsRefreshTokenRequest()
                            setBody(RefreshTokenRequest(refreshToken))
                        }.body<TokenResponse>()

                        // Save new tokens
                        tokenProvider.saveTokens(
                            accessToken = response.accessToken,
                            refreshToken = response.refreshToken
                        )

                        BearerTokens(
                            accessToken = response.accessToken,
                            refreshToken = response.refreshToken
                        )
                    } catch (e: Exception) {
                        // Refresh failed, user needs to re-login
                        tokenProvider.clearTokens()
                        null
                    }
                }

                sendWithoutRequest { request ->
                    // Send token with all requests except auth endpoints
                    !request.url.encodedPath.startsWith("/auth/")
                }
            }
        }

        // Handle 401 Unauthorized
        HttpResponseValidator {
            handleResponseExceptionWithRequest { exception, request ->
                if (exception is ClientRequestException &&
                    exception.response.status == HttpStatusCode.Unauthorized
                ) {
                    // Clear tokens and notify UI
                    tokenProvider.clearTokens()
                    throw UnauthorizedException("Session expired")
                }
            }
        }
    }
}

interface TokenProvider {
    suspend fun getAccessToken(): String?
    suspend fun getRefreshToken(): String?
    suspend fun saveTokens(accessToken: String, refreshToken: String)
    suspend fun clearTokens()
}

class UnauthorizedException(message: String) : Exception(message)
```

**2. Custom Authentication Header**
```kotlin
// API Key authentication
class ApiKeyAuthClient(private val apiKey: String) {
    val client = HttpClient {
        defaultRequest {
            url("https://api.example.com/")

            // Custom auth header
            header("X-API-Key", apiKey)
        }

        install(ContentNegotiation) {
            json()
        }
    }
}

// OAuth 2.0
class OAuth2Client(
    private val clientId: String,
    private val clientSecret: String,
    private val tokenProvider: TokenProvider
) {
    val client = HttpClient {
        install(Auth) {
            bearer {
                loadTokens {
                    val token = tokenProvider.getAccessToken()
                    token?.let {
                        BearerTokens(accessToken = it, refreshToken = "")
                    }
                }

                refreshTokens {
                    // OAuth refresh flow
                    val response = client.submitForm(
                        url = "https://oauth.example.com/token",
                        formParameters = parameters {
                            append("grant_type", "refresh_token")
                            append("refresh_token", tokenProvider.getRefreshToken() ?: "")
                            append("client_id", clientId)
                            append("client_secret", clientSecret)
                        }
                    ).body<OAuthTokenResponse>()

                    tokenProvider.saveTokens(
                        accessToken = response.accessToken,
                        refreshToken = response.refreshToken
                    )

                    BearerTokens(
                        accessToken = response.accessToken,
                        refreshToken = response.refreshToken
                    )
                }
            }
        }
    }
}
```

#### Retry Logic

**1. Automatic Retry Plugin**
```kotlin
// commonMain/network/plugins/RetryPlugin.kt
class RetryPlugin(
    private val maxRetries: Int = 3,
    private val retryableStatusCodes: Set<HttpStatusCode> = setOf(
        HttpStatusCode.RequestTimeout,
        HttpStatusCode.TooManyRequests,
        HttpStatusCode.InternalServerError,
        HttpStatusCode.BadGateway,
        HttpStatusCode.ServiceUnavailable,
        HttpStatusCode.GatewayTimeout
    ),
    private val delayMillis: (attempt: Int) -> Long = { attempt ->
        // Exponential backoff: 1s, 2s, 4s, 8s
        (1000L * (1 shl (attempt - 1))).coerceAtMost(30_000L)
    }
) {
    fun install(client: HttpClient) {
        client.plugin(HttpSend).intercept { request ->
            var attempt = 0
            var response: HttpResponse? = null
            var lastException: Exception? = null

            while (attempt < maxRetries) {
                attempt++

                try {
                    response = execute(request)

                    // Check if we should retry
                    if (response.status in retryableStatusCodes && attempt < maxRetries) {
                        Logger.w {
                            "Request failed with ${response.status}, " +
                                    "retrying (attempt $attempt/$maxRetries)"
                        }

                        // Wait before retry
                        delay(delayMillis(attempt))
                        continue
                    }

                    // Success or non-retryable error
                    return@intercept response

                } catch (e: Exception) {
                    lastException = e

                    if (isRetryableException(e) && attempt < maxRetries) {
                        Logger.w {
                            "Request failed with ${e.message}, " +
                                    "retrying (attempt $attempt/$maxRetries)"
                        }
                        delay(delayMillis(attempt))
                        continue
                    }

                    // Non-retryable exception or max retries reached
                    throw e
                }
            }

            // Max retries reached
            response ?: throw lastException
                ?: Exception("Max retries reached")
        }
    }

    private fun isRetryableException(exception: Exception): Boolean {
        return when (exception) {
            is SocketTimeoutException,
            is ConnectException,
            is UnknownHostException -> true
            else -> false
        }
    }
}

// Usage
val client = HttpClient {
    install(ContentNegotiation) { json() }
}.also { client ->
    RetryPlugin(
        maxRetries = 3,
        delayMillis = { attempt -> 1000L * attempt }
    ).install(client)
}
```

**2. Conditional Retry**
```kotlin
// Retry only for specific requests
suspend inline fun <reified T> HttpClient.getWithRetry(
    urlString: String,
    maxRetries: Int = 3,
    block: HttpRequestBuilder.() -> Unit = {}
): T {
    var attempt = 0
    var lastException: Exception? = null

    while (attempt < maxRetries) {
        attempt++

        try {
            return get(urlString, block).body<T>()
        } catch (e: Exception) {
            lastException = e

            val shouldRetry = when {
                attempt >= maxRetries -> false
                e is HttpRequestTimeoutException -> true
                e is ConnectTimeoutException -> true
                e is ClientRequestException &&
                    e.response.status == HttpStatusCode.TooManyRequests -> {
                    // Parse Retry-After header
                    val retryAfter = e.response.headers["Retry-After"]
                        ?.toLongOrNull() ?: 1L
                    delay(retryAfter * 1000)
                    true
                }
                else -> false
            }

            if (!shouldRetry) {
                throw e
            }

            Logger.w { "Retrying request (attempt $attempt/$maxRetries)" }
            delay(1000L * attempt) // Linear backoff
        }
    }

    throw lastException ?: Exception("Max retries reached")
}

// Usage
val users = client.getWithRetry<List<User>>("users") {
    parameter("page", 1)
}
```

#### Error Handling

**1. Comprehensive Error Handling**
```kotlin
// commonMain/network/NetworkError.kt
sealed class NetworkError : Exception() {
    data class HttpError(
        val statusCode: HttpStatusCode,
        val errorBody: String?,
        override val message: String
    ) : NetworkError()

    data class TimeoutError(
        override val message: String = "Request timeout"
    ) : NetworkError()

    data class NoInternetError(
        override val message: String = "No internet connection"
    ) : NetworkError()

    data class SerializationError(
        override val message: String,
        override val cause: Throwable?
    ) : NetworkError()

    data class UnknownError(
        override val message: String,
        override val cause: Throwable?
    ) : NetworkError()
}

// Error response model
@Serializable
data class ErrorResponse(
    val code: String,
    val message: String,
    val details: Map<String, String>? = null
)

// Error handling extension
suspend inline fun <reified T> HttpResponse.bodyOrError(): Result<T> {
    return try {
        if (status.isSuccess()) {
            Result.success(body<T>())
        } else {
            val errorBody = bodyAsText()
            val errorResponse = try {
                Json.decodeFromString<ErrorResponse>(errorBody)
            } catch (e: Exception) {
                null
            }

            val error = NetworkError.HttpError(
                statusCode = status,
                errorBody = errorBody,
                message = errorResponse?.message ?: "HTTP ${status.value}"
            )
            Result.failure(error)
        }
    } catch (e: Exception) {
        Result.failure(mapException(e))
    }
}

fun mapException(e: Exception): NetworkError {
    return when (e) {
        is HttpRequestTimeoutException,
        is ConnectTimeoutException,
        is SocketTimeoutException -> {
            NetworkError.TimeoutError()
        }

        is UnknownHostException,
        is ConnectException -> {
            NetworkError.NoInternetError()
        }

        is SerializationException,
        is JsonDecodingException -> {
            NetworkError.SerializationError(
                message = "Failed to parse response",
                cause = e
            )
        }

        is ClientRequestException -> {
            NetworkError.HttpError(
                statusCode = e.response.status,
                errorBody = null,
                message = e.message
            )
        }

        else -> {
            NetworkError.UnknownError(
                message = e.message ?: "Unknown error",
                cause = e
            )
        }
    }
}

// Usage in repository
class UserRepository(private val client: HttpClient) {
    suspend fun getUser(userId: String): Result<User> {
        return try {
            val response = client.get("users/$userId")
            response.bodyOrError<User>()
        } catch (e: Exception) {
            Result.failure(mapException(e))
        }
    }

    suspend fun getUsers(): Result<List<User>> {
        return runCatching {
            client.get("users").body<List<User>>()
        }.fold(
            onSuccess = { Result.success(it) },
            onFailure = { Result.failure(mapException(it as Exception)) }
        )
    }
}
```

**2. Network Availability Check**
```kotlin
// Platform-specific network checking
expect class NetworkMonitor() {
    fun isNetworkAvailable(): Boolean
    fun observeNetworkStatus(): Flow<Boolean>
}

// androidMain
actual class NetworkMonitor(private val context: Context) {
    private val connectivityManager = context.getSystemService(
        Context.CONNECTIVITY_SERVICE
    ) as ConnectivityManager

    actual fun isNetworkAvailable(): Boolean {
        val network = connectivityManager.activeNetwork ?: return false
        val capabilities = connectivityManager.getNetworkCapabilities(network)
        return capabilities?.hasCapability(
            NetworkCapabilities.NET_CAPABILITY_INTERNET
        ) == true
    }

    actual fun observeNetworkStatus(): Flow<Boolean> = callbackFlow {
        val callback = object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) {
                trySend(true)
            }

            override fun onLost(network: Network) {
                trySend(false)
            }
        }

        connectivityManager.registerDefaultNetworkCallback(callback)

        // Send initial state
        trySend(isNetworkAvailable())

        awaitClose {
            connectivityManager.unregisterNetworkCallback(callback)
        }
    }
}

// iosMain
actual class NetworkMonitor {
    private val reachability = SCNetworkReachabilityCreateWithName(
        null,
        "www.google.com"
    )

    actual fun isNetworkAvailable(): Boolean {
        var flags: SCNetworkReachabilityFlags = 0u
        SCNetworkReachabilityGetFlags(reachability, flags.ptr)
        return flags.toInt() and kSCNetworkReachabilityFlagsReachable != 0
    }

    actual fun observeNetworkStatus(): Flow<Boolean> = flow {
        // iOS implementation using NWPathMonitor
        // Simplified for brevity
        while (true) {
            emit(isNetworkAvailable())
            delay(1000)
        }
    }
}

// Usage with network check
class SafeApiClient(
    private val client: HttpClient,
    private val networkMonitor: NetworkMonitor
) {
    suspend fun <T> executeWithNetworkCheck(
        block: suspend () -> T
    ): Result<T> {
        if (!networkMonitor.isNetworkAvailable()) {
            return Result.failure(
                NetworkError.NoInternetError()
            )
        }

        return try {
            Result.success(block())
        } catch (e: Exception) {
            Result.failure(mapException(e))
        }
    }
}
```

#### Advanced Features

**1. Request/Response Interceptors**
```kotlin
// Request interceptor for analytics
class AnalyticsInterceptor(
    private val analytics: Analytics
) {
    fun install(client: HttpClient) {
        client.plugin(HttpSend).intercept { request ->
            val startTime = currentTimeMillis()

            analytics.logEvent("api_request_started") {
                param("endpoint", request.url.encodedPath)
                param("method", request.method.value)
            }

            val response = try {
                execute(request)
            } catch (e: Exception) {
                val duration = currentTimeMillis() - startTime

                analytics.logEvent("api_request_failed") {
                    param("endpoint", request.url.encodedPath)
                    param("duration_ms", duration)
                    param("error", e.message ?: "unknown")
                }

                throw e
            }

            val duration = currentTimeMillis() - startTime

            analytics.logEvent("api_request_completed") {
                param("endpoint", request.url.encodedPath)
                param("status_code", response.status.value)
                param("duration_ms", duration)
            }

            response
        }
    }
}

// Response caching
class CacheInterceptor(
    private val cache: ResponseCache
) {
    fun install(client: HttpClient) {
        client.plugin(HttpSend).intercept { request ->
            // Only cache GET requests
            if (request.method != HttpMethod.Get) {
                return@intercept execute(request)
            }

            val cacheKey = request.url.toString()

            // Check cache first
            cache.get(cacheKey)?.let { cachedResponse ->
                if (!cachedResponse.isExpired()) {
                    Logger.d { "Cache hit: $cacheKey" }
                    return@intercept cachedResponse.toHttpResponse()
                }
            }

            // Execute request
            val response = execute(request)

            // Cache successful responses
            if (response.status.isSuccess()) {
                val cacheControl = response.headers["Cache-Control"]
                val maxAge = parseCacheControl(cacheControl)

                if (maxAge > 0) {
                    cache.put(
                        key = cacheKey,
                        response = CachedResponse.from(response, maxAge)
                    )
                }
            }

            response
        }
    }
}
```

**2. File Upload/Download**
```kotlin
// File upload with progress
suspend fun HttpClient.uploadFile(
    url: String,
    file: ByteArray,
    fileName: String,
    onProgress: (Float) -> Unit
): Result<UploadResponse> {
    return try {
        val response = post(url) {
            setBody(
                MultiPartFormDataContent(
                    formData {
                        append("file", file, Headers.build {
                            append(HttpHeaders.ContentType, "image/jpeg")
                            append(HttpHeaders.ContentDisposition, "filename=$fileName")
                        })
                    }
                )
            )

            onUpload { bytesSentTotal, contentLength ->
                val progress = bytesSentTotal.toFloat() / contentLength.toFloat()
                onProgress(progress)
            }
        }

        Result.success(response.body<UploadResponse>())
    } catch (e: Exception) {
        Result.failure(mapException(e))
    }
}

// File download with progress
suspend fun HttpClient.downloadFile(
    url: String,
    onProgress: (Float) -> Unit
): Result<ByteArray> {
    return try {
        val response = get(url) {
            onDownload { bytesSentTotal, contentLength ->
                val progress = bytesSentTotal.toFloat() / contentLength.toFloat()
                onProgress(progress)
            }
        }

        Result.success(response.body<ByteArray>())
    } catch (e: Exception) {
        Result.failure(mapException(e))
    }
}
```

**3. GraphQL Support**
```kotlin
// GraphQL client
class GraphQLClient(
    private val client: HttpClient,
    private val endpoint: String = "https://api.example.com/graphql"
) {
    suspend inline fun <reified T> query(
        query: String,
        variables: Map<String, Any> = emptyMap()
    ): Result<T> {
        return try {
            val response = client.post(endpoint) {
                contentType(ContentType.Application.Json)
                setBody(GraphQLRequest(query, variables))
            }.body<GraphQLResponse<T>>()

            if (response.errors != null) {
                Result.failure(
                    Exception(response.errors.joinToString { it.message })
                )
            } else {
                Result.success(response.data!!)
            }
        } catch (e: Exception) {
            Result.failure(mapException(e))
        }
    }
}

@Serializable
data class GraphQLRequest(
    val query: String,
    val variables: Map<String, Any> = emptyMap()
)

@Serializable
data class GraphQLResponse<T>(
    val data: T? = null,
    val errors: List<GraphQLError>? = null
)

@Serializable
data class GraphQLError(
    val message: String,
    val path: List<String>? = null
)

// Usage
val client = GraphQLClient(httpClient)

val result = client.query<UserQuery>("""
    query GetUser(${'$'}id: ID!) {
        user(id: ${'$'}id) {
            id
            name
            email
        }
    }
""", mapOf("id" to "123"))
```

#### Testing

**1. Mock Client for Testing**
```kotlin
// commonTest
class MockHttpClient {
    fun create(
        mockResponses: Map<String, MockResponse> = emptyMap()
    ): HttpClient {
        return HttpClient(MockEngine) {
            engine {
                addHandler { request ->
                    val endpoint = request.url.encodedPath
                    val mockResponse = mockResponses[endpoint]
                        ?: return@addHandler respondError(HttpStatusCode.NotFound)

                    respond(
                        content = mockResponse.content,
                        status = mockResponse.status,
                        headers = headersOf(
                            HttpHeaders.ContentType to listOf(
                                ContentType.Application.Json.toString()
                            )
                        )
                    )
                }
            }

            install(ContentNegotiation) {
                json()
            }
        }
    }
}

data class MockResponse(
    val content: String,
    val status: HttpStatusCode = HttpStatusCode.OK
)

// Test
class UserRepositoryTest {
    @Test
    fun `getUser returns user on success`() = runTest {
        val mockClient = MockHttpClient().create(
            mapOf(
                "/users/123" to MockResponse(
                    content = """{"id":"123","name":"John"}""",
                    status = HttpStatusCode.OK
                )
            )
        )

        val repository = UserRepository(mockClient)
        val result = repository.getUser("123")

        assertTrue(result.isSuccess)
        assertEquals("John", result.getOrNull()?.name)
    }
}
```

### Summary

Ktor provides comprehensive multiplatform networking:
- **Platform Engines**: OkHttp (Android), NSURLSession (iOS)
- **Authentication**: Bearer tokens, OAuth, API keys with auto-refresh
- **Retry Logic**: Exponential backoff, conditional retries
- **Error Handling**: Type-safe errors, network monitoring
- **Advanced Features**: Interceptors, caching, file upload/download
- **Testing**: Mock engine for unit tests

Key considerations: proper error handling, retry strategies, authentication management, and platform-specific optimizations.

---

# Вопрос (RU)
> 
Объясните как использовать Ktor client для multiplatform networking в KMM проектах. Как настроить platform-specific engines, обработать аутентификацию, реализовать retry логику и управлять network ошибками на Android и iOS?

## Ответ (RU)
Ktor — рекомендуемый HTTP client для Kotlin Multiplatform, предоставляющий единый API с platform-optimized engines (OkHttp для Android, NSURLSession для iOS) и comprehensive plugin support.

#### Ключевые возможности

**Platform Engines**:
- Android: OkHttp (производительный, feature-rich)
- iOS: NSURLSession (native, iOS-оптимизирован)
- Автоматический выбор оптимального engine

**Plugins**:
- ContentNegotiation: JSON serialization/deserialization
- Auth: Bearer tokens, OAuth, custom auth
- Logging: Детальное логирование запросов
- HttpTimeout: Таймауты запросов
- Retry: Автоматические повторы

#### Аутентификация

**Bearer Token**:
- Auto-refresh на 401
- Secure token storage
- Concurrent request handling

**OAuth 2.0**:
- Authorization code flow
- Client credentials
- Refresh token rotation

#### Retry Logic

**Стратегии**:
- Exponential backoff (1s, 2s, 4s, 8s)
- Linear backoff
- Custom delay functions

**Retryable условия**:
- Timeout errors
- Network errors
- 5xx server errors
- 429 Too Many Requests (с Retry-After)

#### Error Handling

**Type-safe errors**:
- HttpError (4xx, 5xx)
- TimeoutError
- NoInternetError
- SerializationError
- UnknownError

**Network monitoring**:
- Real-time connectivity status
- Platform-specific APIs
- Reactive Flow<Boolean>

#### Advanced Features

**Interceptors**:
- Request/response logging
- Analytics tracking
- Custom headers injection
- Response caching

**File Operations**:
- Upload с progress
- Download с progress
- Multipart form data

**GraphQL**:
- Query/mutation support
- Error handling
- Variable substitution

### Резюме

Ktor обеспечивает полнофункциональный networking:
- **Unified API**: Один код для Android и iOS
- **Platform-optimized**: Нативные engines
- **Type-safe**: Compile-time проверки
- **Feature-rich**: Auth, retry, logging, caching
- **Testable**: Mock engine для unit tests

Ключевые моменты: правильная обработка ошибок, retry стратегии, authentication management, platform-specific оптимизации.

---

## Related Questions

### Prerequisites (Easier)
- [[q-graphql-vs-rest--networking--easy]] - Networking

### Related (Medium)
- [[q-http-protocols-comparison--android--medium]] - Networking
- [[q-retrofit-call-adapter-advanced--networking--medium]] - Networking
- [[q-network-error-handling-strategies--networking--medium]] - Networking
- [[q-okhttp-interceptors-advanced--networking--medium]] - Networking
- [[q-graphql-apollo-android--networking--medium]] - Networking

### Advanced (Harder)
- [[q-data-sync-unstable-network--android--hard]] - Networking
- [[q-network-request-deduplication--networking--hard]] - Networking
