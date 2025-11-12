---
id: android-629
title: TFLite Acceleration Strategies / Стратегии ускорения TFLite
aliases:
- TFLite Acceleration Strategies
- Стратегии ускорения TFLite
topic: android
subtopics:
- performance-battery
- performance-memory
- threads-sync
question_kind: android
difficulty: hard
original_language: ru
language_tags:
- ru
- en
status: draft
moc: moc-android
related:
- c-android-profiling
- q-android-performance-measurement-tools--android--medium
created: 2025-11-02
updated: 2025-11-11
tags:
- android/performance-battery
- android/performance-memory
- android/threads-sync
- performance
- difficulty/hard
sources:
- "https://www.tensorflow.org/lite/performance/delegates"
- "https://firebase.google.com/docs/ml/manage-hosted-models"

---

# Вопрос (RU)
> Как построить высокопроизводительный pipeline on-device ML на Android: подготовить модель, включить NNAPI/GPU delegate, организовать поток выполнения и обновлять модель по воздуху?

# Question (EN)
> How do you build a high-performance on-device ML pipeline on Android, including model optimization, NNAPI/GPU delegation, execution threading, and over-the-air model updates?

---

## Ответ (RU)

## Краткая Версия
- Оптимизировать модель под TFLite (квантование, упрощение графа).
- Memory-map'ить модель и переиспользовать один/несколько интерпретаторов.
- Динамически выбирать NNAPI/GPU/CPU delegate с надёжным fallback.
- Выполнять inference вне UI-потока, с очередью запросов и контролем частоты.
- Обновлять модель OTA с проверкой целостности и безопасным rollback.
- Мониторить latency/ошибки/делегаты, адаптируя конфигурацию.

## Подробная Версия

### Требования (RU)
- Функциональные:
  - Он-дивайс inference без сетевой зависимости.
  - Поддержка нескольких делегатов (CPU/NNAPI/GPU) с fallback.
  - OTA-обновления модели без остановки приложения.
  - Поддержка real-time/near-real-time use-case'ов (камера, стримы).
- Нефункциональные:
  - Низкая латентность и вариативность задержек.
  - Контролируемое потребление батареи и памяти.
  - Надёжность (fallback при сбоях делегатов/модели).
  - Наблюдаемость: метрики, логи, краши.

### Архитектура (RU)
- Отдельный модуль/слой для ML pipeline (загрузка модели, делегаты, очередь запросов).
- Одна или несколько long-lived копий `Interpreter`, управляемые через пул.
- Компонент для выбора делегата (feature detection + конфигурация с сервера).
- Компонент OTA-обновлений модели (Downloader + верификация + hot-swap с fallback).
- Интеграция с системой телеметрии (логирование делегатов, версий моделей, латентности).

#### 1. Подготовка модели

- Используйте `tf.lite.TFLiteConverter` с оптимизациями через `converter.optimizations = [tf.lite.Optimize.DEFAULT]`, применяйте post-training quantization (динамическая, full integer) и/или проводите quantization-aware training на стороне обучения до конвертации.
- При целевом использовании NNAPI/других делегатов проверяйте совместимость операторов (поддержка INT8/FP16, отсутствие редких/нестандартных ops); понимайте, какие части графа реально пойдут через делегат, а какие останутся на CPU.
- Для больших моделей минимизируйте использование `FlexDelegate` (он тянет TF runtime и ухудшает размер/latency) и по возможности избегайте TensorFlow ops вне основного TFLite набора.

#### 2. Загрузка и кеш

```kotlin
val fileDescriptor = context.assets.openFd("model.tflite")
val inputStream = FileInputStream(fileDescriptor.fileDescriptor)
val mapped = inputStream.channel.map(
    FileChannel.MapMode.READ_ONLY,
    fileDescriptor.startOffset,
    fileDescriptor.declaredLength
)
```

- Маппинг через `ByteBuffer` снижает накладные расходы на загрузку и уменьшает пиковое потребление памяти. Важно: такой подход работает только для неупакованных (uncompressed) assets; для сжатых используйте файл во внутреннем хранилище.
- Для OTA используйте `ModelDownloader` (Firebase ML) или собственный CDN + проверку целостности (hash, подпись) и хранение локального файла, который затем memory-map'ится аналогично.

#### 3. Делегаты

```kotlin
val gpuDelegate = GpuDelegate(GpuDelegate.Options().apply {
    // См. актуальные поля Options; FAST_SINGLE_ANSWER задаётся через соответствующий enum/флаг
})

val nnapiDelegate = NnApiDelegate(NnApiDelegate.Options().apply {
    setAllowFp16(true)
})

val options = Interpreter.Options().apply {
    // Делегаты не комбинируйте без необходимости, выбирайте один наиболее подходящий.
    addDelegate(selectDelegate())
    // Количество потоков влияет только на CPU backend, делегаты обычно игнорируют этот параметр.
    setNumThreads(4)
}

val interpreter = Interpreter(mapped, options)
```

- GPU delegate подходит для conv-heavy computer vision моделей и даёт выигрыш при достаточно больших батчах/тензорах; основан на OpenGL/Vulkan, доступность и производительность зависят от устройства.
- NNAPI delegate — универсальный слой над аппаратными акселераторами OEM; поведение зависит от реализации драйверов. Не все операторы и типы (например, INT8/FP16) гарантированно поддержаны.
- Выбирайте делегат динамически (feature detection, проверка доступности/поддержки) и всегда обеспечивайте падение обратно на CPU: перехватывайте ошибки делегата (`IllegalArgumentException`/`UnsupportedOperationException`/внутренние ошибки) и пересоздавайте интерпретатор без делегата.

#### 4. Потоки и батчинг

- Выполняйте inference на `HandlerThread`/`Executors`/корутинах, чтобы не блокировать UI.
- Поддерживайте очередь запросов (например, через `Channel`/`Flow` или собственный пул), чтобы избегать contention и не создавать интерпретатор на каждый запрос.
- Для видеопотоков снижайте частоту inference и/или используйте `ImageAnalysis` с `setBackpressureStrategy(KEEP_ONLY_LATEST)` вместо ручного накопления очереди.

#### 5. OTA обновления

- Для Firebase Model Downloader: используйте `getModel(name, DownloadType.LOCAL_MODEL)`/`getModelDetails` и регистрируйте observer/worker, обновляющий локальный файл и перезагружающий интерпретатор безопасно.
- Верифицируйте hash и подпись скачанной модели. Храните текущую и предыдущую версии (например, в Proto DataStore), чтобы иметь возможность rollback.
- Планируйте поэтапный rollout через Feature Flag и всегда держите встроенную (bundled) модель как fallback.

#### 6. Мониторинг

- Логируйте latency, chosen delegate type, события fallback с делегатов на CPU, а также частоту ошибок.
- Используйте `PerformanceTrace` (Firebase Performance) или собственные метрики/логирование для разных версий модели и конфигураций делегатов.
- Собирайте crash dumps и отчёты: делегаты (особенно NNAPI/GPU на старых драйверах) могут приводить к нестабильности; при выявлении проблем динамически отключайте проблемный делегат для затронутых устройств.

#### 7. Ссылки на концепции

- См. также: [[c-android-profiling]]

---

## Answer (EN)

## Short Version
- Optimize the model for TFLite (quantization, pruning/simplified graph).
- Memory-map the model and reuse a small number of interpreters.
- Dynamically choose NNAPI/GPU/CPU delegate with robust fallback.
- Run inference off the main thread with a request queue and controlled rates.
- Update models OTA with integrity checks and safe rollback.
- Monitor latency/errors/delegate usage and adapt configuration.

## Detailed Version

### Requirements
- Functional:
  - On-device inference without hard dependency on network.
  - Support for multiple delegates (CPU/NNAPI/GPU) with fallback.
  - OTA model updates without breaking running flows.
  - Support for real-time/near-real-time use cases (camera, streaming).
- Non-functional:
  - Low latency and predictable performance.
  - Controlled battery and memory usage.
  - High reliability (fallback on delegate/model failures).
  - Observability via metrics, logs, crash reports.

### Architecture
- Dedicated ML pipeline module/layer (model loading, delegates, request queue).
- One or more long-lived `Interpreter` instances managed via a pool.
- Delegate selection component (feature detection + remote configuration).
- OTA model update component (downloader + verification + hot-swap with fallback).
- Telemetry integration (log delegates, model versions, latencies).

#### 1. Model preparation

- Use `tf.lite.TFLiteConverter` with `converter.optimizations = [tf.lite.Optimize.DEFAULT]`, apply post-training quantization (dynamic or full integer) and/or quantization-aware training before conversion.
- When targeting NNAPI/other delegates, verify operator and dtype compatibility (INT8/FP16, no rare/custom ops); understand which graph segments will actually run on the delegate vs CPU.
- Minimize `FlexDelegate` usage for large models because it pulls in the full TensorFlow runtime and significantly increases binary size and can hurt startup/latency; whenever possible, stay within the native TFLite operator set.

#### 2. Loading and cache

- Memory-map the `.tflite` file (for uncompressed assets or a downloaded file) using a `ByteBuffer` to reduce load time and peak memory usage. For compressed assets, first write the model to internal storage, then memory-map it from there.
- For OTA, use Firebase ML `ModelDownloader` or your own CDN plus integrity checks (hash/signature), then memory-map the verified local file in the same way.

#### 3. Delegates

- Configure delegates similarly to:

```kotlin
val gpuDelegate = GpuDelegate(GpuDelegate.Options().apply {
    // See current Options fields; use appropriate flags such as FAST_SINGLE_ANSWER if available.
})

val nnapiDelegate = NnApiDelegate(NnApiDelegate.Options().apply {
    setAllowFp16(true)
})

val options = Interpreter.Options().apply {
    // Do not combine multiple delegates unless you have a strong reason; pick the most appropriate one.
    addDelegate(selectDelegate())
    // Thread count only affects the CPU backend; most delegates ignore this setting.
    setNumThreads(4)
}

val interpreter = Interpreter(mapped, options)
```

- Use GPU delegate for conv-heavy vision models where the device GPU/driver is stable.
- Use NNAPI as an abstraction over vendor accelerators; behavior and supported ops/dtypes depend on OEM drivers.
- Select the delegate dynamically via feature detection; always provide a robust CPU fallback: catch delegate-related failures (e.g., `IllegalArgumentException`, `UnsupportedOperationException`, internal errors), recreate the interpreter without the delegate, and continue on CPU.

#### 4. Threading and batching

- Run inference off the main thread (HandlerThread/Executors/coroutines).
- Maintain a request queue (e.g., via `Channel`/`Flow` or your own pool) instead of creating an interpreter per request to avoid contention and churn.
- For video/camera pipelines, reduce inference frequency and explicitly use `ImageAnalysis` with `setBackpressureStrategy(KEEP_ONLY_LATEST)` to avoid unbounded frame queues.

#### 5. OTA updates

- With Firebase Model Downloader, use `getModel(name, DownloadType.LOCAL_MODEL)` / `getModelDetails` and a worker/observer that updates the on-disk model file and reloads the interpreter safely.
- Verify downloaded model integrity via hash and signature; keep both current and previous versions (e.g., tracked in Proto DataStore) to support rollback.
- Roll out new models gradually using feature flags, and always keep a bundled on-device model as a fallback.

#### 6. Monitoring

- Log latency, chosen delegate, delegate-to-CPU fallbacks, and error rates.
- Use Firebase Performance or custom telemetry to correlate metrics with model/delegate versions and device classes.
- Collect crash reports; if specific devices/drivers are unstable with certain delegates, remotely disable those delegates for affected segments.

#### 7. Concept references

- See also: [[c-android-profiling]]

---

## Follow-ups (RU)
- Как профилировать NNAPI на конкретном устройстве (NNAPI benchmark tools)?
- Как реализовать multi-model scheduler (vision + NLP) без конфликтов за GPU?
- Как обеспечить приватность при сборе телеметрии inference?

## Follow-ups (EN)
- How to profile NNAPI performance on a specific device (NNAPI benchmark tools)?
- How to implement a multi-model scheduler (vision + NLP) without GPU contention?
- How to ensure privacy when collecting inference telemetry?

## References (RU/EN)
- https://www.tensorflow.org/lite/performance/delegates
- https://firebase.google.com/docs/ml/manage-hosted-models

## Related Questions (RU/EN)
- [[q-android-performance-measurement-tools--android--medium]]
