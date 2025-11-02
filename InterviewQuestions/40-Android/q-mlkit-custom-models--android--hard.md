---
id: android-126
title: "ML Kit Custom Models / Кастомные модели ML Kit"
aliases: ["ML Kit Custom Models", "Кастомные модели ML Kit"]
topic: android
subtopics: [ab-testing, analytics, performance-memory]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-performance-optimization-android--android--medium, q-when-is-it-better-to-use-png-and-webp-and-when-svg--android--easy]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [android/ab-testing, android/analytics, android/performance-memory, difficulty/hard, machine-learning, ml-kit, tensorflow-lite]
date created: Monday, October 27th 2025, 3:39:17 pm
date modified: Saturday, November 1st 2025, 5:43:34 pm
---

# Вопрос (RU)

> Как интегрировать пользовательские модели TensorFlow Lite с ML Kit? В чём разница между встроенными, динамическими и AutoML моделями? Как реализовать развёртывание моделей, обновления и A/B тестирование?

# Question (EN)

> How do you integrate custom TensorFlow Lite models with ML Kit? What are the differences between bundled, dynamic, and AutoML models? How do you implement model deployment, updates, and A/B testing?

## Ответ (RU)

ML Kit поддерживает пользовательские модели через интеграцию TensorFlow Lite, позволяя использовать специализированные модели для конкретных случаев. Это обеспечивает гибкость за пределами предобученных моделей ML Kit.

### Типы Моделей

**1. Локальные модели (Bundled):**
- Упакованы в APK, доступны офлайн
- Увеличивают размер приложения
- Требуют обновления приложения для обновления модели

**2. Удалённые модели (Dynamic):**
- Размещены в Firebase ML
- Загружаются по требованию, можно обновлять без релиза
- Требуют интернет для первой загрузки

**3. AutoML модели:**
- Обучены через Google Cloud AutoML
- Автоматическая оптимизация архитектуры
- Упрощённый процесс обучения

### Интеграция TensorFlow Lite

```kotlin
class CustomModelManager(private val context: Context) {
    // ✅ Локальная модель как fallback
    private val localModel = LocalModel.Builder()
        .setAssetFilePath("models/classifier.tflite")
        .build()

    // ✅ Удалённая модель с условиями загрузки
    private val remoteModel = CustomRemoteModel.Builder(
        FirebaseModelSource.Builder("custom_classifier")
            .enableModelUpdates(true)
            .setInitialDownloadConditions(
                DownloadConditions.Builder()
                    .requireWifi()  // ✅ Только по WiFi
                    .build()
            )
            .build()
    ).build()

    suspend fun initialize(): Result<Unit> = withContext(Dispatchers.IO) {
        try {
            val modelFile = if (remoteModelManager.isModelDownloaded(remoteModel).await()) {
                remoteModelManager.getLatestModelFile(remoteModel).await()
            } else {
                FileUtil.loadMappedFile(context, localModel.assetFilePath)
            }

            interpreter = Interpreter(modelFile, Interpreter.Options().apply {
                setNumThreads(4)
                setUseNNAPI(true)  // ✅ Аппаратное ускорение
            })
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

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

    // ✅ Консистентное назначение на основе user ID
    private fun selectModelByUserId(): ModelSelection {
        val userId = getUserId()
        val modelAWeight = remoteConfig.getLong("model_a_weight").toInt()
        val totalWeight = modelAWeight + remoteConfig.getLong("model_b_weight").toInt()

        return if (Math.abs(userId.hashCode() % totalWeight) < modelAWeight) {
            ModelSelection(remoteConfig.getString("model_a_name"), "variant_a")
        } else {
            ModelSelection(remoteConfig.getString("model_b_name"), "variant_b")
        }
    }

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
        FirebaseAnalytics.getInstance(context).logEvent("ml_model_inference", bundle)
    }
}
```

### Оптимизация Моделей

**Post-training quantization (Python):**
```python
import tensorflow as tf

def quantize_model(model_path, output_path):
    converter = tf.lite.TFLiteConverter.from_saved_model(model_path)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]

    # ✅ INT8 квантизация для уменьшения размера на 75%
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.uint8
    converter.inference_output_type = tf.uint8

    quantized_model = converter.convert()
    with open(output_path, 'wb') as f:
        f.write(quantized_model)
```

**GPU делегирование:**
```kotlin
fun createOptimizedInterpreter(modelPath: String): Interpreter {
    val options = Interpreter.Options().apply {
        addDelegate(GpuDelegate())  // ✅ Ускорение до 10x
        setNumThreads(4)
        setAllowFp16PrecisionForFp32(true)
    }
    return Interpreter(FileUtil.loadMappedFile(context, modelPath), options)
}
```

### Стратегии Развёртывания

**1. Постепенный rollout:**
- 10% пользователей → мониторинг метрик
- 50% пользователей → валидация стабильности
- 100% пользователей → полный запуск

**2. Условия загрузки:**
```kotlin
val conditions = DownloadConditions.Builder()
    .requireWifi()      // ✅ Только WiFi
    .requireCharging()  // ✅ Во время зарядки для больших моделей
    .build()
```

**3. Fallback стратегия:**
- Всегда включать локальную модель в APK
- Использовать удалённую при доступности
- Graceful degradation при ошибках

### Метрики Производительности

Отслеживать:
- **Inference time** (latency): <100ms для real-time
- **Model size**: <10MB для локальных моделей
- **Accuracy**: baseline метрика качества
- **Memory usage**: peak memory во время inference
- **Success rate**: процент успешных inference

### Лучшие Практики

1. **Всегда имейте локальную fallback модель**
2. **Используйте условия загрузки (WiFi, зарядка)**
3. **Отслеживайте метрики производительности моделей**
4. **Применяйте квантизацию для уменьшения размера**
5. **Тестируйте на целевом диапазоне устройств**
6. **Реализуйте постепенный rollout для новых моделей**

## Answer (EN)

ML Kit supports custom models through TensorFlow Lite integration, allowing specialized models trained for specific use cases beyond pre-trained ML Kit models.

### Model Types

**1. Bundled Models (Local):**
- Packaged in APK, work offline
- Increase app size
- Require app update for model updates

**2. Dynamic Models (Remote):**
- Hosted on Firebase ML
- Downloaded on demand, updatable without releases
- Require internet for initial download

**3. AutoML Models:**
- Trained via Google Cloud AutoML
- Automatic architecture optimization
- Simplified training process

### TensorFlow Lite Integration

```kotlin
class CustomModelManager(private val context: Context) {
    // ✅ Local model as fallback
    private val localModel = LocalModel.Builder()
        .setAssetFilePath("models/classifier.tflite")
        .build()

    // ✅ Remote model with download conditions
    private val remoteModel = CustomRemoteModel.Builder(
        FirebaseModelSource.Builder("custom_classifier")
            .enableModelUpdates(true)
            .setInitialDownloadConditions(
                DownloadConditions.Builder()
                    .requireWifi()  // ✅ WiFi only
                    .build()
            )
            .build()
    ).build()

    suspend fun initialize(): Result<Unit> = withContext(Dispatchers.IO) {
        try {
            val modelFile = if (remoteModelManager.isModelDownloaded(remoteModel).await()) {
                remoteModelManager.getLatestModelFile(remoteModel).await()
            } else {
                FileUtil.loadMappedFile(context, localModel.assetFilePath)
            }

            interpreter = Interpreter(modelFile, Interpreter.Options().apply {
                setNumThreads(4)
                setUseNNAPI(true)  // ✅ Hardware acceleration
            })
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

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

    // ✅ Consistent assignment based on user ID
    private fun selectModelByUserId(): ModelSelection {
        val userId = getUserId()
        val modelAWeight = remoteConfig.getLong("model_a_weight").toInt()
        val totalWeight = modelAWeight + remoteConfig.getLong("model_b_weight").toInt()

        return if (Math.abs(userId.hashCode() % totalWeight) < modelAWeight) {
            ModelSelection(remoteConfig.getString("model_a_name"), "variant_a")
        } else {
            ModelSelection(remoteConfig.getString("model_b_name"), "variant_b")
        }
    }

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
        FirebaseAnalytics.getInstance(context).logEvent("ml_model_inference", bundle)
    }
}
```

### Model Optimization

**Post-training quantization (Python):**
```python
import tensorflow as tf

def quantize_model(model_path, output_path):
    converter = tf.lite.TFLiteConverter.from_saved_model(model_path)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]

    # ✅ INT8 quantization reduces size by 75%
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.uint8
    converter.inference_output_type = tf.uint8

    quantized_model = converter.convert()
    with open(output_path, 'wb') as f:
        f.write(quantized_model)
```

**GPU delegation:**
```kotlin
fun createOptimizedInterpreter(modelPath: String): Interpreter {
    val options = Interpreter.Options().apply {
        addDelegate(GpuDelegate())  // ✅ Up to 10x speedup
        setNumThreads(4)
        setAllowFp16PrecisionForFp32(true)
    }
    return Interpreter(FileUtil.loadMappedFile(context, modelPath), options)
}
```

### Deployment Strategies

**1. Gradual rollout:**
- 10% users → monitor metrics
- 50% users → validate stability
- 100% users → full launch

**2. Download conditions:**
```kotlin
val conditions = DownloadConditions.Builder()
    .requireWifi()      // ✅ WiFi only
    .requireCharging()  // ✅ While charging for large models
    .build()
```

**3. Fallback strategy:**
- Always bundle local model in APK
- Use remote when available
- Graceful degradation on errors

### Performance Metrics

Track:
- **Inference time** (latency): <100ms for real-time
- **Model size**: <10MB for bundled models
- **Accuracy**: baseline quality metric
- **Memory usage**: peak memory during inference
- **Success rate**: percentage of successful inferences

### Best Practices

1. **Always have a local fallback model**
2. **Use download conditions (WiFi, charging)**
3. **Track model performance metrics**
4. **Apply quantization to reduce size**
5. **Test on target device range**
6. **Implement gradual rollout for new models**

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

### Prerequisites
- [[q-when-is-it-better-to-use-png-and-webp-and-when-svg--android--easy]]

### Related
- ML concepts and fundamentals
- Model optimization techniques

### Advanced
- Model ensemble strategies
- Custom model training pipelines
