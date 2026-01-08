---\
id: "20260108-110549"
title: "Android Surfaces (Tiles, Shortcuts, QS) / Поверхности Android (Tiles, Shortcuts, QS)"
aliases: ["Android Surface Integrations", "App Shortcuts", "Quick Settings Tiles"]
summary: "System surfaces outside the main app UI including Quick Settings tiles, App Shortcuts, Bubbles, and ambient surfaces"
topic: "android"
subtopics: ["quick-settings", "shortcuts", "surfaces"]
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
tags: ["android", "concept", "quick-settings", "shortcuts", "surfaces", "difficulty/medium"]
---\

# Summary (EN)

Android offers multiple system-driven surfaces beyond activities: **Quick Settings tiles**, **App Shortcuts**, **Bubbles**, **Slices**, and **ambient experiences**. They require lightweight, reactive integrations, secured intents, and compliance with background execution limits.

# Сводка (RU)

Android предоставляет несколько системных поверхностей помимо `Activity`: **плитки шторки (Quick Settings)**, **ярлыки приложений**, **Bubbles**, **Slices** и **ambient-экраны**. Интеграция должна быть лёгкой, реактивной, с безопасными интентами и учётом ограничений фонового выполнения.

## Key Components

- Quick Settings: `TileService`, `qsTile`, `onClick`, listening state
- App Shortcuts: static/dynamic/pinned (`ShortcutManager`)
- Bubbles & Notification surfaces
- Slices / Widgets interplay
- Permissions & background execution (Android 13+ restrictions)

## Considerations

- TileService требует foreground-сервиса для длительных операций.
- Shortcuts должны быть idempotent, обновляться при состоянии.
- Соблюдайте UX guidelines (less than 3s to action, descriptive labels).
