---
id: "20251015082237485"
title: "Mlkit Object Detection / Распознавание объектов ML Kit"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [ml-kit, object-detection, image-labeling, barcode-scanning, machine-learning, camera, difficulty/medium]
---
# ML Kit Object Detection, Image Labeling, and Barcode Scanning

# Question (EN)
> 

# Вопрос (RU)
> 

---

## Answer (EN)
# Question (EN)
How do you implement object detection, image labeling, and barcode scanning using ML Kit? What are the differences between on-device and cloud-based models? How do you handle real-time detection with camera input?

## Answer (EN)
ML Kit provides several pre-trained models for visual recognition tasks including object detection, image labeling, and barcode scanning. These capabilities enable apps to understand image content without requiring custom ML expertise.

#### 1. Image Labeling (Object Recognition)

**On-Device Image Labeling:**
```kotlin
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.label.ImageLabeling
import com.google.mlkit.vision.label.defaults.ImageLabelerOptions
import com.google.mlkit.vision.label.ImageLabel
import kotlinx.coroutines.tasks.await

class ImageLabelingManager(private val context: Context) {

    // On-device labeler with default options
    private val onDeviceLabeler = ImageLabeling.getClient(
        ImageLabelerOptions.Builder()
            .setConfidenceThreshold(0.7f) // Only labels with 70%+ confidence
            .build()
    )

    // Custom model labeler
    private val customLabeler by lazy {
        val localModel = LocalModel.Builder()
            .setAssetFilePath("custom_classifier.tflite")
            .build()

        val customOptions = CustomImageLabelerOptions.Builder(localModel)
            .setConfidenceThreshold(0.6f)
            .setMaxResultCount(10)
            .build()

        ImageLabeling.getClient(customOptions)
    }

    /**
     * Analyze image and return detected labels with confidence scores
     */
    suspend fun labelImage(
        image: InputImage,
        useCustomModel: Boolean = false
    ): Result<List<ImageLabel>> {
        return try {
            val labeler = if (useCustomModel) customLabeler else onDeviceLabeler
            val labels = labeler.process(image).await()
            Result.success(labels)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Analyze bitmap and get structured label information
     */
    suspend fun analyzeImageContent(bitmap: Bitmap): ImageAnalysisResult {
        val inputImage = InputImage.fromBitmap(bitmap, 0)
        val labels = labelImage(inputImage).getOrThrow()

        return ImageAnalysisResult(
            primaryCategory = labels.firstOrNull()?.text,
            allLabels = labels.map {
                LabelInfo(
                    text = it.text,
                    confidence = it.confidence,
                    index = it.index
                )
            },
            hasAnimals = labels.any { it.text.lowercase() in animalCategories },
            hasFood = labels.any { it.text.lowercase() in foodCategories },
            hasPeople = labels.any { it.text.lowercase() in peopleCategories },
            isOutdoor = labels.any { it.text.lowercase() in outdoorCategories }
        )
    }

    /**
     * Batch process multiple images
     */
    suspend fun batchLabelImages(
        images: List<Bitmap>,
        onProgress: (Int, Int) -> Unit = { _, _ -> }
    ): List<ImageAnalysisResult> = coroutineScope {
        images.mapIndexed { index, bitmap ->
            async {
                onProgress(index + 1, images.size)
                analyzeImageContent(bitmap)
            }
        }.awaitAll()
    }

    fun release() {
        onDeviceLabeler.close()
        if (::customLabeler.isInitialized) {
            customLabeler.close()
        }
    }

    companion object {
        private val animalCategories = setOf("animal", "dog", "cat", "bird", "fish", "pet")
        private val foodCategories = setOf("food", "fruit", "vegetable", "dish", "meal")
        private val peopleCategories = setOf("person", "people", "human", "face")
        private val outdoorCategories = setOf("outdoor", "nature", "landscape", "sky", "tree")
    }
}

data class ImageAnalysisResult(
    val primaryCategory: String?,
    val allLabels: List<LabelInfo>,
    val hasAnimals: Boolean,
    val hasFood: Boolean,
    val hasPeople: Boolean,
    val isOutdoor: Boolean
)

data class LabelInfo(
    val text: String,
    val confidence: Float,
    val index: Int
)
```

**Cloud-Based Image Labeling:**
```kotlin
import com.google.mlkit.vision.label.ImageLabeling
import com.google.mlkit.vision.label.defaults.ImageLabelerOptions
import com.google.mlkit.vision.cloud.label.CloudImageLabelerOptions

class CloudImageLabelingManager {

    // Cloud labeler with more extensive label database
    private val cloudLabeler = ImageLabeling.getClient(
        CloudImageLabelerOptions.Builder()
            .setConfidenceThreshold(0.75f)
            .build()
    )

    /**
     * Cloud-based labeling provides more labels and better accuracy
     * but requires internet connection and has API usage limits
     */
    suspend fun labelImageWithCloud(image: InputImage): Result<List<ImageLabel>> {
        return try {
            val labels = cloudLabeler.process(image).await()
            Result.success(labels)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Hybrid approach: try cloud first, fallback to on-device
     */
    suspend fun labelImageHybrid(
        image: InputImage,
        onDeviceLabeler: ImageLabeler
    ): LabelingResult {
        // Try cloud first
        val cloudResult = labelImageWithCloud(image)

        if (cloudResult.isSuccess) {
            return LabelingResult(
                labels = cloudResult.getOrThrow(),
                source = LabelSource.CLOUD
            )
        }

        // Fallback to on-device
        val onDeviceResult = onDeviceLabeler.process(image).await()
        return LabelingResult(
            labels = onDeviceResult,
            source = LabelSource.ON_DEVICE
        )
    }

    fun release() {
        cloudLabeler.close()
    }
}

data class LabelingResult(
    val labels: List<ImageLabel>,
    val source: LabelSource
)

enum class LabelSource {
    ON_DEVICE,
    CLOUD
}
```

#### 2. Object Detection and Tracking

```kotlin
import com.google.mlkit.vision.objects.ObjectDetection
import com.google.mlkit.vision.objects.defaults.ObjectDetectorOptions
import com.google.mlkit.vision.objects.DetectedObject
import com.google.mlkit.vision.objects.custom.CustomObjectDetectorOptions

class ObjectDetectionManager {

    // Object detector with tracking enabled
    private val objectDetector = ObjectDetection.getClient(
        ObjectDetectorOptions.Builder()
            .setDetectorMode(ObjectDetectorOptions.STREAM_MODE) // or SINGLE_IMAGE_MODE
            .enableMultipleObjects() // Detect multiple objects in single image
            .enableClassification() // Classify objects into categories
            .build()
    )

    // Custom model for specific object detection
    private val customObjectDetector by lazy {
        val localModel = LocalModel.Builder()
            .setAssetFilePath("object_detection_model.tflite")
            .build()

        val customOptions = CustomObjectDetectorOptions.Builder(localModel)
            .setDetectorMode(CustomObjectDetectorOptions.STREAM_MODE)
            .enableMultipleObjects()
            .enableClassification()
            .setClassificationConfidenceThreshold(0.7f)
            .setMaxPerObjectLabelCount(3)
            .build()

        ObjectDetection.getClient(customOptions)
    }

    /**
     * Detect objects in image with bounding boxes and labels
     */
    suspend fun detectObjects(
        image: InputImage,
        useCustomModel: Boolean = false
    ): Result<List<DetectedObject>> {
        return try {
            val detector = if (useCustomModel) customObjectDetector else objectDetector
            val objects = detector.process(image).await()
            Result.success(objects)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Process detected objects and extract detailed information
     */
    fun analyzeDetectedObjects(objects: List<DetectedObject>): ObjectAnalysisResult {
        val objectInfos = objects.map { obj ->
            ObjectInfo(
                trackingId = obj.trackingId,
                boundingBox = obj.boundingBox,
                labels = obj.labels.map { label ->
                    ObjectLabel(
                        text = label.text,
                        confidence = label.confidence,
                        index = label.index
                    )
                }
            )
        }

        return ObjectAnalysisResult(
            objectCount = objects.size,
            objects = objectInfos,
            hasTrackedObjects = objects.any { it.trackingId != null }
        )
    }

    /**
     * Track object movement across frames
     */
    class ObjectTracker {
        private val trackedObjects = mutableMapOf<Int, TrackedObjectHistory>()

        fun updateTracking(detectedObjects: List<DetectedObject>) {
            detectedObjects.forEach { obj ->
                obj.trackingId?.let { trackingId ->
                    val history = trackedObjects.getOrPut(trackingId) {
                        TrackedObjectHistory(trackingId)
                    }

                    history.addPosition(
                        obj.boundingBox.centerX().toFloat(),
                        obj.boundingBox.centerY().toFloat(),
                        System.currentTimeMillis()
                    )
                }
            }

            // Remove old tracking data
            val now = System.currentTimeMillis()
            trackedObjects.entries.removeIf { (_, history) ->
                now - history.lastSeen > 5000 // 5 seconds timeout
            }
        }

        fun getObjectVelocity(trackingId: Int): Pair<Float, Float>? {
            val history = trackedObjects[trackingId] ?: return null
            if (history.positions.size < 2) return null

            val recent = history.positions.takeLast(5)
            val deltaX = recent.last().x - recent.first().x
            val deltaY = recent.last().y - recent.first().y
            val deltaTime = (recent.last().timestamp - recent.first().timestamp) / 1000f

            return Pair(deltaX / deltaTime, deltaY / deltaTime)
        }

        fun getTrackedObjectsCount() = trackedObjects.size

        fun clear() = trackedObjects.clear()
    }

    fun release() {
        objectDetector.close()
        if (::customObjectDetector.isInitialized) {
            customObjectDetector.close()
        }
    }
}

data class ObjectAnalysisResult(
    val objectCount: Int,
    val objects: List<ObjectInfo>,
    val hasTrackedObjects: Boolean
)

data class ObjectInfo(
    val trackingId: Int?,
    val boundingBox: Rect,
    val labels: List<ObjectLabel>
)

data class ObjectLabel(
    val text: String,
    val confidence: Float,
    val index: Int
)

data class TrackedObjectHistory(
    val trackingId: Int
) {
    val positions = mutableListOf<Position>()
    var lastSeen: Long = System.currentTimeMillis()

    fun addPosition(x: Float, y: Float, timestamp: Long) {
        positions.add(Position(x, y, timestamp))
        lastSeen = timestamp

        // Keep only last 30 positions
        if (positions.size > 30) {
            positions.removeAt(0)
        }
    }

    data class Position(val x: Float, val y: Float, val timestamp: Long)
}
```

#### 3. Barcode Scanning

```kotlin
import com.google.mlkit.vision.barcode.BarcodeScanning
import com.google.mlkit.vision.barcode.common.Barcode
import com.google.mlkit.vision.barcode.BarcodeScannerOptions

class BarcodeScanningManager {

    // Scanner supporting multiple barcode formats
    private val barcodeScanner = BarcodeScanning.getClient(
        BarcodeScannerOptions.Builder()
            .setBarcodeFormats(
                Barcode.FORMAT_QR_CODE,
                Barcode.FORMAT_AZTEC,
                Barcode.FORMAT_EAN_13,
                Barcode.FORMAT_EAN_8,
                Barcode.FORMAT_UPC_A,
                Barcode.FORMAT_UPC_E,
                Barcode.FORMAT_CODE_128,
                Barcode.FORMAT_CODE_39,
                Barcode.FORMAT_CODE_93,
                Barcode.FORMAT_CODABAR,
                Barcode.FORMAT_ITF,
                Barcode.FORMAT_PDF417,
                Barcode.FORMAT_DATA_MATRIX
            )
            .build()
    )

    // QR code specific scanner (optimized)
    private val qrScanner = BarcodeScanning.getClient(
        BarcodeScannerOptions.Builder()
            .setBarcodeFormats(Barcode.FORMAT_QR_CODE)
            .build()
    )

    /**
     * Scan barcodes from image
     */
    suspend fun scanBarcodes(
        image: InputImage,
        qrOnly: Boolean = false
    ): Result<List<Barcode>> {
        return try {
            val scanner = if (qrOnly) qrScanner else barcodeScanner
            val barcodes = scanner.process(image).await()
            Result.success(barcodes)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Extract structured information from barcode
     */
    fun extractBarcodeInfo(barcode: Barcode): BarcodeInfo {
        return BarcodeInfo(
            rawValue = barcode.rawValue,
            displayValue = barcode.displayValue,
            format = getBarcodeFormatName(barcode.format),
            valueType = getBarcodeValueType(barcode.valueType),
            boundingBox = barcode.boundingBox,
            cornerPoints = barcode.cornerPoints?.toList(),

            // Extract type-specific data
            url = barcode.url?.url,
            email = barcode.email?.let {
                EmailInfo(it.address, it.subject, it.body)
            },
            phone = barcode.phone?.number,
            sms = barcode.sms?.let {
                SmsInfo(it.phoneNumber, it.message)
            },
            wifi = barcode.wifi?.let {
                WifiInfo(it.ssid, it.password, getWifiEncryptionType(it.encryptionType))
            },
            geoPoint = barcode.geoPoint?.let {
                GeoPointInfo(it.lat, it.lng)
            },
            calendarEvent = barcode.calendarEvent?.let {
                CalendarEventInfo(
                    summary = it.summary,
                    description = it.description,
                    location = it.location,
                    organizer = it.organizer,
                    status = it.status,
                    start = it.start?.rawValue,
                    end = it.end?.rawValue
                )
            },
            contactInfo = barcode.contactInfo?.let { contact ->
                ContactInfo(
                    name = contact.name?.let {
                        PersonName(it.first, it.last, it.middle, it.prefix, it.suffix)
                    },
                    organization = contact.organization,
                    title = contact.title,
                    phones = contact.phones?.map { it.number },
                    emails = contact.emails?.map { it.address },
                    urls = contact.urls,
                    addresses = contact.addresses?.map { addr ->
                        Address(addr.addressLines?.toList(), addr.type)
                    }
                )
            },
            driverLicense = barcode.driverLicense?.let {
                DriverLicenseInfo(
                    documentType = it.documentType,
                    firstName = it.firstName,
                    lastName = it.lastName,
                    gender = it.gender,
                    addressStreet = it.addressStreet,
                    addressCity = it.addressCity,
                    addressState = it.addressState,
                    addressZip = it.addressZip,
                    licenseNumber = it.licenseNumber,
                    issueDate = it.issueDate,
                    expiryDate = it.expiryDate,
                    birthDate = it.birthDate,
                    issuingCountry = it.issuingCountry
                )
            }
        )
    }

    /**
     * Handle barcode based on its type
     */
    suspend fun handleBarcode(barcode: Barcode, context: Context) {
        when (barcode.valueType) {
            Barcode.TYPE_URL -> {
                barcode.url?.url?.let { url ->
                    openUrl(context, url)
                }
            }
            Barcode.TYPE_WIFI -> {
                barcode.wifi?.let { wifi ->
                    connectToWifi(context, wifi.ssid ?: "", wifi.password ?: "", wifi.encryptionType)
                }
            }
            Barcode.TYPE_EMAIL -> {
                barcode.email?.let { email ->
                    openEmailClient(context, email.address ?: "", email.subject, email.body)
                }
            }
            Barcode.TYPE_PHONE -> {
                barcode.phone?.number?.let { phone ->
                    dialPhone(context, phone)
                }
            }
            Barcode.TYPE_SMS -> {
                barcode.sms?.let { sms ->
                    openSmsApp(context, sms.phoneNumber ?: "", sms.message ?: "")
                }
            }
            Barcode.TYPE_GEO -> {
                barcode.geoPoint?.let { geo ->
                    openMaps(context, geo.lat, geo.lng)
                }
            }
            Barcode.TYPE_CALENDAR_EVENT -> {
                barcode.calendarEvent?.let { event ->
                    addToCalendar(context, event)
                }
            }
            Barcode.TYPE_CONTACT_INFO -> {
                barcode.contactInfo?.let { contact ->
                    addToContacts(context, contact)
                }
            }
            else -> {
                // Generic text barcode
                copyToClipboard(context, barcode.rawValue ?: "")
            }
        }
    }

    private fun getBarcodeFormatName(format: Int): String = when (format) {
        Barcode.FORMAT_QR_CODE -> "QR Code"
        Barcode.FORMAT_AZTEC -> "Aztec"
        Barcode.FORMAT_EAN_13 -> "EAN-13"
        Barcode.FORMAT_EAN_8 -> "EAN-8"
        Barcode.FORMAT_UPC_A -> "UPC-A"
        Barcode.FORMAT_UPC_E -> "UPC-E"
        Barcode.FORMAT_CODE_128 -> "Code 128"
        Barcode.FORMAT_CODE_39 -> "Code 39"
        Barcode.FORMAT_CODE_93 -> "Code 93"
        Barcode.FORMAT_CODABAR -> "Codabar"
        Barcode.FORMAT_ITF -> "ITF"
        Barcode.FORMAT_PDF417 -> "PDF417"
        Barcode.FORMAT_DATA_MATRIX -> "Data Matrix"
        else -> "Unknown"
    }

    private fun getBarcodeValueType(type: Int): String = when (type) {
        Barcode.TYPE_URL -> "URL"
        Barcode.TYPE_WIFI -> "WiFi"
        Barcode.TYPE_EMAIL -> "Email"
        Barcode.TYPE_PHONE -> "Phone"
        Barcode.TYPE_SMS -> "SMS"
        Barcode.TYPE_GEO -> "Geographic Point"
        Barcode.TYPE_CALENDAR_EVENT -> "Calendar Event"
        Barcode.TYPE_CONTACT_INFO -> "Contact Info"
        Barcode.TYPE_DRIVER_LICENSE -> "Driver License"
        Barcode.TYPE_TEXT -> "Text"
        Barcode.TYPE_ISBN -> "ISBN"
        Barcode.TYPE_PRODUCT -> "Product"
        else -> "Unknown"
    }

    private fun getWifiEncryptionType(type: Int): String = when (type) {
        Barcode.WiFi.TYPE_OPEN -> "Open"
        Barcode.WiFi.TYPE_WPA -> "WPA"
        Barcode.WiFi.TYPE_WEP -> "WEP"
        else -> "Unknown"
    }

    private fun openUrl(context: Context, url: String) {
        val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
        context.startActivity(intent)
    }

    private fun connectToWifi(context: Context, ssid: String, password: String, encryptionType: Int) {
        // WiFi connection logic (requires permissions)
        val wifiManager = context.getSystemService(Context.WIFI_SERVICE) as WifiManager
        // Implementation depends on Android version
    }

    private fun openEmailClient(context: Context, address: String, subject: String?, body: String?) {
        val intent = Intent(Intent.ACTION_SENDTO).apply {
            data = Uri.parse("mailto:")
            putExtra(Intent.EXTRA_EMAIL, arrayOf(address))
            subject?.let { putExtra(Intent.EXTRA_SUBJECT, it) }
            body?.let { putExtra(Intent.EXTRA_TEXT, it) }
        }
        context.startActivity(intent)
    }

    private fun dialPhone(context: Context, phone: String) {
        val intent = Intent(Intent.ACTION_DIAL, Uri.parse("tel:$phone"))
        context.startActivity(intent)
    }

    private fun openSmsApp(context: Context, phone: String, message: String) {
        val intent = Intent(Intent.ACTION_SENDTO).apply {
            data = Uri.parse("smsto:$phone")
            putExtra("sms_body", message)
        }
        context.startActivity(intent)
    }

    private fun openMaps(context: Context, lat: Double, lng: Double) {
        val intent = Intent(Intent.ACTION_VIEW, Uri.parse("geo:$lat,$lng"))
        context.startActivity(intent)
    }

    private fun addToCalendar(context: Context, event: Barcode.CalendarEvent) {
        val intent = Intent(Intent.ACTION_INSERT).apply {
            data = CalendarContract.Events.CONTENT_URI
            putExtra(CalendarContract.Events.TITLE, event.summary)
            putExtra(CalendarContract.Events.DESCRIPTION, event.description)
            putExtra(CalendarContract.Events.EVENT_LOCATION, event.location)
            event.start?.rawValue?.let { putExtra(CalendarContract.EXTRA_EVENT_BEGIN_TIME, it) }
            event.end?.rawValue?.let { putExtra(CalendarContract.EXTRA_EVENT_END_TIME, it) }
        }
        context.startActivity(intent)
    }

    private fun addToContacts(context: Context, contact: Barcode.ContactInfo) {
        val intent = Intent(ContactsContract.Intents.Insert.ACTION).apply {
            type = ContactsContract.RawContacts.CONTENT_TYPE
            contact.name?.let {
                putExtra(ContactsContract.Intents.Insert.NAME, "${it.first} ${it.last}")
            }
            contact.organization?.let {
                putExtra(ContactsContract.Intents.Insert.COMPANY, it)
            }
            contact.phones?.firstOrNull()?.let {
                putExtra(ContactsContract.Intents.Insert.PHONE, it.number)
            }
            contact.emails?.firstOrNull()?.let {
                putExtra(ContactsContract.Intents.Insert.EMAIL, it.address)
            }
        }
        context.startActivity(intent)
    }

    private fun copyToClipboard(context: Context, text: String) {
        val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        val clip = ClipData.newPlainText("Barcode", text)
        clipboard.setPrimaryClip(clip)
    }

    fun release() {
        barcodeScanner.close()
        qrScanner.close()
    }
}

// Data classes for barcode information
data class BarcodeInfo(
    val rawValue: String?,
    val displayValue: String?,
    val format: String,
    val valueType: String,
    val boundingBox: Rect?,
    val cornerPoints: List<Point>?,
    val url: String? = null,
    val email: EmailInfo? = null,
    val phone: String? = null,
    val sms: SmsInfo? = null,
    val wifi: WifiInfo? = null,
    val geoPoint: GeoPointInfo? = null,
    val calendarEvent: CalendarEventInfo? = null,
    val contactInfo: ContactInfo? = null,
    val driverLicense: DriverLicenseInfo? = null
)

data class EmailInfo(val address: String?, val subject: String?, val body: String?)
data class SmsInfo(val phoneNumber: String?, val message: String?)
data class WifiInfo(val ssid: String?, val password: String?, val encryptionType: String)
data class GeoPointInfo(val lat: Double, val lng: Double)

data class CalendarEventInfo(
    val summary: String?,
    val description: String?,
    val location: String?,
    val organizer: String?,
    val status: String?,
    val start: String?,
    val end: String?
)

data class ContactInfo(
    val name: PersonName?,
    val organization: String?,
    val title: String?,
    val phones: List<String?>?,
    val emails: List<String?>?,
    val urls: List<String>?,
    val addresses: List<Address>?
)

data class PersonName(
    val first: String?,
    val last: String?,
    val middle: String?,
    val prefix: String?,
    val suffix: String?
)

data class Address(val lines: List<String>?, val type: Int)

data class DriverLicenseInfo(
    val documentType: String?,
    val firstName: String?,
    val lastName: String?,
    val gender: String?,
    val addressStreet: String?,
    val addressCity: String?,
    val addressState: String?,
    val addressZip: String?,
    val licenseNumber: String?,
    val issueDate: String?,
    val expiryDate: String?,
    val birthDate: String?,
    val issuingCountry: String?
)
```

#### 4. Real-Time Camera Integration

```kotlin
import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.lifecycle.LifecycleOwner
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

class MLKitCameraAnalyzer(
    private val context: Context,
    private val lifecycleOwner: LifecycleOwner,
    private val previewView: PreviewView
) {

    private var cameraProvider: ProcessCameraProvider? = null
    private val cameraExecutor: ExecutorService = Executors.newSingleThreadExecutor()

    private var imageLabeler: ImageLabeler? = null
    private var objectDetector: com.google.mlkit.vision.objects.ObjectDetector? = null
    private var barcodeScanner: com.google.mlkit.vision.barcode.BarcodeScanner? = null

    private var analysisMode = AnalysisMode.IMAGE_LABELING

    private var onLabelsDetected: ((List<ImageLabel>) -> Unit)? = null
    private var onObjectsDetected: ((List<DetectedObject>) -> Unit)? = null
    private var onBarcodesDetected: ((List<Barcode>) -> Unit)? = null

    /**
     * Start camera with ML Kit analysis
     */
    suspend fun startCamera(mode: AnalysisMode = AnalysisMode.IMAGE_LABELING) {
        this.analysisMode = mode

        // Initialize ML Kit processor based on mode
        when (mode) {
            AnalysisMode.IMAGE_LABELING -> {
                imageLabeler = ImageLabeling.getClient(ImageLabelerOptions.DEFAULT_OPTIONS)
            }
            AnalysisMode.OBJECT_DETECTION -> {
                objectDetector = ObjectDetection.getClient(
                    ObjectDetectorOptions.Builder()
                        .setDetectorMode(ObjectDetectorOptions.STREAM_MODE)
                        .enableMultipleObjects()
                        .enableClassification()
                        .build()
                )
            }
            AnalysisMode.BARCODE_SCANNING -> {
                barcodeScanner = BarcodeScanning.getClient()
            }
        }

        val cameraProviderFuture = ProcessCameraProvider.getInstance(context)
        cameraProvider = cameraProviderFuture.await()

        bindCameraUseCases()
    }

    private fun bindCameraUseCases() {
        val cameraProvider = cameraProvider ?: return

        // Preview use case
        val preview = Preview.Builder()
            .build()
            .also {
                it.setSurfaceProvider(previewView.surfaceProvider)
            }

        // Image analysis use case
        val imageAnalyzer = ImageAnalysis.Builder()
            .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
            .build()
            .also {
                it.setAnalyzer(cameraExecutor) { imageProxy ->
                    processImage(imageProxy)
                }
            }

        // Camera selector
        val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA

        try {
            // Unbind all use cases before rebinding
            cameraProvider.unbindAll()

            // Bind use cases to camera
            cameraProvider.bindToLifecycle(
                lifecycleOwner,
                cameraSelector,
                preview,
                imageAnalyzer
            )
        } catch (e: Exception) {
            Log.e("MLKitCamera", "Use case binding failed", e)
        }
    }

    @androidx.camera.core.ExperimentalGetImage
    private fun processImage(imageProxy: ImageProxy) {
        val mediaImage = imageProxy.image
        if (mediaImage != null) {
            val image = InputImage.fromMediaImage(
                mediaImage,
                imageProxy.imageInfo.rotationDegrees
            )

            when (analysisMode) {
                AnalysisMode.IMAGE_LABELING -> processImageLabeling(image, imageProxy)
                AnalysisMode.OBJECT_DETECTION -> processObjectDetection(image, imageProxy)
                AnalysisMode.BARCODE_SCANNING -> processBarcodeScanning(image, imageProxy)
            }
        } else {
            imageProxy.close()
        }
    }

    private fun processImageLabeling(image: InputImage, imageProxy: ImageProxy) {
        imageLabeler?.process(image)
            ?.addOnSuccessListener { labels ->
                onLabelsDetected?.invoke(labels)
            }
            ?.addOnFailureListener { e ->
                Log.e("MLKitCamera", "Image labeling failed", e)
            }
            ?.addOnCompleteListener {
                imageProxy.close()
            }
    }

    private fun processObjectDetection(image: InputImage, imageProxy: ImageProxy) {
        objectDetector?.process(image)
            ?.addOnSuccessListener { objects ->
                onObjectsDetected?.invoke(objects)
            }
            ?.addOnFailureListener { e ->
                Log.e("MLKitCamera", "Object detection failed", e)
            }
            ?.addOnCompleteListener {
                imageProxy.close()
            }
    }

    private fun processBarcodeScanning(image: InputImage, imageProxy: ImageProxy) {
        barcodeScanner?.process(image)
            ?.addOnSuccessListener { barcodes ->
                if (barcodes.isNotEmpty()) {
                    onBarcodesDetected?.invoke(barcodes)
                }
            }
            ?.addOnFailureListener { e ->
                Log.e("MLKitCamera", "Barcode scanning failed", e)
            }
            ?.addOnCompleteListener {
                imageProxy.close()
            }
    }

    fun setOnLabelsDetectedListener(listener: (List<ImageLabel>) -> Unit) {
        onLabelsDetected = listener
    }

    fun setOnObjectsDetectedListener(listener: (List<DetectedObject>) -> Unit) {
        onObjectsDetected = listener
    }

    fun setOnBarcodesDetectedListener(listener: (List<Barcode>) -> Unit) {
        onBarcodesDetected = listener
    }

    fun switchMode(mode: AnalysisMode) {
        if (mode != analysisMode) {
            releaseDetectors()
            analysisMode = mode
            bindCameraUseCases()
        }
    }

    fun shutdown() {
        releaseDetectors()
        cameraProvider?.unbindAll()
        cameraExecutor.shutdown()
    }

    private fun releaseDetectors() {
        imageLabeler?.close()
        objectDetector?.close()
        barcodeScanner?.close()
        imageLabeler = null
        objectDetector = null
        barcodeScanner = null
    }
}

enum class AnalysisMode {
    IMAGE_LABELING,
    OBJECT_DETECTION,
    BARCODE_SCANNING
}
```

#### 5. Compose UI Example

```kotlin
@Composable
fun MLKitScannerScreen(
    viewModel: MLKitScannerViewModel = viewModel()
) {
    val state by viewModel.state.collectAsState()
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current

    var hasCameraPermission by remember {
        mutableStateOf(
            ContextCompat.checkSelfPermission(
                context,
                android.Manifest.permission.CAMERA
            ) == PackageManager.PERMISSION_GRANTED
        )
    }

    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        hasCameraPermission = isGranted
    }

    LaunchedEffect(Unit) {
        if (!hasCameraPermission) {
            permissionLauncher.launch(android.Manifest.permission.CAMERA)
        }
    }

    Box(modifier = Modifier.fillMaxSize()) {
        if (hasCameraPermission) {
            AndroidView(
                factory = { ctx ->
                    PreviewView(ctx).apply {
                        viewModel.setupCamera(ctx, lifecycleOwner, this)
                    }
                },
                modifier = Modifier.fillMaxSize()
            )

            // Overlay with detection results
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(16.dp)
            ) {
                // Mode selector
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(Color.Black.copy(alpha = 0.5f), RoundedCornerShape(8.dp))
                        .padding(8.dp),
                    horizontalArrangement = Arrangement.SpaceEvenly
                ) {
                    AnalysisMode.values().forEach { mode ->
                        Button(
                            onClick = { viewModel.switchMode(mode) },
                            colors = ButtonDefaults.buttonColors(
                                containerColor = if (state.currentMode == mode)
                                    MaterialTheme.colorScheme.primary
                                else
                                    MaterialTheme.colorScheme.surfaceVariant
                            )
                        ) {
                            Text(mode.name.replace("_", " "))
                        }
                    }
                }

                Spacer(modifier = Modifier.weight(1f))

                // Results display
                when (state.currentMode) {
                    AnalysisMode.IMAGE_LABELING -> {
                        ImageLabelsDisplay(labels = state.detectedLabels)
                    }
                    AnalysisMode.OBJECT_DETECTION -> {
                        ObjectsDisplay(objects = state.detectedObjects)
                    }
                    AnalysisMode.BARCODE_SCANNING -> {
                        BarcodesDisplay(
                            barcodes = state.detectedBarcodes,
                            onBarcodeClick = { barcode ->
                                viewModel.handleBarcode(barcode, context)
                            }
                        )
                    }
                }
            }
        } else {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                Text("Camera permission is required")
                Button(
                    onClick = { permissionLauncher.launch(android.Manifest.permission.CAMERA) }
                ) {
                    Text("Grant Permission")
                }
            }
        }
    }
}

@Composable
fun ImageLabelsDisplay(labels: List<ImageLabel>) {
    if (labels.isNotEmpty()) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .background(Color.Black.copy(alpha = 0.7f), RoundedCornerShape(8.dp))
                .padding(16.dp)
        ) {
            Text(
                "Detected Labels:",
                style = MaterialTheme.typography.titleMedium,
                color = Color.White
            )
            Spacer(modifier = Modifier.height(8.dp))
            labels.take(5).forEach { label ->
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(label.text, color = Color.White)
                    Text(
                        "${(label.confidence * 100).toInt()}%",
                        color = Color.Green
                    )
                }
            }
        }
    }
}

@Composable
fun ObjectsDisplay(objects: List<DetectedObject>) {
    if (objects.isNotEmpty()) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .background(Color.Black.copy(alpha = 0.7f), RoundedCornerShape(8.dp))
                .padding(16.dp)
        ) {
            Text(
                "Detected Objects: ${objects.size}",
                style = MaterialTheme.typography.titleMedium,
                color = Color.White
            )
            Spacer(modifier = Modifier.height(8.dp))
            objects.forEach { obj ->
                Text(
                    "Object ${obj.trackingId ?: "Unknown"}: ${obj.labels.firstOrNull()?.text ?: "Unknown"}",
                    color = Color.White
                )
            }
        }
    }
}

@Composable
fun BarcodesDisplay(
    barcodes: List<Barcode>,
    onBarcodeClick: (Barcode) -> Unit
) {
    if (barcodes.isNotEmpty()) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .background(Color.Black.copy(alpha = 0.7f), RoundedCornerShape(8.dp))
                .padding(16.dp)
        ) {
            Text(
                "Detected Barcodes:",
                style = MaterialTheme.typography.titleMedium,
                color = Color.White
            )
            Spacer(modifier = Modifier.height(8.dp))
            barcodes.forEach { barcode ->
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 4.dp)
                        .clickable { onBarcodeClick(barcode) },
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.surfaceVariant
                    )
                ) {
                    Column(modifier = Modifier.padding(12.dp)) {
                        Text(
                            barcode.displayValue ?: barcode.rawValue ?: "Unknown",
                            style = MaterialTheme.typography.bodyLarge
                        )
                        Text(
                            "Format: ${barcode.format}",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
        }
    }
}
```

### Best Practices

1. **On-Device vs Cloud Models:**
   - Use on-device for real-time, privacy-sensitive, or offline scenarios
   - Use cloud for higher accuracy and broader label coverage
   - Implement hybrid approach with cloud fallback

2. **Performance Optimization:**
   - Process images at appropriate resolution (640x480 or lower for real-time)
   - Use STREAM_MODE for video/camera analysis
   - Use SINGLE_IMAGE_MODE for static images
   - Throttle frame processing (e.g., process every 3rd frame)

3. **Barcode Handling:**
   - Validate barcode data before acting on it
   - Implement appropriate actions for each barcode type
   - Request user confirmation for sensitive actions (WiFi connection, contacts)

4. **Object Tracking:**
   - Use tracking IDs for continuous object monitoring
   - Implement velocity calculation for motion detection
   - Clean up old tracking data periodically

5. **Error Handling:**
   - Handle ML Kit exceptions gracefully
   - Provide fallback for network failures (cloud models)
   - Validate extracted data before using it

### Common Pitfalls

1. **Not closing detectors** → Memory leaks
   - Always call `close()` on detectors when done

2. **Processing every camera frame** → Poor performance
   - Use backpressure strategy and throttling

3. **Using wrong detector mode** → Suboptimal performance
   - STREAM_MODE for real-time, SINGLE_IMAGE_MODE for photos

4. **Not handling permissions** → Runtime crashes
   - Check and request CAMERA permission

5. **Acting on unvalidated barcode data** → Security issues
   - Validate URLs, sanitize input data

6. **Not releasing ImageProxy** → Camera freeze
   - Always call `imageProxy.close()` after processing

### Summary

ML Kit provides powerful pre-trained models for image labeling, object detection, and barcode scanning with minimal implementation effort. On-device processing ensures privacy and offline capability, while cloud models offer higher accuracy. Real-time camera integration enables live detection scenarios for various use cases from inventory management to augmented reality.

---



## Ответ (RU)
# Вопрос (RU)
Как реализовать обнаружение объектов, распознавание изображений и сканирование штрих-кодов с помощью ML Kit? В чём разница между моделями на устройстве и облачными моделями? Как обрабатывать обнаружение в реальном времени с камеры?

## Ответ (RU)
ML Kit предоставляет несколько предобученных моделей для задач визуального распознавания, включая обнаружение объектов, маркировку изображений и сканирование штрих-кодов. Эти возможности позволяют приложениям понимать содержимое изображений без необходимости экспертизы в ML.

#### 1. Маркировка изображений (распознавание объектов)

**Маркировка на устройстве:**
- Обработка полностью на устройстве
- Работает офлайн
- Около 400+ стандартных меток
- Низкая задержка (~100-300мс)
- Приватность данных

**Облачная маркировка:**
- Требует интернет-соединения
- 10,000+ меток
- Более высокая точность
- Более высокая задержка (~500-1500мс)
- Лимиты API

#### 2. Обнаружение объектов

**Режимы обнаружения:**
- **STREAM_MODE**: Оптимизирован для видео/камеры в реальном времени
- **SINGLE_IMAGE_MODE**: Оптимизирован для статических изображений

**Возможности:**
- Обнаружение нескольких объектов
- Отслеживание объектов с постоянными ID
- Классификация объектов (5 категорий)
- Ограничивающие рамки и позиции

#### 3. Сканирование штрих-кодов

**Поддерживаемые форматы:**
- 1D: EAN-13, EAN-8, UPC-A, UPC-E, Code-128, Code-39, Code-93, Codabar, ITF
- 2D: QR Code, Aztec, PDF417, Data Matrix

**Извлечение структурированных данных:**
- URL, Email, SMS, Phone
- WiFi credentials
- Geographic coordinates
- Calendar events
- Contact information
- Driver license data

#### 4. Интеграция камеры в реальном времени

**Оптимизация производительности:**
- Используйте `STRATEGY_KEEP_ONLY_LATEST` для backpressure
- Обрабатывайте изображения с пониженным разрешением
- Пропускайте кадры (обрабатывайте каждый 3-й кадр)
- Закрывайте ImageProxy сразу после обработки

**Обработка результатов:**
- Обновляйте UI в главном потоке
- Реализуйте дебаунсинг для частых обнаружений
- Кешируйте результаты для стабильности

### Лучшие практики

1. **Выбор модели:** On-device для реального времени и приватности, cloud для точности
2. **Управление ресурсами:** Всегда закрывайте детекторы после использования
3. **Производительность:** Используйте правильный режим детектора и стратегию обработки кадров
4. **Безопасность:** Валидируйте данные штрих-кодов перед использованием
5. **UX:** Предоставляйте визуальную обратную связь о процессе обнаружения

### Распространённые ошибки

1. Не закрывать детекторы → утечки памяти
2. Обрабатывать каждый кадр камеры → низкая производительность
3. Неправильный режим детектора → субоптимальная работа
4. Не обрабатывать разрешения → краши
5. Действовать по невалидированным данным → проблемы безопасности
6. Не освобождать ImageProxy → зависание камеры

### Резюме

ML Kit предоставляет мощные предобученные модели для маркировки изображений, обнаружения объектов и сканирования штрих-кодов с минимальными усилиями по реализации. Обработка на устройстве обеспечивает приватность и офлайн-возможности, в то время как облачные модели предлагают более высокую точность. Интеграция камеры в реальном времени позволяет создавать сценарии живого обнаружения для различных случаев использования от управления инвентарём до дополненной реальности.
