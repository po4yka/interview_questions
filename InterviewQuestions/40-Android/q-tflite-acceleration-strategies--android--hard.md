---
id: android-629
title: TFLite Acceleration Strategies / Стратегии ускорения TFLite
aliases:
  - TFLite Acceleration Strategies
  - Стратегии ускорения TFLite
topic: android
subtopics:
  - ml
  - tflite
  - nnapi
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - ru
  - en
status: draft
moc: moc-android
related:
  - c-ondevice-ml
  - q-android-coverage-gaps--android--hard
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/ml
  - android/tflite
  - android/nnapi
  - performance
  - difficulty/hard
sources:
  - url: https://www.tensorflow.org/lite/performance/delegates
    note: TFLite delegates performance guide
  - url: https://firebase.google.com/docs/ml/manage-hosted-models
    note: Remote model management
---

# Вопрос (RU)
> Как построить высокопроизводительный pipeline on-device ML на Android: подготовить модель, включить NNAPI/GPU delegate, организовать поток выполнения и обновлять модель по воздуху?

# Question (EN)
> How do you build a high-performance on-device ML pipeline on Android, including model optimization, NNAPI/GPU delegation, execution threading, and over-the-air model updates?

---

## Ответ (RU)

### 1. Подготовка модели

- Используйте `tf.lite.TFLiteConverter` с оптимизациями (`OPTIMIZE_DEFAULT`, quantization aware training).
- Проверяйте `compatibleOps` для NNAPI; fallback на CPU, если оператор не поддерживается.
- Для больших моделей используйте `FlexDelegate` минимально (дорого).

### 2. Загрузка и кеш

```kotlin
val fileDescriptor = context.assets.openFd("model.tflite")
val inputStream = FileInputStream(fileDescriptor.fileDescriptor)
val mapped = inputStream.channel.map(
    FileChannel.MapMode.READ_ONLY,
    fileDescriptor.startOffset,
    fileDescriptor.declaredLength
)
```

- Маппинг через `ByteBuffer` снижает память/время.
- Для OTA используйте `ModelDownloader` (Firebase ML) или собственный CDN + integrity check.

### 3. Делегаты

```kotlin
val gpuDelegate = GpuDelegate(GpuDelegate.Options().apply {
    inferencePreference = TfLiteGpuInferenceOptionsDelegate.InferencePreference.FAST_SINGLE_ANSWER
})

val nnapiDelegate = NnApiDelegate(NnApiDelegate.Options().apply {
    allowFp16(true)
})

val interpreter = Interpreter(mapped, Interpreter.Options().apply {
    addDelegate(selectDelegate())
    setNumThreads(4)
})
```

- GPU delegate подходит для conv/vision (OpenGL/Vulkan). NNAPI — универсальный с драйверами OEM.
- Выберите делегат динамически (feature detection). Если `UnsupportedOperationException` — fallback.

### 4. Потоки и батчинг

- Выполняйте inference на `HandlerThread`/`Executors`.
- Поддерживайте очередь запросов (`Channel`/`Flow`), чтобы избегать contention.
- Для видеопотоков батчите кадры или используйте `ImageAnalysis` с `keepOnlyLatest`.

### 5. OTA обновления

- Firebase Model Downloader: `getModel(name, DownloadType.LOCAL_MODEL)` → зарегистрируйте observer.
- Верифицируйте hash, подпись. Храните версии в Proto DataStore.
- Планируйте rollout через Feature Flag + fallback на bundled модель.

### 6. Мониторинг

- Логируйте latency, delegate type, fallback события.
- Используйте `PerformanceTrace` (Firebase) или собственные метрики.
- Собирайте crash dumps (delegates могут падать на старых драйверах).

---

## Answer (EN)

- Optimize your TFLite model (quantization, pruning), ensure operator compatibility, and memory-map the file for fast loading.
- Select and configure delegates (GPU or NNAPI) at runtime, falling back to CPU when unsupported.
- Run inference on background threads with request queues, batching high-frequency inputs.
- Deliver OTA model updates via Firebase Model Downloader or custom backend with integrity checks and staged rollout.
- Monitor latency, delegate use, and failures to adjust deployments over time.

---

## Follow-ups
- Как профилировать NNAPI на конкретном устройстве (NNAPI benchmark tools)?
- Как реализовать multi-model scheduler (vision + NLP) без конфликтов за GPU?
- Как обеспечить приватность при сборе телеметрии inference?

## References
- [[c-ondevice-ml]]
- [[q-android-coverage-gaps--android--hard]]
- https://www.tensorflow.org/lite/performance/delegates
