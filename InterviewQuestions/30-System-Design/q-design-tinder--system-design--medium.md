---
id: sysdes-078
title: Design Tinder
aliases:
- Design Tinder
- Dating App System
- Swipe-Based Matching
topic: system-design
subtopics:
- design-problems
- matching
- geospatial
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
- q-design-uber--system-design--hard
- q-geospatial-indexing--system-design--medium
- q-websockets-sse-long-polling--system-design--medium
- q-design-notification-system--system-design--hard
created: 2025-01-26
updated: 2025-01-26
tags:
- design-problems
- difficulty/medium
- matching
- geospatial
- system-design
---
# Question (EN)
> How would you design a dating app like Tinder?

# Vopros (RU)
> Как бы вы спроектировали приложение для знакомств, подобное Tinder?

---

## Answer (EN)

### Requirements

**Functional**: User profiles, photo upload, swipe left/right, mutual match detection, chat after match, location-based discovery, filters (age, distance, preferences)
**Non-functional**: Low latency swipes (<100ms), real-time match notifications, horizontal scalability for millions of daily active users

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Mobile Apps                           │
│                   (iOS / Android / Web)                     │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      API Gateway                            │
│           (Auth, Rate Limiting, Load Balancing)             │
└────┬──────────┬──────────┬──────────┬──────────┬────────────┘
     │          │          │          │          │
┌────▼────┐┌────▼────┐┌────▼────┐┌────▼────┐┌────▼────┐
│ Profile ││  Swipe  ││  Match  ││  Chat   ││  Feed   │
│ Service ││ Service ││ Service ││ Service ││ Service │
└────┬────┘└────┬────┘└────┬────┘└────┬────┘└────┬────┘
     │          │          │          │          │
┌────▼──────────▼──────────▼──────────▼──────────▼────────────┐
│                     Data Layer                              │
│  PostgreSQL │ Redis │ Elasticsearch │ S3 │ Kafka            │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. Profile Service
```
Responsibilities:
- User registration and authentication
- Profile CRUD (bio, preferences, settings)
- Photo management (upload, moderation, ordering)

Storage:
- PostgreSQL: user profiles, preferences
- S3/CDN: photos with multiple resolutions
- Elasticsearch: profile search with filters

Photo Pipeline:
  Upload → Virus scan → NSFW detection →
  Resize (thumb, medium, full) → CDN distribution
```

#### 2. Geospatial Discovery
```
Location-based matching:
- Store user location in geospatial index
- Query nearby users within configured radius

Redis Geospatial:
  GEOADD users:active longitude latitude user_id
  GEORADIUS users:active lng lat 50 km COUNT 1000

Alternative: PostGIS, Elasticsearch geo_distance

Location Update Strategy:
- Update on app open
- Background updates every 15-30 min
- Significant location change (>1km)
```

#### 3. Recommendation Engine
```
Feed Generation Algorithm:
1. Get nearby users (geospatial query)
2. Filter by preferences:
   - Age range
   - Gender
   - Distance limit
3. Exclude:
   - Already swiped
   - Blocked users
   - Inactive accounts (>7 days)
4. Rank candidates:
   - Profile completeness score
   - Activity level
   - Photo quality (ML score)
   - Mutual interests
5. Apply exploration vs exploitation balance

Caching Strategy:
- Pre-compute daily feed batch (~500 profiles)
- Store in Redis sorted set
- Refresh when exhausted or location changes
```

#### 4. Swipe Mechanism
```
Swipe Flow:
  User A swipes right on User B
       │
       ▼
  ┌─────────────────┐
  │ Record decision │ (Kafka → swipes table)
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐     No
  │ Did B swipe on A?│────────► Done
  └────────┬────────┘
           │ Yes
           ▼
  ┌─────────────────┐
  │  CREATE MATCH!  │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │ Notify both via │
  │   Push + WS     │
  └─────────────────┘

Storage:
  swipes(user_id, target_id, action, timestamp)
  - Partition by user_id for fast lookups
  - TTL: 30 days for "left" swipes
```

#### 5. Match Detection
```
Two approaches:

A) Synchronous (simple):
   On swipe: SELECT * FROM swipes
             WHERE user_id = target AND target_id = me AND action = 'right'

B) Async with Bloom Filter (scalable):
   - Bloom filter per user with right-swiped IDs
   - Check bloom filter first (fast negative)
   - Confirm with DB on positive
   - Update both bloom filters on match

Match Storage:
  matches(user_a, user_b, matched_at, status)
  - Both user IDs stored (A < B for dedup)
  - Status: active, unmatched, blocked
```

#### 6. Chat System
```
Post-Match Messaging:
- WebSocket for real-time delivery
- Message queue (Kafka) for persistence
- Read receipts, typing indicators

Schema:
  conversations(match_id, last_message_at)
  messages(conversation_id, sender_id, content, sent_at, read_at)

Features:
- Text, GIFs, voice messages
- Photo sharing (with moderation)
- Video calls (WebRTC integration)
- Message reactions
```

### Key Technical Challenges

| Challenge | Solution |
|-----------|----------|
| Swipe volume (billions/day) | Kafka for async processing, batch writes |
| Real-time match notification | WebSocket + push notifications fallback |
| Photo storage at scale | S3 + CloudFront CDN, lazy loading |
| Feed freshness | Incremental updates, location-triggered refresh |
| Abuse prevention | Rate limiting swipes, report system, ML detection |
| Gender imbalance | Boost new users, limit daily swipes |

### Anti-Abuse & Safety

```
Moderation Pipeline:
1. Automated:
   - NSFW image detection (ML)
   - Spam text detection
   - Fake profile detection (reverse image search)

2. User Reports:
   - Harassment, fake profile, underage
   - Priority queue for manual review

3. Shadowbanning:
   - Hidden from others' feeds
   - No notification to violator

Safety Features:
- Photo verification (selfie match)
- Video chat before meeting
- Share location with friends
- Panic button / emergency services
```

### Scale Numbers

```
Tinder scale (approximate):
- 75M+ monthly active users
- 2B+ swipes per day
- 1.5M+ matches per day
- 50M+ messages per day
- Peak: 100K+ concurrent users per region

Infrastructure:
- Multi-region deployment
- CDN for 10B+ image requests/day
- <100ms p99 swipe latency
```

---

## Otvet (RU)

### Требования

**Функциональные**: Профили пользователей, загрузка фото, свайпы влево/вправо, определение взаимного матча, чат после матча, поиск по локации
**Нефункциональные**: Низкая задержка свайпов (<100мс), уведомления о матче в реальном времени, горизонтальная масштабируемость

### Ключевые компоненты

#### 1. Сервис профилей
```
Ответственность:
- Регистрация и аутентификация
- CRUD профилей (био, настройки)
- Управление фотографиями

Хранилище:
- PostgreSQL: профили, настройки
- S3/CDN: фото с разными разрешениями
- Elasticsearch: поиск с фильтрами

Пайплайн фото:
  Загрузка → Проверка на вирусы → Детекция NSFW →
  Ресайз → Раздача через CDN
```

#### 2. Геопространственный поиск
```
Матчинг по локации:
- Хранение локации в геоиндексе
- Запрос ближайших пользователей

Redis Geospatial:
  GEOADD users:active longitude latitude user_id
  GEORADIUS users:active lng lat 50 km COUNT 1000

Обновление локации:
- При открытии приложения
- Фоновое обновление каждые 15-30 мин
- При значительном изменении (>1км)
```

#### 3. Рекомендательный движок
```
Алгоритм генерации ленты:
1. Получить ближайших пользователей
2. Фильтр по настройкам:
   - Возрастной диапазон
   - Пол
   - Максимальное расстояние
3. Исключить:
   - Уже просмотренных
   - Заблокированных
   - Неактивных (>7 дней)
4. Ранжирование:
   - Полнота профиля
   - Уровень активности
   - Качество фото (ML)
   - Общие интересы
```

#### 4. Механизм свайпов
```
Поток свайпа:
  Пользователь A свайпает вправо на B
       │
       ▼
  ┌─────────────────┐
  │ Записать решение│ (Kafka → таблица свайпов)
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐     Нет
  │ B свайпал на A? │────────► Готово
  └────────┬────────┘
           │ Да
           ▼
  ┌─────────────────┐
  │  СОЗДАТЬ МАТЧ!  │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │ Уведомить обоих │
  │  Push + WS      │
  └─────────────────┘
```

#### 5. Детекция матча
```
Два подхода:

A) Синхронный (простой):
   При свайпе: SELECT * FROM swipes
               WHERE user_id = target AND target_id = me AND action = 'right'

B) Async с Bloom Filter (масштабируемый):
   - Bloom filter на пользователя с ID "правых" свайпов
   - Сначала проверка bloom filter (быстрый негатив)
   - Подтверждение в БД при позитиве
```

### Ключевые технические вызовы

| Вызов | Решение |
|-------|---------|
| Объём свайпов (миллиарды/день) | Kafka для async обработки, batch записи |
| Уведомления о матче в реальном времени | WebSocket + push уведомления |
| Хранение фото в масштабе | S3 + CloudFront CDN |
| Свежесть ленты | Инкрементальные обновления |
| Предотвращение абьюза | Rate limiting, репорты, ML детекция |

### Безопасность и модерация

```
Пайплайн модерации:
1. Автоматическая:
   - Детекция NSFW изображений (ML)
   - Детекция спама
   - Детекция фейковых профилей

2. Пользовательские жалобы:
   - Харассмент, фейк, несовершеннолетние
   - Приоритетная очередь на ручную проверку

Функции безопасности:
- Верификация фото (сравнение с селфи)
- Видеочат перед встречей
- Поделиться локацией с друзьями
```

### Масштабные числа

```
Масштаб Tinder (примерно):
- 75M+ MAU
- 2B+ свайпов в день
- 1.5M+ матчей в день
- 50M+ сообщений в день
- Пик: 100K+ конкурентных пользователей на регион
```

---

## Follow-ups

- How would you implement Tinder's "Super Like" and "Boost" features?
- How do you handle the cold start problem for new users?
- How would you design the algorithm to prevent swipe fatigue?
- What's the tradeoff between batch feed generation vs real-time?
- How do you prevent catfishing and verify user identity?
