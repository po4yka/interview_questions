---
id: android-634
title: Media3 Transformer Workflows / Пайплайны Media3 Transformer
aliases:
  - Media3 Transformer Workflows
  - Пайплайны Media3 Transformer
topic: android
subtopics:
  - media
  - media3
  - editing
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - ru
  - en
status: draft
moc: moc-android
related:
  - c-media3-transformer
  - q-media3-migration-strategy--android--hard
  - q-android-coverage-gaps--android--hard
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/media3
  - android/editing
  - video
  - difficulty/hard
sources:
  - url: https://developer.android.com/guide/topics/media/media3/transformer
    note: Media3 Transformer guide
  - url: https://medium.com/androiddevelopers/media3-transformer-deep-dive
    note: Transformer deep dive
---

# Вопрос (RU)
> Как построить pipeline для редактирования видео на Media3 Transformer: комбинировать клипы, применять эффекты, контролировать кодеки/битрейт, выполнять экспорт в фоне и обрабатывать ошибки?

# Question (EN)
> How do you design a Media3 Transformer pipeline that composes clips, applies effects, manages codec/bitrate choices, exports in the background, and handles errors gracefully?

---

## Ответ (RU)

### 1. Структура Composition

```kotlin
val composition = Composition.Builder(
    EditedMediaItem.Builder(MediaItem.fromUri(uri1))
        .setRemoveAudio(true)
        .setEffects(
            Effects(
                listOf(ColorFilterEffect(ColorMatrix().apply { setSaturation(0.8f) })),
                listOf(VolumeEffect(0.8f))
            )
        )
        .build()
).addEditedMediaItem(
    EditedMediaItem.Builder(MediaItem.fromUri(uri2))
        .setClippingConfiguration(
            EditedMediaItem.ClippingConfiguration.Builder()
                .setStartTimeMs(1_000)
                .setEndTimeMs(10_000)
                .build()
        )
        .build()
).build()
```

- `Composition` объединяет несколько `EditedMediaItem`.
- Эффекты: LUT/ColorMatrix, overlays (`OverlayEffect`), text animations.

### 2. Настройка Transformer

```kotlin
val request = ExportRequest.Builder(context)
    .setComposition(composition)
    .setOutputUri(outputUri)
    .setVideoMimeType(MimeTypes.VIDEO_H264)
    .setResolution(Resolution.HD_1080)
    .setEstimatedBitrate(8_000_000)
    .build()

val transformer = Transformer.Builder(context)
    .setTransformationRequest(
        TransformationRequest.Builder()
            .setVideoMimeType(MimeTypes.VIDEO_H265)
            .setAudioMimeType(MimeTypes.AUDIO_AAC)
            .setResolution(1920, 1080)
            .setEnableFallback(true)
            .build()
    )
    .addListener(listener)
    .build()
```

- Используйте `enableFallback` для перехода на поддерживаемые кодеки.
- Настраивайте target bitrate/resolution, hardware acceleration.

### 3. Фоновая обработка

- Запускайте Transformer в `ForegroundService` или `WorkManager` (Expedited).
- Прогресс через `Transformer.Listener.onProgress(ProgressHolder)` → отправляйте notifications.
- Сохраняйте state (cancel/resume). При сбое cleanup temp files.

### 4. Управление кодеками

- Проверьте `MediaCodecInfo` (profile/level). Если H.265 недоступен → fallback H.264.
- Для HDR → поддержка `ColorTransfer`, `ColorSpace`.
- Аудио: AAC/Opus, bit depth controlling.

### 5. Ошибки

- `TransformationException` → анализируйте `errorCode` (decoder failure, unsupported format).
- Добавьте retry logic с пониженной конфигурацией (720p).
- Логируйте metrics (duration, success rate) для аналитики.

### 6. Тестирование и перформанс

- Тестируйте на разных чипсетах (hardware codecs сильно отличаются).
- Измеряйте экспортное время, memory footprint.
- Используйте `Media3` test utilities (`FakeClock`, instrumentation).

---

## Answer (EN)

- Assemble a `Composition` of `EditedMediaItem` entries with clipping and effects, and configure `Transformer` with desired codecs/resolution and fallback settings.
- Run exports off the main thread via ForegroundService/WorkManager, surfacing progress notifications and handling cancellations.
- Probe codec availability to choose H.265/H.264 and vary bitrate; manage audio settings accordingly.
- Catch `TransformationException` errors, retry with safe presets, and log metrics.
- Validate across devices to ensure hardware codecs work and exports meet latency/quality targets.

---

## Follow-ups
- Как внедрить custom shaders (GLSL) для эффекта блендинга?
- Как реализовать incremental export (resume) при обрыве?
- Какие метрики качества (SSIM/PSNR) стоит собирать в QA?

## References
- [[c-media3-transformer]]
- [[q-media3-migration-strategy--android--hard]]
- [[q-android-coverage-gaps--android--hard]]
- https://developer.android.com/guide/topics/media/media3/transformer
