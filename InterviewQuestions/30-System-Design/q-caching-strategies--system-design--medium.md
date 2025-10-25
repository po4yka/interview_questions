---
id: 20251012-300003
title: "Caching Strategies and Patterns / Стратегии и паттерны кеширования"
aliases: ["Caching Strategies", "Стратегии кеширования"]
topic: system-design
subtopics: [caching, performance, redis, memcached]
question_kind: system-design
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-system-design
related: [c-caching-strategies, q-load-balancing-strategies--system-design--medium, q-horizontal-vertical-scaling--system-design--medium]
created: 2025-10-12
updated: 2025-01-25
tags: [system-design, caching, performance, scalability, difficulty/medium]
sources: [https://en.wikipedia.org/wiki/Cache_(computing)]
---

# Вопрос (RU)
> Каковы основные стратегии кеширования? Когда следует использовать каждую стратегию, и каковы распространённые паттерны кеширования?

# Question (EN)
> What are the main caching strategies? When should you use each strategy, and what are common caching patterns?

---

## Ответ (RU)

**Теория стратегий кеширования:**
Кеширование - эффективный способ улучшить производительность системы. Различные стратегии имеют разные характеристики консистентности, производительности и сложности реализации.

**Основные стратегии:**

**1. Cache-Aside (Ленивая загрузка):**
```kotlin
// Приложение управляет кешем напрямую
class UserService(
    private val cache: RedisCache,
    private val database: UserRepository
) {
    suspend fun getUser(userId: Long): User {
        val cacheKey = "user:$userId"

        // 1. Проверяем кеш
        cache.get<User>(cacheKey)?.let { return it }

        // 2. Промах кеша - загружаем из БД
        val user = database.findById(userId) ?: throw UserNotFoundException(userId)

        // 3. Записываем в кеш
        cache.set(cacheKey, user, ttl = 1.hours)

        return user
    }
}
```

**2. Write-Through (Сквозная запись):**
```kotlin
// Запись в кеш и БД одновременно
class UserService(
    private val cache: RedisCache,
    private val database: UserRepository
) {
    suspend fun updateUser(userId: Long, updates: UserUpdates): User {
        // 1. Обновляем БД
        val updatedUser = database.update(userId, updates)

        // 2. Обновляем кеш немедленно
        cache.set("user:$userId", updatedUser, ttl = 1.hours)

        return updatedUser
    }
}
```

**3. Write-Behind (Отложенная запись):**
```kotlin
// Запись в кеш немедленно, в БД асинхронно
class WriteBackCache(
    private val cache: RedisCache,
    private val database: UserRepository,
    private val writeQueue: Queue<WriteOperation>
) {
    suspend fun updateUser(userId: Long, updates: UserUpdates): User {
        // 1. Обновляем кеш немедленно (быстро)
        val user = applyUpdates(userId, updates)
        cache.set("user:$userId", user, ttl = 1.hours)

        // 2. Ставим в очередь для записи в БД
        writeQueue.enqueue(WriteOperation("UPDATE_USER", userId, updates))

        return user
    }
}
```

**Политики вытеснения:**
```kotlin
// LRU (Least Recently Used) - наиболее популярная
// LFU (Least Frequently Used) - по частоте использования
// TTL (Time To Live) - по времени жизни
cache.set("user:123", user, ttl = 1.hours)
```

**Многоуровневое кеширование:**
```kotlin
// L1: Локальный кеш (самый быстрый)
// L2: Redis (распределённый)
// L3: База данных (источник истины)
class MultiLevelCache(
    private val localCache: CaffeineCache,
    private val redisCache: RedisCache,
    private val database: Database
) {
    suspend fun get(key: String): User? {
        // L1: Проверяем локальный кеш
        localCache.get(key)?.let { return it }

        // L2: Проверяем Redis
        redisCache.get<User>(key)?.let { user ->
            localCache.put(key, user) // Заполняем L1
            return user
        }

        // L3: Загружаем из БД
        val user = database.findUser(key) ?: return null

        // Заполняем оба кеша
        redisCache.set(key, user, ttl = 1.hours)
        localCache.put(key, user)

        return user
    }
}
```

**Инвалидация кеша:**
```kotlin
// TTL-based инвалидация
cache.set("user:123", user, ttl = 5.minutes)

// Event-based инвалидация
@EventListener
fun onUserUpdated(event: UserUpdatedEvent) {
    cache.delete("user:${event.userId}")
}

// Tag-based инвалидация
cache.setWithTags("product:123", product, tags = listOf("products", "electronics"))
cache.invalidateByTag("electronics")
```

## Answer (EN)

**Caching Strategies Theory:**
Caching is an effective way to improve system performance. Different strategies have different consistency, performance, and implementation complexity characteristics.

**Main Strategies:**

**1. Cache-Aside (Lazy Loading):**
```kotlin
// Application manages cache directly
class UserService(
    private val cache: RedisCache,
    private val database: UserRepository
) {
    suspend fun getUser(userId: Long): User {
        val cacheKey = "user:$userId"

        // 1. Check cache first
        cache.get<User>(cacheKey)?.let { return it }

        // 2. Cache miss - load from DB
        val user = database.findById(userId) ?: throw UserNotFoundException(userId)

        // 3. Write to cache
        cache.set(cacheKey, user, ttl = 1.hours)

        return user
    }
}
```

**2. Write-Through (Synchronous Write):**
```kotlin
// Write to cache and DB simultaneously
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
}
```

**3. Write-Behind (Asynchronous Write):**
```kotlin
// Write to cache immediately, DB asynchronously
class WriteBackCache(
    private val cache: RedisCache,
    private val database: UserRepository,
    private val writeQueue: Queue<WriteOperation>
) {
    suspend fun updateUser(userId: Long, updates: UserUpdates): User {
        // 1. Update cache immediately (fast)
        val user = applyUpdates(userId, updates)
        cache.set("user:$userId", user, ttl = 1.hours)

        // 2. Queue for DB write
        writeQueue.enqueue(WriteOperation("UPDATE_USER", userId, updates))

        return user
    }
}
```

**Eviction Policies:**
```kotlin
// LRU (Least Recently Used) - most popular
// LFU (Least Frequently Used) - by frequency
// TTL (Time To Live) - by expiration time
cache.set("user:123", user, ttl = 1.hours)
```

**Multi-Level Caching:**
```kotlin
// L1: Local cache (fastest)
// L2: Redis (distributed)
// L3: Database (source of truth)
class MultiLevelCache(
    private val localCache: CaffeineCache,
    private val redisCache: RedisCache,
    private val database: Database
) {
    suspend fun get(key: String): User? {
        // L1: Check local cache
        localCache.get(key)?.let { return it }

        // L2: Check Redis
        redisCache.get<User>(key)?.let { user ->
            localCache.put(key, user) // Populate L1
            return user
        }

        // L3: Load from DB
        val user = database.findUser(key) ?: return null

        // Populate both caches
        redisCache.set(key, user, ttl = 1.hours)
        localCache.put(key, user)

        return user
    }
}
```

**Cache Invalidation:**
```kotlin
// TTL-based invalidation
cache.set("user:123", user, ttl = 5.minutes)

// Event-based invalidation
@EventListener
fun onUserUpdated(event: UserUpdatedEvent) {
    cache.delete("user:${event.userId}")
}

// Tag-based invalidation
cache.setWithTags("product:123", product, tags = listOf("products", "electronics"))
cache.invalidateByTag("electronics")
```

---

## Follow-ups

- What is cache stampede and how do you prevent it?
- How do you implement distributed cache invalidation?
- Explain the difference between Redis and Memcached

## Related Questions

### Prerequisites (Easier)
- [[q-sql-nosql-databases--system-design--medium]] - Database fundamentals
- [[q-load-balancing-strategies--system-design--medium]] - Load balancing

### Related (Same Level)
- [[q-horizontal-vertical-scaling--system-design--medium]] - Scaling strategies
- [[q-design-url-shortener--system-design--medium]] - System design patterns

### Advanced (Harder)
- [[q-microservices-vs-monolith--system-design--hard]] - Architecture patterns
- [[q-database-sharding-partitioning--system-design--hard]] - Database scaling
