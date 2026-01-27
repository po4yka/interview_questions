---
id: sysdes-078
title: Design Spotify
aliases:
- Design Spotify
- Music Streaming Service
- Audio Streaming Platform
topic: system-design
subtopics:
- design-problems
- streaming
- recommendation
- music
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-design-netflix--system-design--hard
- q-design-youtube--system-design--hard
- q-cdn-content-delivery-network--system-design--medium
created: 2025-01-26
updated: 2025-01-26
tags:
- design-problems
- difficulty/medium
- streaming
- system-design
---
# Question (EN)
> How would you design a music streaming service like Spotify?

# Vopros (RU)
> Как бы вы спроектировали сервис потоковой музыки, подобный Spotify?

---

## Answer (EN)

### Requirements

**Functional**: Stream music, search songs/artists/albums, create playlists, personalized recommendations, offline mode, social features (follow, share)
**Non-functional**: 99.9% availability, <200ms playback start, support 500M users, 100M songs, efficient royalty tracking

### Scale Estimation

```
Users: 500M total, 50M concurrent peak
Songs: 100M tracks, average 4MB each = 400TB audio
Daily plays: 10B streams/day
Writes: Low (user actions) vs Reads: Very high (streaming)
```

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      Client Apps                              │
│            (Mobile, Desktop, Web, Smart Speakers)            │
└───────────────────────────┬──────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────┐
│                     API Gateway                               │
│              (Rate limiting, Auth, Routing)                  │
└───────────────────────────┬──────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────┐
│                    Core Services                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐   │
│  │ Playback │ │ Search   │ │ Playlist │ │ Recommendation │   │
│  │ Service  │ │ Service  │ │ Service  │ │ Service        │   │
│  └──────────┘ └──────────┘ └──────────┘ └────────────────┘   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐   │
│  │ User     │ │ Catalog  │ │ Social   │ │ Royalty        │   │
│  │ Service  │ │ Service  │ │ Service  │ │ Service        │   │
│  └──────────┘ └──────────┘ └──────────┘ └────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────┐
│                        CDN Layer                              │
│              (Audio file distribution globally)              │
└──────────────────────────────────────────────────────────────┘
```

### Audio Storage and Delivery

```
Audio Processing Pipeline:
1. Ingest: Original audio files (WAV, FLAC)
2. Transcode: Multiple formats/bitrates
   - 96 kbps (low quality, mobile data saving)
   - 160 kbps (normal quality)
   - 320 kbps (high quality, premium)
   - Ogg Vorbis format (efficient compression)
3. Store: Object storage (S3-like) with metadata
4. Distribute: CDN edge servers worldwide

CDN Strategy:
- Popular songs pre-cached at all edges
- Regional hits cached at regional PoPs
- Long-tail fetched on-demand from origin
- 95%+ cache hit ratio target
```

### Streaming Protocol

```
Audio Streaming Flow:
┌────────┐    1. Request song     ┌────────────┐
│ Client │ ──────────────────────→│  Playback  │
│        │                        │  Service   │
│        │←── 2. Signed CDN URL ──│            │
└────────┘                        └────────────┘
    │
    │ 3. Fetch audio chunks (HLS/DASH)
    ▼
┌────────────────────────────────────────────┐
│                   CDN                       │
│  - Chunked delivery (10-30 sec segments)   │
│  - Adaptive bitrate based on network       │
│  - Gapless playback support                │
└────────────────────────────────────────────┘

Key Features:
- Pre-buffer next song for gapless playback
- Adaptive bitrate switching mid-stream
- Resume playback from last position
```

### Offline Mode and Caching

```
Offline Download Flow:
1. User marks song/playlist for offline
2. Client requests encrypted download URLs
3. Download audio files with DRM protection
4. Store in local encrypted cache
5. Playback requires valid license (periodic check)

Cache Hierarchy:
┌─────────────────────────────────────┐
│ Device Cache (local storage)        │
│  - Downloaded songs (encrypted)     │
│  - Recently played (LRU cache)      │
│  - Pre-fetched next-up songs        │
└─────────────────────────────────────┘
```

### Search Architecture

```
Search Components:
┌─────────────────────────────────────────────────┐
│                Search Service                    │
├─────────────────────────────────────────────────┤
│ 1. Query Processing                             │
│    - Tokenization, normalization                │
│    - Spell correction, autocomplete             │
│    - Language detection                         │
│                                                 │
│ 2. Elasticsearch Cluster                        │
│    - Songs index (title, artist, album, lyrics)│
│    - Artists index                              │
│    - Playlists index                            │
│    - Sharded by region/alphabet                 │
│                                                 │
│ 3. Ranking                                      │
│    - Relevance score                            │
│    - Popularity boost                           │
│    - Personalization factors                    │
└─────────────────────────────────────────────────┘

Autocomplete: Prefix trie + popularity ranking
Fuzzy matching: Edit distance for typo tolerance
```

### Recommendation Engine

```
Recommendation System:
┌─────────────────────────────────────────────────┐
│           Recommendation Pipeline               │
├─────────────────────────────────────────────────┤
│ Data Sources:                                   │
│  - Listening history                            │
│  - Playlist composition                         │
│  - Skip/save behavior                           │
│  - Time of day, location                        │
│  - Audio features (tempo, energy, mood)         │
├─────────────────────────────────────────────────┤
│ Algorithms:                                     │
│  1. Collaborative Filtering                     │
│     - Users who liked X also liked Y            │
│     - Matrix factorization (ALS)                │
│                                                 │
│  2. Content-Based                               │
│     - Audio analysis (tempo, key, energy)       │
│     - Genre/mood classification                 │
│                                                 │
│  3. Hybrid Approach                             │
│     - Combine collaborative + content-based     │
│     - ML ranking model (XGBoost, Neural)        │
├─────────────────────────────────────────────────┤
│ Features:                                       │
│  - Discover Weekly (personalized weekly mix)    │
│  - Daily Mix (genre-based personal playlists)  │
│  - Release Radar (new from followed artists)   │
└─────────────────────────────────────────────────┘
```

### Playlist Management

```
Playlist Data Model:
┌─────────────────────────────────────────────────┐
│ Playlist                                        │
│  - id: UUID                                     │
│  - owner_id: user reference                     │
│  - name, description, cover_image               │
│  - is_public: boolean                           │
│  - collaborative: boolean                       │
│  - tracks: ordered list of track_ids            │
│  - created_at, updated_at                       │
└─────────────────────────────────────────────────┘

Storage:
- Metadata: PostgreSQL (ACID for user data)
- Track lists: Redis for fast access
- Large playlists (>1000 songs): Paginated storage

Collaborative Playlists:
- Optimistic locking for concurrent edits
- Event sourcing for edit history
- Real-time sync via WebSocket
```

### Royalty Tracking

```
Royalty Calculation Pipeline:
┌────────────────────────────────────────────────┐
│ 1. Stream Event Collection                      │
│    - Track ID, user ID, timestamp, duration    │
│    - Country, subscription type                │
│    - Minimum play threshold (30 seconds)       │
├────────────────────────────────────────────────┤
│ 2. Aggregation (Apache Kafka + Flink)          │
│    - Real-time stream processing               │
│    - Deduplication (same user, same song)      │
│    - Fraud detection (bot plays)               │
├────────────────────────────────────────────────┤
│ 3. Royalty Calculation                         │
│    - Pro-rata model: pays per stream share     │
│    - Revenue pool / total streams × artist     │
│    - Different rates by country, tier          │
├────────────────────────────────────────────────┤
│ 4. Reporting                                    │
│    - Monthly artist statements                 │
│    - Label and publisher splits                │
│    - Rights holder payouts                     │
└────────────────────────────────────────────────┘
```

### Database Schema

```sql
-- Core entities
Users (id, email, name, country, subscription_tier, created_at)
Artists (id, name, bio, image_url, verified, monthly_listeners)
Albums (id, artist_id, title, release_date, cover_url)
Tracks (id, album_id, title, duration_ms, audio_url, popularity)

-- User activity
Playlists (id, user_id, name, is_public, track_ids[])
ListeningHistory (user_id, track_id, played_at, duration_played)
SavedTracks (user_id, track_id, saved_at)
Follows (follower_id, followee_id, followee_type)

-- Streaming events (for royalties)
StreamEvents (event_id, user_id, track_id, timestamp, country, duration_ms)
```

### Key Technical Decisions

| Component | Technology | Why |
|-----------|------------|-----|
| Audio Storage | S3 + CDN | Durability, global distribution |
| Streaming | HLS/DASH | Adaptive bitrate, industry standard |
| Metadata DB | PostgreSQL | ACID, relational queries |
| Cache | Redis Cluster | Low latency, pub/sub |
| Search | Elasticsearch | Full-text, fuzzy matching |
| Stream Processing | Kafka + Flink | Real-time royalty tracking |
| Recommendations | Spark MLlib | Batch ML training |
| DRM | Widevine/FairPlay | Content protection |

---

## Otvet (RU)

### Требования

**Функциональные**: Стриминг музыки, поиск песен/артистов, создание плейлистов, рекомендации, офлайн-режим
**Нефункциональные**: 99.9% доступность, <200мс до начала воспроизведения, 500М пользователей, 100М треков

### Оценка масштаба

```
Пользователи: 500М всего, 50М одновременно в пике
Песни: 100М треков, в среднем 4МБ = 400ТБ аудио
Ежедневно: 10 млрд прослушиваний
Записи: Мало (действия) vs Чтения: Очень много (стриминг)
```

### Хранение и доставка аудио

```
Пайплайн обработки аудио:
1. Приём: Оригинальные файлы (WAV, FLAC)
2. Транскодирование: Несколько форматов/битрейтов
   - 96 kbps (экономия трафика)
   - 160 kbps (нормальное качество)
   - 320 kbps (высокое, премиум)
   - Формат Ogg Vorbis (эффективное сжатие)
3. Хранение: Object storage с метаданными
4. Распространение: CDN по всему миру

Стратегия CDN:
- Популярные песни кешируются везде
- Региональные хиты на региональных серверах
- Long-tail по запросу с origin
- Цель: 95%+ cache hit ratio
```

### Протокол стриминга

```
Поток воспроизведения:
1. Клиент запрашивает трек
2. Playback Service возвращает подписанный URL CDN
3. Клиент получает аудио чанками (HLS/DASH)

Ключевые особенности:
- Предзагрузка следующей песни (gapless playback)
- Адаптивный битрейт на лету
- Возобновление с последней позиции
```

### Офлайн-режим

```
Поток скачивания:
1. Пользователь отмечает для офлайна
2. Клиент запрашивает зашифрованные URL
3. Скачивание с DRM-защитой
4. Хранение в локальном зашифрованном кеше
5. Воспроизведение требует валидной лицензии

Иерархия кеша:
- Скачанные песни (зашифрованы)
- Недавно прослушанные (LRU кеш)
- Предзагруженные следующие треки
```

### Архитектура поиска

```
Компоненты поиска:
1. Обработка запроса
   - Токенизация, нормализация
   - Исправление опечаток, автодополнение

2. Elasticsearch кластер
   - Индекс песен (название, артист, альбом, тексты)
   - Индекс артистов
   - Индекс плейлистов
   - Шардирование по региону/алфавиту

3. Ранжирование
   - Оценка релевантности
   - Буст популярности
   - Персонализация
```

### Система рекомендаций

```
Источники данных:
- История прослушиваний
- Состав плейлистов
- Поведение (скип/сохранение)
- Время суток, локация
- Аудио-характеристики (темп, энергия, настроение)

Алгоритмы:
1. Коллаборативная фильтрация
   - Пользователи с похожими вкусами
   - Матричная факторизация (ALS)

2. Content-Based
   - Анализ аудио (темп, тональность, энергия)
   - Классификация жанра/настроения

3. Гибридный подход
   - Комбинация collaborative + content-based
   - ML ранжирование (XGBoost, нейросети)

Фичи:
- Discover Weekly (персональный микс)
- Daily Mix (плейлисты по жанрам)
- Release Radar (новинки от артистов)
```

### Учёт роялти

```
Пайплайн расчёта роялти:
1. Сбор событий стриминга
   - ID трека, пользователя, время, длительность
   - Страна, тип подписки
   - Порог: минимум 30 секунд

2. Агрегация (Kafka + Flink)
   - Real-time обработка
   - Дедупликация
   - Обнаружение фрода (ботов)

3. Расчёт роялти
   - Pro-rata модель: оплата за долю стримов
   - Пул выручки / общие стримы × артист
   - Разные ставки по странам и тарифам

4. Отчётность
   - Ежемесячные выписки артистов
   - Распределение лейблам и издателям
```

### Ключевые технические решения

| Компонент | Технология | Причина |
|-----------|------------|---------|
| Audio Storage | S3 + CDN | Надёжность, глобальность |
| Streaming | HLS/DASH | Adaptive bitrate |
| Metadata DB | PostgreSQL | ACID, SQL |
| Cache | Redis Cluster | Низкая задержка |
| Search | Elasticsearch | Полнотекстовый поиск |
| Stream Processing | Kafka + Flink | Real-time роялти |
| Recommendations | Spark MLlib | Batch ML |
| DRM | Widevine/FairPlay | Защита контента |

---

## Follow-ups

- How does Spotify handle music licensing in different countries?
- What is the difference between Spotify's recommendation approach and Netflix's?
- How would you design the "Wrapped" year-end summary feature?
- How does Spotify implement crossfade and gapless playback?
- How would you handle live audio streaming (podcasts, live sessions)?
