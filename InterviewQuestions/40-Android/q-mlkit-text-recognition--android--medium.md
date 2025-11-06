---
id: android-398
title: "ML Kit Text Recognition / Распознавание текста ML Kit"
aliases: ["ML Kit Text Recognition", "MLKit OCR", "OCR Android", "Распознавание текста ML Kit"]
topic: android
subtopics: [camera, media]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-camerax-integration--android--medium]
sources: []
created: 2025-10-15
updated: 2025-10-31
tags: [android/camera, android/media, difficulty/medium, image-processing, mlkit, ocr, text-recognition]
---

# Вопрос (RU)

> Как реализовать распознавание текста с помощью ML Kit? Как обрабатывать on-device vs cloud распознавание? Каковы best practices для предобработки изображений, оптимизации и обработки разных языков и скриптов?

# Question (EN)

> How to implement text recognition using ML Kit? How to handle on-device vs cloud-based recognition? What are best practices for image preprocessing, optimization, and handling different languages and scripts?

---

## Ответ (RU)

ML Kit предоставляет on-device OCR для Latin (встроенный), Chinese, Japanese, Korean, Devanagari (требуют загрузки моделей ~10-30 MB).

### Базовая Реализация

```kotlin
// app/build.gradle.kts
dependencies {
    implementation("com.google.mlkit:text-recognition")
    implementation("com.google.mlkit:text-recognition-chinese")
}

// ✅ Правильно: Suspend wrapper + resource cleanup
class TextRecognitionManager(context: Context) {
    private val latinRecognizer = TextRecognition.getClient(
        TextRecognizerOptions.DEFAULT_OPTIONS
    )

    suspend fun recognizeText(image: InputImage): Result<Text> =
        suspendCancellableCoroutine { continuation ->
            latinRecognizer.process(image)
                .addOnSuccessListener { continuation.resume(Result.success(it)) }
                .addOnFailureListener { continuation.resume(Result.failure(it)) }
        }

    fun close() = latinRecognizer.close()
}

// ❌ Неправильно: Нет close() - утечка памяти
class BadManager {
    private val recognizer = TextRecognition.getClient(...)
}
```

**Ключевые моменты:**
- Latin bundled (0 MB), остальные требуют WiFi download
- On-device: быстро (~50-150ms), offline, приватно
- Cloud API существует, но on-device достаточно для 95% случаев
- Всегда закрывайте recognizers в onCleared()

### Image Preprocessing

Критично для accuracy. Оптимальные размеры: 640x480 - 1920x1080.

```kotlin
class ImagePreprocessor {
    suspend fun preprocessImage(bitmap: Bitmap): Bitmap =
        withContext(Dispatchers.Default) {
            var processed = bitmap

            // 1. ✅ Resize если превышает 1920x1080
            if (bitmap.width > 1920 || bitmap.height > 1920) {
                val scale = min(1920f / bitmap.width, 1920f / bitmap.height)
                processed = Bitmap.createScaledBitmap(
                    bitmap,
                    (bitmap.width * scale).toInt(),
                    (bitmap.height * scale).toInt(),
                    true
                )
            }

            // 2. ✅ Grayscale улучшает OCR на 15-20%
            val result = Bitmap.createBitmap(processed.width, processed.height, ARGB_8888)
            Canvas(result).drawBitmap(processed, 0f, 0f, Paint().apply {
                colorFilter = ColorMatrixColorFilter(ColorMatrix().apply { setSaturation(0f) })
            })

            result
        }
}
```

**Impact:** Grayscale +15-20% accuracy, resize балансирует speed/quality. Contrast enhancement критичен только для low-light.

### Real-time Camera Recognition

```kotlin
@HiltViewModel
class TextRecognitionViewModel @Inject constructor(
    private val manager: TextRecognitionManager
) : ViewModel() {
    private val _recognizedText = MutableStateFlow<String?>(null)
    val recognizedText: StateFlow<String?> = _recognizedText

    private var lastProcessed = 0L
    private val throttleMs = 1000L  // ✅ 1 frame/sec

    @OptIn(ExperimentalGetImage::class)
    fun analyzeImage(imageProxy: ImageProxy) {
        val now = System.currentTimeMillis()

        // ✅ Правильно: Throttling предотвращает CPU overload
        if (now - lastProcessed < throttleMs) {
            imageProxy.close()
            return
        }

        lastProcessed = now
        viewModelScope.launch {
            try {
                val inputImage = InputImage.fromMediaImage(
                    imageProxy.image!!,
                    imageProxy.imageInfo.rotationDegrees
                )
                manager.recognizeText(inputImage)
                    .onSuccess { _recognizedText.value = it.text }
            } finally {
                imageProxy.close()  // ✅ Всегда закрываем
            }
        }
    }

    override fun onCleared() {
        manager.close()
    }
}

// ❌ Неправильно: Processing 30 FPS
fun bad(imageProxy: ImageProxy) {
    // CPU 100%, батарея за 20 минут
    viewModelScope.launch { manager.recognizeText(...) }
}
```

### Document Scanning + Data Extraction

```kotlin
class DocumentScannerViewModel @Inject constructor(
    private val manager: TextRecognitionManager,
    private val preprocessor: ImagePreprocessor
) : ViewModel() {

    suspend fun scanDocument(uri: Uri, context: Context): Result<ScannedDocument> {
        return try {
            val bitmap = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                ImageDecoder.decodeBitmap(ImageDecoder.createSource(context.contentResolver, uri))
            } else {
                MediaStore.Images.Media.getBitmap(context.contentResolver, uri)
            }

            val processed = preprocessor.preprocessImage(bitmap)
            val inputImage = InputImage.fromBitmap(processed, 0)

            manager.recognizeText(inputImage).map { text ->
                ScannedDocument(
                    fullText = text.text,
                    confidence = text.textBlocks.averageOf { it.confidence ?: 0f },
                    emails = extractEmails(text.text),
                    phoneNumbers = extractPhones(text.text)
                )
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // ✅ Regex extraction
    private fun extractEmails(text: String) =
        Regex("[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}")
            .findAll(text).map { it.value }.toList()

    private fun extractPhones(text: String) =
        Regex("\\+?\\d{1,4}[-.\\s]?\\(?\\d{1,3}?\\)?[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,9}")
            .findAll(text).map { it.value }.toList()
}

data class ScannedDocument(
    val fullText: String,
    val confidence: Float,  // 0.0-1.0, обычно >0.8
    val emails: List<String>,
    val phoneNumbers: List<String>
)
```

### Model Management

```kotlin
class ModelDownloadManager(private val context: Context) {
    // ✅ WiFi-only для экономии mobile data
    fun downloadModel(script: ScriptType, onProgress: (Int) -> Unit) {
        if (script == ScriptType.LATIN) return  // Bundled

        val conditions = DownloadConditions.Builder().requireWifi().build()
        val options = ChineseTextRecognizerOptions.Builder().build()

        RemoteModelManager.getInstance()
            .download(options, conditions)
            .addOnProgressListener { snapshot ->
                val progress = (snapshot.bytesDownloaded * 100 / snapshot.totalByteCount).toInt()
                onProgress(progress)
            }
    }

    fun isModelDownloaded(script: ScriptType): Boolean =
        script == ScriptType.LATIN ||
        RemoteModelManager.getInstance().isModelDownloaded(getOptions(script))
}
```

### Best Practices

**Image Quality (критические факторы):**
- Resolution: 640x480 минимум, 1920x1080 оптимум (выше бесполезно)
- Освещение: 300+ lux для document scanning
- ML Kit handles ±45° rotation автоматически

**Preprocessing (в порядке важности):**
1. Grayscale (+15-20% accuracy) - обязательно
2. Resize (balance speed/quality) - обязательно если >1920x1080
3. Contrast (только для low-light)

**Performance:**
- Throttle: 1 frame/sec для camera, 500ms минимум
- Thread: Dispatchers.Default для preprocessing
- Cleanup: всегда close() recognizers
- Battery: throttling экономит 70% батареи

**Accuracy:**
- Confidence threshold: ≥0.8 для production
- Latin fastest (~50ms), CJK ~150ms
- Verify extracted data: regex дает false positives

---

## Answer (EN)

ML Kit provides on-device OCR for Latin (bundled), Chinese, Japanese, Korean, Devanagari (require ~10-30 MB download).

### Basic Implementation

```kotlin
// app/build.gradle.kts
dependencies {
    implementation("com.google.mlkit:text-recognition")
    implementation("com.google.mlkit:text-recognition-chinese")
}

// ✅ Correct: Suspend wrapper + resource cleanup
class TextRecognitionManager(context: Context) {
    private val latinRecognizer = TextRecognition.getClient(
        TextRecognizerOptions.DEFAULT_OPTIONS
    )

    suspend fun recognizeText(image: InputImage): Result<Text> =
        suspendCancellableCoroutine { continuation ->
            latinRecognizer.process(image)
                .addOnSuccessListener { continuation.resume(Result.success(it)) }
                .addOnFailureListener { continuation.resume(Result.failure(it)) }
        }

    fun close() = latinRecognizer.close()
}

// ❌ Wrong: No close() - memory leak
class BadManager {
    private val recognizer = TextRecognition.getClient(...)
}
```

**Key points:**
- Latin bundled (0 MB), others require WiFi download
- On-device: fast (~50-150ms), offline, private
- Cloud API exists, but on-device sufficient for 95% of cases
- Always close recognizers in onCleared()

### Image Preprocessing

Critical for accuracy. Optimal dimensions: 640x480 - 1920x1080.

```kotlin
class ImagePreprocessor {
    suspend fun preprocessImage(bitmap: Bitmap): Bitmap =
        withContext(Dispatchers.Default) {
            var processed = bitmap

            // 1. ✅ Resize if exceeds 1920x1080
            if (bitmap.width > 1920 || bitmap.height > 1920) {
                val scale = min(1920f / bitmap.width, 1920f / bitmap.height)
                processed = Bitmap.createScaledBitmap(
                    bitmap,
                    (bitmap.width * scale).toInt(),
                    (bitmap.height * scale).toInt(),
                    true
                )
            }

            // 2. ✅ Grayscale improves OCR by 15-20%
            val result = Bitmap.createBitmap(processed.width, processed.height, ARGB_8888)
            Canvas(result).drawBitmap(processed, 0f, 0f, Paint().apply {
                colorFilter = ColorMatrixColorFilter(ColorMatrix().apply { setSaturation(0f) })
            })

            result
        }
}
```

**Impact:** Grayscale +15-20% accuracy, resize balances speed/quality. Contrast enhancement critical only for low-light.

### Real-time Camera Recognition

```kotlin
@HiltViewModel
class TextRecognitionViewModel @Inject constructor(
    private val manager: TextRecognitionManager
) : ViewModel() {
    private val _recognizedText = MutableStateFlow<String?>(null)
    val recognizedText: StateFlow<String?> = _recognizedText

    private var lastProcessed = 0L
    private val throttleMs = 1000L  // ✅ 1 frame/sec

    @OptIn(ExperimentalGetImage::class)
    fun analyzeImage(imageProxy: ImageProxy) {
        val now = System.currentTimeMillis()

        // ✅ Correct: Throttling prevents CPU overload
        if (now - lastProcessed < throttleMs) {
            imageProxy.close()
            return
        }

        lastProcessed = now
        viewModelScope.launch {
            try {
                val inputImage = InputImage.fromMediaImage(
                    imageProxy.image!!,
                    imageProxy.imageInfo.rotationDegrees
                )
                manager.recognizeText(inputImage)
                    .onSuccess { _recognizedText.value = it.text }
            } finally {
                imageProxy.close()  // ✅ Always close
            }
        }
    }

    override fun onCleared() {
        manager.close()
    }
}

// ❌ Wrong: Processing 30 FPS
fun bad(imageProxy: ImageProxy) {
    // CPU 100%, drains battery in 20 minutes
    viewModelScope.launch { manager.recognizeText(...) }
}
```

### Document Scanning + Data Extraction

```kotlin
class DocumentScannerViewModel @Inject constructor(
    private val manager: TextRecognitionManager,
    private val preprocessor: ImagePreprocessor
) : ViewModel() {

    suspend fun scanDocument(uri: Uri, context: Context): Result<ScannedDocument> {
        return try {
            val bitmap = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                ImageDecoder.decodeBitmap(ImageDecoder.createSource(context.contentResolver, uri))
            } else {
                MediaStore.Images.Media.getBitmap(context.contentResolver, uri)
            }

            val processed = preprocessor.preprocessImage(bitmap)
            val inputImage = InputImage.fromBitmap(processed, 0)

            manager.recognizeText(inputImage).map { text ->
                ScannedDocument(
                    fullText = text.text,
                    confidence = text.textBlocks.averageOf { it.confidence ?: 0f },
                    emails = extractEmails(text.text),
                    phoneNumbers = extractPhones(text.text)
                )
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // ✅ Regex extraction
    private fun extractEmails(text: String) =
        Regex("[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}")
            .findAll(text).map { it.value }.toList()

    private fun extractPhones(text: String) =
        Regex("\\+?\\d{1,4}[-.\\s]?\\(?\\d{1,3}?\\)?[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,9}")
            .findAll(text).map { it.value }.toList()
}

data class ScannedDocument(
    val fullText: String,
    val confidence: Float,  // 0.0-1.0, typically >0.8
    val emails: List<String>,
    val phoneNumbers: List<String>
)
```

### Model Management

```kotlin
class ModelDownloadManager(private val context: Context) {
    // ✅ WiFi-only to save mobile data
    fun downloadModel(script: ScriptType, onProgress: (Int) -> Unit) {
        if (script == ScriptType.LATIN) return  // Bundled

        val conditions = DownloadConditions.Builder().requireWifi().build()
        val options = ChineseTextRecognizerOptions.Builder().build()

        RemoteModelManager.getInstance()
            .download(options, conditions)
            .addOnProgressListener { snapshot ->
                val progress = (snapshot.bytesDownloaded * 100 / snapshot.totalByteCount).toInt()
                onProgress(progress)
            }
    }

    fun isModelDownloaded(script: ScriptType): Boolean =
        script == ScriptType.LATIN ||
        RemoteModelManager.getInstance().isModelDownloaded(getOptions(script))
}
```

### Best Practices

**Image Quality (critical factors):**
- Resolution: 640x480 minimum, 1920x1080 optimal (higher is useless)
- Lighting: 300+ lux for document scanning
- ML Kit handles ±45° rotation automatically

**Preprocessing (in order of importance):**
1. Grayscale (+15-20% accuracy) - mandatory
2. Resize (balance speed/quality) - mandatory if >1920x1080
3. Contrast (only for low-light)

**Performance:**
- Throttle: 1 frame/sec for camera, 500ms minimum
- Thread: Dispatchers.Default for preprocessing
- Cleanup: always close() recognizers
- Battery: throttling saves 70% battery

**Accuracy:**
- Confidence threshold: ≥0.8 for production
- Latin fastest (~50ms), CJK ~150ms
- Verify extracted data: regex produces false positives

---

## Follow-ups

1. How does ML Kit handle rotated or skewed text in images?
2. What are accuracy differences between on-device Latin vs other script recognizers?
3. How to implement batch processing for multiple document scans efficiently?
4. What preprocessing techniques work best for handwritten text recognition?
5. How to handle mixed-language documents (e.g., English + Chinese)?

## References

- [[c-camerax]] - CameraX integration patterns
- [[c-coroutines]] - Async processing with coroutines
- [[c-dependency-injection]] - Hilt/Koin setup
- [ML Kit Text Recognition Guide](https://developers.google.com/ml-kit/vision/text-recognition)
- [CameraX Image Analysis](https://developer.android.com/training/camerax/analyze)

## Related Questions

### Prerequisites (Easier)
- Related content to be added

### Related (Same Level)
- [[q-camerax-integration--android--medium]] - Advanced CameraX patterns

### Advanced (Harder)
- Related content to be added
