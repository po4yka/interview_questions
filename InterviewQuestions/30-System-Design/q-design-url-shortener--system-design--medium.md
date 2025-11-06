---
id: sysdes-006
title: "Design URL Shortener (like bit.ly) / Проектирование сокращателя URL"
aliases: ["URL Shortener Design", "Проектирование сокращателя URL"]
topic: system-design
subtopics: [scalability, system-design-interview, url-shortener]
question_kind: system-design
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-system-design
related: [c-url-shortener, q-caching-strategies--system-design--medium, q-database-sharding-partitioning--system-design--hard]
created: 2025-10-12
updated: 2025-01-25
tags: [difficulty/medium, interview, scalability, system-design, url-shortener]
sources: [https://en.wikipedia.org/wiki/URL_shortening]
---

# Вопрос (RU)
> Спроектируйте сервис сокращения URL (как bit.ly). Каковы требования, архитектура и ключевые компромиссы?

# Question (EN)
> Design a URL shortening service (like bit.ly). What are the requirements, architecture, and key trade-offs?

---

## Ответ (RU)

**Теория проектирования URL shortener:**
URL shortener преобразует длинные URL в короткие, легко распространяемые ссылки. Ключевые задачи: генерация уникальных коротких кодов, быстрое перенаправление (low latency), масштабируемость (billions of URLs), высокая доступность.

**Требования:**

*Функциональные:*
- Создание короткого URL из длинного
- Перенаправление короткого URL на оригинальный
- Опционально: пользовательские aliases, аналитика, срок действия

*Нефункциональные:*
- Высокая доступность (99.99%)
- Низкая задержка (<100ms для redirect)
- Масштабируемость (billions of URLs)
- Read-heavy система (100:1 read:write ratio)

**Оценка ёмкости:**
```
Запись: 100M URLs/день = ~1,200 writes/sec
Чтение: 10B redirects/день = ~115,000 reads/sec
Хранение (5 лет): 182.5B URLs * 500 bytes ≈ 91 TB
```

**API Design:**
```kotlin
// REST API
@POST("/api/v1/urls")
fun createShortUrl(longUrl: String, customAlias: String? = null): ShortUrl

@GET("/{shortCode}")
fun redirect(shortCode: String): RedirectResponse // 302 redirect
```

**Генерация коротких кодов:**

*Теория:* Нужно генерировать уникальные короткие коды. Основные подходы: Base62 encoding, Hash-based, Random generation.

*1. Base62 Encoding (рекомендуется):*
```kotlin
// Кодирование auto-increment ID в Base62
class Base62Encoder {
    private val charset = "0-9a-zA-Z" // 62 символа

    fun encode(num: Long): String {
        // Преобразует число в Base62 строку
        // ID=1 → "1", ID=62 → "10", ID=3844 → "100"
    }
}
```
*Теория:* Использует auto-increment ID из БД, кодирует в Base62. 7 символов = 62^7 = 3.5 триллиона комбинаций. Гарантирует уникальность, предсказуемая длина. Минус: последовательные ID (можно решить добавлением random offset).

*2. Hash-based (MD5/SHA256):*
```kotlin
// Хеширование URL
fun generateShortCode(longUrl: String): String {
    val hash = md5(longUrl)
    return hash.substring(0, 7) // Первые 7 символов
}
```
*Теория:* Хеширует URL, берёт первые N символов. Минус: коллизии (нужна проверка уникальности и retry).

*3. Random Generation:*
```kotlin
// Случайная генерация
fun generateShortCode(): String {
    return (1..7).map { charset.random() }.joinToString("")
}
```
*Теория:* Генерирует случайную строку. Минус: коллизии, нужна проверка в БД.

**Схема БД:**
```sql
CREATE TABLE urls (
    id BIGSERIAL PRIMARY KEY,
    short_code VARCHAR(10) UNIQUE NOT NULL,
    long_url TEXT NOT NULL,
    created_at TIMESTAMP,
    expires_at TIMESTAMP,
    INDEX idx_short_code (short_code)
);
```

**Архитектура системы:**

*Теория:* Read-heavy система требует агрессивного кеширования. Используем CDN для географического распределения, Redis для кеша, шардирование БД для масштабирования.

*Компоненты:*
1. **Load Balancer** - распределение трафика
2. **Application Servers** - бизнес-логика
3. **Redis Cache** - кеш short_code → long_url (TTL 24 часа)
4. **Database (sharded)** - постоянное хранилище
5. **Analytics Service** - асинхронная обработка кликов

```kotlin
// Сервис с кешированием
class URLShortenerService(
    private val cache: RedisCache,
    private val database: URLRepository
) {
    suspend fun redirect(shortCode: String): String {
        // 1. Проверяем кеш (99% hit rate)
        cache.get(shortCode)?.let { return it }

        // 2. Cache miss - загружаем из БД
        val longUrl = database.findByShortCode(shortCode) ?: throw NotFoundException()

        // 3. Записываем в кеш
        cache.set(shortCode, longUrl, ttl = 24.hours)

        return longUrl
    }
}
```

**Масштабирование:**

*1. Кеширование:*
- Redis для hot URLs (80/20 rule - 20% URLs получают 80% трафика)
- CDN для статических ресурсов и редиректов
- Cache hit rate 99%+ критичен для производительности

*2. Шардирование БД:*
```kotlin
// Шардирование по short_code
fun getShard(shortCode: String): DataSource {
    val shardId = shortCode.hashCode() % numShards
    return shards[shardId]
}
```

*3. Асинхронная аналитика:*
```kotlin
// Не блокируем redirect для записи аналитики
fun redirect(shortCode: String): String {
    val longUrl = getUrl(shortCode)

    // Асинхронная запись клика в очередь
    analyticsQueue.enqueue(ClickEvent(shortCode, timestamp, userAgent))

    return longUrl
}
```

**Ключевые компромиссы:**

1. **Eventual consistency для счётчиков** - точность vs производительность
2. **302 vs 301 redirect** - 302 позволяет отслеживать клики, 301 быстрее (браузер кеширует)
3. **Длина короткого кода** - короче = меньше комбинаций, длиннее = больше символов
4. **Шардирование** - сложность vs масштабируемость

## Answer (EN)

**URL Shortener Design Theory:**
URL shortener converts long URLs into short, easily shareable links. Key challenges: unique short code generation, fast redirection (low latency), scalability (billions of URLs), high availability.

**Requirements:**

*Functional:*
- Create short URL from long URL
- Redirect short URL to original URL
- Optional: custom aliases, analytics, expiration

*Non-Functional:*
- High availability (99.99%)
- Low latency (<100ms for redirect)
- Scalability (billions of URLs)
- Read-heavy system (100:1 read:write ratio)

**Capacity Estimation:**
```
Write: 100M URLs/day = ~1,200 writes/sec
Read: 10B redirects/day = ~115,000 reads/sec
Storage (5 years): 182.5B URLs * 500 bytes ≈ 91 TB
```

**API Design:**
```kotlin
// REST API
@POST("/api/v1/urls")
fun createShortUrl(longUrl: String, customAlias: String? = null): ShortUrl

@GET("/{shortCode}")
fun redirect(shortCode: String): RedirectResponse // 302 redirect
```

**Short Code Generation:**

*Theory:* Need to generate unique short codes. Main approaches: Base62 encoding, Hash-based, Random generation.

*1. Base62 Encoding (recommended):*
```kotlin
// Encode auto-increment ID to Base62
class Base62Encoder {
    private val charset = "0-9a-zA-Z" // 62 characters

    fun encode(num: Long): String {
        // Converts number to Base62 string
        // ID=1 → "1", ID=62 → "10", ID=3844 → "100"
    }
}
```
*Theory:* Uses auto-increment ID from DB, encodes to Base62. 7 characters = 62^7 = 3.5 trillion combinations. Guarantees uniqueness, predictable length. Downside: sequential IDs (can solve with random offset).

*2. Hash-based (MD5/SHA256):*
```kotlin
// Hash URL
fun generateShortCode(longUrl: String): String {
    val hash = md5(longUrl)
    return hash.substring(0, 7) // First 7 characters
}
```
*Theory:* Hashes URL, takes first N characters. Downside: collisions (need uniqueness check and retry).

*3. Random Generation:*
```kotlin
// Random generation
fun generateShortCode(): String {
    return (1..7).map { charset.random() }.joinToString("")
}
```
*Theory:* Generates random string. Downside: collisions, need DB check.

**Database Schema:**
```sql
CREATE TABLE urls (
    id BIGSERIAL PRIMARY KEY,
    short_code VARCHAR(10) UNIQUE NOT NULL,
    long_url TEXT NOT NULL,
    created_at TIMESTAMP,
    expires_at TIMESTAMP,
    INDEX idx_short_code (short_code)
);
```

**System Architecture:**

*Theory:* Read-heavy system requires aggressive caching. Use CDN for geographic distribution, Redis for cache, DB sharding for scaling.

*Components:*
1. **Load Balancer** - traffic distribution
2. **Application Servers** - business logic
3. **Redis Cache** - cache short_code → long_url (TTL 24 hours)
4. **Database (sharded)** - persistent storage
5. **Analytics Service** - asynchronous click processing

```kotlin
// Service with caching
class URLShortenerService(
    private val cache: RedisCache,
    private val database: URLRepository
) {
    suspend fun redirect(shortCode: String): String {
        // 1. Check cache (99% hit rate)
        cache.get(shortCode)?.let { return it }

        // 2. Cache miss - load from DB
        val longUrl = database.findByShortCode(shortCode) ?: throw NotFoundException()

        // 3. Write to cache
        cache.set(shortCode, longUrl, ttl = 24.hours)

        return longUrl
    }
}
```

**Scaling:**

*1. Caching:*
- Redis for hot URLs (80/20 rule - 20% URLs get 80% traffic)
- CDN for static resources and redirects
- Cache hit rate 99%+ critical for performance

*2. Database Sharding:*
```kotlin
// Shard by short_code
fun getShard(shortCode: String): DataSource {
    val shardId = shortCode.hashCode() % numShards
    return shards[shardId]
}
```

*3. Asynchronous Analytics:*
```kotlin
// Don't block redirect for analytics write
fun redirect(shortCode: String): String {
    val longUrl = getUrl(shortCode)

    // Async write click to queue
    analyticsQueue.enqueue(ClickEvent(shortCode, timestamp, userAgent))

    return longUrl
}
```

**Key Trade-offs:**

1. **Eventual consistency for counters** - accuracy vs performance
2. **302 vs 301 redirect** - 302 allows tracking clicks, 301 faster (browser caches)
3. **Short code length** - shorter = fewer combinations, longer = more characters
4. **Sharding** - complexity vs scalability

---

## Follow-ups

- How do you handle custom aliases and prevent collisions?
- What's the difference between 301 and 302 redirects?
- How do you implement rate limiting for URL creation?

## Related Questions

### Prerequisites (Easier)
- [[q-caching-strategies--system-design--medium]] - Caching fundamentals
- [[q-rest-api-design-best-practices--system-design--medium]] - API design

### Related (Same Level)
- [[q-load-balancing-strategies--system-design--medium]] - Load balancing
- [[q-horizontal-vertical-scaling--system-design--medium]] - Scaling strategies

### Advanced (Harder)
- [[q-database-sharding-partitioning--system-design--hard]] - Database sharding
- [[q-cap-theorem-distributed-systems--system-design--hard]] - CAP theorem
