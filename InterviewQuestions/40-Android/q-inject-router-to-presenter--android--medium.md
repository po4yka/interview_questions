---
id: 20251003140217
title: What to use to inject router directly into presenter / Что использовать для того чтобы роутер инжектился напрямую в презентер
aliases: []

# Classification
topic: android
subtopics: [di-hilt, architecture-mvi]
question_kind: android
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/833
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
tags: [android, dependency-injection, dagger/hilt, koin, android/di-hilt, android/architecture-mvi, difficulty/medium, easy_kotlin, lang/ru, platform/android]
---

# Question (EN)
> What to use to inject router directly into presenter

# Вопрос (RU)
> Что использовать для того чтобы роутер инжектился напрямую в презентер

---

## Answer (EN)

To inject a router into a presenter, you can use Dependency Injection frameworks like Dagger, Hilt, or Koin. This allows passing the router to the presenter through constructor or method, ensuring loose coupling and ease of testing.

## Ответ (RU)

Для внедрения роутера в презентер можно использовать Dependency Injection например Dagger Hilt или Koin Это позволяет передать роутер в презентер через конструктор или метод обеспечивая слабую связность и удобство тестирования

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
