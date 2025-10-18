---
id: 20251012-12271184
title: "Retrofit Modify All Requests / Изменение всех запросов Retrofit"
topic: android
difficulty: hard
status: draft
created: 2025-10-13
tags: [android/networking, authentication, interceptor, logging, networking, okhttp, retrofit, difficulty/hard]
moc: moc-android
related: [q-room-relations-embedded--room--medium, q-what-are-services-used-for--android--medium, q-view-fundamentals--android--easy]
  - q-http-protocols-comparison--android--medium
  - q-retrofit-call-adapter-advanced--networking--medium
  - q-retrofit-usage-tutorial--android--medium
  - q-data-sync-unstable-network--android--hard
---
# Как в Ретрофите изменять все запросы?

**English**: How to modify all requests globally in Retrofit?

## Answer (EN)
In Retrofit, you can modify all requests globally using **Interceptor** (перехватчик) in OkHttp. This allows you to add or modify headers, query parameters, authentication, logging, and more.

**Common uses:**
1. **Add headers** (authorization, API keys)
2. **Add query parameters** (API version, language)
3. **Logging** (request/response details)
4. **Refresh token** (automatic re-authentication)
5. **Modify base URL** dynamically

---

## What is an Interceptor?

An **Interceptor** is a mechanism in OkHttp that intercepts network requests/responses and allows you to modify them before they're sent or after they're received.

```
Client → Interceptor → Network → Server
       ↑              ↓
       
    Can modify request/response
```

---

## Types of Interceptors

### 1. Application Interceptor

- Runs **first**, before network connection
- Can modify request before it reaches the network
- Use for: adding headers, logging, retries

```kotlin
okHttpClient.addInterceptor(MyInterceptor())  // Application interceptor
```

---

### 2. Network Interceptor

- Runs **closer to network**, after URL rewriting
- Sees actual network request
- Use for: low-level network logging

```kotlin
okHttpClient.addNetworkInterceptor(MyInterceptor())  // Network interceptor
```

---

## Common Interceptor Examples

### Example 1: Add Authorization Header

```kotlin
class AuthInterceptor(private val tokenProvider: () -> String) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()

        // Add Authorization header
        val requestWithAuth = originalRequest.newBuilder()
            .addHeader("Authorization", "Bearer ${tokenProvider()}")
            .build()

        return chain.proceed(requestWithAuth)
    }
}

// Usage
val okHttpClient = OkHttpClient.Builder()
    .addInterceptor(AuthInterceptor { getAuthToken() })
    .build()

val retrofit = Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .client(okHttpClient)
    .addConverterFactory(GsonConverterFactory.create())
    .build()
```

**All requests now include:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

### Example 2: Add Common Query Parameters

```kotlin
class QueryParameterInterceptor : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()
        val originalUrl = originalRequest.url

        // Add query parameters to URL
        val urlWithParams = originalUrl.newBuilder()
            .addQueryParameter("api_version", "v1")
            .addQueryParameter("platform", "android")
            .addQueryParameter("app_version", BuildConfig.VERSION_NAME)
            .build()

        val requestWithParams = originalRequest.newBuilder()
            .url(urlWithParams)
            .build()

        return chain.proceed(requestWithParams)
    }
}

// Usage
val okHttpClient = OkHttpClient.Builder()
    .addInterceptor(QueryParameterInterceptor())
    .build()
```

**All requests now include:**
```
?api_version=v1&platform=android&app_version=1.2.3
```

---

### Example 3: Logging Interceptor

```kotlin
// Using OkHttp's built-in logging interceptor
val loggingInterceptor = HttpLoggingInterceptor().apply {
    level = HttpLoggingInterceptor.Level.BODY  // Log request and response body
}

val okHttpClient = OkHttpClient.Builder()
    .addInterceptor(loggingInterceptor)
    .build()

// Or create custom logging
class CustomLoggingInterceptor : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()

        // Log request
        Log.d("HTTP", "→ ${request.method} ${request.url}")
        Log.d("HTTP", "Headers: ${request.headers}")

        val startTime = System.currentTimeMillis()
        val response = chain.proceed(request)
        val duration = System.currentTimeMillis() - startTime

        // Log response
        Log.d("HTTP", "← ${response.code} (${duration}ms)")
        Log.d("HTTP", "Headers: ${response.headers}")

        return response
    }
}
```

**Log output:**
```
→ GET https://api.example.com/users/123
Headers: Authorization: Bearer token...
← 200 (234ms)
Headers: Content-Type: application/json
```

---

### Example 4: Refresh Token Interceptor

```kotlin
class TokenRefreshInterceptor(
    private val tokenManager: TokenManager
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()

        // Add current token
        val requestWithToken = originalRequest.newBuilder()
            .addHeader("Authorization", "Bearer ${tokenManager.getAccessToken()}")
            .build()

        val response = chain.proceed(requestWithToken)

        // If 401 Unauthorized, refresh token and retry
        if (response.code == 401) {
            response.close()

            synchronized(this) {
                // Refresh token
                val newToken = tokenManager.refreshToken()

                // Retry with new token
                val retryRequest = originalRequest.newBuilder()
                    .addHeader("Authorization", "Bearer $newToken")
                    .build()

                return chain.proceed(retryRequest)
            }
        }

        return response
    }
}

// Token Manager
class TokenManager {
    private var accessToken: String? = null
    private var refreshToken: String? = null

    fun getAccessToken(): String = accessToken ?: ""

    fun refreshToken(): String {
        // Call refresh token endpoint
        // Update accessToken
        // Return new token
        return "new_access_token"
    }
}
```

---

### Example 5: Modify Base URL Dynamically

```kotlin
class DynamicBaseUrlInterceptor(
    private val hostSelector: () -> String
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()
        val originalUrl = originalRequest.url

        // Replace host
        val newUrl = originalUrl.newBuilder()
            .host(hostSelector())
            .build()

        val newRequest = originalRequest.newBuilder()
            .url(newUrl)
            .build()

        return chain.proceed(newRequest)
    }
}

// Usage
val okHttpClient = OkHttpClient.Builder()
    .addInterceptor(DynamicBaseUrlInterceptor {
        if (isDebugMode) "api-dev.example.com" else "api.example.com"
    })
    .build()
```

---

### Example 6: Add Multiple Headers

```kotlin
class HeaderInterceptor : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()

        val requestWithHeaders = originalRequest.newBuilder()
            .addHeader("Content-Type", "application/json")
            .addHeader("Accept", "application/json")
            .addHeader("Accept-Language", Locale.getDefault().language)
            .addHeader("User-Agent", "MyApp/${BuildConfig.VERSION_NAME}")
            .addHeader("X-Device-ID", getDeviceId())
            .addHeader("X-Platform", "Android")
            .addHeader("X-OS-Version", Build.VERSION.RELEASE)
            .build()

        return chain.proceed(requestWithHeaders)
    }

    private fun getDeviceId(): String {
        // Return unique device identifier
        return "device_12345"
    }
}
```

---

## Complete Example: Production Setup

```kotlin
object NetworkModule {

    private const val BASE_URL = "https://api.example.com/"
    private const val TIMEOUT_SECONDS = 30L

    fun provideRetrofit(
        context: Context,
        tokenManager: TokenManager
    ): Retrofit {
        val okHttpClient = OkHttpClient.Builder()
            .connectTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .readTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .writeTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
            // Add interceptors in order
            .addInterceptor(HeaderInterceptor(context))
            .addInterceptor(AuthInterceptor(tokenManager))
            .addInterceptor(QueryParameterInterceptor())
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = if (BuildConfig.DEBUG) {
                    HttpLoggingInterceptor.Level.BODY
                } else {
                    HttpLoggingInterceptor.Level.NONE
                }
            })
            .addInterceptor(TokenRefreshInterceptor(tokenManager))
            .build()

        return Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }
}

// Header Interceptor
class HeaderInterceptor(private val context: Context) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request().newBuilder()
            .addHeader("Content-Type", "application/json")
            .addHeader("Accept", "application/json")
            .addHeader("Accept-Language", Locale.getDefault().language)
            .addHeader("User-Agent", getUserAgent())
            .addHeader("X-Device-ID", getDeviceId(context))
            .addHeader("X-Platform", "Android")
            .addHeader("X-OS-Version", Build.VERSION.RELEASE)
            .build()

        return chain.proceed(request)
    }

    private fun getUserAgent(): String {
        return "MyApp/${BuildConfig.VERSION_NAME} (Android ${Build.VERSION.RELEASE})"
    }

    private fun getDeviceId(context: Context): String {
        return Settings.Secure.getString(
            context.contentResolver,
            Settings.Secure.ANDROID_ID
        )
    }
}

// Auth Interceptor
class AuthInterceptor(private val tokenManager: TokenManager) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val token = tokenManager.getAccessToken()

        val request = if (token.isNotEmpty()) {
            chain.request().newBuilder()
                .addHeader("Authorization", "Bearer $token")
                .build()
        } else {
            chain.request()
        }

        return chain.proceed(request)
    }
}

// Query Parameter Interceptor
class QueryParameterInterceptor : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()
        val url = originalRequest.url.newBuilder()
            .addQueryParameter("api_version", "v1")
            .addQueryParameter("platform", "android")
            .build()

        val request = originalRequest.newBuilder()
            .url(url)
            .build()

        return chain.proceed(request)
    }
}

// Token Refresh Interceptor
class TokenRefreshInterceptor(
    private val tokenManager: TokenManager
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        val response = chain.proceed(request)

        if (response.code == 401) {
            response.close()

            synchronized(this) {
                val currentToken = tokenManager.getAccessToken()
                val newToken = tokenManager.refreshToken()

                if (newToken != currentToken) {
                    val newRequest = request.newBuilder()
                        .header("Authorization", "Bearer $newToken")
                        .build()

                    return chain.proceed(newRequest)
                }
            }
        }

        return response
    }
}
```

---

## Interceptor Order Matters

Interceptors are executed in the **order they're added**:

```kotlin
val okHttpClient = OkHttpClient.Builder()
    .addInterceptor(interceptor1)  // Runs first
    .addInterceptor(interceptor2)  // Runs second
    .addInterceptor(interceptor3)  // Runs third
    .build()
```

**Request flow:**
```
Request → Interceptor1 → Interceptor2 → Interceptor3 → Network → Server
```

**Response flow:**
```
Response ← Interceptor1 ← Interceptor2 ← Interceptor3 ← Network ← Server
```

**Best practice order:**
1. Headers (common headers)
2. Authentication (token)
3. Query parameters
4. Logging
5. Token refresh (last)

---

## Advanced: Conditional Interceptors

### Skip Interceptor for Specific Requests

```kotlin
class ConditionalAuthInterceptor(
    private val tokenManager: TokenManager
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()

        // Check if request needs authentication
        val needsAuth = request.header("No-Auth") == null

        return if (needsAuth) {
            val authenticatedRequest = request.newBuilder()
                .addHeader("Authorization", "Bearer ${tokenManager.getAccessToken()}")
                .build()
            chain.proceed(authenticatedRequest)
        } else {
            // Remove No-Auth header and proceed
            val cleanRequest = request.newBuilder()
                .removeHeader("No-Auth")
                .build()
            chain.proceed(cleanRequest)
        }
    }
}

// API usage
interface ApiService {
    // Requires authentication
    @GET("user/profile")
    suspend fun getProfile(): Response<User>

    // No authentication needed
    @Headers("No-Auth: true")
    @POST("auth/login")
    suspend fun login(@Body credentials: Credentials): Response<AuthResponse>
}
```

---

### Different Interceptors for Different Endpoints

```kotlin
class SmartInterceptor(
    private val tokenManager: TokenManager
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        val path = request.url.encodedPath

        val modifiedRequest = when {
            path.startsWith("/api/v1/") -> {
                // V1 API: use API key
                request.newBuilder()
                    .addHeader("X-API-Key", "api_key_v1")
                    .build()
            }
            path.startsWith("/api/v2/") -> {
                // V2 API: use Bearer token
                request.newBuilder()
                    .addHeader("Authorization", "Bearer ${tokenManager.getAccessToken()}")
                    .build()
            }
            else -> request
        }

        return chain.proceed(modifiedRequest)
    }
}
```

---

## Testing with Interceptors

### Mock Interceptor for Testing

```kotlin
class MockInterceptor : Interceptor {

    private val mockResponses = mutableMapOf<String, String>()

    fun addMockResponse(url: String, jsonResponse: String) {
        mockResponses[url] = jsonResponse
    }

    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        val url = request.url.toString()

        val mockResponse = mockResponses[url]

        return if (mockResponse != null) {
            // Return mock response
            Response.Builder()
                .request(request)
                .protocol(Protocol.HTTP_1_1)
                .code(200)
                .message("OK")
                .body(mockResponse.toResponseBody("application/json".toMediaTypeOrNull()))
                .build()
        } else {
            // Proceed with real request
            chain.proceed(request)
        }
    }
}

// Usage in tests
val mockInterceptor = MockInterceptor()
mockInterceptor.addMockResponse(
    "https://api.example.com/users/123",
    """{"id":"123","name":"John"}"""
)

val okHttpClient = OkHttpClient.Builder()
    .addInterceptor(mockInterceptor)
    .build()
```

---

## Summary

**How to modify all requests in Retrofit:**

Use **OkHttp Interceptors** to modify requests globally.

**Common use cases:**

1. **Add headers** (authorization, API keys)
   ```kotlin
   .addHeader("Authorization", "Bearer $token")
   ```

2. **Add query parameters** (API version, platform)
   ```kotlin
   .addQueryParameter("api_version", "v1")
   ```

3. **Logging** (request/response details)
   ```kotlin
   HttpLoggingInterceptor()
   ```

4. **Refresh token** (automatic re-authentication)
   ```kotlin
   if (response.code == 401) { refreshToken() }
   ```

5. **Modify base URL** dynamically
   ```kotlin
   .host(newHost)
   ```

**Setup:**
```kotlin
val okHttpClient = OkHttpClient.Builder()
    .addInterceptor(HeaderInterceptor())
    .addInterceptor(AuthInterceptor(tokenManager))
    .addInterceptor(loggingInterceptor)
    .build()

val retrofit = Retrofit.Builder()
    .client(okHttpClient)
    .build()
```

**Interceptor order matters:**
- Headers → Auth → Query params → Logging → Token refresh

**Types:**
- **Application Interceptor** - runs first, modify before network
- **Network Interceptor** - runs close to network, see actual request

**Best practices:**
- Add interceptors in logical order
- Use conditional logic for specific endpoints
- Log only in debug builds
- Handle token refresh gracefully
- Test with mock interceptors

---

## Ответ (RU)
В Retrofit можно изменять все запросы глобально с помощью **Interceptor (перехватчика)** в OkHttp.

**Основные примеры:**

1. **Добавление заголовков** (авторизация, API ключи)
2. **Добавление query параметров** (версия API, платформа)
3. **Логирование** всех запросов
4. **Автоматическое обновление токена** (refresh token)
5. **Динамическое изменение baseUrl**

**Пример:**
```kotlin
class AuthInterceptor(private val tokenProvider: () -> String) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request().newBuilder()
            .addHeader("Authorization", "Bearer ${tokenProvider()}")
            .build()
        return chain.proceed(request)
    }
}

val okHttpClient = OkHttpClient.Builder()
    .addInterceptor(AuthInterceptor { getToken() })
    .build()

val retrofit = Retrofit.Builder()
    .client(okHttpClient)
    .build()
```

**Порядок важен:** перехватчики выполняются в порядке добавления.


---

## Related Questions

### Prerequisites (Easier)
- [[q-http-protocols-comparison--android--medium]] - Networking
- [[q-retrofit-call-adapter-advanced--networking--medium]] - Networking
- [[q-retrofit-usage-tutorial--android--medium]] - Networking

### Related (Hard)
- [[q-data-sync-unstable-network--android--hard]] - Networking
