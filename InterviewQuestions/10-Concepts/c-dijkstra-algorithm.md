---
id: "20251111-100605"
title: "Dijkstra Algorithm / Dijkstra Algorithm"
aliases: ["Dijkstra Algorithm"]
summary: "Foundational concept for interview preparation"
topic: "algorithms"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-algorithms"
related: []
created: "2025-11-11"
updated: "2025-11-11"
tags: ["algorithms", "concept", "difficulty/medium", "auto-generated"]
---

# Summary (EN)

Dijkstra's algorithm is a classic shortest-path algorithm that computes the minimum distance from a single source node to all other nodes in a weighted graph with non-negative edge weights. It is widely used in routing, navigation systems, and network optimization due to its efficiency and deterministic behavior. Understanding its priority-queue-based implementation and complexity is a common expectation in technical interviews.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

Алгоритм Дейкстры — классический алгоритм поиска кратчайших путей от одной исходной вершины до всех остальных в взвешенном графе с неотрицательными весами рёбер. Широко используется в задачах маршрутизации, навигационных системах и оптимизации сетей благодаря эффективности и предсказуемости результатов. Понимание реализации с очередью с приоритетами и оценки сложности часто ожидается на технических собеседованиях.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Works only with non-negative edge weights; negative weights require other algorithms (e.g., Bellman-Ford).
- Typical implementation uses a min-priority queue (often a binary heap) to repeatedly extract the closest unvisited node.
- Time complexity: O((V + E) log V) with a binary heap; O(V^2) with a simple array implementation.
- Produces both minimum distances and, by storing predecessors, the actual shortest paths from the source.
- Commonly applied in routing protocols, map services (GPS), and resource/latency optimization problems.

## Ключевые Моменты (RU)

- Корректно работает только при неотрицательных весах рёбер; для отрицательных весов применяют другие алгоритмы (например, Беллмана–Форда).
- Типичная реализация использует очередь с приоритетами (минимальную кучу) для выбора ближайшей непосещённой вершины.
- Временная сложность: O((V + E) log V) при использовании бинарной кучи; O(V^2) при простой массивной реализации.
- Позволяет получить как значения кратчайших расстояний, так и сами пути при хранении предшественников вершин.
- Часто используется в протоколах маршрутизации, картографических сервисах (GPS) и задачах оптимизации задержек и ресурсов.

## References

- CLRS: "Introduction to Algorithms" — chapter on single-source shortest paths / Dijkstra's algorithm
- Dijkstra's algorithm article on GeeksforGeeks and similar reputable algorithm resources
