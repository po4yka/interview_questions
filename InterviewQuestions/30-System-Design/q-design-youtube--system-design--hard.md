---
id: sysdes-045
title: Design YouTube
aliases:
- Design YouTube
- Video Streaming System
- Video Platform Design
topic: system-design
subtopics:
- design-problems
- video-streaming
- storage
question_kind: system-design
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-design-netflix--system-design--hard
- q-cdn--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- design-problems
- difficulty/hard
- video-streaming
- system-design
anki_cards:
- slug: sysdes-045-0-en
  language: en
  anki_id: 1769159521947
  synced_at: '2026-01-23T13:49:17.835359'
- slug: sysdes-045-0-ru
  language: ru
  anki_id: 1769159521969
  synced_at: '2026-01-23T13:49:17.836476'
---
# Question (EN)
> Design a video sharing platform like YouTube. Focus on video upload, processing, and streaming.

# Vopros (RU)
> Спроектируйте платформу для обмена видео типа YouTube. Фокус на загрузку, обработку и стриминг видео.

---

## Answer (EN)

### Requirements

**Functional**: Upload videos, stream videos, search, recommendations
**Non-functional**: High availability, low latency streaming, scalable to billions of videos

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Clients                              │
│    (Web, Mobile, Smart TV, Gaming Consoles)                │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                     CDN (Edge)                              │
│              (Cached video chunks)                          │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    API Gateway                              │
│         (Rate limiting, auth, routing)                     │
└─────────┬───────────────┬───────────────┬───────────────────┘
          │               │               │
    ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
    │  Upload   │   │  Video    │   │  Search   │
    │  Service  │   │  Service  │   │  Service  │
    └─────┬─────┘   └─────┬─────┘   └─────┬─────┘
          │               │               │
    ┌─────▼─────┐   ┌─────▼─────┐   ┌─────▼─────┐
    │   Blob    │   │ Metadata  │   │Elasticsearch│
    │  Storage  │   │    DB     │   │           │
    └───────────┘   └───────────┘   └───────────┘
```

### Video Upload Pipeline

```
1. Client uploads → Upload Service
2. Store original → Blob Storage (S3)
3. Queue processing → Message Queue
4. Transcoding Service:
   - Multiple resolutions (240p, 480p, 720p, 1080p, 4K)
   - Multiple formats (H.264, VP9, AV1)
   - Generate thumbnails
5. Store processed → Blob Storage
6. Update metadata → Database
7. Push to CDN → Pre-warm popular regions
```

### Video Streaming

```
Adaptive Bitrate Streaming (HLS/DASH):

manifest.m3u8:
  #EXT-X-STREAM-INF:BANDWIDTH=800000
  480p/playlist.m3u8
  #EXT-X-STREAM-INF:BANDWIDTH=2000000
  720p/playlist.m3u8
  #EXT-X-STREAM-INF:BANDWIDTH=5000000
  1080p/playlist.m3u8

Client:
1. Fetch manifest
2. Measure bandwidth
3. Request appropriate quality chunks
4. Adapt as bandwidth changes
```

### Key Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| Blob Storage | S3, GCS | Store video files |
| CDN | CloudFront, Akamai | Global video delivery |
| Transcoding | FFmpeg clusters | Video processing |
| Metadata DB | MySQL/Postgres + sharding | Video info |
| Search | Elasticsearch | Video search |
| Cache | Redis | Hot metadata |
| Queue | Kafka | Async processing |

### Scale Estimates

```
500M daily active users
5M video uploads/day
Average video: 5 minutes, 500MB raw

Storage: 5M * 500MB = 2.5PB/day raw
Transcoded: ~5x = 12.5PB/day
Bandwidth: Peak 100M concurrent streams
```

---

## Otvet (RU)

### Требования

**Функциональные**: Загрузка видео, стриминг, поиск, рекомендации
**Нефункциональные**: Высокая доступность, низкая задержка стриминга, масштабирование на миллиарды видео

### Конвейер загрузки видео

```
1. Клиент загружает → Upload Service
2. Сохранить оригинал → Blob Storage (S3)
3. Очередь обработки → Message Queue
4. Transcoding Service:
   - Множество разрешений (240p, 480p, 720p, 1080p, 4K)
   - Множество форматов (H.264, VP9, AV1)
   - Генерация превью
5. Сохранить обработанное → Blob Storage
6. Обновить метаданные → Database
7. Пуш в CDN → Pre-warm популярных регионов
```

### Стриминг видео

```
Adaptive Bitrate Streaming (HLS/DASH):

Клиент:
1. Получить манифест
2. Измерить пропускную способность
3. Запросить чанки соответствующего качества
4. Адаптироваться при изменении bandwidth
```

### Ключевые компоненты

| Компонент | Технология | Назначение |
|-----------|------------|------------|
| Blob Storage | S3, GCS | Хранение видеофайлов |
| CDN | CloudFront, Akamai | Глобальная доставка |
| Transcoding | FFmpeg кластеры | Обработка видео |
| Metadata DB | MySQL/Postgres + шардинг | Инфо о видео |
| Search | Elasticsearch | Поиск видео |
| Cache | Redis | Горячие метаданные |
| Queue | Kafka | Async обработка |

### Оценка масштаба

```
500M DAU
5M загрузок видео/день
Среднее видео: 5 минут, 500MB raw

Storage: 5M * 500MB = 2.5PB/день raw
С транскодингом: ~5x = 12.5PB/день
```

---

## Follow-ups

- How do you handle copyright detection?
- How does live streaming differ from VOD?
- How do you design the recommendation system?
