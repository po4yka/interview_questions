---
id: algo-004
title: "Advanced Graph Algorithms (Dijkstra, MST, Floyd-Warshall) / Продвинутые алгоритмы на графах"
aliases: ["Advanced Graph Algorithms", "Продвинутые алгоритмы на графах"]
topic: algorithms
subtopics: [graph, minimum-spanning-tree, shortest-path]
question_kind: coding
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-algorithms
related: [c-dijkstra-algorithm, c-mst-algorithms, q-graph-algorithms-bfs-dfs--algorithms--hard]
created: 2025-10-12
updated: 2025-01-25
tags: [algorithms, bellman-ford, difficulty/hard, dijkstra, floyd-warshall, graph, mst, shortest-path]
sources: [https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm, https://en.wikipedia.org/wiki/Minimum_spanning_tree]
date created: Sunday, October 12th 2025, 10:33:05 pm
date modified: Saturday, October 25th 2025, 5:07:35 pm
---

# Вопрос (RU)
> Как работают алгоритмы Дейкстры, MST (Краскал, Прим), Флойда-Уоршелла и Беллмана-Форда?

# Question (EN)
> How do Dijkstra's algorithm, MST (Kruskal, Prim), Floyd-Warshall, and Bellman-Ford work?

---

## Ответ (RU)

**Теория продвинутых алгоритмов на графах:**
Продвинутые алгоритмы на графах решают две основные категории задач: кратчайшие пути и минимальные остовные деревья. Выбор алгоритма зависит от характеристик графа и требований задачи.

**Основные концепции:**
- **Кратчайшие пути**: нахождение оптимальных маршрутов между вершинами
- **MST**: соединение всех вершин с минимальной стоимостью
- **Жадные алгоритмы**: локально оптимальный выбор на каждом шаге
- **Динамическое программирование**: решение через подзадачи

**Алгоритм Дейкстры:**
```kotlin
// Находит кратчайшие пути от одной исходной вершины с неотрицательными весами
data class Edge(val to: Int, val weight: Int)
data class Node(val vertex: Int, val distance: Int) : Comparable<Node> {
    override fun compareTo(other: Node) = distance - other.distance
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

            if (distances[u] != Int.MAX_VALUE &&
                distances[u] + weight < distances[v]) {
                distances[v] = distances[u] + weight
                priorityQueue.offer(Node(v, distances[v]))
            }
        }
    }

    return distances
}
```

**Алгоритм Краскала (MST):**
```kotlin
// Находит минимальное остовное дерево через сортировку рёбер
data class MSTEdge(val from: Int, val to: Int, val weight: Int) : Comparable<MSTEdge> {
    override fun compareTo(other: MSTEdge) = weight - other.weight
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

**Алгоритм Прима (MST):**
```kotlin
// Растит MST от стартовой вершины
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
        if (visited[edge.to]) continue

        mst.add(edge)
        visited[edge.to] = true

        // Добавляем рёбра из новой вершины
        for (nextEdge in graph.adj[edge.to]) {
            if (!visited[nextEdge.to]) {
                pq.offer(MSTEdge(edge.to, nextEdge.to, nextEdge.weight))
            }
        }
    }

    return mst
}
```

**Алгоритм Флойда-Уоршелла:**
```kotlin
// Находит кратчайшие пути между всеми парами вершин
fun floydWarshall(graph: Array<IntArray>): Array<IntArray> {
    val V = graph.size
    val dist = Array(V) { i -> graph[i].clone() }

    // Для каждой промежуточной вершины k
    for (k in 0 until V) {
        // Для каждой пары вершин (i, j)
        for (i in 0 until V) {
            for (j in 0 until V) {
                // Если путь через k короче текущего
                if (dist[i][k] != Int.MAX_VALUE &&
                    dist[k][j] != Int.MAX_VALUE &&
                    dist[i][k] + dist[k][j] < dist[i][j]) {
                    dist[i][j] = dist[i][k] + dist[k][j]
                }
            }
        }
    }

    return dist
}

// Обнаружение отрицательных циклов
fun hasNegativeCycle(dist: Array<IntArray>): Boolean {
    val V = dist.size
    for (i in 0 until V) {
        if (dist[i][i] < 0) return true
    }
    return false
}
```

**Алгоритм Беллмана-Форда:**
```kotlin
// Находит кратчайшие пути с отрицательными весами и обнаруживает циклы
fun bellmanFord(graph: Graph, edges: List<MSTEdge>, source: Int): IntArray? {
    val V = graph.vertices
    val distances = IntArray(V) { Int.MAX_VALUE }
    distances[source] = 0

    // Релаксируем все рёбра V-1 раз
    repeat(V - 1) {
        for (edge in edges) {
            val (u, v, weight) = edge
            if (distances[u] != Int.MAX_VALUE &&
                distances[u] + weight < distances[v]) {
                distances[v] = distances[u] + weight
            }
        }
    }

    // V-я итерация: проверка на отрицательные циклы
    for (edge in edges) {
        val (u, v, weight) = edge
        if (distances[u] != Int.MAX_VALUE &&
            distances[u] + weight < distances[v]) {
            return null  // Обнаружен отрицательный цикл
        }
    }

    return distances
}
```

## Answer (EN)

**Advanced Graph Algorithms Theory:**
Advanced graph algorithms solve two main categories of problems: shortest paths and minimum spanning trees. Algorithm choice depends on graph characteristics and problem requirements.

**Main concepts:**
- **Shortest paths**: finding optimal routes between vertices
- **MST**: connecting all vertices with minimum cost
- **Greedy algorithms**: locally optimal choice at each step
- **Dynamic programming**: solving through subproblems

**Dijkstra's Algorithm:**
```kotlin
// Finds shortest paths from single source with non-negative weights
data class Edge(val to: Int, val weight: Int)
data class Node(val vertex: Int, val distance: Int) : Comparable<Node> {
    override fun compareTo(other: Node) = distance - other.distance
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

            if (distances[u] != Int.MAX_VALUE &&
                distances[u] + weight < distances[v]) {
                distances[v] = distances[u] + weight
                priorityQueue.offer(Node(v, distances[v]))
            }
        }
    }

    return distances
}
```

**Kruskal's Algorithm (MST):**
```kotlin
// Finds minimum spanning tree through edge sorting
data class MSTEdge(val from: Int, val to: Int, val weight: Int) : Comparable<MSTEdge> {
    override fun compareTo(other: MSTEdge) = weight - other.weight
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

**Prim's Algorithm (MST):**
```kotlin
// Grows MST from starting vertex
fun primMST(graph: Graph): List<MSTEdge> {
    val mst = mutableListOf<MSTEdge>()
    val visited = BooleanArray(graph.vertices)
    val pq = PriorityQueue<MSTEdge>()

    // Start with vertex 0
    visited[0] = true
    for (edge in graph.adj[0]) {
        pq.offer(MSTEdge(0, edge.to, edge.weight))
    }

    while (pq.isNotEmpty() && mst.size < graph.vertices - 1) {
        val edge = pq.poll()
        if (visited[edge.to]) continue

        mst.add(edge)
        visited[edge.to] = true

        // Add edges from new vertex
        for (nextEdge in graph.adj[edge.to]) {
            if (!visited[nextEdge.to]) {
                pq.offer(MSTEdge(edge.to, nextEdge.to, nextEdge.weight))
            }
        }
    }

    return mst
}
```

**Floyd-Warshall Algorithm:**
```kotlin
// Finds shortest paths between all pairs of vertices
fun floydWarshall(graph: Array<IntArray>): Array<IntArray> {
    val V = graph.size
    val dist = Array(V) { i -> graph[i].clone() }

    // For each intermediate vertex k
    for (k in 0 until V) {
        // For each pair of vertices (i, j)
        for (i in 0 until V) {
            for (j in 0 until V) {
                // If path through k is shorter than current
                if (dist[i][k] != Int.MAX_VALUE &&
                    dist[k][j] != Int.MAX_VALUE &&
                    dist[i][k] + dist[k][j] < dist[i][j]) {
                    dist[i][j] = dist[i][k] + dist[k][j]
                }
            }
        }
    }

    return dist
}

// Detect negative cycles
fun hasNegativeCycle(dist: Array<IntArray>): Boolean {
    val V = dist.size
    for (i in 0 until V) {
        if (dist[i][i] < 0) return true
    }
    return false
}
```

**Bellman-Ford Algorithm:**
```kotlin
// Finds shortest paths with negative weights and detects cycles
fun bellmanFord(graph: Graph, edges: List<MSTEdge>, source: Int): IntArray? {
    val V = graph.vertices
    val distances = IntArray(V) { Int.MAX_VALUE }
    distances[source] = 0

    // Relax all edges V-1 times
    repeat(V - 1) {
        for (edge in edges) {
            val (u, v, weight) = edge
            if (distances[u] != Int.MAX_VALUE &&
                distances[u] + weight < distances[v]) {
                distances[v] = distances[u] + weight
            }
        }
    }

    // V-th iteration: check for negative cycles
    for (edge in edges) {
        val (u, v, weight) = edge
        if (distances[u] != Int.MAX_VALUE &&
            distances[u] + weight < distances[v]) {
            return null  // Negative cycle detected
        }
    }

    return distances
}
```

---

## Follow-ups

- How do you choose between Dijkstra and Bellman-Ford?
- What are the trade-offs between Kruskal and Prim for MST?
- When is Floyd-Warshall better than running Dijkstra V times?

## Related Questions

### Prerequisites (Easier)
- [[q-graph-algorithms-bfs-dfs--algorithms--hard]] - Graph basics
- [[q-data-structures-overview--algorithms--easy]] - Data structures

### Related (Same Level)
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - DP concepts
- [[q-binary-search-trees-bst--algorithms--hard]] - Tree algorithms

### Advanced (Harder)
- [[q-advanced-graph-algorithms--algorithms--hard]] - Advanced graph topics
- [[q-network-flow-algorithms--algorithms--hard]] - Network flow
