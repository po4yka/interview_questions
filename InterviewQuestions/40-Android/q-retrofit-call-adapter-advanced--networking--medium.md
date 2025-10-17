---
id: 20251012-12271183
title: "Retrofit Call Adapter Advanced / Продвинутый CallAdapter для Retrofit"
topic: networking
difficulty: medium
status: draft
created: 2025-10-15
tags: [retrofit, call-adapter, result, error-handling, sealed-classes, difficulty/medium]
---

# Retrofit CallAdapter Advanced / Продвинутый CallAdapter для Retrofit

**English**: Implement custom Retrofit CallAdapter for Result<T> type. Handle different response types and errors uniformly with sealed classes.

## Answer (EN)

**Retrofit CallAdapter** is a powerful abstraction that allows you to transform API responses into custom types. By creating a custom CallAdapter, you can standardize error handling, wrap responses in Result types, and integrate seamlessly with Kotlin Coroutines and Flow.

### Why Custom CallAdapter?

Without a custom CallAdapter, error handling becomes repetitive:

```kotlin
// BAD: Repetitive error handling
suspend fun getUser(id: String): User? {
    return try {
        val response = apiService.getUser(id)
        if (response.isSuccessful) {
            response.body()
        } else {
            // Handle error
            null
        }
    } catch (e: IOException) {
        // Handle network error
        null
    } catch (e: Exception) {
        // Handle other errors
        null
    }
}

// This pattern repeats for every API call!
```

With a custom CallAdapter, error handling is centralized:

```kotlin
// GOOD: Clean, centralized error handling
suspend fun getUser(id: String): Result<User> {
    return apiService.getUser(id) // Returns Result<User> automatically
}
```

### Result Type Design

First, let's design a comprehensive Result type using sealed classes:

```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()

    sealed class Error : Result<Nothing>() {
        data class HttpError(
            val code: Int,
            val message: String,
            val body: String?
        ) : Error()

        data class NetworkError(
            val exception: IOException
        ) : Error()

        data class SerializationError(
            val exception: Exception
        ) : Error()

        data class UnknownError(
            val exception: Throwable
        ) : Error()
    }

    // Convenience properties
    val isSuccess: Boolean get() = this is Success
    val isError: Boolean get() = this is Error

    fun getOrNull(): T? = when (this) {
        is Success -> data
        is Error -> null
    }

    fun exceptionOrNull(): Throwable? = when (this) {
        is Success -> null
        is Error.HttpError -> IOException("HTTP $code: $message")
        is Error.NetworkError -> exception
        is Error.SerializationError -> exception
        is Error.UnknownError -> exception
    }

    inline fun onSuccess(action: (T) -> Unit): Result<T> {
        if (this is Success) action(data)
        return this
    }

    inline fun onError(action: (Error) -> Unit): Result<T> {
        if (this is Error) action(this)
        return this
    }

    inline fun <R> map(transform: (T) -> R): Result<R> {
        return when (this) {
            is Success -> Success(transform(data))
            is Error -> this
        }
    }

    inline fun <R> flatMap(transform: (T) -> Result<R>): Result<R> {
        return when (this) {
            is Success -> transform(data)
            is Error -> this
        }
    }
}

// Extension for easy error message retrieval
fun Result.Error.toUserMessage(): String {
    return when (this) {
        is Result.Error.HttpError -> when (code) {
            400 -> "Invalid request"
            401 -> "Authentication required"
            403 -> "Access denied"
            404 -> "Resource not found"
            408 -> "Request timeout"
            429 -> "Too many requests, please try again later"
            in 500..599 -> "Server error, please try again"
            else -> message
        }
        is Result.Error.NetworkError -> "No internet connection"
        is Result.Error.SerializationError -> "Data parsing error"
        is Result.Error.UnknownError -> "Unexpected error occurred"
    }
}
```

### CallAdapter Implementation

Now let's implement the custom CallAdapter:

```kotlin
import retrofit2.Call
import retrofit2.CallAdapter
import retrofit2.Retrofit
import java.lang.reflect.ParameterizedType
import java.lang.reflect.Type

class ResultCallAdapterFactory : CallAdapter.Factory() {

    override fun get(
        returnType: Type,
        annotations: Array<out Annotation>,
        retrofit: Retrofit
    ): CallAdapter<*, *>? {
        // Check if the return type is Call<Result<T>>
        if (getRawType(returnType) != Call::class.java) {
            return null
        }

        // Get the response type inside Call<...>
        val callType = getParameterUpperBound(0, returnType as ParameterizedType)

        // Check if it's Result<T>
        if (getRawType(callType) != Result::class.java) {
            return null
        }

        // Get the success type T from Result<T>
        val resultType = getParameterUpperBound(0, callType as ParameterizedType)

        return ResultCallAdapter<Any>(resultType)
    }
}

private class ResultCallAdapter<T>(
    private val successType: Type
) : CallAdapter<T, Call<Result<T>>> {

    override fun responseType(): Type = successType

    override fun adapt(call: Call<T>): Call<Result<T>> {
        return ResultCall(call)
    }
}

private class ResultCall<T>(
    private val delegate: Call<T>
) : Call<Result<T>> {

    override fun enqueue(callback: Callback<Result<T>>) {
        delegate.enqueue(object : Callback<T> {
            override fun onResponse(call: Call<T>, response: Response<T>) {
                val result = response.toResult()
                callback.onResponse(this@ResultCall, Response.success(result))
            }

            override fun onFailure(call: Call<T>, t: Throwable) {
                val result = when (t) {
                    is IOException -> Result.Error.NetworkError(t)
                    else -> Result.Error.UnknownError(t)
                }
                callback.onResponse(this@ResultCall, Response.success(result))
            }
        })
    }

    override fun execute(): Response<Result<T>> {
        return try {
            val response = delegate.execute()
            Response.success(response.toResult())
        } catch (e: IOException) {
            Response.success(Result.Error.NetworkError(e))
        } catch (e: Exception) {
            Response.success(Result.Error.UnknownError(e))
        }
    }

    override fun isExecuted() = delegate.isExecuted
    override fun cancel() = delegate.cancel()
    override fun isCanceled() = delegate.isCanceled
    override fun request() = delegate.request()
    override fun timeout() = delegate.timeout()
    override fun clone() = ResultCall(delegate.clone())
}

private fun <T> Response<T>.toResult(): Result<T> {
    return if (isSuccessful) {
        val body = body()
        if (body != null) {
            Result.Success(body)
        } else {
            Result.Error.UnknownError(NullPointerException("Response body is null"))
        }
    } else {
        Result.Error.HttpError(
            code = code(),
            message = message(),
            body = errorBody()?.string()
        )
    }
}
```

### Suspend Function Support

For Kotlin coroutines, we need a different approach:

```kotlin
class ResultCallAdapterFactory : CallAdapter.Factory() {

    override fun get(
        returnType: Type,
        annotations: Array<out Annotation>,
        retrofit: Retrofit
    ): CallAdapter<*, *>? {
        // Check if return type is suspend function
        val isSuspend = annotations.any { it is Suspend }

        if (isSuspend) {
            // For suspend functions, return type is already unwrapped from Call
            // Check if it's Result<T>
            if (getRawType(returnType) != Result::class.java) {
                return null
            }

            val resultType = getParameterUpperBound(0, returnType as ParameterizedType)
            return SuspendResultCallAdapter<Any>(resultType)
        }

        // Standard Call<Result<T>> handling
        if (getRawType(returnType) != Call::class.java) {
            return null
        }

        val callType = getParameterUpperBound(0, returnType as ParameterizedType)
        if (getRawType(callType) != Result::class.java) {
            return null
        }

        val resultType = getParameterUpperBound(0, callType as ParameterizedType)
        return ResultCallAdapter<Any>(resultType)
    }
}

private class SuspendResultCallAdapter<T>(
    private val successType: Type
) : CallAdapter<T, Any> {

    override fun responseType(): Type = successType

    override fun adapt(call: Call<T>): Any {
        return suspend {
            try {
                val response = call.awaitResponse()
                response.toResult()
            } catch (e: IOException) {
                Result.Error.NetworkError(e)
            } catch (e: Exception) {
                Result.Error.UnknownError(e)
            }
        }
    }
}

// Extension to await response in suspend function
suspend fun <T> Call<T>.awaitResponse(): Response<T> {
    return suspendCancellableCoroutine { continuation ->
        continuation.invokeOnCancellation {
            cancel()
        }

        enqueue(object : Callback<T> {
            override fun onResponse(call: Call<T>, response: Response<T>) {
                continuation.resume(response)
            }

            override fun onFailure(call: Call<T>, t: Throwable) {
                continuation.resumeWithException(t)
            }
        })
    }
}

@Target(AnnotationTarget.FUNCTION)
@Retention(AnnotationRetention.RUNTIME)
annotation class Suspend
```

### Flow Support

For reactive streams with Flow:

```kotlin
class FlowResultCallAdapter<T>(
    private val successType: Type
) : CallAdapter<T, Flow<Result<T>>> {

    override fun responseType(): Type = successType

    override fun adapt(call: Call<T>): Flow<Result<T>> = flow {
        try {
            val response = call.awaitResponse()
            emit(response.toResult())
        } catch (e: IOException) {
            emit(Result.Error.NetworkError(e))
        } catch (e: Exception) {
            emit(Result.Error.UnknownError(e))
        }
    }
}

// In factory
class ResultCallAdapterFactory : CallAdapter.Factory() {
    override fun get(
        returnType: Type,
        annotations: Array<out Annotation>,
        retrofit: Retrofit
    ): CallAdapter<*, *>? {
        val rawType = getRawType(returnType)

        // Handle Flow<Result<T>>
        if (rawType == Flow::class.java) {
            val flowType = getParameterUpperBound(0, returnType as ParameterizedType)
            if (getRawType(flowType) != Result::class.java) {
                return null
            }
            val resultType = getParameterUpperBound(0, flowType as ParameterizedType)
            return FlowResultCallAdapter<Any>(resultType)
        }

        // ... other cases
    }
}
```

### Complete Retrofit Setup

```kotlin
import com.google.gson.Gson
import com.google.gson.GsonBuilder
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.*

class ApiClientBuilder(
    private val baseUrl: String,
    private val okHttpClient: OkHttpClient
) {

    private val gson: Gson = GsonBuilder()
        .setFieldNamingPolicy(FieldNamingPolicy.LOWER_CASE_WITH_UNDERSCORES)
        .create()

    fun build(): ApiService {
        return Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create(gson))
            .addCallAdapterFactory(ResultCallAdapterFactory())
            .build()
            .create(ApiService::class.java)
    }
}

// API Service with Result types
interface ApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: String): Result<User>

    @GET("users/{id}/posts")
    suspend fun getUserPosts(
        @Path("id") userId: String,
        @Query("page") page: Int = 1
    ): Result<List<Post>>

    @POST("posts")
    suspend fun createPost(@Body post: CreatePostRequest): Result<Post>

    @PUT("posts/{id}")
    suspend fun updatePost(
        @Path("id") postId: String,
        @Body post: UpdatePostRequest
    ): Result<Post>

    @DELETE("posts/{id}")
    suspend fun deletePost(@Path("id") postId: String): Result<Unit>

    @GET("posts/search")
    suspend fun searchPosts(@Query("q") query: String): Result<SearchResponse>

    // Flow example for streaming updates
    @GET("users/{id}/feed")
    fun getUserFeed(@Path("id") userId: String): Flow<Result<List<Post>>>
}

// Data models
data class User(
    val id: String,
    val name: String,
    val email: String,
    val avatar: String?
)

data class Post(
    val id: String,
    val userId: String,
    val title: String,
    val content: String,
    val createdAt: Long
)

data class CreatePostRequest(
    val title: String,
    val content: String
)

data class UpdatePostRequest(
    val title: String?,
    val content: String?
)

data class SearchResponse(
    val results: List<Post>,
    val totalCount: Int,
    val hasMore: Boolean
)
```

### Repository Layer Integration

```kotlin
class UserRepository(
    private val apiService: ApiService,
    private val userDao: UserDao,
    private val dispatcher: CoroutineDispatcher = Dispatchers.IO
) {

    // Simple case: Direct pass-through
    suspend fun getUser(userId: String): Result<User> {
        return withContext(dispatcher) {
            apiService.getUser(userId)
        }
    }

    // With caching
    suspend fun getUserWithCache(userId: String): Result<User> {
        return withContext(dispatcher) {
            val result = apiService.getUser(userId)

            result.onSuccess { user ->
                userDao.insertUser(user)
            }

            // If API fails, try cache
            if (result is Result.Error) {
                val cachedUser = userDao.getUserById(userId)
                if (cachedUser != null) {
                    return@withContext Result.Success(cachedUser)
                }
            }

            result
        }
    }

    // With transformation
    suspend fun getUserProfile(userId: String): Result<UserProfile> {
        return withContext(dispatcher) {
            apiService.getUser(userId).map { user ->
                UserProfile(
                    user = user,
                    postCount = getPostCount(userId)
                )
            }
        }
    }

    // With flatMap for dependent calls
    suspend fun getUserWithLatestPost(userId: String): Result<UserWithPost> {
        return withContext(dispatcher) {
            apiService.getUser(userId).flatMap { user ->
                apiService.getUserPosts(userId, page = 1).map { posts ->
                    UserWithPost(user, posts.firstOrNull())
                }
            }
        }
    }

    // Handling multiple results
    suspend fun getUserDashboard(userId: String): Result<Dashboard> {
        return withContext(dispatcher) {
            val userResult = apiService.getUser(userId)
            val postsResult = apiService.getUserPosts(userId)

            // Combine results
            when {
                userResult is Result.Success && postsResult is Result.Success -> {
                    Result.Success(
                        Dashboard(
                            user = userResult.data,
                            posts = postsResult.data
                        )
                    )
                }
                userResult is Result.Error -> userResult
                postsResult is Result.Error -> postsResult
                else -> Result.Error.UnknownError(IllegalStateException("Unexpected state"))
            }
        }
    }

    // Stream with Flow
    fun observeUserFeed(userId: String): Flow<Result<List<Post>>> {
        return apiService.getUserFeed(userId)
            .onEach { result ->
                result.onSuccess { posts ->
                    // Cache posts
                    posts.forEach { post ->
                        postDao.insertPost(post)
                    }
                }
            }
    }
}

data class UserProfile(
    val user: User,
    val postCount: Int
)

data class UserWithPost(
    val user: User,
    val latestPost: Post?
)

data class Dashboard(
    val user: User,
    val posts: List<Post>
)
```

### ViewModel Layer

```kotlin
class UserViewModel(
    private val userRepository: UserRepository,
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val userId: String = savedStateHandle.get<String>("userId")
        ?: throw IllegalArgumentException("userId required")

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    sealed class UiState {
        object Loading : UiState()
        data class Success(val user: User) : UiState()
        data class Error(val message: String) : UiState()
    }

    init {
        loadUser()
    }

    fun loadUser() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            val result = userRepository.getUserWithCache(userId)

            _uiState.value = result.fold(
                onSuccess = { user -> UiState.Success(user) },
                onError = { error -> UiState.Error(error.toUserMessage()) }
            )
        }
    }

    fun retry() {
        loadUser()
    }
}

// Extension for convenient fold
inline fun <T> Result<T>.fold(
    onSuccess: (T) -> Unit,
    onError: (Result.Error) -> Unit
) {
    when (this) {
        is Result.Success -> onSuccess(data)
        is Result.Error -> onError(this)
    }
}
```

### UI Layer with Compose

```kotlin
@Composable
fun UserScreen(
    viewModel: UserViewModel = viewModel(),
    onNavigateBack: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("User Profile") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, "Back")
                    }
                }
            )
        }
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            when (val state = uiState) {
                is UserViewModel.UiState.Loading -> {
                    CircularProgressIndicator(
                        modifier = Modifier.align(Alignment.Center)
                    )
                }

                is UserViewModel.UiState.Success -> {
                    UserContent(user = state.user)
                }

                is UserViewModel.UiState.Error -> {
                    ErrorContent(
                        message = state.message,
                        onRetry = { viewModel.retry() }
                    )
                }
            }
        }
    }
}

@Composable
private fun UserContent(user: User) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        AsyncImage(
            model = user.avatar,
            contentDescription = null,
            modifier = Modifier
                .size(120.dp)
                .clip(CircleShape)
        )

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = user.name,
            style = MaterialTheme.typography.headlineMedium
        )

        Text(
            text = user.email,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

@Composable
private fun ErrorContent(
    message: String,
    onRetry: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = Icons.Default.Error,
            contentDescription = null,
            modifier = Modifier.size(64.dp),
            tint = MaterialTheme.colorScheme.error
        )

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = message,
            style = MaterialTheme.typography.bodyLarge,
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(16.dp))

        Button(onClick = onRetry) {
            Text("Retry")
        }
    }
}
```

### Testing

```kotlin
class ResultCallAdapterTest {

    private lateinit var mockWebServer: MockWebServer
    private lateinit var apiService: ApiService

    @Before
    fun setup() {
        mockWebServer = MockWebServer()
        mockWebServer.start()

        val okHttpClient = OkHttpClient.Builder()
            .build()

        apiService = Retrofit.Builder()
            .baseUrl(mockWebServer.url("/"))
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .addCallAdapterFactory(ResultCallAdapterFactory())
            .build()
            .create(ApiService::class.java)
    }

    @After
    fun teardown() {
        mockWebServer.shutdown()
    }

    @Test
    fun `success response returns Success result`() = runBlocking {
        // Given
        val user = User("1", "John Doe", "john@example.com", null)
        val json = Gson().toJson(user)
        mockWebServer.enqueue(
            MockResponse()
                .setResponseCode(200)
                .setBody(json)
        )

        // When
        val result = apiService.getUser("1")

        // Then
        assertTrue(result is Result.Success)
        assertEquals(user.name, (result as Result.Success).data.name)
    }

    @Test
    fun `404 response returns HttpError`() = runBlocking {
        // Given
        mockWebServer.enqueue(
            MockResponse()
                .setResponseCode(404)
                .setBody("Not found")
        )

        // When
        val result = apiService.getUser("999")

        // Then
        assertTrue(result is Result.Error.HttpError)
        assertEquals(404, (result as Result.Error.HttpError).code)
    }

    @Test
    fun `network error returns NetworkError`() = runBlocking {
        // Given
        mockWebServer.shutdown() // Force network error

        // When
        val result = apiService.getUser("1")

        // Then
        assertTrue(result is Result.Error.NetworkError)
    }
}
```

### Best Practices

1. **Use Sealed Classes**: Type-safe error handling with exhaustive when expressions

2. **Centralize Error Mapping**: Convert all errors in CallAdapter, not in repositories

3. **Provide User-Friendly Messages**: Map technical errors to user-friendly text

4. **Support Multiple Return Types**: Handle suspend, Call<T>, and Flow<T>

5. **Keep Repository Clean**: Let CallAdapter handle low-level errors

6. **Cache on Errors**: Fallback to cache when API fails

7. **Test Thoroughly**: Test all error scenarios

8. **Document Error Types**: Clear documentation of what each error means

9. **Avoid Throwing Exceptions**: Return Result.Error instead

10. **Handle Null Bodies**: Treat null response bodies as errors

### Common Pitfalls

1. **Not Handling All Error Types**:

    ```kotlin
    // BAD: Only handles HTTP errors
    when (result) {
        is Result.Success -> handleSuccess()
        is Result.Error.HttpError -> handleError()
        // Missing other error types!
    }

    // GOOD: Exhaustive handling
    when (result) {
        is Result.Success -> handleSuccess()
        is Result.Error.HttpError -> handleHttpError()
        is Result.Error.NetworkError -> handleNetworkError()
        is Result.Error.SerializationError -> handleSerializationError()
        is Result.Error.UnknownError -> handleUnknownError()
    }
    ```

2. **Losing Type Information**: Erasing type with Result<Any>

3. **Throwing in CallAdapter**: Should return Result.Error instead

4. **Not Closing Response Bodies**: Memory leaks

5. **Ignoring Cancellation**: Not handling coroutine cancellation

6. **Incorrect Type Checking**: Wrong reflection logic in factory

7. **No Retrofit Registration**: Forgetting to add factory to Retrofit

### Performance Considerations

1. **Reflection Overhead**: Minimize reflection in CallAdapter.Factory

2. **Object Allocation**: Reuse Result instances where possible

3. **Error Body Reading**: Read error body efficiently, don't convert large bodies

4. **Coroutine Dispatchers**: Use appropriate dispatcher for IO operations

### Summary

Custom Retrofit CallAdapter provides:

-   **Unified Error Handling**: Single place for all error conversion
-   **Type Safety**: Sealed classes for exhaustive error handling
-   **Clean Code**: Repositories don't need try-catch everywhere
-   **Testability**: Easy to test with MockWebServer
-   **Flexibility**: Support for Call, suspend, and Flow
-   **User Experience**: Convert technical errors to user-friendly messages
-   **Maintainability**: Centralized error logic

Master CallAdapter to build robust, maintainable Android network layers.

---

## Ответ (RU)

**Retrofit CallAdapter** - мощная абстракция, позволяющая трансформировать API-ответы в пользовательские типы. Создав кастомный CallAdapter, можно стандартизировать обработку ошибок, обернуть ответы в Result типы и бесшовно интегрироваться с Kotlin Coroutines и Flow.

### Зачем нужен кастомный CallAdapter?

Без кастомного CallAdapter обработка ошибок становится повторяющейся:

```kotlin
// ПЛОХО: Повторяющаяся обработка ошибок
suspend fun getUser(id: String): User? {
    return try {
        val response = apiService.getUser(id)
        if (response.isSuccessful) {
            response.body()
        } else {
            null
        }
    } catch (e: IOException) {
        null
    }
}
// Этот паттерн повторяется для каждого API вызова!
```

С кастомным CallAdapter обработка ошибок централизована:

```kotlin
// ХОРОШО: Чистая, централизованная обработка
suspend fun getUser(id: String): Result<User> {
    return apiService.getUser(id)
}
```

### Дизайн Result типа

```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()

    sealed class Error : Result<Nothing>() {
        data class HttpError(
            val code: Int,
            val message: String,
            val body: String?
        ) : Error()

        data class NetworkError(
            val exception: IOException
        ) : Error()

        data class SerializationError(
            val exception: Exception
        ) : Error()

        data class UnknownError(
            val exception: Throwable
        ) : Error()
    }

    val isSuccess: Boolean get() = this is Success
    val isError: Boolean get() = this is Error

    inline fun onSuccess(action: (T) -> Unit): Result<T> {
        if (this is Success) action(data)
        return this
    }

    inline fun onError(action: (Error) -> Unit): Result<T> {
        if (this is Error) action(this)
        return this
    }

    inline fun <R> map(transform: (T) -> R): Result<R> {
        return when (this) {
            is Success -> Success(transform(data))
            is Error -> this
        }
    }
}

fun Result.Error.toUserMessage(): String {
    return when (this) {
        is Result.Error.HttpError -> when (code) {
            400 -> "Неверный запрос"
            401 -> "Требуется аутентификация"
            403 -> "Доступ запрещён"
            404 -> "Ресурс не найден"
            in 500..599 -> "Ошибка сервера"
            else -> message
        }
        is Result.Error.NetworkError -> "Нет интернета"
        is Result.Error.SerializationError -> "Ошибка парсинга"
        is Result.Error.UnknownError -> "Неожиданная ошибка"
    }
}
```

### Реализация CallAdapter

```kotlin
class ResultCallAdapterFactory : CallAdapter.Factory() {

    override fun get(
        returnType: Type,
        annotations: Array<out Annotation>,
        retrofit: Retrofit
    ): CallAdapter<*, *>? {
        if (getRawType(returnType) != Call::class.java) {
            return null
        }

        val callType = getParameterUpperBound(0, returnType as ParameterizedType)

        if (getRawType(callType) != Result::class.java) {
            return null
        }

        val resultType = getParameterUpperBound(0, callType as ParameterizedType)

        return ResultCallAdapter<Any>(resultType)
    }
}

private class ResultCallAdapter<T>(
    private val successType: Type
) : CallAdapter<T, Call<Result<T>>> {

    override fun responseType(): Type = successType

    override fun adapt(call: Call<T>): Call<Result<T>> {
        return ResultCall(call)
    }
}

private class ResultCall<T>(
    private val delegate: Call<T>
) : Call<Result<T>> {

    override fun enqueue(callback: Callback<Result<T>>) {
        delegate.enqueue(object : Callback<T> {
            override fun onResponse(call: Call<T>, response: Response<T>) {
                val result = response.toResult()
                callback.onResponse(this@ResultCall, Response.success(result))
            }

            override fun onFailure(call: Call<T>, t: Throwable) {
                val result = when (t) {
                    is IOException -> Result.Error.NetworkError(t)
                    else -> Result.Error.UnknownError(t)
                }
                callback.onResponse(this@ResultCall, Response.success(result))
            }
        })
    }

    override fun execute(): Response<Result<T>> {
        return try {
            val response = delegate.execute()
            Response.success(response.toResult())
        } catch (e: IOException) {
            Response.success(Result.Error.NetworkError(e))
        }
    }

    override fun isExecuted() = delegate.isExecuted
    override fun cancel() = delegate.cancel()
    override fun isCanceled() = delegate.isCanceled
    override fun request() = delegate.request()
    override fun timeout() = delegate.timeout()
    override fun clone() = ResultCall(delegate.clone())
}

private fun <T> Response<T>.toResult(): Result<T> {
    return if (isSuccessful) {
        val body = body()
        if (body != null) {
            Result.Success(body)
        } else {
            Result.Error.UnknownError(NullPointerException("Body is null"))
        }
    } else {
        Result.Error.HttpError(
            code = code(),
            message = message(),
            body = errorBody()?.string()
        )
    }
}
```

### Полная настройка Retrofit

```kotlin
class ApiClientBuilder(
    private val baseUrl: String,
    private val okHttpClient: OkHttpClient
) {

    fun build(): ApiService {
        return Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .addCallAdapterFactory(ResultCallAdapterFactory())
            .build()
            .create(ApiService::class.java)
    }
}

interface ApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: String): Result<User>

    @GET("users/{id}/posts")
    suspend fun getUserPosts(@Path("id") userId: String): Result<List<Post>>

    @POST("posts")
    suspend fun createPost(@Body post: CreatePostRequest): Result<Post>
}
```

### Интеграция со слоем Repository

```kotlin
class UserRepository(
    private val apiService: ApiService,
    private val userDao: UserDao
) {

    suspend fun getUser(userId: String): Result<User> {
        return apiService.getUser(userId)
    }

    suspend fun getUserWithCache(userId: String): Result<User> {
        val result = apiService.getUser(userId)

        result.onSuccess { user ->
            userDao.insertUser(user)
        }

        if (result is Result.Error) {
            val cachedUser = userDao.getUserById(userId)
            if (cachedUser != null) {
                return Result.Success(cachedUser)
            }
        }

        return result
    }

    suspend fun getUserProfile(userId: String): Result<UserProfile> {
        return apiService.getUser(userId).map { user ->
            UserProfile(user = user, postCount = getPostCount(userId))
        }
    }
}
```

### ViewModel слой

```kotlin
class UserViewModel(
    private val userRepository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    sealed class UiState {
        object Loading : UiState()
        data class Success(val user: User) : UiState()
        data class Error(val message: String) : UiState()
    }

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            when (val result = userRepository.getUser(userId)) {
                is Result.Success -> {
                    _uiState.value = UiState.Success(result.data)
                }
                is Result.Error -> {
                    _uiState.value = UiState.Error(result.toUserMessage())
                }
            }
        }
    }
}
```

### Best Practices

1. **Использовать Sealed Classes**: Типобезопасная обработка ошибок

2. **Централизовать маппинг ошибок**: Конвертировать все ошибки в CallAdapter

3. **Предоставлять понятные сообщения**: Преобразовывать технические ошибки

4. **Поддерживать разные типы возврата**: suspend, Call<T>, Flow<T>

5. **Держать Repository чистым**: Позволить CallAdapter обрабатывать низкоуровневые ошибки

6. **Кешировать при ошибках**: Резервный вариант с кешем

7. **Тщательно тестировать**: Тестировать все сценарии ошибок

### Распространённые ошибки

1. **Не обрабатывать все типы ошибок**: Неполное when выражение

2. **Потеря информации о типе**: Использование Result<Any>

3. **Исключения в CallAdapter**: Следует возвращать Result.Error

4. **Не закрывать response body**: Утечки памяти

5. **Игнорировать отмену**: Не обрабатывать отмену корутин

### Резюме

Кастомный Retrofit CallAdapter обеспечивает:

-   **Единообразную обработку ошибок**: Одно место для конвертации
-   **Типобезопасность**: Sealed classes для полной обработки
-   **Чистый код**: Репозитории без try-catch
-   **Тестируемость**: Лёгкое тестирование
-   **Гибкость**: Поддержка Call, suspend, Flow
-   **UX**: Понятные сообщения об ошибках
-   **Поддерживаемость**: Централизованная логика ошибок

---

## Related Questions

### Prerequisites (Easier)

-   [[q-why-separate-ui-and-business-logic--android--easy]] - Ui
-   [[q-how-to-start-drawing-ui-in-android--android--easy]] - Ui
-   [[q-recyclerview-sethasfixedsize--android--easy]] - Ui

### Related (Medium)

-   [[q-http-protocols-comparison--android--medium]] - Networking
-   [[q-dagger-build-time-optimization--android--medium]] - Ui
-   [[q-rxjava-pagination-recyclerview--android--medium]] - Ui
-   [[q-build-optimization-gradle--gradle--medium]] - Ui
-   [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - Ui

### Advanced (Harder)

-   [[q-data-sync-unstable-network--android--hard]] - Networking
