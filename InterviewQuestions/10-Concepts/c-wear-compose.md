---
id: "20260108-110551"
title: "Wear OS Compose UI / Compose UI для Wear OS"
aliases: ["Compose for Wearables", "Wear OS Compose"]
summary: "Compose toolkit tailored for Wear OS including scaffolds, scaling layouts, rotary input, and Tiles"
topic: "android"
subtopics: ["compose", "ui", "wear"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-android"
related: []
created: "2025-11-02"
updated: "2025-11-02"
tags: ["android", "compose", "concept", "ui", "wear", "difficulty/medium"]
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
