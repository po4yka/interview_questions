---
id: 20251012-1227111170
title: "Priorityqueue Vs Deque / Priorityqueue против Deque"
topic: computer-science
difficulty: easy
status: draft
moc: moc-compSci
related: [q-data-class-component-functions--programming-languages--easy, q-class-composition--oop--medium, q-what-is-coroutinescope--programming-languages--medium]
created: 2025-10-15
tags:
  - collections
  - data-structures
  - deque
  - kotlin
  - priority-queue
  - programming-languages
  - queue
---
# Какова разница между PriorityQueue и Deque?

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

---

## Ответ (RU)

PriorityQueue — структура данных, где элементы обрабатываются по приоритету вместо порядка добавления. Deque (двусторонняя очередь) позволяет добавлять и удалять элементы с обеих сторон, поддерживая поведение как стека, так и очереди.

## Related Questions

- [[q-data-class-component-functions--programming-languages--easy]]
- [[q-class-composition--oop--medium]]
- [[q-what-is-coroutinescope--programming-languages--medium]]
