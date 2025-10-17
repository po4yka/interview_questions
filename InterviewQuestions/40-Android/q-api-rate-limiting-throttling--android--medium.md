---
id: "20251015082237588"
title: "Api Rate Limiting Throttling"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: - android
  - networking
  - api
  - rate-limiting
  - throttling
  - retrofit
  - okhttp
---
# API Rate Limiting and Throttling in Android

**Сложность**: Medium
**Источник**: Amit Shekhar Android Interview Questions

# Question (EN)
> How do you implement API rate limiting and throttling on the client side in Android? What strategies prevent exceeding server limits?

# Вопрос (RU)
> Как реализовать ограничение скорости API и троттлинг на стороне клиента в Android? Какие стратегии предотвращают превышение лимитов сервера?

---

## Answer (EN)

API rate limiting prevents clients from exceeding allowed request quotas, protecting servers from overload and ensuring fair resource distribution. Client-side throttling improves app efficiency and reduces server load.

#### 1. **OkHttp Interceptor for Rate Limiting**

```kotlin
class RateLimitInterceptor(
    private val maxRequests: Int = 60,
    private val timeWindowMs: Long = 60_000 // 1 minute
) : Interceptor {

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
                    Log.d("RateLimit", "Rate limit exceeded, waiting ${waitTime}ms")
                    Thread.sleep(waitTime)
                }

                // Clean up old timestamps after waiting
                while (requestTimestamps.isNotEmpty() &&
                    System.currentTimeMillis() - requestTimestamps.peek() > timeWindowMs
                ) {
                    requestTimestamps.poll()
                }
            }

            // Record this request
            requestTimestamps.offer(System.currentTimeMillis())
        }

        return chain.proceed(chain.request())
    }
}

// Usage
val client = OkHttpClient.Builder()
    .addInterceptor(RateLimitInterceptor(maxRequests = 60, timeWindowMs = 60_000))
    .build()
```

#### 2. **Token Bucket Algorithm**

```kotlin
class TokenBucketRateLimiter(
    private val capacity: Int,
    private val refillRate: Int, // tokens per second
    private val refillPeriodMs: Long = 1000
) : Interceptor {

    private var tokens = capacity
    private var lastRefillTime = System.currentTimeMillis()
    private val lock = ReentrantLock()

    override fun intercept(chain: Interceptor.Chain): Response {
        lock.withLock {
            refillTokens()

            while (tokens < 1) {
                val waitTime = refillPeriodMs / refillRate
                Log.d("TokenBucket", "No tokens available, waiting ${waitTime}ms")
                Thread.sleep(waitTime)
                refillTokens()
            }

            tokens--
        }

        return chain.proceed(chain.request())
    }

    private fun refillTokens() {
        val now = System.currentTimeMillis()
        val timePassed = now - lastRefillTime

        if (timePassed >= refillPeriodMs) {
            val tokensToAdd = ((timePassed / refillPeriodMs) * refillRate).toInt()
            tokens = minOf(capacity, tokens + tokensToAdd)
            lastRefillTime = now
        }
    }

    fun getAvailableTokens(): Int = lock.withLock { tokens }
}
```

#### 3. **Retry with Exponential Backoff**

```kotlin
class RetryInterceptor(
    private val maxRetries: Int = 3,
    private val initialDelayMs: Long = 1000
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        var attempt = 0
        var response: Response? = null
        var lastException: IOException? = null

        while (attempt < maxRetries) {
            try {
                response = chain.proceed(chain.request())

                when {
                    response.isSuccessful -> return response

                    response.code == 429 -> { // Too Many Requests
                        val retryAfter = response.header("Retry-After")?.toLongOrNull()
                        val delay = retryAfter?.let { it * 1000 } ?: calculateDelay(attempt)

                        Log.d("Retry", "Rate limited, retrying after ${delay}ms")
                        response.close()
                        Thread.sleep(delay)
                        attempt++
                    }

                    response.code in 500..599 -> { // Server errors
                        val delay = calculateDelay(attempt)
                        Log.d("Retry", "Server error, retrying after ${delay}ms")
                        response.close()
                        Thread.sleep(delay)
                        attempt++
                    }

                    else -> return response
                }
            } catch (e: IOException) {
                lastException = e
                if (attempt >= maxRetries - 1) break

                val delay = calculateDelay(attempt)
                Log.d("Retry", "Request failed, retrying after ${delay}ms", e)
                Thread.sleep(delay)
                attempt++
            }
        }

        throw lastException ?: IOException("Max retries exceeded")
    }

    private fun calculateDelay(attempt: Int): Long {
        return initialDelayMs * (1 shl attempt) // Exponential: 1s, 2s, 4s, 8s...
    }
}
```

#### 4. **Request Throttling with Debounce**

```kotlin
class ThrottledSearchViewModel(
    private val searchRepository: SearchRepository
) : ViewModel() {

    private val searchQuery = MutableStateFlow("")

    // Debounce: Wait for user to stop typing
    val searchResults = searchQuery
        .debounce(300) // Wait 300ms after last input
        .distinctUntilChanged()
        .filter { it.length >= 2 }
        .flatMapLatest { query ->
            flow {
                emit(Resource.Loading)
                try {
                    val results = searchRepository.search(query)
                    emit(Resource.Success(results))
                } catch (e: Exception) {
                    emit(Resource.Error(e.message))
                }
            }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = Resource.Loading
        )

    fun onSearchQueryChanged(query: String) {
        searchQuery.value = query
    }
}

// Alternative: Throttle (emit at most once per time period)
val throttledClicks = clickEvents
    .throttleFirst(1000) // Emit first, ignore rest for 1 second
    .onEach { performAction() }
```

#### 5. **Request Queue with Priority**

```kotlin
data class PrioritizedRequest(
    val request: Request,
    val priority: Priority,
    val timestamp: Long = System.currentTimeMillis()
) : Comparable<PrioritizedRequest> {
    override fun compareTo(other: PrioritizedRequest): Int {
        return when {
            priority != other.priority -> other.priority.compareTo(priority)
            else -> timestamp.compareTo(other.timestamp)
        }
    }
}

enum class Priority {
    LOW, MEDIUM, HIGH, CRITICAL
}

class RequestQueueManager(
    private val maxConcurrentRequests: Int = 4
) {
    private val requestQueue = PriorityBlockingQueue<PrioritizedRequest>()
    private val activeRequests = AtomicInteger(0)
    private val executor = Executors.newFixedThreadPool(maxConcurrentRequests)

    fun enqueue(request: Request, priority: Priority = Priority.MEDIUM): Deferred<Response> {
        val deferred = CompletableDeferred<Response>()
        val prioritizedRequest = PrioritizedRequest(request, priority)
        requestQueue.offer(prioritizedRequest)

        processQueue()
        return deferred
    }

    private fun processQueue() {
        while (activeRequests.get() < maxConcurrentRequests && requestQueue.isNotEmpty()) {
            requestQueue.poll()?.let { prioritizedRequest ->
                activeRequests.incrementAndGet()

                executor.submit {
                    try {
                        val response = executeRequest(prioritizedRequest.request)
                        // Handle response
                    } finally {
                        activeRequests.decrementAndGet()
                        processQueue()
                    }
                }
            }
        }
    }

    private fun executeRequest(request: Request): Response {
        // Execute the actual request
        return OkHttpClient().newCall(request).execute()
    }
}
```

#### 6. **Caching to Reduce API Calls**

```kotlin
class CachingInterceptor(
    private val cache: Cache,
    private val cacheMaxAge: Int = 60 * 5 // 5 minutes
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()

        // Try cache first for GET requests
        if (request.method == "GET") {
            val cacheControl = CacheControl.Builder()
                .maxAge(cacheMaxAge, TimeUnit.SECONDS)
                .build()

            val cachedRequest = request.newBuilder()
                .cacheControl(cacheControl)
                .build()

            val response = chain.proceed(cachedRequest)

            // Rewrite response headers to force caching
            return response.newBuilder()
                .removeHeader("Pragma")
                .removeHeader("Cache-Control")
                .header("Cache-Control", "public, max-age=$cacheMaxAge")
                .build()
        }

        return chain.proceed(request)
    }
}

// Setup cache
val cacheSize = 10L * 1024 * 1024 // 10 MB
val cache = Cache(context.cacheDir, cacheSize)

val client = OkHttpClient.Builder()
    .cache(cache)
    .addNetworkInterceptor(CachingInterceptor())
    .build()
```

#### 7. **Batch Requests**

```kotlin
class BatchRequestManager(
    private val apiService: ApiService,
    private val batchSize: Int = 10,
    private val batchDelayMs: Long = 500
) {
    private val pendingRequests = mutableListOf<DeferredRequest>()
    private var batchJob: Job? = null

    data class DeferredRequest(
        val id: String,
        val deferred: CompletableDeferred<Item>
    )

    suspend fun getItem(id: String): Item {
        val deferred = CompletableDeferred<Item>()

        synchronized(pendingRequests) {
            pendingRequests.add(DeferredRequest(id, deferred))

            if (pendingRequests.size >= batchSize) {
                processBatch()
            } else {
                scheduleBatch()
            }
        }

        return deferred.await()
    }

    private fun scheduleBatch() {
        batchJob?.cancel()
        batchJob = CoroutineScope(Dispatchers.IO).launch {
            delay(batchDelayMs)
            processBatch()
        }
    }

    private suspend fun processBatch() {
        val batch = synchronized(pendingRequests) {
            pendingRequests.toList().also { pendingRequests.clear() }
        }

        if (batch.isEmpty()) return

        try {
            val ids = batch.map { it.id }
            val response = apiService.getItemsBatch(ids)

            if (response.isSuccessful) {
                response.body()?.let { items ->
                    val itemMap = items.associateBy { it.id }

                    batch.forEach { request ->
                        itemMap[request.id]?.let { item ->
                            request.deferred.complete(item)
                        } ?: request.deferred.completeExceptionally(
                            Exception("Item not found")
                        )
                    }
                }
            } else {
                batch.forEach {
                    it.deferred.completeExceptionally(
                        Exception("Batch request failed: ${response.code()}")
                    )
                }
            }
        } catch (e: Exception) {
            batch.forEach { it.deferred.completeExceptionally(e) }
        }
    }
}
```

#### 8. **Monitoring and Analytics**

```kotlin
class RateLimitAnalyticsInterceptor(
    private val analytics: Analytics
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val startTime = System.currentTimeMillis()
        val request = chain.request()

        try {
            val response = chain.proceed(request)
            val duration = System.currentTimeMillis() - startTime

            when (response.code) {
                429 -> {
                    val retryAfter = response.header("Retry-After")
                    analytics.trackRateLimit(
                        endpoint = request.url.toString(),
                        retryAfter = retryAfter,
                        duration = duration
                    )
                }
                in 200..299 -> {
                    analytics.trackSuccess(
                        endpoint = request.url.toString(),
                        duration = duration
                    )
                }
            }

            // Track remaining rate limit
            response.header("X-RateLimit-Remaining")?.toIntOrNull()?.let { remaining ->
                analytics.trackRateLimitStatus(
                    endpoint = request.url.toString(),
                    remaining = remaining,
                    limit = response.header("X-RateLimit-Limit")?.toIntOrNull() ?: 0
                )
            }

            return response
        } catch (e: Exception) {
            analytics.trackError(
                endpoint = request.url.toString(),
                error = e.message ?: "Unknown error"
            )
            throw e
        }
    }
}
```

#### 9. **Complete Setup Example**

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideOkHttpClient(
        context: Context,
        tokenBucketLimiter: TokenBucketRateLimiter,
        retryInterceptor: RetryInterceptor,
        analyticsInterceptor: RateLimitAnalyticsInterceptor
    ): OkHttpClient {
        val cacheSize = 10L * 1024 * 1024 // 10 MB
        val cache = Cache(context.cacheDir, cacheSize)

        return OkHttpClient.Builder()
            .cache(cache)
            .addInterceptor(tokenBucketLimiter)
            .addInterceptor(retryInterceptor)
            .addInterceptor(analyticsInterceptor)
            .addInterceptor(CachingInterceptor())
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .build()
    }

    @Provides
    @Singleton
    fun provideTokenBucketLimiter(): TokenBucketRateLimiter {
        return TokenBucketRateLimiter(
            capacity = 100,
            refillRate = 10 // 10 tokens per second
        )
    }

    @Provides
    @Singleton
    fun provideRetryInterceptor(): RetryInterceptor {
        return RetryInterceptor(
            maxRetries = 3,
            initialDelayMs = 1000
        )
    }
}
```

### Best Practices

**Client-Side:**
- [ ] Implement token bucket or leaky bucket algorithm
- [ ] Use exponential backoff for retries
- [ ] Respect Retry-After headers
- [ ] Cache responses aggressively
- [ ] Batch requests when possible
- [ ] Implement request debouncing/throttling

**Server Communication:**
- [ ] Monitor rate limit headers (X-RateLimit-*)
- [ ] Handle 429 responses gracefully
- [ ] Implement request prioritization
- [ ] Use conditional requests (ETag, If-Modified-Since)

**Performance:**
- [ ] Minimize redundant requests
- [ ] Use WebSocket for real-time data
- [ ] Implement offline-first architecture
- [ ] Compress request/response data

**Monitoring:**
- [ ] Track rate limit violations
- [ ] Monitor request patterns
- [ ] Alert on excessive 429 responses
- [ ] Analyze cache hit rates

---

## Ответ (RU)

Ограничение скорости API предотвращает превышение разрешенных квот запросов, защищая серверы от перегрузки.

#### Стратегии:

**1. Rate Limiting Interceptor**
- Ограничение количества запросов в единицу времени
- Автоматическое ожидание при превышении лимита

**2. Token Bucket Algorithm**
- Токены пополняются с фиксированной скоростью
- Запрос потребляет токен
- Более гибкий подход к всплескам трафика

**3. Retry with Exponential Backoff**
- Автоматический повтор при ошибках 429, 5xx
- Экспоненциальная задержка между попытками
- Уважение заголовка Retry-After

**4. Request Throttling/Debouncing**
- Debounce: ожидание окончания ввода
- Throttle: ограничение частоты событий
- Подходит для поиска, автодополнения

**5. Request Queue with Priority**
- Приоритизация критичных запросов
- Ограничение одновременных запросов
- Очередь с приоритетами

**6. Caching**
- Кэширование GET-запросов
- Условные запросы (ETag)
- Снижение нагрузки на сервер

**7. Batch Requests**
- Объединение множественных запросов
- Снижение количества HTTP-запросов
- Оптимизация производительности

**8. Monitoring**
- Отслеживание заголовков X-RateLimit-*
- Аналитика нарушений лимитов
- Мониторинг паттернов запросов

### Лучшие практики:

**Клиентская сторона:**
- Реализация token bucket/leaky bucket
- Экспоненциальная задержка
- Уважение заголовков Retry-After
- Агрессивное кэширование
- Пакетные запросы
- Debouncing/throttling

**Производительность:**
- Минимизация избыточных запросов
- WebSocket для real-time данных
- Offline-first архитектура
- Сжатие данных

**Мониторинг:**
- Отслеживание нарушений лимитов
- Анализ паттернов запросов
- Алерты на 429 ответы
