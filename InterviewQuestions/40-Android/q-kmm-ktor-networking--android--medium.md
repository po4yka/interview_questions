---
id: android-164
title: "KMM Ktor Networking / Сетевое взаимодействие с Ktor в KMM"
aliases: ["KMM Ktor Networking", "Сетевое взаимодействие с Ktor в KMM"]
topic: android
subtopics: [coroutines, networking-http]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: []
created: 2025-10-15
updated: 2025-01-27
tags: [android/coroutines, android/networking-http, difficulty/medium, kmm, ktor, multiplatform]
sources: []
date created: Monday, October 27th 2025, 5:12:45 pm
date modified: Saturday, November 1st 2025, 5:43:34 pm
---

# Вопрос (RU)

> Объясните как использовать Ktor client для multiplatform networking в KMM проектах. Как настроить platform-specific engines, обработать аутентификацию, реализовать retry логику и управлять сетевыми ошибками на Android и iOS?

# Question (EN)

> Explain how to use Ktor client for multiplatform networking in KMM projects. How do you configure platform-specific engines, handle authentication, implement retry logic, and manage network errors across Android and iOS?

## Ответ (RU)

Ktor — рекомендуемый HTTP-клиент для Kotlin Multiplatform, предоставляющий единый API с platform-optimized движками (OkHttp для Android, NSURLSession для iOS) и comprehensive поддержкой плагинов.

### Основная Конфигурация

**Зависимости**: добавьте `ktor-client-core` в `commonMain`, platform-specific движки (`ktor-client-android`, `ktor-client-darwin`) в соответствующие sourceSet'ы, плагины для serialization, logging, auth.

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
            expectSuccess = true // ❌ Отключено = ручная обработка
        }
    }
}
```

**Platform-specific движки**: используйте `expect/actual` для конфигурации OkHttp (Android) и NSURLSession (iOS), например таймауты, proxy settings.

### Аутентификация

**Bearer tokens**:
```kotlin
// ✅ Auth plugin с auto-refresh
install(Auth) {
    bearer {
        loadTokens {
            BearerTokens(
                accessToken = tokenProvider.getAccessToken() ?: "",
                refreshToken = tokenProvider.getRefreshToken() ?: ""
            )
        }
        refreshTokens {
            val response = client.post("auth/refresh") {
                markAsRefreshTokenRequest()
                setBody(RefreshTokenRequest(tokenProvider.getRefreshToken()))
            }.body<TokenResponse>()

            tokenProvider.saveTokens(response.accessToken, response.refreshToken)
            BearerTokens(response.accessToken, response.refreshToken)
        }
    }
}
```

**Обработка 401**: используйте `HttpResponseValidator` для перехвата Unauthorized, очищайте токены и сигнализируйте UI о необходимости повторной авторизации.

### Retry Logic

**Exponential backoff**:
```kotlin
// ✅ Interceptor с умными повторами
client.plugin(HttpSend).intercept { request ->
    var attempt = 0
    while (attempt < maxRetries) {
        attempt++
        try {
            val response = execute(request)
            // ✅ Retry на 5xx, 429, timeout
            if (response.status in retryableStatusCodes && attempt < maxRetries) {
                delay((1000L * (1 shl (attempt - 1))).coerceAtMost(30_000L))
                continue
            }
            return@intercept response
        } catch (e: Exception) {
            if (isRetryableException(e) && attempt < maxRetries) {
                delay(delayMillis(attempt))
                continue
            }
            throw e
        }
    }
}
```

**Retryable условия**: timeout errors, `UnknownHostException`, 5xx codes, 429 с `Retry-After` header.

### Обработка Ошибок

**Type-safe errors**:
```kotlin
sealed class NetworkError : Exception() {
    data class HttpError(val statusCode: HttpStatusCode, val errorBody: String?) : NetworkError()
    object TimeoutError : NetworkError()
    object NoInternetError : NetworkError()
}

// ✅ Маппинг исключений
fun mapException(e: Exception): NetworkError = when (e) {
    is HttpRequestTimeoutException -> NetworkError.TimeoutError
    is UnknownHostException -> NetworkError.NoInternetError
    is ClientRequestException -> NetworkError.HttpError(e.response.status, null)
    else -> NetworkError.UnknownError(e.message ?: "Unknown")
}
```

**Network monitoring**: используйте platform-specific APIs (`ConnectivityManager` на Android, `NWPathMonitor` на iOS) для проверки доступности сети перед запросами.

### Advanced Features

**Interceptors**: используйте `HttpSend.intercept` для analytics logging, response caching, custom headers.

**File upload/download**: используйте `MultiPartFormDataContent` для upload с `onUpload` callback, `get` с `onDownload` для прогресса.

**GraphQL**: оборачивайте запросы в `GraphQLRequest(query, variables)`, парсите `GraphQLResponse<T>` с `errors` handling.

### Тестирование

```kotlin
// ✅ MockEngine для unit-тестов
HttpClient(MockEngine) {
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

**Резюме**: Ktor обеспечивает unified multiplatform networking с platform-optimized движками, comprehensive auth/retry/error handling, extensible plugin system. Ключевые моменты: правильная обработка ошибок, retry стратегии с exponential backoff, secure token management, platform-specific оптимизации.

## Answer (EN)

Ktor is the recommended HTTP client for Kotlin Multiplatform, providing a unified API with platform-optimized engines (OkHttp for Android, NSURLSession for iOS) and comprehensive plugin support.

### Basic Configuration

**Dependencies**: Add `ktor-client-core` to `commonMain`, platform-specific engines (`ktor-client-android`, `ktor-client-darwin`) to respective sourceSets, plugins for serialization, logging, auth.

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
            expectSuccess = true // ❌ Disabled = manual error handling
        }
    }
}
```

**Platform-specific engines**: Use `expect/actual` to configure OkHttp (Android) and NSURLSession (iOS) with timeouts, proxy settings.

### Authentication

**Bearer tokens**:
```kotlin
// ✅ Auth plugin with auto-refresh
install(Auth) {
    bearer {
        loadTokens {
            BearerTokens(
                accessToken = tokenProvider.getAccessToken() ?: "",
                refreshToken = tokenProvider.getRefreshToken() ?: ""
            )
        }
        refreshTokens {
            val response = client.post("auth/refresh") {
                markAsRefreshTokenRequest()
                setBody(RefreshTokenRequest(tokenProvider.getRefreshToken()))
            }.body<TokenResponse>()

            tokenProvider.saveTokens(response.accessToken, response.refreshToken)
            BearerTokens(response.accessToken, response.refreshToken)
        }
    }
}
```

**Handle 401**: Use `HttpResponseValidator` to intercept Unauthorized, clear tokens and signal UI to re-authenticate.

### Retry Logic

**Exponential backoff**:
```kotlin
// ✅ Interceptor with smart retries
client.plugin(HttpSend).intercept { request ->
    var attempt = 0
    while (attempt < maxRetries) {
        attempt++
        try {
            val response = execute(request)
            // ✅ Retry on 5xx, 429, timeout
            if (response.status in retryableStatusCodes && attempt < maxRetries) {
                delay((1000L * (1 shl (attempt - 1))).coerceAtMost(30_000L))
                continue
            }
            return@intercept response
        } catch (e: Exception) {
            if (isRetryableException(e) && attempt < maxRetries) {
                delay(delayMillis(attempt))
                continue
            }
            throw e
        }
    }
}
```

**Retryable conditions**: timeout errors, `UnknownHostException`, 5xx codes, 429 with `Retry-After` header.

### Error Handling

**Type-safe errors**:
```kotlin
sealed class NetworkError : Exception() {
    data class HttpError(val statusCode: HttpStatusCode, val errorBody: String?) : NetworkError()
    object TimeoutError : NetworkError()
    object NoInternetError : NetworkError()
}

// ✅ Exception mapping
fun mapException(e: Exception): NetworkError = when (e) {
    is HttpRequestTimeoutException -> NetworkError.TimeoutError
    is UnknownHostException -> NetworkError.NoInternetError
    is ClientRequestException -> NetworkError.HttpError(e.response.status, null)
    else -> NetworkError.UnknownError(e.message ?: "Unknown")
}
```

**Network monitoring**: Use platform-specific APIs (`ConnectivityManager` on Android, `NWPathMonitor` on iOS) to check network availability before requests.

### Advanced Features

**Interceptors**: Use `HttpSend.intercept` for analytics logging, response caching, custom headers.

**File upload/download**: Use `MultiPartFormDataContent` for upload with `onUpload` callback, `get` with `onDownload` for progress.

**GraphQL**: Wrap queries in `GraphQLRequest(query, variables)`, parse `GraphQLResponse<T>` with `errors` handling.

### Testing

```kotlin
// ✅ MockEngine for unit tests
HttpClient(MockEngine) {
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

**Summary**: Ktor provides unified multiplatform networking with platform-optimized engines, comprehensive auth/retry/error handling, extensible plugin system. Key considerations: proper error handling, retry strategies with exponential backoff, secure token management, platform-specific optimizations.

---

## Follow-ups

- How would you implement certificate pinning in Ktor for both Android and iOS?
- What strategies exist for handling token refresh races when multiple concurrent requests hit 401?
- How do you implement request prioritization and cancellation in Ktor client?

## References

- Ktor documentation: https://ktor.io/
- Kotlin Multiplatform: https://kotlinlang.org/docs/multiplatform.html

## Related Questions

### Prerequisites (Easier)

- Basic HTTP client configuration and usage
- Coroutines fundamentals for async networking

### Related (Medium)

- Comparing different HTTP client libraries (Retrofit vs Ktor)
- Structuring multiplatform projects architecture

### Advanced (Harder)

- Advanced caching strategies and offline-first patterns
- Request deduplication and concurrent request management
