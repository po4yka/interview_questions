---
id: q-topological-sort
title: Topological Sort / Топологическая сортировка
aliases:
- Topological Sort
- Топологическая сортировка
- Toposort
- DAG ordering
topic: algorithms
subtopics:
- graphs
- dag
- ordering
question_kind: coding
difficulty: medium
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
- dag
- topological-sort
- difficulty/medium
sources:
- https://en.wikipedia.org/wiki/Topological_sorting
- https://cp-algorithms.com/graph/topological-sort.html
anki_cards:
- slug: q-topological-sort-0-en
  language: en
  anki_id: 1769404211319
  synced_at: '2026-01-26T09:10:14.464797'
- slug: q-topological-sort-0-ru
  language: ru
  anki_id: 1769404211340
  synced_at: '2026-01-26T09:10:14.465846'
---
# Вопрос (RU)
> Объясните топологическую сортировку. Какие два основных подхода к её реализации?

# Question (EN)
> Explain Topological Sort. What are the two main approaches to implement it?

---

## Ответ (RU)

**Топологическая сортировка** — линейное упорядочение вершин направленного ациклического графа (DAG), при котором для каждого ребра (u, v) вершина u предшествует вершине v в упорядочении.

**Применение:**
- Системы сборки (Make, Gradle) — порядок компиляции зависимостей
- Планирование задач с зависимостями
- Порядок прохождения курсов с пререквизитами
- Разрешение зависимостей пакетов (npm, pip)
- Порядок инициализации модулей

**Ключевые свойства:**
- Работает **только для DAG** (направленных ациклических графов)
- Если граф содержит цикл, топологическая сортировка **невозможна**
- Для одного графа может существовать **несколько** корректных порядков
- Сложность: **O(V + E)** по времени и памяти

---

### Подход 1: Алгоритм Кана (на основе BFS)

Идея: итеративно удаляем вершины с нулевой входящей степенью.

```kotlin
fun kahnTopologicalSort(graph: List<List<Int>>): List<Int>? {
    val n = graph.size
    val inDegree = IntArray(n)

    // Вычисляем входящие степени
    for (u in 0 until n) {
        for (v in graph[u]) {
            inDegree[v]++
        }
    }

    // Очередь вершин с нулевой входящей степенью
    val queue = ArrayDeque<Int>()
    for (i in 0 until n) {
        if (inDegree[i] == 0) queue.add(i)
    }

    val result = mutableListOf<Int>()

    while (queue.isNotEmpty()) {
        val u = queue.removeFirst()
        result.add(u)

        for (v in graph[u]) {
            inDegree[v]--
            if (inDegree[v] == 0) {
                queue.add(v)
            }
        }
    }

    // Если не все вершины обработаны — есть цикл
    return if (result.size == n) result else null
}
```

**Обнаружение цикла:** если `result.size < n`, граф содержит цикл.

---

### Подход 2: На основе DFS

Идея: выполняем DFS и добавляем вершину в результат **после** обхода всех её соседей (post-order). Затем разворачиваем результат.

```kotlin
fun dfsTopologicalSort(graph: List<List<Int>>): List<Int>? {
    val n = graph.size
    val visited = IntArray(n)  // 0=не посещена, 1=в обработке, 2=завершена
    val result = mutableListOf<Int>()
    var hasCycle = false

    fun dfs(u: Int) {
        if (hasCycle) return
        visited[u] = 1  // Помечаем как «в обработке»

        for (v in graph[u]) {
            when (visited[v]) {
                0 -> dfs(v)
                1 -> { hasCycle = true; return }  // Обратное ребро = цикл
                // 2 -> уже обработана, пропускаем
            }
        }

        visited[u] = 2  // Помечаем как завершённую
        result.add(u)   // Post-order: добавляем после всех соседей
    }

    for (i in 0 until n) {
        if (visited[i] == 0) dfs(i)
    }

    return if (hasCycle) null else result.reversed()
}
```

**Обнаружение цикла:** находим обратное ребро (ребро к вершине со статусом «в обработке»).

---

### Сравнение подходов

| Критерий | Алгоритм Кана (BFS) | DFS-подход |
|----------|---------------------|------------|
| Структура данных | Очередь + массив степеней | Стек вызовов |
| Порядок вывода | Прямой | Требуется разворот |
| Обнаружение цикла | count < n | Обратное ребро |
| Параллелизация | Легче (по слоям) | Сложнее |
| Память (рекурсия) | Итеративный | Рекурсивный стек |

---

### Типичные задачи на интервью

1. **Course Schedule (LeetCode 207, 210)** — проверка возможности пройти все курсы
2. **Alien Dictionary (LeetCode 269)** — восстановить порядок букв по словарю
3. **Parallel Courses** — минимальное число семестров
4. **Build Order** — порядок сборки проектов с зависимостями

---

## Answer (EN)

**Topological Sort** is a linear ordering of vertices in a Directed Acyclic Graph (DAG) such that for every edge (u, v), vertex u comes before vertex v in the ordering.

**Use Cases:**
- Build systems (Make, Gradle) — compilation order of dependencies
- Task scheduling with dependencies
- Course prerequisites ordering
- Package dependency resolution (npm, pip)
- Module initialization order

**Key Properties:**
- Works **only on DAGs** (Directed Acyclic Graphs)
- If the graph contains a cycle, topological sort is **impossible**
- **Multiple valid orderings** may exist for the same graph
- Complexity: **O(V + E)** time and space

---

### Approach 1: Kahn's Algorithm (BFS-based)

Idea: iteratively remove vertices with zero in-degree.

```kotlin
fun kahnTopologicalSort(graph: List<List<Int>>): List<Int>? {
    val n = graph.size
    val inDegree = IntArray(n)

    // Calculate in-degrees
    for (u in 0 until n) {
        for (v in graph[u]) {
            inDegree[v]++
        }
    }

    // Queue of vertices with zero in-degree
    val queue = ArrayDeque<Int>()
    for (i in 0 until n) {
        if (inDegree[i] == 0) queue.add(i)
    }

    val result = mutableListOf<Int>()

    while (queue.isNotEmpty()) {
        val u = queue.removeFirst()
        result.add(u)

        for (v in graph[u]) {
            inDegree[v]--
            if (inDegree[v] == 0) {
                queue.add(v)
            }
        }
    }

    // If not all vertices processed — cycle exists
    return if (result.size == n) result else null
}
```

**Cycle Detection:** if `result.size < n`, the graph contains a cycle.

---

### Approach 2: DFS-based

Idea: perform DFS and add vertex to result **after** visiting all neighbors (post-order). Then reverse the result.

```kotlin
fun dfsTopologicalSort(graph: List<List<Int>>): List<Int>? {
    val n = graph.size
    val visited = IntArray(n)  // 0=unvisited, 1=processing, 2=done
    val result = mutableListOf<Int>()
    var hasCycle = false

    fun dfs(u: Int) {
        if (hasCycle) return
        visited[u] = 1  // Mark as processing

        for (v in graph[u]) {
            when (visited[v]) {
                0 -> dfs(v)
                1 -> { hasCycle = true; return }  // Back edge = cycle
                // 2 -> already done, skip
            }
        }

        visited[u] = 2  // Mark as done
        result.add(u)   // Post-order: add after all neighbors
    }

    for (i in 0 until n) {
        if (visited[i] == 0) dfs(i)
    }

    return if (hasCycle) null else result.reversed()
}
```

**Cycle Detection:** find a back edge (edge to a vertex with "processing" status).

---

### Comparison of Approaches

| Criterion | Kahn's Algorithm (BFS) | DFS-based |
|-----------|------------------------|-----------|
| Data structure | Queue + in-degree array | Call stack |
| Output order | Direct | Requires reversal |
| Cycle detection | count < n | Back edge |
| Parallelization | Easier (layer by layer) | Harder |
| Memory (recursion) | Iterative | Recursive stack |

---

### Common Interview Problems

1. **Course Schedule (LeetCode 207, 210)** — check if all courses can be completed
2. **Alien Dictionary (LeetCode 269)** — reconstruct letter order from dictionary
3. **Parallel Courses** — minimum number of semesters
4. **Build Order** — project build order with dependencies

---

## Ключевые моменты / Key Takeaways

| RU | EN |
|----|-----|
| Топосорт работает только для DAG | Toposort only works on DAGs |
| Алгоритм Кана: BFS + входящие степени | Kahn's: BFS + in-degrees |
| DFS: post-order + разворот | DFS: post-order + reverse |
| Цикл = невозможность сортировки | Cycle = impossible to sort |
| O(V + E) для обоих подходов | O(V + E) for both approaches |
