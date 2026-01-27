---
id: algo-004
title: Advanced Graph Algorithms (Dijkstra, MST, Floyd-Warshall) / Продвинутые алгоритмы
  на графах
aliases:
- Advanced Graph Algorithms
- Продвинутые алгоритмы на графах
topic: algorithms
subtopics:
- graph
- minimum-spanning-tree
- shortest-path
question_kind: coding
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-algorithms
related:
- c-algorithms
- c-graph-algorithms
- q-graph-algorithms-bfs-dfs--algorithms--hard
created: 2025-10-12
updated: 2025-11-11
tags:
- algorithms
- bellman-ford
- difficulty/hard
- dijkstra
- floyd-warshall
- graph
- mst
- shortest-path
sources:
- https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
- https://en.wikipedia.org/wiki/Minimum_spanning_tree
anki_cards:
- slug: algo-004-0-en
  language: en
  anki_id: 1768457298477
  synced_at: '2026-01-26T09:10:14.474886'
- slug: algo-004-0-ru
  language: ru
  anki_id: 1768457298503
  synced_at: '2026-01-26T09:10:14.476194'
- slug: algo-004-1-en
  language: en
  anki_id: 1768457298528
  synced_at: '2026-01-26T09:10:14.477883'
- slug: algo-004-1-ru
  language: ru
  anki_id: 1768457298553
  synced_at: '2026-01-26T09:10:14.480030'
- slug: algo-004-2-en
  language: en
  anki_id: 1768457298578
  synced_at: '2026-01-26T09:10:14.482028'
- slug: algo-004-2-ru
  language: ru
  anki_id: 1768457298604
  synced_at: '2026-01-26T09:10:14.483358'
---
# Вопрос (RU)
> Как работают алгоритмы Дейкстры, MST (Краскал, Прим), Флойда-Уоршелла и Беллмана-Форда?

# Question (EN)
> How do Dijkstra's algorithm, MST (Kruskal, Prim), Floyd-Warshall, and Bellman-Ford work?

---

## Ответ (RU)

**Теория продвинутых алгоритмов на графах:**
Продвинутые алгоритмы на графах решают две основные категории задач: кратчайшие пути и минимальные остовные деревья. Выбор алгоритма зависит от характеристик графа (ориентированный/неориентированный, наличие отрицательных весов, плотность) и требований задачи. См. также [[c-algorithms]].

**Основные концепции:**
- **Кратчайшие пути**: нахождение оптимальных маршрутов между вершинами.
- **MST**: соединение всех вершин связного неориентированного взвешенного графа с минимальной суммарной стоимостью (без циклов).
- **Жадные алгоритмы**: локально оптимальный выбор на каждом шаге (Дейкстра, Краскал, Прим).
- **Динамическое программирование**: решение через подзадачи (Флойд–Уоршелл).

Ниже приведены канонические реализации и ключевые идеи.

**Алгоритм Дейкстры (O((V + E) log V) с очередью с приоритетом):**
```kotlin
// Находит кратчайшие пути от одной исходной вершины в графе без отрицательных весов рёбер
// graph.vertices: количество вершин
// graph.adj[u]: список рёбер из u, каждое Edge(to, weight)
data class Edge(val to: Int, val weight: Int)
data class Node(val vertex: Int, val distance: Int) : Comparable<Node> {
    override fun compareTo(other: Node): Int = compareValues(this.distance, other.distance)
}

fun dijkstra(graph: Graph, source: Int): IntArray {
    val distances = IntArray(graph.vertices) { Int.MAX_VALUE }
    distances[source] = 0

    val priorityQueue = PriorityQueue<Node>()
    priorityQueue.offer(Node(source, 0))
    val visited = BooleanArray(graph.vertices)

    while (priorityQueue.isNotEmpty()) {
        val (u, dist) = priorityQueue.poll()
        if (visited[u]) continue
        visited[u] = true

        // Релаксация: обновляем расстояния до соседей
        for (edge in graph.adj[u]) {
            val v = edge.to
            val weight = edge.weight

            if (dist != Int.MAX_VALUE &&
                dist + weight < distances[v]) {
                distances[v] = dist + weight
                priorityQueue.offer(Node(v, distances[v]))
            }
        }
    }

    return distances
}
```

**Алгоритм Краскала (MST, O(E log E)):**
```kotlin
// Находит минимальное остовное дерево в связном неориентированном взвешенном графе через сортировку рёбер
// edges: список рёбер вида (u, v, weight)
data class MSTEdge(val from: Int, val to: Int, val weight: Int) : Comparable<MSTEdge> {
    override fun compareTo(other: MSTEdge): Int = compareValues(this.weight, other.weight)
}

class UnionFind(size: Int) {
    private val parent = IntArray(size) { it }
    private val rank = IntArray(size) { 0 }

    fun find(x: Int): Int {
        if (parent[x] != x) {
            parent[x] = find(parent[x])  // Сжатие пути
        }
        return parent[x]
    }

    fun union(x: Int, y: Int): Boolean {
        val rootX = find(x)
        val rootY = find(y)
        if (rootX == rootY) return false

        // Объединение по рангу
        when {
            rank[rootX] < rank[rootY] -> parent[rootX] = rootY
            rank[rootX] > rank[rootY] -> parent[rootY] = rootX
            else -> {
                parent[rootY] = rootX
                rank[rootX]++
            }
        }
        return true
    }
}

fun kruskalMST(vertices: Int, edges: List<MSTEdge>): List<MSTEdge> {
    val mst = mutableListOf<MSTEdge>()
    val uf = UnionFind(vertices)

    // Сортируем рёбра по возрастанию веса
    val sortedEdges = edges.sorted()

    // Жадно добавляем рёбра, которые не создают циклы
    for (edge in sortedEdges) {
        if (uf.union(edge.from, edge.to)) {
            mst.add(edge)
            if (mst.size == vertices - 1) break
        }
    }

    return mst
}
```

**Алгоритм Прима (MST, O(E log V) с очередью с приоритетом):**
```kotlin
// Растит MST от стартовой вершины в связном неориентированном взвешенном графе
// graph.adj[u]: список рёбер Edge(to, weight) для неориентированного графа
fun primMST(graph: Graph): List<MSTEdge> {
    val mst = mutableListOf<MSTEdge>()
    val visited = BooleanArray(graph.vertices)
    val pq = PriorityQueue<MSTEdge>()

    // Начинаем с вершины 0
    visited[0] = true
    for (edge in graph.adj[0]) {
        pq.offer(MSTEdge(0, edge.to, edge.weight))
    }

    while (pq.isNotEmpty() && mst.size < graph.vertices - 1) {
        val edge = pq.poll()
        val u = edge.from
        val v = edge.to

        // Выбираем ребро, которое ведет в ещё не посещённую вершину
        if (visited[u] && visited[v]) continue

        val next = if (visited[u]) v else u
        mst.add(MSTEdge(u, next, edge.weight))
        visited[next] = true

        // Добавляем рёбра из новой вершины
        for (nextEdge in graph.adj[next]) {
            val to = nextEdge.to
            if (!visited[to]) {
                pq.offer(MSTEdge(next, to, nextEdge.weight))
            }
        }
    }

    return mst
}
```

**Алгоритм Флойда–Уоршелла (O(V^3)):**
```kotlin
// Находит кратчайшие пути между всеми парами вершин
// graph[i][j]: вес ребра i->j или INF (например, Int.MAX_VALUE / 2) если ребра нет;
// graph[i][i] обычно 0.
fun floydWarshall(graph: Array<IntArray>): Array<IntArray> {
    val V = graph.size
    val dist = Array(V) { i -> graph[i].clone() }

    for (k in 0 until V) {
        for (i in 0 until V) {
            if (dist[i][k] == Int.MAX_VALUE) continue
            for (j in 0 until V) {
                if (dist[k][j] == Int.MAX_VALUE) continue
                val throughK = dist[i][k] + dist[k][j]
                if (throughK < dist[i][j]) {
                    dist[i][j] = throughK
                }
            }
        }
    }

    return dist
}

// Обнаружение отрицательных циклов (если dist[i][i] < 0)
fun hasNegativeCycle(dist: Array<IntArray>): Boolean {
    val V = dist.size
    for (i in 0 until V) {
        if (dist[i][i] < 0) return true
    }
    return false
}
```

**Алгоритм Беллмана–Форда (O(V * E)):**
```kotlin
// Находит кратчайшие пути от одной вершины в ориентированном графе,
// поддерживает отрицательные веса и обнаруживает отрицательные циклы, достижимые из source.
// edges: список направленных рёбер Edge(u, v, weight)
data class BFEdge(val from: Int, val to: Int, val weight: Int)

fun bellmanFord(vertices: Int, edges: List<BFEdge>, source: Int): IntArray? {
    val distances = IntArray(vertices) { Int.MAX_VALUE }
    distances[source] = 0

    // Релаксируем все рёбра V-1 раз
    repeat(vertices - 1) {
        var updated = false
        for (edge in edges) {
            val u = edge.from
            val v = edge.to
            val w = edge.weight
            if (distances[u] != Int.MAX_VALUE &&
                distances[u] + w < distances[v]) {
                distances[v] = distances[u] + w
                updated = true
            }
        }
        if (!updated) return distances
    }

    // Дополнительная итерация: проверка на отрицательные циклы
    for (edge in edges) {
        val u = edge.from
        val v = edge.to
        val w = edge.weight
        if (distances[u] != Int.MAX_VALUE &&
            distances[u] + w < distances[v]) {
            return null  // Обнаружен отрицательный цикл
        }
    }

    return distances
}
```

## Answer (EN)

**Advanced Graph Algorithms Theory:**
Advanced graph algorithms primarily solve two categories of problems: shortest paths and minimum spanning trees. The choice of algorithm depends on graph characteristics (directed/undirected, presence of negative weights, density) and problem requirements. See also [[c-algorithms]].

**Main concepts:**
- **Shortest paths**: finding optimal routes between vertices.
- **MST**: connecting all vertices of a connected, undirected, weighted graph with minimum total cost (no cycles).
- **Greedy algorithms**: locally optimal choice at each step (Dijkstra, Kruskal, Prim).
- **Dynamic programming**: solving via subproblems (Floyd–Warshall).

Below are canonical implementations and key ideas.

**Dijkstra's Algorithm (O((V + E) log V) with a priority queue):**
```kotlin
// Finds shortest paths from a single source in a graph with non-negative edge weights
// graph.vertices: number of vertices
// graph.adj[u]: list of edges from u, each Edge(to, weight)
data class Edge(val to: Int, val weight: Int)
data class Node(val vertex: Int, val distance: Int) : Comparable<Node> {
    override fun compareTo(other: Node): Int = compareValues(this.distance, other.distance)
}

fun dijkstra(graph: Graph, source: Int): IntArray {
    val distances = IntArray(graph.vertices) { Int.MAX_VALUE }
    distances[source] = 0

    val priorityQueue = PriorityQueue<Node>()
    priorityQueue.offer(Node(source, 0))
    val visited = BooleanArray(graph.vertices)

    while (priorityQueue.isNotEmpty()) {
        val (u, dist) = priorityQueue.poll()
        if (visited[u]) continue
        visited[u] = true

        // Relaxation: update distances to neighbors
        for (edge in graph.adj[u]) {
            val v = edge.to
            val weight = edge.weight

            if (dist != Int.MAX_VALUE &&
                dist + weight < distances[v]) {
                distances[v] = dist + weight
                priorityQueue.offer(Node(v, distances[v]))
            }
        }
    }

    return distances
}
```

**Kruskal's Algorithm (MST, O(E log E)):**
```kotlin
// Finds a minimum spanning tree of a connected, undirected, weighted graph via edge sorting
// edges: list of edges (u, v, weight)
data class MSTEdge(val from: Int, val to: Int, val weight: Int) : Comparable<MSTEdge> {
    override fun compareTo(other: MSTEdge): Int = compareValues(this.weight, other.weight)
}

class UnionFind(size: Int) {
    private val parent = IntArray(size) { it }
    private val rank = IntArray(size) { 0 }

    fun find(x: Int): Int {
        if (parent[x] != x) {
            parent[x] = find(parent[x])  // Path compression
        }
        return parent[x]
    }

    fun union(x: Int, y: Int): Boolean {
        val rootX = find(x)
        val rootY = find(y)
        if (rootX == rootY) return false

        // Union by rank
        when {
            rank[rootX] < rank[rootY] -> parent[rootX] = rootY
            rank[rootX] > rank[rootY] -> parent[rootY] = rootX
            else -> {
                parent[rootY] = rootX
                rank[rootX]++
            }
        }
        return true
    }
}

fun kruskalMST(vertices: Int, edges: List<MSTEdge>): List<MSTEdge> {
    val mst = mutableListOf<MSTEdge>()
    val uf = UnionFind(vertices)

    // Sort edges by weight
    val sortedEdges = edges.sorted()

    // Greedily add edges that don't create cycles
    for (edge in sortedEdges) {
        if (uf.union(edge.from, edge.to)) {
            mst.add(edge)
            if (mst.size == vertices - 1) break
        }
    }

    return mst
}
```

**Prim's Algorithm (MST, O(E log V) with a priority queue):**
```kotlin
// Grows an MST from a starting vertex in a connected, undirected, weighted graph
// graph.adj[u]: list of edges Edge(to, weight) for an undirected graph
fun primMST(graph: Graph): List<MSTEdge> {
    val mst = mutableListOf<MSTEdge>()
    val visited = BooleanArray(graph.vertices)
    val pq = PriorityQueue<MSTEdge>()

    // Start from vertex 0
    visited[0] = true
    for (edge in graph.adj[0]) {
        pq.offer(MSTEdge(0, edge.to, edge.weight))
    }

    while (pq.isNotEmpty() && mst.size < graph.vertices - 1) {
        val edge = pq.poll()
        val u = edge.from
        val v = edge.to

        // Choose edge that leads to an unvisited vertex
        if (visited[u] && visited[v]) continue

        val next = if (visited[u]) v else u
        mst.add(MSTEdge(u, next, edge.weight))
        visited[next] = true

        // Add edges from the new vertex
        for (nextEdge in graph.adj[next]) {
            val to = nextEdge.to
            if (!visited[to]) {
                pq.offer(MSTEdge(next, to, nextEdge.weight))
            }
        }
    }

    return mst
}
```

**Floyd–Warshall Algorithm (O(V^3)):**
```kotlin
// Finds shortest paths between all pairs of vertices
// graph[i][j]: weight of edge i->j or INF (e.g., Int.MAX_VALUE / 2) if no edge;
// graph[i][i] is typically 0.
fun floydWarshall(graph: Array<IntArray>): Array<IntArray> {
    val V = graph.size
    val dist = Array(V) { i -> graph[i].clone() }

    for (k in 0 until V) {
        for (i in 0 until V) {
            if (dist[i][k] == Int.MAX_VALUE) continue
            for (j in 0 until V) {
                if (dist[k][j] == Int.MAX_VALUE) continue
                val throughK = dist[i][k] + dist[k][j]
                if (throughK < dist[i][j]) {
                    dist[i][j] = throughK
                }
            }
        }
    }

    return dist
}

// Detect negative cycles (if dist[i][i] < 0)
fun hasNegativeCycle(dist: Array<IntArray>): Boolean {
    val V = dist.size
    for (i in 0 until V) {
        if (dist[i][i] < 0) return true
    }
    return false
}
```

**Bellman–Ford Algorithm (O(V * E)):**
```kotlin
// Finds shortest paths from a single source in a directed graph,
// supports negative weights and detects negative-weight cycles reachable from the source.
// edges: list of directed edges Edge(u, v, weight)
data class BFEdge(val from: Int, val to: Int, val weight: Int)

fun bellmanFord(vertices: Int, edges: List<BFEdge>, source: Int): IntArray? {
    val distances = IntArray(vertices) { Int.MAX_VALUE }
    distances[source] = 0

    // Relax all edges V-1 times
    repeat(vertices - 1) {
        var updated = false
        for (edge in edges) {
            val u = edge.from
            val v = edge.to
            val w = edge.weight
            if (distances[u] != Int.MAX_VALUE &&
                distances[u] + w < distances[v]) {
                distances[v] = distances[u] + w
                updated = true
            }
        }
        if (!updated) return distances
    }

    // Extra iteration: check for negative-weight cycles
    for (edge in edges) {
        val u = edge.from
        val v = edge.to
        val w = edge.weight
        if (distances[u] != Int.MAX_VALUE &&
            distances[u] + w < distances[v]) {
            return null  // Negative cycle detected
        }
    }

    return distances
}
```

---

## Дополнительные Вопросы (RU)
- Как выбрать между алгоритмами Дейкстры и Беллмана-Форда?
- Каковы особенности и trade-off'ы между алгоритмами Краскала и Прима для построения MST?
- В каких случаях алгоритм Флойда-Уоршелла предпочтительнее, чем запускать Дейкстру V раз?

## Follow-ups

- How do you choose between Dijkstra and Bellman-Ford?
- What are the trade-offs between Kruskal and Prim for MST?
- When is Floyd-Warshall better than running Dijkstra V times?

## Связанные Вопросы (RU)

### Предварительные (проще)
- [[q-graph-algorithms-bfs-dfs--algorithms--hard]] - Базовые алгоритмы на графах
- [[q-data-structures-overview--algorithms--easy]] - Структуры данных

### Связанные (тот Же уровень)
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - Основы динамического программирования
- [[q-binary-search-trees-bst--algorithms--hard]] - Алгоритмы на деревьях

### Продвинутые (сложнее)
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - Комбинирование DP и графов

## Related Questions

### Prerequisites (Easier)
- [[q-graph-algorithms-bfs-dfs--algorithms--hard]] - Graph basics
- [[q-data-structures-overview--algorithms--easy]] - Data structures

### Related (Same Level)
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - DP concepts
- [[q-binary-search-trees-bst--algorithms--hard]] - Tree algorithms

### Advanced (Harder)
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - Combining DP with graphs

## References
- [[c-algorithms]]
- "https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm"
- "https://en.wikipedia.org/wiki/Minimum_spanning_tree"