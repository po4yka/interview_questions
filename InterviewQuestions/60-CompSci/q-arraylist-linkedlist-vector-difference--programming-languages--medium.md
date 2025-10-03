---
id: 20251003140103
title: What is the difference between ArrayList, LinkedList, Vector / В чем разница ArrayList, LinkedList, Vector
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, collections]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/156
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
tags: [kotlin, collections, collections,data structures, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What is the difference between ArrayList, LinkedList, Vector

# Вопрос (RU)
> В чем разница ArrayList, LinkedList, Vector

---

## Answer (EN)

ArrayList implements a mutable array with fast random access but slow insertions/deletions. LinkedList implements a doubly-linked list with fast insertions/deletions but slow random access. Vector is similar to ArrayList but synchronized for thread safety and slower due to synchronization.

## Ответ (RU)

ArrayList реализует изменяемый массив с быстрым произвольным доступом, но медленными вставками/удалениями. LinkedList реализует двунаправленный список с быстрыми вставками/удалениями, но медленным произвольным доступом. Vector похож на ArrayList, но синхронизирован для потокобезопасности и медленнее из-за синхронизации.

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
