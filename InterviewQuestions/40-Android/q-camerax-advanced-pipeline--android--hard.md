---
id: android-614
title: CameraX Advanced Pipeline / Продвинутый pipeline CameraX
aliases:
- CameraX Advanced Pipeline
- Продвинутый pipeline CameraX
topic: android
subtopics:
- camera
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
updated: 2025-11-10
tags:
- android/camerax
- realtime-processing
- difficulty/hard
sources:
- url: "https://developer.android.com/training/camerax"
  note: Official CameraX guide
- url: "https://medium.com/androiddevelopers/camerax-advanced-usage-article"
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
    .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
    .setOutputImageFormat(ImageAnalysis.OUTPUT_IMAGE_FORMAT_YUV_420_888)
    .build().apply {
        setAnalyzer(cameraExecutor, MlAnalyzer(model))
    }

val recorder = Recorder.Builder()
    .setQualitySelector(QualitySelector.from(Quality.HD))
    .build()

val videoCapture = VideoCapture.withOutput(recorder)

cameraProvider.bindToLifecycle(
    lifecycleOwner,
    CameraSelector.DEFAULT_BACK_CAMERA,
    preview,
    analysis,
    videoCapture
)
```

### Краткая версия

- Используйте `ProcessCameraProvider` для биндинга нескольких use case (`Preview`, `ImageAnalysis`, `VideoCapture`).
- Распараллеливайте ML-инференс через выделенный `Executor`/корутины, используйте `STRATEGY_KEEP_ONLY_LATEST`.
- Настраивайте ручные параметры через `Camera2Interop` до биндинга use case.
- Регулируйте разрешение и качество под возможности устройства, следите за backpressure и временем обработки.

### Подробная версия

#### Требования

- Функциональные:
  - Одновременная работа `Preview`, `ImageAnalysis`, `VideoCapture`.
  - Возможность ручного контроля (экспозиция, фокус, ISO) через `Camera2Interop`.
  - Встраивание ML-инференса в реальном времени без заметных лагов.
- Нефункциональные:
  - Низкая задержка предпросмотра и анализа.
  - Стабильная работа на разных устройствах с разными возможностями камеры.
  - Контролируемое потребление ресурсов (CPU/GPU/память).

#### Camera2Interop: ручные настройки

Важно: ручной контроль (AE/AF/ISO/выдержка) через `Camera2Interop` зависит от конкретного устройства и может быть частично ограничен. Опции задаются на `Builder` соответствующего use case до биндинга.

```kotlin
val previewBuilder = Preview.Builder()
val previewExt = Camera2Interop.Extender(previewBuilder)
previewExt.setCaptureRequestOption(
    CaptureRequest.CONTROL_AE_MODE,
    CaptureRequest.CONTROL_AE_MODE_OFF
)
previewExt.setCaptureRequestOption(
    CaptureRequest.SENSOR_EXPOSURE_TIME,
    10_000_000L
)
val preview = previewBuilder.build().apply {
    setSurfaceProvider(previewView.surfaceProvider)
}

val imageCaptureBuilder = ImageCapture.Builder()
val focusExt = Camera2Interop.Extender(imageCaptureBuilder)
focusExt.setCaptureRequestOption(
    CaptureRequest.CONTROL_AF_MODE,
    CaptureRequest.CONTROL_AF_MODE_OFF
)
val imageCapture = imageCaptureBuilder.build()
```

- Через `Extender` можно (в пределах возможностей устройства) управлять экспозицией, ISO, фокусом, HDR, стабилизацией.
- Доступны vendor-extensions для специализированных режимов (HDR, night mode и др.).

#### ML-интеграция без лагов

- Обработка выносится в `Executor` (`newFixedThreadPool`) или `CoroutineDispatcher` — не блокируйте главный поток.
- `ImageAnalysis` должен использовать `setBackpressureStrategy(STRATEGY_KEEP_ONLY_LATEST)` для предотвращения роста очереди.
- Для TensorFlow Lite и других моделей работайте напрямую с `YUV_420_888` через `image.planes` и избегайте лишних конверсий в `Bitmap`.
- При необходимости длительной обработки копируйте данные (copy-out) и как можно раньше закрывайте `ImageProxy` вызовом `image.close()`.

#### Работа с VideoCapture

- Для одновременной записи и анализа используйте `VideoCapture` + `ImageAnalysis`; на слабых устройствах ограничьте разрешение/фреймрейт/битрейт.
- При переключении качества применяйте `unbind`/`bind` с новым `Recorder`/`VideoCapture` — горячая смена большинства параметров ограничена.

#### Управление состоянием камеры

- Используйте `camera.cameraInfo` для мониторинга `zoomState`, `exposureState`.
- Для плавного зума — `camera.cameraControl.setLinearZoom()`.
- Проверяйте `camera.cameraInfo.exposureState.isExposureCompensationSupported` перед изменением компенсации экспозиции.

#### Оптимизация под устройство

- CameraX применяет "quirks" и обходные решения автоматически; учитывайте, что реальные ограничения (например, cap на 30 fps или ограничения manual control) зависят от устройства.
- Используйте `previewView.previewStreamState` для реакции на `STREAMING`/`IDLE` и отображения skeleton UI.
- При проблемах с ресурсами ограничьте одновременно активные use case (например, временно отключите `ImageCapture` или снизьте качество видео).

#### Тестирование и профилирование

- Для unit/UI-тестов pipeline можно использовать `FakeLifecycleOwner` + Robolectric / инструментальные тесты.
- Производительность профилируйте с помощью Android Studio профайлеров и Perfetto (следите за потоками камеры/кодека и задержками анализа).
- Для большей предсказуемости используйте артефакты CameraX Testing и кастомные `CameraFactory`/`CameraXConfig.Provider` для fake-камер.

---

## Answer (EN)

Modern CameraX pipelines orchestrate multiple use cases through `ProcessCameraProvider`. The main goals are parallel processing, low latency, and fine-grained control via `Camera2Interop`.

### Pipeline Architecture

```kotlin
private val cameraExecutor = Executors.newFixedThreadPool(2)

val preview = Preview.Builder()
    .setTargetResolution(Size(1280, 720))
    .build().apply {
        setSurfaceProvider(previewView.surfaceProvider)
    }

val analysis = ImageAnalysis.Builder()
    .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
    .setOutputImageFormat(ImageAnalysis.OUTPUT_IMAGE_FORMAT_YUV_420_888)
    .build().apply {
        setAnalyzer(cameraExecutor, MlAnalyzer(model))
    }

val recorder = Recorder.Builder()
    .setQualitySelector(QualitySelector.from(Quality.HD))
    .build()

val videoCapture = VideoCapture.withOutput(recorder)

cameraProvider.bindToLifecycle(
    lifecycleOwner,
    CameraSelector.DEFAULT_BACK_CAMERA,
    preview,
    analysis,
    videoCapture
)
```

### Short Version

- Use `ProcessCameraProvider` to bind `Preview`, `ImageAnalysis`, and `VideoCapture` together.
- Offload ML inference to dedicated executors/coroutines and use `STRATEGY_KEEP_ONLY_LATEST`.
- Configure manual parameters with `Camera2Interop` on use case builders before binding.
- Tune resolution and quality based on device capabilities; monitor backpressure and processing time.

### Detailed Version

#### Requirements

- Functional:
  - Run `Preview`, `ImageAnalysis`, and `VideoCapture` simultaneously.
  - Provide manual controls (exposure, focus, ISO) via `Camera2Interop`.
  - Integrate real-time ML inference with minimal visible latency.
- Non-functional:
  - Low preview and analysis latency.
  - Robust behavior across devices with varying camera capabilities.
  - Predictable resource usage (CPU/GPU/memory).

#### Manual Controls with Camera2Interop

Note: full manual control (AE/AF/ISO/exposure) via `Camera2Interop` is device-dependent and may be limited. Options must be configured on the corresponding use case builder before binding.

```kotlin
val previewBuilder = Preview.Builder()
val previewExt = Camera2Interop.Extender(previewBuilder)
previewExt.setCaptureRequestOption(
    CaptureRequest.CONTROL_AE_MODE,
    CaptureRequest.CONTROL_AE_MODE_OFF
)
previewExt.setCaptureRequestOption(
    CaptureRequest.SENSOR_EXPOSURE_TIME,
    10_000_000L
)
val preview = previewBuilder.build().apply {
    setSurfaceProvider(previewView.surfaceProvider)
}

val imageCaptureBuilder = ImageCapture.Builder()
val focusExt = Camera2Interop.Extender(imageCaptureBuilder)
focusExt.setCaptureRequestOption(
    CaptureRequest.CONTROL_AF_MODE,
    CaptureRequest.CONTROL_AF_MODE_OFF
)
val imageCapture = imageCaptureBuilder.build()
```

- Use `Extender` (where supported) to adjust exposure, ISO, focus, HDR, and stabilization.
- Vendor extensions enable device-specific HDR or night modes without abandoning CameraX.

#### ML Integration

- Run analyzers on background executors or coroutine dispatchers; never block the main thread.
- Use `STRATEGY_KEEP_ONLY_LATEST` to avoid backpressure and high latency.
- Consume `YUV_420_888` planes directly and avoid unnecessary `Bitmap` conversions.
- For long-running inference, copy frame data out and close `ImageProxy` as early as possible.

#### VideoCapture Considerations

- Combine `VideoCapture` with `ImageAnalysis` cautiously; adjust resolution/frame rate/bitrate for lower-end devices.
- When switching quality profiles, unbind and rebind use cases with a new `Recorder` / `VideoCapture` instance; hot updates are limited.

#### State Management & Optimization

- Use `camera.cameraInfo` for zoom/exposure state and `camera.cameraControl` for smooth zoom (`setLinearZoom`).
- Check `camera.cameraInfo.exposureState.isExposureCompensationSupported` before applying exposure compensation.
- Monitor `previewView.previewStreamState` to update UI when frames start/stop streaming.
- Remember that CameraX applies internal device quirks; capabilities (fps caps, manual controls) vary by device. Disable non-essential use cases or lower quality on constrained devices.

#### Testing & Profiling

- Test with `FakeLifecycleOwner` and Robolectric / instrumentation tests.
- Profile with Android Studio profilers and Perfetto to monitor camera/codec threads and analysis latency.
- Use CameraX Testing artifacts and custom `CameraFactory` / `CameraXConfig.Provider` to run deterministic tests with fake cameras.

---

## Дополнительные вопросы (RU)
- Как реализовать HDR-режим с использованием vendor extension в CameraX?
- Какие ограничения накладывает одновременное использование `VideoCapture` и `ImageCapture`?
- Как организовать ML-инференс на GPU/NNAPI внутри CameraX pipeline?

## Follow-ups
- How can you implement HDR mode using a CameraX vendor extension?
- What constraints arise when using `VideoCapture` and `ImageCapture` simultaneously?
- How would you run ML inference on GPU/NNAPI inside a CameraX pipeline?

## Ссылки (RU)

- [[c-camerax]]
- [CameraX](https://developer.android.com/training/camerax)
- https://medium.com/androiddevelopers/camerax-advanced-usage-article

## References

- [[c-camerax]]
- [CameraX](https://developer.android.com/training/camerax)
- https://medium.com/androiddevelopers/camerax-advanced-usage-article

## Related Questions

- [[c-camerax]]
