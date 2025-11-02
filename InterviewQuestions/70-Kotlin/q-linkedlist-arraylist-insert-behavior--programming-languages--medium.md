---
id: lang-006
title: "LinkedList ArrayList Insert Behavior / Поведение вставки LinkedList и ArrayList"
aliases: [LinkedList ArrayList Insert Behavior, Поведение вставки LinkedList и ArrayList]
topic: programming-languages
subtopics: [collections, complexity-analysis, data-structures]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-programming-languages
related: [q-flow-map-operator--programming-languages--medium, q-iterator-pattern--design-patterns--medium, q-what-is-flow--programming-languages--medium]
created: 2025-10-13
updated: 2025-10-31
tags: [arraylist, collections, data-structures, difficulty/medium, kotlin, linkedlist, programming-languages]
date created: Friday, October 3rd 2025, 4:14:01 pm
date modified: Saturday, November 1st 2025, 5:43:24 pm
---

# Как Будут Вести Себя Linked List И Array List, Если Вставить В Них Элемент?

# Question (EN)
> How will LinkedList and ArrayList behave when inserting an element?

# Вопрос (RU)
> Как будут вести себя linked list и array list, если вставить в них элемент?

---

## Answer (EN)

LinkedList and ArrayList are two different implementations of the List interface, each with its own characteristics for element insertion. ArrayList is based on a dynamic array, and adding an element to the end of the list takes O(1) time, but may require array expansion which takes O(n). Adding an element to the middle of the list has time complexity O(n - index). LinkedList implements a doubly-linked list data structure, and adding an element to the end or beginning takes O(1) time. Adding an element to the middle has time complexity O(n) due to the need to find the node.

---

## Ответ (RU)

LinkedList и ArrayList представляют собой две разные реализации интерфейса List, и каждая из них имеет свои особенности поведения при вставке элементов. ArrayList основан на динамическом массиве и добавление элемента в конец списка выполняется за время O(1), но может потребовать расширения массива, что занимает O(n). Добавление элемента в середину списка имеет временную сложность O(n - index). LinkedList реализует структуру данных двунаправленного связного списка и добавление элемента в конец или начало списка выполняется за время O(1). Добавление элемента в середину списка имеет временную сложность O(n) из-за необходимости найти узел.


---

## Related Questions

### Android Implementation
- [[q-how-to-implement-view-behavior-when-it-is-added-to-the-tree--android--easy]] - Data Structures
-  - Data Structures

### Kotlin Language Features
-  - Data Structures
-  - Data Structures
-  - Data Structures
-  - Data Structures
- [[q-kotlin-immutable-collections--programming-languages--easy]] - Data Structures
