---
id: sysdes-029
title: Design Instagram
aliases:
- Instagram Design
- Photo Sharing
- Feed Design
topic: system-design
subtopics:
- social-media
- media-storage
- feed
question_kind: system-design
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-design-twitter--system-design--hard
- q-cdn-content-delivery-network--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- system-design
- difficulty/hard
- social-media
- media-storage
anki_cards:
- slug: sysdes-029-0-en
  language: en
  anki_id: 1769158888941
  synced_at: '2026-01-23T13:29:45.869076'
- slug: sysdes-029-0-ru
  language: ru
  anki_id: 1769158888965
  synced_at: '2026-01-23T13:29:45.870808'
---
# Question (EN)
> Design Instagram. Focus on uploading photos, generating the news feed, and following users.

# Vopros (RU)
> Спроектируйте Instagram. Сфокусируйтесь на загрузке фото, генерации ленты новостей и подписках.

---

## Answer (EN)

### Requirements

**Functional:**
- Upload photos/videos with captions
- Follow/unfollow users
- View news feed (posts from followed users)
- Like and comment on posts
- View user profiles
- Stories (24h ephemeral content)

**Non-Functional:**
- 1B users, 500M DAU
- 100M photos uploaded/day
- Low latency feed generation (<200ms)
- High availability (99.9%)
- Global scale with CDN

### Capacity Estimation

```
Photo uploads: 100M/day = 1,157/sec
Average photo size: 2MB
Storage/day: 100M * 2MB = 200TB/day
Storage/year: 73PB

Feed reads: 500M DAU * 20 reads = 10B reads/day = 115K reads/sec
```

### High-Level Architecture

```
                     ┌─────────────────┐
                     │   Load Balancer │
                     └────────┬────────┘
                              │
       ┌──────────────────────┼──────────────────────┐
       │                      │                      │
  ┌────▼────┐           ┌─────▼─────┐          ┌─────▼─────┐
  │ Upload  │           │   Feed    │          │   User    │
  │ Service │           │  Service  │          │  Service  │
  └────┬────┘           └─────┬─────┘          └─────┬─────┘
       │                      │                      │
       │    ┌─────────────────┼─────────────────┐    │
       │    │                 │                 │    │
  ┌────▼────▼───┐       ┌─────▼─────┐     ┌─────▼────▼───┐
  │ Object      │       │  Feed     │     │   Posts DB   │
  │ Storage(S3) │       │  Cache    │     │  (Sharded)   │
  └──────┬──────┘       └───────────┘     └──────────────┘
         │
    ┌────▼────┐
    │   CDN   │
    └─────────┘
```

### Core Components

**1. Upload Service**
- Handle image/video uploads
- Generate thumbnails (multiple sizes)
- Store metadata in DB
- Store media in object storage

**2. Feed Service**
- Generate news feed
- Hybrid push/pull approach
- Cache pre-generated feeds

**3. User Service**
- User profiles
- Follow relationships
- Authentication

### Photo Upload Flow

```
1. Client → API Gateway (auth check)
2. Get pre-signed URL from Upload Service
3. Client uploads directly to S3 (bypass app servers)
4. S3 triggers Lambda/notification
5. Image processing pipeline:
   - Resize to multiple dimensions
   - Generate thumbnails
   - Apply filters (optional)
   - Store in S3
6. Update metadata DB
7. Trigger feed fanout (for followers)
8. Return success with CDN URLs
```

### Feed Generation (Hybrid Approach)

```
Regular users (< 10K followers): Push on write
  - When posting, push post_id to all followers' feeds

Celebrities (> 10K followers): Pull on read
  - Don't push, fetch on demand

Feed loading:
1. Get pre-computed feed from cache
2. Fetch recent celebrity posts (users follows)
3. Merge, rank, return
```

### Data Models

**Post**
```sql
posts (
    post_id: bigint PRIMARY KEY,  -- Snowflake ID
    user_id: bigint,
    caption: text,
    media_type: enum(photo, video, carousel),
    created_at: timestamp,
    location: point,
    INDEX (user_id, created_at)
)
```

**Post Media**
```sql
post_media (
    media_id: bigint PRIMARY KEY,
    post_id: bigint,
    media_url: varchar(500),
    thumbnail_url: varchar(500),
    width: int,
    height: int,
    order: int
)
```

**Feed Cache (Redis)**
```
Key: feed:{user_id}
Value: Sorted Set of (post_id, score/timestamp)

ZREVRANGE feed:123 0 19 WITHSCORES
```

### Media Storage Strategy

```
Original uploads: S3 Standard
Thumbnails: S3 (frequently accessed)
Old media (>1 year): S3 Glacier

Serving:
- CDN (CloudFront) caches at edge
- Multiple resolutions (150px, 320px, 640px, 1080px)
- WebP format for modern browsers
```

### Ranking Algorithm (Simplified)

```python
def calculate_score(post, user):
    base_score = post.timestamp

    # Engagement signals
    engagement = (
        post.likes * 1.0 +
        post.comments * 2.0 +
        post.shares * 3.0
    )

    # Relationship signals
    relationship = get_interaction_score(user, post.author)

    # Recency decay
    age_hours = (now - post.timestamp).hours
    recency = 1 / (1 + age_hours * 0.1)

    return base_score + engagement * relationship * recency
```

### Scaling Strategies

| Component | Strategy |
|-----------|----------|
| Posts DB | Shard by user_id |
| Media | S3 + CDN (geo-distributed) |
| Feed cache | Shard by user_id (Redis Cluster) |
| Social graph | Shard by user_id |
| Upload | Pre-signed URLs (bypass app servers) |

---

## Otvet (RU)

### Требования

**Функциональные:**
- Загрузка фото/видео с подписями
- Подписка/отписка на пользователей
- Просмотр ленты новостей (посты от подписок)
- Лайки и комментарии к постам
- Просмотр профилей
- Stories (24ч эфемерный контент)

**Нефункциональные:**
- 1B пользователей, 500M DAU
- 100M фото загружается/день
- Низкая задержка генерации ленты (<200мс)
- Высокая доступность (99.9%)
- Глобальный масштаб с CDN

### Оценка мощности

```
Загрузки фото: 100M/день = 1,157/сек
Средний размер фото: 2MB
Хранение/день: 100M * 2MB = 200TB/день
Хранение/год: 73PB

Чтения ленты: 500M DAU * 20 чтений = 10B чтений/день = 115K чтений/сек
```

### Поток загрузки фото

```
1. Клиент → API Gateway (проверка auth)
2. Получить pre-signed URL от Upload Service
3. Клиент загружает напрямую в S3 (обход app серверов)
4. S3 триггерит Lambda/уведомление
5. Pipeline обработки изображения:
   - Ресайз в несколько размеров
   - Генерация превью
   - Применение фильтров (опционально)
   - Сохранение в S3
6. Обновление metadata DB
7. Триггер feed fanout (для подписчиков)
8. Возврат успеха с CDN URLs
```

### Генерация ленты (гибридный подход)

```
Обычные пользователи (< 10K подписчиков): Push on write
  - При постинге push post_id во все ленты подписчиков

Знаменитости (> 10K подписчиков): Pull on read
  - Не push'ить, получать on demand

Загрузка ленты:
1. Получить предвычисленную ленту из кеша
2. Получить недавние посты знаменитостей (на которых подписан)
3. Смержить, ранжировать, вернуть
```

### Стратегия хранения медиа

```
Оригинальные загрузки: S3 Standard
Превью: S3 (часто доступаемые)
Старые медиа (>1 года): S3 Glacier

Раздача:
- CDN (CloudFront) кеширует на edge
- Несколько разрешений (150px, 320px, 640px, 1080px)
- WebP формат для современных браузеров
```

### Стратегии масштабирования

| Компонент | Стратегия |
|-----------|-----------|
| Posts DB | Шардирование по user_id |
| Media | S3 + CDN (гео-распределенный) |
| Feed cache | Шардирование по user_id (Redis Cluster) |
| Social graph | Шардирование по user_id |
| Upload | Pre-signed URLs (обход app серверов) |

---

## Follow-ups

- How do you implement Stories (ephemeral content)?
- How do you handle video uploads and streaming?
- How do you implement explore/discover feature?

## Related Questions

### Prerequisites (Easier)
- [[q-cdn-content-delivery-network--system-design--medium]] - CDN
- [[q-caching-strategies--system-design--medium]] - Caching

### Related (Same Level)
- [[q-design-twitter--system-design--hard]] - Twitter
- [[q-design-notification-system--system-design--hard]] - Notifications

### Advanced (Harder)
- [[q-database-sharding-partitioning--system-design--hard]] - Sharding
