---
id: android-276
title: "Retrofit Usage Tutorial / Retrofit Использование Tutorial"
aliases: ["Retrofit Usage Tutorial", "Retrofit Использование Tutorial"]
topic: android
subtopics: [architecture-mvvm, coroutines, networking-http]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-compose-navigation-advanced--jetpack-compose--medium, q-flow-testing-turbine--android--medium, q-what-is-data-binding--android--easy]
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android/architecture-mvvm, android/coroutines, android/networking-http, difficulty/medium, networking, retrofit]
date created: Saturday, November 1st 2025, 12:47:02 pm
date modified: Saturday, November 1st 2025, 5:43:32 pm
---

# Вопрос (RU)

Как делать сетевые запросы с помощью Retrofit?

# Question (EN)

How to make network requests with Retrofit?

---

## Ответ (RU)

Retrofit — это type-safe HTTP клиент для Android. Основная идея: вы описываете API через интерфейс с аннотациями, а Retrofit генерирует реализацию.

### Основные Шаги

**1. Добавить зависимости**

```gradle
// app/build.gradle
dependencies {
    implementation 'com.squareup.retrofit2:retrofit:2.9.0'
    implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
    implementation 'com.squareup.okhttp3:logging-interceptor:4.11.0'
}
```

**2. Создать модель данных**

```kotlin
data class User(
    val id: Int,
    val name: String,
    val email: String
)
```

**3. Определить API интерфейс**

```kotlin
interface ApiService {
    @GET("users")
    suspend fun getUsers(): List<User>

    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: Int): User

    @POST("users")
    suspend fun createUser(@Body user: User): User
}
```

**Аннотации Retrofit**:
- `@GET`, `@POST`, `@PUT`, `@DELETE` — HTTP методы
- `@Path` — параметр пути URL (users/{id})
- `@Query` — query параметры (?userId=123)
- `@Body` — тело запроса (JSON)
- `@Header` — заголовок запроса

**4. Создать экземпляр Retrofit**

```kotlin
object RetrofitClient {
    private const val BASE_URL = "https://api.example.com/"

    // ✅ Правильно: OkHttp с логированием для отладки
    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(HttpLoggingInterceptor().apply {
            level = if (BuildConfig.DEBUG) {
                HttpLoggingInterceptor.Level.BODY
            } else {
                HttpLoggingInterceptor.Level.NONE
            }
        })
        .addInterceptor { chain ->
            val request = chain.request().newBuilder()
                .addHeader("Content-Type", "application/json")
                .build()
            chain.proceed(request)
        }
        .build()

    val apiService: ApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }
}
```

**5. Использовать в Repository**

```kotlin
class UserRepository {
    private val api = RetrofitClient.apiService

    suspend fun getUsers(): Result<List<User>> = try {
        Result.Success(api.getUsers())
    } catch (e: HttpException) {
        Result.Error("HTTP ${e.code()}: ${e.message()}")
    } catch (e: IOException) {
        Result.Error("Network error: ${e.message}")
    }
}

sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
}
```

**6. Вызвать из ViewModel**

```kotlin
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _users = MutableLiveData<List<User>>()
    val users: LiveData<List<User>> = _users

    fun loadUsers() {
        viewModelScope.launch {
            when (val result = repository.getUsers()) {
                is Result.Success -> _users.value = result.data
                is Result.Error -> /* показать ошибку */
            }
        }
    }
}
```

### Особые Случаи

**Form URL Encoded (логин)**

```kotlin
@FormUrlEncoded
@POST("login")
suspend fun login(
    @Field("username") username: String,
    @Field("password") password: String
): LoginResponse
```

**Multipart (загрузка файлов)**

```kotlin
@Multipart
@POST("upload")
suspend fun uploadFile(
    @Part file: MultipartBody.Part
): UploadResponse

// Использование
val requestFile = imageFile.asRequestBody("image/*".toMediaType())
val filePart = MultipartBody.Part.createFormData("image", imageFile.name, requestFile)
val response = api.uploadFile(filePart)
```

**Query параметры**

```kotlin
// ✅ Правильно: опциональные параметры с default значениями
@GET("posts")
suspend fun getPosts(
    @Query("userId") userId: Int? = null,
    @Query("_limit") limit: Int = 10
): List<Post>

// ❌ Неправильно: без default, клиент должен всегда передавать
@GET("posts")
suspend fun getPosts(
    @Query("userId") userId: Int,
    @Query("_limit") limit: Int
): List<Post>
```

### Лучшие Практики

1. **Используйте suspend функции** с корутинами вместо Call<T>
2. **Оборачивайте в Result/Either** для обработки ошибок
3. **Выносите в Repository** — не вызывайте API напрямую из ViewModel
4. **Логируйте только в DEBUG** — HttpLoggingInterceptor с проверкой BuildConfig
5. **Добавляйте timeouts** в OkHttp (connectTimeout, readTimeout)

## Answer (EN)

Retrofit is a type-safe HTTP client for Android. The core concept: you describe the API through an interface with annotations, and Retrofit generates the implementation.

### Key Steps

**1. Add dependencies**

```gradle
// app/build.gradle
dependencies {
    implementation 'com.squareup.retrofit2:retrofit:2.9.0'
    implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
    implementation 'com.squareup.okhttp3:logging-interceptor:4.11.0'
}
```

**2. Create data model**

```kotlin
data class User(
    val id: Int,
    val name: String,
    val email: String
)
```

**3. Define API interface**

```kotlin
interface ApiService {
    @GET("users")
    suspend fun getUsers(): List<User>

    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: Int): User

    @POST("users")
    suspend fun createUser(@Body user: User): User
}
```

**Retrofit annotations**:
- `@GET`, `@POST`, `@PUT`, `@DELETE` — HTTP methods
- `@Path` — URL path parameter (users/{id})
- `@Query` — query parameters (?userId=123)
- `@Body` — request body (JSON)
- `@Header` — request header

**4. Create Retrofit instance**

```kotlin
object RetrofitClient {
    private const val BASE_URL = "https://api.example.com/"

    // ✅ Correct: OkHttp with logging for debugging
    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(HttpLoggingInterceptor().apply {
            level = if (BuildConfig.DEBUG) {
                HttpLoggingInterceptor.Level.BODY
            } else {
                HttpLoggingInterceptor.Level.NONE
            }
        })
        .addInterceptor { chain ->
            val request = chain.request().newBuilder()
                .addHeader("Content-Type", "application/json")
                .build()
            chain.proceed(request)
        }
        .build()

    val apiService: ApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }
}
```

**5. Use in Repository**

```kotlin
class UserRepository {
    private val api = RetrofitClient.apiService

    suspend fun getUsers(): Result<List<User>> = try {
        Result.Success(api.getUsers())
    } catch (e: HttpException) {
        Result.Error("HTTP ${e.code()}: ${e.message()}")
    } catch (e: IOException) {
        Result.Error("Network error: ${e.message}")
    }
}

sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
}
```

**6. Call from ViewModel**

```kotlin
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _users = MutableLiveData<List<User>>()
    val users: LiveData<List<User>> = _users

    fun loadUsers() {
        viewModelScope.launch {
            when (val result = repository.getUsers()) {
                is Result.Success -> _users.value = result.data
                is Result.Error -> /* show error */
            }
        }
    }
}
```

### Special Cases

**Form URL Encoded (login)**

```kotlin
@FormUrlEncoded
@POST("login")
suspend fun login(
    @Field("username") username: String,
    @Field("password") password: String
): LoginResponse
```

**Multipart (file uploads)**

```kotlin
@Multipart
@POST("upload")
suspend fun uploadFile(
    @Part file: MultipartBody.Part
): UploadResponse

// Usage
val requestFile = imageFile.asRequestBody("image/*".toMediaType())
val filePart = MultipartBody.Part.createFormData("image", imageFile.name, requestFile)
val response = api.uploadFile(filePart)
```

**Query parameters**

```kotlin
// ✅ Correct: optional parameters with defaults
@GET("posts")
suspend fun getPosts(
    @Query("userId") userId: Int? = null,
    @Query("_limit") limit: Int = 10
): List<Post>

// ❌ Wrong: no defaults, client must always provide
@GET("posts")
suspend fun getPosts(
    @Query("userId") userId: Int,
    @Query("_limit") limit: Int
): List<Post>
```

### Best Practices

1. **Use suspend functions** with coroutines instead of Call<T>
2. **Wrap in Result/Either** for error handling
3. **Extract to Repository** — don't call API directly from ViewModel
4. **Log only in DEBUG** — HttpLoggingInterceptor with BuildConfig check
5. **Add timeouts** in OkHttp (connectTimeout, readTimeout)

---

## Follow-ups

- How to handle authentication tokens with Retrofit interceptors?
- What's the difference between suspend functions and Call<T> in Retrofit?
- How to implement retry logic for failed network requests?
- When should you use @QueryMap vs individual @Query parameters?
- How to test Retrofit API calls with MockWebServer?

## References

- [[c-retrofit]] - Retrofit concept note
- [[c-okhttp]] - OkHttp concept note
- [[c-coroutines]] - Coroutines concept note
- [Retrofit Documentation](https://square.github.io/retrofit/)
- [OkHttp Interceptors](https://square.github.io/okhttp/interceptors/)

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-data-binding--android--easy]] - Android data binding basics
- [[q-graphql-vs-rest--networking--easy]] - REST API concepts

### Related (Medium)
- [[q-flow-testing-turbine--android--medium]] - Testing with Flow
- [[q-http-protocols-comparison--android--medium]] - HTTP protocols
- [[q-retrofit-path-parameter--android--medium]] - Retrofit path parameters
- [[q-retrofit-library--android--medium]] - Retrofit library overview
- [[q-kmm-ktor-networking--android--medium]] - KMM with Ktor

### Advanced (Harder)
- [[q-data-sync-unstable-network--android--hard]] - Network resilience
- [[q-retrofit-modify-all-requests--android--hard]] - Advanced Retrofit interceptors
