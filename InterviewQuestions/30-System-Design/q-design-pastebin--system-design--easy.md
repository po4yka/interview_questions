---
id: q-design-pastebin
title: Design Pastebin / Проектирование Pastebin
aliases:
- Pastebin Design
- Проектирование Pastebin
topic: system-design
subtopics:
- storage
- url-shortening
- text
question_kind: system-design
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-design-url-shortener--system-design--medium
- q-caching-strategies--system-design--medium
- q-object-vs-block-storage--system-design--medium
created: 2026-01-26
updated: 2026-01-26
tags:
- difficulty/easy
- interview
- storage
- system-design
- url-shortening
sources:
- https://pastebin.com/
anki_cards:
- slug: q-design-pastebin-0-en
  anki_id: null
  synced_at: null
- slug: q-design-pastebin-0-ru
  anki_id: null
  synced_at: null
---
# Vopros (RU)
> Как бы вы спроектировали сервис хранения текста, подобный Pastebin?

# Question (EN)
> How would you design a text storage service like Pastebin?

---

## Otvet (RU)

### Требования

**Функциональные:**
- Загрузка текста и получение короткой ссылки
- Просмотр текста по ссылке
- Опционально: срок действия, приватные пасты, синтаксическая подсветка

**Нефункциональные:**
- Высокая доступность (99.9%)
- Низкая задержка чтения (<200ms)
- Масштабируемость (миллионы паст)
- Read-heavy система (5:1 read:write ratio)

### Оценка Масштаба

**Теория:**
Для easy-level собеседования достаточно базовых расчётов.

*Допущения:*
- 1 млн новых паст в день
- Средний размер пасты: 10 KB
- Хранение: 5 лет

*Расчёты:*
- Хранилище в день: 1M * 10 KB = 10 GB/день
- Хранилище за 5 лет: 10 GB * 365 * 5 = 18 TB
- Write QPS: 1M / 86400 = ~12 writes/sec
- Read QPS (5:1): ~60 reads/sec

### Архитектура

**Компоненты:**
1. **Load Balancer** - распределение трафика
2. **Application Servers** - бизнес-логика
3. **Object Storage** (S3/GCS) - хранение текста паст
4. **Metadata Database** - метаданные (PostgreSQL)
5. **Cache** (Redis) - кеш популярных паст
6. **Cleanup Service** - удаление истёкших паст

### Генерация Короткого URL

*Теория:* Используем Base62 encoding для генерации коротких кодов.

```kotlin
// Base62 encoding
class PasteKeyGenerator {
    private val charset = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    fun generate(id: Long): String {
        var n = id
        val sb = StringBuilder()
        while (n > 0) {
            sb.append(charset[(n % 62).toInt()])
            n /= 62
        }
        return sb.reverse().toString().padStart(8, '0')
    }
}
```

*8 символов Base62 = 62^8 = 218 триллионов комбинаций*

### Хранение Текста

**Object Storage vs Database:**

| Подход | Плюсы | Минусы |
|--------|-------|--------|
| Object Storage (S3) | Дёшево, масштабируется, CDN-ready | Дополнительный hop |
| Database (BLOB) | Простота, одна система | Дорого при масштабе |

*Рекомендация:* Object Storage для текста, Database для метаданных.

```kotlin
// Структура хранения
data class Paste(
    val key: String,          // короткий ключ "abc12345"
    val storageUrl: String,   // s3://pastebin/abc12345
    val createdAt: Instant,
    val expiresAt: Instant?,
    val isPrivate: Boolean,
    val syntaxType: String?   // "kotlin", "python", etc.
)
```

### Схема БД Метаданных

```sql
CREATE TABLE pastes (
    id BIGSERIAL PRIMARY KEY,
    key VARCHAR(10) UNIQUE NOT NULL,
    storage_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    is_private BOOLEAN DEFAULT FALSE,
    syntax_type VARCHAR(50),
    view_count BIGINT DEFAULT 0,
    INDEX idx_key (key),
    INDEX idx_expires_at (expires_at)
);
```

### API Design

```kotlin
// REST API
@POST("/api/v1/pastes")
fun createPaste(
    content: String,
    expiresIn: Duration? = null,
    syntax: String? = null,
    isPrivate: Boolean = false
): PasteResponse  // { "key": "abc12345", "url": "https://paste.bin/abc12345" }

@GET("/api/v1/pastes/{key}")
fun getPaste(key: String): PasteContent

@DELETE("/api/v1/pastes/{key}")
fun deletePaste(key: String, apiKey: String): DeleteResponse
```

### Сервис с Кешированием

```kotlin
class PasteService(
    private val storage: ObjectStorage,
    private val metadata: PasteRepository,
    private val cache: RedisCache
) {
    suspend fun getPaste(key: String): String {
        // 1. Проверяем кеш
        cache.get(key)?.let { return it }

        // 2. Получаем метаданные
        val paste = metadata.findByKey(key)
            ?: throw NotFoundException()

        // 3. Проверяем срок действия
        if (paste.expiresAt != null && paste.expiresAt < Instant.now()) {
            throw ExpiredException()
        }

        // 4. Загружаем контент
        val content = storage.get(paste.storageUrl)

        // 5. Кешируем
        cache.set(key, content, ttl = 1.hours)

        return content
    }
}
```

### Обработка Срока Действия

**Подходы:**

*1. Lazy Deletion (рекомендуется):*
- Проверяем `expires_at` при чтении
- Фоновый job удаляет старые записи

*2. TTL в Object Storage:*
- S3 Lifecycle Rules автоматически удаляют объекты

```kotlin
// Cleanup job (запускается периодически)
class CleanupJob(
    private val metadata: PasteRepository,
    private val storage: ObjectStorage
) {
    @Scheduled(cron = "0 0 * * *") // ежедневно
    fun cleanupExpired() {
        val expired = metadata.findExpiredBefore(Instant.now(), limit = 1000)
        expired.forEach { paste ->
            storage.delete(paste.storageUrl)
            metadata.delete(paste.key)
        }
    }
}
```

### Rate Limiting

```kotlin
// Простой rate limiter (token bucket)
class RateLimiter(
    private val maxRequests: Int = 100,
    private val windowSeconds: Int = 60
) {
    suspend fun checkLimit(clientIp: String): Boolean {
        val key = "rate:$clientIp"
        val count = redis.incr(key)
        if (count == 1L) {
            redis.expire(key, windowSeconds)
        }
        return count <= maxRequests
    }
}
```

### Синтаксическая Подсветка

*Теория:* Подсветка выполняется на клиенте для снижения нагрузки.

- Храним `syntax_type` в метаданных
- Клиент использует библиотеки (Highlight.js, Prism)
- Сервер возвращает raw text + syntax hint

### Кеширование

**Стратегия:**
- Redis для hot pastes (LRU eviction)
- CDN для публичных паст
- TTL 1-24 часа в зависимости от популярности

### Масштабирование

| Компонент | Стратегия |
|-----------|-----------|
| App Servers | Горизонтальное (stateless) |
| Database | Read replicas, позже sharding |
| Object Storage | Встроенная (S3/GCS) |
| Cache | Redis Cluster |

### Ключевые Компромиссы

1. **Object Storage vs DB** - стоимость vs простота
2. **Eager vs Lazy deletion** - ресурсы vs сложность
3. **Client vs Server syntax highlighting** - нагрузка vs контроль
4. **Cache TTL** - свежесть vs производительность

### Дополнительные Вопросы (RU)

- Как добавить поддержку редактирования паст?
- Как реализовать версионирование паст?
- Как защитить от спама и злоупотреблений?

### Связанные Вопросы (RU)

- [[q-design-url-shortener--system-design--medium]]
- [[q-caching-strategies--system-design--medium]]
- [[q-object-vs-block-storage--system-design--medium]]

---

## Answer (EN)

### Requirements

**Functional:**
- Upload text and receive short link
- View text by link
- Optional: expiration, private pastes, syntax highlighting

**Non-Functional:**
- High availability (99.9%)
- Low read latency (<200ms)
- Scalability (millions of pastes)
- Read-heavy system (5:1 read:write ratio)

### Back-of-Envelope Estimation

**Theory:**
For an easy-level interview, basic calculations suffice.

*Assumptions:*
- 1M new pastes per day
- Average paste size: 10 KB
- Retention: 5 years

*Calculations:*
- Daily storage: 1M * 10 KB = 10 GB/day
- 5-year storage: 10 GB * 365 * 5 = 18 TB
- Write QPS: 1M / 86400 = ~12 writes/sec
- Read QPS (5:1): ~60 reads/sec

### Architecture

**Components:**
1. **Load Balancer** - traffic distribution
2. **Application Servers** - business logic
3. **Object Storage** (S3/GCS) - paste content storage
4. **Metadata Database** - metadata (PostgreSQL)
5. **Cache** (Redis) - cache for popular pastes
6. **Cleanup Service** - delete expired pastes

### Short URL Generation

*Theory:* Use Base62 encoding for short code generation.

```kotlin
// Base62 encoding
class PasteKeyGenerator {
    private val charset = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    fun generate(id: Long): String {
        var n = id
        val sb = StringBuilder()
        while (n > 0) {
            sb.append(charset[(n % 62).toInt()])
            n /= 62
        }
        return sb.reverse().toString().padStart(8, '0')
    }
}
```

*8 Base62 characters = 62^8 = 218 trillion combinations*

### Text Storage

**Object Storage vs Database:**

| Approach | Pros | Cons |
|----------|------|------|
| Object Storage (S3) | Cheap, scalable, CDN-ready | Extra hop |
| Database (BLOB) | Simple, single system | Expensive at scale |

*Recommendation:* Object Storage for text, Database for metadata.

```kotlin
// Storage structure
data class Paste(
    val key: String,          // short key "abc12345"
    val storageUrl: String,   // s3://pastebin/abc12345
    val createdAt: Instant,
    val expiresAt: Instant?,
    val isPrivate: Boolean,
    val syntaxType: String?   // "kotlin", "python", etc.
)
```

### Metadata Database Schema

```sql
CREATE TABLE pastes (
    id BIGSERIAL PRIMARY KEY,
    key VARCHAR(10) UNIQUE NOT NULL,
    storage_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    is_private BOOLEAN DEFAULT FALSE,
    syntax_type VARCHAR(50),
    view_count BIGINT DEFAULT 0,
    INDEX idx_key (key),
    INDEX idx_expires_at (expires_at)
);
```

### API Design

```kotlin
// REST API
@POST("/api/v1/pastes")
fun createPaste(
    content: String,
    expiresIn: Duration? = null,
    syntax: String? = null,
    isPrivate: Boolean = false
): PasteResponse  // { "key": "abc12345", "url": "https://paste.bin/abc12345" }

@GET("/api/v1/pastes/{key}")
fun getPaste(key: String): PasteContent

@DELETE("/api/v1/pastes/{key}")
fun deletePaste(key: String, apiKey: String): DeleteResponse
```

### Service with Caching

```kotlin
class PasteService(
    private val storage: ObjectStorage,
    private val metadata: PasteRepository,
    private val cache: RedisCache
) {
    suspend fun getPaste(key: String): String {
        // 1. Check cache
        cache.get(key)?.let { return it }

        // 2. Get metadata
        val paste = metadata.findByKey(key)
            ?: throw NotFoundException()

        // 3. Check expiration
        if (paste.expiresAt != null && paste.expiresAt < Instant.now()) {
            throw ExpiredException()
        }

        // 4. Load content
        val content = storage.get(paste.storageUrl)

        // 5. Cache it
        cache.set(key, content, ttl = 1.hours)

        return content
    }
}
```

### Expiration Handling

**Approaches:**

*1. Lazy Deletion (recommended):*
- Check `expires_at` on read
- Background job cleans up old entries

*2. TTL in Object Storage:*
- S3 Lifecycle Rules auto-delete objects

```kotlin
// Cleanup job (runs periodically)
class CleanupJob(
    private val metadata: PasteRepository,
    private val storage: ObjectStorage
) {
    @Scheduled(cron = "0 0 * * *") // daily
    fun cleanupExpired() {
        val expired = metadata.findExpiredBefore(Instant.now(), limit = 1000)
        expired.forEach { paste ->
            storage.delete(paste.storageUrl)
            metadata.delete(paste.key)
        }
    }
}
```

### Rate Limiting

```kotlin
// Simple rate limiter (token bucket)
class RateLimiter(
    private val maxRequests: Int = 100,
    private val windowSeconds: Int = 60
) {
    suspend fun checkLimit(clientIp: String): Boolean {
        val key = "rate:$clientIp"
        val count = redis.incr(key)
        if (count == 1L) {
            redis.expire(key, windowSeconds)
        }
        return count <= maxRequests
    }
}
```

### Syntax Highlighting

*Theory:* Highlighting is done client-side to reduce server load.

- Store `syntax_type` in metadata
- Client uses libraries (Highlight.js, Prism)
- Server returns raw text + syntax hint

### Caching

**Strategy:**
- Redis for hot pastes (LRU eviction)
- CDN for public pastes
- TTL 1-24 hours based on popularity

### Scaling

| Component | Strategy |
|-----------|----------|
| App Servers | Horizontal (stateless) |
| Database | Read replicas, later sharding |
| Object Storage | Built-in (S3/GCS) |
| Cache | Redis Cluster |

### Key Trade-offs

1. **Object Storage vs DB** - cost vs simplicity
2. **Eager vs Lazy deletion** - resources vs complexity
3. **Client vs Server syntax highlighting** - load vs control
4. **Cache TTL** - freshness vs performance

## Follow-ups

- How would you add support for editing pastes?
- How would you implement paste versioning?
- How would you protect against spam and abuse?

## Related Questions

- [[q-design-url-shortener--system-design--medium]]
- [[q-caching-strategies--system-design--medium]]
- [[q-object-vs-block-storage--system-design--medium]]
