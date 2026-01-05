---
id: "20251110-150456"
title: "Android Lifecycle / Android Lifecycle"
aliases: ["Android Lifecycle"]
summary: "Foundational concept for interview preparation"
topic: "android"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-android"
related: [c-activity-lifecycle, c-fragment-lifecycle, c-lifecycle, c-viewmodel, c-configuration-changes]
created: "2025-11-10"
updated: "2025-11-10"
tags: ["android", "auto-generated", "concept", "difficulty/medium"]
---

# Summary (EN)

Android Lifecycle describes the sequence of states and callbacks that Activities, Fragments, and other Android components go through from creation to destruction. It is critical for managing UI state, resources, background work, and navigation correctly, especially under configuration changes and process death. A solid understanding of the lifecycle helps prevent memory leaks, crashes, and inconsistent behavior in real-world Android apps.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Android Lifecycle описывает последовательность состояний и колбэков, через которые проходят Activity, Fragment и другие компоненты Android от создания до уничтожения. Грамотная работа с жизненным циклом важна для управления состоянием интерфейса, ресурсами, фоновыми задачами и навигацией, особенно при конфигурационных изменениях и убийстве процесса системой. Хорошее понимание жизненного цикла помогает избежать утечек памяти, падений и некорректного поведения приложения.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Component states: Activities and Fragments pass through callbacks like onCreate, onStart, onResume, onPause, onStop, and onDestroy that define when to initialize UI, start/stop listeners, and release resources.
- Configuration changes: The system may destroy and recreate components (e.g., on rotation); use lifecycle-aware patterns (ViewModel, onSaveInstanceState) to preserve state safely.
- Process and memory management: Android can kill background components to reclaim resources; code must assume callbacks may not all be called symmetrically and avoid relying on "always running" components.
- Lifecycle-aware components: Use AndroidX Lifecycle, ViewModel, LiveData, and coroutines/Flow with lifecycleScope to automatically tie work to the appropriate lifecycle state.
- Common pitfalls: Doing heavy work or long-running tasks in UI callbacks, leaking Context or Views beyond their lifecycle, and ignoring lifecycle events during navigation and configuration changes.

## Ключевые Моменты (RU)

- Состояния компонентов: Activity и Fragment проходят через колбэки onCreate, onStart, onResume, onPause, onStop и onDestroy, которые определяют, когда инициализировать UI, запускать/останавливать слушатели и освобождать ресурсы.
- Конфигурационные изменения: Система может уничтожать и пересоздавать компоненты (например, при повороте экрана); для корректного сохранения состояния используйте паттерны ViewModel и onSaveInstanceState.
- Управление процессом и памятью: Android может убивать фоновые компоненты для освобождения ресурсов; нельзя полагаться на симметричный вызов всех колбэков или на "вечно работающие" компоненты.
- Компоненты, учитывающие жизненный цикл: Используйте AndroidX Lifecycle, ViewModel, LiveData, а также корутины/Flow с lifecycleScope для автоматической привязки работы к нужным состояниям жизненного цикла.
- Типичные ошибки: Тяжелые операции в UI-колбэках, долгие задачи без учета жизненного цикла, утечки Context или View и игнорирование событий жизненного цикла при навигации и изменении конфигурации.

## References

- Android official docs: https://developer.android.com/guide/components/activities/activity-lifecycle
- Android official docs (Lifecycle-aware components): https://developer.android.com/topic/libraries/architecture/lifecycle

