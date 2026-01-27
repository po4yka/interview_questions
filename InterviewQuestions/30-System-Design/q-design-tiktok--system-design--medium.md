---
id: sysdes-078
title: Design TikTok
aliases:
- Design TikTok
- Short Video Platform
- Social Video App
topic: system-design
subtopics:
- design-problems
- video-streaming
- recommendation
- social-media
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-design-youtube--system-design--hard
- q-design-instagram--system-design--hard
- q-cdn-content-delivery-network--system-design--medium
created: 2025-01-26
updated: 2025-01-26
tags:
- design-problems
- difficulty/medium
- video-streaming
- recommendation
- system-design
---
# Question (EN)
> How would you design a short-video platform like TikTok?

# Vopros (RU)
> Как бы вы спроектировали платформу коротких видео, подобную TikTok?

---

## Answer (EN)

### Requirements

**Functional**: Upload short videos (15s-3min), infinite scroll feed, recommendations (For You page), likes/comments/shares, follow creators, duets/stitches, sound library, creator tools
**Non-functional**: <100ms feed load, 99.9% availability, billions of videos, millions of concurrent users, global reach

### TikTok vs YouTube Key Differences

| Aspect | TikTok | YouTube |
|--------|--------|---------|
| Video length | 15s - 10min | Minutes to hours |
| Discovery | Algorithm-first (FYP) | Search + subscribe |
| Content | Vertical, mobile-native | Horizontal, multi-device |
| Engagement | Passive (swipe) | Active (search, click) |
| Virality | Any video can go viral | Subscribers matter more |

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     Mobile Clients                           │
│              (iOS, Android - vertical video)                 │
└─────────────────────────┬────────────────────────────────────┘
                          │
┌─────────────────────────▼────────────────────────────────────┐
│                      CDN Layer                               │
│      (Video chunks, thumbnails, audio files)                │
└─────────────────────────┬────────────────────────────────────┘
                          │
┌─────────────────────────▼────────────────────────────────────┐
│                    API Gateway                               │
│         (Auth, rate limiting, routing)                      │
└────┬──────────┬──────────┬──────────┬──────────┬────────────┘
     │          │          │          │          │
┌────▼────┐ ┌───▼───┐ ┌────▼────┐ ┌───▼───┐ ┌────▼────┐
│ Upload  │ │ Feed  │ │ User    │ │Social │ │ Search  │
│ Service │ │Service│ │ Service │ │Service│ │ Service │
└────┬────┘ └───┬───┘ └────┬────┘ └───┬───┘ └────┬────┘
     │          │          │          │          │
┌────▼──────────▼──────────▼──────────▼──────────▼────────────┐
│                    Data Layer                                │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐    │
│  │  S3    │ │ Redis  │ │Postgres│ │ Kafka  │ │  ML    │    │
│  │(Video) │ │(Cache) │ │(Meta)  │ │(Events)│ │Platform│    │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘    │
└──────────────────────────────────────────────────────────────┘
```

### Video Upload & Processing Pipeline

```
1. Client uploads video (up to 10min, vertical 9:16)
   └── Chunked upload for reliability
   └── Resume capability

2. Upload Service
   └── Store raw video → S3
   └── Extract audio track
   └── Generate video ID
   └── Queue for processing

3. Transcoding Pipeline (async)
   ├── Multiple resolutions (480p, 720p, 1080p)
   ├── Optimize for mobile (H.264/H.265)
   ├── Generate thumbnails (multiple frames)
   ├── Extract audio fingerprint (copyright check)
   └── Run content moderation (ML + human review)

4. Post-Processing
   ├── Add to creator's profile
   ├── Index for search
   ├── Notify followers
   └── Begin distribution to FYP candidates
```

### For You Page (Recommendation Engine)

```
TikTok's Secret Sauce: The Algorithm

Input Signals:
┌──────────────────────────────────────────────┐
│ User Interactions                             │
│ - Watch time (most important)                │
│ - Completion rate                            │
│ - Replays, shares, likes, comments           │
│ - Follows from video                         │
│ - "Not interested" signals                   │
├──────────────────────────────────────────────┤
│ Video Metadata                               │
│ - Hashtags, captions, sounds                 │
│ - Creator info                               │
│ - Video length, effects used                 │
├──────────────────────────────────────────────┤
│ Device/Account Settings                      │
│ - Language, country                          │
│ - Device type                                │
│ - Time of day                                │
└──────────────────────────────────────────────┘

Recommendation Pipeline:
1. Candidate Generation (1M+ videos → 10K)
   └── Collaborative filtering
   └── Content-based filtering
   └── Trending/viral boost

2. Ranking Model (10K → 100)
   └── Deep learning model
   └── Predict: P(watch), P(like), P(share)
   └── Weighted score

3. Re-ranking & Diversity (100 → final feed)
   └── Remove duplicates
   └── Ensure content diversity
   └── Apply content policy filters
   └── Inject new creators (exploration)

Key Insight: TikTok prioritizes completion rate over likes
```

### Feed Generation & Delivery

```
Feed Pre-computation Strategy:

For Active Users (online):
┌─────────────────────────────────────────────┐
│ Real-time feed (low latency)                │
│ 1. Fetch pre-computed candidates (Redis)    │
│ 2. Apply real-time signals                  │
│ 3. Return batch of 10-20 videos            │
│ 4. Prefetch next batch while watching      │
└─────────────────────────────────────────────┘

For Returning Users (periodic):
┌─────────────────────────────────────────────┐
│ Batch computation (Spark/Flink)             │
│ 1. Run recommendation pipeline offline      │
│ 2. Store personalized candidates in Redis   │
│ 3. TTL: 1-4 hours                          │
└─────────────────────────────────────────────┘

Video Delivery:
1. Feed service returns video metadata + CDN URLs
2. Client prefetches next 2-3 videos
3. Adaptive bitrate based on network
4. Videos cached on device
```

### Video Encoding Strategy

```
Encoding for Mobile-First:

Format: H.264 (compatibility) + H.265 (efficiency)
Container: MP4 with fragmented streaming

Resolution Ladder:
┌───────────┬──────────┬────────────┐
│ Quality   │ Bitrate  │ Use Case   │
├───────────┼──────────┼────────────┤
│ 480p      │ 1 Mbps   │ Poor 3G    │
│ 720p      │ 2.5 Mbps │ Good 4G    │
│ 1080p     │ 5 Mbps   │ WiFi       │
└───────────┴──────────┴────────────┘

Chunk Size: 2-4 seconds (quick quality switch)
First Frame: Keyframe for instant start
```

### Real-Time Engagement

```
Like/Comment/Share Flow:

Client Action → API Gateway → Social Service
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
        ┌─────▼─────┐        ┌─────▼─────┐       ┌─────▼─────┐
        │  Update   │        │   Kafka   │       │  Update   │
        │  Counter  │        │  (Event)  │       │  User     │
        │  (Redis)  │        │           │       │  Profile  │
        └───────────┘        └─────┬─────┘       └───────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │              │              │
              ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐
              │ Analytics │  │Notification│  │ Creator   │
              │           │  │  Service   │  │ Dashboard │
              └───────────┘  └───────────┘  └───────────┘

Counter Strategy:
- Redis for real-time counts
- Batch persist to DB every N seconds
- Approximate counts for high-traffic videos
```

### Content Moderation

```
Multi-Layer Moderation:

Layer 1: Upload Time (ML)
├── Nudity/violence detection
├── Copyright audio fingerprinting
├── Text extraction + toxicity check
└── Block or flag for review

Layer 2: Before Distribution
├── Human review queue (high-risk)
├── Geographic restrictions
└── Age-gate content

Layer 3: Post-Distribution
├── User reports
├── Viral content monitoring
├── Retroactive removal

Response Time:
- Automated: <1 second
- Human review: 10min - 24 hours
- Appeals: 24-72 hours
```

### Viral Content Detection

```
Virality Signals (Real-time):

Early Indicators (first 30 min):
- High completion rate (>80%)
- Share rate > 2x average
- Comment velocity
- Cross-demographic appeal

Response:
1. Boost in recommendation pool
2. Pre-cache on more CDN edges
3. Scale encoding to more formats
4. Monitor for policy violations
```

### Creator Tools

```
Creator Features:

Recording:
- In-app camera with effects
- Green screen, filters, AR
- Speed controls (0.5x - 3x)
- Timer and countdown

Editing:
- Trim, split, merge clips
- Add text, stickers
- Voiceover
- Duet/Stitch with other videos

Sounds:
- Music library (licensed)
- Original audio extraction
- Sound trends

Analytics:
- View demographics
- Traffic sources
- Best posting times
- Follower growth
```

### Key Technical Choices

| Component | Technology | Why |
|-----------|------------|-----|
| Video Storage | S3 + CDN | Durability, global reach |
| Metadata | PostgreSQL (sharded) | Relational integrity |
| Cache | Redis Cluster | Low latency feed |
| Events | Kafka | High throughput, replay |
| ML Platform | Custom + TensorFlow | Recommendation at scale |
| Transcoding | FFmpeg + GPU clusters | Speed, quality |
| Search | Elasticsearch | Full-text + filters |

### Scale Estimates

```
1B monthly active users
100M videos uploaded/day
Average video: 30 seconds, 50MB raw

Storage: 100M * 50MB = 5PB/day raw
With transcoding: ~15PB/day

Peak concurrent users: 50M
Feed requests: 500M/hour (swipes)
Video streams: 10B/day
```

---

## Otvet (RU)

### Требования

**Функциональные**: Загрузка коротких видео (15с-3мин), бесконечная лента, рекомендации (For You), лайки/комментарии/репосты, подписки, дуэты/стичи, библиотека звуков
**Нефункциональные**: <100мс загрузка ленты, 99.9% доступность, миллиарды видео, миллионы одновременных пользователей

### Отличия TikTok от YouTube

| Аспект | TikTok | YouTube |
|--------|--------|---------|
| Длина видео | 15с - 10мин | Минуты - часы |
| Открытие | Алгоритм (FYP) | Поиск + подписки |
| Контент | Вертикальный, mobile | Горизонтальный |
| Вовлечение | Пассивное (свайп) | Активное (поиск) |
| Виральность | Любое видео | Важны подписчики |

### Конвейер загрузки и обработки видео

```
1. Клиент загружает видео (до 10мин, 9:16)
   └── Chunked upload для надёжности
   └── Возможность возобновления

2. Upload Service
   └── Сохранить raw видео → S3
   └── Извлечь аудиодорожку
   └── Поставить в очередь обработки

3. Transcoding Pipeline (async)
   ├── Множество разрешений (480p, 720p, 1080p)
   ├── Оптимизация для mobile (H.264/H.265)
   ├── Генерация превью
   ├── Fingerprint аудио (проверка копирайта)
   └── Модерация контента (ML + человек)

4. Пост-обработка
   ├── Добавить в профиль автора
   ├── Индексировать для поиска
   ├── Уведомить подписчиков
   └── Начать распространение в FYP
```

### For You Page (Система рекомендаций)

```
Секрет алгоритма TikTok:

Входные сигналы:
┌──────────────────────────────────────────────┐
│ Взаимодействия пользователя                 │
│ - Время просмотра (самый важный)            │
│ - Процент досмотра                          │
│ - Повторы, репосты, лайки, комменты         │
│ - Подписки после видео                      │
│ - Сигналы "не интересно"                    │
├──────────────────────────────────────────────┤
│ Метаданные видео                            │
│ - Хештеги, описания, звуки                  │
│ - Информация о создателе                    │
│ - Длина видео, эффекты                      │
└──────────────────────────────────────────────┘

Конвейер рекомендаций:
1. Генерация кандидатов (1M+ → 10K)
   └── Коллаборативная фильтрация
   └── Content-based фильтрация
   └── Буст трендов/вирального

2. Модель ранжирования (10K → 100)
   └── Deep learning модель
   └── Предсказание: P(watch), P(like), P(share)

3. Пере-ранжирование и разнообразие (100 → финал)
   └── Удалить дубликаты
   └── Обеспечить diversity
   └── Добавить новых авторов (exploration)

Ключевой инсайт: TikTok приоритизирует completion rate над лайками
```

### Генерация и доставка ленты

```
Стратегия предрасчёта ленты:

Для активных пользователей (онлайн):
┌─────────────────────────────────────────────┐
│ Real-time лента (низкая задержка)           │
│ 1. Взять предрасчитанных кандидатов (Redis) │
│ 2. Применить real-time сигналы              │
│ 3. Вернуть batch из 10-20 видео            │
│ 4. Prefetch следующего batch при просмотре │
└─────────────────────────────────────────────┘

Для возвращающихся (периодически):
┌─────────────────────────────────────────────┐
│ Batch computation (Spark/Flink)             │
│ 1. Запустить pipeline оффлайн              │
│ 2. Сохранить кандидатов в Redis            │
│ 3. TTL: 1-4 часа                           │
└─────────────────────────────────────────────┘
```

### Стратегия кодирования видео

```
Кодирование для mobile-first:

Формат: H.264 (совместимость) + H.265 (эффективность)
Контейнер: MP4 с fragmented streaming

Лестница разрешений:
┌───────────┬──────────┬────────────┐
│ Качество  │ Bitrate  │ Случай     │
├───────────┼──────────┼────────────┤
│ 480p      │ 1 Mbps   │ Слабый 3G  │
│ 720p      │ 2.5 Mbps │ Хороший 4G │
│ 1080p     │ 5 Mbps   │ WiFi       │
└───────────┴──────────┴────────────┘

Размер chunk: 2-4 секунды (быстрое переключение)
```

### Real-Time вовлечение

```
Поток лайка/комментария/репоста:

Client → API Gateway → Social Service
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────▼─────┐ ┌────▼────┐ ┌─────▼─────┐
        │  Счётчик  │ │  Kafka  │ │  Профиль  │
        │  (Redis)  │ │ (Event) │ │   юзера   │
        └───────────┘ └────┬────┘ └───────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────▼─────┐ ┌────▼────┐ ┌─────▼─────┐
        │ Аналитика │ │  Push   │ │ Dashboard │
        │           │ │ уведомл.│ │  автора   │
        └───────────┘ └─────────┘ └───────────┘

Стратегия счётчиков:
- Redis для real-time
- Batch persist в DB каждые N секунд
- Приблизительные значения для вирального контента
```

### Модерация контента

```
Многоуровневая модерация:

Уровень 1: При загрузке (ML)
├── Детекция nudity/насилия
├── Fingerprinting аудио (копирайт)
├── Извлечение текста + токсичность
└── Блок или флаг на ревью

Уровень 2: До распространения
├── Очередь на ручной просмотр
├── Географические ограничения
└── Возрастные ограничения

Уровень 3: После распространения
├── Жалобы пользователей
├── Мониторинг вирального контента
├── Ретроактивное удаление
```

### Детекция вирального контента

```
Сигналы виральности (real-time):

Ранние индикаторы (первые 30 мин):
- Высокий completion rate (>80%)
- Share rate > 2x от среднего
- Скорость комментариев
- Кросс-демографический appeal

Реакция:
1. Буст в пуле рекомендаций
2. Pre-cache на больше CDN edge
3. Масштабировать encoding
4. Мониторинг на нарушения политики
```

### Ключевые технические решения

| Компонент | Технология | Почему |
|-----------|------------|--------|
| Video Storage | S3 + CDN | Durability, глобальный охват |
| Metadata | PostgreSQL (sharded) | Relational integrity |
| Cache | Redis Cluster | Низкая задержка ленты |
| Events | Kafka | Высокий throughput |
| ML Platform | Custom + TensorFlow | Рекомендации на масштабе |
| Transcoding | FFmpeg + GPU | Скорость, качество |

### Оценка масштаба

```
1B MAU
100M загрузок видео/день
Среднее видео: 30 секунд, 50MB raw

Storage: 100M * 50MB = 5PB/день raw
С транскодингом: ~15PB/день

Peak одновременных: 50M
Feed запросов: 500M/час (свайпы)
Video streams: 10B/день
```

---

## Follow-ups

- How does TikTok handle copyright for sounds/music?
- How would you design the Duet/Stitch feature?
- How does the algorithm balance creator exposure vs user engagement?
- How would you handle live streaming on TikTok?
- What's the difference between TikTok's and Instagram Reels' algorithms?
