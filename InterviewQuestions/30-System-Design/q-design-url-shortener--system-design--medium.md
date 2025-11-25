---
id: sysdes-006
title: "Design URL Shortener (like bit.ly) / Проектирование сокращателя URL"
aliases: ["URL Shortener Design", "Проектирование сокращателя URL"]
topic: system-design
subtopics: [scalability, url-shortener]
question_kind: system-design
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-system-design
related: [c-caching-strategies, q-caching-strategies--system-design--medium, q-database-sharding-partitioning--system-design--hard]
created: 2025-10-12
updated: 2025-11-11
tags: [difficulty/medium, interview, scalability, system-design, url-shortener]
sources: ["https://en.wikipedia.org/wiki/URL_shortening"]

date created: Sunday, October 12th 2025, 8:45:45 pm
date modified: Tuesday, November 25th 2025, 8:53:55 pm
---

# Вопрос (RU)
> Спроектируйте сервис сокращения URL (как bit.ly). Каковы требования, архитектура и ключевые компромиссы?

# Question (EN)
> Design a URL shortening service (like bit.ly). What are the requirements, architecture, and key trade-offs?

---

## Ответ (RU)

### Требования

**Функциональные:**
- Создание короткого URL из длинного
- Перенаправление короткого URL на оригинальный
- Опционально: пользовательские алиасы, аналитика, срок действия

**Нефункциональные:**
- Высокая доступность (99.99%)
- Низкая задержка (<100ms для redirect)
- Масштабируемость (billions of URLs)
- Read-heavy система (100:1 read:write ratio)

### Архитектура

**Теория проектирования URL shortener:**
URL shortener преобразует длинные URL в короткие, легко распространяемые ссылки. Ключевые задачи: генерация уникальных коротких кодов, быстрое перенаправление (low latency), масштабируемость (billions of URLs), высокая доступность.

*Теория:* Read-heavy система требует агрессивного кеширования. Используем Redis для кеша, шардирование БД для масштабирования. Для географического распределения и быстрой доставки можно использовать CDN/edge (например, для статики, а также для выполнения логики редиректа как edge-функций). Также полезно понимать общие [[c-caching-strategies]].

*Компоненты:*
1. Load Balancer — распределение трафика
2. `Application` Servers — бизнес-логика
3. Redis Cache — кеш short_code → long_url (TTL ~24 часа, можно адаптивно)
4. Database (sharded) — постоянное хранилище
5. Analytics `Service` — асинхронная обработка кликов

**API Design:**
```kotlin
// REST API
@POST("/api/v1/urls")
fun createShortUrl(longUrl: String, customAlias: String? = null): ShortUrl

@GET("/{shortCode}")
fun redirect(shortCode: String): RedirectResponse // возвращает HTTP 302 Redirect (Location: longUrl)
```

**Генерация коротких кодов:**

*Теория:* Нужно генерировать уникальные короткие коды. Основные подходы: Base62 encoding, hash-based, random generation.

*1. Base62 Encoding (рекомендуется):*
```kotlin
// Кодирование auto-increment ID в Base62
class Base62Encoder {
    private val charset = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ" // 62 символа

    fun encode(num: Long): String {
        var n = num
        require(n >= 0) { "num must be non-negative" }
        if (n == 0L) return charset[0].toString()
        val sb = StringBuilder()
        while (n > 0) {
            val i = (n % 62).toInt()
            sb.append(charset[i])
            n /= 62
        }
        return sb.reverse().toString()
    }
}
```
*Теория:* Использует auto-increment ID из БД, кодирует в Base62. 7 символов = 62^7 ≈ 3.5 триллиона комбинаций. При уникальных ID получаем уникальные коды, предсказуемая длина. Минус: последовательные ID (можно частично скрыть добавлением random offset или permuting).

*2. Hash-based (MD5/SHA-256):*
```kotlin
// Хеширование URL
fun generateShortCode(longUrl: String): String {
    val hash = md5(longUrl)
    val code = hash.substring(0, 7) // Первые 7 символов
    // При коллизии: проверить в БД и при необходимости выбрать другие биты/символы
    return code
}
```
*Теория:* Хеширует URL, берёт первые N символов. Минус: возможны коллизии (нужна проверка уникальности и стратегия разрешения).

*3. Random Generation:*
```kotlin
// Случайная генерация
private val charset = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

fun generateShortCode(): String {
    return (1..7)
        .map { charset.random() }
        .joinToString("")
}
```
*Теория:* Генерирует случайную строку. Минус: коллизии, нужна проверка в БД/кеше и возможный retry.

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

**Сервис с кешированием:**
```kotlin
class URLShortenerService(
    private val cache: RedisCache,
    private val database: URLRepository
) {
    suspend fun redirect(shortCode: String): String {
        // 1. Проверяем кеш
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
- CDN/edge для статики и/или выполнения логики редиректа ближе к пользователю
- Высокий cache hit rate (стремимся к ~99%) критичен для производительности

*2. Шардирование БД:*
```kotlin
// Шардирование по short_code
fun getShard(shortCode: String): DataSource {
    val shardId = (shortCode.hashCode().absoluteValue) % numShards
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

1. Eventual consistency для счётчиков — точность vs производительность (агрегировать асинхронно)
2. 302 vs 301 redirect — выбор кода влияет на кеширование и гибкость
3. Длина короткого кода — баланс между количеством комбинаций и удобством
4. Шардирование — сложность против масштабируемости и отказоустойчивости

### Дополнительные Вопросы (RU)

- Как изменить дизайн для поддержки пользовательских доменов для коротких ссылок?
- Как обрабатывать массовое создание ссылок (batch API) и rate limiting?
- Какие стратегии использовать для защиты от злоупотреблений (phishing, spam, brute-force перебор кодов)?

### Ссылки (RU)

- "https://en.wikipedia.org/wiki/URL_shortening"

### Связанные Вопросы (RU)

- [[q-caching-strategies--system-design--medium]]
- [[q-database-sharding-partitioning--system-design--hard]]

## Answer (EN)

### Requirements

**Functional:**
- Create short URL from long URL
- Redirect short URL to original URL
- Optional: custom aliases, analytics, expiration

**Non-Functional:**
- High availability (99.99%)
- Low latency (<100ms for redirect)
- Scalability (billions of URLs)
- Read-heavy system (100:1 read:write ratio)

### Architecture

**URL Shortener Design Theory:**
URL shortener converts long URLs into short, easily shareable links. Key challenges: unique short code generation, fast redirection (low latency), scalability (billions of URLs), high availability.

*Theory:* Read-heavy system requires aggressive caching. Use Redis for cache, DB sharding for scaling. For geographic distribution and low latency we can use CDN/edge (e.g., for static assets and to run redirect logic at the edge). Also see [[c-caching-strategies]] for general caching patterns.

*Components:*
1. Load Balancer - traffic distribution
2. `Application` Servers - business logic
3. Redis Cache - cache short_code → long_url (TTL ~24 hours, can be tuned)
4. Database (sharded) - persistent storage
5. Analytics `Service` - asynchronous click processing

**API Design:**
```kotlin
// REST API
@POST("/api/v1/urls")
fun createShortUrl(longUrl: String, customAlias: String? = null): ShortUrl

@GET("/{shortCode}")
fun redirect(shortCode: String): RedirectResponse // returns HTTP 302 Redirect (Location: longUrl)
```

**Short Code Generation:**

*Theory:* Need to generate unique short codes. Main approaches: Base62 encoding, hash-based, random generation.

*1. Base62 Encoding (recommended):*
```kotlin
// Encode auto-increment ID to Base62
class Base62Encoder {
    private val charset = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ" // 62 characters

    fun encode(num: Long): String {
        var n = num
        require(n >= 0) { "num must be non-negative" }
        if (n == 0L) return charset[0].toString()
        val sb = StringBuilder()
        while (n > 0) {
            val i = (n % 62).toInt()
            sb.append(charset[i])
            n /= 62
        }
        return sb.reverse().toString()
    }
}
```
*Theory:* Uses auto-increment ID from DB, encodes to Base62. 7 characters = 62^7 ≈ 3.5 trillion combinations. With unique IDs, we get unique codes and predictable length. Downside: sequential IDs (can be partially hidden via random offset or permutation).

*2. Hash-based (MD5/SHA-256):*
```kotlin
// Hash URL
fun generateShortCode(longUrl: String): String {
    val hash = md5(longUrl)
    val code = hash.substring(0, 7) // First 7 characters
    // On collision: check DB and, if needed, use different bits/characters
    return code
}
```
*Theory:* Hashes URL, takes first N characters. Downside: possible collisions (need uniqueness check and collision resolution strategy).

*3. Random Generation:*
```kotlin
// Random generation
private val charset = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

fun generateShortCode(): String {
    return (1..7)
        .map { charset.random() }
        .joinToString("")
}
```
*Theory:* Generates random string. Downside: collisions, requires DB/cache check and retry.

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

**Service with caching:**
```kotlin
class URLShortenerService(
    private val cache: RedisCache,
    private val database: URLRepository
) {
    suspend fun redirect(shortCode: String): String {
        // 1. Check cache
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
- CDN/edge for static resources and/or executing redirect logic closer to users
- High cache hit rate (target around 99%) is critical for performance

*2. Database Sharding:*
```kotlin
// Shard by short_code
fun getShard(shortCode: String): DataSource {
    val shardId = (shortCode.hashCode().absoluteValue) % numShards
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

1. Eventual consistency for counters - accuracy vs performance (aggregate asynchronously)
2. 302 vs 301 redirect - impact on caching and flexibility
3. Short code length - balance between number of combinations and usability
4. Sharding - complexity vs scalability and fault isolation

## Follow-ups

- How would you adapt the design to support custom domains for short links?
- How would you handle bulk URL creation (batch API) and rate limiting?
- What strategies would you use to protect against abuse (phishing, spam, brute-force code scanning)?

## References

- "https://en.wikipedia.org/wiki/URL_shortening"

## Related Questions

- [[q-caching-strategies--system-design--medium]]
- [[q-database-sharding-partitioning--system-design--hard]]
