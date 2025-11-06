---
id: android-628
title: ARCore Shared Experiences / Совместные ARCore-сцены
aliases:
  - ARCore Shared Experiences
  - Совместные ARCore-сцены
topic: android
subtopics:
  - arcore
  - xr
  - 3d
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - ru
  - en
status: draft
moc: moc-android
related:
  - c-arcore
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/arcore
  - android/xr
  - realtime-networking
  - difficulty/hard
sources:
  - url: https://developers.google.com/ar/develop/java/cloud-anchors/overview
    note: Cloud Anchors overview
  - url: https://developers.google.com/ar/develop/depth
    note: Depth API documentation
  - url: https://developers.google.com/ar/reference/java
    note: ARCore Java API reference
---

# Вопрос (RU)
> Как построить многопользовательский AR-опыт на ARCore: синхронизировать Cloud Anchors, использовать Depth API для окклюзии, совмещать Sceneform/Filament рендеринг и гарантировать стабильность трекинга?

# Question (EN)
> How do you architect a multi-user ARCore experience, synchronizing Cloud Anchors, leveraging the Depth API for occlusion, integrating Sceneform/Filament rendering, and keeping tracking stable?

---

## Ответ (RU)

### 1. Архитектура

- **Client AR pipeline**: `Session` + `Config` (Plane + Depth + Augmented Images).
- **Networking**: backend (Firebase/Cloud Functions/WebRTC) для обмена Cloud Anchor ID и состояния.
- **Rendering**: Sceneform / Filament / custom GL renderer.

### 2. Инициализация сессии

```kotlin
val session = Session(context)
val config = Config(session).apply {
    planeFindingMode = Config.PlaneFindingMode.HORIZONTAL_AND_VERTICAL
    depthMode = Config.DepthMode.AUTOMATIC
    lightEstimationMode = Config.LightEstimationMode.ENVIRONMENTAL_HDR
    cloudAnchorMode = Config.CloudAnchorMode.ENABLED
}
session.configure(config)
```

- Проверьте установку Google Play Services for AR.
- Обрабатывайте `session.resume()`/`pause()` в lifecycle.

### 3. Создание и обмен Cloud Anchor

```kotlin
val anchor = hitResult.createAnchor()
val cloudAnchor = session.hostCloudAnchor(anchor)

session.cloudAnchorStateUpdatedListener = { anchorUpdated ->
    if (anchorUpdated.cloudAnchorState == CloudAnchorState.SUCCESS) {
        backend.sendAnchorId(anchorUpdated.cloudAnchorId)
    }
}
```

- Клиенты слушают backend, вызывая `session.resolveCloudAnchor(anchorId)`.
- Управляйте временем жизни (Cloud Anchors истекают через 24 ч/365 д).

### 4. Depth API и окклюзия

```kotlin
val frame = session.update()
val depthImage = frame.acquireDepthImage16Bits()
renderer.updateDepth(depthImage)
depthImage.close()
```

- Используйте Raw Depth для собственных шейдеров окклюзии.
- На устройствах без Depth API fallback на plane-based occlusion.

### 5. Рендеринг

- Sceneform 1.20+ или Filament для PBR, HDR lighting.
- Синхронизируйте `Camera.getViewMatrix()` и `getProjectionMatrix()` для виртуальных объектов.
- Адаптируйте освещение: `LightEstimation` → spherical harmonics / main light.

### 6. Трекинг и устойчивость

- Обновляйте анкер при `TrackingState.TRACKING`; если `PAUSED`, показывайте подсказки.
- Используйте `Trackable` для визуализации плоскостей.
- Перезапускайте сессию, если `Camera.getTrackingFailureReason()` persistent (insufficient light).

### 7. Тестирование

- Тестовые устройства: разные сенсоры (Pixel, Samsung, Xiaomi).
- Темные/перегруженные сценари; тестите occlusion, latency Cloud Anchor.
- Интегрируйте instrumentation: логируйте FPS, CPU usage (AR тяжелый).

---

## Answer (EN)

- Configure ARCore session with Cloud Anchor and Depth modes, and manage lifecycle resume/pause carefully.
- Host a Cloud Anchor after a hit-test; share the resulting ID via backend so peers resolve it and place shared content.
- Pull depth images to drive occlusion shaders; fall back to plane-based occlusion when depth is unavailable.
- Render via Sceneform/Filament using ARCore camera matrices and light estimation for realistic PBR output.
- Monitor tracking state/failure reasons and prompt users; profile across devices to ensure latency targets.

---

## Follow-ups
- Как синхронизировать состояние объектов (physics/animations) между клиентами?
- Как хранить и обновлять Cloud Anchors дольше 24 часов?
- Как адаптировать pipeline под ARCore Geospatial Anchors (outdoor AR)?

## References
- [[c-arcore]]
- https://developers.google.com/ar/develop/java/cloud-anchors/overview
- https://developers.google.com/ar/develop/depth

## Related Questions

- [[c-arcore]]
