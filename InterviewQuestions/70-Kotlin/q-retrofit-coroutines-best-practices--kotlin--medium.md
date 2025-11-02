---
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
related: [q-by-keyword-function-call--programming-languages--easy, q-flow-basics--kotlin--easy, q-why-data-sealed-classes--programming-languages--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [android, best-practices, coroutines, difficulty/medium, error-handling, kotlin, networking, okhttp, rest-api, retrofit]
date created: Friday, October 31st 2025, 6:30:28 pm
date modified: Saturday, November 1st 2025, 5:43:24 pm
---

# Retrofit with Coroutines: Best Practices

**English** | [Русский](#russian-version)

---

## Table of Contents

- [Overview](#overview)
- [Suspend Functions in Retrofit](#suspend-functions-in-retrofit)
- [Response Types: Response&lt;T&gt; vs T](#response-types-responset-vs-t)
- [Error Handling Strategies](#error-handling-strategies)
- [Timeout Configuration](#timeout-configuration)
- [Cancellation Handling](#cancellation-handling)
- [Concurrent Requests](#concurrent-requests)
- [Sequential vs Parallel Patterns](#sequential-vs-parallel-patterns)
- [Call Adapter vs Suspend Functions](#call-adapter-vs-suspend-functions)
- [Flow Return Types](#flow-return-types)
- [Complete Repository Implementation](#complete-repository-implementation)
- [Caching with Room + Flow](#caching-with-room--flow)
- [Retry Logic with Exponential Backoff](#retry-logic-with-exponential-backoff)
- [Testing](#testing)
- [OkHttp Interceptors](#okhttp-interceptors)
- [Best Practices Checklist](#best-practices-checklist)
- [Complete Android App Example](#complete-android-app-example)
- [Common Pitfalls](#common-pitfalls)
- [Follow-up Questions](#follow-up-questions)
- [References](#references)
- [Related Questions](#related-questions)

---

## Overview

Retrofit with Kotlin Coroutines provides a modern, efficient way to handle network operations in Android applications. This guide covers best practices for integrating Retrofit with coroutines.

**Key Benefits:**
- Natural async/await syntax with suspend functions
- Automatic request cancellation when coroutine is cancelled
- Seamless integration with Flow for reactive streams
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

    //  Old approach: Call<T> (not needed with coroutines)
    @GET("users/{id}")
    fun getUserOld(@Path("id") userId: String): Call<User>

    //  Multiple suspend operations
    @POST("users")
    suspend fun createUser(@Body user: UserRequest): User

    @PUT("users/{id}")
    suspend fun updateUser(@Path("id") id: String, @Body user: UserRequest): User

    @DELETE("users/{id}")
    suspend fun deleteUser(@Path("id") id: String): Unit

    //  Query parameters
    @GET("users")
    suspend fun getUsers(
        @Query("page") page: Int,
        @Query("limit") limit: Int
    ): List<User>

    //  Headers
    @GET("profile")
    suspend fun getProfile(@Header("Authorization") token: String): Profile
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
        // No need for CallAdapter with suspend functions
        .build()

    val apiService: ApiService = retrofit.create(ApiService::class.java)
}
```

---

## Response Types: Response&lt;T&gt; Vs T

### When to Use Direct T

Use direct type `T` when you only care about the success case:

```kotlin
interface ApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: String): User
}

// Usage
suspend fun loadUser(userId: String): Result<User> {
    return try {
        val user = apiService.getUser(userId)
        Result.success(user)
    } catch (e: Exception) {
        Result.failure(e)
    }
}
```

**Pros:**
- Cleaner API
- Less boilerplate
- Automatic error on non-2xx status codes

**Cons:**
- No access to headers
- No access to status code
- Throws exception on error

### When to Use Response&lt;T&gt;

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
            val user = response.body()!!
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
            val errorBody = response.errorBody()?.string()
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
- No exception on error

**Cons:**
- More boilerplate
- Manual success/error checking

---

## Error Handling Strategies

### Strategy 1: Try-Catch (Simple)

```kotlin
class UserRepository(private val api: ApiService) {
    suspend fun getUser(userId: String): User? {
        return try {
            api.getUser(userId)
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

### Strategy 2: Result&lt;T&gt; Sealed Class

```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val exception: Throwable) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

class UserRepository(private val api: ApiService) {
    suspend fun getUser(userId: String): Result<User> {
        return try {
            val user = api.getUser(userId)
            Result.Success(user)
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
}

// Usage in ViewModel
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    private val _userState = MutableStateFlow<Result<User>>(Result.Loading)
    val userState: StateFlow<Result<User>> = _userState.asStateFlow()

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _userState.value = Result.Loading
            _userState.value = repository.getUser(userId)
        }
    }
}
```

### Strategy 3: NetworkResponse&lt;T, E&gt; (Advanced)

```kotlin
sealed class NetworkResponse<out T, out E> {
    data class Success<T>(val data: T) : NetworkResponse<T, Nothing>()
    data class ApiError<E>(val body: E, val code: Int) : NetworkResponse<Nothing, E>()
    data class NetworkError(val error: IOException) : NetworkResponse<Nothing, Nothing>()
    data class UnknownError(val error: Throwable) : NetworkResponse<Nothing, Nothing>()
}

// Error response models
data class ApiErrorResponse(
    val message: String,
    val code: String?,
    val details: Map<String, String>?
)

// Extension function to wrap API calls
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
            val errorBody = response.errorBody()?.string()
            val errorResponse = try {
                Gson().fromJson(errorBody, errorClass)
            } catch (e: Exception) {
                null
            }
            if (errorResponse != null) {
                NetworkResponse.ApiError(errorResponse, response.code())
            } else {
                NetworkResponse.UnknownError(Exception("Unknown API error"))
            }
        }
    } catch (e: IOException) {
        NetworkResponse.NetworkError(e)
    } catch (e: Exception) {
        NetworkResponse.UnknownError(e)
    }
}

// Usage
class UserRepository(private val api: ApiService) {
    suspend fun getUser(userId: String): NetworkResponse<User, ApiErrorResponse> {
        return safeApiCall(ApiErrorResponse::class.java) {
            api.getUserWithResponse(userId)
        }
    }
}

// In ViewModel
fun loadUser(userId: String) {
    viewModelScope.launch {
        when (val result = repository.getUser(userId)) {
            is NetworkResponse.Success -> {
                _userState.value = UserState.Success(result.data)
            }
            is NetworkResponse.ApiError -> {
                _userState.value = UserState.Error(result.body.message)
            }
            is NetworkResponse.NetworkError -> {
                _userState.value = UserState.Error("Network error. Please check your connection.")
            }
            is NetworkResponse.UnknownError -> {
                _userState.value = UserState.Error("An unexpected error occurred")
            }
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

    // Read timeout: time between each byte read from server
    .readTimeout(30, TimeUnit.SECONDS)

    // Write timeout: time between each byte sent to server
    .writeTimeout(30, TimeUnit.SECONDS)

    // Call timeout: entire call duration (connection + read + write)
    .callTimeout(60, TimeUnit.SECONDS)
    .build()
```

### Per-Request Timeout with Coroutines

```kotlin
// Using withTimeout
suspend fun getUserWithTimeout(userId: String): User? {
    return try {
        withTimeout(5000) { // 5 seconds
            apiService.getUser(userId)
        }
    } catch (e: TimeoutCancellationException) {
        Log.e("API", "Request timed out")
        null
    } catch (e: Exception) {
        Log.e("API", "Error", e)
        null
    }
}

// Using withTimeoutOrNull (returns null on timeout)
suspend fun getUserWithTimeoutOrNull(userId: String): User? {
    return withTimeoutOrNull(5000) {
        apiService.getUser(userId)
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

        // Check for custom timeout annotation or header
        val customTimeout = request.header("X-Timeout")?.toLongOrNull()

        return if (customTimeout != null) {
            chain.withConnectTimeout(customTimeout.toInt(), TimeUnit.SECONDS)
                .withReadTimeout(customTimeout.toInt(), TimeUnit.SECONDS)
                .withWriteTimeout(customTimeout.toInt(), TimeUnit.SECONDS)
                .proceed(request)
        } else {
            chain.proceed(request)
        }
    }
}

// Usage with custom timeout header
interface ApiService {
    @Headers("X-Timeout: 60")
    @GET("large-data")
    suspend fun getLargeData(): LargeDataResponse
}
```

---

## Cancellation Handling

### Automatic Cancellation

When a coroutine is cancelled, Retrofit automatically cancels the underlying OkHttp call:

```kotlin
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    private var loadJob: Job? = null

    fun loadUser(userId: String) {
        // Cancel previous request
        loadJob?.cancel()

        loadJob = viewModelScope.launch {
            try {
                val user = repository.getUser(userId)
                _userState.value = UserState.Success(user)
            } catch (e: CancellationException) {
                // Request was cancelled, don't update UI
                throw e // Re-throw to propagate cancellation
            } catch (e: Exception) {
                _userState.value = UserState.Error(e.message ?: "Unknown error")
            }
        }
    }
}
```

### Manual Cancellation with Job Tracking

```kotlin
class UserRepository(private val api: ApiService) {
    private val activeRequests = mutableMapOf<String, Job>()

    suspend fun getUser(userId: String): User? = coroutineScope {
        // Cancel existing request for this user
        activeRequests[userId]?.cancel()

        val job = launch {
            try {
                val user = api.getUser(userId)
                activeRequests.remove(userId)
                user
            } catch (e: CancellationException) {
                activeRequests.remove(userId)
                throw e
            }
        }

        activeRequests[userId] = job
        job.await()
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
class UserRepository(private val api: ApiService) {
    // Run requests in parallel
    suspend fun getUserWithPosts(userId: String): Pair<User, List<Post>> = coroutineScope {
        val userDeferred = async { api.getUser(userId) }
        val postsDeferred = async { api.getUserPosts(userId) }

        // Await both results
        val user = userDeferred.await()
        val posts = postsDeferred.await()

        user to posts
    }

    // Multiple parallel requests
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

### Handling Partial Failures

```kotlin
suspend fun getDashboardDataSafe(): DashboardData = coroutineScope {
    // Use awaitAll with error handling
    val results = listOf(
        async {
            try {
                api.getUser("me")
            } catch (e: Exception) {
                null
            }
        },
        async {
            try {
                api.getNotifications()
            } catch (e: Exception) {
                emptyList()
            }
        },
        async {
            try {
                api.getFeedPosts()
            } catch (e: Exception) {
                emptyList()
            }
        }
    )

    DashboardData(
        user = results[0].await() as? User,
        notifications = results[1].await() as? List<Notification> ?: emptyList(),
        posts = results[2].await() as? List<Post> ?: emptyList(),
        suggestions = emptyList()
    )
}

// Better approach with supervisorScope
suspend fun getDashboardDataSupervisor(): DashboardData = supervisorScope {
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
        user = userDeferred.await(),
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
    userRequest: UserRequest,
    profileRequest: ProfileRequest
): Profile {
    // Step 1: Create user
    val user = apiService.createUser(userRequest)

    // Step 2: Create profile (needs user.id from step 1)
    val profile = apiService.createProfile(user.id, profileRequest)

    // Step 3: Upload avatar (needs profile.id from step 2)
    val avatarUrl = apiService.uploadAvatar(profile.id, profileRequest.avatar)

    return profile.copy(avatarUrl = avatarUrl)
}
```

### Parallel Execution

Use when requests are independent:

```kotlin
suspend fun loadMultipleUsers(userIds: List<String>): List<User> = coroutineScope {
    userIds.map { userId ->
        async { apiService.getUser(userId) }
    }.awaitAll()
}

// With error handling
suspend fun loadMultipleUsersSafe(userIds: List<String>): List<User> = coroutineScope {
    userIds.mapNotNull { userId ->
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
suspend fun processOrder(orderId: String): OrderResult = coroutineScope {
    // Step 1: Get order (sequential - must be first)
    val order = apiService.getOrder(orderId)

    // Step 2: Parallel operations that depend on order
    val userDeferred = async { apiService.getUser(order.userId) }
    val productsDeferred = async {
        order.productIds.map { productId ->
            async { apiService.getProduct(productId) }
        }.awaitAll()
    }
    val shippingDeferred = async { apiService.getShippingInfo(order.shippingId) }

    // Step 3: Wait for all parallel operations
    val user = userDeferred.await()
    val products = productsDeferred.await()
    val shipping = shippingDeferred.await()

    // Step 4: Process payment (sequential - must be last)
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
// Old way (not recommended for new code)
class RxJava2CallAdapterFactory // or CoroutineCallAdapterFactory

val retrofit = Retrofit.Builder()
    .baseUrl(BASE_URL)
    .addCallAdapterFactory(RxJava2CallAdapterFactory.create())
    .addConverterFactory(GsonConverterFactory.create())
    .build()

interface ApiService {
    @GET("users/{id}")
    fun getUser(@Path("id") userId: String): Single<User>
}
```

### Modern Approach: Suspend Functions

```kotlin
// Modern way (recommended)
val retrofit = Retrofit.Builder()
    .baseUrl(BASE_URL)
    .addConverterFactory(GsonConverterFactory.create())
    // No call adapter needed!
    .build()

interface ApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: String): User
}
```

**Why suspend functions are better:**
- Built-in support (Retrofit 2.6+)
- No extra dependency
- Natural Kotlin syntax
- Better error handling
- Automatic cancellation support
- Simpler testing

**When you might still use Call Adapters:**
- Legacy codebase with RxJava
- Need for specific reactive features
- Custom call handling logic

---

## Flow Return Types

### Basic Flow with callbackFlow

```kotlin
interface ApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: String): User
}

class UserRepository(private val api: ApiService) {
    // Polling with Flow
    fun observeUser(userId: String, intervalMs: Long = 5000): Flow<User> = flow {
        while (currentCoroutineContext().isActive) {
            val user = api.getUser(userId)
            emit(user)
            delay(intervalMs)
        }
    }.flowOn(Dispatchers.IO)
}
```

### Server-Sent Events (SSE) with Flow

```kotlin
interface ApiService {
    @GET("notifications/stream")
    @Streaming
    suspend fun getNotificationStream(): ResponseBody
}

class NotificationRepository(private val api: ApiService) {
    fun observeNotifications(): Flow<Notification> = callbackFlow {
        val response = api.getNotificationStream()
        val reader = response.byteStream().bufferedReader()

        try {
            while (isActive) {
                val line = reader.readLine() ?: break
                if (line.startsWith("data: ")) {
                    val json = line.substring(6)
                    val notification = Gson().fromJson(json, Notification::class.java)
                    send(notification)
                }
            }
        } catch (e: Exception) {
            close(e)
        } finally {
            reader.close()
            response.close()
        }

        awaitClose {
            reader.close()
            response.close()
        }
    }.flowOn(Dispatchers.IO)
}
```

### WebSocket with Flow

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

    suspend fun sendMessage(roomId: String, message: String) {
        // Implementation for sending messages
    }
}
```

---

## Complete Repository Implementation

```kotlin
/**
 * Complete repository implementation with all best practices
 */
class UserRepository(
    private val api: ApiService,
    private val userDao: UserDao,
    private val dispatcher: CoroutineDispatcher = Dispatchers.IO
) {
    // StateFlow for current user
    private val _currentUser = MutableStateFlow<Result<User>>(Result.Loading)
    val currentUser: StateFlow<Result<User>> = _currentUser.asStateFlow()

    // Flow from Room database
    fun observeUser(userId: String): Flow<User?> {
        return userDao.observeUser(userId)
    }

    // Single fetch with caching
    suspend fun getUser(
        userId: String,
        forceRefresh: Boolean = false
    ): Result<User> = withContext(dispatcher) {
        try {
            // Check cache first
            if (!forceRefresh) {
                val cachedUser = userDao.getUser(userId)
                if (cachedUser != null && !cachedUser.isExpired()) {
                    return@withContext Result.Success(cachedUser)
                }
            }

            // Fetch from network
            val user = api.getUser(userId)

            // Update cache
            userDao.insertUser(user)

            Result.Success(user)
        } catch (e: IOException) {
            // Network error - return cached data if available
            val cachedUser = userDao.getUser(userId)
            if (cachedUser != null) {
                Result.Success(cachedUser)
            } else {
                Result.Error(e)
            }
        } catch (e: HttpException) {
            Result.Error(e)
        } catch (e: Exception) {
            Result.Error(e)
        }
    }

    // Update user
    suspend fun updateUser(userId: String, updates: UserUpdate): Result<User> {
        return withContext(dispatcher) {
            try {
                val user = api.updateUser(userId, updates)
                userDao.insertUser(user)
                _currentUser.value = Result.Success(user)
                Result.Success(user)
            } catch (e: Exception) {
                Result.Error(e)
            }
        }
    }

    // Delete user
    suspend fun deleteUser(userId: String): Result<Unit> {
        return withContext(dispatcher) {
            try {
                api.deleteUser(userId)
                userDao.deleteUser(userId)
                Result.Success(Unit)
            } catch (e: Exception) {
                Result.Error(e)
            }
        }
    }

    // Search users (no caching)
    suspend fun searchUsers(query: String): Result<List<User>> {
        return withContext(dispatcher) {
            try {
                val users = api.searchUsers(query)
                Result.Success(users)
            } catch (e: Exception) {
                Result.Error(e)
            }
        }
    }

    // Paginated fetch
    suspend fun getUsersPaginated(page: Int, limit: Int): Result<List<User>> {
        return withContext(dispatcher) {
            try {
                val users = api.getUsers(page, limit)
                Result.Success(users)
            } catch (e: Exception) {
                Result.Error(e)
            }
        }
    }
}

// Result sealed class
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val exception: Throwable) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

// User entity with expiration
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

// Room DAO
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

## Caching with Room + Flow

### Cache-First Strategy

```kotlin
class ProductRepository(
    private val api: ApiService,
    private val productDao: ProductDao
) {
    // Observe product with cache-first strategy
    fun observeProduct(productId: String): Flow<Product?> = flow {
        // Emit cached data immediately
        emitAll(productDao.observeProduct(productId))

        // Refresh from network in background
        try {
            val product = api.getProduct(productId)
            productDao.insertProduct(product)
        } catch (e: Exception) {
            Log.e("ProductRepository", "Failed to refresh product", e)
        }
    }

    // Get product with cache
    suspend fun getProduct(
        productId: String,
        forceRefresh: Boolean = false
    ): Flow<Result<Product>> = flow {
        emit(Result.Loading)

        // Emit cached data
        if (!forceRefresh) {
            val cached = productDao.getProduct(productId)
            if (cached != null) {
                emit(Result.Success(cached))
            }
        }

        // Fetch from network
        try {
            val product = api.getProduct(productId)
            productDao.insertProduct(product)
            emit(Result.Success(product))
        } catch (e: Exception) {
            // If we have cached data, don't emit error
            val cached = productDao.getProduct(productId)
            if (cached == null) {
                emit(Result.Error(e))
            }
        }
    }
}
```

### Network-First Strategy

```kotlin
fun getProductNetworkFirst(productId: String): Flow<Result<Product>> = flow {
    emit(Result.Loading)

    try {
        // Try network first
        val product = api.getProduct(productId)
        productDao.insertProduct(product)
        emit(Result.Success(product))
    } catch (e: Exception) {
        // Fall back to cache on error
        val cached = productDao.getProduct(productId)
        if (cached != null) {
            emit(Result.Success(cached))
        } else {
            emit(Result.Error(e))
        }
    }
}
```

### Reactive Cache Updates

```kotlin
class ProductRepository(
    private val api: ApiService,
    private val productDao: ProductDao
) {
    // Automatically refresh cache on app start
    init {
        CoroutineScope(Dispatchers.IO).launch {
            refreshAllProducts()
        }
    }

    // Observe all products with automatic refresh
    fun observeProducts(): Flow<List<Product>> = productDao.observeAllProducts()
        .onStart {
            // Trigger refresh when collection starts
            refreshAllProducts()
        }

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
    initialDelay: Long = 100, // milliseconds
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

// Usage
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

            // Check if exception is retryable
            val isRetryable = config.retryableExceptions.any { it.isInstance(e) }

            if (!isRetryable || attempt == config.maxAttempts - 1) {
                throw e
            }

            Log.w("Retry", "Attempt ${attempt + 1} failed, retrying in ${currentDelay}ms", e)
            delay(currentDelay)
            currentDelay = (currentDelay * config.factor).toLong().coerceAtMost(config.maxDelay)
        }
    }

    throw lastException ?: Exception("Retry failed")
}

// Usage with custom config
suspend fun uploadFile(file: File): UploadResult {
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

### Retry with Flow

```kotlin
fun <T> Flow<T>.retryWithBackoff(
    retries: Long = 3,
    initialDelay: Long = 100,
    maxDelay: Long = 1000,
    factor: Double = 2.0,
    predicate: (Throwable) -> Boolean = { true }
): Flow<T> = this.retryWhen { cause, attempt ->
    if (attempt < retries && predicate(cause)) {
        val delay = (initialDelay * factor.pow(attempt.toDouble()))
            .toLong()
            .coerceAtMost(maxDelay)
        delay(delay)
        true
    } else {
        false
    }
}

// Usage
fun observeUserWithRetry(userId: String): Flow<User> = flow {
    emit(apiService.getUser(userId))
}.retryWithBackoff(
    retries = 3,
    predicate = { it is IOException }
)
```

---

## Testing

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
        repository = UserRepository(apiService)
    }

    @After
    fun teardown() {
        mockWebServer.shutdown()
    }

    @Test
    fun `getUser returns user on success`() = runTest {
        // Arrange
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

        // Act
        val result = repository.getUser("123")

        // Assert
        assertTrue(result is Result.Success)
        val user = (result as Result.Success).data
        assertEquals("123", user.id)
        assertEquals("John Doe", user.name)
    }

    @Test
    fun `getUser returns error on 404`() = runTest {
        // Arrange
        mockWebServer.enqueue(
            MockResponse()
                .setResponseCode(404)
                .setBody("{\"error\": \"User not found\"}")
        )

        // Act
        val result = repository.getUser("999")

        // Assert
        assertTrue(result is Result.Error)
    }

    @Test
    fun `getUser handles network error`() = runTest {
        // Arrange
        mockWebServer.enqueue(
            MockResponse()
                .setSocketPolicy(SocketPolicy.DISCONNECT_AT_START)
        )

        // Act
        val result = repository.getUser("123")

        // Assert
        assertTrue(result is Result.Error)
        assertTrue((result as Result.Error).exception is IOException)
    }
}
```

### Testing with TestDispatcher

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
        // Arrange
        val mockRepository = mock<UserRepository>()
        val expectedUser = User("123", "John", "john@example.com", null)
        whenever(mockRepository.getUser("123")).thenReturn(Result.Success(expectedUser))

        val viewModel = UserViewModel(mockRepository)

        // Act
        viewModel.loadUser("123")

        // Assert
        val state = viewModel.userState.value
        assertTrue(state is UserState.Success)
        assertEquals(expectedUser, (state as UserState.Success).user)
    }

    @Test
    fun `loadUser handles error`() = runTest {
        // Arrange
        val mockRepository = mock<UserRepository>()
        val exception = IOException("Network error")
        whenever(mockRepository.getUser("123")).thenReturn(Result.Error(exception))

        val viewModel = UserViewModel(mockRepository)

        // Act
        viewModel.loadUser("123")

        // Assert
        val state = viewModel.userState.value
        assertTrue(state is UserState.Error)
    }
}
```

### Testing Concurrent Requests

```kotlin
@Test
fun `loadMultipleUsers makes parallel requests`() = runTest {
    // Arrange
    val userIds = listOf("1", "2", "3")
    val responses = userIds.map { id ->
        """{"id": "$id", "name": "User $id", "email": "user$id@example.com"}"""
    }

    responses.forEach { response ->
        mockWebServer.enqueue(
            MockResponse()
                .setResponseCode(200)
                .setBody(response)
                .setBodyDelay(100, TimeUnit.MILLISECONDS) // Simulate network delay
        )
    }

    val startTime = System.currentTimeMillis()

    // Act
    val users = repository.loadMultipleUsers(userIds)

    val endTime = System.currentTimeMillis()
    val duration = endTime - startTime

    // Assert
    assertEquals(3, users.size)
    // Should complete in ~100ms (parallel), not 300ms (sequential)
    assertTrue(duration < 200, "Requests should be parallel, took ${duration}ms")
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

        val endTime = System.nanoTime()
        val duration = (endTime - startTime) / 1_000_000 // Convert to ms

        Log.d("HTTP", "← ${response.code} ${request.url} (${duration}ms)")

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

        // Skip auth for certain endpoints
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

### Token Refresh Interceptor

```kotlin
class TokenRefreshInterceptor(
    private val tokenManager: TokenManager,
    private val authApi: AuthApi
) : Interceptor {
    private val mutex = Mutex()

    override fun intercept(chain: Interceptor.Chain): okhttp3.Response {
        val request = chain.request()
        val token = tokenManager.getAccessToken()

        // Add token to request
        val authenticatedRequest = request.newBuilder()
            .header("Authorization", "Bearer $token")
            .build()

        var response = chain.proceed(authenticatedRequest)

        // If 401, refresh token and retry
        if (response.code == 401) {
            response.close()

            // Use runBlocking for synchronous refresh in interceptor
            runBlocking {
                mutex.withLock {
                    // Check if token was already refreshed by another thread
                    val currentToken = tokenManager.getAccessToken()
                    if (currentToken != token) {
                        // Token was refreshed, retry with new token
                        val retryRequest = request.newBuilder()
                            .header("Authorization", "Bearer $currentToken")
                            .build()
                        return@runBlocking chain.proceed(retryRequest)
                    }

                    // Refresh token
                    try {
                        val refreshToken = tokenManager.getRefreshToken()
                        val tokenResponse = authApi.refreshToken(refreshToken)
                        tokenManager.saveTokens(
                            tokenResponse.accessToken,
                            tokenResponse.refreshToken
                        )

                        // Retry with new token
                        val retryRequest = request.newBuilder()
                            .header("Authorization", "Bearer ${tokenResponse.accessToken}")
                            .build()
                        chain.proceed(retryRequest)
                    } catch (e: Exception) {
                        // Refresh failed, logout user
                        tokenManager.clearTokens()
                        response
                    }
                }
            }
        }

        return response
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
        var request = chain.request()
        var response: okhttp3.Response? = null
        var exception: IOException? = null

        repeat(maxRetries) { attempt ->
            try {
                response?.close()
                response = chain.proceed(request)

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
        val request = chain.request()

        // Add cache control header
        val cacheRequest = request.newBuilder()
            .header("Cache-Control", "public, max-age=300") // 5 minutes
            .build()

        return chain.proceed(cacheRequest)
    }
}

// OkHttp cache setup
val cacheSize = 10 * 1024 * 1024 // 10 MB
val cache = Cache(context.cacheDir, cacheSize.toLong())

val okHttpClient = OkHttpClient.Builder()
    .cache(cache)
    .addNetworkInterceptor(CacheInterceptor())
    .build()
```

---

## Best Practices Checklist

### Do's

1. **Use suspend functions instead of Call&lt;T&gt;**
   ```kotlin
   //  Good
   @GET("users/{id}")
   suspend fun getUser(@Path("id") id: String): User

   //  Avoid
   @GET("users/{id}")
   fun getUser(@Path("id") id: String): Call<User>
   ```

2. **Handle cancellation properly**
   ```kotlin
   //  Good
   try {
       val user = api.getUser(id)
   } catch (e: CancellationException) {
       throw e // Re-throw cancellation
   } catch (e: Exception) {
       // Handle other errors
   }
   ```

3. **Use appropriate dispatcher**
   ```kotlin
   //  Good - Retrofit already uses background thread
   suspend fun getUser(id: String): User {
       return api.getUser(id) // No withContext needed
   }

   //  Good - Only for database operations
   suspend fun getUserFromDb(id: String): User {
       return withContext(Dispatchers.IO) {
           userDao.getUser(id)
       }
   }
   ```

4. **Implement proper timeout configuration**
   ```kotlin
   //  Good
   val okHttpClient = OkHttpClient.Builder()
       .connectTimeout(30, TimeUnit.SECONDS)
       .readTimeout(30, TimeUnit.SECONDS)
       .writeTimeout(30, TimeUnit.SECONDS)
       .build()
   ```

5. **Use structured concurrency for parallel requests**
   ```kotlin
   //  Good
   suspend fun loadData() = coroutineScope {
       val user = async { api.getUser() }
       val posts = async { api.getPosts() }
       Data(user.await(), posts.await())
   }
   ```

6. **Implement proper error handling**
   ```kotlin
   //  Good
   sealed class Result<out T> {
       data class Success<T>(val data: T) : Result<T>()
       data class Error(val exception: Throwable) : Result<Nothing>()
   }
   ```

7. **Cache with Room for offline support**
   ```kotlin
   //  Good
   suspend fun getUser(id: String) = flow {
       emit(userDao.getUser(id)) // Emit cached
       val fresh = api.getUser(id)
       userDao.insert(fresh) // Update cache
   }
   ```

8. **Use Flow for reactive streams**
   ```kotlin
   //  Good
   fun observeUser(id: String): Flow<User> =
       userDao.observeUser(id)
   ```

### Don'ts

1. **Don't use Call&lt;T&gt; with coroutines**
   ```kotlin
   //  Bad
   val call = api.getUser(id)
   call.enqueue(object : Callback<User> { ... })
   ```

2. **Don't ignore cancellation**
   ```kotlin
   //  Bad
   try {
       val user = api.getUser(id)
   } catch (e: Exception) {
       // CancellationException caught here too!
   }
   ```

3. **Don't use GlobalScope**
   ```kotlin
   //  Bad
   GlobalScope.launch {
       val user = api.getUser(id)
   }

   //  Good
   viewModelScope.launch {
       val user = api.getUser(id)
   }
   ```

4. **Don't use runBlocking in production code**
   ```kotlin
   //  Bad
   fun getUser(id: String): User {
       return runBlocking {
           api.getUser(id)
       }
   }
   ```

5. **Don't forget to handle errors**
   ```kotlin
   //  Bad
   suspend fun getUser(id: String): User {
       return api.getUser(id) // What if it fails?
   }

   //  Good
   suspend fun getUser(id: String): Result<User> {
       return try {
           Result.Success(api.getUser(id))
       } catch (e: Exception) {
           Result.Error(e)
       }
   }
   ```

6. **Don't use synchronous OkHttp calls**
   ```kotlin
   //  Bad
   val response = okHttpClient.newCall(request).execute()

   //  Good
   suspend fun makeRequest() {
       api.getUser(id)
   }
   ```

7. **Don't create new Retrofit instance for each request**
   ```kotlin
   //  Bad
   fun getApi(): ApiService {
       return Retrofit.Builder()
           .baseUrl(BASE_URL)
           .build()
           .create(ApiService::class.java)
   }

   //  Good - Singleton
   object RetrofitClient {
       val api: ApiService = Retrofit.Builder()
           .baseUrl(BASE_URL)
           .build()
           .create(ApiService::class.java)
   }
   ```

---

## Complete Android App Example

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

data class User(
    val id: String,
    val name: String,
    val email: String,
    val avatarUrl: String?
)

data class CreateUserRequest(
    val name: String,
    val email: String
)

data class UpdateUserRequest(
    val name: String?,
    val email: String?
)
```

### Repository

```kotlin
class UserRepository(
    private val api: UserApiService,
    private val userDao: UserDao,
    private val dispatcher: CoroutineDispatcher = Dispatchers.IO
) {
    fun observeUsers(): Flow<List<User>> = userDao.observeAllUsers()
        .onStart {
            refreshUsers()
        }

    fun observeUser(userId: String): Flow<User?> = userDao.observeUser(userId)

    suspend fun refreshUsers() = withContext(dispatcher) {
        try {
            val users = api.getUsers(page = 1)
            userDao.insertAllUsers(users)
        } catch (e: Exception) {
            Log.e("UserRepository", "Failed to refresh users", e)
        }
    }

    suspend fun getUser(userId: String, forceRefresh: Boolean = false): Result<User> {
        return withContext(dispatcher) {
            try {
                if (!forceRefresh) {
                    val cached = userDao.getUser(userId)
                    if (cached != null) {
                        return@withContext Result.Success(cached)
                    }
                }

                val user = api.getUser(userId)
                userDao.insertUser(user)
                Result.Success(user)
            } catch (e: Exception) {
                Result.Error(e)
            }
        }
    }

    suspend fun createUser(name: String, email: String): Result<User> {
        return withContext(dispatcher) {
            try {
                val request = CreateUserRequest(name, email)
                val user = api.createUser(request)
                userDao.insertUser(user)
                Result.Success(user)
            } catch (e: Exception) {
                Result.Error(e)
            }
        }
    }

    suspend fun updateUser(userId: String, name: String?, email: String?): Result<User> {
        return withContext(dispatcher) {
            try {
                val request = UpdateUserRequest(name, email)
                val user = api.updateUser(userId, request)
                userDao.insertUser(user)
                Result.Success(user)
            } catch (e: Exception) {
                Result.Error(e)
            }
        }
    }

    suspend fun deleteUser(userId: String): Result<Unit> {
        return withContext(dispatcher) {
            try {
                api.deleteUser(userId)
                userDao.deleteUser(userId)
                Result.Success(Unit)
            } catch (e: Exception) {
                Result.Error(e)
            }
        }
    }
}
```

### ViewModel

```kotlin
class UserListViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    val users: StateFlow<List<User>> = repository.observeUsers()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    init {
        loadUsers()
    }

    fun loadUsers() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            repository.refreshUsers()
            _uiState.value = UiState.Success
        }
    }

    fun createUser(name: String, email: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            when (val result = repository.createUser(name, email)) {
                is Result.Success -> {
                    _uiState.value = UiState.Success
                }
                is Result.Error -> {
                    _uiState.value = UiState.Error(result.exception.message ?: "Unknown error")
                }
                else -> {}
            }
        }
    }

    fun deleteUser(userId: String) {
        viewModelScope.launch {
            when (val result = repository.deleteUser(userId)) {
                is Result.Success -> {
                    // User deleted successfully
                }
                is Result.Error -> {
                    _uiState.value = UiState.Error(result.exception.message ?: "Failed to delete user")
                }
                else -> {}
            }
        }
    }

    sealed class UiState {
        object Loading : UiState()
        object Success : UiState()
        data class Error(val message: String) : UiState()
    }
}
```

### Compose UI

```kotlin
@Composable
fun UserListScreen(
    viewModel: UserListViewModel = viewModel()
) {
    val users by viewModel.users.collectAsState()
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(title = { Text("Users") })
        },
        floatingActionButton = {
            FloatingActionButton(onClick = { /* Show create dialog */ }) {
                Icon(Icons.Default.Add, contentDescription = "Add user")
            }
        }
    ) { padding ->
        when (uiState) {
            is UserListViewModel.UiState.Loading -> {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            }
            is UserListViewModel.UiState.Error -> {
                val error = (uiState as UserListViewModel.UiState.Error).message
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                    Text(text = error, color = MaterialTheme.colorScheme.error)
                    Button(
                        onClick = { viewModel.loadUsers() },
                        modifier = Modifier.padding(top = 16.dp)
                    ) {
                        Text("Retry")
                    }
                }
            }
            is UserListViewModel.UiState.Success -> {
                LazyColumn(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(padding)
                ) {
                    items(users) { user ->
                        UserListItem(
                            user = user,
                            onDelete = { viewModel.deleteUser(user.id) }
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun UserListItem(
    user: User,
    onDelete: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            AsyncImage(
                model = user.avatarUrl,
                contentDescription = "Avatar",
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
            )
            Column(
                modifier = Modifier
                    .weight(1f)
                    .padding(start = 16.dp)
            ) {
                Text(text = user.name, style = MaterialTheme.typography.titleMedium)
                Text(text = user.email, style = MaterialTheme.typography.bodyMedium)
            }
            IconButton(onClick = onDelete) {
                Icon(Icons.Default.Delete, contentDescription = "Delete")
            }
        }
    }
}
```

### Dependency Injection (Hilt)

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            })
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    fun provideUserApiService(retrofit: Retrofit): UserApiService {
        return retrofit.create(UserApiService::class.java)
    }
}

@Module
@InstallIn(SingletonComponent::class)
object RepositoryModule {
    @Provides
    @Singleton
    fun provideUserRepository(
        api: UserApiService,
        userDao: UserDao
    ): UserRepository {
        return UserRepository(api, userDao)
    }
}
```

---

## Common Pitfalls

### 1. Not Re-throwing CancellationException

```kotlin
//  Wrong
try {
    val user = api.getUser(id)
} catch (e: Exception) {
    // CancellationException caught here!
    Log.e("Error", "Failed", e)
}

//  Correct
try {
    val user = api.getUser(id)
} catch (e: CancellationException) {
    throw e // Re-throw cancellation
} catch (e: Exception) {
    Log.e("Error", "Failed", e)
}
```

### 2. Using withContext(Dispatchers.IO) for Retrofit

```kotlin
//  Wrong - Unnecessary dispatcher switch
suspend fun getUser(id: String): User {
    return withContext(Dispatchers.IO) {
        api.getUser(id) // Retrofit already uses background thread
    }
}

//  Correct
suspend fun getUser(id: String): User {
    return api.getUser(id)
}
```

### 3. Not Handling Response Body Null

```kotlin
//  Wrong
val response = api.getUserWithResponse(id)
val user = response.body()!! // Can throw NPE!

//  Correct
val response = api.getUserWithResponse(id)
val user = response.body() ?: throw Exception("Empty response body")
```

### 4. Forgetting to Close Error Body

```kotlin
//  Wrong - Memory leak
val response = api.getUserWithResponse(id)
if (!response.isSuccessful) {
    val error = response.errorBody()?.string()
    // errorBody not closed!
}

//  Correct
val response = api.getUserWithResponse(id)
if (!response.isSuccessful) {
    response.errorBody()?.use { errorBody ->
        val error = errorBody.string()
    }
}
```

### 5. Creating Multiple Retrofit Instances

```kotlin
//  Wrong
class UserRepository {
    private fun getApi(): ApiService {
        return Retrofit.Builder()
            .baseUrl(BASE_URL)
            .build()
            .create(ApiService::class.java)
    }
}

//  Correct - Singleton
object RetrofitClient {
    val api: ApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .build()
            .create(ApiService::class.java)
    }
}
```

### 6. Not Implementing Proper Timeout

```kotlin
//  Wrong - Using default timeouts (10 seconds)
val okHttpClient = OkHttpClient.Builder().build()

//  Correct
val okHttpClient = OkHttpClient.Builder()
    .connectTimeout(30, TimeUnit.SECONDS)
    .readTimeout(30, TimeUnit.SECONDS)
    .writeTimeout(30, TimeUnit.SECONDS)
    .build()
```

### 7. Blocking Main Thread with runBlocking

```kotlin
//  Wrong
fun onCreate() {
    val user = runBlocking {
        api.getUser("123")
    } // Blocks UI thread!
}

//  Correct
fun onCreate() {
    lifecycleScope.launch {
        val user = api.getUser("123")
    }
}
```

---

## Follow-ups

1. **When should you use `Response<T>` vs direct `T` return type in Retrofit?**
   - Use `T` for simple cases where you only need success data
   - Use `Response<T>` when you need headers, status codes, or custom error handling

2. **How does Retrofit handle coroutine cancellation automatically?**
   - Retrofit detects coroutine cancellation via `CancellationException`
   - Automatically cancels the underlying OkHttp call
   - Closes network connections and frees resources

3. **What's the difference between `flowOn()` and `withContext()` for Retrofit calls?**
   - `flowOn()` changes dispatcher for entire Flow upstream
   - `withContext()` changes dispatcher for specific suspend function
   - Retrofit calls don't need either (already on background thread)

4. **How do you implement request coalescing to avoid duplicate concurrent API calls?**
   - Track in-flight requests with `Deferred` in a map
   - Share the same `Deferred` for duplicate requests
   - Clean up map when request completes

5. **What's the best way to implement offline-first architecture with Retrofit + Room?**
   - Cache API responses in Room database
   - Emit cached data first, then fetch from network
   - Use Flow to reactively update UI on database changes

6. **How do you handle token refresh with Retrofit and coroutines?**
   - Use OkHttp interceptor to detect 401 responses
   - Refresh token synchronously with Mutex for thread-safety
   - Retry original request with new token

7. **What are the benefits of using sealed classes for API result handling?**
   - Type-safe error handling with `when` expression
   - Compiler ensures all cases are handled
   - Clear separation between success, error, and loading states

---

## References

- [Retrofit Official Documentation](https://square.github.io/retrofit/)
- [Kotlin Coroutines Guide](https://kotlinlang.org/docs/coroutines-guide.html)
- [OkHttp Documentation](https://square.github.io/okhttp/)
- [Android Developers - Background Work](https://developer.android.com/topic/libraries/architecture/workmanager)
- [Retrofit with Coroutines Codelab](https://developer.android.com/codelabs/kotlin-coroutines)

---

## Related Questions

- [Kotlin Coroutines Flow operators](q-flow-operators--kotlin--medium.md)
- [Coroutine exception handling](q-exception-handling-coroutines--kotlin--medium.md)
- [Testing coroutines](q-testing-coroutines--kotlin--medium.md)
- [Room database with Flow](q-room-flow-integration--kotlin--medium.md)

---

<a name="russian-version"></a>

# Retrofit С Корутинами: Лучшие Практики

[English](#retrofit-with-coroutines-best-practices) | **Русский**

---

## Содержание

- [Обзор](#обзор-ru)
- [Suspend функции в Retrofit](#suspend-функции-в-retrofit)
- [Типы ответов Response&lt;T&gt; vs T](#типы-ответов-responset-vs-t)
- [Стратегии обработки ошибок](#стратегии-обработки-ошибок-ru)
- [Конфигурация таймаутов](#конфигурация-таймаутов)
- [Обработка отмены](#обработка-отмены)
- [Конкурентные запросы](#конкурентные-запросы-ru)
- [Последовательные vs параллельные паттерны](#последовательные-vs-параллельные-паттерны)
- [Call Adapter vs suspend функции](#call-adapter-vs-suspend-функции)
- [Flow типы возврата](#flow-типы-возврата)
- [Полная реализация репозитория](#полная-реализация-репозитория)
- [Кеширование с Room + Flow](#кеширование-с-room--flow)
- [Логика повторных попыток с экспоненциальной задержкой](#логика-повторных-попыток-с-экспоненциальной-задержкой)
- [Тестирование](#тестирование-ru)
- [OkHttp перехватчики](#okhttp-перехватчики)
- [Чек-лист лучших практик](#чек-лист-лучших-практик)
- [Полный пример Android приложения](#полный-пример-android-приложения)
- [Распространенные ошибки](#распространенные-ошибки-ru)

---

<a name="обзор-ru"></a>
## Обзор

Retrofit с Kotlin корутинами предоставляет современный, эффективный способ обработки сетевых операций в Android приложениях. Это руководство охватывает лучшие практики интеграции Retrofit с корутинами.

**Ключевые преимущества:**
- Естественный синтаксис async/await с suspend функциями
- Автоматическая отмена запросов при отмене корутины
- Бесшовная интеграция с Flow для реактивных потоков
- Улучшенная обработка ошибок с try-catch
- Отсутствие callback hell

---

## Suspend Функции В Retrofit

### Современный Retrofit Интерфейс

```kotlin
interface ApiService {
    //  Современный подход: suspend функция
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: String): User

    //  С Response обёрткой для заголовков/статуса
    @GET("users/{id}")
    suspend fun getUserWithResponse(@Path("id") userId: String): Response<User>

    //  Старый подход: Call<T> (не нужен с корутинами)
    @GET("users/{id}")
    fun getUserOld(@Path("id") userId: String): Call<User>

    //  Множественные suspend операции
    @POST("users")
    suspend fun createUser(@Body user: UserRequest): User

    @PUT("users/{id}")
    suspend fun updateUser(@Path("id") id: String, @Body user: UserRequest): User

    @DELETE("users/{id}")
    suspend fun deleteUser(@Path("id") id: String): Unit

    //  Query параметры
    @GET("users")
    suspend fun getUsers(
        @Query("page") page: Int,
        @Query("limit") limit: Int
    ): List<User>

    //  Заголовки
    @GET("profile")
    suspend fun getProfile(@Header("Authorization") token: String): Profile
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
        // Не нужен CallAdapter с suspend функциями
        .build()

    val apiService: ApiService = retrofit.create(ApiService::class.java)
}
```

---

<a name="типы-ответов-responset-vs-t"></a>
## Типы Ответов: Response&lt;T&gt; Vs T

### Когда Использовать Прямой Тип T

Используйте прямой тип `T`, когда вас интересует только случай успеха:

```kotlin
interface ApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: String): User
}

// Использование
suspend fun loadUser(userId: String): Result<User> {
    return try {
        val user = apiService.getUser(userId)
        Result.success(user)
    } catch (e: Exception) {
        Result.failure(e)
    }
}
```

**Плюсы:**
- Более чистый API
- Меньше шаблонного кода
- Автоматическая ошибка при статусе не 2xx

**Минусы:**
- Нет доступа к заголовкам
- Нет доступа к коду статуса
- Выбрасывает исключение при ошибке

### Когда Использовать Response&lt;T&gt;

Используйте `Response<T>`, когда нужны заголовки, коды статуса или пользовательская обработка ошибок:

```kotlin
interface ApiService {
    @GET("users/{id}")
    suspend fun getUserWithResponse(@Path("id") userId: String): Response<User>
}

// Использование
suspend fun loadUserWithDetails(userId: String): UserResult {
    val response = apiService.getUserWithResponse(userId)

    return when {
        response.isSuccessful -> {
            val user = response.body()!!
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
            val errorBody = response.errorBody()?.string()
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

---

<a name="стратегии-обработки-ошибок-ru"></a>
## Стратегии Обработки Ошибок

### Стратегия 1: Try-Catch (Простая)

```kotlin
class UserRepository(private val api: ApiService) {
    suspend fun getUser(userId: String): User? {
        return try {
            api.getUser(userId)
        } catch (e: IOException) {
            // Ошибка сети
            Log.e("UserRepository", "Ошибка сети", e)
            null
        } catch (e: HttpException) {
            // HTTP ошибка (4xx, 5xx)
            Log.e("UserRepository", "HTTP ошибка: ${e.code()}", e)
            null
        } catch (e: Exception) {
            // Другие ошибки
            Log.e("UserRepository", "Неизвестная ошибка", e)
            null
        }
    }
}
```

### Стратегия 2: Result&lt;T&gt; Sealed Class

```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val exception: Throwable) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

class UserRepository(private val api: ApiService) {
    suspend fun getUser(userId: String): Result<User> {
        return try {
            val user = api.getUser(userId)
            Result.Success(user)
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
}

// Использование в ViewModel
class UserViewModel(private val repository: UserRepository) : ViewModel() {
    private val _userState = MutableStateFlow<Result<User>>(Result.Loading)
    val userState: StateFlow<Result<User>> = _userState.asStateFlow()

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _userState.value = Result.Loading
            _userState.value = repository.getUser(userId)
        }
    }
}
```

### Стратегия 3: NetworkResponse&lt;T, E&gt; (Продвинутая)

```kotlin
sealed class NetworkResponse<out T, out E> {
    data class Success<T>(val data: T) : NetworkResponse<T, Nothing>()
    data class ApiError<E>(val body: E, val code: Int) : NetworkResponse<Nothing, E>()
    data class NetworkError(val error: IOException) : NetworkResponse<Nothing, Nothing>()
    data class UnknownError(val error: Throwable) : NetworkResponse<Nothing, Nothing>()
}

// Модели ответов с ошибками
data class ApiErrorResponse(
    val message: String,
    val code: String?,
    val details: Map<String, String>?
)

// Функция-расширение для оборачивания API вызовов
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
                NetworkResponse.UnknownError(NullPointerException("Тело ответа null"))
            }
        } else {
            val errorBody = response.errorBody()?.string()
            val errorResponse = try {
                Gson().fromJson(errorBody, errorClass)
            } catch (e: Exception) {
                null
            }
            if (errorResponse != null) {
                NetworkResponse.ApiError(errorResponse, response.code())
            } else {
                NetworkResponse.UnknownError(Exception("Неизвестная API ошибка"))
            }
        }
    } catch (e: IOException) {
        NetworkResponse.NetworkError(e)
    } catch (e: Exception) {
        NetworkResponse.UnknownError(e)
    }
}

// Использование
class UserRepository(private val api: ApiService) {
    suspend fun getUser(userId: String): NetworkResponse<User, ApiErrorResponse> {
        return safeApiCall(ApiErrorResponse::class.java) {
            api.getUserWithResponse(userId)
        }
    }
}
```

---

<a name="конкурентные-запросы-ru"></a>
## Конкурентные Запросы

### Параллельные Запросы С async/await

```kotlin
class UserRepository(private val api: ApiService) {
    // Выполнение запросов параллельно
    suspend fun getUserWithPosts(userId: String): Pair<User, List<Post>> = coroutineScope {
        val userDeferred = async { api.getUser(userId) }
        val postsDeferred = async { api.getUserPosts(userId) }

        // Ожидание обоих результатов
        val user = userDeferred.await()
        val posts = postsDeferred.await()

        user to posts
    }

    // Множественные параллельные запросы
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
```

---

<a name="тестирование-ru"></a>
## Тестирование

### Настройка MockWebServer

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
        repository = UserRepository(apiService)
    }

    @After
    fun teardown() {
        mockWebServer.shutdown()
    }

    @Test
    fun `getUser возвращает пользователя при успехе`() = runTest {
        // Подготовка
        val mockResponse = """
            {
                "id": "123",
                "name": "Иван Иванов",
                "email": "ivan@example.com"
            }
        """.trimIndent()

        mockWebServer.enqueue(
            MockResponse()
                .setResponseCode(200)
                .setBody(mockResponse)
        )

        // Действие
        val result = repository.getUser("123")

        // Проверка
        assertTrue(result is Result.Success)
        val user = (result as Result.Success).data
        assertEquals("123", user.id)
        assertEquals("Иван Иванов", user.name)
    }

    @Test
    fun `getUser возвращает ошибку при 404`() = runTest {
        // Подготовка
        mockWebServer.enqueue(
            MockResponse()
                .setResponseCode(404)
                .setBody("{\"error\": \"Пользователь не найден\"}")
        )

        // Действие
        val result = repository.getUser("999")

        // Проверка
        assertTrue(result is Result.Error)
    }
}
```

---

<a name="распространенные-ошибки-ru"></a>
## Распространенные Ошибки

### 1. Не Повторное Выбрасывание CancellationException

```kotlin
//  Неправильно
try {
    val user = api.getUser(id)
} catch (e: Exception) {
    // CancellationException поймано здесь!
    Log.e("Error", "Ошибка", e)
}

//  Правильно
try {
    val user = api.getUser(id)
} catch (e: CancellationException) {
    throw e // Повторно выбросить отмену
} catch (e: Exception) {
    Log.e("Error", "Ошибка", e)
}
```

### 2. Использование withContext(Dispatchers.IO) Для Retrofit

```kotlin
//  Неправильно - Ненужное переключение диспетчера
suspend fun getUser(id: String): User {
    return withContext(Dispatchers.IO) {
        api.getUser(id) // Retrofit уже использует фоновый поток
    }
}

//  Правильно
suspend fun getUser(id: String): User {
    return api.getUser(id)
}
```

### 3. Не Обработка Null Тела Ответа

```kotlin
//  Неправильно
val response = api.getUserWithResponse(id)
val user = response.body()!! // Может выбросить NPE!

//  Правильно
val response = api.getUserWithResponse(id)
val user = response.body() ?: throw Exception("Пустое тело ответа")
```

### 4. Забывание Закрыть Тело Ошибки

```kotlin
//  Неправильно - Утечка памяти
val response = api.getUserWithResponse(id)
if (!response.isSuccessful) {
    val error = response.errorBody()?.string()
    // errorBody не закрыто!
}

//  Правильно
val response = api.getUserWithResponse(id)
if (!response.isSuccessful) {
    response.errorBody()?.use { errorBody ->
        val error = errorBody.string()
    }
}
```

### 5. Создание Множественных Экземпляров Retrofit

```kotlin
//  Неправильно
class UserRepository {
    private fun getApi(): ApiService {
        return Retrofit.Builder()
            .baseUrl(BASE_URL)
            .build()
            .create(ApiService::class.java)
    }
}

//  Правильно - Singleton
object RetrofitClient {
    val api: ApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .build()
            .create(ApiService::class.java)
    }
}
```

### 6. Не Реализация Правильного Таймаута

```kotlin
//  Неправильно - Использование таймаутов по умолчанию (10 секунд)
val okHttpClient = OkHttpClient.Builder().build()

//  Правильно
val okHttpClient = OkHttpClient.Builder()
    .connectTimeout(30, TimeUnit.SECONDS)
    .readTimeout(30, TimeUnit.SECONDS)
    .writeTimeout(30, TimeUnit.SECONDS)
    .build()
```

### 7. Блокирование Главного Потока С runBlocking

```kotlin
//  Неправильно
fun onCreate() {
    val user = runBlocking {
        api.getUser("123")
    } // Блокирует UI поток!
}

//  Правильно
fun onCreate() {
    lifecycleScope.launch {
        val user = api.getUser("123")
    }
}
```

---

## Чек-лист Лучших Практик

### Делать:

1. **Используйте suspend функции вместо Call&lt;T&gt;**
   ```kotlin
   //  Хорошо
   @GET("users/{id}")
   suspend fun getUser(@Path("id") id: String): User

   //  Избегайте
   @GET("users/{id}")
   fun getUser(@Path("id") id: String): Call<User>
   ```

2. **Правильно обрабатывайте отмену**
   ```kotlin
   //  Хорошо
   try {
       val user = api.getUser(id)
   } catch (e: CancellationException) {
       throw e // Повторно выбросить отмену
   } catch (e: Exception) {
       // Обработать другие ошибки
   }
   ```

3. **Используйте подходящий диспетчер**
   ```kotlin
   //  Хорошо - Retrofit уже использует фоновый поток
   suspend fun getUser(id: String): User {
       return api.getUser(id) // Не нужен withContext
   }

   //  Хорошо - Только для операций с базой данных
   suspend fun getUserFromDb(id: String): User {
       return withContext(Dispatchers.IO) {
           userDao.getUser(id)
       }
   }
   ```

4. **Реализуйте правильную конфигурацию таймаута**
   ```kotlin
   //  Хорошо
   val okHttpClient = OkHttpClient.Builder()
       .connectTimeout(30, TimeUnit.SECONDS)
       .readTimeout(30, TimeUnit.SECONDS)
       .writeTimeout(30, TimeUnit.SECONDS)
       .build()
   ```

5. **Используйте структурированный параллелизм для параллельных запросов**
   ```kotlin
   //  Хорошо
   suspend fun loadData() = coroutineScope {
       val user = async { api.getUser() }
       val posts = async { api.getPosts() }
       Data(user.await(), posts.await())
   }
   ```

6. **Реализуйте правильную обработку ошибок**
   ```kotlin
   //  Хорошо
   sealed class Result<out T> {
       data class Success<T>(val data: T) : Result<T>()
       data class Error(val exception: Throwable) : Result<Nothing>()
   }
   ```

7. **Кешируйте с Room для оффлайн поддержки**
   ```kotlin
   //  Хорошо
   suspend fun getUser(id: String) = flow {
       emit(userDao.getUser(id)) // Отправить закешированное
       val fresh = api.getUser(id)
       userDao.insert(fresh) // Обновить кеш
   }
   ```

8. **Используйте Flow для реактивных потоков**
   ```kotlin
   //  Хорошо
   fun observeUser(id: String): Flow<User> =
       userDao.observeUser(id)
   ```

### Не Делать:

1. **Не используйте Call&lt;T&gt; с корутинами**
   ```kotlin
   //  Плохо
   val call = api.getUser(id)
   call.enqueue(object : Callback<User> { ... })
   ```

2. **Не игнорируйте отмену**
   ```kotlin
   //  Плохо
   try {
       val user = api.getUser(id)
   } catch (e: Exception) {
       // CancellationException тоже поймано здесь!
   }
   ```

3. **Не используйте GlobalScope**
   ```kotlin
   //  Плохо
   GlobalScope.launch {
       val user = api.getUser(id)
   }

   //  Хорошо
   viewModelScope.launch {
       val user = api.getUser(id)
   }
   ```

4. **Не используйте runBlocking в production коде**
   ```kotlin
   //  Плохо
   fun getUser(id: String): User {
       return runBlocking {
           api.getUser(id)
       }
   }
   ```

5. **Не забывайте обрабатывать ошибки**
   ```kotlin
   //  Плохо
   suspend fun getUser(id: String): User {
       return api.getUser(id) // Что если ошибка?
   }

   //  Хорошо
   suspend fun getUser(id: String): Result<User> {
       return try {
           Result.Success(api.getUser(id))
       } catch (e: Exception) {
           Result.Error(e)
       }
   }
   ```

---

**Краткое резюме:**

Retrofit с Kotlin корутинами предоставляет мощный, современный способ обработки сетевых операций. Используйте suspend функции вместо Call&lt;T&gt;, правильно обрабатывайте ошибки с sealed классами, реализуйте кеширование с Room для оффлайн поддержки, и всегда помните о правильной обработке отмены корутин. Структурированный параллелизм с async/await позволяет эффективно выполнять параллельные запросы. Для лучших результатов используйте OkHttp interceptors для логирования, аутентификации и обновления токенов.

---

**Конец документа**
