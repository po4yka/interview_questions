---
id: 20251003140304
title: What are the features of sealed classes / В чем особенность sealed классов
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, sealed-classes]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/85
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
tags: [kotlin, sealed-classes, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What are the features of sealed classes

# Вопрос (RU)
> В чем особенность sealed классов

---

## Answer (EN)

The feature of sealed classes is restricting the inheritance hierarchy: all their subclasses must be declared in the same file as the sealed class itself. This makes it an ideal tool for creating restricted class hierarchies where you need strict control over the set of possible subtypes, especially when modeling states or operation results as an inheritance tree.

## Ответ (RU)

Особенность запечатанных классов заключается в ограничении иерархии наследования: все их подклассы должны быть объявлены в том же файле что и сам запечатанный класс Это делает его идеальным инструментом для создания ограниченных иерархий классов где требуется строго контролировать набор возможных подтипов особенно при моделировании состояний или результатов операций в виде дерева наследования

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
