---
id: 20251003140316
title: How do SAM (Single Abstract Method) conversions work / Как работают SAM (Single Abstract Method)?
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, sam, lambda]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/1067
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
tags: [kotlin, sam, lambda-functions, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> How do SAM (Single Abstract Method) conversions work

# Вопрос (RU)
> Как работают SAM (Single Abstract Method)?

---

## Answer (EN)

SAM conversions allow using lambda functions instead of objects of classes with one abstract method. This makes code more concise and readable when working with Java APIs or interfaces in Kotlin. Example: an interface with one method is automatically converted to a functional type.

## Ответ (RU)

SAM-конверсии позволяют использовать лямбда-функции вместо объектов классов с одним абстрактным методом Это делает код более кратким и читабельным при работе с Java API или интерфейсами в Kotlin Пример интерфейс с одним методом автоматически превращается в функциональный тип

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
