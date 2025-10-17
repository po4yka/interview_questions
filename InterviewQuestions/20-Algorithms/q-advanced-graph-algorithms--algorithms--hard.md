---
id: 20251012-200007
title: "Advanced Graph Algorithms (Dijkstra, MST, Floyd-Warshall) / Продвинутые алгоритмы на графах"
topic: algorithms
difficulty: hard
status: draft
created: 2025-10-12
tags: - algorithms
  - graph
  - dijkstra
  - mst
  - shortest-path
  - floyd-warshall
  - bellman-ford
date_created: 2025-10-12
date_updated: 2025-10-12
moc: moc-algorithms
related_questions:   - q-graph-algorithms-bfs-dfs--algorithms--hard
  - q-dynamic-programming-fundamentals--algorithms--hard
  - q-binary-search-trees-bst--algorithms--hard
slug: advanced-graph-algorithms-algorithms-hard
subtopics:   - graph
  - dijkstra
  - mst
  - shortest-path
  - minimum-spanning-tree
---
# Advanced Graph Algorithms

## English Version

### Problem Statement

Advanced graph algorithms are essential for solving complex shortest path and minimum spanning tree problems. These algorithms are fundamental in network routing, map applications, social networks, and infrastructure optimization.

**The Question:** How do Dijkstra's algorithm, Minimum Spanning Tree (Kruskal's, Prim's), Floyd-Warshall, and Bellman-Ford work? When should you use each one?

## Answer (EN)

**Dijkstra's Algorithm**: Finds the shortest path from a single source in a graph with non-negative edge weights. Time complexity is O((V+E) log V).
**Minimum Spanning Tree (MST)**: Finds a subset of edges that connects all vertices with minimum total weight.
- **Kruskal's Algorithm**: Sorts all edges and adds them to the MST if they don't form a cycle. Time complexity is O(E log E).
- **Prim's Algorithm**: Grows the MST from a starting vertex by adding the cheapest edge to a vertex not yet in the MST. Time complexity is O((V+E) log V).
**Floyd-Warshall Algorithm**: Finds the shortest paths between all pairs of vertices. Time complexity is O(V³).
**Bellman-Ford Algorithm**: Finds the shortest path from a single source, even with negative edge weights, and can detect negative cycles. Time complexity is O(V*E).

## Ответ (RU)

### АЛГОРИТМ ДЕЙКСТРЫ

**Находит кратчайший путь от исходной вершины до всех остальных (при неотрицательных весах).**

#### Базовая реализация с приоритетной очередью

```kotlin
data class Edge(val to: Int, val weight: Int)

data class Node(val vertex: Int, val distance: Int) : Comparable<Node> {
    override fun compareTo(other: Node) = distance - other.distance
}

class Graph(val vertices: Int) {
    val adj = Array(vertices) { mutableListOf<Edge>() }

    fun addEdge(from: Int, to: Int, weight: Int) {
        adj[from].add(Edge(to, weight))
    }
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

        // Ослабление всех ребер из u
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

---

### МИНИМАЛЬНОЕ ОСТОВНОЕ ДЕРЕВО (MST)

**Находит подмножество ребер, которое соединяет все вершины с минимальным общим весом.**

#### Алгоритм Краскала (Union-Find)

```kotlin
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

        if (rootX == rootY) return false  // Уже в одном множестве

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

    // Сортировка ребер по весу
    val sortedEdges = edges.sorted()

    for (edge in sortedEdges) {
        // Добавляем ребро, если оно не создает цикл
        if (uf.union(edge.from, edge.to)) {
            mst.add(edge)

            // MST имеет ровно V-1 ребер
            if (mst.size == vertices - 1) break
        }
    }

    return mst
}
```

---

#### Алгоритм Прима (Жадный + Приоритетная очередь)

```kotlin
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

        if (visited[edge.to]) continue  // Пропускаем, если создает цикл

        // Добавляем ребро в MST
        mst.add(edge)
        visited[edge.to] = true

        // Добавляем все ребра из новой вершины
        for (nextEdge in graph.adj[edge.to]) {
            if (!visited[nextEdge.to]) {
                pq.offer(MSTEdge(edge.to, nextEdge.to, nextEdge.weight))
            }
        }
    }

    return mst
}
```

---

### АЛГОРИТМ ФЛОЙДА-УОРШЕЛЛА

**Находит кратчайшие пути между ВСЕМИ парами вершин.**

```kotlin
fun floydWarshall(graph: Array<IntArray>): Array<IntArray> {
    val V = graph.size
    val dist = Array(V) { i -> graph[i].clone() }

    // Пробуем все промежуточные вершины
    for (k in 0 until V) {
        for (i in 0 until V) {
            for (j in 0 until V) {
                // Если путь через k короче
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
```

---

### АЛГОРИТМ БЕЛЛМАНА-ФОРДА

**Находит кратчайший путь с ОТРИЦАТЕЛЬНЫМИ весами (обнаруживает отрицательные циклы).**

```kotlin
fun bellmanFord(graph: Graph, edges: List<MSTEdge>, source: Int): IntArray? {
    val V = graph.vertices
    val distances = IntArray(V) { Int.MAX_VALUE }
    distances[source] = 0

    // Ослабляем все ребра V-1 раз
    repeat(V - 1) {
        for (edge in edges) {
            val (u, v, weight) = edge

            if (distances[u] != Int.MAX_VALUE &&
                distances[u] + weight < distances[v]) {
                distances[v] = distances[u] + weight
            }
        }
    }

    // Проверка на отрицательные циклы
    for (edge in edges) {
        val (u, v, weight) = edge

        if (distances[u] != Int.MAX_VALUE &&
            distances[u] + weight < distances[v]) {
            return null  // Обнаружен отрицательный цикл!
        }
    }

    return distances
}


---

## Russian Version

### Постановка задачи

Продвинутые алгоритмы на графах необходимы для решения сложных задач кратчайших путей и минимальных остовных деревьев. Эти алгоритмы фундаментальны в сетевой маршрутизации, картографических приложениях, социальных сетях и оптимизации инфраструктуры.

**Вопрос:** Как работают алгоритмы Дейкстры, минимального остовного дерева (Краскала, Прима), Флойда-Уоршелла и Беллмана-Форда? Когда использовать каждый из них?

### Ключевые выводы

1. **Дейкстра** - Кратчайший путь из одной вершины, неотрицательные веса, O((V+E) log V)
2. **Беллман-Форд** - Работает с отрицательными весами, находит отрицательные циклы, O(V*E)
3. **Флойд-Уоршелл** - Кратчайшие пути между всеми парами, O(V³), для малых плотных графов
4. **Краскал (MST)** - На основе Union-Find, O(E log E), хорош для разреженных графов
5. **Прим (MST)** - На основе приоритетной очереди, O((V+E) log V), хорош для плотных графов
6. **Используйте Дейкстру** для большинства задач кратчайшего пути (GPS, маршрутизация)
7. **Используйте Флойда-Уоршелла** когда нужны расстояния между всеми парами вершин
8. **Используйте MST** для проектирования сетей, кластеризации, минимальной стоимости соединений
9. **Приоритетная очередь** критична для эффективных алгоритмов на графах
10. **Восстановление пути** требует отслеживания родительских указателей

### Сравнение алгоритмов

**Алгоритм Дейкстры**: находит кратчайший путь от одной исходной вершины во взвешенном графе с неотрицательными весами ребер. Использует жадный подход с приоритетной очередью. Временная сложность O((V+E) log V) с приоритетной очередью. Не работает с отрицательными весами.

**Минимальное остовное дерево**: находит подмножество ребер, соединяющих все вершины с минимальным общим весом. Краскал сортирует все ребра и добавляет их в MST, если они не создают цикл (Union-Find). Прим растит MST от стартовой вершины, добавляя самое дешевое ребро.

**Флойд-Уоршелл**: находит кратчайшие пути между всеми парами вершин. Использует динамическое программирование. Сложность O(V³). Работает с отрицательными весами (но не циклами). Подходит для плотных графов малого размера.

**Беллман-Форд**: находит кратчайший путь от одной исходной вершины, работает с отрицательными весами и обнаруживает отрицательные циклы. Сложность O(V*E). Медленнее Дейкстры, но более универсален.

### Когда использовать

**Дейкстра**: GPS-навигация, сетевая маршрутизация, поиск пути в играх. Требования: неотрицательные веса, нужен путь от одной вершины.

**MST (Краскал/Прим)**: проектирование сетей, кластеризация данных, минимизация стоимости соединений, построение дорог между городами.

**Флойд-Уоршелл**: когда нужны расстояния между всеми парами вершин, транзитивное замыкание, малые плотные графы.

**Беллман-Форд**: графы с отрицательными весами, обнаружение арбитража в валютных курсах, обнаружение отрицательных циклов.

## Follow-ups

1. How does A* algorithm improve on Dijkstra for pathfinding?
2. What is the difference between Kruskal's and Prim's MST algorithms?
3. How do you detect a negative cycle using Bellman-Ford?
4. When would you use Floyd-Warshall over running Dijkstra V times?
5. How does the priority queue optimization work in Dijkstra?
6. What is the role of Union-Find in Kruskal's algorithm?
7. How do you handle disconnected graphs in MST algorithms?
8. What is the Johnson's algorithm for all-pairs shortest paths?
9. How do you implement bidirectional Dijkstra?
10. What are the trade-offs between adjacency matrix and adjacency list for these algorithms?

---

## Related Questions

### Android Implementation
- [[q-recyclerview-itemdecoration-advanced--android--medium]] - Data Structures
- [[q-recyclerview-diffutil-advanced--recyclerview--medium]] - Data Structures
- [[q-opengl-advanced-rendering--graphics--medium]] - Data Structures
- [[q-recyclerview-itemdecoration-advanced--recyclerview--medium]] - Data Structures
- [[q-compose-canvas-graphics--jetpack-compose--hard]] - Data Structures

### Kotlin Language Features
- [[q-kotlin-collections--kotlin--medium]] - Data Structures

### System Design Concepts
- [[q-message-queues-event-driven--system-design--medium]] - Data Structures
