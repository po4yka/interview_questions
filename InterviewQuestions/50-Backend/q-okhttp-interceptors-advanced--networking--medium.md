---\
id: net-004
title: "OkHttp Interceptors Advanced / Продвинутые перехватчики OkHttp"
aliases: ["OkHttp Interceptors Advanced", "Продвинутые перехватчики OkHttp"]
topic: databases
subtopics: [api-clients, authentication, caching, http-clients]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-backend
related: [c-coroutines]
created: 2025-10-15
updated: 2025-11-11
sources: []
tags: [authentication, caching, difficulty/medium, interceptors, networking, okhttp, retry]

---\
# Вопрос (RU)

> Реализовать пользовательские интерцепторы `OkHttp` для обновления аутентификации, повторных попыток запросов и кеширования ответов. Объяснить порядок цепочки `application` vs `network` интерцепторов.

# Question (EN)

> Implement custom `OkHttp` interceptors for authentication refresh, request retry, and response caching. Explain `application` vs `network` interceptor chain order.

## Ответ (RU)

**Интерцепторы `OkHttp`** — механизмы для перехвата, модификации и обработки HTTP-запросов/ответов без загрязнения бизнес-логики.

См. также: [[c-coroutines]]

### Типы Интерцепторов

**`Application` Interceptors**:
- Выполняются первыми, ближе к коду приложения
- Вызываются один раз на запрос (даже для кешированных)
- Видят оригинальный запрос до редиректов/повторов
- Могут прервать цепочку без вызова сети (вернув собственный `Response`)

**`Network` Interceptors**:
- Выполняются последними перед сетевым вызовом
- Вызываются для каждого сетевого запроса + повторов
- Видят реальный запрос с добавленными заголовками
- Обычно используются для работы с сетью и логирования низкого уровня; могут вернуть собственный `Response` вместо вызова `proceed()`, но при этом обязаны соблюдать контракт `chain`

### Порядок Выполнения

```text
Application Code
  → Application Interceptor
  → OkHttp internal (Retry, Bridge, Cache, Connect)
  → Network Interceptor
  → Network Call
```

### 1. Authentication Interceptor

Обновление токена при `401` с `Mutex` для синхронизации:

```kotlin
class AuthenticationInterceptor(
    private val tokenProvider: TokenProvider
) : Interceptor {
    private val refreshMutex = Mutex()

    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()

        // ✅ Add token to request
        val token = tokenProvider.getAccessToken()
        val authenticatedRequest = request.newBuilder()
            .apply { if (token != null) header("Authorization", "Bearer $token") }
            .build()

        var response = chain.proceed(authenticatedRequest)

        // ✅ Refresh on 401, avoid auth endpoints
        if (response.code == 401 && !request.url.encodedPath.contains("/auth/")) {
            response.close()  // ✅ Always close before retry
            response = refreshAndRetry(chain, request)
        }

        return response
    }

    private fun refreshAndRetry(chain: Interceptor.Chain, request: Request): Response {
        // ⚠️ intercept вызывается в синхронном потоке OkHttp, поэтому runBlocking здесь допустим,
        // но важно не вызывать его из основного UI-потока.
        return runBlocking {
            refreshMutex.withLock {  // ✅ Prevent concurrent refresh
                val newToken = tokenProvider.refreshToken()
                if (newToken != null) {
                    chain.proceed(
                        request.newBuilder()
                            .header("Authorization", "Bearer $newToken")
                            .build()
                    )
                } else {
                    tokenProvider.clearTokens()
                    chain.proceed(request)  // ❌ Ожидаемо приведет к ошибке и триггернет re-auth на уровне приложения
                }
            }
        }
    }
}

interface TokenProvider {
    fun getAccessToken(): String?
    suspend fun refreshToken(): String?
    fun clearTokens()
}
```

### 2. Retry Interceptor

Экспоненциальная задержка с учетом `Retry-After`:

```kotlin
class RetryInterceptor(
    private val maxRetries: Int = 3,
    private val initialDelayMs: Long = 1000L,
    private val factor: Double = 2.0,
    private val retryableCodes: Set<Int> = setOf(408, 429, 500, 502, 503, 504)
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        var response: Response? = null
        var retryCount = 0

        while (retryCount <= maxRetries) {
            try {
                response?.close()  // ✅ Close previous attempt
                response = chain.proceed(chain.request())

                if (response.isSuccessful || response.code !in retryableCodes) {
                    return response  // ✅ Success or non-retryable
                }

                if (retryCount >= maxRetries) return response  // ❌ Max retries reached

                // ✅ Check server-provided delay
                val retryAfter = response.header("Retry-After")?.toLongOrNull()
                val delay = retryAfter?.times(1000) ?: calculateDelay(retryCount)

                response.close()
                Thread.sleep(delay)

            } catch (e: IOException) {
                if (retryCount >= maxRetries) throw e
                Thread.sleep(calculateDelay(retryCount))
            }
            retryCount++
        }
        throw IOException("Max retries exceeded")
    }

    private fun calculateDelay(count: Int): Long =
        (initialDelayMs * factor.pow(count)).toLong().coerceAtMost(10000L)
}
```

### 3. Cache Interceptor

Адаптивное кеширование в зависимости от состояния сети:

```kotlin
class CacheInterceptor(
    private val context: Context,
    private val onlineMaxAge: Int = 60,  // 1 minute
    private val offlineMaxStale: Int = 604800  // 7 days
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        var request = chain.request()
        val isOnline = isNetworkAvailable()

        if (!isOnline) {
            // ✅ Offline: accept stale cache, не ходим в сеть
            request = request.newBuilder()
                .cacheControl(
                    CacheControl.Builder()
                        .onlyIfCached()
                        .maxStale(offlineMaxStale, TimeUnit.SECONDS)
                        .build()
                )
                .build()
        }

        val response = chain.proceed(request)

        return response.newBuilder()
            .removeHeader("Pragma")
            .removeHeader("Cache-Control")
            .header(
                "Cache-Control",
                if (isOnline) {
                    "public, max-age=$onlineMaxAge"  // ✅ Fresh data online
                } else {
                    "public, only-if-cached, max-stale=$offlineMaxStale"  // ✅ Stale data offline from cache
                }
            )
            .build()
    }

    private fun isNetworkAvailable(): Boolean {
        val cm = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val network = cm.activeNetwork ?: return false
        val caps = cm.getNetworkCapabilities(network) ?: return false
        return caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
    }
}
```

### 4. Конфигурация OkHttpClient

```kotlin
class OkHttpClientFactory(
    private val context: Context,
    private val tokenProvider: TokenProvider
) {
    fun create(): OkHttpClient {
        return OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .cache(Cache(File(context.cacheDir, "http"), 10 * 1024 * 1024))

            // ✅ Application Interceptors (see original request)
            .addInterceptor(LoggingInterceptor())  // Log what app sends
            .addInterceptor(AuthenticationInterceptor(tokenProvider))  // Add auth
            .addInterceptor(CacheInterceptor(context))  // Cache strategy
            .addInterceptor(RetryInterceptor(maxRetries = 3))  // Retry logic

            // ✅ Network Interceptors (see network request)
            .addNetworkInterceptor(NetworkCacheInterceptor())  // Cache headers

            .build()
    }
}
```

### Лучшие Практики

1. Порядок важен: `Application` (Logging → Auth → Cache → Retry) → `Network`
2. Закрывайте ответы: вызывайте `response.close()` перед повторами
3. Потокобезопасность: используйте `Mutex` для обновления токена
4. Избегайте циклов: выделяйте отдельный клиент для auth без auth-interceptor
5. Маскируйте чувствительные данные: не логируйте токены в production

### Распространённые Ошибки

```kotlin
// ❌ Auth loop: auth interceptor вызывает защищённый endpoint
authApi.refreshToken()  // → добавляет auth header → 401 → refresh → loop

// ✅ Separate auth client
val authClient = OkHttpClient.Builder().build()  // Нет auth interceptor

// ❌ Memory leak: не закрыт response
val resp = chain.proceed(req)
return chain.proceed(modified)  // resp утечет

// ✅ Always close
resp.close()
return chain.proceed(modified)

// ❌ Concurrent token refresh
val token = refresh()  // Несколько потоков

// ✅ Synchronized with Mutex
refreshMutex.withLock { refresh() }
```

---

## Answer (EN)

**`OkHttp` Interceptors** intercept, modify, and handle HTTP requests/responses without polluting business logic.

See also: [[c-coroutines]]

### Interceptor Types

**`Application` Interceptors**:
- Execute first, closer to app code
- Called once per request (even for cached)
- See original request before redirects/retries
- Can short-circuit without network call by returning a custom `Response`

**`Network` Interceptors**:
- Execute last, just before network call
- Called for every network request + retries
- See actual request with added headers
- Typically used for low-level concerns (network logging, caching). They may return a synthetic `Response` instead of calling `proceed()`, but must respect the `chain` contract.

### Execution Order

```text
Application Code
  → Application Interceptor
  → OkHttp internal (Retry, Bridge, Cache, Connect)
  → Network Interceptor
  → Network Call
```

### 1. Authentication Interceptor

Token refresh on `401` with `Mutex` for thread safety:

```kotlin
class AuthenticationInterceptor(
    private val tokenProvider: TokenProvider
) : Interceptor {
    private val refreshMutex = Mutex()

    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()

        // ✅ Add token to request
        val token = tokenProvider.getAccessToken()
        val authenticatedRequest = request.newBuilder()
            .apply { if (token != null) header("Authorization", "Bearer $token") }
            .build()

        var response = chain.proceed(authenticatedRequest)

        // ✅ Refresh on 401, avoid auth endpoints
        if (response.code == 401 && !request.url.encodedPath.contains("/auth/")) {
            response.close()  // ✅ Always close before retry
            response = refreshAndRetry(chain, request)
        }

        return response
    }

    private fun refreshAndRetry(chain: Interceptor.Chain, request: Request): Response {
        // ⚠️ intercept runs on an OkHttp worker thread, so runBlocking is acceptable here
        // as long as this interceptor is not invoked from the main/UI thread.
        return runBlocking {
            refreshMutex.withLock {  // ✅ Prevent concurrent refresh
                val newToken = tokenProvider.refreshToken()
                if (newToken != null) {
                    chain.proceed(
                        request.newBuilder()
                            .header("Authorization", "Bearer $newToken")
                            .build()
                    )
                } else {
                    tokenProvider.clearTokens()
                    chain.proceed(request)  // ❌ Expected to fail; lets app trigger re-auth flow
                }
            }
        }
    }
}

interface TokenProvider {
    fun getAccessToken(): String?
    suspend fun refreshToken(): String?
    fun clearTokens()
}
```

### 2. Retry Interceptor

Exponential backoff respecting `Retry-After`:

```kotlin
class RetryInterceptor(
    private val maxRetries: Int = 3,
    private val initialDelayMs: Long = 1000L,
    private val factor: Double = 2.0,
    private val retryableCodes: Set<Int> = setOf(408, 429, 500, 502, 503, 504)
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        var response: Response? = null
        var retryCount = 0

        while (retryCount <= maxRetries) {
            try {
                response?.close()  // ✅ Close previous attempt
                response = chain.proceed(chain.request())

                if (response.isSuccessful || response.code !in retryableCodes) {
                    return response  // ✅ Success or non-retryable
                }

                if (retryCount >= maxRetries) return response  // ❌ Max retries reached

                // ✅ Check server-provided delay
                val retryAfter = response.header("Retry-After")?.toLongOrNull()
                val delay = retryAfter?.times(1000) ?: calculateDelay(retryCount)

                response.close()
                Thread.sleep(delay)

            } catch (e: IOException) {
                if (retryCount >= maxRetries) throw e
                Thread.sleep(calculateDelay(retryCount))
            }
            retryCount++
        }
        throw IOException("Max retries exceeded")
    }

    private fun calculateDelay(count: Int): Long =
        (initialDelayMs * factor.pow(count)).toLong().coerceAtMost(10000L)
}
```

### 3. Cache Interceptor

Adaptive caching based on network state:

```kotlin
class CacheInterceptor(
    private val context: Context,
    private val onlineMaxAge: Int = 60,  // 1 minute
    private val offlineMaxStale: Int = 604800  // 7 days
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        var request = chain.request()
        val isOnline = isNetworkAvailable()

        if (!isOnline) {
            // ✅ Offline: accept stale cache only, do not hit network
            request = request.newBuilder()
                .cacheControl(
                    CacheControl.Builder()
                        .onlyIfCached()
                        .maxStale(offlineMaxStale, TimeUnit.SECONDS)
                        .build()
                )
                .build()
        }

        val response = chain.proceed(request)

        return response.newBuilder()
            .removeHeader("Pragma")
            .removeHeader("Cache-Control")
            .header(
                "Cache-Control",
                if (isOnline) {
                    "public, max-age=$onlineMaxAge"  // ✅ Fresh data online
                } else {
                    "public, only-if-cached, max-stale=$offlineMaxStale"  // ✅ Stale data offline from cache
                }
            )
            .build()
    }

    private fun isNetworkAvailable(): Boolean {
        val cm = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val network = cm.activeNetwork ?: return false
        val caps = cm.getNetworkCapabilities(network) ?: return false
        return caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
    }
}
```

### 4. OkHttpClient Configuration

```kotlin
class OkHttpClientFactory(
    private val context: Context,
    private val tokenProvider: TokenProvider
) {
    fun create(): OkHttpClient {
        return OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .cache(Cache(File(context.cacheDir, "http"), 10 * 1024 * 1024))

            // ✅ Application Interceptors (see original request)
            .addInterceptor(LoggingInterceptor())  // Log what app sends
            .addInterceptor(AuthenticationInterceptor(tokenProvider))  // Add auth
            .addInterceptor(CacheInterceptor(context))  // Cache strategy
            .addInterceptor(RetryInterceptor(maxRetries = 3))  // Retry logic

            // ✅ Network Interceptors (see network request)
            .addNetworkInterceptor(NetworkCacheInterceptor())  // Cache headers

            .build()
    }
}
```

### Best Practices

1. Order matters: `Application` (Logging → Auth → Cache → Retry) → `Network`
2. Close responses: call `response.close()` before retries
3. `Thread` safety: use `Mutex` for token refresh
4. Avoid loops: separate auth client without auth interceptor
5. Redact sensitive data: don't log tokens in production

### Common Pitfalls

```kotlin
// ❌ Auth loop: auth interceptor calls protected endpoint
authApi.refreshToken()  // → adds auth header → 401 → refresh → loop

// ✅ Separate auth client
val authClient = OkHttpClient.Builder().build()  // No auth interceptor

// ❌ Memory leak: unclosed response
val resp = chain.proceed(req)
return chain.proceed(modified)  // resp leaked

// ✅ Always close
resp.close()
return chain.proceed(modified)

// ❌ Concurrent token refresh
val token = refresh()  // Multiple threads

// ✅ Synchronized with Mutex
refreshMutex.withLock { refresh() }
```

---

## Дополнительные Вопросы (RU)

- Как бы вы реализовали дедупликацию запросов для параллельных идентичных запросов?
- Каковы последствия использования `runBlocking` в auth-interceptor-е для не-UI-потоков?
- Как обрабатывать обновление токена, когда несколько запросов одновременно получают `401`?
- Какие стратегии вы бы использовали для приоритизации запросов при перегрузке сети?
- Как реализовать условное кеширование на основе заголовков запроса или шаблонов URL?

## Follow-ups

- How would you implement request deduplication for concurrent identical requests?
- What are the implications of using `runBlocking` in the auth interceptor for non-main threads?
- How would you handle token refresh when multiple requests fail with 401 simultaneously?
- What strategies would you use to prioritize requests during network congestion?
- How would you implement conditional caching based on request headers or URL patterns?

## Ссылки (RU)

- Документация по `OkHttp` Interceptors: https://square.github.io/okhttp/features/interceptors/
- Документация по `Retrofit`: https://square.github.io/retrofit/
- Android Network Security: https://developer.android.com/training/articles/security-config

## References

- `OkHttp` Interceptors Documentation: https://square.github.io/okhttp/features/interceptors/
- `Retrofit` Documentation: https://square.github.io/retrofit/
- Android Network Security: https://developer.android.com/training/articles/security-config

## Связанные Вопросы (RU)

### Предварительные Знания
- Базовая настройка HTTP-клиента с `Retrofit`
- Понимание корутин для асинхронного обновления токена
- Основы конфигурации `OkHttp`-клиента

### Связанные
- Продвинутые call adapters и конвертеры в `Retrofit`
- Стратегии обработки сетевых ошибок и политики повторных попыток
- Архитектурные паттерны API-клиентов (Repository, DataSource)

### Продвинуто
- Дедупликация запросов для параллельных идентичных запросов
- Certificate pinning и security-interceptors
- Тестирование сетевого слоя с MockWebServer

## Related Questions

### Prerequisites
- Basic HTTP client setup with `Retrofit`
- Understanding coroutines for async token refresh
- `OkHttp` client configuration fundamentals

### Related
- Advanced `Retrofit` call adapters and converters
- Network error handling strategies and retry policies
- API client architecture patterns (Repository, DataSource)

### Advanced
- `Request` deduplication for concurrent identical requests
- Certificate pinning and security interceptors
- Network layer testing with MockWebServer
