---
id: android-283
title: Network Operations Android / Сетевые операции в Android
aliases:
- Network Operations Android
- Сетевые операции в Android
topic: android
subtopics:
- networking-http
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-android-components
- q-android-app-components--android--easy
- q-what-does-the-lifecycle-library-do--android--medium
created: 2025-10-15
updated: 2025-11-10
sources: []
tags:
- android/networking-http
- difficulty/medium
- http
- networking
anki_cards:
- slug: android-283-0-en
  language: en
  anki_id: 1768398016656
  synced_at: '2026-01-23T16:45:06.013221'
- slug: android-283-0-ru
  language: ru
  anki_id: 1768398016681
  synced_at: '2026-01-23T16:45:06.014787'
---
# Вопрос (RU)

> Какие инструменты используются для сетевых операций в Android?

# Question (EN)

> What tools are used for network operations in Android?

---

## Ответ (RU)

В Android для сетевых операций используются как встроенные средства, так и популярные библиотеки: от низкоуровневого `HttpURLConnection` до современных решений вроде `OkHttp`, `Retrofit` и `Ktor` (см. также [[c-android-components]]).

### Основные Инструменты

**HttpURLConnection** — встроенный низкоуровневый HTTP-клиент. Требует много шаблонного кода, не имеет встроенного маппинга JSON и выполняет блокирующие вызовы, которые нельзя делать на главном потоке.

**`OkHttp`** — мощный HTTP-клиент от Square. Обеспечивает эффективный пул соединений, обработку редиректов/повторов, поддержку HTTP/2 и WebSocket, гибкую систему интерсепторов. Часто используется как транспортный слой для `Retrofit`.

**`Retrofit`** — популярный type-safe REST-клиент. Предоставляет декларативный API через аннотации, интеграцию с `Kotlin coroutines`/suspend-функциями, автоматическую (де)сериализацию.

```kotlin
// Интерфейс API для Retrofit
interface ApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: Int): User

    @POST("users")
    suspend fun createUser(@Body user: User): User
}

// Создание Retrofit
val retrofit = Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .addConverterFactory(GsonConverterFactory.create())
    .client(okHttpClient)
    .build()

// Создание ApiService
val apiService = retrofit.create(ApiService::class.java)

// ✅ Использование с корутинами.
// suspend-вызовы Retrofit/Ktor не блокируют поток напрямую (они "блокируют" корутину),
// но по умолчанию вызываются на том диспетчере, с которого были вызваны.
// Поэтому синхронные/blocking вызовы execute() и другие блокирующие операции
// никогда нельзя выполнять на главном потоке — выносите их на Dispatchers.IO.
lifecycleScope.launch {
    try {
        val user = apiService.getUser(123)
        updateUI(user)
    } catch (e: Exception) {
        handleError(e)
    }
}
```

**Volley** — библиотека от Google, ориентированная на множество относительно небольших запросов. Предоставляет кэширование, приоритизацию запросов и вспомогательные средства для загрузки изображений.

**Ktor Client** — асинхронный Kotlin-first клиент для Kotlin Multiplatform. Из коробки использует корутины, расширяется через плагины.

### Критически Важные Правила

**Не блокировать главный поток сетевыми операциями**

```kotlin
// ❌ НЕПРАВИЛЬНО — для блокирующих вызовов это приведёт к NetworkOnMainThreadException
button.setOnClickListener {
    val data = fetchData() // прямой синхронный HTTP-вызов
}

// ✅ ПРАВИЛЬНО — использовать Dispatchers.IO (или другой фоновой диспетчер) для блокирующих вызовов
button.setOnClickListener {
    lifecycleScope.launch(Dispatchers.IO) {
        val data = fetchData()
        withContext(Dispatchers.Main) {
            updateUI(data)
        }
    }
}
```

Suspend-API `Retrofit`/`Ktor` спроектированы так, чтобы не блокировать главный поток (они работают через неблокирующую модель ввода-вывода и корутины), но если используются синхронные вызовы `execute()` или другие блокирующие клиенты, нужно выполнять их на `Dispatchers.IO`.

**Разрешения в манифесте**

```xml
<manifest>
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
</manifest>
```

**HTTPS по умолчанию (Android 9+)**

```kotlin
// ✅ Рекомендуется использовать HTTPS
const val BASE_URL = "https://api.example.com/"

// ⚠️ На Android 9+ cleartext HTTP (http://) по умолчанию ограничен политикой безопасности
// (используется cleartextTrafficPermitted=false), и его нужно явно разрешать
// через usesCleartextTraffic или networkSecurityConfig при необходимости.
const val BASE_URL_HTTP = "http://api.example.com/"
```

**Обработка ошибок**

```kotlin
suspend fun safeApiCall(): Result<User> {
    return try {
        Result.success(apiService.getUser(123))
    } catch (e: HttpException) {
        // HTTP-ошибки 4xx/5xx
        Result.failure(e)
    } catch (e: IOException) {
        // Сетевые ошибки (таймауты, отсутствие интернета и т.п.)
        Result.failure(e)
    }
}
```

### Проверка Доступности Сети

```kotlin
fun isNetworkAvailable(context: Context): Boolean {
    val cm = context.getSystemService<ConnectivityManager>() ?: return false

    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
        val network = cm.activeNetwork ?: return false
        val capabilities = cm.getNetworkCapabilities(network) ?: return false
        // Предпочтительно наличие INTERNET; при наличии также VALIDATED сеть прошла проверку.
        // Здесь мы требуем INTERNET и, если доступно, VALIDATED.
        capabilities.hasCapability(NET_CAPABILITY_INTERNET) &&
            capabilities.hasCapability(NET_CAPABILITY_VALIDATED)
    } else {
        cm.activeNetworkInfo?.isConnected == true
    }
}
```

(Примечание: даже при наличии доступной сети достижимость конкретного сервера не гарантирована, поэтому обработка ошибок на уровне HTTP-клиента обязательна.)

### Рекомендации

**Для большинства приложений**: `Retrofit` + `OkHttp` + `Gson`/`Moshi` + `Coroutines`

**Для простых сценариев**: прямое использование `OkHttp`

**Для Kotlin Multiplatform**: `Ktor Client`

---

## Answer (EN)

Android uses several libraries for network operations: from built-in HttpURLConnection to modern solutions like `Retrofit` and Ktor (see also [[c-android-components]]).

### Core Tools

**HttpURLConnection** is the built-in low-level HTTP client. Requires a lot of boilerplate, no built-in JSON mapping, and blocking calls must be off the main thread.

**`OkHttp`** is a powerful HTTP client from Square. Efficient connection pooling, robust redirect/retry handling, HTTP/2 and WebSocket support, rich interceptor system. Commonly used as the transport layer for `Retrofit`.

**`Retrofit`** is the most popular type-safe REST client. Declarative API via annotations, integration with Kotlin coroutines/suspend functions, automatic serialization/deserialization.

```kotlin
// Retrofit API interface
interface ApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: Int): User

    @POST("users")
    suspend fun createUser(@Body user: User): User
}

// Create Retrofit
val retrofit = Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .addConverterFactory(GsonConverterFactory.create())
    .client(okHttpClient)
    .build()

// Create ApiService
val apiService = retrofit.create(ApiService::class.java)

// ✅ Usage with coroutines.
// Retrofit/Ktor suspend calls do not block the thread directly (they "block" the coroutine),
// but by default run on the dispatcher from which they are invoked.
// Therefore, synchronous/blocking execute() calls and other blocking operations
// must never run on the main thread — move them to Dispatchers.IO.
lifecycleScope.launch {
    try {
        val user = apiService.getUser(123)
        updateUI(user)
    } catch (e: Exception) {
        handleError(e)
    }
}
```

**Volley** is Google's library intended for many small network requests. It provides automatic caching, request prioritization, and built-in image loading helpers.

**Ktor Client** is an asynchronous Kotlin-first client for Kotlin Multiplatform. Coroutines out of the box, extensible via plugins.

### Critical Rules

**Do not block the main thread with network I/O**

```kotlin
// ❌ WRONG - would cause NetworkOnMainThreadException for blocking calls
button.setOnClickListener {
    val data = fetchData() // direct synchronous HTTP call
}

// ✅ CORRECT - use Dispatchers.IO (or another background dispatcher) for blocking calls
button.setOnClickListener {
    lifecycleScope.launch(Dispatchers.IO) {
        val data = fetchData()
        withContext(Dispatchers.Main) {
            updateUI(data)
        }
    }
}
```

Suspend-based APIs of Retrofit/Ktor are designed to avoid blocking the main thread (using non-blocking I/O and coroutines), but if you use synchronous execute() or other blocking clients, always switch to Dispatchers.IO.

**Manifest permissions**

```xml
<manifest>
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
</manifest>
```

**HTTPS by default (Android 9+)**

```kotlin
// ✅ Recommended: use HTTPS
const val BASE_URL = "https://api.example.com/"

// ⚠️ Note: On Android 9+, cleartext HTTP (http://) is restricted by default
// (cleartextTrafficPermitted=false) and must be explicitly allowed via
// usesCleartextTraffic or a networkSecurityConfig when needed.
const val BASE_URL_HTTP = "http://api.example.com/"
```

**Error handling**

```kotlin
suspend fun safeApiCall(): Result<User> {
    return try {
        Result.success(apiService.getUser(123))
    } catch (e: HttpException) {
        // HTTP errors 4xx/5xx
        Result.failure(e)
    } catch (e: IOException) {
        // Network errors (timeouts, no internet, etc.)
        Result.failure(e)
    }
}
```

### Network Checking

```kotlin
fun isNetworkAvailable(context: Context): Boolean {
    val cm = context.getSystemService<ConnectivityManager>() ?: return false

    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
        val network = cm.activeNetwork ?: return false
        val capabilities = cm.getNetworkCapabilities(network) ?: return false
        // Prefer a network that has INTERNET, and when available also VALIDATED.
        // Here we require INTERNET and VALIDATED for a "usable" connection.
        capabilities.hasCapability(NET_CAPABILITY_INTERNET) &&
            capabilities.hasCapability(NET_CAPABILITY_VALIDATED)
    } else {
        cm.activeNetworkInfo?.isConnected == true
    }
}
```

(Note: Even with a reported available network, actual server reachability is not guaranteed; always handle failures at the HTTP client level.)

### Recommendations

**For most apps**: `Retrofit` + `OkHttp` + Gson/Moshi + Coroutines

**For simple requests**: `OkHttp` directly

**For Kotlin Multiplatform**: Ktor Client

---

## Дополнительные Вопросы (RU)

- Как реализовать retry-логику с экспоненциальной задержкой?
- В чем разница между интерсепторами `OkHttp` и конвертерами `Retrofit`?
- Как настроить certificate pinning для усиления безопасности?
- Как реализовать дедупликацию запросов при параллельных одинаковых запросах?
- Каковы лучшие практики кэширования сетевых ответов?

## Follow-ups

- How to implement retry logic with exponential backoff?
- What's the difference between `OkHttp` interceptors and `Retrofit` converters?
- How to handle certificate pinning for security?
- How to implement request deduplication for concurrent identical requests?
- What are the best practices for caching network responses?

## Ссылки (RU)

- [Android Developers: Connect to the network](https://developer.android.com/training/basics/network-ops/connecting)
- [Retrofit documentation](https://square.github.io/retrofit/)
- [OkHttp documentation](https://square.github.io/okhttp/)

## References

- [Android Developers: Connect to the network](https://developer.android.com/training/basics/network-ops/connecting)
- [Retrofit documentation](https://square.github.io/retrofit/)
- [OkHttp documentation](https://square.github.io/okhttp/)

## Связанные Вопросы (RU)

### База (проще)
- [[q-android-app-components--android--easy]] — компоненты Android

### Средний Уровень
- [[q-what-does-the-lifecycle-library-do--android--medium]] — использование `Lifecycle` для сетевых операций

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - Understanding Android components

### Related (Medium)
- [[q-what-does-the-lifecycle-library-do--android--medium]] - `Lifecycle`-aware networking
