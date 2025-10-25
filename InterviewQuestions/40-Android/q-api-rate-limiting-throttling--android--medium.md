---
id: 20251012-122780
title: API Rate Limiting and Throttling / Ограничение скорости API и троттлинг
aliases: [API Rate Limiting and Throttling, Ограничение скорости API и троттлинг]
topic: android
subtopics:
  - networking-http
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - q-android-build-optimization--android--medium
  - q-android-performance-measurement-tools--android--medium
  - q-android-testing-strategies--android--medium
created: 2025-10-15
updated: 2025-10-15
tags: [android/networking-http, difficulty/medium]
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Saturday, October 25th 2025, 4:53:04 pm
---

# Вопрос (RU)
> Что такое Ограничение скорости API и троттлинг?

---

# Question (EN)
> What is API Rate Limiting and Throttling?

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

- c-networking
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