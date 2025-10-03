---
id: 20251003140311
title: What are the limitations of sealed classes / Какие есть ограничения у sealed классов
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, sealed-classes]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/704
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
tags: [kotlin, sealed-classes, class-hierarchy, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What are the limitations of sealed classes

# Вопрос (RU)
> Какие есть ограничения у sealed классов

---

## Answer (EN)

Sealed class limitations: all subtypes must be defined in the same file, sealed class cannot be an interface or abstract class directly, sealed classes and their subtypes cannot be private, sealed classes don't support inheritance from other classes except Any and can only be used for classes and objects but not interfaces. Sealed classes also provide exhaustive when expressions, full control over class hierarchy, and pattern matching support.

## Ответ (RU)

Ограничения sealed классов: все подтипы должны быть определены в том же файле, sealed класс не может быть интерфейсом или абстрактным классом напрямую, sealed классы и их подтипы не могут быть private, sealed классы не поддерживают наследование от других классов кроме Any и могут использоваться только для классов и объектов но не интерфейсов. Также sealed классы обеспечивают исчерпывающие выражения when, полный контроль над иерархией классов и поддержку сопоставления с образцом.

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
