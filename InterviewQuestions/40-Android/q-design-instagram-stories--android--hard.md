---
id: 20251020-200000
title: Design Instagram Stories / Проектирование Instagram Stories
aliases: [Design Instagram Stories, Проектирование Instagram Stories]
topic: android
subtopics: [architecture-clean, files-media, service]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
sources: [https://developer.android.com/guide/topics/media]
status: draft
moc: moc-android
related:
  - q-data-sync-unstable-network--android--hard
  - q-database-optimization-android--android--medium
created: 2025-10-20
updated: 2025-01-27
tags: [android/architecture-clean, android/files-media, android/service, cdn, difficulty/hard, media, stories]
---
# Вопрос (RU)
> Как спроектировать Instagram Stories для Android?

# Question (EN)
> How to design Instagram Stories for Android?

---
## Ответ (RU)

Instagram Stories — система для создания, загрузки, воспроизведения и автоматического удаления медиа через 24ч.

### Архитектура

**Android-клиент:**
- [[c-clean-architecture]]: Domain (Story entity, TTL logic), Data (Repository для загрузки/кеша), Presentation (MVVM для камеры и просмотра)
- [[c-workmanager]] для надежной загрузки с повторами и очистки истекших
- ExoPlayer для видео, Coil для изображений
- Многоуровневый кеш (Memory/Disk/Network)

**Backend:**
- API: загрузка, транскодирование, TTL-джобы, ACL
- Хранилище: S3/GCS + CDN; метаданные в БД
- Realtime: WebSocket/Pub-Sub для счетчиков просмотров

### Ключевые потоки

**Создание и загрузка:**

```kotlin
// ✅ Надежная загрузка с повторами
class UploadStoryWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params) {
  override suspend fun doWork(): Result =
    try {
      val uri = inputData.getString("uri")!!
      val compressed = compressMedia(uri) // JPEG/WEBP, H.264, ≤2Mbps
      storyRepo.upload(compressed, expiresAt = now() + 24.hours)
      Result.success()
    } catch (e: Exception) {
      if (runAttemptCount < 3) Result.retry() else Result.failure()
    }
}
```

**Просмотр:**
- Предзагрузка текущей + 2 следующих stories
- OkHttp DiskCache + память для превью
- Пауза ExoPlayer в фоне для экономии батареи

**TTL (24ч):**

```kotlin
// ✅ Периодическая очистка истекших
class CleanupExpiredWorker : CoroutineWorker(ctx, params) {
  override suspend fun doWork(): Result {
    storyRepo.deleteExpired(before = now())
    cacheManager.evict { it.expiresAt < now() }
    return Result.success()
  }
}
```

### Оптимизация

- **Offline:** очередь в WorkManager, локальная БД с метаданными
- **CDN:** подписанные URL с коротким TTL
- **Скейлинг:** партиционирование по userId, денормализация seen/unseen ring

## Answer (EN)

Instagram Stories is a system for creating, uploading, playing, and auto-deleting media after 24h.

### Architecture

**Android client:**
- [[c-clean-architecture]]: Domain (Story entity, TTL logic), Data (Repository for upload/cache), Presentation (MVVM for camera and viewer)
- [[c-workmanager]] for reliable upload with retries and cleanup of expired stories
- ExoPlayer for video, Coil for images
- Multi-level caching (Memory/Disk/Network)

**Backend:**
- API: upload, transcode, TTL jobs, ACL
- Storage: S3/GCS + CDN; metadata in DB
- Realtime: WebSocket/Pub-Sub for view counters

### Key Flows

**Create and Upload:**

```kotlin
// ✅ Reliable upload with retries
class UploadStoryWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params) {
  override suspend fun doWork(): Result =
    try {
      val uri = inputData.getString("uri")!!
      val compressed = compressMedia(uri) // JPEG/WEBP, H.264, ≤2Mbps
      storyRepo.upload(compressed, expiresAt = now() + 24.hours)
      Result.success()
    } catch (e: Exception) {
      if (runAttemptCount < 3) Result.retry() else Result.failure()
    }
}
```

**Playback:**
- Preload current + next 2 stories
- OkHttp DiskCache + memory for previews
- Pause ExoPlayer in background to save battery

**TTL (24h):**

```kotlin
// ✅ Periodic cleanup of expired stories
class CleanupExpiredWorker : CoroutineWorker(ctx, params) {
  override suspend fun doWork(): Result {
    storyRepo.deleteExpired(before = now())
    cacheManager.evict { it.expiresAt < now() }
    return Result.success()
  }
}
```

### Optimization

- **Offline:** WorkManager queue, local DB for metadata
- **CDN:** signed URLs with short TTL
- **Scaling:** partition by userId, denormalize seen/unseen ring

## Follow-ups

- How to handle video transcoding failures and retry strategies?
- What caching strategy minimizes bandwidth while ensuring smooth playback?
- How to implement efficient preloading without draining battery?
- What security measures prevent unauthorized access to expired stories?

## References

- [[c-clean-architecture]]
- [[c-workmanager]]
- https://developer.android.com/guide/topics/media
- https://developer.android.com/guide/background

## Related Questions

### Prerequisites
- Understanding of WorkManager retry policies and constraints
- ExoPlayer basics for video playback

### Related
- [[q-data-sync-unstable-network--android--hard]]
- [[q-database-optimization-android--android--medium]]

### Advanced
- Design a CDN caching strategy for ephemeral content
- Implement real-time view counters at Instagram scale
