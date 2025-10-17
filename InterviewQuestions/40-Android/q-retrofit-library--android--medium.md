---
id: "20251015082237566"
title: "Retrofit Library / Библиотека Retrofit"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [retrofit, networking, rest-api, difficulty/medium]
---
# Что из себя представляет Retrofit?

**English**: What is Retrofit?

## Answer (EN)
Retrofit — это типобезопасный HTTP-клиент, разработанный компанией Square для Android и Java. Этот инструмент предназначен для упрощения процесса отправки сетевых запросов к RESTful API и обработки ответов сервера.

### Key Features

#### 1. Простота в использовании

Retrofit превращает HTTP API в Java/Kotlin интерфейс, что делает код более читаемым и легко поддерживаемым.

```kotlin
interface ApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: Int): User

    @POST("users")
    suspend fun createUser(@Body user: User): User

    @GET("users")
    suspend fun getUsers(@Query("page") page: Int): List<User>
}
```

#### 2. Data Conversion

Автоматически обрабатывает данные запросов и ответов с помощью конвертеров (Gson, Moshi, Jackson и др.).

```kotlin
// Создание Retrofit instance с Gson конвертером
val retrofit = Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .addConverterFactory(GsonConverterFactory.create())
    .build()

val apiService = retrofit.create(ApiService::class.java)

// Data class автоматически сериализуется/десериализуется
data class User(
    val id: Int,
    val name: String,
    val email: String
)
```

#### 3. Asynchronous and Synchronous Calls

Поддерживаются как синхронные, так и асинхронные вызовы API.

```kotlin
// Асинхронный вызов с корутинами (современный подход)
lifecycleScope.launch {
    try {
        val user = apiService.getUser(123)
        updateUI(user)
    } catch (e: Exception) {
        handleError(e)
    }
}

// Асинхронный вызов с callback (устаревший подход)
interface ApiService {
    @GET("users/{id}")
    fun getUser(@Path("id") userId: Int): Call<User>
}

apiService.getUser(123).enqueue(object : Callback<User> {
    override fun onResponse(call: Call<User>, response: Response<User>) {
        if (response.isSuccessful) {
            val user = response.body()
            updateUI(user)
        }
    }

    override fun onFailure(call: Call<User>, t: Throwable) {
        handleError(t)
    }
})
```

#### 4. Customizability

Благодаря использованию OkHttp в качестве сетевого клиента, Retrofit предлагает расширенные возможности по настройке HTTP-клиентов.

```kotlin
// Кастомная настройка OkHttp
val okHttpClient = OkHttpClient.Builder()
    .connectTimeout(30, TimeUnit.SECONDS)
    .readTimeout(30, TimeUnit.SECONDS)
    .addInterceptor(HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    })
    .addInterceptor { chain ->
        val request = chain.request().newBuilder()
            .addHeader("Authorization", "Bearer $token")
            .build()
        chain.proceed(request)
    }
    .build()

val retrofit = Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .client(okHttpClient)
    .addConverterFactory(GsonConverterFactory.create())
    .build()
```

### Complete Usage Example

```kotlin
// 1. Определение API интерфейса
interface GitHubService {
    @GET("users/{username}")
    suspend fun getUser(@Path("username") username: String): GitHubUser

    @GET("users/{username}/repos")
    suspend fun getRepos(
        @Path("username") username: String,
        @Query("sort") sort: String = "updated"
    ): List<Repository>
}

// 2. Создание Retrofit instance
object RetrofitClient {
    private const val BASE_URL = "https://api.github.com/"

    val apiService: GitHubService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(GitHubService::class.java)
    }
}

// 3. Использование в ViewModel
class UserViewModel : ViewModel() {
    private val _user = MutableLiveData<GitHubUser>()
    val user: LiveData<GitHubUser> = _user

    fun loadUser(username: String) {
        viewModelScope.launch {
            try {
                val result = RetrofitClient.apiService.getUser(username)
                _user.value = result
            } catch (e: Exception) {
                // Handle error
            }
        }
    }
}

// 4. Использование в Activity/Fragment
class MainActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        viewModel.user.observe(this) { user ->
            textView.text = user.name
        }

        viewModel.loadUser("square")
    }
}
```

### Аннотации HTTP методов

```kotlin
interface ApiService {
    @GET("endpoint")          // GET запрос
    @POST("endpoint")         // POST запрос
    @PUT("endpoint")          // PUT запрос
    @DELETE("endpoint")       // DELETE запрос
    @PATCH("endpoint")        // PATCH запрос
    @HEAD("endpoint")         // HEAD запрос
    @OPTIONS("endpoint")      // OPTIONS запрос

    @FormUrlEncoded          // Отправка форм
    @POST("login")
    suspend fun login(
        @Field("username") username: String,
        @Field("password") password: String
    ): LoginResponse

    @Multipart               // Загрузка файлов
    @POST("upload")
    suspend fun uploadFile(
        @Part("description") description: RequestBody,
        @Part file: MultipartBody.Part
    ): UploadResponse
}
```

### Обработка ошибок

```kotlin
suspend fun safeApiCall(): Result<User> {
    return try {
        val response = apiService.getUser(123)
        Result.success(response)
    } catch (e: HttpException) {
        // HTTP ошибка (4xx, 5xx)
        Result.failure(e)
    } catch (e: IOException) {
        // Сетевая ошибка
        Result.failure(e)
    } catch (e: Exception) {
        // Другие ошибки
        Result.failure(e)
    }
}
```

**English**: Retrofit is a type-safe HTTP client for Android and Java developed by Square. It converts HTTP APIs into Java/Kotlin interfaces, automatically handles request/response data conversion (Gson, Moshi), supports async/sync calls, and offers extensive customization through OkHttp (caching, timeouts, interceptors).
