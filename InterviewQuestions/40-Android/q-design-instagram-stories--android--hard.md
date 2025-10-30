---
id: 20251020-200000
title: Design Instagram Stories / Проектирование Instagram Stories
aliases: [Design Instagram Stories, Проектирование Instagram Stories]
topic: android
subtopics: [architecture-clean, media, service]
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
tags:
    [
        android/architecture-clean,
        android/media,
        android/service,
        cdn,
        difficulty/hard,
        media,
        stories,
        platform/android,
        lang/kotlin,
    ]
date created: Monday, October 27th 2025, 3:37:27 pm
date modified: Wednesday, October 29th 2025, 5:07:33 pm
---

# Вопрос (RU)

> Как спроектировать Instagram Stories для Android?

# Question (EN)

> How to design Instagram Stories for Android?

---

### Upgraded Interview Prompt (RU)

Спроектируйте захват и воспроизведение Stories на Android. Захват: видео 15с @ 720p/30fps, опциональные AR‑эффекты, экспорт <3с (p95) на устройстве среднего уровня (например, Snapdragon 7‑серии). Воспроизведение: старт <150мс (p95), плавные 60fps на современных устройствах с graceful degradation на бюджетных. Поддержать прерывистую связь и фоновую возобновляемую загрузку. Покажите: выбор камеры (CameraX vs Camera2), конвейер рендеринга (zero‑copy к энкодеру), конфигурацию кодека (codec/profile/bitrate/GOP), чанковую/возобновляемую загрузку, CDN‑кеш и prefetch, политику on‑device кеша, стратегию ExoPlayer, аудиофокус, меры по теплу/батарее, наблюдаемость, релиз/откат и доступность.

### Upgraded Interview Prompt (EN)

Design Stories capture & playback on Android. Capture: 15s video @ 720p/30fps, optional AR effects, and export <3s (p95) on a mid‑tier device (e.g., Snapdragon 7‑series). Playback: startup <150ms (p95), smooth 60fps on modern devices with graceful degradation on low‑end. Support intermittent connectivity and background‑resumable upload. Show: camera stack choice (CameraX vs. Camera2), render pipeline (zero-copy to encoder), encoder config (codec/profile/bitrate/GOP), chunked/resumable upload, CDN caching & prefetch, on‑device cache policy, ExoPlayer playback strategy, audio focus, thermal/battery mitigation, observability, release/rollback, and accessibility.

## Ответ (RU)

Instagram Stories — система для создания, загрузки, воспроизведения и автоматического удаления медиа через 24ч.

### Архитектура

**Android-клиент:**

-   [[c-clean-architecture]]: Domain (Story entity, TTL logic), Data (Repository для загрузки/кеша), Presentation (MVVM для камеры и просмотра)
-   [[c-workmanager]] для надежной загрузки с повторами и очистки истекших
-   ExoPlayer для видео, Coil для изображений
-   Многоуровневый кеш (Memory/Disk/Network)

**Backend:**

-   API: загрузка, транскодирование, TTL-джобы, ACL
-   Хранилище: S3/GCS + CDN; метаданные в БД
-   Realtime: WebSocket/Pub-Sub для счетчиков просмотров

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

-   Предзагрузка текущей + 2 следующих stories
-   OkHttp DiskCache + память для превью
-   Пауза ExoPlayer в фоне для экономии батареи

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

-   **Offline:** очередь в WorkManager, локальная БД с метаданными
-   **CDN:** подписанные URL с коротким TTL
-   **Скейлинг:** партиционирование по userId, денормализация seen/unseen ring

### Staff-level Model Answer (RU)

Архитектура: модули feature-stories-capture, feature-stories-playback, media-core (Camera/GL/Codec), upload, cache, analytics, flags. MVVM + однонаправленный поток данных; DI (Hilt); флаги для кодеков, длины сегментов, prefetch.

Захват: CameraX (широкая совместимость), при необходимости путь Camera2 для ручного контроля. Рендер через OpenGL ES, zero‑copy путь: Camera → SurfaceTexture → GL → Surface(Encoder). MediaCodec H.264 (Baseline/High; HEVC под флагом). 4–6 Mbps @720p30, GOP=1s, VBR с упором на стабильный размер. AAC 128–192 kbps. Мультиплексирование MediaMuxer в MP4. Тепло/батарея: даунскейл до 540p/понизить битрейт при троттлинге; отключать тяжёлые фильтры.

Загрузка: превью/thumbnail, perceptual hash для дедупликации. Чанки 4–8MB, SHA‑256 per‑chunk, возобновление по смещению, TLS; при политике — шифрование AES‑GCM клиента. WorkManager с ограничениями, экспоненциальный backoff, уважать Doze.

Воспроизведение: HLS/DASH с ~1s сегментами для старта <150мс; несколько битрейтов, ABR. Prefetch 2–3 сегментов следующей истории, отмена при свайпе. LRU‑кеш ~250MB, эвикция по времени/просмотру; хранить первые N сегментов для редких историй. На слабых — 30fps, меньшие разрешения, отключить тяжёлые переходы. Аудиофокус и PiP по требованиям.

Наблюдаемость/операции: метрики p95 старта/экспорта, rebuffer, ошибки кодека, ANR/крэши, hit‑rate кеша, ретраи загрузок. Килл‑свитчи для кодеков/размеров сегментов, staged rollout с авто‑откатом по деградации.

Тестирование/релиз: юнит‑тесты фильтров и конфигов, интеграция ExoPlayer с throttle‑сетью, перф‑тесты на матрице устройств, golden тесты запись→воспроизведение, бета 5–10%.

Последовательность: MVP (базовый захват→H.264→одношаговая загрузка→простое воспроизведение) → упрочнение (prefetch, кеш, возобновляемые загрузки, обработка ошибок) → масштаб (ABR, HEVC под флагом, термальная адаптация, эксперименты).

## Answer (EN)

Instagram Stories is a system for creating, uploading, playing, and auto-deleting media after 24h.

### Architecture

**Android client:**

-   [[c-clean-architecture]]: Domain (Story entity, TTL logic), Data (Repository for upload/cache), Presentation (MVVM for camera and viewer)
-   [[c-workmanager]] for reliable upload with retries and cleanup of expired stories
-   ExoPlayer for video, Coil for images
-   Multi-level caching (Memory/Disk/Network)

**Backend:**

-   API: upload, transcode, TTL jobs, ACL
-   Storage: S3/GCS + CDN; metadata in DB
-   Realtime: WebSocket/Pub-Sub for view counters

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

-   Preload current + next 2 stories
-   OkHttp DiskCache + memory for previews
-   Pause ExoPlayer in background to save battery

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

-   **Offline:** WorkManager queue, local DB for metadata
-   **CDN:** signed URLs with short TTL
-   **Scaling:** partition by userId, denormalize seen/unseen ring

### Staff-level Model Answer (EN)

Architecture overview

Modules: feature-stories-capture, feature-stories-playback, media-core (Camera/GL/Codec), upload, cache, analytics, flags, ab-testing. Patterns: MVVM + unidirectional data flow; DI via Hilt. Feature flags for codecs, segment length, prefetch size.

Capture pipeline

Camera: Prefer CameraX; fallback to Camera2 for manual controls. Request 720p/30. Effects: OpenGL ES chain; zero‑copy path Camera → SurfaceTexture → GL → Surface(Encoder). Encoder: MediaCodec H.264 (Baseline/High), HEVC behind flag. Target 4–6 Mbps @720p30, GOP 1s, CBR‑biased VBR. Audio AAC 128–192 kbps. Mux with MediaMuxer to MP4. Export <3s p95 via HW codec and GL.

Upload pipeline

Pre-upload: thumbnail + low‑res preview; perceptual hash. Chunking: 4–8MB with SHA‑256 per chunk; resumable with offset negotiation; TLS; optional AES‑GCM client-side. Background via WorkManager; respect Doze; exponential backoff with Retry‑After.

Playback system (ExoPlayer)

HLS/DASH with ~1s segments to hit <150ms start; multiple bitrates with ABR. Prefetch next 2–3 segments; cancel on swipe away. On-device LRU cache (~250MB) and evict by age/last-viewed; store only first N segments for infrequent stories. Graceful degradation on low-end (30fps cap, lower ladder). Audio focus and PiP as needed.

Accessibility & UX resilience

TalkBack labels, captions/subtitles, larger tap targets; retry flows for drops.

Observability & safety

Metrics: startup p95, rebuffer ratio, export p95, encoder error rate, crash/ANR, cache hit rate, upload retries. Guardrails: health gates, kill‑switches, staged rollout with automated rollback.

Testing & release

Unit for filter graph/encoder configs/state machines. Integration for ExoPlayer with throttled networks. On‑device perf matrix. Golden record+playback tests. Beta 5–10% with monitoring.

Sequencing and tradeoffs

MVP → Hardening → Scale. Short 1s segments reduce start latency but raise CDN overhead; HEVC reduces bitrate but risks compatibility → guard by flags and dual-mux where needed.

## Follow-ups

-   How to handle video transcoding failures and retry strategies?
-   What caching strategy minimizes bandwidth while ensuring smooth playback?
-   How to implement efficient preloading without draining battery?
-   What security measures prevent unauthorized access to expired stories?

## References

-   [[c-clean-architecture]]
-   [[c-workmanager]]
-   https://developer.android.com/guide/topics/media
-   https://developer.android.com/guide/background
-   [[ANDROID-SYSTEM-DESIGN-CHECKLIST]]
-   [[ANDROID-INTERVIEWER-GUIDE]]

## Related Questions

### Prerequisites

-   Understanding of WorkManager retry policies and constraints
-   ExoPlayer basics for video playback

### Related

-   [[q-data-sync-unstable-network--android--hard]]
-   [[q-database-optimization-android--android--medium]]

### Advanced

-   Design a CDN caching strategy for ephemeral content
-   Implement real-time view counters at Instagram scale
