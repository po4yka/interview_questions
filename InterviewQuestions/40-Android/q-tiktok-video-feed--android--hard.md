---
id: android-486
title: Design TikTok-style Short-Video Feed / Проектирование коротких видео (TikTok-стиль)
aliases: [Design TikTok-style Short-Video Feed, Проектирование коротких видео (TikTok-стиль)]
topic: android
subtopics: [media, performance-rendering, service]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-workmanager, q-design-instagram-stories--android--hard, q-design-uber-app--android--hard, q-implement-voice-video-call--android--hard]
sources: []
created: 2025-10-29
updated: 2025-11-11
tags: [android/media, android/performance-rendering, android/service, difficulty/hard, topic/android]

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

HLS/DASH с сегментами ~1с; включить low‑latency режим где доступен. ExoPlayer: быстрая инициализация, использование CacheDataSource/MediaSource для сегментного кеширования и частично скачанных сегментов, переиспользование surface для избежания GL churn. Seek pre-roll отключён, если продуктом не требуется.

ABR: ограничивать варианты профилями устройства и сети; prefetch ориентировать на текущий/ожидаемый bitrate, чтобы не тратить трафик и кеш.

### Prefetch

Пока просматривается элемент i, префетч первых 2–3 сегментов i+1 (с учётом выбранного/ожидаемого bitrate) и thumbnails для i+2..i+5. Prefetch выполняется только при активном экране/foreground-сценарии, отменяется при быстрой прокрутке. Эвристический throttle на metered/low‑battery.

### Кеширование

LRU по last‑played и возрасту с лимитом 300MB. Использовать сегментный кеш (ExoPlayer Cache) и хранить только первые N сегментов для холодных видео для минимизации write‑amplification. Гарантировать неполный кеш (частичные сегменты) для быстрого старта на следующем просмотре. Персист позиции просмотра.

### Загрузка

Hardware MediaCodec H.264 (HEVC под флагом); GOP=1с; CBR‑biased VBR. Чанки 4–8MB с SHA‑256; возобновление с offset negotiation; TLS; опционально клиентское AES‑GCM шифрование.

Для длинных/критичных загрузок использовать Foreground `Service` + WorkManager (expedited / с ограничениями) в соответствии с требованиями Android 11–15, с видимым уведомлением для пользователя. Генерация poster frame + blur превью на устройстве; отправка pre‑upload metadata.

### Фон/Питание

WorkManager для отложенных загрузок с constraints; backoff с server hints. Prefetch ограничивать только foreground-воспроизведением, без долгоживущих фоновых задач, чтобы не нарушать ограничения ОС.

Воспроизведение адаптирует bitrate и (при необходимости) frame rate при термальных событиях через callbacks thermal API/PerformanceHint и настройки ExoPlayer (ограничение резолюции/bitrate).

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

Use HLS/DASH with ~1s segments; enable low-latency mode where available. Configure ExoPlayer for fast startup, using CacheDataSource/MediaSource for segment-level caching and partial segment reuse; reuse the same Surface to avoid GL churn. Disable seek pre-roll if not required by the product.

ABR: constrain variants based on device/network profiles; align prefetch with the current/likely bitrate to avoid wasting bandwidth and cache.

### Prefetch

While viewing item i, prefetch the first 2–3 segments of i+1 (using the selected/expected bitrate) and thumbnails for i+2..i+5. Run prefetch only while the app/screen is in foreground and cancel on rapid scroll. Apply heuristic throttling on metered networks / low battery.

### Caching

Use an LRU policy by last-played and age with a 300MB cap. Rely on ExoPlayer's segment cache; for cold videos store only the first N segments to reduce write amplification. Allow partial cache for segments to speed up future starts. Persist watch position.

### Upload

Use hardware MediaCodec for H.264 (HEVC behind a flag); GOP=1s; CBR-biased VBR. Chunk uploads into 4–8MB pieces with SHA-256; support resumable uploads with offset negotiation; use TLS; optionally encrypt chunks client-side with AES-GCM.

For long/critical uploads, use a Foreground `Service` combined with WorkManager (expedited/with constraints) per Android 11–15 requirements, with a visible notification so the OS does not kill the job silently. Generate a poster frame + blurred preview on-device; send pre-upload metadata.

### Background/Power

Use WorkManager for deferred uploads with constraints; apply backoff with server hints. Restrict prefetch to foreground playback (no long-running background prefetch loops) to comply with OS limits.

Handle thermal events by adapting bitrate and, if needed, frame rate using thermal/PerformanceHint APIs and ExoPlayer configuration (e.g., cap resolution/bitrate on high thermal states).

### Observability

Track startup p95, first-frame time, rebuffer%, cache hit rate, upload retry histogram, crash/ANR. Use health gates with automated rollback.

### Testing

Test with throttled networks, CDN outage drills, a representative device matrix for performance, process-death, and scroll-storm scenarios.

### Sequencing

MVP (basic playback + simple upload) → Prefetch/cache → ABR/LL-HLS → Thermal adaptations.

### Tradeoffs

Short segments improve startup but add overhead; mitigate via HTTP/2 and tuned prefetch. HEVC saves bandwidth but has compatibility risks—protect behind flags.

---

## Дополнительные Вопросы (RU)

- Как обрабатывать ошибки кодирования видео и стратегии повторных попыток?
- Какая стратегия prefetch минимизирует трафик при сохранении плавного воспроизведения?
- Как оптимизировать расход батареи для непрерывного автоплея?
- Как реализовать эффективную эвикцию кеша без влияния на воспроизведение?

## Follow-ups

- How to handle video encoding failures and retry strategies?
- What prefetch strategy minimizes bandwidth while ensuring smooth playback?
- How to optimize battery for continuous autoplay?
- How to implement efficient cache eviction without impacting playback?

## Ссылки (RU)

- [[c-workmanager]]
- https://developer.android.com/guide/topics/media/exoplayer

## References

- [[c-workmanager]]
- https://developer.android.com/guide/topics/media/exoplayer

## Связанные Вопросы (RU)

### Предпосылки (проще)

- [[q-design-instagram-stories--android--hard]]

### Связанные (того Же уровня)

- [[q-design-instagram-stories--android--hard]]
- [[q-data-sync-unstable-network--android--hard]]

### Продвинутые (сложнее)

- Спроектируйте стратегию CDN-кеширования для видео-контента на масштабе TikTok

## Related Questions

### Prerequisites (Easier)

- [[q-design-instagram-stories--android--hard]]

### Related (Same Level)

- [[q-design-instagram-stories--android--hard]]
- [[q-data-sync-unstable-network--android--hard]]

### Advanced (Harder)

- Design a CDN caching strategy for video content at TikTok scale
