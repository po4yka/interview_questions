---
id: sysdes-005
title: "Caching Strategies and Patterns / 2240"
aliases: ["2240", "Caching Strategies"]
topic: system-design
subtopics: [caching, memcached, redis]
question_kind: system-design
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-system-design
related: [c-architecture-patterns, q-horizontal-vertical-scaling--system-design--medium, q-load-balancing-strategies--system-design--medium]
created: 2025-10-12
updated: 2025-11-11
tags: [caching, difficulty/medium, performance, scalability, system-design]
sources: ["https://en.wikipedia.org/wiki/Cache_(computing)"]

---
# Вопрос (RU)
> Каковы основные стратегии кеширования? Когда следует использовать каждую стратегию, и каковы распространённые паттерны кеширования?

# Question (EN)
> What are the main caching strategies? When should you use each strategy, and what are common caching patterns?

---

## Ответ (RU)

**Теория стратегий кеширования:**
Кеширование - эффективный способ улучшить производительность системы. Различные стратегии имеют разные характеристики консистентности, производительности и сложности реализации.

См. также: кеш-стратегии и паттерны кеширования (см. [[c-architecture-patterns]]).

### Требования (System Design контекст)
- Функциональные:
  - Снизить латентность чтения горячих данных.
  - Уменьшить нагрузку на базу данных и другие бэкенд-сервисы.
  - Обеспечить управляемые механизмы инвалидации кеша.
- Нефункциональные:
  - Высокая доступность и предсказуемая производительность.
  - Масштабируемость при росте трафика.
  - Контролируемая согласованность данных между кешом и источником истины.

### Архитектура (Высокоуровневый взгляд)
- Клиент → API/сервер приложений.
- Кеш-слой (например, Redis/Memcached) перед базой данных.
- Возможное многоуровневое кеширование: локальный кеш (L1) + распределённый кеш (L2) + БД.
- Механизмы инвалидации и/или событийная шина для согласованности.

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
Когда использовать: подходит, когда доминируют чтения, допустимы редкие промахи кеша, а кеш можно рассматривать как best-effort слой, который может независимо очищаться или вытесняться без нарушения целостности данных в БД.

**2. Write-Through (Сквозная запись через кеш):**
```kotlin
// Концептуальный пример: запись проходит через кеш и считается успешной,
// только когда обновлены и кеш, и БД
class WriteThroughUserService(
    private val cache: RedisCache,
    private val database: UserRepository
) {
    suspend fun updateUser(userId: Long, updates: UserUpdates): User {
        val updatedUser = database.update(userId, updates)
        cache.set("user:$userId", updatedUser, ttl = 1.hours)
        return updatedUser
    }
}
```
Когда использовать: когда нужна сильная согласованность между кешем и БД при записях, и вы можете позволить себе дополнительную латентность записи.

**3. Write-Behind / Write-Back (Отложенная асинхронная запись):**
```kotlin
// Сначала записываем в кеш, затем асинхронно обновляем БД
class WriteBackCache(
    private val cache: RedisCache,
    private val database: UserRepository,
    private val writeQueue: Queue<WriteOperation>
) {
    suspend fun updateUser(userId: Long, updates: UserUpdates): User {
        // 1. Читаем актуальное состояние из кеша или БД
        val current = cache.get<User>("user:$userId") ?: database.findById(userId)
            ?: throw UserNotFoundException(userId)
        val updated = current.applyUpdates(updates)

        // 2. Немедленно обновляем кеш (быстро для клиента)
        cache.set("user:$userId", updated, ttl = 1.hours)

        // 3. Ставим операцию в очередь для асинхронной записи в БД
        writeQueue.enqueue(WriteOperation("UPDATE_USER", userId, updates))

        return updated
    }
}
```
Когда использовать: когда критична минимальная латентность записи и допустима краткосрочная несогласованность между кешем и БД; требует надёжной очереди и аккуратной обработки ошибок.

**Политики вытеснения / истечения:**
```kotlin
// LRU (Least Recently Used) - наиболее популярная политика вытеснения
// LFU (Least Frequently Used) - по частоте использования
// TTL (Time To Live) - истечение по времени (ортогонально LRU/LFU; часто комбинируется)
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

// Tag-based инвалидация (иллюстративный паттерн API; не встроен по умолчанию в Redis/Memcached)
cache.setWithTags("product:123", product, tags = listOf("products", "electronics"))
cache.invalidateByTag("electronics")
```

## Answer (EN)

**Caching Strategies Theory:**
Caching is an effective way to improve system performance. Different strategies have different consistency, performance, and implementation complexity characteristics.

See also: caching strategies and caching patterns (see [[c-architecture-patterns]]).

### Requirements (System Design Context)
- Functional:
  - Reduce read latency for hot data.
  - Offload databases and backend services.
  - Provide controllable cache invalidation mechanisms.
- Non-functional:
  - High availability and predictable performance.
  - Scalability with traffic growth.
  - Manageable consistency between cache and source of truth.

### Architecture (High-level View)
- Client → API/application servers.
- Cache layer (e.g., Redis/Memcached) in front of the database.
- Possible multi-level cache: local (L1) + distributed (L2) + DB.
- Invalidation mechanisms and/or event bus for consistency.

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

When to use: suitable when reads dominate, you can tolerate occasional cache misses, and your cache can be treated as a best-effort layer that may be evicted independently from the DB.

**2. Write-Through (Synchronous Write via Cache):**
```kotlin
// Conceptual example: write goes through cache and only succeeds when both cache and DB are updated
class WriteThroughUserService(
    private val cache: RedisCache,
    private val database: UserRepository
) {
    suspend fun updateUser(userId: Long, updates: UserUpdates): User {
        val updatedUser = database.update(userId, updates)
        cache.set("user:$userId", updatedUser, ttl = 1.hours)
        return updatedUser
    }
}
```

When to use: when you need strong consistency between cache and database on writes and can afford the extra write latency.

**3. Write-Behind / Write-Back (Asynchronous Write):**
```kotlin
// Write to cache immediately, enqueue async DB update
class WriteBackCache(
    private val cache: RedisCache,
    private val database: UserRepository,
    private val writeQueue: Queue<WriteOperation>
) {
    suspend fun updateUser(userId: Long, updates: UserUpdates): User {
        // 1. Read current from cache or DB
        val current = cache.get<User>("user:$userId") ?: database.findById(userId)
            ?: throw UserNotFoundException(userId)
        val updated = current.applyUpdates(updates)
        // 2. Update cache immediately
        cache.set("user:$userId", updated, ttl = 1.hours)
        // 3. Enqueue write for DB
        writeQueue.enqueue(WriteOperation("UPDATE_USER", userId, updates))
        return updated
    }
}
```

When to use: when write latency must be minimal and occasional short-term inconsistency between cache and DB is acceptable; requires durable queues and careful failure handling.

**Eviction / Expiration Policies:**
```kotlin
// LRU (Least Recently Used) - most popular replacement policy
// LFU (Least Frequently Used) - based on access frequency
// TTL (Time To Live) - time-based expiration (orthogonal to LRU/LFU; often combined)
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

// Tag-based invalidation pattern (illustrative API; not built into Redis/Memcached by default)
cache.setWithTags("product:123", product, tags = listOf("products", "electronics"))
cache.invalidateByTag("electronics")
```

---

## Follow-ups

- What is cache stampede and how do you prevent it?
- How do you implement distributed cache invalidation?
- Explain the difference between Redis and Memcached

## References

- "Cache (computing)", Wikipedia — https://en.wikipedia.org/wiki/Cache_(computing)

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

## Дополнительные Вопросы (RU)
- Что такое cache stampede и как его предотвратить?
- Как реализовать распределённую инвалидацию кеша?
- В чём разница между Redis и Memcached?
## Связанные Вопросы (RU)
### Предварительные (Проще)
- [[q-sql-nosql-databases--system-design--medium]] - Основы работы с базами данных
- [[q-load-balancing-strategies--system-design--medium]] - Балансировка нагрузки
### Связанные (Такой Же уровень)
- [[q-horizontal-vertical-scaling--system-design--medium]] - Стратегии масштабирования
- [[q-design-url-shortener--system-design--medium]] - Паттерны системного дизайна
### Продвинутые (Сложнее)
- [[q-microservices-vs-monolith--system-design--hard]] - Архитектурные подходы
- [[q-database-sharding-partitioning--system-design--hard]] - Масштабирование баз данных