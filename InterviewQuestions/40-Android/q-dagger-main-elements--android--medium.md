---
id: 20251003140214
title: What are the main elements of Dagger / Из каких основных элементов состоит Dagger
aliases: []

# Classification
topic: android
subtopics: [di-hilt]
question_kind: android
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/764
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
tags: [android, dagger, dependency-injection, android/di-hilt, difficulty/medium, easy_kotlin, lang/ru, platform/android]
---

# Question (EN)
> What are the main elements of Dagger

# Вопрос (RU)
> Из каких основных элементов состоит Dagger

---

## Answer (EN)

1. Component: Interface defining which dependencies can be provided. 2. Module: Class providing dependencies through @Provides annotated methods. 3. Scope: Annotations for managing object lifetime (e.g., @Singleton).

## Ответ (RU)

1. Component: Интерфейс, определяющий, какие зависимости могут быть предоставлены.", "2. Module: Класс, предоставляющий зависимости через аннотированные методы @Provides.", "3. Scope: Аннотации для управления временем жизни объектов (например, @Singleton).").

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
