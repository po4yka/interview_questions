---
id: android-090
title: "Retrofit Modify All Requests / Изменение всех запросов Retrofit"
aliases: ["Retrofit Modify All Requests", "Изменение всех запросов Retrofit"]
topic: android
subtopics: [di-hilt, networking-http]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-retrofit-interceptors, q-networking-basics--android--easy]
created: 2025-10-13
updated: 2025-10-28
tags: [android/di-hilt, android/networking-http, authentication, difficulty/hard, interceptor, logging, okhttp]
sources: [https://square.github.io/okhttp/interceptors/]
---

# Вопрос (RU)
> Как в Retrofit изменять все запросы глобально (добавлять заголовки, параметры, логирование)?

# Question (EN)
> How to modify all requests globally in Retrofit (add headers, parameters, logging)?

---

## Ответ (RU)

**Концепция:**
OkHttp Interceptors - это цепочка обработчиков, которые перехватывают каждый запрос и ответ. Используются для кросс-cutting concerns: аутентификация, логирование, добавление общих параметров.

**Два типа:**
- **Application Interceptor** - выполняется до кеширования, видит только запросы приложения
- **Network Interceptor** - выполняется после кеширования, видит все сетевые запросы (включая редиректы)

**Порядок выполнения:**
Application Interceptors → Cache → Network Interceptors → Network

### Пример 1: Авторизация

```kotlin
// ✅ Best: Инжектируем TokenManager для тестируемости
class AuthInterceptor @Inject constructor(
    private val tokenManager: TokenManager
) : Interceptor {
    override fun intercept(chain: Chain): Response {
        val token = tokenManager.getToken() ?: return chain.proceed(chain.request())

        val authenticatedRequest = chain.request().newBuilder()
            .header("Authorization", "Bearer $token") // ✅ header заменяет предыдущие значения
            .build()

        return chain.proceed(authenticatedRequest)
    }
}

// ❌ Wrong: Hardcoded dependencies, нет DI
class BadAuthInterceptor : Interceptor {
    private val sharedPrefs = context.getSharedPreferences(...) // ❌ Context leak
    override fun intercept(chain: Chain) = ...
}
```

### Пример 2: Обработка 401 С Обновлением Токена

```kotlin
class TokenRefreshInterceptor @Inject constructor(
    private val tokenManager: TokenManager,
    private val authApi: AuthApi
) : Interceptor {
    override fun intercept(chain: Chain): Response {
        val request = chain.request()
        val response = chain.proceed(request)

        // ✅ Best: Синхронизируем обновление токена
        if (response.code == 401) {
            synchronized(this) {
                val newToken = tokenManager.refreshTokenSync() // Блокирующий вызов
                return if (newToken != null) {
                    response.close() // ✅ Важно: закрываем старый response
                    chain.proceed(request.newBuilder()
                        .header("Authorization", "Bearer $newToken")
                        .build())
                } else {
                    response // Logout или показ экрана логина
                }
            }
        }
        return response
    }
}
```

### Пример 3: Общие Query-параметры

```kotlin
// ✅ Best: Добавляем только если параметр отсутствует
class CommonParamsInterceptor : Interceptor {
    override fun intercept(chain: Chain): Response {
        val original = chain.request()
        val url = original.url.newBuilder()
            .apply {
                if (original.url.queryParameter("platform") == null) {
                    addQueryParameter("platform", "android")
                }
            }
            .build()

        return chain.proceed(original.newBuilder().url(url).build())
    }
}
```

### Пример 4: Логирование (только Для debug)

```kotlin
// ✅ Best: Conditional logging с разными уровнями
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient = OkHttpClient.Builder()
        .apply {
            if (BuildConfig.DEBUG) {
                addInterceptor(HttpLoggingInterceptor().apply {
                    level = HttpLoggingInterceptor.Level.BODY // ✅ Полное логирование в debug
                })
            }
        }
        .addInterceptor(AuthInterceptor(tokenManager))
        .connectTimeout(30, TimeUnit.SECONDS) // ✅ Настройки таймаутов
        .build()
}

// ❌ Wrong: Логируем все в production
addInterceptor(HttpLoggingInterceptor().apply {
    level = HttpLoggingInterceptor.Level.BODY // ❌ Утечка данных, performance hit
})
```

**Ключевые паттерны:**
- Используйте DI (Hilt/Koin) для инжекта interceptors
- Application interceptor для auth, query params
- Network interceptor для логирования сетевых деталей
- Синхронизация при обновлении токенов
- Закрывайте Response при retry
- Условное логирование только в debug builds

## Answer (EN)

**Concept:**
OkHttp Interceptors are a chain of handlers that intercept every request and response. Used for cross-cutting concerns: authentication, logging, adding common parameters.

**Two types:**
- **Application Interceptor** - runs before caching, sees only app requests
- **Network Interceptor** - runs after caching, sees all network requests (including redirects)

**Execution order:**
Application Interceptors → Cache → Network Interceptors → Network

### Example 1: Authorization

```kotlin
// ✅ Best: Inject TokenManager for testability
class AuthInterceptor @Inject constructor(
    private val tokenManager: TokenManager
) : Interceptor {
    override fun intercept(chain: Chain): Response {
        val token = tokenManager.getToken() ?: return chain.proceed(chain.request())

        val authenticatedRequest = chain.request().newBuilder()
            .header("Authorization", "Bearer $token") // ✅ header replaces previous values
            .build()

        return chain.proceed(authenticatedRequest)
    }
}

// ❌ Wrong: Hardcoded dependencies, no DI
class BadAuthInterceptor : Interceptor {
    private val sharedPrefs = context.getSharedPreferences(...) // ❌ Context leak
    override fun intercept(chain: Chain) = ...
}
```

### Example 2: Handle 401 with Token Refresh

```kotlin
class TokenRefreshInterceptor @Inject constructor(
    private val tokenManager: TokenManager,
    private val authApi: AuthApi
) : Interceptor {
    override fun intercept(chain: Chain): Response {
        val request = chain.request()
        val response = chain.proceed(request)

        // ✅ Best: Synchronize token refresh
        if (response.code == 401) {
            synchronized(this) {
                val newToken = tokenManager.refreshTokenSync() // Blocking call
                return if (newToken != null) {
                    response.close() // ✅ Important: close old response
                    chain.proceed(request.newBuilder()
                        .header("Authorization", "Bearer $newToken")
                        .build())
                } else {
                    response // Logout or show login screen
                }
            }
        }
        return response
    }
}
```

### Example 3: Common Query Parameters

```kotlin
// ✅ Best: Add only if parameter is missing
class CommonParamsInterceptor : Interceptor {
    override fun intercept(chain: Chain): Response {
        val original = chain.request()
        val url = original.url.newBuilder()
            .apply {
                if (original.url.queryParameter("platform") == null) {
                    addQueryParameter("platform", "android")
                }
            }
            .build()

        return chain.proceed(original.newBuilder().url(url).build())
    }
}
```

### Example 4: Logging (debug only)

```kotlin
// ✅ Best: Conditional logging with different levels
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient = OkHttpClient.Builder()
        .apply {
            if (BuildConfig.DEBUG) {
                addInterceptor(HttpLoggingInterceptor().apply {
                    level = HttpLoggingInterceptor.Level.BODY // ✅ Full logging in debug
                })
            }
        }
        .addInterceptor(AuthInterceptor(tokenManager))
        .connectTimeout(30, TimeUnit.SECONDS) // ✅ Timeout configuration
        .build()
}

// ❌ Wrong: Log everything in production
addInterceptor(HttpLoggingInterceptor().apply {
    level = HttpLoggingInterceptor.Level.BODY // ❌ Data leaks, performance hit
})
```

**Key patterns:**
- Use DI (Hilt/Koin) to inject interceptors
- Application interceptor for auth, query params
- Network interceptor for logging network details
- Synchronize token refresh operations
- Close Response on retry
- Conditional logging in debug builds only

---

## Follow-ups

- What's the difference between Application and Network interceptors in terms of caching behavior?
- How do you handle concurrent token refresh requests in interceptors (race condition)?
- What are the performance implications of adding multiple interceptors?
- How do you test interceptors in unit tests without making real network calls?
- When should you use Authenticator vs Interceptor for handling 401 responses?
- How do you implement request prioritization or retry logic in interceptors?
- What's the order of execution when you have multiple interceptors?

## References

**Concepts:**
- [[c-retrofit-interceptors]] - Interceptor patterns and chain of responsibility
- [[c-okhttp-architecture]] - OkHttp architecture and request lifecycle
- [[c-dependency-injection]] - DI patterns for network layer
- [[c-token-management]] - Token storage and refresh strategies
**Official Documentation:**
- https://square.github.io/okhttp/interceptors/
- https://square.github.io/okhttp/features/interceptors/
- https://square.github.io/retrofit/
- [Network Security Configuration](https://developer.android.com/training/articles/security-config)
**Related Resources:**
- OkHttp Authenticator for 401 handling
- HttpLoggingInterceptor levels and security
- Certificate pinning with CertificatePinner


## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - App components
- [[q-networking-basics--android--easy]] - Networking basics

### Related (Same Level)
- [[q-retrofit-basics--android--medium]] - Retrofit basics
- [[q-okhttp-interceptors--android--medium]] - OkHttp interceptors
- [[q-authentication-patterns--android--medium]] - Authentication patterns
- [[q-cicd-multi-module--android--medium]] - DI with Hilt modules

### Advanced (Harder)
- [[q-retrofit-advanced--android--hard]] - Retrofit advanced
- [[q-network-security--android--hard]] - Network security
- [[q-concurrent-token-refresh--android--hard]] - Race condition handling
