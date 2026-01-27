---
id: q-shortest-path-algorithms
title: Shortest Path Algorithms / Алгоритмы кратчайших путей
aliases:
- Shortest Path
- Кратчайший путь
- Dijkstra
- Bellman-Ford
- Floyd-Warshall
topic: algorithms
subtopics:
- graphs
- dynamic-programming
- greedy
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
- q-graph-algorithms-bfs-dfs--algorithms--hard
- q-advanced-graph-algorithms--algorithms--hard
created: 2025-01-26
updated: 2025-01-26
tags:
- algorithms
- graphs
- shortest-path
- dijkstra
- bellman-ford
- floyd-warshall
- difficulty/hard
sources:
- https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
- https://en.wikipedia.org/wiki/Bellman%E2%80%93Ford_algorithm
- https://en.wikipedia.org/wiki/Floyd%E2%80%93Warshall_algorithm
anki_cards:
- slug: q-shortest-path-algorithms-0-en
  language: en
  anki_id: 1769404213765
  synced_at: '2026-01-26T09:10:14.539424'
- slug: q-shortest-path-algorithms-0-ru
  language: ru
  anki_id: 1769404213790
  synced_at: '2026-01-26T09:10:14.540503'
---
# Question (EN)
> Explain the main shortest path algorithms: Dijkstra, Bellman-Ford, and Floyd-Warshall. When should you use each?

# Vopros (RU)
> Объясните основные алгоритмы поиска кратчайшего пути: Дейкстры, Беллмана-Форда и Флойда-Уоршелла. Когда следует использовать каждый?

---

## Answer (EN)

**Shortest Path Algorithms Overview:**
Shortest path problems find the minimum-weight path between vertices in a weighted graph. The choice of algorithm depends on: (1) single-source vs all-pairs, (2) presence of negative weights, and (3) graph density. See also [[c-algorithms]].

Key concepts:
- **Relaxation**: Update distance if a shorter path is found: `if dist[u] + weight(u,v) < dist[v]`
- **Single-source**: Find shortest paths from one vertex to all others
- **All-pairs**: Find shortest paths between all vertex pairs

---

### 1. Dijkstra's Algorithm

**Purpose**: Single-source shortest path for graphs with **non-negative** weights.

**Key idea**: Greedily select the unvisited vertex with the smallest known distance.

**Time complexity**:
- With binary heap: **O((V + E) log V)**
- With Fibonacci heap: O(E + V log V)
- With array (no heap): O(V^2) - better for dense graphs

**Space complexity**: O(V)

```kotlin
// Dijkstra's Algorithm with Priority Queue
data class Edge(val to: Int, val weight: Int)

fun dijkstra(graph: List<List<Edge>>, source: Int): IntArray {
    val n = graph.size
    val dist = IntArray(n) { Int.MAX_VALUE }
    dist[source] = 0

    // Min-heap: Pair(distance, vertex)
    val pq = PriorityQueue<Pair<Int, Int>>(compareBy { it.first })
    pq.add(0 to source)

    while (pq.isNotEmpty()) {
        val (d, u) = pq.poll()

        // Skip if we already found a better path
        if (d > dist[u]) continue

        for (edge in graph[u]) {
            val newDist = dist[u] + edge.weight
            if (newDist < dist[edge.to]) {
                dist[edge.to] = newDist
                pq.add(newDist to edge.to)
            }
        }
    }

    return dist
}
```

**When to use**:
- Non-negative edge weights only
- Need single-source shortest paths
- Most common choice for road networks, GPS navigation

**Limitations**:
- Fails with negative weights (greedy assumption breaks)
- Cannot detect negative cycles

---

### 2. Bellman-Ford Algorithm

**Purpose**: Single-source shortest path that **handles negative weights** and **detects negative cycles**.

**Key idea**: Relax all edges V-1 times. If any edge can still be relaxed after V-1 iterations, a negative cycle exists.

**Time complexity**: **O(V * E)**

**Space complexity**: O(V)

```kotlin
// Bellman-Ford Algorithm
data class WeightedEdge(val from: Int, val to: Int, val weight: Int)

fun bellmanFord(
    vertices: Int,
    edges: List<WeightedEdge>,
    source: Int
): Pair<IntArray, Boolean> {
    val dist = IntArray(vertices) { Int.MAX_VALUE }
    dist[source] = 0

    // Relax all edges V-1 times
    repeat(vertices - 1) {
        for (edge in edges) {
            if (dist[edge.from] != Int.MAX_VALUE) {
                val newDist = dist[edge.from] + edge.weight
                if (newDist < dist[edge.to]) {
                    dist[edge.to] = newDist
                }
            }
        }
    }

    // Check for negative cycles (one more iteration)
    var hasNegativeCycle = false
    for (edge in edges) {
        if (dist[edge.from] != Int.MAX_VALUE &&
            dist[edge.from] + edge.weight < dist[edge.to]) {
            hasNegativeCycle = true
            break
        }
    }

    return dist to hasNegativeCycle
}
```

**When to use**:
- Graph may have negative edge weights
- Need to detect negative cycles
- Currency arbitrage detection
- Network routing with variable costs

**Optimization**: SPFA (Shortest Path Faster Algorithm) - uses a queue to avoid unnecessary relaxations; average case O(E), worst case O(V*E).

---

### 3. Floyd-Warshall Algorithm

**Purpose**: **All-pairs** shortest paths using dynamic programming.

**Key idea**: For each intermediate vertex k, check if path i -> k -> j is shorter than current i -> j.

**Time complexity**: **O(V^3)**

**Space complexity**: O(V^2)

```kotlin
// Floyd-Warshall Algorithm
fun floydWarshall(graph: Array<IntArray>): Array<IntArray> {
    val n = graph.size
    val dist = Array(n) { i -> graph[i].copyOf() }

    // k = intermediate vertex
    for (k in 0 until n) {
        for (i in 0 until n) {
            for (j in 0 until n) {
                if (dist[i][k] != Int.MAX_VALUE &&
                    dist[k][j] != Int.MAX_VALUE) {
                    val through = dist[i][k] + dist[k][j]
                    if (through < dist[i][j]) {
                        dist[i][j] = through
                    }
                }
            }
        }
    }

    return dist
}

// Detect negative cycle: check if dist[i][i] < 0 for any i
fun hasNegativeCycle(dist: Array<IntArray>): Boolean {
    return dist.indices.any { dist[it][it] < 0 }
}
```

**When to use**:
- Need all-pairs shortest paths
- Dense graphs (E close to V^2)
- Graph is small (V <= 400-500)
- Transitive closure problems

**Path reconstruction**:
```kotlin
// Track predecessors for path reconstruction
val next = Array(n) { i -> IntArray(n) { j -> if (graph[i][j] != INF) j else -1 } }

// Update in main loop:
if (through < dist[i][j]) {
    dist[i][j] = through
    next[i][j] = next[i][k]  // Path goes through k
}

// Reconstruct path from i to j:
fun getPath(i: Int, j: Int): List<Int> {
    if (next[i][j] == -1) return emptyList()
    val path = mutableListOf(i)
    var current = i
    while (current != j) {
        current = next[current][j]
        path.add(current)
    }
    return path
}
```

---

### 4. A* Algorithm (Bonus)

**Purpose**: Single-source single-target with heuristic guidance. Optimal for pathfinding in games and maps.

**Key idea**: Like Dijkstra, but prioritizes by `f(n) = g(n) + h(n)` where:
- `g(n)` = actual cost from start
- `h(n)` = heuristic estimate to goal (must be admissible: never overestimate)

**Time complexity**: O(E) in best case, O((V + E) log V) in worst case

```kotlin
// A* for grid pathfinding
fun aStar(
    grid: Array<IntArray>,
    start: Pair<Int, Int>,
    goal: Pair<Int, Int>
): Int {
    val rows = grid.size
    val cols = grid[0].size

    // Heuristic: Manhattan distance
    fun heuristic(r: Int, c: Int) = abs(r - goal.first) + abs(c - goal.second)

    val dist = Array(rows) { IntArray(cols) { Int.MAX_VALUE } }
    dist[start.first][start.second] = 0

    // Priority by f = g + h
    val pq = PriorityQueue<Triple<Int, Int, Int>>(compareBy { it.first })
    pq.add(Triple(heuristic(start.first, start.second), start.first, start.second))

    val directions = listOf(-1 to 0, 1 to 0, 0 to -1, 0 to 1)

    while (pq.isNotEmpty()) {
        val (_, r, c) = pq.poll()

        if (r == goal.first && c == goal.second) {
            return dist[r][c]
        }

        for ((dr, dc) in directions) {
            val nr = r + dr
            val nc = c + dc
            if (nr in 0 until rows && nc in 0 until cols && grid[nr][nc] != 1) {
                val newDist = dist[r][c] + 1
                if (newDist < dist[nr][nc]) {
                    dist[nr][nc] = newDist
                    val f = newDist + heuristic(nr, nc)
                    pq.add(Triple(f, nr, nc))
                }
            }
        }
    }

    return -1  // No path found
}
```

---

### Comparison Table

| Algorithm | Type | Negative Weights | Negative Cycles | Time | Space |
|-----------|------|------------------|-----------------|------|-------|
| **Dijkstra** | Single-source | No | No | O((V+E) log V) | O(V) |
| **Bellman-Ford** | Single-source | Yes | Detects | O(VE) | O(V) |
| **Floyd-Warshall** | All-pairs | Yes | Detects | O(V^3) | O(V^2) |
| **A*** | Single-target | No | No | O(E) to O((V+E) log V) | O(V) |
| **BFS** | Unweighted | N/A | N/A | O(V+E) | O(V) |

### Decision Tree

```
Need shortest path?
├─ Unweighted graph? → BFS (O(V+E))
├─ Single source?
│   ├─ Non-negative weights? → Dijkstra
│   └─ Negative weights possible? → Bellman-Ford
├─ All pairs needed?
│   ├─ V <= 400-500? → Floyd-Warshall
│   └─ V > 500? → Run Dijkstra from each vertex
└─ Single target with heuristic? → A*
```

---

### Common Interview Variations

1. **Network Delay Time** (LC 743): Dijkstra from source, return max distance
2. **Cheapest Flights Within K Stops** (LC 787): Modified Bellman-Ford with K iterations
3. **Path With Minimum Effort** (LC 1631): Dijkstra with max-edge cost metric
4. **Shortest Path in Binary Matrix** (LC 1091): BFS (unweighted)
5. **Find the City With Smallest Number of Neighbors** (LC 1334): Floyd-Warshall

---

## Otvet (RU)

**Обзор алгоритмов кратчайших путей:**
Задачи поиска кратчайших путей находят путь минимального веса между вершинами во взвешенном графе. Выбор алгоритма зависит от: (1) один источник или все пары, (2) наличие отрицательных весов, (3) плотность графа. См. также [[c-algorithms]].

Ключевые понятия:
- **Релаксация**: Обновляем расстояние, если найден более короткий путь: `if dist[u] + weight(u,v) < dist[v]`
- **Один источник**: Найти кратчайшие пути от одной вершины до всех остальных
- **Все пары**: Найти кратчайшие пути между всеми парами вершин

---

### 1. Алгоритм Дейкстры

**Назначение**: Кратчайший путь от одного источника для графов с **неотрицательными** весами.

**Ключевая идея**: Жадно выбираем непосещённую вершину с наименьшим известным расстоянием.

**Временная сложность**:
- С бинарной кучей: **O((V + E) log V)**
- С кучей Фибоначчи: O(E + V log V)
- С массивом (без кучи): O(V^2) - лучше для плотных графов

**Пространственная сложность**: O(V)

```kotlin
// Алгоритм Дейкстры с приоритетной очередью
data class Edge(val to: Int, val weight: Int)

fun dijkstra(graph: List<List<Edge>>, source: Int): IntArray {
    val n = graph.size
    val dist = IntArray(n) { Int.MAX_VALUE }
    dist[source] = 0

    // Мин-куча: Pair(расстояние, вершина)
    val pq = PriorityQueue<Pair<Int, Int>>(compareBy { it.first })
    pq.add(0 to source)

    while (pq.isNotEmpty()) {
        val (d, u) = pq.poll()

        // Пропускаем, если уже нашли лучший путь
        if (d > dist[u]) continue

        for (edge in graph[u]) {
            val newDist = dist[u] + edge.weight
            if (newDist < dist[edge.to]) {
                dist[edge.to] = newDist
                pq.add(newDist to edge.to)
            }
        }
    }

    return dist
}
```

**Когда использовать**:
- Только неотрицательные веса рёбер
- Нужны кратчайшие пути от одного источника
- Чаще всего используется для дорожных сетей, GPS-навигации

**Ограничения**:
- Не работает с отрицательными весами (нарушается жадное предположение)
- Не может обнаружить отрицательные циклы

---

### 2. Алгоритм Беллмана-Форда

**Назначение**: Кратчайший путь от одного источника, который **обрабатывает отрицательные веса** и **обнаруживает отрицательные циклы**.

**Ключевая идея**: Выполняем релаксацию всех рёбер V-1 раз. Если после V-1 итерации какое-то ребро всё ещё можно релаксировать - существует отрицательный цикл.

**Временная сложность**: **O(V * E)**

**Пространственная сложность**: O(V)

```kotlin
// Алгоритм Беллмана-Форда
data class WeightedEdge(val from: Int, val to: Int, val weight: Int)

fun bellmanFord(
    vertices: Int,
    edges: List<WeightedEdge>,
    source: Int
): Pair<IntArray, Boolean> {
    val dist = IntArray(vertices) { Int.MAX_VALUE }
    dist[source] = 0

    // Релаксируем все рёбра V-1 раз
    repeat(vertices - 1) {
        for (edge in edges) {
            if (dist[edge.from] != Int.MAX_VALUE) {
                val newDist = dist[edge.from] + edge.weight
                if (newDist < dist[edge.to]) {
                    dist[edge.to] = newDist
                }
            }
        }
    }

    // Проверка на отрицательный цикл (ещё одна итерация)
    var hasNegativeCycle = false
    for (edge in edges) {
        if (dist[edge.from] != Int.MAX_VALUE &&
            dist[edge.from] + edge.weight < dist[edge.to]) {
            hasNegativeCycle = true
            break
        }
    }

    return dist to hasNegativeCycle
}
```

**Когда использовать**:
- Граф может иметь отрицательные веса рёбер
- Нужно обнаружить отрицательные циклы
- Обнаружение валютного арбитража
- Сетевая маршрутизация с переменными затратами

**Оптимизация**: SPFA (Shortest Path Faster Algorithm) - использует очередь для избежания ненужных релаксаций; средний случай O(E), худший случай O(V*E).

---

### 3. Алгоритм Флойда-Уоршелла

**Назначение**: Кратчайшие пути между **всеми парами** вершин с использованием динамического программирования.

**Ключевая идея**: Для каждой промежуточной вершины k проверяем, короче ли путь i -> k -> j, чем текущий i -> j.

**Временная сложность**: **O(V^3)**

**Пространственная сложность**: O(V^2)

```kotlin
// Алгоритм Флойда-Уоршелла
fun floydWarshall(graph: Array<IntArray>): Array<IntArray> {
    val n = graph.size
    val dist = Array(n) { i -> graph[i].copyOf() }

    // k = промежуточная вершина
    for (k in 0 until n) {
        for (i in 0 until n) {
            for (j in 0 until n) {
                if (dist[i][k] != Int.MAX_VALUE &&
                    dist[k][j] != Int.MAX_VALUE) {
                    val through = dist[i][k] + dist[k][j]
                    if (through < dist[i][j]) {
                        dist[i][j] = through
                    }
                }
            }
        }
    }

    return dist
}

// Обнаружение отрицательного цикла: проверяем, если dist[i][i] < 0 для любого i
fun hasNegativeCycle(dist: Array<IntArray>): Boolean {
    return dist.indices.any { dist[it][it] < 0 }
}
```

**Когда использовать**:
- Нужны кратчайшие пути между всеми парами
- Плотные графы (E близко к V^2)
- Граф небольшой (V <= 400-500)
- Задачи на транзитивное замыкание

**Восстановление пути**:
```kotlin
// Отслеживаем предшественников для восстановления пути
val next = Array(n) { i -> IntArray(n) { j -> if (graph[i][j] != INF) j else -1 } }

// Обновление в основном цикле:
if (through < dist[i][j]) {
    dist[i][j] = through
    next[i][j] = next[i][k]  // Путь проходит через k
}

// Восстановление пути от i до j:
fun getPath(i: Int, j: Int): List<Int> {
    if (next[i][j] == -1) return emptyList()
    val path = mutableListOf(i)
    var current = i
    while (current != j) {
        current = next[current][j]
        path.add(current)
    }
    return path
}
```

---

### 4. Алгоритм A* (Бонус)

**Назначение**: Один источник - одна цель с эвристическим направлением. Оптимален для поиска пути в играх и на картах.

**Ключевая идея**: Как Дейкстра, но приоритет по `f(n) = g(n) + h(n)`, где:
- `g(n)` = фактическая стоимость от старта
- `h(n)` = эвристическая оценка до цели (должна быть допустимой: никогда не переоценивать)

**Временная сложность**: O(E) в лучшем случае, O((V + E) log V) в худшем

```kotlin
// A* для поиска пути на сетке
fun aStar(
    grid: Array<IntArray>,
    start: Pair<Int, Int>,
    goal: Pair<Int, Int>
): Int {
    val rows = grid.size
    val cols = grid[0].size

    // Эвристика: манхэттенское расстояние
    fun heuristic(r: Int, c: Int) = abs(r - goal.first) + abs(c - goal.second)

    val dist = Array(rows) { IntArray(cols) { Int.MAX_VALUE } }
    dist[start.first][start.second] = 0

    // Приоритет по f = g + h
    val pq = PriorityQueue<Triple<Int, Int, Int>>(compareBy { it.first })
    pq.add(Triple(heuristic(start.first, start.second), start.first, start.second))

    val directions = listOf(-1 to 0, 1 to 0, 0 to -1, 0 to 1)

    while (pq.isNotEmpty()) {
        val (_, r, c) = pq.poll()

        if (r == goal.first && c == goal.second) {
            return dist[r][c]
        }

        for ((dr, dc) in directions) {
            val nr = r + dr
            val nc = c + dc
            if (nr in 0 until rows && nc in 0 until cols && grid[nr][nc] != 1) {
                val newDist = dist[r][c] + 1
                if (newDist < dist[nr][nc]) {
                    dist[nr][nc] = newDist
                    val f = newDist + heuristic(nr, nc)
                    pq.add(Triple(f, nr, nc))
                }
            }
        }
    }

    return -1  // Путь не найден
}
```

---

### Сравнительная таблица

| Алгоритм | Тип | Отриц. веса | Отриц. циклы | Время | Память |
|----------|-----|-------------|--------------|-------|--------|
| **Дейкстра** | Один источник | Нет | Нет | O((V+E) log V) | O(V) |
| **Беллман-Форд** | Один источник | Да | Обнаруживает | O(VE) | O(V) |
| **Флойд-Уоршелл** | Все пары | Да | Обнаруживает | O(V^3) | O(V^2) |
| **A*** | Одна цель | Нет | Нет | O(E) до O((V+E) log V) | O(V) |
| **BFS** | Без весов | Н/Д | Н/Д | O(V+E) | O(V) |

### Дерево решений

```
Нужен кратчайший путь?
├─ Граф без весов? → BFS (O(V+E))
├─ Один источник?
│   ├─ Неотрицательные веса? → Дейкстра
│   └─ Возможны отрицательные веса? → Беллман-Форд
├─ Нужны все пары?
│   ├─ V <= 400-500? → Флойд-Уоршелл
│   └─ V > 500? → Запускаем Дейкстру из каждой вершины
└─ Одна цель с эвристикой? → A*
```

---

### Частые вариации на интервью

1. **Network Delay Time** (LC 743): Дейкстра от источника, вернуть максимальное расстояние
2. **Cheapest Flights Within K Stops** (LC 787): Модифицированный Беллман-Форд с K итерациями
3. **Path With Minimum Effort** (LC 1631): Дейкстра с метрикой максимального веса ребра
4. **Shortest Path in Binary Matrix** (LC 1091): BFS (без весов)
5. **Find the City With Smallest Number of Neighbors** (LC 1334): Флойд-Уоршелл
