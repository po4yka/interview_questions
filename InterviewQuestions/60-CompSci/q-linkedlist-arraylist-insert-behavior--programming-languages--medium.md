---
id: 20251003140101
title: How will LinkedList and ArrayList behave when inserting an element / Как будут вести себя linked list и array list, если вставить в них элемент
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, collections]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/73
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
tags: [kotlin, collections, data structures,collections, difficulty/medium, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> How will LinkedList and ArrayList behave when inserting an element

# Вопрос (RU)
> Как будут вести себя linked list и array list, если вставить в них элемент

---

## Answer (EN)

LinkedList and ArrayList are two different implementations of the List interface, each with its own characteristics for element insertion. ArrayList is based on a dynamic array, and adding an element to the end of the list takes O(1) time, but may require array expansion which takes O(n). Adding an element to the middle of the list has time complexity O(n - index). LinkedList implements a doubly-linked list data structure, and adding an element to the end or beginning takes O(1) time. Adding an element to the middle has time complexity O(n) due to the need to find the node.

## Ответ (RU)

LinkedList и ArrayList представляют собой две разные реализации интерфейса List, и каждая из них имеет свои особенности поведения при вставке элементов. ArrayList основан на динамическом массиве и добавление элемента в конец списка выполняется за время O(1), но может потребовать расширения массива, что занимает O(n). Добавление элемента в середину списка имеет временную сложность O(n - index). LinkedList реализует структуру данных двунаправленного связного списка и добавление элемента в конец или начало списка выполняется за время O(1). Добавление элемента в середину списка имеет временную сложность O(n) из-за необходимости найти узел.

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
