---
id: 20251012-122780
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
related: [c-okhttp-interceptors, c-networking, q-retrofit-error-handling--android--medium, q-android-caching-strategies--android--medium]
sources: []
created: 2025-10-15
updated: 2025-10-29
tags: [android/networking-http, android/performance-startup, okhttp, retrofit, networking, performance, difficulty/medium]
---

# Вопрос (RU)
> Как реализовать rate limiting и throttling для API запросов в Android?

# Question (EN)
> How to implement rate limiting and throttling for API requests in Android?

---

## Ответ (RU)

**Rate limiting** и **throttling** — техники контроля частоты запросов для защиты серверов от перегрузки и обеспечения стабильности приложения.

**Ключевые подходы:**

**1. Token Bucket Interceptor**

Позволяет всплески трафика при сохранении средней скорости.

```kotlin
class TokenBucketInterceptor(
    private val capacity: Int = 10,
    private val refillRate: Long = 1000 // ms per token
) : Interceptor {
    private var tokens = capacity
    private var lastRefill = System.currentTimeMillis()

    override fun intercept(chain: Interceptor.Chain): Response {
        synchronized(this) {
            // ✅ Пополнение токенов
            val now = System.currentTimeMillis()
            val elapsed = now - lastRefill
            tokens = minOf(capacity, tokens + (elapsed / refillRate).toInt())
            lastRefill = now

            // ❌ Неправильно: блокировать основной поток
            if (tokens < 1) throw TooManyRequestsException()
            tokens--
        }
        return chain.proceed(chain.request())
    }
}
```

**2. Exponential Backoff**

Обрабатывает 429 и 5xx ошибки с увеличивающимися задержками.

```kotlin
class RetryInterceptor(
    private val maxRetries: Int = 3,
    private val initialDelay: Long = 1000
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        var attempt = 0
        while (attempt <= maxRetries) {
            val response = chain.proceed(chain.request())

            when (response.code) {
                in 200..299 -> return response
                429, in 500..599 -> {
                    response.close()
                    if (attempt == maxRetries) throw MaxRetriesExceededException()

                    // ✅ Учитываем Retry-After
                    val delay = response.header("Retry-After")?.toLongOrNull()?.times(1000)
                        ?: (initialDelay shl attempt)
                    Thread.sleep(delay)
                    attempt++
                }
                else -> return response
            }
        }
        throw MaxRetriesExceededException()
    }
}
```

**3. Flow Debounce**

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
        .catch { emit(emptyList()) }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(), emptyList())

    fun onSearchQueryChanged(query: String) {
        searchQuery.value = query
    }
}
```

**4. WorkManager Constraints**

Ограничивает фоновые задачи по сети и батарее.

```kotlin
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)
    .setRequiresBatteryNotLow(true)
    .build()

// ✅ Используем ExistingWorkPolicy для ограничения частоты
val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(15, TimeUnit.MINUTES)
    .setConstraints(constraints)
    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 1, TimeUnit.MINUTES)
    .build()

WorkManager.getInstance(context).enqueueUniquePeriodicWork(
    "sync",
    ExistingPeriodicWorkPolicy.KEEP, // ❌ REPLACE создаёт новые задачи
    syncRequest
)
```

**Практические советы:**
- Используйте token bucket для API с burst traffic
- Всегда учитывайте `Retry-After` header
- Применяйте debounce 300-500ms для поиска
- Кешируйте с ETag для условных запросов
- Мониторьте 429 responses в analytics

## Answer (EN)

**Rate limiting** and **throttling** control request frequency to protect servers from overload and ensure app stability.

**Key approaches:**

**1. Token Bucket Interceptor**

Allows burst traffic while maintaining average rate.

```kotlin
class TokenBucketInterceptor(
    private val capacity: Int = 10,
    private val refillRate: Long = 1000 // ms per token
) : Interceptor {
    private var tokens = capacity
    private var lastRefill = System.currentTimeMillis()

    override fun intercept(chain: Interceptor.Chain): Response {
        synchronized(this) {
            // ✅ Refill tokens
            val now = System.currentTimeMillis()
            val elapsed = now - lastRefill
            tokens = minOf(capacity, tokens + (elapsed / refillRate).toInt())
            lastRefill = now

            // ❌ Wrong: blocking main thread
            if (tokens < 1) throw TooManyRequestsException()
            tokens--
        }
        return chain.proceed(chain.request())
    }
}
```

**2. Exponential Backoff**

Handles 429 and 5xx errors with increasing delays.

```kotlin
class RetryInterceptor(
    private val maxRetries: Int = 3,
    private val initialDelay: Long = 1000
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        var attempt = 0
        while (attempt <= maxRetries) {
            val response = chain.proceed(chain.request())

            when (response.code) {
                in 200..299 -> return response
                429, in 500..599 -> {
                    response.close()
                    if (attempt == maxRetries) throw MaxRetriesExceededException()

                    // ✅ Respect Retry-After header
                    val delay = response.header("Retry-After")?.toLongOrNull()?.times(1000)
                        ?: (initialDelay shl attempt)
                    Thread.sleep(delay)
                    attempt++
                }
                else -> return response
            }
        }
        throw MaxRetriesExceededException()
    }
}
```

**3. Flow Debounce**

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
        .catch { emit(emptyList()) }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(), emptyList())

    fun onSearchQueryChanged(query: String) {
        searchQuery.value = query
    }
}
```

**4. WorkManager Constraints**

Limits background tasks based on network and battery.

```kotlin
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)
    .setRequiresBatteryNotLow(true)
    .build()

// ✅ Use ExistingWorkPolicy to limit frequency
val syncRequest = PeriodicWorkRequestBuilder<SyncWorker>(15, TimeUnit.MINUTES)
    .setConstraints(constraints)
    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 1, TimeUnit.MINUTES)
    .build()

WorkManager.getInstance(context).enqueueUniquePeriodicWork(
    "sync",
    ExistingPeriodicWorkPolicy.KEEP, // ❌ REPLACE creates new tasks
    syncRequest
)
```

**Best practices:**
- Use token bucket for burst-friendly APIs
- Always respect `Retry-After` header
- Apply 300-500ms debounce for search
- Cache with ETag for conditional requests
- Monitor 429 responses in analytics

---

## Follow-ups

- How to test rate limiting interceptors with MockWebServer?
- What's the difference between token bucket and leaky bucket?
- How to implement per-endpoint rate limiting with different limits?
- When should you use coroutine delay() vs Thread.sleep()?
- How to implement adaptive rate limiting based on server headers?

## References

- [[c-okhttp-interceptors]]
- [[c-networking]]
- [OkHttp Interceptors](https://square.github.io/okhttp/interceptors/)
- [Kotlin Flow Operators](https://kotlinlang.org/docs/flow.html)

## Related Questions

### Prerequisites (Easier)
- [[q-okhttp-basics--android--easy]]
- [[q-coroutines-flow-basics--kotlin--easy]]

### Related (Same Level)
- [[q-retrofit-error-handling--android--medium]]
- [[q-android-caching-strategies--android--medium]]
- [[q-workmanager-constraints--android--medium]]

### Advanced (Harder)
- [[q-reactive-backpressure--kotlin--hard]]
- [[q-distributed-rate-limiting--system-design--hard]]