---
id: ivc-20251102-017
title: Wear OS Compose UI / Compose UI для Wear OS
aliases:
  - Wear OS Compose
  - Compose for Wearables
kind: concept
summary: Compose toolkit tailored for Wear OS including scaffolds, scaling layouts, rotary input, and Tiles
links: []
created: 2025-11-02
updated: 2025-11-02
tags:
  - android
  - concept
  - wear
  - compose
  - ui
---

# Summary (EN)

Compose for Wear OS delivers components optimized for round displays, limited space, and rotational input. Key pieces include `Scaffold`, `ScalingLazyColumn`, `SwipeToDismissBox`, `TimeText`, `Chip`, and navigation patterns integrated with Horologist libraries. Compose also supports Tiles (`TileLayout`) and complications via data sources.

# Сводка (RU)

Compose для Wear OS предоставляет компоненты, оптимизированные под круглые экраны, ограниченное пространство и вращаемый ввод. Основные элементы: `Scaffold`, `ScalingLazyColumn`, `SwipeToDismissBox`, `TimeText`, `Chip`, а также навигационные паттерны из Horologist. Compose поддерживает Tiles (`TileLayout`) и complications через источники данных.

## Key Concepts

- Scaling layouts (`ScalingLazyColumn`, `CurvedText`)
- Navigation with `SwipeDismissableNavHost`
- Haptics/rotary input (`rememberScrollableState`, `RotaryScrollAdapter`)
- Tiles API (`Timeline`, `TileService`) и Compose Tiles
- Wear Material theming, device classes (round, square)

## Considerations

- Храните state в `rememberSwipeDismissableNavController`.
- Обрабатывайте ограничения батареи (lightweight UI, avoid heavy recomposition).
- Tiles/Complications работают вне Compose runtime — используйте отдельные entrypoints.
