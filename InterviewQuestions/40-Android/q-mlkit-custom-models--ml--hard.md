---
id: "20251015082237384"
title: "Mlkit Custom Models / Кастомные модели ML Kit"
topic: android
difficulty: hard
status: draft
created: 2025-10-15
tags: - android
  - ml-kit
  - tensorflow-lite
  - custom-models
  - machine-learning
  - automl
  - model-deployment
---
# ML Kit Custom Models and TensorFlow Lite Integration

# Question (EN)
> 

# Вопрос (RU)
> 

---

## Answer (EN)
# Question (EN)
How do you integrate custom TensorFlow Lite models with ML Kit? What are the differences between bundled, dynamic, and AutoML models? How do you implement model deployment, updates, and A/B testing?

## Answer (EN)
ML Kit supports custom models through TensorFlow Lite integration, allowing you to use specialized models trained for specific use cases. This provides flexibility beyond pre-trained ML Kit models while maintaining ease of integration.

#### 1. TensorFlow Lite Model Integration

**Basic Custom Model Setup:**
```kotlin
import com.google.mlkit.common.model.CustomRemoteModel
import com.google.mlkit.common.model.LocalModel
import com.google.mlkit.common.model.RemoteModelManager
import com.google.mlkit.linkfirebase.FirebaseModelSource
import com.google.mlkit.vision.common.InputImage
import org.tensorflow.lite.Interpreter
import org.tensorflow.lite.support.common.FileUtil
import org.tensorflow.lite.support.image.ImageProcessor
import org.tensorflow.lite.support.image.TensorImage
import org.tensorflow.lite.support.image.ops.ResizeOp
import org.tensorflow.lite.support.image.ops.ResizeWithCropOrPadOp
import org.tensorflow.lite.support.image.ops.Rot90Op
import org.tensorflow.lite.support.label.TensorLabel
import org.tensorflow.lite.support.tensorbuffer.TensorBuffer
import java.nio.ByteBuffer

class CustomModelManager(private val context: Context) {

    // Local model bundled with the app
    private val localModel = LocalModel.Builder()
        .setAssetFilePath("models/custom_classifier.tflite")
        .build()

    // Remote model from Firebase ML
    private val remoteModelSource = FirebaseModelSource.Builder("custom_classifier")
        .enableModelUpdates(true)
        .setInitialDownloadConditions(
            DownloadConditions.Builder()
                .requireWifi()
                .build()
        )
        .setUpdatesDownloadConditions(
            DownloadConditions.Builder()
                .requireCharging()
                .requireWifi()
                .build()
        )
        .build()

    private val remoteModel = CustomRemoteModel.Builder(remoteModelSource)
        .build()

    private val remoteModelManager = RemoteModelManager.getInstance()

    private var interpreter: Interpreter? = null

    /**
     * Initialize model - download remote or use local fallback
     */
    suspend fun initialize(): Result<Unit> = withContext(Dispatchers.IO) {
        try {
            // Check if remote model is downloaded
            val isDownloaded = remoteModelManager.isModelDownloaded(remoteModel).await()

            val modelFile = if (isDownloaded) {
                remoteModelManager.getLatestModelFile(remoteModel).await()
            } else {
                // Trigger download in background
                downloadRemoteModel()
                // Use local model meanwhile
                FileUtil.loadMappedFile(context, localModel.assetFilePath)
            }

            // Initialize TensorFlow Lite interpreter
            interpreter = Interpreter(
                modelFile,
                Interpreter.Options().apply {
                    setNumThreads(4)
                    setUseNNAPI(true) // Use Android Neural Networks API if available
                }
            )

            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Download remote model with progress tracking
     */
    private suspend fun downloadRemoteModel() {
        val conditions = DownloadConditions.Builder()
            .requireWifi()
            .build()

        remoteModelManager
            .download(remoteModel, conditions)
            .addOnProgressListener { taskSnapshot ->
                val progress = (100.0 * taskSnapshot.bytesTransferred / taskSnapshot.totalByteCount).toInt()
                Log.d("CustomModel", "Download progress: $progress%")
            }
            .await()
    }

    /**
     * Check for model updates
     */
    suspend fun checkForUpdates(): Boolean {
        return try {
            val isUpdateAvailable = remoteModelManager.isModelDownloaded(remoteModel).await()
            if (!isUpdateAvailable) {
                downloadRemoteModel()
                true
            } else {
                false
            }
        } catch (e: Exception) {
            Log.e("CustomModel", "Failed to check for updates", e)
            false
        }
    }

    /**
     * Run inference on image
     */
    suspend fun runInference(
        bitmap: Bitmap,
        labels: List<String>
    ): Result<ClassificationResult> = withContext(Dispatchers.Default) {
        try {
            val interpreter = interpreter ?: return@withContext Result.failure(
                IllegalStateException("Model not initialized")
            )

            // Preprocess image
            val inputImage = preprocessImage(bitmap)

            // Prepare output buffer
            val outputShape = interpreter.getOutputTensor(0).shape()
            val outputBuffer = TensorBuffer.createFixedSize(
                outputShape,
                interpreter.getOutputTensor(0).dataType()
            )

            // Run inference
            interpreter.run(inputImage.buffer, outputBuffer.buffer.rewind())

            // Process results
            val results = processOutput(outputBuffer, labels)

            Result.success(results)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    private fun preprocessImage(bitmap: Bitmap): TensorImage {
        val imageProcessor = ImageProcessor.Builder()
            .add(ResizeWithCropOrPadOp(bitmap.height, bitmap.width))
            .add(ResizeOp(224, 224, ResizeOp.ResizeMethod.BILINEAR)) // Model input size
            .add(Rot90Op(0))
            .build()

        val tensorImage = TensorImage.fromBitmap(bitmap)
        return imageProcessor.process(tensorImage)
    }

    private fun processOutput(
        outputBuffer: TensorBuffer,
        labels: List<String>
    ): ClassificationResult {
        val tensorLabel = TensorLabel(labels, outputBuffer)
        val probabilities = tensorLabel.mapWithFloatValue

        val sortedResults = probabilities.entries
            .sortedByDescending { it.value }
            .take(5)
            .map { (label, confidence) ->
                Classification(label, confidence)
            }

        return ClassificationResult(
            topResult = sortedResults.first(),
            allResults = sortedResults,
            processingTimeMs = 0 // Can be tracked with timing
        )
    }

    fun release() {
        interpreter?.close()
        interpreter = null
    }
}

data class ClassificationResult(
    val topResult: Classification,
    val allResults: List<Classification>,
    val processingTimeMs: Long
)

data class Classification(
    val label: String,
    val confidence: Float
)
```

#### 2. AutoML Vision Edge Integration

**AutoML Model Setup:**
```kotlin
import com.google.mlkit.vision.label.automl.AutoMLImageLabelerLocalModel
import com.google.mlkit.vision.label.automl.AutoMLImageLabelerOptions
import com.google.mlkit.vision.label.automl.AutoMLImageLabelerRemoteModel

class AutoMLModelManager(private val context: Context) {

    // Local AutoML model
    private val localAutoMLModel = AutoMLImageLabelerLocalModel.Builder()
        .setAssetFilePath("automl_model/manifest.json")
        .build()

    // Remote AutoML model
    private val remoteAutoMLModel = AutoMLImageLabelerRemoteModel.Builder("automl_classifier")
        .build()

    // AutoML labeler options
    private val labelerOptions = AutoMLImageLabelerOptions.Builder(localAutoMLModel)
        .setConfidenceThreshold(0.6f)
        .setMaxResultCount(5)
        .build()

    // Alternative: Remote model with fallback
    private val remoteLabelerOptions = AutoMLImageLabelerOptions.Builder(remoteAutoMLModel)
        .setLocalModelName(localAutoMLModel.modelName)
        .setConfidenceThreshold(0.6f)
        .setMaxResultCount(5)
        .build()

    private val imageLabeler = ImageLabeling.getClient(labelerOptions)

    /**
     * Classify image using AutoML model
     */
    suspend fun classifyImage(inputImage: InputImage): Result<List<ImageLabel>> {
        return try {
            val labels = imageLabeler.process(inputImage).await()
            Result.success(labels)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Batch classify multiple images
     */
    suspend fun classifyBatch(
        images: List<Bitmap>
    ): List<AutoMLClassificationResult> = coroutineScope {
        images.map { bitmap ->
            async {
                val inputImage = InputImage.fromBitmap(bitmap, 0)
                val result = classifyImage(inputImage)

                AutoMLClassificationResult(
                    bitmap = bitmap,
                    labels = result.getOrNull() ?: emptyList(),
                    error = result.exceptionOrNull()
                )
            }
        }.awaitAll()
    }

    fun release() {
        imageLabeler.close()
    }
}

data class AutoMLClassificationResult(
    val bitmap: Bitmap,
    val labels: List<ImageLabel>,
    val error: Throwable?
)
```

#### 3. Model Deployment and Updates

**Firebase ML Model Management:**
```kotlin
import com.google.firebase.ml.modeldownloader.CustomModel
import com.google.firebase.ml.modeldownloader.CustomModelDownloadConditions
import com.google.firebase.ml.modeldownloader.DownloadType
import com.google.firebase.ml.modeldownloader.FirebaseModelDownloader

class ModelDeploymentManager {

    private val modelDownloader = FirebaseModelDownloader.getInstance()

    /**
     * Download model with specific conditions
     */
    suspend fun downloadModel(
        modelName: String,
        downloadType: DownloadType = DownloadType.LOCAL_MODEL_UPDATE_IN_BACKGROUND
    ): Result<CustomModel> {
        return try {
            val conditions = CustomModelDownloadConditions.Builder()
                .requireWifi()
                .build()

            val model = modelDownloader
                .getModel(modelName, downloadType, conditions)
                .await()

            Result.success(model)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Get model with fallback strategy
     */
    suspend fun getModelWithFallback(
        modelName: String,
        localModelPath: String
    ): File {
        return try {
            // Try to get latest model from Firebase
            val model = downloadModel(modelName, DownloadType.LATEST_MODEL).getOrNull()
            model?.file ?: loadLocalModel(localModelPath)
        } catch (e: Exception) {
            loadLocalModel(localModelPath)
        }
    }

    private fun loadLocalModel(assetPath: String): File {
        // Load from assets
        return File(assetPath)
    }

    /**
     * Check if model update is available
     */
    suspend fun isUpdateAvailable(modelName: String): Boolean {
        return try {
            val localModel = modelDownloader
                .getModel(modelName, DownloadType.LOCAL_MODEL, CustomModelDownloadConditions.Builder().build())
                .await()

            val latestModel = modelDownloader
                .getModel(modelName, DownloadType.LATEST_MODEL, CustomModelDownloadConditions.Builder().build())
                .await()

            localModel.modelHash != latestModel.modelHash
        } catch (e: Exception) {
            false
        }
    }

    /**
     * Delete downloaded model
     */
    suspend fun deleteModel(modelName: String): Boolean {
        return try {
            modelDownloader.deleteDownloadedModel(modelName).await()
            true
        } catch (e: Exception) {
            false
        }
    }

    /**
     * List all downloaded models
     */
    suspend fun listDownloadedModels(): Set<CustomModel> {
        return try {
            modelDownloader.listDownloadedModels().await()
        } catch (e: Exception) {
            emptySet()
        }
    }
}
```

#### 4. A/B Testing for Models

**Model A/B Testing Framework:**
```kotlin
import com.google.firebase.remoteconfig.FirebaseRemoteConfig
import com.google.firebase.remoteconfig.FirebaseRemoteConfigSettings

class ModelABTestingManager(private val context: Context) {

    private val remoteConfig = FirebaseRemoteConfig.getInstance()
    private val modelDeployment = ModelDeploymentManager()

    init {
        // Configure Remote Config
        val configSettings = FirebaseRemoteConfigSettings.Builder()
            .setMinimumFetchIntervalInSeconds(3600) // 1 hour
            .build()
        remoteConfig.setConfigSettingsAsync(configSettings)

        // Set default values
        remoteConfig.setDefaultsAsync(
            mapOf(
                "active_model_version" to "v1",
                "model_a_name" to "classifier_v1",
                "model_b_name" to "classifier_v2",
                "model_selection_strategy" to "random", // or "performance_based"
                "model_a_weight" to 50, // 50% traffic
                "model_b_weight" to 50
            )
        )
    }

    /**
     * Fetch and activate latest A/B test configuration
     */
    suspend fun fetchConfig() {
        try {
            remoteConfig.fetchAndActivate().await()
        } catch (e: Exception) {
            Log.e("ABTesting", "Failed to fetch config", e)
        }
    }

    /**
     * Select model based on A/B test configuration
     */
    fun selectModel(): ModelSelection {
        val strategy = remoteConfig.getString("model_selection_strategy")

        return when (strategy) {
            "random" -> selectModelRandomly()
            "performance_based" -> selectModelByPerformance()
            "user_based" -> selectModelByUserId()
            else -> ModelSelection(
                modelName = remoteConfig.getString("active_model_version"),
                variant = "control"
            )
        }
    }

    private fun selectModelRandomly(): ModelSelection {
        val modelAWeight = remoteConfig.getLong("model_a_weight").toInt()
        val modelBWeight = remoteConfig.getLong("model_b_weight").toInt()
        val totalWeight = modelAWeight + modelBWeight

        val random = (0 until totalWeight).random()

        return if (random < modelAWeight) {
            ModelSelection(
                modelName = remoteConfig.getString("model_a_name"),
                variant = "variant_a"
            )
        } else {
            ModelSelection(
                modelName = remoteConfig.getString("model_b_name"),
                variant = "variant_b"
            )
        }
    }

    private fun selectModelByPerformance(): ModelSelection {
        // Load performance metrics from local storage
        val prefs = context.getSharedPreferences("model_metrics", Context.MODE_PRIVATE)
        val modelAAccuracy = prefs.getFloat("model_a_accuracy", 0.5f)
        val modelBAccuracy = prefs.getFloat("model_b_accuracy", 0.5f)

        // Select model with better accuracy
        return if (modelAAccuracy >= modelBAccuracy) {
            ModelSelection(
                modelName = remoteConfig.getString("model_a_name"),
                variant = "variant_a"
            )
        } else {
            ModelSelection(
                modelName = remoteConfig.getString("model_b_name"),
                variant = "variant_b"
            )
        }
    }

    private fun selectModelByUserId(): ModelSelection {
        // Consistent selection based on user ID hash
        val userId = getUserId()
        val hash = userId.hashCode()
        val modelAWeight = remoteConfig.getLong("model_a_weight").toInt()
        val totalWeight = modelAWeight + remoteConfig.getLong("model_b_weight").toInt()

        return if (Math.abs(hash % totalWeight) < modelAWeight) {
            ModelSelection(
                modelName = remoteConfig.getString("model_a_name"),
                variant = "variant_a"
            )
        } else {
            ModelSelection(
                modelName = remoteConfig.getString("model_b_name"),
                variant = "variant_b"
            )
        }
    }

    /**
     * Track model performance metrics
     */
    fun trackModelPerformance(
        modelName: String,
        inferenceTimeMs: Long,
        accuracy: Float?,
        success: Boolean
    ) {
        val prefs = context.getSharedPreferences("model_metrics", Context.MODE_PRIVATE)

        prefs.edit {
            // Update average inference time
            val currentAvgTime = prefs.getFloat("${modelName}_avg_time", 0f)
            val inferenceCount = prefs.getInt("${modelName}_count", 0)
            val newAvgTime = (currentAvgTime * inferenceCount + inferenceTimeMs) / (inferenceCount + 1)

            putFloat("${modelName}_avg_time", newAvgTime)
            putInt("${modelName}_count", inferenceCount + 1)

            // Update accuracy if provided
            accuracy?.let {
                val currentAvgAccuracy = prefs.getFloat("${modelName}_accuracy", 0.5f)
                val newAvgAccuracy = (currentAvgAccuracy * inferenceCount + accuracy) / (inferenceCount + 1)
                putFloat("${modelName}_accuracy", newAvgAccuracy)
            }

            // Track success rate
            val successCount = prefs.getInt("${modelName}_success", 0)
            val failureCount = prefs.getInt("${modelName}_failure", 0)
            if (success) {
                putInt("${modelName}_success", successCount + 1)
            } else {
                putInt("${modelName}_failure", failureCount + 1)
            }
        }

        // Log to Firebase Analytics
        logModelMetrics(modelName, inferenceTimeMs, accuracy, success)
    }

    private fun logModelMetrics(
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

    private fun getUserId(): String {
        val prefs = context.getSharedPreferences("app_prefs", Context.MODE_PRIVATE)
        return prefs.getString("user_id", null) ?: run {
            val newId = UUID.randomUUID().toString()
            prefs.edit { putString("user_id", newId) }
            newId
        }
    }

    /**
     * Get model metrics summary
     */
    fun getModelMetrics(modelName: String): ModelMetrics {
        val prefs = context.getSharedPreferences("model_metrics", Context.MODE_PRIVATE)

        return ModelMetrics(
            modelName = modelName,
            averageInferenceTime = prefs.getFloat("${modelName}_avg_time", 0f),
            inferenceCount = prefs.getInt("${modelName}_count", 0),
            averageAccuracy = prefs.getFloat("${modelName}_accuracy", 0f),
            successCount = prefs.getInt("${modelName}_success", 0),
            failureCount = prefs.getInt("${modelName}_failure", 0)
        )
    }
}

data class ModelSelection(
    val modelName: String,
    val variant: String
)

data class ModelMetrics(
    val modelName: String,
    val averageInferenceTime: Float,
    val inferenceCount: Int,
    val averageAccuracy: Float,
    val successCount: Int,
    val failureCount: Int
) {
    val successRate: Float
        get() = if (inferenceCount > 0) {
            successCount.toFloat() / inferenceCount
        } else 0f
}
```

#### 5. Advanced Model Pipeline

**Multi-Model Inference Pipeline:**
```kotlin
class ModelPipeline(private val context: Context) {

    private val abTestingManager = ModelABTestingManager(context)
    private val modelCache = mutableMapOf<String, Interpreter>()

    /**
     * Run inference through multiple models and ensemble results
     */
    suspend fun runEnsembleInference(
        bitmap: Bitmap,
        labels: List<String>
    ): EnsembleResult = withContext(Dispatchers.Default) {
        // Select models for ensemble
        val primaryModel = abTestingManager.selectModel()
        val ensembleModels = listOf(
            "classifier_v1",
            "classifier_v2",
            "classifier_v3"
        )

        // Run inference on all models in parallel
        val results = ensembleModels.map { modelName ->
            async {
                runSingleModelInference(modelName, bitmap, labels)
            }
        }.awaitAll()

        // Combine results using voting or averaging
        val combinedResult = combineResults(results, labels)

        EnsembleResult(
            primaryResult = results.first(),
            ensembleResult = combinedResult,
            allResults = results
        )
    }

    private suspend fun runSingleModelInference(
        modelName: String,
        bitmap: Bitmap,
        labels: List<String>
    ): ModelInferenceResult {
        val startTime = System.currentTimeMillis()

        return try {
            val interpreter = getOrLoadInterpreter(modelName)

            // Preprocess
            val inputBuffer = preprocessForModel(bitmap, modelName)

            // Run inference
            val outputBuffer = ByteBuffer.allocateDirect(labels.size * 4)
            interpreter.run(inputBuffer, outputBuffer)

            // Process output
            val probabilities = extractProbabilities(outputBuffer, labels)

            val inferenceTime = System.currentTimeMillis() - startTime

            // Track metrics
            abTestingManager.trackModelPerformance(
                modelName,
                inferenceTime,
                probabilities.maxOfOrNull { it.second },
                true
            )

            ModelInferenceResult(
                modelName = modelName,
                classifications = probabilities.map { (label, confidence) ->
                    Classification(label, confidence)
                },
                inferenceTimeMs = inferenceTime,
                success = true
            )
        } catch (e: Exception) {
            abTestingManager.trackModelPerformance(modelName, 0, null, false)

            ModelInferenceResult(
                modelName = modelName,
                classifications = emptyList(),
                inferenceTimeMs = System.currentTimeMillis() - startTime,
                success = false,
                error = e.message
            )
        }
    }

    private fun getOrLoadInterpreter(modelName: String): Interpreter {
        return modelCache.getOrPut(modelName) {
            val modelFile = loadModelFile(modelName)
            Interpreter(modelFile, Interpreter.Options().apply {
                setNumThreads(2)
                setUseNNAPI(false) // Disable for ensemble to avoid conflicts
            })
        }
    }

    private fun loadModelFile(modelName: String): File {
        // Load from assets or downloaded models
        val assetPath = "models/$modelName.tflite"
        return FileUtil.loadMappedFile(context, assetPath)
    }

    private fun preprocessForModel(bitmap: Bitmap, modelName: String): ByteBuffer {
        // Model-specific preprocessing
        val inputSize = when (modelName) {
            "classifier_v1" -> 224
            "classifier_v2" -> 299
            "classifier_v3" -> 331
            else -> 224
        }

        val resizedBitmap = Bitmap.createScaledBitmap(bitmap, inputSize, inputSize, true)

        val buffer = ByteBuffer.allocateDirect(4 * inputSize * inputSize * 3)
        buffer.order(ByteOrder.nativeOrder())

        val pixels = IntArray(inputSize * inputSize)
        resizedBitmap.getPixels(pixels, 0, inputSize, 0, 0, inputSize, inputSize)

        for (pixel in pixels) {
            buffer.putFloat(((pixel shr 16 and 0xFF) - 127.5f) / 127.5f)
            buffer.putFloat(((pixel shr 8 and 0xFF) - 127.5f) / 127.5f)
            buffer.putFloat(((pixel and 0xFF) - 127.5f) / 127.5f)
        }

        return buffer
    }

    private fun extractProbabilities(
        outputBuffer: ByteBuffer,
        labels: List<String>
    ): List<Pair<String, Float>> {
        outputBuffer.rewind()
        return labels.map { label ->
            label to outputBuffer.float
        }.sortedByDescending { it.second }
    }

    private fun combineResults(
        results: List<ModelInferenceResult>,
        labels: List<String>
    ): List<Classification> {
        // Ensemble strategy: Average probabilities
        val averagedScores = mutableMapOf<String, Float>()

        results.filter { it.success }.forEach { result ->
            result.classifications.forEach { classification ->
                averagedScores[classification.label] =
                    (averagedScores[classification.label] ?: 0f) + classification.confidence
            }
        }

        val successCount = results.count { it.success }
        averagedScores.replaceAll { _, score -> score / successCount }

        return averagedScores.entries
            .sortedByDescending { it.value }
            .take(5)
            .map { (label, confidence) ->
                Classification(label, confidence)
            }
    }

    fun release() {
        modelCache.values.forEach { it.close() }
        modelCache.clear()
    }
}

data class ModelInferenceResult(
    val modelName: String,
    val classifications: List<Classification>,
    val inferenceTimeMs: Long,
    val success: Boolean,
    val error: String? = null
)

data class EnsembleResult(
    val primaryResult: ModelInferenceResult,
    val ensembleResult: List<Classification>,
    val allResults: List<ModelInferenceResult>
)
```

#### 6. Model Quantization and Optimization

**Post-Training Quantization:**
```python
# Python script for model optimization (run offline)
import tensorflow as tf

def quantize_model(model_path, output_path):
    """
    Convert TensorFlow model to quantized TFLite
    """
    converter = tf.lite.TFLiteConverter.from_saved_model(model_path)

    # Post-training quantization
    converter.optimizations = [tf.lite.Optimize.DEFAULT]

    # Optional: Full integer quantization
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.uint8
    converter.inference_output_type = tf.uint8

    # Provide representative dataset for calibration
    def representative_dataset():
        for _ in range(100):
            yield [np.random.rand(1, 224, 224, 3).astype(np.float32)]

    converter.representative_dataset = representative_dataset

    # Convert model
    quantized_tflite_model = converter.convert()

    # Save quantized model
    with open(output_path, 'wb') as f:
        f.write(quantized_tflite_model)

    print(f"Model quantized and saved to {output_path}")

# Usage
quantize_model('saved_model/', 'optimized_model.tflite')
```

**Android Model Optimization:**
```kotlin
class OptimizedModelRunner(private val context: Context) {

    /**
     * Load quantized model with GPU delegation
     */
    fun createOptimizedInterpreter(modelPath: String): Interpreter {
        val modelFile = FileUtil.loadMappedFile(context, modelPath)

        val options = Interpreter.Options().apply {
            // Use GPU delegate for better performance
            val gpuDelegate = GpuDelegate()
            addDelegate(gpuDelegate)

            // Or use NNAPI delegate
            // setUseNNAPI(true)

            // Set number of threads
            setNumThreads(4)

            // Allow FP16 precision for GPU
            setAllowFp16PrecisionForFp32(true)
        }

        return Interpreter(modelFile, options)
    }

    /**
     * Benchmark model performance
     */
    suspend fun benchmarkModel(
        interpreter: Interpreter,
        inputBuffer: ByteBuffer,
        iterations: Int = 100
    ): BenchmarkResult = withContext(Dispatchers.Default) {
        val times = mutableListOf<Long>()
        val outputBuffer = ByteBuffer.allocateDirect(1000 * 4) // Adjust size

        repeat(iterations) {
            inputBuffer.rewind()
            val startTime = System.nanoTime()
            interpreter.run(inputBuffer, outputBuffer.rewind())
            val endTime = System.nanoTime()
            times.add((endTime - startTime) / 1_000_000) // Convert to ms
        }

        BenchmarkResult(
            averageTimeMs = times.average(),
            minTimeMs = times.minOrNull() ?: 0.0,
            maxTimeMs = times.maxOrNull() ?: 0.0,
            standardDeviation = calculateStdDev(times)
        )
    }

    private fun calculateStdDev(values: List<Long>): Double {
        val mean = values.average()
        val variance = values.map { (it - mean).pow(2) }.average()
        return sqrt(variance)
    }
}

data class BenchmarkResult(
    val averageTimeMs: Double,
    val minTimeMs: Double,
    val maxTimeMs: Double,
    val standardDeviation: Double
)
```

### Best Practices

1. **Model Deployment:**
   - Bundle a local model as fallback
   - Use Firebase ML for remote model updates
   - Implement download conditions (WiFi, charging)
   - Track model versions

2. **A/B Testing:**
   - Use Firebase Remote Config for experiment configuration
   - Track model performance metrics (inference time, accuracy, crash rate)
   - Implement consistent user assignment (hash-based)
   - Gradual rollout strategy (10% → 50% → 100%)

3. **Model Optimization:**
   - Apply post-training quantization to reduce model size
   - Use GPU/NNAPI delegates for hardware acceleration
   - Benchmark models on target devices
   - Consider model compression techniques

4. **Resource Management:**
   - Load models lazily
   - Implement model caching
   - Release interpreters when not needed
   - Monitor memory usage

5. **Versioning:**
   - Use semantic versioning for models
   - Track model hash/checksum
   - Implement backward compatibility
   - Test model migrations

### Common Pitfalls

1. **Not implementing fallback** → App fails when model download fails
   - Always bundle a local model

2. **Downloading models on cellular** → Expensive data usage
   - Use appropriate download conditions

3. **Loading models on main thread** → UI freeze
   - Load models asynchronously

4. **Not tracking model performance** → Can't evaluate model quality
   - Implement comprehensive metrics tracking

5. **Ignoring model size** → Large app size and slow downloads
   - Apply quantization and compression

6. **Not testing on low-end devices** → Poor performance
   - Benchmark on representative device range

### Summary

Integrating custom TensorFlow Lite models with ML Kit provides flexibility for specialized use cases while maintaining ease of deployment. Firebase ML enables seamless model updates, A/B testing, and monitoring. Proper model optimization (quantization, hardware acceleration) and deployment strategy (fallback, conditional downloads) are essential for production-quality ML features in Android apps.

---



## Ответ (RU)
# Вопрос (RU)
Как интегрировать пользовательские модели TensorFlow Lite с ML Kit? В чём разница между встроенными, динамическими и AutoML моделями? Как реализовать развёртывание моделей, обновления и A/B тестирование?

## Ответ (RU)
ML Kit поддерживает пользовательские модели через интеграцию TensorFlow Lite, позволяя использовать специализированные модели, обученные для конкретных случаев использования. Это обеспечивает гибкость за пределами предобученных моделей ML Kit, сохраняя простоту интеграции.

#### Типы моделей

**1. Локальные модели (Bundled):**
- Упакованы в APK
- Нет зависимости от сети
- Увеличивают размер приложения
- Требуют обновления приложения для обновления модели

**2. Удалённые модели (Dynamic):**
- Размещены в Firebase ML
- Загружаются по требованию
- Можно обновлять без обновления приложения
- Требуют интернет-соединения для первой загрузки

**3. AutoML модели:**
- Обучены через Google Cloud AutoML
- Автоматическая оптимизация архитектуры
- Упрощённый процесс обучения
- Интеграция с Firebase ML

#### Развёртывание и обновление моделей

**Стратегии развёртывания:**
1. **Постепенный rollout**: 10% → 50% → 100%
2. **Условная загрузка**: WiFi + зарядка
3. **Fallback модель**: Локальная резервная копия
4. **Версионирование**: Семантическое версионирование моделей

**A/B тестирование:**
- Firebase Remote Config для конфигурации экспериментов
- Отслеживание метрик производительности
- Консистентное назначение пользователей (на основе хэша)
- Анализ результатов в Firebase Analytics

#### Оптимизация моделей

**Техники оптимизации:**
1. **Post-training quantization**: Уменьшение размера на 75%
2. **GPU delegation**: Ускорение до 10x
3. **NNAPI**: Аппаратное ускорение
4. **Модельное сжатие**: Pruning, knowledge distillation

**Метрики производительности:**
- Время инференса (latency)
- Размер модели
- Точность (accuracy)
- Потребление памяти
- Энергопотребление

### Лучшие практики

1. **Всегда имейте локальную fallback модель**
2. **Используйте условия загрузки (WiFi, зарядка)**
3. **Отслеживайте метрики производительности моделей**
4. **Применяйте квантизацию для уменьшения размера**
5. **Тестируйте на целевом диапазоне устройств**
6. **Реализуйте постепенный rollout для новых моделей**

### Распространённые ошибки

1. Нет fallback модели → сбой при ошибке загрузки
2. Загрузка по мобильной сети → дорогой трафик
3. Загрузка в главном потоке → зависание UI
4. Не отслеживать производительность → нет оценки качества
5. Игнорировать размер модели → большой размер приложения
6. Не тестировать на слабых устройствах → плохая производительность

### Резюме

Интеграция пользовательских моделей TensorFlow Lite с ML Kit обеспечивает гибкость для специализированных случаев использования при сохранении простоты развёртывания. Firebase ML обеспечивает бесшовные обновления моделей, A/B тестирование и мониторинг. Правильная оптимизация моделей (квантизация, аппаратное ускорение) и стратегия развёртывания (fallback, условная загрузка) критически важны для production-качества ML функций в Android приложениях.
