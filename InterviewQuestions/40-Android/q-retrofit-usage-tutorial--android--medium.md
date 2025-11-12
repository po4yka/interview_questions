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
related: [q-flow-testing-turbine--android--medium, q-what-is-data-binding--android--easy]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/architecture-mvvm, android/coroutines, android/networking-http, difficulty/medium, networking, retrofit]

---

# Вопрос (RU)

> Как делать сетевые запросы с помощью Retrofit?

# Question (EN)

> How to make network requests with Retrofit?

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

    // suspend-функции Retrofit выбрасывают HttpException для неуспешных HTTP ответов (не 2xx)
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

**6. Вызвать из `ViewModel`**

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
// ✅ Пример: опциональные параметры с default значениями для удобного вызова
@GET("posts")
suspend fun getPosts(
    @Query("userId") userId: Int? = null,
    @Query("_limit") limit: Int = 10
): List<Post>

// ✅ Также валидно: без значений по умолчанию, если API требует явной передачи
@GET("posts")
suspend fun getPostsRequired(
    @Query("userId") userId: Int,
    @Query("_limit") limit: Int
): List<Post>
```

### Лучшие Практики

1. Используйте suspend-функции с корутинами вместо `Call<T>`, если вы уже на coroutines stack
2. Оборачивайте результаты в Result/Either для централизованной обработки ошибок
3. Выносите сетевую логику в Repository — не вызывайте API напрямую из `ViewModel`
4. Логируйте только в DEBUG — HttpLoggingInterceptor с проверкой BuildConfig
5. Добавляйте timeouts в OkHttp (connectTimeout, readTimeout)

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

    // Retrofit suspend functions throw HttpException for non-successful HTTP responses (non-2xx)
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

**6. Call from `ViewModel`**

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
// ✅ Example: optional parameters with defaults for convenient calls
@GET("posts")
suspend fun getPosts(
    @Query("userId") userId: Int? = null,
    @Query("_limit") limit: Int = 10
): List<Post>

// ✅ Also valid: no defaults when your API requires explicit values
@GET("posts")
suspend fun getPostsRequired(
    @Query("userId") userId: Int,
    @Query("_limit") limit: Int
): List<Post>
```

### Best Practices

1. Use suspend functions with coroutines instead of `Call<T>` when you are on a coroutines-based stack
2. Wrap results in Result/Either for centralized error handling
3. Extract networking into a Repository — don't call the API directly from the `ViewModel`
4. Log only in DEBUG — HttpLoggingInterceptor with a BuildConfig check
5. Add timeouts in OkHttp (connectTimeout, readTimeout)

---

## Дополнительные вопросы (RU)

- Как обрабатывать токены аутентификации с помощью интерсепторов Retrofit?
- В чем разница между suspend-функциями и `Call<T>` в Retrofit?
- Как реализовать логику повторных попыток для неудачных сетевых запросов?
- Когда стоит использовать `@QueryMap` вместо отдельных `@Query` параметров?
- Как тестировать вызовы Retrofit с помощью MockWebServer?

## Ссылки (RU)

- Официальная документация Retrofit: https://square.github.io/retrofit/
- Документация по OkHttp Interceptors: https://square.github.io/okhttp/interceptors/

## Связанные вопросы (RU)

### База (проще)
- [[q-what-is-data-binding--android--easy]] - Базовые концепции data binding в Android

### Связанные (средние)
- [[q-flow-testing-turbine--android--medium]] - Тестирование с использованием `Flow`

---

## Follow-ups

- How to handle authentication tokens with Retrofit interceptors?
- What's the difference between suspend functions and `Call<T>` in Retrofit?
- How to implement retry logic for failed network requests?
- When should you use `@QueryMap` vs individual `@Query` parameters?
- How to test Retrofit API calls with MockWebServer?

## References

- [Retrofit Documentation](https://square.github.io/retrofit/)
- [OkHttp Interceptors](https://square.github.io/okhttp/interceptors/)

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-data-binding--android--easy]] - Android data binding basics

### Related (Medium)
- [[q-flow-testing-turbine--android--medium]] - Testing with `Flow`
