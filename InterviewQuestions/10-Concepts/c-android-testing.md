---
id: "20251110-195642"
title: "Android Testing / Android Testing"
aliases: ["Android Testing"]
summary: "Foundational concept for interview preparation"
topic: "android"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-android"
related: [c-android-testing-pyramid, c-unit-testing, c-espresso-testing, c-junit, c-testing]
created: "2025-11-10"
updated: "2025-11-10"
tags: ["android", "auto-generated", "concept", "difficulty/medium"]
date created: Monday, November 10th 2025, 8:37:43 pm
date modified: Tuesday, November 25th 2025, 8:54:04 pm
---

# Summary (EN)

Android testing is the practice of verifying the correctness, stability, performance, and user experience of Android apps across different devices, OS versions, and configurations. It combines local JVM tests and on-device (instrumented) tests to validate both business logic and UI behavior. Effective Android testing reduces regressions, enables safer refactoring, and is essential for shipping reliable apps at scale.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Тестирование Android-приложений — это практика проверки корректности, стабильности, производительности и пользовательского опыта Android-приложений на разных устройствах, версиях ОС и конфигурациях. Оно сочетает локальные JVM-тесты и инструментальные тесты на устройстве для проверки бизнес-логики и поведения UI. Эффективное тестирование Android снижает число регрессий, упрощает рефакторинг и критично для надежного выпуска приложений.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- **Test levels**: Android testing обычно включает unit tests (JVM), integration tests и UI/functional tests (instrumented, Espresso, Compose Testing, UI Automator).
- **Local vs instrumented tests**: Local tests запускаются на JVM и быстры, подходят для бизнес-логики; instrumented tests запускаются на эмуляторе/устройстве и проверяют работу с Android framework и UI.
- **Tooling**: Основные инструменты — JUnit, Kotlin test, Mockito/MockK, Espresso/Compose UI Test, Robolectric, UI Automator, AndroidX Test libraries.
- **Environment fragmentation**: Тесты должны учитывать разнообразие устройств, экранов, API levels, разрешений и условий сети, чтобы выявлять проблемы совместимости.
- **Automation & CI**: Интеграция тестов в CI/CD (Gradle, GitHub Actions, GitLab CI, Jenkins, etc.) обеспечивает раннее обнаружение дефектов и стабильные релизы.

## Ключевые Моменты (RU)

- **Уровни тестирования**: В Android обычно используют unit-тесты (JVM), интеграционные и UI/функциональные тесты (instrumented, Espresso, Compose Testing, UI Automator).
- **Локальные vs инструментальные тесты**: Локальные тесты выполняются на JVM и быстры, подходят для проверки бизнес-логики; инструментальные запускаются на эмуляторе/устройстве и проверяют взаимодействие с Android framework и UI.
- **Инструменты**: Ключевые инструменты — JUnit, Kotlin test, Mockito/MockK, Espresso/Compose UI Test, Robolectric, UI Automator, AndroidX Test библиотеки.
- **Фрагментация среды**: Тесты должны учитывать различия устройств, разрешений экранов, уровней API, разрешений и сетевых условий для выявления проблем совместимости.
- **Автоматизация и CI**: Интеграция тестов в CI/CD (Gradle, GitHub Actions, GitLab CI, Jenkins и др.) обеспечивает раннее обнаружение дефектов и надежные релизы.

## References

- Android Developers - Testing documentation: https://developer.android.com/training/testing
