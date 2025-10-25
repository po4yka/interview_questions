---
id: 20251012-12271184
title: "Retrofit Modify All Requests / Изменение всех запросов Retrofit"
aliases:
  - "Retrofit Modify All Requests"
  - "Изменение всех запросов Retrofit"
topic: android
subtopics: [networking, retrofit]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-retrofit-interceptors, q-retrofit-basics--android--medium, q-okhttp-interceptors--android--medium]
created: 2025-10-13
updated: 2025-01-25
tags: [android/networking, android/retrofit, authentication, interceptor, logging, networking, okhttp, retrofit, difficulty/hard]
sources: [https://square.github.io/okhttp/interceptors/]
---

# Вопрос (RU)
> Как в Retrofit изменять все запросы глобально?

# Question (EN)
> How to modify all requests globally in Retrofit?

---

## Ответ (RU)

**Теория Interceptors:**
Interceptors в OkHttp позволяют перехватывать и модифицировать все HTTP-запросы и ответы. Это основной механизм для глобального изменения запросов в Retrofit.

**Типы Interceptors:**
- Application Interceptor - выполняется первым, до сетевого соединения
- Network Interceptor - выполняется ближе к сети, после переписывания URL

**Основные применения:**
- Добавление заголовков авторизации
- Логирование запросов/ответов
- Добавление общих параметров
- Обновление токенов
- Модификация URL

```kotlin
// Создание OkHttpClient с interceptor
val okHttpClient = OkHttpClient.Builder()
    .addInterceptor(AuthInterceptor { getAuthToken() })
    .addInterceptor(LoggingInterceptor())
    .build()

val retrofit = Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .client(okHttpClient)
    .build()
```

**Authorization Interceptor:**
```kotlin
class AuthInterceptor(private val tokenProvider: () -> String) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()

        val requestWithAuth = originalRequest.newBuilder()
            .addHeader("Authorization", "Bearer ${tokenProvider()}")
            .build()

        return chain.proceed(requestWithAuth)
    }
}
```

**Query Parameters Interceptor:**
```kotlin
class QueryParameterInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()
        val originalUrl = originalRequest.url

        val urlWithParams = originalUrl.newBuilder()
            .addQueryParameter("api_version", "v1")
            .addQueryParameter("platform", "android")
            .build()

        val requestWithParams = originalRequest.newBuilder()
            .url(urlWithParams)
            .build()

        return chain.proceed(requestWithParams)
    }
}
```

**Logging Interceptor:**
```kotlin
// Использование встроенного logging interceptor
val loggingInterceptor = HttpLoggingInterceptor().apply {
    level = HttpLoggingInterceptor.Level.BODY
}

val okHttpClient = OkHttpClient.Builder()
    .addInterceptor(loggingInterceptor)
    .build()
```

## Answer (EN)

**Interceptors Theory:**
Interceptors in OkHttp allow intercepting and modifying all HTTP requests and responses. This is the primary mechanism for globally modifying requests in Retrofit.

**Interceptor Types:**
- Application Interceptor - runs first, before network connection
- Network Interceptor - runs closer to network, after URL rewriting

**Main use cases:**
- Adding authorization headers
- Logging requests/responses
- Adding common parameters
- Token refresh
- URL modification

```kotlin
// Creating OkHttpClient with interceptor
val okHttpClient = OkHttpClient.Builder()
    .addInterceptor(AuthInterceptor { getAuthToken() })
    .addInterceptor(LoggingInterceptor())
    .build()

val retrofit = Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .client(okHttpClient)
    .build()
```

**Authorization Interceptor:**
```kotlin
class AuthInterceptor(private val tokenProvider: () -> String) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()

        val requestWithAuth = originalRequest.newBuilder()
            .addHeader("Authorization", "Bearer ${tokenProvider()}")
            .build()

        return chain.proceed(requestWithAuth)
    }
}
```

**Query Parameters Interceptor:**
```kotlin
class QueryParameterInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()
        val originalUrl = originalRequest.url

        val urlWithParams = originalUrl.newBuilder()
            .addQueryParameter("api_version", "v1")
            .addQueryParameter("platform", "android")
            .build()

        val requestWithParams = originalRequest.newBuilder()
            .url(urlWithParams)
            .build()

        return chain.proceed(requestWithParams)
    }
}
```

**Logging Interceptor:**
```kotlin
// Using built-in logging interceptor
val loggingInterceptor = HttpLoggingInterceptor().apply {
    level = HttpLoggingInterceptor.Level.BODY
}

val okHttpClient = OkHttpClient.Builder()
    .addInterceptor(loggingInterceptor)
    .build()
```

---

## Follow-ups

- What's the difference between Application and Network interceptors?
- How do you handle token refresh in interceptors?
- What are the performance implications of interceptors?

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]] - App components
- [[q-networking-basics--android--easy]] - Networking basics

### Related (Same Level)
- [[q-retrofit-basics--android--medium]] - Retrofit basics
- [[q-okhttp-interceptors--android--medium]] - OkHttp interceptors
- [[q-authentication-patterns--android--medium]] - Authentication patterns

### Advanced (Harder)
- [[q-retrofit-advanced--android--hard]] - Retrofit advanced
- [[q-network-security--android--hard]] - Network security
