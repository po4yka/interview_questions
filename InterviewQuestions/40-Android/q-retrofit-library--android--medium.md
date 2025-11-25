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
related: [c-android, c-coroutines, q-coroutine-exception-handling--kotlin--medium]
sources: []
created: 2025-10-15
updated: 2025-11-10
tags: [android/architecture-mvvm, android/coroutines, android/networking-http, difficulty/medium, networking, rest-api, retrofit]
date created: Saturday, November 1st 2025, 1:04:11 pm
date modified: Tuesday, November 25th 2025, 8:53:57 pm
---

# Вопрос (RU)

> Что из себя представляет Retrofit и зачем он нужен в Android-разработке?

# Question (EN)

> What is Retrofit and why is it needed in Android development?

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
    .addConverterFactory(GsonConverterFactory.create())  // ✅ JSON → POJO/data class
    .build()

data class User(val id: Int, val name: String)  // ✅ Auto-mapped
```

**3. Интеграция с корутинами**

```kotlin
// ✅ Рекомендуемый подход: suspend-функции с корутинами
viewModelScope.launch {
    try {
        val user = apiService.getUser(123)
        _state.value = Success(user)  // _state: например, MutableStateFlow или LiveData
    } catch (e: HttpException) {
        _state.value = Error(e.code())  // 404, 500, etc.
    }
}

// Поддерживается и callback-API (Call<T>),
// но в современном корутинном коде обычно предпочтительнее suspend-функции.
apiService.getUser(123).enqueue(object : Callback<User> { /* ... */ })
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
    .baseUrl("https://api.example.com/")
    .client(client)
    .addConverterFactory(GsonConverterFactory.create())
    .build()
```

### Пример С Repository-паттерном

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
            Result.failure(e)  // ✅ Обработка ошибок на уровне репозитория
        }
}

// ViewModel
class RepoViewModel(private val repo: RepoRepository) : ViewModel() {
    private val _state = MutableStateFlow<List<Repo>>(emptyList())
    val state: StateFlow<List<Repo>> = _state

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
    // Примеры HTTP-методов объявляются по одному на функцию:
    @GET("items")
    suspend fun getItems(): List<Item>

    @POST("items")
    suspend fun createItem(@Body item: Item): Item

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

**Итого**: Retrofit превращает HTTP API в идиоматичный Kotlin-код, убирая boilerplate для networking-логики.

## Answer (EN)

**Retrofit** is a type-safe HTTP client by Square that transforms REST APIs into Kotlin/Java interfaces. It simplifies networking via a declarative, annotation-based approach.

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
    .addConverterFactory(GsonConverterFactory.create())  // ✅ JSON → POJO/data class
    .build()

data class User(val id: Int, val name: String)  // ✅ Auto-mapped
```

**3. Coroutines Integration**

```kotlin
// ✅ Recommended: suspend functions with coroutines
viewModelScope.launch {
    try {
        val user = apiService.getUser(123)
        _state.value = Success(user)  // _state: e.g., MutableStateFlow or LiveData
    } catch (e: HttpException) {
        _state.value = Error(e.code())  // 404, 500, etc.
    }
}

// Callback-based Call<T> API is still supported,
// but suspend functions are usually preferred in modern coroutine-based code.
apiService.getUser(123).enqueue(object : Callback<User> { /* ... */ })
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
    .baseUrl("https://api.example.com/")
    .client(client)
    .addConverterFactory(GsonConverterFactory.create())
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
    private val _state = MutableStateFlow<List<Repo>>(emptyList())
    val state: StateFlow<List<Repo>> = _state

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
    // HTTP method annotations are used one per function, for example:
    @GET("items")
    suspend fun getItems(): List<Item>

    @POST("items")
    suspend fun createItem(@Body item: Item): Item

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

**Summary**: Retrofit transforms HTTP APIs into idiomatic Kotlin code, removing much of the networking boilerplate.

---

## Follow-ups

1. How does Retrofit integrate with [[c-coroutines]] and structured concurrency in Android apps?
2. How would you choose between different call adapters (e.g. coroutines, RxJava, `Call<T>`) when using Retrofit?
3. How can you design error-handling and result wrappers (e.g. `sealed class`) around Retrofit calls in a clean architecture setup?
4. How would you configure different Retrofit instances (base URLs, interceptors, timeouts) for staging/production with dependency injection (e.g. [[c-dagger]])?
5. How can you combine Retrofit with response caching and logging using OkHttp interceptors?

## References

- [[c-coroutines]]
- https://square.github.io/retrofit/ - Official Retrofit documentation
- https://square.github.io/okhttp/ - OkHttp documentation

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]]
- [[q-android-manifest-file--android--easy]]

### Related (Same Level)
- [[q-android-architectural-patterns--android--medium]]
- [[q-android-lint-tool--android--medium]]
- [[q-coroutine-exception-handling--kotlin--medium]]

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]]
- [[q-android-build-optimization--android--medium]]
