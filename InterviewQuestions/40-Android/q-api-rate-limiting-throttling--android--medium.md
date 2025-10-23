---
id: 20251012-122780
title: API Rate Limiting and Throttling / Ограничение скорости API и троттлинг
aliases:
- API Rate Limiting and Throttling
- Ограничение скорости API и троттлинг
topic: android
subtopics:
- networking
- api
- rate-limiting
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-android-testing-strategies--android--medium
- q-android-build-optimization--android--medium
- q-android-performance-measurement-tools--android--medium
created: 2025-10-15
updated: 2025-10-15
tags:
- android/networking
- android/api
- android/rate-limiting
- networking
- api
- rate-limiting
- throttling
- retrofit
- okhttp
- difficulty/medium
---# Вопрос (RU)
> Как реализовать ограничение скорости API и троттлинг на стороне клиента в Android? Какие стратегии предотвращают превышение лимитов сервера?

---

# Question (EN)
> How do you implement API rate limiting and throttling on the client side in Android? What strategies prevent exceeding server limits?

## Ответ (RU)

**Ограничение скорости API и троттлинг** предотвращает превышение клиентами квот запросов сервера, защищая серверы от перегрузки и обеспечивая справедливое распределение ресурсов через управление запросами на стороне клиента.

**Теория ограничения скорости:**
Ограничение скорости контролирует количество запросов в единицу времени для предотвращения перегрузки сервера. Клиентский троттлинг улучшает эффективность приложения путем группировки запросов, реализации стратегий задержки и соблюдения лимитов сервера перед выполнением запросов.

**1. OkHttp Interceptor для ограничения скорости:**

**Ограничитель скользящего окна:**
Реализует алгоритм скользящего окна, который отслеживает временные метки запросов и блокирует запросы при превышении лимита. Автоматически ждет сброса временного окна перед разрешением новых запросов.

```kotlin
class RateLimitInterceptor(
    private val maxRequests: Int = 60,
    private val timeWindowMs: Long = 60_000 // 1 минута
) : Interceptor {

    // Потокобезопасная очередь для хранения временных меток запросов
    private val requestTimestamps = ConcurrentLinkedQueue<Long>()
    private val lock = ReentrantLock()

    override fun intercept(chain: Interceptor.Chain): Response {
        lock.withLock {
            val now = System.currentTimeMillis()

            // Удалить временные метки вне временного окна
            while (requestTimestamps.isNotEmpty() &&
                now - requestTimestamps.peek() > timeWindowMs
            ) {
                requestTimestamps.poll()
            }

            // Проверить превышение лимита скорости
            if (requestTimestamps.size >= maxRequests) {
                val oldestTimestamp = requestTimestamps.peek()
                val waitTime = timeWindowMs - (now - oldestTimestamp)

                if (waitTime > 0) {
                    // Блокировать поток до сброса временного окна
                    Thread.sleep(waitTime)
                }
            }

            // Записать временную метку этого запроса
            requestTimestamps.offer(System.currentTimeMillis())
        }

        // Продолжить с фактическим запросом
        return chain.proceed(chain.request())
    }
}
```

**2. Алгоритм Token Bucket:**

**Ограничение скорости на основе токенов:**
Использует bucket токенов, который пополняется с фиксированной скоростью. Каждый запрос потребляет токен, позволяя всплески трафика при поддержании средних лимитов скорости. Более гибкий подход чем фиксированные окна.

```kotlin
class TokenBucketRateLimiter(
    private val capacity: Int,
    private val refillRate: Int, // токены в секунду
    private val refillPeriodMs: Long = 1000
) : Interceptor {

    // Текущее количество доступных токенов
    private var tokens = capacity
    private var lastRefillTime = System.currentTimeMillis()
    private val lock = ReentrantLock()

    override fun intercept(chain: Interceptor.Chain): Response {
        lock.withLock {
            // Пополнить токены на основе прошедшего времени
            refillTokens()

            // Ждать если нет доступных токенов
            while (tokens < 1) {
                val waitTime = refillPeriodMs / refillRate
                Thread.sleep(waitTime)
                refillTokens()
            }

            // Потребить один токен для этого запроса
            tokens--
        }

        return chain.proceed(chain.request())
    }

    private fun refillTokens() {
        val now = System.currentTimeMillis()
        val timePassed = now - lastRefillTime

        // Добавить токены на основе прошедшего времени
        if (timePassed >= refillPeriodMs) {
            val tokensToAdd = ((timePassed / refillPeriodMs) * refillRate).toInt()
            // Не превышать емкость bucket
            tokens = minOf(capacity, tokens + tokensToAdd)
            lastRefillTime = now
        }
    }
}
```

**3. Повторные попытки с экспоненциальной задержкой:**

**Стратегия автоматических повторных попыток:**
Обрабатывает ответы ограничения скорости (429) и ошибки сервера (5xx) с экспоненциальной задержкой. Соблюдает заголовки Retry-After и реализует интеллектуальную логику повторных попыток для избежания перегрузки серверов.

```kotlin
class RetryInterceptor(
    private val maxRetries: Int = 3,
    private val initialDelayMs: Long = 1000
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        var attempt = 0
        var response: Response? = null
        var lastException: IOException? = null

        // Цикл повторных попыток с экспоненциальной задержкой
        while (attempt < maxRetries) {
            try {
                response = chain.proceed(chain.request())

                when {
                    response.isSuccessful -> return response

                    response.code == 429 -> { // Слишком много запросов
                        // Соблюдать заголовок Retry-After сервера
                        val retryAfter = response.header("Retry-After")?.toLongOrNull()
                        val delay = retryAfter?.let { it * 1000 } ?: calculateDelay(attempt)

                        response.close()
                        Thread.sleep(delay)
                        attempt++
                    }

                    response.code in 500..599 -> { // Ошибки сервера
                        val delay = calculateDelay(attempt)
                        response.close()
                        Thread.sleep(delay)
                        attempt++
                    }

                    else -> return response // Не повторять другие ошибки
                }
            } catch (e: IOException) {
                lastException = e
                if (attempt >= maxRetries - 1) break

                val delay = calculateDelay(attempt)
                Thread.sleep(delay)
                attempt++
            }
        }

        throw lastException ?: IOException("Max retries exceeded")
    }

    private fun calculateDelay(attempt: Int): Long {
        // Экспоненциальная задержка: 1с, 2с, 4с, 8с...
        return initialDelayMs * (1 shl attempt)
    }
}
```

**4. Троттлинг запросов с дебаунсом:**

**Троттлинг пользовательского ввода:**
Реализует дебаунсинг для поискового ввода и троттлинг для частых событий. Предотвращает чрезмерные API вызовы от быстрых пользовательских взаимодействий, ожидая стабилизации ввода.

```kotlin
class ThrottledSearchViewModel(
    private val searchRepository: SearchRepository
) : ViewModel() {

    // Изменяемое состояние для поискового запроса
    private val searchQuery = MutableStateFlow("")

    // Дебаунс: Ждать окончания ввода пользователя
    val searchResults = searchQuery
        .debounce(300) // Ждать 300мс после последнего ввода
        .distinctUntilChanged() // Эмитировать только при реальном изменении запроса
        .flatMapLatest { query ->
            if (query.isBlank()) {
                // Возвращать пустой список для пустых запросов
                flowOf(emptyList())
            } else {
                // Выполнить поиск и обработать ошибки корректно
                searchRepository.search(query)
                    .catch { emit(emptyList()) }
            }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000), // Остановить через 5с без подписчиков
            initialValue = emptyList()
        )

    fun search(query: String) {
        searchQuery.value = query
    }
}
```

**5. Очередь запросов с приоритетом:**

**Управление запросами на основе приоритета:**
Реализует систему очереди приоритетов, которая обрабатывает критические запросы первыми при поддержании лимитов скорости. Обеспечивает прохождение важных запросов даже в периоды высокой нагрузки.

```kotlin
class PriorityRequestQueue(
    private val maxConcurrentRequests: Int = 5
) {
    // Очередь приоритетов для упорядочивания запросов
    private val requestQueue = PriorityBlockingQueue<RequestItem>()
    private val activeRequests = AtomicInteger(0)
    private val executor = Executors.newFixedThreadPool(maxConcurrentRequests)

    fun enqueue(request: Request, priority: Priority = Priority.NORMAL) {
        // Добавить запрос в очередь приоритетов
        requestQueue.offer(RequestItem(request, priority))
        processNext()
    }

    private fun processNext() {
        // Обрабатывать запросы если под лимитом параллельности
        if (activeRequests.get() < maxConcurrentRequests) {
            val requestItem = requestQueue.poll() ?: return

            activeRequests.incrementAndGet()
            executor.submit {
                try {
                    // Обработать запрос
                    processRequest(requestItem.request)
                } finally {
                    activeRequests.decrementAndGet()
                    processNext() // Обработать следующий запрос
                }
            }
        }
    }
}

enum class Priority {
    HIGH, NORMAL, LOW
}
```

**6. Стратегия кэширования:**

**Кэширование ответов:**
Реализует интеллектуальное кэширование для уменьшения API вызовов. Использует заголовки ETag для условных запросов и реализует стратегии инвалидации кэша.

```kotlin
class CacheInterceptor : Interceptor {
    // LRU кэш для хранения ответов
    private val cache = LruCache<String, Response>(100)

    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()

        // Кэшировать только GET запросы
        if (request.method != "GET") {
            return chain.proceed(request)
        }

        val cacheKey = request.url.toString()
        val cachedResponse = cache.get(cacheKey)

        if (cachedResponse != null) {
            // Использовать ETag для условного запроса
            val etag = cachedResponse.header("ETag")
            val conditionalRequest = request.newBuilder()
                .header("If-None-Match", etag ?: "")
                .build()

            val response = chain.proceed(conditionalRequest)

            if (response.code == 304) { // Не изменено
                // Возвратить кэшированный ответ со статусом 200
                return cachedResponse.newBuilder()
                    .code(200)
                    .build()
            }
        }

        // Выполнить фактический запрос
        val response = chain.proceed(request)

        // Кэшировать успешные ответы
        if (response.isSuccessful) {
            cache.put(cacheKey, response)
        }

        return response
    }
}
```

**Лучшие практики:**
- Реализуйте алгоритмы token bucket или скользящего окна
- Используйте экспоненциальную задержку для повторных попыток
- Соблюдайте заголовки Retry-After от сервера
- Агрессивно кэшируйте ответы для уменьшения API вызовов
- Группируйте запросы когда возможно
- Реализуйте дебаунсинг для пользовательского ввода
- Отслеживайте заголовки ограничения скорости (X-RateLimit-*)
- Используйте условные запросы (ETag, If-Modified-Since)
- Реализуйте архитектуру offline-first
- Отслеживайте нарушения лимитов скорости для мониторинга

---

## Answer (EN)

**API Rate Limiting and Throttling** prevents clients from exceeding server request quotas, protecting servers from overload and ensuring fair resource distribution through client-side request management.

**Rate Limiting Theory:**
Rate limiting controls the number of requests per time window to prevent server overload. Client-side throttling improves app efficiency by batching requests, implementing backoff strategies, and respecting server limits before making requests.

**1. OkHttp Interceptor for Rate Limiting:**

**Sliding Window Rate Limiter:**
Implements a sliding window algorithm that tracks request timestamps and blocks requests when the limit is exceeded. Automatically waits for the time window to reset before allowing new requests.

```kotlin
class RateLimitInterceptor(
    private val maxRequests: Int = 60,
    private val timeWindowMs: Long = 60_000 // 1 minute
) : Interceptor {

    // Thread-safe queue to store request timestamps
    private val requestTimestamps = ConcurrentLinkedQueue<Long>()
    private val lock = ReentrantLock()

    override fun intercept(chain: Interceptor.Chain): Response {
        lock.withLock {
            val now = System.currentTimeMillis()

            // Remove timestamps outside the time window
            while (requestTimestamps.isNotEmpty() &&
                now - requestTimestamps.peek() > timeWindowMs
            ) {
                requestTimestamps.poll()
            }

            // Check if rate limit is exceeded
            if (requestTimestamps.size >= maxRequests) {
                val oldestTimestamp = requestTimestamps.peek()
                val waitTime = timeWindowMs - (now - oldestTimestamp)

                if (waitTime > 0) {
                    // Block thread until time window resets
                    Thread.sleep(waitTime)
                }
            }

            // Record this request timestamp
            requestTimestamps.offer(System.currentTimeMillis())
        }

        // Proceed with the actual request
        return chain.proceed(chain.request())
    }
}
```

**2. Token Bucket Algorithm:**

**Token-Based Rate Limiting:**
Uses a token bucket that refills at a fixed rate. Each request consumes a token, allowing for burst traffic while maintaining average rate limits. More flexible than fixed window approaches.

```kotlin
class TokenBucketRateLimiter(
    private val capacity: Int,
    private val refillRate: Int, // tokens per second
    private val refillPeriodMs: Long = 1000
) : Interceptor {

    // Current number of available tokens
    private var tokens = capacity
    private var lastRefillTime = System.currentTimeMillis()
    private val lock = ReentrantLock()

    override fun intercept(chain: Interceptor.Chain): Response {
        lock.withLock {
            // Refill tokens based on time elapsed
            refillTokens()

            // Wait if no tokens available
            while (tokens < 1) {
                val waitTime = refillPeriodMs / refillRate
                Thread.sleep(waitTime)
                refillTokens()
            }

            // Consume one token for this request
            tokens--
        }

        return chain.proceed(chain.request())
    }

    private fun refillTokens() {
        val now = System.currentTimeMillis()
        val timePassed = now - lastRefillTime

        // Add tokens based on time elapsed
        if (timePassed >= refillPeriodMs) {
            val tokensToAdd = ((timePassed / refillPeriodMs) * refillRate).toInt()
            // Don't exceed bucket capacity
            tokens = minOf(capacity, tokens + tokensToAdd)
            lastRefillTime = now
        }
    }
}
```

**3. Retry with Exponential Backoff:**

**Automatic Retry Strategy:**
Handles rate limit responses (429) and server errors (5xx) with exponential backoff. Respects Retry-After headers and implements intelligent retry logic to avoid overwhelming servers.

```kotlin
class RetryInterceptor(
    private val maxRetries: Int = 3,
    private val initialDelayMs: Long = 1000
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        var attempt = 0
        var response: Response? = null
        var lastException: IOException? = null

        // Retry loop with exponential backoff
        while (attempt < maxRetries) {
            try {
                response = chain.proceed(chain.request())

                when {
                    response.isSuccessful -> return response

                    response.code == 429 -> { // Too Many Requests
                        // Respect server's Retry-After header
                        val retryAfter = response.header("Retry-After")?.toLongOrNull()
                        val delay = retryAfter?.let { it * 1000 } ?: calculateDelay(attempt)

                        response.close()
                        Thread.sleep(delay)
                        attempt++
                    }

                    response.code in 500..599 -> { // Server errors
                        val delay = calculateDelay(attempt)
                        response.close()
                        Thread.sleep(delay)
                        attempt++
                    }

                    else -> return response // Don't retry other errors
                }
            } catch (e: IOException) {
                lastException = e
                if (attempt >= maxRetries - 1) break

                val delay = calculateDelay(attempt)
                Thread.sleep(delay)
                attempt++
            }
        }

        throw lastException ?: IOException("Max retries exceeded")
    }

    private fun calculateDelay(attempt: Int): Long {
        // Exponential backoff: 1s, 2s, 4s, 8s...
        return initialDelayMs * (1 shl attempt)
    }
}
```

**4. Request Throttling with Debounce:**

**User Input Throttling:**
Implements debouncing for search inputs and throttling for frequent events. Prevents excessive API calls from rapid user interactions by waiting for input to stabilize.

```kotlin
class ThrottledSearchViewModel(
    private val searchRepository: SearchRepository
) : ViewModel() {

    // Mutable state for search query
    private val searchQuery = MutableStateFlow("")

    // Debounce: Wait for user to stop typing
    val searchResults = searchQuery
        .debounce(300) // Wait 300ms after last input
        .distinctUntilChanged() // Only emit if query actually changed
        .flatMapLatest { query ->
            if (query.isBlank()) {
                // Return empty list for blank queries
                flowOf(emptyList())
            } else {
                // Perform search and handle errors gracefully
                searchRepository.search(query)
                    .catch { emit(emptyList()) }
            }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000), // Stop after 5s of no subscribers
            initialValue = emptyList()
        )

    fun search(query: String) {
        searchQuery.value = query
    }
}
```

**5. Request Queue with Priority:**

**Priority-Based Request Management:**
Implements a priority queue system that processes critical requests first while maintaining rate limits. Ensures important requests get through even during high traffic periods.

```kotlin
class PriorityRequestQueue(
    private val maxConcurrentRequests: Int = 5
) {
    // Priority queue for request ordering
    private val requestQueue = PriorityBlockingQueue<RequestItem>()
    private val activeRequests = AtomicInteger(0)
    private val executor = Executors.newFixedThreadPool(maxConcurrentRequests)

    fun enqueue(request: Request, priority: Priority = Priority.NORMAL) {
        // Add request to priority queue
        requestQueue.offer(RequestItem(request, priority))
        processNext()
    }

    private fun processNext() {
        // Process requests if under concurrency limit
        if (activeRequests.get() < maxConcurrentRequests) {
            val requestItem = requestQueue.poll() ?: return

            activeRequests.incrementAndGet()
            executor.submit {
                try {
                    // Process request
                    processRequest(requestItem.request)
                } finally {
                    activeRequests.decrementAndGet()
                    processNext() // Process next request
                }
            }
        }
    }
}

enum class Priority {
    HIGH, NORMAL, LOW
}
```

**6. Caching Strategy:**

**Response Caching:**
Implements intelligent caching to reduce API calls. Uses ETag headers for conditional requests and implements cache invalidation strategies.

```kotlin
class CacheInterceptor : Interceptor {
    // LRU cache for storing responses
    private val cache = LruCache<String, Response>(100)

    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()

        // Only cache GET requests
        if (request.method != "GET") {
            return chain.proceed(request)
        }

        val cacheKey = request.url.toString()
        val cachedResponse = cache.get(cacheKey)

        if (cachedResponse != null) {
            // Use ETag for conditional request
            val etag = cachedResponse.header("ETag")
            val conditionalRequest = request.newBuilder()
                .header("If-None-Match", etag ?: "")
                .build()

            val response = chain.proceed(conditionalRequest)

            if (response.code == 304) { // Not Modified
                // Return cached response with 200 status
                return cachedResponse.newBuilder()
                    .code(200)
                    .build()
            }
        }

        // Make actual request
        val response = chain.proceed(request)

        // Cache successful responses
        if (response.isSuccessful) {
            cache.put(cacheKey, response)
        }

        return response
    }
}
```

**Best Practices:**
- Implement token bucket or sliding window algorithms
- Use exponential backoff for retries
- Respect Retry-After headers from server
- Cache responses aggressively to reduce API calls
- Batch requests when possible
- Implement request debouncing for user input
- Monitor rate limit headers (X-RateLimit-*)
- Use conditional requests (ETag, If-Modified-Since)
- Implement offline-first architecture
- Track rate limit violations for monitoring

## Follow-ups

- How do you handle rate limiting in offline scenarios?
- What's the difference between rate limiting and throttling?
- How do you implement adaptive rate limiting based on server responses?
- What are the trade-offs between different rate limiting algorithms?

## References

- [[c-networking]]
- [OkHttp Interceptors](https://square.github.io/okhttp/interceptors/)
- [Rate Limiting Patterns](https://cloud.google.com/architecture/rate-limiting-strategies-techniques)

## Related Questions

### Prerequisites (Easier)
- [[q-android-app-components--android--easy]]
- [[q-android-project-parts--android--easy]]

### Related (Same Level)
- [[q-android-testing-strategies--android--medium]]
- [[q-android-build-optimization--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]]

