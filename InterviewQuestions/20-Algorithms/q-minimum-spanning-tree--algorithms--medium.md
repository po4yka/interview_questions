---
id: q-minimum-spanning-tree
title: Minimum Spanning Tree
aliases:
- MST Algorithms
- Kruskal and Prim
difficulty: medium
topic: algorithms
subtopics:
- graphs
- greedy
- trees
question_kind: conceptual
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-algorithms
related:
- c-algorithms
- q-advanced-graph-algorithms--algorithms--hard
- q-graph-algorithms-bfs-dfs--algorithms--hard
created: 2025-01-26
updated: 2025-01-26
tags:
- algorithms
- difficulty/medium
- graph
- greedy
- mst
- union-find
sources:
- https://en.wikipedia.org/wiki/Minimum_spanning_tree
- https://en.wikipedia.org/wiki/Kruskal%27s_algorithm
- https://en.wikipedia.org/wiki/Prim%27s_algorithm
anki_cards:
- slug: q-minimum-spanning-tree-0-en
  language: en
  anki_id: 1769404213719
  synced_at: '2026-01-26T09:10:14.536889'
- slug: q-minimum-spanning-tree-0-ru
  language: ru
  anki_id: 1769404213741
  synced_at: '2026-01-26T09:10:14.538244'
---
# Question (EN)
> Explain Kruskal's and Prim's algorithms for finding Minimum Spanning Tree.

## Answer (EN)

**What is a Minimum Spanning Tree (MST)?**

A **Minimum Spanning Tree** is a subset of edges from a connected, undirected, weighted graph that:
- Connects all vertices (spanning)
- Forms a tree (no cycles, exactly V-1 edges)
- Has minimum total edge weight

**Why greedy works (Cut Property):**
For any cut (partition of vertices into two sets), the minimum-weight edge crossing the cut is safe to include in the MST. Both Kruskal's and Prim's algorithms exploit this property.

---

### Kruskal's Algorithm

**Approach:** Process edges globally, sorted by weight.

**Steps:**
1. Sort all edges by weight (ascending)
2. For each edge, if it connects two different components, add it to MST
3. Use **Union-Find** to efficiently detect cycles
4. Stop when MST has V-1 edges

**Time Complexity:** O(E log E) - dominated by sorting

```kotlin
data class Edge(val u: Int, val v: Int, val weight: Int) : Comparable<Edge> {
    override fun compareTo(other: Edge) = weight.compareTo(other.weight)
}

class UnionFind(size: Int) {
    private val parent = IntArray(size) { it }
    private val rank = IntArray(size)

    fun find(x: Int): Int {
        if (parent[x] != x) parent[x] = find(parent[x])  // Path compression
        return parent[x]
    }

    fun union(x: Int, y: Int): Boolean {
        val px = find(x)
        val py = find(y)
        if (px == py) return false  // Already connected (would create cycle)

        // Union by rank
        when {
            rank[px] < rank[py] -> parent[px] = py
            rank[px] > rank[py] -> parent[py] = px
            else -> { parent[py] = px; rank[px]++ }
        }
        return true
    }
}

fun kruskal(vertices: Int, edges: List<Edge>): List<Edge> {
    val mst = mutableListOf<Edge>()
    val uf = UnionFind(vertices)

    for (edge in edges.sorted()) {
        if (uf.union(edge.u, edge.v)) {
            mst.add(edge)
            if (mst.size == vertices - 1) break
        }
    }
    return mst
}
```

---

### Prim's Algorithm

**Approach:** Grow tree from a starting vertex, always adding the cheapest edge to an unvisited vertex.

**Steps:**
1. Start from any vertex, mark it visited
2. Add all its edges to a priority queue
3. Extract minimum-weight edge leading to unvisited vertex
4. Mark new vertex visited, add its edges to queue
5. Repeat until all vertices visited

**Time Complexity:** O(E log V) with binary heap priority queue

```kotlin
data class Edge(val to: Int, val weight: Int)

fun prim(graph: List<List<Edge>>): Int {
    val V = graph.size
    val visited = BooleanArray(V)
    val pq = PriorityQueue<Pair<Int, Int>>(compareBy { it.first })  // (weight, vertex)

    var totalWeight = 0
    pq.offer(0 to 0)  // Start from vertex 0 with 0 cost

    while (pq.isNotEmpty()) {
        val (weight, u) = pq.poll()
        if (visited[u]) continue

        visited[u] = true
        totalWeight += weight

        for (edge in graph[u]) {
            if (!visited[edge.to]) {
                pq.offer(edge.weight to edge.to)
            }
        }
    }
    return totalWeight
}
```

---

### Kruskal vs Prim: When to Use Each

| Criterion | Kruskal | Prim |
|-----------|---------|------|
| **Graph density** | Better for sparse graphs | Better for dense graphs |
| **Data structure** | Edge list | Adjacency list |
| **Time complexity** | O(E log E) | O(E log V) |
| **Parallelizable** | Yes (edges independent) | No (sequential growth) |
| **Disconnected graphs** | Finds forest naturally | Needs multiple starts |
| **Implementation** | Needs Union-Find | Needs Priority Queue |

**Rule of thumb:**
- **Sparse graph (E ~ V):** Kruskal
- **Dense graph (E ~ V^2):** Prim
- **Need forest (disconnected):** Kruskal
- **Already have adjacency list:** Prim

---

### Applications

1. **Network design:** Minimum cost to connect all nodes (cables, roads)
2. **Clustering:** Remove heaviest edges from MST to form k clusters
3. **Approximation algorithms:** MST-based 2-approximation for TSP
4. **Image segmentation:** Graph-based region merging

---

## Vopros (RU)
> Объясните алгоритмы Краскала и Прима для поиска минимального остовного дерева.

## Otvet (RU)

**Что такое минимальное остовное дерево (MST)?**

**Минимальное остовное дерево** - это подмножество рёбер связного неориентированного взвешенного графа, которое:
- Соединяет все вершины (остовное)
- Образует дерево (без циклов, ровно V-1 рёбер)
- Имеет минимальный суммарный вес рёбер

**Почему жадный подход работает (свойство разреза):**
Для любого разреза (разбиения вершин на два множества) ребро минимального веса, пересекающее разрез, безопасно включать в MST. Оба алгоритма используют это свойство.

---

### Алгоритм Краскала

**Подход:** Обрабатываем рёбра глобально, отсортированные по весу.

**Шаги:**
1. Сортируем все рёбра по весу (по возрастанию)
2. Для каждого ребра: если оно соединяет две разные компоненты, добавляем в MST
3. Используем **Union-Find** для эффективного обнаружения циклов
4. Останавливаемся, когда в MST V-1 рёбер

**Сложность:** O(E log E) - определяется сортировкой

---

### Алгоритм Прима

**Подход:** Растим дерево от стартовой вершины, всегда добавляя самое дешёвое ребро к непосещённой вершине.

**Шаги:**
1. Начинаем с любой вершины, помечаем как посещённую
2. Добавляем все её рёбра в очередь с приоритетом
3. Извлекаем ребро минимального веса, ведущее к непосещённой вершине
4. Помечаем новую вершину посещённой, добавляем её рёбра в очередь
5. Повторяем, пока не посетим все вершины

**Сложность:** O(E log V) с бинарной кучей

---

### Краскал vs Прим: Когда использовать

| Критерий | Краскал | Прим |
|----------|---------|------|
| **Плотность графа** | Лучше для разреженных | Лучше для плотных |
| **Структура данных** | Список рёбер | Список смежности |
| **Сложность** | O(E log E) | O(E log V) |
| **Параллелизация** | Да (рёбра независимы) | Нет (последовательный рост) |
| **Несвязные графы** | Находит лес естественно | Нужно несколько запусков |
| **Реализация** | Нужен Union-Find | Нужна очередь с приоритетом |

**Практическое правило:**
- **Разреженный граф (E ~ V):** Краскал
- **Плотный граф (E ~ V^2):** Прим
- **Нужен лес (несвязный граф):** Краскал
- **Уже есть список смежности:** Прим

---

### Применения

1. **Проектирование сетей:** минимальная стоимость соединения всех узлов
2. **Кластеризация:** удаляем самые тяжёлые рёбра MST для получения k кластеров
3. **Приближённые алгоритмы:** 2-аппроксимация для задачи коммивояжёра на основе MST
4. **Сегментация изображений:** объединение регионов на основе графов

---

## Follow-ups

- How would you modify Kruskal's to find a maximum spanning tree?
- Can MST algorithms handle negative edge weights?
- How do you find the second-best MST?
- What is Boruvka's algorithm and when is it useful?

## Дополнительные вопросы (RU)

- Как модифицировать алгоритм Краскала для поиска максимального остовного дерева?
- Работают ли алгоритмы MST с отрицательными весами рёбер?
- Как найти второе по оптимальности MST?
- Что такое алгоритм Борувки и когда он полезен?

---

## Related Questions

### Prerequisites (Easier)
- [[q-data-structures-overview--algorithms--easy]] - Basic data structures
- [[q-graph-algorithms-bfs-dfs--algorithms--hard]] - Graph traversal basics

### Related (Same Level)
- [[q-union-find--algorithms--medium]] - Union-Find data structure in depth

### Advanced (Harder)
- [[q-advanced-graph-algorithms--algorithms--hard]] - Includes Dijkstra, Floyd-Warshall, Bellman-Ford

## Связанные вопросы (RU)

### Предварительные (проще)
- [[q-data-structures-overview--algorithms--easy]] - Базовые структуры данных
- [[q-graph-algorithms-bfs-dfs--algorithms--hard]] - Обход графов

### Связанные (тот же уровень)
- [[q-union-find--algorithms--medium]] - Структура Union-Find подробно

### Продвинутые (сложнее)
- [[q-advanced-graph-algorithms--algorithms--hard]] - Дейкстра, Флойд-Уоршелл, Беллман-Форд

## References
- [[c-algorithms]]
- https://en.wikipedia.org/wiki/Minimum_spanning_tree
- https://en.wikipedia.org/wiki/Kruskal%27s_algorithm
- https://en.wikipedia.org/wiki/Prim%27s_algorithm
