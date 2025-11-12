---
id: android-385
title: API Rate Limiting and Throttling / Ограничение скорости API и троттлинг
aliases: [API Rate Limiting and Throttling, Ограничение скорости API и троттлинг]
topic: android
subtopics: [networking-http, performance-startup]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-basics, q-android-testing-strategies--android--medium]
sources: []
created: 2025-10-15
updated: 2025-11-10
tags: [android/networking-http, android/performance-startup, difficulty/medium, networking, okhttp, performance, retrofit]

---

# Вопрос (RU)
> Как реализовать rate limiting и throttling для API запросов в Android?

# Question (EN)
> How to implement rate limiting and throttling for API requests in Android?

---

## Ответ (RU)

**Rate limiting** и **throttling** — техники контроля частоты запросов для защиты серверов от перегрузки и обеспечения стабильности приложения. На клиенте это дополняет, но не заменяет серверные лимиты — стратегии должны согласовываться с ограничениями API.

См. также: [[c-android-basics]].

### 1. Token Bucket Interceptor

Позволяет всплески трафика при сохранении средней скорости. Состояние ведра общее для всех запросов в рамках одного экземпляра OkHttpClient (что обычно и требуется).

```kotlin
class TokenBucketInterceptor(
    private val capacity: Int = 10,
    private val refillRateMsPerToken: Long = 1000 // мс за токен
) : Interceptor {
    private var tokens = capacity
    private var lastRefillTime = System.currentTimeMillis()

    override fun intercept(chain: Interceptor.Chain): Response {
        synchronized(this) {
            val now = System.currentTimeMillis()
            val elapsed = now - lastRefillTime

            // ✅ Пополняем токены пропорционально прошедшему времени
            if (elapsed > 0) {
                val newTokens = (elapsed / refillRateMsPerToken).toInt()
                if (newTokens > 0) {
                    tokens = minOf(capacity, tokens + newTokens)
                    lastRefillTime += newTokens * refillRateMsPerToken
                }
            }

            if (tokens < 1) {
                // В реальном приложении обычно возвращают контролируемую ошибку/результат,
                // а не "падает" исключением как 429.
                throw TooManyRequestsException()
            }
            tokens--
        }
        return chain.proceed(chain.request())
    }
}
```

### 2. Exponential Backoff

Обрабатывает 429 и 5xx ошибки с увеличивающимися задержками. Пример ниже синхронный и блокирующий (подходит только для фоновых потоков OkHttp / синхронных вызовов; не использовать на главном потоке).

Важно: слепое повторение небезопасно для неидемпотентных методов (POST и др.); в реальных приложениях ограничивайтесь идемпотентными запросами или следуйте рекомендациям API.

```kotlin
class RetryInterceptor(
    private val maxRetries: Int = 3,
    private val initialDelayMs: Long = 1000
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        var attempt = 0

        while (attempt <= maxRetries) {
            val response = chain.proceed(chain.request())

            when (response.code) {
                in 200..299 -> return response
                429, in 500..599 -> {
                    if (attempt == maxRetries) {
                        response.close()
                        throw MaxRetriesExceededException()
                    }

                    // ✅ Учитываем Retry-After header (секунды), иначе экспоненциальный backoff
                    val retryAfterSeconds = response.header("Retry-After")?.toLongOrNull()
                    response.close()

                    val delayMs = retryAfterSeconds?.times(1000)
                        ?: (initialDelayMs * (1L shl attempt)) // 1, 2, 4, ... * initialDelayMs

                    // ⚠️ Thread.sleep блокирует поток OkHttp.
                    // Использовать только там, где блокировка допустима; в корутинах реализуйте
                    // ретраи в suspend-контексте через delay(), а не внутри стандартного Interceptor.
                    Thread.sleep(delayMs)
                    attempt++
                }
                else -> return response
            }
        }
        throw MaxRetriesExceededException()
    }
}
```

### 3. `Flow` Debounce

Ограничивает частые запросы от пользовательского ввода.

```kotlin
class SearchViewModel(private val repo: SearchRepository) : ViewModel() {
    private val searchQuery = MutableStateFlow("")

    val searchResults = searchQuery
        .debounce(300) // ✅ Ждём паузы в наборе
        .distinctUntilChanged()
        .flatMapLatest { query ->
            if (query.length < 3) flowOf(emptyList())
            else repo.search(query)
        }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(), emptyList())
}
```

### 4. WorkManager Rate Limiting

Ограничивает частоту фоновой синхронизации через периодичность задач, ограничения и backoff (это не классический per-request rate limiting, а управление частотой фоновых операций).

```kotlin
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)
    .setRequiresBatteryNotLow(true)
    .build()

val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(15, TimeUnit.MINUTES)
    .setConstraints(constraints)
    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 1, TimeUnit.MINUTES)
    .build()

// ✅ KEEP предотвращает дублирование задач
WorkManager.getInstance(context).enqueueUniquePeriodicWork(
    "sync",
    ExistingPeriodicWorkPolicy.KEEP,
    syncRequest
)
```

**Рекомендации:**
- Использовать token bucket для API, допускающих burst-трафик.
- Учитывать `Retry-After` header и применять экспоненциальный backoff.
- Повторно отправлять только те запросы, которые безопасно ретраить (обычно идемпотентные).
- Применять debounce 300–500 мс для поиска.
- Использовать кеширование с ETag для условных запросов как дополнение к лимитированию.
- Мониторить ответы 429 в аналитике и корректировать стратегии.

## Answer (EN)

**Rate limiting** and **throttling** control request frequency to protect servers from overload and ensure app stability. On the client side this complements, but does not replace, server-side limits; your strategy should align with the API's documented constraints.

See also: [[c-android-basics]].

### 1. Token Bucket Interceptor

Allows burst traffic while maintaining average rate. The bucket state is shared across all requests made with the same OkHttpClient instance (which is typically desired).

```kotlin
class TokenBucketInterceptor(
    private val capacity: Int = 10,
    private val refillRateMsPerToken: Long = 1000 // ms per token
) : Interceptor {
    private var tokens = capacity
    private var lastRefillTime = System.currentTimeMillis()

    override fun intercept(chain: Interceptor.Chain): Response {
        synchronized(this) {
            val now = System.currentTimeMillis()
            val elapsed = now - lastRefillTime

            // ✅ Refill tokens proportionally to elapsed time
            if (elapsed > 0) {
                val newTokens = (elapsed / refillRateMsPerToken).toInt()
                if (newTokens > 0) {
                    tokens = minOf(capacity, tokens + newTokens)
                    lastRefillTime += newTokens * refillRateMsPerToken
                }
            }

            if (tokens < 1) {
                // In a real app you often map this to a controlled error/result
                // instead of throwing as if it were a raw 429.
                throw TooManyRequestsException()
            }
            tokens--
        }
        return chain.proceed(chain.request())
    }
}
```

### 2. Exponential Backoff

Handles 429 and 5xx errors with increasing delays. The example below is synchronous and blocking (intended only for OkHttp background threads / synchronous calls; do not use this pattern on the main thread).

Important: blindly retrying is unsafe for non-idempotent methods (e.g. POST); in real apps restrict retries to idempotent requests or follow the API's guidelines.

```kotlin
class RetryInterceptor(
    private val maxRetries: Int = 3,
    private val initialDelayMs: Long = 1000
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        var attempt = 0

        while (attempt <= maxRetries) {
            val response = chain.proceed(chain.request())

            when (response.code) {
                in 200..299 -> return response
                429, in 500..599 -> {
                    if (attempt == maxRetries) {
                        response.close()
                        throw MaxRetriesExceededException()
                    }

                    // ✅ Respect Retry-After header (seconds) or fall back to exponential backoff
                    val retryAfterSeconds = response.header("Retry-After")?.toLongOrNull()
                    response.close()

                    val delayMs = retryAfterSeconds?.times(1000)
                        ?: (initialDelayMs * (1L shl attempt)) // 1, 2, 4, ... * initialDelayMs

                    // ⚠️ Thread.sleep blocks the OkHttp thread.
                    // Use only where blocking is acceptable; in coroutines implement retries
                    // in a suspend context with delay(), not inside a standard Interceptor.
                    Thread.sleep(delayMs)
                    attempt++
                }
                else -> return response
            }
        }
        throw MaxRetriesExceededException()
    }
}
```

### 3. `Flow` Debounce

Limits frequent requests from user input.

```kotlin
class SearchViewModel(private val repo: SearchRepository) : ViewModel() {
    private val searchQuery = MutableStateFlow("")

    val searchResults = searchQuery
        .debounce(300) // ✅ Wait for typing pause
        .distinctUntilChanged()
        .flatMapLatest { query ->
            if (query.length < 3) flowOf(emptyList())
            else repo.search(query)
        }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(), emptyList())
}
```

### 4. WorkManager Rate Limiting

Controls frequency of background sync via periodic work, constraints, and backoff. This is not classic per-request rate limiting but scheduling policies that effectively throttle background operations.

```kotlin
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)
    .setRequiresBatteryNotLow(true)
    .build()

val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(15, TimeUnit.MINUTES)
    .setConstraints(constraints)
    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 1, TimeUnit.MINUTES)
    .build()

// ✅ KEEP prevents duplicate tasks
WorkManager.getInstance(context).enqueueUniquePeriodicWork(
    "sync",
    ExistingPeriodicWorkPolicy.KEEP,
    syncRequest
)
```

**Best practices:**
- Use token bucket for burst-friendly APIs.
- Always respect `Retry-After` header and apply exponential backoff.
- Retry only requests that are safe to retry (typically idempotent).
- Apply 300–500 ms debounce for search.
- Use ETag-based conditional requests as a complement to rate limiting.
- Monitor 429 responses in analytics and adjust strategies.

---

## Дополнительные вопросы (RU)

- Как тестировать rate limiting интерцепторы с MockWebServer?
- В чем разница между алгоритмами token bucket и leaky bucket?
- Как реализовать per-endpoint rate limiting с разными лимитами?
- Когда использовать `delay()` корутин вместо `Thread.sleep()` в реализациях ретраев?
- Как реализовать адаптивный rate limiting на основе заголовков ответа сервера?

## Follow-ups

- How to test rate limiting interceptors with MockWebServer?
- What's the difference between token bucket and leaky bucket algorithms?
- How to implement per-endpoint rate limiting with different limits?
- When to use coroutine `delay()` vs `Thread.sleep()` in retry implementations?
- How to implement adaptive rate limiting based on server response headers?

## Ссылки (RU)

- [OkHttp Interceptors](https://square.github.io/okhttp/interceptors/)
- [Kotlin `Flow` Operators](https://kotlinlang.org/docs/flow.html)
- [WorkManager Documentation](https://developer.android.com/topic/libraries/architecture/workmanager)

## References

- [OkHttp Interceptors](https://square.github.io/okhttp/interceptors/)
- [Kotlin `Flow` Operators](https://kotlinlang.org/docs/flow.html)
- [WorkManager Documentation](https://developer.android.com/topic/libraries/architecture/workmanager)

## Связанные вопросы (RU)

### Базовые (проще)

- [[q-android-app-components--android--easy]]

### На том же уровне сложности

- [[q-android-testing-strategies--android--medium]]

### Продвинутые (сложнее)

- [[q-android-runtime-art--android--medium]]

## Related Questions

### Prerequisites (Easier)

- [[q-android-app-components--android--easy]]

### Related (Same Level)

- [[q-android-testing-strategies--android--medium]]

### Advanced (Harder)

- [[q-android-runtime-art--android--medium]]
