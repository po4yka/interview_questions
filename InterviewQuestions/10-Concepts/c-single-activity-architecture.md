---
id: "20251110-142349"
title: "Single Activity Architecture / Single Activity Architecture"
aliases: ["Single Activity Architecture"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-kotlin"
related: []
created: "2025-11-10"
updated: "2025-11-10"
tags: ["programming-languages", "concept", "difficulty/medium", "auto-generated"]
---

# Summary (EN)

Single Activity Architecture is an Android application design approach where the app uses a single Activity as the main entry point and navigation host, while individual screens are represented by Fragments or composable destinations. It centralizes navigation, lifecycle handling, and state management, simplifying back stack control and reducing Activity-level boilerplate. This pattern is common in modern Android apps, especially with Jetpack Navigation and Jetpack Compose.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Single Activity Architecture — это подход к архитектуре Android-приложений, при котором используется одна основная Activity в роли точki входа и навигационного хоста, а отдельные экраны реализуются через Fragment-ы или composable-дестинации. Такой подход централизует навигацию, управление жизненным циклом и состоянием, упрощая работу с back stack и уменьшая boilerplate на уровне Activity. Широко применяется в современных Android-приложениях вместе с Jetpack Navigation и Jetpack Compose.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Centralized navigation: A single Activity hosts a NavHost (Fragments or Compose destinations), making navigation and back stack logic consistent and easier to manage.
- Lifecycle simplification: Fewer Activities means fewer complex lifecycle transitions; most UI logic lives in Fragments/Composables and ViewModels scoped appropriately.
- Better state sharing: Shared ViewModels and a single host Activity make it easier to share state between screens and handle process death/restoration.
- Reduced boilerplate: Eliminates repetitive Activity setup (toolbars, dependency injection wiring, navigation handling) across multiple screens.
- Trade-offs: Increases responsibility of the main Activity and navigation graph; requires careful modularization and screen separation to avoid a “god Activity” or monolithic module.

## Ключевые Моменты (RU)

- Централизованная навигация: Одна Activity выступает NavHost-ом (для Fragment-ов или Compose-дестинаций), что упрощает управление навигацией и back stack.
- Упрощённый жизненный цикл: Меньше Activity — меньше сложных переходов; UI-логика сосредоточена во Fragment-ах/Composable-ах и корректно scope-ленных ViewModel-ях.
- Удобный шаринг состояния: Общие ViewModel-и и один хост позволяют легко делиться состоянием между экранами и корректно обрабатывать восстановление после убийства процесса.
- Меньше boilerplate: Нет дублирования однотипной Activity-конфигурации (toolbar, DI, навигация) для каждого экрана.
- Компромиссы: Возрастает ответственность главной Activity и навигационной схемы; важно следить за модульностью, чтобы не получить «god-Activity» и чрезмерно связанный код.

## References

- Android Developers: Guide to Navigation component (developer.android.com/guide/navigation)
- Android Developers: Principles of modern Android app architecture (developer.android.com/topic/architecture)
