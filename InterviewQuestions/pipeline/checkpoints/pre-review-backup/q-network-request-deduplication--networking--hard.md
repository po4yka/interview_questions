---
id: 20251012-12271153
title: "Network Request Deduplication / Дедупликация сетевых запросов"
topic: networking
difficulty: hard
status: draft
moc: moc-android
related: [q-fragments-vs-activity--android--medium, q-launch-modes-android--android--medium, q-canvas-drawing-optimization--custom-views--hard]
created: 2025-10-15
tags: [optimization, deduplication, concurrency, performance, caching, difficulty/hard]
---
# Network Request Deduplication / Дедупликация сетевых запросов

**English**: Implement request deduplication to prevent multiple identical requests. Handle concurrent API calls efficiently with Flow and coroutines.

## Answer (EN)
**Request deduplication** is an optimization technique that prevents making multiple identical network requests simultaneously. When multiple parts of an application request the same data concurrently, deduplication ensures only one actual network call is made, with all callers receiving the same response.

### The Problem

```kotlin
// Problem: Multiple simultaneous requests for same data
class UserViewModel(private val repository: UserRepository) : ViewModel() {

    init {
        viewModelScope.launch {
            // Request 1: Load user profile
            val user = repository.getUser("123")
        }

        viewModelScope.launch {
            // Request 2: Load user for avatar
            val user = repository.getUser("123") // Duplicate request!
        }

        viewModelScope.launch {
            // Request 3: Load user for settings
            val user = repository.getUser("123") // Another duplicate!
        }
    }

    // Result: 3 identical network requests made simultaneously
    // Wastes bandwidth, server resources, and increases latency
}
```

### Request Deduplication Strategies

#### 1. Mutex-Based Deduplication

The simplest approach uses a Mutex to ensure only one request executes at a time.

```kotlin
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import java.util.concurrent.ConcurrentHashMap

/**
 * Simple request deduplicator using Mutex
 */
class MutexDeduplicator {

    private val mutexMap = ConcurrentHashMap<String, Mutex>()

    suspend fun <T> deduplicate(
        key: String,
        block: suspend () -> T
    ): T {
        // Get or create mutex for this key
        val mutex = mutexMap.getOrPut(key) { Mutex() }

        // Only one coroutine can execute block at a time for this key
        return mutex.withLock {
            block()
        }
    }
}

// Usage
class UserRepository(
    private val api: ApiService,
    private val deduplicator: MutexDeduplicator
) {

    suspend fun getUser(userId: String): User {
        return deduplicator.deduplicate("user:$userId") {
            // Only one request executes, others wait
            api.getUser(userId)
        }
    }
}
```

#### 2. SharedFlow-Based Deduplication

A more sophisticated approach using SharedFlow allows multiple collectors to share a single request.

```kotlin
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import java.util.concurrent.ConcurrentHashMap

/**
 * SharedFlow-based deduplicator
 * Allows multiple callers to share the same request result
 */
class SharedFlowDeduplicator {

    private data class RequestState<T>(
        val flow: SharedFlow<Result<T>>,
        val complete: Boolean = false
    )

    private val requests = ConcurrentHashMap<String, RequestState<*>>()
    private val mutex = Mutex()

    suspend fun <T> deduplicate(
        key: String,
        block: suspend () -> T
    ): T {
        // Check if request already exists
        @Suppress("UNCHECKED_CAST")
        val existingState = mutex.withLock {
            requests[key] as? RequestState<T>
        }

        if (existingState != null && !existingState.complete) {
            // Request in progress, wait for result
            return existingState.flow.first().getOrThrow()
        }

        // Create new shared request
        val sharedFlow = MutableSharedFlow<Result<T>>(replay = 1)
        val state = RequestState(sharedFlow, complete = false)

        mutex.withLock {
            requests[key] = state
        }

        try {
            // Execute request
            val result = kotlin.runCatching { block() }

            // Emit result to all waiting collectors
            sharedFlow.emit(result)

            // Mark as complete
            mutex.withLock {
                requests[key] = state.copy(complete = true)
            }

            return result.getOrThrow()
        } catch (e: Exception) {
            // Clean up on error
            mutex.withLock {
                requests.remove(key)
            }
            throw e
        }
    }

    fun clear() {
        requests.clear()
    }
}
```

#### 3. Deferred-Based Deduplication

Using Deferred for efficient concurrent request handling.

```kotlin
import kotlinx.coroutines.*
import java.util.concurrent.ConcurrentHashMap

/**
 * Deferred-based deduplicator
 * Most efficient for many concurrent callers
 */
class DeferredDeduplicator(
    private val scope: CoroutineScope
) {

    private val requests = ConcurrentHashMap<String, Deferred<*>>()

    suspend fun <T> deduplicate(
        key: String,
        block: suspend () -> T
    ): T {
        @Suppress("UNCHECKED_CAST")
        val deferred = requests.getOrPut(key) {
            scope.async {
                try {
                    block()
                } finally {
                    // Clean up after completion
                    requests.remove(key)
                }
            }
        } as Deferred<T>

        return deferred.await()
    }

    fun cancel(key: String) {
        requests[key]?.cancel()
        requests.remove(key)
    }

    fun cancelAll() {
        requests.values.forEach { it.cancel() }
        requests.clear()
    }
}
```

### Complete Deduplication Layer

```kotlin
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import java.util.concurrent.ConcurrentHashMap

/**
 * Complete request deduplication system
 * Combines multiple strategies for optimal performance
 */
class RequestDeduplicator(
    private val scope: CoroutineScope
) {

    private val inFlightRequests = ConcurrentHashMap<String, Deferred<*>>()
    private val requestMutex = Mutex()

    /**
     * Deduplicate a suspend function call
     */
    suspend fun <T> deduplicate(
        key: String,
        forceRefresh: Boolean = false,
        block: suspend () -> T
    ): T {
        if (forceRefresh) {
            cancelRequest(key)
        }

        @Suppress("UNCHECKED_CAST")
        val deferred = requestMutex.withLock {
            inFlightRequests.getOrPut(key) {
                scope.async {
                    try {
                        block()
                    } finally {
                        // Clean up after completion
                        requestMutex.withLock {
                            inFlightRequests.remove(key)
                        }
                    }
                }
            }
        } as Deferred<T>

        return deferred.await()
    }

    /**
     * Deduplicate a Flow
     */
    fun <T> deduplicateFlow(
        key: String,
        block: suspend () -> Flow<T>
    ): Flow<T> = flow {
        @Suppress("UNCHECKED_CAST")
        val deferred = requestMutex.withLock {
            inFlightRequests.getOrPut(key) {
                scope.async {
                    block()
                }
            }
        } as Deferred<Flow<T>>

        deferred.await().collect { value ->
            emit(value)
        }
    }

    /**
     * Cancel a specific request
     */
    suspend fun cancelRequest(key: String) {
        requestMutex.withLock {
            inFlightRequests[key]?.cancel()
            inFlightRequests.remove(key)
        }
    }

    /**
     * Cancel all in-flight requests
     */
    suspend fun cancelAll() {
        requestMutex.withLock {
            inFlightRequests.values.forEach { it.cancel() }
            inFlightRequests.clear()
        }
    }

    /**
     * Get count of in-flight requests
     */
    fun getInFlightCount(): Int = inFlightRequests.size

    /**
     * Check if request is in flight
     */
    fun isInFlight(key: String): Boolean = inFlightRequests.containsKey(key)
}
```

### Cache-Aside Pattern with Deduplication

```kotlin
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import java.util.concurrent.TimeUnit

/**
 * Cache-aside pattern with request deduplication
 * Combines memory cache with deduplicated network requests
 */
class CacheAsideRepository<K, V>(
    private val cache: Cache<K, V>,
    private val deduplicator: RequestDeduplicator,
    private val keyGenerator: (K) -> String
) {

    /**
     * Get value with cache-aside pattern
     */
    suspend fun get(
        key: K,
        forceRefresh: Boolean = false,
        loader: suspend (K) -> V
    ): V {
        // Check cache first
        if (!forceRefresh) {
            cache.get(key)?.let { return it }
        }

        // Not in cache, load with deduplication
        val deduplicationKey = keyGenerator(key)
        val value = deduplicator.deduplicate(deduplicationKey) {
            loader(key)
        }

        // Store in cache
        cache.put(key, value)

        return value
    }

    /**
     * Get as Flow with cache-aside pattern
     */
    fun getAsFlow(
        key: K,
        forceRefresh: Boolean = false,
        loader: suspend (K) -> V
    ): Flow<V> = flow {
        // Emit cached value first if available
        if (!forceRefresh) {
            cache.get(key)?.let { emit(it) }
        }

        // Then fetch fresh value
        val deduplicationKey = keyGenerator(key)
        val freshValue = deduplicator.deduplicate(deduplicationKey) {
            loader(key)
        }

        cache.put(key, freshValue)
        emit(freshValue)
    }

    /**
     * Put value in cache and invalidate request
     */
    suspend fun put(key: K, value: V) {
        cache.put(key, value)
        deduplicator.cancelRequest(keyGenerator(key))
    }

    /**
     * Invalidate cache entry
     */
    suspend fun invalidate(key: K) {
        cache.remove(key)
        deduplicator.cancelRequest(keyGenerator(key))
    }

    /**
     * Clear all cache and cancel all requests
     */
    suspend fun clear() {
        cache.clear()
        deduplicator.cancelAll()
    }
}

/**
 * Simple LRU memory cache
 */
class MemoryCache<K, V>(
    private val maxSize: Int = 100,
    private val ttlMs: Long = TimeUnit.MINUTES.toMillis(5)
) : Cache<K, V> {

    private data class CacheEntry<V>(
        val value: V,
        val timestamp: Long = System.currentTimeMillis()
    )

    private val cache = object : LinkedHashMap<K, CacheEntry<V>>(
        maxSize,
        0.75f,
        true // Access order
    ) {
        override fun removeEldestEntry(eldest: MutableMap.MutableEntry<K, CacheEntry<V>>?): Boolean {
            return size > maxSize
        }
    }

    @Synchronized
    override fun get(key: K): V? {
        val entry = cache[key] ?: return null

        // Check if expired
        if (System.currentTimeMillis() - entry.timestamp > ttlMs) {
            cache.remove(key)
            return null
        }

        return entry.value
    }

    @Synchronized
    override fun put(key: K, value: V) {
        cache[key] = CacheEntry(value)
    }

    @Synchronized
    override fun remove(key: K) {
        cache.remove(key)
    }

    @Synchronized
    override fun clear() {
        cache.clear()
    }

    @Synchronized
    fun size(): Int = cache.size
}

interface Cache<K, V> {
    fun get(key: K): V?
    fun put(key: K, value: V)
    fun remove(key: K)
    fun clear()
}
```

### Debouncing and Throttling

```kotlin
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import java.util.concurrent.atomic.AtomicLong

/**
 * Debouncing: Wait for quiet period before executing
 * Useful for search queries, text input
 */
class Debouncer {

    private val lastCallTime = AtomicLong(0)
    private val mutex = Mutex()

    suspend fun <T> debounce(
        delayMs: Long,
        block: suspend () -> T
    ): T? {
        val currentTime = System.currentTimeMillis()
        lastCallTime.set(currentTime)

        delay(delayMs)

        // Only execute if no newer calls were made
        return if (lastCallTime.get() == currentTime) {
            mutex.withLock {
                if (lastCallTime.get() == currentTime) {
                    block()
                } else {
                    null
                }
            }
        } else {
            null
        }
    }
}

/**
 * Throttling: Limit execution frequency
 * Useful for scroll events, button clicks
 */
class Throttler {

    private val lastExecutionTime = AtomicLong(0)
    private val mutex = Mutex()

    suspend fun <T> throttle(
        intervalMs: Long,
        block: suspend () -> T
    ): T? {
        val currentTime = System.currentTimeMillis()
        val lastTime = lastExecutionTime.get()

        if (currentTime - lastTime < intervalMs) {
            return null // Too soon, skip
        }

        return mutex.withLock {
            // Double-check after acquiring lock
            val recheckTime = lastExecutionTime.get()
            if (currentTime - recheckTime < intervalMs) {
                return@withLock null
            }

            lastExecutionTime.set(currentTime)
            block()
        }
    }
}

/**
 * Flow-based debouncing
 */
fun <T> Flow<T>.debounce(timeoutMillis: Long): Flow<T> = flow {
    var lastEmission = 0L
    collect { value ->
        val currentTime = System.currentTimeMillis()
        if (currentTime - lastEmission > timeoutMillis) {
            lastEmission = currentTime
            emit(value)
        } else {
            delay(timeoutMillis - (currentTime - lastEmission))
            lastEmission = System.currentTimeMillis()
            emit(value)
        }
    }
}

/**
 * Flow-based throttling
 */
fun <T> Flow<T>.throttleFirst(periodMillis: Long): Flow<T> = flow {
    var lastEmissionTime = 0L
    collect { value ->
        val currentTime = System.currentTimeMillis()
        if (currentTime - lastEmissionTime >= periodMillis) {
            lastEmissionTime = currentTime
            emit(value)
        }
    }
}
```

### Complete Repository with Deduplication

```kotlin
/**
 * Complete repository with deduplication, caching, and priority
 */
class OptimizedUserRepository(
    private val api: UserApiService,
    private val scope: CoroutineScope
) {

    private val deduplicator = RequestDeduplicator(scope)
    private val cache = MemoryCache<String, User>(maxSize = 100)
    private val cacheAsideRepo = CacheAsideRepository(
        cache = cache,
        deduplicator = deduplicator,
        keyGenerator = { userId -> "user:$userId" }
    )

    /**
     * Get user with deduplication and caching
     */
    suspend fun getUser(
        userId: String,
        forceRefresh: Boolean = false
    ): Result<User> {
        return runCatching {
            cacheAsideRepo.get(
                key = userId,
                forceRefresh = forceRefresh
            ) { id ->
                api.getUser(id)
            }
        }
    }

    /**
     * Get user as Flow (emits cached then fresh)
     */
    fun getUserFlow(
        userId: String,
        forceRefresh: Boolean = false
    ): Flow<User> {
        return cacheAsideRepo.getAsFlow(
            key = userId,
            forceRefresh = forceRefresh
        ) { id ->
            api.getUser(id)
        }
    }

    /**
     * Search users with debouncing
     */
    private val searchDebouncer = Debouncer()

    suspend fun searchUsers(query: String): Result<List<User>> {
        if (query.isBlank()) {
            return Result.success(emptyList())
        }

        return runCatching {
            searchDebouncer.debounce(300L) {
                deduplicator.deduplicate("search:$query") {
                    api.searchUsers(query)
                }
            } ?: emptyList()
        }
    }

    /**
     * Get multiple users with batching
     */
    suspend fun getUsers(userIds: List<String>): Result<List<User>> {
        return runCatching {
            // Check cache first
            val cached = userIds.mapNotNull { cache.get(it) }
            val cachedIds = cached.map { it.id }.toSet()

            // Fetch missing users
            val missingIds = userIds.filter { it !in cachedIds }

            if (missingIds.isEmpty()) {
                return@runCatching cached
            }

            // Batch fetch with deduplication
            val fresh = deduplicator.deduplicate("users:${missingIds.sorted().joinToString(",")}") {
                api.getUsers(missingIds)
            }

            // Update cache
            fresh.forEach { cache.put(it.id, it) }

            cached + fresh
        }
    }

    /**
     * Update user with optimistic update
     */
    suspend fun updateUser(
        userId: String,
        update: UserUpdate
    ): Result<User> {
        return runCatching {
            // Optimistic update
            cache.get(userId)?.let { currentUser ->
                val optimistic = currentUser.copy(
                    name = update.name ?: currentUser.name,
                    email = update.email ?: currentUser.email
                )
                cache.put(userId, optimistic)
            }

            // Actual update
            val updated = deduplicator.deduplicate("update:$userId") {
                api.updateUser(userId, update)
            }

            // Update cache with server response
            cache.put(userId, updated)

            updated
        }.onFailure {
            // Revert optimistic update on failure
            deduplicator.cancelRequest("user:$userId")
        }
    }

    /**
     * Invalidate user cache
     */
    suspend fun invalidateUser(userId: String) {
        cacheAsideRepo.invalidate(userId)
    }

    /**
     * Clear all caches
     */
    suspend fun clearAll() {
        cacheAsideRepo.clear()
    }
}
```

### Testing Concurrent Requests

```kotlin
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.test.runTest
import org.junit.Test
import kotlin.system.measureTimeMillis
import kotlin.test.assertEquals

class DeduplicationTest {

    @Test
    fun `test request deduplication prevents multiple calls`() = runTest {
        var requestCount = 0
        val deduplicator = RequestDeduplicator(this)

        // Simulate 100 concurrent requests for same data
        val requests = (1..100).map {
            async {
                deduplicator.deduplicate("test") {
                    requestCount++
                    delay(100) // Simulate network delay
                    "result"
                }
            }
        }

        val results = requests.awaitAll()

        // Assert only 1 actual request was made
        assertEquals(1, requestCount)

        // Assert all got same result
        assertEquals(100, results.size)
        results.forEach { assertEquals("result", it) }
    }

    @Test
    fun `test performance improvement with deduplication`() = runTest {
        val repository = OptimizedUserRepository(mockApi, this)

        // Without deduplication: ~1000ms (10 requests * 100ms each)
        // With deduplication: ~100ms (1 request * 100ms)

        val timeWithDedup = measureTimeMillis {
            val requests = (1..10).map {
                async {
                    repository.getUser("123")
                }
            }
            requests.awaitAll()
        }

        // Should be close to single request time
        assert(timeWithDedup < 200L) { "Expected < 200ms, got ${timeWithDedup}ms" }
    }

    @Test
    fun `test cache-aside pattern reduces network calls`() = runTest {
        var networkCalls = 0
        val mockApi = object : UserApiService {
            override suspend fun getUser(userId: String): User {
                networkCalls++
                delay(100)
                return User(userId, "Test User")
            }
        }

        val repository = OptimizedUserRepository(mockApi, this)

        // First call: cache miss, network call
        repository.getUser("123")
        assertEquals(1, networkCalls)

        // Second call: cache hit, no network call
        repository.getUser("123")
        assertEquals(1, networkCalls)

        // Force refresh: network call
        repository.getUser("123", forceRefresh = true)
        assertEquals(2, networkCalls)
    }
}
```

### Best Practices

1. **Choose Right Strategy**
   ```kotlin
   // Mutex: Simple, sequential execution
   // Deferred: Best for many concurrent callers
   // SharedFlow: Best for reactive streams
   ```

2. **Set Appropriate TTL**
   ```kotlin
   val cache = MemoryCache<String, User>(
       maxSize = 100,
       ttlMs = TimeUnit.MINUTES.toMillis(5) // 5 minutes
   )
   ```

3. **Handle Cancellation**
   ```kotlin
   fun cancelRequest(key: String) {
       deduplicator.cancelRequest(key)
   }
   ```

4. **Use Debouncing for User Input**
   ```kotlin
   // Debounce search queries
   searchDebouncer.debounce(300L) {
       searchUsers(query)
   }
   ```

5. **Monitor In-Flight Requests**
   ```kotlin
   val count = deduplicator.getInFlightCount()
   logger.debug("In-flight requests: $count")
   ```

### Common Pitfalls

1. **Not Handling Errors**
   ```kotlin
   // BAD: Error doesn't clean up
   // GOOD: Clean up on error
   try {
       block()
   } finally {
       requests.remove(key)
   }
   ```

2. **Memory Leaks from Unbounded Cache**
   ```kotlin
   // BAD: Unbounded cache
   val cache = mutableMapOf<String, Data>()

   // GOOD: LRU cache with max size
   val cache = MemoryCache(maxSize = 100)
   ```

3. **Not Considering TTL**
   ```kotlin
   // Stale data can be served without TTL
   val cache = MemoryCache(ttlMs = TimeUnit.MINUTES.toMillis(5))
   ```

4. **Forgetting forceRefresh**
   ```kotlin
   // Allow bypassing cache when needed
   fun getUser(userId: String, forceRefresh: Boolean = false)
   ```

### Summary

Request deduplication provides:

- **Reduced Network Calls**: Multiple callers share single request
- **Better Performance**: Less latency, bandwidth, and server load
- **Resource Efficiency**: Fewer concurrent connections
- **Improved UX**: Faster responses from cache
- **Scalability**: Handle many concurrent users efficiently

**Key Techniques:**
- Deduplication with Mutex/Deferred
- Cache-aside pattern
- Debouncing for user input
- Throttling for frequent events
- LRU caching with TTL

---

## Ответ (RU)
**Дедупликация запросов** - это техника оптимизации, которая предотвращает выполнение множественных идентичных сетевых запросов одновременно. Когда несколько частей приложения запрашивают одни и те же данные одновременно, дедупликация гарантирует, что выполняется только один реальный сетевой вызов, а все вызывающие получают один и тот же результат.

### Проблема

```kotlin
// Проблема: Множественные одновременные запросы одних данных
class UserViewModel(private val repository: UserRepository) : ViewModel() {

    init {
        viewModelScope.launch {
            val user = repository.getUser("123") // Запрос 1
        }

        viewModelScope.launch {
            val user = repository.getUser("123") // Дубликат!
        }

        viewModelScope.launch {
            val user = repository.getUser("123") // Ещё дубликат!
        }
    }

    // Результат: 3 идентичных сетевых запроса выполняются одновременно
}
```

### Стратегии дедупликации

#### 1. Дедупликация на основе Mutex

```kotlin
class MutexDeduplicator {
    private val mutexMap = ConcurrentHashMap<String, Mutex>()

    suspend fun <T> deduplicate(
        key: String,
        block: suspend () -> T
    ): T {
        val mutex = mutexMap.getOrPut(key) { Mutex() }

        return mutex.withLock {
            block()
        }
    }
}
```

#### 2. Дедупликация на основе Deferred

```kotlin
class DeferredDeduplicator(private val scope: CoroutineScope) {
    private val requests = ConcurrentHashMap<String, Deferred<*>>()

    suspend fun <T> deduplicate(
        key: String,
        block: suspend () -> T
    ): T {
        @Suppress("UNCHECKED_CAST")
        val deferred = requests.getOrPut(key) {
            scope.async {
                try {
                    block()
                } finally {
                    requests.remove(key)
                }
            }
        } as Deferred<T>

        return deferred.await()
    }
}
```

### Паттерн Cache-Aside с дедупликацией

```kotlin
class CacheAsideRepository<K, V>(
    private val cache: Cache<K, V>,
    private val deduplicator: RequestDeduplicator,
    private val keyGenerator: (K) -> String
) {

    suspend fun get(
        key: K,
        forceRefresh: Boolean = false,
        loader: suspend (K) -> V
    ): V {
        // Сначала проверить кеш
        if (!forceRefresh) {
            cache.get(key)?.let { return it }
        }

        // Нет в кеше, загрузить с дедупликацией
        val deduplicationKey = keyGenerator(key)
        val value = deduplicator.deduplicate(deduplicationKey) {
            loader(key)
        }

        cache.put(key, value)
        return value
    }
}
```

### Debouncing и Throttling

```kotlin
// Debouncing: Ждать период тишины перед выполнением
class Debouncer {
    private val lastCallTime = AtomicLong(0)
    private val mutex = Mutex()

    suspend fun <T> debounce(
        delayMs: Long,
        block: suspend () -> T
    ): T? {
        val currentTime = System.currentTimeMillis()
        lastCallTime.set(currentTime)

        delay(delayMs)

        // Выполнить только если не было новых вызовов
        return if (lastCallTime.get() == currentTime) {
            mutex.withLock {
                if (lastCallTime.get() == currentTime) {
                    block()
                } else null
            }
        } else null
    }
}

// Throttling: Ограничить частоту выполнения
class Throttler {
    private val lastExecutionTime = AtomicLong(0)

    suspend fun <T> throttle(
        intervalMs: Long,
        block: suspend () -> T
    ): T? {
        val currentTime = System.currentTimeMillis()
        val lastTime = lastExecutionTime.get()

        if (currentTime - lastTime < intervalMs) {
            return null // Слишком рано, пропустить
        }

        lastExecutionTime.set(currentTime)
        return block()
    }
}
```

### Полный Repository с дедупликацией

```kotlin
class OptimizedUserRepository(
    private val api: UserApiService,
    private val scope: CoroutineScope
) {

    private val deduplicator = RequestDeduplicator(scope)
    private val cache = MemoryCache<String, User>(maxSize = 100)

    suspend fun getUser(
        userId: String,
        forceRefresh: Boolean = false
    ): Result<User> {
        return runCatching {
            // Проверить кеш
            if (!forceRefresh) {
                cache.get(userId)?.let { return@runCatching it }
            }

            // Загрузить с дедупликацией
            deduplicator.deduplicate("user:$userId") {
                val user = api.getUser(userId)
                cache.put(userId, user)
                user
            }
        }
    }

    // Поиск с debouncing
    private val searchDebouncer = Debouncer()

    suspend fun searchUsers(query: String): Result<List<User>> {
        return runCatching {
            searchDebouncer.debounce(300L) {
                deduplicator.deduplicate("search:$query") {
                    api.searchUsers(query)
                }
            } ?: emptyList()
        }
    }
}
```

### Best Practices

1. **Выбирайте правильную стратегию**
   - Mutex: Простая, последовательное выполнение
   - Deferred: Лучше для многих одновременных вызовов
   - SharedFlow: Лучше для реактивных потоков

2. **Устанавливайте подходящий TTL**
   ```kotlin
   val cache = MemoryCache(ttlMs = TimeUnit.MINUTES.toMillis(5))
   ```

3. **Обрабатывайте отмену**
   ```kotlin
   deduplicator.cancelRequest(key)
   ```

4. **Используйте debouncing для пользовательского ввода**
   ```kotlin
   searchDebouncer.debounce(300L) { searchUsers(query) }
   ```

### Распространённые ошибки

1. **Не обработка ошибок**
2. **Утечки памяти из неограниченного кеша**
3. **Не учёт TTL**
4. **Забывание forceRefresh**

### Резюме

Дедупликация запросов обеспечивает:

- **Сокращение сетевых вызовов**: Множество вызывающих делят один запрос
- **Лучшая производительность**: Меньше задержек и нагрузки на сервер
- **Эффективность ресурсов**: Меньше одновременных соединений
- **Улучшенный UX**: Быстрые ответы из кеша
- **Масштабируемость**: Эффективная обработка многих пользователей

**Ключевые техники:**
- Дедупликация с Mutex/Deferred
- Паттерн Cache-aside
- Debouncing для пользовательского ввода
- Throttling для частых событий
- LRU кеширование с TTL

---

## Related Questions

### Prerequisites (Easier)
- [[q-http-protocols-comparison--android--medium]] - Networking
- [[q-kmm-ktor-networking--multiplatform--medium]] - Networking
- [[q-retrofit-call-adapter-advanced--networking--medium]] - Networking

### Related (Hard)
- [[q-data-sync-unstable-network--android--hard]] - Networking
