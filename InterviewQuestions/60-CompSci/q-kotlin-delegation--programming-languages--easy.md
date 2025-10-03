---
id: 20251003140312
title: What do you know about delegation / Что известно о делегировании?
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, delegates]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/726
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-features
  - c-kotlin-advanced

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, delegation, by-keyword, difficulty/easy, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What do you know about delegation

# Вопрос (RU)
> Что известно о делегировании?

---

## Answer (EN)

Delegation allows transferring implementation of certain functions or properties to other objects. The by keyword is used to transfer logic, e.g., class MyClass : Interface by Delegate. Kotlin provides built-in delegates like lazy, observable, and vetoable for convenient state management of properties.

## Ответ (RU)

Делегирование позволяет передавать реализацию определённых функций или свойств другим объектам. Используется ключевое слово by для передачи логики например class MyClass : Interface by Delegate. Kotlin предоставляет встроенные делегаты такие как lazy observable и vetoable для удобного управления состоянием свойств.

---

## Follow-ups
- How does this compare to other approaches?
- What are the performance implications?
- When should you use this feature?

## References
- [[c-kotlin-features]]
- [[c-kotlin-advanced]]
- [[moc-kotlin]]

## Related Questions
- [[q-kotlin-inline-functions--programming-languages--medium]]
