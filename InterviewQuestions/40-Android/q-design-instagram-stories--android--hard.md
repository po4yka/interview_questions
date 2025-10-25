---
id: 20251020-200000
title: Design Instagram Stories / Проектирование Instagram Stories
aliases: [Design Instagram Stories, Проектирование Instagram Stories]
topic: android
subtopics:
  - architecture-clean
  - files-media
  - service

question_kind: android
difficulty: hard
original_language: en
language_tags:
  - en
  - ru
source: https://developer.android.com/guide/topics/media
source_note: Android media stack overview
status: draft
moc: moc-android
related:
  - q-data-sync-unstable-network--android--hard
  - q-database-optimization-android--android--medium
  - q-deep-link-vs-app-link--android--medium
created: 2025-10-20
updated: 2025-10-20
tags: [android/architecture-clean, android/files-media, android/service, cdn, difficulty/hard, media, stories]
date created: Saturday, October 25th 2025, 1:26:29 pm
date modified: Saturday, October 25th 2025, 4:52:08 pm
---

# Вопрос (RU)
> Как спроектировать Instagram Stories для Android?

# Question (EN)
> How to design Instagram Stories for Android?

---
## Ответ (RU)

Instagram Stories включает захват и обработку медиа, загрузку, доставку через CDN, просмотр, счетчики/реакции в реальном времени и автоматическое истечение через 24 часа.

### Требования
- Функциональные: создание фото/видео ≤15s, редактор (фильтры/стикеры/текст), просмотр, индикаторы seen/unseen, ответы в DM, близкие друзья, highlights, свайп-навигация, счетчики просмотров.
- Нефункциональные: быстрая загрузка (<5s при хорошем канале), плавное воспроизведение, устойчивость к плохой сети, экономия батареи/памяти, безопасность и приватность.

### Архитектура (высокий уровень)
- Клиент Android: камера, редактор, загрузчик, просмотрщик, кеш/предзагрузка, офлайн-очередь, фоновые задачи (WorkManager).
- Backend API: прием загрузок, транскодирование, генерация превью, TTL/истечение, ACL, счетчики/аналитика.
- Хранилище: объектное (S3/GCS) + CDN для доставки; БД для метаданных; кэш (Redis) для фидов/счетчиков.
- Реал-тайм: Pub/Sub/WebSocket для обновлений просмотров/реакций и инвалидации кеша.

### Клиент Android: Потоки
1. Создание → обработка → загрузка:
   - Изображение: ресайз ≤1080x1920, JPEG/WEBP, генерация thumbnail.
   - Видео: обрезка ≤15s, H.264/HEVC, bitrate ~2Mbps, thumbnail первого кадра.
   - Мета-данные: userId, expiresAt=now+24h, mediaType, размеры.
   - Надежная отправка: WorkManager, повтор с backoff, возобновление.
2. Просмотр:
   - ExoPlayer (видео) + Coil (картинки), прогресс-индикаторы.
   - Предзагрузка: текущая + следующие 2–3 stories; многоуровневое кеширование (Memory→Disk→Network).
   - Управление энергией: пауза в фоне, остановка при сворачивании.
3. Офлайн:
   - Очередь загрузки, локальные метаданные, синхронизация при онлайне.

### Медиа-пайплайн (сервер)
- Транскодирование видео в HLS/DASH профили (мобильные битрейты), хранение мастер-файла и адаптивных слоев.
- Генерация preview/thumbnail; оптимизация изображений под viewport.
- Подписи URL (signed URLs) для защищенной доставки, короткий TTL на ссылки.

### Истечение (TTL 24h)
- На сервере: периодическая джоб/streaming TTL (delete marker) + асинхронное удаление объектов, инвалидация CDN.
- На клиенте: периодическая очистка локальных файлов/кеша и метаданных.

```kotlin
// WorkManager: периодическая чистка локально
class StoryTtlWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params) {
  override suspend fun doWork(): Result { /* delete expired local media + DB */ return Result.success() }
}
```

### Приватность, Доступ, Безопасность
- ACL уровней: автор, близкие друзья, все подписчики.
- Подписанные ссылки (CDN), проверка токенов, ограничение скорости, защита от горячих ссылок.
- Валидация входящих параметров deep/app links.

### Масштабирование И Производительность
- CDN для медиа; кэш фидов и списков сторис; денормализация «кольца» seen/unseen.
- Партиционирование по userId/time; очередь фона для транскодирования/TTL.
- Backpressure на загрузки; лимиты размера/длительности; сжатие на клиенте.

### Метрики И Тестирование
- Время загрузки, время к первому кадру, процент буферизации, ошибки загрузки/воспроизведения.
- Нагрузочное тестирование CDN/транскодера; тесты на плохой сети; battery profile.

## Answer (EN)

Instagram Stories spans capture/processing, upload, CDN delivery, viewing, realtime counters/reactions, and 24h expiration.

### Requirements
- Functional: photo/video ≤15s, editor (filters/stickers/text), viewing, seen/unseen, DM replies, close friends, highlights, swipe nav, view counters.
- Non-functional: fast upload (<5s on good network), smooth playback, network resilience, battery/memory efficiency, security/privacy.

### Architecture (high-level)
- Android client: camera, editor, uploader, viewer, cache/preload, offline queue, background jobs (WorkManager).
- Backend API: ingest, transcode, previews, TTL/expiration, ACL, counters/analytics.
- Storage: object store (S3/GCS) + CDN; DB for metadata; cache (Redis) for feeds/counters.
- Realtime: Pub/Sub/WebSocket for view/reaction updates and cache invalidation.

### Android Client Flows
1. Create → process → upload:
   - Image: resize ≤1080x1920, JPEG/WEBP, thumbnail.
   - Video: trim ≤15s, H.264/HEVC ~2Mbps, first-frame thumbnail.
   - Metadata: userId, expiresAt=now+24h, mediaType, dimensions.
   - Reliability: WorkManager, retry with backoff, resume uploads.
2. Playback:
   - ExoPlayer for video, Coil for images, progress indicators.
   - Preload current + next 2–3; multi-level caching (Memory→Disk→Network).
   - Power: pause in background, stop on app background.
3. Offline:
   - Upload queue, local metadata, sync on reconnect.

### Media Pipeline (server)
- Transcode video to HLS/DASH mobile renditions; keep master and adaptive layers.
- Generate previews/thumbnails; optimize images for viewport.
- Signed URLs with short TTL; secure delivery via CDN.

### Expiration (24h TTL)
- Server: periodic job/streaming TTL marker + async object deletion; CDN invalidation.
- Client: periodic local cleanup of files/cache and metadata.

```kotlin
// WorkManager: periodic local cleanup
class StoryTtlWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params) {
  override suspend fun doWork(): Result { /* delete expired local media + DB */ return Result.success() }
}
```

### Privacy, Access, Security
- ACL tiers: author, close friends, all followers.
- Signed URLs (CDN), token checks, rate limits, hotlink protection.
- Validate deep/app link parameters.

### Scalability & Performance
- CDN for media; cache rings/feeds; denormalize seen/unseen ring.
- Partition by userId/time; background queues for transcode/TTL.
- Client-side compression; enforce size/duration limits; backpressure uploads.

### Metrics & Testing
- Upload time, time-to-first-frame, rebuffer ratio, upload/playback errors.
- Load test CDN/transcoder; poor-network tests; battery profiling.

**See also:** c-mvvm, c-clean-architecture


## Follow-ups
- How to order story buckets efficiently (ranking, freshness, edges)?
- How to handle abusive content detection at scale?
- How to minimize rebuffering on low bandwidth?

## References
- https://exoplayer.dev/
- https://developer.android.com/guide/background
- https://developer.android.com/guide/topics/media/mediaplayer
- https://cloud.google.com/cdn

## Related Questions
- [[q-deep-link-vs-app-link--android--medium]]
- [[q-data-sync-unstable-network--android--hard]]
- [[q-database-optimization-android--android--medium]]
