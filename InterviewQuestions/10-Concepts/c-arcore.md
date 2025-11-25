---
id: ivc-20251102-015
title: ARCore / ARCore
aliases: [ARCore, Google ARCore]
kind: concept
summary: Google’s augmented reality SDK for motion tracking, environmental understanding, and light estimation
links: []
created: 2025-11-02
updated: 2025-11-02
tags: [3d, android, arcore, concept, xr]
date created: Thursday, November 6th 2025, 4:39:51 pm
date modified: Tuesday, November 25th 2025, 8:54:04 pm
---

# Summary (EN)

**ARCore** is Google’s augmented reality SDK that combines motion tracking, environmental understanding, and light estimation to place digital content in the physical world. It provides session management, camera intrinsics, plane detection, hit testing, anchors, depth API, and occlusion features. ARCore integrates with rendering engines like Sceneform, Filament, or Unity, and supports persisted anchors via Cloud Anchors.

# Сводка (RU)

**ARCore** — SDK дополненной реальности от Google, объединяющий отслеживание движения, понимание окружения и оценку освещенности для размещения цифрового контента в реальном мире. ARCore предоставляет управление сессиями, параметры камеры, детекцию плоскостей, hit-test, якоря, Depth API и возможности окклюзии. Интегрируется с движками Sceneform, Filament, Unity и поддерживает постоянные якоря (Cloud Anchors).

## Core Components

- `Session`, `Config`, `Frame`, `Camera`
- Plane detection (`Plane`), point clouds, Depth API
- Anchors & Trackables, Cloud Anchors for shared experiences
- Augmented Images & Faces
- Camera intrinsics/extrinsics for rendering alignment

## Considerations

- Требует ARCore-совместимых устройств (Play Services for AR).
- Depth API и Raw Depth зависят от аппаратной поддержки.
- Нужно управлять освещением и окклюзией для реалистичных сцен.

