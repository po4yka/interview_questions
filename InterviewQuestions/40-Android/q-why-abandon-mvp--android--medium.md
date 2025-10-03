---
id: 20251003140219
title: Why do many people abandon MVP / Почему многие отказываются от MVP
aliases: []

# Classification
topic: android
subtopics: [architecture-mvvm, architecture-mvi]
question_kind: android
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/1084
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
tags: [android, mvp, mvvm, mvi, livedata, flow, coroutines, android/architecture-mvvm, android/architecture-mvi, difficulty/medium, easy_kotlin, lang/ru, platform/android]
---

# Question (EN)
> Why do many people abandon MVP

# Вопрос (RU)
> Почему многие отказываются от MVP

---

## Answer (EN)

Requires a lot of boilerplate code. Hard to scale. Not very flexible with asynchronous data. Modern alternatives MVVM and MVI work better with LiveData, Flow, State, and coroutines.

## Ответ (RU)

Требует много шаблонного кода. Сложно масштабировать. Не очень гибко при асинхронных данных. Современные альтернативы MVVM MVI лучше сочетаются с LiveData Flow State и coroutines

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
