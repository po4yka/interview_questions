---
id: "20260108-110549"
title: "Android on ChromeOS / Android на ChromeOS"
aliases: ["Android ChromeOS", "Desktop Android Patterns"]
summary: "Patterns for running Android apps on ChromeOS and desktop-class environments, including mouse/keyboard, windowing, and Play Games on PC"
topic: "android"
subtopics: ["adaptive-ui", "chromeos", "desktop"]
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
tags: ["adaptive-ui", "android", "chromeos", "concept", "desktop", "difficulty/medium"]
---

# Summary (EN)

ChromeOS runs Android apps in a windowed desktop environment. Apps must handle resizable windows, keyboard/mouse input, file pickers, and multi-instance support. Play Games on PC adds higher performance and controller input expectations.

# Сводка (RU)

ChromeOS запускает Android-приложения в оконной среде desktop. Приложения должны поддерживать изменение размеров окна, клавиатуру/мышь, файловые диалоги и многократные экземпляры. Play Games on PC добавляет требования по производительности и контроллерам.

## Key Topics

- Windowing: `android:resizeableActivity`, `WindowMetrics`, `ActivityEmbedding`
- Input: `onGenericMotionEvent`, `Keyboard`, right-click, hover
- File system: `ACTION_OPEN_DOCUMENT`, shared storage, copy/paste
- Play Games on PC: high FPS, game controllers, x86_64 builds

## Considerations

- Обрабатывайте drag-and-drop (`View.startDragAndDrop`).
- Используйте desktop-style shortcuts/menus (shortcut manager, context menus).
- Тестируйте на ChromeOS emulator + physical Chromebooks.
