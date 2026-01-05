---
id: android-164
title: KMM Ktor Networking / Сетевое взаимодействие с Ktor в KMM
aliases: [KMM Ktor Networking, Сетевое взаимодействие с Ktor в KMM]
topic: android
subtopics: [coroutines, networking-http]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-coroutines, c-retrofit, q-flutter-comparison--android--medium, q-kmm-dependency-injection--android--medium, q-react-native-comparison--android--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [android/coroutines, android/networking-http, difficulty/medium, kmm, ktor, multiplatform]
sources: []
---
# Вопрос (RU)

> Объясните как использовать Ktor client для multiplatform networking в KMM проектах. Как настроить platform-specific engines, обработать аутентификацию, реализовать retry логику и управлять сетевыми ошибками на Android и iOS?

# Question (EN)

> Explain how to use Ktor client for multiplatform networking in KMM projects. How do you configure platform-specific engines, handle authentication, implement retry logic, and manage network errors across Android and iOS?

## Ответ (RU)

Ktor — один из основных HTTP-клиентов для Kotlin Multiplatform от JetBrains, предоставляющий единый API с platform-optimized движками (OkHttp для Android, NSURLSession/Darwin для iOS) и широкую поддержку плагинов.

### Основная Конфигурация

**Зависимости**: добавьте `ktor-client-core` в `commonMain`, platform-specific движки (например, `ktor-client-okhttp` или `ktor-client-android` для Android, `ktor-client-darwin` для iOS) в соответствующие sourceSet'ы, плагины для serialization, logging, auth.

**Фабрика клиента**:
```kotlin
// ✅ Централизованная конфигурация
object HttpClientFactory {
    fun create(baseUrl: String): HttpClient {
        return HttpClient {
            defaultRequest { url(baseUrl) }
            install(ContentNegotiation) {
                json(Json { ignoreUnknownKeys = true })
            }
            install(HttpTimeout) {
                requestTimeoutMillis = 30_000
            }
            // true: 4xx/5xx выбросят исключение; false: проверяем статус вручную
            expectSuccess = false
        }
    }
}
```

**Platform-specific движки**: используйте `expect/actual` для конфигурации OkHttp (Android) и NSURLSession/Darwin (iOS), например таймауты, proxy settings, TLS.

### Аутентификация

**Bearer tokens** (пример для общей конфигурации клиента):
```kotlin
// ✅ Auth plugin с auto-refresh
val client = HttpClient {
    install(Auth) {
        bearer {
            loadTokens {
                val access = tokenProvider.getAccessToken()
                val refresh = tokenProvider.getRefreshToken()
                if (access != null && refresh != null) {
                    BearerTokens(access, refresh)
                } else {
                    null // нет токенов — без авторизации
                }
            }
            refreshTokens {
                val refresh = tokenProvider.getRefreshToken()
                    ?: throw IllegalStateException("No refresh token")

                // В реальном коде используйте относительный путь или отдельный клиент,
                // а не ссылку на client внутри его же инициализации.
                val response: TokenResponse = client.post("auth/refresh") {
                    markAsRefreshTokenRequest()
                    setBody(RefreshTokenRequest(refresh))
                }.body()

                tokenProvider.saveTokens(response.accessToken, response.refreshToken)
                BearerTokens(response.accessToken, response.refreshToken)
            }
        }
    }
}
```

**Обработка 401**: используйте `HttpResponseValidator` или обработку исключений из `expectSuccess`/`ClientRequestException` для перехвата Unauthorized, очищайте токены и сигнализируйте UI о необходимости повторной авторизации.

### Retry Logic

**Exponential backoff** (упрощённый пример, важно всегда возвращать ответ или кидать исключение):
```kotlin
// ✅ Interceptor с умными повторами
client.plugin(HttpSend).intercept { request ->
    var attempt = 0
    while (true) {
        attempt++
        try {
            val response = execute(request)
            // ✅ Retry на 5xx, 429 (и другие retryableStatusCodes, если заданы)
            if (response.status in retryableStatusCodes && attempt < maxRetries) {
                delay((1000L * (1 shl (attempt - 1))).coerceAtMost(30_000L))
                continue
            }
            return@intercept response
        } catch (e: Exception) {
            // Таймауты и сетевые ошибки приходят как исключения
            if (isRetryableException(e) && attempt < maxRetries) {
                delay(delayMillis(attempt))
                continue
            }
            throw e
        }
    }
}
```

Здесь `retryableStatusCodes`, `maxRetries`, `isRetryableException` и `delayMillis` — это ваши вспомогательные настройки и функции, определённые в общем слое.

**Retryable условия**: timeout errors, сетевые ошибки (например, отсутствие хоста или подключения) и временные статусы сервера: 5xx коды, 429 (с учётом `Retry-After` header). В `commonMain` избегайте прямой зависимости от JVM-специфичных исключений: обрабатывайте их в платформенных модулях или через свои абстракции/обёртки.

### Обработка Ошибок

**Type-safe errors** (пример маппинга с явным UnknownError):
```kotlin
sealed class NetworkError(message: String? = null) : Exception(message) {
    data class HttpError(val statusCode: HttpStatusCode, val errorBody: String?) : NetworkError()
    object TimeoutError : NetworkError()
    object NoInternetError : NetworkError()
    data class UnknownError(val reason: String) : NetworkError(reason)
}

// ✅ Маппинг исключений (пример для JVM; для других платформ используйте actual-реализации)
fun mapException(e: Throwable): NetworkError = when (e) {
    is HttpRequestTimeoutException -> NetworkError.TimeoutError
    is UnresolvedAddressException, // JVM: проблемы DNS/сети
    is UnknownHostException -> NetworkError.NoInternetError
    is ClientRequestException -> NetworkError.HttpError(e.response.status, null)
    else -> NetworkError.UnknownError(e.message ?: "Unknown")
}
```

В multiplatform-коде избегайте использования JVM-специфичных типов напрямую: вынесите детали в платформенные реализации (`actual` функции) или оборачивайте в свои error-типы.

**Network monitoring**: используйте platform-specific APIs (`ConnectivityManager` / `NetworkCallback` на Android, `NWPathMonitor` на iOS) для отслеживания доступности сети и информирования слоя данных/UI. Это дополняет, но не заменяет обработку исключений.

### Advanced Features

**Interceptors / плагины**: используйте `HttpSend.intercept` и/или собственные плагины Ktor для:
- логирования и аналитики,
- добавления общих заголовков,
- кэширования ответов (в связке с storage-слоем).

**File upload/download**: используйте `MultiPartFormDataContent` для upload; для прогресса реализуйте чтение/запись потоков блоками и коллбеки/flows, так как универсальные `onUpload`/`onDownload` коллбеки зависят от конкретной версии и реализации клиента.

**GraphQL**: оборачивайте запросы в свою модель `GraphQLRequest(query, variables)` и парсите `GraphQLResponse<T>` с обработкой `errors` — это логический слой поверх Ktor.

### Тестирование

```kotlin
// ✅ MockEngine для unit-тестов
val client = HttpClient(MockEngine) {
    engine {
        addHandler { request ->
            respond(
                content = """{"id":"123","name":"Test"}""",
                status = HttpStatusCode.OK
            )
        }
    }
}
```

**Резюме**: Ktor обеспечивает единый multiplatform HTTP-клиент с platform-optimized движками и плагинами для аутентификации, ретраев и обработки ошибок. Ключевые моменты: корректная стратегия retry с exponential backoff, безопасное управление токенами, platform-specific оптимизации и единый слой маппинга ошибок между Android и iOS.

## Answer (EN)

Ktor is one of the primary HTTP clients for Kotlin Multiplatform from JetBrains, providing a unified API with platform-optimized engines (OkHttp for Android, NSURLSession/Darwin for iOS) and rich plugin support.

### Basic Configuration

**Dependencies**: Add `ktor-client-core` to `commonMain`, platform-specific engines (e.g., `ktor-client-okhttp` or `ktor-client-android` for Android, `ktor-client-darwin` for iOS) to respective sourceSets, plus plugins for serialization, logging, and auth.

**Client factory**:
```kotlin
// ✅ Centralized configuration
object HttpClientFactory {
    fun create(baseUrl: String): HttpClient {
        return HttpClient {
            defaultRequest { url(baseUrl) }
            install(ContentNegotiation) {
                json(Json { ignoreUnknownKeys = true })
            }
            install(HttpTimeout) {
                requestTimeoutMillis = 30_000
            }
            // true: 4xx/5xx throw exceptions; false: handle status codes manually
            expectSuccess = false
        }
    }
}
```

**Platform-specific engines**: Use `expect/actual` to configure OkHttp (Android) and NSURLSession/Darwin (iOS) for timeouts, proxy settings, TLS, etc.

### Authentication

**Bearer tokens** (example applied inside client configuration):
```kotlin
// ✅ Auth plugin with auto-refresh
val client = HttpClient {
    install(Auth) {
        bearer {
            loadTokens {
                val access = tokenProvider.getAccessToken()
                val refresh = tokenProvider.getRefreshToken()
                if (access != null && refresh != null) {
                    BearerTokens(access, refresh)
                } else {
                    null // no tokens yet
                }
            }
            refreshTokens {
                val refresh = tokenProvider.getRefreshToken()
                    ?: throw IllegalStateException("No refresh token")

                // In real code, use a relative URL or a separate client,
                // not a reference to `client` from inside its own initialization.
                val response: TokenResponse = client.post("auth/refresh") {
                    markAsRefreshTokenRequest()
                    setBody(RefreshTokenRequest(refresh))
                }.body()

                tokenProvider.saveTokens(response.accessToken, response.refreshToken)
                BearerTokens(response.accessToken, response.refreshToken)
            }
        }
    }
}
```

**Handle 401**: Use `HttpResponseValidator` or exceptions from `expectSuccess` / `ClientRequestException` to intercept Unauthorized, clear tokens, and signal the UI to re-authenticate.

### Retry Logic

**Exponential backoff** (simplified; must always return or throw):
```kotlin
// ✅ Interceptor with smart retries
client.plugin(HttpSend).intercept { request ->
    var attempt = 0
    while (true) {
        attempt++
        try {
            val response = execute(request)
            // ✅ Retry on 5xx, 429 (and other retryableStatusCodes, if defined)
            if (response.status in retryableStatusCodes && attempt < maxRetries) {
                delay((1000L * (1 shl (attempt - 1))).coerceAtMost(30_000L))
                continue
            }
            return@intercept response
        } catch (e: Exception) {
            // Timeouts and network issues are thrown as exceptions
            if (isRetryableException(e) && attempt < maxRetries) {
                delay(delayMillis(attempt))
                continue
            }
            throw e
        }
    }
}
```

Here `retryableStatusCodes`, `maxRetries`, `isRetryableException`, and `delayMillis` are your own helpers/configuration defined in the shared layer.

**Retryable conditions**: timeout errors, network connectivity errors, and transient server statuses: 5xx codes, 429 (respecting the `Retry-After` header). In `commonMain`, avoid direct use of JVM-specific exceptions like `UnknownHostException`; handle such details in platform modules or via your own abstraction.

### Error Handling

**Type-safe errors** (with an explicit UnknownError type):
```kotlin
sealed class NetworkError(message: String? = null) : Exception(message) {
    data class HttpError(val statusCode: HttpStatusCode, val errorBody: String?) : NetworkError()
    object TimeoutError : NetworkError()
    object NoInternetError : NetworkError()
    data class UnknownError(val reason: String) : NetworkError(reason)
}

// ✅ Exception mapping (JVM example; use actual implementations per platform)
fun mapException(e: Throwable): NetworkError = when (e) {
    is HttpRequestTimeoutException -> NetworkError.TimeoutError
    is UnresolvedAddressException, // JVM: DNS/network issues
    is UnknownHostException -> NetworkError.NoInternetError
    is ClientRequestException -> NetworkError.HttpError(e.response.status, null)
    else -> NetworkError.UnknownError(e.message ?: "Unknown")
}
```

In multiplatform code, avoid binding to JVM-specific exceptions directly; expose them via platform-specific `actual` implementations or map them into `NetworkError` (or similar) at the platform boundary.

**Network monitoring**: Use platform-specific APIs (`ConnectivityManager` / `NetworkCallback` on Android, `NWPathMonitor` on iOS) to track connectivity and inform your data/UI layer. This complements, but does not replace, exception-based handling.

### Advanced Features

**Interceptors / plugins**: Use `HttpSend.intercept` and/or custom Ktor plugins for:
- logging and analytics,
- common headers,
- integration with your caching/offline layer.

**File upload/download**: Use `MultiPartFormDataContent` for uploads. For progress reporting, stream content in chunks and expose callbacks/Flows; Ktor's built-in hooks differ by version and engine, so explicit streaming gives consistent behavior.

**GraphQL**: Wrap HTTP calls with your own `GraphQLRequest(query, variables)` and parse `GraphQLResponse<T>` with `errors` handling; this is a logical layer built on top of Ktor.

### Testing

```kotlin
// ✅ MockEngine for unit tests
val client = HttpClient(MockEngine) {
    engine {
        addHandler { request ->
            respond(
                content = """{"id":"123","name":"Test"}""",
                status = HttpStatusCode.OK
            )
        }
    }
}
```

**Summary**: Ktor provides a unified multiplatform HTTP client with platform-optimized engines and plugins for authentication, retries, and error handling. Key considerations: robust error mapping, retry strategies with exponential backoff, secure token management, platform-specific optimizations, and a shared API between Android and iOS.

---

## Follow-ups

- How would you implement certificate pinning in Ktor for both Android and iOS?
- What strategies exist for handling token refresh races when multiple concurrent requests hit 401?
- How do you implement request prioritization and cancellation in Ktor client?

## References

- Ktor documentation: https://ktor.io/
- Kotlin Multiplatform: https://kotlinlang.org/docs/multiplatform.html

## Related Questions

### Prerequisites / Concepts

- [[c-coroutines]]
- [[c-retrofit]]

### Prerequisites (Easier)

- Basic HTTP client configuration and usage
- Coroutines fundamentals for async networking

### Related (Medium)

- Comparing different HTTP client libraries (Retrofit vs Ktor)
- Structuring multiplatform projects architecture

### Advanced (Harder)

- Advanced caching strategies and offline-first patterns
- Request deduplication and concurrent request management
