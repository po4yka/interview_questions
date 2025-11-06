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
related: []
sources: []
created: 2025-10-15
updated: 2025-10-30
tags: [android/networking-http, android/performance-startup, difficulty/medium, networking, okhttp, performance, retrofit]
---

# Вопрос (RU)
> Как реализовать rate limiting и throttling для API запросов в Android?

# Question (EN)
> How to implement rate limiting and throttling for API requests in Android?

---

## Ответ (RU)

**Rate limiting** и **throttling** — техники контроля частоты запросов для защиты серверов от перегрузки и обеспечения стабильности приложения.

### 1. Token Bucket Interceptor

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
 val now = System.currentTimeMillis()
 val elapsed = now - lastRefill
 tokens = minOf(capacity, tokens + (elapsed / refillRate).toInt())
 lastRefill = now

 // ✅ Пополнение токенов основано на времени
 if (tokens < 1) throw TooManyRequestsException()
 tokens--
 }
 return chain.proceed(chain.request())
 }
}
```

### 2. Exponential Backoff

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

 // ✅ Учитываем Retry-After header
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

Ограничивает фоновые задачи по сети и батарее.

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
- Token bucket для API с burst traffic
- Учитывать `Retry-After` header
- Debounce 300-500ms для поиска
- Кешировать с ETag для условных запросов
- Мониторить 429 responses в analytics

## Answer (EN)

**Rate limiting** and **throttling** control request frequency to protect servers from overload and ensure app stability.

### 1. Token Bucket Interceptor

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
 val now = System.currentTimeMillis()
 val elapsed = now - lastRefill
 tokens = minOf(capacity, tokens + (elapsed / refillRate).toInt())
 lastRefill = now

 // ✅ Token refill based on elapsed time
 if (tokens < 1) throw TooManyRequestsException()
 tokens--
 }
 return chain.proceed(chain.request())
 }
}
```

### 2. Exponential Backoff

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

Limits background tasks based on network and battery.

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
- Use token bucket for burst-friendly APIs
- Always respect `Retry-After` header
- Apply 300-500ms debounce for search
- Cache with ETag for conditional requests
- Monitor 429 responses in analytics

---

## Follow-ups

- How to test rate limiting interceptors with MockWebServer?
- What's the difference between token bucket and leaky bucket algorithms?
- How to implement per-endpoint rate limiting with different limits?
- When to use coroutine delay() vs `Thread`.sleep() in interceptors?
- How to implement adaptive rate limiting based on server response headers?

## References

- 
- 
- [OkHttp Interceptors](https://square.github.io/okhttp/interceptors/)
- [Kotlin `Flow` Operators](https://kotlinlang.org/docs/flow.html)
- [WorkManager Documentation](https://developer.android.com/topic/libraries/architecture/workmanager)

## Related Questions

### Prerequisites (Easier)

### Related (Same Level)
- 
- [[q-android-testing-strategies--android--medium]]
- 

### Advanced (Harder)
- 
- 
