---
id: cs-035
title: "Data Structures and Algorithms Fundamentals / Фундаментальные структуры данных и алгоритмы"
aliases: ["Data Structures and Algorithms Fundamentals", "Фундаментальные структуры данных и алгоритмы"]
topic: cs
subtopics: [algorithms, complexity-analysis, data-structures]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-algorithms, c-data-structures, q-sorting-algorithms-comparison--algorithms--medium]
created: "2025-01-13"
updated: "2025-01-25"
tags: [algorithms, big-o, complexity, data-structures, difficulty/hard, dynamic-programming, graphs, recursion, searching, sorting, trees]
sources: ["https://en.wikipedia.org/wiki/Data_structure"]

date created: Monday, October 13th 2025, 8:01:06 am
date modified: Tuesday, November 25th 2025, 8:53:54 pm
---
# Вопрос (RU)
> Объясните фундаментальные структуры данных и алгоритмы. Какие особенности у каждой структуры и когда их использовать?

# Question (EN)
> Explain fundamental data structures and algorithms. What are the characteristics of each structure and when to use them?

---

## Ответ (RU)

**Теория структур данных:**
Структуры данных — это способы организации и хранения данных для эффективного доступа и модификации. Основные характеристики: время доступа, время вставки/удаления, использование памяти. Выбор структуры данных зависит от паттернов использования. Big O-нотация описывает асимптотическую (обычно по размеру входа) временную и пространственную сложность алгоритмов (часто рассматривают худший и средний случаи отдельно).

**1. Линейные структуры данных:**

**Массивы (Arrays):**

*Теория:* Массивы хранят элементы в contiguous memory с O(1) доступом по индексу. Размер фиксирован (в классическом массиве) или динамический с периодическим копированием. Cache-friendly благодаря locality. Используются для коллекций с известным или верхнеограниченным размером, когда важен произвольный доступ.

```kotlin
// ✅ Массивы: O(1) доступ, O(n) вставка/удаление из середины
class ArrayOperations {
    fun demonstrateArrays() {
        val fixedArray = IntArray(5) { it * 2 }  // [0, 2, 4, 6, 8]
        val element = fixedArray[2]  // O(1) доступ

        val dynamicArray = mutableListOf<Int>()
        dynamicArray.add(10)          // O(1) амортизированно при добавлении в конец
        dynamicArray.add(0, 5)        // O(n) вставка в начало
    }
}

// Сложность (динамический массив):
// Доступ по индексу: O(1)
// Поиск по значению: O(n)
// Вставка в конец: O(1) амортизированно, O(n) в худшем случае при расширении
// Вставка/удаление в середине или начале: O(n)
```

**Связные списки (Linked Lists):**

*Теория:* Связные списки хранят элементы в узлах с указателями. Односвязные (next) или двусвязные (prev + next). Доступ по индексу O(n) из-за последовательного прохода. Вставка/удаление в начало O(1). Вставка/удаление в конец также O(1) при наличии tail-указателя и известном узле. Используются для динамических коллекций с частыми вставками/удалениями, особенно в начале/середине при известном месте.

```kotlin
// ✅ Односвязный список (упрощённо)
data class Node<T>(var data: T, var next: Node<T>? = null)

class LinkedList<T> {
    private var head: Node<T>? = null
    private var tail: Node<T>? = null

    fun addFirst(data: T) {           // O(1)
        head = Node(data, head)
        if (tail == null) tail = head
    }

    fun addLast(data: T) {            // O(1) при наличии tail
        val newNode = Node(data)
        if (tail == null) {
            head = newNode
            tail = newNode
        } else {
            tail!!.next = newNode
            tail = newNode
        }
    }
}

// Сложность:
// Доступ по индексу: O(n)
// Поиск по значению: O(n)
// Вставка/удаление в начало при известном узле: O(1)
// Вставка/удаление после данного узла: O(1)
// Вставка/удаление по индексу: O(n) из-за поиска узла
```

**Стеки (Stacks):**

*Теория:* Стек — LIFO структура (Last In First Out). Реализуется через массив или связный список. Операции `push`/`pop`/`peek` — O(1). Используется для: разбора выражений, backtracking, навигации (history), call stack.

```kotlin
// ✅ Стек: LIFO
class Stack<T> {
    private val items = mutableListOf<T>()

    fun push(item: T) {              // O(1)
        items.add(item)
    }

    fun pop(): T? =                  // O(1)
        if (items.isNotEmpty()) items.removeAt(items.lastIndex) else null

    fun peek(): T? =                 // O(1)
        items.lastOrNull()

    fun isEmpty(): Boolean = items.isEmpty()
}

// Use case: проверка сбалансированности скобок
fun isBalanced(s: String): Boolean {
    val stack = Stack<Char>()
    val pairs = mapOf('(' to ')', '[' to ']', '{' to '}')

    for (char in s) {
        when {
            char in pairs.keys -> stack.push(char)
            char in pairs.values -> {
                val top = stack.pop() ?: return false
                if (pairs[top] != char) return false
            }
        }
    }
    return stack.isEmpty()           // O(n) по времени, O(n) по памяти в худшем случае
}
```

**Очереди (Queues):**

*Теория:* Очередь — FIFO структура (First In First Out). Реализуется через связный список (enqueue/dequeue O(1)) или кольцевой буфер. Используется для: BFS, очередей задач, сообщений и т.п.

```kotlin
// ✅ Очередь: FIFO (простая реализация на списке индексов)
class Queue<T> {
    private val items = ArrayList<T>()
    private var head = 0

    fun enqueue(item: T) {           // O(1) амортизированно
        items.add(item)
    }

    fun dequeue(): T? {              // O(1) амортизированно
        if (isEmpty()) return null
        val item = items[head]
        head++
        // Опциональная очистка для избежания утечек
        if (head > items.size / 2) {
            items.subList(0, head).clear()
            head = 0
        }
        return item
    }

    fun peek(): T? = if (isEmpty()) null else items[head]

    fun isEmpty(): Boolean = head >= items.size
}

// Use case: очередь загрузок
class DownloadQueue {
    private val queue = Queue<DownloadTask>()

    fun addDownload(task: DownloadTask) {
        queue.enqueue(task)          // O(1) амортизированно
    }
}
```

**2. Хеш-таблицы (Hash Tables):**

*Теория:* Хеш-таблицы обеспечивают O(1) среднее время операций поиска/вставки/удаления при хорошей хеш-функции и контроле коэффициента заполнения. Коллизии решаются через chaining (списки) или open addressing. В худшем случае при деградации — O(n).

```kotlin
// ✅ Hash Table с chaining (упрощённо)
class HashTable<K, V>(capacity: Int = 16) {
    private val buckets = Array<MutableList<Pair<K, V>>>(capacity) { mutableListOf() }

    private fun hash(key: K): Int {
        val h = key?.hashCode() ?: 0
        return (h and Int.MAX_VALUE) % buckets.size   // нормализация для неотрицательного индекса
    }

    fun put(key: K, value: V) {                      // O(1) в среднем
        val bucket = buckets[hash(key)]
        val i = bucket.indexOfFirst { it.first == key }
        if (i >= 0) {
            bucket[i] = key to value
        } else {
            bucket.add(key to value)
        }
    }

    fun get(key: K): V? {                            // O(1) в среднем, O(n) в худшем
        val bucket = buckets[hash(key)]
        return bucket.firstOrNull { it.first == key }?.second
    }
}

// Use case: LRU Cache (используем LinkedHashMap с accessOrder=true)
class LRUCache<K, V>(private val capacity: Int) {
    private val cache = object : LinkedHashMap<K, V>(capacity, 0.75f, true) {
        override fun removeEldestEntry(eldest: MutableMap.MutableEntry<K, V>?): Boolean {
            return size > capacity
        }
    }

    fun get(key: K): V? = cache[key]                 // O(1) в среднем

    fun put(key: K, value: V) {                      // O(1) в среднем
        cache[key] = value
    }
}
```

**3. Деревья (Trees):**

*Теория:* Деревья — иерархические структуры. Бинарные деревья имеют до 2 потомков. BST (Binary Search Tree) поддерживает свойство: left < node < right. Сбалансированные деревья (AVL, Red-Black и др.) обеспечивают O(log n) для основных операций; несбалансированное BST может деградировать до O(n).

```kotlin
// ✅ BST (несбалансированное, для иллюстрации)
data class TreeNode(val data: Int, var left: TreeNode? = null, var right: TreeNode? = null)

class BinarySearchTree {
    private var root: TreeNode? = null

    fun insert(data: Int) {                            // O(log n) в среднем/сбалансированное, O(n) худший случай
        root = insertHelper(root, data)
    }

    private fun insertHelper(node: TreeNode?, data: Int): TreeNode {
        if (node == null) return TreeNode(data)
        when {
            data < node.data -> node.left = insertHelper(node.left, data)
            data > node.data -> node.right = insertHelper(node.right, data)
        }
        return node
    }

    fun search(data: Int): Boolean {                   // O(log n) в среднем, O(n) худший случай
        var current = root
        while (current != null) {
            current = when {
                data < current.data -> current.left
                data > current.data -> current.right
                else -> return true
            }
        }
        return false
    }
}

// Сложность (BST):
// Search/Insert/Delete: O(log n) в среднем/сбалансированное, O(n) в худшем случае
// Обход (inorder/preorder/postorder): O(n)
```

**4. Графы (Graphs):**

*Теория:* Графы представляют сети через вершины (vertices) и рёбра (edges). Список смежности (adjacency list) компактен и эффективен по памяти. Матрица смежности даёт O(1) проверку ребра, но требует O(V²) памяти. Используются для: социальных графов, маршрутизации, зависимостей, рекомендаций.

```kotlin
// ✅ Граф: список смежности + BFS с восстановлением пути
class Graph<T> {
    private val adjacencyList = mutableMapOf<T, MutableList<T>>()

    fun addVertex(vertex: T) {
        adjacencyList.putIfAbsent(vertex, mutableListOf())
    }

    fun addEdge(from: T, to: T) {
        adjacencyList.putIfAbsent(from, mutableListOf())
        adjacencyList.putIfAbsent(to, mutableListOf())
        adjacencyList[from]!!.add(to)
        adjacencyList[to]!!.add(from)   // Ненаправленный граф
    }

    fun bfs(start: T, target: T): List<T> {           // O(V + E)
        if (start == target) return listOf(start)

        val queue = Queue<T>()
        val visited = mutableSetOf<T>()
        val parent = mutableMapOf<T, T>()

        queue.enqueue(start)
        visited.add(start)

        while (!queue.isEmpty()) {
            val current = queue.dequeue() ?: break
            if (current == target) {
                return reconstructPath(parent, start, target)
            }
            adjacencyList[current]?.forEach { neighbor ->
                if (neighbor !in visited) {
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.enqueue(neighbor)
                }
            }
        }
        return emptyList()
    }

    private fun reconstructPath(parent: Map<T, T>, start: T, target: T): List<T> {
        val path = mutableListOf<T>()
        var cur: T? = target
        while (cur != null) {
            path.add(cur)
            if (cur == start) break
            cur = parent[cur]
        }
        path.reverse()
        return if (path.firstOrNull() == start) path else emptyList()
    }
}

// Сложность:
// BFS/DFS: O(V + E)
// Кратчайший путь в невзвешенном графе: BFS, O(V + E)
// Кратчайший путь в взвешенном графе (Dijkstra с очередью с приоритетом): O(E log V)
```

**5. Сложность алгоритмов (Big O):**

*Теория:* Big O описывает асимптотический рост времени или памяти в зависимости от размера входа и, как правило, используется для верхней оценки (худший случай). Часто также указывают средний случай (average-case) отдельно.

Примеры:
- O(1): доступ к элементу массива по индексу.
- O(log n): бинарный поиск.
- O(n): линейный проход по массиву.
- O(n log n): эффективные сортировки (MergeSort, HeapSort, QuickSort в среднем).
- O(n²): вложенные циклы по всем парам элементов.

Сводная таблица (типичные оценки):

| Структура   | Access       | Search                 | Insert                               | Delete                               | Space |
|------------|--------------|------------------------|--------------------------------------|--------------------------------------|-------|
| Array      | O(1)         | O(n)                   | O(n) (в середину), O(1)* в конец    | O(n)                                 | O(n) |
| `LinkedList` | O(n)         | O(n)                   | O(1) при известном месте             | O(1) при известном месте             | O(n) |
| `Stack`      | O(1) (top)   | - (через pop: O(n))    | O(1)                                 | O(1)                                 | O(n) |
| `Queue`      | O(1) (front) | - (через dequeue: O(n))| O(1)                                 | O(1)                                 | O(n) |
| HashTable  | -            | O(1) avg, O(n) worst   | O(1) avg, O(n) worst                 | O(1) avg, O(n) worst                 | O(n) |
| BST (bal.) | O(log n)     | O(log n)               | O(log n)                             | O(log n)                             | O(n) |

*O(1) амортизированно при динамическом массиве.

**6. Алгоритмы сортировки:**

*Теория:*
- QuickSort — разделяй и властвуй, выбор опорного элемента. Среднее O(n log n), худшее O(n²), in-place, обычно не стабильный.
- MergeSort — стабильный, гарантированно O(n log n), требует O(n) дополнительной памяти.
- HeapSort — in-place, гарантированно O(n log n), обычно не стабильный.
Выбор зависит от требований к стабильности, памяти и худшему случаю.

**7. Алгоритмы поиска:**

*Теория:*
- Линейный поиск: O(n), подходит для неотсортированных коллекций.
- Бинарный поиск: O(log n), применим только для отсортированных массивов/списков с произвольным доступом.
- BFS и DFS для графов: O(V + E), выбор зависит от задачи (поиск кратчайшего пути в невзвешенном графе, проверка связности, топологическая сортировка и т.д.).

**Ключевые концепции:**

1. Trade-offs — каждая структура имеет преимущества и ограничения.
2. Usage patterns — выбор зависит от частоты операций и требований.
3. Complexity analysis — учитывайте худший и средний случаи.
4. Memory usage — пространство так же важно, как время.
5. Practical constraints — кэш, константы, реализация в стандартной библиотеке.

---

## Answer (EN)

**Data Structures Theory:**
Data structures are ways of organizing and storing data for efficient access and modification. Key characteristics: access time, insertion/deletion time, memory usage. Choice of data structure depends on usage patterns. Big O notation describes asymptotic time and space complexity as input size grows (often specifying worst-case and average-case separately).

**1. Linear Data Structures:**

**Arrays:**

*Theory:* Arrays store elements in contiguous memory with O(1) indexed access. Size is fixed (in a plain array) or dynamic with occasional resizing and copying. Cache-friendly due to locality. Used when you need random access and size is known or bounded.

```kotlin
// ✅ Arrays: O(1) index access, O(n) insert/delete from middle
class ArrayOperations {
    fun demonstrateArrays() {
        val fixedArray = IntArray(5) { it * 2 }  // [0, 2, 4, 6, 8]
        val element = fixedArray[2]              // O(1) access

        val dynamicArray = mutableListOf<Int>()
        dynamicArray.add(10)                     // Amortized O(1) append
        dynamicArray.add(0, 5)                   // O(n) insert at start
    }
}

// Complexity (dynamic array):
// Access by index: O(1)
// Search by value: O(n)
// Insert at end: amortized O(1), worst O(n) on resize
// Insert/delete in middle or at start: O(n)
```

**Linked Lists:**

*Theory:* Linked lists store elements in nodes with pointers. Singly-linked (next) or doubly-linked (prev + next). Indexed access is O(n) due to traversal. Insertion/deletion at head is O(1); insertion/deletion given a node reference is O(1). Used for dynamic collections with frequent insertions/deletions.

```kotlin
// ✅ Singly-linked list (simplified)
data class Node<T>(var data: T, var next: Node<T>? = null)

class LinkedList<T> {
    private var head: Node<T>? = null
    private var tail: Node<T>? = null

    fun addFirst(data: T) {                  // O(1)
        head = Node(data, head)
        if (tail == null) tail = head
    }

    fun addLast(data: T) {                   // O(1) with tail reference
        val newNode = Node(data)
        if (tail == null) {
            head = newNode
            tail = newNode
        } else {
            tail!!.next = newNode
            tail = newNode
        }
    }
}

// Complexity:
// Access by index: O(n)
// Search by value: O(n)
// Insert/delete at head or after a known node: O(1)
// Insert/delete by index: O(n) (need to find node)
```

**Stacks:**

*Theory:* `Stack` is a LIFO (Last In, First Out) structure. Implemented via arrays or linked lists. Operations `push`, `pop`, and `peek` are O(1). Used for expression evaluation, backtracking, navigation history, call stack.

```kotlin
// ✅ Stack: LIFO
class Stack<T> {
    private val items = mutableListOf<T>()

    fun push(item: T) {                      // O(1)
        items.add(item)
    }

    fun pop(): T? =                          // O(1)
        if (items.isNotEmpty()) items.removeAt(items.lastIndex) else null

    fun peek(): T? =                         // O(1)
        items.lastOrNull()

    fun isEmpty(): Boolean = items.isEmpty()
}

// Use case: Balanced parentheses
fun isBalanced(s: String): Boolean {
    val stack = Stack<Char>()
    val pairs = mapOf('(' to ')', '[' to ']', '{' to '}')

    for (char in s) {
        when {
            char in pairs.keys -> stack.push(char)
            char in pairs.values -> {
                val top = stack.pop() ?: return false
                if (pairs[top] != char) return false
            }
        }
    }
    return stack.isEmpty()                   // O(n) time, O(n) space worst-case
}
```

**Queues:**

*Theory:* `Queue` is a FIFO (First In, First Out) structure. Implemented via linked lists (enqueue/dequeue O(1)) or circular arrays. Used for BFS traversal, task scheduling, message queues, etc.

```kotlin
// ✅ Queue: FIFO (simple amortized O(1) implementation)
class Queue<T> {
    private val items = ArrayList<T>()
    private var head = 0

    fun enqueue(item: T) {                   // Amortized O(1)
        items.add(item)
    }

    fun dequeue(): T? {                      // Amortized O(1)
        if (isEmpty()) return null
        val item = items[head]
        head++
        if (head > items.size / 2) {
            items.subList(0, head).clear()
            head = 0
        }
        return item
    }

    fun peek(): T? = if (isEmpty()) null else items[head]

    fun isEmpty(): Boolean = head >= items.size
}

// Use case: Download queue
class DownloadQueue {
    private val queue = Queue<DownloadTask>()

    fun addDownload(task: DownloadTask) {
        queue.enqueue(task)
    }
}
```

**2. Hash Tables:**

*Theory:* Hash tables provide O(1) average-case lookup/insert/delete using hash functions and buckets. Collisions are resolved via chaining or open addressing. Load factor affects performance; worst-case operations can degrade to O(n).

```kotlin
// ✅ Hash Table with chaining (simplified)
class HashTable<K, V>(capacity: Int = 16) {
    private val buckets = Array<MutableList<Pair<K, V>>>(capacity) { mutableListOf() }

    private fun hash(key: K): Int {
        val h = key?.hashCode() ?: 0
        return (h and Int.MAX_VALUE) % buckets.size  // ensure non-negative index
    }

    fun put(key: K, value: V) {                      // O(1) average
        val bucket = buckets[hash(key)]
        val i = bucket.indexOfFirst { it.first == key }
        if (i >= 0) bucket[i] = key to value else bucket.add(key to value)
    }

    fun get(key: K): V? {                            // O(1) average, O(n) worst
        val bucket = buckets[hash(key)]
        return bucket.firstOrNull { it.first == key }?.second
    }
}

// Use case: LRU Cache using LinkedHashMap with access-order
class LRUCache<K, V>(private val capacity: Int) {
    private val cache = object : LinkedHashMap<K, V>(capacity, 0.75f, true) {
        override fun removeEldestEntry(eldest: MutableMap.MutableEntry<K, V>?): Boolean {
            return size > capacity
        }
    }

    fun get(key: K): V? = cache[key]                 // O(1) average

    fun put(key: K, value: V) {                      // O(1) average
        cache[key] = value
    }
}
```

**3. Trees:**

*Theory:* Trees are hierarchical structures. Binary trees have up to 2 children per node. A BST (Binary Search Tree) maintains the invariant left < node < right. Balanced trees (AVL, Red-Black, etc.) guarantee O(log n) operations; an unbalanced BST can degrade to O(n).

```kotlin
// ✅ BST (unbalanced, for illustration)
data class TreeNode(val data: Int, var left: TreeNode? = null, var right: TreeNode? = null)

class BinarySearchTree {
    private var root: TreeNode? = null

    fun insert(data: Int) {                            // O(log n) avg/balanced, O(n) worst
        root = insertHelper(root, data)
    }

    private fun insertHelper(node: TreeNode?, data: Int): TreeNode {
        if (node == null) return TreeNode(data)
        when {
            data < node.data -> node.left = insertHelper(node.left, data)
            data > node.data -> node.right = insertHelper(node.right, data)
        }
        return node
    }

    fun search(data: Int): Boolean {                   // O(log n) avg, O(n) worst
        var current = root
        while (current != null) {
            current = when {
                data < current.data -> current.left
                data > current.data -> current.right
                else -> return true
            }
        }
        return false
    }
}

// Complexity (BST):
// Search/Insert/Delete: O(log n) average/balanced, O(n) worst
// Traversal (inorder/preorder/postorder): O(n)
```

**4. Graphs:**

*Theory:* Graphs represent networks via vertices and edges. Adjacency list is memory-efficient; adjacency matrix allows O(1) edge checks at O(V²) space. Used for social networks, routing, dependencies, recommendations, etc.

```kotlin
// ✅ Graph: adjacency list + BFS with path reconstruction
class Graph<T> {
    private val adjacencyList = mutableMapOf<T, MutableList<T>>()

    fun addVertex(vertex: T) {
        adjacencyList.putIfAbsent(vertex, mutableListOf())
    }

    fun addEdge(from: T, to: T) {
        adjacencyList.putIfAbsent(from, mutableListOf())
        adjacencyList.putIfAbsent(to, mutableListOf())
        adjacencyList[from]!!.add(to)
        adjacencyList[to]!!.add(from)   // Undirected graph
    }

    fun bfs(start: T, target: T): List<T> {           // O(V + E)
        if (start == target) return listOf(start)

        val queue = Queue<T>()
        val visited = mutableSetOf<T>()
        val parent = mutableMapOf<T, T>()

        queue.enqueue(start)
        visited.add(start)

        while (!queue.isEmpty()) {
            val current = queue.dequeue() ?: break
            if (current == target) {
                return reconstructPath(parent, start, target)
            }
            adjacencyList[current]?.forEach { neighbor ->
                if (neighbor !in visited) {
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.enqueue(neighbor)
                }
            }
        }
        return emptyList()
    }

    private fun reconstructPath(parent: Map<T, T>, start: T, target: T): List<T> {
        val path = mutableListOf<T>()
        var cur: T? = target
        while (cur != null) {
            path.add(cur)
            if (cur == start) break
            cur = parent[cur]
        }
        path.reverse()
        return if (path.firstOrNull() == start) path else emptyList()
    }
}

// Complexity:
// BFS/DFS: O(V + E)
// Shortest path in unweighted graph: BFS, O(V + E)
// Shortest path in weighted graph (e.g., Dijkstra with priority queue): O(E log V)
```

**5. Algorithm Complexity (Big O):**

*Theory:* Big O describes the asymptotic upper bound of time or space as input size grows. Common classes:
- O(1): constant time — e.g., array index access.
- O(log n): logarithmic — e.g., binary search.
- O(n): linear — e.g., scanning an array.
- O(n log n): linearithmic — e.g., efficient comparison-based sorting.
- O(n²): quadratic — e.g., double nested loops over n elements.
Average-case behavior is often also discussed separately.

Summary table (typical):

| Structure  | Access        | Search                     | Insert                               | Delete                               | Space |
|-----------|---------------|----------------------------|--------------------------------------|--------------------------------------|-------|
| Array     | O(1)          | O(n)                       | O(n) middle, amortized O(1) end     | O(n)                                 | O(n) |
| `LinkedList`| O(n)          | O(n)                       | O(1) at known position               | O(1) at known position               | O(n) |
| `Stack`     | O(1) (top)    | - (via pops: O(n))         | O(1)                                 | O(1)                                 | O(n) |
| `Queue`     | O(1) (front)  | - (via dequeues: O(n))     | O(1)                                 | O(1)                                 | O(n) |
| HashTable | -             | O(1) avg, O(n) worst       | O(1) avg, O(n) worst                 | O(1) avg, O(n) worst                 | O(n) |
| BST (bal.)| O(log n)      | O(log n)                   | O(log n)                             | O(log n)                             | O(n) |

**6. Sorting Algorithms:**

*Theory:*
- QuickSort: divide and conquer, pivot-based partitioning; average O(n log n), worst O(n²); in-place, typically not stable.
- MergeSort: stable; guaranteed O(n log n); requires O(n) extra space.
- HeapSort: in-place; guaranteed O(n log n); typically not stable.
Choice depends on stability, space, and worst-case guarantees.

**7. Search Algorithms:**

*Theory:*
- Linear Search: O(n); works on unsorted collections.
- Binary Search: O(log n); requires sorted array/random access.
- BFS and DFS for graphs: O(V + E); selected based on goals (shortest path in unweighted graphs, connectivity, topological sort, etc.).

**Key Concepts:**

1. Trade-offs — each structure has strengths and limitations.
2. Usage patterns — choose based on operation frequency and constraints.
3. Complexity analysis — consider both worst-case and average-case.
4. Memory usage — space complexity matters.
5. Practical constraints — cache behavior, constants, and standard library implementations.

---

## Дополнительные Вопросы (RU)

- Как вы выбираете между массивом и связным списком для конкретной задачи?
- В чем разница между разрешением коллизий в хеш-таблицах через chaining и open addressing?
- В каких случаях вы выберете BFS, а в каких DFS для обхода графа?

## Follow-ups

- How do you choose between array and linked list for a given problem?
- What is the difference between hash table chaining and open addressing?
- When would you use BFS vs DFS for graph traversal?

## Связанные Вопросы (RU)

### Предпосылки (проще)
- Базовые программные концепции
- Анализ сложности

### Связанные (тот Же уровень)
- [[c-data-structures]] — Концепции структур данных
- [[c-algorithms]] — Концепции алгоритмов

### Продвинутое (сложнее)
- Продвинутые алгоритмы на графах
- Оптимизация динамического программирования
- Распределенные структуры данных

## Related Questions

### Prerequisites (Easier)
- Basic programming concepts
- Complexity analysis

### Related (Same Level)
- [[c-data-structures]] - Data structures concepts
- [[c-algorithms]] - Algorithms concepts

### Advanced (Harder)
- Advanced graph algorithms
- Dynamic programming optimization
- Distributed data structures

## Ссылки (RU)

- [[c-data-structures]]
- [[c-algorithms]]
- https://en.wikipedia.org/wiki/Data_structure

## References

- [[c-data-structures]]
- [[c-algorithms]]
- https://en.wikipedia.org/wiki/Data_structure
