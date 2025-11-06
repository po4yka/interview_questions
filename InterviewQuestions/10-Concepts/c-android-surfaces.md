---
id: ivc-20251102-018
title: Android Surfaces (Tiles, Shortcuts, QS) / Поверхности Android (Tiles, Shortcuts, QS)
aliases:
  - Android Surface Integrations
  - Quick Settings Tiles
  - App Shortcuts
kind: concept
summary: System surfaces outside the main app UI including Quick Settings tiles, App Shortcuts, Bubbles, and ambient surfaces
links: []
created: 2025-11-02
updated: 2025-11-02
tags:
  - android
  - concept
  - surfaces
  - quick-settings
  - shortcuts
---

# Summary (EN)

Android offers multiple system-driven surfaces beyond activities: **Quick Settings tiles**, **App Shortcuts**, **Bubbles**, **Slices**, and **ambient experiences**. They require lightweight, reactive integrations, secured intents, and compliance with background execution limits.

# Сводка (RU)

Android предоставляет несколько системных поверхностей помимо Activity: **плитки шторки (Quick Settings)**, **ярлыки приложений**, **Bubbles**, **Slices** и **ambient-экраны**. Интеграция должна быть лёгкой, реактивной, с безопасными интентами и учётом ограничений фонового выполнения.

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
