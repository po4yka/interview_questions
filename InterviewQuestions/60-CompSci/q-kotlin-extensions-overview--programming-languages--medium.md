---
id: 20251003140303
title: What do you know about extensions / Что известно про extension ?
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, extensions]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/74
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
tags: [kotlin, extension-functions, extension-properties, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What do you know about extensions

# Вопрос (RU)
> Что известно про extension ?

---

## Answer (EN)

Extension functions and properties allow adding new functionality to existing classes without modifying them or using inheritance. Extensions don't change the class they're added to, but provide a way to extend its functionality. Extension functions add new methods to classes and are declared with the type they extend. Extension properties add new properties to existing classes and are declared similarly to functions. Extensions cannot access private or protected class members. Benefits include improved code readability, convenient code organization, and increased flexibility.

## Ответ (RU)

Extension функции и свойства позволяют добавлять новую функциональность к существующим классам без их модификации или наследования. Расширения не изменяют класс, к которому они добавлены, а предоставляют способ расширить его функциональность. Extension функции позволяют добавлять новые методы к классу и объявляются с указанием типа, который они расширяют. Extension свойства позволяют добавлять новые свойства к существующим классам и объявляются аналогично функциям. Расширения не могут доступать к приватным или защищенным членам класса. Преимущества использования включают улучшение читаемости кода, удобную организацию кода и повышение гибкости.

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
