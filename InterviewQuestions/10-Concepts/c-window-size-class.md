---
id: ivc-20251102-003
title: Window Size Class / Window Size Class
aliases:
  - Window Size Class
  - Jetpack Window Manager
kind: concept
summary: Jetpack Window Manager heuristics for adaptive layouts across large screens and foldables
links: []
created: 2025-11-02
updated: 2025-11-02
tags:
  - android
  - concept
  - window-manager
  - foldable
  - adaptive-ui
date created: Sunday, November 2nd 2025, 12:10:00 pm
date modified: Sunday, November 2nd 2025, 12:10:00 pm
---

# Summary (EN)

**Window Size Class** is part of Jetpack Window Manager that categorizes an activity window into standard breakpoints (`Compact`, `Medium`, `Expanded`) for width and height. Combined with posture APIs and folding features, it enables adaptive layouts for tablets, foldables, and desktops.

**Key Elements**
- `WindowSizeClass.compute{Width|Height}SizeClass(windowMetrics)`
- `WindowLayoutInfo` for fold hinge/posture events
- `FoldingFeature` to detect hinge orientation and occlusion

# Сводка (RU)

**Window Size Class** — компонент Jetpack Window Manager, классифицирующий окно Activity по предустановленным диапазонам (`Compact`, `Medium`, `Expanded`) по ширине и высоте. В связке с API позы (`WindowLayoutInfo`, `FoldingFeature`) позволяет адаптировать интерфейс под планшеты, складные устройства и настольные оболочки.

**Ключевые элементы**
- `WindowSizeClass.compute{Width|Height}SizeClass(windowMetrics)`
- `WindowLayoutInfo` для событий о складывании/двойных экранах
- `FoldingFeature` для определения типа и состояния шарнира

## Usage Patterns

- Храните размер класса в `ViewModel`/`remember` и используйте в Compose/Views.
- Реализуйте master-detail UI на `Expanded` ширине.
- Обновляйте layout при изменении позы (`HALF_OPENED`, `FLAT`).

## Considerations

- Window Manager требует AndroidX `window` dependency и совместим с API 14+ через backport.
- Для ChromeOS используйте `ActivityEmbedding`.
- Foldables могут иметь occluding hinge — следуйте рекомендациям по safe area.

