---
id: "20251111-100541"
title: "Mst Algorithms / Mst Algorithms"
aliases: ["Mst Algorithms"]
summary: "Foundational concept for interview preparation"
topic: "algorithms"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-algorithms"
related: [c-graph-algorithms, c-algorithms, c-dijkstra-algorithm, c-data-structures, c-dynamic-programming]
created: "2025-11-11"
updated: "2025-11-11"
tags: ["algorithms", "auto-generated", "concept", "difficulty/medium"]
date created: Tuesday, November 11th 2025, 10:05:41 am
date modified: Tuesday, November 25th 2025, 8:54:03 pm
---

# Summary (EN)

MST (Minimum Spanning Tree) algorithms find a subset of edges in a connected, weighted, undirected graph that connects all vertices with the minimum possible total edge weight and without cycles. They are crucial for designing cost-efficient networks (e.g., communication, power, road networks) and appear frequently in interview problems involving graphs, greedy strategies, and optimization. The two classic MST algorithms are Kruskal's (edge-based, using sorting and Union-Find) and Prim's (vertex-based, using priority queues).

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Алгоритмы поиска минимального остовного дерева (MST, Minimum Spanning Tree) находят подмножество рёбер в связном взвешенном неориентированном графе, которое соединяет все вершины без циклов и с минимальной возможной суммарной весовой стоимостью. Они важны для проектирования минимально стоящих сетей (сети связи, электросети, дорожные сети) и часто встречаются в собеседованиях на темы графов, жадных алгоритмов и оптимизации. Классические алгоритмы MST — это алгоритм Крускала (по рёбрам, с сортировкой и Union-Find) и алгоритм Прима (по вершинам, с очередью с приоритетами).

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- MST requirements: works on connected, weighted, undirected graphs; if the graph is disconnected, algorithms find a minimum spanning forest instead.
- Kruskal's algorithm: greedy edge-selection; sort edges by weight and add the smallest edge that does not create a cycle, typically using Disjoint Set (Union-Find); time complexity O(E log E).
- Prim's algorithm: greedy vertex-expansion; grow the tree from a start vertex by repeatedly adding the minimum-weight edge to a new vertex; with a binary heap runs in O(E log V).
- Multiple MSTs: when edge weights are not unique, multiple distinct MSTs may exist with the same total weight; correctness proofs rely on cut and cycle properties.
- Interview focus: choose between Kruskal vs Prim based on graph density and representation; be ready to reason about complexity, implementation details, and edge cases (disconnected graphs, negative weights allowed, etc.).

## Ключевые Моменты (RU)

- Условия для MST: алгоритмы работают для связных взвешенных неориентированных графов; для несвязного графа находят минимальный остовный лес.
- Алгоритм Крускала: жадный выбор рёбер; сортируем рёбра по весу и добавляем минимальное, не образующее цикл, обычно используя структуру "Система непересекающихся множеств" (Union-Find); сложность O(E log E).
- Алгоритм Прима: жадное наращивание от вершины; начинаем с произвольной вершины и каждый раз добавляем минимальное ребро к новой вершине; с бинарной кучей работает за O(E log V).
- Множественность MST: при неуникальных весах возможно несколько различных MST с одинаковой суммарной стоимостью; корректность опирается на свойства разрезов и циклов.
- Фокус на собеседовании: уметь выбирать между Крускалом и Примом в зависимости от плотности графа и представления, анализировать сложность, обсуждать реализацию и крайние случаи (несвязность, отрицательные веса и т.п.).

## References

- "Introduction to Algorithms" by Cormen, Leiserson, Rivest, Stein (CLRS), chapter on Minimum Spanning Trees
- GeeksforGeeks: Minimum Spanning Tree (Kruskal's and Prim's algorithms)
