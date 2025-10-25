---
id: 20251012-200004
title: "Graph Algorithms: BFS and DFS / Алгоритмы графов: BFS и DFS"
aliases: ["BFS and DFS", "BFS и DFS", "Graph Algorithms", "Алгоритмы графов"]
topic: algorithms
subtopics: [bfs, dfs, graphs, traversal]
question_kind: coding
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-algorithms
related: [c-graph-algorithms, q-advanced-graph-algorithms--algorithms--hard, q-dynamic-programming-fundamentals--algorithms--hard]
created: 2025-10-12
updated: 2025-01-25
tags: [algorithms, bfs, dfs, difficulty/hard, graphs, traversal]
sources: [https://en.wikipedia.org/wiki/Breadth-first_search, https://en.wikipedia.org/wiki/Depth-first_search]
date created: Sunday, October 12th 2025, 9:44:02 pm
date modified: Saturday, October 25th 2025, 5:23:33 pm
---

# Вопрос (RU)
> Как работают BFS и DFS? Когда следует использовать каждый? Каковы распространённые задачи и паттерны с графами?

# Question (EN)
> How do BFS and DFS work? When should you use each? What are common graph problems and patterns?

---

## Ответ (RU)

**Теория алгоритмов графов:**
Графы - структуры данных, представляющие отношения между сущностями. BFS (поиск в ширину) и DFS (поиск в глубину) - основные алгоритмы обхода графов с различными характеристиками и применениями.

**Представление графа:**
```kotlin
// Список смежности - наиболее распространённый способ
class Graph(val vertices: Int) {
    val adj = Array(vertices) { mutableListOf<Int>() }

    fun addEdge(u: Int, v: Int) {
        adj[u].add(v)
        adj[v].add(u)  // Для неориентированного графа
    }
}
```

**BFS (Breadth-First Search):**
```kotlin
// Обход по уровням с использованием очереди
fun bfs(graph: Graph, start: Int) {
    val visited = BooleanArray(graph.vertices)
    val queue = LinkedList<Int>()

    visited[start] = true
    queue.offer(start)

    while (queue.isNotEmpty()) {
        val vertex = queue.poll()
        print("$vertex ")

        for (neighbor in graph.adj[vertex]) {
            if (!visited[neighbor]) {
                visited[neighbor] = true
                queue.offer(neighbor)
            }
        }
    }
}
```

**DFS (Depth-First Search):**
```kotlin
// Обход в глубину с использованием рекурсии
fun dfs(graph: Graph, start: Int, visited: BooleanArray = BooleanArray(graph.vertices)) {
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
    val stack = Stack<Int>()

    stack.push(start)

    while (stack.isNotEmpty()) {
        val vertex = stack.pop()

        if (!visited[vertex]) {
            visited[vertex] = true
            print("$vertex ")

            // Добавляем соседей в обратном порядке для сохранения порядка слева направо
            for (i in graph.adj[vertex].size - 1 downTo 0) {
                if (!visited[graph.adj[vertex][i]]) {
                    stack.push(graph.adj[vertex][i])
                }
            }
        }
    }
}
```

**Кратчайший путь (BFS):**
```kotlin
// Найти кратчайший путь между двумя узлами
fun shortestPath(graph: Graph, start: Int, end: Int): Int {
    val visited = BooleanArray(graph.vertices)
    val queue = LinkedList<Pair<Int, Int>>()  // (вершина, расстояние)

    visited[start] = true
    queue.offer(start to 0)

    while (queue.isNotEmpty()) {
        val (vertex, dist) = queue.poll()

        if (vertex == end) return dist

        for (neighbor in graph.adj[vertex]) {
            if (!visited[neighbor]) {
                visited[neighbor] = true
                queue.offer(neighbor to dist + 1)
            }
        }
    }

    return -1  // Путь не найден
}
```

**Обнаружение цикла (DFS):**
```kotlin
// Обнаружить цикл в ориентированном графе
fun canFinish(numCourses: Int, prerequisites: Array<IntArray>): Boolean {
    val adj = Array(numCourses) { mutableListOf<Int>() }

    // Строим список смежности
    for ((course, prereq) in prerequisites) {
        adj[prereq].add(course)
    }

    val visited = IntArray(numCourses)  // 0=не посещён, 1=посещается, 2=посещён

    fun hasCycle(course: Int): Boolean {
        if (visited[course] == 1) return true  // Цикл обнаружен!
        if (visited[course] == 2) return false // Уже посещён

        visited[course] = 1  // Отмечаем как посещаемый

        for (neighbor in adj[course]) {
            if (hasCycle(neighbor)) return true
        }

        visited[course] = 2  // Отмечаем как посещённый
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
// Подсчитать количество связанных компонентов в 2D сетке
fun numIslands(grid: Array<CharArray>): Int {
    if (grid.isEmpty()) return 0

    val m = grid.size
    val n = grid[0].size
    var count = 0

    fun dfs(i: Int, j: Int) {
        if (i < 0 || i >= m || j < 0 || j >= n || grid[i][j] == '0') {
            return
        }

        grid[i][j] = '0'  // Отмечаем как посещённый

        // Исследуем 4 направления
        dfs(i + 1, j)  // Вниз
        dfs(i - 1, j)  // Вверх
        dfs(i, j + 1)  // Вправо
        dfs(i, j - 1)  // Влево
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

## Answer (EN)

**Graph Algorithms Theory:**
Graphs are data structures representing relationships between entities. BFS (Breadth-First Search) and DFS (Depth-First Search) are fundamental graph traversal algorithms with different characteristics and applications.

**Graph Representation:**
```kotlin
// Adjacency list - most common representation
class Graph(val vertices: Int) {
    val adj = Array(vertices) { mutableListOf<Int>() }

    fun addEdge(u: Int, v: Int) {
        adj[u].add(v)
        adj[v].add(u)  // For undirected graph
    }
}
```

**BFS (Breadth-First Search):**
```kotlin
// Level-by-level traversal using queue
fun bfs(graph: Graph, start: Int) {
    val visited = BooleanArray(graph.vertices)
    val queue = LinkedList<Int>()

    visited[start] = true
    queue.offer(start)

    while (queue.isNotEmpty()) {
        val vertex = queue.poll()
        print("$vertex ")

        for (neighbor in graph.adj[vertex]) {
            if (!visited[neighbor]) {
                visited[neighbor] = true
                queue.offer(neighbor)
            }
        }
    }
}
```

**DFS (Depth-First Search):**
```kotlin
// Deep traversal using recursion
fun dfs(graph: Graph, start: Int, visited: BooleanArray = BooleanArray(graph.vertices)) {
    visited[start] = true
    print("$start ")

    for (neighbor in graph.adj[start]) {
        if (!visited[neighbor]) {
            dfs(graph, neighbor, visited)
        }
    }
}

// Iterative DFS with stack
fun dfsIterative(graph: Graph, start: Int) {
    val visited = BooleanArray(graph.vertices)
    val stack = Stack<Int>()

    stack.push(start)

    while (stack.isNotEmpty()) {
        val vertex = stack.pop()

        if (!visited[vertex]) {
            visited[vertex] = true
            print("$vertex ")

            // Push neighbors in reverse order to maintain left-to-right order
            for (i in graph.adj[vertex].size - 1 downTo 0) {
                if (!visited[graph.adj[vertex][i]]) {
                    stack.push(graph.adj[vertex][i])
                }
            }
        }
    }
}
```

**Shortest Path (BFS):**
```kotlin
// Find shortest path between two nodes
fun shortestPath(graph: Graph, start: Int, end: Int): Int {
    val visited = BooleanArray(graph.vertices)
    val queue = LinkedList<Pair<Int, Int>>()  // (vertex, distance)

    visited[start] = true
    queue.offer(start to 0)

    while (queue.isNotEmpty()) {
        val (vertex, dist) = queue.poll()

        if (vertex == end) return dist

        for (neighbor in graph.adj[vertex]) {
            if (!visited[neighbor]) {
                visited[neighbor] = true
                queue.offer(neighbor to dist + 1)
            }
        }
    }

    return -1  // No path found
}
```

**Cycle Detection (DFS):**
```kotlin
// Detect cycle in directed graph
fun canFinish(numCourses: Int, prerequisites: Array<IntArray>): Boolean {
    val adj = Array(numCourses) { mutableListOf<Int>() }

    // Build adjacency list
    for ((course, prereq) in prerequisites) {
        adj[prereq].add(course)
    }

    val visited = IntArray(numCourses)  // 0=unvisited, 1=visiting, 2=visited

    fun hasCycle(course: Int): Boolean {
        if (visited[course] == 1) return true  // Cycle detected!
        if (visited[course] == 2) return false // Already visited

        visited[course] = 1  // Mark as visiting

        for (neighbor in adj[course]) {
            if (hasCycle(neighbor)) return true
        }

        visited[course] = 2  // Mark as visited
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
// Count connected components in 2D grid
fun numIslands(grid: Array<CharArray>): Int {
    if (grid.isEmpty()) return 0

    val m = grid.size
    val n = grid[0].size
    var count = 0

    fun dfs(i: Int, j: Int) {
        if (i < 0 || i >= m || j < 0 || j >= n || grid[i][j] == '0') {
            return
        }

        grid[i][j] = '0'  // Mark as visited

        // Explore 4 directions
        dfs(i + 1, j)  // Down
        dfs(i - 1, j)  // Up
        dfs(i, j + 1)  // Right
        dfs(i, j - 1)  // Left
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

---

## Follow-ups

- What is the difference between BFS and DFS space complexity?
- How do you detect a cycle in an undirected vs directed graph?
- What is bidirectional BFS and when is it useful?

## Related Questions

### Prerequisites (Easier)
- [[q-data-structures-overview--algorithms--easy]] - Data structures basics
- [[q-recursion-basics--algorithms--easy]] - Recursion concepts

### Related (Same Level)
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - DP algorithms
- [[q-binary-search-variants--algorithms--medium]] - Search algorithms

### Advanced (Harder)
- [[q-advanced-graph-algorithms--algorithms--hard]] - Advanced graph algorithms
- [[q-dijkstra-algorithm--algorithms--hard]] - Shortest path algorithms
