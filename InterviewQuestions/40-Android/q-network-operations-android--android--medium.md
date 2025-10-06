---
topic: android
tags:
  - android
  - networking
  - http
difficulty: medium
---

# Что используется для работы с сетью в Android?

**English**: What is used for network operations in Android?

## Answer

Для работы с сетью в Android используются различные библиотеки и инструменты, обеспечивающие выполнение сетевых запросов, обработку ответов и управление асинхронными операциями.

### Основные инструменты

#### 1. HttpURLConnection (встроенный)

Базовый инструмент для простых HTTP запросов.

```kotlin
fun fetchData(): String {
    val url = URL("https://api.example.com/data")
    val connection = url.openConnection() as HttpURLConnection

    try {
        connection.requestMethod = "GET"
        connection.connectTimeout = 5000
        connection.readTimeout = 5000

        val responseCode = connection.responseCode
        if (responseCode == HttpURLConnection.HTTP_OK) {
            val inputStream = connection.inputStream
            return inputStream.bufferedReader().use { it.readText() }
        }
    } finally {
        connection.disconnect()
    }

    return ""
}
```

**Минусы:**
- Много boilerplate кода
- Нет автоматической конвертации JSON
- Сложно управлять async операциями

#### 2. OkHttp (рекомендуется)

Мощный HTTP клиент от Square.

```kotlin
// Зависимость
// implementation 'com.squareup.okhttp3:okhttp:4.11.0'

val client = OkHttpClient.Builder()
    .connectTimeout(30, TimeUnit.SECONDS)
    .readTimeout(30, TimeUnit.SECONDS)
    .addInterceptor(HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    })
    .build()

fun fetchData() {
    val request = Request.Builder()
        .url("https://api.example.com/data")
        .get()
        .build()

    client.newCall(request).enqueue(object : Callback {
        override fun onFailure(call: Call, e: IOException) {
            // Ошибка сети
        }

        override fun onResponse(call: Call, response: Response) {
            response.use {
                if (it.isSuccessful) {
                    val body = it.body?.string()
                    // Обработка ответа
                }
            }
        }
    })
}
```

**Преимущества:**
- Эффективное управление соединениями
- Connection pooling
- Автоматические retry
- Поддержка HTTP/2
- WebSocket support

#### 3. Retrofit (самый популярный)

Type-safe HTTP клиент, использует OkHttp внутри.

```kotlin
// Зависимости
// implementation 'com.squareup.retrofit2:retrofit:2.9.0'
// implementation 'com.squareup.retrofit2:converter-gson:2.9.0'

// API интерфейс
interface ApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: Int): User

    @POST("users")
    suspend fun createUser(@Body user: User): User

    @GET("users")
    suspend fun getUsers(
        @Query("page") page: Int,
        @Query("limit") limit: Int
    ): List<User>
}

// Создание Retrofit
val retrofit = Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .addConverterFactory(GsonConverterFactory.create())
    .client(okHttpClient)
    .build()

val apiService = retrofit.create(ApiService::class.java)

// Использование с корутинами
lifecycleScope.launch {
    try {
        val user = apiService.getUser(123)
        updateUI(user)
    } catch (e: Exception) {
        handleError(e)
    }
}
```

#### 4. Volley (от Google)

Библиотека для быстрых небольших запросов.

```kotlin
// implementation 'com.android.volley:volley:1.2.1'

val queue = Volley.newRequestQueue(context)

val request = StringRequest(
    Request.Method.GET,
    "https://api.example.com/data",
    { response ->
        // Успешный ответ
        Log.d("Response", response)
    },
    { error ->
        // Ошибка
        Log.e("Error", error.toString())
    }
)

queue.add(request)
```

**Особенности:**
- Автоматическое кэширование
- Приоритизация запросов
- Отмена запросов
- Хорошо для множества мелких запросов

#### 5. Ktor Client (Kotlin-first)

Асинхронный HTTP клиент для Kotlin.

```kotlin
// implementation("io.ktor:ktor-client-android:2.3.0")
// implementation("io.ktor:ktor-client-content-negotiation:2.3.0")

val client = HttpClient(Android) {
    install(ContentNegotiation) {
        json()
    }
}

suspend fun fetchUser(id: Int): User {
    return client.get("https://api.example.com/users/$id").body()
}
```

### Сравнительная таблица

| Библиотека | Простота | Производительность | Функциональность | Use Case |
|------------|----------|-------------------|------------------|----------|
| **HttpURLConnection** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | Простые запросы |
| **OkHttp** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Гибкий HTTP клиент |
| **Retrofit** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | RESTful API |
| **Volley** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | Множество мелких запросов |
| **Ktor** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Kotlin multiplatform |

### Важные правила

**1. Сетевые операции в фоновом потоке**

```kotlin
// ❌ НЕПРАВИЛЬНО - в main thread
button.setOnClickListener {
    val data = fetchData()  // NetworkOnMainThreadException!
}

// ✓ ПРАВИЛЬНО - в фоновом потоке
button.setOnClickListener {
    lifecycleScope.launch(Dispatchers.IO) {
        val data = fetchData()
        withContext(Dispatchers.Main) {
            updateUI(data)
        }
    }
}
```

**2. Разрешения в манифесте**

```xml
<manifest>
    <!-- Обязательно! -->
    <uses-permission android:name="android.permission.INTERNET" />

    <!-- Опционально для проверки состояния сети -->
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
</manifest>
```

**3. HTTPS вместо HTTP**

```kotlin
// Android 9+ блокирует cleartext (HTTP) по умолчанию
// Используйте HTTPS!
const val BASE_URL = "https://api.example.com/"  // ✓
const val BASE_URL = "http://api.example.com/"   // ❌
```

**4. Обработка ошибок**

```kotlin
suspend fun safeApiCall(): Result<User> {
    return try {
        val user = apiService.getUser(123)
        Result.success(user)
    } catch (e: HttpException) {
        // HTTP ошибка (4xx, 5xx)
        Result.failure(e)
    } catch (e: IOException) {
        // Сетевая ошибка (нет интернета)
        Result.failure(e)
    } catch (e: Exception) {
        // Другие ошибки
        Result.failure(e)
    }
}
```

### Проверка интернет-соединения

```kotlin
fun isNetworkAvailable(context: Context): Boolean {
    val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE)
        as ConnectivityManager

    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
        val network = connectivityManager.activeNetwork ?: return false
        val capabilities = connectivityManager.getNetworkCapabilities(network)
            ?: return false

        return capabilities.hasCapability(
            NetworkCapabilities.NET_CAPABILITY_INTERNET
        )
    } else {
        @Suppress("DEPRECATION")
        val networkInfo = connectivityManager.activeNetworkInfo
        @Suppress("DEPRECATION")
        return networkInfo?.isConnected == true
    }
}
```

### Рекомендации

**Для большинства приложений:**
```kotlin
// Retrofit + OkHttp + Gson/Moshi + Coroutines
```

**Для простых запросов:**
```kotlin
// OkHttp
```

**Для Kotlin Multiplatform:**
```kotlin
// Ktor Client
```

**English**: Android network operations use: **HttpURLConnection** (basic, built-in), **OkHttp** (powerful HTTP client with connection pooling, HTTP/2), **Retrofit** (most popular, type-safe REST client), **Volley** (Google's library for multiple small requests), **Ktor** (Kotlin-first async client). Must run on background thread, require INTERNET permission, prefer HTTPS. Retrofit + OkHttp recommended for most apps.
