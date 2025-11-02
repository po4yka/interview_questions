---
id: cs-035
title: "Data Structures and Algorithms Fundamentals / Фундаментальные структуры данных и алгоритмы"
aliases: ["Data Structures and Algorithms Fundamentals", "Фундаментальные структуры данных и алгоритмы"]
topic: cs
subtopics: [algorithms, complexity-analysis, data-structures, programming-languages]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-algorithms, c-data-structures, q-sorting-algorithms-comparison--algorithms--medium]
created: "2025-10-13"
updated: 2025-01-25
tags: [algorithms, big-o, complexity, data-structures, difficulty/hard, dynamic-programming, graphs, recursion, searching, sorting, trees]
sources: [https://en.wikipedia.org/wiki/Data_structure]
date created: Monday, October 13th 2025, 8:01:06 am
date modified: Saturday, November 1st 2025, 5:43:28 pm
---

# Вопрос (RU)
> Объясните фундаментальные структуры данных и алгоритмы. Какие особенности у каждой структуры и когда их использовать?

# Question (EN)
> Explain fundamental data structures and algorithms. What are the characteristics of each structure and when to use them?

---

## Ответ (RU)

**Теория структур данных:**
Структуры данных — это способы организации и хранения данных для эффективного доступа и модификации. Основные характеристики: время доступа, время вставки/удаления, использование памяти. Выбор структуры данных зависит от паттернов использования. Big O нотация описывает асимптотическую сложность алгоритмов.

**1. Линейные структуры данных:**

**Массивы (Arrays):**

*Теория:* Массивы хранят элементы в contiguous memory с O(1) доступом по индексу. Фиксированный размер или dynamic с копированием. Cache-friendly благодаря locality. Используются для коллекций с известным размером, произвольным доступом.

```kotlin
// ✅ Массивы: O(1) доступ, O(n) вставка/удаление
class ArrayOperations {
    fun demonstrateArrays() {
        val fixedArray = IntArray(5) { it * 2 }  // [0, 2, 4, 6, 8]
        val element = fixedArray[2]  // O(1) доступ

        val dynamicArray = mutableListOf<Int>()
        dynamicArray.add(10)  // O(1) добавление в конец
        dynamicArray.add(0, 5)  // O(n) вставка в начало
    }
}

// Use case: RecyclerView adapter
class TodoAdapter(private val items: MutableList<Todo>) {
    // O(1) доступ для binding
    override fun onBindViewHolder(holder: TodoViewHolder, position: Int) {
        holder.bind(items[position])
    }
}

// Сложность:
// Доступ: O(1)
// Поиск: O(n)
// Вставка в конец: O(1) amortized
// Вставка в середину: O(n)
// Удаление: O(n)
```

**Связные списки (Linked Lists):**

*Теория:* Связные списки хранят элементы в узлах с указателями. Односвязные (next pointer) или двусвязные (prev + next pointers). Доступ O(n) из-за последовательного прохода. Вставка/удаление в начало O(1). Используются для динамических коллекций, frequent insertions/deletions.

```kotlin
// ✅ Односвязный список
data class Node<T>(var data: T, var next: Node<T>? = null)

class LinkedList<T> {
    private var head: Node<T>? = null
    private var tail: Node<T>? = null

    fun addFirst(data: T) {  // O(1)
        head = Node(data, head)
        if (tail == null) tail = head
    }

    fun addLast(data: T) {  // O(1)
        val newNode = Node(data)
        tail?.next = newNode
        tail = newNode
    }
}

// Use case: Undo/Redo stack
class UndoRedoManager {
    private val undoStack = LinkedList<String>()

    fun execute(action: String) {  // O(1)
        undoStack.addFirst(action)
    }
}

// Сложность:
// Доступ: O(n)
// Вставка в начало: O(1)
// Вставка в конец: O(1) с tail pointer
```

**Стеки (Stacks):**

*Теория:* Стеки - LIFO структура (Last In First Out). Реализованы через массивы или linked lists. Операции: push O(1), pop O(1), peek O(1). Используются для: expression evaluation, backtracking, navigation back stack, call stack.

```kotlin
// ✅ Стек: LIFO
class Stack<T> {
    private val items = mutableListOf<T>()

    fun push(item: T) = items.add(item)  // O(1)
    fun pop(): T? = items.removeLastOrNull()  // O(1)
    fun peek(): T? = items.lastOrNull()  // O(1)
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
    return stack.isEmpty()  // O(n) time
}
```

**Очереди (Queues):**

*Теория:* Очереди - FIFO структура (First In First Out). Реализованы через linked lists (enqueue O(1), dequeue O(1)) или circular arrays. Используются для: BFS traversal, task scheduling, message queues, print queues.

```kotlin
// ✅ Очередь: FIFO
class Queue<T> {
    private val items = LinkedList<T>()

    fun enqueue(item: T) = items.addLast(item)  // O(1)
    fun dequeue(): T? = items.removeFirst()  // O(1)
    fun peek(): T? = items.firstOrNull()  // O(1)
}

// Use case: Download queue
class DownloadQueue {
    private val queue = Queue<DownloadTask>()

    fun addDownload(task: DownloadTask) {
        queue.enqueue(task)  // O(1)
    }

    private fun processNext() {
        val task = queue.dequeue() ?: return
        task.execute { processNext() }
    }
}
```

**2. Хеш-таблицы (Hash Tables):**

*Теория:* Хеш-таблицы обеспечивают O(1) средний случай lookup с использованием hash functions. Коллизии решаются через chaining (linked list) или open addressing (linear probing, double hashing). Load factor влияет на performance. Используются для: key-value storage, caches, dictionaries, frequency counting.

```kotlin
// ✅ Hash Table с chaining
class HashTable<K, V>(capacity: Int = 16) {
    private val buckets = Array<MutableList<Pair<K, V>>>(capacity) { mutableListOf() }

    private fun hash(key: K): Int = key.hashCode() % buckets.size

    fun put(key: K, value: V) {  // O(1) average
        val bucket = buckets[hash(key)]
        val existing = bucket.indexOfFirst { it.first == key }

        if (existing >= 0) {
            bucket[existing] = key to value
        } else {
            bucket.add(key to value)
        }
    }

    fun get(key: K): V? {  // O(1) average, O(n) worst
        return buckets[hash(key)].firstOrNull { it.first == key }?.second
    }
}

// Use case: LRU Cache
class LRUCache<K, V>(capacity: Int) {
    private val cache = LinkedHashMap<K, V>(capacity, 0.75f, true)

    fun get(key: K): V? = cache[key]  // O(1)

    fun put(key: K, value: V) {  // O(1)
        if (cache.size >= capacity && !cache.containsKey(key)) {
            cache.remove(cache.keys.first())
        }
        cache[key] = value
    }
}
```

**3. Деревья (Trees):**

*Теория:* Деревья - иерархические структуры. Binary trees имеют ≤2 children per node. BST (Binary Search Tree) поддерживает left < node < right property. Сбалансированные деревья (AVL, Red-Black) обеспечивают O(log n) операции. Используются для: hierarchical data, search optimization, priority queues, syntax trees.

```kotlin
// ✅ BST
data class TreeNode(val data: Int, var left: TreeNode? = null, var right: TreeNode? = null)

class BinarySearchTree {
    private var root: TreeNode? = null

    fun insert(data: Int) {  // O(log n) balanced, O(n) worst
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

    fun search(data: Int): Boolean {  // O(log n) balanced
        return searchHelper(root, data)
    }

    private fun searchHelper(node: TreeNode?, data: Int): Boolean {
        if (node == null) return false
        return when {
            data == node.data -> true
            data < node.data -> searchHelper(node.left, data)
            else -> searchHelper(node.right, data)
        }
    }
}

// Сложность:
// Search/Insert/Delete: O(log n) balanced, O(n) unbalanced
// Inorder traversal: O(n)
```

**4. Графы (Graphs):**

*Теория:* Графы представляют networks через vertices и edges. Adjacency list (список соседей для каждой вершины) compact и efficient. Adjacency matrix O(1) edge lookup, но O(V²) память. Используются для: social networks, routing, dependencies, recommendations.

```kotlin
// ✅ Граф: Adjacency List
class Graph<T> {
    private val adjacencyList = mutableMapOf<T, MutableList<T>>()

    fun addVertex(vertex: T) {
        adjacencyList[vertex] = mutableListOf()
    }

    fun addEdge(from: T, to: T) {
        adjacencyList[from]?.add(to)
        adjacencyList[to]?.add(from)  // Undirected
    }

    fun bfs(start: T, target: T): List<T> {  // O(V + E)
        val queue = Queue<T>()
        val visited = mutableSetOf<T>()
        val path = mutableMapOf<T, T>()

        queue.enqueue(start)
        visited.add(start)

        while (!queue.isEmpty) {
            val current = queue.dequeue()!!
            if (current == target) {
                return reconstructPath(path, start, target)
            }

            adjacencyList[current]?.forEach { neighbor ->
                if (!visited.contains(neighbor)) {
                    visited.add(neighbor)
                    path[neighbor] = current
                    queue.enqueue(neighbor)
                }
            }
        }
        return emptyList()
    }
}

// Сложность:
// BFS/DFS: O(V + E)
// Shortest path: O(E log V) с priority queue
```

**5. Сложность алгоритмов (Big O):**

*Теория:* Big O описывает worst-case asymptotic behavior. O(1) constant - доступ к массиву. O(log n) logarithmic - binary search. O(n) linear - traversing array. O(n log n) linearithmic - efficient sorting. O(n²) quadratic - nested loops. Важны и time, и space complexity.

| Структура | Access | Search | Insert | Delete | Space |
|-----------|--------|--------|--------|--------|-------|
| Array | O(1) | O(n) | O(n) | O(n) | O(n) |
| LinkedList | O(n) | O(n) | O(1) | O(1) | O(n) |
| Stack | O(n) | O(n) | O(1) | O(1) | O(n) |
| Queue | O(n) | O(n) | O(1) | O(1) | O(n) |
| HashTable | O(1) | O(1) | O(1) | O(1) | O(n) |
| BST | O(log n) | O(log n) | O(log n) | O(log n) | O(n) |

**6. Алгоритмы сортировки:**

*Теория:* QuickSort - divide and conquer, pivot element, O(n log n) average, O(n²) worst. MergeSort - stable, guaranteed O(n log n), O(n) space. HeapSort - in-place, guaranteed O(n log n), не stable. Выбор зависит от requirements (stability, space, worst-case guarantee).

**7. Алгоритмы поиска:**

*Теория:* Linear Search O(n) - простой, но медленный. Binary Search O(log n) - только для sorted arrays. BFS и DFS для графов - зависит от структуры и целей (shortest path vs connectivity).

**Ключевые концепции:**

1. **Trade-offs** - каждая структура имеет преимущества/недостатки
2. **Patterns Usage** - выбор зависит от операций
3. **Complexity Analysis** - важны worst-case и average-case
4. **Memory Usage** - учитывать space complexity
5. **Practical Constraints** - cache effects, actual performance

## Answer (EN)

**Data Structures Theory:**
Data structures are ways of organizing and storing data for efficient access and modification. Main characteristics: access time, insertion/deletion time, memory usage. Choice of data structure depends on usage patterns. Big O notation describes asymptotic complexity of algorithms.

**1. Linear Data Structures:**

**Arrays:**

*Theory:* Arrays store elements in contiguous memory with O(1) indexed access. Fixed size or dynamic with copying. Cache-friendly due to locality. Used for collections with known size, random access.

```kotlin
// ✅ Arrays: O(1) access, O(n) insertion/deletion
class ArrayOperations {
    fun demonstrateArrays() {
        val fixedArray = IntArray(5) { it * 2 }  // [0, 2, 4, 6, 8]
        val element = fixedArray[2]  // O(1) access

        val dynamicArray = mutableListOf<Int>()
        dynamicArray.add(10)  // O(1) append to end
        dynamicArray.add(0, 5)  // O(n) insert at start
    }
}

// Complexity:
// Access: O(1)
// Search: O(n)
// Insert at end: O(1) amortized
// Insert in middle: O(n)
// Delete: O(n)
```

**Linked Lists:**

*Theory:* Linked lists store elements in nodes with pointers. Singly-linked (next pointer) or doubly-linked (prev + next pointers). Access O(n) due to sequential traversal. Insertion/deletion at start O(1). Used for dynamic collections, frequent insertions/deletions.

```kotlin
// ✅ Singly-linked list
data class Node<T>(var data: T, var next: Node<T>? = null)

class LinkedList<T> {
    private var head: Node<T>? = null
    private var tail: Node<T>? = null

    fun addFirst(data: T) {  // O(1)
        head = Node(data, head)
        if (tail == null) tail = head
    }

    fun addLast(data: T) {  // O(1)
        val newNode = Node(data)
        tail?.next = newNode
        tail = newNode
    }
}

// Complexity:
// Access: O(n)
// Insert at start: O(1)
// Insert at end: O(1) with tail pointer
```

**Stacks:**

*Theory:* Stacks - LIFO structure (Last In First Out). Implemented via arrays or linked lists. Operations: push O(1), pop O(1), peek O(1). Used for: expression evaluation, backtracking, navigation back stack, call stack.

```kotlin
// ✅ Stack: LIFO
class Stack<T> {
    private val items = mutableListOf<T>()

    fun push(item: T) = items.add(item)  // O(1)
    fun pop(): T? = items.removeLastOrNull()  // O(1)
    fun peek(): T? = items.lastOrNull()  // O(1)
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
    return stack.isEmpty()  // O(n) time
}
```

**Queues:**

*Theory:* Queues - FIFO structure (First In First Out). Implemented via linked lists (enqueue O(1), dequeue O(1)) or circular arrays. Used for: BFS traversal, task scheduling, message queues, print queues.

```kotlin
// ✅ Queue: FIFO
class Queue<T> {
    private val items = LinkedList<T>()

    fun enqueue(item: T) = items.addLast(item)  // O(1)
    fun dequeue(): T? = items.removeFirst()  // O(1)
    fun peek(): T? = items.firstOrNull()  // O(1)
}

// Use case: Download queue
class DownloadQueue {
    private val queue = Queue<DownloadTask>()

    fun addDownload(task: DownloadTask) {
        queue.enqueue(task)  // O(1)
    }
}
```

**2. Hash Tables:**

*Theory:* Hash tables provide O(1) average case lookup using hash functions. Collisions resolved via chaining (linked list) or open addressing (linear probing, double hashing). Load factor affects performance. Used for: key-value storage, caches, dictionaries, frequency counting.

```kotlin
// ✅ Hash Table with chaining
class HashTable<K, V>(capacity: Int = 16) {
    private val buckets = Array<MutableList<Pair<K, V>>>(capacity) { mutableListOf() }

    private fun hash(key: K): Int = key.hashCode() % buckets.size

    fun put(key: K, value: V) {  // O(1) average
        val bucket = buckets[hash(key)]
        val existing = bucket.indexOfFirst { it.first == key }

        if (existing >= 0) {
            bucket[existing] = key to value
        } else {
            bucket.add(key to value)
        }
    }

    fun get(key: K): V? {  // O(1) average, O(n) worst
        return buckets[hash(key)].firstOrNull { it.first == key }?.second
    }
}
```

**3. Trees:**

*Theory:* Trees - hierarchical structures. Binary trees have ≤2 children per node. BST (Binary Search Tree) maintains left < node < right property. Balanced trees (AVL, Red-Black) ensure O(log n) operations. Used for: hierarchical data, search optimization, priority queues, syntax trees.

```kotlin
// ✅ BST
data class TreeNode(val data: Int, var left: TreeNode? = null, var right: TreeNode? = null)

class BinarySearchTree {
    private var root: TreeNode? = null

    fun insert(data: Int) {  // O(log n) balanced, O(n) worst
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
}

// Complexity:
// Search/Insert/Delete: O(log n) balanced, O(n) unbalanced
```

**4. Graphs:**

*Theory:* Graphs represent networks through vertices and edges. Adjacency list (list of neighbors for each vertex) compact and efficient. Adjacency matrix O(1) edge lookup, but O(V²) memory. Used for: social networks, routing, dependencies, recommendations.

```kotlin
// ✅ Graph: Adjacency List
class Graph<T> {
    private val adjacencyList = mutableMapOf<T, MutableList<T>>()

    fun addVertex(vertex: T) {
        adjacencyList[vertex] = mutableListOf()
    }

    fun addEdge(from: T, to: T) {
        adjacencyList[from]?.add(to)
        adjacencyList[to]?.add(from)  // Undirected
    }

    fun bfs(start: T, target: T): List<T> {  // O(V + E)
        val queue = Queue<T>()
        val visited = mutableSetOf<T>()
        // ... BFS implementation
    }
}

// Complexity:
// BFS/DFS: O(V + E)
```

**5. Algorithm Complexity (Big O):**

*Theory:* Big O describes worst-case asymptotic behavior. O(1) constant - array access. O(log n) logarithmic - binary search. O(n) linear - traversing array. O(n log n) linearithmic - efficient sorting. O(n²) quadratic - nested loops. Both time and space complexity matter.

**6. Sorting Algorithms:**

*Theory:* QuickSort - divide and conquer, pivot element, O(n log n) average, O(n²) worst. MergeSort - stable, guaranteed O(n log n), O(n) space. HeapSort - in-place, guaranteed O(n log n), not stable. Choice depends on requirements (stability, space, worst-case guarantee).

**7. Search Algorithms:**

*Theory:* Linear Search O(n) - simple but slow. Binary Search O(log n) - only for sorted arrays. BFS and DFS for graphs - depends on structure and goals (shortest path vs connectivity).

**Key Concepts:**

1. **Trade-offs** - each structure has advantages/disadvantages
2. **Patterns Usage** - choice depends on operations
3. **Complexity Analysis** - consider worst-case and average-case
4. **Memory Usage** - consider space complexity
5. **Practical Constraints** - cache effects, actual performance

---

## Follow-ups

- How do you choose between array and linked list for a given problem?
- What is the difference between hash table chaining and open addressing?
- When would you use BFS vs DFS for graph traversal?

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
