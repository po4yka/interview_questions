---
id: sysdes-078
title: Design Reddit
aliases:
- Reddit Design
- Discussion Platform
- Forum Design
topic: system-design
subtopics:
- social-media
- ranking
- real-time
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-design-twitter--system-design--hard
- q-caching-strategies--system-design--medium
- q-pubsub-patterns--system-design--medium
created: 2025-01-26
updated: 2025-01-26
tags:
- system-design
- difficulty/medium
- social-media
- ranking
---
# Question (EN)
> How would you design a discussion platform like Reddit?

# Vopros (RU)
> Как бы вы спроектировали дискуссионную платформу, подобную Reddit?

---

## Answer (EN)

### Requirements

**Functional:**
- Create and manage subreddits (communities)
- Post text, links, images, videos
- Comment on posts (threaded/nested)
- Upvote/downvote posts and comments
- Subscribe to subreddits
- View feeds: Home, Popular, All
- Search posts, comments, subreddits
- User profiles and karma

**Non-Functional:**
- 500M monthly active users, 50M DAU
- 100K posts/day, 1M comments/day
- Read-heavy (100:1 read/write ratio)
- Feed load < 200ms
- Real-time vote updates
- High availability (99.9%)

### Capacity Estimation

```
Posts: 100K/day = 1.2 posts/sec
Comments: 1M/day = 12 comments/sec
Votes: 100M/day = 1,157 votes/sec
Reads: 50M DAU * 50 page views = 2.5B reads/day = 29K reads/sec
Storage: 100K posts * 10KB = 1GB/day (text only)
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
   │  Post   │           │   Feed    │          │  Vote     │
   │ Service │           │  Service  │          │  Service  │
   └────┬────┘           └─────┬─────┘          └─────┬─────┘
        │                      │                      │
        │    ┌─────────────────┼─────────────────┐    │
        │    │                 │                 │    │
   ┌────▼────▼───┐       ┌─────▼─────┐     ┌─────▼────▼───┐
   │   Posts DB  │       │   Feed    │     │   Vote       │
   │  (Sharded)  │       │   Cache   │     │   Cache      │
   └─────────────┘       └───────────┘     └──────────────┘
```

### Core Components

**1. Post Service**
- Create, edit, delete posts
- Store post metadata and content
- Sharded by subreddit_id or post_id

**2. Comment Service**
- Threaded comment storage
- Materialized path or adjacency list for tree structure
- Support for comment expansion

**3. Vote Service**
- Handle upvotes/downvotes
- Prevent vote manipulation (rate limiting, bot detection)
- Update karma asynchronously

**4. Feed Service**
- Generate personalized home feed
- Hot, New, Top, Controversial rankings
- Pre-compute popular feeds

**5. Subreddit Service**
- Community management
- Moderation tools
- Subscription management

### Post Ranking Algorithms

**Hot Algorithm (Time-Decay)**
```python
def hot_score(upvotes, downvotes, created_at):
    score = upvotes - downvotes
    order = log10(max(abs(score), 1))

    if score > 0:
        sign = 1
    elif score < 0:
        sign = -1
    else:
        sign = 0

    seconds = created_at - EPOCH  # Reddit epoch: Dec 8, 2005
    return round(sign * order + seconds / 45000, 7)
```

**Top Algorithm**
```
top_score = upvotes - downvotes
# Filtered by time period (hour, day, week, month, year, all)
```

**Controversial Algorithm**
```python
def controversial_score(upvotes, downvotes):
    if upvotes <= 0 or downvotes <= 0:
        return 0
    magnitude = upvotes + downvotes
    balance = min(upvotes, downvotes) / max(upvotes, downvotes)
    return magnitude * balance
```

**New Algorithm**
```
Simply sorted by created_at timestamp
```

### Comment Threading

**Materialized Path Approach**
```sql
comments (
    comment_id: bigint PRIMARY KEY,
    post_id: bigint,
    user_id: bigint,
    parent_id: bigint,
    path: varchar(500),    -- e.g., "001.002.001"
    depth: int,
    content: text,
    upvotes: int,
    downvotes: int,
    created_at: timestamp,
    INDEX (post_id, path),
    INDEX (post_id, created_at)
)

-- Fetch comment tree
SELECT * FROM comments
WHERE post_id = ?
ORDER BY path
LIMIT 200;
```

**Nested Set Alternative**
```
Pros: Fast subtree queries
Cons: Expensive inserts (must renumber)
Use when: Read-heavy comment sections
```

### Data Models

**Post**
```sql
posts (
    post_id: bigint PRIMARY KEY,  -- Snowflake ID
    subreddit_id: bigint,
    user_id: bigint,
    title: varchar(300),
    content: text,
    url: varchar(500),
    post_type: enum(text, link, image, video),
    upvotes: int DEFAULT 0,
    downvotes: int DEFAULT 0,
    comment_count: int DEFAULT 0,
    created_at: timestamp,
    is_deleted: boolean DEFAULT FALSE,
    INDEX (subreddit_id, created_at),
    INDEX (subreddit_id, hot_score)
)
```

**Subreddit**
```sql
subreddits (
    subreddit_id: bigint PRIMARY KEY,
    name: varchar(21),  -- r/name, max 21 chars
    description: text,
    rules: json,
    subscriber_count: int,
    created_at: timestamp,
    is_nsfw: boolean,
    UNIQUE (name)
)
```

**Vote (Sparse)**
```sql
votes (
    user_id: bigint,
    entity_id: bigint,  -- post_id or comment_id
    entity_type: enum(post, comment),
    vote_type: int,     -- 1 or -1
    created_at: timestamp,
    PRIMARY KEY (user_id, entity_id, entity_type)
)
```

### Voting System

**Anti-Manipulation Measures**
- Rate limiting per user
- Account age requirements
- IP-based detection
- Shadow banning (votes don't count)
- Fuzzing displayed vote counts

**Vote Processing Flow**
```
1. User votes → Vote Service
2. Check rate limits and account status
3. Store vote in DB (idempotent)
4. Publish vote event to Kafka
5. Vote Aggregator consumes events:
   a. Update post/comment vote count
   b. Update user karma
   c. Recalculate ranking scores
6. Invalidate cached feeds
```

### Feed Generation

**Home Feed (Personalized)**
```
1. Get user's subscribed subreddits
2. For each subreddit, fetch top N posts by hot_score
3. Merge and re-rank globally
4. Cache result with short TTL (1-5 min)
```

**Popular/All Feed (Global)**
```
Pre-computed every minute:
1. Aggregate posts across all subreddits
2. Rank by hot_score
3. Store in Redis sorted set
4. Serve directly from cache
```

**Feed Cache (Redis)**
```
Key: feed:{user_id}:home OR feed:popular
Value: Sorted Set of (post_id, score)

ZREVRANGE feed:123:home 0 24 WITHSCORES
```

### Search Architecture

```
                  ┌─────────────────┐
                  │  Search Service │
                  └────────┬────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐       ┌─────▼─────┐      ┌─────▼─────┐
   │ Posts   │       │ Comments  │      │Subreddits │
   │  Index  │       │   Index   │      │   Index   │
   └─────────┘       └───────────┘      └───────────┘
   (Elasticsearch)

Search features:
- Full-text search with relevance ranking
- Filters: subreddit, time range, author
- Autocomplete for subreddit names
- Typeahead for users
```

### Real-Time Updates

**WebSocket for Live Updates**
```
1. Client subscribes to post_id
2. Server maintains WebSocket connection
3. On new vote/comment:
   a. Publish to Redis Pub/Sub channel
   b. Server broadcasts to subscribed clients
4. Client updates UI (vote count, new comments)
```

**Scaling WebSockets**
```
- Sticky sessions by user_id
- Redis Pub/Sub for cross-server messaging
- Connection pooling per subreddit/post
```

### Caching Strategies

| Data | Cache | TTL | Strategy |
|------|-------|-----|----------|
| Popular feed | Redis | 1 min | Write-through |
| Home feed | Redis | 5 min | Cache-aside |
| Post content | Redis | 1 hour | Cache-aside |
| Vote counts | Redis | Real-time | Write-through |
| Comment trees | Redis | 10 min | Cache-aside |
| User profiles | Redis | 30 min | Cache-aside |

### Scaling Strategies

| Component | Strategy |
|-----------|----------|
| Posts DB | Shard by subreddit_id (co-locate subreddit content) |
| Comments DB | Shard by post_id |
| Votes DB | Shard by entity_id |
| Feed cache | Shard by user_id (Redis Cluster) |
| Search | Elasticsearch cluster with replicas |
| Media | S3 + CDN |

### Moderation System

```
Moderation features:
- AutoModerator (rules-based)
- Spam detection (ML-based)
- Report queue for human review
- Mod actions: remove, lock, sticky, flair
- Mod logs for transparency
```

---

## Otvet (RU)

### Требования

**Функциональные:**
- Создание и управление сабреддитами (сообществами)
- Публикация текста, ссылок, изображений, видео
- Комментирование постов (древовидная структура)
- Голосование за/против постов и комментариев
- Подписка на сабреддиты
- Просмотр лент: Home, Popular, All
- Поиск постов, комментариев, сабреддитов
- Профили пользователей и карма

**Нефункциональные:**
- 500M MAU, 50M DAU
- 100K постов/день, 1M комментариев/день
- Read-heavy (соотношение чтение/запись 100:1)
- Загрузка ленты < 200мс
- Real-time обновление голосов
- Высокая доступность (99.9%)

### Оценка мощности

```
Посты: 100K/день = 1.2 поста/сек
Комментарии: 1M/день = 12 комментариев/сек
Голоса: 100M/день = 1,157 голосов/сек
Чтения: 50M DAU * 50 просмотров = 2.5B чтений/день = 29K чтений/сек
Хранение: 100K постов * 10KB = 1GB/день (только текст)
```

### Алгоритмы ранжирования постов

**Hot Algorithm (Time-Decay)**
```python
def hot_score(upvotes, downvotes, created_at):
    score = upvotes - downvotes
    order = log10(max(abs(score), 1))

    if score > 0:
        sign = 1
    elif score < 0:
        sign = -1
    else:
        sign = 0

    seconds = created_at - EPOCH  # Reddit epoch: 8 декабря 2005
    return round(sign * order + seconds / 45000, 7)
```

**Controversial Algorithm**
```python
def controversial_score(upvotes, downvotes):
    if upvotes <= 0 or downvotes <= 0:
        return 0
    magnitude = upvotes + downvotes
    balance = min(upvotes, downvotes) / max(upvotes, downvotes)
    return magnitude * balance
```

### Древовидные комментарии

**Подход Materialized Path**
```sql
comments (
    comment_id: bigint PRIMARY KEY,
    post_id: bigint,
    user_id: bigint,
    parent_id: bigint,
    path: varchar(500),    -- например, "001.002.001"
    depth: int,
    content: text,
    upvotes: int,
    downvotes: int,
    created_at: timestamp,
    INDEX (post_id, path)
)

-- Получить дерево комментариев
SELECT * FROM comments
WHERE post_id = ?
ORDER BY path
LIMIT 200;
```

### Модели данных

**Post**
```sql
posts (
    post_id: bigint PRIMARY KEY,  -- Snowflake ID
    subreddit_id: bigint,
    user_id: bigint,
    title: varchar(300),
    content: text,
    url: varchar(500),
    post_type: enum(text, link, image, video),
    upvotes: int DEFAULT 0,
    downvotes: int DEFAULT 0,
    comment_count: int DEFAULT 0,
    created_at: timestamp,
    INDEX (subreddit_id, created_at),
    INDEX (subreddit_id, hot_score)
)
```

**Subreddit**
```sql
subreddits (
    subreddit_id: bigint PRIMARY KEY,
    name: varchar(21),  -- r/name, макс 21 символ
    description: text,
    rules: json,
    subscriber_count: int,
    created_at: timestamp,
    is_nsfw: boolean,
    UNIQUE (name)
)
```

### Система голосования

**Меры против манипуляции**
- Rate limiting на пользователя
- Требования к возрасту аккаунта
- Детекция по IP
- Shadow banning (голоса не учитываются)
- Fuzzing отображаемых счетчиков

**Поток обработки голосов**
```
1. Пользователь голосует → Vote Service
2. Проверка rate limits и статуса аккаунта
3. Сохранение голоса в БД (идемпотентно)
4. Публикация события в Kafka
5. Vote Aggregator обрабатывает события:
   a. Обновление счетчика голосов
   b. Обновление кармы пользователя
   c. Пересчет рейтинговых score
6. Инвалидация закешированных лент
```

### Генерация ленты

**Home Feed (персонализированная)**
```
1. Получить подписки пользователя
2. Для каждого сабреддита получить топ N постов по hot_score
3. Смержить и переранжировать глобально
4. Закешировать с коротким TTL (1-5 мин)
```

**Popular/All Feed (глобальная)**
```
Предвычисляется каждую минуту:
1. Агрегация постов со всех сабреддитов
2. Ранжирование по hot_score
3. Хранение в Redis sorted set
4. Раздача напрямую из кеша
```

### Real-Time обновления

**WebSocket для live-обновлений**
```
1. Клиент подписывается на post_id
2. Сервер поддерживает WebSocket соединение
3. При новом голосе/комментарии:
   a. Публикация в Redis Pub/Sub канал
   b. Сервер бродкастит подписанным клиентам
4. Клиент обновляет UI
```

### Стратегии кеширования

| Данные | Кеш | TTL | Стратегия |
|--------|-----|-----|-----------|
| Popular feed | Redis | 1 мин | Write-through |
| Home feed | Redis | 5 мин | Cache-aside |
| Контент постов | Redis | 1 час | Cache-aside |
| Счетчики голосов | Redis | Real-time | Write-through |
| Деревья комментариев | Redis | 10 мин | Cache-aside |

### Стратегии масштабирования

| Компонент | Стратегия |
|-----------|-----------|
| Posts DB | Шардирование по subreddit_id |
| Comments DB | Шардирование по post_id |
| Votes DB | Шардирование по entity_id |
| Feed cache | Шардирование по user_id (Redis Cluster) |
| Search | Elasticsearch кластер с репликами |
| Media | S3 + CDN |

### Система модерации

```
Функции модерации:
- AutoModerator (на основе правил)
- Детекция спама (на основе ML)
- Очередь репортов для ревью
- Действия модераторов: удаление, блокировка, закрепление
- Логи модерации для прозрачности
```

---

## Follow-ups

- How do you implement cross-posting between subreddits?
- How do you handle subreddit bans and quarantines?
- How do you implement awards/gilding system?
- How do you detect and handle brigading?

## Related Questions

### Prerequisites (Easier)
- [[q-caching-strategies--system-design--medium]] - Caching strategies
- [[q-pubsub-patterns--system-design--medium]] - Pub/Sub patterns

### Related (Same Level)
- [[q-design-twitter--system-design--hard]] - Twitter (similar feed generation)
- [[q-elasticsearch-full-text-search--system-design--medium]] - Search

### Advanced (Harder)
- [[q-database-sharding-partitioning--system-design--hard]] - Sharding details
- [[q-websockets-sse-long-polling--system-design--medium]] - Real-time communication
