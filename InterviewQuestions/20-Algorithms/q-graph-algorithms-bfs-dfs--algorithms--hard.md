---\
id: algo-002
title: "Graph Algorithms: BFS and DFS / Алгоритмы графов: BFS и DFS"
aliases: ["BFS and DFS", "BFS и DFS", "Graph Algorithms", "Алгоритмы графов"]
topic: algorithms
subtopics: [bfs, dfs, graphs]
question_kind: coding
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-algorithms
related: [c-algorithms, q-advanced-graph-algorithms--algorithms--hard]
created: 2025-10-12
updated: 2025-11-11
tags: [algorithms, bfs, dfs, difficulty/hard, graphs, traversal]
sources: ["https://en.wikipedia.org/wiki/Breadth-first_search", "https://en.wikipedia.org/wiki/Depth-first_search"]

---\
# Вопрос (RU)
> Как работают BFS и DFS? Когда следует использовать каждый? Каковы распространённые задачи и паттерны с графами?

# Question (EN)
> How do BFS and DFS work? When should you use each? What are common graph problems and patterns?

---

## Ответ (RU)

**Теория алгоритмов графов:**
Графы — структуры данных, представляющие отношения между сущностями. BFS (поиск в ширину) и DFS (поиск в глубину) — базовые алгоритмы обхода графов с разными свойствами и применением. См. также [[c-algorithms]].

Ключевые идеи:
- Оба алгоритма посещают вершины и рёбра максимум по одному разу: сложность O(V + E).
- BFS использует очередь и обходит граф по слоям.
- DFS использует стек (явный или стек вызовов) и уходит в глубину.
- По памяти:
  - BFS в худшем случае хранит весь «фронт» слоя: O(V).
  - DFS хранит путь (глубину рекурсии/стека): O(H), где H ≤ V; в худшем случае O(V).

**Представление графа:**
```kotlin
// Список смежности — распространённый способ для разреженных графов
class Graph(val vertices: Int, val directed: Boolean = false) {
    val adj = Array(vertices) { mutableListOf<Int>() }

    fun addEdge(u: Int, v: Int) {
        adj[u].add(v)
        if (!directed) {
            adj[v].add(u)  // Для неориентированного графа
        }
    }
}
```

**BFS (Breadth-First Search):**
```kotlin
// Обход по уровням с использованием очереди
// Предполагается, что граф не взвешенный, рёбра равной «стоимости»
fun bfs(graph: Graph, start: Int) {
    val visited = BooleanArray(graph.vertices)
    val queue: ArrayDeque<Int> = ArrayDeque()

    visited[start] = true
    queue.add(start)

    while (queue.isNotEmpty()) {
        val vertex = queue.removeFirst()
        print("$vertex ")

        for (neighbor in graph.adj[vertex]) {
            if (!visited[neighbor]) {
                visited[neighbor] = true
                queue.add(neighbor)
            }
        }
    }
}
```

**DFS (Depth-First Search):**
```kotlin
// Обход в глубину с использованием рекурсии
fun dfs(graph: Graph, start: Int, visited: BooleanArray = BooleanArray(graph.vertices)) {
    if (visited[start]) return
    visited[start] = true
    print("$start ")

    for (neighbor in graph.adj[start]) {
        if (!visited[neighbor]) {
            dfs(graph, neighbor, visited)
        }
    }
}

// Итеративная версия DFS со стеком
fun dfsIterative(graph: Graph, start: Int) {
    val visited = BooleanArray(graph.vertices)
    val stack = ArrayDeque<Int>()

    stack.addLast(start)

    while (stack.isNotEmpty()) {
        val vertex = stack.removeLast()

        if (!visited[vertex]) {
            visited[vertex] = true
            print("$vertex ")

            // Добавляем соседей в обратном порядке для сохранения детерминированного порядка обхода
            for (i in graph.adj[vertex].size - 1 downTo 0) {
                val neighbor = graph.adj[vertex][i]
                if (!visited[neighbor]) {
                    stack.addLast(neighbor)
                }
            }
        }
    }
}
```

**Кратчайший путь (BFS в невзвешенном графе):**
```kotlin
// Найти длину кратчайшего пути между двумя узлами в невзвешенном графе
fun shortestPath(graph: Graph, start: Int, end: Int): Int {
    val visited = BooleanArray(graph.vertices)
    val queue: ArrayDeque<Pair<Int, Int>> = ArrayDeque()  // (вершина, расстояние)

    visited[start] = true
    queue.add(start to 0)

    while (queue.isNotEmpty()) {
        val (vertex, dist) = queue.removeFirst()

        if (vertex == end) return dist

        for (neighbor in graph.adj[vertex]) {
            if (!visited[neighbor]) {
                visited[neighbor] = true
                queue.add(neighbor to dist + 1)
            }
        }
    }

    return -1  // Путь не найден
}
```

**Обнаружение цикла (DFS в ориентированном графе):**
```kotlin
// Обнаружить цикл в ориентированном графе (классическая задача Course Schedule)
fun canFinish(numCourses: Int, prerequisites: Array<IntArray>): Boolean {
    val adj = Array(numCourses) { mutableListOf<Int>() }

    // Строим список смежности: prereq -> course
    for ((course, prereq) in prerequisites) {
        adj[prereq].add(course)
    }

    val state = IntArray(numCourses)  // 0=не посещён, 1=в стеке (visiting), 2=завершён

    fun hasCycle(v: Int): Boolean {
        if (state[v] == 1) return true       // Цикл обнаружен
        if (state[v] == 2) return false      // Уже обработан

        state[v] = 1
        for (to in adj[v]) {
            if (hasCycle(to)) return true
        }
        state[v] = 2
        return false
    }

    for (i in 0 until numCourses) {
        if (hasCycle(i)) return false
    }

    return true
}
```

**Количество островов (DFS):**
```kotlin
// Подсчитать количество «островов» (связанных компонент из '1') в 2D-сетке.
// Мы умышленно модифицируем grid, помечая посещённые клетки как '0'.
fun numIslands(grid: Array<CharArray>): Int {
    if (grid.isEmpty()) return 0

    val m = grid.size
    val n = grid[0].size
    var count = 0

    fun dfs(i: Int, j: Int) {
        if (i < 0 || i >= m || j < 0 || j >= n || grid[i][j] == '0') return

        grid[i][j] = '0'  // Отмечаем как посещённую; можно также использовать отдельный visited[][]

        // Исследуем 4 направления
        dfs(i + 1, j)
        dfs(i - 1, j)
        dfs(i, j + 1)
        dfs(i, j - 1)
    }

    for (i in 0 until m) {
        for (j in 0 until n) {
            if (grid[i][j] == '1') {
                count++
                dfs(i, j)
            }
        }
    }

    return count
}
```

**Когда использовать BFS vs DFS (RU):**
- BFS:
  - Кратчайший путь в невзвешенном графе (по количеству рёбер).
  - Обход по слоям (поиск ближайшего решения, многoисточниковый BFS и подобные задачи).
- DFS:
  - Обход всей компоненты, проверка достижимости.
  - Обнаружение циклов, топологическая сортировка (ориентированные графы).
  - Задачи на связные компоненты ("острова", компоненты в неориентированном графе).

## Answer (EN)

**Graph Algorithms Theory:**
Graphs are data structures representing relationships between entities. BFS (Breadth-First Search) and DFS (Depth-First Search) are fundamental traversal algorithms with different properties and use cases.

Key points:
- Both run in O(V + E), visiting each vertex and edge at most once.
- BFS uses a queue and explores the graph level by level.
- DFS uses a stack (explicit or call stack) and explores as deep as possible.
- Space:
  - BFS may keep an entire frontier level in memory: O(V) in the worst case.
  - DFS keeps the recursion/stack path: O(H) where H ≤ V; O(V) in the worst case.

**Graph Representation:**
```kotlin
// Adjacency list — typical for sparse graphs
class Graph(val vertices: Int, val directed: Boolean = false) {
    val adj = Array(vertices) { mutableListOf<Int>() }

    fun addEdge(u: Int, v: Int) {
        adj[u].add(v)
        if (!directed) {
            adj[v].add(u)  // For undirected graphs
        }
    }
}
```

**BFS (Breadth-First Search):**
```kotlin
// Level-order traversal using a queue
// Assumes an unweighted graph with equal edge "cost"
fun bfs(graph: Graph, start: Int) {
    val visited = BooleanArray(graph.vertices)
    val queue: ArrayDeque<Int> = ArrayDeque()

    visited[start] = true
    queue.add(start)

    while (queue.isNotEmpty()) {
        val vertex = queue.removeFirst()
        print("$vertex ")

        for (neighbor in graph.adj[vertex]) {
            if (!visited[neighbor]) {
                visited[neighbor] = true
                queue.add(neighbor)
            }
        }
    }
}
```

**DFS (Depth-First Search):**
```kotlin
// Depth-first traversal using recursion
fun dfs(graph: Graph, start: Int, visited: BooleanArray = BooleanArray(graph.vertices)) {
    if (visited[start]) return
    visited[start] = true
    print("$start ")

    for (neighbor in graph.adj[start]) {
        if (!visited[neighbor]) {
            dfs(graph, neighbor, visited)
        }
    }
}

// Iterative DFS using a stack
fun dfsIterative(graph: Graph, start: Int) {
    val visited = BooleanArray(graph.vertices)
    val stack = ArrayDeque<Int>()

    stack.addLast(start)

    while (stack.isNotEmpty()) {
        val vertex = stack.removeLast()

        if (!visited[vertex]) {
            visited[vertex] = true
            print("$vertex ")

            // Push neighbors in reverse order for deterministic left-to-right traversal
            for (i in graph.adj[vertex].size - 1 downTo 0) {
                val neighbor = graph.adj[vertex][i]
                if (!visited[neighbor]) {
                    stack.addLast(neighbor)
                }
            }
        }
    }
}
```

**Shortest `Path` (BFS on Unweighted Graph):**
```kotlin
// Find the length of the shortest path between two nodes in an unweighted graph
fun shortestPath(graph: Graph, start: Int, end: Int): Int {
    val visited = BooleanArray(graph.vertices)
    val queue: ArrayDeque<Pair<Int, Int>> = ArrayDeque()  // (vertex, distance)

    visited[start] = true
    queue.add(start to 0)

    while (queue.isNotEmpty()) {
        val (vertex, dist) = queue.removeFirst()

        if (vertex == end) return dist

        for (neighbor in graph.adj[vertex]) {
            if (!visited[neighbor]) {
                visited[neighbor] = true
                queue.add(neighbor to dist + 1)
            }
        }
    }

    return -1  // No path found
}
```

**Cycle Detection (DFS in Directed Graph):**
```kotlin
// Detect a cycle in a directed graph (classic Course Schedule problem)
fun canFinish(numCourses: Int, prerequisites: Array<IntArray>): Boolean {
    val adj = Array(numCourses) { mutableListOf<Int>() }

    // Build adjacency list: prereq -> course
    for ((course, prereq) in prerequisites) {
        adj[prereq].add(course)
    }

    val state = IntArray(numCourses)  // 0=unvisited, 1=visiting, 2=visited

    fun hasCycle(v: Int): Boolean {
        if (state[v] == 1) return true      // Back edge -> cycle
        if (state[v] == 2) return false     // Already fully processed

        state[v] = 1
        for (to in adj[v]) {
            if (hasCycle(to)) return true
        }
        state[v] = 2
        return false
    }

    for (i in 0 until numCourses) {
        if (hasCycle(i)) return false
    }

    return true
}
```

**Number of Islands (DFS):**
```kotlin
// Count the number of "islands" (connected components of '1') in a 2D grid.
// We intentionally mutate the grid, marking visited land cells as '0'.
fun numIslands(grid: Array<CharArray>): Int {
    if (grid.isEmpty()) return 0

    val m = grid.size
    val n = grid[0].size
    var count = 0

    fun dfs(i: Int, j: Int) {
        if (i < 0 || i >= m || j < 0 || j >= n || grid[i][j] == '0') return

        grid[i][j] = '0'  // Mark as visited; alternatively, use a separate visited[][] array

        // Explore 4 directions
        dfs(i + 1, j)
        dfs(i - 1, j)
        dfs(i, j + 1)
        dfs(i, j - 1)
    }

    for (i in 0 until m) {
        for (j in 0 until n) {
            if (grid[i][j] == '1') {
                count++
                dfs(i, j)
            }
        }
    }

    return count
}
```

**When to use BFS vs DFS (EN):**
- BFS:
  - Shortest path in an unweighted graph (by number of edges).
  - Level-order exploration (finding nearest solution, multi-source BFS, etc.).
- DFS:
  - Exploring full components and reachability.
  - Cycle detection, topological sort (directed graphs).
  - Connected components / island-style problems.

---

## Follow-ups

- What is the difference between BFS and DFS space complexity?
- How do you detect a cycle in an undirected vs directed graph?
- What is bidirectional BFS and when is it useful?

## References

- [[c-algorithms]]
- "Breadth-First Search" — Wikipedia
- "Depth-First Search" — Wikipedia

## Related Questions

### Prerequisites (Easier)
- [[q-data-structures-overview--algorithms--easy]] - Data structures basics

### Related (Same Level)
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - DP algorithms
- [[q-binary-search-variants--algorithms--medium]] - Search algorithms

### Advanced (Harder)

## Дополнительные Вопросы (RU)
- В чём разница в потреблении памяти между BFS и DFS?
- Как обнаружить цикл в неориентированном и ориентированном графе?
- Что такое двунаправленный BFS и когда он полезен?
## Связанные Вопросы (RU)
### Предпосылки (проще)
- [[q-data-structures-overview--algorithms--easy]] - Базовые структуры данных
### Связанные (такой Же уровень)
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - Алгоритмы динамического программирования
- [[q-binary-search-variants--algorithms--medium]] - Варианты бинарного поиска
### Продвинутые (сложнее)