---
id: algo-001
title: Data Structures Overview / Обзор структур данных
aliases:
- Data Structures Overview
- Обзор структур данных
topic: algorithms
subtopics:
- data-structures
- fundamentals
question_kind: theory
difficulty: easy
original_language: ru
language_tags:
- en
- ru
status: draft
moc: moc-algorithms
related:
- c-algorithms
- c-data-structures
- q-binary-search-variants--algorithms--medium
created: 2025-10-03
updated: 2025-01-25
tags:
- algorithms
- data-structures
- difficulty/easy
- fundamentals
- overview
anki_cards:
- slug: algo-001-0-en
  language: en
  anki_id: 1768457299227
  synced_at: '2026-01-26T09:10:14.558455'
- slug: algo-001-0-ru
  language: ru
  anki_id: 1768457299253
  synced_at: '2026-01-26T09:10:14.559603'
- slug: algo-001-1-en
  language: en
  anki_id: 1768457299277
  synced_at: '2026-01-26T09:10:14.561197'
- slug: algo-001-1-ru
  language: ru
  anki_id: 1768457299303
  synced_at: '2026-01-26T09:10:14.562635'
---
# Вопрос (RU)
> Расскажи про какие структуры данных знаешь

# Question (EN)
> Tell me about data structures you know

---

## Ответ (RU)

**Теория структур данных:**
Структуры данных - это способы организации и хранения данных в памяти компьютера для эффективного доступа и модификации. Выбор правильной структуры данных критичен для производительности алгоритмов.

**Основные категории:**

**Линейные структуры:**
- **Массивы** - последовательность элементов с O(1) доступом по индексу, фиксированный размер
- **Связные списки** - динамический размер, эффективные вставки/удаления, O(n) доступ по индексу
- **Стеки** - LIFO (Last In, First Out), используются для DFS, отмены действий
- **Очереди** - FIFO (First In, First Out), используются для BFS, обработки задач

**Древовидные структуры:**
- **Бинарные деревья** - каждый узел имеет максимум двух детей
- **BST (Binary Search Trees)** - упорядоченные деревья для эффективного поиска O(log n)
- **AVL деревья** - самобалансирующиеся BST с гарантированной высотой O(log n)
- **Красно-чёрные деревья** - самобалансирующиеся деревья с менее строгими требованиями
- **B-деревья** - многопутевые деревья для баз данных и файловых систем
- **Tries (префиксные деревья)** - для эффективного поиска строк и префиксов

**Хеш-структуры:**
- **Хеш-таблицы** - O(1) среднее время поиска, вставки и удаления по ключу

**Графовые структуры:**
- **Графы** - множество вершин и рёбер, могут быть направленными и ненаправленными

**Структуры типа "куча":**
- **Min/Max Heaps** - деревья для быстрого нахождения минимума/максимума, приоритетные очереди

**Принципы выбора:**
- Операции доступа: массивы O(1), списки O(n)
- Операции поиска: BST O(log n), хеш-таблицы O(1)
- Операции вставки/удаления: списки O(1), массивы O(n)
- Память: массивы компактны, списки с накладными расходами на указатели

## Answer (EN)

**Data Structures Theory:**
Data structures are ways of organizing and storing data in computer memory for efficient access and modification. Choosing the right data structure is critical for algorithm performance.

**Main Categories:**

**Linear Structures:**
- **Arrays** - sequence of elements with O(1) index access, fixed size
- **Linked Lists** - dynamic size, efficient insertions/deletions, O(n) index access
- **Stacks** - LIFO (Last In, First Out), used for DFS, undo operations
- **Queues** - FIFO (First In, First Out), used for BFS, task processing

**Tree Structures:**
- **Binary Trees** - each node has at most two children
- **BST (Binary Search Trees)** - ordered trees for efficient O(log n) search
- **AVL Trees** - self-balancing BST with guaranteed O(log n) height
- **Red-Black Trees** - self-balancing trees with less strict balance requirements
- **B-Trees** - multi-way trees for databases and file systems
- **Tries (Prefix Trees)** - for efficient string and prefix searching

**Hash-based Structures:**
- **Hash Tables** - O(1) average time for search, insert, and delete by key

**Graph Structures:**
- **Graphs** - set of vertices and edges, can be directed or undirected

**Heap Structures:**
- **Min/Max Heaps** - trees for fast min/max finding, priority queues

**Selection Principles:**
- Access operations: arrays O(1), lists O(n)
- Search operations: BST O(log n), hash tables O(1)
- Insert/delete operations: lists O(1), arrays O(n)
- Memory: arrays compact, lists have pointer overhead

---

## Follow-ups

- What are the time/space complexities for each structure?
- When should you choose one structure over another?
- How are these structures implemented in Kotlin/Java?

## Related Questions

### Prerequisites (Easier)
- [[q-kotlin-collections--kotlin--easy]] - Collections basics

### Related (Same Level)
- [[q-binary-search-variants--algorithms--medium]] - Search algorithms
- [[q-sorting-algorithms-comparison--algorithms--medium]] - Sorting algorithms

### Advanced (Harder)
- [[q-binary-search-trees-bst--algorithms--hard]] - BST implementation
- [[q-graph-algorithms-bfs-dfs--algorithms--hard]] - Graph algorithms
