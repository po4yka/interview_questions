---
id: 20251012-122752
title: Data structures overview / Обзор структур данных
aliases: []

# Classification
topic: algorithms
subtopics: [data-structures, fundamentals]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/478
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-algorithms
related: [q-graph-algorithms-bfs-dfs--algorithms--hard, q-binary-search-variants--algorithms--medium, q-sorting-algorithms-comparison--algorithms--medium]
  - c-data-structures
  - c-algorithms

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [data-structures, overview, algorithms/data-structures, algorithms/fundamentals, difficulty/easy, easy_kotlin, lang/ru]
---
# Question (EN)
> Tell me about data structures you know
# Вопрос (RU)
> Расскажи про какие структуры данных знаешь

---

## Answer (EN)

I know many data structures, including:

**Linear structures:**
- Arrays
- Linked lists (singly and doubly-linked)
- Stacks
- Queues

**Tree structures:**
- Binary trees
- AVL trees
- Red-black trees
- B-trees
- Prefix trees (tries)

**Hash-based structures:**
- Hash tables

**Graph structures:**
- Graphs

**Heap structures:**
- Min heaps
- Max heaps

Each data structure has its own characteristics and is used depending on the algorithm requirements and operations that need to be optimized.

## Ответ (RU)

Я знаю о многих структурах данных. Вот основные категории:

**Линейные структуры:**
- **Массивы (Arrays)** - последовательность элементов фиксированного размера с O(1) доступом по индексу
- **Связные списки (Linked Lists)** - элементы связаны указателями, бывают односвязные и двусвязные
  - Односвязные: каждый элемент хранит ссылку на следующий
  - Двусвязные: каждый элемент хранит ссылки на следующий и предыдущий
- **Стеки (Stacks)** - LIFO (Last In, First Out) - последним пришёл, первым ушёл
- **Очереди (Queues)** - FIFO (First In, First Out) - первым пришёл, первым ушёл

**Древовидные структуры:**
- **Бинарные деревья (Binary Trees)** - каждый узел имеет максимум двух детей
- **Деревья поиска (BST - Binary Search Trees)** - упорядоченные бинарные деревья для эффективного поиска
- **AVL деревья** - самобалансирующиеся деревья поиска с гарантированной высотой O(log n)
- **Красно-чёрные деревья (Red-Black Trees)** - самобалансирующиеся деревья с менее строгими требованиями баланса
- **B-деревья** - многопутевые деревья, используются в базах данных и файловых системах
- **Префиксные деревья (Tries)** - деревья для эффективного поиска строк и префиксов

**Структуры на основе хеширования:**
- **Хеш-таблицы (Hash Tables)** - структура данных с O(1) средним временем поиска, вставки и удаления

**Графовые структуры:**
- **Графы (Graphs)** - множество вершин и рёбер, могут быть направленными и ненаправленными

**Структуры типа "куча":**
- **Минимальные кучи (Min Heaps)** - дерево, где родитель меньше детей, используется для приоритетных очередей
- **Максимальные кучи (Max Heaps)** - дерево, где родитель больше детей

**Характеристики и применение:**

Каждая структура данных имеет свои особенности и используется в зависимости от требований к алгоритму и операциям, которые необходимо оптимизировать:

- **Массивы** - быстрый доступ по индексу, но фиксированный размер
- **Связные списки** - динамический размер, эффективные вставки/удаления, но медленный доступ по индексу
- **Стеки** - для отмены действий (undo), обхода в глубину (DFS), вычисления выражений
- **Очереди** - для обработки задач по порядку, обхода в ширину (BFS)
- **Деревья поиска** - для поддержания отсортированных данных с быстрым поиском
- **Хеш-таблицы** - для быстрого поиска по ключу
- **Графы** - для моделирования сетей, связей, зависимостей
- **Кучи** - для быстрого нахождения минимума/максимума, реализации приоритетных очередей

Выбор структуры данных критичен для производительности алгоритма и зависит от операций, которые будут выполняться чаще всего.

---

## Follow-ups
- What are the time/space complexities for each structure?
- When should you choose one structure over another?
- How are these structures implemented in Kotlin/Java?

## References
- [[c-data-structures]]
- [[c-algorithms]]
- [[moc-algorithms]]

## Related Questions

### Related (Easy)
- [[q-kotlin-collections--kotlin--easy]] - Collections
