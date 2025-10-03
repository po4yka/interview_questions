---
id: 20251003140104
title: What is the result of executing val result = (1..3).flatMap { listOf(it, it * 2) }? / Какой результат выполнения выражения val result = (1..3).flatMap { listOf(it, it * 2) }?
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, collections]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/303
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-collections
  - c-collections

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, collections, ranges,flatMap, difficulty/easy, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What is the result of executing val result = (1..3).flatMap { listOf(it, it * 2) }?

# Вопрос (RU)
> Какой результат выполнения выражения val result = (1..3).flatMap { listOf(it, it * 2) }?

---

## Answer (EN)

The result of executing the expression will be the list [1, 2, 2, 4, 3, 6].

## Ответ (RU)

Результат выполнения выражения будет список [1, 2, 2, 4, 3, 6].

---

## Follow-ups
- How does this compare to other collection types?
- What are the performance implications?
- When should you use this approach?

## References
- [[c-kotlin-collections]]
- [[c-collections]]
- [[moc-kotlin]]

## Related Questions
- [[q-list-set-map-differences--programming-languages--easy]]
