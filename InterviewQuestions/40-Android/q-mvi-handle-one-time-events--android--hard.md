---
id: 20251003140215
title: How to handle events in MVI that don't need to be stored / Как с MVI обрабатывать события, которые не нужно хранить?
aliases: []

# Classification
topic: android
subtopics: [architecture-mvi, lifecycle]
question_kind: android
difficulty: hard

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/769
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
tags: [android, mvi, livedata, viewmodel, sharedflow, stateflow, android/architecture-mvi, android/lifecycle, difficulty/hard, easy_kotlin, lang/ru, platform/android]
---

# Question (EN)
> How to handle events in MVI that don't need to be stored

# Вопрос (RU)
> Как с MVI обрабатывать события, которые не нужно хранить?

---

## Answer (EN)

In MVI (Model-View-Intent), to handle events that don't need to be stored in State and avoid re-displaying them when the screen is recreated, you can use: 1. SingleLiveEvent - LiveData that sends an event only once and doesn't resend it to new subscribers. 2. SharedFlow with replay = 0 for events that shouldn't repeat on new subscriber. 3. EventWrapper as a workaround for StateFlow - a class that checks if an event was already handled and doesn't show it again.

## Ответ (RU)

В MVI (Model-View-Intent) для обработки событий, которые не нужно хранить в State и избежать их повторного отображения при пересоздании экрана можно использовать следующие подходы: 1. Использовать SingleLiveEvent - LiveData, которая отправляет событие только один раз и не пересылает его новым подписчикам. Пример реализации SingleLiveEvent и использования в ViewModel показаны в тексте вопроса. 2. Использовать SharedFlow с replay = 0 для событий, которые не должны повторяться при подписке новых потребителей. Пример реализации SharedFlow в ViewModel и подписки на него показаны в тексте вопроса. 3. Использовать EventWrapper как обходной путь для StateFlow - класс, который позволяет проверять было ли событие уже обработано и не показывать его повторно.

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
