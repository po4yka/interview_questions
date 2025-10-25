---
id: 20251012-12271139
title: "Mlkit Face Detection / Распознавание лиц ML Kit"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-until-what-point-does-viewmodel-guarantee-state-preservation--android--medium, q-what-is-pendingintent--programming-languages--medium, q-dagger-framework-overview--android--hard]
created: 2025-10-15
tags: [Kotlin, MLKit, MachineLearning, FaceDetection, difficulty/medium]
---

# ML Kit Face Detection and Analysis

# Question (EN)
> 
Explain how to implement face detection and analysis using ML Kit. How do you detect faces, landmarks, contours, and classify facial expressions? What are best practices for real-time face tracking, performance optimization, and privacy considerations?

## Answer (EN)
ML Kit Face Detection provides fast, accurate face detection with detailed facial features including landmarks, contours, and facial expressions, enabling applications from basic face detection to advanced AR effects and biometric analysis.

#### ML Kit Face Detection Setup

**1. Dependencies**
```kotlin
// app/build.gradle.kts
dependencies {
    // Face detection
    implementation("com.google.mlkit:face-detection:16.1.5")

    // Camera
    implementation("androidx.camera:camera-camera2:1.3.1")
    implementation("androidx.camera:camera-lifecycle:1.3.1")
    implementation("androidx.camera:camera-view:1.3.1")

    // Graphics
    implementation("androidx.compose.ui:ui-graphics:1.5.4")
}
```

**2. Face Detector Configuration**
```kotlin
// FaceDetectionManager.kt
class FaceDetectionManager {

    // Fast detector (real-time)
    private val fastDetector = FaceDetection.getClient(
        FaceDetectorOptions.Builder()
            .setPerformanceMode(FaceDetectorOptions.PERFORMANCE_MODE_FAST)
            .setLandmarkMode(FaceDetectorOptions.LANDMARK_MODE_NONE)
            .setContourMode(FaceDetectorOptions.CONTOUR_MODE_NONE)
            .setClassificationMode(FaceDetectorOptions.CLASSIFICATION_MODE_NONE)
            .setMinFaceSize(0.15f) // Minimum 15% of image
            .enableTracking() // Track faces across frames
            .build()
    )

    // Accurate detector (photo analysis)
    private val accurateDetector = FaceDetection.getClient(
        FaceDetectorOptions.Builder()
            .setPerformanceMode(FaceDetectorOptions.PERFORMANCE_MODE_ACCURATE)
            .setLandmarkMode(FaceDetectorOptions.LANDMARK_MODE_ALL)
            .setContourMode(FaceDetectorOptions.CONTOUR_MODE_ALL)
            .setClassificationMode(FaceDetectorOptions.CLASSIFICATION_MODE_ALL)
            .setMinFaceSize(0.1f)
            .enableTracking()
            .build()
    )

    suspend fun detectFaces(
        image: InputImage,
        mode: DetectionMode = DetectionMode.FAST
    ): Result<List<Face>> = suspendCancellableCoroutine { continuation ->
        val detector = when (mode) {
            DetectionMode.FAST -> fastDetector
            DetectionMode.ACCURATE -> accurateDetector
        }

        detector.process(image)
            .addOnSuccessListener { faces ->
                continuation.resume(Result.success(faces))
            }
            .addOnFailureListener { exception ->
                continuation.resume(Result.failure(exception))
            }

        continuation.invokeOnCancellation {
            // Cleanup if needed
        }
    }

    fun close() {
        fastDetector.close()
        accurateDetector.close()
    }
}

enum class DetectionMode {
    FAST,      // Real-time camera
    ACCURATE   // Photo analysis
}
```

**3. Face Analysis**
```kotlin
// FaceAnalyzer.kt
class FaceAnalyzer {

    fun analyzeFace(face: Face): FaceAnalysis {
        return FaceAnalysis(
            trackingId = face.trackingId,
            boundingBox = face.boundingBox,
            headEulerAngleX = face.headEulerAngleX, // Pitch
            headEulerAngleY = face.headEulerAngleY, // Yaw
            headEulerAngleZ = face.headEulerAngleZ, // Roll
            landmarks = extractLandmarks(face),
            contours = extractContours(face),
            expressions = classifyExpressions(face)
        )
    }

    private fun extractLandmarks(face: Face): FaceLandmarks? {
        val leftEye = face.getLandmark(FaceLandmark.LEFT_EYE)
        val rightEye = face.getLandmark(FaceLandmark.RIGHT_EYE)
        val leftEar = face.getLandmark(FaceLandmark.LEFT_EAR)
        val rightEar = face.getLandmark(FaceLandmark.RIGHT_EAR)
        val leftCheek = face.getLandmark(FaceLandmark.LEFT_CHEEK)
        val rightCheek = face.getLandmark(FaceLandmark.RIGHT_CHEEK)
        val noseBase = face.getLandmark(FaceLandmark.NOSE_BASE)
        val mouthBottom = face.getLandmark(FaceLandmark.MOUTH_BOTTOM)
        val mouthLeft = face.getLandmark(FaceLandmark.MOUTH_LEFT)
        val mouthRight = face.getLandmark(FaceLandmark.MOUTH_RIGHT)

        if (leftEye == null || rightEye == null) {
            return null // Minimum required landmarks not found
        }

        return FaceLandmarks(
            leftEye = leftEye.position,
            rightEye = rightEye.position,
            leftEar = leftEar?.position,
            rightEar = rightEar?.position,
            leftCheek = leftCheek?.position,
            rightCheek = rightCheek?.position,
            noseBase = noseBase?.position,
            mouthBottom = mouthBottom?.position,
            mouthLeft = mouthLeft?.position,
            mouthRight = mouthRight?.position
        )
    }

    private fun extractContours(face: Face): FaceContours {
        return FaceContours(
            faceOval = face.getContour(FaceContour.FACE)?.points,
            leftEyebrowTop = face.getContour(FaceContour.LEFT_EYEBROW_TOP)?.points,
            leftEyebrowBottom = face.getContour(FaceContour.LEFT_EYEBROW_BOTTOM)?.points,
            rightEyebrowTop = face.getContour(FaceContour.RIGHT_EYEBROW_TOP)?.points,
            rightEyebrowBottom = face.getContour(FaceContour.RIGHT_EYEBROW_BOTTOM)?.points,
            leftEye = face.getContour(FaceContour.LEFT_EYE)?.points,
            rightEye = face.getContour(FaceContour.RIGHT_EYE)?.points,
            upperLipTop = face.getContour(FaceContour.UPPER_LIP_TOP)?.points,
            upperLipBottom = face.getContour(FaceContour.UPPER_LIP_BOTTOM)?.points,
            lowerLipTop = face.getContour(FaceContour.LOWER_LIP_TOP)?.points,
            lowerLipBottom = face.getContour(FaceContour.LOWER_LIP_BOTTOM)?.points,
            noseBridge = face.getContour(FaceContour.NOSE_BRIDGE)?.points,
            noseBottom = face.getContour(FaceContour.NOSE_BOTTOM)?.points
        )
    }

    private fun classifyExpressions(face: Face): FaceExpressions {
        val smilingProbability = face.smilingProbability ?: 0f
        val leftEyeOpenProbability = face.leftEyeOpenProbability ?: 0f
        val rightEyeOpenProbability = face.rightEyeOpenProbability ?: 0f

        return FaceExpressions(
            isSmiling = smilingProbability > 0.5f,
            smilingConfidence = smilingProbability,
            leftEyeOpen = leftEyeOpenProbability > 0.5f,
            leftEyeOpenConfidence = leftEyeOpenProbability,
            rightEyeOpen = rightEyeOpenProbability > 0.5f,
            rightEyeOpenConfidence = rightEyeOpenProbability,
            expression = determineExpression(
                smilingProbability,
                leftEyeOpenProbability,
                rightEyeOpenProbability
            )
        )
    }

    private fun determineExpression(
        smiling: Float,
        leftEyeOpen: Float,
        rightEyeOpen: Float
    ): Expression {
        return when {
            smiling > 0.7f -> Expression.HAPPY
            leftEyeOpen < 0.3f && rightEyeOpen < 0.3f -> Expression.EYES_CLOSED
            leftEyeOpen < 0.3f || rightEyeOpen < 0.3f -> Expression.WINKING
            smiling < 0.2f -> Expression.NEUTRAL
            else -> Expression.NEUTRAL
        }
    }
}

data class FaceAnalysis(
    val trackingId: Int?,
    val boundingBox: Rect,
    val headEulerAngleX: Float, // Pitch: up/down (-90 to +90)
    val headEulerAngleY: Float, // Yaw: left/right (-90 to +90)
    val headEulerAngleZ: Float, // Roll: tilt (-180 to +180)
    val landmarks: FaceLandmarks?,
    val contours: FaceContours,
    val expressions: FaceExpressions
)

data class FaceLandmarks(
    val leftEye: PointF,
    val rightEye: PointF,
    val leftEar: PointF?,
    val rightEar: PointF?,
    val leftCheek: PointF?,
    val rightCheek: PointF?,
    val noseBase: PointF?,
    val mouthBottom: PointF?,
    val mouthLeft: PointF?,
    val mouthRight: PointF?
)

data class FaceContours(
    val faceOval: List<PointF>?,
    val leftEyebrowTop: List<PointF>?,
    val leftEyebrowBottom: List<PointF>?,
    val rightEyebrowTop: List<PointF>?,
    val rightEyebrowBottom: List<PointF>?,
    val leftEye: List<PointF>?,
    val rightEye: List<PointF>?,
    val upperLipTop: List<PointF>?,
    val upperLipBottom: List<PointF>?,
    val lowerLipTop: List<PointF>?,
    val lowerLipBottom: List<PointF>?,
    val noseBridge: List<PointF>?,
    val noseBottom: List<PointF>?
)

data class FaceExpressions(
    val isSmiling: Boolean,
    val smilingConfidence: Float,
    val leftEyeOpen: Boolean,
    val leftEyeOpenConfidence: Float,
    val rightEyeOpen: Boolean,
    val rightEyeOpenConfidence: Float,
    val expression: Expression
)

enum class Expression {
    HAPPY, NEUTRAL, EYES_CLOSED, WINKING
}
```

**4. Real-Time Face Tracking**
```kotlin
// FaceTrackingViewModel.kt
@HiltViewModel
class FaceTrackingViewModel @Inject constructor(
    private val faceDetectionManager: FaceDetectionManager,
    private val faceAnalyzer: FaceAnalyzer
) : ViewModel() {

    private val _detectedFaces = MutableStateFlow<List<FaceAnalysis>>(emptyList())
    val detectedFaces: StateFlow<List<FaceAnalysis>> = _detectedFaces.asStateFlow()

    private val _isProcessing = MutableStateFlow(false)
    val isProcessing: StateFlow<Boolean> = _isProcessing.asStateFlow()

    private var lastProcessedTime = 0L
    private val processingInterval = 100L // Process every 100ms

    @OptIn(ExperimentalGetImage::class)
    fun processFrame(imageProxy: ImageProxy) {
        val currentTime = System.currentTimeMillis()

        if (currentTime - lastProcessedTime < processingInterval) {
            imageProxy.close()
            return
        }

        lastProcessedTime = currentTime

        viewModelScope.launch {
            _isProcessing.value = true

            try {
                val mediaImage = imageProxy.image
                if (mediaImage != null) {
                    val inputImage = InputImage.fromMediaImage(
                        mediaImage,
                        imageProxy.imageInfo.rotationDegrees
                    )

                    val result = faceDetectionManager.detectFaces(
                        image = inputImage,
                        mode = DetectionMode.FAST
                    )

                    result.onSuccess { faces ->
                        val analyses = faces.map { face ->
                            faceAnalyzer.analyzeFace(face)
                        }
                        _detectedFaces.value = analyses
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
        faceDetectionManager.close()
    }
}
```

**5. Face Overlay Drawing**
```kotlin
// FaceOverlayView.kt
@Composable
fun FaceOverlayView(
    faces: List<FaceAnalysis>,
    imageSize: Size,
    modifier: Modifier = Modifier
) {
    Canvas(modifier = modifier.fillMaxSize()) {
        val scaleX = size.width / imageSize.width
        val scaleY = size.height / imageSize.height

        faces.forEach { face ->
            // Draw bounding box
            drawFaceBoundingBox(face.boundingBox, scaleX, scaleY)

            // Draw landmarks
            face.landmarks?.let { landmarks ->
                drawLandmarks(landmarks, scaleX, scaleY)
            }

            // Draw contours
            drawContours(face.contours, scaleX, scaleY)

            // Draw expression label
            drawExpressionLabel(
                face.boundingBox,
                face.expressions,
                scaleX,
                scaleY
            )
        }
    }
}

private fun DrawScope.drawFaceBoundingBox(
    boundingBox: Rect,
    scaleX: Float,
    scaleY: Float
) {
    drawRect(
        color = Color.Green,
        topLeft = Offset(
            x = boundingBox.left * scaleX,
            y = boundingBox.top * scaleY
        ),
        size = androidx.compose.ui.geometry.Size(
            width = boundingBox.width() * scaleX,
            height = boundingBox.height() * scaleY
        ),
        style = Stroke(width = 4f)
    )
}

private fun DrawScope.drawLandmarks(
    landmarks: FaceLandmarks,
    scaleX: Float,
    scaleY: Float
) {
    val landmarkPoints = listOfNotNull(
        landmarks.leftEye,
        landmarks.rightEye,
        landmarks.leftEar,
        landmarks.rightEar,
        landmarks.leftCheek,
        landmarks.rightCheek,
        landmarks.noseBase,
        landmarks.mouthBottom,
        landmarks.mouthLeft,
        landmarks.mouthRight
    )

    landmarkPoints.forEach { point ->
        drawCircle(
            color = Color.Red,
            radius = 6f,
            center = Offset(
                x = point.x * scaleX,
                y = point.y * scaleY
            )
        )
    }
}

private fun DrawScope.drawContours(
    contours: FaceContours,
    scaleX: Float,
    scaleY: Float
) {
    val contourLists = listOfNotNull(
        contours.faceOval,
        contours.leftEyebrowTop,
        contours.leftEyebrowBottom,
        contours.rightEyebrowTop,
        contours.rightEyebrowBottom,
        contours.leftEye,
        contours.rightEye,
        contours.upperLipTop,
        contours.upperLipBottom,
        contours.lowerLipTop,
        contours.lowerLipBottom,
        contours.noseBridge,
        contours.noseBottom
    )

    contourLists.forEach { points ->
        if (points.size > 1) {
            val path = Path()
            path.moveTo(
                x = points[0].x * scaleX,
                y = points[0].y * scaleY
            )

            for (i in 1 until points.size) {
                path.lineTo(
                    x = points[i].x * scaleX,
                    y = points[i].y * scaleY
                )
            }

            drawPath(
                path = path,
                color = Color.Blue,
                style = Stroke(width = 2f)
            )
        }
    }
}

private fun DrawScope.drawExpressionLabel(
    boundingBox: Rect,
    expressions: FaceExpressions,
    scaleX: Float,
    scaleY: Float
) {
    val text = when (expressions.expression) {
        Expression.HAPPY -> " Smiling"
        Expression.EYES_CLOSED -> " Eyes Closed"
        Expression.WINKING -> " Winking"
        Expression.NEUTRAL -> " Neutral"
    }

    // Draw label background
    drawRect(
        color = Color.Black.copy(alpha = 0.7f),
        topLeft = Offset(
            x = boundingBox.left * scaleX,
            y = (boundingBox.top * scaleY) - 40f
        ),
        size = androidx.compose.ui.geometry.Size(
            width = 200f,
            height = 35f
        )
    )

    // Draw text (simplified - use actual text drawing in production)
    // Use drawIntoCanvas with nativeCanvas.drawText() for actual text
}
```

**6. Advanced Face Features**
```kotlin
// FaceFeatureExtractor.kt
class FaceFeatureExtractor {

    fun calculateInterEyeDistance(landmarks: FaceLandmarks): Float {
        val leftEye = landmarks.leftEye
        val rightEye = landmarks.rightEye

        val dx = rightEye.x - leftEye.x
        val dy = rightEye.y - leftEye.y

        return sqrt(dx * dx + dy * dy)
    }

    fun estimateFaceDistance(
        landmarks: FaceLandmarks,
        knownFaceWidthCm: Float = 14f, // Average human face width
        focalLengthPixels: Float = 1000f // Camera focal length
    ): Float {
        val interEyeDistance = calculateInterEyeDistance(landmarks)

        // Distance = (Known Width × Focal Length) / Perceived Width
        return (knownFaceWidthCm * focalLengthPixels) / interEyeDistance
    }

    fun detectHeadPose(analysis: FaceAnalysis): HeadPose {
        val pitch = analysis.headEulerAngleX
        val yaw = analysis.headEulerAngleY
        val roll = analysis.headEulerAngleZ

        return HeadPose(
            pitch = pitch,
            yaw = yaw,
            roll = roll,
            direction = when {
                abs(yaw) > 30 -> if (yaw > 0) Direction.RIGHT else Direction.LEFT
                abs(pitch) > 20 -> if (pitch > 0) Direction.DOWN else Direction.UP
                else -> Direction.FORWARD
            },
            isLookingAtCamera = abs(yaw) < 15 && abs(pitch) < 15
        )
    }

    fun detectBlink(
        previousExpressions: FaceExpressions?,
        currentExpressions: FaceExpressions
    ): BlinkDetection {
        if (previousExpressions == null) {
            return BlinkDetection(false, BlinkType.NONE)
        }

        val leftEyeClosedNow = !currentExpressions.leftEyeOpen
        val rightEyeClosedNow = !currentExpressions.rightEyeOpen
        val leftEyeClosedBefore = !previousExpressions.leftEyeOpen
        val rightEyeClosedBefore = !previousExpressions.rightEyeOpen

        return when {
            leftEyeClosedNow && rightEyeClosedNow &&
                !leftEyeClosedBefore && !rightEyeClosedBefore -> {
                BlinkDetection(true, BlinkType.BOTH)
            }
            leftEyeClosedNow && !leftEyeClosedBefore -> {
                BlinkDetection(true, BlinkType.LEFT)
            }
            rightEyeClosedNow && !rightEyeClosedBefore -> {
                BlinkDetection(true, BlinkType.RIGHT)
            }
            else -> {
                BlinkDetection(false, BlinkType.NONE)
            }
        }
    }

    fun calculateFaceSymmetry(landmarks: FaceLandmarks): Float {
        // Simple symmetry check based on eye positions
        val leftEyeX = landmarks.leftEye.x
        val rightEyeX = landmarks.rightEye.x
        val centerX = (leftEyeX + rightEyeX) / 2

        val leftDistance = abs(centerX - leftEyeX)
        val rightDistance = abs(rightEyeX - centerX)

        val difference = abs(leftDistance - rightDistance)
        val average = (leftDistance + rightDistance) / 2

        return 1f - (difference / average).coerceIn(0f, 1f)
    }
}

data class HeadPose(
    val pitch: Float,
    val yaw: Float,
    val roll: Float,
    val direction: Direction,
    val isLookingAtCamera: Boolean
)

enum class Direction {
    FORWARD, UP, DOWN, LEFT, RIGHT
}

data class BlinkDetection(
    val didBlink: Boolean,
    val type: BlinkType
)

enum class BlinkType {
    NONE, LEFT, RIGHT, BOTH
}
```

**7. Face Authentication**
```kotlin
// FaceLivenessDetector.kt
class FaceLivenessDetector {
    private val challengeSequence = mutableListOf<LivenessChallenge>()
    private val completedChallenges = mutableSetOf<LivenessChallenge>()

    fun initializeLivenessCheck(): List<LivenessChallenge> {
        challengeSequence.clear()
        completedChallenges.clear()

        challengeSequence.addAll(
            listOf(
                LivenessChallenge.LOOK_LEFT,
                LivenessChallenge.LOOK_RIGHT,
                LivenessChallenge.SMILE,
                LivenessChallenge.BLINK
            ).shuffled()
        )

        return challengeSequence
    }

    fun checkChallenge(
        challenge: LivenessChallenge,
        analysis: FaceAnalysis
    ): ChallengeResult {
        val passed = when (challenge) {
            LivenessChallenge.LOOK_LEFT -> {
                analysis.headEulerAngleY < -20
            }
            LivenessChallenge.LOOK_RIGHT -> {
                analysis.headEulerAngleY > 20
            }
            LivenessChallenge.LOOK_UP -> {
                analysis.headEulerAngleX < -15
            }
            LivenessChallenge.LOOK_DOWN -> {
                analysis.headEulerAngleX > 15
            }
            LivenessChallenge.SMILE -> {
                analysis.expressions.isSmiling &&
                    analysis.expressions.smilingConfidence > 0.7f
            }
            LivenessChallenge.BLINK -> {
                !analysis.expressions.leftEyeOpen &&
                    !analysis.expressions.rightEyeOpen
            }
        }

        if (passed) {
            completedChallenges.add(challenge)
        }

        return ChallengeResult(
            challenge = challenge,
            passed = passed,
            completed = completedChallenges.size,
            total = challengeSequence.size,
            allCompleted = completedChallenges.size == challengeSequence.size
        )
    }

    fun getCurrentChallenge(): LivenessChallenge? {
        return challengeSequence.firstOrNull { it !in completedChallenges }
    }
}

enum class LivenessChallenge(val instruction: String) {
    LOOK_LEFT("Turn your head to the left"),
    LOOK_RIGHT("Turn your head to the right"),
    LOOK_UP("Look up"),
    LOOK_DOWN("Look down"),
    SMILE("Smile"),
    BLINK("Blink your eyes")
}

data class ChallengeResult(
    val challenge: LivenessChallenge,
    val passed: Boolean,
    val completed: Int,
    val total: Int,
    val allCompleted: Boolean
)
```

#### Performance Optimization

**1. Frame Processing Optimization**
```kotlin
// OptimizedFrameProcessor.kt
class OptimizedFrameProcessor(
    private val faceDetectionManager: FaceDetectionManager
) {
    private var lastProcessedFrame = 0L
    private val minFrameInterval = 100L // 10 FPS max

    private val processingScope = CoroutineScope(
        Dispatchers.Default + SupervisorJob()
    )

    @OptIn(ExperimentalGetImage::class)
    fun processFrame(
        imageProxy: ImageProxy,
        onResult: (List<Face>) -> Unit
    ) {
        val currentTime = System.currentTimeMillis()

        if (currentTime - lastProcessedFrame < minFrameInterval) {
            imageProxy.close()
            return
        }

        lastProcessedFrame = currentTime

        processingScope.launch {
            try {
                val mediaImage = imageProxy.image ?: return@launch

                val inputImage = InputImage.fromMediaImage(
                    mediaImage,
                    imageProxy.imageInfo.rotationDegrees
                )

                faceDetectionManager.detectFaces(inputImage, DetectionMode.FAST)
                    .onSuccess { faces ->
                        withContext(Dispatchers.Main) {
                            onResult(faces)
                        }
                    }
            } finally {
                imageProxy.close()
            }
        }
    }

    fun cleanup() {
        processingScope.cancel()
    }
}
```

**2. Image Resolution Optimization**
```kotlin
// Reduce image resolution for faster processing
val imageAnalyzer = ImageAnalysis.Builder()
    .setTargetResolution(Size(480, 640)) // Lower resolution for speed
    .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
    .build()
```

#### Privacy Considerations

**1. Local Processing**
```kotlin
// All face detection happens on-device
// No images sent to servers
class PrivacyAwareFaceDetection(
    private val faceDetectionManager: FaceDetectionManager
) {
    suspend fun detectFaces(image: InputImage): Result<List<Face>> {
        // Processing happens entirely on-device
        // No network calls
        // No data sent to cloud
        return faceDetectionManager.detectFaces(image, DetectionMode.FAST)
    }

    // Store only metadata, not images
    fun saveFaceMetadata(analysis: FaceAnalysis): FaceMetadata {
        return FaceMetadata(
            trackingId = analysis.trackingId,
            timestamp = Clock.System.now(),
            boundingBox = analysis.boundingBox,
            // Do NOT store actual image
            // Do NOT store biometric templates without consent
        )
    }
}

data class FaceMetadata(
    val trackingId: Int?,
    val timestamp: Instant,
    val boundingBox: Rect
    // No image data stored
)
```

**2. User Consent**
```kotlin
// FaceDetectionPermissionManager.kt
class FaceDetectionPermissionManager(private val context: Context) {

    suspend fun requestFaceDetectionPermission(): Boolean {
        // Show permission dialog explaining:
        // 1. What face data is collected
        // 2. How it's used
        // 3. Where it's stored (on-device only)
        // 4. How long it's retained
        // 5. User's right to delete

        return withContext(Dispatchers.Main) {
            // Show dialog and await user response
            true // Placeholder
        }
    }

    fun hasFaceDetectionPermission(): Boolean {
        val prefs = context.getSharedPreferences("face_detection", Context.MODE_PRIVATE)
        return prefs.getBoolean("permission_granted", false)
    }

    fun revokeFaceDetectionPermission() {
        val prefs = context.getSharedPreferences("face_detection", Context.MODE_PRIVATE)
        prefs.edit().putBoolean("permission_granted", false).apply()

        // Delete all stored face data
        deleteFaceData()
    }

    private fun deleteFaceData() {
        // Delete all face metadata
        // Clear any cached face templates
    }
}
```

#### Best Practices

1. **Performance**:
   - Use FAST mode for real-time
   - Throttle frame processing (10 FPS)
   - Reduce image resolution
   - Process on background thread
   - Close detector when done

2. **Accuracy**:
   - Good lighting conditions
   - Face occupies 15%+ of frame
   - Clear, unobstructed face
   - Frontal face for best results
   - Use ACCURATE mode for photos

3. **Privacy**:
   - Process on-device only
   - Get explicit user consent
   - Don't store biometric data without permission
   - Allow users to delete data
   - Be transparent about usage

4. **User Experience**:
   - Show clear instructions
   - Provide visual feedback
   - Handle no-face scenarios
   - Guide user positioning
   - Smooth overlay animations

5. **Face Tracking**:
   - Enable tracking for consistent IDs
   - Handle lost tracking gracefully
   - Smooth transitions between frames
   - Validate tracking consistency

#### Common Pitfalls

1. **Processing Every Frame**: Overwhelming the device
2. **High Resolution**: Slow processing
3. **No Privacy Consent**: Legal/ethical issues
4. **Storing Face Images**: Privacy violation
5. **Poor Lighting Handling**: Low accuracy
6. **No User Guidance**: Poor UX

### Summary

ML Kit Face Detection provides comprehensive face analysis:
- **Detection**: Fast, accurate face detection
- **Landmarks**: Eyes, nose, mouth, ears, cheeks
- **Contours**: Detailed face outline, eyebrows, lips
- **Classification**: Smiling, eye open/closed
- **Tracking**: Consistent face IDs across frames
- **Head Pose**: Pitch, yaw, roll angles
- **Privacy**: On-device processing

Key considerations: performance optimization, privacy compliance, user consent, appropriate use cases, and smooth user experience.

---

# Вопрос (RU)
> 
Объясните как реализовать face detection и analysis с помощью ML Kit. Как детектировать лица, landmarks, contours и классифицировать facial expressions? Каковы best practices для real-time face tracking, оптимизации производительности и privacy соображений?

## Ответ (RU)
ML Kit Face Detection обеспечивает быструю, точную детекцию лиц с детальными facial features включая landmarks, contours и facial expressions.

#### Ключевые возможности

**Detection Modes**:
- FAST: Real-time camera (10 FPS)
- ACCURATE: Photo analysis (higher quality)

**Features**:
- Bounding boxes
- Facial landmarks (10 points)
- Face contours (13 groups)
- Expressions (smiling, eyes open)
- Head pose (pitch, yaw, roll)
- Face tracking (consistent IDs)

#### Face Analysis

**Landmarks**:
- Eyes, ears, cheeks
- Nose base
- Mouth (3 points)

**Contours**:
- Face oval
- Eyebrows (4 contours)
- Eyes (2 contours)
- Lips (4 contours)
- Nose (2 contours)

**Expressions**:
- Smiling probability (0-1)
- Left eye open probability
- Right eye open probability

#### Real-Time Tracking

**Optimization**:
- Process 10 FPS (100ms interval)
- Reduce resolution (480x640)
- Background thread processing
- KEEP_ONLY_LATEST strategy

**Tracking**:
- Enable tracking для consistent IDs
- Track faces across frames
- Handle lost tracking
- Smooth transitions

#### Advanced Features

**Head Pose**:
- Pitch: up/down (-90 to +90)
- Yaw: left/right (-90 to +90)
- Roll: tilt (-180 to +180)

**Liveness Detection**:
- Look left/right/up/down
- Smile challenge
- Blink detection
- Random sequence

**Measurements**:
- Inter-eye distance
- Face distance estimation
- Face symmetry

#### Privacy

**On-Device**:
- Вся обработка локально
- Нет отправки на сервер
- Нет cloud processing

**Best Practices**:
- Explicit user consent
- Don't store biometric data
- Allow data deletion
- Transparent usage
- GDPR/CCPA compliance

#### Оптимизация

**Performance**:
- Throttle processing (10 FPS)
- Lower resolution
- Background threads
- Close detector properly

**Accuracy**:
- Good lighting
- Face 15%+ of frame
- Frontal face
- Clear, unobstructed

### Резюме

ML Kit Face Detection обеспечивает comprehensive face analysis:
- **Detection**: Fast, accurate
- **Landmarks**: 10 facial points
- **Contours**: 13 face contours
- **Expressions**: Smiling, eyes
- **Tracking**: Consistent IDs
- **Privacy**: On-device only

Ключевые моменты: performance optimization, privacy compliance, user consent, smooth UX.

## Related Questions

- [[q-until-what-point-does-viewmodel-guarantee-state-preservation--android--medium]]
- [[q-what-is-pendingintent--android--medium]]
- [[q-dagger-framework-overview--android--hard]]
