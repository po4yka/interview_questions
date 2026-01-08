---\
id: android-362
title: ML Kit Object Detection / Распознавание объектов ML Kit
aliases: [ML Kit Barcode Scanning, ML Kit Image Labeling, ML Kit Object Detection, Распознавание объектов ML Kit]
topic: android
subtopics: [camera, media]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-camerax, c-media3, q-compose-gesture-detection--android--medium, q-compose-performance-optimization--android--hard, q-mlkit-custom-models--android--hard, q-mlkit-face-detection--android--medium, q-when-can-the-system-restart-a-service--android--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [android/camera, android/media, barcode-scanning, difficulty/medium, ml-kit, object-detection]
---\
# Вопрос (RU)

> Как реализовать обнаружение объектов, распознавание изображений и сканирование штрих-кодов с помощью ML Kit? В чём разница между моделями на устройстве и облачными моделями? Как обрабатывать обнаружение в реальном времени с камеры?

# Question (EN)

> How do you implement object detection, image labeling, and barcode scanning using ML Kit? What are the differences between on-device and cloud-based models? How do you handle real-time detection with camera input?

---

## Ответ (RU)

ML Kit предоставляет предобученные модели для визуального распознавания без необходимости ML-экспертизы.

(Примечание: численные значения для количества меток и задержек являются ориентировочными и могут меняться в зависимости от версии ML Kit и устройства. Облачные API и их статус (поддерживаются/устарели/перенесены) необходимо всегда уточнять в актуальной документации Google.)

### Маркировка Изображений

**On-Device vs Cloud:**
- **On-Device**: порядка сотен стандартных меток, офлайн-работа, низкая задержка (десятки-сотни мс), лучше для приватности
- **Cloud**: значительно больше меток и выше точность, требует интернет, больше задержка (сотни-тысячи мс); часть облачных ML Kit / Cloud Vision API была изменена или устарела, поэтому перед использованием гибридного подхода обязательно проверяйте актуальные рекомендации и доступность API

✅ **Лучшая практика - On-Device маркировка:**
```kotlin
class ImageLabelingManager(private val context: Context) {
    private val labeler = ImageLabeling.getClient(
        ImageLabelerOptions.Builder()
            .setConfidenceThreshold(0.7f)
            .build()
    )

    // Требуются Kotlin Coroutines extensions для Task (kotlinx-coroutines-play-services)
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

(Примечание: пример гибридного подхода предполагает, что вы используете поддерживаемые на момент реализации облачные API.)

### Обнаружение Объектов

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

    // Требуются Kotlin Coroutines extensions для Task (kotlinx-coroutines-play-services)
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

✅ **Отслеживание движения (упрощённый пример, вспомогательные типы опущены):**
```kotlin
// TrackedHistory - ваш собственный тип: должен содержать историю позиций
// и timestamp последнего появления объекта. Это не часть ML Kit API.
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

### Сканирование Штрих-кодов

**Поддерживаемые форматы (основные):**
- 1D: EAN-13, EAN-8, UPC, Code-128, Code-39 и др.
- 2D: QR Code, Aztec, PDF417, Data Matrix

✅ **Сканер с обработкой типов (обработчики действий условные):**
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

    // Требуются Kotlin Coroutines extensions для Task (kotlinx-coroutines-play-services)
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

### Интеграция Камеры В Реальном Времени

✅ **CameraX + ML Kit (пример для on-device Image Labeling):**
```kotlin
class MLKitCameraAnalyzer(
    private val context: Context,
    private val lifecycleOwner: LifecycleOwner,
    private val previewView: PreviewView
) {
    // В этом примере используется ImageLabeler; для Object Detection или Barcode Scanning
    // создайте и передайте соответствующий detector.
    private var detector: ImageLabeler? = null
    private val cameraExecutor = Executors.newSingleThreadExecutor()

    // Требуются Kotlin Coroutines extensions для ProcessCameraProvider (androidx.concurrent:concurrent-futures-ktx)
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
            ?.addOnSuccessListener { labels ->
                // Обработчик результатов должен быть реализован вызывающей стороной
                onLabelsDetected(labels)
            }
            ?.addOnCompleteListener { imageProxy.close() }
    }

    private fun onLabelsDetected(labels: List<ImageLabel>) {
        // Placeholder: обновление состояния или UI
    }

    fun shutdown() {
        detector?.close()
        cameraExecutor.shutdown()
    }
}
```

✅ **Compose UI с ML Kit (упрощённый пример взаимодействия `ViewModel` и CameraX):**
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
                    // Предполагается, что setupCamera внутри ViewModel вызывает
                    // логику, аналогичную MLKitCameraAnalyzer / bindToLifecycle.
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

### Лучшие Практики

**Выбор модели:**
- ✅ On-device для реального времени, офлайн и приватности
- ✅ Cloud для более высокой точности и большего покрытия меток (при условии актуальной поддержки соответствующих API)
- ✅ Гибридный подход с fallback на on-device (после проверки статуса облачных сервисов)

**Оптимизация производительности:**
- ✅ `STRATEGY_KEEP_ONLY_LATEST` для backpressure
- ✅ Пониженное разрешение (например, около 640x480) для реального времени
- ✅ Пропуск кадров (например, обрабатывать каждый 3-й кадр)
- ✅ Всегда вызывать `imageProxy.close()`

**Управление ресурсами:**
- ✅ Вызывать `detector.close()` при уничтожении (реализует Closeable и освобождает внутренние ресурсы)
- ✅ Использовать `ExecutorService` для фоновой обработки
- ✅ Останавливать камеру при неактивности

**Безопасность:**
- ✅ Валидировать данные штрих-кодов перед использованием
- ✅ Запрашивать подтверждение для чувствительных действий
- ✅ Санитизировать URL перед открытием и относиться к данным из штрих-кодов как к недоверенным

❌ **Распространённые ошибки:**
- ❌ Не закрывать детекторы → утечки ресурсов и памяти
- ❌ Обрабатывать каждый кадр → низкая производительность
- ❌ Неправильно выбирать режим детектора (STREAM vs SINGLE_IMAGE)
- ❌ Не обрабатывать разрешения камеры → краши
- ❌ Не освобождать ImageProxy → зависание камеры

---

## Answer (EN)

ML Kit provides pre-trained models for visual recognition tasks without requiring ML expertise.

(Note: label counts and latency ranges below are approximate and may change with ML Kit version and device. Always verify current Google documentation for the latest status of ML Kit and any cloud-based APIs.)

### Image Labeling

**On-Device vs Cloud:**
- **On-Device**: on the order of hundreds of standard labels, works offline, low latency (tens-hundreds of ms), better for privacy
- **Cloud**: significantly more labels and often higher accuracy, requires internet, higher latency (hundreds-thousands of ms); parts of the legacy ML Kit / Cloud Vision APIs have changed or been deprecated, so verify current recommendations and API availability before adopting a hybrid architecture

✅ **Best Practice - On-Device labeling:**
```kotlin
class ImageLabelingManager(private val context: Context) {
    private val labeler = ImageLabeling.getClient(
        ImageLabelerOptions.Builder()
            .setConfidenceThreshold(0.7f)
            .build()
    )

    // Requires Kotlin Coroutines Task extensions (kotlinx-coroutines-play-services)
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

(Note: this hybrid example assumes that the cloud-based API you integrate is currently supported.)

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

    // Requires Kotlin Coroutines Task extensions (kotlinx-coroutines-play-services)
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

✅ **Motion tracking (simplified, helper types omitted):**
```kotlin
// TrackedHistory is your own type: it should track position history
// and last-seen timestamp for an object. It is not part of ML Kit API.
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

**Supported formats (common):**
- 1D: EAN-13, EAN-8, UPC, Code-128, Code-39, etc.
- 2D: QR Code, Aztec, PDF417, Data Matrix

✅ **Scanner with type handling (action handlers are placeholders):**
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

    // Requires Kotlin Coroutines Task extensions (kotlinx-coroutines-play-services)
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

✅ **CameraX + ML Kit (example for on-device Image Labeling):**
```kotlin
class MLKitCameraAnalyzer(
    private val context: Context,
    private val lifecycleOwner: LifecycleOwner,
    private val previewView: PreviewView
) {
    // This example uses an ImageLabeler; for Object Detection or Barcode Scanning
    // instantiate and use the corresponding detector instead.
    private var detector: ImageLabeler? = null
    private val cameraExecutor = Executors.newSingleThreadExecutor()

    // Requires Kotlin Coroutines ProcessCameraProvider extension (androidx.concurrent:concurrent-futures-ktx)
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
            ?.addOnSuccessListener { labels ->
                // Result handler should be implemented by the caller
                onLabelsDetected(labels)
            }
            ?.addOnCompleteListener { imageProxy.close() }
    }

    private fun onLabelsDetected(labels: List<ImageLabel>) {
        // Placeholder: update state or UI
    }

    fun shutdown() {
        detector?.close()
        cameraExecutor.shutdown()
    }
}
```

✅ **Compose UI with ML Kit (simplified example of `ViewModel` + CameraX coordination):**
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
                    // Assumes setupCamera in ViewModel wires CameraX + ML Kit,
                    // similar to MLKitCameraAnalyzer / bindToLifecycle.
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
- ✅ On-device for real-time, offline usage, and privacy
- ✅ Cloud for higher accuracy and broader label coverage (subject to current API support)
- ✅ Hybrid approach with on-device fallback (after confirming cloud service status)

**Performance optimization:**
- ✅ `STRATEGY_KEEP_ONLY_LATEST` for backpressure
- ✅ Lower resolution (e.g., around 640x480) for real-time
- ✅ Skip frames (e.g., process every 3rd frame)
- ✅ Always call `imageProxy.close()`

**Resource management:**
- ✅ `Call` `detector.close()` on destroy (it implements Closeable and releases internal resources)
- ✅ Use `ExecutorService` for background processing
- ✅ Stop camera when inactive

**Security:**
- ✅ Validate barcode data before use
- ✅ `Request` confirmation for sensitive actions
- ✅ Sanitize URLs before opening; treat all barcode-derived data as untrusted

❌ **Common pitfalls:**
- ❌ Not closing detectors → resource and memory leaks
- ❌ Processing every frame → poor performance
- ❌ Using wrong detector mode (STREAM vs SINGLE_IMAGE)
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

### Prerequisites / Concepts

- [[c-media3]]
- [[c-camerax]]

### Prerequisites (Easier)
- [[q-when-can-the-system-restart-a-service--android--medium]]

### Related (Same Level)
- [[q-compose-performance-optimization--android--hard]]

### Advanced (Harder)
- Custom TensorFlow Lite integration
- Multi-model ML pipelines
- Real-time AR with ML Kit
