---
id: "20251015082237496"
title: "Mlkit Text Recognition / Распознавание текста ML Kit"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: - Android
  - Kotlin
  - MLKit
  - MachineLearning
  - TextRecognition
---
# ML Kit Text Recognition and OCR

# Question (EN)
> 
Explain how to implement text recognition using ML Kit. How do you handle on-device vs cloud-based text recognition? What are best practices for image preprocessing, optimization, and handling different languages and scripts?

## Answer (EN)
ML Kit provides powerful on-device and cloud-based text recognition capabilities, enabling optical character recognition (OCR) for both Latin and non-Latin scripts with high accuracy and minimal latency.

#### ML Kit Text Recognition Setup

**1. Dependencies**
```kotlin
// app/build.gradle.kts
dependencies {
    // On-device text recognition (bundled with app)
    implementation("com.google.mlkit:text-recognition:16.0.0")

    // On-device text recognition for Chinese, Japanese, Korean, Devanagari
    implementation("com.google.mlkit:text-recognition-chinese:16.0.0")
    implementation("com.google.mlkit:text-recognition-japanese:16.0.0")
    implementation("com.google.mlkit:text-recognition-korean:16.0.0")
    implementation("com.google.mlkit:text-recognition-devanagari:16.0.0")

    // Camera
    implementation("androidx.camera:camera-camera2:1.3.1")
    implementation("androidx.camera:camera-lifecycle:1.3.1")
    implementation("androidx.camera:camera-view:1.3.1")

    // Image processing
    implementation("androidx.core:core-ktx:1.12.0")
}
```

**2. Basic Text Recognition**
```kotlin
// TextRecognitionManager.kt
class TextRecognitionManager(
    private val context: Context
) {
    // Latin script recognizer (bundled)
    private val latinRecognizer = TextRecognition.getClient(
        TextRecognizerOptions.DEFAULT_OPTIONS
    )

    // Chinese script recognizer (requires model download)
    private val chineseRecognizer = TextRecognition.getClient(
        ChineseTextRecognizerOptions.Builder().build()
    )

    // Japanese script recognizer
    private val japaneseRecognizer = TextRecognition.getClient(
        JapaneseTextRecognizerOptions.Builder().build()
    )

    // Korean script recognizer
    private val koreanRecognizer = TextRecognition.getClient(
        KoreanTextRecognizerOptions.Builder().build()
    )

    // Devanagari script recognizer
    private val devanagariRecognizer = TextRecognition.getClient(
        DevanagariTextRecognizerOptions.Builder().build()
    )

    suspend fun recognizeText(
        image: InputImage,
        script: ScriptType = ScriptType.LATIN
    ): Result<Text> = suspendCancellableCoroutine { continuation ->
        val recognizer = when (script) {
            ScriptType.LATIN -> latinRecognizer
            ScriptType.CHINESE -> chineseRecognizer
            ScriptType.JAPANESE -> japaneseRecognizer
            ScriptType.KOREAN -> koreanRecognizer
            ScriptType.DEVANAGARI -> devanagariRecognizer
        }

        recognizer.process(image)
            .addOnSuccessListener { text ->
                continuation.resume(Result.success(text))
            }
            .addOnFailureListener { exception ->
                continuation.resume(Result.failure(exception))
            }

        continuation.invokeOnCancellation {
            // Clean up if needed
        }
    }

    fun close() {
        latinRecognizer.close()
        chineseRecognizer.close()
        japaneseRecognizer.close()
        koreanRecognizer.close()
        devanagariRecognizer.close()
    }
}

enum class ScriptType {
    LATIN, CHINESE, JAPANESE, KOREAN, DEVANAGARI
}
```

**3. Image Preprocessing**
```kotlin
// ImagePreprocessor.kt
class ImagePreprocessor(private val context: Context) {

    suspend fun preprocessImage(
        bitmap: Bitmap,
        config: PreprocessConfig = PreprocessConfig()
    ): Bitmap = withContext(Dispatchers.Default) {
        var processedBitmap = bitmap

        // 1. Resize if too large (optimal: 640x480 to 1920x1080)
        if (config.autoResize) {
            processedBitmap = resizeImage(processedBitmap, config.maxDimension)
        }

        // 2. Convert to grayscale for better OCR
        if (config.convertToGrayscale) {
            processedBitmap = toGrayscale(processedBitmap)
        }

        // 3. Enhance contrast
        if (config.enhanceContrast) {
            processedBitmap = enhanceContrast(processedBitmap)
        }

        // 4. Reduce noise
        if (config.denoiseImage) {
            processedBitmap = denoise(processedBitmap)
        }

        // 5. Rotate if needed (correct orientation)
        if (config.autoRotate) {
            processedBitmap = correctOrientation(processedBitmap)
        }

        // 6. Sharpen image
        if (config.sharpenImage) {
            processedBitmap = sharpen(processedBitmap)
        }

        processedBitmap
    }

    private fun resizeImage(bitmap: Bitmap, maxDimension: Int): Bitmap {
        val width = bitmap.width
        val height = bitmap.height

        if (width <= maxDimension && height <= maxDimension) {
            return bitmap
        }

        val scale = if (width > height) {
            maxDimension.toFloat() / width
        } else {
            maxDimension.toFloat() / height
        }

        val newWidth = (width * scale).toInt()
        val newHeight = (height * scale).toInt()

        return Bitmap.createScaledBitmap(bitmap, newWidth, newHeight, true)
    }

    private fun toGrayscale(bitmap: Bitmap): Bitmap {
        val width = bitmap.width
        val height = bitmap.height

        val grayscaleBitmap = Bitmap.createBitmap(
            width, height,
            Bitmap.Config.ARGB_8888
        )

        val canvas = Canvas(grayscaleBitmap)
        val paint = Paint()
        val colorMatrix = ColorMatrix()
        colorMatrix.setSaturation(0f)
        paint.colorFilter = ColorMatrixColorFilter(colorMatrix)
        canvas.drawBitmap(bitmap, 0f, 0f, paint)

        return grayscaleBitmap
    }

    private fun enhanceContrast(bitmap: Bitmap): Bitmap {
        val width = bitmap.width
        val height = bitmap.height
        val contrastedBitmap = Bitmap.createBitmap(width, height, bitmap.config)

        val canvas = Canvas(contrastedBitmap)
        val paint = Paint()

        // Increase contrast using ColorMatrix
        val colorMatrix = ColorMatrix(
            floatArrayOf(
                1.5f, 0f, 0f, 0f, -50f,  // Red
                0f, 1.5f, 0f, 0f, -50f,  // Green
                0f, 0f, 1.5f, 0f, -50f,  // Blue
                0f, 0f, 0f, 1f, 0f       // Alpha
            )
        )

        paint.colorFilter = ColorMatrixColorFilter(colorMatrix)
        canvas.drawBitmap(bitmap, 0f, 0f, paint)

        return contrastedBitmap
    }

    private fun denoise(bitmap: Bitmap): Bitmap {
        // Simple median filter for noise reduction
        val width = bitmap.width
        val height = bitmap.height
        val denoisedBitmap = Bitmap.createBitmap(width, height, bitmap.config)

        val pixels = IntArray(width * height)
        bitmap.getPixels(pixels, 0, width, 0, 0, width, height)

        val result = IntArray(width * height)
        val windowSize = 3

        for (y in windowSize until height - windowSize) {
            for (x in windowSize until width - windowSize) {
                val window = mutableListOf<Int>()

                for (ky in -windowSize..windowSize) {
                    for (kx in -windowSize..windowSize) {
                        val idx = (y + ky) * width + (x + kx)
                        window.add(pixels[idx])
                    }
                }

                window.sort()
                result[y * width + x] = window[window.size / 2]
            }
        }

        denoisedBitmap.setPixels(result, 0, width, 0, 0, width, height)
        return denoisedBitmap
    }

    private fun correctOrientation(bitmap: Bitmap): Bitmap {
        // Detect and correct text orientation
        // This is a simplified version - in production, use ML-based orientation detection
        return bitmap
    }

    private fun sharpen(bitmap: Bitmap): Bitmap {
        val width = bitmap.width
        val height = bitmap.height
        val sharpenedBitmap = Bitmap.createBitmap(width, height, bitmap.config)

        val canvas = Canvas(sharpenedBitmap)
        val paint = Paint()

        // Sharpening kernel
        val sharpenMatrix = ColorMatrix(
            floatArrayOf(
                0f, -1f, 0f, 0f, 0f,
                -1f, 5f, -1f, 0f, 0f,
                0f, -1f, 0f, 0f, 0f,
                0f, 0f, 0f, 1f, 0f
            )
        )

        paint.colorFilter = ColorMatrixColorFilter(sharpenMatrix)
        canvas.drawBitmap(bitmap, 0f, 0f, paint)

        return sharpenedBitmap
    }
}

data class PreprocessConfig(
    val autoResize: Boolean = true,
    val maxDimension: Int = 1920,
    val convertToGrayscale: Boolean = true,
    val enhanceContrast: Boolean = true,
    val denoiseImage: Boolean = true,
    val autoRotate: Boolean = false,
    val sharpenImage: Boolean = true
)
```

**4. Real-time Camera Text Recognition**
```kotlin
// CameraTextRecognitionScreen.kt
@Composable
fun CameraTextRecognitionScreen(
    viewModel: TextRecognitionViewModel = hiltViewModel()
) {
    val recognizedText by viewModel.recognizedText.collectAsState()
    val isProcessing by viewModel.isProcessing.collectAsState()

    val lifecycleOwner = LocalLifecycleOwner.current
    val context = LocalContext.current

    var preview by remember { mutableStateOf<Preview?>(null) }
    val cameraProviderFuture = remember {
        ProcessCameraProvider.getInstance(context)
    }

    Box(modifier = Modifier.fillMaxSize()) {
        AndroidView(
            factory = { ctx ->
                PreviewView(ctx).apply {
                    scaleType = PreviewView.ScaleType.FILL_CENTER

                    val cameraProvider = cameraProviderFuture.get()
                    val previewUseCase = Preview.Builder().build()
                    preview = previewUseCase

                    val imageAnalyzer = ImageAnalysis.Builder()
                        .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                        .build()
                        .apply {
                            setAnalyzer(
                                Executors.newSingleThreadExecutor()
                            ) { imageProxy ->
                                viewModel.analyzeImage(imageProxy)
                            }
                        }

                    try {
                        cameraProvider.unbindAll()
                        cameraProvider.bindToLifecycle(
                            lifecycleOwner,
                            CameraSelector.DEFAULT_BACK_CAMERA,
                            previewUseCase,
                            imageAnalyzer
                        )

                        previewUseCase.setSurfaceProvider(surfaceProvider)
                    } catch (e: Exception) {
                        Log.e("Camera", "Failed to bind camera", e)
                    }
                }
            },
            modifier = Modifier.fillMaxSize()
        )

        // Overlay with recognized text
        Column(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .fillMaxWidth()
                .background(Color.Black.copy(alpha = 0.7f))
                .padding(16.dp)
        ) {
            if (isProcessing) {
                CircularProgressIndicator(
                    modifier = Modifier.align(Alignment.CenterHorizontally),
                    color = Color.White
                )
            }

            recognizedText?.let { text ->
                Text(
                    text = text,
                    color = Color.White,
                    style = MaterialTheme.typography.bodyLarge,
                    modifier = Modifier.verticalScroll(rememberScrollState())
                )
            }
        }
    }
}

@HiltViewModel
class TextRecognitionViewModel @Inject constructor(
    private val textRecognitionManager: TextRecognitionManager,
    private val imagePreprocessor: ImagePreprocessor
) : ViewModel() {

    private val _recognizedText = MutableStateFlow<String?>(null)
    val recognizedText: StateFlow<String?> = _recognizedText.asStateFlow()

    private val _isProcessing = MutableStateFlow(false)
    val isProcessing: StateFlow<Boolean> = _isProcessing.asStateFlow()

    private var lastProcessedTimestamp = 0L
    private val processingInterval = 1000L // Process every 1 second

    @OptIn(ExperimentalGetImage::class)
    fun analyzeImage(imageProxy: ImageProxy) {
        val currentTime = System.currentTimeMillis()

        if (currentTime - lastProcessedTimestamp < processingInterval) {
            imageProxy.close()
            return
        }

        lastProcessedTimestamp = currentTime

        viewModelScope.launch {
            _isProcessing.value = true

            try {
                val mediaImage = imageProxy.image
                if (mediaImage != null) {
                    val inputImage = InputImage.fromMediaImage(
                        mediaImage,
                        imageProxy.imageInfo.rotationDegrees
                    )

                    val result = textRecognitionManager.recognizeText(
                        image = inputImage,
                        script = ScriptType.LATIN
                    )

                    result.onSuccess { text ->
                        _recognizedText.value = text.text
                    }.onFailure { exception ->
                        Log.e("TextRecognition", "Failed to recognize text", exception)
                    }
                }
            } finally {
                _isProcessing.value = false
                imageProxy.close()
            }
        }
    }

    override fun onCleared() {
        super.onCleared()
        textRecognitionManager.close()
    }
}
```

**5. Document Scanner with Text Extraction**
```kotlin
// DocumentScannerViewModel.kt
@HiltViewModel
class DocumentScannerViewModel @Inject constructor(
    private val textRecognitionManager: TextRecognitionManager,
    private val imagePreprocessor: ImagePreprocessor
) : ViewModel() {

    private val _scannedDocument = MutableStateFlow<ScannedDocument?>(null)
    val scannedDocument: StateFlow<ScannedDocument?> = _scannedDocument.asStateFlow()

    private val _isProcessing = MutableStateFlow(false)
    val isProcessing: StateFlow<Boolean> = _isProcessing.asStateFlow()

    suspend fun scanDocument(
        uri: Uri,
        context: Context
    ): Result<ScannedDocument> {
        _isProcessing.value = true

        return try {
            // Load image
            val bitmap = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                val source = ImageDecoder.createSource(context.contentResolver, uri)
                ImageDecoder.decodeBitmap(source)
            } else {
                @Suppress("DEPRECATION")
                MediaStore.Images.Media.getBitmap(context.contentResolver, uri)
            }

            // Preprocess image
            val preprocessedBitmap = imagePreprocessor.preprocessImage(
                bitmap = bitmap,
                config = PreprocessConfig(
                    autoResize = true,
                    convertToGrayscale = true,
                    enhanceContrast = true,
                    denoiseImage = true,
                    sharpenImage = true
                )
            )

            // Create InputImage
            val inputImage = InputImage.fromBitmap(preprocessedBitmap, 0)

            // Recognize text
            val textResult = textRecognitionManager.recognizeText(
                image = inputImage,
                script = ScriptType.LATIN
            )

            textResult.map { text ->
                val document = ScannedDocument(
                    originalImage = bitmap,
                    processedImage = preprocessedBitmap,
                    fullText = text.text,
                    textBlocks = text.textBlocks.map { block ->
                        TextBlockData(
                            text = block.text,
                            boundingBox = block.boundingBox,
                            confidence = block.confidence ?: 0f,
                            lines = block.lines.map { line ->
                                TextLineData(
                                    text = line.text,
                                    boundingBox = line.boundingBox,
                                    confidence = line.confidence ?: 0f,
                                    elements = line.elements.map { element ->
                                        TextElementData(
                                            text = element.text,
                                            boundingBox = element.boundingBox,
                                            confidence = element.confidence ?: 0f
                                        )
                                    }
                                )
                            }
                        )
                    },
                    timestamp = Clock.System.now()
                )

                _scannedDocument.value = document
                document
            }
        } catch (e: Exception) {
            Result.failure(e)
        } finally {
            _isProcessing.value = false
        }
    }

    fun extractDataFromDocument(document: ScannedDocument): ExtractedData {
        // Extract structured data (emails, phone numbers, dates, etc.)
        val text = document.fullText

        return ExtractedData(
            emails = extractEmails(text),
            phoneNumbers = extractPhoneNumbers(text),
            urls = extractUrls(text),
            dates = extractDates(text),
            addresses = extractAddresses(text)
        )
    }

    private fun extractEmails(text: String): List<String> {
        val emailRegex = "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}".toRegex()
        return emailRegex.findAll(text).map { it.value }.toList()
    }

    private fun extractPhoneNumbers(text: String): List<String> {
        val phoneRegex = "\\+?\\d{1,4}?[-.\\s]?\\(?\\d{1,3}?\\)?[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,4}[-.\\s]?\\d{1,9}".toRegex()
        return phoneRegex.findAll(text).map { it.value }.toList()
    }

    private fun extractUrls(text: String): List<String> {
        val urlRegex = "https?://[\\w\\-._~:/?#\\[\\]@!$&'()*+,;=%]+".toRegex()
        return urlRegex.findAll(text).map { it.value }.toList()
    }

    private fun extractDates(text: String): List<String> {
        val dateRegex = "\\d{1,2}[/-]\\d{1,2}[/-]\\d{2,4}".toRegex()
        return dateRegex.findAll(text).map { it.value }.toList()
    }

    private fun extractAddresses(text: String): List<String> {
        // Simplified address extraction
        val addressRegex = "\\d+\\s+[\\w\\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd)".toRegex()
        return addressRegex.findAll(text).map { it.value }.toList()
    }
}

data class ScannedDocument(
    val originalImage: Bitmap,
    val processedImage: Bitmap,
    val fullText: String,
    val textBlocks: List<TextBlockData>,
    val timestamp: Instant
)

data class TextBlockData(
    val text: String,
    val boundingBox: Rect?,
    val confidence: Float,
    val lines: List<TextLineData>
)

data class TextLineData(
    val text: String,
    val boundingBox: Rect?,
    val confidence: Float,
    val elements: List<TextElementData>
)

data class TextElementData(
    val text: String,
    val boundingBox: Rect?,
    val confidence: Float
)

data class ExtractedData(
    val emails: List<String>,
    val phoneNumbers: List<String>,
    val urls: List<String>,
    val dates: List<String>,
    val addresses: List<String>
)
```

#### Performance Optimization

**1. Model Management**
```kotlin
// ModelDownloadManager.kt
class ModelDownloadManager(
    private val context: Context
) {
    fun downloadModel(
        script: ScriptType,
        onProgress: (progress: Int) -> Unit,
        onComplete: () -> Unit,
        onError: (Exception) -> Unit
    ) {
        val conditions = DownloadConditions.Builder()
            .requireWifi()
            .build()

        val model = when (script) {
            ScriptType.CHINESE -> ChineseTextRecognizerOptions.Builder().build()
            ScriptType.JAPANESE -> JapaneseTextRecognizerOptions.Builder().build()
            ScriptType.KOREAN -> KoreanTextRecognizerOptions.Builder().build()
            ScriptType.DEVANAGARI -> DevanagariTextRecognizerOptions.Builder().build()
            ScriptType.LATIN -> return // Already bundled
        }

        RemoteModelManager.getInstance()
            .download(model, conditions)
            .addOnProgressListener { taskSnapshot ->
                val progress = (taskSnapshot.bytesDownloaded * 100 / taskSnapshot.totalByteCount).toInt()
                onProgress(progress)
            }
            .addOnSuccessListener {
                onComplete()
            }
            .addOnFailureListener { exception ->
                onError(exception)
            }
    }

    fun isModelDownloaded(script: ScriptType): Boolean {
        val model = when (script) {
            ScriptType.CHINESE -> ChineseTextRecognizerOptions.Builder().build()
            ScriptType.JAPANESE -> JapaneseTextRecognizerOptions.Builder().build()
            ScriptType.KOREAN -> KoreanTextRecognizerOptions.Builder().build()
            ScriptType.DEVANAGARI -> DevanagariTextRecognizerOptions.Builder().build()
            ScriptType.LATIN -> return true
        }

        return RemoteModelManager.getInstance()
            .isModelDownloaded(model)
    }

    fun deleteModel(script: ScriptType) {
        val model = when (script) {
            ScriptType.CHINESE -> ChineseTextRecognizerOptions.Builder().build()
            ScriptType.JAPANESE -> JapaneseTextRecognizerOptions.Builder().build()
            ScriptType.KOREAN -> KoreanTextRecognizerOptions.Builder().build()
            ScriptType.DEVANAGARI -> DevanagariTextRecognizerOptions.Builder().build()
            ScriptType.LATIN -> return
        }

        RemoteModelManager.getInstance().deleteDownloadedModel(model)
    }
}
```

**2. Batch Processing**
```kotlin
// BatchTextRecognizer.kt
class BatchTextRecognizer(
    private val textRecognitionManager: TextRecognitionManager
) {
    suspend fun processImages(
        images: List<InputImage>,
        onProgress: (processed: Int, total: Int) -> Unit
    ): List<Result<Text>> = withContext(Dispatchers.Default) {
        val results = mutableListOf<Result<Text>>()

        images.forEachIndexed { index, image ->
            val result = textRecognitionManager.recognizeText(image)
            results.add(result)

            onProgress(index + 1, images.size)

            // Add delay to avoid overwhelming the device
            delay(100)
        }

        results
    }

    suspend fun processImagesInParallel(
        images: List<InputImage>,
        maxConcurrent: Int = 3
    ): List<Result<Text>> = coroutineScope {
        images.chunked(maxConcurrent).flatMap { chunk ->
            chunk.map { image ->
                async {
                    textRecognitionManager.recognizeText(image)
                }
            }.awaitAll()
        }
    }
}
```

#### Best Practices

1. **Image Quality**:
   - Use high-resolution images (at least 640x480)
   - Ensure good lighting conditions
   - Minimize motion blur
   - Keep text orientation correct

2. **Preprocessing**:
   - Convert to grayscale for better accuracy
   - Enhance contrast for faded text
   - Denoise for blurry images
   - Resize to optimal dimensions

3. **Performance**:
   - Throttle camera frame processing
   - Use appropriate thread pools
   - Close recognizers when done
   - Download models on WiFi only

4. **Accuracy**:
   - Choose correct script recognizer
   - Preprocess images appropriately
   - Handle low-confidence results
   - Verify extracted data

5. **User Experience**:
   - Show processing indicators
   - Provide manual correction options
   - Cache results appropriately
   - Handle errors gracefully

#### Common Pitfalls

1. **Poor Image Quality**: Blurry or low-resolution images
2. **Wrong Script Recognizer**: Using Latin for Chinese text
3. **No Preprocessing**: Raw camera images without enhancement
4. **Memory Leaks**: Not closing recognizers
5. **Processing Every Frame**: Throttle camera analysis
6. **Ignoring Confidence**: Accepting low-confidence results

### Summary

ML Kit Text Recognition provides powerful OCR capabilities:
- **On-Device**: Fast, private, works offline
- **Multiple Scripts**: Latin, Chinese, Japanese, Korean, Devanagari
- **Preprocessing**: Critical for accuracy improvement
- **Real-Time**: Camera-based text detection
- **Structured Data**: Extract emails, phones, dates, URLs

Key considerations: image quality, preprocessing, script selection, performance optimization, and user experience.

---

# Вопрос (RU)
> 
Объясните как реализовать text recognition с помощью ML Kit. Как обрабатывать on-device vs cloud-based распознавание текста? Каковы best practices для image preprocessing, оптимизации и обработки разных языков и скриптов?

## Ответ (RU)
ML Kit предоставляет мощные on-device и cloud-based возможности распознавания текста, обеспечивая OCR для латинских и нелатинских скриптов с высокой точностью и минимальной задержкой.

#### Ключевые возможности

**Поддерживаемые скрипты**:
- Latin (встроенный)
- Chinese (требует загрузки модели)
- Japanese (требует загрузки)
- Korean (требует загрузки)
- Devanagari (требует загрузки)

**On-Device**:
- Быстрое распознавание
- Работает offline
- Приватность данных
- Бесплатно

#### Image Preprocessing

**Критические шаги**:
1. Resize (оптимально 640x480 - 1920x1080)
2. Grayscale conversion
3. Contrast enhancement
4. Noise reduction
5. Sharpening

**Techniques**:
- ColorMatrix для grayscale
- Median filter для denoising
- Sharpening kernel
- Contrast adjustment

#### Real-Time Recognition

**Camera Integration**:
- CameraX для camera feed
- ImageAnalysis для frame processing
- Throttling (1 кадр в секунду)
- Background processing

**Performance**:
- Process every N frames
- Use background thread
- Close recognizers properly
- Limit concurrent operations

#### Document Scanning

**Features**:
- Text extraction
- Bounding boxes
- Confidence scores
- Structured data extraction (emails, phones, URLs)

**Data Extraction**:
- Regex для patterns
- Email detection
- Phone number parsing
- Date recognition
- URL extraction

#### Model Management

**Download Strategy**:
- WiFi-only downloads
- Progress tracking
- Model deletion when not needed
- Check availability before use

**Best Practices**:
- Bundle Latin model
- Download others on-demand
- Cache downloaded models
- Handle download failures

#### Оптимизация

**Image Quality**:
- Минимум 640x480 resolution
- Хорошее освещение
- Минимизация motion blur
- Правильная ориентация

**Processing**:
- Batch processing для multiple images
- Parallel processing (3-5 concurrent)
- Throttle camera frames
- Appropriate thread pools

### Резюме

ML Kit Text Recognition обеспечивает мощный OCR:
- **On-Device**: Быстро, приватно, offline
- **Multiple Scripts**: 5+ language families
- **Preprocessing**: Критично для точности
- **Real-Time**: Camera-based detection
- **Structured Data**: Auto-extraction

Ключевые моменты: image quality, preprocessing, script selection, performance optimization, UX.
