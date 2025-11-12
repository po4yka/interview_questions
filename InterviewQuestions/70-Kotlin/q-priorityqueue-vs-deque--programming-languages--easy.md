---
id: lang-070
title: "PriorityQueue Vs Deque / PriorityQueue против Deque"
aliases: [PriorityQueue Vs Deque, PriorityQueue против Deque]
topic: kotlin
subtopics: [collections, queues]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-collections, q-class-composition--oop--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [collections, deque, difficulty/easy, kotlin, priority-queue, queue]

---

# Вопрос (RU)
> Какова разница между `PriorityQueue` и `Deque`?

# Question (EN)
> What is the difference between `PriorityQueue` and `Deque`?

## Ответ (RU)

`PriorityQueue` — структура данных, где элемент для извлечения выбирается по приоритету (обычно минимальный или максимальный по заданному сравнению), а не по простому порядку добавления. Как правило, эффективные реализации основаны на куче и обеспечивают быстрый доступ только к элементу с наивысшим (или наинизшим) приоритетом в "голове".

`Deque` (двусторонняя очередь) — структура данных, которая позволяет эффективно добавлять и удалять элементы как с начала, так и с конца. Она может моделировать:
- обычную очередь (FIFO), если операции идут с разных концов;
- стек (LIFO), если операции идут с одного конца.

Ключевые отличия:
- Упорядочивание: `PriorityQueue` упорядочивает элементы по приоритету (естественный порядок или компаратор); `Deque` сохраняет последовательность в соответствии с тем, как элементы добавляются в начало и/или конец.
- Шаблоны доступа: `PriorityQueue` обеспечивает эффективный доступ к элементу с наивысшим приоритетом в голове структуры; `Deque` обеспечивает эффективный доступ к элементам с обоих концов.
- Применение: `PriorityQueue` — для задач планирования, обработки событий, когда важен приоритет; `Deque` — для реализации очередей, стеков, алгоритмов со скользящим окном и двусторонних буферов.
- В контексте Kotlin/JVM: стандартная библиотека Kotlin не имеет собственных `PriorityQueue`/`Deque`, обычно используются соответствующие реализации Java (например, `java.util.PriorityQueue` и `java.util.ArrayDeque`), которые ведут себя описанным образом.

## Answer (EN)

A `PriorityQueue` is a data structure where the element to be removed next is chosen by priority (typically smallest or largest according to a comparator), not by simple insertion order. Efficient implementations are usually heap-based and provide fast access only to the head element with highest (or lowest) priority.

A `Deque` (double-ended queue) is a data structure that allows efficient insertion and removal of elements at both the front and the back. It can act as:
- a queue (FIFO) if you enqueue at one end and dequeue at the other;
- a stack (LIFO) if you push and pop at the same end.

Key differences:
- Ordering: `PriorityQueue` orders elements by priority (natural ordering or a comparator); `Deque` preserves the sequence according to how elements are added to the front and/or back.
- Access patterns: `PriorityQueue` provides efficient access/removal for the head element with highest priority; `Deque` provides efficient access/removal from both ends.
- Use cases: `PriorityQueue` is used for task scheduling, event processing, and algorithms where priority matters; `Deque` is used to implement queues, stacks, sliding window algorithms, and double-ended buffers.
- In the Kotlin/JVM context: the Kotlin standard library does not define its own concrete `PriorityQueue`/`Deque` types; you typically use the underlying Java implementations (such as `java.util.PriorityQueue` and `java.util.ArrayDeque`), which follow this behavior.

## Дополнительные вопросы (RU)
- В чем ключевые отличия между этими структурами и Java-реализациями, которые вы используете из Kotlin?
- Когда вы бы использовали каждую из этих структур на практике?
- Какие распространенные подводные камни нужно учитывать?

## Follow-ups

- What are the key differences between this and Java implementations you would use from Kotlin?
- When would you use each of these in practice?
- What are common pitfalls to avoid?

## Ссылки (RU)
- [Документация Kotlin](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- [[c-kotlin]]

## Связанные вопросы (RU)
- [[q-class-composition--oop--medium]]

## Related Questions

- [[q-class-composition--oop--medium]]
