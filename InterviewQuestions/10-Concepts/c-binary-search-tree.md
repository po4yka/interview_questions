---
id: "20251111-101046"
title: "Binary Search Tree / Binary Search Tree"
aliases: ["Binary Search Tree"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-cs"
related: ["c-binary-search", "c-data-structures", "c-algorithms", "c-graph-algorithms"]
created: "2025-11-11"
updated: "2025-11-11"
tags: [concept, difficulty/medium, programming-languages]
---

# Summary (EN)

A Binary Search Tree (BST) is a binary tree data structure where each node's left subtree contains only keys less than the node's key and the right subtree contains only keys greater than the node's key. This ordering property enables efficient search, insertion, and deletion operations in average-case O(log n) time. BSTs are widely used in in-memory indexing, symbol tables, and implementing ordered sets/maps.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Дерево двоичного поиска (Binary Search Tree, BST) — это структура данных в виде бинарного дерева, в которой левое поддерево узла содержит только ключи, строго меньшие ключа узла, а правое — только ключи, строго большие ключа узла. Благодаря этому свойству поиск, вставка и удаление в среднем выполняются за O(log n). BST широко используется для индексации в памяти, реализации упорядоченных множеств и отображений.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Ordered structure: Maintains a strict left < node < right key order, enabling binary search over tree nodes.
- Time complexity: Search/insert/delete are O(log n) on average for balanced trees, but degrade to O(n) in the worst case for skewed trees.
- No duplicates (classic BST): Standard definition disallows duplicate keys or requires a clear rule (e.g., duplicates go consistently to one side).
- Traversals: In-order traversal of a BST produces all keys in sorted ascending order, useful for range queries and ordered iteration.
- Foundation for advanced trees: Conceptually underlies balanced variants like AVL trees, Red-Black trees, and Treaps used in production libraries.

## Ключевые Моменты (RU)

- Упорядоченность: Строгое свойство left < node < right позволяет выполнять двоичный поиск по узлам дерева.
- Временная сложность: Поиск/вставка/удаление в среднем O(log n) для сбалансированных деревьев, но в худшем случае (перекошенное дерево) — O(n).
- Обращение с дубликатами: В классическом определении либо запрещены дубликаты, либо используется чёткое правило (например, все дубликаты влево/вправо).
- Обходы: Симметричный (in-order) обход BST возвращает ключи в отсортированном порядке, что удобно для диапазонных запросов и упорядоченного обхода.
- Основа для продвинутых структур: Лежит в основе сбалансированных деревьев (AVL, красно-черные деревья, Treap), используемых в стандартных библиотеках.

## References

- CLRS "Introduction to Algorithms" — Chapter on Binary Search Trees
- MIT 6.006 Introduction to Algorithms — lectures on trees and BSTs
