---
id: sysdes-028
title: Design Twitter
aliases:
- Twitter Design
- Social Media Feed
- Timeline Design
topic: system-design
subtopics:
- social-media
- feed
- scalability
question_kind: system-design
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-design-instagram--system-design--hard
- q-caching-strategies--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- system-design
- difficulty/hard
- social-media
- scalability
anki_cards:
- slug: sysdes-028-0-en
  language: en
  anki_id: 1769158889191
  synced_at: '2026-01-23T13:29:45.875461'
- slug: sysdes-028-0-ru
  language: ru
  anki_id: 1769158889216
  synced_at: '2026-01-23T13:29:45.876878'
---
# Question (EN)
> Design Twitter. Focus on the timeline/feed generation, posting tweets, and following users.

# Vopros (RU)
> Спроектируйте Twitter. Сфокусируйтесь на генерации ленты/timeline, постинге твитов и подписках.

---

## Answer (EN)

### Requirements

**Functional:**
- Post tweets (280 chars, media)
- Follow/unfollow users
- View home timeline (tweets from followed users)
- View user timeline (user's own tweets)
- Like, retweet, reply

**Non-Functional:**
- 500M users, 200M DAU
- 500M tweets/day
- Read-heavy (100:1 read/write ratio)
- Timeline load < 200ms
- High availability

### Capacity Estimation

```
Tweets: 500M/day = 6000 tweets/sec
Reads: 200M users * 10 timeline loads = 2B reads/day = 23K reads/sec
Storage: 500M tweets * 300 bytes = 150GB/day
```

### High-Level Architecture

```
                        ┌─────────────────┐
                        │   Load Balancer │
                        └────────┬────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
        ┌─────▼─────┐     ┌──────▼──────┐    ┌─────▼─────┐
        │ Tweet     │     │  Timeline   │    │  User     │
        │ Service   │     │  Service    │    │  Service  │
        └─────┬─────┘     └──────┬──────┘    └─────┬─────┘
              │                  │                  │
              └──────────────────┼──────────────────┘
                                 │
        ┌──────────────┬─────────┴─────────┬──────────────┐
        │              │                   │              │
   ┌────▼────┐   ┌─────▼─────┐      ┌──────▼──────┐  ┌────▼────┐
   │ Tweets  │   │ Timeline  │      │   Social    │  │  User   │
   │   DB    │   │   Cache   │      │   Graph     │  │  Cache  │
   └─────────┘   └───────────┘      └─────────────┘  └─────────┘
```

### Core Components

**1. Tweet Service**
- Store and retrieve tweets
- Sharded by tweet_id or user_id
- Write-through to cache

**2. Timeline Service**
- Generate and serve home timeline
- Two approaches: Push vs Pull

**3. Social Graph Service**
- Manage follow relationships
- Query followers/following

### Fan-Out Approaches

**Pull Model (Fan-out on Read)**
```
User opens app → Query all followed users → Merge tweets → Sort → Display

Pros: Simple writes, good for celebrities
Cons: Slow reads, high read latency
```

**Push Model (Fan-out on Write)**
```
User posts tweet → Push to all followers' timelines (pre-computed)
User opens app → Read pre-computed timeline

Pros: Fast reads
Cons: High write amplification for celebrities
```

**Hybrid Approach (Twitter's Actual Design)**
```
Regular users: Push model (fan-out on write)
Celebrities (>10K followers): Pull model (fan-out on read)

When loading timeline:
1. Fetch pre-computed timeline from cache
2. Merge with celebrity tweets (pulled on demand)
3. Return merged result
```

### Data Models

**Tweet**
```sql
tweets (
    tweet_id: bigint PRIMARY KEY,  -- Snowflake ID
    user_id: bigint,
    content: varchar(280),
    media_urls: json,
    created_at: timestamp,
    reply_to: bigint,
    retweet_of: bigint
)
```

**User Timeline (Redis)**
```
Key: timeline:{user_id}
Value: Sorted Set of (tweet_id, timestamp)

# Get latest 20 tweets
ZREVRANGE timeline:123 0 19
```

**Social Graph (Adjacency List)**
```sql
follows (
    follower_id: bigint,
    followee_id: bigint,
    created_at: timestamp,
    PRIMARY KEY (follower_id, followee_id)
)
```

### Posting a Tweet Flow

```
1. Client → API Gateway → Tweet Service
2. Store tweet in DB (sharded by user_id)
3. If followers < 10K:
   a. Fetch follower list
   b. Push tweet_id to each follower's timeline cache
4. Return success

For celebrities:
- Skip fan-out, tweet pulled on read
```

### Loading Home Timeline Flow

```
1. Client requests timeline
2. Fetch pre-computed timeline from Redis
3. Fetch celebrity list user follows
4. Pull recent tweets from celebrities
5. Merge and sort
6. Return top N tweets
7. Fetch tweet content (parallel) using tweet_ids
```

### Scaling Strategies

| Component | Strategy |
|-----------|----------|
| Tweet DB | Shard by user_id (co-locate user's tweets) |
| Timeline Cache | Shard by user_id |
| Social Graph | Shard by follower_id |
| Media | CDN + Object storage (S3) |

---

## Otvet (RU)

### Требования

**Функциональные:**
- Постить твиты (280 символов, медиа)
- Подписка/отписка на пользователей
- Просмотр домашней ленты (твиты от подписок)
- Просмотр ленты пользователя (собственные твиты)
- Лайки, ретвиты, ответы

**Нефункциональные:**
- 500M пользователей, 200M DAU
- 500M твитов/день
- Read-heavy (соотношение чтение/запись 100:1)
- Загрузка ленты < 200мс
- Высокая доступность

### Оценка мощности

```
Твиты: 500M/день = 6000 твитов/сек
Чтения: 200M пользователей * 10 загрузок ленты = 2B чтений/день = 23K чтений/сек
Хранение: 500M твитов * 300 байт = 150GB/день
```

### Высокоуровневая архитектура

```
                        ┌─────────────────┐
                        │   Load Balancer │
                        └────────┬────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
        ┌─────▼─────┐     ┌──────▼──────┐    ┌─────▼─────┐
        │ Tweet     │     │  Timeline   │    │  User     │
        │ Service   │     │  Service    │    │  Service  │
        └─────┬─────┘     └──────┬──────┘    └─────┬─────┘
              │                  │                  │
              └──────────────────┼──────────────────┘
                                 │
        ┌──────────────┬─────────┴─────────┬──────────────┐
        │              │                   │              │
   ┌────▼────┐   ┌─────▼─────┐      ┌──────▼──────┐  ┌────▼────┐
   │ Tweets  │   │ Timeline  │      │   Social    │  │  User   │
   │   DB    │   │   Cache   │      │   Graph     │  │  Cache  │
   └─────────┘   └───────────┘      └─────────────┘  └─────────┘
```

### Подходы Fan-Out

**Pull Model (Fan-out on Read)**
```
Пользователь открывает приложение → Запрос всех подписок → Merge твитов → Сортировка → Отображение

Плюсы: Простые записи, хорошо для знаменитостей
Минусы: Медленное чтение, высокая задержка
```

**Push Model (Fan-out on Write)**
```
Пользователь постит твит → Push в ленты всех подписчиков (предвычислено)
Пользователь открывает приложение → Чтение предвычисленной ленты

Плюсы: Быстрое чтение
Минусы: Высокое write amplification для знаменитостей
```

**Гибридный подход (реальный дизайн Twitter)**
```
Обычные пользователи: Push model (fan-out on write)
Знаменитости (>10K подписчиков): Pull model (fan-out on read)

При загрузке ленты:
1. Получить предвычисленную ленту из кеша
2. Смержить с твитами знаменитостей (pulled on demand)
3. Вернуть объединенный результат
```

### Модели данных

**Tweet**
```sql
tweets (
    tweet_id: bigint PRIMARY KEY,  -- Snowflake ID
    user_id: bigint,
    content: varchar(280),
    media_urls: json,
    created_at: timestamp,
    reply_to: bigint,
    retweet_of: bigint
)
```

**User Timeline (Redis)**
```
Key: timeline:{user_id}
Value: Sorted Set из (tweet_id, timestamp)

# Получить последние 20 твитов
ZREVRANGE timeline:123 0 19
```

### Стратегии масштабирования

| Компонент | Стратегия |
|-----------|-----------|
| Tweet DB | Шардирование по user_id |
| Timeline Cache | Шардирование по user_id |
| Social Graph | Шардирование по follower_id |
| Media | CDN + Object storage (S3) |

---

## Follow-ups

- How do you handle trending topics?
- How do you implement search?
- How do you handle spam and abuse?

## Related Questions

### Prerequisites (Easier)
- [[q-caching-strategies--system-design--medium]] - Caching
- [[q-pubsub-patterns--system-design--medium]] - Pub/Sub

### Related (Same Level)
- [[q-design-instagram--system-design--hard]] - Instagram
- [[q-design-notification-system--system-design--hard]] - Notifications

### Advanced (Harder)
- [[q-database-sharding-partitioning--system-design--hard]] - Sharding details
