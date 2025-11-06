---
id: ivc-20251102-001
title: CameraX / CameraX
aliases:
  - CameraX
  - Android CameraX
kind: concept
summary: Jetpack camera library simplifying camera development with backward compatibility and Camera2 interoperability
links: []
created: 2025-11-02
updated: 2025-11-02
tags:
  - android
  - concept
  - camera
  - camerax
  - imaging
---

# Summary (EN)

**CameraX** is a Jetpack library that wraps the low-level Camera2 API to provide consistent camera behavior across Android devices. It focuses on ease of use, lifecycle awareness, and plug-and-play use cases such as Preview, ImageCapture, ImageAnalysis, and VideoCapture. CameraX also exposes the **Camera2Interop** layer so developers can access advanced controls (exposure, focus, zoom, session configuration) without abandoning its high-level API.

**Key Capabilities**
- Lifecycle-aware bindings (`ProcessCameraProvider`, `CameraSelector`)
- Extensible use cases (Preview, ImageCapture, ImageAnalysis, VideoCapture)
- Automatic device compatibility (quirk system, vendor extensions)
- Interoperability with Camera2 for manual controls
- Support for ML pipelines via `ImageAnalysis` and `Executor` strategies

# Сводка (RU)

**CameraX** — библиотека Jetpack, упрощающая работу с камерой и обеспечивающая стабильное поведение на широком спектре устройств. Она предлагает высокоуровневые use case-объекты (Preview, ImageCapture, ImageAnalysis, VideoCapture), умеет управлять жизненным циклом и предоставляет слой **Camera2Interop** для доступа к ручным настройкам камеры без полного перехода на Camera2.

**Ключевые возможности**
- Привязка к жизненному циклу (`ProcessCameraProvider`, `CameraSelector`)
- Готовые use case (Preview, ImageCapture, ImageAnalysis, VideoCapture)
- Автоматическая адаптация к устройству (система quirks, vendor extensions)
- Доступ к Camera2-API через Interop для продвинутых контролов
- Поддержка ML-пайплайна через `ImageAnalysis` и кастомные executors

## Core Components

- `ProcessCameraProvider`: центральная точка подключения use case
- `CameraSelector`: выбор фронтальной/задней камеры, линз, уровней
- `UseCase`: декларация контракта (Preview, Capture, Analysis)
- `Preview.SurfaceProvider`: интеграция с UI (View + Compose)
- Quirk механизм и `CameraInfo` для работы с vendor-ограничениями

## Usage Considerations

- По умолчанию CameraX управляет потоками, но для ML следует задавать собственный `Executor`.
- Для нестандартных сценариев требуется `Camera2Interop.Extender`.
- При одновременной работе нескольких use case важно контролировать расходы на память/энергию.

