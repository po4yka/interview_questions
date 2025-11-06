---
id: lang-070
title: "PriorityQueue Vs Deque / PriorityQueue против Deque"
aliases: [PriorityQueue Vs Deque, PriorityQueue против Deque]
topic: programming-languages
subtopics: [collections, data-structures, queues]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-class-composition--oop--medium, q-what-is-coroutinescope--programming-languages--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [collections, data-structures, deque, difficulty/easy, kotlin, priority-queue, programming-languages, queue]
---
# Какова Разница Между PriorityQueue И Deque?

# Вопрос (RU)
> Какова разница между PriorityQueue и Deque?

---

# Question (EN)
> What is the difference between PriorityQueue and Deque?

## Ответ (RU)

PriorityQueue — структура данных, где элементы обрабатываются по приоритету вместо порядка добавления. Deque (двусторонняя очередь) позволяет добавлять и удалять элементы с обеих сторон, поддерживая поведение как стека, так и очереди.

## Answer (EN)

**PriorityQueue** is a data structure where elements are processed by priority instead of insertion order. Elements with higher priority are dequeued first, regardless of when they were added.

**Deque** (double-ended queue) allows adding and removing elements from both ends, supporting behavior of both stack (LIFO) and queue (FIFO).

**Key differences:**
- **Ordering**: PriorityQueue orders by priority (natural ordering or comparator), Deque maintains insertion order
- **Access patterns**: PriorityQueue only allows access to the highest-priority element, Deque allows access from both ends
- **Use cases**: PriorityQueue for task scheduling, event processing; Deque for implementing stacks, queues, or sliding window algorithms

---

## Follow-ups

- What are the key differences between this and Java?
- When would you use this in practice?
- What are common pitfalls to avoid?

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Related Questions

-
- [[q-class-composition--oop--medium]]
- [[q-what-is-coroutinescope--programming-languages--medium]]
