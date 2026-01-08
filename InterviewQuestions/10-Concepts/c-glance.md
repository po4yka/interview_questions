---\
id: "20260108-110550"
title: "Jetpack Glance / Jetpack Glance"
aliases: ["Compose Widgets", "Glance App Widgets"]
summary: "Jetpack Glance brings Compose-based app widgets with the Glance composition runtime and state management"
topic: "android"
subtopics: ["compose", "glance", "widgets"]
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
tags: ["android", "compose", "concept", "glance", "widgets", "difficulty/medium"]
---\

# Summary (EN)

**Jetpack Glance** is a Compose-inspired framework for building app widgets. It provides a declarative API, state management via `GlanceStateDefinition`, and integrates with `WorkManager` for updates.

# Сводка (RU)

**Jetpack Glance** — это фреймворк Jetpack, переносящий принципы Compose в аппвиджеты. Он предлагает декларативный API, управление состоянием через `GlanceStateDefinition` и тесно интегрируется с `WorkManager` для обновлений.

## Key Components

- `GlanceAppWidget`, `GlanceComposable`
- `GlanceList`, `ActionCallback`, `RemoteViewsAdapter`
- `GlanceId`, `GlanceStateDefinition`, `PreferencesGlanceStateDefinition`
- Update scheduling с `WorkManager`/`CoroutineScope`

## Considerations

- Ограничения RemoteViews: no custom draw, ограниченный набор виджетов.
- Необходимо обрабатывать размеры (recompose на `onState`) и ограничения по частоте обновлений.
- Поддерживает Material 3 Glance Theme (Android 12+ dynamic color).

