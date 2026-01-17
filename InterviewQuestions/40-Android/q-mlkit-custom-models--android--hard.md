---
id: android-126
anki_cards:
  - slug: android-126-0-en
    front: "How do you integrate custom TensorFlow Lite models with ML Kit?"
    back: |
      **Model types:**
      - **Bundled** - in APK, offline, increases size
      - **Remote** - downloaded, updateable without release
      - **AutoML** - trained via Vertex AI, exported as TFLite

      **Integration:**
      ```kotlin
      val interpreter = Interpreter(modelBuffer, options)
      // Always have local fallback
      ```

      **A/B testing:**
      - Remote Config for model selection
      - User-based bucketing for consistency
      - Track inference time, accuracy, success rate

      **Best practices:**
      - GPU/NNAPI delegates for speedup
      - Quantization to reduce size
      - Gradual rollout (10% -> 50% -> 100%)
    tags:
      - android_general
      - difficulty::hard
  - slug: android-126-0-ru
    front: "Как интегрировать пользовательские TensorFlow Lite модели с ML Kit?"
    back: |
      **Типы моделей:**
      - **Локальные** - в APK, офлайн, увеличивают размер
      - **Удаленные** - загружаются, обновляются без релиза
      - **AutoML** - обучены через Vertex AI, экспортированы как TFLite

      **Интеграция:**
      ```kotlin
      val interpreter = Interpreter(modelBuffer, options)
      // Всегда имейте локальный fallback
      ```

      **A/B тестирование:**
      - Remote Config для выбора модели
      - User-based bucketing для консистентности
      - Отслеживайте inference time, accuracy, success rate

      **Лучшие практики:**
      - GPU/NNAPI делегаты для ускорения
      - Квантизация для уменьшения размера
      - Постепенный rollout (10% -> 50% -> 100%)
    tags:
      - android_general
      - difficulty::hard
title: ML Kit Custom Models / Кастомные модели ML Kit
aliases: [ML Kit Custom Models, Кастомные модели ML Kit]
topic: android
subtopics: [ab-testing, analytics, performance-memory]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-memory-management, c-mobile-observability, q-compose-custom-animations--android--medium, q-custom-view-attributes--android--medium, q-mlkit-face-detection--android--medium, q-performance-optimization-android--android--medium, q-when-is-it-better-to-use-png-and-webp-and-when-svg--android--easy]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [android/ab-testing, android/analytics, android/performance-memory, difficulty/hard, machine-learning, ml-kit, tensorflow-lite]

---
# Вопрос (RU)

> Как интегрировать пользовательские модели TensorFlow Lite с ML Kit? В чём разница между встроенными, динамическими и AutoML моделями? Как реализовать развёртывание моделей, обновления и A/B тестирование?

# Question (EN)

> How do you integrate custom TensorFlow Lite models with ML Kit? What are the differences between bundled, dynamic, and AutoML models? How do you implement model deployment, updates, and A/B testing?

## Ответ (RU)

ML Kit поддерживает работу с пользовательскими моделями через TensorFlow Lite (TFLite) и связанные сервисы Firebase/Google Cloud.
На практике обычно:
- либо используем (если доступно) API ML Kit для загрузки кастомных моделей как on-device/remote (актуальную документацию нужно проверять, так как часть старых API устарела),
- либо интегрируем TFLite-интерпретатор напрямую и реализуем загрузку, кеширование, обновления и A/B тестирование на уровне приложения, используя Firebase Remote Config / A/B Testing / Storage или собственный backend.

Это даёт гибкость сверх предобученных моделей ML Kit. Важно учитывать актуальность API: старый Firebase ML (например, FirebaseModelSource и т.п.) устарел; необходимо использовать современные подходы на базе TFLite, актуальных ML Kit APIs и/или собственных механизмов доставки моделей.

### Краткий Вариант

- Используйте TFLite модель (кастомную или AutoML) либо как локальную (в APK/AAB), либо как удалённую (через Firebase/Cloud Storage/CDN/ML Kit Custom Models, если доступны в текущем SDK).
- Всегда имейте локальный fallback.
- Для обновлений и A/B тестов управляйте выбором модели через Remote Config / feature flags и отслеживайте метрики.

### Подробный Вариант

### Типы Моделей

**1. Локальные модели (Bundled / On-device):**
- Упакованы в APK/AAB, доступны офлайн
- Увеличивают размер приложения
- Требуют обновления приложения для обновления модели

**2. Удалённые модели (Dynamic / Remote):**
- Хостятся в удалённом источнике (например, Firebase Storage + собственная логика загрузки, собственный CDN/endpoint или ML Kit Custom Remote Models, если используется соответствующий SDK)
- Загружаются по требованию, можно обновлять без релиза приложения
- Требуют интернет для первой загрузки и обновлений

**3. AutoML модели:**
- Обучены через Google Cloud AutoML / Vertex AI и экспортированы как TFLite
- Автоматическая/полуавтоматическая оптимизация архитектуры под задачу
- Развёртывание аналогично кастомным TFLite моделям (локально или удалённо)

### Интеграция TensorFlow Lite (пример)

Ниже — упрощённый пример, показывающий общую идею сочетания локальной и удалённой модели. Вспомогательные компоненты (RemoteModelProvider, ModelLoader и т.п.) предполагаются реализованными отдельно.

```kotlin
class CustomModelManager(private val context: Context) {
    // ✅ Локальная модель как fallback (asset)
    private val localModelPath = "models/classifier.tflite"

    private var interpreter: Interpreter? = null

    suspend fun initialize(): Result<Unit> = withContext(Dispatchers.IO) {
        try {
            // pseudo: проверяем наличие обновлённой удалённой модели
            val remoteFile: File? = RemoteModelProvider.getLatestModelFileIfAvailable()

            val modelBuffer: MappedByteBuffer = if (remoteFile != null) {
                FileUtil.loadMappedFile(remoteFile)
            } else {
                // локальный asset fallback
                FileUtil.loadMappedFile(context, localModelPath)
            }

            val options = Interpreter.Options().apply {
                setNumThreads(4)
                // Использование NNAPI / других делегатов зависит от версии TFLite и поддержки устройством;
                // в продакшене предпочитайте явные делегаты (NNAPI/GPU) и проверку доступности.
            }

            interpreter = Interpreter(modelBuffer, options)

            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

Примечания:
- RemoteModelProvider и FileUtil.loadMappedFile(File) здесь условные/примерные — в реальном коде нужно использовать конкретный способ загрузки (ML Kit Custom Model API, если доступно, или собственную реализацию скачивания/кеша файлов).
- Важно валидировать совместимость версии модели и входных данных и не использовать один и тот же Interpreter из разных потоков без синхронизации.

### Требования

- Функциональные:
  - Поддержка локальной и удалённой загрузки моделей.
  - Возможность безопасного обновления модели без крашей и деградации UX.
  - Механизм A/B тестирования и постепенного rollout.
- Нефункциональные:
  - Низкая задержка и ограниченное использование памяти.
  - Работоспособность офлайн за счёт локальной модели.
  - Надёжный откат на стабильную модель.

### Архитектура

- Компонент управления моделями (ModelManager), инкапсулирующий загрузку локальной/удалённой модели, валидацию и версионирование.
- Слой конфигурации/feature flags (например, Remote Config) для выбора активной модели и A/B стратегий.
- Отдельный слой логирования и метрик (Firebase Analytics/Crashlytics и др.) для мониторинга качества и производительности.
- Инференс из UI/Domain слоя идёт только через абстракцию, не напрямую к TFLite.

### A/B Тестирование Моделей

```kotlin
class ModelABTestingManager(private val context: Context) {
    private val remoteConfig = FirebaseRemoteConfig.getInstance()

    fun selectModel(): ModelSelection {
        val strategy = remoteConfig.getString("model_selection_strategy")

        return when (strategy) {
            "random" -> selectModelRandomly()
            "user_based" -> selectModelByUserId()  // ✅ Консистентный выбор
            else -> ModelSelection(remoteConfig.getString("active_model"), "control")
        }
    }

    // ✅ Консистентное назначение на основе user ID (пример)
    private fun selectModelByUserId(): ModelSelection {
        val userId = getUserId()
        val modelAWeight = remoteConfig.getLong("model_a_weight").toInt()
        val modelBWeight = remoteConfig.getLong("model_b_weight").toInt()
        val totalWeight = (modelAWeight + modelBWeight).coerceAtLeast(1)

        val bucket = kotlin.math.abs(userId.hashCode() % totalWeight)
        return if (bucket < modelAWeight) {
            ModelSelection(remoteConfig.getString("model_a_name"), "variant_a")
        } else {
            ModelSelection(remoteConfig.getString("model_b_name"), "variant_b")
        }
    }

    // Эти функции/тип должны быть реализованы в вашем коде:
    private fun selectModelRandomly(): ModelSelection { /* ... */ TODO() }
    private fun getUserId(): String { /* ... */ TODO() }
    data class ModelSelection(val modelName: String, val variant: String)

    // ✅ Трекинг метрик производительности
    fun trackModelPerformance(
        modelName: String,
        inferenceTimeMs: Long,
        accuracy: Float?,
        success: Boolean
    ) {
        val bundle = Bundle().apply {
            putString("model_name", modelName)
            putLong("inference_time_ms", inferenceTimeMs)
            accuracy?.let { putDouble("accuracy", it.toDouble()) }
            putBoolean("success", success)
        }
        FirebaseAnalytics.getInstance(context)
            .logEvent("ml_model_inference", bundle)
    }
}
```

### Оптимизация Моделей

**Post-training quantization (Python, упрощённый пример):**
```python
import tensorflow as tf

def quantize_model(model_path, output_path):
    converter = tf.lite.TFLiteConverter.from_saved_model(model_path)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]

    # ✅ Полная integer-квантизация (пример с uint8 I/O)
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.uint8
    converter.inference_output_type = tf.uint8

    quantized_model = converter.convert()
    with open(output_path, 'wb') as f:
        f.write(quantized_model)
```
Комментарий: уменьшение размера "до ~75%" — ориентировочная оценка и зависит от модели; точное значение не гарантируется.

**GPU делегирование (пример):**
```kotlin
fun createOptimizedInterpreter(context: Context, modelPath: String): Interpreter {
    val modelBuffer = FileUtil.loadMappedFile(context, modelPath)
    val options = Interpreter.Options().apply {
        // GPU делегат может существенно ускорить inference на поддерживаемых устройствах и моделях
        addDelegate(GpuDelegate())
        setNumThreads(4)
        setAllowFp16PrecisionForFp32(true)
    }
    // В реальном коде важно корректно освобождать делегат и интерпретатор
    return Interpreter(modelBuffer, options)
}
```
Примечания:
- Фактический выигрыш (например, "до 10x") не гарантирован и сильно зависит от устройства и модели.
- Необходимо корректно управлять жизненным циклом делегатов и интерпретатора и иметь fallback на CPU.

### Стратегии Развёртывания

**1. Постепенный rollout (примерная схема):**
- 10% пользователей → мониторинг метрик
- 50% пользователей → проверка стабильности и качества
- 100% пользователей → полный запуск

**2. Условия загрузки (для удалённых моделей через ML Kit Custom Remote Models):**
```kotlin
val conditions = DownloadConditions.Builder()
    .requireWifi()      // ✅ Только Wi‑Fi
    .requireCharging()  // ✅ Для больших моделей — во время зарядки
    .build()
```
Если вы хостите модели на своём CDN/сервере, аналогичные условия (Wi‑Fi, зарядка, не в роуминге) реализуются собственной логикой.

**3. Fallback стратегия:**
- Всегда включать локальную модель в APK/AAB как безопасный вариант
- Использовать удалённую при доступности и успешной валидации
- Обеспечить graceful degradation при ошибках загрузки/инициализации

### Метрики Производительности

Рекомендуется отслеживать (ориентиры, а не жёсткие правила):
- Inference time (latency)
- Model size
- Accuracy / quality metrics
- Memory usage
- Success rate

### Лучшие Практики

1. Всегда имейте локальную fallback модель.
2. Используйте условия загрузки (Wi‑Fi, зарядка, не в роуминге) для удалённых моделей.
3. Отслеживайте метрики производительности и качества моделей.
4. Применяйте квантизацию и другие оптимизации для снижения размера и задержки.
5. Тестируйте на целевом диапазоне устройств (GPU/NNAPI/CPU, разные SoC и память).
6. Реализуйте постепенный rollout и A/B тестирование для новых моделей с возможностью быстрого отката.

## Answer (EN)

ML Kit supports working with custom models via TensorFlow Lite (TFLite) and related Firebase/Google Cloud services.
In practice, you typically:
- use the ML Kit custom model capabilities (where available in the current SDK) to manage on-device/remote models, and
- or integrate TFLite directly and implement model file delivery, caching, updates, and A/B testing at the app/backend level using Firebase Remote Config / A/B Testing / Storage or your own infrastructure.

This gives you flexibility beyond ML Kit’s built-in models. Be aware that the older Firebase ML APIs (e.g., FirebaseModelSource and friends) are deprecated; rely on TFLite-based flows, up-to-date ML Kit APIs, and/or your own delivery mechanism.

### Short Version

- Use a TFLite model (custom or AutoML) either bundled in the app or downloaded remotely (Firebase/Cloud Storage/CDN/ML Kit Custom Models where available).
- Always keep a local fallback.
- Control active model and A/B experiments via Remote Config/feature flags and track metrics.

### Detailed Version

### Model Types

**1. Bundled / On-device Models (Local):**
- Packaged in the APK/AAB, work fully offline
- Increase app size
- Require app update to ship a new model version

**2. Dynamic / Remote Models:**
- Hosted remotely (e.g., Firebase Storage plus your own loading logic, your CDN/endpoint, or ML Kit Custom Remote Models where supported)
- Downloaded on demand; can be updated without releasing a new app build
- Require network for initial download and updates

**3. AutoML Models:**
- Trained using Google Cloud AutoML / Vertex AI and exported as TFLite
- (Semi-)automatic architecture/search/optimization
- Deployed the same way as other TFLite custom models (bundled or remote)

### TensorFlow Lite Integration (example)

Below is a simplified example that shows the idea of combining a bundled fallback model with a remotely updated one. Helper components (RemoteModelProvider, etc.) are assumed to be implemented separately.

```kotlin
class CustomModelManager(private val context: Context) {
    // ✅ Local model as fallback (asset)
    private val localModelPath = "models/classifier.tflite"

    private var interpreter: Interpreter? = null

    suspend fun initialize(): Result<Unit> = withContext(Dispatchers.IO) {
        try {
            // pseudo: check if an updated remote model is available
            val remoteFile: File? = RemoteModelProvider.getLatestModelFileIfAvailable()

            val modelBuffer: MappedByteBuffer = if (remoteFile != null) {
                FileUtil.loadMappedFile(remoteFile)
            } else {
                // fallback to bundled asset
                FileUtil.loadMappedFile(context, localModelPath)
            }

            val options = Interpreter.Options().apply {
                setNumThreads(4)
                // NNAPI / other delegates usage depends on your TFLite version and device support;
                // in production prefer explicit delegates (NNAPI/GPU) with capability checks.
            }

            interpreter = Interpreter(modelBuffer, options)

            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

Notes:
- RemoteModelProvider and FileUtil.loadMappedFile(File) are placeholders; in production you must implement robust download/cache logic or use ML Kit Custom Model APIs where available.
- Validate I/O tensor compatibility and handle model versioning; avoid sharing a single Interpreter instance across threads without proper synchronization.

### Requirements

- Functional:
  - Support both bundled and remote models.
  - Allow safe model updates without crashes or UX regressions.
  - Provide A/B testing and gradual rollout mechanism.
- Non-functional:
  - Low latency and controlled memory usage.
  - Offline capability via bundled model.
  - Reliable rollback to a stable model.

### Architecture

- Model Manager component abstracting model loading (local/remote), validation, and versioning.
- Config/feature-flag layer (e.g., Remote Config) controlling active model and experiments.
- Metrics/logging layer (Firebase Analytics/Crashlytics etc.) monitoring quality/performance.
- UI/Domain layers call inference only through an abstraction, not directly through TFLite.

### Model A/B Testing

```kotlin
class ModelABTestingManager(private val context: Context) {
    private val remoteConfig = FirebaseRemoteConfig.getInstance()

    fun selectModel(): ModelSelection {
        val strategy = remoteConfig.getString("model_selection_strategy")

        return when (strategy) {
            "random" -> selectModelRandomly()
            "user_based" -> selectModelByUserId()  // ✅ Consistent selection
            else -> ModelSelection(remoteConfig.getString("active_model"), "control")
        }
    }

    // ✅ Consistent assignment based on user ID (example)
    private fun selectModelByUserId(): ModelSelection {
        val userId = getUserId()
        val modelAWeight = remoteConfig.getLong("model_a_weight").toInt()
        val modelBWeight = remoteConfig.getLong("model_b_weight").toInt()
        val totalWeight = (modelAWeight + modelBWeight).coerceAtLeast(1)

        val bucket = kotlin.math.abs(userId.hashCode() % totalWeight)
        return if (bucket < modelAWeight) {
            ModelSelection(remoteConfig.getString("model_a_name"), "variant_a")
        } else {
            ModelSelection(remoteConfig.getString("model_b_name"), "variant_b")
        }
    }

    // These are placeholders and must be implemented in real code:
    private fun selectModelRandomly(): ModelSelection { /* ... */ TODO() }
    private fun getUserId(): String { /* ... */ TODO() }
    data class ModelSelection(val modelName: String, val variant: String)

    // ✅ Track performance metrics
    fun trackModelPerformance(
        modelName: String,
        inferenceTimeMs: Long,
        accuracy: Float?,
        success: Boolean
    ) {
        val bundle = Bundle().apply {
            putString("model_name", modelName)
            putLong("inference_time_ms", inferenceTimeMs)
            accuracy?.let { putDouble("accuracy", it.toDouble()) }
            putBoolean("success", success)
        }
        FirebaseAnalytics.getInstance(context)
            .logEvent("ml_model_inference", bundle)
    }
}
```

### Model Optimization

**Post-training quantization (Python, simplified):**
```python
import tensorflow as tf

def quantize_model(model_path, output_path):
    converter = tf.lite.TFLiteConverter.from_saved_model(model_path)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]

    # ✅ Example of full integer quantization with uint8 I/O
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.uint8
    converter.inference_output_type = tf.uint8

    quantized_model = converter.convert()
    with open(output_path, 'wb') as f:
        f.write(quantized_model)
```
Note: "up to ~75% size reduction" is typical but not guaranteed; depends on the model.

**GPU delegation (example):**
```kotlin
fun createOptimizedInterpreter(context: Context, modelPath: String): Interpreter {
    val modelBuffer = FileUtil.loadMappedFile(context, modelPath)
    val options = Interpreter.Options().apply {
        // GPU delegate can provide significant speedups on supported devices/models
        addDelegate(GpuDelegate())
        setNumThreads(4)
        setAllowFp16PrecisionForFp32(true)
    }
    // In production, properly manage delegate/interpreter lifecycle
    return Interpreter(modelBuffer, options)
}
```
Notes:
- Actual speedups vary; 10x improvements are not guaranteed.
- Always manage delegate lifecycle and have a CPU fallback if GPU is unavailable or fails.

### Deployment Strategies

**1. Gradual rollout (illustrative):**
- 10% of users → monitor key metrics
- 50% of users → validate stability and quality
- 100% of users → full rollout

**2. Download conditions (for remote models via ML Kit Custom Remote Models):**
```kotlin
val conditions = DownloadConditions.Builder()
    .requireWifi()      // ✅ Wi‑Fi only
    .requireCharging()  // ✅ While charging for large models
    .build()
```
If you host models on your own CDN/server, implement equivalent conditions (Wi‑Fi, charging, no roaming) in your own logic.

**3. Fallback strategy:**
- Always bundle a local model in APK/AAB as a safe default
- Prefer remote model when available and validated
- Implement graceful degradation on download/init failures

### Performance Metrics

Recommended to track (heuristics, not strict rules):
- Inference time (latency)
- Model size
- Accuracy / quality metrics
- Memory usage
- Success rate

### Best Practices

1. Always have a local fallback model.
2. Use download conditions (Wi‑Fi, charging, no roaming) for remote models.
3. Track performance and quality metrics for each model version.
4. Apply quantization and other optimizations to reduce size and latency.
5. Test across your target device range (GPU/NNAPI/CPU, different SoCs and memory).
6. Implement gradual rollout and A/B testing with the ability to quickly roll back.

## Follow-ups

- How do you handle model versioning and backward compatibility?
- What are the trade-offs between model accuracy and inference speed?
- How do you debug model inference issues in production?
- When should you use NNAPI vs GPU delegation?
- How do you implement ensemble learning with multiple models?

## References

- https://developers.google.com/ml-kit/custom-models
- https://www.tensorflow.org/lite/performance/post_training_quantization
- https://firebase.google.com/docs/ml

## Related Questions

### Prerequisites / Concepts

- [[c-memory-management]]
- [[c-mobile-observability]]

### Prerequisites
- [[q-when-is-it-better-to-use-png-and-webp-and-when-svg--android--easy]]

### Related
- ML concepts and fundamentals
- Model optimization techniques

### Advanced
- Model ensemble strategies
- Custom model training pipelines
