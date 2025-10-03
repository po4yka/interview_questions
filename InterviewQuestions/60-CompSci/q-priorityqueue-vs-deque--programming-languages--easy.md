---
id: 20251003140502
title: PriorityQueue vs Deque / Различия между PriorityQueue и Deque
aliases: []

# Classification
topic: programming-languages
subtopics: [kotlin, collections, queue]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/1445
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-kotlin
related:
  - c-kotlin-collections
  - c-data-structures

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [kotlin, collections, queue, priority-queue, deque, data-structures, difficulty/easy, easy_kotlin, lang/ru, programming-languages]
---

# Question (EN)
> What is the difference between PriorityQueue and Deque?

# Вопрос (RU)
> Какова разница между PriorityQueue и Deque?

---

## Answer (EN)

**PriorityQueue** is a data structure where elements are processed by priority instead of insertion order. Elements with higher priority are dequeued first, regardless of when they were added.

**Deque** (double-ended queue) allows adding and removing elements from both ends, supporting behavior of both stack (LIFO) and queue (FIFO).

**Key differences:**
- **Ordering**: PriorityQueue orders by priority (natural ordering or comparator), Deque maintains insertion order
- **Access patterns**: PriorityQueue only allows access to the highest-priority element, Deque allows access from both ends
- **Use cases**: PriorityQueue for task scheduling, event processing; Deque for implementing stacks, queues, or sliding window algorithms

## Ответ (RU)

PriorityQueue — структура данных, где элементы обрабатываются по приоритету вместо порядка добавления. Deque (двусторонняя очередь) позволяет добавлять и удалять элементы с обеих сторон, поддерживая поведение как стека, так и очереди.

---

## Follow-ups
- How is priority determined in PriorityQueue?
- What are the time complexities of operations in both structures?
- When should you use ArrayDeque vs LinkedList for Deque implementation?

## References
- [[c-kotlin-collections]]
- [[c-data-structures]]
- [[moc-kotlin]]

## Related Questions
- [[q-list-vs-sequence--programming-languages--medium]]
- [[q-data-structures-overview--algorithms--easy]]
