---
id: 20251003140110
title: After iterating data with an iterator, is the order of obtaining this data guaranteed? / После перебирания данных итератором, гарантируется ли очередность получения этих данных?
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, collections]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/976
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
tags: [kotlin, collections, collections,iterators, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> After iterating data with an iterator, is the order of obtaining this data guaranteed?

# Вопрос (RU)
> После перебирания данных итератором, гарантируется ли очередность получения этих данных?

---

## Answer (EN)

It is guaranteed only if the data structure supports order (e.g., List, LinkedList). If the collection is unordered (e.g., HashSet, HashMap.keySet()), the order may be arbitrary and not repeatable.

## Ответ (RU)

Гарантируется только в том случае, если структура данных поддерживает порядок (например, List, LinkedList). Если коллекция неупорядоченная (например, HashSet, HashMap.keySet()), порядок может быть произвольным и не повторяться.

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
