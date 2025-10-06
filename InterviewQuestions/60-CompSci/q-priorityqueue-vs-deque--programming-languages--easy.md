---
tags:
  - collections
  - data-structures
  - deque
  - kotlin
  - priority-queue
  - programming-languages
  - queue
difficulty: easy
---

# Какова разница между PriorityQueue и Deque?

**English**: What is the difference between PriorityQueue and Deque?

## Answer

**PriorityQueue** is a data structure where elements are processed by priority instead of insertion order. Elements with higher priority are dequeued first, regardless of when they were added.

**Deque** (double-ended queue) allows adding and removing elements from both ends, supporting behavior of both stack (LIFO) and queue (FIFO).

**Key differences:**
- **Ordering**: PriorityQueue orders by priority (natural ordering or comparator), Deque maintains insertion order
- **Access patterns**: PriorityQueue only allows access to the highest-priority element, Deque allows access from both ends
- **Use cases**: PriorityQueue for task scheduling, event processing; Deque for implementing stacks, queues, or sliding window algorithms

## Ответ

PriorityQueue — структура данных, где элементы обрабатываются по приоритету вместо порядка добавления. Deque (двусторонняя очередь) позволяет добавлять и удалять элементы с обеих сторон, поддерживая поведение как стека, так и очереди.

