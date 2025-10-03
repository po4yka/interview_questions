---
id: 20251003140107
title: What is the difference between working with list and sequence / В чем разница между работой с list и работой с sequence
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, collections]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/433
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
tags: [kotlin, collections, list,sequence, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What is the difference between working with list and sequence

# Вопрос (RU)
> В чем разница между работой с list и работой с sequence

---

## Answer (EN)

List is an eager collection where all operations are executed immediately and entirely on all elements at once. Sequence is a lazy collection where operations process elements as needed through a chain. List is suitable for small collections and may use more memory due to intermediate collections. Sequence is efficient for large collections and reduces memory usage.

## Ответ (RU)

List является жадной коллекцией, где все операции выполняются немедленно и целиком над всеми элементами сразу. Sequence является ленивой коллекцией, где операции обрабатывают элементы по мере необходимости через цепочку. List подходит для небольших коллекций и может использовать больше памяти из-за промежуточных коллекций. Sequence эффективен для больших коллекций и уменьшает использование памяти.

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
