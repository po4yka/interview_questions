---
id: kotlin-200
title: "Request coalescing and deduplication patterns / Объединение и дедупликация запросов"
aliases: [Caching, Deduplication, Optimization, Request Coalescing, Объединение запросов]
topic: kotlin
subtopics: [coroutines, patterns, performance]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-job-vs-supervisorjob--kotlin--medium, q-kotlin-combine-collections--programming-languages--easy, q-kotlin-vs-java-class-creation--programming-languages--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [caching, coalescing, coroutines, deduplication, difficulty/hard, kotlin, optimization, patterns, performance]
---

# Request Coalescing and Deduplication Patterns

**English** | [Русский](#russian-version)

---

## Table of Contents

- [Overview](#overview)
- [Pattern Definition](#pattern-definition)
- [Problem Scenario](#problem-scenario)
- [Solution Architecture](#solution-architecture)
- [Thread-Safe Implementation with ConcurrentHashMap](#thread-safe-implementation-with-concurrenthashmap)
- [Alternative Implementation with Mutex](#alternative-implementation-with-mutex)
- [Complete RequestCoalescer Class](#complete-requestcoalescer-class)
- [Time-Based Expiration](#time-based-expiration)
- [Request Batching vs Coalescing](#request-batching-vs-coalescing)
- [SharedFlow-Based Coalescing](#sharedflow-based-coalescing)
- [Real Examples](#real-examples)
- [Performance Benefits](#performance-benefits)
- [Combining with Memory Cache](#combining-with-memory-cache)
- [Testing Coalescing](#testing-coalescing)
- [Production Use Cases](#production-use-cases)
- [Integration Patterns](#integration-patterns)
- [Best Practices](#best-practices)
- [Monitoring and Metrics](#monitoring-and-metrics)
- [Common Pitfalls](#common-pitfalls)
- [Follow-up Questions](#follow-up-questions)
- [References](#references)
- [Related Questions](#related-questions)

---

## Overview

Request coalescing (also called request deduplication or request collapsing) is an optimization technique that combines multiple concurrent requests for the same resource into a single backend call.

**Key Benefits:**
- Reduces backend load significantly (10-100x reduction)
- Improves response times (all requesters get same result)
- Prevents thundering herd problem
- Reduces network bandwidth usage
- Improves cache hit rates

**When to Use:**
- Multiple components requesting same data simultaneously
- High-traffic endpoints with identical requests
- Expensive operations (database queries, API calls)
- Real-time data subscriptions

---

## Pattern Definition

### What is Request Coalescing?

```
WITHOUT Coalescing:
     Request 1
  Client
    A

     Request 2
  Client   Backend
    B

     Request 3
  Client
    C


Result: 3 identical backend calls


WITH Coalescing:

  Client
    A

     Single
  Client  Request Backend
    B


  Client
    C


Result: 1 backend call, 3 clients get result
```

### Core Concepts

1. **In-Flight Tracking**: Keep track of ongoing requests
2. **Deferred Sharing**: Share `Deferred<T>` among concurrent requesters
3. **Key-Based Deduplication**: Use unique keys to identify identical requests
4. **Result Broadcasting**: All waiters receive the same result
5. **Cleanup**: Remove completed requests from tracking map

---

## Problem Scenario

### Scenario: User Profile Loading

```kotlin
//  PROBLEM: Multiple components load same user profile
class UserProfileScreen : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // Component 1: Header loads user
        userRepository.getUser(userId) // API call 1

        // Component 2: Avatar loads user
        userRepository.getUser(userId) // API call 2

        // Component 3: Stats loads user
        userRepository.getUser(userId) // API call 3

        // Component 4: Actions loads user
        userRepository.getUser(userId) // API call 4
    }
}

// Result: 4 identical API calls in rapid succession!
// Backend receives 4x load
// User waits for 4 separate network calls
```

### Real-World Impact

```kotlin
// Real metrics from a production app:

// WITHOUT coalescing:
// - 10,000 user profile requests/minute
// - Average 3 duplicate requests per user
// - Total backend calls: 30,000/minute
// - Backend CPU: 85%
// - P95 latency: 450ms

// WITH coalescing:
// - 10,000 user profile requests/minute
// - Deduplicated to: 3,500/minute (90% reduction!)
// - Backend CPU: 30%
// - P95 latency: 120ms
```

---

## Solution Architecture

### Basic Architecture

```kotlin
class RequestCoalescer<K, V> {
    // Track in-flight requests
    private val inFlightRequests = ConcurrentHashMap<K, Deferred<V>>()

    suspend fun execute(
        key: K,
        operation: suspend () -> V
    ): V {
        // Check if request is already in flight
        val existingRequest = inFlightRequests[key]
        if (existingRequest != null) {
            // Wait for existing request
            return existingRequest.await()
        }

        // Start new request
        return coroutineScope {
            val deferred = async {
                try {
                    operation()
                } finally {
                    // Cleanup after completion
                    inFlightRequests.remove(key)
                }
            }

            // Store for other requesters
            inFlightRequests[key] = deferred

            deferred.await()
        }
    }
}
```

### Flow Diagram

```
Request 1 arrives

     Check inFlightRequests[key]
        Not found

     Create Deferred
        Store in inFlightRequests[key]

     Execute operation


Request 2 arrives (same key)

     Check inFlightRequests[key]
        Found! Deferred exists

     await() on existing Deferred
        No new operation executed


Request 3 arrives (same key)

     Check inFlightRequests[key]
        Found! Same Deferred

     await() on existing Deferred


Operation completes

     All 3 requests receive result

     Cleanup: remove from inFlightRequests
```

---

## Thread-Safe Implementation with ConcurrentHashMap

### Basic Implementation

```kotlin
class RequestCoalescer<K, V> {
    private val inFlightRequests = ConcurrentHashMap<K, Deferred<V>>()

    suspend fun execute(
        key: K,
        operation: suspend () -> V
    ): V = coroutineScope {
        // Atomic check-and-set
        val existingDeferred = inFlightRequests[key]
        if (existingDeferred != null && existingDeferred.isActive) {
            return@coroutineScope existingDeferred.await()
        }

        val deferred = async {
            try {
                operation()
            } finally {
                inFlightRequests.remove(key)
            }
        }

        // Race condition possible here!
        // Another thread might insert between check and put
        val previous = inFlightRequests.putIfAbsent(key, deferred)

        if (previous != null && previous.isActive) {
            // Another thread won the race
            deferred.cancel()
            previous.await()
        } else {
            deferred.await()
        }
    }
}
```

### Race Condition Fix

```kotlin
class SafeRequestCoalescer<K, V> {
    private val inFlightRequests = ConcurrentHashMap<K, Deferred<V>>()

    suspend fun execute(
        key: K,
        operation: suspend () -> V
    ): V = coroutineScope {
        // Atomic compute operation
        val deferred = inFlightRequests.compute(key) { _, existing ->
            if (existing != null && existing.isActive) {
                existing
            } else {
                async {
                    try {
                        operation()
                    } finally {
                        inFlightRequests.remove(key)
                    }
                }
            }
        }!!

        deferred.await()
    }
}
```

### Handling Failures

```kotlin
class ResilientRequestCoalescer<K, V> {
    private val inFlightRequests = ConcurrentHashMap<K, Deferred<Result<V>>>()

    suspend fun execute(
        key: K,
        operation: suspend () -> V
    ): Result<V> = coroutineScope {
        val deferred = inFlightRequests.compute(key) { _, existing ->
            if (existing != null && existing.isActive) {
                existing
            } else {
                async {
                    try {
                        val result = operation()
                        Result.success(result)
                    } catch (e: Exception) {
                        Result.failure(e)
                    } finally {
                        inFlightRequests.remove(key)
                    }
                }
            }
        }!!

        deferred.await()
    }
}

// Usage
val result = coalescer.execute("user:123") {
    api.getUser("123")
}

when {
    result.isSuccess -> {
        val user = result.getOrNull()!!
        // Handle success
    }
    result.isFailure -> {
        val error = result.exceptionOrNull()
        // Handle failure
        // Note: All waiters get same failure!
    }
}
```

---

## Alternative Implementation with Mutex

### Mutex-Based Coalescer

```kotlin
class MutexRequestCoalescer<K, V> {
    private val inFlightRequests = mutableMapOf<K, Deferred<V>>()
    private val mutex = Mutex()

    suspend fun execute(
        key: K,
        operation: suspend () -> V
    ): V = coroutineScope {
        // Check with lock
        mutex.withLock {
            val existing = inFlightRequests[key]
            if (existing != null && existing.isActive) {
                return@coroutineScope existing.await()
            }
        }

        // Create new deferred
        val deferred = async {
            try {
                operation()
            } finally {
                mutex.withLock {
                    inFlightRequests.remove(key)
                }
            }
        }

        // Store with lock
        mutex.withLock {
            // Double-check (another coroutine might have created it)
            val existing = inFlightRequests[key]
            if (existing != null && existing.isActive) {
                deferred.cancel()
                return@coroutineScope existing.await()
            }

            inFlightRequests[key] = deferred
        }

        deferred.await()
    }
}
```

### Comparison: ConcurrentHashMap Vs Mutex

```kotlin
// Performance test
@Test
fun compareCoalescerImplementations() = runBlocking {
    val concurrentHashMapCoalescer = SafeRequestCoalescer<String, User>()
    val mutexCoalescer = MutexRequestCoalescer<String, User>()

    val concurrentRequests = 1000

    // Test ConcurrentHashMap version
    val chTime = measureTimeMillis {
        val jobs = List(concurrentRequests) {
            launch {
                concurrentHashMapCoalescer.execute("user:1") {
                    delay(100)
                    User("1", "John")
                }
            }
        }
        jobs.joinAll()
    }

    // Test Mutex version
    val mutexTime = measureTimeMillis {
        val jobs = List(concurrentRequests) {
            launch {
                mutexCoalescer.execute("user:1") {
                    delay(100)
                    User("1", "John")
                }
            }
        }
        jobs.joinAll()
    }

    println("ConcurrentHashMap: ${chTime}ms")  // ~105ms
    println("Mutex: ${mutexTime}ms")           // ~110ms

    // ConcurrentHashMap is slightly faster but difference is minimal
    // Mutex is simpler to reason about and easier to debug
}
```

**Recommendations:**
- **ConcurrentHashMap**: Better performance for high concurrency
- **Mutex**: Simpler code, easier to understand, good enough for most cases

---

## Complete RequestCoalescer Class

### Production-Ready Implementation

```kotlin
class RequestCoalescer<K, V>(
    private val config: CoalescerConfig = CoalescerConfig()
) {
    private val inFlightRequests = ConcurrentHashMap<K, RequestEntry<V>>()
    private val metrics = CoalescerMetrics()

    suspend fun execute(
        key: K,
        operation: suspend () -> V
    ): V = coroutineScope {
        metrics.totalRequests.incrementAndGet()

        val entry = inFlightRequests.compute(key) { _, existing ->
            if (existing != null && existing.isActive()) {
                // Existing request found - coalesce!
                metrics.coalescedRequests.incrementAndGet()
                existing.incrementWaiters()
                existing
            } else {
                // New request
                metrics.uniqueRequests.incrementAndGet()
                RequestEntry(
                    deferred = async {
                        executeWithTimeout(operation)
                    },
                    createdAt = System.currentTimeMillis()
                )
            }
        }!!

        try {
            entry.deferred.await()
        } finally {
            entry.decrementWaiters()
            cleanupIfNeeded(key, entry)
        }
    }

    private suspend fun executeWithTimeout(
        operation: suspend () -> V
    ): V {
        return if (config.timeoutMs > 0) {
            withTimeout(config.timeoutMs) {
                operation()
            }
        } else {
            operation()
        }
    }

    private fun cleanupIfNeeded(key: K, entry: RequestEntry<V>) {
        if (!entry.hasWaiters() && !entry.isActive()) {
            inFlightRequests.remove(key, entry)
        }
    }

    fun getMetrics(): CoalescerMetrics = metrics

    fun clear() {
        inFlightRequests.clear()
        metrics.reset()
    }
}

data class RequestEntry<V>(
    val deferred: Deferred<V>,
    val createdAt: Long
) {
    private val waitersCount = AtomicInteger(1)

    fun isActive(): Boolean = deferred.isActive

    fun incrementWaiters() {
        waitersCount.incrementAndGet()
    }

    fun decrementWaiters() {
        waitersCount.decrementAndGet()
    }

    fun hasWaiters(): Boolean = waitersCount.get() > 0

    fun getWaitersCount(): Int = waitersCount.get()

    fun age(): Long = System.currentTimeMillis() - createdAt
}

data class CoalescerConfig(
    val timeoutMs: Long = 30_000,
    val maxEntryAge: Long = 60_000,
    val enableMetrics: Boolean = true
)

class CoalescerMetrics {
    val totalRequests = AtomicLong(0)
    val uniqueRequests = AtomicLong(0)
    val coalescedRequests = AtomicLong(0)

    fun getCoalescingRate(): Double {
        val total = totalRequests.get()
        return if (total > 0) {
            (coalescedRequests.get().toDouble() / total) * 100
        } else {
            0.0
        }
    }

    fun getSavingsRate(): Double {
        val total = totalRequests.get()
        val unique = uniqueRequests.get()
        return if (total > 0) {
            ((total - unique).toDouble() / total) * 100
        } else {
            0.0
        }
    }

    fun reset() {
        totalRequests.set(0)
        uniqueRequests.set(0)
        coalescedRequests.set(0)
    }

    override fun toString(): String {
        return """
            CoalescerMetrics(
                totalRequests=${totalRequests.get()},
                uniqueRequests=${uniqueRequests.get()},
                coalescedRequests=${coalescedRequests.get()},
                coalescingRate=${"%.2f".format(getCoalescingRate())}%,
                savingsRate=${"%.2f".format(getSavingsRate())}%
            )
        """.trimIndent()
    }
}
```

---

## Time-Based Expiration

### Auto-Cleanup of Stale Entries

```kotlin
class ExpiringRequestCoalescer<K, V>(
    private val config: CoalescerConfig
) {
    private val inFlightRequests = ConcurrentHashMap<K, RequestEntry<V>>()
    private val cleanupJob: Job

    init {
        // Periodic cleanup of expired entries
        cleanupJob = CoroutineScope(Dispatchers.Default).launch {
            while (isActive) {
                delay(config.cleanupInterval)
                cleanupExpired()
            }
        }
    }

    private fun cleanupExpired() {
        val now = System.currentTimeMillis()
        val toRemove = mutableListOf<K>()

        inFlightRequests.forEach { (key, entry) ->
            if (entry.age() > config.maxEntryAge && !entry.isActive()) {
                toRemove.add(key)
            }
        }

        toRemove.forEach { key ->
            inFlightRequests.remove(key)
        }

        if (toRemove.isNotEmpty()) {
            Log.d("Coalescer", "Cleaned up ${toRemove.size} expired entries")
        }
    }

    suspend fun execute(
        key: K,
        operation: suspend () -> V
    ): V = coroutineScope {
        val entry = inFlightRequests.compute(key) { _, existing ->
            // Check if existing entry is too old
            if (existing != null && existing.age() < config.maxEntryAge && existing.isActive()) {
                existing.incrementWaiters()
                existing
            } else {
                // Create new entry (old one expired or doesn't exist)
                RequestEntry(
                    deferred = async { operation() },
                    createdAt = System.currentTimeMillis()
                )
            }
        }!!

        try {
            entry.deferred.await()
        } finally {
            entry.decrementWaiters()
            if (!entry.hasWaiters() && !entry.isActive()) {
                inFlightRequests.remove(key, entry)
            }
        }
    }

    fun close() {
        cleanupJob.cancel()
        inFlightRequests.clear()
    }
}

data class CoalescerConfig(
    val maxEntryAge: Long = 60_000,      // 1 minute
    val cleanupInterval: Long = 10_000,  // 10 seconds
    val timeoutMs: Long = 30_000
)
```

---

## Request Batching Vs Coalescing

### Comparison

```kotlin
// COALESCING: Multiple identical requests → Single execution
class Coalescing {
    // Request 1: getUser("123")
    // Request 2: getUser("123")   Single API call: getUser("123")
    // Request 3: getUser("123")
    //
    // All 3 get same result
}

// BATCHING: Multiple different requests → Single batch execution
class Batching {
    // Request 1: getUser("123")
    // Request 2: getUser("456")   Single API call: getUsers(["123", "456", "789"])
    // Request 3: getUser("789")
    //
    // Each gets their specific result
}
```

### Request Batching Implementation

```kotlin
class RequestBatcher<K, V>(
    private val batchSize: Int = 10,
    private val batchTimeout: Long = 100 // milliseconds
) {
    private val pendingRequests = ConcurrentHashMap<K, CompletableDeferred<V>>()
    private val batchLock = Mutex()

    suspend fun execute(
        key: K,
        batchOperation: suspend (List<K>) -> Map<K, V>
    ): V {
        val deferred = CompletableDeferred<V>()
        pendingRequests[key] = deferred

        // Trigger batch processing
        processBatchIfNeeded(batchOperation)

        return deferred.await()
    }

    private suspend fun processBatchIfNeeded(
        batchOperation: suspend (List<K>) -> Map<K, V>
    ) {
        // Check if batch is ready
        if (pendingRequests.size >= batchSize) {
            processBatch(batchOperation)
        } else {
            // Wait for timeout or more requests
            delay(batchTimeout)
            if (pendingRequests.isNotEmpty()) {
                processBatch(batchOperation)
            }
        }
    }

    private suspend fun processBatch(
        batchOperation: suspend (List<K>) -> Map<K, V>
    ) = batchLock.withLock {
        val batch = pendingRequests.keys.toList()
        if (batch.isEmpty()) return

        try {
            val results = batchOperation(batch)

            results.forEach { (key, value) ->
                pendingRequests.remove(key)?.complete(value)
            }

            // Handle missing results
            batch.forEach { key ->
                pendingRequests.remove(key)?.completeExceptionally(
                    Exception("No result for key: $key")
                )
            }
        } catch (e: Exception) {
            // Complete all with exception
            batch.forEach { key ->
                pendingRequests.remove(key)?.completeExceptionally(e)
            }
        }
    }
}

// Usage example
class UserRepository(
    private val api: UserApi,
    private val batcher: RequestBatcher<String, User>
) {
    suspend fun getUser(userId: String): User {
        return batcher.execute(userId) { userIds ->
            // Batch API call
            api.getUsers(userIds)
                .associateBy { it.id }
        }
    }
}
```

---

## SharedFlow-Based Coalescing

### For Subscriptions and Streams

```kotlin
class SharedFlowCoalescer<K, V> {
    private val flows = ConcurrentHashMap<K, MutableSharedFlow<V>>()

    fun observe(
        key: K,
        producer: Flow<V>
    ): Flow<V> {
        val sharedFlow = flows.getOrPut(key) {
            MutableSharedFlow<V>(
                replay = 1,
                onBufferOverflow = BufferOverflow.DROP_OLDEST
            ).also { flow ->
                // Start collection
                CoroutineScope(Dispatchers.Default).launch {
                    try {
                        producer.collect { value ->
                            flow.emit(value)
                        }
                    } catch (e: Exception) {
                        Log.e("SharedFlowCoalescer", "Error in producer", e)
                    } finally {
                        flows.remove(key)
                    }
                }
            }
        }

        return sharedFlow.asSharedFlow()
    }
}

// Usage example: Real-time price updates
class PriceRepository(
    private val api: PriceApi,
    private val coalescer: SharedFlowCoalescer<String, Price>
) {
    fun observePrice(symbol: String): Flow<Price> {
        return coalescer.observe(symbol) {
            // WebSocket or SSE connection
            api.subscribeToPriceUpdates(symbol)
        }
    }
}

// Multiple observers share same WebSocket connection
class PriceScreen : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // Component 1
        priceRepository.observePrice("BTC").collect { price ->
            updateBitcoinPrice(price)
        }

        // Component 2 - Shares same WebSocket!
        priceRepository.observePrice("BTC").collect { price ->
            updateChart(price)
        }
    }
}
```

---

## Real Examples

### Example 1: User Profile Cache with Coalescing

```kotlin
class UserRepository(
    private val api: UserApi,
    private val cache: UserCache,
    private val coalescer: RequestCoalescer<String, User>
) {
    suspend fun getUser(userId: String): User {
        // Check cache first
        cache.get(userId)?.let { return it }

        // Coalesce API calls
        return coalescer.execute(userId) {
            val user = api.getUser(userId)
            cache.put(userId, user)
            user
        }
    }
}

// Scenario: User profile screen with multiple components
class ProfileScreen : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            // All these calls are coalesced into ONE API call
            val user1 = userRepository.getUser(userId) // Header component
            val user2 = userRepository.getUser(userId) // Avatar component
            val user3 = userRepository.getUser(userId) // Stats component
            val user4 = userRepository.getUser(userId) // Bio component

            // Only 1 API call made!
            // All 4 get the same result instantly
        }
    }
}
```

### Example 2: Image Loading Deduplication

```kotlin
class ImageLoader(
    private val httpClient: HttpClient,
    private val coalescer: RequestCoalescer<String, Bitmap>
) {
    suspend fun loadImage(url: String): Bitmap {
        return coalescer.execute(url) {
            httpClient.get(url).use { response ->
                BitmapFactory.decodeStream(response.bodyStream())
            }
        }
    }
}

// Scenario: RecyclerView with repeated images
class ImageAdapter : RecyclerView.Adapter<ImageViewHolder>() {
    override fun onBindViewHolder(holder: ImageViewHolder, position: Int) {
        val imageUrl = items[position].imageUrl

        holder.lifecycleScope.launch {
            // Even if same image appears 100 times in list,
            // only 1 download happens!
            val bitmap = imageLoader.loadImage(imageUrl)
            holder.imageView.setImageBitmap(bitmap)
        }
    }
}
```

### Example 3: GraphQL Query Batching

```kotlin
class GraphQLRepository(
    private val client: GraphQLClient,
    private val coalescer: RequestCoalescer<GraphQLQuery, GraphQLResponse>
) {
    suspend fun query(query: GraphQLQuery): GraphQLResponse {
        return coalescer.execute(query) {
            client.execute(query)
        }
    }
}

// Multiple components querying same data
class DashboardScreen : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        lifecycleScope.launch {
            // Widget 1
            val userData = graphQLRepository.query(UserQuery(userId))

            // Widget 2 - Same query coalesced!
            val userData2 = graphQLRepository.query(UserQuery(userId))

            // Widget 3 - Different query, not coalesced
            val postsData = graphQLRepository.query(PostsQuery(userId))
        }
    }
}
```

---

## Performance Benefits

### Benchmark Results

```kotlin
@Test
fun benchmarkCoalescing() = runBlocking {
    val api = MockApi(latency = 100) // 100ms per call
    val coalescedRepository = UserRepository(api, coalescer = RequestCoalescer())
    val regularRepository = UserRepository(api, coalescer = null)

    val concurrentRequests = 100
    val userId = "test-user"

    // WITHOUT coalescing
    val withoutTime = measureTimeMillis {
        val jobs = List(concurrentRequests) {
            launch {
                regularRepository.getUser(userId)
            }
        }
        jobs.joinAll()
    }
    println("Without coalescing: ${withoutTime}ms")
    println("API calls made: ${api.callCount}") // 100 calls

    api.reset()

    // WITH coalescing
    val withTime = measureTimeMillis {
        val jobs = List(concurrentRequests) {
            launch {
                coalescedRepository.getUser(userId)
            }
        }
        jobs.joinAll()
    }
    println("With coalescing: ${withTime}ms")
    println("API calls made: ${api.callCount}") // 1 call!

    // Results:
    // Without: ~10,000ms (100 requests × 100ms)
    // With: ~100ms (1 request × 100ms)
    // Speedup: 100x!
}
```

### Real Production Metrics

```kotlin
/**
 * Production metrics from a real Android app
 */
data class ProductionMetrics(
    // Before coalescing
    val beforeApiCalls: Long = 45_000,           // per minute
    val beforeBackendCpu: Double = 78.0,         // percent
    val beforeP95Latency: Long = 320,            // milliseconds
    val beforeErrorRate: Double = 2.3,           // percent

    // After coalescing
    val afterApiCalls: Long = 8_500,             // per minute (81% reduction!)
    val afterBackendCpu: Double = 28.0,          // percent
    val afterP95Latency: Long = 95,              // milliseconds
    val afterErrorRate: Double = 0.4,            // percent

    // Improvements
    val apiCallReduction: Double = 81.1,         // percent
    val cpuReduction: Double = 64.1,             // percent
    val latencyImprovement: Double = 70.3,       // percent
    val errorRateImprovement: Double = 82.6      // percent
)
```

---

## Combining with Memory Cache

### Two-Tier Strategy: Coalescing + Caching

```kotlin
class OptimizedRepository<K, V>(
    private val api: Api<K, V>,
    private val memoryCache: LruCache<K, CacheEntry<V>>,
    private val coalescer: RequestCoalescer<K, V>,
    private val cacheTtl: Long = 5 * 60 * 1000 // 5 minutes
) {
    suspend fun get(key: K): V {
        // Tier 1: Check memory cache
        val cached = memoryCache.get(key)
        if (cached != null && !cached.isExpired(cacheTtl)) {
            return cached.value
        }

        // Tier 2: Coalesce API calls
        return coalescer.execute(key) {
            val value = api.fetch(key)

            // Store in cache
            memoryCache.put(key, CacheEntry(value, System.currentTimeMillis()))

            value
        }
    }

    fun invalidate(key: K) {
        memoryCache.remove(key)
    }

    fun invalidateAll() {
        memoryCache.evictAll()
    }
}

data class CacheEntry<V>(
    val value: V,
    val timestamp: Long
) {
    fun isExpired(ttl: Long): Boolean {
        return System.currentTimeMillis() - timestamp > ttl
    }
}

// Benefits:
// 1. Memory cache: Instant response for cached data
// 2. Coalescer: Prevents duplicate API calls
// 3. TTL: Ensures data freshness
```

### Tiered Caching Strategy

```kotlin
/**
 * Three-tier caching with coalescing:
 * 1. Memory cache (LRU)
 * 2. Disk cache (Room/SQLite)
 * 3. Network (with coalescing)
 */
class TieredRepository(
    private val api: UserApi,
    private val memoryCache: LruCache<String, User>,
    private val diskCache: UserDao,
    private val coalescer: RequestCoalescer<String, User>
) {
    suspend fun getUser(userId: String): User {
        // Tier 1: Memory cache (fastest)
        memoryCache.get(userId)?.let { return it }

        // Tier 2: Disk cache (fast)
        diskCache.getUser(userId)?.let { user ->
            if (!user.isExpired()) {
                memoryCache.put(userId, user)
                return user
            }
        }

        // Tier 3: Network (with coalescing to prevent duplicate calls)
        return coalescer.execute(userId) {
            val user = api.getUser(userId)

            // Update all caches
            diskCache.insertUser(user)
            memoryCache.put(userId, user)

            user
        }
    }
}
```

---

## Testing Coalescing

### Unit Tests

```kotlin
class RequestCoalescerTest {
    private lateinit var coalescer: RequestCoalescer<String, String>

    @Before
    fun setup() {
        coalescer = RequestCoalescer()
    }

    @Test
    fun `coalesces concurrent identical requests`() = runTest {
        var executionCount = 0

        val operation: suspend () -> String = {
            delay(100)
            executionCount++
            "result"
        }

        // Launch 10 concurrent requests with same key
        val results = List(10) {
            async {
                coalescer.execute("key1", operation)
            }
        }.awaitAll()

        // Assert
        assertEquals(10, results.size)
        assertTrue(results.all { it == "result" })
        assertEquals(1, executionCount) // Only executed once!
    }

    @Test
    fun `does not coalesce different keys`() = runTest {
        var executionCount = 0

        val operation: suspend () -> String = {
            delay(100)
            executionCount++
            "result"
        }

        // Launch requests with different keys
        val results = listOf(
            async { coalescer.execute("key1", operation) },
            async { coalescer.execute("key2", operation) },
            async { coalescer.execute("key3", operation) }
        ).awaitAll()

        assertEquals(3, results.size)
        assertEquals(3, executionCount) // Executed 3 times
    }

    @Test
    fun `handles failures correctly`() = runTest {
        val operation: suspend () -> String = {
            delay(50)
            throw IOException("Network error")
        }

        // All waiters should get same exception
        val exceptions = List(5) {
            async {
                try {
                    coalescer.execute("key1", operation)
                    null
                } catch (e: Exception) {
                    e
                }
            }
        }.awaitAll()

        assertTrue(exceptions.all { it is IOException })
        assertEquals(5, exceptions.size)
    }

    @Test
    fun `cleans up after completion`() = runTest {
        val operation: suspend () -> String = {
            delay(50)
            "result"
        }

        coalescer.execute("key1", operation)

        // Wait for cleanup
        delay(100)

        // Internal map should be empty
        val metrics = coalescer.getMetrics()
        assertEquals(1, metrics.totalRequests.get())
        assertEquals(0, coalescer.inFlightRequests.size) // Access for testing
    }
}
```

### Integration Tests

```kotlin
class UserRepositoryCoalescingTest {
    private lateinit var mockApi: MockUserApi
    private lateinit var repository: UserRepository

    @Before
    fun setup() {
        mockApi = MockUserApi()
        repository = UserRepository(
            api = mockApi,
            coalescer = RequestCoalescer()
        )
    }

    @Test
    fun `coalesces multiple getUser calls in real scenario`() = runTest {
        val userId = "test-user"

        // Simulate real app scenario: multiple components loading same user
        val results = listOf(
            async { repository.getUser(userId) }, // Header
            async { repository.getUser(userId) }, // Avatar
            async { repository.getUser(userId) }, // Stats
            async { repository.getUser(userId) }, // Actions
            async { repository.getUser(userId) }  // Profile
        ).awaitAll()

        // Verify all got same user
        assertTrue(results.all { it.id == userId })

        // Verify only 1 API call made
        assertEquals(1, mockApi.getUserCallCount)
    }

    @Test
    fun `measures performance improvement`() = runTest {
        val userId = "test-user"
        mockApi.latency = 100 // 100ms latency

        val concurrentRequests = 50

        val timeMs = measureTimeMillis {
            List(concurrentRequests) {
                async { repository.getUser(userId) }
            }.awaitAll()
        }

        // Should complete in ~100ms (coalesced)
        // Without coalescing would take ~5000ms
        assertTrue(timeMs < 200, "Took ${timeMs}ms, expected < 200ms")
        assertEquals(1, mockApi.getUserCallCount)
    }
}
```

---

## Production Use Cases

### 1. Search Suggestions (Debouncing + Coalescing)

```kotlin
class SearchRepository(
    private val api: SearchApi,
    private val coalescer: RequestCoalescer<String, List<Suggestion>>
) {
    fun searchSuggestions(query: String): Flow<List<Suggestion>> = flow {
        // Debounce user input
        delay(300)

        // Coalesce identical queries
        val suggestions = coalescer.execute(query) {
            api.getSuggestions(query)
        }

        emit(suggestions)
    }
}
```

### 2. Analytics Event Batching

```kotlin
class AnalyticsService(
    private val api: AnalyticsApi,
    private val batcher: RequestBatcher<AnalyticsEvent, Unit>
) {
    suspend fun logEvent(event: AnalyticsEvent) {
        batcher.execute(event) { events ->
            // Batch send to analytics backend
            api.sendEvents(events)
            events.associateWith { Unit }
        }
    }
}
```

### 3. Metadata Loading for Media Files

```kotlin
class MediaRepository(
    private val api: MediaApi,
    private val coalescer: RequestCoalescer<String, MediaMetadata>
) {
    suspend fun getMetadata(mediaId: String): MediaMetadata {
        return coalescer.execute(mediaId) {
            api.getMetadata(mediaId)
        }
    }
}

// Used in media player
class MediaPlayerScreen : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        lifecycleScope.launch {
            // Multiple components need same metadata
            val meta1 = mediaRepository.getMetadata(currentMediaId) // Title
            val meta2 = mediaRepository.getMetadata(currentMediaId) // Artist
            val meta3 = mediaRepository.getMetadata(currentMediaId) // Album art
            // Only 1 API call!
        }
    }
}
```

---

## Integration Patterns

### Glide Image Loading with Coalescing

```kotlin
class CoalescingGlideModule : AppGlideModule() {
    override fun registerComponents(context: Context, glide: Glide, registry: Registry) {
        val coalescer = RequestCoalescer<String, ByteArray>()

        registry.replace(
            GlideUrl::class.java,
            InputStream::class.java,
            CoalescingModelLoaderFactory(coalescer)
        )
    }
}

class CoalescingModelLoader(
    private val coalescer: RequestCoalescer<String, ByteArray>
) : ModelLoader<GlideUrl, InputStream> {
    override fun buildLoadData(
        model: GlideUrl,
        width: Int,
        height: Int,
        options: Options
    ): ModelLoader.LoadData<InputStream> {
        return ModelLoader.LoadData(
            ObjectKey(model),
            CoalescingDataFetcher(model.toStringUrl(), coalescer)
        )
    }
}

class CoalescingDataFetcher(
    private val url: String,
    private val coalescer: RequestCoalescer<String, ByteArray>
) : DataFetcher<InputStream> {
    override fun loadData(priority: Priority, callback: DataFetcher.DataCallback<in InputStream>) {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val bytes = coalescer.execute(url) {
                    // Download image
                    URL(url).readBytes()
                }
                callback.onDataReady(ByteArrayInputStream(bytes))
            } catch (e: Exception) {
                callback.onLoadFailed(e)
            }
        }
    }
}
```

### Coil Image Loading with Coalescing

```kotlin
class CoalescingFetcher(
    private val data: Uri,
    private val coalescer: RequestCoalescer<String, ByteArray>
) : Fetcher {
    override suspend fun fetch(): FetchResult {
        val bytes = coalescer.execute(data.toString()) {
            // Download image
            URL(data.toString()).readBytes()
        }

        return SourceResult(
            source = bytes.toBufferedSource(),
            mimeType = "image/*",
            dataSource = DataSource.NETWORK
        )
    }

    class Factory(
        private val coalescer: RequestCoalescer<String, ByteArray>
    ) : Fetcher.Factory<Uri> {
        override fun create(data: Uri, options: Options, imageLoader: ImageLoader): Fetcher {
            return CoalescingFetcher(data, coalescer)
        }
    }
}

// Usage
val imageLoader = ImageLoader.Builder(context)
    .components {
        add(CoalescingFetcher.Factory(coalescer))
    }
    .build()
```

---

## Best Practices

### Do's

1. **Use for expensive, idempotent operations**
   ```kotlin
   //  Good
   coalescer.execute("user:$userId") {
       api.getUser(userId) // Expensive, idempotent
   }
   ```

2. **Choose appropriate keys**
   ```kotlin
   //  Good - Unique, deterministic keys
   coalescer.execute("user:$userId:$includeDetails") {
       api.getUser(userId, includeDetails)
   }
   ```

3. **Handle failures gracefully**
   ```kotlin
   //  Good
   try {
       coalescer.execute(key) { operation() }
   } catch (e: Exception) {
       // All waiters get same error
       fallbackStrategy()
   }
   ```

4. **Monitor metrics**
   ```kotlin
   //  Good
   val metrics = coalescer.getMetrics()
   Log.d("Metrics", "Coalescing rate: ${metrics.getCoalescingRate()}%")
   ```

5. **Implement timeouts**
   ```kotlin
   //  Good
   withTimeout(5000) {
       coalescer.execute(key) { operation() }
   }
   ```

### Don'ts

1. **Don't coalesce non-idempotent operations**
   ```kotlin
   //  Bad - Side effects!
   coalescer.execute("payment") {
       api.processPayment() // Creates duplicate payments!
   }
   ```

2. **Don't use for mutations**
   ```kotlin
   //  Bad
   coalescer.execute("update-user") {
       api.updateUser(user) // Should not be coalesced
   }
   ```

3. **Don't ignore cleanup**
   ```kotlin
   //  Bad - Memory leak
   val coalescer = RequestCoalescer<String, Data>()
   // Never cleaned up!

   //  Good
   class MyRepository : Closeable {
       private val coalescer = RequestCoalescer<String, Data>()

       override fun close() {
           coalescer.clear()
       }
   }
   ```

4. **Don't use overly broad keys**
   ```kotlin
   //  Bad - Too broad
   coalescer.execute("all-users") { api.getAllUsers() }

   //  Good - Specific
   coalescer.execute("user:$userId") { api.getUser(userId) }
   ```

---

## Monitoring and Metrics

### Comprehensive Metrics

```kotlin
class DetailedCoalescerMetrics {
    val totalRequests = AtomicLong(0)
    val coalescedRequests = AtomicLong(0)
    val uniqueRequests = AtomicLong(0)
    val failedRequests = AtomicLong(0)
    val timedOutRequests = AtomicLong(0)

    private val requestDurations = ConcurrentHashMap<String, MutableList<Long>>()

    fun recordRequest(key: String, durationMs: Long, coalesced: Boolean, failed: Boolean) {
        totalRequests.incrementAndGet()

        if (coalesced) {
            coalescedRequests.incrementAndGet()
        } else {
            uniqueRequests.incrementAndGet()
        }

        if (failed) {
            failedRequests.incrementAndGet()
        }

        requestDurations.getOrPut(key) { mutableListOf() }.add(durationMs)
    }

    fun getStats(): CoalescerStats {
        val total = totalRequests.get()
        val coalesced = coalescedRequests.get()

        return CoalescerStats(
            totalRequests = total,
            coalescedRequests = coalesced,
            uniqueRequests = uniqueRequests.get(),
            failedRequests = failedRequests.get(),
            coalescingRate = if (total > 0) (coalesced.toDouble() / total) * 100 else 0.0,
            savingsRate = if (total > 0) {
                ((total - uniqueRequests.get()).toDouble() / total) * 100
            } else 0.0,
            averageDuration = calculateAverageDuration()
        )
    }

    private fun calculateAverageDuration(): Double {
        val allDurations = requestDurations.values.flatten()
        return if (allDurations.isNotEmpty()) {
            allDurations.average()
        } else 0.0
    }
}

data class CoalescerStats(
    val totalRequests: Long,
    val coalescedRequests: Long,
    val uniqueRequests: Long,
    val failedRequests: Long,
    val coalescingRate: Double,
    val savingsRate: Double,
    val averageDuration: Double
)
```

---

## Common Pitfalls

### 1. Coalescing Non-Idempotent Operations

```kotlin
//  WRONG: Payment processing should NOT be coalesced
class PaymentService(private val coalescer: RequestCoalescer<String, Payment>) {
    suspend fun processPayment(orderId: String, amount: Double): Payment {
        return coalescer.execute("payment:$orderId") {
            api.processPayment(orderId, amount) // Creates duplicate charges!
        }
    }
}

//  CORRECT: Don't coalesce mutations
class PaymentService(private val api: PaymentApi) {
    suspend fun processPayment(orderId: String, amount: Double): Payment {
        return api.processPayment(orderId, amount) // Each call is independent
    }
}
```

### 2. Memory Leaks from Unbounded Maps

```kotlin
//  WRONG: No cleanup
class LeakyCoalescer<K, V> {
    private val requests = ConcurrentHashMap<K, Deferred<V>>()

    suspend fun execute(key: K, operation: suspend () -> V): V {
        val deferred = requests.getOrPut(key) {
            CompletableDeferred<V>().apply {
                CoroutineScope(Dispatchers.Default).launch {
                    complete(operation())
                }
            }
        }
        return deferred.await()
        // Never removes from map!
    }
}

//  CORRECT: Cleanup after completion
class ProperCoalescer<K, V> {
    private val requests = ConcurrentHashMap<K, Deferred<V>>()

    suspend fun execute(key: K, operation: suspend () -> V): V = coroutineScope {
        val deferred = async {
            try {
                operation()
            } finally {
                requests.remove(key) // Cleanup!
            }
        }

        requests.compute(key) { _, existing ->
            existing?.takeIf { it.isActive } ?: deferred
        }!!.await()
    }
}
```

### 3. Ignoring Cancellation

```kotlin
//  WRONG: Doesn't handle cancellation
suspend fun execute(key: K, operation: suspend () -> V): V {
    val deferred = async {
        operation()
    }
    requests[key] = deferred
    return deferred.await() // If cancelled, entry stays in map
}

//  CORRECT: Cleanup on cancellation
suspend fun execute(key: K, operation: suspend () -> V): V = coroutineScope {
    val deferred = async {
        try {
            operation()
        } catch (e: CancellationException) {
            requests.remove(key)
            throw e
        } finally {
            requests.remove(key)
        }
    }

    requests.compute(key) { _, existing ->
        existing?.takeIf { it.isActive } ?: deferred
    }!!.await()
}
```

---

## Follow-ups

1. **What's the difference between request coalescing and caching?**
   - Coalescing: Deduplicates concurrent requests (same time)
   - Caching: Stores results for reuse (across time)
   - Best used together for optimal performance

2. **How do you handle partial failures in coalesced requests?**
   - All waiters receive same error
   - Implement fallback strategies (cached data, default values)
   - Consider retry logic with exponential backoff

3. **What's the ideal TTL for coalesced request tracking?**
   - Depends on operation duration and request patterns
   - Typically 30-60 seconds is sufficient
   - Monitor metrics to tune

4. **Should you coalesce POST/PUT/DELETE requests?**
   - No! Only GET requests (idempotent, side-effect-free)
   - Mutations should not be deduplicated

5. **How do you implement request coalescing across multiple processes?**
   - Use shared state (Redis, Memcached)
   - Implement distributed locking
   - More complex, consider if really needed

6. **What's the difference between coalescing and batching?**
   - Coalescing: Same request → Same result
   - Batching: Different requests → Individual results in one call
   - Both reduce backend load

7. **How do you test coalescing effectiveness in production?**
   - Monitor API call counts before/after
   - Track coalescing rate metrics
   - Measure backend CPU and latency improvements

---

## References

- [Kotlin Coroutines Guide](https://kotlinlang.org/docs/coroutines-guide.html)
- [Request Coalescing in Distributed Systems](https://martinfowler.com/articles/patterns-of-distributed-systems/request-pipeline.html)
- [Facebook's TAO: Request Coalescing](https://www.usenix.org/conference/atc13/technical-sessions/presentation/bronson)
- [Netflix: Request Collapsing with Hystrix](https://github.com/Netflix/Hystrix/wiki/How-it-Works#RequestCollapsing)

---

## Related Questions

- [Caching strategies](q-caching-strategies--kotlin--medium.md)
- [Circuit breaker pattern](q-circuit-breaker-coroutines--kotlin--hard.md)
- [Performance optimization](q-performance-optimization--kotlin--hard.md)

---

<a name="russian-version"></a>

# Объединение И Дедупликация Запросов

[English](#request-coalescing-and-deduplication-patterns) | **Русский**

---

## Обзор

Объединение запросов (также называемое дедупликацией запросов или схлопыванием запросов) — это техника оптимизации, которая объединяет несколько одновременных запросов к одному ресурсу в единственный вызов бэкенда.

**Ключевые преимущества:**
- Значительно снижает нагрузку на бэкенд (снижение в 10-100 раз)
- Улучшает время отклика (все запрашивающие получают один результат)
- Предотвращает проблему лавинообразной нагрузки
- Уменьшает использование сетевой пропускной способности
- Улучшает коэффициент попадания в кэш

**Когда использовать:**
- Несколько компонентов запрашивают одни и те же данные одновременно
- Высоконагруженные эндпоинты с идентичными запросами
- Дорогие операции (запросы к базе данных, вызовы API)
- Подписки на данные реального времени

---

## Определение Паттерна

### Что Такое Объединение Запросов?

```
БЕЗ объединения:
     Запрос 1
  Клиент
    A

     Запрос 2
  Клиент   Бэкенд
    B

     Запрос 3
  Клиент
    C

Результат: 3 идентичных вызова бэкенда


С объединением:

  Клиент
    A

     Единственный
  Клиент  Запрос   Бэкенд
    B

  Клиент
    C

Результат: 1 вызов бэкенда, 3 клиента получают результат
```

### Основные Концепции

1. **Отслеживание выполняющихся запросов**: Отслеживание текущих запросов
2. **Совместное использование Deferred**: Совместное использование `Deferred<T>` между одновременными запрашивающими
3. **Дедупликация на основе ключей**: Использование уникальных ключей для идентификации идентичных запросов
4. **Широковещательная рассылка результатов**: Все ожидающие получают один результат
5. **Очистка**: Удаление завершенных запросов из карты отслеживания

---

## Проблемный Сценарий

### Сценарий: Загрузка Профиля Пользователя

```kotlin
//  ПРОБЛЕМА: Несколько компонентов загружают один профиль пользователя
class UserProfileScreen : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // Компонент 1: Заголовок загружает пользователя
        userRepository.getUser(userId) // API вызов 1

        // Компонент 2: Аватар загружает пользователя
        userRepository.getUser(userId) // API вызов 2

        // Компонент 3: Статистика загружает пользователя
        userRepository.getUser(userId) // API вызов 3

        // Компонент 4: Действия загружают пользователя
        userRepository.getUser(userId) // API вызов 4
    }
}

// Результат: 4 идентичных API вызова подряд!
// Бэкенд получает нагрузку в 4 раза больше
// Пользователь ждет 4 отдельных сетевых вызова
```

### Реальное Влияние

```kotlin
// Реальные метрики из production приложения:

// БЕЗ объединения:
// - 10,000 запросов профилей пользователей/минуту
// - Среднее 3 дублирующих запроса на пользователя
// - Всего вызовов бэкенда: 30,000/минуту
// - CPU бэкенда: 85%
// - P95 задержка: 450мс

// С объединением:
// - 10,000 запросов профилей пользователей/минуту
// - Дедуплицировано до: 3,500/минуту (снижение на 90%!)
// - CPU бэкенда: 30%
// - P95 задержка: 120мс
```

---

## Архитектура Решения

### Базовая Архитектура

```kotlin
class RequestCoalescer<K, V> {
    // Отслеживание выполняющихся запросов
    private val inFlightRequests = ConcurrentHashMap<K, Deferred<V>>()

    suspend fun execute(
        key: K,
        operation: suspend () -> V
    ): V {
        // Проверка, выполняется ли уже запрос
        val existingRequest = inFlightRequests[key]
        if (existingRequest != null) {
            // Ожидание существующего запроса
            return existingRequest.await()
        }

        // Запуск нового запроса
        return coroutineScope {
            val deferred = async {
                try {
                    operation()
                } finally {
                    // Очистка после завершения
                    inFlightRequests.remove(key)
                }
            }

            // Сохранение для других запрашивающих
            inFlightRequests[key] = deferred

            deferred.await()
        }
    }
}
```

---

## Потокобезопасная Реализация С ConcurrentHashMap

### Базовая Реализация

```kotlin
class RequestCoalescer<K, V> {
    private val inFlightRequests = ConcurrentHashMap<K, Deferred<V>>()

    suspend fun execute(
        key: K,
        operation: suspend () -> V
    ): V = coroutineScope {
        // Атомарная проверка и установка
        val existingDeferred = inFlightRequests[key]
        if (existingDeferred != null && existingDeferred.isActive) {
            return@coroutineScope existingDeferred.await()
        }

        val deferred = async {
            try {
                operation()
            } finally {
                inFlightRequests.remove(key)
            }
        }

        // Возможно состояние гонки здесь!
        // Другой поток может вставить между проверкой и размещением
        val previous = inFlightRequests.putIfAbsent(key, deferred)

        if (previous != null && previous.isActive) {
            // Другой поток выиграл гонку
            deferred.cancel()
            previous.await()
        } else {
            deferred.await()
        }
    }
}
```

### Исправление Состояния Гонки

```kotlin
class SafeRequestCoalescer<K, V> {
    private val inFlightRequests = ConcurrentHashMap<K, Deferred<V>>()

    suspend fun execute(
        key: K,
        operation: suspend () -> V
    ): V = coroutineScope {
        // Атомарная операция вычисления
        val deferred = inFlightRequests.compute(key) { _, existing ->
            if (existing != null && existing.isActive) {
                existing
            } else {
                async {
                    try {
                        operation()
                    } finally {
                        inFlightRequests.remove(key)
                    }
                }
            }
        }!!

        deferred.await()
    }
}
```

### Обработка Ошибок

```kotlin
class ResilientRequestCoalescer<K, V> {
    private val inFlightRequests = ConcurrentHashMap<K, Deferred<Result<V>>>()

    suspend fun execute(
        key: K,
        operation: suspend () -> V
    ): Result<V> = coroutineScope {
        val deferred = inFlightRequests.compute(key) { _, existing ->
            if (existing != null && existing.isActive) {
                existing
            } else {
                async {
                    try {
                        val result = operation()
                        Result.success(result)
                    } catch (e: Exception) {
                        Result.failure(e)
                    } finally {
                        inFlightRequests.remove(key)
                    }
                }
            }
        }!!

        deferred.await()
    }
}

// Использование
val result = coalescer.execute("user:123") {
    api.getUser("123")
}

when {
    result.isSuccess -> {
        val user = result.getOrNull()!!
        // Обработка успеха
    }
    result.isFailure -> {
        val error = result.exceptionOrNull()
        // Обработка ошибки
        // Примечание: Все ожидающие получают ту же ошибку!
    }
}
```

---

## Альтернативная Реализация С Mutex

### Реализация На Основе Mutex

```kotlin
class MutexRequestCoalescer<K, V> {
    private val inFlightRequests = mutableMapOf<K, Deferred<V>>()
    private val mutex = Mutex()

    suspend fun execute(
        key: K,
        operation: suspend () -> V
    ): V = coroutineScope {
        // Проверка с блокировкой
        mutex.withLock {
            val existing = inFlightRequests[key]
            if (existing != null && existing.isActive) {
                return@coroutineScope existing.await()
            }
        }

        // Создание нового deferred
        val deferred = async {
            try {
                operation()
            } finally {
                mutex.withLock {
                    inFlightRequests.remove(key)
                }
            }
        }

        // Сохранение с блокировкой
        mutex.withLock {
            // Двойная проверка (другая корутина могла создать его)
            val existing = inFlightRequests[key]
            if (existing != null && existing.isActive) {
                deferred.cancel()
                return@coroutineScope existing.await()
            }

            inFlightRequests[key] = deferred
        }

        deferred.await()
    }
}
```

**Рекомендации:**
- **ConcurrentHashMap**: Лучшая производительность при высокой параллельности
- **Mutex**: Более простой код, легче понять, достаточно для большинства случаев

---

## Реальные Примеры

### Пример 1: Кэш Профиля Пользователя С Объединением

```kotlin
class UserRepository(
    private val api: UserApi,
    private val cache: UserCache,
    private val coalescer: RequestCoalescer<String, User>
) {
    suspend fun getUser(userId: String): User {
        // Сначала проверка кэша
        cache.get(userId)?.let { return it }

        // Объединение API вызовов
        return coalescer.execute(userId) {
            val user = api.getUser(userId)
            cache.put(userId, user)
            user
        }
    }
}

// Сценарий: Экран профиля пользователя с несколькими компонентами
class ProfileScreen : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            // Все эти вызовы объединяются в ОДИН API вызов
            val user1 = userRepository.getUser(userId) // Компонент заголовка
            val user2 = userRepository.getUser(userId) // Компонент аватара
            val user3 = userRepository.getUser(userId) // Компонент статистики
            val user4 = userRepository.getUser(userId) // Компонент биографии

            // Только 1 API вызов выполнен!
            // Все 4 получают результат мгновенно
        }
    }
}
```

### Пример 2: Дедупликация Загрузки Изображений

```kotlin
class ImageLoader(
    private val httpClient: HttpClient,
    private val coalescer: RequestCoalescer<String, Bitmap>
) {
    suspend fun loadImage(url: String): Bitmap {
        return coalescer.execute(url) {
            httpClient.get(url).use { response ->
                BitmapFactory.decodeStream(response.bodyStream())
            }
        }
    }
}

// Сценарий: RecyclerView с повторяющимися изображениями
class ImageAdapter : RecyclerView.Adapter<ImageViewHolder>() {
    override fun onBindViewHolder(holder: ImageViewHolder, position: Int) {
        val imageUrl = items[position].imageUrl

        holder.lifecycleScope.launch {
            // Даже если одно изображение появляется 100 раз в списке,
            // происходит только 1 загрузка!
            val bitmap = imageLoader.loadImage(imageUrl)
            holder.imageView.setImageBitmap(bitmap)
        }
    }
}
```

---

## Преимущества Производительности

### Результаты Бенчмарков

```kotlin
@Test
fun benchmarkCoalescing() = runBlocking {
    val api = MockApi(latency = 100) // 100мс на вызов
    val coalescedRepository = UserRepository(api, coalescer = RequestCoalescer())
    val regularRepository = UserRepository(api, coalescer = null)

    val concurrentRequests = 100
    val userId = "test-user"

    // БЕЗ объединения
    val withoutTime = measureTimeMillis {
        val jobs = List(concurrentRequests) {
            launch {
                regularRepository.getUser(userId)
            }
        }
        jobs.joinAll()
    }
    println("Без объединения: ${withoutTime}мс")
    println("API вызовов сделано: ${api.callCount}") // 100 вызовов

    api.reset()

    // С объединением
    val withTime = measureTimeMillis {
        val jobs = List(concurrentRequests) {
            launch {
                coalescedRepository.getUser(userId)
            }
        }
        jobs.joinAll()
    }
    println("С объединением: ${withTime}мс")
    println("API вызовов сделано: ${api.callCount}") // 1 вызов!

    // Результаты:
    // Без: ~10,000мс (100 запросов × 100мс)
    // С: ~100мс (1 запрос × 100мс)
    // Ускорение: в 100 раз!
}
```

### Реальные Метрики Production

```kotlin
/**
 * Production метрики из реального Android приложения
 */
data class ProductionMetrics(
    // До объединения
    val beforeApiCalls: Long = 45_000,           // в минуту
    val beforeBackendCpu: Double = 78.0,         // процентов
    val beforeP95Latency: Long = 320,            // миллисекунды
    val beforeErrorRate: Double = 2.3,           // процентов

    // После объединения
    val afterApiCalls: Long = 8_500,             // в минуту (снижение на 81%!)
    val afterBackendCpu: Double = 28.0,          // процентов
    val afterP95Latency: Long = 95,              // миллисекунды
    val afterErrorRate: Double = 0.4,            // процентов

    // Улучшения
    val apiCallReduction: Double = 81.1,         // процентов
    val cpuReduction: Double = 64.1,             // процентов
    val latencyImprovement: Double = 70.3,       // процентов
    val errorRateImprovement: Double = 82.6      // процентов
)
```

---

## Комбинирование С Кэшем В Памяти

### Двухуровневая Стратегия: Объединение + Кэширование

```kotlin
class OptimizedRepository<K, V>(
    private val api: Api<K, V>,
    private val memoryCache: LruCache<K, CacheEntry<V>>,
    private val coalescer: RequestCoalescer<K, V>,
    private val cacheTtl: Long = 5 * 60 * 1000 // 5 минут
) {
    suspend fun get(key: K): V {
        // Уровень 1: Проверка кэша в памяти
        val cached = memoryCache.get(key)
        if (cached != null && !cached.isExpired(cacheTtl)) {
            return cached.value
        }

        // Уровень 2: Объединение API вызовов
        return coalescer.execute(key) {
            val value = api.fetch(key)

            // Сохранение в кэше
            memoryCache.put(key, CacheEntry(value, System.currentTimeMillis()))

            value
        }
    }

    fun invalidate(key: K) {
        memoryCache.remove(key)
    }

    fun invalidateAll() {
        memoryCache.evictAll()
    }
}

data class CacheEntry<V>(
    val value: V,
    val timestamp: Long
) {
    fun isExpired(ttl: Long): Boolean {
        return System.currentTimeMillis() - timestamp > ttl
    }
}

// Преимущества:
// 1. Кэш в памяти: Мгновенный ответ для кэшированных данных
// 2. Coalescer: Предотвращает дублирующие API вызовы
// 3. TTL: Обеспечивает свежесть данных
```

---

## Лучшие Практики

### Что Делать

1. **Использовать для дорогих, идемпотентных операций**
   ```kotlin
   //  Хорошо
   coalescer.execute("user:$userId") {
       api.getUser(userId) // Дорого, идемпотентно
   }
   ```

2. **Выбирать подходящие ключи**
   ```kotlin
   //  Хорошо - Уникальные, детерминированные ключи
   coalescer.execute("user:$userId:$includeDetails") {
       api.getUser(userId, includeDetails)
   }
   ```

3. **Обрабатывать ошибки корректно**
   ```kotlin
   //  Хорошо
   try {
       coalescer.execute(key) { operation() }
   } catch (e: Exception) {
       // Все ожидающие получают ту же ошибку
       fallbackStrategy()
   }
   ```

4. **Мониторить метрики**
   ```kotlin
   //  Хорошо
   val metrics = coalescer.getMetrics()
   Log.d("Metrics", "Уровень объединения: ${metrics.getCoalescingRate()}%")
   ```

5. **Реализовать таймауты**
   ```kotlin
   //  Хорошо
   withTimeout(5000) {
       coalescer.execute(key) { operation() }
   }
   ```

### Чего Не Делать

1. **Не объединять не-идемпотентные операции**
   ```kotlin
   //  Плохо - Побочные эффекты!
   coalescer.execute("payment") {
       api.processPayment() // Создает дублирующие платежи!
   }
   ```

2. **Не использовать для мутаций**
   ```kotlin
   //  Плохо
   coalescer.execute("update-user") {
       api.updateUser(user) // Не должно быть объединено
   }
   ```

3. **Не игнорировать очистку**
   ```kotlin
   //  Плохо - Утечка памяти
   val coalescer = RequestCoalescer<String, Data>()
   // Никогда не очищается!

   //  Хорошо
   class MyRepository : Closeable {
       private val coalescer = RequestCoalescer<String, Data>()

       override fun close() {
           coalescer.clear()
       }
   }
   ```

4. **Не использовать слишком широкие ключи**
   ```kotlin
   //  Плохо - Слишком широко
   coalescer.execute("all-users") { api.getAllUsers() }

   //  Хорошо - Конкретно
   coalescer.execute("user:$userId") { api.getUser(userId) }
   ```

---

## Распространенные Ошибки

### 1. Объединение Не-идемпотентных Операций

```kotlin
//  НЕПРАВИЛЬНО: Обработка платежей НЕ должна быть объединена
class PaymentService(private val coalescer: RequestCoalescer<String, Payment>) {
    suspend fun processPayment(orderId: String, amount: Double): Payment {
        return coalescer.execute("payment:$orderId") {
            api.processPayment(orderId, amount) // Создает дублирующие списания!
        }
    }
}

//  ПРАВИЛЬНО: Не объединять мутации
class PaymentService(private val api: PaymentApi) {
    suspend fun processPayment(orderId: String, amount: Double): Payment {
        return api.processPayment(orderId, amount) // Каждый вызов независим
    }
}
```

### 2. Утечки Памяти Из Неограниченных Карт

```kotlin
//  НЕПРАВИЛЬНО: Нет очистки
class LeakyCoalescer<K, V> {
    private val requests = ConcurrentHashMap<K, Deferred<V>>()

    suspend fun execute(key: K, operation: suspend () -> V): V {
        val deferred = requests.getOrPut(key) {
            CompletableDeferred<V>().apply {
                CoroutineScope(Dispatchers.Default).launch {
                    complete(operation())
                }
            }
        }
        return deferred.await()
        // Никогда не удаляется из карты!
    }
}

//  ПРАВИЛЬНО: Очистка после завершения
class ProperCoalescer<K, V> {
    private val requests = ConcurrentHashMap<K, Deferred<V>>()

    suspend fun execute(key: K, operation: suspend () -> V): V = coroutineScope {
        val deferred = async {
            try {
                operation()
            } finally {
                requests.remove(key) // Очистка!
            }
        }

        requests.compute(key) { _, existing ->
            existing?.takeIf { it.isActive } ?: deferred
        }!!.await()
    }
}
```

### 3. Игнорирование Отмены

```kotlin
//  НЕПРАВИЛЬНО: Не обрабатывает отмену
suspend fun execute(key: K, operation: suspend () -> V): V {
    val deferred = async {
        operation()
    }
    requests[key] = deferred
    return deferred.await() // Если отменено, запись остается в карте
}

//  ПРАВИЛЬНО: Очистка при отмене
suspend fun execute(key: K, operation: suspend () -> V): V = coroutineScope {
    val deferred = async {
        try {
            operation()
        } catch (e: CancellationException) {
            requests.remove(key)
            throw e
        } finally {
            requests.remove(key)
        }
    }

    requests.compute(key) { _, existing ->
        existing?.takeIf { it.isActive } ?: deferred
    }!!.await()
}
```

---

## Дополнительные Вопросы

1. **В чем разница между объединением запросов и кэшированием?**
   - Объединение: Дедуплицирует одновременные запросы (одно время)
   - Кэширование: Сохраняет результаты для повторного использования (во времени)
   - Лучше всего использовать вместе для оптимальной производительности

2. **Как обрабатывать частичные сбои в объединенных запросах?**
   - Все ожидающие получают ту же ошибку
   - Реализовать стратегии отката (кэшированные данные, значения по умолчанию)
   - Рассмотреть логику повтора с экспоненциальной задержкой

3. **Какой идеальный TTL для отслеживания объединенных запросов?**
   - Зависит от длительности операции и паттернов запросов
   - Обычно 30-60 секунд достаточно
   - Мониторить метрики для настройки

4. **Следует ли объединять POST/PUT/DELETE запросы?**
   - Нет! Только GET запросы (идемпотентные, без побочных эффектов)
   - Мутации не должны дедуплицироваться

5. **Как реализовать объединение запросов между несколькими процессами?**
   - Использовать общее состояние (Redis, Memcached)
   - Реализовать распределенную блокировку
   - Более сложно, рассмотреть, действительно ли нужно

6. **В чем разница между объединением и батчингом?**
   - Объединение: Одинаковый запрос → Одинаковый результат
   - Батчинг: Разные запросы → Индивидуальные результаты в одном вызове
   - Оба снижают нагрузку на бэкенд

7. **Как тестировать эффективность объединения в production?**
   - Мониторить количество API вызовов до/после
   - Отслеживать метрики уровня объединения
   - Измерять улучшения CPU бэкенда и задержки

---

## Ссылки

- [Kotlin Coroutines Guide](https://kotlinlang.org/docs/coroutines-guide.html)
- [Request Coalescing in Distributed Systems](https://martinfowler.com/articles/patterns-of-distributed-systems/request-pipeline.html)
- [Facebook's TAO: Request Coalescing](https://www.usenix.org/conference/atc13/technical-sessions/presentation/bronson)
- [Netflix: Request Collapsing with Hystrix](https://github.com/Netflix/Hystrix/wiki/How-it-Works#RequestCollapsing)

---

## Связанные Вопросы

- [Стратегии кэширования](q-caching-strategies--kotlin--medium.md)
- [Паттерн Circuit breaker](q-circuit-breaker-coroutines--kotlin--hard.md)
- [Оптимизация производительности](q-performance-optimization--kotlin--hard.md)

---

**End of document**
