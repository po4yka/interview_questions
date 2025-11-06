---
id: android-486
title: Design TikTok-style Short-Video Feed / Проектирование коротких видео (TikTok-стиль)
aliases:
- Design TikTok-style Short-Video Feed
- Проектирование коротких видео (TikTok-стиль)
topic: android
subtopics:
- media
- performance-rendering
- service
question_kind: android
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-room
- c-workmanager
- q-design-instagram-stories--android--hard
sources: []
created: 2025-10-29
updated: 2025-10-29
tags:
- difficulty/hard
- android/media
- android/performance-rendering
- android/service
- topic/android
---

# Вопрос (RU)

> Как спроектировать ленту коротких видео (TikTok-стиль) для Android?

# Question (EN)

> How to design a TikTok-style short-video feed for Android?

---

### Upgraded Interview Prompt (RU)

Спроектируйте ленту коротких видео для Android. Цели: холодный старт <2.0с (p95), первый кадр <120мс (p95), коэффициент rebuffer <1%, 60fps на современных устройствах, graceful degradation на бюджетных. Добавьте загрузку контента (15–60с, возобновляемая), ABR‑воспроизведение, prefetch, on‑device кеш (лимит 300MB) и фоновые ограничения (Android 11–15). Покажите: модульную архитектуру, политику prefetch, эвикцию кеша, чанкование загрузки, пайплайн thumbnail/preview, наблюдаемость, защиту релиза.

### Upgraded Interview Prompt (EN)

Design a short‑video feed for Android. Targets: cold start <2.0s (p95), first frame <120ms (p95), rebuffer ratio <1%, 60fps on modern devices, graceful on low‑end. Add creator upload (15–60s, resumable), ABR playback, prefetch, on‑device caching (300MB cap), and background constraints (Android 11–15). Show: module architecture, prefetch policy, cache eviction, upload chunking, thumbnail/preview pipeline, observability, rollout guards.

## Ответ (RU)

Лента коротких видео включает автоплей, префетч, кеширование и загрузку контента.

### Архитектура

Модули: feed-ui, player-core (ExoPlayer), media-cache, prefetcher, uploader, analytics, flags. MVVM + UDF; Hilt DI; feature flags для размера сегмента, лестницы битрейтов, глубины prefetch.

### Воспроизведение

HLS/DASH с сегментами ~1с; включить low‑latency режим где доступен. ExoPlayer: фоновый prefetch и быстрый старт; отключен seek pre-roll; переиспользование surface для избежания GL churn.

### Prefetch

Пока просматривается элемент i, префетч первых 2–3 сегментов элемента i+1 и thumbnails для i+2..i+5. Отмена при быстрой прокрутке. Эвристический throttle на metered/low‑battery.

### Кеширование

LRU по last‑played и возрасту с лимитом 300MB; хранить только первые N сегментов для холодных видео для минимизации write‑amplification. Персист позиции просмотра.

### Загрузка

Hardware MediaCodec H.264 (HEVC под флагом); GOP=1с; CBR‑biased VBR. Чанки 4–8MB с SHA‑256; возобновление с offset negotiation; TLS; опционально клиентское AES‑GCM шифрование. Генерация poster frame + blur превью; pre‑upload metadata.

### Фон/Питание

WorkManager для загрузок с constraints; backoff с server hints. Воспроизведение адаптирует битрейт и frame rate при термальных событиях.

### Наблюдаемость

Startup p95, first‑frame time, rebuffer%, cache hit rate, upload retry histogram, crash/ANR. Health gates с автоматическим откатом.

### Тестирование

Throttled networks, CDN outage drills, device matrix perf, process‑death, scroll‑storm тесты.

### Последовательность

MVP (базовое воспроизведение + простая загрузка) → Prefetch/cache → ABR/LL‑HLS → Термальные адаптации.

### Tradeoffs

Короткие сегменты улучшают старт, но добавляют overhead; компенсируем HTTP/2 и настроенным prefetch. HEVC экономит bandwidth, но рискует совместимостью — guard через флаги.

## Answer (EN)

A short-video feed includes autoplay, prefetch, caching, and content upload.

### Architecture

Modules: feed-ui, player-core (ExoPlayer), media-cache, prefetcher, uploader, analytics, flags. MVVM + UDF; Hilt DI; feature flags for segment size, bitrate ladder, prefetch depth.

### Playback

HLS/DASH with ~1s segments; enable low‑latency mode where available. Configure ExoPlayer with background prefetch and fast start; seek pre-roll disabled; surface reuse to avoid GL churn.

### Prefetch

While viewing item i, prefetch first 2–3 segments of i+1 and thumbnails for i+2..i+5. Cancel on rapid scroll. Heuristic throttle on metered/low‑battery.

### Caching

LRU by last‑played and age with 300MB cap; keep first N segments only for cold videos to minimize write‑amplification. Persist watch position.

### Upload

Hardware MediaCodec H.264 (HEVC via flag); GOP=1s; CBR‑biased VBR. Chunk 4–8MB with SHA‑256; resumable with offset negotiation; TLS; optional client‑side AES‑GCM encrypt. Generate poster frame + blurred preview; pre‑upload metadata.

### Background/Power

Rely on WorkManager for uploads with constraints; backoff with server hints. Playback adapts bitrate and frame rate under thermal events.

### Observability

Startup p95, first‑frame time, rebuffer%, cache hit rate, upload retry histogram, crash/ANR. Health gates with automated rollback.

### Testing

Throttled networks, CDN outage drills, device matrix perf, process‑death, scroll‑storm tests.

### Sequencing

MVP (basic playback + simple upload) → Prefetch/cache → ABR/LL‑HLS → Thermal adaptations.

### Tradeoffs

`Short` segments improve start but add overhead; use HTTP/2 and tuned prefetch to compensate. HEVC saves bandwidth but risks compatibility—flag‑guard.

---

## Follow-ups

-   How to handle video encoding failures and retry strategies?
-   What prefetch strategy minimizes bandwidth while ensuring smooth playback?
-   How to optimize battery for continuous autoplay?
-   How to implement efficient cache eviction without impacting playback?

## References

-   [[c-workmanager]]
-   [[c-room]]
-   https://developer.android.com/guide/topics/media/exoplayer
-   [[ANDROID-SYSTEM-DESIGN-CHECKLIST]]
-   [[ANDROID-INTERVIEWER-GUIDE]]

## Related Questions

### Prerequisites (Easier)

-   [[q-design-instagram-stories--android--hard]]

### Related (Same Level)

-   [[q-design-instagram-stories--android--hard]]
-   [[q-data-sync-unstable-network--android--hard]]

### Advanced (Harder)

-   Design a CDN caching strategy for video content at TikTok scale
