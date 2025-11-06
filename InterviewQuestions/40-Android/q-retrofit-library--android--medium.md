---
id: android-369
title: "Retrofit Library / Библиотека Retrofit"
aliases: ["Retrofit Library", "Библиотека Retrofit"]
topic: android
subtopics: [architecture-mvvm, coroutines, networking-http]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-http-client, c-rest-api, q-what-is-rest-api--networking--easy]
sources: []
created: 2025-10-15
updated: 2025-10-28
tags: [android/architecture-mvvm, android/coroutines, android/networking-http, difficulty/medium, networking, rest-api, retrofit]
---

# Вопрос (RU)

Что из себя представляет Retrofit и зачем он нужен в Android-разработке?

# Question (EN)

What is Retrofit and why is it needed in Android development?

## Ответ (RU)

**Retrofit** — типобезопасный HTTP-клиент от Square, преобразующий REST API в Kotlin/Java интерфейсы. Упрощает сетевое взаимодействие через декларативный подход с аннотациями.

### Ключевые Возможности

**1. Декларативные API интерфейсы**

```kotlin
interface ApiService {
    @GET("users/{id}")  // ✅ Path parameter
    suspend fun getUser(@Path("id") userId: Int): User

    @POST("users")      // ✅ Body serialization
    suspend fun createUser(@Body user: User): User

    @GET("search")      // ✅ Query parameters
    suspend fun search(@Query("q") query: String): List<Result>
}
```

**2. Автоматическая (де)сериализация**

```kotlin
val retrofit = Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .addConverterFactory(GsonConverterFactory.create())  // ✅ JSON → POJO
    .build()

data class User(val id: Int, val name: String)  // ✅ Auto-mapped
```

**3. Интеграция с корутинами**

```kotlin
// ✅ Modern: suspend functions
viewModelScope.launch {
    try {
        val user = apiService.getUser(123)
        _state.value = Success(user)
    } catch (e: HttpException) {
        _state.value = Error(e.code())  // 404, 500, etc.
    }
}

// ❌ Legacy: callback-based (avoid)
apiService.getUser(123).enqueue(object : Callback<User> { ... })
```

**4. Настройка через OkHttp**

```kotlin
val client = OkHttpClient.Builder()
    .addInterceptor { chain ->  // ✅ Add auth headers
        chain.proceed(
            chain.request().newBuilder()
                .addHeader("Authorization", "Bearer $token")
                .build()
        )
    }
    .connectTimeout(30, TimeUnit.SECONDS)  // ✅ Timeouts
    .build()

val retrofit = Retrofit.Builder()
    .client(client)
    .build()
```

### Пример С Repository Паттерном

```kotlin
// API definition
interface GitHubApi {
    @GET("users/{username}/repos")
    suspend fun getRepos(@Path("username") name: String): List<Repo>
}

// Repository layer
class RepoRepository(private val api: GitHubApi) {
    suspend fun fetchRepos(username: String): Result<List<Repo>> =
        try {
            Result.success(api.getRepos(username))
        } catch (e: Exception) {
            Result.failure(e)  // ✅ Handle errors at repository level
        }
}

// ViewModel
class RepoViewModel(private val repo: RepoRepository) : ViewModel() {
    fun loadRepos() = viewModelScope.launch {
        repo.fetchRepos("square").onSuccess { repos ->
            _state.value = repos
        }
    }
}
```

### HTTP Методы И Формы

```kotlin
interface ApiService {
    @GET @POST @PUT @DELETE @PATCH  // Standard methods

    @FormUrlEncoded  // ✅ application/x-www-form-urlencoded
    @POST("login")
    suspend fun login(
        @Field("username") user: String,
        @Field("password") pass: String
    ): Token

    @Multipart  // ✅ multipart/form-data (file uploads)
    @POST("upload")
    suspend fun upload(@Part file: MultipartBody.Part): UploadResponse
}
```

### Обработка Ошибок

```kotlin
sealed class ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>()
    data class Error(val code: Int, val message: String) : ApiResult<Nothing>()
}

suspend fun <T> safeCall(call: suspend () -> T): ApiResult<T> =
    try {
        ApiResult.Success(call())
    } catch (e: HttpException) {  // ✅ HTTP errors (4xx, 5xx)
        ApiResult.Error(e.code(), e.message())
    } catch (e: IOException) {    // ✅ Network errors
        ApiResult.Error(-1, "Network error")
    }
```

**Итого**: Retrofit превращает HTTP API в идиоматичный Kotlin код, убирая boilerplate для networking логики.

## Answer (EN)

**Retrofit** is a type-safe HTTP client by Square that transforms REST APIs into Kotlin/Java interfaces. Simplifies networking via declarative annotation-based approach.

### Key Capabilities

**1. Declarative API Interfaces**

```kotlin
interface ApiService {
    @GET("users/{id}")  // ✅ Path parameter
    suspend fun getUser(@Path("id") userId: Int): User

    @POST("users")      // ✅ Body serialization
    suspend fun createUser(@Body user: User): User

    @GET("search")      // ✅ Query parameters
    suspend fun search(@Query("q") query: String): List<Result>
}
```

**2. Automatic (De)Serialization**

```kotlin
val retrofit = Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .addConverterFactory(GsonConverterFactory.create())  // ✅ JSON → POJO
    .build()

data class User(val id: Int, val name: String)  // ✅ Auto-mapped
```

**3. Coroutines Integration**

```kotlin
// ✅ Modern: suspend functions
viewModelScope.launch {
    try {
        val user = apiService.getUser(123)
        _state.value = Success(user)
    } catch (e: HttpException) {
        _state.value = Error(e.code())  // 404, 500, etc.
    }
}

// ❌ Legacy: callback-based (avoid)
apiService.getUser(123).enqueue(object : Callback<User> { ... })
```

**4. OkHttp Customization**

```kotlin
val client = OkHttpClient.Builder()
    .addInterceptor { chain ->  // ✅ Add auth headers
        chain.proceed(
            chain.request().newBuilder()
                .addHeader("Authorization", "Bearer $token")
                .build()
        )
    }
    .connectTimeout(30, TimeUnit.SECONDS)  // ✅ Timeouts
    .build()

val retrofit = Retrofit.Builder()
    .client(client)
    .build()
```

### Repository Pattern Example

```kotlin
// API definition
interface GitHubApi {
    @GET("users/{username}/repos")
    suspend fun getRepos(@Path("username") name: String): List<Repo>
}

// Repository layer
class RepoRepository(private val api: GitHubApi) {
    suspend fun fetchRepos(username: String): Result<List<Repo>> =
        try {
            Result.success(api.getRepos(username))
        } catch (e: Exception) {
            Result.failure(e)  // ✅ Handle errors at repository level
        }
}

// ViewModel
class RepoViewModel(private val repo: RepoRepository) : ViewModel() {
    fun loadRepos() = viewModelScope.launch {
        repo.fetchRepos("square").onSuccess { repos ->
            _state.value = repos
        }
    }
}
```

### HTTP Methods and Forms

```kotlin
interface ApiService {
    @GET @POST @PUT @DELETE @PATCH  // Standard methods

    @FormUrlEncoded  // ✅ application/x-www-form-urlencoded
    @POST("login")
    suspend fun login(
        @Field("username") user: String,
        @Field("password") pass: String
    ): Token

    @Multipart  // ✅ multipart/form-data (file uploads)
    @POST("upload")
    suspend fun upload(@Part file: MultipartBody.Part): UploadResponse
}
```

### Error Handling

```kotlin
sealed class ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>()
    data class Error(val code: Int, val message: String) : ApiResult<Nothing>()
}

suspend fun <T> safeCall(call: suspend () -> T): ApiResult<T> =
    try {
        ApiResult.Success(call())
    } catch (e: HttpException) {  // ✅ HTTP errors (4xx, 5xx)
        ApiResult.Error(e.code(), e.message())
    } catch (e: IOException) {    // ✅ Network errors
        ApiResult.Error(-1, "Network error")
    }
```

**Summary**: Retrofit transforms HTTP APIs into idiomatic Kotlin code, eliminating networking boilerplate.

---

## Follow-ups

1. How does Retrofit handle response caching and what's the role of OkHttp's cache interceptor?
2. What are the differences between Retrofit's `Call<T>`, `suspend` functions, and `Flow<T>` return types?
3. How would you implement request retry logic with exponential backoff in Retrofit?
4. What's the proper way to handle multipart uploads with progress tracking?
5. When should you use custom `Converter.Factory` vs. built-in ones (Gson, Moshi)?

## References

- [[c-http-client]] - HTTP client fundamentals
- [[c-rest-api]] - REST API design principles
- [[c-serialization]] - JSON serialization patterns
- https://square.github.io/retrofit/ - Official Retrofit documentation
- https://square.github.io/okhttp/ - OkHttp documentation

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-rest-api--networking--easy]]
- [[q-kotlin-suspend-functions--kotlin--easy]]

### Related (Same Level)
- [[q-okhttp-vs-retrofit--android--medium]]
- [[q-repository-pattern--architecture-patterns--medium]]
- [[q-coroutine-exception-handling--kotlin--medium]]

### Advanced (Harder)
- [[q-custom-retrofit-call-adapter--android--hard]]
- [[q-network-request-deduplication--networking--hard]]
