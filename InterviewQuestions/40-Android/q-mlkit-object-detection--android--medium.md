---
id: 20251012-12271140
title: "ML Kit Object Detection / Распознавание объектов ML Kit"
aliases: [ML Kit Object Detection, Распознавание объектов ML Kit, ML Kit Image Labeling, ML Kit Barcode Scanning]
topic: android
subtopics: [camera, media]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-compose-performance-optimization--android--hard, q-when-can-the-system-restart-a-service--android--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [android/camera, android/media, ml-kit, object-detection, barcode-scanning, difficulty/medium]
---

# Вопрос (RU)

> Как реализовать обнаружение объектов, распознавание изображений и сканирование штрих-кодов с помощью ML Kit? В чём разница между моделями на устройстве и облачными моделями? Как обрабатывать обнаружение в реальном времени с камеры?

# Question (EN)

> How do you implement object detection, image labeling, and barcode scanning using ML Kit? What are the differences between on-device and cloud-based models? How do you handle real-time detection with camera input?

---

## Ответ (RU)

ML Kit предоставляет предобученные модели для визуального распознавания без необходимости ML-экспертизы.

### Маркировка изображений

**On-Device vs Cloud:**
- **On-Device**: ~400 меток, офлайн, 100-300мс задержка, приватность
- **Cloud**: 10,000+ меток, требует интернет, 500-1500мс, лучшая точность

✅ **Лучшая практика - On-Device маркировка:**
```kotlin
class ImageLabelingManager(private val context: Context) {
    private val labeler = ImageLabeling.getClient(
        ImageLabelerOptions.Builder()
            .setConfidenceThreshold(0.7f)
            .build()
    )

    suspend fun labelImage(image: InputImage): Result<List<ImageLabel>> {
        return try {
            val labels = labeler.process(image).await()
            Result.success(labels)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    fun release() = labeler.close()
}
```

✅ **Гибридный подход (Cloud с fallback):**
```kotlin
suspend fun labelImageHybrid(
    image: InputImage,
    cloudLabeler: ImageLabeler,
    onDeviceLabeler: ImageLabeler
): LabelingResult {
    val cloudResult = runCatching {
        cloudLabeler.process(image).await()
    }

    return if (cloudResult.isSuccess) {
        LabelingResult(cloudResult.getOrThrow(), LabelSource.CLOUD)
    } else {
        LabelingResult(onDeviceLabeler.process(image).await(), LabelSource.ON_DEVICE)
    }
}
```

### Обнаружение объектов

**Режимы:**
- **STREAM_MODE**: Видео/камера в реальном времени
- **SINGLE_IMAGE_MODE**: Статические изображения

✅ **Обнаружение с отслеживанием:**
```kotlin
class ObjectDetectionManager {
    private val detector = ObjectDetection.getClient(
        ObjectDetectorOptions.Builder()
            .setDetectorMode(ObjectDetectorOptions.STREAM_MODE)
            .enableMultipleObjects()
            .enableClassification()
            .build()
    )

    suspend fun detectObjects(image: InputImage): List<DetectedObject> {
        return detector.process(image).await()
    }

    fun release() = detector.close()
}

data class ObjectInfo(
    val trackingId: Int?,
    val boundingBox: Rect,
    val labels: List<ObjectLabel>
)
```

✅ **Отслеживание движения:**
```kotlin
class ObjectTracker {
    private val tracked = mutableMapOf<Int, TrackedHistory>()

    fun updateTracking(objects: List<DetectedObject>) {
        objects.forEach { obj ->
            obj.trackingId?.let { id ->
                tracked.getOrPut(id) { TrackedHistory(id) }
                    .addPosition(
                        obj.boundingBox.centerX().toFloat(),
                        obj.boundingBox.centerY().toFloat()
                    )
            }
        }

        removeStaleObjects()
    }

    private fun removeStaleObjects() {
        val now = System.currentTimeMillis()
        tracked.entries.removeIf { (_, history) ->
            now - history.lastSeen > 5000
        }
    }
}
```

### Сканирование штрих-кодов

**Поддерживаемые форматы:**
- 1D: EAN-13, EAN-8, UPC, Code-128, Code-39
- 2D: QR Code, Aztec, PDF417, Data Matrix

✅ **Сканер с обработкой типов:**
```kotlin
class BarcodeScanningManager {
    private val scanner = BarcodeScanning.getClient(
        BarcodeScannerOptions.Builder()
            .setBarcodeFormats(
                Barcode.FORMAT_QR_CODE,
                Barcode.FORMAT_EAN_13,
                Barcode.FORMAT_CODE_128
            )
            .build()
    )

    suspend fun scanBarcodes(image: InputImage): List<Barcode> {
        return scanner.process(image).await()
    }

    fun handleBarcode(barcode: Barcode, context: Context) {
        when (barcode.valueType) {
            Barcode.TYPE_URL -> openUrl(context, barcode.url?.url)
            Barcode.TYPE_WIFI -> connectToWifi(context, barcode.wifi)
            Barcode.TYPE_EMAIL -> openEmail(context, barcode.email)
            Barcode.TYPE_PHONE -> dialPhone(context, barcode.phone?.number)
            else -> copyToClipboard(context, barcode.rawValue)
        }
    }

    fun release() = scanner.close()
}
```

### Интеграция камеры в реальном времени

✅ **CameraX + ML Kit:**
```kotlin
class MLKitCameraAnalyzer(
    private val context: Context,
    private val lifecycleOwner: LifecycleOwner,
    private val previewView: PreviewView
) {
    private var detector: ImageLabeler? = null
    private val cameraExecutor = Executors.newSingleThreadExecutor()

    suspend fun startCamera() {
        detector = ImageLabeling.getClient(ImageLabelerOptions.DEFAULT_OPTIONS)

        val cameraProvider = ProcessCameraProvider.getInstance(context).await()
        val preview = Preview.Builder().build()
            .also { it.setSurfaceProvider(previewView.surfaceProvider) }

        val imageAnalyzer = ImageAnalysis.Builder()
            .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
            .build()
            .also { it.setAnalyzer(cameraExecutor, this::processImage) }

        cameraProvider.bindToLifecycle(
            lifecycleOwner,
            CameraSelector.DEFAULT_BACK_CAMERA,
            preview,
            imageAnalyzer
        )
    }

    @ExperimentalGetImage
    private fun processImage(imageProxy: ImageProxy) {
        val mediaImage = imageProxy.image ?: run {
            imageProxy.close()
            return
        }

        val image = InputImage.fromMediaImage(
            mediaImage,
            imageProxy.imageInfo.rotationDegrees
        )

        detector?.process(image)
            ?.addOnSuccessListener { labels -> onLabelsDetected(labels) }
            ?.addOnCompleteListener { imageProxy.close() }
    }

    fun shutdown() {
        detector?.close()
        cameraExecutor.shutdown()
    }
}
```

✅ **Compose UI с ML Kit:**
```kotlin
@Composable
fun MLKitScannerScreen(viewModel: MLKitScannerViewModel = viewModel()) {
    val state by viewModel.state.collectAsState()
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current

    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted -> if (granted) viewModel.startCamera() }

    LaunchedEffect(Unit) {
        permissionLauncher.launch(Manifest.permission.CAMERA)
    }

    Box(modifier = Modifier.fillMaxSize()) {
        AndroidView(
            factory = { ctx ->
                PreviewView(ctx).apply {
                    viewModel.setupCamera(ctx, lifecycleOwner, this)
                }
            },
            modifier = Modifier.fillMaxSize()
        )

        // Результаты обнаружения
        state.detectedLabels.takeIf { it.isNotEmpty() }?.let { labels ->
            DetectionOverlay(labels)
        }
    }
}

@Composable
fun DetectionOverlay(labels: List<ImageLabel>) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(Color.Black.copy(alpha = 0.7f))
            .padding(16.dp)
    ) {
        labels.take(5).forEach { label ->
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(label.text, color = Color.White)
                Text("${(label.confidence * 100).toInt()}%", color = Color.Green)
            }
        }
    }
}
```

### Лучшие практики

**Выбор модели:**
- ✅ On-device для реального времени, офлайн, приватности
- ✅ Cloud для высокой точности, большего покрытия меток
- ✅ Гибридный подход с fallback на on-device

**Оптимизация производительности:**
- ✅ `STRATEGY_KEEP_ONLY_LATEST` для backpressure
- ✅ Пониженное разрешение (640x480) для реального времени
- ✅ Пропуск кадров (обрабатывайте каждый 3-й кадр)
- ✅ Всегда закрывайте `imageProxy.close()`

**Управление ресурсами:**
- ✅ Вызывайте `detector.close()` при уничтожении
- ✅ Используйте `ExecutorService` для фоновой обработки
- ✅ Останавливайте камеру при неактивности

**Безопасность:**
- ✅ Валидируйте данные штрих-кодов перед использованием
- ✅ Запрашивайте подтверждение для чувствительных действий
- ✅ Санитизируйте URLs перед открытием

❌ **Распространённые ошибки:**
- ❌ Не закрывать детекторы → утечки памяти
- ❌ Обрабатывать каждый кадр → низкая производительность
- ❌ Неправильный режим детектора (STREAM vs SINGLE_IMAGE)
- ❌ Не обрабатывать разрешения камеры → краши
- ❌ Не освобождать ImageProxy → зависание камеры

---

## Answer (EN)

ML Kit provides pre-trained models for visual recognition tasks without requiring ML expertise.

### Image Labeling

**On-Device vs Cloud:**
- **On-Device**: ~400 labels, offline, 100-300ms latency, privacy
- **Cloud**: 10,000+ labels, requires internet, 500-1500ms, better accuracy

✅ **Best Practice - On-Device labeling:**
```kotlin
class ImageLabelingManager(private val context: Context) {
    private val labeler = ImageLabeling.getClient(
        ImageLabelerOptions.Builder()
            .setConfidenceThreshold(0.7f)
            .build()
    )

    suspend fun labelImage(image: InputImage): Result<List<ImageLabel>> {
        return try {
            val labels = labeler.process(image).await()
            Result.success(labels)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    fun release() = labeler.close()
}
```

✅ **Hybrid approach (Cloud with fallback):**
```kotlin
suspend fun labelImageHybrid(
    image: InputImage,
    cloudLabeler: ImageLabeler,
    onDeviceLabeler: ImageLabeler
): LabelingResult {
    val cloudResult = runCatching {
        cloudLabeler.process(image).await()
    }

    return if (cloudResult.isSuccess) {
        LabelingResult(cloudResult.getOrThrow(), LabelSource.CLOUD)
    } else {
        LabelingResult(onDeviceLabeler.process(image).await(), LabelSource.ON_DEVICE)
    }
}
```

### Object Detection

**Modes:**
- **STREAM_MODE**: Real-time video/camera
- **SINGLE_IMAGE_MODE**: Static images

✅ **Detection with tracking:**
```kotlin
class ObjectDetectionManager {
    private val detector = ObjectDetection.getClient(
        ObjectDetectorOptions.Builder()
            .setDetectorMode(ObjectDetectorOptions.STREAM_MODE)
            .enableMultipleObjects()
            .enableClassification()
            .build()
    )

    suspend fun detectObjects(image: InputImage): List<DetectedObject> {
        return detector.process(image).await()
    }

    fun release() = detector.close()
}

data class ObjectInfo(
    val trackingId: Int?,
    val boundingBox: Rect,
    val labels: List<ObjectLabel>
)
```

✅ **Motion tracking:**
```kotlin
class ObjectTracker {
    private val tracked = mutableMapOf<Int, TrackedHistory>()

    fun updateTracking(objects: List<DetectedObject>) {
        objects.forEach { obj ->
            obj.trackingId?.let { id ->
                tracked.getOrPut(id) { TrackedHistory(id) }
                    .addPosition(
                        obj.boundingBox.centerX().toFloat(),
                        obj.boundingBox.centerY().toFloat()
                    )
            }
        }

        removeStaleObjects()
    }

    private fun removeStaleObjects() {
        val now = System.currentTimeMillis()
        tracked.entries.removeIf { (_, history) ->
            now - history.lastSeen > 5000
        }
    }
}
```

### Barcode Scanning

**Supported formats:**
- 1D: EAN-13, EAN-8, UPC, Code-128, Code-39
- 2D: QR Code, Aztec, PDF417, Data Matrix

✅ **Scanner with type handling:**
```kotlin
class BarcodeScanningManager {
    private val scanner = BarcodeScanning.getClient(
        BarcodeScannerOptions.Builder()
            .setBarcodeFormats(
                Barcode.FORMAT_QR_CODE,
                Barcode.FORMAT_EAN_13,
                Barcode.FORMAT_CODE_128
            )
            .build()
    )

    suspend fun scanBarcodes(image: InputImage): List<Barcode> {
        return scanner.process(image).await()
    }

    fun handleBarcode(barcode: Barcode, context: Context) {
        when (barcode.valueType) {
            Barcode.TYPE_URL -> openUrl(context, barcode.url?.url)
            Barcode.TYPE_WIFI -> connectToWifi(context, barcode.wifi)
            Barcode.TYPE_EMAIL -> openEmail(context, barcode.email)
            Barcode.TYPE_PHONE -> dialPhone(context, barcode.phone?.number)
            else -> copyToClipboard(context, barcode.rawValue)
        }
    }

    fun release() = scanner.close()
}
```

### Real-Time Camera Integration

✅ **CameraX + ML Kit:**
```kotlin
class MLKitCameraAnalyzer(
    private val context: Context,
    private val lifecycleOwner: LifecycleOwner,
    private val previewView: PreviewView
) {
    private var detector: ImageLabeler? = null
    private val cameraExecutor = Executors.newSingleThreadExecutor()

    suspend fun startCamera() {
        detector = ImageLabeling.getClient(ImageLabelerOptions.DEFAULT_OPTIONS)

        val cameraProvider = ProcessCameraProvider.getInstance(context).await()
        val preview = Preview.Builder().build()
            .also { it.setSurfaceProvider(previewView.surfaceProvider) }

        val imageAnalyzer = ImageAnalysis.Builder()
            .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
            .build()
            .also { it.setAnalyzer(cameraExecutor, this::processImage) }

        cameraProvider.bindToLifecycle(
            lifecycleOwner,
            CameraSelector.DEFAULT_BACK_CAMERA,
            preview,
            imageAnalyzer
        )
    }

    @ExperimentalGetImage
    private fun processImage(imageProxy: ImageProxy) {
        val mediaImage = imageProxy.image ?: run {
            imageProxy.close()
            return
        }

        val image = InputImage.fromMediaImage(
            mediaImage,
            imageProxy.imageInfo.rotationDegrees
        )

        detector?.process(image)
            ?.addOnSuccessListener { labels -> onLabelsDetected(labels) }
            ?.addOnCompleteListener { imageProxy.close() }
    }

    fun shutdown() {
        detector?.close()
        cameraExecutor.shutdown()
    }
}
```

✅ **Compose UI with ML Kit:**
```kotlin
@Composable
fun MLKitScannerScreen(viewModel: MLKitScannerViewModel = viewModel()) {
    val state by viewModel.state.collectAsState()
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current

    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted -> if (granted) viewModel.startCamera() }

    LaunchedEffect(Unit) {
        permissionLauncher.launch(Manifest.permission.CAMERA)
    }

    Box(modifier = Modifier.fillMaxSize()) {
        AndroidView(
            factory = { ctx ->
                PreviewView(ctx).apply {
                    viewModel.setupCamera(ctx, lifecycleOwner, this)
                }
            },
            modifier = Modifier.fillMaxSize()
        )

        // Detection results
        state.detectedLabels.takeIf { it.isNotEmpty() }?.let { labels ->
            DetectionOverlay(labels)
        }
    }
}

@Composable
fun DetectionOverlay(labels: List<ImageLabel>) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(Color.Black.copy(alpha = 0.7f))
            .padding(16.dp)
    ) {
        labels.take(5).forEach { label ->
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(label.text, color = Color.White)
                Text("${(label.confidence * 100).toInt()}%", color = Color.Green)
            }
        }
    }
}
```

### Best Practices

**Model selection:**
- ✅ On-device for real-time, offline, privacy
- ✅ Cloud for higher accuracy, broader label coverage
- ✅ Hybrid approach with on-device fallback

**Performance optimization:**
- ✅ `STRATEGY_KEEP_ONLY_LATEST` for backpressure
- ✅ Lower resolution (640x480) for real-time
- ✅ Skip frames (process every 3rd frame)
- ✅ Always close with `imageProxy.close()`

**Resource management:**
- ✅ Call `detector.close()` on destroy
- ✅ Use `ExecutorService` for background processing
- ✅ Stop camera when inactive

**Security:**
- ✅ Validate barcode data before use
- ✅ Request confirmation for sensitive actions
- ✅ Sanitize URLs before opening

❌ **Common pitfalls:**
- ❌ Not closing detectors → memory leaks
- ❌ Processing every frame → poor performance
- ❌ Wrong detector mode (STREAM vs SINGLE_IMAGE)
- ❌ Not handling camera permissions → crashes
- ❌ Not releasing ImageProxy → camera freeze

---

## Follow-ups

1. How do you implement custom TensorFlow Lite models with ML Kit?
2. How do you optimize ML Kit performance for low-end devices?
3. How do you handle multiple concurrent ML Kit detectors?
4. How do you implement barcode scanning with custom overlay UI?
5. How do you batch process images with ML Kit?

## References

- [ML Kit Documentation](https://developers.google.com/ml-kit)
- [CameraX Documentation](https://developer.android.com/training/camerax)
- [TensorFlow Lite Models](https://www.tensorflow.org/lite/models)

## Related Questions

### Prerequisites (Easier)
- [[q-when-can-the-system-restart-a-service--android--medium]]

### Related (Same Level)
- [[q-compose-performance-optimization--android--hard]]

### Advanced (Harder)
- Custom TensorFlow Lite integration
- Multi-model ML pipelines
- Real-time AR with ML Kit
