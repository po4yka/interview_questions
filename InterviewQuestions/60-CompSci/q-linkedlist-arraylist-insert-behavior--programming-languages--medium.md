---
id: 20251012-1227111161
title: "Linkedlist Arraylist Insert Behavior / Поведение вставки LinkedList и ArrayList"
topic: programming-languages
difficulty: medium
status: draft
created: 2025-10-13
tags:
  - collections
  - data structures
  - kotlin
  - programming-languages
moc: moc-programming-languages
related: [q-what-is-flow--programming-languages--medium, q-flow-map-operator--programming-languages--medium, q-iterator-pattern--design-patterns--medium]
---
# Как будут вести себя linked list и array list, если вставить в них элемент?

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
- [[q-kak-izmenit-kolichestvo-kolonok-v-recyclerview-v-zavisimosti-ot-orientatsii--programming-languages--easy]] - Data Structures

### Kotlin Language Features
- [[q-arraylist-linkedlist-vector-difference--programming-languages--medium]] - Data Structures
- [[q-collection-implementations--programming-languages--easy]] - Data Structures
- [[q-list-set-map-differences--programming-languages--easy]] - Data Structures
- [[q-equals-hashcode-contracts--programming-languages--hard]] - Data Structures
- [[q-kotlin-immutable-collections--programming-languages--easy]] - Data Structures
