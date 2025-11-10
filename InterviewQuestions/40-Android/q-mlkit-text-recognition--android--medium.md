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
related: [q-android-async-primitives--android--easy, c-coroutines]
sources: []
created: 2025-10-15
updated: 2025-11-10
tags: [android/camera, android/media, difficulty/medium, image-processing, mlkit, ocr, text-recognition]

---

# Вопрос (RU)

> Как реализовать распознавание текста с помощью ML Kit? Как обрабатывать on-device vs cloud распознавание? Каковы best practices для предобработки изображений, оптимизации и обработки разных языков и скриптов?

# Question (EN)

> How to implement text recognition using ML Kit? How to handle on-device vs cloud-based recognition? What are best practices for image preprocessing, optimization, and handling different languages and scripts?

---

## Ответ (RU)

ML Kit предоставляет on-device OCR для разных скриптов через отдельные модули: Latin, Chinese, Japanese, Korean, Devanagari (каждый требует загрузки модели ~10–30 MB при первом использовании, кроме Latin, который встроен).

### Базовая Реализация

```kotlin
// app/build.gradle.kts
// Пример для Latin и Chinese Text Recognition v2
dependencies {
    implementation("com.google.mlkit:text-recognition-latin:16.0.0")
    implementation("com.google.mlkit:text-recognition-chinese:16.0.0")
}

// ✅ Правильно: Suspend-обертка + явное управление ресурсами
class TextRecognitionManager(context: Context) {
    private val latinRecognizer = TextRecognition.getClient(
        TextRecognizerOptions.DEFAULT_OPTIONS
    )

    suspend fun recognizeText(image: InputImage): Result<Text> =
        suspendCancellableCoroutine { continuation ->
            val task = latinRecognizer.process(image)
            task
                .addOnSuccessListener { result ->
                    if (continuation.isActive) {
                        continuation.resume(Result.success(result))
                    }
                }
                .addOnFailureListener { e ->
                    if (continuation.isActive) {
                        continuation.resume(Result.failure(e))
                    }
                }

            // Опционально: при отмене корутины можно отменить Task, если это критично
            continuation.invokeOnCancellation {
                task.cancel()
            }
        }

    fun close() = latinRecognizer.close()
}

// 🔎 Плохо на практике: создание множества recognizer-экземпляров без закрытия
// повышает потребление памяти/ресурсов. Используйте скоуп и close(), когда более не нужно.
class BadManager {
    private val recognizer = TextRecognition.getClient(/* options */)
}
```

**Ключевые моменты:**
- Latin распознавание встроено (модель поставляется с библиотекой), остальные скрипты загружаются отдельно при первом использовании.
- On-device: быстро (~десятки-сотни мс), offline, приватно; подходит для большинства сценариев.
- Облачное распознавание (Cloud Vision / Firebase ML) — отдельный сервис; выбирайте его только при жёстких требованиях к качеству, редким скриптам или сложным документам.
- Закрывайте recognizers, когда они больше не нужны (например, в onCleared() `ViewModel` или при уничтожении компонента), чтобы освободить ресурсы.

### Image Preprocessing

Качество входного изображения критично для точности. Практичные размеры: от 640x480 до 1920x1080; значительно большие размеры дают убывающую отдачу и повышают задержки.

```kotlin
class ImagePreprocessor {
    suspend fun preprocessImage(bitmap: Bitmap): Bitmap =
        withContext(Dispatchers.Default) {
            var processed = bitmap

            // 1. ✅ Resize, если одна из сторон > 1920
            if (bitmap.width > 1920 || bitmap.height > 1920) {
                val scale = min(1920f / bitmap.width, 1920f / bitmap.height)
                processed = Bitmap.createScaledBitmap(
                    bitmap,
                    (bitmap.width * scale).toInt(),
                    (bitmap.height * scale).toInt(),
                    true
                )
            }

            // 2. ✅ Grayscale: упрощает картинку и может улучшить устойчивость на некоторых сценариях
            val result = Bitmap.createBitmap(processed.width, processed.height, Bitmap.Config.ARGB_8888)
            Canvas(result).drawBitmap(processed, 0f, 0f, Paint().apply {
                colorFilter = ColorMatrixColorFilter(ColorMatrix().apply { setSaturation(0f) })
            })

            result
        }
}
```

**Замечания:**
- Перевод в grayscale и изменение размера часто помогают балансировать скорость и качество, но прирост точности зависит от устройства и данных; любые конкретные проценты улучшения следует считать приблизительными, а не гарантированными.
- Повышение контраста полезно для низкой освещенности и слабого контраста, но не всегда необходимо.

### Real-time Camera Recognition

```kotlin
@HiltViewModel
class TextRecognitionViewModel @Inject constructor(
    private val manager: TextRecognitionManager
) : ViewModel() {
    private val _recognizedText = MutableStateFlow<String?>(null)
    val recognizedText: StateFlow<String?> = _recognizedText

    private var lastProcessed = 0L
    private val throttleMs = 1000L  // ✅ 1 frame/sec (пример разумного троттлинга)

    @OptIn(ExperimentalGetImage::class)
    fun analyzeImage(imageProxy: ImageProxy) {
        val now = System.currentTimeMillis()

        // ✅ Троттлинг уменьшает нагрузку на CPU и экономит батарею
        if (now - lastProcessed < throttleMs) {
            imageProxy.close()
            return
        }

        lastProcessed = now
        val mediaImage = imageProxy.image
        if (mediaImage == null) {
            imageProxy.close()
            return
        }

        val inputImage = InputImage.fromMediaImage(
            mediaImage,
            imageProxy.imageInfo.rotationDegrees
        )

        viewModelScope.launch {
            try {
                manager.recognizeText(inputImage)
                    .onSuccess { _recognizedText.value = it.text }
                    .onFailure { /* логирование / обработка ошибок */ }
            } finally {
                imageProxy.close()  // ✅ Всегда закрываем
            }
        }
    }

    override fun onCleared() {
        manager.close()
        super.onCleared()
    }
}

// ❌ Плохо: попытка обрабатывать каждый кадр (30 FPS) тяжёлыми ML-вызовами
fun bad(imageProxy: ImageProxy) {
    // Это приведёт к высокой загрузке CPU/батареи и очереди необработанных кадров.
    // viewModelScope.launch { manager.recognizeText(...) }
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
                @Suppress("DEPRECATION")
                MediaStore.Images.Media.getBitmap(context.contentResolver, uri)
            }

            val processed = preprocessor.preprocessImage(bitmap)
            val inputImage = InputImage.fromBitmap(processed, 0)

            manager.recognizeText(inputImage).map { text ->
                ScannedDocument(
                    fullText = text.text,
                    // У API TextRecognition нет общего поля confidence для всего блока текста;
                    // при необходимости используйте наличные confidence-поля элементов/символов.
                    confidenceHint = null,
                    emails = extractEmails(text.text),
                    phoneNumbers = extractPhones(text.text)
                )
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // ✅ Regex extraction (пример, может давать false positives)
    private fun extractEmails(text: String) =
        Regex("[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}")
            .findAll(text).map { it.value }.toList()

    private fun extractPhones(text: String) =
        Regex("\\+?\\d{1,4}[-.\\s]?\\(?\\d{1,3}?\\)?[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,9}")
            .findAll(text).map { it.value }.toList()
}

data class ScannedDocument(
    val fullText: String,
    val confidenceHint: Float?,  // Может быть рассчитанным или null, в зависимости от используемого API
    val emails: List<String>,
    val phoneNumbers: List<String>
)
```

### Model Management

```kotlin
enum class ScriptType { LATIN, CHINESE, JAPANESE, KOREAN, DEVANAGARI }

class ModelDownloadManager(private val context: Context) {
    // ✅ Пример: принудительная загрузка модели для конкретного скрипта (на основе опций)
    fun downloadModelIfNeeded(script: ScriptType, onProgress: (Int) -> Unit) {
        if (script == ScriptType.LATIN) return  // Latin модель уже доступна с библиотекой

        val conditions = DownloadConditions.Builder()
            .requireWifi()
            .build()

        val options = when (script) {
            ScriptType.CHINESE -> ChineseTextRecognizerOptions.Builder().build()
            ScriptType.JAPANESE -> JapaneseTextRecognizerOptions.Builder().build()
            ScriptType.KOREAN -> KoreanTextRecognizerOptions.Builder().build()
            ScriptType.DEVANAGARI -> DevanagariTextRecognizerOptions.Builder().build()
            ScriptType.LATIN -> return
        }

        val client = TextRecognition.getClient(options)
        client.downloadModelIfNeeded(conditions)
            .addOnProgressListener { snapshot ->
                val total = snapshot.totalByteCount
                if (total > 0) {
                    val progress = (snapshot.bytesDownloaded * 100 / total).toInt()
                    onProgress(progress)
                }
            }
    }
}
```

### Best Practices

**Качество изображения (важные факторы):**
- Разрешение: не ниже 640x480; диапазон до 1920x1080 обычно даёт хороший баланс между качеством и скоростью.
- Освещение: хорошее освещение существенно повышает точность; избегайте сильных бликов и шума.
- ML Kit автоматически обрабатывает типичные повороты (rotationDegrees), умеренный наклон и перспективные искажения, но сильный skew лучше корректировать на стороне клиента.

**Preprocessing (приоритетно):**
1. Нормальный размер кадра (уменьшение очень больших изображений).
2. Нормальное освещение и контраст; при необходимости — автоконтраст или бинаризация.
3. Grayscale как простой способ уменьшить шум цветовой компоненты, если это улучшает качество на ваших данных.

**Performance:**
- Троттлинг: обрабатывать не каждый кадр, а с интервалом (например, 500–1000 мс) или по событию.
- Heavy-предобработку выполнять на Dispatchers.Default / worker threads.
- Закрывать recognizer'ы, когда они больше не используются.
- Избегать очереди из необработанных ImageProxy: всегда закрывайте кадр.

**Accuracy:**
- Используйте собственные эвристики и пороги уверенности; значение вроде 0.8 — это стартовая рекомендация, а не универсальное правило.
- Модели для латиницы обычно быстрее и могут показывать лучшую точность на латинских текстах по сравнению с сложными иероглифическими скриптами.
- Постобработка (regex, валидация форматов) помогает отсечь ложные срабатывания, но не гарантирует 100% точность.

---

## Answer (EN)

ML Kit provides on-device OCR for different scripts via separate modules: Latin, Chinese, Japanese, Korean, Devanagari. Latin is bundled via its library; other script models are downloaded on demand (typically ~10–30 MB each).

### Basic Implementation

```kotlin
// app/build.gradle.kts
// Example for Text Recognition v2 (Latin + Chinese)
dependencies {
    implementation("com.google.mlkit:text-recognition-latin:16.0.0")
    implementation("com.google.mlkit:text-recognition-chinese:16.0.0")
}

// ✅ Correct: suspend wrapper + explicit resource management
class TextRecognitionManager(context: Context) {
    private val latinRecognizer = TextRecognition.getClient(
        TextRecognizerOptions.DEFAULT_OPTIONS
    )

    suspend fun recognizeText(image: InputImage): Result<Text> =
        suspendCancellableCoroutine { continuation ->
            val task = latinRecognizer.process(image)
            task
                .addOnSuccessListener { result ->
                    if (continuation.isActive) {
                        continuation.resume(Result.success(result))
                    }
                }
                .addOnFailureListener { e ->
                    if (continuation.isActive) {
                        continuation.resume(Result.failure(e))
                    }
                }

            // Optionally cancel the Task if coroutine is cancelled
            continuation.invokeOnCancellation {
                task.cancel()
            }
        }

    fun close() = latinRecognizer.close()
}

// 🔎 Not ideal: creating many recognizer instances and never closing them
// can waste memory/resources. Prefer scoped usage and close() when done.
class BadManager {
    private val recognizer = TextRecognition.getClient(/* options */)
}
```

**Key points:**
- Latin model is available with the library; other script models are downloaded on first use.
- On-device: fast (tens to low hundreds of ms), offline, privacy-preserving; suitable for most use cases.
- Cloud-based text recognition (Cloud Vision / Firebase ML) is a separate product; use it only when you need higher accuracy on complex layouts, rare scripts, or server-side processing.
- Close recognizers when they are no longer needed (e.g., in `ViewModel`.onCleared or component teardown) to release resources.

### Image Preprocessing

Image quality is critical for accuracy. Practical dimensions: from 640x480 up to around 1920x1080; much higher resolutions increase latency with diminishing returns.

```kotlin
class ImagePreprocessor {
    suspend fun preprocessImage(bitmap: Bitmap): Bitmap =
        withContext(Dispatchers.Default) {
            var processed = bitmap

            // 1. ✅ Resize if one side > 1920
            if (bitmap.width > 1920 || bitmap.height > 1920) {
                val scale = min(1920f / bitmap.width, 1920f / bitmap.height)
                processed = Bitmap.createScaledBitmap(
                    bitmap,
                    (bitmap.width * scale).toInt(),
                    (bitmap.height * scale).toInt(),
                    true
                )
            }

            // 2. ✅ Grayscale: simplifies the image and can help robustness in some cases
            val result = Bitmap.createBitmap(processed.width, processed.height, Bitmap.Config.ARGB_8888)
            Canvas(result).drawBitmap(processed, 0f, 0f, Paint().apply {
                colorFilter = ColorMatrixColorFilter(ColorMatrix().apply { setSaturation(0f) })
            })

            result
        }
}
```

**Notes:**
- Grayscale and resizing often help balance speed and quality, but exact gains depend on device and data; any specific improvement figures should be treated as rough heuristics rather than guarantees.
- Contrast enhancement is useful for low-light or low-contrast input but is not universally required.

### Real-time Camera Recognition

```kotlin
@HiltViewModel
class TextRecognitionViewModel @Inject constructor(
    private val manager: TextRecognitionManager
) : ViewModel() {
    private val _recognizedText = MutableStateFlow<String?>(null)
    val recognizedText: StateFlow<String?> = _recognizedText

    private var lastProcessed = 0L
    private val throttleMs = 1000L  // ✅ 1 frame/sec as a reasonable throttling example

    @OptIn(ExperimentalGetImage::class)
    fun analyzeImage(imageProxy: ImageProxy) {
        val now = System.currentTimeMillis()

        // ✅ Throttling prevents CPU overload and reduces battery drain
        if (now - lastProcessed < throttleMs) {
            imageProxy.close()
            return
        }

        lastProcessed = now
        val mediaImage = imageProxy.image
        if (mediaImage == null) {
            imageProxy.close()
            return
        }

        val inputImage = InputImage.fromMediaImage(
            mediaImage,
            imageProxy.imageInfo.rotationDegrees
        )

        viewModelScope.launch {
            try {
                manager.recognizeText(inputImage)
                    .onSuccess { _recognizedText.value = it.text }
                    .onFailure { /* log / handle error */ }
            } finally {
                imageProxy.close()  // ✅ Always close
            }
        }
    }

    override fun onCleared() {
        manager.close()
        super.onCleared()
    }
}

// ❌ Not recommended: running heavy recognition on every frame (~30 FPS)
fun bad(imageProxy: ImageProxy) {
    // This will saturate CPU and drain battery; avoid naive per-frame processing.
    // viewModelScope.launch { manager.recognizeText(...) }
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
                @Suppress("DEPRECATION")
                MediaStore.Images.Media.getBitmap(context.contentResolver, uri)
            }

            val processed = preprocessor.preprocessImage(bitmap)
            val inputImage = InputImage.fromBitmap(processed, 0)

            manager.recognizeText(inputImage).map { text ->
                ScannedDocument(
                    fullText = text.text,
                    // Text Recognition API does not expose a single global confidence.
                    // If needed, derive your own metric from element/line/character confidences.
                    confidenceHint = null,
                    emails = extractEmails(text.text),
                    phoneNumbers = extractPhones(text.text)
                )
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // ✅ Regex extraction example (may produce false positives)
    private fun extractEmails(text: String) =
        Regex("[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}")
            .findAll(text).map { it.value }.toList()

    private fun extractPhones(text: String) =
        Regex("\\+?\\d{1,4}[-.\\s]?\\(?\\d{1,3}?\\)?[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,9}")
            .findAll(text).map { it.value }.toList()
}

data class ScannedDocument(
    val fullText: String,
    val confidenceHint: Float?,  // null or custom aggregate metric
    val emails: List<String>,
    val phoneNumbers: List<String>
)
```

### Model Management

```kotlin
enum class ScriptType { LATIN, CHINESE, JAPANESE, KOREAN, DEVANAGARI }

class ModelDownloadManager(private val context: Context) {
    // ✅ Example: proactively ensure model download for a given script using v2 APIs
    fun downloadModelIfNeeded(script: ScriptType, onProgress: (Int) -> Unit) {
        if (script == ScriptType.LATIN) return  // Latin is available with the library

        val conditions = DownloadConditions.Builder()
            .requireWifi()
            .build()

        val options = when (script) {
            ScriptType.CHINESE -> ChineseTextRecognizerOptions.Builder().build()
            ScriptType.JAPANESE -> JapaneseTextRecognizerOptions.Builder().build()
            ScriptType.KOREAN -> KoreanTextRecognizerOptions.Builder().build()
            ScriptType.DEVANAGARI -> DevanagariTextRecognizerOptions.Builder().build()
            ScriptType.LATIN -> return
        }

        val client = TextRecognition.getClient(options)
        client.downloadModelIfNeeded(conditions)
            .addOnProgressListener { snapshot ->
                val total = snapshot.totalByteCount
                if (total > 0) {
                    val progress = (snapshot.bytesDownloaded * 100 / total).toInt()
                    onProgress(progress)
                }
            }
    }
}
```

### Best Practices

**Image Quality (critical factors):**
- Resolution: at least 640x480; up to around 1920x1080 is typically a good balance.
- Lighting: good, even lighting significantly improves accuracy; avoid glare and heavy noise.
- ML Kit handles normal rotations (via rotationDegrees) and moderate skew; strong skew/perspective may require client-side correction.

**Preprocessing (in order of importance):**
1. Reasonable downscaling of very large images.
2. Adequate lighting and contrast; apply contrast/thresholding when needed.
3. Grayscale as a simple, sometimes helpful optimization.

**Performance:**
- Throttle processing (e.g., every 500–1000 ms) or trigger on demand instead of every frame.
- Run heavy preprocessing on Dispatchers.Default / background threads.
- Always close ImageProxy and release recognizers when no longer needed.
- Avoid building up a backlog of frames.

**Accuracy:**
- Tune confidence thresholds empirically for your use case; 0.8 is a common starting point, not a rule.
- Latin models are typically faster; complex scripts (CJK, etc.) may be slower and need more tuning.
- Post-processing (regex, checksums, format validation) helps filter out false positives.

---

## Дополнительные вопросы (RU)

1. Как ML Kit обрабатывает повёрнутый или перспективно искажённый текст на изображении?
2. Каковы практические trade-off'ы между on-device и облачным распознаванием текста в проде?
3. Как спроектировать пайплайн CameraX + ML Kit, чтобы избежать очереди кадров и ANR?
4. Как обрабатывать документы с несколькими языками (например, английский + китайский) с использованием нескольких recognizer'ов?
5. Как безопасно сохранять и синхронизировать распознанный текст на устройстве и в бэкенде?

## Follow-ups

1. How does ML Kit handle rotated or skewed text in images?
2. What are the trade-offs between on-device and cloud-based text recognition for production apps?
3. How to design a CameraX + ML Kit pipeline to avoid frame backlog and ANRs?
4. How to support mixed-language documents (e.g., English + Chinese) with multiple recognizers?
5. How to persist and sync recognized text securely on-device and in the backend?

## Ссылки (RU)

- [[c-coroutines]]
- [ML Kit Text Recognition Guide](https://developers.google.com/ml-kit/vision/text-recognition)
- [CameraX Image Analysis](https://developer.android.com/training/camerax/analyze)

## References

- [[c-coroutines]]
- [ML Kit Text Recognition Guide](https://developers.google.com/ml-kit/vision/text-recognition)
- [CameraX Image Analysis](https://developer.android.com/training/camerax/analyze)

## Связанные вопросы (RU)

### База (проще)
- [[q-android-async-primitives--android--easy]]

### Похожие (средний уровень)
- [[q-mlkit-object-detection--android--medium]]
- [[q-biometric-authentication--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]

### Продвинутое (сложнее)
- [[q-mlkit-custom-models--android--hard]]
- [[q-tflite-acceleration-strategies--android--hard]]

## Related Questions

### Prerequisites (Easier)
- [[q-android-async-primitives--android--easy]]

### Related (Same Level)
- [[q-mlkit-object-detection--android--medium]]
- [[q-biometric-authentication--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]

### Advanced (Harder)
- [[q-mlkit-custom-models--android--hard]]
- [[q-tflite-acceleration-strategies--android--hard]]
