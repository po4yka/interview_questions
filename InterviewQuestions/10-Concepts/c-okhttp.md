---
id: ivc-20251030-143000
title: OkHttp / OkHttp
aliases: [OkHttp, OkHttp Library, Square OkHttp]
kind: concept
summary: Efficient HTTP client for Android and Java by Square
links: []
created: 2025-10-30
updated: 2025-10-30
tags: [android, concept, http, networking, okhttp]
---

# Summary (EN)

OkHttp is a modern, efficient HTTP client for Android and Java developed by Square. It provides advanced features like connection pooling, transparent GZIP compression, HTTP/2 support, and automatic retry mechanisms. OkHttp is the foundation for Retrofit and many other networking libraries.

**Core Features**:
- Connection pooling for reduced latency
- HTTP/2 and WebSocket support
- Transparent GZIP compression
- Response caching
- Interceptor chain for request/response manipulation
- Automatic handling of common connection problems

# Сводка (RU)

OkHttp - современный, эффективный HTTP-клиент для Android и Java, разработанный компанией Square. Предоставляет продвинутые возможности, такие как пулинг соединений, прозрачное сжатие GZIP, поддержка HTTP/2 и автоматические механизмы повторных попыток. OkHttp является основой для Retrofit и многих других сетевых библиотек.

**Основные возможности**:
- Пулинг соединений для снижения латентности
- Поддержка HTTP/2 и WebSocket
- Прозрачное сжатие GZIP
- Кэширование ответов
- Цепочка перехватчиков для манипуляции запросами/ответами
- Автоматическая обработка распространенных проблем соединения

---

## Core Concept (EN)

**Connection Pooling**: OkHttp maintains a pool of connections that can be reused, reducing latency and improving performance. Connections are automatically released when idle.

**HTTP/2 Support**: Multiple requests to the same host share a single socket, improving efficiency through multiplexing.

**Interceptors**: Powerful mechanism to observe, modify, and retry requests. Interceptors can be added at application or network level.

**Automatic Retries**: OkHttp automatically recovers from common connection failures, including routing failures and socket timeout exceptions.

**Caching**: Built-in response cache that respects HTTP cache headers, reducing bandwidth and improving response times.

## Основная Концепция (RU)

**Пулинг соединений**: OkHttp поддерживает пул соединений, которые можно переиспользовать, снижая латентность и улучшая производительность. Соединения автоматически освобождаются при простое.

**Поддержка HTTP/2**: Множественные запросы к одному хосту разделяют один сокет, повышая эффективность через мультиплексирование.

**Перехватчики**: Мощный механизм для наблюдения, модификации и повтора запросов. Перехватчики можно добавлять на уровне приложения или сети.

**Автоматические повторы**: OkHttp автоматически восстанавливается после распространенных ошибок соединения, включая ошибки маршрутизации и таймауты сокета.

**Кэширование**: Встроенный кэш ответов, учитывающий HTTP-заголовки кэширования, снижает использование трафика и улучшает время отклика.

---

## Key Features (EN)

**Singleton Pattern**: Create a single `OkHttpClient` instance and reuse it across the application to maximize connection pooling and reduce memory overhead.

**Custom Timeouts**: Configure connect, read, and write timeouts for specific requirements.

**Certificate Pinning**: Enhance security by restricting trusted certificates for specific hosts.

**WebSocket Support**: Full-duplex communication over a single TCP connection.

**Integration with Retrofit**: Retrofit uses OkHttp as its HTTP client, benefiting from all OkHttp features.

## Ключевые Возможности (RU)

**Паттерн Singleton**: Создайте один экземпляр `OkHttpClient` и переиспользуйте его во всем приложении для максимизации пулинга соединений и снижения расхода памяти.

**Настраиваемые таймауты**: Настройка таймаутов подключения, чтения и записи для конкретных требований.

**Закрепление сертификатов**: Повышение безопасности путем ограничения доверенных сертификатов для конкретных хостов.

**Поддержка WebSocket**: Полнодуплексная коммуникация через одно TCP-соединение.

**Интеграция с Retrofit**: Retrofit использует OkHttp в качестве HTTP-клиента, получая все преимущества OkHttp.

---

## Code Example (EN)

```kotlin
// Singleton OkHttpClient configuration
class NetworkModule {
    companion object {
        private val loggingInterceptor = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }

        val okHttpClient: OkHttpClient = OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .addInterceptor(loggingInterceptor)
            .addInterceptor { chain ->
                val request = chain.request().newBuilder()
                    .addHeader("User-Agent", "MyApp/1.0")
                    .build()
                chain.proceed(request)
            }
            .connectionPool(ConnectionPool(5, 5, TimeUnit.MINUTES))
            .build()
    }
}

// Basic usage
fun makeRequest() {
    val request = Request.Builder()
        .url("https://api.example.com/data")
        .get()
        .build()

    NetworkModule.okHttpClient.newCall(request).enqueue(object : Callback {
        override fun onFailure(call: Call, e: IOException) {
            // Handle failure
        }

        override fun onResponse(call: Call, response: Response) {
            response.use {
                if (response.isSuccessful) {
                    val body = response.body?.string()
                    // Process response
                }
            }
        }
    })
}
```

---

## Use Cases / Trade-offs

**Use Cases**:
- RESTful API communication
- File downloads/uploads with progress tracking
- WebSocket real-time communication
- Custom authentication flows via interceptors
- Response caching for offline support
- Certificate pinning for enhanced security

**Trade-offs**:
- Adds ~1MB to APK size
- Requires manual lifecycle management for requests
- Callback-based API (can be wrapped with coroutines)
- More verbose than higher-level libraries like Retrofit

**Best Practices**:
- Use a single `OkHttpClient` instance per application
- Configure appropriate timeouts based on use case
- Implement retry logic with exponential backoff for critical requests
- Use `response.use { }` to ensure resources are properly closed
- Add logging interceptor only in debug builds

---

## References

- Official Documentation: https://square.github.io/okhttp/
- GitHub Repository: https://github.com/square/okhttp
- Recipes: https://square.github.io/okhttp/recipes/
- Interceptors Guide: https://square.github.io/okhttp/features/interceptors/
- Connection Pooling: https://square.github.io/okhttp/features/connections/
