---
id: 20251003140213
title: After getting a result inside Presenter, how to notify the View / После получения результата внутри Presenter как сообщить об этом View
aliases: []

# Classification
topic: android
subtopics: [architecture-mvi, lifecycle]
question_kind: android
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/762
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
tags: [android, presenter, view, callback, livedata, android/architecture-mvi, android/lifecycle, difficulty/medium, easy_kotlin, lang/ru, platform/android]
---

# Question (EN)
> After getting a result inside Presenter, how to notify the View

# Вопрос (RU)
> После получения результата внутри Presenter как сообщить об этом View

---

## Answer (EN)

Through an interface: Presenter calls interface methods that View implements. Using callbacks: View provides Presenter with a callback that's invoked when data updates. Through LiveData if using MVVM: Presenter can update data that View observes.

## Ответ (RU)

Через интерфейс: Presenter вызывает методы интерфейса который реализует View С помощью callback-ов: View предоставляет Presenter-у callback который вызывается при обновлении данных Через LiveData если используется MVVM: Presenter может обновить данные которые View наблюдает

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
