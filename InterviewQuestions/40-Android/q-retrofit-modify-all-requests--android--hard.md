---\
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
related: [c-android, c-dependency-injection]
created: 2025-10-13
updated: 2025-11-10
tags: [android/di-hilt, android/networking-http, authentication, difficulty/hard, interceptor, logging, okhttp]
sources: ["https://square.github.io/okhttp/interceptors/"]
anki_cards:
  - slug: android-090-0-en
    front: "How to modify all requests globally in Retrofit?"
    back: |
      Use **OkHttp Interceptors** on the OkHttpClient:

      **Two types:**
      - **Application** - before retries/redirects (auth, common params)
      - **Network** - sees actual network requests

      ```kotlin
      class AuthInterceptor(val tokenManager: TokenManager) : Interceptor {
          override fun intercept(chain: Chain): Response {
              val request = chain.request().newBuilder()
                  .header("Authorization", "Bearer ${tokenManager.getToken()}")
                  .build()
              return chain.proceed(request)
          }
      }
      ```
    tags:
      - android_general
      - difficulty::hard
  - slug: android-090-0-ru
    front: "Как глобально изменять все запросы в Retrofit?"
    back: |
      Используйте **OkHttp Interceptors** на OkHttpClient:

      **Два типа:**
      - **Application** - до повторов/редиректов (авторизация, общие параметры)
      - **Network** - видит реальные сетевые запросы

      ```kotlin
      class AuthInterceptor(val tokenManager: TokenManager) : Interceptor {
          override fun intercept(chain: Chain): Response {
              val request = chain.request().newBuilder()
                  .header("Authorization", "Bearer ${tokenManager.getToken()}")
                  .build()
              return chain.proceed(request)
          }
      }
      ```
    tags:
      - android_general
      - difficulty::hard

---\
# Вопрос (RU)
> Как в `Retrofit` изменять все запросы глобально (добавлять заголовки, параметры, логирование)?

# Question (EN)
> How to modify all requests globally in `Retrofit` (add headers, parameters, logging)?

---

## Ответ (RU)

**Краткий ответ:**
Используйте `OkHttpClient` с глобальными `Interceptor` для добавления заголовков, query-параметров, логирования и обработки ошибок для всех запросов `Retrofit`.

### Подробный Ответ

**Концепция:**
`OkHttp` Interceptors — это цепочка обработчиков, которые могут перехватывать каждый запрос и ответ. Используются для cross-cutting concerns: аутентификация, логирование, добавление общих параметров.

**Два типа:**
- **`Application` Interceptor** — выполняется на уровне клиента до повторов/redirects, не взаимодействует напрямую с кэшем и не видит промежуточные ответы (redirects, retries).
- **Network Interceptor** — выполняется ближе к сети, видит фактические сетевые запросы (включая redirects/retries), может наблюдать кэшированные ответы и управлять низкоуровневыми деталями.

**Порядок выполнения (упрощённо):**
`Application` Interceptors → (Кэш/повторы/redirects) → Network Interceptors → Network

### Пример 1: Авторизация

```kotlin
// ✅ Best: Инжектируем TokenManager для тестируемости
class AuthInterceptor @Inject constructor(
    private val tokenManager: TokenManager
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val token = tokenManager.getToken() ?: return chain.proceed(chain.request())

        val authenticatedRequest = chain.request().newBuilder()
            .header("Authorization", "Bearer $token") // ✅ header заменяет предыдущие значения
            .build()

        return chain.proceed(authenticatedRequest)
    }
}

// ❌ Wrong: Жёстко зашитые зависимости, нет DI
class BadAuthInterceptor(/* нет безопасного способа получить Context */) : Interceptor {
    private val sharedPrefs = /* context.getSharedPreferences(...) */ null // ❌ Потенциальная утечка Context и слабая тестируемость
    override fun intercept(chain: Interceptor.Chain): Response {
        // ...
        return chain.proceed(chain.request())
    }
}
```

### Пример 2: Обработка 401 С Обновлением Токена (упрощённый пример)

```kotlin
class TokenRefreshInterceptor @Inject constructor(
    private val tokenManager: TokenManager,
    private val authApi: AuthApi
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        val response = chain.proceed(request)

        // ✅ Упрощённый вариант: синхронизируем обновление токена для избежания гонок
        if (response.code == 401) {
            synchronized(this) {
                val newToken = tokenManager.refreshTokenSync() // Блокирующий вызов, должен быть безопасен для okhttp-потока
                return if (newToken != null) {
                    response.close() // ✅ Важно: закрываем старый response перед повтором
                    chain.proceed(
                        request.newBuilder()
                            .header("Authorization", "Bearer $newToken")
                            .build()
                    )
                } else {
                    // В реальном приложении здесь инициируем logout / экран логина
                    response
                }
            }
        }
        return response
    }
}
```

(Для продакшена зачастую предпочтительнее использовать `OkHttp` `Authenticator` для автоматической обработки 401, особенно при работе с refresh token.)

### Пример 3: Общие Query-параметры

```kotlin
// ✅ Best: Добавляем только если параметр отсутствует
class CommonParamsInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val original = chain.request()
        val originalUrl = original.url

        val newUrl = originalUrl.newBuilder()
            .apply {
                if (originalUrl.queryParameter("platform") == null) {
                    addQueryParameter("platform", "android")
                }
            }
            .build()

        val newRequest = original.newBuilder().url(newUrl).build()
        return chain.proceed(newRequest)
    }
}
```

### Пример 4: Логирование (только Для debug)

```kotlin
// ✅ Best: Условное логирование с разными уровнями (как application interceptor)
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideAuthInterceptor(tokenManager: TokenManager): AuthInterceptor =
        AuthInterceptor(tokenManager)

    @Provides
    @Singleton
    fun provideOkHttpClient(
        authInterceptor: AuthInterceptor
    ): OkHttpClient = OkHttpClient.Builder()
        .apply {
            if (BuildConfig.DEBUG) {
                addInterceptor(HttpLoggingInterceptor().apply {
                    level = HttpLoggingInterceptor.Level.BODY // ✅ Полное логирование только в debug
                })
            }
        }
        .addInterceptor(authInterceptor) // Application interceptor
        .connectTimeout(30, TimeUnit.SECONDS) // ✅ Настройки таймаутов
        .build()
}

// ❌ Wrong: Логируем BODY в production — риск утечки данных и падения производительности
addInterceptor(HttpLoggingInterceptor().apply {
    level = HttpLoggingInterceptor.Level.BODY
})
```

**Ключевые паттерны:**
- Используйте DI (Hilt/Koin) для инжекта interceptors.
- Используйте application interceptors для аутентификации и общих параметров.
- Логирование обычно реализуется как application interceptor (`HttpLoggingInterceptor`), network interceptors нужны для специфичных сетевых кейсов.
- Синхронизируйте логику обновления токена, учитывая конкурентные запросы.
- Закрывайте `Response` при повторном запросе.
- Включайте подробное логирование только в debug-сборках.

## Answer (EN)

**`Short` Version:**
Configure a single `OkHttpClient` used by `Retrofit` and register global `Interceptor`s there to add headers, query params, logging, and error handling for all requests.

### Detailed Version

**Concept:**
`OkHttp` Interceptors are a chain of handlers that can intercept every request and response. They are used for cross-cutting concerns: authentication, logging, adding common parameters.

**Two types:**
- **`Application` Interceptor** - runs at the client level before retries/follow-ups, does not directly interact with the cache, and does not see intermediate responses (redirects, retries) in the same way as network interceptors.
- **Network Interceptor** - runs closer to the network layer, sees actual network requests (including redirects/retries), can observe cached responses, and can control low-level network details.

**Execution order (simplified):**
`Application` Interceptors → (Cache/retries/redirects) → Network Interceptors → Network

### Example 1: Authorization

```kotlin
// ✅ Best: Inject TokenManager for testability
class AuthInterceptor @Inject constructor(
    private val tokenManager: TokenManager
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val token = tokenManager.getToken() ?: return chain.proceed(chain.request())

        val authenticatedRequest = chain.request().newBuilder()
            .header("Authorization", "Bearer $token") // ✅ header replaces previous values
            .build()

        return chain.proceed(authenticatedRequest)
    }
}

// ❌ Wrong: Hardcoded dependencies, no proper DI
class BadAuthInterceptor(/* no safe Context injection */) : Interceptor {
    private val sharedPrefs = /* context.getSharedPreferences(...) */ null // ❌ Potential Context leak and poor testability
    override fun intercept(chain: Interceptor.Chain): Response {
        // ...
        return chain.proceed(chain.request())
    }
}
```

### Example 2: Handle 401 with Token Refresh (simplified)

```kotlin
class TokenRefreshInterceptor @Inject constructor(
    private val tokenManager: TokenManager,
    private val authApi: AuthApi
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        val response = chain.proceed(request)

        // ✅ Simplified approach: synchronize token refresh to avoid race conditions
        if (response.code == 401) {
            synchronized(this) {
                val newToken = tokenManager.refreshTokenSync() // Blocking call; must be safe on OkHttp thread
                return if (newToken != null) {
                    response.close() // ✅ Important: close old response before retry
                    chain.proceed(
                        request.newBuilder()
                            .header("Authorization", "Bearer $newToken")
                            .build()
                    )
                } else {
                    // In a real app, trigger logout / show login screen
                    response
                }
            }
        }
        return response
    }
}
```

(For production, using `OkHttp` `Authenticator` is often preferable for robust 401/refresh token handling.)

### Example 3: Common Query Parameters

```kotlin
// ✅ Best: Add only if parameter is missing
class CommonParamsInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val original = chain.request()
        val originalUrl = original.url

        val newUrl = originalUrl.newBuilder()
            .apply {
                if (originalUrl.queryParameter("platform") == null) {
                    addQueryParameter("platform", "android")
                }
            }
            .build()

        val newRequest = original.newBuilder().url(newUrl).build()
        return chain.proceed(newRequest)
    }
}
```

### Example 4: Logging (debug only)

```kotlin
// ✅ Best: Conditional logging with appropriate levels (as application interceptor)
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideAuthInterceptor(tokenManager: TokenManager): AuthInterceptor =
        AuthInterceptor(tokenManager)

    @Provides
    @Singleton
    fun provideOkHttpClient(
        authInterceptor: AuthInterceptor
    ): OkHttpClient = OkHttpClient.Builder()
        .apply {
            if (BuildConfig.DEBUG) {
                addInterceptor(HttpLoggingInterceptor().apply {
                    level = HttpLoggingInterceptor.Level.BODY // ✅ Full logging only in debug
                })
            }
        }
        .addInterceptor(authInterceptor) // Application interceptor
        .connectTimeout(30, TimeUnit.SECONDS) // ✅ Timeout configuration
        .build()
}

// ❌ Wrong: Logging BODY in production — risk of data leaks and performance issues
addInterceptor(HttpLoggingInterceptor().apply {
    level = HttpLoggingInterceptor.Level.BODY
})
```

**Key patterns:**
- Use DI (Hilt/Koin) to inject interceptors.
- Use application interceptors for auth and common parameters.
- Logging is typically implemented as an application interceptor (`HttpLoggingInterceptor`); use network interceptors only for specific low-level network needs.
- Synchronize token refresh logic, considering concurrent requests.
- Close `Response` before retrying a request.
- Enable verbose logging only in debug builds.

---

## Дополнительные Вопросы (RU)

- В чем разница между `Application` и Network интерцепторами с точки зрения кэширования?
- Как обрабатывать конкурентные обновления токена в интерцепторах (гонки)?
- Каковы последствия для производительности при использовании нескольких интерцепторов?
- Как тестировать интерцепторы юнит-тестами без реальных сетевых вызовов?
- Когда предпочтительнее использовать `Authenticator` вместо Interceptor для обработки 401?
- Как реализовать приоритизацию запросов или retry-логику в интерцепторах?
- Каков порядок выполнения при наличии нескольких интерцепторов?

## Follow-ups

- What's the difference between `Application` and Network interceptors in terms of caching behavior?
- How do you handle concurrent token refresh requests in interceptors (race condition)?
- What are the performance implications of adding multiple interceptors?
- How do you test interceptors in unit tests without making real network calls?
- When should you use Authenticator vs Interceptor for handling 401 responses?
- How do you implement request prioritization or retry logic in interceptors?
- What's the order of execution when you have multiple interceptors?

## Ссылки (RU)

**Концепты:**
- [[c-android]]
- [[c-dependency-injection]]

**Официальная документация:**
- https://square.github.io/okhttp/interceptors/
- https://square.github.io/okhttp/features/interceptors/
- https://square.github.io/retrofit/
- https://developer.android.com/training/articles/security-config

**Дополнительные материалы:**
- `OkHttp` Authenticator для обработки 401
- HttpLoggingInterceptor: уровни логирования и безопасность
- Пиннинг сертификатов с помощью `CertificatePinner`

## References

**Concepts:**
- [[c-android]]
- [[c-dependency-injection]]

**Official Documentation:**
- https://square.github.io/okhttp/interceptors/
- https://square.github.io/okhttp/features/interceptors/
- https://square.github.io/retrofit/
- https://developer.android.com/training/articles/security-config

**Related Resources:**
- `OkHttp` Authenticator for 401 handling
- HttpLoggingInterceptor levels and security
- Certificate pinning with CertificatePinner

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - App components

### Related (Same Level)
- [[q-cicd-multi-module--android--medium]] - DI with `Hilt` modules

### Advanced (Harder)
- [[q-android-enterprise-mdm-architecture--android--hard]] - Related enterprise networking and security patterns
