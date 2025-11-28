---
id: "20251110-160513"
title: "Android Basics / Android Basics"
aliases: ["Android Basics"]
summary: "Foundational concept for interview preparation"
topic: "android"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-android"
related: [c-android, c-activity, c-activity-lifecycle, c-intent, c-android-manifest]
created: "2025-11-10"
updated: "2025-11-10"
tags: ["android", "auto-generated", "concept", "difficulty/medium"]
date created: Monday, November 10th 2025, 8:37:43 pm
date modified: Tuesday, November 25th 2025, 8:54:04 pm
---

# Summary (EN)

Android Basics covers the core concepts required to understand how Android applications are built, structured, and run on mobile devices. It includes the Android architecture (Linux kernel, libraries, Android Runtime, framework), app components (Activities, Services, Broadcast Receivers, Content Providers), UI and resources, and basic data storage and networking. Mastering these fundamentals is essential for writing stable, responsive apps and for succeeding in Android interviews.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Android Basics охватывает основные концепции, необходимые для понимания того, как Android-приложения создаются, структурируются и выполняются на мобильных устройствах. В это входят архитектура Android (ядро Linux, библиотеки, Android Runtime, фреймворк), компоненты приложения (Activity, Service, Broadcast Receiver, Content Provider), пользовательский интерфейс и ресурсы, а также базовое хранение данных и сетевое взаимодействие. Знание этих основ критично для написания стабильных, отзывчивых приложений и успешного прохождения Android-собеседований.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Android architecture: Built on the Linux kernel with system libraries, Android Runtime (ART), application framework APIs, and apps running in separate processes with their own sandbox.
- Core app components: Activities (UI screens), Services (background work), Broadcast Receivers (react to system/global events), Content Providers (structured data sharing).
- UI and resources: Layouts (XML), views, themes/styles, drawables, and resource qualifiers for different screens, locales, and configurations.
- Data and lifecycle: Activity/Fragment lifecycles, configuration changes, persistence via SharedPreferences/DataStore, files, databases (Room/SQLite).
- Permissions and intents: Using intents for navigation and inter-app communication; understanding runtime permissions and basic security considerations.

## Ключевые Моменты (RU)

- Архитектура Android: Основана на ядре Linux, системных библиотеках, Android Runtime (ART), уровне фреймворка и приложениях, работающих в отдельных процессах и песочницах.
- Основные компоненты приложения: Activity (экраны с UI), Service (фоновая работа), Broadcast Receiver (реакция на системные/глобальные события), Content Provider (структурированный доступ и обмен данными).
- UI и ресурсы: Разметки (XML), View-компоненты, темы/стили, графические ресурсы и квалификаторы ресурсов для разных экранов, языков и конфигураций.
- Жизненный цикл и данные: Жизненный цикл Activity/Fragment, обработка смены конфигурации, сохранение данных через SharedPreferences/DataStore, файлы и базы данных (Room/SQLite).
- Разрешения и Intent: Использование intent для навигации и взаимодействия между приложениями; понимание runtime-разрешений и базовых аспектов безопасности.

## References

- https://developer.android.com/guide
- https://developer.android.com/guide/components/fundamentals
