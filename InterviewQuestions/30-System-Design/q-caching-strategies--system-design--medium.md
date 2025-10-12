---
id: 20251012-300003
title: "Caching Strategies and Patterns / Стратегии и паттерны кеширования"
slug: caching-strategies-system-design-medium
topic: system-design
subtopics:
  - caching
  - performance
  - redis
  - memcached
  - cdn
status: draft
difficulty: medium
moc: moc-system-design
date_created: 2025-10-12
date_updated: 2025-10-12
related_questions:
  - q-cache-invalidation--system-design--hard
  - q-cdn-architecture--system-design--medium
  - q-database-sharding--system-design--hard
tags:
  - system-design
  - caching
  - performance
  - scalability
---

# Caching Strategies and Patterns

## English Version

### Problem Statement

Caching is one of the most effective ways to improve system performance. However, implementing caching incorrectly can lead to stale data, cache misses, and even worse performance. Understanding different caching strategies is essential for building high-performance systems.

**The Question:** What are the main caching strategies? When should you use each strategy, and what are common caching patterns?

### Detailed Answer

#### Why Caching?

**Performance gains:**
- Database query: ~10-100ms
- Cache (Redis): ~1ms
- **10-100x faster!**

**Benefits:**
- ✅ Reduced latency
- ✅ Lower database load
- ✅ Better scalability
- ✅ Cost savings

```
Without Cache:          With Cache:
Client → DB (100ms)     Client → Cache (1ms) ✓
Client → DB (100ms)     Client → Cache (1ms) ✓
Client → DB (100ms)     Client → DB (100ms) → Cache ✓
                        Client → Cache (1ms) ✓
```

---

### Caching Strategies

#### 1. Cache-Aside (Lazy Loading)

**How it works:**
1. Application checks cache first
2. If **cache miss**, load from database
3. Write to cache for next time
4. Return data

```
┌─────────┐
│  App    │
└────┬────┘
     │ 1. Check cache
     ▼
┌─────────┐     Cache Miss
│  Cache  │ ────────────────┐
└─────────┘                 │
                            │ 2. Load from DB
                   ┌────────▼────────┐
                   │    Database     │
                   └────────┬────────┘
                            │ 3. Write to cache
┌─────────┐                │
│  Cache  │ ◄──────────────┘
└─────────┘
     │ 4. Return data
     ▼
┌─────────┐
│  App    │
└─────────┘
```

**Implementation:**
```kotlin
class UserService(
    private val cache: RedisCache,
    private val database: UserRepository
) {
    suspend fun getUser(userId: Long): User {
        val cacheKey = "user:$userId"

        // 1. Try cache first
        cache.get<User>(cacheKey)?.let { return it }

        // 2. Cache miss - load from database
        val user = database.findById(userId)
            ?: throw UserNotFoundException(userId)

        // 3. Write to cache
        cache.set(cacheKey, user, ttl = 1.hours)

        // 4. Return
        return user
    }
}
```

**✅ Pros:**
- Only cache what's actually needed
- Cache failure doesn't break system
- Simple to implement

**❌ Cons:**
- Cache miss penalty (3 network calls: check cache, DB, write cache)
- Potential for stale data
- Cache warming needed

**Best for:** Read-heavy workloads, data that changes infrequently

---

#### 2. Read-Through Cache

**How it works:**
- Cache sits between app and database
- Cache automatically loads from DB on miss
- Application only talks to cache

```
┌─────────┐
│  App    │ ────────► Only talks to cache
└─────────┘
                ┌───────────────┐
                │  Cache Layer  │
                │  (Redis)      │
                └───────┬───────┘
                        │ Automatically fetches on miss
                ┌───────▼───────┐
                │   Database    │
                └───────────────┘
```

**Implementation:**
```kotlin
// Cache library handles DB fetch automatically
class ReadThroughCache(
    private val redis: Redis,
    private val database: Database
) {
    suspend fun <T> get(key: String, loader: suspend () -> T): T {
        // Check cache
        redis.get<T>(key)?.let { return it }

        // Cache miss - load from DB (cache does this automatically)
        val value = loader()

        // Store in cache
        redis.set(key, value, ttl = 1.hours)

        return value
    }
}

// Usage
val user = cache.get("user:$userId") {
    database.findUser(userId) // Executed only on cache miss
}
```

**✅ Pros:**
- Cleaner application code
- Cache logic centralized
- Consistent loading pattern

**❌ Cons:**
- Cache becomes critical dependency
- More complex cache layer

**Best for:** When you want cache to be transparent to application

---

#### 3. Write-Through Cache

**How it works:**
- Write to cache AND database simultaneously
- Data always in sync
- Slower writes, but cache always fresh

```
Write Operation:
┌─────────┐
│  App    │ Write user
└────┬────┘
     │
     ▼
┌────────────┐
│   Cache    │ 1. Write to cache
└────┬───────┘
     │ 2. Write to DB
     ▼
┌────────────┐
│  Database  │
└────────────┘

Read Operation:
┌─────────┐
│  App    │ Read user
└────┬────┘
     │
     ▼
┌────────────┐
│   Cache    │ Always has fresh data ✓
└────────────┘
```

**Implementation:**
```kotlin
class UserService(
    private val cache: RedisCache,
    private val database: UserRepository
) {
    suspend fun updateUser(userId: Long, updates: UserUpdates): User {
        // 1. Update database
        val updatedUser = database.update(userId, updates)

        // 2. Update cache immediately
        cache.set("user:$userId", updatedUser, ttl = 1.hours)

        return updatedUser
    }

    suspend fun createUser(user: User): User {
        // 1. Write to database
        val saved = database.save(user)

        // 2. Write to cache
        cache.set("user:${saved.id}", saved, ttl = 1.hours)

        return saved
    }
}
```

**✅ Pros:**
- Cache always has fresh data
- No stale reads
- Good for read-heavy after writes

**❌ Cons:**
- Slower writes (2 operations)
- Writes to cache items that may never be read
- Cache failure affects writes

**Best for:** Applications that need strong consistency

---

#### 4. Write-Behind (Write-Back) Cache

**How it works:**
- Write to cache immediately
- Asynchronously write to database later
- Fastest writes, but risk of data loss

```
Write Operation:
┌─────────┐
│  App    │ Write user (fast!)
└────┬────┘
     │
     ▼
┌────────────┐
│   Cache    │ 1. Write to cache (immediate)
└────┬───────┘
     │ 2. Async queue
     ▼
┌────────────┐
│   Queue    │
└────┬───────┘
     │ 3. Background worker writes to DB
     ▼
┌────────────┐
│  Database  │
└────────────┘
```

**Implementation:**
```kotlin
class WriteBackCache(
    private val cache: RedisCache,
    private val database: UserRepository,
    private val writeQueue: Queue<WriteOperation>
) {
    suspend fun updateUser(userId: Long, updates: UserUpdates): User {
        // 1. Update cache immediately (fast)
        val user = applyUpdates(userId, updates)
        cache.set("user:$userId", user, ttl = 1.hours)

        // 2. Queue database write for later
        writeQueue.enqueue(
            WriteOperation(
                type = "UPDATE_USER",
                userId = userId,
                data = updates
            )
        )

        // 3. Return immediately
        return user
    }

    // Background worker
    @Scheduled(fixedDelay = 100)
    fun processWrites() {
        val batch = writeQueue.dequeueBatch(maxSize = 100)
        batch.forEach { operation ->
            try {
                database.execute(operation)
            } catch (e: Exception) {
                // Retry or dead-letter queue
                handleFailure(operation, e)
            }
        }
    }
}
```

**✅ Pros:**
- Extremely fast writes
- Can batch database writes
- Reduces database load

**❌ Cons:**
- Data loss risk if cache fails before DB write
- Complex implementation
- Eventual consistency

**Best for:** High write throughput, acceptable data loss risk (e.g., analytics)

---

### Cache Eviction Policies

When cache is full, what to remove?

#### LRU (Least Recently Used)
Most popular choice. Removes oldest accessed item.
```
Cache: [A:10s, B:5s, C:1s] (C accessed most recently)
Cache full → Evict A (accessed 10 seconds ago)
```

#### LFU (Least Frequently Used)
Removes least frequently accessed item.
```
Cache: [A:10hits, B:5hits, C:50hits]
Cache full → Evict B (only 5 hits)
```

#### FIFO (First In First Out)
Removes oldest item regardless of access.

#### TTL (Time To Live)
Expires items after fixed time.
```kotlin
cache.set("user:123", user, ttl = 1.hours)
// Automatically removed after 1 hour
```

**Redis Configuration:**
```redis
# Redis eviction policies
maxmemory 2gb
maxmemory-policy allkeys-lru  # or allkeys-lfu, volatile-lru, volatile-ttl
```

---

### Caching Patterns

#### 1. Cache-Aside Pattern (Already covered)

#### 2. Refresh-Ahead

**Proactively refresh cache before expiration:**
```kotlin
class RefreshAheadCache(
    private val cache: RedisCache,
    private val database: UserRepository
) {
    suspend fun getUser(userId: Long): User {
        val cacheKey = "user:$userId"
        val cachedUser = cache.get<CachedUser>(cacheKey)

        return when {
            cachedUser == null -> {
                // Cache miss - load from DB
                val user = database.findById(userId)
                cache.set(cacheKey, CachedUser(user, System.currentTimeMillis()))
                user
            }
            cachedUser.isNearExpiration() -> {
                // Proactively refresh in background
                launch { refreshUser(userId) }
                cachedUser.data // Return stale data immediately
            }
            else -> cachedUser.data
        }
    }

    private suspend fun refreshUser(userId: Long) {
        val user = database.findById(userId)
        cache.set("user:$userId", CachedUser(user, System.currentTimeMillis()))
    }

    data class CachedUser(
        val data: User,
        val cachedAt: Long,
        val ttl: Long = 3600_000 // 1 hour
    ) {
        fun isNearExpiration(): Boolean {
            val age = System.currentTimeMillis() - cachedAt
            return age > (ttl * 0.8) // Refresh at 80% of TTL
        }
    }
}
```

#### 3. Cache Warming

**Preload cache with expected data:**
```kotlin
@Component
class CacheWarmer(
    private val cache: RedisCache,
    private val userRepository: UserRepository,
    private val productRepository: ProductRepository
) {
    @EventListener(ApplicationReadyEvent::class)
    suspend fun warmCache() {
        log.info("Warming cache...")

        // Load popular users
        val popularUsers = userRepository.findMostActive(limit = 1000)
        popularUsers.forEach { user ->
            cache.set("user:${user.id}", user, ttl = 1.hours)
        }

        // Load featured products
        val featuredProducts = productRepository.findFeatured()
        featuredProducts.forEach { product ->
            cache.set("product:${product.id}", product, ttl = 30.minutes)
        }

        log.info("Cache warming complete")
    }
}
```

#### 4. Multi-Level Caching

```
┌──────────────────────────────────────┐
│  Client Browser (L1 Cache)           │
│  - HTML, CSS, JS cached locally      │
└──────────┬───────────────────────────┘
           │
┌──────────▼───────────────────────────┐
│  CDN (L2 Cache)                      │
│  - Static assets, images             │
└──────────┬───────────────────────────┘
           │
┌──────────▼───────────────────────────┐
│  Application Server L3 (In-Memory)   │
│  - Hot data in local cache           │
└──────────┬───────────────────────────┘
           │
┌──────────▼───────────────────────────┐
│  Redis (L4 Distributed Cache)        │
│  - Shared across all servers         │
└──────────┬───────────────────────────┘
           │
┌──────────▼───────────────────────────┐
│  Database                            │
└──────────────────────────────────────┘
```

**Implementation:**
```kotlin
class MultiLevelCache(
    private val localCache: CaffeineCache, // L1: In-memory
    private val redisCache: RedisCache,    // L2: Distributed
    private val database: Database          // L3: Source of truth
) {
    suspend fun get(key: String): User? {
        // L1: Check local cache (fastest, ~1μs)
        localCache.get(key)?.let { return it }

        // L2: Check Redis (fast, ~1ms)
        redisCache.get<User>(key)?.let { user ->
            localCache.put(key, user) // Populate L1
            return user
        }

        // L3: Load from database (slow, ~10-100ms)
        val user = database.findUser(key) ?: return null

        // Populate both caches
        redisCache.set(key, user, ttl = 1.hours)
        localCache.put(key, user)

        return user
    }
}
```

---

### Cache Invalidation Strategies

**"There are only two hard things in Computer Science: cache invalidation and naming things" - Phil Karlton**

#### 1. TTL-Based
```kotlin
cache.set("user:123", user, ttl = 5.minutes)
// Automatically expires
```

#### 2. Event-Based Invalidation
```kotlin
@EventListener
fun onUserUpdated(event: UserUpdatedEvent) {
    cache.delete("user:${event.userId}")
    cache.delete("user:${event.userId}:profile")
    cache.delete("user:${event.userId}:settings")
}
```

#### 3. Tag-Based Invalidation
```kotlin
// Set cache with tags
cache.setWithTags(
    key = "product:123",
    value = product,
    tags = listOf("products", "category:electronics", "brand:apple")
)

// Invalidate all products with tag
cache.invalidateByTag("category:electronics")
```

---

### Real-World Example

**E-commerce Product Cache:**
```kotlin
@Service
class ProductService(
    private val cache: RedisCache,
    private val database: ProductRepository,
    private val searchIndex: ElasticsearchClient
) {
    // Cache-aside pattern
    suspend fun getProduct(productId: Long): Product? {
        return cache.get("product:$productId") ?: run {
            val product = database.findById(productId) ?: return null
            cache.set("product:$productId", product, ttl = 1.hours)
            product
        }
    }

    // Write-through pattern
    suspend fun updateProduct(productId: Long, updates: ProductUpdates): Product {
        // 1. Update database
        val product = database.update(productId, updates)

        // 2. Update cache
        cache.set("product:$productId", product, ttl = 1.hours)

        // 3. Update search index (async)
        launch { searchIndex.index(product) }

        // 4. Invalidate related caches
        cache.delete("category:${product.categoryId}:products")
        cache.delete("brand:${product.brandId}:products")

        return product
    }

    // Cache popular products
    @Scheduled(cron = "0 */15 * * * *") // Every 15 minutes
    suspend fun cachePopularProducts() {
        val popular = database.findTopProducts(limit = 100)
        popular.forEach { product ->
            cache.set("product:${product.id}", product, ttl = 1.hours)
        }
    }
}
```

### Key Takeaways

1. **Cache-Aside** - Most common, lazy loading
2. **Read-Through** - Cache handles DB fetching
3. **Write-Through** - Write to cache + DB synchronously (strong consistency)
4. **Write-Behind** - Write to cache first, DB async (high performance)
5. **TTL** is essential to prevent stale data
6. **LRU** is the most common eviction policy
7. **Multi-level caching** maximizes performance
8. **Cache invalidation** is hard - use TTL + events
9. **Cache warming** reduces initial cache misses
10. Always have a **fallback** if cache fails

---

## Russian Version

### Постановка задачи

Кеширование - один из самых эффективных способов улучшить производительность системы. Однако, неправильная реализация кеширования может привести к устаревшим данным, промахам кеша и даже худшей производительности.

**Вопрос:** Каковы основные стратегии кеширования? Когда следует использовать каждую стратегию, и каковы распространённые паттерны кеширования?

### Детальный ответ

#### Зачем кеширование?

**Выигрыш в производительности:**
- Запрос к БД: ~10-100ms
- Кеш (Redis): ~1ms
- **В 10-100 раз быстрее!**

### Стратегии кеширования

#### 1. Cache-Aside (Ленивая загрузка)

**Как работает:**
1. Приложение сначала проверяет кеш
2. Если **промах кеша**, загружает из БД
3. Записывает в кеш для следующего раза
4. Возвращает данные

**✅ Плюсы:**
- Кешируется только то, что действительно нужно
- Сбой кеша не ломает систему
- Просто реализовать

**❌ Минусы:**
- Штраф за промах кеша (3 сетевых вызова)
- Возможны устаревшие данные
- Нужен прогрев кеша

**Подходит для:** Workloads с частым чтением, редко меняющиеся данные

#### 2. Write-Through (Сквозная запись)

**Как работает:**
- Запись в кеш И БД одновременно
- Данные всегда синхронизированы
- Медленнее записи, но кеш всегда свежий

**✅ Плюсы:**
- В кеше всегда свежие данные
- Нет устаревших чтений
- Хорошо для частого чтения после записи

**❌ Минусы:**
- Медленнее запись (2 операции)
- Записи в кеш элементов, которые могут никогда не прочитаться

**Подходит для:** Приложений, требующих строгой консистентности

#### 3. Write-Behind (Отложенная запись)

**Как работает:**
- Запись в кеш немедленно
- Асинхронная запись в БД позже
- Самая быстрая запись, но риск потери данных

**✅ Плюсы:**
- Чрезвычайно быстрые записи
- Можно батчить записи в БД
- Снижает нагрузку на БД

**❌ Минусы:**
- Риск потери данных при сбое кеша
- Сложная реализация
- Eventual consistency

**Подходит для:** Высокая пропускная способность записи, допустим риск потери данных

### Ключевые выводы

1. **Cache-Aside** - Наиболее распространённый, ленивая загрузка
2. **Write-Through** - Запись в кеш + БД синхронно (строгая консистентность)
3. **Write-Behind** - Запись в кеш сначала, БД асинхронно (высокая производительность)
4. **TTL** необходим для предотвращения устаревших данных
5. **LRU** - наиболее распространённая политика вытеснения
6. **Многоуровневое кеширование** максимизирует производительность
7. **Инвалидация кеша** сложна - используйте TTL + события
8. Всегда имейте **fallback** если кеш падает

## Follow-ups

1. What is cache stampede and how do you prevent it?
2. How do you implement distributed cache invalidation?
3. Explain the difference between Redis and Memcached
4. What is cache penetration and how do you handle it?
5. How do you monitor cache hit rates and effectiveness?
6. What is the Thundering Herd problem?
7. How do you handle cache consistency in microservices?
8. Explain CDN caching and edge caching strategies
9. What are the security considerations for caching sensitive data?
10. How do you implement cache sharding?
