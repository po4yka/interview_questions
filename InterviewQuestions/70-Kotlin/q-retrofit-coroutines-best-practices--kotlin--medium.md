---
anki_cards:
- slug: q-retrofit-coroutines-best-practices--kotlin--medium-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-retrofit-coroutines-best-practices--kotlin--medium-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
---\
id: kotlin-184
title: "Retrofit with coroutines: best practices / Retrofit с корутинами: лучшие практики"
aliases: [Coroutines Retrofit, Networking, REST API, Retrofit, Retrofit с корутинами]
topic: kotlin
subtopics: [coroutines, networking]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-coroutines, q-flow-basics--kotlin--easy]
created: 2025-10-15
updated: 2025-11-11
tags: [android, best-practices, coroutines, difficulty/medium, error-handling, kotlin, networking, okhttp, rest-api, retrofit]

---\
# Вопрос (RU)

> Лучшие практики использования `Retrofit` с корутинами в Kotlin для реальных Android-приложений.

# Question (EN)

> Best practices for using `Retrofit` with coroutines in Kotlin for real-world Android apps.

## Ответ (RU)

Ниже приведено детальное двуязычное руководство. Русская секция эквивалентна английской по структуре и коду; все ключевые примеры и практики представлены.

## Answer (EN)

Detailed best-practices guide follows below. English and Russian sections are structurally equivalent with identical code where provided.

---

# Retrofit with Coroutines: Best Practices

**English** | [Русский](#retrofit-с-корутинами-лучшие-практики)

---

## Table of Contents

- [Overview](#overview)
- [Suspend Functions in Retrofit](#suspend-functions-in-retrofit)
- [Response Types: `Response<T>` vs `T`](#response-types-responset-vs-t)
- [Error Handling Strategies](#error-handling-strategies)
- [Timeout Configuration](#timeout-configuration)
- [Cancellation Handling](#cancellation-handling)
- [Concurrent Requests](#concurrent-requests)
- [Sequential vs Parallel Patterns](#sequential-vs-parallel-patterns)
- [Call `Adapter` vs Suspend Functions](#call-adapter-vs-suspend-functions)
- [`Flow` Return Types](#flow-return-types)
- [Complete Repository Implementation](#complete-repository-implementation)
- [Caching with `Room` + `Flow`](#caching-with-room--flow)
- [Retry Logic with Exponential Backoff](#retry-logic-with-exponential-backoff)
- [Testing](#testing)
- [OkHttp Interceptors](#okhttp-interceptors)
- [Best Practices Checklist](#best-practices-checklist)
- [Complete Android App Example](#complete-android-app-example)
- [Common Pitfalls](#common-pitfalls)
- [Follow-ups](#follow-ups)
- [References](#references)
- [Related Questions](#related-questions)

---

## Overview

`Retrofit` with Kotlin Coroutines provides a modern, efficient way to handle network operations in Android applications. This guide covers best practices for integrating `Retrofit` with coroutines. See also [[c-coroutines]].

**Key Benefits:**
- Natural async/await syntax with suspend functions
- Automatic request cancellation when coroutine is cancelled
- Seamless integration with `Flow` for reactive streams
- Better error handling with try-catch
- No callback hell

---

## Suspend Functions in Retrofit

### Modern Retrofit Interface

```kotlin
interface ApiService {
    //  Modern approach: suspend function
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: String): User

    //  With Response wrapper for headers/status
    @GET("users/{id}")
    suspend fun getUserWithResponse(@Path("id") userId: String): Response<User>

    //  Old approach: `Call<T>` (not needed with coroutines in new code)
    @GET("users/{id}")
    fun getUserOld(@Path("id") userId: String): Call<User>

    //  Multiple suspend operations
    @POST("users")
    suspend fun createUser(@Body user: UserRequest): User

    @PUT("users/{id}")
    suspend fun updateUser(@Path("id") id: String, @Body user: UserRequest): User

    @DELETE("users/{id}")
    suspend fun deleteUser(@Path("id") id: String)

    //  Query parameters
    @GET("users")
    suspend fun getUsers(
        @Query("page") page: Int,
        @Query("limit") limit: Int
    ): List<User>

    //  Headers
    @GET("profile")
    suspend fun getProfile(@Header("Authorization") token: String): Profile

    @GET("users/{id}/posts")
    suspend fun getUserPosts(@Path("id") userId: String): List<Post>

    @GET("notifications")
    suspend fun getNotifications(): List<Notification>

    @GET("feed")
    suspend fun getFeedPosts(): List<Post>

    @GET("suggestions")
    suspend fun getSuggestions(): List<User>

    @GET("orders/{id}")
    suspend fun getOrder(@Path("id") orderId: String): Order

    @GET("products/{id}")
    suspend fun getProduct(@Path("id") productId: String): Product

    @POST("orders/{id}/payment")
    suspend fun processPayment(
        @Path("id") orderId: String,
        @Query("amount") amount: Long,
        @Query("userId") userId: String
    ): Payment

    @POST("profiles/{id}")
    suspend fun createProfile(@Path("id") userId: String, @Body profile: ProfileRequest): Profile

    @POST("profiles/{id}/avatar")
    suspend fun uploadAvatar(@Path("id") profileId: String, @Body avatar: ByteArray): String

    @GET("products")
    suspend fun getAllProducts(): List<Product>

    @POST("upload")
    suspend fun uploadFile(@Body file: File): UploadResult

    @GET("search/users")
    suspend fun searchUsers(@Query("q") query: String): List<User>
}
```

### Retrofit Setup for Coroutines

```kotlin
object RetrofitClient {
    private const val BASE_URL = "https://api.example.com/"

    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        })
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()

    val retrofit: Retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        // No custom coroutine CallAdapter needed with suspend functions (Retrofit 2.6+)
        .build()

    val apiService: ApiService = retrofit.create(ApiService::class.java)
}
```

---

## Response Types: `Response<T>` Vs `T`

### When to Use Direct `T`

Use direct type `T` when you only care about the success case and can treat non-2xx as exceptions:

```kotlin
interface ApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: String): User
}

// Usage
suspend fun loadUser(userId: String): ApiResult<User> {
    return try {
        val user = apiService.getUser(userId)
        ApiResult.Success(user)
    } catch (e: CancellationException) {
        throw e
    } catch (e: Exception) {
        ApiResult.Error(e)
    }
}
```

**Pros:**
- Cleaner API
- Less boilerplate
- `Retrofit` throws on non-2xx / network failures, handled in one place

**Cons:**
- No access to headers
- No access to status code
- Errors are exposed via exceptions

### When to Use `Response<T>`

Use `Response<T>` when you need headers, status codes, or custom error handling:

```kotlin
interface ApiService {
    @GET("users/{id}")
    suspend fun getUserWithResponse(@Path("id") userId: String): Response<User>
}

// Usage
suspend fun loadUserWithDetails(userId: String): UserResult {
    val response = apiService.getUserWithResponse(userId)

    return when {
        response.isSuccessful -> {
            val user = response.body()
                ?: return UserResult.Error(response.code(), "Empty response body")
            val etag = response.headers()["ETag"]
            UserResult.Success(user, etag)
        }
        response.code() == 404 -> {
            UserResult.NotFound
        }
        response.code() == 429 -> {
            val retryAfter = response.headers()["Retry-After"]?.toIntOrNull()
            UserResult.RateLimited(retryAfter)
        }
        else -> {
            val errorBody = response.errorBody()?.use { it.string() }
            UserResult.Error(response.code(), errorBody)
        }
    }
}

sealed class UserResult {
    data class Success(val user: User, val etag: String?) : UserResult()
    object NotFound : UserResult()
    data class RateLimited(val retryAfterSeconds: Int?) : UserResult()
    data class Error(val code: Int, val message: String?) : UserResult()
}
```

**Pros:**
- Access to headers (ETag, Cache-Control, etc.)
- Access to status code
- Custom error handling per status
- No implicit exception on non-2xx

**Cons:**
- More boilerplate
- Manual success/error checking

---

## Error Handling Strategies

Note: In all strategies below, avoid swallowing `CancellationException`; always rethrow it.

### Strategy 1: Try-Catch (Simple)

```kotlin
class UserRepository(private val api: ApiService) {
    suspend fun getUser(userId: String): User? {
        return try {
            api.getUser(userId)
        } catch (e: CancellationException) {
            throw e
        } catch (e: IOException) {
            // Network error
            Log.e("UserRepository", "Network error", e)
            null
        } catch (e: HttpException) {
            // HTTP error (4xx, 5xx)
            Log.e("UserRepository", "HTTP error: ${e.code()}", e)
            null
        } catch (e: Exception) {
            // Other errors
            Log.e("UserRepository", "Unknown error", e)
            null
        }
    }
}
```

### Strategy 2: `ApiResult<T>` Sealed Class

```kotlin
sealed class ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>()
    data class Error(val exception: Throwable) : ApiResult<Nothing>()
    object Loading : ApiResult<Nothing>()
}

class UserRepository(private val api: ApiService) {
    suspend fun getUser(userId: String): ApiResult<User> {
        return try {
            val user = api.getUser(userId)
            ApiResult.Success(user)
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            ApiResult.Error(e)
        }
    }
}

// Usage in `ViewModel`
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    private val _userState = MutableStateFlow<ApiResult<User>>(ApiResult.Loading)
    val userState: StateFlow<ApiResult<User>> = _userState.asStateFlow()

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _userState.value = ApiResult.Loading
            _userState.value = repository.getUser(userId)
        }
    }
}
```

### Strategy 3: `NetworkResponse<T, E>` (Advanced)

```kotlin
sealed class NetworkResponse<out T, out E> {
    data class Success<T>(val data: T) : NetworkResponse<T, Nothing>()
    data class ApiError<E>(val body: E, val code: Int) : NetworkResponse<Nothing, E>()
    data class NetworkError(val error: IOException) : NetworkResponse<Nothing, Nothing>()
    data class UnknownError(val error: Throwable) : NetworkResponse<Nothing, Nothing>()
}

data class ApiErrorResponse(
    val message: String,
    val code: String?,
    val details: Map<String, String>?
)

suspend fun <T, E> safeApiCall(
    errorClass: Class<E>,
    apiCall: suspend () -> Response<T>
): NetworkResponse<T, E> {
    return try {
        val response = apiCall()
        if (response.isSuccessful) {
            val body = response.body()
            if (body != null) {
                NetworkResponse.Success(body)
            } else {
                NetworkResponse.UnknownError(NullPointerException("Response body is null"))
            }
        } else {
            val errorBody = response.errorBody()?.use { it.string() }
            val errorResponse = try {
                if (errorBody != null) Gson().fromJson(errorBody, errorClass) else null
            } catch (e: Exception) {
                null
            }
            if (errorResponse != null) {
                NetworkResponse.ApiError(errorResponse, response.code())
            } else {
                NetworkResponse.UnknownError(Exception("Unknown API error"))
            }
        }
    } catch (e: CancellationException) {
        throw e
    } catch (e: IOException) {
        NetworkResponse.NetworkError(e)
    } catch (e: Exception) {
        NetworkResponse.UnknownError(e)
    }
}

// Usage
class NetworkUserRepository(private val api: ApiService) {
    suspend fun getUser(userId: String): NetworkResponse<User, ApiErrorResponse> {
        return safeApiCall(ApiErrorResponse::class.java) {
            api.getUserWithResponse(userId)
        }
    }
}
```

---

## Timeout Configuration

### OkHttp Level Timeouts

```kotlin
val okHttpClient = OkHttpClient.Builder()
    // Connection timeout: time to establish connection
    .connectTimeout(30, TimeUnit.SECONDS)

    // Read timeout: max time without data from server after connection established
    .readTimeout(30, TimeUnit.SECONDS)

    // Write timeout: max time between bytes sent to server
    .writeTimeout(30, TimeUnit.SECONDS)

    // Call timeout: entire call duration (connection + write + read)
    .callTimeout(60, TimeUnit.SECONDS)
    .build()
```

### Per-Request Timeout with Coroutines

```kotlin
suspend fun getUserWithTimeout(userId: String): User? {
    return try {
        withTimeout(5000) { // 5 seconds
            apiService.getUser(userId)
        }
    } catch (e: TimeoutCancellationException) {
        Log.e("API", "Request timed out")
        null
    } catch (e: CancellationException) {
        throw e
    } catch (e: Exception) {
        Log.e("API", "Error", e)
        null
    }
}

suspend fun getUserWithTimeoutOrNull(userId: String): User? {
    return try {
        withTimeoutOrNull(5000) {
            apiService.getUser(userId)
        }
    } catch (e: CancellationException) {
        throw e
    }
}
```

### Custom Timeout Interceptor

```kotlin
class TimeoutInterceptor(
    private val connectTimeout: Long = 30,
    private val readTimeout: Long = 30,
    private val writeTimeout: Long = 30
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): okhttp3.Response {
        val request = chain.request()

        val customTimeout = request.header("X-Timeout")?.toLongOrNull()

        return if (customTimeout != null) {
            chain
                .withConnectTimeout(customTimeout.toInt(), TimeUnit.SECONDS)
                .withReadTimeout(customTimeout.toInt(), TimeUnit.SECONDS)
                .withWriteTimeout(customTimeout.toInt(), TimeUnit.SECONDS)
                .proceed(request)
        } else {
            chain.proceed(request)
        }
    }
}

// Usage with custom timeout header
interface TimeoutApiService {
    @Headers("X-Timeout: 60")
    @GET("large-data")
    suspend fun getLargeData(): LargeDataResponse
}
```

---

## Cancellation Handling

### Automatic Cancellation

When a coroutine is cancelled, `Retrofit` (2.6+) automatically cancels the underlying `OkHttp` call.

```kotlin
class CancellableUserViewModel(private val repository: UserRepository) : ViewModel() {
    private val _userState = MutableStateFlow<UserState>(UserState.Loading)
    val userState: StateFlow<UserState> = _userState.asStateFlow()

    private var loadJob: Job? = null

    fun loadUser(userId: String) {
        // Cancel previous request
        loadJob?.cancel()

        loadJob = viewModelScope.launch {
            try {
                val result = repository.getUser(userId)
                _userState.value = when (result) {
                    is ApiResult.Success -> UserState.Success(result.data)
                    is ApiResult.Error -> UserState.Error(result.exception.message ?: "Unknown error")
                    ApiResult.Loading -> UserState.Loading
                }
            } catch (e: CancellationException) {
                // Propagate cancellation
                throw e
            }
        }
    }
}
```

### Manual Cancellation with Job Tracking (Illustrative)

```kotlin
class CancellableRepository(private val api: ApiService) {
    // This simple map assumes single-threaded access within a given scope.
    private val activeRequests = mutableMapOf<String, Deferred<User>>()

    suspend fun getUser(userId: String): User = coroutineScope {
        // Cancel existing request for this user if needed
        activeRequests[userId]?.cancel()

        val deferred = async {
            try {
                api.getUser(userId)
            } finally {
                activeRequests.remove(userId)
            }
        }

        activeRequests[userId] = deferred
        deferred.await()
    }

    fun cancelAllRequests() {
        activeRequests.values.forEach { it.cancel() }
        activeRequests.clear()
    }
}
```

### Cancellation-Safe Cleanup

```kotlin
suspend fun downloadFile(url: String, outputFile: File) {
    var outputStream: FileOutputStream? = null

    try {
        withContext(Dispatchers.IO) {
            val response = apiService.downloadFile(url)
            val inputStream = response.body()?.byteStream()
                ?: throw IOException("Empty response body")

            outputStream = FileOutputStream(outputFile)

            inputStream.use { input ->
                outputStream!!.use { output ->
                    input.copyTo(output)
                }
            }
        }
    } catch (e: CancellationException) {
        // Clean up on cancellation
        outputStream?.close()
        outputFile.delete()
        throw e
    }
}
```

---

## Concurrent Requests

### Parallel Requests with async/await

```kotlin
class ConcurrentUserRepository(private val api: ApiService) {
    suspend fun getUserWithPosts(userId: String): Pair<User, List<Post>> = coroutineScope {
        val userDeferred = async { api.getUser(userId) }
        val postsDeferred = async { api.getUserPosts(userId) }

        val user = userDeferred.await()
        val posts = postsDeferred.await()

        user to posts
    }

    suspend fun getDashboardData(): DashboardData = coroutineScope {
        val userDeferred = async { api.getUser("me") }
        val notificationsDeferred = async { api.getNotifications() }
        val postsDeferred = async { api.getFeedPosts() }
        val suggestionsDeferred = async { api.getSuggestions() }

        DashboardData(
            user = userDeferred.await(),
            notifications = notificationsDeferred.await(),
            posts = postsDeferred.await(),
            suggestions = suggestionsDeferred.await()
        )
    }
}

data class DashboardData(
    val user: User,
    val notifications: List<Notification>,
    val posts: List<Post>,
    val suggestions: List<User>
)
```

### Handling Partial Failures (Illustrative)

```kotlin
suspend fun getDashboardDataSafe(api: ApiService): DashboardData = coroutineScope {
    val userDeferred = async {
        try {
            api.getUser("me")
        } catch (e: Exception) {
            null
        }
    }
    val notificationsDeferred = async {
        try {
            api.getNotifications()
        } catch (e: Exception) {
            emptyList()
        }
    }
    val postsDeferred = async {
        try {
            api.getFeedPosts()
        } catch (e: Exception) {
            emptyList()
        }
    }

    DashboardData(
        user = userDeferred.await() ?: error("User is required"),
        notifications = notificationsDeferred.await(),
        posts = postsDeferred.await(),
        suggestions = emptyList()
    )
}

suspend fun getDashboardDataSupervisor(api: ApiService): DashboardData = supervisorScope {
    val userDeferred = async {
        try {
            api.getUser("me")
        } catch (e: Exception) {
            Log.e("Dashboard", "Failed to load user", e)
            null
        }
    }
    val notificationsDeferred = async {
        try {
            api.getNotifications()
        } catch (e: Exception) {
            Log.e("Dashboard", "Failed to load notifications", e)
            emptyList()
        }
    }

    DashboardData(
        user = userDeferred.await() ?: error("User is required"),
        notifications = notificationsDeferred.await(),
        posts = emptyList(),
        suggestions = emptyList()
    )
}
```

---

## Sequential Vs Parallel Patterns

### Sequential Execution

Use when requests depend on each other:

```kotlin
suspend fun createUserWithProfile(
    apiService: ApiService,
    userRequest: UserRequest,
    profileRequest: ProfileRequest
): Profile {
    val user = apiService.createUser(userRequest)
    val profile = apiService.createProfile(user.id, profileRequest)
    val avatarUrl = apiService.uploadAvatar(profile.id, profileRequest.avatar)
    return profile.copy(avatarUrl = avatarUrl)
}
```

### Parallel Execution

Use when requests are independent:

```kotlin
suspend fun loadMultipleUsers(apiService: ApiService, userIds: List<String>): List<User> = coroutineScope {
    userIds.map { userId ->
        async { apiService.getUser(userId) }
    }.awaitAll()
}

suspend fun loadMultipleUsersSafe(apiService: ApiService, userIds: List<String>): List<User> = coroutineScope {
    userIds.map { userId ->
        async {
            try {
                apiService.getUser(userId)
            } catch (e: Exception) {
                Log.e("UserLoad", "Failed to load user $userId", e)
                null
            }
        }
    }.awaitAll().filterNotNull()
}
```

### Mixed Pattern (Sequential + Parallel)

```kotlin
suspend fun processOrder(apiService: ApiService, orderId: String): OrderResult = coroutineScope {
    val order = apiService.getOrder(orderId)

    val userDeferred = async { apiService.getUser(order.userId) }
    val productsDeferred = async {
        order.productIds.map { productId ->
            async { apiService.getProduct(productId) }
        }.awaitAll()
    }
    val shippingDeferred = async { apiService.getShippingInfo(order.shippingId) }

    val user = userDeferred.await()
    val products = productsDeferred.await()
    val shipping = shippingDeferred.await()

    val payment = apiService.processPayment(
        orderId = orderId,
        amount = products.sumOf { it.price },
        userId = user.id
    )

    OrderResult(order, user, products, shipping, payment)
}
```

---

## Call Adapter Vs Suspend Functions

### Old Approach: Call Adapter

```kotlin
// Old way (typically for RxJava / legacy)
class RxJava2CallAdapterFactory

val retrofit = Retrofit.Builder()
    .baseUrl(BASE_URL)
    .addCallAdapterFactory(RxJava2CallAdapterFactory())
    .addConverterFactory(GsonConverterFactory.create())
    .build()

interface RxApiService {
    @GET("users/{id}")
    fun getUser(@Path("id") userId: String): Single<User>
}
```

### Modern Approach: Suspend Functions

```kotlin
val retrofit = Retrofit.Builder()
    .baseUrl(BASE_URL)
    .addConverterFactory(GsonConverterFactory.create())
    .build()

interface CoroutineApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: String): User
}
```

Why suspend functions are generally preferred:
- Built-in support (`Retrofit` 2.6+)
- No extra dependency
- Natural Kotlin syntax
- Automatic cancellation support
- Simple testing

---

## Flow Return Types

### Basic `Flow`

```kotlin
interface ApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: String): User
}

class UserRepository(private val api: ApiService) {
    fun observeUser(userId: String, intervalMs: Long = 5000): Flow<User> = flow {
        while (currentCoroutineContext().isActive) {
            val user = api.getUser(userId)
            emit(user)
            delay(intervalMs)
        }
    }.flowOn(Dispatchers.IO)
}
```

### Server-Sent Events (SSE) with `Flow`

```kotlin
interface NotificationApiService {
    @GET("notifications/stream")
    @Streaming
    suspend fun getNotificationStream(): ResponseBody
}

class NotificationRepository(private val api: NotificationApiService) {
    fun observeNotifications(): Flow<Notification> = callbackFlow {
        val response = api.getNotificationStream()
        val reader = response.byteStream().bufferedReader()

        try {
            while (isActive) {
                val line = reader.readLine() ?: break
                if (line.startsWith("data: ")) {
                    val json = line.substring(6)
                    val notification = Gson().fromJson(json, Notification::class.java)
                    trySend(notification)
                }
            }
        } catch (e: Exception) {
            close(e)
        }

        awaitClose {
            try {
                reader.close()
            } catch (_: Exception) {}
            try {
                response.close()
            } catch (_: Exception) {}
        }
    }.flowOn(Dispatchers.IO)
}
```

### WebSocket with `Flow`

```kotlin
class ChatRepository(private val okHttpClient: OkHttpClient) {
    fun observeMessages(roomId: String): Flow<ChatMessage> = callbackFlow {
        val request = Request.Builder()
            .url("wss://api.example.com/chat/$roomId")
            .build()

        val listener = object : WebSocketListener() {
            override fun onMessage(webSocket: WebSocket, text: String) {
                val message = Gson().fromJson(text, ChatMessage::class.java)
                trySend(message)
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: okhttp3.Response?) {
                close(t)
            }
        }

        val webSocket = okHttpClient.newWebSocket(request, listener)

        awaitClose {
            webSocket.close(1000, "Client closed")
        }
    }.flowOn(Dispatchers.IO)

    suspend fun sendMessage(webSocket: WebSocket, message: String) {
        webSocket.send(message)
    }
}
```

---

## Complete Repository Implementation

```kotlin
class UserRepository(
    private val api: ApiService,
    private val userDao: UserDao,
    private val dispatcher: CoroutineDispatcher = Dispatchers.IO
) {
    private val _currentUser = MutableStateFlow<ApiResult<User>>(ApiResult.Loading)
    val currentUser: StateFlow<ApiResult<User>> = _currentUser.asStateFlow()

    fun observeUser(userId: String): Flow<User?> {
        return userDao.observeUser(userId)
    }

    suspend fun getUser(
        userId: String,
        forceRefresh: Boolean = false
    ): ApiResult<User> = withContext(dispatcher) {
        try {
            if (!forceRefresh) {
                val cachedUser = userDao.getUser(userId)
                if (cachedUser != null && !cachedUser.isExpired()) {
                    return@withContext ApiResult.Success(cachedUser)
                }
            }

            val user = api.getUser(userId)
            userDao.insertUser(user)
            ApiResult.Success(user)
        } catch (e: CancellationException) {
            throw e
        } catch (e: IOException) {
            val cachedUser = userDao.getUser(userId)
            if (cachedUser != null) {
                ApiResult.Success(cachedUser)
            } else {
                ApiResult.Error(e)
            }
        } catch (e: Exception) {
            ApiResult.Error(e)
        }
    }

    suspend fun updateUser(userId: String, updates: UserUpdate): ApiResult<User> = withContext(dispatcher) {
        try {
            val user = api.updateUser(userId, updates)
            userDao.insertUser(user)
            _currentUser.value = ApiResult.Success(user)
            ApiResult.Success(user)
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            ApiResult.Error(e)
        }
    }

    suspend fun deleteUser(userId: String): ApiResult<Unit> = withContext(dispatcher) {
        try {
            api.deleteUser(userId)
            userDao.deleteUser(userId)
            ApiResult.Success(Unit)
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            ApiResult.Error(e)
        }
    }

    suspend fun searchUsers(query: String): ApiResult<List<User>> = withContext(dispatcher) {
        try {
            val users = api.searchUsers(query)
            ApiResult.Success(users)
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            ApiResult.Error(e)
        }
    }

    suspend fun getUsersPaginated(page: Int, limit: Int): ApiResult<List<User>> = withContext(dispatcher) {
        try {
            val users = api.getUsers(page, limit)
            ApiResult.Success(users)
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            ApiResult.Error(e)
        }
    }
}

@Entity(tableName = "users")
data class User(
    @PrimaryKey val id: String,
    val name: String,
    val email: String,
    val avatarUrl: String?,
    val cachedAt: Long = System.currentTimeMillis()
) {
    fun isExpired(ttlMs: Long = 5 * 60 * 1000): Boolean {
        return System.currentTimeMillis() - cachedAt > ttlMs
    }
}

@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUser(userId: String): User?

    @Query("SELECT * FROM users WHERE id = :userId")
    fun observeUser(userId: String): Flow<User?>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: User)

    @Query("DELETE FROM users WHERE id = :userId")
    suspend fun deleteUser(userId: String)

    @Query("DELETE FROM users WHERE cachedAt < :expirationTime")
    suspend fun deleteExpiredUsers(expirationTime: Long)
}
```

---

## Caching with Room + `Flow`

### Cache-First Strategy

```kotlin
class ProductRepository(
    private val api: ApiService,
    private val productDao: ProductDao
) {
    fun observeProduct(productId: String): Flow<Product?> =
        productDao.observeProduct(productId)
            .onStart { emitInitial(productId) }

    private suspend fun emitInitial(productId: String) {
        try {
            val product = api.getProduct(productId)
            productDao.insertProduct(product)
        } catch (e: Exception) {
            Log.e("ProductRepository", "Failed to refresh product", e)
        }
    }

    suspend fun getProduct(
        productId: String,
        forceRefresh: Boolean = false
    ): Flow<ApiResult<Product>> = flow {
        emit(ApiResult.Loading)

        if (!forceRefresh) {
            val cached = productDao.getProduct(productId)
            if (cached != null) {
                emit(ApiResult.Success(cached))
            }
        }

        try {
            val product = api.getProduct(productId)
            productDao.insertProduct(product)
            emit(ApiResult.Success(product))
        } catch (e: Exception) {
            val cached = productDao.getProduct(productId)
            if (cached == null) {
                emit(ApiResult.Error(e))
            }
        }
    }
}
```

### Network-First Strategy

```kotlin
fun ProductRepository.getProductNetworkFirst(productId: String): Flow<ApiResult<Product>> = flow {
    emit(ApiResult.Loading)

    try {
        val product = api.getProduct(productId)
        productDao.insertProduct(product)
        emit(ApiResult.Success(product))
    } catch (e: Exception) {
        val cached = productDao.getProduct(productId)
        if (cached != null) {
            emit(ApiResult.Success(cached))
        } else {
            emit(ApiResult.Error(e))
        }
    }
}
```

### Reactive Cache Updates

```kotlin
class ReactiveProductRepository(
    private val api: ApiService,
    private val productDao: ProductDao,
    scope: CoroutineScope
) {
    init {
        scope.launch(Dispatchers.IO) {
            refreshAllProducts()
        }
    }

    fun observeProducts(): Flow<List<Product>> = productDao.observeAllProducts()
        .onStart { refreshAllProducts() }

    private suspend fun refreshAllProducts() {
        try {
            val products = api.getAllProducts()
            productDao.insertAllProducts(products)
        } catch (e: Exception) {
            Log.e("ProductRepository", "Failed to refresh products", e)
        }
    }
}

@Dao
interface ProductDao {
    @Query("SELECT * FROM products")
    fun observeAllProducts(): Flow<List<Product>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAllProducts(products: List<Product>)
}
```

---

## Retry Logic with Exponential Backoff

### Simple Retry

```kotlin
suspend fun <T> retryIO(
    times: Int = 3,
    initialDelay: Long = 100,
    maxDelay: Long = 1000,
    factor: Double = 2.0,
    block: suspend () -> T
): T {
    var currentDelay = initialDelay
    repeat(times - 1) { attempt ->
        try {
            return block()
        } catch (e: IOException) {
            Log.w("Retry", "Attempt ${attempt + 1} failed", e)
        }
        delay(currentDelay)
        currentDelay = (currentDelay * factor).toLong().coerceAtMost(maxDelay)
    }
    return block() // last attempt
}

suspend fun getUserWithRetry(userId: String): User {
    return retryIO(times = 3) {
        apiService.getUser(userId)
    }
}
```

### Advanced Retry with Custom Conditions

```kotlin
class RetryConfig(
    val maxAttempts: Int = 3,
    val initialDelay: Long = 100,
    val maxDelay: Long = 1000,
    val factor: Double = 2.0,
    val retryableExceptions: List<Class<out Exception>> = listOf(
        IOException::class.java,
        SocketTimeoutException::class.java
    )
)

suspend fun <T> retryWithPolicy(
    config: RetryConfig = RetryConfig(),
    block: suspend (attempt: Int) -> T
): T {
    var currentDelay = config.initialDelay
    var lastException: Exception? = null

    repeat(config.maxAttempts) { attempt ->
        try {
            return block(attempt)
        } catch (e: Exception) {
            lastException = e

            val isRetryable = config.retryableExceptions.any { it.isInstance(e) }
            if (!isRetryable || attempt == config.maxAttempts - 1) {
                throw e
            }

            Log.w(
                "Retry",
                "Attempt ${attempt + 1} failed, retrying in ${currentDelay}ms",
                e
            )
            delay(currentDelay)
            currentDelay = (currentDelay * config.factor)
                .toLong()
                .coerceAtMost(config.maxDelay)
        }
    }

    throw lastException ?: Exception("Retry failed")
}

suspend fun uploadFileWithRetry(file: File): UploadResult {
    return retryWithPolicy(
        config = RetryConfig(
            maxAttempts = 5,
            initialDelay = 1000,
            maxDelay = 10000,
            factor = 2.0
        )
    ) { attempt ->
        Log.d("Upload", "Upload attempt ${attempt + 1}")
        apiService.uploadFile(file)
    }
}
```

### Retry with `Flow`

```kotlin
fun <T> Flow<T>.retryWithBackoff(
    retries: Long = 3,
    initialDelay: Long = 100,
    maxDelay: Long = 1000,
    factor: Double = 2.0,
    predicate: (Throwable) -> Boolean = { true }
): Flow<T> = retryWhen { cause, attempt ->
    if (attempt < retries && predicate(cause)) {
        val delayMs = (initialDelay * factor.pow(attempt.toDouble()))
            .toLong()
            .coerceAtMost(maxDelay)
        delay(delayMs)
        true
    } else {
        false
    }
}

fun observeUserWithRetry(userId: String): Flow<User> = flow {
    emit(apiService.getUser(userId))
}.retryWithBackoff(
    retries = 3,
    predicate = { it is IOException }
)
```

---

## Testing

Note: Examples are illustrative; inject dispatchers and dependencies in real tests.

### MockWebServer Setup

```kotlin
class UserRepositoryTest {
    private lateinit var mockWebServer: MockWebServer
    private lateinit var apiService: ApiService
    private lateinit var repository: UserRepository

    @Before
    fun setup() {
        mockWebServer = MockWebServer()
        mockWebServer.start()

        val retrofit = Retrofit.Builder()
            .baseUrl(mockWebServer.url("/"))
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        apiService = retrofit.create(ApiService::class.java)
        repository = UserRepository(apiService, /* userDao = */ FakeUserDao())
    }

    @After
    fun teardown() {
        mockWebServer.shutdown()
    }

    @Test
    fun `getUser returns user on success`() = runTest {
        val mockResponse = """
            {
                "id": "123",
                "name": "John Doe",
                "email": "john@example.com"
            }
        """.trimIndent()

        mockWebServer.enqueue(
            MockResponse()
                .setResponseCode(200)
                .setBody(mockResponse)
        )

        val result = repository.getUser("123")

        assertTrue(result is ApiResult.Success)
        val user = (result as ApiResult.Success).data
        assertEquals("123", user.id)
        assertEquals("John Doe", user.name)
    }
}
```

### Testing with `TestDispatcher` (Illustrative)

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class UserViewModelTest {
    private val testDispatcher = UnconfinedTestDispatcher()

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
    }

    @After
    fun teardown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `loadUser updates state correctly`() = runTest {
        val fakeRepository = object : UserRepository(/* ... */) { /* implement for test */ }
        val viewModel = UserViewModel(fakeRepository)

        // Call and assert on viewModel.userState
    }
}
```

---

## OkHttp Interceptors

### Logging Interceptor

```kotlin
class LoggingInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): okhttp3.Response {
        val request = chain.request()
        val startTime = System.nanoTime()
        Log.d("HTTP", "→ ${request.method} ${request.url}")

        val response = chain.proceed(request)

        val durationMs = (System.nanoTime() - startTime) / 1_000_000
        Log.d("HTTP", "← ${response.code} ${request.url} (${durationMs}ms)")

        return response
    }
}
```

### Authentication Interceptor

```kotlin
class AuthInterceptor(
    private val tokenProvider: TokenProvider
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): okhttp3.Response {
        val originalRequest = chain.request()

        if (originalRequest.url.encodedPath.contains("/auth/")) {
            return chain.proceed(originalRequest)
        }

        val token = tokenProvider.getToken()

        val authenticatedRequest = originalRequest.newBuilder()
            .header("Authorization", "Bearer $token")
            .build()

        return chain.proceed(authenticatedRequest)
    }
}

interface TokenProvider {
    fun getToken(): String
}
```

### Token Refresh Interceptor (Corrected Pattern)

```kotlin
class TokenRefreshInterceptor(
    private val tokenManager: TokenManager,
    private val authApi: AuthApi
) : Interceptor {
    private val mutex = Mutex()

    override fun intercept(chain: Interceptor.Chain): okhttp3.Response {
        var request = chain.request().withAccessToken()
        var response = chain.proceed(request)

        if (response.code != 401) return response

        response.close()

        val newToken = runBlocking {
            mutex.withLock {
                val current = tokenManager.getAccessToken()
                val usedToken = request.header("Authorization")?.removePrefix("Bearer ")

                if (current != null && current != usedToken) {
                    // Another thread has already refreshed the token
                    current
                } else {
                    val refreshToken = tokenManager.getRefreshToken()
                        ?: return@withLock null
                    try {
                        val tokenResponse = authApi.refreshToken(refreshToken)
                        tokenManager.saveTokens(tokenResponse.accessToken, tokenResponse.refreshToken)
                        tokenResponse.accessToken
                    } catch (e: Exception) {
                        tokenManager.clearTokens()
                        null
                    }
                }
            }
        }

        return if (newToken != null) {
            val newRequest = chain.request().newBuilder()
                .header("Authorization", "Bearer $newToken")
                .build()
            chain.proceed(newRequest)
        } else {
            chain.proceed(chain.request())
        }
    }

    private fun Request.withAccessToken(): Request {
        val token = tokenManager.getAccessToken()
        return if (token != null) {
            newBuilder()
                .header("Authorization", "Bearer $token")
                .build()
        } else this
    }
}
```

### Retry Interceptor

```kotlin
class RetryInterceptor(
    private val maxRetries: Int = 3,
    private val retryDelay: Long = 1000
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): okhttp3.Response {
        var response: okhttp3.Response? = null
        var exception: IOException? = null

        repeat(maxRetries) { attempt ->
            try {
                response?.close()
                response = chain.proceed(chain.request())

                if (response!!.isSuccessful || response!!.code !in 500..599) {
                    return response!!
                }

                Log.w("RetryInterceptor", "Attempt ${attempt + 1} failed with ${response!!.code}")
            } catch (e: IOException) {
                Log.w("RetryInterceptor", "Attempt ${attempt + 1} failed", e)
                exception = e
            }

            if (attempt < maxRetries - 1) {
                Thread.sleep(retryDelay * (attempt + 1))
            }
        }

        return response ?: throw exception ?: IOException("Request failed after $maxRetries attempts")
    }
}
```

### Cache Interceptor

```kotlin
class CacheInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): okhttp3.Response {
        val cacheRequest = chain.request().newBuilder()
            .header("Cache-Control", "public, max-age=300")
            .build()
        return chain.proceed(cacheRequest)
    }
}

val cacheSize = 10 * 1024 * 1024 // 10 MB
val cache = Cache(context.cacheDir, cacheSize.toLong())

val okHttpClient = OkHttpClient.Builder()
    .cache(cache)
    .addNetworkInterceptor(CacheInterceptor())
    .build()
```

---

## Best Practices Checklist

Do's and Don'ts below use `ApiResult` to avoid confusion with Kotlin's built-in `Result`.

### Do's

1. Use suspend functions instead of `Call<T>` in new code.
2. Handle cancellation by rethrowing `CancellationException`.
3. Let `Retrofit` handle threading for network; use `Dispatchers.IO` for disk.
4. Configure appropriate timeouts instead of relying on defaults.
5. Use structured concurrency (`coroutineScope`/`async`) for parallel requests.
6. Use sealed result types (e.g., `ApiResult`) for clear error handling.
7. Cache responses with `Room` for offline support.
8. Use `Flow` for reactive streams over your cache.

### Don'ts

1. Do not mix `Call<T>.enqueue` callbacks with coroutines for the same API.
2. Do not swallow `CancellationException` in catch-all blocks.
3. Do not use `GlobalScope` in production; prefer scoped coroutines.
4. Do not block main thread with `runBlocking`.
5. Do not ignore error handling around network calls.
6. Do not use synchronous `OkHttp` `execute()` on the main thread.
7. Do not create a new Retrofit/OkHttp client per request.

---

## Complete Android App Example

(Conceptual, focuses on patterns rather than all types.)

### API Service

```kotlin
interface UserApiService {
    @GET("users")
    suspend fun getUsers(@Query("page") page: Int): List<User>

    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: String): User

    @POST("users")
    suspend fun createUser(@Body user: CreateUserRequest): User

    @PUT("users/{id}")
    suspend fun updateUser(@Path("id") id: String, @Body user: UpdateUserRequest): User

    @DELETE("users/{id}")
    suspend fun deleteUser(@Path("id") id: String)
}
```

### Repository / `ViewModel` / Compose UI / Hilt

(The following sections mirror patterns above: inject `Retrofit` service and DAO, expose `Flow`/`StateFlow`, use `viewModelScope` for calls, no `runBlocking`/`GlobalScope`, and use `ApiResult` for state.)

---

## Common Pitfalls

Key pitfalls (with correct patterns embedded earlier):
- Not rethrowing `CancellationException`.
- Wrapping `Retrofit` suspend calls in `withContext(Dispatchers.IO)` unnecessarily.
- Assuming `Response.body()` is non-null without checking.
- Forgetting to close `errorBody()`.
- Creating multiple `Retrofit` instances.
- Relying on unsuitable timeout defaults instead of configuring for your needs.
- Blocking the main thread with `runBlocking`.
- Mixing callbacks and coroutines for the same API surface.
- Swallowing exceptions without surfacing them to callers or UI state.

---

## Follow-ups

1. When should you prefer `Response<T>` over direct `T` in suspend endpoints, and how does that choice change your error parsing and logging strategy for different status codes?
2. How does `Retrofit` cooperate with coroutine cancellation and structured concurrency on complex screens (e.g., dashboards) that fire multiple parallel requests and navigations?
3. What concrete patterns can you use to combine `flowOn()` and `withContext()` when exposing `Retrofit`-backed data as `Flow` from repositories without breaking dispatcher confinement?
4. How can you deduplicate concurrent requests for the same resource across multiple consumers (for example, different `ViewModel`s or screens) while still keeping proper cancellation semantics?
5. How would you design an offline-first stack with `Retrofit`, `Room`, and `Flow` that includes cache invalidation rules, retry with exponential backoff, and proper handling of stale-but-usable data?
6. How can you implement robust, race-free token refresh with `OkHttp` interceptors and coroutines so that all pending requests either reuse the refreshed token or fail fast when refresh is impossible?
7. Why are sealed result hierarchies (`ApiResult`, `NetworkResponse`) more suitable for modeling API outcomes in coroutine-based architectures than nullable types or unchecked exceptions alone?

---

## References

- https://square.github.io/retrofit/
- https://kotlinlang.org/docs/coroutines-guide.html
- https://square.github.io/okhttp/
- https://developer.android.com/topic/libraries/architecture

---

## Related Questions

- [[q-flow-basics--kotlin--easy]]
- [[q-flow-operators--kotlin--medium]]

---

# Retrofit С Корутинами: Лучшие Практики

[English](#retrofit-with-coroutines-best-practices) | **Русский**

---

## Содержание

- [Обзор](#обзор-ru)
- [Suspend функции в Retrofit](#suspend-функции-в-retrofit)
- [Типы ответов: `Response<T>` vs `T`](#типы-ответов-responset-vs-t)
- [Стратегии обработки ошибок](#стратегии-обработки-ошибок-ru)
- [Конфигурация таймаутов](#конфигурация-таймаутов)
- [Обработка отмены](#обработка-отмены)
- [Конкурентные запросы](#конкурентные-запросы-ru)
- [Последовательные vs параллельные паттерны](#последовательные-vs-параллельные-паттерны)
- [Call `Adapter` vs suspend функции](#call-adapter-vs-suspend-функции)
- [`Flow` типы возврата](#flow-типы-возврата)
- [Полная реализация репозитория](#полная-реализация-репозитория)
- [Кеширование с `Room` + `Flow`](#кеширование-с-room--flow)
- [Логика повторных попыток с экспоненциальной задержкой](#логика-повторных-попыток-с-экспоненциальной-задержкой)
- [Тестирование](#тестирование-ru)
- [OkHttp перехватчики](#okhttp-перехватчики)
- [Чек-лист лучших практик](#чек-лист-лучших-практик)
- [Полный пример Android приложения](#полный-пример-android-приложения)
- [Распространенные ошибки](#распространенные-ошибки-ru)
- [Дополнительные вопросы](#дополнительные-вопросы-ru)
- [Ссылки](#ссылки-ru)
- [Связанные вопросы](#связанные-вопросы-ru)

---

<a name="обзор-ru"></a>
## Обзор

`Retrofit` с Kotlin корутинами предоставляет современный и эффективный способ обработки сетевых операций в Android-приложениях. Далее приведены лучшие практики интеграции `Retrofit` и корутин. См. также [[c-coroutines]].

**Ключевые преимущества:**
- Естественный синтаксис async/await с suspend-функциями
- Автоматическая отмена HTTP-запроса при отмене корутины
- Интеграция с `Flow` для реактивных потоков данных
- Улучшенная обработка ошибок через try-catch и типизированные результаты
- Отсутствие callback hell

---

## Suspend Функции В Retrofit

### Современный Интерфейс Retrofit

```kotlin
interface ApiService {
    // Современный подход: suspend-функция
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: String): User

    // Обёртка Response для доступа к заголовкам и статусу
    @GET("users/{id}")
    suspend fun getUserWithResponse(@Path("id") userId: String): Response<User>

    // Старый подход: `Call<T>` (в новом коде с корутинами не нужен)
    @GET("users/{id}")
    fun getUserOld(@Path("id") userId: String): Call<User>

    // Создание/обновление/удаление
    @POST("users")
    suspend fun createUser(@Body user: UserRequest): User

    @PUT("users/{id}")
    suspend fun updateUser(@Path("id") id: String, @Body user: UserRequest): User

    @DELETE("users/{id}")
    suspend fun deleteUser(@Path("id") id: String)

    // Query-параметры
    @GET("users")
    suspend fun getUsers(
        @Query("page") page: Int,
        @Query("limit") limit: Int
    ): List<User>

    // Заголовки
    @GET("profile")
    suspend fun getProfile(@Header("Authorization") token: String): Profile

    @GET("users/{id}/posts")
    suspend fun getUserPosts(@Path("id") userId: String): List<Post>

    @GET("notifications")
    suspend fun getNotifications(): List<Notification>

    @GET("feed")
    suspend fun getFeedPosts(): List<Post>

    @GET("suggestions")
    suspend fun getSuggestions(): List<User>

    @GET("orders/{id}")
    suspend fun getOrder(@Path("id") orderId: String): Order

    @GET("products/{id}")
    suspend fun getProduct(@Path("id") productId: String): Product

    @POST("orders/{id}/payment")
    suspend fun processPayment(
        @Path("id") orderId: String,
        @Query("amount") amount: Long,
        @Query("userId") userId: String
    ): Payment

    @POST("profiles/{id}")
    suspend fun createProfile(@Path("id") userId: String, @Body profile: ProfileRequest): Profile

    @POST("profiles/{id}/avatar")
    suspend fun uploadAvatar(@Path("id") profileId: String, @Body avatar: ByteArray): String

    @GET("products")
    suspend fun getAllProducts(): List<Product>

    @POST("upload")
    suspend fun uploadFile(@Body file: File): UploadResult

    @GET("search/users")
    suspend fun searchUsers(@Query("q") query: String): List<User>
}
```

### Настройка Retrofit Для Корутин

```kotlin
object RetrofitClient {
    private const val BASE_URL = "https://api.example.com/"

    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        })
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()

    val retrofit: Retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        // Для suspend-функций (Retrofit 2.6+) отдельный CallAdapter не требуется
        .build()

    val apiService: ApiService = retrofit.create(ApiService::class.java)
}
```

---

<a name="типы-ответов-responset-vs-t"></a>
## Типы Ответов: `Response<T>` Vs `T`

### Когда Использовать Прямой `T`

Используйте прямой тип `T`, когда важен только успешный результат, а не 2xx/сетевые ошибки вы готовы обрабатывать через исключения в одном месте:

```kotlin
interface ApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: String): User
}

suspend fun loadUser(userId: String): ApiResult<User> {
    return try {
        val user = apiService.getUser(userId)
        ApiResult.Success(user)
    } catch (e: CancellationException) {
        throw e
    } catch (e: Exception) {
        ApiResult.Error(e)
    }
}
```

**Плюсы:**
- Простой и чистый API
- Меньше шаблонного кода
- Все неуспехи централизованно ловятся как исключения

**Минусы:**
- Нет доступа к заголовкам
- Нет прямого доступа к коду ответа
- Ошибки только через исключения

### Когда Использовать `Response<T>`

Используйте `Response<T>`, если нужны заголовки, статус-коды или тонкая логика ошибок:

```kotlin
interface ApiService {
    @GET("users/{id}")
    suspend fun getUserWithResponse(@Path("id") userId: String): Response<User>
}

suspend fun loadUserWithDetails(userId: String): UserResult {
    val response = apiService.getUserWithResponse(userId)

    return when {
        response.isSuccessful -> {
            val user = response.body()
                ?: return UserResult.Error(response.code(), "Empty response body")
            val etag = response.headers()["ETag"]
            UserResult.Success(user, etag)
        }
        response.code() == 404 -> UserResult.NotFound
        response.code() == 429 -> {
            val retryAfter = response.headers()["Retry-After"]?.toIntOrNull()
            UserResult.RateLimited(retryAfter)
        }
        else -> {
            val errorBody = response.errorBody()?.use { it.string() }
            UserResult.Error(response.code(), errorBody)
        }
    }
}

sealed class UserResult {
    data class Success(val user: User, val etag: String?) : UserResult()
    object NotFound : UserResult()
    data class RateLimited(val retryAfterSeconds: Int?) : UserResult()
    data class Error(val code: Int, val message: String?) : UserResult()
}
```

**Плюсы:**
- Доступ к заголовкам (ETag, Cache-Control и др.)
- Доступ к статус-коду
- Гибкая обработка разных ошибок
- Неуспешные коды не превращаются автоматически в исключения

**Минусы:**
- Больше кода
- Нужно явно проверять `isSuccessful`

---

<a name="стратегии-обработки-ошибок-ru"></a>
## Стратегии Обработки Ошибок

Во всех стратегиях ниже важно не глотать `CancellationException` — его нужно пробрасывать дальше.

### Стратегия 1: Простой Try-catch

```kotlin
class UserRepository(private val api: ApiService) {
    suspend fun getUser(userId: String): User? {
        return try {
            api.getUser(userId)
        } catch (e: CancellationException) {
            throw e
        } catch (e: IOException) {
            // Сетевые ошибки
            Log.e("UserRepository", "Network error", e)
            null
        } catch (e: HttpException) {
            // HTTP-ошибки (4xx, 5xx)
            Log.e("UserRepository", "HTTP error: ${e.code()}", e)
            null
        } catch (e: Exception) {
            // Прочие ошибки
            Log.e("UserRepository", "Unknown error", e)
            null
        }
    }
}
```

### Стратегия 2: Sealed-класс `ApiResult<T>`

```kotlin
sealed class ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>()
    data class Error(val exception: Throwable) : ApiResult<Nothing>()
    object Loading : ApiResult<Nothing>()
}

class UserRepository(private val api: ApiService) {
    suspend fun getUser(userId: String): ApiResult<User> {
        return try {
            val user = api.getUser(userId)
            ApiResult.Success(user)
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            ApiResult.Error(e)
        }
    }
}

class UserViewModel(private val repository: UserRepository) : ViewModel() {
    private val _userState = MutableStateFlow<ApiResult<User>>(ApiResult.Loading)
    val userState: StateFlow<ApiResult<User>> = _userState.asStateFlow()

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _userState.value = ApiResult.Loading
            _userState.value = repository.getUser(userId)
        }
    }
}
```

### Стратегия 3: `NetworkResponse<T, E>` (расширенная)

```kotlin
sealed class NetworkResponse<out T, out E> {
    data class Success<T>(val data: T) : NetworkResponse<T, Nothing>()
    data class ApiError<E>(val body: E, val code: Int) : NetworkResponse<Nothing, E>()
    data class NetworkError(val error: IOException) : NetworkResponse<Nothing, Nothing>()
    data class UnknownError(val error: Throwable) : NetworkResponse<Nothing, Nothing>()
}

data class ApiErrorResponse(
    val message: String,
    val code: String?,
    val details: Map<String, String>?
)

suspend fun <T, E> safeApiCall(
    errorClass: Class<E>,
    apiCall: suspend () -> Response<T>
): NetworkResponse<T, E> {
    return try {
        val response = apiCall()
        if (response.isSuccessful) {
            val body = response.body()
            if (body != null) {
                NetworkResponse.Success(body)
            } else {
                NetworkResponse.UnknownError(NullPointerException("Response body is null"))
            }
        } else {
            val errorBody = response.errorBody()?.use { it.string() }
            val errorResponse = try {
                if (errorBody != null) Gson().fromJson(errorBody, errorClass) else null
            } catch (e: Exception) {
                null
            }
            if (errorResponse != null) {
                NetworkResponse.ApiError(errorResponse, response.code())
            } else {
                NetworkResponse.UnknownError(Exception("Unknown API error"))
            }
        }
    } catch (e: CancellationException) {
        throw e
    } catch (e: IOException) {
        NetworkResponse.NetworkError(e)
    } catch (e: Exception) {
        NetworkResponse.UnknownError(e)
    }
}

class NetworkUserRepository(private val api: ApiService) {
    suspend fun getUser(userId: String): NetworkResponse<User, ApiErrorResponse> {
        return safeApiCall(ApiErrorResponse::class.java) {
            api.getUserWithResponse(userId)
        }
    }
}
```

---

## Конфигурация Таймаутов

- Настройте `connectTimeout`, `readTimeout`, `writeTimeout`, `callTimeout` на уровне `OkHttp`.
- Используйте `withTimeout` / `withTimeoutOrNull` для ограничений на уровне корутин.
- При необходимости добавьте `TimeoutInterceptor` и заголовки вроде `X-Timeout` для специфичных запросов.

(Код совпадает с английским разделом Timeout Configuration.)

---

## Обработка Отмены

- `Retrofit` (2.6+) отменяет HTTP-вызов при отмене корутины.
- В `ViewModel` храните `Job` и отменяйте предыдущие загрузки при новых запросах.
- Для нескольких запросов одного ресурса можно отслеживать активные `Deferred` (пример `CancellableRepository`).
- При отмене выполняйте очистку ресурсов (файлы, стримы) и пробрасывайте `CancellationException` дальше.

(Код совпадает с английскими примерами Cancellation Handling.)

---

<a name="конкурентные-запросы-ru"></a>
## Конкурентные Запросы

- Для параллельных запросов используйте `coroutineScope` + `async/await`.
- Для дашбордов и комплексных экранов объединяйте несколько запросов в один результат (`DashboardData`).
- Для частичных отказов оборачивайте каждый `async` в `try-catch`.
- При необходимости изолировать ошибки используйте `supervisorScope`.

(Код идентичен разделу Concurrent Requests на английском.)

---

## Последовательные Vs Параллельные Паттерны

- Последовательные: когда каждый следующий запрос зависит от результата предыдущего (пример `createUserWithProfile`).
- Параллельные: независимые запросы (`loadMultipleUsers`).
- Смешанные: часть данных грузится параллельно, затем используется в последующих шагах (`processOrder`).

(Код совпадает с английской секцией Sequential Vs Parallel Patterns.)

---

## Call Adapter Vs Suspend Функции

- Устаревший подход: `CallAdapter` (RxJava и др.) с возвратом `Call<T>` или `Single<T>`.
- Современный подход: нативные suspend-функции в `Retrofit` (2.6+) без дополнительных адаптеров.

(Кодовые примеры `Call` `Adapter` и CoroutineApiService совпадают с английскими.)

---

## `Flow` Типы Возврата

- Используйте `Flow` для периодического опроса (polling) и подписок.
- Для SSE/WebSocket используйте `callbackFlow` с ручным управлением ресурсами и `awaitClose`.
- Переключайте выполнение на `Dispatchers.IO` через `flowOn`.

(Кодовые примеры `observeUser`, SSE и WebSocket идентичны английской секции `Flow` Return Types.)

---

## Полная Реализация Репозитория

- Репозиторий объединяет `Retrofit` и `Room`.
- Используются `ApiResult` для представления состояний (Loading/Success/Error).
- Реализованы кеширование, пагинация, обновление и удаление пользователя.
- Корутинный контекст (`Dispatchers.IO`) применяется для операций ввода-вывода.

(Код полностью совпадает с английской секцией Complete Repository Implementation.)

---

## Кеширование С Room + `Flow`

- Подход Cache-First: сначала отдать кеш, затем обновить из сети.
- Подход Network-First: сначала сеть, в случае неудачи — кеш.
- Реактивные обновления: `Flow` из DAO + фоновые синхронизации.

(Кодовые примеры ProductRepository и ReactiveProductRepository идентичны английскому разделу.)

---

## Логика Повторных Попыток С Экспоненциальной Задержкой

- `retryIO` для простого ретрая по `IOException`.
- `RetryConfig` + `retryWithPolicy` для гибких политик (типы ошибок, лимиты, коэффициенты).
- `retryWithBackoff` для `Flow` с экспоненциальной задержкой между попытками.

(Код совпадает с английской секцией Retry Logic with Exponential Backoff.)

---

<a name="тестирование-ru"></a>
## Тестирование

- Используйте `MockWebServer` для контролируемых ответов сервера.
- Применяйте тестовые диспетчеры (`UnconfinedTestDispatcher`, `runTest`) для управления корутинами.
- Инъецируйте зависимости (API, DAO, диспетчеры), не используйте реальные сети/БД в unit-тестах.

(Код идентичен английской секции Testing.)

---

<a name="okhttp-перехватчики"></a>
## OkHttp Перехватчики

- Перехватчик логирования запросов/ответов.
- Перехватчик авторизации: добавление `Authorization`-заголовка.
- Перехватчик обновления токена с синхронизацией через `Mutex`.
- Перехватчик повторных попыток для 5xx/сетевых ошибок.
- Перехватчик кеширования с заголовками `Cache-Control`.

(Код идентичен английским примерам `OkHttp` Interceptors.)

---

<a name="чек-лист-лучших-практик"></a>
## Чек-лист Лучших Практик

### Что Делать

1. Использовать suspend-функции вместо `Call<T>` в новом коде.
2. Явно обрабатывать отмену (пробрасывать `CancellationException`).
3. Поручать `Retrofit` управление потоками для сети, использовать `Dispatchers.IO` для диска.
4. Настраивать таймауты под реальные условия.
5. Использовать структурированный параллелизм (`coroutineScope`/`async`).
6. Применять sealed-классы (`ApiResult`, `NetworkResponse`) для результатов запросов.
7. Кешировать ответы через `Room` для оффлайн-режима.
8. Использовать `Flow` для реактивной работы с кешом и сетью.

### Чего Избегать

1. Не смешивать `Call<T>.enqueue` и корутины для одного и того же API.
2. Не глотать `CancellationException`.
3. Не использовать `GlobalScope` в продакшене.
4. Не блокировать главный поток через `runBlocking`.
5. Не игнорировать обработку ошибок.
6. Не вызывать синхронный `execute()` на главном потоке.
7. Не создавать новый Retrofit/OkHttp client на каждый запрос.

---

<a name="полный-пример-android-приложения"></a>
## Полный Пример Android Приложения

- API-сервис определяет suspend-эндпоинты (пример `UserApiService`).
- Репозитории инкапсулируют сетевую и кеширующую логику, возвращают `Flow`/`ApiResult`.
- `ViewModel` использует `viewModelScope`, слушает репозитории и предоставляет `StateFlow` в UI.
- UI (Compose/Views) подписывается на состояния и не содержит сетевой логики.

(Структура слоев соответствует английскому разделу Complete Android App Example.)

---

<a name="распространенные-ошибки-ru"></a>
## Распространенные Ошибки

Основные типичные ошибки:
- Не пробрасывается `CancellationException`.
- Обращение к `Response.body()` без проверки на null.
- Забывают закрыть `errorBody()`.
- Создают несколько экземпляров Retrofit/OkHttp без необходимости.
- Смешивают callback-API и корутины для одного и того же эндпоинта.
- Используют неподходящие значения таймаутов.
- Блокируют главный поток с помощью `runBlocking` или синхронных вызовов.

---

<a name="дополнительные-вопросы-ru"></a>
## Дополнительные Вопросы (RU)

1. В каких случаях стоит предпочесть `Response<T>` прямому `T` в suspend-эндпоинтах и как это влияет на стратегию парсинга и логирования ошибок для разных статус-кодов?
2. Как `Retrofit` взаимодействует с отменой корутин и структурированным параллелизмом на сложных экранах (например, дашбордах) с несколькими параллельными запросами и навигацией?
3. Какие конкретные паттерны позволяют корректно сочетать `flowOn()` и `withContext()` при экспонировании данных `Retrofit` как `Flow` из репозиториев, не нарушая ограничений диспетчеров?
4. Как дедуплицировать параллельные запросы одного и того же ресурса между несколькими потребителями (например, разными `ViewModel` или экранами), сохраняя корректную отмену?
5. Как спроектировать offline-first стек с `Retrofit`, `Room` и `Flow`, включающий правила инвалидации кеша, ретраи с экспоненциальной задержкой и обработку устаревших, но пригодных данных?
6. Как реализовать надёжную, свободную от гонок логику обновления токена с `OkHttp`-перехватчиками и корутинами так, чтобы ожидающие запросы либо переиспользовали новый токен, либо быстро завершались при неуспешном обновлении?
7. Почему и в каких сценариях иерархии результатов (`ApiResult`, `NetworkResponse`) удобнее для моделирования исходов API в корутинной архитектуре, чем nullable-типы или только исключения?

---

<a name="ссылки-ru"></a>
## Ссылки (RU)

- https://square.github.io/retrofit/
- https://kotlinlang.org/docs/coroutines-guide.html
- https://square.github.io/okhttp/
- https://developer.android.com/topic/libraries/architecture

---

<a name="связанные-вопросы-ru"></a>
## Связанные Вопросы (RU)

- [[q-flow-basics--kotlin--easy]]
- [[q-flow-operators--kotlin--medium]]

---
