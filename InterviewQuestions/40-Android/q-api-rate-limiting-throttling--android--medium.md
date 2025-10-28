---
id: 20251012-122780
title: API Rate Limiting and Throttling / Ограничение скорости API и троттлинг
aliases: [API Rate Limiting and Throttling, Ограничение скорости API и троттлинг]
topic: android
subtopics: [networking-http]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-build-optimization--android--medium, q-android-performance-measurement-tools--android--medium, q-android-testing-strategies--android--medium]
sources: []
created: 2025-10-15
updated: 2025-10-28
tags: [android/networking-http, networking, http, okhttp, difficulty/medium]
---

# Question (EN)
> What is API Rate Limiting and Throttling?

# Вопрос (RU)
> Что такое Ограничение скорости API и троттлинг?

---

## Answer (EN)

**API Rate Limiting and Throttling** are techniques to control request frequency, protecting servers from overload and ensuring fair resource distribution.

**Core Concepts:**
- **Rate Limiting**: Server-enforced limits on requests per time window (e.g., 100 req/min)
- **Throttling**: Client-side request pacing to stay within limits
- **Common Algorithms**: Token bucket, sliding window, fixed window

**1. Sliding Window Rate Limiter (OkHttp Interceptor)**

Tracks timestamps to enforce limits; blocks when exceeded.

```kotlin
class RateLimitInterceptor(
    private val maxRequests: Int = 60,
    private val timeWindowMs: Long = 60_000
) : Interceptor {
    private val timestamps = ConcurrentLinkedQueue<Long>()
    private val lock = ReentrantLock()

    override fun intercept(chain: Interceptor.Chain): Response {
        lock.withLock {
            val now = System.currentTimeMillis()
            // ✅ Remove expired timestamps
            while (timestamps.peek()?.let { now - it > timeWindowMs } == true) {
                timestamps.poll()
            }
            // ❌ Don't forget to enforce limit
            if (timestamps.size >= maxRequests) {
                Thread.sleep(timeWindowMs - (now - timestamps.peek()))
            }
            timestamps.offer(now)
        }
        return chain.proceed(chain.request())
    }
}
```

**2. Token Bucket Algorithm**

Allows burst traffic while maintaining average rate; tokens refill over time.

```kotlin
class TokenBucketRateLimiter(
    private val capacity: Int,
    private val refillRate: Int // tokens/sec
) : Interceptor {
    private var tokens = capacity
    private var lastRefill = System.currentTimeMillis()

    override fun intercept(chain: Interceptor.Chain): Response {
        synchronized(this) {
            refillTokens()
            // ✅ Wait for token availability
            while (tokens < 1) {
                Thread.sleep(1000 / refillRate)
                refillTokens()
            }
            tokens--
        }
        return chain.proceed(chain.request())
    }

    private fun refillTokens() {
        val elapsed = System.currentTimeMillis() - lastRefill
        val tokensToAdd = (elapsed * refillRate / 1000).toInt()
        tokens = minOf(capacity, tokens + tokensToAdd)
        lastRefill = System.currentTimeMillis()
    }
}
```

**3. Exponential Backoff for Retries**

Handles 429 (Too Many Requests) and 5xx errors with increasing delays.

```kotlin
class RetryInterceptor(
    private val maxRetries: Int = 3,
    private val initialDelay: Long = 1000
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        repeat(maxRetries) { attempt ->
            val response = chain.proceed(chain.request())
            when (response.code) {
                429 -> {
                    // ✅ Respect Retry-After header
                    val delay = response.header("Retry-After")
                        ?.toLongOrNull()?.times(1000)
                        ?: (initialDelay shl attempt)
                    response.close()
                    Thread.sleep(delay)
                }
                in 200..299 -> return response
                in 500..599 -> Thread.sleep(initialDelay shl attempt)
                else -> return response
            }
        }
        throw IOException("Max retries exceeded")
    }
}
```

**4. Debouncing User Input (Flow)**

Prevents excessive API calls from rapid typing.

```kotlin
class SearchViewModel(private val repo: SearchRepository) : ViewModel() {
    private val query = MutableStateFlow("")

    val results = query
        .debounce(300) // ✅ Wait for typing to stop
        .distinctUntilChanged()
        .flatMapLatest { q ->
            if (q.isBlank()) flowOf(emptyList())
            else repo.search(q).catch { emit(emptyList()) }
        }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    fun search(q: String) { query.value = q }
}
```

**Best Practices:**
- Use token bucket for flexible burst handling
- Implement exponential backoff (1s, 2s, 4s...)
- Respect `Retry-After` and `X-RateLimit-*` headers
- Cache aggressively; use ETags for conditional requests
- Debounce user input (300-500ms)
- Monitor 429 responses for tuning
- Implement offline-first architecture

## Ответ (RU)

**API Rate Limiting и Throttling** — техники контроля частоты запросов для защиты серверов от перегрузки и обеспечения справедливого распределения ресурсов.

**Основные концепции:**
- **Rate Limiting**: серверные ограничения на количество запросов за период (напр., 100 req/мин)
- **Throttling**: клиентская регулировка для соблюдения лимитов
- **Популярные алгоритмы**: Token bucket, скользящее окно, фиксированное окно

**1. Rate Limiter со скользящим окном (OkHttp Interceptor)**

Отслеживает временные метки для применения лимитов; блокирует при превышении.

```kotlin
class RateLimitInterceptor(
    private val maxRequests: Int = 60,
    private val timeWindowMs: Long = 60_000
) : Interceptor {
    private val timestamps = ConcurrentLinkedQueue<Long>()
    private val lock = ReentrantLock()

    override fun intercept(chain: Interceptor.Chain): Response {
        lock.withLock {
            val now = System.currentTimeMillis()
            // ✅ Удаление устаревших меток
            while (timestamps.peek()?.let { now - it > timeWindowMs } == true) {
                timestamps.poll()
            }
            // ❌ Не забывайте применять лимит
            if (timestamps.size >= maxRequests) {
                Thread.sleep(timeWindowMs - (now - timestamps.peek()))
            }
            timestamps.offer(now)
        }
        return chain.proceed(chain.request())
    }
}
```

**2. Алгоритм Token Bucket**

Позволяет всплески трафика при сохранении средней скорости; токены пополняются со временем.

```kotlin
class TokenBucketRateLimiter(
    private val capacity: Int,
    private val refillRate: Int // токенов/сек
) : Interceptor {
    private var tokens = capacity
    private var lastRefill = System.currentTimeMillis()

    override fun intercept(chain: Interceptor.Chain): Response {
        synchronized(this) {
            refillTokens()
            // ✅ Ожидание доступности токена
            while (tokens < 1) {
                Thread.sleep(1000 / refillRate)
                refillTokens()
            }
            tokens--
        }
        return chain.proceed(chain.request())
    }

    private fun refillTokens() {
        val elapsed = System.currentTimeMillis() - lastRefill
        val tokensToAdd = (elapsed * refillRate / 1000).toInt()
        tokens = minOf(capacity, tokens + tokensToAdd)
        lastRefill = System.currentTimeMillis()
    }
}
```

**3. Экспоненциальная задержка для повторов**

Обрабатывает 429 (Too Many Requests) и 5xx ошибки с увеличивающимися задержками.

```kotlin
class RetryInterceptor(
    private val maxRetries: Int = 3,
    private val initialDelay: Long = 1000
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        repeat(maxRetries) { attempt ->
            val response = chain.proceed(chain.request())
            when (response.code) {
                429 -> {
                    // ✅ Учитываем заголовок Retry-After
                    val delay = response.header("Retry-After")
                        ?.toLongOrNull()?.times(1000)
                        ?: (initialDelay shl attempt)
                    response.close()
                    Thread.sleep(delay)
                }
                in 200..299 -> return response
                in 500..599 -> Thread.sleep(initialDelay shl attempt)
                else -> return response
            }
        }
        throw IOException("Превышено максимальное количество попыток")
    }
}
```

**4. Debouncing пользовательского ввода (Flow)**

Предотвращает избыточные API вызовы от быстрого набора текста.

```kotlin
class SearchViewModel(private val repo: SearchRepository) : ViewModel() {
    private val query = MutableStateFlow("")

    val results = query
        .debounce(300) // ✅ Ожидание завершения ввода
        .distinctUntilChanged()
        .flatMapLatest { q ->
            if (q.isBlank()) flowOf(emptyList())
            else repo.search(q).catch { emit(emptyList()) }
        }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    fun search(q: String) { query.value = q }
}
```

**Лучшие практики:**
- Используйте token bucket для гибкой обработки всплесков
- Применяйте экспоненциальную задержку (1с, 2с, 4с...)
- Учитывайте заголовки `Retry-After` и `X-RateLimit-*`
- Кешируйте агрессивно; используйте ETags для условных запросов
- Применяйте debounce для ввода (300-500мс)
- Мониторьте 429 ответы для настройки
- Реализуйте offline-first архитектуру

---

## Follow-ups

- How do you test rate limiting logic in unit and integration tests?
- What's the difference between token bucket and leaky bucket algorithms?
- How do you handle rate limiting for multiple API endpoints with different limits?
- When would you choose client-side vs server-side rate limiting?
- How do you implement adaptive rate limiting that adjusts based on server responses?
- What are the trade-offs between blocking (Thread.sleep) and suspending in coroutines?

## References

- [[c-networking]]
- [[c-okhttp-interceptors]]
- [OkHttp Interceptors](https://square.github.io/okhttp/interceptors/)
- [Rate Limiting Patterns](https://cloud.google.com/architecture/rate-limiting-strategies-techniques)
- [HTTP 429 Too Many Requests](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/429)

## Related Questions

### Prerequisites (Easier)
- [[q-okhttp-basics--android--easy]] - Understanding OkHttp fundamentals
- [[q-coroutines-flow-basics--kotlin--easy]] - Flow operators for debouncing

### Related (Same Level)
- [[q-retrofit-error-handling--android--medium]] - Handling API errors including rate limits
- [[q-android-caching-strategies--android--medium]] - Reducing API calls through caching
- [[q-workmanager-scheduling--android--medium]] - Background task scheduling and rate limiting

### Advanced (Harder)
- [[q-reactive-backpressure--kotlin--hard]] - Advanced flow control patterns
- [[q-distributed-rate-limiting--system-design--hard]] - Rate limiting in distributed systems