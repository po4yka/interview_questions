---
id: android-283
title: "Network Operations Android / Сетевые операции в Android"
aliases: ["Network Operations Android", "Сетевые операции в Android"]
topic: android
subtopics: [networking-http]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-app-components--android--easy, q-koin-vs-hilt-comparison--dependency-injection--medium, q-what-does-the-lifecycle-library-do--android--medium]
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android/networking-http, difficulty/medium, http, networking]

---

# Вопрос (RU)

> Какие инструменты используются для работы с сетью в Android?

# Question (EN)

> What tools are used for network operations in Android?

---

## Ответ (RU)

В Android используется несколько библиотек для сетевых операций: от встроенного HttpURLConnection до современных решений вроде Retrofit и Ktor.

### Основные Инструменты

**HttpURLConnection** — встроенный базовый HTTP-клиент. Требует много boilerplate-кода, нет автоматического парсинга JSON, сложно управлять асинхронностью.

**OkHttp** — мощный HTTP-клиент от Square. Эффективный connection pooling, автоматический retry, поддержка HTTP/2 и WebSocket. Используется как базовый транспорт для Retrofit.

**Retrofit** — наиболее популярный тайп-сейф REST-клиент. Декларативный API через аннотации, интеграция с Kotlin coroutines, автоматическая сериализация/десериализация.

```kotlin
// Retrofit API interface
interface ApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: Int): User

    @POST("users")
    suspend fun createUser(@Body user: User): User
}

// Создание клиента
val retrofit = Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .addConverterFactory(GsonConverterFactory.create())
    .client(okHttpClient)
    .build()

// ✅ Использование с coroutines
lifecycleScope.launch {
    try {
        val user = apiService.getUser(123)
        updateUI(user)
    } catch (e: Exception) {
        handleError(e)
    }
}
```

**Volley** — библиотека от Google для множества мелких запросов. Автоматическое кеширование, приоритезация запросов, встроенная поддержка изображений.

**Ktor Client** — асинхронный Kotlin-first клиент для Kotlin Multiplatform проектов. Корутины из коробки, расширяемая архитектура через plugins.

### Критические Правила

**Фоновый поток обязателен**

```kotlin
// ❌ НЕПРАВИЛЬНО - NetworkOnMainThreadException
button.setOnClickListener {
    val data = fetchData()
}

// ✅ ПРАВИЛЬНО - Dispatchers.IO
button.setOnClickListener {
    lifecycleScope.launch(Dispatchers.IO) {
        val data = fetchData()
        withContext(Dispatchers.Main) {
            updateUI(data)
        }
    }
}
```

**Манифест permissions**

```xml
<manifest>
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
</manifest>
```

**HTTPS required**

```kotlin
// ✅ Android 9+ требует HTTPS по умолчанию
const val BASE_URL = "https://api.example.com/"

// ❌ HTTP блокируется (cleartext traffic)
const val BASE_URL = "http://api.example.com/"
```

**Error handling**

```kotlin
suspend fun safeApiCall(): Result<User> {
    return try {
        Result.success(apiService.getUser(123))
    } catch (e: HttpException) {
        // HTTP ошибка 4xx/5xx
        Result.failure(e)
    } catch (e: IOException) {
        // Сетевая ошибка (нет интернета)
        Result.failure(e)
    }
}
```

### Проверка Сети

```kotlin
fun isNetworkAvailable(context: Context): Boolean {
    val cm = context.getSystemService<ConnectivityManager>() ?: return false

    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
        val network = cm.activeNetwork ?: return false
        val capabilities = cm.getNetworkCapabilities(network) ?: return false
        return capabilities.hasCapability(NET_CAPABILITY_INTERNET)
    } else {
        return cm.activeNetworkInfo?.isConnected == true
    }
}
```

### Рекомендации

**Для большинства приложений**: Retrofit + OkHttp + Gson/Moshi + Coroutines

**Для простых запросов**: OkHttp напрямую

**Для Kotlin Multiplatform**: Ktor Client

---

## Answer (EN)

Android uses several libraries for network operations: from built-in HttpURLConnection to modern solutions like Retrofit and Ktor.

### Core Tools

**HttpURLConnection** — built-in basic HTTP client. Requires lots of boilerplate, no automatic JSON parsing, difficult async management.

**OkHttp** — powerful HTTP client from Square. Efficient connection pooling, automatic retry, HTTP/2 and WebSocket support. Used as transport layer for Retrofit.

**Retrofit** — most popular type-safe REST client. Declarative API via annotations, Kotlin coroutines integration, automatic serialization/deserialization.

```kotlin
// Retrofit API interface
interface ApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: Int): User

    @POST("users")
    suspend fun createUser(@Body user: User): User
}

// Create client
val retrofit = Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .addConverterFactory(GsonConverterFactory.create())
    .client(okHttpClient)
    .build()

// ✅ Usage with coroutines
lifecycleScope.launch {
    try {
        val user = apiService.getUser(123)
        updateUI(user)
    } catch (e: Exception) {
        handleError(e)
    }
}
```

**Volley** — Google's library for multiple small requests. Automatic caching, request prioritization, built-in image support.

**Ktor Client** — asynchronous Kotlin-first client for Kotlin Multiplatform. Coroutines out of the box, extensible architecture through plugins.

### Critical Rules

**Background thread required**

```kotlin
// ❌ WRONG - NetworkOnMainThreadException
button.setOnClickListener {
    val data = fetchData()
}

// ✅ CORRECT - Dispatchers.IO
button.setOnClickListener {
    lifecycleScope.launch(Dispatchers.IO) {
        val data = fetchData()
        withContext(Dispatchers.Main) {
            updateUI(data)
        }
    }
}
```

**Manifest permissions**

```xml
<manifest>
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
</manifest>
```

**HTTPS required**

```kotlin
// ✅ Android 9+ requires HTTPS by default
const val BASE_URL = "https://api.example.com/"

// ❌ HTTP blocked (cleartext traffic)
const val BASE_URL = "http://api.example.com/"
```

**Error handling**

```kotlin
suspend fun safeApiCall(): Result<User> {
    return try {
        Result.success(apiService.getUser(123))
    } catch (e: HttpException) {
        // HTTP error 4xx/5xx
        Result.failure(e)
    } catch (e: IOException) {
        // Network error (no internet)
        Result.failure(e)
    }
}
```

### Network Checking

```kotlin
fun isNetworkAvailable(context: Context): Boolean {
    val cm = context.getSystemService<ConnectivityManager>() ?: return false

    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
        val network = cm.activeNetwork ?: return false
        val capabilities = cm.getNetworkCapabilities(network) ?: return false
        return capabilities.hasCapability(NET_CAPABILITY_INTERNET)
    } else {
        return cm.activeNetworkInfo?.isConnected == true
    }
}
```

### Recommendations

**For most apps**: Retrofit + OkHttp + Gson/Moshi + Coroutines

**For simple requests**: OkHttp directly

**For Kotlin Multiplatform**: Ktor Client

---

## Follow-ups

- How to implement retry logic with exponential backoff?
- What's the difference between OkHttp interceptors and Retrofit converters?
- How to handle certificate pinning for security?
- How to implement request deduplication for concurrent identical requests?
- What are the best practices for caching network responses?

## References

- [[c-retrofit]] - Type-safe HTTP client for Android
- [[c-okhttp]] - HTTP client library fundamentals
-  - Asynchronous programming in Kotlin
- [Android Developers: Connect to the network](https://developer.android.com/training/basics/network-ops/connecting)
- [Retrofit documentation](https://square.github.io/retrofit/)
- [OkHttp documentation](https://square.github.io/okhttp/)

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - Understanding Android components
- [[q-graphql-vs-rest--networking--easy]] - API architecture comparison

### Related (Medium)
- [[q-what-does-the-lifecycle-library-do--android--medium]] - `Lifecycle`-aware networking
- [[q-http-protocols-comparison--android--medium]] - HTTP protocol details
- [[q-network-error-handling-strategies--networking--medium]] - Error handling patterns
- [[q-kmm-ktor-networking--android--medium]] - Multiplatform networking
- [[q-api-file-upload-server--android--medium]] - File upload implementation

### Advanced (Harder)
- [[q-data-sync-unstable-network--android--hard]] - Sync strategies
- [[q-network-request-deduplication--networking--hard]] - Request optimization
