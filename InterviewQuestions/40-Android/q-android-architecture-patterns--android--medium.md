---
id: 20251003140202
title: What architectural patterns are used in the Android framework / Какие архитектурные паттерны используются в Android-фреймворке?
aliases: []

# Classification
topic: android
subtopics: [architecture-mvvm, architecture-mvi, architecture-clean]
question_kind: android
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/81
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-android
related:
  - c-android-architecture
  - c-dependency-injection

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [android, mvc, mvp, mvvm, clean-architecture, android/architecture-mvvm, android/architecture-mvi, android/architecture-clean, difficulty/medium, easy_kotlin, lang/ru, platform/android]
---

# Question (EN)
> What architectural patterns are used in the Android framework

# Вопрос (RU)
> Какие архитектурные паттерны используются в Android-фреймворке?

---

## Answer (EN)

Android development uses the following architectural patterns: Model-View-Controller (MVC), where Model contains business logic and data, View displays the UI, and Controller manages data flow. Model-View-Presenter (MVP), where Model represents the data layer, View delegates user actions to Presenter, and Presenter contains presentation logic. Model-View-ViewModel (MVVM), where Model provides data structure, View displays visual elements, and ViewModel serves as View abstraction with presentation logic. Clean Architecture, proposed by Robert Martin and adapted for Android with separation into domain layer, data layer, and presentation layer. Component-Based Architecture focuses on dividing the application into reusable components.

## Ответ (RU)

В разработке Android-приложений применяются следующие архитектурные паттерны: Model-View-Controller (MVC), где Model содержит бизнес-логику и данные приложения, View отвечает за отображение данных пользовательского интерфейса и Controller управляет потоком данных между Model и View. Model-View-Presenter (MVP), где Model представляет слой данных и бизнес-логику, View делегирует обработку пользовательских действий Presenterу и Presenter содержит логику представления. Model-View-ViewModel (MVVM), где Model обеспечивает структуру данных и бизнес-логику, View отображает визуальные элементы и действия пользователя и ViewModel служит абстракцией View с логикой представления. Clean Architecture, предложенная Робертом Мартином и адаптированная для Android с разделением кода на доменный слой бизнес-логики, слой данных и презентационный слой. Component-Based Architecture фокусируется на разделении приложения на переиспользуемые компоненты.

---

## Follow-ups
- How does this pattern compare to alternatives?
- What are the performance implications?
- When should you use this approach?

## References
- [[c-android-architecture]]
- [[c-dependency-injection]]
- [[moc-android]]

## Related Questions
- [[q-mvvm-vs-mvp--android--medium]]
- [[q-single-activity-approach--android--medium]]
