---\
id: android-628
title: ARCore Shared Experiences / Совместные ARCore-сцены
aliases: [ARCore Shared Experiences, Совместные ARCore-сцены]
topic: android
subtopics: [camera, networking-http, sensors]
question_kind: android
difficulty: hard
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-arcore, q-android-tv-compose-leanback--android--hard, q-dagger-build-time-optimization--android--medium, q-data-sync-unstable-network--android--hard, q-shared-element-transitions--android--hard]
created: 2025-11-02
updated: 2025-11-10
tags: [android/camera, android/networking-http, android/sensors, difficulty/hard]
sources:
  - "https://developers.google.com/ar/develop/depth"
  - "https://developers.google.com/ar/develop/java/cloud-anchors/overview"
  - "https://developers.google.com/ar/reference/java"
---\
# Вопрос (RU)
> Как построить многопользовательский AR-опыт на ARCore: синхронизировать Cloud Anchors, использовать Depth API для окклюзии, совмещать Sceneform/Filament рендеринг и гарантировать стабильность трекинга?

# Question (EN)
> How do you architect a multi-user ARCore experience, synchronizing Cloud Anchors, leveraging the Depth API for occlusion, integrating Sceneform/Filament rendering, and keeping tracking stable?

---

## Ответ (RU)

## Краткая Версия
- ARCore-сессия с `Config` (Plane + Depth + Augmented Images, `cloudAnchorMode = ENABLED`) и корректной обработкой lifecycle.
- Backend (например, Firebase/Cloud Functions/WebRTC-сигналинг) для обмена Cloud Anchor ID и состоянием объектов.
- Рендеринг через Sceneform / Filament / кастомный GL с использованием Depth API и Light Estimation.
- Жесткие требования к трекингу, UI-обратная связь, визуализация плоскостей/feature points (`Trackable`), логирование метрик (FPS, CPU/GPU, память).

## Подробная Версия
### 1. Требования

### Requirements

- Функциональные:
  - Совместная AR-сцена для нескольких пользователей с общими объектами.
  - Синхронизация Cloud Anchors и состояний объектов через backend.
  - Корректная окклюзия виртуальных объектов реальным окружением (Depth API).
- Нефункциональные:
  - Низкая задержка синхронизации.
  - Стабильный трекинг на разных устройствах.
  - Энергоэффективность и контроль нагрузки на CPU/GPU.

### 2. Архитектура

### Architecture

- **Client AR pipeline**: `Session` + `Config` (Plane + Depth + Augmented Images) с проверкой поддержки нужных фич и корректной инициализацией (ARCore availability, разрешения на камеру).
- **Networking**: backend (Firebase/Cloud Functions/WebRTC) для обмена Cloud Anchor ID и состояния объектов.
- **Rendering**: Sceneform / Filament / custom GL renderer.

### 3. Инициализация Сессии

```kotlin
// Предполагается, что уже проверены доступность ARCore и установлены
// Google Play Services for AR, а также получено разрешение на камеру.

val session = Session(context)

val config = Config(session).apply {
    planeFindingMode = Config.PlaneFindingMode.HORIZONTAL_AND_VERTICAL
    if (session.isDepthModeSupported(Config.DepthMode.AUTOMATIC)) {
        depthMode = Config.DepthMode.AUTOMATIC
    }
    lightEstimationMode = Config.LightEstimationMode.ENVIRONMENTAL_HDR
    cloudAnchorMode = Config.CloudAnchorMode.ENABLED
}

session.configure(config)
```

- Проверьте доступность ARCore (Availability API) и установку Google Play Services for AR до создания `Session`.
- Запросите и проверьте разрешение на камеру перед запуском AR-сессии.
- Обрабатывайте `session.resume()`/`pause()` в lifecycle.
- Проверяйте поддержку Depth/Cloud Anchors/Augmented Images на устройстве и отключайте соответствующие фичи при отсутствии.

### 4. Создание И Обмен Cloud Anchor

```kotlin
val anchor = hitResult.createAnchor()
val cloudAnchor = session.hostCloudAnchor(anchor)

// Периодически проверяем состояние (например, в рендер-цикле или через отдельный колбэк-слой)
if (cloudAnchor.cloudAnchorState == CloudAnchorState.SUCCESS) {
    backend.sendAnchorId(cloudAnchor.cloudAnchorId)
}
```

- Клиенты слушают backend и вызывают `session.resolveCloudAnchor(anchorId)` для привязки к общей сцене.
- Управляйте временем жизни: у Cloud Anchors есть ограниченный срок действия (типично до 24 ч по умолчанию); для длительного хранения используйте режимы с увеличенным TTL (до ~365 д) и отражайте выбранный режим в архитектуре backend и данных.

### 5. Depth API И Окклюзия

```kotlin
val frame = session.update()

if (frame.camera.trackingState == TrackingState.TRACKING &&
    session.config.depthMode != Config.DepthMode.DISABLED) {
    try {
        val depthImage = frame.acquireDepthImage16Bits()
        renderer.updateDepth(depthImage)
        depthImage.close()
    } catch (e: NotYetAvailableException) {
        // Depth данные ещё не готовы в этом кадре
    }
}
```

- Используйте raw depth для собственных шейдеров окклюзии; всегда освобождайте ресурсы.
- Учитывайте, что глубина доступна только при включённом поддерживаемом режиме Depth (`AUTOMATIC` или `RAW_DEPTH_ONLY`).
- На устройствах без поддерживаемого Depth API используйте резервный вариант: окклюзия на основе плоскостей или простые эвристики.

### 6. Рендеринг

- Sceneform (community форк 1.20+) или Filament для PBR и HDR lighting.
- Синхронизируйте `Camera.getViewMatrix()` и `getProjectionMatrix()` для виртуальных объектов.
- Адаптируйте освещение: `LightEstimation` → spherical harmonics / main light.

### 7. Трекинг И Устойчивость

- Обновляйте анкерные объекты только при `TrackingState.TRACKING`; при `PAUSED`/ограниченном трекинге показывайте пользователю подсказки (освещение, текстура, движение устройства).
- Визуализируйте `Trackable` (плоскости, point cloud), чтобы явно показать, где можно разместить якоря.
- Анализируйте `Camera.getTrackingFailureReason()` и предлагайте корректирующие действия; пересоздавайте сессию только если состояние явно не восстанавливается.

### 8. Тестирование

- Тестовые устройства: разные сенсоры и производители (Pixel, Samsung, Xiaomi и др.).
- Темные/перегруженные/слаботекстурированные/зеркальные сцены; тестируйте окклюзию, задержку и надёжность обмена Cloud Anchors.
- Интегрируйте instrumentation/логирование: FPS, CPU/GPU usage, memory, сетевые метрики (AR сильно нагружает устройство и сеть).

---

## Answer (EN)

## Short Version
- Configure `Session`/`Config` with Plane + Depth + Augmented Images and `cloudAnchorMode = ENABLED`, handle lifecycle correctly, check ARCore availability and camera permissions, and validate feature support per device.
- Use a backend (e.g., Firebase/Cloud Functions/WebRTC signaling) to share Cloud Anchor IDs and synchronize object state.
- Render via Sceneform / Filament / custom GL with Depth-based occlusion and Light Estimation, and enforce robust tracking with clear UI feedback and performance instrumentation.

## Detailed Version
### 1. Requirements

### Requirements

- Functional:
  - Multi-user shared AR scene with common virtual objects.
  - Synchronization of Cloud Anchors and object states via backend.
  - Correct occlusion of virtual objects by real-world geometry using Depth API.
- Non-functional:
  - Low synchronization latency.
  - Stable tracking across a variety of devices.
  - Power efficiency and controlled CPU/GPU load.

### 2. Architecture

### Architecture

- **Client AR pipeline**: `Session` + `Config` (Plane + Depth + Augmented Images), validating device support for required capabilities and doing proper ARCore/permission initialization.
- **Networking**: backend (Firebase/Cloud Functions/WebRTC) used to exchange Cloud Anchor IDs and shared object state between clients.
- **Rendering**: Sceneform / Filament / custom GL renderer to draw shared virtual content consistently.

### 3. Session Initialization

```kotlin
// Assumes ARCore availability and Google Play Services for AR are verified
// and camera permission is granted before creating the Session.

val session = Session(context)

val config = Config(session).apply {
    planeFindingMode = Config.PlaneFindingMode.HORIZONTAL_AND_VERTICAL
    if (session.isDepthModeSupported(Config.DepthMode.AUTOMATIC)) {
        depthMode = Config.DepthMode.AUTOMATIC
    }
    lightEstimationMode = Config.LightEstimationMode.ENVIRONMENTAL_HDR
    cloudAnchorMode = Config.CloudAnchorMode.ENABLED
}

session.configure(config)
```

- Ensure ARCore is supported (Availability API) and Google Play Services for AR is installed before creating the `Session`.
- `Request` and confirm camera permission before starting the AR session.
- Properly handle `session.resume()` / `pause()` in the lifecycle.
- Check support for Depth, Cloud Anchors, and Augmented Images per device and disable unsupported features.

### 4. Cloud Anchor Creation and Sharing

```kotlin
val anchor = hitResult.createAnchor()
val cloudAnchor = session.hostCloudAnchor(anchor)

// Periodically check state (e.g., in render loop or via a callback layer)
if (cloudAnchor.cloudAnchorState == CloudAnchorState.SUCCESS) {
    backend.sendAnchorId(cloudAnchor.cloudAnchorId)
}
```

- Other clients subscribe to the backend and call `session.resolveCloudAnchor(anchorId)` to join the shared coordinate frame.
- Manage anchor lifetime: Cloud Anchors have limited TTL (commonly up to 24 hours by default); for long-term persistence use extended TTL/persistent modes (up to ~365 days) and reflect that choice in your backend and data model.

### 5. Depth API and Occlusion

```kotlin
val frame = session.update()

if (frame.camera.trackingState == TrackingState.TRACKING &&
    session.config.depthMode != Config.DepthMode.DISABLED) {
    try {
        val depthImage = frame.acquireDepthImage16Bits()
        renderer.updateDepth(depthImage)
        depthImage.close()
    } catch (e: NotYetAvailableException) {
        // Depth data is not yet available for this frame
    }
}
```

- Use raw depth data in custom occlusion shaders; always release images promptly.
- Depth is only available with supported depth modes (`AUTOMATIC` or `RAW_DEPTH_ONLY`).
- On devices without supported Depth API, fall back to plane-based occlusion or simpler heuristics.

### 6. Rendering

- Use Sceneform (community 1.20+) or Filament for PBR and HDR lighting.
- Feed ARCore camera `getViewMatrix()` and `getProjectionMatrix()` into your renderer for proper alignment.
- Apply Light Estimation: use spherical harmonics and main directional light to match real-world lighting.

### 7. Tracking and Stability

- Update anchors/virtual objects only while `TrackingState.TRACKING`; when tracking is `PAUSED`/limited, show clear guidance (move device, improve lighting, look at textured surfaces).
- Visualize `Trackable` data (planes, point cloud) to give precise feedback where anchors can be placed.
- Inspect `Camera.getTrackingFailureReason()` and suggest corrective actions; recreate the session only if recovery is not possible.

### 8. Testing

- Test on multiple OEMs and devices with different sensors (Pixel, Samsung, Xiaomi, etc.).
- Cover dark/texture-poor/reflective/cluttered scenes; validate occlusion quality and Cloud Anchor sync latency/reliability.
- Add instrumentation/logging: FPS, CPU/GPU usage, memory, and networking stats to ensure the multi-user experience stays responsive.

---

## Дополнительные Вопросы (RU)
- Как синхронизировать состояние объектов (physics/animations) между клиентами?
- Как хранить и обновлять Cloud Anchors дольше 24 часов (персистентные/расширенный TTL-якоря)?
- Как адаптировать pipeline под ARCore Geospatial Anchors (outdoor AR)?

## Follow-ups
- How to synchronize object state (physics/animations) between clients?
- How to store and update Cloud Anchors for more than 24 hours (persistent/extended TTL anchors)?
- How to adapt the pipeline for ARCore Geospatial Anchors (outdoor AR)?

## Ссылки (RU)
- [[c-arcore]]
- https://developers.google.com/ar/develop/java/cloud-anchors/overview
- https://developers.google.com/ar/develop/depth

## References
- [[c-arcore]]
- https://developers.google.com/ar/develop/java/cloud-anchors/overview
- https://developers.google.com/ar/develop/depth

## Связанные Вопросы (RU)
- [[c-arcore]]

## Related Questions
- [[c-arcore]]
