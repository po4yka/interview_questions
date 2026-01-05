---
id: "20251110-173028"
title: "Choreographer / Choreographer"
aliases: ["Choreographer"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-kotlin"
related: [c-android-graphics-pipeline, c-android-frame-budget, c-main-thread, c-android-graphics]
created: "2025-11-10"
updated: "2025-11-10"
tags: ["auto-generated", "concept", "difficulty/medium", "programming-languages"]
---

# Summary (EN)

Choreographer (in Android/Kotlin) is a framework component that coordinates the timing of UI rendering and animations with the display's refresh rate. It posts frame callbacks that run just before a new frame is drawn, helping avoid jank and ensuring smooth, synchronized visual updates. Commonly used under the hood by higher-level UI toolkits, it is also available directly for fine-grained control over rendering loops.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Choreographer (в Android/Kotlin) — это компонент фреймворка, который координирует момент отрисовки интерфейса и анимаций с частотой обновления экрана. Он регистрирует колбэки кадра, выполняемые непосредственно перед отрисовкой нового кадра, что помогает избегать «фризов» и обеспечивает плавные, синхронизированные визуальные обновления. Обычно используется во внутренних механизмах UI-фреймворков, но также доступен напрямую для точного контроля рендеринга.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Frame synchronization: Choreographer triggers callbacks (e.g., via `postFrameCallback`) aligned with the display vsync signal, ensuring rendering happens at the optimal time for the next frame.
- Smooth animations: By running animation and layout updates in these callbacks, it reduces dropped frames and visible jank in complex UI or scrolling.
- Centralized timing: Provides a single timing source for multiple subsystems (views, animations, input), simplifying coordination of visual updates.
- Performance awareness: Misusing Choreographer (heavy work in callbacks, blocking the main thread) directly impacts FPS and user-perceived smoothness, making it an important concept for performance tuning.
- Typical usage: Used when implementing custom rendering loops, advanced animations, or integrating game/graphics engines with the Android UI thread.

## Ключевые Моменты (RU)

- Синхронизация с кадром: Choreographer вызывает колбэки (например, через `postFrameCallback`) по сигналу vsync дисплея, чтобы отрисовка происходила в оптимальный момент перед новым кадром.
- Плавные анимации: Выполнение анимаций и обновления layout в этих колбэках уменьшает количество пропущенных кадров и визуальных рывков при сложном UI или прокрутке.
- Централизованное время: Предоставляет единый источник тайминга для разных подсистем (view-иерархии, анимаций, обработки ввода), упрощая согласование визуальных обновлений.
- Влияние на производительность: Неправильное использование (тяжелые операции в колбэках, блокировка main thread) напрямую снижает FPS и качество UX, поэтому понимание Choreographer важно для оптимизации.
- Типичные сценарии: Применяется при реализации кастомных циклов рендеринга, продвинутых анимаций или интеграции графических движков с UI-потоком Android.

## References

- Android Developers: `android.view.Choreographer` class reference (developer.android.com)

