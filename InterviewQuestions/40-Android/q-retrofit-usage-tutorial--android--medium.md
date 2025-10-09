---
topic: android
tags:
  - android
  - retrofit
  - networking
  - tutorial
difficulty: medium
status: reviewed
---

# Как делать сетевые запросы с помощью Retrofit?

**English**: How to make network requests with Retrofit?

## Answer

Retrofit — это type-safe HTTP клиент для Android и Java. Вот пошаговое руководство по его использованию.

### Шаг 1: Добавление зависимостей

```gradle
// app/build.gradle
dependencies {
    // Retrofit
    implementation 'com.squareup.retrofit2:retrofit:2.9.0'

    // Конвертер JSON (выберите один)
    implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
    // или Moshi
    // implementation 'com.squareup.retrofit2:converter-moshi:2.9.0'

    // Для корутин (опционально)
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3'

    // Логирование (для отладки)
    implementation 'com.squareup.okhttp3:logging-interceptor:4.11.0'
}
```

### Шаг 2: Создание модели данных

```kotlin
// User.kt
data class User(
    val id: Int,
    val name: String,
    val email: String,
    val username: String
)

// Post.kt
data class Post(
    val userId: Int,
    val id: Int,
    val title: String,
    val body: String
)

// Для POST запросов
data class CreateUserRequest(
    val name: String,
    val email: String
)
```

### Шаг 3: Определение API интерфейса

```kotlin
// ApiService.kt
interface ApiService {
    // GET запрос
    @GET("users")
    suspend fun getUsers(): List<User>

    // GET с параметром в пути
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: Int): User

    // GET с query параметрами
    @GET("posts")
    suspend fun getPosts(
        @Query("userId") userId: Int,
        @Query("_limit") limit: Int = 10
    ): List<Post>

    // POST запрос
    @POST("users")
    suspend fun createUser(@Body user: CreateUserRequest): User

    // PUT запрос
    @PUT("users/{id}")
    suspend fun updateUser(
        @Path("id") userId: Int,
        @Body user: User
    ): User

    // DELETE запрос
    @DELETE("users/{id}")
    suspend fun deleteUser(@Path("id") userId: Int): Response<Unit>

    // Заголовки
    @GET("users/{id}")
    suspend fun getUserWithAuth(
        @Path("id") userId: Int,
        @Header("Authorization") token: String
    ): User

    // Несколько query параметров
    @GET("search")
    suspend fun search(
        @QueryMap parameters: Map<String, String>
    ): List<User>
}
```

### Шаг 4: Создание Retrofit instance

```kotlin
// RetrofitClient.kt
object RetrofitClient {
    private const val BASE_URL = "https://jsonplaceholder.typicode.com/"

    // OkHttp клиент с логированием
    private val okHttpClient = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .addInterceptor(HttpLoggingInterceptor().apply {
            level = if (BuildConfig.DEBUG) {
                HttpLoggingInterceptor.Level.BODY
            } else {
                HttpLoggingInterceptor.Level.NONE
            }
        })
        .addInterceptor { chain ->
            // Добавление headers ко всем запросам
            val request = chain.request().newBuilder()
                .addHeader("Content-Type", "application/json")
                .addHeader("Accept", "application/json")
                .build()
            chain.proceed(request)
        }
        .build()

    // Retrofit instance
    val retrofit: Retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()

    // API Service
    val apiService: ApiService by lazy {
        retrofit.create(ApiService::class.java)
    }
}
```

### Шаг 5: Использование в ViewModel

```kotlin
// UserViewModel.kt
class UserViewModel : ViewModel() {
    private val apiService = RetrofitClient.apiService

    private val _users = MutableLiveData<List<User>>()
    val users: LiveData<List<User>> = _users

    private val _error = MutableLiveData<String>()
    val error: LiveData<String> = _error

    private val _loading = MutableLiveData<Boolean>()
    val loading: LiveData<Boolean> = _loading

    fun loadUsers() {
        viewModelScope.launch {
            _loading.value = true
            try {
                val result = apiService.getUsers()
                _users.value = result
            } catch (e: HttpException) {
                // HTTP ошибка (4xx, 5xx)
                _error.value = "HTTP Error: ${e.code()}"
            } catch (e: IOException) {
                // Сетевая ошибка
                _error.value = "Network Error: ${e.message}"
            } catch (e: Exception) {
                // Другие ошибки
                _error.value = "Error: ${e.message}"
            } finally {
                _loading.value = false
            }
        }
    }

    fun createUser(name: String, email: String) {
        viewModelScope.launch {
            try {
                val request = CreateUserRequest(name, email)
                val newUser = apiService.createUser(request)
                // Обновить список пользователей
                _users.value = _users.value?.plus(newUser)
            } catch (e: Exception) {
                _error.value = e.message
            }
        }
    }
}
```

### Шаг 6: Использование в Activity/Fragment

```kotlin
// MainActivity.kt
class MainActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()
    private lateinit var adapter: UserAdapter

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        setupRecyclerView()
        observeViewModel()

        // Загрузить данные
        viewModel.loadUsers()
    }

    private fun setupRecyclerView() {
        adapter = UserAdapter()
        recyclerView.apply {
            layoutManager = LinearLayoutManager(this@MainActivity)
            adapter = this@MainActivity.adapter
        }
    }

    private fun observeViewModel() {
        // Наблюдение за пользователями
        viewModel.users.observe(this) { users ->
            adapter.submitList(users)
        }

        // Наблюдение за загрузкой
        viewModel.loading.observe(this) { isLoading ->
            progressBar.isVisible = isLoading
        }

        // Наблюдение за ошибками
        viewModel.error.observe(this) { errorMessage ->
            Toast.makeText(this, errorMessage, Toast.LENGTH_LONG).show()
        }
    }
}
```

### Обработка различных типов запросов

#### Form URL Encoded

```kotlin
interface ApiService {
    @FormUrlEncoded
    @POST("login")
    suspend fun login(
        @Field("username") username: String,
        @Field("password") password: String
    ): LoginResponse
}

// Использование
val response = apiService.login("user@example.com", "password123")
```

#### Multipart (Загрузка файлов)

```kotlin
interface ApiService {
    @Multipart
    @POST("upload")
    suspend fun uploadFile(
        @Part("description") description: RequestBody,
        @Part file: MultipartBody.Part
    ): UploadResponse
}

// Использование
fun uploadImage(imageFile: File) {
    viewModelScope.launch {
        val requestFile = imageFile.asRequestBody("image/*".toMediaType())
        val filePart = MultipartBody.Part.createFormData(
            "image",
            imageFile.name,
            requestFile
        )
        val description = "Profile picture".toRequestBody("text/plain".toMediaType())

        val response = apiService.uploadFile(description, filePart)
    }
}
```

#### Headers

```kotlin
interface ApiService {
    // Статический header
    @Headers("Cache-Control: max-age=640000")
    @GET("users")
    suspend fun getUsers(): List<User>

    // Динамический header
    @GET("users/{id}")
    suspend fun getUserWithToken(
        @Path("id") userId: Int,
        @Header("Authorization") token: String
    ): User

    // Множественные headers
    @GET("users")
    suspend fun getUsersWithHeaders(
        @HeaderMap headers: Map<String, String>
    ): List<User>
}
```

### Обработка ошибок с sealed class

```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val exception: Exception) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

class UserRepository {
    suspend fun getUsers(): Result<List<User>> {
        return try {
            Result.Loading
            val users = RetrofitClient.apiService.getUsers()
            Result.Success(users)
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
}

// В ViewModel
viewModelScope.launch {
    when (val result = repository.getUsers()) {
        is Result.Success -> _users.value = result.data
        is Result.Error -> _error.value = result.exception.message
        is Result.Loading -> _loading.value = true
    }
}
```

### Полный пример с Repository pattern

```kotlin
// UserRepository.kt
class UserRepository {
    private val apiService = RetrofitClient.apiService

    suspend fun getUsers(): List<User> {
        return withContext(Dispatchers.IO) {
            apiService.getUsers()
        }
    }

    suspend fun getUserById(id: Int): User {
        return withContext(Dispatchers.IO) {
            apiService.getUser(id)
        }
    }
}

// UserViewModel.kt
class UserViewModel(
    private val repository: UserRepository = UserRepository()
) : ViewModel() {

    private val _users = MutableLiveData<List<User>>()
    val users: LiveData<List<User>> = _users

    fun loadUsers() {
        viewModelScope.launch {
            try {
                val result = repository.getUsers()
                _users.value = result
            } catch (e: Exception) {
                // Handle error
            }
        }
    }
}
```

**English**: Retrofit usage steps: 1) Add dependencies (Retrofit + converter), 2) Create data models, 3) Define API interface with annotations (@GET, @POST, @Path, @Query, @Body), 4) Create Retrofit instance with baseUrl and converter, 5) Use in ViewModel with coroutines, 6) Observe in Activity/Fragment. Supports form-urlencoded, multipart uploads, headers, and error handling with sealed classes.
