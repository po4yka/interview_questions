---
id: 20251012-300010
title: "Design URL Shortener (like bit.ly) / Проектирование сокращателя URL"
topic: system-design
difficulty: medium
status: draft
created: 2025-10-12
tags: - system-design
  - url-shortener
  - interview
  - scalability
date_created: 2025-10-12
date_updated: 2025-10-12
moc: moc-system-design
related_questions:   - q-database-sharding-partitioning--system-design--hard
  - q-caching-strategies--system-design--medium
  - q-rest-api-design-best-practices--system-design--medium
slug: design-url-shortener-system-design-medium
subtopics:   - system-design-interview
  - url-shortener
  - scalability
  - distributed-systems
---
# Design URL Shortener (like bit.ly)

## English Version

### Problem Statement

Design a URL shortening service like bit.ly, TinyURL, or goo.gl that converts long URLs into short, easy-to-share links.

**Example:**
```
Long URL:  https://www.example.com/articles/2024/how-to-design-systems?utm_source=twitter
Short URL: https://bit.ly/3xY9zK2
```

**Requirements:**
1. **Functional:**
   - Create short URL from long URL
   - Redirect short URL to original URL
   - Custom aliases (optional)
   - Analytics (click count, referrers, etc.)
   - Expiration (optional)

2. **Non-Functional:**
   - High availability (99.99%)
   - Low latency (<100ms)
   - Scalable (billions of URLs)
   - Durable (URLs never lost)

### Detailed Answer

#### 1. Requirements Clarification

**Questions to ask:**
```
Q: How many URLs created per day?
A: 100 million new URLs/day

Q: What's the read:write ratio?
A: Read-heavy, 100:1 ratio (10 billion redirects/day)

Q: How long should URLs be stored?
A: Forever (or configurable expiration)

Q: Can users customize short codes?
A: Yes (premium feature)

Q: Do we need analytics?
A: Yes (click count, location, referrer)
```

**Capacity Estimation:**
```
Write: 100M URLs/day = ~1,200 writes/sec
Read:  10B redirects/day = ~115,000 reads/sec

Storage (5 years):
100M URLs/day * 365 days * 5 years = 182.5B URLs
Each URL: ~500 bytes (long URL + metadata)
Total: 182.5B * 500 bytes ≈ 91 TB

Bandwidth:
Write: 1,200 req/s * 500 bytes = 600 KB/s
Read:  115,000 req/s * 500 bytes = 57.5 MB/s
```

---

#### 2. API Design

```kotlin
// REST API
interface URLShortenerAPI {
    
    // Create short URL
    @POST("/api/v1/urls")
    suspend fun createShortUrl(
        @Body request: CreateUrlRequest
    ): CreateUrlResponse
    
    // Get original URL (for redirect)
    @GET("/{shortCode}")
    suspend fun redirect(
        @Path shortCode: String
    ): RedirectResponse
    
    // Get analytics
    @GET("/api/v1/urls/{shortCode}/analytics")
    suspend fun getAnalytics(
        @Path shortCode: String
    ): AnalyticsResponse
}

data class CreateUrlRequest(
    val longUrl: String,
    val customAlias: String? = null,  // Optional custom short code
    val expiresAt: Instant? = null     // Optional expiration
)

data class CreateUrlResponse(
    val shortUrl: String,              // e.g., "https://bit.ly/3xY9zK2"
    val shortCode: String,             // e.g., "3xY9zK2"
    val longUrl: String,
    val createdAt: Instant
)

data class RedirectResponse(
    val longUrl: String,
    val status: Int = 302  // Temporary redirect
)
```

---

#### 3. Database Schema

```sql
-- URL mappings table
CREATE TABLE urls (
    id BIGSERIAL PRIMARY KEY,
    short_code VARCHAR(10) UNIQUE NOT NULL,
    long_url TEXT NOT NULL,
    user_id BIGINT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP,
    click_count BIGINT DEFAULT 0,
    INDEX idx_short_code (short_code),
    INDEX idx_user_id (user_id)
);

-- Analytics table (separate for scalability)
CREATE TABLE url_clicks (
    id BIGSERIAL PRIMARY KEY,
    short_code VARCHAR(10) NOT NULL,
    clicked_at TIMESTAMP NOT NULL DEFAULT NOW(),
    ip_address VARCHAR(45),
    user_agent TEXT,
    referer TEXT,
    country VARCHAR(2),
    INDEX idx_short_code_time (short_code, clicked_at)
);

-- Users table
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

---

#### 4. Short Code Generation

**Key Design Decision:** How to generate unique short codes?

**Option 1: Base62 Encoding (Recommended)**

```kotlin
class Base62Encoder {
    private val charset = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    private val base = charset.length  // 62
    
    fun encode(num: Long): String {
        if (num == 0L) return charset[0].toString()
        
        val sb = StringBuilder()
        var n = num
        
        while (n > 0) {
            sb.append(charset[(n % base).toInt()])
            n /= base
        }
        
        return sb.reverse().toString()
    }
    
    fun decode(str: String): Long {
        var num = 0L
        str.forEach { char ->
            num = num * base + charset.indexOf(char)
        }
        return num
    }
}

// Usage
@Service
class URLShortener(
    private val encoder: Base62Encoder,
    private val repository: URLRepository
) {
    suspend fun createShortUrl(longUrl: String): String {
        // Get next ID from database sequence
        val id = repository.getNextId()
        
        // Encode ID to base62
        val shortCode = encoder.encode(id)
        
        // Store mapping
        repository.save(URL(
            id = id,
            shortCode = shortCode,
            longUrl = longUrl
        ))
        
        return "https://bit.ly/$shortCode"
    }
}

// Examples:
encode(1) = "1"
encode(62) = "10"
encode(1000) = "g8"
encode(1000000) = "4C92"
encode(1000000000) = "15ftgG"

// 7 characters = 62^7 = 3.5 trillion URLs!
```

**Length calculation:**
```
6 characters: 62^6 = 56.8 billion URLs
7 characters: 62^7 = 3.5 trillion URLs
8 characters: 62^8 = 218 trillion URLs

For 182.5B URLs (5 years), 7 characters enough!
```

**Option 2: MD5/SHA256 Hash (with collision handling)**

```kotlin
class HashBasedShortener {
    suspend fun createShortUrl(longUrl: String): String {
        // Generate hash
        val hash = MessageDigest.getInstance("MD5")
            .digest(longUrl.toByteArray())
            .toHexString()
        
        // Take first 7 characters
        var shortCode = hash.substring(0, 7)
        
        // Handle collision
        var attempt = 0
        while (repository.exists(shortCode)) {
            // Append counter and re-hash
            val newInput = "$longUrl-$attempt"
            hash = md5(newInput)
            shortCode = hash.substring(0, 7)
            attempt++
        }
        
        repository.save(URL(shortCode, longUrl))
        return shortCode
    }
}
```

** Base62 Pros:**
- No collisions (unique sequence)
- Short codes (7 chars)
- Predictable length

** Base62 Cons:**
- Sequential (can guess next URL)
- Needs centralized sequence

** Hash Pros:**
- Decentralized (any server can generate)
- Same URL always gets same hash (idempotent)

** Hash Cons:**
- Collisions possible (need handling)
- Longer codes (7+ chars minimum)

**Recommendation: Base62 with distributed ID generation (Snowflake)**

---

#### 5. System Architecture

```
                          
                            CDN/CloudFlare
                            (Caching)     
                          
                                   
                          
                           Load Balancer  
                          
                                     
                    
                                                
                
              API           API           API       
              Server 1      Server 2      Server 3  
                
                                                
                  
                                         
                    
                    Redis Cache     Analytics   
                    (Read cache)    Queue       
                      (Kafka)     
                                   
                  
                    PostgreSQL  
                    (Sharded)   
                    - Shard 1   
                    - Shard 2   
                    - Shard 3   
                  
```

---

#### 6. Implementation

**Create Short URL:**
```kotlin
@RestController
@RequestMapping("/api/v1")
class URLController(
    private val urlService: URLService,
    private val cache: RedisCache
) {
    @PostMapping("/urls")
    suspend fun createShortUrl(
        @Valid @RequestBody request: CreateUrlRequest
    ): CreateUrlResponse {
        
        // Validate URL
        if (!isValidUrl(request.longUrl)) {
            throw BadRequestException("Invalid URL")
        }
        
        // Check if custom alias requested
        val shortCode = if (request.customAlias != null) {
            // Check availability
            if (urlService.exists(request.customAlias)) {
                throw ConflictException("Alias already taken")
            }
            request.customAlias
        } else {
            // Generate short code
            urlService.generateShortCode()
        }
        
        // Save to database
        val url = urlService.create(URL(
            shortCode = shortCode,
            longUrl = request.longUrl,
            expiresAt = request.expiresAt
        ))
        
        // Cache the mapping
        cache.set(
            key = "url:$shortCode",
            value = url.longUrl,
            ttl = 24.hours
        )
        
        return CreateUrlResponse(
            shortUrl = "https://bit.ly/$shortCode",
            shortCode = shortCode,
            longUrl = url.longUrl,
            createdAt = url.createdAt
        )
    }
}
```

**Redirect (Read Path - Critical for Performance):**
```kotlin
@RestController
class RedirectController(
    private val cache: RedisCache,
    private val urlService: URLService,
    private val analyticsQueue: KafkaProducer
) {
    @GetMapping("/{shortCode}")
    suspend fun redirect(
        @PathVariable shortCode: String,
        request: HttpServletRequest
    ): ResponseEntity<Void> {
        
        // 1. Check cache first (99% hit rate)
        var longUrl = cache.get<String>("url:$shortCode")
        
        if (longUrl == null) {
            // 2. Cache miss - query database
            val url = urlService.findByShortCode(shortCode)
                ?: throw NotFoundException("URL not found")
            
            // Check expiration
            if (url.expiresAt != null && url.expiresAt < Instant.now()) {
                throw GoneException("URL expired")
            }
            
            longUrl = url.longUrl
            
            // 3. Populate cache
            cache.set("url:$shortCode", longUrl, ttl = 24.hours)
        }
        
        // 4. Track analytics asynchronously (non-blocking)
        launch {
            analyticsQueue.send(ClickEvent(
                shortCode = shortCode,
                timestamp = Instant.now(),
                ipAddress = request.remoteAddr,
                userAgent = request.getHeader("User-Agent"),
                referer = request.getHeader("Referer")
            ))
        }
        
        // 5. Return redirect (302 temporary, allows analytics tracking)
        return ResponseEntity
            .status(HttpStatus.FOUND)  // 302
            .location(URI(longUrl))
            .cacheControl(CacheControl.noCache())  // Don't cache redirects
            .build()
    }
}
```

**Analytics Processing:**
```kotlin
@Service
class AnalyticsProcessor {
    
    @KafkaListener(topics = ["click-events"])
    suspend fun processClick(event: ClickEvent) {
        // Save to analytics database
        analyticsRepository.save(URLClick(
            shortCode = event.shortCode,
            clickedAt = event.timestamp,
            ipAddress = event.ipAddress,
            userAgent = event.userAgent,
            referer = event.referer,
            country = geoService.getCountry(event.ipAddress)
        ))
        
        // Increment counter (can batch)
        urlRepository.incrementClickCount(event.shortCode)
        
        // Update cache
        cache.increment("clicks:${event.shortCode}")
    }
}
```

---

#### 7. Optimizations

**Caching Strategy:**
```kotlin
// Multi-level caching
class MultiLevelCache {
    suspend fun getLongUrl(shortCode: String): String? {
        // L1: Local in-memory cache (fastest, ~1μs)
        localCache.get(shortCode)?.let { return it }
        
        // L2: Redis (fast, ~1ms)
        redisCache.get(shortCode)?.let { url ->
            localCache.put(shortCode, url)  // Populate L1
            return url
        }
        
        // L3: Database (slow, ~10-100ms)
        database.findByShortCode(shortCode)?.let { url ->
            redisCache.set(shortCode, url.longUrl)  // Populate L2
            localCache.put(shortCode, url.longUrl)  // Populate L1
            return url.longUrl
        }
        
        return null
    }
}
```

**Database Sharding:**
```kotlin
// Shard by short code hash
class URLShardRouter(private val shards: List<DataSource>) {
    fun getShard(shortCode: String): DataSource {
        val hash = shortCode.hashCode()
        val shardIndex = abs(hash % shards.size)
        return shards[shardIndex]
    }
}

// Write to specific shard
suspend fun createUrl(url: URL) {
    val shard = shardRouter.getShard(url.shortCode)
    shard.insert(url)
}

// Read from specific shard
suspend fun getUrl(shortCode: String): URL? {
    val shard = shardRouter.getShard(shortCode)
    return shard.query(shortCode)
}
```

**Rate Limiting:**
```kotlin
@Component
class RateLimiter(private val redis: RedisTemplate) {
    
    fun isAllowed(userId: String): Boolean {
        val key = "rate_limit:$userId"
        val count = redis.increment(key)
        
        if (count == 1L) {
            redis.expire(key, 1, TimeUnit.HOURS)
        }
        
        return count <= 100  // 100 URLs per hour
    }
}
```

---

#### 8. Monitoring & Analytics

```kotlin
// Metrics
@Service
class MetricsService {
    private val createCounter = Counter.build()
        .name("url_creates_total")
        .help("Total URL creations")
        .register()
    
    private val redirectCounter = Counter.build()
        .name("url_redirects_total")
        .help("Total redirects")
        .labelNames("status")
        .register()
    
    private val cacheHitRate = Gauge.build()
        .name("cache_hit_rate")
        .help("Cache hit percentage")
        .register()
    
    private val latency = Summary.build()
        .name("redirect_latency_seconds")
        .help("Redirect latency")
        .register()
}
```

---

### Key Takeaways

1. **Short code generation:** Base62 encoding (7 chars = 3.5T URLs)
2. **Database:** Sharded PostgreSQL for scalability
3. **Caching:** Multi-level (CDN → Redis → DB), 99%+ hit rate
4. **Analytics:** Async processing with Kafka
5. **API:** REST with create + redirect endpoints
6. **Performance:** <100ms latency with caching
7. **Scalability:** Horizontal scaling with sharding
8. **Availability:** Multi-region, load balanced
9. **ID generation:** Snowflake for distributed unique IDs
10. **Monitoring:** Metrics, logging, distributed tracing

---

## Russian Version

### Постановка задачи

Спроектируйте сервис сокращения URL как bit.ly, TinyURL или goo.gl, который конвертирует длинные URLs в короткие, удобные для обмена ссылки.

**Пример:**
```
Длинный URL:  https://www.example.com/articles/2024/how-to-design-systems
Короткий URL: https://bit.ly/3xY9zK2
```

### Ключевые выводы

1. **Генерация короткого кода:** Base62 кодирование (7 символов = 3.5T URLs)
2. **База данных:** Шардированная PostgreSQL
3. **Кеширование:** Многоуровневое (CDN → Redis → DB), 99%+ hit rate
4. **Аналитика:** Async обработка с Kafka
5. **API:** REST с create + redirect endpoints
6. **Производительность:** <100ms latency с кешированием
7. **Масштабируемость:** Горизонтальное масштабирование с шардированием
8. **Мониторинг:** Метрики, логирование, distributed tracing

## Follow-ups

1. How do you prevent malicious URLs or spam?
2. What happens if the same long URL is submitted multiple times?
3. How do you handle URL expiration and cleanup?
4. What's the difference between 301 and 302 redirects?
5. How do you implement custom domain support (e.g., custom.ly/abc)?
6. How do you handle peak traffic (e.g., viral links)?
7. What security measures prevent short code enumeration?
8. How do you implement geographic routing for lower latency?
9. How do you backup and recover URL mappings?
10. How do you handle duplicate custom aliases across users?

---

## Related Questions

### Related (Medium)
- [[q-sql-nosql-databases--system-design--medium]] - sql nosql databases   system
- [[q-caching-strategies--system-design--medium]] - caching strategies   system design 
- [[q-load-balancing-strategies--system-design--medium]] - load balancing strategies   system
- [[q-horizontal-vertical-scaling--system-design--medium]] - horizontal vertical scaling   system

### Advanced (Harder)
- [[q-microservices-vs-monolith--system-design--hard]] - microservices vs monolith   system
- [[q-database-sharding-partitioning--system-design--hard]] - database sharding partitioning   system
### Related (Medium)
- [[q-sql-nosql-databases--system-design--medium]] - sql nosql databases   system
- [[q-caching-strategies--system-design--medium]] - caching strategies   system design 
- [[q-load-balancing-strategies--system-design--medium]] - load balancing strategies   system
- [[q-horizontal-vertical-scaling--system-design--medium]] - horizontal vertical scaling   system

### Advanced (Harder)
- [[q-microservices-vs-monolith--system-design--hard]] - microservices vs monolith   system
- [[q-database-sharding-partitioning--system-design--hard]] - database sharding partitioning   system
### Related (Medium)
- [[q-sql-nosql-databases--system-design--medium]] - sql nosql databases   system
- [[q-caching-strategies--system-design--medium]] - caching strategies   system design 
- [[q-load-balancing-strategies--system-design--medium]] - load balancing strategies   system
- [[q-horizontal-vertical-scaling--system-design--medium]] - horizontal vertical scaling   system

### Advanced (Harder)
- [[q-microservices-vs-monolith--system-design--hard]] - microservices vs monolith   system
- [[q-database-sharding-partitioning--system-design--hard]] - database sharding partitioning   system
