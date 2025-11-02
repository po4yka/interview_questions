---
id: android-166
title: "Mlkit Face Detection / Распознавание лиц ML Kit"
aliases: ["ML Kit Face Detection", "Распознавание лиц ML Kit"]
topic: android
subtopics: [camera, performance-rendering, ui-graphics]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-dagger-framework-overview--android--hard, q-until-what-point-does-viewmodel-guarantee-state-preservation--android--medium]
sources: []
created: 2025-10-15
updated: 2025-01-27
tags: [android/camera, android/performance-rendering, android/ui-graphics, difficulty/medium, face-detection, kotlin, machine-learning]
date created: Monday, October 27th 2025, 5:12:57 pm
date modified: Saturday, November 1st 2025, 5:43:34 pm
---

# Вопрос (RU)
> Объясните как реализовать распознавание и анализ лиц с помощью ML Kit. Как детектировать лица, landmarks, контуры и классифицировать выражения лица? Каковы best practices для real-time отслеживания, оптимизации производительности и приватности?

# Question (EN)
> Explain how to implement face detection and analysis using ML Kit. How do you detect faces, landmarks, contours, and classify facial expressions? What are best practices for real-time face tracking, performance optimization, and privacy considerations?

## Ответ (RU)

ML Kit Face Detection предоставляет on-device распознавание лиц с landmarks, контурами и классификацией выражений для AR-эффектов и биометрического анализа.

### Конфигурация Детектора

```kotlin
class FaceDetectionManager {
    // ✅ FAST mode для real-time (10 FPS)
    private val fastDetector = FaceDetection.getClient(
        FaceDetectorOptions.Builder()
            .setPerformanceMode(PERFORMANCE_MODE_FAST)
            .setMinFaceSize(0.15f) // минимум 15% изображения
            .enableTracking() // tracking ID для frames
            .build()
    )

    // ✅ ACCURATE mode для фото-анализа
    private val accurateDetector = FaceDetection.getClient(
        FaceDetectorOptions.Builder()
            .setPerformanceMode(PERFORMANCE_MODE_ACCURATE)
            .setLandmarkMode(LANDMARK_MODE_ALL) // 10 точек
            .setContourMode(CONTOUR_MODE_ALL) // 13 контуров
            .setClassificationMode(CLASSIFICATION_MODE_ALL)
            .build()
    )

    suspend fun detectFaces(image: InputImage): Result<List<Face>> =
        suspendCancellableCoroutine { cont ->
            fastDetector.process(image)
                .addOnSuccessListener { cont.resume(Result.success(it)) }
                .addOnFailureListener { cont.resume(Result.failure(it)) }
        }
}
```

### Анализ Лица

**Landmarks** (10 точек):
- Глаза, уши, щёки
- Основание носа
- Рот (3 точки)

**Contours** (13 групп точек):
- Face oval, eyebrows (4), eyes (2), lips (4), nose (2)

**Expressions**:
```kotlin
data class FaceExpressions(
    val smilingProbability: Float, // 0.0 to 1.0
    val leftEyeOpenProbability: Float,
    val rightEyeOpenProbability: Float
)
```

**Head Pose**:
```kotlin
data class HeadPose(
    val pitch: Float, // вверх/вниз: -90 до +90
    val yaw: Float, // влево/вправо: -90 до +90
    val roll: Float // наклон: -180 до +180
)
```

### Real-Time Tracking

```kotlin
class FaceTrackingViewModel : ViewModel() {
    private var lastProcessed = 0L
    private val interval = 100L // ✅ throttle до 10 FPS

    fun processFrame(imageProxy: ImageProxy) {
        val current = System.currentTimeMillis()

        // ❌ НЕ обрабатывать каждый frame
        if (current - lastProcessed < interval) {
            imageProxy.close()
            return
        }

        viewModelScope.launch {
            val inputImage = InputImage.fromMediaImage(
                imageProxy.image!!,
                imageProxy.imageInfo.rotationDegrees
            )

            detectFaces(inputImage).onSuccess { faces ->
                _detectedFaces.value = faces
            }
            imageProxy.close()
        }
    }
}
```

### Performance Optimization

**Image Resolution**:
```kotlin
// ✅ Reduced resolution для скорости
val analyzer = ImageAnalysis.Builder()
    .setTargetResolution(Size(480, 640))
    .setBackpressureStrategy(STRATEGY_KEEP_ONLY_LATEST)
    .build()
```

**Best Practices**:
1. Throttle до 10 FPS (100ms интервал)
2. Reduce resolution до 480x640
3. Background thread processing
4. Close detector в onCleared()
5. FAST mode для real-time, ACCURATE для фото

### Privacy Considerations

```kotlin
class PrivacyAwareFaceDetection {
    // ✅ Вся обработка on-device
    // ✅ NO network calls
    // ✅ NO cloud processing

    // ❌ НЕ хранить biometric templates без согласия
    // ❌ НЕ хранить изображения лиц
    fun saveFaceMetadata(face: Face): FaceMetadata {
        return FaceMetadata(
            trackingId = face.trackingId,
            boundingBox = face.boundingBox
            // NO image data
        )
    }
}
```

**User Consent Requirements**:
- Explicit permission для face detection
- Transparent disclosure о сборе данных
- Right to delete all data
- GDPR/CCPA compliance

### Liveness Detection

```kotlin
// Для биометрической аутентификации
enum class LivenessChallenge {
    LOOK_LEFT, LOOK_RIGHT, SMILE, BLINK
}

fun checkChallenge(challenge: LivenessChallenge, face: Face): Boolean {
    return when (challenge) {
        LOOK_LEFT -> face.headEulerAngleY < -20
        SMILE -> face.smilingProbability > 0.7f
        BLINK -> face.leftEyeOpenProbability < 0.3f
        else -> false
    }
}
```

### Ключевые Моменты

**Performance**:
- 10 FPS throttling обязателен
- Lower resolution (480x640) для real-time
- Background processing via coroutines

**Accuracy**:
- Face должно занимать 15%+ frame
- Good lighting critical
- Frontal face для best results

**Privacy**:
- On-device processing только
- NO biometric storage без consent
- User-controlled data deletion

### Common Pitfalls

1. **Processing every frame** → device перегрузка
2. **High resolution** → slow detection
3. **No privacy consent** → legal issues
4. **Storing face images** → privacy violation

## Answer (EN)

ML Kit Face Detection provides on-device face recognition with landmarks, contours, and expression classification for AR effects and biometric analysis.

### Detector Configuration

```kotlin
class FaceDetectionManager {
    // ✅ FAST mode for real-time (10 FPS)
    private val fastDetector = FaceDetection.getClient(
        FaceDetectorOptions.Builder()
            .setPerformanceMode(PERFORMANCE_MODE_FAST)
            .setMinFaceSize(0.15f) // minimum 15% of image
            .enableTracking() // tracking ID across frames
            .build()
    )

    // ✅ ACCURATE mode for photo analysis
    private val accurateDetector = FaceDetection.getClient(
        FaceDetectorOptions.Builder()
            .setPerformanceMode(PERFORMANCE_MODE_ACCURATE)
            .setLandmarkMode(LANDMARK_MODE_ALL) // 10 points
            .setContourMode(CONTOUR_MODE_ALL) // 13 contours
            .setClassificationMode(CLASSIFICATION_MODE_ALL)
            .build()
    )

    suspend fun detectFaces(image: InputImage): Result<List<Face>> =
        suspendCancellableCoroutine { cont ->
            fastDetector.process(image)
                .addOnSuccessListener { cont.resume(Result.success(it)) }
                .addOnFailureListener { cont.resume(Result.failure(it)) }
        }
}
```

### Face Analysis

**Landmarks** (10 points):
- Eyes, ears, cheeks
- Nose base
- Mouth (3 points)

**Contours** (13 groups):
- Face oval, eyebrows (4), eyes (2), lips (4), nose (2)

**Expressions**:
```kotlin
data class FaceExpressions(
    val smilingProbability: Float, // 0.0 to 1.0
    val leftEyeOpenProbability: Float,
    val rightEyeOpenProbability: Float
)
```

**Head Pose**:
```kotlin
data class HeadPose(
    val pitch: Float, // up/down: -90 to +90
    val yaw: Float, // left/right: -90 to +90
    val roll: Float // tilt: -180 to +180
)
```

### Real-Time Tracking

```kotlin
class FaceTrackingViewModel : ViewModel() {
    private var lastProcessed = 0L
    private val interval = 100L // ✅ throttle to 10 FPS

    fun processFrame(imageProxy: ImageProxy) {
        val current = System.currentTimeMillis()

        // ❌ DON'T process every frame
        if (current - lastProcessed < interval) {
            imageProxy.close()
            return
        }

        viewModelScope.launch {
            val inputImage = InputImage.fromMediaImage(
                imageProxy.image!!,
                imageProxy.imageInfo.rotationDegrees
            )

            detectFaces(inputImage).onSuccess { faces ->
                _detectedFaces.value = faces
            }
            imageProxy.close()
        }
    }
}
```

### Performance Optimization

**Image Resolution**:
```kotlin
// ✅ Reduced resolution for speed
val analyzer = ImageAnalysis.Builder()
    .setTargetResolution(Size(480, 640))
    .setBackpressureStrategy(STRATEGY_KEEP_ONLY_LATEST)
    .build()
```

**Best Practices**:
1. Throttle to 10 FPS (100ms interval)
2. Reduce resolution to 480x640
3. Background thread processing
4. Close detector in onCleared()
5. FAST mode for real-time, ACCURATE for photos

### Privacy Considerations

```kotlin
class PrivacyAwareFaceDetection {
    // ✅ All processing on-device
    // ✅ NO network calls
    // ✅ NO cloud processing

    // ❌ DON'T store biometric templates without consent
    // ❌ DON'T store face images
    fun saveFaceMetadata(face: Face): FaceMetadata {
        return FaceMetadata(
            trackingId = face.trackingId,
            boundingBox = face.boundingBox
            // NO image data
        )
    }
}
```

**User Consent Requirements**:
- Explicit permission for face detection
- Transparent disclosure about data collection
- Right to delete all data
- GDPR/CCPA compliance

### Liveness Detection

```kotlin
// For biometric authentication
enum class LivenessChallenge {
    LOOK_LEFT, LOOK_RIGHT, SMILE, BLINK
}

fun checkChallenge(challenge: LivenessChallenge, face: Face): Boolean {
    return when (challenge) {
        LOOK_LEFT -> face.headEulerAngleY < -20
        SMILE -> face.smilingProbability > 0.7f
        BLINK -> face.leftEyeOpenProbability < 0.3f
        else -> false
    }
}
```

### Key Takeaways

**Performance**:
- 10 FPS throttling mandatory
- Lower resolution (480x640) for real-time
- Background processing via coroutines

**Accuracy**:
- Face must occupy 15%+ of frame
- Good lighting critical
- Frontal face for best results

**Privacy**:
- On-device processing only
- NO biometric storage without consent
- User-controlled data deletion

### Common Pitfalls

1. **Processing every frame** → device overload
2. **High resolution** → slow detection
3. **No privacy consent** → legal issues
4. **Storing face images** → privacy violation

## Follow-ups

- How does ML Kit Face Detection perform with multiple faces in a single frame?
- What are the trade-offs between FAST and ACCURATE performance modes in production apps?
- How do you handle face detection in low-light or outdoor bright-light conditions?
- What are the memory implications of enabling all detection features (landmarks, contours, classification)?
- How do you implement privacy-compliant biometric data retention policies?

## References

- ML Kit Face Detection documentation
- CameraX integration guides
- Android privacy best practices

## Related Questions

### Prerequisites
- [[q-until-what-point-does-viewmodel-guarantee-state-preservation--android--medium]]

### Related
- ML Kit Text Recognition implementation
- CameraX integration patterns
- Privacy compliance for biometric data

### Advanced
- [[q-dagger-framework-overview--android--hard]]
- Custom ML model deployment with ML Kit
- Real-time AR effects using face tracking
