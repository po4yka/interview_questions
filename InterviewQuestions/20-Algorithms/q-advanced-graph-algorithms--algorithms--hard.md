---
id: 20251012-200007
title: "Advanced Graph Algorithms (Dijkstra, MST, Floyd-Warshall) / Продвинутые алгоритмы на графах"
topic: algorithms
difficulty: hard
status: draft
created: 2025-10-12
tags:
  - algorithms
  - graph
  - dijkstra
  - mst
  - shortest-path
  - floyd-warshall
  - bellman-ford
moc: moc-algorithms
related: [q-graph-algorithms-bfs-dfs--algorithms--hard, q-binary-search-variants--algorithms--medium, q-binary-search-trees-bst--algorithms--hard]
  - q-graph-algorithms-bfs-dfs--algorithms--hard
  - q-dynamic-programming-fundamentals--algorithms--hard
  - q-binary-search-trees-bst--algorithms--hard
subtopics:
  - graph
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

### Обзор продвинутых алгоритмов на графах

Продвинутые алгоритмы на графах решают две основные категории задач:
1. **Задачи кратчайших путей** - нахождение оптимальных маршрутов между вершинами
2. **Задачи минимальных остовных деревьев** - соединение всех вершин с минимальной стоимостью

Выбор правильного алгоритма зависит от характеристик графа и требований задачи.

---

## 1. АЛГОРИТМ ДЕЙКСТРЫ

### Концепция

**Алгоритм Дейкстры** находит кратчайшие пути от одной исходной вершины до всех остальных вершин во взвешенном графе с **неотрицательными весами** рёбер.

### Как работает алгоритм

1. **Инициализация**: расстояние до исходной вершины = 0, до остальных = ∞
2. **Жадный выбор**: всегда выбираем непосещённую вершину с минимальным расстоянием
3. **Релаксация рёбер**: обновляем расстояния до соседей, если нашли более короткий путь
4. **Повторение**: пока не обработаем все вершины

**Ключевая идея**: если мы нашли кратчайший путь до вершины v, то любой более длинный путь до v можно игнорировать.

### Временная и пространственная сложность

- **Временная сложность**: O((V + E) log V) с приоритетной очередью (binary heap)
  - O(V²) с простым массивом (для плотных графов)
  - O(V + E log V) с Fibonacci heap
- **Пространственная сложность**: O(V) для массивов расстояний и посещённых вершин

### Применение

- **GPS навигация** - поиск кратчайшего маршрута на карте
- **Сетевая маршрутизация** - протоколы OSPF (Open Shortest Path First)
- **Игры** - поиск пути для NPC (Non-Player Characters)
- **Социальные сети** - поиск степени разделения между пользователями

### Базовая реализация с приоритетной очередью

```kotlin
// Ребро графа: вершина назначения и вес
data class Edge(val to: Int, val weight: Int)

// Узел для приоритетной очереди: вершина и её текущее расстояние
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
    // Инициализация: расстояния до всех вершин = ∞, кроме исходной
    val distances = IntArray(graph.vertices) { Int.MAX_VALUE }
    distances[source] = 0

    // Приоритетная очередь: всегда извлекаем вершину с минимальным расстоянием
    val priorityQueue = PriorityQueue<Node>()
    priorityQueue.offer(Node(source, 0))

    val visited = BooleanArray(graph.vertices)

    while (priorityQueue.isNotEmpty()) {
        val (u, dist) = priorityQueue.poll()

        // Пропускаем, если вершина уже обработана
        if (visited[u]) continue
        visited[u] = true

        // Релаксация: обновляем расстояния до соседей
        for (edge in graph.adj[u]) {
            val v = edge.to
            val weight = edge.weight

            // Если нашли более короткий путь до v через u
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

### Восстановление пути

Для получения не только расстояния, но и самого пути, необходимо отслеживать предыдущие вершины:

```kotlin
data class DijkstraResult(
    val distances: IntArray,
    val parents: IntArray
)

fun dijkstraWithPath(graph: Graph, source: Int): DijkstraResult {
    val distances = IntArray(graph.vertices) { Int.MAX_VALUE }
    val parents = IntArray(graph.vertices) { -1 }
    distances[source] = 0

    val pq = PriorityQueue<Node>()
    pq.offer(Node(source, 0))
    val visited = BooleanArray(graph.vertices)

    while (pq.isNotEmpty()) {
        val (u, _) = pq.poll()
        if (visited[u]) continue
        visited[u] = true

        for (edge in graph.adj[u]) {
            val v = edge.to
            val newDist = distances[u] + edge.weight

            if (newDist < distances[v]) {
                distances[v] = newDist
                parents[v] = u  // Запоминаем, откуда пришли
                pq.offer(Node(v, newDist))
            }
        }
    }

    return DijkstraResult(distances, parents)
}

// Восстановление пути от source до target
fun reconstructPath(parents: IntArray, target: Int): List<Int> {
    val path = mutableListOf<Int>()
    var current = target

    while (current != -1) {
        path.add(current)
        current = parents[current]
    }

    return path.reversed()  // Разворачиваем путь
}
```

### Преимущества и недостатки

**Преимущества:**
- ✅ Эффективен для графов с неотрицательными весами
- ✅ Находит оптимальное решение (гарантированно кратчайший путь)
- ✅ Хорошо работает на разреженных графах с приоритетной очередью

**Недостатки:**
- ❌ Не работает с отрицательными весами рёбер
- ❌ Вычисляет пути до всех вершин, даже если нужен путь только до одной
- ❌ Неэффективен для очень плотных графов без оптимизаций

---

## 2. МИНИМАЛЬНОЕ ОСТОВНОЕ ДЕРЕВО (MST)

### Концепция

**Минимальное остовное дерево (MST)** — это подмножество рёбер связного взвешенного неориентированного графа, которое:
1. Соединяет все вершины графа
2. Не содержит циклов (является деревом)
3. Имеет минимальную возможную сумму весов рёбер

Для графа с V вершинами MST содержит ровно **V - 1** ребро.

### Два основных алгоритма

1. **Алгоритм Краскала** — сортирует рёбра и добавляет их жадно
2. **Алгоритм Прима** — растит дерево от стартовой вершины

---

## 2.1. АЛГОРИТМ КРАСКАЛА

### Как работает алгоритм

1. **Сортировка**: упорядочиваем все рёбра по возрастанию веса
2. **Инициализация**: каждая вершина — отдельное множество (Union-Find)
3. **Жадный выбор**: берём самое лёгкое ребро, которое не создаёт цикл
4. **Объединение**: добавляем ребро в MST и объединяем множества
5. **Повторение**: пока не добавим V - 1 рёбер

**Ключевая структура данных**: Union-Find (Disjoint Set Union) для эффективной проверки циклов.

### Временная и пространственная сложность

- **Временная сложность**: O(E log E) или O(E log V)
  - Сортировка рёбер: O(E log E)
  - Union-Find операции: почти O(1) с оптимизациями
- **Пространственная сложность**: O(V) для Union-Find структуры

### Применение

- **Проектирование сетей** — минимизация стоимости прокладки кабелей
- **Построение дорог** — соединение городов с минимальными затратами
- **Кластеризация данных** — группировка похожих объектов
- **Аппроксимация задачи коммивояжёра**

### Реализация с Union-Find

```kotlin
// Ребро для MST: начало, конец и вес
data class MSTEdge(val from: Int, val to: Int, val weight: Int) : Comparable<MSTEdge> {
    override fun compareTo(other: MSTEdge) = weight - other.weight
}

// Union-Find (Disjoint Set Union) с оптимизациями
class UnionFind(size: Int) {
    private val parent = IntArray(size) { it }  // Каждая вершина — свой родитель
    private val rank = IntArray(size) { 0 }     // Ранг для балансировки

    // Найти корень множества (с сжатием пути)
    fun find(x: Int): Int {
        if (parent[x] != x) {
            parent[x] = find(parent[x])  // Сжатие пути: присоединяем к корню
        }
        return parent[x]
    }

    // Объединить два множества (возвращает false, если уже в одном)
    fun union(x: Int, y: Int): Boolean {
        val rootX = find(x)
        val rootY = find(y)

        if (rootX == rootY) return false  // Уже в одном множестве — создаст цикл

        // Объединение по рангу: меньшее дерево под большее
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

    // Шаг 1: Сортируем рёбра по возрастанию веса
    val sortedEdges = edges.sorted()

    // Шаг 2: Жадно добавляем рёбра, которые не создают циклы
    for (edge in sortedEdges) {
        // Если вершины в разных множествах — добавляем ребро
        if (uf.union(edge.from, edge.to)) {
            mst.add(edge)

            // MST содержит ровно V-1 рёбер, можно остановиться
            if (mst.size == vertices - 1) break
        }
    }

    return mst
}

// Вычисление общего веса MST
fun calculateMSTWeight(mst: List<MSTEdge>): Int {
    return mst.sumOf { it.weight }
}
```

### Преимущества Краскала

- ✅ Простая реализация
- ✅ Эффективен для разреженных графов (мало рёбер)
- ✅ Естественно работает с списком рёбер
- ✅ Легко распараллеливается

---

## 2.2. АЛГОРИТМ ПРИМА

### Как работает алгоритм

1. **Инициализация**: начинаем с произвольной вершины
2. **Жадный выбор**: выбираем самое лёгкое ребро, соединяющее дерево с новой вершиной
3. **Расширение**: добавляем выбранную вершину в дерево
4. **Обновление**: добавляем все рёбра новой вершины в рассмотрение
5. **Повторение**: пока не включим все вершины

**Отличие от Краскала**: Прим растит одно связное дерево, Краскал может работать с несвязными компонентами.

### Временная и пространственная сложность

- **Временная сложность**: O((V + E) log V) с binary heap
  - O(E log V) для связных графов (E ≥ V - 1)
  - O(V²) с простым массивом
- **Пространственная сложность**: O(V + E)

### Когда использовать Прима вместо Краскала

- ✅ Плотные графы (много рёбер): E близко к V²
- ✅ Граф представлен матрицей смежности
- ✅ Нужно строить MST инкрементально

### Реализация с приоритетной очередью

```kotlin
fun primMST(graph: Graph): List<MSTEdge> {
    val mst = mutableListOf<MSTEdge>()
    val visited = BooleanArray(graph.vertices)
    val pq = PriorityQueue<MSTEdge>()

    // Начинаем с вершины 0 (можно с любой)
    visited[0] = true
    for (edge in graph.adj[0]) {
        pq.offer(MSTEdge(0, edge.to, edge.weight))
    }

    while (pq.isNotEmpty() && mst.size < graph.vertices - 1) {
        val edge = pq.poll()

        // Пропускаем, если вершина уже в дереве (создаст цикл)
        if (visited[edge.to]) continue

        // Добавляем ребро в MST
        mst.add(edge)
        visited[edge.to] = true

        // Добавляем все рёбра из новой вершины в приоритетную очередь
        for (nextEdge in graph.adj[edge.to]) {
            if (!visited[nextEdge.to]) {
                pq.offer(MSTEdge(edge.to, nextEdge.to, nextEdge.weight))
            }
        }
    }

    return mst
}
```

### Сравнение: Краскал vs Прим

| Критерий | Краскал | Прим |
|----------|---------|------|
| **Сложность** | O(E log E) | O((V+E) log V) |
| **Разреженные графы** | ✅ Лучше | ❌ Хуже |
| **Плотные графы** | ❌ Хуже | ✅ Лучше |
| **Структура данных** | Union-Find | Priority Queue |
| **Представление** | Список рёбер | Список смежности |
| **Подход** | Глобальный выбор | Локальное расширение |

---

## 3. АЛГОРИТМ ФЛОЙДА-УОРШЕЛЛА

### Концепция

**Алгоритм Флойда-Уоршелла** находит кратчайшие пути между **всеми парами вершин** во взвешенном графе. Работает с отрицательными весами, но не с отрицательными циклами.

### Как работает алгоритм

Использует **динамическое программирование** с тройным вложенным циклом:

1. **Инициализация**: матрица расстояний = веса рёбер (∞ для несуществующих)
2. **Итерация по промежуточным вершинам k**: для каждой вершины k проверяем
3. **Проверка улучшения**: может ли путь через k быть короче прямого пути
4. **Обновление**: dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

**Ключевая идея**: если кратчайший путь от i до j проходит через k, то он состоит из кратчайших путей i→k и k→j.

### Временная и пространственная сложность

- **Временная сложность**: O(V³) — три вложенных цикла
- **Пространственная сложность**: O(V²) — матрица расстояний

### Применение

- **Транзитивное замыкание** — проверка достижимости между всеми парами
- **Центр графа** — поиск вершины с минимальным максимальным расстоянием
- **Маршрутизация** — таблицы маршрутов для всех узлов сети
- **Малые плотные графы** — когда V небольшое (< 400-500 вершин)

### Реализация

```kotlin
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
    // Если расстояние от вершины до себя отрицательное — есть цикл
    for (i in 0 until V) {
        if (dist[i][i] < 0) return true
    }
    return false
}

// Восстановление пути между всеми парами
fun floydWarshallWithPath(graph: Array<IntArray>): Pair<Array<IntArray>, Array<IntArray>> {
    val V = graph.size
    val dist = Array(V) { i -> graph[i].clone() }
    val next = Array(V) { i -> IntArray(V) { j -> if (graph[i][j] != Int.MAX_VALUE) j else -1 } }

    for (k in 0 until V) {
        for (i in 0 until V) {
            for (j in 0 until V) {
                if (dist[i][k] != Int.MAX_VALUE &&
                    dist[k][j] != Int.MAX_VALUE &&
                    dist[i][k] + dist[k][j] < dist[i][j]) {
                    dist[i][j] = dist[i][k] + dist[k][j]
                    next[i][j] = next[i][k]  // Следующая вершина на пути
                }
            }
        }
    }

    return dist to next
}

// Восстановление конкретного пути
fun getPath(next: Array<IntArray>, u: Int, v: Int): List<Int> {
    if (next[u][v] == -1) return emptyList()  // Пути нет

    val path = mutableListOf(u)
    var current = u

    while (current != v) {
        current = next[current][v]
        path.add(current)
    }

    return path
}
```

### Преимущества и недостатки

**Преимущества:**
- ✅ Находит пути между всеми парами одновременно
- ✅ Простая реализация — всего три цикла
- ✅ Работает с отрицательными весами
- ✅ Может обнаружить отрицательные циклы

**Недостатки:**
- ❌ O(V³) — медленно для больших графов
- ❌ O(V²) памяти — не подходит для огромных разреженных графов
- ❌ Вычисляет все пути, даже если нужна одна пара

---

## 4. АЛГОРИТМ БЕЛЛМАНА-ФОРДА

### Концепция

**Алгоритм Беллмана-Форда** находит кратчайшие пути от одной исходной вершины до всех остальных, **даже при наличии отрицательных весов рёбер**. Также может обнаружить отрицательные циклы.

### Как работает алгоритм

1. **Инициализация**: расстояние до источника = 0, до остальных = ∞
2. **Релаксация V-1 раз**: для каждого ребра (u, v) пытаемся улучшить расстояние до v
3. **Проверка циклов**: если можем ещё улучшить — значит есть отрицательный цикл

**Почему V-1 итераций?** Кратчайший путь в графе без циклов содержит максимум V-1 ребро.

### Временная и пространственная сложность

- **Временная сложность**: O(V × E)
  - V-1 итераций по всем E рёбрам
  - Медленнее Дейкстры, но работает с отрицательными весами
- **Пространственная сложность**: O(V)

### Применение

- **Арбитраж валют** — обнаружение возможности получения прибыли через обмен валют
- **Графы с отрицательными весами** — когда Дейкстра не применим
- **Обнаружение отрицательных циклов** — поиск бесконечного улучшения
- **Системы с затратами и доходами** — где рёбра могут уменьшать стоимость

### Реализация

```kotlin
fun bellmanFord(graph: Graph, edges: List<MSTEdge>, source: Int): IntArray? {
    val V = graph.vertices
    val distances = IntArray(V) { Int.MAX_VALUE }
    distances[source] = 0

    // Релаксируем все рёбра V-1 раз
    repeat(V - 1) {
        for (edge in edges) {
            val (u, v, weight) = edge

            // Если нашли более короткий путь до v через u
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
            return null  // Обнаружен отрицательный цикл!
        }
    }

    return distances
}

// Версия с восстановлением пути
data class BellmanFordResult(
    val distances: IntArray,
    val parents: IntArray,
    val hasNegativeCycle: Boolean
)

fun bellmanFordWithPath(graph: Graph, edges: List<MSTEdge>, source: Int): BellmanFordResult {
    val V = graph.vertices
    val distances = IntArray(V) { Int.MAX_VALUE }
    val parents = IntArray(V) { -1 }
    distances[source] = 0

    // V-1 релаксаций
    repeat(V - 1) {
        for (edge in edges) {
            val (u, v, weight) = edge

            if (distances[u] != Int.MAX_VALUE &&
                distances[u] + weight < distances[v]) {
                distances[v] = distances[u] + weight
                parents[v] = u
            }
        }
    }

    // Проверка на отрицательные циклы
    var hasNegativeCycle = false
    for (edge in edges) {
        val (u, v, weight) = edge

        if (distances[u] != Int.MAX_VALUE &&
            distances[u] + weight < distances[v]) {
            hasNegativeCycle = true
            break
        }
    }

    return BellmanFordResult(distances, parents, hasNegativeCycle)
}

// Поиск вершин, затронутых отрицательным циклом
fun findNegativeCycleAffectedVertices(graph: Graph, edges: List<MSTEdge>, source: Int): Set<Int> {
    val V = graph.vertices
    val distances = IntArray(V) { Int.MAX_VALUE }
    distances[source] = 0

    repeat(V - 1) {
        for (edge in edges) {
            val (u, v, weight) = edge
            if (distances[u] != Int.MAX_VALUE && distances[u] + weight < distances[v]) {
                distances[v] = distances[u] + weight
            }
        }
    }

    // Находим вершины, которые можно ещё улучшить
    val affected = mutableSetOf<Int>()
    repeat(V) {
        for (edge in edges) {
            val (u, v, weight) = edge
            if (distances[u] != Int.MAX_VALUE && distances[u] + weight < distances[v]) {
                distances[v] = distances[u] + weight
                affected.add(v)
            }
        }
    }

    return affected
}
```

### Преимущества и недостатки

**Преимущества:**
- ✅ Работает с отрицательными весами рёбер
- ✅ Обнаруживает отрицательные циклы
- ✅ Простая реализация
- ✅ Может найти вершины, затронутые отрицательными циклами

**Недостатки:**
- ❌ O(V × E) — медленнее Дейкстры
- ❌ Не подходит для плотных графов (E близко к V²)
- ❌ Если есть отрицательный цикл, расстояния не определены

---

## 5. АЛГОРИТМ A* (A-STAR)

### Концепция

**Алгоритм A*** — это улучшенная версия Дейкстры, которая использует **эвристическую функцию** для направленного поиска к целевой вершине. Это делает его значительно быстрее для задач поиска пути.

### Как работает алгоритм

Использует функцию оценки: **f(n) = g(n) + h(n)**, где:
- **g(n)** — фактическая стоимость пути от начала до n (как в Дейкстре)
- **h(n)** — эвристическая оценка стоимости от n до цели
- **f(n)** — полная оценочная стоимость пути через n

**Ключевое условие**: эвристика должна быть **допустимой** (не переоценивать реальную стоимость).

### Популярные эвристики

```kotlin
// Манхэттенское расстояние (для сетки с движением по 4 направлениям)
fun manhattanDistance(x1: Int, y1: Int, x2: Int, y2: Int): Int {
    return abs(x1 - x2) + abs(y1 - y2)
}

// Евклидово расстояние (для движения в любом направлении)
fun euclideanDistance(x1: Int, y1: Int, x2: Int, y2: Int): Double {
    return sqrt((x1 - x2).toDouble().pow(2) + (y1 - y2).toDouble().pow(2))
}

// Диагональное расстояние (для движения по 8 направлениям)
fun diagonalDistance(x1: Int, y1: Int, x2: Int, y2: Int): Double {
    val dx = abs(x1 - x2)
    val dy = abs(y1 - y2)
    return (dx + dy) + (sqrt(2.0) - 2) * min(dx, dy)
}
```

### Реализация A*

```kotlin
data class AStarNode(
    val vertex: Int,
    val g: Int,  // Стоимость от начала
    val h: Int,  // Эвристическая оценка до цели
    val f: Int = g + h  // Полная оценка
) : Comparable<AStarNode> {
    override fun compareTo(other: AStarNode) = f - other.f
}

fun aStarSearch(
    graph: Graph,
    start: Int,
    goal: Int,
    heuristic: (Int) -> Int  // Функция эвристики
): List<Int>? {
    val openSet = PriorityQueue<AStarNode>()
    val closedSet = mutableSetOf<Int>()
    val gScore = IntArray(graph.vertices) { Int.MAX_VALUE }
    val parents = IntArray(graph.vertices) { -1 }

    gScore[start] = 0
    openSet.offer(AStarNode(start, 0, heuristic(start)))

    while (openSet.isNotEmpty()) {
        val current = openSet.poll()

        // Достигли цели
        if (current.vertex == goal) {
            return reconstructPath(parents, goal)
        }

        // Пропускаем, если уже обработали
        if (current.vertex in closedSet) continue
        closedSet.add(current.vertex)

        // Проверяем соседей
        for (edge in graph.adj[current.vertex]) {
            val neighbor = edge.to
            if (neighbor in closedSet) continue

            val tentativeG = gScore[current.vertex] + edge.weight

            // Если нашли лучший путь
            if (tentativeG < gScore[neighbor]) {
                gScore[neighbor] = tentativeG
                parents[neighbor] = current.vertex
                openSet.offer(AStarNode(neighbor, tentativeG, heuristic(neighbor)))
            }
        }
    }

    return null  // Путь не найден
}
```

### Применение

- **Видеоигры** — поиск пути для персонажей (навигация NPC)
- **GPS навигация** — быстрый поиск маршрута
- **Робототехника** — планирование траектории движения
- **Головоломки** — решение 15-puzzle, судоку

### Сравнение: Дейкстра vs A*

| Критерий | Дейкстра | A* |
|----------|----------|-----|
| **Скорость** | Медленнее | Быстрее |
| **Эвристика** | Не использует | Требуется |
| **Исследование** | Равномерное во все стороны | Направленное к цели |
| **Гарантия оптимальности** | Всегда | Если эвристика допустима |
| **Применение** | Все кратчайшие пути | Путь к конкретной цели |

---

## 6. ТОПОЛОГИЧЕСКАЯ СОРТИРОВКА

### Концепция

**Топологическая сортировка** — это линейное упорядочивание вершин **направленного ациклического графа (DAG)**, при котором для каждого ребра (u, v) вершина u идёт раньше v.

**Важно**: топологическая сортировка возможна только для DAG (графов без циклов).

### Применение

- **Планирование задач** — определение порядка выполнения зависимых задач
- **Компиляция** — порядок компиляции модулей с зависимостями
- **Системы сборки** — Gradle, Maven, Make
- **Разрешение зависимостей** — пакетные менеджеры (npm, pip)

### Метод 1: DFS (Depth-First Search)

```kotlin
fun topologicalSortDFS(graph: Graph): List<Int>? {
    val visited = BooleanArray(graph.vertices)
    val stack = mutableListOf<Int>()
    val inRecursion = BooleanArray(graph.vertices)

    fun dfs(v: Int): Boolean {
        visited[v] = true
        inRecursion[v] = true

        for (edge in graph.adj[v]) {
            val neighbor = edge.to

            // Обнаружен цикл
            if (inRecursion[neighbor]) return false

            if (!visited[neighbor] && !dfs(neighbor)) {
                return false
            }
        }

        inRecursion[v] = false
        stack.add(v)  // Добавляем после обработки всех потомков
        return true
    }

    // Запускаем DFS от каждой непосещённой вершины
    for (v in 0 until graph.vertices) {
        if (!visited[v]) {
            if (!dfs(v)) return null  // Есть цикл
        }
    }

    return stack.reversed()  // Разворачиваем стек
}
```

### Метод 2: Алгоритм Кана (BFS)

```kotlin
fun topologicalSortKahn(graph: Graph): List<Int>? {
    // Подсчитываем входящие рёбра для каждой вершины
    val inDegree = IntArray(graph.vertices)
    for (v in 0 until graph.vertices) {
        for (edge in graph.adj[v]) {
            inDegree[edge.to]++
        }
    }

    // Очередь вершин без входящих рёбер
    val queue = LinkedList<Int>()
    for (v in 0 until graph.vertices) {
        if (inDegree[v] == 0) {
            queue.offer(v)
        }
    }

    val result = mutableListOf<Int>()

    while (queue.isNotEmpty()) {
        val v = queue.poll()
        result.add(v)

        // Удаляем исходящие рёбра
        for (edge in graph.adj[v]) {
            inDegree[edge.to]--

            // Если у вершины больше нет входящих рёбер
            if (inDegree[edge.to] == 0) {
                queue.offer(edge.to)
            }
        }
    }

    // Если не все вершины обработаны — есть цикл
    return if (result.size == graph.vertices) result else null
}
```

### Временная и пространственная сложность

- **Временная сложность**: O(V + E) для обоих методов
- **Пространственная сложность**: O(V)

### Сравнение методов

| Метод | Преимущества | Недостатки |
|-------|--------------|------------|
| **DFS** | Проще понять, естественная рекурсия | Требует стек вызовов |
| **Kahn (BFS)** | Итеративный, легко найти все начальные вершины | Больше кода |

---

## 7. СРАВНИТЕЛЬНАЯ ТАБЛИЦА АЛГОРИТМОВ

### Алгоритмы кратчайших путей

| Алгоритм | Сложность | Отриц. веса | Все пары | Применение |
|----------|-----------|-------------|----------|------------|
| **Дейкстра** | O((V+E) log V) | ❌ | ❌ | GPS, маршрутизация |
| **Беллман-Форд** | O(V×E) | ✅ | ❌ | Арбитраж валют |
| **Флойд-Уоршелл** | O(V³) | ✅ | ✅ | Малые плотные графы |
| **A*** | O((V+E) log V) | ❌ | ❌ | Видеоигры, быстрый поиск |

### Когда использовать каждый алгоритм

**Используйте Дейкстру:**
- Все веса неотрицательные
- Нужны пути от одной вершины
- Граф достаточно большой
- Требуется высокая производительность

**Используйте Беллман-Форд:**
- Есть отрицательные веса
- Нужно обнаружить отрицательные циклы
- Граф разреженный
- Важна простота реализации

**Используйте Флойд-Уоршелла:**
- Нужны расстояния между всеми парами
- Граф малый (V < 400-500)
- Граф плотный (много рёбер)
- Нужна матрица смежности

**Используйте A*:**
- Известна целевая вершина
- Есть хорошая эвристика
- Нужна максимальная скорость
- Реал-тайм приложения (игры)

**Используйте MST (Краскал/Прим):**
- Нужно соединить все вершины минимально
- Проектирование сетей
- Кластеризация
- Аппроксимация TSP

**Используйте топологическую сортировку:**
- DAG (направленный ациклический граф)
- Планирование задач
- Разрешение зависимостей
- Системы сборки

---

## 8. ПРАКТИЧЕСКИЕ СОВЕТЫ И ОПТИМИЗАЦИИ

### Оптимизации Дейкстры

1. **Bidirectional Search** — поиск одновременно от начала и конца
2. **Early termination** — останавливаемся при достижении целевой вершины
3. **Fibonacci Heap** — улучшает сложность до O(E + V log V)

### Оптимизации A*

1. **Jump Point Search** — пропускаем симметричные пути на сетке
2. **Weighted A*** — жертвуем оптимальностью ради скорости
3. **Hierachical A*** — многоуровневая навигация

### Частые ошибки

1. **Использование Дейкстры с отрицательными весами** — даст неверный результат
2. **Забыть проверку на посещённые вершины** — бесконечный цикл
3. **Неправильная эвристика в A*** — неоптимальный путь
4. **Топологическая сортировка графа с циклами** — бесконечный цикл
5. **Переполнение Int.MAX_VALUE** — использовать Long или проверять

### Выбор структуры данных

```kotlin
// Разреженный граф (мало рёбер): список смежности
class SparseGraph(val vertices: Int) {
    val adj = Array(vertices) { mutableListOf<Edge>() }
}

// Плотный граф (много рёбер): матрица смежности
class DenseGraph(val vertices: Int) {
    val matrix = Array(vertices) { IntArray(vertices) { Int.MAX_VALUE } }
}

// Выбор зависит от E:
// Если E близко к V²: используйте матрицу
// Если E близко к V: используйте список
```

---

## 9. ПРИМЕРЫ ЗАДАЧ

### Задача 1: Поиск кратчайшего пути в городе

**Условие**: Дан граф дорог между перекрёстками с временем проезда. Найти кратчайший маршрут от дома до работы.

**Решение**: Используем алгоритм Дейкстры

```kotlin
fun shortestPathInCity(
    intersections: Int,
    roads: List<Triple<Int, Int, Int>>,  // from, to, time
    home: Int,
    work: Int
): Int {
    val graph = Graph(intersections)
    roads.forEach { (from, to, time) ->
        graph.addEdge(from, to, time)
        graph.addEdge(to, from, time)  // Двусторонняя дорога
    }

    val result = dijkstraWithPath(graph, home)
    return result.distances[work]
}
```

### Задача 2: Network Design Problem

**Условие**: Соединить N офисов оптоволоконным кабелем с минимальной стоимостью.

**Решение**: Используем алгоритм Краскала для MST

```kotlin
fun minCostToConnectOffices(
    offices: Int,
    connections: List<Triple<Int, Int, Int>>  // office1, office2, cost
): Int {
    val edges = connections.map { (from, to, cost) ->
        MSTEdge(from, to, cost)
    }

    val mst = kruskalMST(offices, edges)
    return calculateMSTWeight(mst)
}
```

### Задача 3: Currency Arbitrage

**Условие**: Найти возможность арбитража в обмене валют (получить прибыль через цикл обменов).

**Решение**: Используем алгоритм Беллмана-Форда с логарифмами

```kotlin
fun findArbitrage(
    currencies: Int,
    exchangeRates: Array<DoubleArray>  // rates[i][j] = курс i -> j
): Boolean {
    // Преобразуем в граф с весами: -log(rate)
    val edges = mutableListOf<MSTEdge>()
    for (i in 0 until currencies) {
        for (j in 0 until currencies) {
            if (i != j && exchangeRates[i][j] > 0) {
                val weight = (-ln(exchangeRates[i][j]) * 1000).toInt()
                edges.add(MSTEdge(i, j, weight))
            }
        }
    }

    val graph = Graph(currencies)
    val result = bellmanFord(graph, edges, 0)
    return result == null  // null означает отрицательный цикл (арбитраж!)
}
```

### Задача 4: Task Scheduling

**Условие**: Дан список задач с зависимостями. В каком порядке их выполнять?

**Решение**: Используем топологическую сортировку

```kotlin
fun scheduleTasksWithDependencies(
    tasks: Int,
    dependencies: List<Pair<Int, Int>>  // (task, dependsOn)
): List<Int>? {
    val graph = Graph(tasks)
    dependencies.forEach { (task, dependsOn) ->
        graph.addEdge(dependsOn, task, 1)  // dependsOn должен быть раньше task
    }

    return topologicalSortKahn(graph)
}

// Пример использования
fun main() {
    // Задачи: 0=Дизайн, 1=Код, 2=Тесты, 3=Деплой
    val dependencies = listOf(
        1 to 0,  // Код зависит от Дизайна
        2 to 1,  // Тесты зависят от Кода
        3 to 2   // Деплой зависит от Тестов
    )

    val order = scheduleTasksWithDependencies(4, dependencies)
    println("Порядок выполнения: $order")  // [0, 1, 2, 3]
}
```

---

## 10. КЛЮЧЕВЫЕ ВЫВОДЫ

### Краткая шпаргалка

1. **Дейкстра** → Кратчайший путь от одной вершины, неотрицательные веса, O((V+E) log V)
2. **A*** → Улучшенный Дейкстра с эвристикой, быстрее для конкретной цели
3. **Беллман-Форд** → Работает с отрицательными весами, находит циклы, O(V×E)
4. **Флойд-Уоршелл** → Все пары вершин, O(V³), малые плотные графы
5. **Краскал (MST)** → Union-Find, O(E log E), разреженные графы
6. **Прим (MST)** → Priority Queue, O((V+E) log V), плотные графы
7. **Топологическая сортировка** → Порядок в DAG, O(V+E), планирование задач

### Дерево принятия решений

```
Нужен кратчайший путь?
├─ Да → Есть отрицательные веса?
│   ├─ Да → Беллман-Форд
│   └─ Нет → Известна цель?
│       ├─ Да → A* (с хорошей эвристикой)
│       └─ Нет → Дейкстра
│
└─ Нет → Нужно соединить все вершины минимально?
    ├─ Да → MST (Краскал для разреженных, Прим для плотных)
    └─ Нет → Нужен порядок выполнения?
        ├─ Да → Топологическая сортировка (если DAG)
        └─ Нет → Нужны расстояния между всеми парами?
            └─ Да → Флойд-Уоршелл (если граф небольшой)
```

### Сложность алгоритмов (сводная таблица)

| Алгоритм | Время | Память | Отриц. веса | Все пары |
|----------|-------|--------|-------------|----------|
| Дейкстра | O((V+E) log V) | O(V) | ❌ | ❌ |
| A* | O((V+E) log V) | O(V) | ❌ | ❌ |
| Беллман-Форд | O(V×E) | O(V) | ✅ | ❌ |
| Флойд-Уоршелл | O(V³) | O(V²) | ✅ | ✅ |
| Краскал | O(E log E) | O(V) | N/A | N/A |
| Прим | O((V+E) log V) | O(V+E) | N/A | N/A |
| Топ. сортировка | O(V+E) | O(V) | N/A | N/A |

### Практические советы для собеседований

1. **Уточните требования**: отрицательные веса? все пары? конкретная цель?
2. **Начните с простого**: предложите базовый алгоритм, потом оптимизируйте
3. **Обсудите trade-offs**: время vs память, простота vs производительность
4. **Проверьте граничные случаи**: пустой граф, несвязный граф, циклы
5. **Упомяните оптимизации**: bidirectional search, early termination, лучшие структуры данных

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
