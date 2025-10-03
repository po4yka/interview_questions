---
id: 20251003140111
title: What is the difference between collection functions associateWith() and associateBy() / В чём разница между функциями коллекций associateWith() и associateBy()
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, collections]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/1053
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
tags: [kotlin, collections, collections,associateWith,associateBy, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What is the difference between collection functions associateWith() and associateBy()

# Вопрос (RU)
> В чём разница между функциями коллекций associateWith() и associateBy()

---

## Answer (EN)

associateBy creates a Map where keys are taken from the given logic and values are collection elements. associateWith is the opposite - the element becomes the key and the value is specified separately.

## Ответ (RU)

associateBy создаёт Map, где ключи берутся из заданной логики, а значениями становятся элементы коллекции. associateWith наоборот — элемент становится ключом, а значение задаётся отдельно.

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
