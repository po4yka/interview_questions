---
id: 20251012-12271156
title: "Okhttp Interceptors Advanced / Продвинутые перехватчики OkHttp"
topic: networking
difficulty: medium
status: draft
created: 2025-10-15
tags: [okhttp, interceptors, authentication, caching, retry, difficulty/medium]
---
# OkHttp Interceptors Advanced / Продвинутые интерцепторы OkHttp

**English**: Implement custom OkHttp interceptors for authentication refresh, request retry, and response caching. Explain application vs network interceptor chain order.

## Answer (EN)
**OkHttp Interceptors** are powerful mechanisms for observing, modifying, and potentially short-circuiting HTTP requests and responses. They enable cross-cutting concerns like authentication, logging, caching, and error handling to be implemented cleanly without polluting business logic.

### Understanding Interceptor Types

OkHttp has two types of interceptors with different execution contexts:

#### Application Interceptors

- Execute first in the chain, closest to your application code
- Called once per request, even if HTTP response is served from cache
- See the original request before redirects and retries
- Don't see intermediate responses from redirects
- Can short-circuit and not call the network

#### Network Interceptors

- Execute last, just before the network call
- Called for every network request, including retries
- See the complete request going to network (after headers added)
- Observe actual network data
- Cannot short-circuit without making a network call

### Interceptor Chain Order

```
Application Code
      ↓
Application Interceptor 1
      ↓
Application Interceptor 2
      ↓
RetryAndFollowUpInterceptor (OkHttp internal)
      ↓
BridgeInterceptor (OkHttp internal - adds headers)
      ↓
CacheInterceptor (OkHttp internal)
      ↓
ConnectInterceptor (OkHttp internal)
      ↓
Network Interceptor 1
      ↓
Network Interceptor 2
      ↓
CallServerInterceptor (OkHttp internal - actual network call)
      ↓
Network
```

### Complete Implementation

Let's implement a production-ready OkHttp client with custom interceptors.

#### 1. Authentication Token Refresh Interceptor

This interceptor handles automatic token refresh when receiving 401 responses.

```kotlin
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import okhttp3.Interceptor
import okhttp3.Response
import java.io.IOException
import java.util.concurrent.atomic.AtomicBoolean

class AuthenticationInterceptor(
    private val tokenProvider: TokenProvider
) : Interceptor {

    private val refreshMutex = Mutex()
    private val isRefreshing = AtomicBoolean(false)

    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()

        // Add current token to request
        val token = tokenProvider.getAccessToken()
        val authenticatedRequest = originalRequest.newBuilder()
            .apply {
                if (token != null) {
                    header("Authorization", "Bearer $token")
                }
            }
            .build()

        // Make the request
        var response = chain.proceed(authenticatedRequest)

        // If unauthorized, try to refresh token
        if (response.code == 401 && !originalRequest.url.encodedPath.contains("/auth/")) {
            response.close()
            response = handleUnauthorized(chain, originalRequest)
        }

        return response
    }

    private fun handleUnauthorized(
        chain: Interceptor.Chain,
        originalRequest: okhttp3.Request
    ): Response {
        return runBlocking {
            // Use mutex to ensure only one thread refreshes token
            refreshMutex.withLock {
                // Check if token was already refreshed by another thread
                val currentToken = tokenProvider.getAccessToken()
                val requestToken = originalRequest.header("Authorization")
                    ?.removePrefix("Bearer ")

                // If token has changed, another thread already refreshed it
                if (currentToken != requestToken && currentToken != null) {
                    return@withLock retryWithNewToken(chain, originalRequest, currentToken)
                }

                // Attempt to refresh token
                try {
                    val newToken = tokenProvider.refreshToken()
                    if (newToken != null) {
                        retryWithNewToken(chain, originalRequest, newToken)
                    } else {
                        // Refresh failed, user needs to re-authenticate
                        tokenProvider.clearTokens()
                        chain.proceed(originalRequest)
                    }
                } catch (e: Exception) {
                    tokenProvider.clearTokens()
                    chain.proceed(originalRequest)
                }
            }
        }
    }

    private fun retryWithNewToken(
        chain: Interceptor.Chain,
        originalRequest: okhttp3.Request,
        token: String
    ): Response {
        val newRequest = originalRequest.newBuilder()
            .header("Authorization", "Bearer $token")
            .build()

        return chain.proceed(newRequest)
    }
}

interface TokenProvider {
    fun getAccessToken(): String?
    fun getRefreshToken(): String?
    suspend fun refreshToken(): String?
    fun clearTokens()
}

class TokenProviderImpl(
    private val tokenStorage: TokenStorage,
    private val authApi: AuthApi
) : TokenProvider {

    override fun getAccessToken(): String? {
        return tokenStorage.getAccessToken()
    }

    override fun getRefreshToken(): String? {
        return tokenStorage.getRefreshToken()
    }

    override suspend fun refreshToken(): String? {
        val refreshToken = getRefreshToken() ?: return null

        return try {
            val response = authApi.refreshToken(RefreshTokenRequest(refreshToken))
            if (response.isSuccessful && response.body() != null) {
                val tokens = response.body()!!
                tokenStorage.saveTokens(tokens.accessToken, tokens.refreshToken)
                tokens.accessToken
            } else {
                null
            }
        } catch (e: Exception) {
            null
        }
    }

    override fun clearTokens() {
        tokenStorage.clearTokens()
    }
}
```

#### 2. Retry Interceptor with Exponential Backoff

Automatically retries failed requests with configurable strategy.

```kotlin
import okhttp3.Interceptor
import okhttp3.Response
import java.io.IOException
import kotlin.math.pow

class RetryInterceptor(
    private val maxRetries: Int = 3,
    private val initialDelayMs: Long = 1000L,
    private val maxDelayMs: Long = 10000L,
    private val factor: Double = 2.0,
    private val retryableStatusCodes: Set<Int> = setOf(408, 429, 500, 502, 503, 504)
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        var request = chain.request()
        var response: Response? = null
        var exception: IOException? = null

        var retryCount = 0

        while (retryCount <= maxRetries) {
            try {
                // Close previous response if exists
                response?.close()

                // Make the request
                response = chain.proceed(request)

                // If successful or non-retryable error, return response
                if (response.isSuccessful || !isRetryable(response.code)) {
                    return response
                }

                // Close response before retry
                response.close()

                // Don't retry if we've exhausted attempts
                if (retryCount >= maxRetries) {
                    // Re-make request one final time to return the error response
                    return chain.proceed(request)
                }

                // Calculate delay with exponential backoff
                val delay = calculateDelay(retryCount)

                // Check for Retry-After header
                val retryAfter = response.header("Retry-After")?.toLongOrNull()
                val actualDelay = retryAfter?.let { it * 1000 } ?: delay

                Thread.sleep(actualDelay)

            } catch (e: IOException) {
                exception = e

                // Don't retry on last attempt
                if (retryCount >= maxRetries) {
                    throw e
                }

                // Calculate delay and retry
                val delay = calculateDelay(retryCount)
                Thread.sleep(delay)
            }

            retryCount++
        }

        // If we get here, throw the last exception
        throw exception ?: IOException("Max retries exceeded")
    }

    private fun isRetryable(statusCode: Int): Boolean {
        return statusCode in retryableStatusCodes
    }

    private fun calculateDelay(retryCount: Int): Long {
        val delay = initialDelayMs * factor.pow(retryCount).toLong()
        return delay.coerceAtMost(maxDelayMs)
    }
}
```

#### 3. Custom Cache Interceptor

Implements intelligent caching strategies based on network availability and custom headers.

```kotlin
import android.content.Context
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import okhttp3.CacheControl
import okhttp3.Interceptor
import okhttp3.Response
import java.util.concurrent.TimeUnit

class CacheInterceptor(
    private val context: Context,
    private val onlineMaxAge: Int = 60, // 1 minute
    private val offlineMaxStale: Int = 60 * 60 * 24 * 7 // 7 days
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        var request = chain.request()

        // Check network connectivity
        val isOnline = isNetworkAvailable()

        // Modify request cache control based on connectivity
        if (!isOnline) {
            // If offline, serve from cache even if stale
            val cacheControl = CacheControl.Builder()
                .maxStale(offlineMaxStale, TimeUnit.SECONDS)
                .build()

            request = request.newBuilder()
                .cacheControl(cacheControl)
                .build()
        }

        // Proceed with request
        val response = chain.proceed(request)

        // Modify response cache control
        return if (isOnline) {
            // If online, cache for a short time
            val cacheControl = CacheControl.Builder()
                .maxAge(onlineMaxAge, TimeUnit.SECONDS)
                .build()

            response.newBuilder()
                .removeHeader("Pragma")
                .removeHeader("Cache-Control")
                .header("Cache-Control", cacheControl.toString())
                .build()
        } else {
            // If offline, allow serving stale cache
            val cacheControl = CacheControl.Builder()
                .maxStale(offlineMaxStale, TimeUnit.SECONDS)
                .build()

            response.newBuilder()
                .removeHeader("Pragma")
                .removeHeader("Cache-Control")
                .header("Cache-Control", cacheControl.toString())
                .build()
        }
    }

    private fun isNetworkAvailable(): Boolean {
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE)
            as ConnectivityManager

        val network = connectivityManager.activeNetwork ?: return false
        val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false

        return capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET) &&
               capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED)
    }
}

// Network-only cache interceptor (goes in network interceptor chain)
class NetworkCacheInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val response = chain.proceed(chain.request())

        // Read cache control from response or set default
        val cacheControl = response.header("Cache-Control")
            ?: "public, max-age=60"

        return response.newBuilder()
            .removeHeader("Pragma")
            .header("Cache-Control", cacheControl)
            .build()
    }
}
```

#### 4. Logging Interceptor

Comprehensive logging of requests and responses for debugging.

```kotlin
import okhttp3.Interceptor
import okhttp3.Response
import okhttp3.internal.http.promisesBody
import okio.Buffer
import okio.GzipSource
import java.nio.charset.Charset
import java.nio.charset.StandardCharsets
import java.util.concurrent.TimeUnit

class DetailedLoggingInterceptor(
    private val logger: Logger = Logger.Default,
    private val level: Level = Level.BODY
) : Interceptor {

    enum class Level {
        NONE,        // No logging
        BASIC,       // Request/response line only
        HEADERS,     // Request/response line + headers
        BODY         // Request/response line + headers + body
    }

    interface Logger {
        fun log(message: String)

        object Default : Logger {
            override fun log(message: String) {
                println(message)
            }
        }
    }

    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()

        if (level == Level.NONE) {
            return chain.proceed(request)
        }

        val logHeaders = level == Level.HEADERS || level == Level.BODY
        val logBody = level == Level.BODY

        // Log request
        logger.log("")
        logger.log(" REQUEST")
        logger.log("")
        logger.log(" ${request.method} ${request.url}")

        if (logHeaders) {
            val headers = request.headers
            for (i in 0 until headers.size) {
                logHeader(headers.name(i), headers.value(i))
            }

            if (logBody && request.body != null) {
                logger.log("")
                val buffer = Buffer()
                request.body!!.writeTo(buffer)

                val charset = request.body!!.contentType()?.charset(StandardCharsets.UTF_8)
                    ?: StandardCharsets.UTF_8

                if (buffer.isProbablyUtf8()) {
                    logger.log(" Body: ${buffer.readString(charset)}")
                    logger.log(" Body Size: ${request.body!!.contentLength()} bytes")
                } else {
                    logger.log(" Body: (binary ${request.body!!.contentLength()} bytes)")
                }
            }
        }

        // Make request
        val startTime = System.nanoTime()
        val response: Response
        try {
            response = chain.proceed(request)
        } catch (e: Exception) {
            logger.log("")
            logger.log(" EXCEPTION")
            logger.log("")
            logger.log(" ${e.javaClass.simpleName}: ${e.message}")
            logger.log("")
            throw e
        }

        val durationMs = TimeUnit.NANOSECONDS.toMillis(System.nanoTime() - startTime)

        // Log response
        logger.log("")
        logger.log(" RESPONSE")
        logger.log("")
        logger.log(" ${response.code} ${response.message} (${durationMs}ms)")
        logger.log(" ${response.request.url}")

        if (logHeaders) {
            val headers = response.headers
            for (i in 0 until headers.size) {
                logHeader(headers.name(i), headers.value(i))
            }

            if (logBody && response.promisesBody()) {
                logger.log("")

                val source = response.body!!.source()
                source.request(Long.MAX_VALUE)
                var buffer = source.buffer

                var gzippedLength: Long? = null
                if ("gzip".equals(response.header("Content-Encoding"), ignoreCase = true)) {
                    gzippedLength = buffer.size
                    GzipSource(buffer.clone()).use { gzippedResponseBody ->
                        buffer = Buffer()
                        buffer.writeAll(gzippedResponseBody)
                    }
                }

                val contentType = response.body!!.contentType()
                val charset: Charset = contentType?.charset(StandardCharsets.UTF_8)
                    ?: StandardCharsets.UTF_8

                if (!buffer.isProbablyUtf8()) {
                    logger.log(" Body: (binary ${buffer.size} bytes)")
                } else {
                    if (buffer.size != 0L) {
                        val body = buffer.clone().readString(charset)
                        logger.log(" Body: $body")
                    }

                    if (gzippedLength != null) {
                        logger.log(" Body Size: ${buffer.size} bytes (gzipped: $gzippedLength bytes)")
                    } else {
                        logger.log(" Body Size: ${buffer.size} bytes")
                    }
                }
            }
        }

        logger.log("")

        return response
    }

    private fun logHeader(name: String, value: String) {
        // Redact sensitive headers
        val redactedValue = when (name.lowercase()) {
            "authorization", "cookie", "set-cookie" -> ""
            else -> value
        }
        logger.log(" $name: $redactedValue")
    }

    private fun Buffer.isProbablyUtf8(): Boolean {
        try {
            val prefix = Buffer()
            val byteCount = size.coerceAtMost(64)
            copyTo(prefix, 0, byteCount)

            for (i in 0 until 16) {
                if (prefix.exhausted()) {
                    break
                }
                val codePoint = prefix.readUtf8CodePoint()
                if (Character.isISOControl(codePoint) && !Character.isWhitespace(codePoint)) {
                    return false
                }
            }
            return true
        } catch (e: Exception) {
            return false
        }
    }
}
```

#### 5. Complete OkHttpClient Configuration

Putting it all together with proper configuration.

```kotlin
import android.content.Context
import okhttp3.Cache
import okhttp3.OkHttpClient
import java.io.File
import java.util.concurrent.TimeUnit

class OkHttpClientFactory(
    private val context: Context,
    private val tokenProvider: TokenProvider,
    private val enableLogging: Boolean = BuildConfig.DEBUG
) {

    fun create(): OkHttpClient {
        return OkHttpClient.Builder()
            .apply {
                // Timeouts
                connectTimeout(30, TimeUnit.SECONDS)
                readTimeout(30, TimeUnit.SECONDS)
                writeTimeout(30, TimeUnit.SECONDS)

                // Cache (10 MB)
                cache(createCache())

                // Application Interceptors
                // (Executed first, see original request)

                // 1. Logging (see what app sends)
                if (enableLogging) {
                    addInterceptor(
                        DetailedLoggingInterceptor(
                            level = DetailedLoggingInterceptor.Level.BODY
                        )
                    )
                }

                // 2. Authentication (add auth headers)
                addInterceptor(AuthenticationInterceptor(tokenProvider))

                // 3. Custom cache logic
                addInterceptor(CacheInterceptor(context))

                // 4. Retry logic
                addInterceptor(RetryInterceptor(maxRetries = 3))

                // Network Interceptors
                // (Executed last, see actual network request)

                // 1. Network cache headers
                addNetworkInterceptor(NetworkCacheInterceptor())

                // 2. Network logging (see what goes on wire)
                if (enableLogging) {
                    addNetworkInterceptor(
                        DetailedLoggingInterceptor(
                            level = DetailedLoggingInterceptor.Level.HEADERS
                        )
                    )
                }

                // Connection pool
                connectionPool(okhttp3.ConnectionPool(
                    maxIdleConnections = 5,
                    keepAliveDuration = 5,
                    timeUnit = TimeUnit.MINUTES
                ))

                // Retry on connection failure
                retryOnConnectionFailure(true)
            }
            .build()
    }

    private fun createCache(): Cache {
        val cacheDir = File(context.cacheDir, "http_cache")
        val cacheSize = 10L * 1024 * 1024 // 10 MB
        return Cache(cacheDir, cacheSize)
    }
}
```

### Real-World Example: Complete API Client

```kotlin
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.*

// API Service
interface ApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: String): Response<User>

    @GET("users/{id}/posts")
    suspend fun getUserPosts(@Path("id") userId: String): Response<List<Post>>

    @POST("posts")
    suspend fun createPost(@Body post: CreatePostRequest): Response<Post>

    @PUT("posts/{id}")
    suspend fun updatePost(
        @Path("id") postId: String,
        @Body post: UpdatePostRequest
    ): Response<Post>

    @DELETE("posts/{id}")
    suspend fun deletePost(@Path("id") postId: String): Response<Unit>
}

// Auth API (separate client without auth interceptor to avoid loops)
interface AuthApi {
    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): Response<TokenResponse>

    @POST("auth/refresh")
    suspend fun refreshToken(@Body request: RefreshTokenRequest): Response<TokenResponse>

    @POST("auth/logout")
    suspend fun logout(): Response<Unit>
}

// API Client Factory
class ApiClientFactory(
    private val context: Context,
    private val baseUrl: String = "https://api.example.com/"
) {

    private val tokenStorage = TokenStorageImpl(context)
    private val gson = GsonBuilder()
        .setFieldNamingPolicy(FieldNamingPolicy.LOWER_CASE_WITH_UNDERSCORES)
        .create()

    // Auth API client (no auth interceptor)
    private val authOkHttpClient by lazy {
        OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .addInterceptor(
                DetailedLoggingInterceptor(
                    level = if (BuildConfig.DEBUG) {
                        DetailedLoggingInterceptor.Level.BODY
                    } else {
                        DetailedLoggingInterceptor.Level.NONE
                    }
                )
            )
            .build()
    }

    val authApi: AuthApi by lazy {
        Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(authOkHttpClient)
            .addConverterFactory(GsonConverterFactory.create(gson))
            .build()
            .create(AuthApi::class.java)
    }

    // Regular API client (with full interceptor chain)
    private val apiOkHttpClient by lazy {
        val tokenProvider = TokenProviderImpl(tokenStorage, authApi)
        OkHttpClientFactory(context, tokenProvider, BuildConfig.DEBUG).create()
    }

    val apiService: ApiService by lazy {
        Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(apiOkHttpClient)
            .addConverterFactory(GsonConverterFactory.create(gson))
            .build()
            .create(ApiService::class.java)
    }
}

// Repository layer
class UserRepository(
    private val apiService: ApiService,
    private val userDao: UserDao
) {

    suspend fun getUser(userId: String): Result<User> {
        return try {
            val response = apiService.getUser(userId)
            if (response.isSuccessful && response.body() != null) {
                val user = response.body()!!
                // Cache in database
                userDao.insertUser(user)
                Result.success(user)
            } else {
                // Try cache on error
                val cachedUser = userDao.getUserById(userId)
                if (cachedUser != null) {
                    Result.success(cachedUser)
                } else {
                    Result.failure(HttpException(response))
                }
            }
        } catch (e: IOException) {
            // Network error, try cache
            val cachedUser = userDao.getUserById(userId)
            if (cachedUser != null) {
                Result.success(cachedUser)
            } else {
                Result.failure(e)
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### Testing Interceptors

```kotlin
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.After
import org.junit.Before
import org.junit.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class InterceptorTest {

    private lateinit var mockWebServer: MockWebServer
    private lateinit var okHttpClient: OkHttpClient

    @Before
    fun setup() {
        mockWebServer = MockWebServer()
        mockWebServer.start()

        okHttpClient = OkHttpClient.Builder()
            .addInterceptor(RetryInterceptor(maxRetries = 3, initialDelayMs = 100))
            .build()
    }

    @After
    fun teardown() {
        mockWebServer.shutdown()
    }

    @Test
    fun `retry interceptor retries on 503`() {
        // Setup: Return 503 twice, then 200
        mockWebServer.enqueue(MockResponse().setResponseCode(503))
        mockWebServer.enqueue(MockResponse().setResponseCode(503))
        mockWebServer.enqueue(MockResponse().setResponseCode(200).setBody("Success"))

        // Execute
        val request = okhttp3.Request.Builder()
            .url(mockWebServer.url("/test"))
            .build()

        val response = okHttpClient.newCall(request).execute()

        // Verify
        assertTrue(response.isSuccessful)
        assertEquals("Success", response.body?.string())
        assertEquals(3, mockWebServer.requestCount) // 2 retries + 1 success
    }

    @Test
    fun `auth interceptor adds bearer token`() {
        val tokenProvider = object : TokenProvider {
            override fun getAccessToken() = "test_token"
            override fun getRefreshToken() = "refresh_token"
            override suspend fun refreshToken() = null
            override fun clearTokens() {}
        }

        val client = OkHttpClient.Builder()
            .addInterceptor(AuthenticationInterceptor(tokenProvider))
            .build()

        mockWebServer.enqueue(MockResponse().setResponseCode(200))

        val request = okhttp3.Request.Builder()
            .url(mockWebServer.url("/test"))
            .build()

        client.newCall(request).execute()

        val recordedRequest = mockWebServer.takeRequest()
        assertEquals("Bearer test_token", recordedRequest.getHeader("Authorization"))
    }
}
```

### Best Practices

1. **Order Matters**: Place interceptors in logical order
   - Application: Logging → Auth → Cache → Retry
   - Network: Cache headers → Logging

2. **Avoid Blocking Operations**: Don't perform long-running operations in interceptors

3. **Handle Exceptions Gracefully**: Interceptors should not throw unexpected exceptions

4. **Close Responses**: Always close response bodies when creating new responses

5. **Use Appropriate Interceptor Type**:
   - Application: When you need to see original request
   - Network: When you need to see actual network data

6. **Thread Safety**: Ensure interceptors are thread-safe, especially for token refresh

7. **Avoid Infinite Loops**: Be careful with auth interceptors to not create retry loops

8. **Log Sensitive Data Carefully**: Redact tokens, passwords, and PII in logs

9. **Test Thoroughly**: Write unit tests for complex interceptor logic

10. **Performance**: Keep interceptors lightweight, avoid heavy computation

### Common Pitfalls

1. **Auth Loop**: Auth interceptor calling authenticated endpoint during refresh
   ```kotlin
   // BAD: Creates infinite loop
   private fun refreshToken() {
       apiService.refreshToken() // This adds auth header → 401 → refresh → loop
   }

   // GOOD: Separate auth API without auth interceptor
   private fun refreshToken() {
       authApi.refreshToken() // Uses different client
   }
   ```

2. **Not Closing Responses**: Memory leaks from unclosed response bodies
   ```kotlin
   // BAD
   val response = chain.proceed(request)
   return chain.proceed(modifiedRequest) // Original response leaked

   // GOOD
   val response = chain.proceed(request)
   response.close()
   return chain.proceed(modifiedRequest)
   ```

3. **Blocking Network Calls**: Making synchronous network calls in interceptor
   ```kotlin
   // BAD: Blocks OkHttp thread
   override fun intercept(chain: Interceptor.Chain): Response {
       val data = fetchFromNetwork() // Blocking call
       return chain.proceed(request)
   }
   ```

4. **Not Thread-Safe Token Refresh**: Multiple threads refreshing simultaneously
   - Use Mutex or synchronized block

5. **Excessive Logging in Production**: Degrades performance and exposes data
   - Use BuildConfig.DEBUG checks

6. **Cache Interceptor in Wrong Place**:
   - Application interceptor: Control what your app does
   - Network interceptor: Control what hits the network

7. **Not Handling Retry-After Header**: Ignoring server guidance on retries

8. **Infinite Retry Loops**: Not limiting retry attempts

### Performance Considerations

```kotlin
// Cache results where possible
private val authTokenCache = mutableMapOf<String, String>()

// Use efficient data structures
private val pendingRequests = ConcurrentHashMap<String, Deferred<Response>>()

// Minimize allocations
private val buffer = ThreadLocal<Buffer>()

// Avoid unnecessary string operations
// BAD: Creates many objects
val token = "Bearer " + provider.getToken()

// GOOD: Reuse string builder
val token = buildString {
    append("Bearer ")
    append(provider.getToken())
}
```

### Summary

OkHttp Interceptors provide:

- **Separation of Concerns**: Cross-cutting functionality isolated from business logic
- **Flexibility**: Application vs Network interceptors for different use cases
- **Chain of Responsibility**: Clean, composable request/response handling
- **Authentication**: Automatic token management and refresh
- **Retry Logic**: Resilient network calls with exponential backoff
- **Caching**: Intelligent offline support and performance optimization
- **Debugging**: Comprehensive logging for development
- **Testing**: Mockable and testable network layer

Master interceptors to build robust, maintainable Android networking code.

---

## Ответ (RU)
**Интерцепторы OkHttp** - мощные механизмы для наблюдения, модификации и потенциального прерывания HTTP-запросов и ответов. Они позволяют реализовать сквозную функциональность, такую как аутентификация, логирование, кеширование и обработку ошибок, не загрязняя бизнес-логику.

### Понимание типов интерцепторов

OkHttp имеет два типа интерцепторов с разными контекстами выполнения:

#### Application Interceptors (Интерцепторы приложения)

- Выполняются первыми в цепочке, ближайшие к коду приложения
- Вызываются один раз на запрос, даже если ответ берётся из кеша
- Видят оригинальный запрос перед редиректами и повторами
- Не видят промежуточные ответы от редиректов
- Могут прервать цепочку и не вызывать сеть

#### Network Interceptors (Сетевые интерцепторы)

- Выполняются последними, непосредственно перед сетевым вызовом
- Вызываются для каждого сетевого запроса, включая повторы
- Видят полный запрос, идущий в сеть (после добавления заголовков)
- Наблюдают реальные сетевые данные
- Не могут прервать цепочку без выполнения сетевого вызова

### Порядок цепочки интерцепторов

```
Код приложения
      ↓
Application Interceptor 1
      ↓
Application Interceptor 2
      ↓
RetryAndFollowUpInterceptor (внутренний OkHttp)
      ↓
BridgeInterceptor (внутренний OkHttp - добавляет заголовки)
      ↓
CacheInterceptor (внутренний OkHttp)
      ↓
ConnectInterceptor (внутренний OkHttp)
      ↓
Network Interceptor 1
      ↓
Network Interceptor 2
      ↓
CallServerInterceptor (внутренний OkHttp - реальный сетевой вызов)
      ↓
Сеть
```

### Интерцептор обновления токена аутентификации

```kotlin
class AuthenticationInterceptor(
    private val tokenProvider: TokenProvider
) : Interceptor {

    private val refreshMutex = Mutex()

    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()

        // Добавить текущий токен к запросу
        val token = tokenProvider.getAccessToken()
        val authenticatedRequest = originalRequest.newBuilder()
            .apply {
                if (token != null) {
                    header("Authorization", "Bearer $token")
                }
            }
            .build()

        // Выполнить запрос
        var response = chain.proceed(authenticatedRequest)

        // Если неавторизован, попытаться обновить токен
        if (response.code == 401) {
            response.close()
            response = handleUnauthorized(chain, originalRequest)
        }

        return response
    }

    private fun handleUnauthorized(
        chain: Interceptor.Chain,
        originalRequest: okhttp3.Request
    ): Response {
        return runBlocking {
            // Использовать mutex для синхронизации обновления токена
            refreshMutex.withLock {
                val newToken = tokenProvider.refreshToken()
                if (newToken != null) {
                    val newRequest = originalRequest.newBuilder()
                        .header("Authorization", "Bearer $newToken")
                        .build()
                    chain.proceed(newRequest)
                } else {
                    tokenProvider.clearTokens()
                    chain.proceed(originalRequest)
                }
            }
        }
    }
}
```

### Интерцептор повторных попыток с экспоненциальной задержкой

```kotlin
class RetryInterceptor(
    private val maxRetries: Int = 3,
    private val initialDelayMs: Long = 1000L,
    private val factor: Double = 2.0
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        var request = chain.request()
        var response: Response? = null
        var retryCount = 0

        while (retryCount <= maxRetries) {
            try {
                response?.close()
                response = chain.proceed(request)

                if (response.isSuccessful) {
                    return response
                }

                if (retryCount >= maxRetries) {
                    return response
                }

                // Вычислить задержку с экспоненциальным увеличением
                val delay = (initialDelayMs * factor.pow(retryCount)).toLong()
                Thread.sleep(delay)

            } catch (e: IOException) {
                if (retryCount >= maxRetries) throw e
                val delay = (initialDelayMs * factor.pow(retryCount)).toLong()
                Thread.sleep(delay)
            }

            retryCount++
        }

        throw IOException("Превышено максимальное количество повторов")
    }
}
```

### Интерцептор кеширования

```kotlin
class CacheInterceptor(
    private val context: Context,
    private val onlineMaxAge: Int = 60
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        var request = chain.request()
        val isOnline = isNetworkAvailable()

        if (!isOnline) {
            // Если оффлайн, использовать кеш даже если устарел
            val cacheControl = CacheControl.Builder()
                .maxStale(7, TimeUnit.DAYS)
                .build()

            request = request.newBuilder()
                .cacheControl(cacheControl)
                .build()
        }

        val response = chain.proceed(request)

        return if (isOnline) {
            // Если онлайн, кешировать на короткое время
            response.newBuilder()
                .header("Cache-Control", "public, max-age=$onlineMaxAge")
                .build()
        } else {
            response
        }
    }

    private fun isNetworkAvailable(): Boolean {
        val cm = context.getSystemService(Context.CONNECTIVITY_SERVICE)
            as ConnectivityManager
        val network = cm.activeNetwork ?: return false
        val capabilities = cm.getNetworkCapabilities(network) ?: return false
        return capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
    }
}
```

### Полная конфигурация OkHttpClient

```kotlin
class OkHttpClientFactory(
    private val context: Context,
    private val tokenProvider: TokenProvider
) {

    fun create(): OkHttpClient {
        return OkHttpClient.Builder()
            .apply {
                // Таймауты
                connectTimeout(30, TimeUnit.SECONDS)
                readTimeout(30, TimeUnit.SECONDS)
                writeTimeout(30, TimeUnit.SECONDS)

                // Кеш (10 МБ)
                cache(Cache(File(context.cacheDir, "http"), 10 * 1024 * 1024))

                // Application Interceptors
                addInterceptor(DetailedLoggingInterceptor())
                addInterceptor(AuthenticationInterceptor(tokenProvider))
                addInterceptor(CacheInterceptor(context))
                addInterceptor(RetryInterceptor(maxRetries = 3))

                // Network Interceptors
                addNetworkInterceptor(NetworkCacheInterceptor())
            }
            .build()
    }
}
```

### Best Practices

1. **Порядок важен**: Размещайте интерцепторы в логическом порядке

2. **Избегайте блокирующих операций**: Не выполняйте долгие операции

3. **Обрабатывайте исключения gracefully**: Не бросайте неожиданные исключения

4. **Закрывайте ответы**: Всегда закрывайте тела ответов

5. **Используйте подходящий тип**:
   - Application: когда нужен оригинальный запрос
   - Network: когда нужны реальные сетевые данные

6. **Потокобезопасность**: Обеспечьте потокобезопасность интерцепторов

7. **Избегайте бесконечных циклов**: Осторожно с auth интерцепторами

8. **Логируйте осторожно**: Скрывайте токены и конфиденциальные данные

### Распространённые ошибки

1. **Цикл аутентификации**: Auth интерцептор вызывает защищённый эндпоинт при обновлении

2. **Не закрывать ответы**: Утечки памяти

3. **Блокирующие сетевые вызовы**: Синхронные вызовы в интерцепторе

4. **Небезопасное обновление токена**: Множество потоков обновляют одновременно

5. **Избыточное логирование в production**: Снижает производительность

### Резюме

Интерцепторы OkHttp обеспечивают:

- **Разделение ответственности**: Изоляция сквозной функциональности
- **Гибкость**: Application и Network интерцепторы
- **Цепочка обязанностей**: Чистая композиция обработки
- **Аутентификация**: Автоматическое управление токенами
- **Повторы**: Устойчивые сетевые вызовы
- **Кеширование**: Оффлайн поддержка и оптимизация
- **Отладка**: Подробное логирование
- **Тестирование**: Тестируемый сетевой слой

---

## Related Questions

### Prerequisites (Easier)
- [[q-graphql-vs-rest--networking--easy]] - Networking

### Related (Medium)
- [[q-http-protocols-comparison--android--medium]] - Networking
- [[q-kmm-ktor-networking--multiplatform--medium]] - Networking
- [[q-retrofit-call-adapter-advanced--networking--medium]] - Networking
- [[q-network-error-handling-strategies--networking--medium]] - Networking
- [[q-graphql-apollo-android--networking--medium]] - Networking

### Advanced (Harder)
- [[q-data-sync-unstable-network--android--hard]] - Networking
- [[q-network-request-deduplication--networking--hard]] - Networking
