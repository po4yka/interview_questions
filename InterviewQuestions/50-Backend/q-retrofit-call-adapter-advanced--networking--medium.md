---
id: net-002
title: "Retrofit Call Adapter Advanced / Продвинутый CallAdapter для Retrofit"
aliases: ["Retrofit Call Adapter Advanced", "Продвинутый CallAdapter для Retrofit"]
topic: networking
subtopics: [retrofit, error-handling, sealed-classes]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-backend
related: [c-sealed-classes, c-error-handling, c-retrofit]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [networking, retrofit, call-adapter, result, error-handling, sealed-classes, difficulty/medium]
---

# Вопрос (RU)

Как реализовать кастомный Retrofit CallAdapter для типа Result<T>? Как централизованно обрабатывать разные типы ошибок с помощью sealed классов?

# Question (EN)

How to implement custom Retrofit CallAdapter for Result<T> type? How to centrally handle different response types and errors with sealed classes?

---

## Ответ (RU)

**Retrofit CallAdapter** - механизм трансформации HTTP ответов в кастомные типы. Позволяет централизовать обработку ошибок, стандартизировать работу с API и интегрироваться с корутинами.

### Зачем нужен CallAdapter?

Без CallAdapter обработка ошибок дублируется в каждом вызове:

```kotlin
// ❌ Повторяющийся код обработки ошибок
suspend fun getUser(id: String): User? {
    return try {
        val response = apiService.getUser(id)
        if (response.isSuccessful) response.body()
        else null // потеряли информацию об ошибке
    } catch (e: IOException) {
        null // потеряли тип ошибки
    }
}
```

С CallAdapter обработка централизована:

```kotlin
// ✅ Чистый API, централизованная обработка
suspend fun getUser(id: String): Result<User> {
    return apiService.getUser(id) // автоматически обёрнуто в Result
}
```

### Result Type с Sealed Classes

Sealed классы обеспечивают exhaustive checking разных типов ошибок:

```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()

    sealed class Error : Result<Nothing>() {
        data class HttpError(val code: Int, val message: String) : Error()
        data class NetworkError(val exception: IOException) : Error()
        data class SerializationError(val exception: Exception) : Error()
    }

    inline fun <R> map(transform: (T) -> R): Result<R> = when (this) {
        is Success -> Success(transform(data))
        is Error -> this
    }

    inline fun onSuccess(action: (T) -> Unit): Result<T> {
        if (this is Success) action(data)
        return this
    }
}

// ✅ Маппинг ошибок в user-friendly сообщения
fun Result.Error.toUserMessage(): String = when (this) {
    is Result.Error.HttpError -> when (code) {
        401 -> "Требуется авторизация"
        404 -> "Ресурс не найден"
        in 500..599 -> "Ошибка сервера"
        else -> message
    }
    is Result.Error.NetworkError -> "Нет соединения"
    is Result.Error.SerializationError -> "Ошибка парсинга данных"
}
```

### Реализация CallAdapter Factory

```kotlin
class ResultCallAdapterFactory : CallAdapter.Factory() {

    override fun get(
        returnType: Type,
        annotations: Array<out Annotation>,
        retrofit: Retrofit
    ): CallAdapter<*, *>? {
        // ✅ Проверяем что возвращается Call<Result<T>>
        if (getRawType(returnType) != Call::class.java) return null

        val callType = getParameterUpperBound(0, returnType as ParameterizedType)
        if (getRawType(callType) != Result::class.java) return null

        // ✅ Извлекаем тип T из Result<T>
        val resultType = getParameterUpperBound(0, callType as ParameterizedType)
        return ResultCallAdapter<Any>(resultType)
    }
}

private class ResultCallAdapter<T>(
    private val successType: Type
) : CallAdapter<T, Call<Result<T>>> {

    override fun responseType(): Type = successType

    override fun adapt(call: Call<T>): Call<Result<T>> = ResultCall(call)
}
```

### Result Call Wrapper

```kotlin
private class ResultCall<T>(
    private val delegate: Call<T>
) : Call<Result<T>> {

    override fun enqueue(callback: Callback<Result<T>>) {
        delegate.enqueue(object : Callback<T> {
            override fun onResponse(call: Call<T>, response: Response<T>) {
                // ✅ Конвертируем Response в Result
                val result = response.toResult()
                callback.onResponse(this@ResultCall, Response.success(result))
            }

            override fun onFailure(call: Call<T>, t: Throwable) {
                // ✅ Мапим исключения в Result.Error
                val result = when (t) {
                    is IOException -> Result.Error.NetworkError(t)
                    else -> Result.Error.SerializationError(Exception(t))
                }
                callback.onResponse(this@ResultCall, Response.success(result))
            }
        })
    }

    override fun execute(): Response<Result<T>> {
        return try {
            Response.success(delegate.execute().toResult())
        } catch (e: IOException) {
            Response.success(Result.Error.NetworkError(e))
        }
    }

    override fun clone() = ResultCall(delegate.clone())
    override fun cancel() = delegate.cancel()
    override fun isExecuted() = delegate.isExecuted
    override fun isCanceled() = delegate.isCanceled
    override fun request() = delegate.request()
    override fun timeout() = delegate.timeout()
}

private fun <T> Response<T>.toResult(): Result<T> {
    return if (isSuccessful) {
        body()?.let { Result.Success(it) }
            ?: Result.Error.SerializationError(NullPointerException("Body is null"))
    } else {
        Result.Error.HttpError(code = code(), message = message())
    }
}
```

### Настройка Retrofit

```kotlin
val retrofit = Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .client(okHttpClient)
    .addConverterFactory(GsonConverterFactory.create())
    .addCallAdapterFactory(ResultCallAdapterFactory()) // ✅ регистрируем адаптер
    .build()

interface ApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: String): Result<User>

    @GET("users/{id}/posts")
    suspend fun getUserPosts(@Path("id") userId: String): Result<List<Post>>
}
```

### Использование в Repository

```kotlin
class UserRepository(
    private val apiService: ApiService,
    private val userDao: UserDao
) {
    // ✅ Чистый код без try-catch
    suspend fun getUser(userId: String): Result<User> {
        return apiService.getUser(userId)
    }

    // ✅ Трансформация данных
    suspend fun getUserProfile(userId: String): Result<UserProfile> {
        return apiService.getUser(userId).map { user ->
            UserProfile(user, getPostCount(userId))
        }
    }

    // ✅ Fallback на кеш при ошибке
    suspend fun getUserWithCache(userId: String): Result<User> {
        return apiService.getUser(userId).also { result ->
            result.onSuccess { user -> userDao.insert(user) }
        }.let { result ->
            if (result is Result.Error) {
                userDao.getUserById(userId)?.let { Result.Success(it) } ?: result
            } else result
        }
    }
}
```

### Интеграция с ViewModel

```kotlin
class UserViewModel(
    private val repository: UserRepository
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

            // ✅ Exhaustive when с sealed classes
            _uiState.value = when (val result = repository.getUser(userId)) {
                is Result.Success -> UiState.Success(result.data)
                is Result.Error -> UiState.Error(result.toUserMessage())
            }
        }
    }
}
```

### Best Practices

1. **Sealed Classes для типобезопасности** - компилятор гарантирует обработку всех случаев
2. **Централизация маппинга ошибок** - конвертация в CallAdapter, не в репозиториях
3. **User-friendly сообщения** - мапим технические ошибки в понятный текст
4. **Не бросать исключения** - возвращаем Result.Error вместо throw
5. **Тестируемость** - легко тестировать с MockWebServer

### Распространённые ошибки

```kotlin
// ❌ Неполная обработка ошибок (не exhaustive)
when (result) {
    is Result.Success -> show(result.data)
    is Result.Error.HttpError -> showError()
    // забыли NetworkError и SerializationError!
}

// ✅ Exhaustive with sealed class
when (result) {
    is Result.Success -> show(result.data)
    is Result.Error -> showError(result.toUserMessage())
}

// ❌ Потеря типовой информации
val result: Result<Any> = apiService.getUser() // теряем тип User

// ✅ Сохраняем типы
val result: Result<User> = apiService.getUser()

// ❌ Бросаем исключения в CallAdapter
override fun adapt(call: Call<T>): Call<Result<T>> {
    throw RuntimeException() // ломает контракт
}
```

---

## Answer (EN)

**Retrofit CallAdapter** is a mechanism for transforming HTTP responses into custom types. It centralizes error handling, standardizes API interaction, and integrates with coroutines.

### Why Custom CallAdapter?

Without CallAdapter, error handling is duplicated across calls:

```kotlin
// ❌ Repetitive error handling in every call
suspend fun getUser(id: String): User? {
    return try {
        val response = apiService.getUser(id)
        if (response.isSuccessful) response.body()
        else null // lost error information
    } catch (e: IOException) {
        null // lost error type
    }
}
```

With CallAdapter, handling is centralized:

```kotlin
// ✅ Clean API with centralized handling
suspend fun getUser(id: String): Result<User> {
    return apiService.getUser(id) // automatically wrapped in Result
}
```

### Result Type with Sealed Classes

Sealed classes provide exhaustive checking of error types:

```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()

    sealed class Error : Result<Nothing>() {
        data class HttpError(val code: Int, val message: String) : Error()
        data class NetworkError(val exception: IOException) : Error()
        data class SerializationError(val exception: Exception) : Error()
    }

    inline fun <R> map(transform: (T) -> R): Result<R> = when (this) {
        is Success -> Success(transform(data))
        is Error -> this
    }

    inline fun onSuccess(action: (T) -> Unit): Result<T> {
        if (this is Success) action(data)
        return this
    }
}

// ✅ Map errors to user-friendly messages
fun Result.Error.toUserMessage(): String = when (this) {
    is Result.Error.HttpError -> when (code) {
        401 -> "Authentication required"
        404 -> "Resource not found"
        in 500..599 -> "Server error"
        else -> message
    }
    is Result.Error.NetworkError -> "No connection"
    is Result.Error.SerializationError -> "Data parsing error"
}
```

### CallAdapter Factory Implementation

```kotlin
class ResultCallAdapterFactory : CallAdapter.Factory() {

    override fun get(
        returnType: Type,
        annotations: Array<out Annotation>,
        retrofit: Retrofit
    ): CallAdapter<*, *>? {
        // ✅ Check if return type is Call<Result<T>>
        if (getRawType(returnType) != Call::class.java) return null

        val callType = getParameterUpperBound(0, returnType as ParameterizedType)
        if (getRawType(callType) != Result::class.java) return null

        // ✅ Extract type T from Result<T>
        val resultType = getParameterUpperBound(0, callType as ParameterizedType)
        return ResultCallAdapter<Any>(resultType)
    }
}

private class ResultCallAdapter<T>(
    private val successType: Type
) : CallAdapter<T, Call<Result<T>>> {

    override fun responseType(): Type = successType

    override fun adapt(call: Call<T>): Call<Result<T>> = ResultCall(call)
}
```

### Result Call Wrapper

```kotlin
private class ResultCall<T>(
    private val delegate: Call<T>
) : Call<Result<T>> {

    override fun enqueue(callback: Callback<Result<T>>) {
        delegate.enqueue(object : Callback<T> {
            override fun onResponse(call: Call<T>, response: Response<T>) {
                // ✅ Convert Response to Result
                val result = response.toResult()
                callback.onResponse(this@ResultCall, Response.success(result))
            }

            override fun onFailure(call: Call<T>, t: Throwable) {
                // ✅ Map exceptions to Result.Error
                val result = when (t) {
                    is IOException -> Result.Error.NetworkError(t)
                    else -> Result.Error.SerializationError(Exception(t))
                }
                callback.onResponse(this@ResultCall, Response.success(result))
            }
        })
    }

    override fun execute(): Response<Result<T>> {
        return try {
            Response.success(delegate.execute().toResult())
        } catch (e: IOException) {
            Response.success(Result.Error.NetworkError(e))
        }
    }

    override fun clone() = ResultCall(delegate.clone())
    override fun cancel() = delegate.cancel()
    override fun isExecuted() = delegate.isExecuted
    override fun isCanceled() = delegate.isCanceled
    override fun request() = delegate.request()
    override fun timeout() = delegate.timeout()
}

private fun <T> Response<T>.toResult(): Result<T> {
    return if (isSuccessful) {
        body()?.let { Result.Success(it) }
            ?: Result.Error.SerializationError(NullPointerException("Body is null"))
    } else {
        Result.Error.HttpError(code = code(), message = message())
    }
}
```

### Retrofit Setup

```kotlin
val retrofit = Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .client(okHttpClient)
    .addConverterFactory(GsonConverterFactory.create())
    .addCallAdapterFactory(ResultCallAdapterFactory()) // ✅ register adapter
    .build()

interface ApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: String): Result<User>

    @GET("users/{id}/posts")
    suspend fun getUserPosts(@Path("id") userId: String): Result<List<Post>>
}
```

### Repository Layer Usage

```kotlin
class UserRepository(
    private val apiService: ApiService,
    private val userDao: UserDao
) {
    // ✅ Clean code without try-catch
    suspend fun getUser(userId: String): Result<User> {
        return apiService.getUser(userId)
    }

    // ✅ Data transformation
    suspend fun getUserProfile(userId: String): Result<UserProfile> {
        return apiService.getUser(userId).map { user ->
            UserProfile(user, getPostCount(userId))
        }
    }

    // ✅ Fallback to cache on error
    suspend fun getUserWithCache(userId: String): Result<User> {
        return apiService.getUser(userId).also { result ->
            result.onSuccess { user -> userDao.insert(user) }
        }.let { result ->
            if (result is Result.Error) {
                userDao.getUserById(userId)?.let { Result.Success(it) } ?: result
            } else result
        }
    }
}
```

### ViewModel Integration

```kotlin
class UserViewModel(
    private val repository: UserRepository
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

            // ✅ Exhaustive when with sealed classes
            _uiState.value = when (val result = repository.getUser(userId)) {
                is Result.Success -> UiState.Success(result.data)
                is Result.Error -> UiState.Error(result.toUserMessage())
            }
        }
    }
}
```

### Best Practices

1. **Sealed Classes for type safety** - compiler guarantees exhaustive handling
2. **Centralize error mapping** - convert in CallAdapter, not repositories
3. **User-friendly messages** - map technical errors to readable text
4. **Never throw exceptions** - return Result.Error instead of throw
5. **Testability** - easy to test with MockWebServer

### Common Mistakes

```kotlin
// ❌ Incomplete error handling (not exhaustive)
when (result) {
    is Result.Success -> show(result.data)
    is Result.Error.HttpError -> showError()
    // forgot NetworkError and SerializationError!
}

// ✅ Exhaustive with sealed class
when (result) {
    is Result.Success -> show(result.data)
    is Result.Error -> showError(result.toUserMessage())
}

// ❌ Losing type information
val result: Result<Any> = apiService.getUser() // lost User type

// ✅ Preserve types
val result: Result<User> = apiService.getUser()

// ❌ Throwing exceptions in CallAdapter
override fun adapt(call: Call<T>): Call<Result<T>> {
    throw RuntimeException() // breaks contract
}
```

---

## Follow-ups

- How to support Flow<Result<T>> return type in CallAdapter?
- How to handle multipart/form-data uploads with Result wrapper?
- What is the performance overhead of wrapping every response?
- How to integrate custom CallAdapter with OkHttp interceptors?
- How to handle 401 token refresh automatically in CallAdapter?

## References

- [[c-sealed-classes]] - Sealed classes for type-safe hierarchies
- [[c-error-handling]] - Error handling patterns in Kotlin
- [[c-retrofit]] - Retrofit fundamentals and architecture

## Related Questions

### Prerequisites (Easier)

- Basic Retrofit usage and setup
- Sealed classes fundamentals
- Coroutines and suspend functions

### Related (Medium)

- [[q-http-protocols-comparison--android--medium]] - HTTP protocols comparison
- OkHttp interceptor chains
- Repository pattern with error handling

### Advanced (Harder)

- [[q-data-sync-unstable-network--android--hard]] - Data sync in unstable networks
- Custom Retrofit converters
- Advanced type reflection patterns
