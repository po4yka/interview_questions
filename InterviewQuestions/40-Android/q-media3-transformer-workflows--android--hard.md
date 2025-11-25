---
id: android-634
title: Media3 Transformer Workflows / Пайплайны Media3 Transformer
aliases: [Media3 Transformer Workflows, Пайплайны Media3 Transformer]
topic: android
subtopics:
  - files-media
  - media
question_kind: theory
difficulty: hard
original_language: ru
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-android
  - q-dagger-build-time-optimization--android--medium
  - q-data-sync-unstable-network--android--hard
  - q-media3-migration-strategy--android--hard
created: 2025-11-02
updated: 2025-11-10
tags: [android/files-media, android/media, difficulty/hard]
sources:
- url: "https://developer.android.com/guide/topics/media/media3/transformer"
  note: Media3 Transformer guide
- url: "https://medium.com/androiddevelopers/media3-transformer-deep-dive"
  note: Transformer deep dive

date created: Thursday, November 6th 2025, 4:39:51 pm
date modified: Tuesday, November 25th 2025, 8:53:58 pm
---

# Вопрос (RU)
> Как построить pipeline для редактирования видео на Media3 Transformer: комбинировать клипы, применять эффекты, контролировать кодеки/битрейт, выполнять экспорт в фоне и обрабатывать ошибки?

# Question (EN)
> How do you design a Media3 Transformer pipeline that composes clips, applies effects, manages codec/bitrate choices, exports in the background, and handles errors gracefully?

---

## Ответ (RU)

## Краткая Версия
- Использовать `Composition` + `EditedMediaItem` для сборки таймлайна.
- Настроить `TransformationRequest` (кодек, битрейт, разрешение, fallback) и запустить через `Transformer`.
- Выполнять экспорт в фоне (`ForegroundService`/`WorkManager` при соблюдении ограничений), отслеживать прогресс и ошибки через `Transformer.Listener`.
- Проверять доступные кодеки (`MediaCodecList`) и реализовать fallback-стратегии.
- Логировать метрики и тестировать на разных устройствах.

## Подробная Версия
### 1. Структура Composition

```kotlin
val editedItem1 = EditedMediaItem.Builder(MediaItem.fromUri(uri1))
    .setEffects(
        Effects(
            listOf(ColorFilterEffect(ColorMatrix().apply { setSaturation(0.8f) })),
            listOf(VolumeEffect(0.8f))
        )
    )
    // При одновременном использовании аудио-эффектов и removeAudio следует учитывать,
    // что removeAudio удалит дорожку и эффекты к ней не применятся.
    // .setRemoveAudio(true)
    .build()

val editedItem2 = EditedMediaItem.Builder(MediaItem.fromUri(uri2))
    .setClippingConfiguration(
        EditedMediaItem.ClippingConfiguration.Builder()
            .setStartTimeMs(1_000)
            .setEndTimeMs(10_000)
            .build()
    )
    .build()

val composition = Composition.Builder(editedItem1)
    .addEditedMediaItem(editedItem2)
    .build()
```

- `Composition` объединяет несколько `EditedMediaItem` для последовательного воспроизведения/экспорта в один трек.
- Эффекты: LUT/ColorMatrix, overlays (`OverlayEffect`), текст, анимации и другие video/audio эффекты через `Effects`.

### 2. Требования

- Функциональные:
  - Комбинация нескольких клипов в один итоговый ролик.
  - Применение цветокоррекции, оверлеев, текста, аудио/видео-эффектов.
  - Настройка кодеков, битрейта, разрешения, со звуком/без.
  - Фоновый экспорт с прогрессом и возможностью отмены.
  - Обработка ошибок и fallback-конфигураций.
- Нефункциональные:
  - Стабильность на разных устройствах и версиях Android.
  - Приемлемое время экспорта и энергопотребление.
  - Предсказуемое поведение при ограничениях кодеков/железа.

### 3. Архитектура

- Слой конфигурации:
  - Модуль, формирующий `Composition` и `EditedMediaItem` на основе пользовательского сценария.
  - Модуль, формирующий `TransformationRequest` (кодек, битрейт, разрешение, `setEnableFallback(true)`).
- Слой выполнения:
  - Обертка над `Transformer`, запускаемая из `ForegroundService` или `WorkManager` worker-а (с учетом ограничений долгих задач).
  - Подписка на `Transformer.Listener` для прогресса (`onProgress`), завершения (`onCompleted`) и ошибок (`onError`).
- Слой совместимости и аналитики:
  - Проверка кодеков через `MediaCodecList`/`MediaCodecInfo`.
  - Fallback-логика (смена кодека, понижение разрешения/битрейта).
  - Логирование метрик исполнения.

### 4. Настройка Transformer

```kotlin
val transformationRequest = TransformationRequest.Builder()
    .setVideoMimeType(MimeTypes.VIDEO_H265) // целевой кодек; при отсутствии возможен фоллбэк
    .setAudioMimeType(MimeTypes.AUDIO_AAC)
    .setVideoEncodingBitrate(8_000_000)
    // setResolution(int) в текущем API задает целевой размер (одна сторона),
    // точная сигнатура зависит от версии Media3; использовать актуальный метод.
    .setResolution(1080)
    .setEnableFallback(true) // разрешить понижение параметров/смену кодека при неподдержке
    .build()

val transformer = Transformer.Builder(context)
    .setTransformationRequest(transformationRequest)
    .addListener(listener)
    .build()

transformer.start(composition, outputPath)
```

- Используйте `setEnableFallback(true)` для автоматического перехода на поддерживаемые конфигурации (кодек, профиль, разрешение, битрейт).
- Настраивайте целевые `mimeType`, `bitrate`, `resolution`; по умолчанию Transformer старается сохранить исходные параметры.
- Учитывайте, что конкретные доступные конфигурации зависят от `MediaCodec` на устройстве.

### 5. Фоновая Обработка

- `Transformer.start(...)` асинхронен, но сам процесс ресурсоемкий, поэтому его жизненный цикл должен быть привязан к компоненту,
  который система не уничтожит произвольно.
- Для длительных экспортов используйте `ForegroundService` с foreground-уведомлением; `WorkManager` может использоваться,
  если вы учитываете его политику для долгих/foreground задач.
- Прогресс: используйте `Transformer.Listener.onProgress(progressHolder)` и/или `onCompleted`/`onError` для обновления уведомлений.
- Обрабатывайте cancel (например, через `transformer.cancel()`) и при завершении/сбое очищайте временные файлы.

### 6. Управление Кодеками

- При необходимости явно проверяйте доступность кодеков через `MediaCodecList`/`MediaCodecInfo` (поддерживаемые MIME, profile/level), чтобы выбирать между H.265 и H.264.
- Для HDR учитывайте поддержку `ColorTransfer`, `ColorSpace`, `ColorRange`; при отсутствии поддерживающих кодеков/поверхностей используйте SDR fallback.
- Аудио: задавайте MIME (например, AAC, Opus при поддержке), каналы, sample rate и bitrate через соответствующие настройки; произвольное управление битностью сэмплов через high-level API недоступно.

### 7. Ошибки

- Обрабатывайте `TransformationException` в `Transformer.Listener.onError`, анализируйте `errorCode` (например, decoder/encoder failure, unsupported format, file I/O ошибки).
- Добавьте retry-логику с более консервативной конфигурацией (например, понижение разрешения до 720p или переключение на H.264).
- Логируйте метрики (длительность обработки, процент успеха, распределение по устройствам) для диагностики и последующей оптимизации.

### 8. Тестирование И Перформанс

- Тестируйте на разных чипсетах и версиях Android: поддержка hardware-кодеков и стабильность заметно различаются.
- Измеряйте время экспорта, использование памяти и влияние на температуру/троттлинг.
- Автоматизируйте сценарии экспорта (разные форматы, длина, разрешения, эффекты), используя доступные Media3 тестовые утилиты и instrumentation-тесты, чтобы отлавливать регрессии.

---

## Answer (EN)

## Short Version
- Use `Composition` + `EditedMediaItem` to build the editing timeline.
- Configure `TransformationRequest` (codec, bitrate, resolution, fallback) and run via `Transformer`.
- Execute in background (`ForegroundService`/`WorkManager` with constraints) and track progress and errors via `Transformer.Listener`.
- Probe codecs (`MediaCodecList`) and implement fallback strategies.
- Log metrics and test across devices.

## Detailed Version
### 1. Composition Structure

```kotlin
val editedItem1 = EditedMediaItem.Builder(MediaItem.fromUri(uri1))
    .setEffects(
        Effects(
            listOf(ColorFilterEffect(ColorMatrix().apply { setSaturation(0.8f) })),
            listOf(VolumeEffect(0.8f))
        )
    )
    // When combining audio effects with removeAudio, note that removeAudio will drop the track
    // and the audio effects will not be applied.
    // .setRemoveAudio(true)
    .build()

val editedItem2 = EditedMediaItem.Builder(MediaItem.fromUri(uri2))
    .setClippingConfiguration(
        EditedMediaItem.ClippingConfiguration.Builder()
            .setStartTimeMs(1_000)
            .setEndTimeMs(10_000)
            .build()
    )
    .build()

val composition = Composition.Builder(editedItem1)
    .addEditedMediaItem(editedItem2)
    .build()
```

- `Composition` joins multiple `EditedMediaItem` instances into a single sequential track for playback/export.
- Effects: LUT/ColorMatrix, overlays (`OverlayEffect`), text, animations, and other video/audio effects via `Effects`.

### 2. Requirements

- Functional:
  - Combine multiple clips into a single final video.
  - Apply color correction, overlays, text, and audio/video effects.
  - Control codec, bitrate, resolution, and audio presence.
  - Run export in background with progress reporting and cancellation.
  - Handle errors and apply fallback configurations.
- Non-functional:
  - Robust behavior across devices and Android versions.
  - Reasonable export time and power usage.
  - Predictable behavior under codec/hardware constraints.

### 3. Architecture

- Configuration layer:
  - Module building `Composition` and `EditedMediaItem` from user scenarios.
  - Module building `TransformationRequest` (codec, bitrate, resolution, `setEnableFallback(true)`).
- Execution layer:
  - Wrapper around `Transformer` invoked from a `ForegroundService` or a `WorkManager` worker (respecting long-running work constraints).
  - Use `Transformer.Listener` for progress (`onProgress`), completion (`onCompleted`), and errors (`onError`).
- Compatibility and analytics layer:
  - Codec probing via `MediaCodecList`/`MediaCodecInfo`.
  - Fallback logic (codec switch, downscaling/bitrate reduction).
  - Execution metrics logging.

### 4. Transformer Configuration

```kotlin
val transformationRequest = TransformationRequest.Builder()
    .setVideoMimeType(MimeTypes.VIDEO_H265) // target codec; fallback may be needed
    .setAudioMimeType(MimeTypes.AUDIO_AAC)
    .setVideoEncodingBitrate(8_000_000)
    // setResolution(int) in current APIs sets the target size (one dimension);
    // use the concrete signature available in your Media3 version.
    .setResolution(1080)
    .setEnableFallback(true) // allow downgrade/codec switch if unsupported
    .build()

val transformer = Transformer.Builder(context)
    .setTransformationRequest(transformationRequest)
    .addListener(listener)
    .build()

transformer.start(composition, outputPath)
```

- Use `setEnableFallback(true)` so Transformer can automatically switch to supported codec/profile/resolution/bitrate.
- Tune target `mimeType`, bitrate, and resolution; by default Transformer attempts to preserve source properties.
- Valid configurations depend on the available `MediaCodec` implementations on the device.

### 5. Background Execution

- `Transformer.start(...)` is asynchronous, but the transformation is resource-intensive, so tie it to a component that the system will keep alive for its duration.
- For long-running exports, prefer a `ForegroundService` with a proper foreground notification; `WorkManager` can be used when its execution and foreground constraints fit your case.
- Use `Transformer.Listener.onProgress(progressHolder)` and `onCompleted`/`onError` to update notifications and UI.
- Support cancellation (e.g., `transformer.cancel()`) and clean up temporary/partial files on completion or failure.

### 6. Codec Management

- When needed, probe codecs using `MediaCodecList`/`MediaCodecInfo` (supported MIME, profile/level) to choose between H.265 and H.264.
- For HDR, consider `ColorTransfer`, `ColorSpace`, and `ColorRange`; if unsupported by codecs/surfaces, fall back to SDR.
- For audio, choose supported MIME types (e.g., AAC, Opus where available), channels, sample rate, and bitrate; arbitrary sample bit depth control is not exposed via the high-level API.

### 7. Error Handling

- Handle `TransformationException` in `Transformer.Listener.onError` and inspect `errorCode` (decoder/encoder failures, unsupported format, file I/O issues, etc.).
- Add retry logic with more conservative presets (e.g., downscale to 720p or switch to H.264) when errors indicate capability limits.
- Log metrics such as processing duration, success rate, and device distribution to diagnose issues and guide optimization.

### 8. Testing and Performance

- Test across diverse chipsets and Android versions: hardware codec support and stability vary significantly.
- Measure export time, memory usage, and thermal/throttling impact.
- Automate export scenarios (different formats, durations, resolutions, effects) using Media3 test utilities and instrumentation tests to catch regressions.

---

## Follow-ups
- Как внедрить custom shaders (GLSL) для эффекта блендинга?
- Как реализовать incremental export (resume) при обрыве?
- Какие метрики качества (SSIM/PSNR) стоит собирать в QA?

## References
- [[q-media3-migration-strategy--android--hard]]
- [[c-android]]
- https://developer.android.com/guide/topics/media/media3/transformer

## Related Questions

- [[q-media3-migration-strategy--android--hard]]
