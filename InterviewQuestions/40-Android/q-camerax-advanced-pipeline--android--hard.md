---
id: android-614
title: CameraX Advanced Pipeline / Продвинутый pipeline CameraX
aliases:
  - CameraX Advanced Pipeline
  - Продвинутый pipeline CameraX
topic: android
subtopics:
  - camera
  - camerax
  - imaging
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - ru
  - en
status: draft
moc: moc-android
related:
  - c-camerax
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/camerax
  - android/imaging
  - realtime-processing
  - difficulty/hard
sources:
  - url: https://developer.android.com/training/camerax
    note: Official CameraX guide
  - url: https://medium.com/androiddevelopers/camerax-advanced-usage-article
    note: Advanced CameraX best practices
---

# Вопрос (RU)
> Как построить продвинутый pipeline с CameraX: объединить Preview, ImageAnalysis и VideoCapture, вручную контролировать экспозицию/фокус и интегрировать ML-обработку кадров без лагов?

# Question (EN)
> How do you design an advanced CameraX pipeline that combines Preview, ImageAnalysis, and VideoCapture, while manually controlling exposure/focus and integrating ML processing with minimal latency?

---

## Ответ (RU)

Современный pipeline CameraX строится вокруг `ProcessCameraProvider` и нескольких use case. Ключевые задачи — правильно распараллелить обработку, минимизировать лаги и удерживать контроль над камерой через `Camera2Interop`.

### Архитектура Pipeline

```kotlin
private val cameraExecutor = Executors.newFixedThreadPool(2)

val preview = Preview.Builder()
    .setTargetResolution(Size(1280, 720))
    .build().apply {
        setSurfaceProvider(previewView.surfaceProvider)
    }

val analysis = ImageAnalysis.Builder()
    .setBackpressureStrategy(STRATEGY_KEEP_ONLY_LATEST)
    .setOutputImageFormat(IMAGE_FORMAT_YUV_420_888)
    .build().apply {
        setAnalyzer(cameraExecutor, MlAnalyzer(model))
    }

val videoCapture = VideoCapture.Builder()
    .setVideoFrameRate(60)
    .setBitRate(16_000_000)
    .build()

cameraProvider.bindToLifecycle(
    lifecycleOwner,
    CameraSelector.DEFAULT_BACK_CAMERA,
    preview,
    analysis,
    videoCapture
)
```

### Camera2Interop: ручные настройки

```kotlin
val exposureExt = Camera2Interop.Extender(preview)
exposureExt.setCaptureRequestOption(
    CaptureRequest.CONTROL_AE_MODE,
    CaptureRequest.CONTROL_AE_MODE_OFF
)
exposureExt.setCaptureRequestOption(
    CaptureRequest.SENSOR_EXPOSURE_TIME,
    10_000_000L
)

val focusExt = Camera2Interop.Extender(imageCapture)
focusExt.setCaptureRequestOption(
    CaptureRequest.CONTROL_AF_MODE,
    CaptureRequest.CONTROL_AF_MODE_OFF
)
```

- Через `Extender` можно управлять ISO, фокусом, HDR, стабилизацией.
- Доступны vendor-extensions (`Camera2Interop.Extender#implOptions`) для специализированных камер.

### ML-интеграция без лагов

- Обработка выносится в `Executor` (`newFixedThreadPool`) или `CoroutineDispatcher`.
- `ImageAnalysis` должен использовать `setBackpressureStrategy(STRATEGY_KEEP_ONLY_LATEST)` для предотвращения очередей.
- Для TensorFlow Lite используйте плоские ByteBuffer (`image.planes`) и избегайте конверсии в `Bitmap`.
\n- При необходимости дублируйте буфер (copy out) и быстро закрывайте `ImageProxy` (`image.close()`).

### Работа с VideoCapture

- Для одновременной записи и анализа используйте `VideoCapture` + `ImageAnalysis`; однако на слабых устройствах ограничьте разрешение/фреймрейт.
- При переключении качества применяйте `Unbind/Bind` с новым builder (горячая смена параметров ограничена).

### Управление состоянием камеры

- Используйте `Camera.cameraInfo` для мониторинга `zoomState`, `exposureState`.
- Для плавного zoom — `camera.cameraControl.setLinearZoom()`.
- Актуальные `CameraInfo.exposureState.isExposureCompensationSupported`.

### Оптимизация под устройство

- Изучите `CameraInfo.cameraQuirks` — CameraX автоматически применяет обходы, но стоит учитывать ограничения (например, 30fps cap).
- Используйте `previewView.previewStreamState` для реакции на `STREAMING`/`IDLE` и отображения skeleton UI.
- При проблемах с памятью ограничьте одновременно активные use case (например, выключите `ImageCapture`).

### Тестирование и профилирование

- UI тесты — через `FakeLifecycleOwner` + Robolectric.
- Performance профилируется `Frame profiler` и `Perfetto` (следите за `Camera` и `Binder` потоками).
- Для стабильности на реальных устройствах применяйте `CameraX Testing` extension (`CameraXConfig.Provider` с `CameraFactory` fake).

---

## Answer (EN)

Modern CameraX pipelines orchestrate multiple use cases through `ProcessCameraProvider`. The main goals are parallel processing, low latency, and fine-grained control via `Camera2Interop`.

### Pipeline Architecture

- Configure Preview, ImageAnalysis, and VideoCapture together while sharing a lifecycle.
- Use dedicated executors (`newFixedThreadPool`) for analysis to avoid blocking the main thread.
- Leverage `STRATEGY_KEEP_ONLY_LATEST` to prevent backpressure.

### Manual Controls with Camera2Interop

- Attach `Camera2Interop.Extender` to each use case to tweak `CaptureRequest` options (AE/AF modes, exposure, ISO).
- Vendor extensions enable device-specific HDR or night modes without abandoning CameraX.

### ML Integration

- Run analyzers on background threads; extract `YUV_420_888` planes directly for ML.
- Always close `ImageProxy` promptly; copy data if longer processing is needed.

### VideoCapture Considerations

- Combine `VideoCapture` with `ImageAnalysis` cautiously; adjust bitrate/resolution for lower-end phones.
- Rebind use cases when switching quality profiles; hot parameter changes are limited.

### State Management & Optimization

- Use `cameraInfo` for zoom/exposure states and `cameraControl` to apply smooth zoom.
- Monitor `previewStreamState` to update UI when frames start flowing.
- Understand device quirks; disable non-essential use cases when resource constrained.

### Testing & Profiling

- Exercise pipelines with Robolectric + `FakeLifecycleOwner`.
- Profile using `Perfetto` and Android Studio profilers to monitor camera/codec threads.
- Use `CameraX Testing` artifacts for deterministic tests with fake camera implementations.

---

## Follow-ups
- Как реализовать HDR-режим с использованием vendor extension в CameraX?
- Какие ограничения накладывает одновременное использование VideoCapture и ImageCapture?
- Как организовать ML-инференс на GPU/NNAPI внутри CameraX pipeline?

## References

- [[c-camerax]]
- [CameraX](https://developer.android.com/training/camerax)
- https://medium.com/androiddevelopers/camerax-advanced-usage-article


## Related Questions

- [[c-camerax]]
