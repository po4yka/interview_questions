---
id: android-166
title: Mlkit Face Detection / Распознавание лиц ML Kit
aliases: [ML Kit Face Detection, Распознавание лиц ML Kit]
topic: android
subtopics:
  - camera
  - performance-rendering
  - ui-graphics
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-camerax
  - c-performance
  - q-compose-gesture-detection--android--medium
  - q-dagger-framework-overview--android--hard
  - q-mlkit-custom-models--android--hard
  - q-mlkit-object-detection--android--medium
  - q-until-what-point-does-viewmodel-guarantee-state-preservation--android--medium
sources: []
created: 2025-10-15
updated: 2025-11-11
tags: [android/camera, android/performance-rendering, android/ui-graphics, difficulty/medium, face-detection, kotlin, machine-learning]
date created: Saturday, November 1st 2025, 12:46:58 pm
date modified: Tuesday, November 25th 2025, 8:53:58 pm
---
# Вопрос (RU)
> Объясните как реализовать детекцию и анализ лиц с помощью ML Kit. Как детектировать лица, landmarks, контуры и классифицировать выражения лица? Каковы best practices для real-time отслеживания, оптимизации производительности и приватности?

# Question (EN)
> Explain how to implement face detection and analysis using ML Kit. How do you detect faces, landmarks, contours, and classify facial expressions? What are best practices for real-time face tracking, performance optimization, and privacy considerations?

## Ответ (RU)

ML Kit Face Detection предоставляет on-device детекцию и базовый анализ лиц (bounding box, landmarks, контуры, вероятности выражений) для AR-эффектов, UI-реакций и простого поведенческого анализа. Это не сервис biometric face recognition (идентификация личности) или полноценной аутентификации.

### Конфигурация Детектора

```kotlin
class FaceDetectionManager {
    // FAST mode для real-time сценариев
    private val fastDetector = FaceDetection.getClient(
        FaceDetectorOptions.Builder()
            .setPerformanceMode(FaceDetectorOptions.PERFORMANCE_MODE_FAST)
            .setMinFaceSize(0.15f) // рекомендованный минимум ~15% изображения для стабильного трекинга
            .enableTracking() // trackingId для последовательных кадров
            .build()
    )

    // ACCURATE mode для оффлайн/статичного фото-анализа
    private val accurateDetector = FaceDetection.getClient(
        FaceDetectorOptions.Builder()
            .setPerformanceMode(FaceDetectorOptions.PERFORMANCE_MODE_ACCURATE)
            .setLandmarkMode(FaceDetectorOptions.LANDMARK_MODE_ALL)
            .setContourMode(FaceDetectorOptions.CONTOUR_MODE_ALL)
            .setClassificationMode(FaceDetectorOptions.CLASSIFICATION_MODE_ALL)
            .build()
    )

    suspend fun detectFaces(image: InputImage, useAccurate: Boolean = false): Result<List<Face>> =
        suspendCancellableCoroutine { cont ->
            val detector = if (useAccurate) accurateDetector else fastDetector
            detector.process(image)
                .addOnSuccessListener { faces ->
                    if (cont.isActive) cont.resume(Result.success(faces))
                }
                .addOnFailureListener { e ->
                    if (cont.isActive) cont.resume(Result.failure(e))
                }

            cont.invokeOnCancellation {
                // Task API не предоставляет прямой cancel, но предотвращаем resume после cancel через isActive
            }
        }
}
```

### Анализ Лица

**Landmarks** (основные ключевые точки, если включён LandmarkMode):
- Глаза (left/right), уши (left/right), щёки (left/right)
- Основание носа
- Уголки рта (left/right) и центр рта (в зависимости от версии API)

**Contours** (группы точек, если включён ContourMode):
- Овал лица
- Брови: left/right (2 группы)
- Глаза: left/right (2 группы)
- Губы: upper/lower, inner/outer (несколько групп)
- Нос: bridge, bottom (несколько групп)

Точное количество групп/точек может отличаться в зависимости от версии ML Kit, важно опираться на актуальную документацию.

**Expressions / Classification** (при включённом ClassificationMode):
```kotlin
data class FaceExpressions(
    val smilingProbability: Float?, // 0.0 to 1.0, может быть null если недоступно
    val leftEyeOpenProbability: Float?,
    val rightEyeOpenProbability: Float?
)
```

**Head Pose** (Euler angles):
```kotlin
data class HeadPose(
    val pitch: Float, // вверх/вниз, headEulerAngleX
    val yaw: Float,   // влево/вправо, headEulerAngleY
    val roll: Float   // наклон, headEulerAngleZ
)
```

### Real-Time Tracking

Пример потока обработки с CameraX и троттлингом кадров. Важно корректно управлять ImageProxy и не блокировать UI.

```kotlin
class FaceTrackingViewModel(
    private val faceDetectionManager: FaceDetectionManager
) : ViewModel() {

    private var lastProcessed = 0L
    private val intervalMs = 100L // рекомендуемый троттлинг до ~10 FPS для снижения нагрузки

    private val _detectedFaces = MutableStateFlow<List<Face>>(emptyList())
    val detectedFaces: StateFlow<List<Face>> = _detectedFaces

    fun processFrame(imageProxy: ImageProxy) {
        val mediaImage = imageProxy.image
        if (mediaImage == null) {
            imageProxy.close()
            return
        }

        val current = System.currentTimeMillis()
        if (current - lastProcessed < intervalMs) {
            imageProxy.close()
            return
        }
        lastProcessed = current

        val inputImage = InputImage.fromMediaImage(
            mediaImage,
            imageProxy.imageInfo.rotationDegrees
        )

        viewModelScope.launch(Dispatchers.Default) {
            val result = faceDetectionManager.detectFaces(inputImage, useAccurate = false)
            result.onSuccess { faces ->
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
// Уменьшенное разрешение для ускорения обработки
val analyzer = ImageAnalysis.Builder()
    .setTargetResolution(Size(480, 640)) // подбирается под устройство и кейс
    .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
    .build()
```

**Best Practices**:
1. Троттлить обработку кадров (например, до ~10 FPS) или использовать STRATEGY_KEEP_ONLY_LATEST вместо обработки каждого кадра.
2. Уменьшать разрешение предварительного просмотра/анализа до разумного уровня (например, около 480x640), сохранять баланс качество/скорость.
3. Выполнять обработку на background-потоках (Dispatchers.Default/IO или собственный Executor), не блокировать main thread.
4. Переиспользовать один экземпляр детектора и освобождать ресурсы (close()) при завершении (например, в onCleared()/onDestroy()).
5. Использовать FAST для real-time, ACCURATE для одиночных кадров/фото, избегать включения всех фич (landmarks, contours, classification), если они не нужны.

### Privacy Considerations

```kotlin
class PrivacyAwareFaceDetection {
    // Вся обработка on-device (ML Kit Face Detection не требует отправки кадров в облако)
    // Избегать ненужных сетевых вызовов, связанных с сырыми изображениями лиц

    // Не хранить биометрические шаблоны или данные лица для идентификации без явного согласия
    // Не логировать и не кешировать изображения лиц, если это не обосновано и не согласовано
    fun saveFaceMetadata(face: Face): FaceMetadata {
        return FaceMetadata(
            trackingId = face.trackingId,
            boundingBox = face.boundingBox
            // Без сохранения пиксельных данных или эмбеддингов
        )
    }
}
```

**User Consent Requirements** (high-level):
- Явное информирование пользователя о том, что ведётся детекция/анализ лиц, если данные используются сверх локального визуального эффекта.
- Соблюдение требований GDPR/CCPA и местного законодательства (право на удаление, минимизация данных).
- Разделять технические разрешения Android (например, CAMERA) и юридическое согласие на обработку биометрических/чувствительных данных.

### Liveness / Simple Interaction Checks

ML Kit Face Detection можно использовать для простых UX-челленджей (моргни, поверни голову), но это не даёт криптографически надёжной liveness detection или аутентификации банковского уровня.

```kotlin
enum class LivenessChallenge {
    LOOK_LEFT, LOOK_RIGHT, SMILE, BLINK
}

fun checkChallenge(challenge: LivenessChallenge, face: Face): Boolean {
    return when (challenge) {
        LivenessChallenge.LOOK_LEFT -> face.headEulerAngleY < -20
        LivenessChallenge.LOOK_RIGHT -> face.headEulerAngleY > 20
        LivenessChallenge.SMILE -> (face.smilingProbability ?: 0f) > 0.7f
        LivenessChallenge.BLINK -> (face.leftEyeOpenProbability ?: 1f) < 0.3f ||
                                   (face.rightEyeOpenProbability ?: 1f) < 0.3f
    }
}
```

Используйте такие проверки только как UX-элемент или вспомогательный сигнал, а не как единственный фактор биометрической аутентификации.

### Ключевые Моменты

**Performance**:
- Не обрабатывать каждый кадр; использовать троттлинг или backpressure стратегии.
- Снижать разрешение входных кадров для real-time use-cases.
- Выполнять распознавание на фоновых потоках и переиспользовать детектор.

**Accuracy**:
- Рекомендуется, чтобы лицо занимало достаточно большую часть кадра (например, 10–15%+), но это конфигурируемый порог.
- Критичны хорошее освещение и фокус.
- Фронтальный ракурс даёт более стабильные результаты; сильные повороты головы снижают качество.

**Privacy**:
- По умолчанию использовать только on-device обработку.
- Не хранить и не отправлять биометрические данные без прозрачного уведомления и согласия.
- Предоставлять пользователю контроль над удалением данных.

### Common Pitfalls

1. Обработка каждого кадра без троттлинга → перегрузка CPU/GPU, лаги превью.
2. Использование высокого разрешения при включённых всех фичах → медленный детектор.
3. Отсутствие прозрачности и согласия при работе с чувствительными данными → юридические и репутационные риски.
4. Хранение сырых изображений лиц и идентифицирующих шаблонов без необходимости и политики retention.
5. Использование Face Detection как полноценного face recognition / аутентификации без дополнительных, специализированных решений.

## Answer (EN)

ML Kit Face Detection provides on-device face detection and basic face analysis (bounding boxes, landmarks, contours, expression probabilities) for AR effects, UI reactions, and lightweight behavioral analysis. It is not a biometric face recognition (identity) or production-grade authentication solution.

### Detector Configuration

```kotlin
class FaceDetectionManager {
    // FAST mode for real-time scenarios
    private val fastDetector = FaceDetection.getClient(
        FaceDetectorOptions.Builder()
            .setPerformanceMode(FaceDetectorOptions.PERFORMANCE_MODE_FAST)
            .setMinFaceSize(0.15f) // recommended ~15% of image as a tuning value for stable tracking
            .enableTracking() // trackingId across frames
            .build()
    )

    // ACCURATE mode for offline/single-photo analysis
    private val accurateDetector = FaceDetection.getClient(
        FaceDetectorOptions.Builder()
            .setPerformanceMode(FaceDetectorOptions.PERFORMANCE_MODE_ACCURATE)
            .setLandmarkMode(FaceDetectorOptions.LANDMARK_MODE_ALL)
            .setContourMode(FaceDetectorOptions.CONTOUR_MODE_ALL)
            .setClassificationMode(FaceDetectorOptions.CLASSIFICATION_MODE_ALL)
            .build()
    )

    suspend fun detectFaces(image: InputImage, useAccurate: Boolean = false): Result<List<Face>> =
        suspendCancellableCoroutine { cont ->
            val detector = if (useAccurate) accurateDetector else fastDetector
            detector.process(image)
                .addOnSuccessListener { faces ->
                    if (cont.isActive) cont.resume(Result.success(faces))
                }
                .addOnFailureListener { e ->
                    if (cont.isActive) cont.resume(Result.failure(e))
                }

            cont.invokeOnCancellation {
                // Task cannot be actively cancelled; guarded by cont.isActive above.
            }
        }
}
```

### Face Analysis

**Landmarks** (key points when LandmarkMode is enabled):
- Eyes (left/right), ears (left/right), cheeks (left/right)
- Nose base
- Mouth corners (left/right) and center (depending on API version)

**Contours** (point groups when ContourMode is enabled):
- Face oval
- Eyebrows: left/right
- Eyes: left/right
- Lips: upper/lower, inner/outer groups
- Nose: bridge and bottom groups

The exact number of groups/points may vary slightly by ML Kit version; always verify against current documentation.

**Expressions / Classification** (with ClassificationMode enabled):
```kotlin
data class FaceExpressions(
    val smilingProbability: Float?, // 0.0 to 1.0, may be null if not computed
    val leftEyeOpenProbability: Float?,
    val rightEyeOpenProbability: Float?
)
```

**Head Pose** (Euler angles):
```kotlin
data class HeadPose(
    val pitch: Float, // up/down, headEulerAngleX
    val yaw: Float,   // left/right, headEulerAngleY
    val roll: Float   // tilt, headEulerAngleZ
)
```

### Real-Time Tracking

Example of using CameraX frames with throttling. Proper ImageProxy handling and background processing are essential.

```kotlin
class FaceTrackingViewModel(
    private val faceDetectionManager: FaceDetectionManager
) : ViewModel() {

    private var lastProcessed = 0L
    private val intervalMs = 100L // suggested throttling to ~10 FPS for performance

    private val _detectedFaces = MutableStateFlow<List<Face>>(emptyList())
    val detectedFaces: StateFlow<List<Face>> = _detectedFaces

    fun processFrame(imageProxy: ImageProxy) {
        val mediaImage = imageProxy.image
        if (mediaImage == null) {
            imageProxy.close()
            return
        }

        val now = System.currentTimeMillis()
        if (now - lastProcessed < intervalMs) {
            imageProxy.close()
            return
        }
        lastProcessed = now

        val inputImage = InputImage.fromMediaImage(
            mediaImage,
            imageProxy.imageInfo.rotationDegrees
        )

        viewModelScope.launch(Dispatchers.Default) {
            val result = faceDetectionManager.detectFaces(inputImage, useAccurate = false)
            result.onSuccess { faces ->
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
// Reduced resolution for faster processing
val analyzer = ImageAnalysis.Builder()
    .setTargetResolution(Size(480, 640)) // tune per device/use case
    .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
    .build()
```

**Best Practices**:
1. Throttle processing (e.g., ~10 FPS) or rely on STRATEGY_KEEP_ONLY_LATEST instead of processing every frame.
2. Use a reasonable lower resolution (e.g., around 480x640) for analysis to balance speed and accuracy.
3. Run detection on background threads (Dispatchers.Default/IO or a custom Executor); avoid blocking the main thread.
4. Reuse a single detector instance and close it when no longer needed (e.g., in onCleared()/onDestroy()).
5. Use FAST for real-time streams and ACCURATE for single images; enable landmarks/contours/classification only when necessary.

### Privacy Considerations

```kotlin
class PrivacyAwareFaceDetection {
    // All processing on-device; ML Kit Face Detection does not require sending frames to a server.
    // Avoid unnecessary network transfer of raw face images.

    // Do not store biometric templates or identifiers without explicit informed consent.
    // Do not persist face images or detailed tracking logs unless strictly needed and compliant.
    fun saveFaceMetadata(face: Face): FaceMetadata {
        return FaceMetadata(
            trackingId = face.trackingId,
            boundingBox = face.boundingBox
            // No raw image pixels or embeddings stored here
        )
    }
}
```

**User Consent Requirements** (high-level):
- Clearly inform users when face detection/analysis is used beyond transient on-device effects.
- Comply with GDPR/CCPA and local regulations (data minimization, right to deletion, purpose limitation).
- Distinguish Android runtime permissions (e.g., CAMERA) from legal consent to process biometric/sensitive data.

### Liveness / Simple Interaction Checks

ML Kit Face Detection can support simple interaction challenges (e.g., turn head, blink, smile), but this is not robust liveness detection suitable as the sole factor for secure biometric authentication.

```kotlin
enum class LivenessChallenge {
    LOOK_LEFT, LOOK_RIGHT, SMILE, BLINK
}

fun checkChallenge(challenge: LivenessChallenge, face: Face): Boolean {
    return when (challenge) {
        LivenessChallenge.LOOK_LEFT -> face.headEulerAngleY < -20
        LivenessChallenge.LOOK_RIGHT -> face.headEulerAngleY > 20
        LivenessChallenge.SMILE -> (face.smilingProbability ?: 0f) > 0.7f
        LivenessChallenge.BLINK -> (face.leftEyeOpenProbability ?: 1f) < 0.3f ||
                                   (face.rightEyeOpenProbability ?: 1f) < 0.3f
    }
}
```

Use such checks as part of UX or as one of multiple signals, not as a standalone high-security liveness solution.

### Key Takeaways

**Performance**:
- Avoid processing every frame; use throttling and/or backpressure strategies.
- Use lower-resolution analysis frames for real-time use cases.
- Run detection off the main thread and reuse detector instances.

**Accuracy**:
- Ensure the face occupies a reasonable portion of the frame (e.g., 10–15%+), but treat this as a tunable threshold.
- Good lighting and focus are critical.
- Frontal or near-frontal faces yield better results; large angles reduce reliability.

**Privacy**:
- Prefer on-device processing only.
- Do not store or transmit biometric data without consent and clear purpose.
- Provide user controls for data deletion and follow data minimization principles.

### Common Pitfalls

1. Processing every single frame → device overload and UI lag.
2. Very high resolution with all detection features enabled → slow inference and dropped frames.
3. Lack of transparency and consent when handling potentially sensitive face data → legal/compliance issues.
4. Storing raw face images or identifiers without clear need, protection, and retention policy.
5. Misusing Face Detection as full-fledged face recognition or secure biometric auth without additional, appropriate solutions.

## Дополнительные Вопросы (RU)

- Как ML Kit Face Detection обрабатывает несколько лиц в одном кадре?
- Каковы trade-offs между режимами FAST и ACCURATE в продакшене?
- Как обрабатывать детекцию лиц в условиях низкой освещенности или яркого солнечного света?
- Каковы последствия по памяти при включении всех фич (landmarks, contours, classification)?
- Как реализовать политику хранения биометрических данных с учётом приватности?

## Follow-ups

- How does ML Kit Face Detection perform with multiple faces in a single frame?
- What are the trade-offs between FAST and ACCURATE performance modes in production apps?
- How do you handle face detection in low-light or outdoor bright-light conditions?
- What are the memory implications of enabling all detection features (landmarks, contours, classification)?
- How do you implement privacy-compliant biometric data retention policies?

## Ссылки (RU)

- ML Kit Face Detection документация
- Гайды по интеграции CameraX
- Рекомендации Android по приватности

## References

- ML Kit Face Detection documentation
- CameraX integration guides
- Android privacy best practices

## Related Questions

### Prerequisites / Concepts

- [[c-performance]]
- [[c-camerax]]

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
