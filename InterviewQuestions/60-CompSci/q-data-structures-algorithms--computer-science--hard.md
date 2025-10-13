# Data Structures and Algorithms Fundamentals

---
id: "20251013-600005"
title: "Data Structures and Algorithms Fundamentals"
description: "Comprehensive coverage of fundamental data structures (arrays, linked lists, stacks, queues, trees, graphs, hash tables) and core algorithms (sorting, searching, recursion, dynamic programming) with time/space complexity analysis"
topic: cs
subcategory: "algorithms"
difficulty: "hard"
tags: ["data-structures", "algorithms", "complexity", "big-o", "sorting", "searching", "trees", "graphs", "dynamic-programming", "recursion", "kotlin"]
created: "2025-10-13"
updated: "2025-10-13"
moc: moc-cs
related_questions:
  - "20251012-600003"  # Concurrency Fundamentals
  - "20251012-600004"  # OOP Principles
language: "en"
---

## Question

**English:**
Explain the fundamental data structures and algorithms that every software engineer should know. Cover:

1. Core data structures: Arrays, Linked Lists, Stacks, Queues, Trees, Graphs, Hash Tables
2. Time and Space Complexity analysis (Big O notation)
3. Essential algorithms: Sorting (Quick Sort, Merge Sort, Heap Sort), Searching (Binary Search, BFS, DFS)
4. Recursion and Dynamic Programming
5. Common algorithm patterns and when to use each data structure
6. Real-world applications in Android development

Provide production Kotlin code examples with complexity analysis.

**Russian:**
Объясните фундаментальные структуры данных и алгоритмы, которые должен знать каждый инженер. Охватите:

1. Основные структуры данных: Массивы, Связные списки, Стеки, Очереди, Деревья, Графы, Хеш-таблицы
2. Анализ временной и пространственной сложности (нотация Big O)
3. Основные алгоритмы: Сортировки (Quick Sort, Merge Sort, Heap Sort), Поиск (Binary Search, BFS, DFS)
4. Рекурсия и Динамическое программирование
5. Распространенные паттерны алгоритмов и когда использовать каждую структуру данных
6. Реальные применения в Android-разработке

Предоставьте production Kotlin код с анализом сложности.

---

## Answer

### 1. Core Data Structures / Основные Структуры Данных

#### 1.1 Arrays / Массивы

**English:**
Arrays store elements in contiguous memory locations with O(1) access time.

**Russian:**
Массивы хранят элементы в смежных областях памяти с O(1) временем доступа.

```kotlin
// ✅ Arrays: O(1) access, O(n) insertion/deletion
class ArrayOperations {
    fun demonstrateArrays() {
        // Fixed size array
        val fixedArray = IntArray(5) { it * 2 } // [0, 2, 4, 6, 8]

        // Access: O(1)
        val element = fixedArray[2] // 4

        // Dynamic array (ArrayList)
        val dynamicArray = mutableListOf<Int>()

        // Append at end: Amortized O(1)
        dynamicArray.add(10)

        // Insert at beginning: O(n) - shifts all elements
        dynamicArray.add(0, 5)

        // Remove: O(n) - shifts elements
        dynamicArray.removeAt(0)

        // Search: O(n) - linear scan
        val found = dynamicArray.contains(10)
    }

    // Real Android example: RecyclerView data
    class TodoAdapter(private val items: MutableList<Todo>) :
        RecyclerView.Adapter<TodoViewHolder>() {

        // O(1) access for binding
        override fun onBindViewHolder(holder: TodoViewHolder, position: Int) {
            holder.bind(items[position])
        }

        // O(n) worst case for insertion
        fun addItem(todo: Todo) {
            items.add(todo)
            notifyItemInserted(items.size - 1)
        }

        // O(n) for removal
        fun removeItem(position: Int) {
            items.removeAt(position)
            notifyItemRemoved(position)
        }

        override fun getItemCount() = items.size
    }
}

// Complexity Summary:
// Access:      O(1)
// Search:      O(n)
// Insert End:  O(1) amortized
// Insert Mid:  O(n)
// Delete:      O(n)
```

#### 1.2 Linked Lists / Связные Списки

**English:**
Linked Lists store elements in nodes with pointers to the next/previous node.

**Russian:**
Связные списки хранят элементы в узлах с указателями на следующий/предыдущий узел.

```kotlin
// ✅ Singly Linked List
class LinkedList<T> {
    private data class Node<T>(
        var data: T,
        var next: Node<T>? = null
    )

    private var head: Node<T>? = null
    private var tail: Node<T>? = null
    private var size = 0

    // Insert at beginning: O(1)
    fun addFirst(data: T) {
        val newNode = Node(data, head)
        head = newNode
        if (tail == null) {
            tail = head
        }
        size++
    }

    // Insert at end: O(1) with tail pointer
    fun addLast(data: T) {
        val newNode = Node(data)
        if (tail == null) {
            head = newNode
            tail = newNode
        } else {
            tail?.next = newNode
            tail = newNode
        }
        size++
    }

    // Delete first: O(1)
    fun removeFirst(): T? {
        val data = head?.data
        head = head?.next
        if (head == null) {
            tail = null
        }
        if (data != null) size--
        return data
    }

    // Search: O(n)
    fun contains(data: T): Boolean {
        var current = head
        while (current != null) {
            if (current.data == data) return true
            current = current.next
        }
        return false
    }

    // Get by index: O(n)
    fun get(index: Int): T? {
        if (index < 0 || index >= size) return null
        var current = head
        repeat(index) {
            current = current?.next
        }
        return current?.data
    }
}

// Real Android example: Undo/Redo stack
class UndoRedoManager<T> {
    private val undoStack = LinkedList<T>()
    private val redoStack = LinkedList<T>()

    fun execute(action: T) {
        undoStack.addFirst(action) // O(1)
        redoStack.clear() // Clear redo on new action
    }

    fun undo(): T? {
        val action = undoStack.removeFirst() // O(1)
        action?.let { redoStack.addFirst(it) }
        return action
    }

    fun redo(): T? {
        val action = redoStack.removeFirst() // O(1)
        action?.let { undoStack.addFirst(it) }
        return action
    }
}

// Complexity Summary:
// Access:          O(n)
// Search:          O(n)
// Insert First:    O(1)
// Insert Last:     O(1) with tail
// Delete First:    O(1)
// Delete Last:     O(n) in singly linked list
```

#### 1.3 Stacks / Стеки

**English:**
LIFO (Last In First Out) data structure.

**Russian:**
LIFO (Последний Вошел Первый Вышел) структура данных.

```kotlin
// ✅ Stack implementation
class Stack<T> {
    private val items = mutableListOf<T>()

    // Push: O(1)
    fun push(item: T) {
        items.add(item)
    }

    // Pop: O(1)
    fun pop(): T? {
        if (isEmpty()) return null
        return items.removeAt(items.size - 1)
    }

    // Peek: O(1)
    fun peek(): T? = items.lastOrNull()

    fun isEmpty(): Boolean = items.isEmpty()

    fun size(): Int = items.size
}

// Real Android example: Navigation stack
class NavigationStack {
    private val screenStack = Stack<Screen>()

    fun navigateTo(screen: Screen) {
        screenStack.push(screen) // O(1)
    }

    fun navigateBack(): Screen? {
        return screenStack.pop() // O(1)
    }

    fun getCurrentScreen(): Screen? {
        return screenStack.peek() // O(1)
    }
}

// Classic problem: Balanced Parentheses
fun isBalanced(expression: String): Boolean {
    val stack = Stack<Char>()
    val pairs = mapOf('(' to ')', '[' to ']', '{' to '}')

    for (char in expression) {
        when {
            char in pairs.keys -> stack.push(char)
            char in pairs.values -> {
                val top = stack.pop() ?: return false
                if (pairs[top] != char) return false
            }
        }
    }

    return stack.isEmpty()
}

// Test
fun testBalanced() {
    println(isBalanced("({[]})"))    // true
    println(isBalanced("({[})"))     // false
    println(isBalanced("((()))"))    // true
}

// Complexity Summary:
// Push:    O(1)
// Pop:     O(1)
// Peek:    O(1)
// Space:   O(n)
```

#### 1.4 Queues / Очереди

**English:**
FIFO (First In First Out) data structure.

**Russian:**
FIFO (Первый Вошел Первый Вышел) структура данных.

```kotlin
// ✅ Queue implementation using LinkedList
class Queue<T> {
    private val items = LinkedList<T>()

    // Enqueue: O(1)
    fun enqueue(item: T) {
        items.addLast(item)
    }

    // Dequeue: O(1)
    fun dequeue(): T? {
        return items.removeFirst()
    }

    // Peek: O(1)
    fun peek(): T? = items.firstOrNull()

    fun isEmpty(): Boolean = items.isEmpty()

    fun size(): Int = items.size
}

// Real Android example: Download queue
class DownloadQueue {
    private val queue = Queue<DownloadTask>()
    private var isProcessing = false

    fun addDownload(task: DownloadTask) {
        queue.enqueue(task) // O(1)
        if (!isProcessing) {
            processNext()
        }
    }

    private fun processNext() {
        val task = queue.dequeue() ?: return
        isProcessing = true

        // Process task
        task.execute {
            isProcessing = false
            processNext() // Process next in queue
        }
    }
}

// Priority Queue example
class PriorityQueue<T>(
    private val comparator: Comparator<T>
) {
    private val heap = mutableListOf<T>()

    // Insert: O(log n)
    fun insert(item: T) {
        heap.add(item)
        heapifyUp(heap.size - 1)
    }

    // Extract max/min: O(log n)
    fun extractTop(): T? {
        if (heap.isEmpty()) return null
        if (heap.size == 1) return heap.removeAt(0)

        val top = heap[0]
        heap[0] = heap.removeAt(heap.size - 1)
        heapifyDown(0)
        return top
    }

    // Peek: O(1)
    fun peek(): T? = heap.firstOrNull()

    private fun heapifyUp(index: Int) {
        var current = index
        while (current > 0) {
            val parent = (current - 1) / 2
            if (comparator.compare(heap[current], heap[parent]) <= 0) break
            swap(current, parent)
            current = parent
        }
    }

    private fun heapifyDown(index: Int) {
        var current = index
        while (true) {
            val left = 2 * current + 1
            val right = 2 * current + 2
            var largest = current

            if (left < heap.size &&
                comparator.compare(heap[left], heap[largest]) > 0) {
                largest = left
            }
            if (right < heap.size &&
                comparator.compare(heap[right], heap[largest]) > 0) {
                largest = right
            }

            if (largest == current) break
            swap(current, largest)
            current = largest
        }
    }

    private fun swap(i: Int, j: Int) {
        val temp = heap[i]
        heap[i] = heap[j]
        heap[j] = temp
    }
}

// Real example: Task scheduler by priority
data class Task(val name: String, val priority: Int)

class TaskScheduler {
    private val queue = PriorityQueue<Task>(
        compareByDescending { it.priority }
    )

    fun scheduleTask(task: Task) {
        queue.insert(task) // O(log n)
    }

    fun getNextTask(): Task? {
        return queue.extractTop() // O(log n)
    }
}

// Complexity Summary:
// Regular Queue:
//   Enqueue:     O(1)
//   Dequeue:     O(1)
//   Peek:        O(1)
//
// Priority Queue:
//   Insert:      O(log n)
//   Extract:     O(log n)
//   Peek:        O(1)
```

#### 1.5 Hash Tables / Хеш-таблицы

**English:**
Hash tables provide O(1) average-case lookup using hash functions.

**Russian:**
Хеш-таблицы обеспечивают O(1) поиск в среднем случае используя хеш-функции.

```kotlin
// ✅ Simple Hash Table implementation
class HashTable<K, V>(private val capacity: Int = 16) {
    private data class Entry<K, V>(val key: K, var value: V)

    private val buckets: Array<MutableList<Entry<K, V>>> =
        Array(capacity) { mutableListOf() }

    private var size = 0

    // Hash function
    private fun hash(key: K): Int {
        return (key.hashCode() and 0x7FFFFFFF) % capacity
    }

    // Put: O(1) average, O(n) worst case
    fun put(key: K, value: V) {
        val index = hash(key)
        val bucket = buckets[index]

        // Update if key exists
        for (entry in bucket) {
            if (entry.key == key) {
                entry.value = value
                return
            }
        }

        // Add new entry
        bucket.add(Entry(key, value))
        size++
    }

    // Get: O(1) average, O(n) worst case
    fun get(key: K): V? {
        val index = hash(key)
        val bucket = buckets[index]

        for (entry in bucket) {
            if (entry.key == key) {
                return entry.value
            }
        }

        return null
    }

    // Remove: O(1) average, O(n) worst case
    fun remove(key: K): V? {
        val index = hash(key)
        val bucket = buckets[index]

        val iterator = bucket.iterator()
        while (iterator.hasNext()) {
            val entry = iterator.next()
            if (entry.key == key) {
                iterator.remove()
                size--
                return entry.value
            }
        }

        return null
    }

    fun size(): Int = size
}

// Real Android example: In-memory cache
class ImageCache {
    private val cache = hashMapOf<String, Bitmap>()
    private val maxSize = 50

    // O(1) lookup
    fun get(url: String): Bitmap? {
        return cache[url]
    }

    // O(1) insertion
    fun put(url: String, bitmap: Bitmap) {
        if (cache.size >= maxSize) {
            // Remove oldest (simple LRU would use LinkedHashMap)
            cache.remove(cache.keys.first())
        }
        cache[url] = bitmap
    }
}

// LRU Cache implementation
class LRUCache<K, V>(private val capacity: Int) {
    private val cache = LinkedHashMap<K, V>(capacity, 0.75f, true)

    // O(1) get with access order update
    fun get(key: K): V? {
        return cache[key]
    }

    // O(1) put with eviction if needed
    fun put(key: K, value: V) {
        if (cache.size >= capacity && !cache.containsKey(key)) {
            // Remove eldest entry
            val eldest = cache.entries.first()
            cache.remove(eldest.key)
        }
        cache[key] = value
    }
}

// Complexity Summary:
// Average Case:
//   Insert:      O(1)
//   Lookup:      O(1)
//   Delete:      O(1)
//
// Worst Case (all collisions):
//   Insert:      O(n)
//   Lookup:      O(n)
//   Delete:      O(n)
```

#### 1.6 Trees / Деревья

**English:**
Hierarchical data structures with nodes connected by edges.

**Russian:**
Иерархические структуры данных с узлами, соединенными ребрами.

```kotlin
// ✅ Binary Tree
class BinaryTree<T> {
    data class Node<T>(
        var data: T,
        var left: Node<T>? = null,
        var right: Node<T>? = null
    )

    var root: Node<T>? = null

    // Tree traversals

    // Inorder: Left -> Root -> Right
    fun inorderTraversal(node: Node<T>?, result: MutableList<T> = mutableListOf()): List<T> {
        if (node == null) return result
        inorderTraversal(node.left, result)
        result.add(node.data)
        inorderTraversal(node.right, result)
        return result
    }

    // Preorder: Root -> Left -> Right
    fun preorderTraversal(node: Node<T>?, result: MutableList<T> = mutableListOf()): List<T> {
        if (node == null) return result
        result.add(node.data)
        preorderTraversal(node.left, result)
        preorderTraversal(node.right, result)
        return result
    }

    // Postorder: Left -> Right -> Root
    fun postorderTraversal(node: Node<T>?, result: MutableList<T> = mutableListOf()): List<T> {
        if (node == null) return result
        postorderTraversal(node.left, result)
        postorderTraversal(node.right, result)
        result.add(node.data)
        return result
    }

    // Level order (BFS): Level by level
    fun levelOrderTraversal(): List<T> {
        val result = mutableListOf<T>()
        if (root == null) return result

        val queue = LinkedList<Node<T>>()
        queue.add(root!!)

        while (queue.isNotEmpty()) {
            val node = queue.removeFirst()
            result.add(node.data)

            node.left?.let { queue.add(it) }
            node.right?.let { queue.add(it) }
        }

        return result
    }
}

// ✅ Binary Search Tree (BST)
class BinarySearchTree {
    data class Node(
        var value: Int,
        var left: Node? = null,
        var right: Node? = null
    )

    var root: Node? = null

    // Insert: O(log n) average, O(n) worst case
    fun insert(value: Int) {
        root = insertRecursive(root, value)
    }

    private fun insertRecursive(node: Node?, value: Int): Node {
        if (node == null) return Node(value)

        when {
            value < node.value -> node.left = insertRecursive(node.left, value)
            value > node.value -> node.right = insertRecursive(node.right, value)
        }

        return node
    }

    // Search: O(log n) average, O(n) worst case
    fun search(value: Int): Boolean {
        return searchRecursive(root, value)
    }

    private fun searchRecursive(node: Node?, value: Int): Boolean {
        if (node == null) return false

        return when {
            value == node.value -> true
            value < node.value -> searchRecursive(node.left, value)
            else -> searchRecursive(node.right, value)
        }
    }

    // Delete: O(log n) average, O(n) worst case
    fun delete(value: Int) {
        root = deleteRecursive(root, value)
    }

    private fun deleteRecursive(node: Node?, value: Int): Node? {
        if (node == null) return null

        when {
            value < node.value -> {
                node.left = deleteRecursive(node.left, value)
            }
            value > node.value -> {
                node.right = deleteRecursive(node.right, value)
            }
            else -> {
                // Node with only one child or no child
                if (node.left == null) return node.right
                if (node.right == null) return node.left

                // Node with two children: get inorder successor
                node.value = minValue(node.right!!)
                node.right = deleteRecursive(node.right, node.value)
            }
        }

        return node
    }

    private fun minValue(node: Node): Int {
        var current = node
        while (current.left != null) {
            current = current.left!!
        }
        return current.value
    }
}

// Real Android example: File system tree
data class FileNode(
    val name: String,
    val isDirectory: Boolean,
    val children: MutableList<FileNode> = mutableListOf()
)

class FileSystemTree {
    private val root = FileNode("/", isDirectory = true)

    // DFS to find file: O(n)
    fun findFile(name: String): FileNode? {
        return dfs(root, name)
    }

    private fun dfs(node: FileNode, target: String): FileNode? {
        if (node.name == target) return node

        for (child in node.children) {
            val result = dfs(child, target)
            if (result != null) return result
        }

        return null
    }

    // Get all files at depth: BFS
    fun getFilesAtDepth(depth: Int): List<FileNode> {
        val result = mutableListOf<FileNode>()
        val queue = LinkedList<Pair<FileNode, Int>>()
        queue.add(root to 0)

        while (queue.isNotEmpty()) {
            val (node, currentDepth) = queue.removeFirst()

            if (currentDepth == depth) {
                result.add(node)
            } else if (currentDepth < depth) {
                node.children.forEach { queue.add(it to currentDepth + 1) }
            }
        }

        return result
    }
}

// Complexity Summary:
// BST (balanced):
//   Insert:      O(log n)
//   Search:      O(log n)
//   Delete:      O(log n)
//
// BST (unbalanced):
//   Insert:      O(n)
//   Search:      O(n)
//   Delete:      O(n)
//
// Traversal:     O(n)
```

#### 1.7 Graphs / Графы

**English:**
Graphs represent networks of nodes connected by edges.

**Russian:**
Графы представляют сети узлов, соединенных ребрами.

```kotlin
// ✅ Graph representation (Adjacency List)
class Graph<T> {
    private val adjacencyList = mutableMapOf<T, MutableList<T>>()

    fun addVertex(vertex: T) {
        adjacencyList.putIfAbsent(vertex, mutableListOf())
    }

    fun addEdge(from: T, to: T) {
        adjacencyList[from]?.add(to)
        // For undirected graph, add reverse edge:
        // adjacencyList[to]?.add(from)
    }

    // Breadth-First Search (BFS): O(V + E)
    fun bfs(start: T): List<T> {
        val visited = mutableSetOf<T>()
        val result = mutableListOf<T>()
        val queue = LinkedList<T>()

        queue.add(start)
        visited.add(start)

        while (queue.isNotEmpty()) {
            val vertex = queue.removeFirst()
            result.add(vertex)

            adjacencyList[vertex]?.forEach { neighbor ->
                if (neighbor !in visited) {
                    visited.add(neighbor)
                    queue.add(neighbor)
                }
            }
        }

        return result
    }

    // Depth-First Search (DFS): O(V + E)
    fun dfs(start: T): List<T> {
        val visited = mutableSetOf<T>()
        val result = mutableListOf<T>()

        dfsRecursive(start, visited, result)

        return result
    }

    private fun dfsRecursive(vertex: T, visited: MutableSet<T>, result: MutableList<T>) {
        visited.add(vertex)
        result.add(vertex)

        adjacencyList[vertex]?.forEach { neighbor ->
            if (neighbor !in visited) {
                dfsRecursive(neighbor, visited, result)
            }
        }
    }

    // Shortest path (BFS for unweighted graph): O(V + E)
    fun shortestPath(start: T, end: T): List<T>? {
        val visited = mutableSetOf<T>()
        val queue = LinkedList<Pair<T, List<T>>>()

        queue.add(start to listOf(start))
        visited.add(start)

        while (queue.isNotEmpty()) {
            val (vertex, path) = queue.removeFirst()

            if (vertex == end) return path

            adjacencyList[vertex]?.forEach { neighbor ->
                if (neighbor !in visited) {
                    visited.add(neighbor)
                    queue.add(neighbor to path + neighbor)
                }
            }
        }

        return null // No path found
    }

    // Cycle detection using DFS: O(V + E)
    fun hasCycle(): Boolean {
        val visited = mutableSetOf<T>()
        val recursionStack = mutableSetOf<T>()

        for (vertex in adjacencyList.keys) {
            if (vertex !in visited) {
                if (hasCycleDFS(vertex, visited, recursionStack)) {
                    return true
                }
            }
        }

        return false
    }

    private fun hasCycleDFS(
        vertex: T,
        visited: MutableSet<T>,
        recursionStack: MutableSet<T>
    ): Boolean {
        visited.add(vertex)
        recursionStack.add(vertex)

        adjacencyList[vertex]?.forEach { neighbor ->
            if (neighbor !in visited) {
                if (hasCycleDFS(neighbor, visited, recursionStack)) {
                    return true
                }
            } else if (neighbor in recursionStack) {
                return true // Back edge found - cycle exists
            }
        }

        recursionStack.remove(vertex)
        return false
    }
}

// Real Android example: Navigation graph
sealed class Screen {
    data object Home : Screen()
    data object Profile : Screen()
    data object Settings : Screen()
    data object Details : Screen()
}

class NavigationGraph {
    private val graph = Graph<Screen>()

    init {
        // Define navigation structure
        graph.addVertex(Screen.Home)
        graph.addVertex(Screen.Profile)
        graph.addVertex(Screen.Settings)
        graph.addVertex(Screen.Details)

        // Define possible navigations
        graph.addEdge(Screen.Home, Screen.Profile)
        graph.addEdge(Screen.Home, Screen.Settings)
        graph.addEdge(Screen.Profile, Screen.Details)
        graph.addEdge(Screen.Settings, Screen.Details)
    }

    fun canNavigate(from: Screen, to: Screen): Boolean {
        val path = graph.shortestPath(from, to)
        return path != null
    }

    fun getNavigationPath(from: Screen, to: Screen): List<Screen>? {
        return graph.shortestPath(from, to)
    }
}

// Weighted graph for Dijkstra's algorithm
class WeightedGraph<T> {
    private val adjacencyList = mutableMapOf<T, MutableList<Pair<T, Int>>>()

    fun addVertex(vertex: T) {
        adjacencyList.putIfAbsent(vertex, mutableListOf())
    }

    fun addEdge(from: T, to: T, weight: Int) {
        adjacencyList[from]?.add(to to weight)
    }

    // Dijkstra's shortest path: O((V + E) log V) with priority queue
    fun dijkstra(start: T, end: T): Pair<Int, List<T>>? {
        val distances = mutableMapOf<T, Int>().withDefault { Int.MAX_VALUE }
        val previous = mutableMapOf<T, T?>()
        val priorityQueue = PriorityQueue<Pair<T, Int>>(compareBy { it.second })

        distances[start] = 0
        priorityQueue.insert(start to 0)

        while (priorityQueue.peek() != null) {
            val (current, currentDist) = priorityQueue.extractTop() ?: break

            if (current == end) {
                // Reconstruct path
                val path = mutableListOf<T>()
                var node: T? = end
                while (node != null) {
                    path.add(0, node)
                    node = previous[node]
                }
                return currentDist to path
            }

            if (currentDist > distances.getValue(current)) continue

            adjacencyList[current]?.forEach { (neighbor, weight) ->
                val newDist = currentDist + weight
                if (newDist < distances.getValue(neighbor)) {
                    distances[neighbor] = newDist
                    previous[neighbor] = current
                    priorityQueue.insert(neighbor to newDist)
                }
            }
        }

        return null
    }
}

// Complexity Summary:
// BFS:             O(V + E)
// DFS:             O(V + E)
// Shortest Path:   O(V + E) unweighted
// Dijkstra:        O((V + E) log V)
// Cycle Detection: O(V + E)
```

---

### 2. Time and Space Complexity / Анализ Сложности

**English:**
Big O notation describes algorithm performance as input size grows.

**Russian:**
Нотация Big O описывает производительность алгоритма при росте размера входных данных.

```kotlin
// Common Time Complexities (from fastest to slowest)

// O(1) - Constant: Same time regardless of input size
fun getFirst(list: List<Int>): Int? = list.firstOrNull()

// O(log n) - Logarithmic: Binary search, balanced tree operations
fun binarySearch(arr: IntArray, target: Int): Int {
    var left = 0
    var right = arr.size - 1

    while (left <= right) {
        val mid = left + (right - left) / 2
        when {
            arr[mid] == target -> return mid
            arr[mid] < target -> left = mid + 1
            else -> right = mid - 1
        }
    }

    return -1
}

// O(n) - Linear: Single loop through data
fun findMax(arr: IntArray): Int? {
    if (arr.isEmpty()) return null
    var max = arr[0]
    for (i in 1 until arr.size) {
        if (arr[i] > max) max = arr[i]
    }
    return max
}

// O(n log n) - Linearithmic: Efficient sorting algorithms
fun mergeSort(arr: IntArray): IntArray {
    if (arr.size <= 1) return arr

    val mid = arr.size / 2
    val left = mergeSort(arr.sliceArray(0 until mid))
    val right = mergeSort(arr.sliceArray(mid until arr.size))

    return merge(left, right)
}

private fun merge(left: IntArray, right: IntArray): IntArray {
    val result = IntArray(left.size + right.size)
    var i = 0
    var j = 0
    var k = 0

    while (i < left.size && j < right.size) {
        if (left[i] <= right[j]) {
            result[k++] = left[i++]
        } else {
            result[k++] = right[j++]
        }
    }

    while (i < left.size) result[k++] = left[i++]
    while (j < right.size) result[k++] = right[j++]

    return result
}

// O(n²) - Quadratic: Nested loops
fun bubbleSort(arr: IntArray) {
    for (i in arr.indices) {
        for (j in 0 until arr.size - i - 1) {
            if (arr[j] > arr[j + 1]) {
                val temp = arr[j]
                arr[j] = arr[j + 1]
                arr[j + 1] = temp
            }
        }
    }
}

// O(2^n) - Exponential: Recursive fibonacci (naive)
fun fibonacci(n: Int): Int {
    if (n <= 1) return n
    return fibonacci(n - 1) + fibonacci(n - 2)
}

// O(n!) - Factorial: Generating all permutations
fun generatePermutations(str: String): List<String> {
    if (str.length <= 1) return listOf(str)

    val result = mutableListOf<String>()
    for (i in str.indices) {
        val char = str[i]
        val remaining = str.substring(0, i) + str.substring(i + 1)
        val perms = generatePermutations(remaining)
        perms.forEach { result.add(char + it) }
    }
    return result
}

// Space Complexity Examples

// O(1) - Constant space
fun sum(arr: IntArray): Int {
    var total = 0  // Only one variable
    for (num in arr) {
        total += num
    }
    return total
}

// O(n) - Linear space
fun copyArray(arr: IntArray): IntArray {
    return arr.copyOf()  // New array of same size
}

// O(n) - Recursive call stack
fun factorial(n: Int): Int {
    if (n <= 1) return 1
    return n * factorial(n - 1)  // n recursive calls on stack
}

// O(n²) - Quadratic space
fun create2DArray(n: Int): Array<IntArray> {
    return Array(n) { IntArray(n) }  // n×n matrix
}
```

**Complexity Comparison Table:**

| Notation | Name | Example | 100 elements | 10,000 elements |
|----------|------|---------|--------------|-----------------|
| O(1) | Constant | Array access | 1 | 1 |
| O(log n) | Logarithmic | Binary search | 7 | 14 |
| O(n) | Linear | Linear search | 100 | 10,000 |
| O(n log n) | Linearithmic | Merge sort | 700 | 140,000 |
| O(n²) | Quadratic | Bubble sort | 10,000 | 100,000,000 |
| O(2^n) | Exponential | Fibonacci (naive) | 1.26×10³⁰ | impossible |
| O(n!) | Factorial | Permutations | 9.3×10¹⁵⁷ | impossible |

---

### 3. Essential Algorithms / Основные Алгоритмы

#### 3.1 Sorting Algorithms / Алгоритмы Сортировки

```kotlin
// ✅ Quick Sort: O(n log n) average, O(n²) worst
fun quickSort(arr: IntArray, low: Int = 0, high: Int = arr.size - 1) {
    if (low < high) {
        val pivotIndex = partition(arr, low, high)
        quickSort(arr, low, pivotIndex - 1)
        quickSort(arr, pivotIndex + 1, high)
    }
}

private fun partition(arr: IntArray, low: Int, high: Int): Int {
    val pivot = arr[high]
    var i = low - 1

    for (j in low until high) {
        if (arr[j] <= pivot) {
            i++
            swap(arr, i, j)
        }
    }

    swap(arr, i + 1, high)
    return i + 1
}

private fun swap(arr: IntArray, i: Int, j: Int) {
    val temp = arr[i]
    arr[i] = arr[j]
    arr[j] = temp
}

// ✅ Merge Sort: O(n log n) always
// (Already implemented above)

// ✅ Heap Sort: O(n log n) always
fun heapSort(arr: IntArray) {
    val n = arr.size

    // Build max heap
    for (i in n / 2 - 1 downTo 0) {
        heapify(arr, n, i)
    }

    // Extract elements from heap one by one
    for (i in n - 1 downTo 1) {
        swap(arr, 0, i)
        heapify(arr, i, 0)
    }
}

private fun heapify(arr: IntArray, n: Int, i: Int) {
    var largest = i
    val left = 2 * i + 1
    val right = 2 * i + 2

    if (left < n && arr[left] > arr[largest]) {
        largest = left
    }

    if (right < n && arr[right] > arr[largest]) {
        largest = right
    }

    if (largest != i) {
        swap(arr, i, largest)
        heapify(arr, n, largest)
    }
}

// Real Android example: Sort by multiple criteria
data class Contact(
    val name: String,
    val lastContacted: Long,
    val isFavorite: Boolean
)

fun sortContacts(contacts: List<Contact>): List<Contact> {
    return contacts.sortedWith(
        compareByDescending<Contact> { it.isFavorite }
            .thenBy { it.name }
            .thenByDescending { it.lastContacted }
    )
}

// Complexity Summary:
// Quick Sort:  O(n log n) average, O(n²) worst
// Merge Sort:  O(n log n) always, O(n) space
// Heap Sort:   O(n log n) always, O(1) space
```

#### 3.2 Searching Algorithms / Алгоритмы Поиска

```kotlin
// ✅ Binary Search: O(log n)
// (Already implemented above)

// ✅ Linear Search: O(n)
fun linearSearch(arr: IntArray, target: Int): Int {
    for (i in arr.indices) {
        if (arr[i] == target) return i
    }
    return -1
}

// ✅ Jump Search: O(√n)
fun jumpSearch(arr: IntArray, target: Int): Int {
    val n = arr.size
    val step = sqrt(n.toDouble()).toInt()
    var prev = 0

    // Find block where target may exist
    while (prev < n && arr[minOf(step, n) - 1] < target) {
        prev = step
        if (prev >= n) return -1
    }

    // Linear search in block
    for (i in prev until minOf(step, n)) {
        if (arr[i] == target) return i
    }

    return -1
}

// Real Android example: Search in RecyclerView
class ContactSearcher(private val contacts: List<Contact>) {

    // Linear search with filter: O(n)
    fun search(query: String): List<Contact> {
        if (query.isEmpty()) return contacts

        return contacts.filter { contact ->
            contact.name.contains(query, ignoreCase = true)
        }
    }

    // Binary search (if sorted by name): O(log n)
    fun binarySearchByName(name: String): Contact? {
        var left = 0
        var right = contacts.size - 1

        while (left <= right) {
            val mid = left + (right - left) / 2
            val comparison = contacts[mid].name.compareTo(name, ignoreCase = true)

            when {
                comparison == 0 -> return contacts[mid]
                comparison < 0 -> left = mid + 1
                else -> right = mid - 1
            }
        }

        return null
    }
}
```

---

### 4. Recursion and Dynamic Programming / Рекурсия и Динамическое Программирование

#### 4.1 Recursion / Рекурсия

```kotlin
// ✅ Basic recursion patterns

// 1. Factorial
fun factorial(n: Int): Int {
    if (n <= 1) return 1
    return n * factorial(n - 1)
}

// 2. Fibonacci (naive): O(2^n)
fun fibonacciNaive(n: Int): Int {
    if (n <= 1) return n
    return fibonacciNaive(n - 1) + fibonacciNaive(n - 2)
}

// 3. Power function
fun power(base: Int, exp: Int): Int {
    if (exp == 0) return 1
    return base * power(base, exp - 1)
}

// 4. Reverse string
fun reverseString(s: String): String {
    if (s.isEmpty()) return s
    return reverseString(s.substring(1)) + s[0]
}

// 5. Sum of array
fun sumArray(arr: IntArray, n: Int = arr.size): Int {
    if (n <= 0) return 0
    return arr[n - 1] + sumArray(arr, n - 1)
}

// Real Android example: File tree traversal
data class FileNode(
    val name: String,
    val size: Long,
    val children: List<FileNode> = emptyList()
)

fun calculateTotalSize(node: FileNode): Long {
    if (node.children.isEmpty()) return node.size

    return node.size + node.children.sumOf { calculateTotalSize(it) }
}

// Tail recursion optimization
tailrec fun factorialTailRec(n: Int, accumulator: Int = 1): Int {
    if (n <= 1) return accumulator
    return factorialTailRec(n - 1, n * accumulator)
}
```

#### 4.2 Dynamic Programming / Динамическое Программирование

**English:**
DP solves problems by breaking them into overlapping subproblems and storing results.

**Russian:**
ДП решает задачи, разбивая их на перекрывающиеся подзадачи и сохраняя результаты.

```kotlin
// ✅ Fibonacci with memoization: O(n)
class FibonacciMemo {
    private val memo = mutableMapOf<Int, Long>()

    fun fib(n: Int): Long {
        if (n <= 1) return n.toLong()

        return memo.getOrPut(n) {
            fib(n - 1) + fib(n - 2)
        }
    }
}

// ✅ Fibonacci with tabulation (bottom-up): O(n)
fun fibonacciTab(n: Int): Long {
    if (n <= 1) return n.toLong()

    val dp = LongArray(n + 1)
    dp[0] = 0
    dp[1] = 1

    for (i in 2..n) {
        dp[i] = dp[i - 1] + dp[i - 2]
    }

    return dp[n]
}

// ✅ Fibonacci with O(1) space
fun fibonacciOptimized(n: Int): Long {
    if (n <= 1) return n.toLong()

    var prev2 = 0L
    var prev1 = 1L

    repeat(n - 1) {
        val current = prev1 + prev2
        prev2 = prev1
        prev1 = current
    }

    return prev1
}

// ✅ Longest Common Subsequence: O(m × n)
fun longestCommonSubsequence(text1: String, text2: String): Int {
    val m = text1.length
    val n = text2.length
    val dp = Array(m + 1) { IntArray(n + 1) }

    for (i in 1..m) {
        for (j in 1..n) {
            dp[i][j] = if (text1[i - 1] == text2[j - 1]) {
                dp[i - 1][j - 1] + 1
            } else {
                maxOf(dp[i - 1][j], dp[i][j - 1])
            }
        }
    }

    return dp[m][n]
}

// ✅ 0/1 Knapsack Problem: O(n × W)
fun knapsack(weights: IntArray, values: IntArray, capacity: Int): Int {
    val n = weights.size
    val dp = Array(n + 1) { IntArray(capacity + 1) }

    for (i in 1..n) {
        for (w in 1..capacity) {
            if (weights[i - 1] <= w) {
                dp[i][w] = maxOf(
                    dp[i - 1][w],  // Don't take item
                    dp[i - 1][w - weights[i - 1]] + values[i - 1]  // Take item
                )
            } else {
                dp[i][w] = dp[i - 1][w]
            }
        }
    }

    return dp[n][capacity]
}

// ✅ Coin Change Problem: O(n × amount)
fun coinChange(coins: IntArray, amount: Int): Int {
    val dp = IntArray(amount + 1) { amount + 1 }
    dp[0] = 0

    for (i in 1..amount) {
        for (coin in coins) {
            if (coin <= i) {
                dp[i] = minOf(dp[i], dp[i - coin] + 1)
            }
        }
    }

    return if (dp[amount] > amount) -1 else dp[amount]
}

// ✅ Edit Distance (Levenshtein): O(m × n)
fun editDistance(word1: String, word2: String): Int {
    val m = word1.length
    val n = word2.length
    val dp = Array(m + 1) { IntArray(n + 1) }

    // Initialize base cases
    for (i in 0..m) dp[i][0] = i
    for (j in 0..n) dp[0][j] = j

    for (i in 1..m) {
        for (j in 1..n) {
            if (word1[i - 1] == word2[j - 1]) {
                dp[i][j] = dp[i - 1][j - 1]
            } else {
                dp[i][j] = 1 + minOf(
                    dp[i - 1][j],      // Delete
                    dp[i][j - 1],      // Insert
                    dp[i - 1][j - 1]   // Replace
                )
            }
        }
    }

    return dp[m][n]
}

// Real Android example: Text diff for "seen" indicator
class MessageDiffer {
    fun calculateDiff(oldMessages: List<String>, newMessages: List<String>): Int {
        // Return edit distance to know how many changes
        val oldText = oldMessages.joinToString("\n")
        val newText = newMessages.joinToString("\n")
        return editDistance(oldText, newText)
    }
}

// DP Pattern Summary:
// 1. Define subproblems
// 2. Write recurrence relation
// 3. Identify base cases
// 4. Decide on memoization (top-down) or tabulation (bottom-up)
// 5. Optimize space if possible
```

---

### 5. Algorithm Patterns / Паттерны Алгоритмов

```kotlin
// ✅ Two Pointers Pattern
fun twoSum(arr: IntArray, target: Int): Pair<Int, Int>? {
    arr.sort()
    var left = 0
    var right = arr.size - 1

    while (left < right) {
        val sum = arr[left] + arr[right]
        when {
            sum == target -> return arr[left] to arr[right]
            sum < target -> left++
            else -> right--
        }
    }

    return null
}

// ✅ Sliding Window Pattern
fun maxSumSubarray(arr: IntArray, k: Int): Int {
    var maxSum = 0
    var windowSum = 0

    // Calculate sum of first window
    for (i in 0 until k) {
        windowSum += arr[i]
    }
    maxSum = windowSum

    // Slide window
    for (i in k until arr.size) {
        windowSum += arr[i] - arr[i - k]
        maxSum = maxOf(maxSum, windowSum)
    }

    return maxSum
}

// ✅ Fast and Slow Pointers (Cycle Detection)
data class ListNode(var value: Int, var next: ListNode? = null)

fun hasCycle(head: ListNode?): Boolean {
    var slow = head
    var fast = head

    while (fast?.next != null) {
        slow = slow?.next
        fast = fast.next?.next

        if (slow == fast) return true
    }

    return false
}

// ✅ Backtracking Pattern
fun generateParentheses(n: Int): List<String> {
    val result = mutableListOf<String>()

    fun backtrack(current: String, open: Int, close: Int) {
        if (current.length == 2 * n) {
            result.add(current)
            return
        }

        if (open < n) {
            backtrack(current + "(", open + 1, close)
        }

        if (close < open) {
            backtrack(current + ")", open, close + 1)
        }
    }

    backtrack("", 0, 0)
    return result
}

// ✅ Divide and Conquer Pattern
fun findMaxSubarray(arr: IntArray): Int {
    fun maxCrossingSum(arr: IntArray, left: Int, mid: Int, right: Int): Int {
        var leftSum = Int.MIN_VALUE
        var sum = 0
        for (i in mid downTo left) {
            sum += arr[i]
            if (sum > leftSum) leftSum = sum
        }

        var rightSum = Int.MIN_VALUE
        sum = 0
        for (i in mid + 1..right) {
            sum += arr[i]
            if (sum > rightSum) rightSum = sum
        }

        return leftSum + rightSum
    }

    fun maxSubarrayRec(arr: IntArray, left: Int, right: Int): Int {
        if (left == right) return arr[left]

        val mid = (left + right) / 2

        return maxOf(
            maxSubarrayRec(arr, left, mid),
            maxSubarrayRec(arr, mid + 1, right),
            maxCrossingSum(arr, left, mid, right)
        )
    }

    return maxSubarrayRec(arr, 0, arr.size - 1)
}

// Real Android example: Sliding window for load more
class PaginationHelper<T>(
    private val pageSize: Int
) {
    private val allItems = mutableListOf<T>()
    private var currentPage = 0

    fun addItems(items: List<T>) {
        allItems.addAll(items)
    }

    fun getCurrentPage(): List<T> {
        val start = currentPage * pageSize
        val end = minOf(start + pageSize, allItems.size)

        if (start >= allItems.size) return emptyList()

        return allItems.subList(start, end)
    }

    fun loadNextPage(): List<T> {
        currentPage++
        return getCurrentPage()
    }
}
```

---

### 6. When to Use Each Data Structure / Когда Использовать Структуры

```kotlin
// Decision Guide:

// Use ARRAY when:
// - Random access needed (O(1))
// - Size is known in advance
// - Memory locality important (cache-friendly)
val scores = IntArray(100)

// Use LINKED LIST when:
// - Frequent insertions/deletions at beginning (O(1))
// - Size unknown
// - No random access needed
val undoStack = LinkedList<Action>()

// Use STACK when:
// - LIFO ordering needed
// - Expression evaluation, undo/redo
// - Backtracking algorithms
val navigationStack = Stack<Screen>()

// Use QUEUE when:
// - FIFO ordering needed
// - Task scheduling, BFS
// - Producer-consumer patterns
val downloadQueue = Queue<Task>()

// Use HASH TABLE when:
// - Fast lookup needed (O(1))
// - Key-value associations
// - Duplicate detection
val userCache = HashMap<String, User>()

// Use BINARY SEARCH TREE when:
// - Sorted data needed
// - Range queries common
// - Frequent insertions/deletions
val sortedSet = TreeSet<Int>()

// Use GRAPH when:
// - Modeling relationships
// - Network topology
// - Dependencies, social networks
val socialGraph = Graph<User>()

// Use HEAP/PRIORITY QUEUE when:
// - Need min/max quickly
// - Task scheduling by priority
// - Top K problems
val taskScheduler = PriorityQueue<Task>(compareBy { it.priority })
```

---

### 7. Real Android Applications / Реальные Android Приложения

```kotlin
// ✅ LRU Cache for images
class ImageLRUCache(maxSize: Int) : LinkedHashMap<String, Bitmap>(
    maxSize,
    0.75f,
    true  // Access order
) {
    private val maxSize = maxSize

    override fun removeEldestEntry(eldest: MutableMap.MutableEntry<String, Bitmap>?): Boolean {
        return size > maxSize
    }
}

// ✅ Trie for autocomplete
class AutocompleteSystem {
    private data class TrieNode(
        val children: MutableMap<Char, TrieNode> = mutableMapOf(),
        var isEndOfWord: Boolean = false
    )

    private val root = TrieNode()

    fun insert(word: String) {
        var current = root
        for (char in word) {
            current = current.children.getOrPut(char) { TrieNode() }
        }
        current.isEndOfWord = true
    }

    fun search(prefix: String): List<String> {
        var current = root

        // Navigate to prefix
        for (char in prefix) {
            current = current.children[char] ?: return emptyList()
        }

        // Collect all words with this prefix
        val results = mutableListOf<String>()
        collectWords(current, prefix, results)
        return results
    }

    private fun collectWords(node: TrieNode, prefix: String, results: MutableList<String>) {
        if (node.isEndOfWord) {
            results.add(prefix)
        }

        for ((char, child) in node.children) {
            collectWords(child, prefix + char, results)
        }
    }
}

// ✅ Union-Find for connected components
class UnionFind(size: Int) {
    private val parent = IntArray(size) { it }
    private val rank = IntArray(size) { 0 }

    fun find(x: Int): Int {
        if (parent[x] != x) {
            parent[x] = find(parent[x])  // Path compression
        }
        return parent[x]
    }

    fun union(x: Int, y: Int) {
        val rootX = find(x)
        val rootY = find(y)

        if (rootX != rootY) {
            // Union by rank
            when {
                rank[rootX] < rank[rootY] -> parent[rootX] = rootY
                rank[rootX] > rank[rootY] -> parent[rootY] = rootX
                else -> {
                    parent[rootY] = rootX
                    rank[rootX]++
                }
            }
        }
    }

    fun connected(x: Int, y: Int): Boolean {
        return find(x) == find(y)
    }
}

// Example: Group contacts by relationship
class ContactGrouper(contactCount: Int) {
    private val unionFind = UnionFind(contactCount)

    fun markRelated(contact1: Int, contact2: Int) {
        unionFind.union(contact1, contact2)
    }

    fun areRelated(contact1: Int, contact2: Int): Boolean {
        return unionFind.connected(contact1, contact2)
    }

    fun getGroups(contactCount: Int): List<List<Int>> {
        val groups = mutableMapOf<Int, MutableList<Int>>()

        for (i in 0 until contactCount) {
            val root = unionFind.find(i)
            groups.getOrPut(root) { mutableListOf() }.add(i)
        }

        return groups.values.toList()
    }
}
```

---

### 8. Common Interview Problems / Распространенные Задачи

```kotlin
// ✅ 1. Reverse Linked List
fun reverseLinkedList(head: ListNode?): ListNode? {
    var prev: ListNode? = null
    var current = head

    while (current != null) {
        val next = current.next
        current.next = prev
        prev = current
        current = next
    }

    return prev
}

// ✅ 2. Valid Palindrome
fun isPalindrome(s: String): Boolean {
    val cleaned = s.filter { it.isLetterOrDigit() }.lowercase()
    return cleaned == cleaned.reversed()
}

// ✅ 3. Two Sum
fun twoSumHashMap(nums: IntArray, target: Int): IntArray {
    val map = mutableMapOf<Int, Int>()

    for (i in nums.indices) {
        val complement = target - nums[i]
        if (complement in map) {
            return intArrayOf(map[complement]!!, i)
        }
        map[nums[i]] = i
    }

    return intArrayOf()
}

// ✅ 4. Maximum Depth of Binary Tree
fun maxDepth(root: BinaryTree.Node<Int>?): Int {
    if (root == null) return 0
    return 1 + maxOf(maxDepth(root.left), maxDepth(root.right))
}

// ✅ 5. Merge Two Sorted Lists
fun mergeTwoLists(l1: ListNode?, l2: ListNode?): ListNode? {
    if (l1 == null) return l2
    if (l2 == null) return l1

    return if (l1.value < l2.value) {
        l1.next = mergeTwoLists(l1.next, l2)
        l1
    } else {
        l2.next = mergeTwoLists(l1, l2.next)
        l2
    }
}

// ✅ 6. Binary Tree Level Order Traversal
fun levelOrder(root: BinaryTree.Node<Int>?): List<List<Int>> {
    val result = mutableListOf<List<Int>>()
    if (root == null) return result

    val queue = LinkedList<BinaryTree.Node<Int>>()
    queue.add(root)

    while (queue.isNotEmpty()) {
        val levelSize = queue.size
        val level = mutableListOf<Int>()

        repeat(levelSize) {
            val node = queue.removeFirst()
            level.add(node.data)
            node.left?.let { queue.add(it) }
            node.right?.let { queue.add(it) }
        }

        result.add(level)
    }

    return result
}

// ✅ 7. Longest Substring Without Repeating Characters
fun lengthOfLongestSubstring(s: String): Int {
    val seen = mutableMapOf<Char, Int>()
    var maxLength = 0
    var start = 0

    for (end in s.indices) {
        val char = s[end]
        if (char in seen && seen[char]!! >= start) {
            start = seen[char]!! + 1
        }
        seen[char] = end
        maxLength = maxOf(maxLength, end - start + 1)
    }

    return maxLength
}

// ✅ 8. Validate Binary Search Tree
fun isValidBST(root: BinaryTree.Node<Int>?): Boolean {
    fun validate(node: BinaryTree.Node<Int>?, min: Int?, max: Int?): Boolean {
        if (node == null) return true

        if ((min != null && node.data <= min) ||
            (max != null && node.data >= max)) {
            return false
        }

        return validate(node.left, min, node.data) &&
               validate(node.right, node.data, max)
    }

    return validate(root, null, null)
}

// ✅ 9. Climbing Stairs (Fibonacci variant)
fun climbStairs(n: Int): Int {
    if (n <= 2) return n

    var prev2 = 1
    var prev1 = 2

    for (i in 3..n) {
        val current = prev1 + prev2
        prev2 = prev1
        prev1 = current
    }

    return prev1
}

// ✅ 10. Lowest Common Ancestor of Binary Tree
fun lowestCommonAncestor(
    root: BinaryTree.Node<Int>?,
    p: BinaryTree.Node<Int>,
    q: BinaryTree.Node<Int>
): BinaryTree.Node<Int>? {
    if (root == null || root == p || root == q) return root

    val left = lowestCommonAncestor(root.left, p, q)
    val right = lowestCommonAncestor(root.right, p, q)

    return when {
        left != null && right != null -> root
        left != null -> left
        else -> right
    }
}
```

---

## Summary / Резюме

**English:**

Key takeaways for Data Structures and Algorithms:

1. **Choose the Right Data Structure:**
   - Arrays: O(1) access, use for fixed-size collections
   - Linked Lists: O(1) insertion at head, use for dynamic size
   - Hash Tables: O(1) lookup, use for key-value storage
   - Trees: O(log n) operations (balanced), use for hierarchical data
   - Graphs: Model relationships and networks

2. **Master Core Algorithms:**
   - Sorting: Quick Sort, Merge Sort, Heap Sort
   - Searching: Binary Search, BFS, DFS
   - Dynamic Programming: Fibonacci, LCS, Knapsack

3. **Analyze Complexity:**
   - Always consider both time and space complexity
   - Big O describes worst-case performance
   - Optimize bottlenecks in your code

4. **Common Patterns:**
   - Two Pointers, Sliding Window
   - Fast & Slow Pointers
   - Backtracking, Divide & Conquer

5. **Android Applications:**
   - RecyclerView: Arrays for item access
   - Navigation: Stack for back stack
   - Image Cache: LRU Cache (LinkedHashMap)
   - Autocomplete: Trie data structure

**Russian:**

Ключевые выводы по структурам данных и алгоритмам:

1. **Выбирайте Правильную Структуру:**
   - Массивы: O(1) доступ, для коллекций фиксированного размера
   - Связные списки: O(1) вставка в начало, для динамического размера
   - Хеш-таблицы: O(1) поиск, для хранения ключ-значение
   - Деревья: O(log n) операции (сбалансированные), для иерархических данных
   - Графы: Моделирование отношений и сетей

2. **Освойте Основные Алгоритмы:**
   - Сортировки: Quick Sort, Merge Sort, Heap Sort
   - Поиск: Binary Search, BFS, DFS
   - Динамическое программирование: Фибоначчи, LCS, Рюкзак

3. **Анализируйте Сложность:**
   - Всегда учитывайте временную и пространственную сложность
   - Big O описывает производительность худшего случая
   - Оптимизируйте узкие места в коде

4. **Распространенные Паттерны:**
   - Два указателя, Скользящее окно
   - Быстрый и медленный указатели
   - Возврат, Разделяй и властвуй

5. **Android Применения:**
   - RecyclerView: Массивы для доступа к элементам
   - Навигация: Стек для back stack
   - Кеш изображений: LRU Cache (LinkedHashMap)
   - Автодополнение: Структура Trie

---

## Follow-up Questions / Вопросы для Закрепления

1. **What is the difference between O(n) and O(log n)? Give examples of each.**
   **В чем разница между O(n) и O(log n)? Приведите примеры.**

2. **When would you use a LinkedList instead of an ArrayList in Android?**
   **Когда бы вы использовали LinkedList вместо ArrayList в Android?**

3. **Explain how a Hash Table handles collisions. What are the methods?**
   **Объясните, как хеш-таблица обрабатывает коллизии. Какие есть методы?**

4. **What is the difference between BFS and DFS? When to use each?**
   **В чем разница между BFS и DFS? Когда использовать каждый?**

5. **How does Dynamic Programming differ from Divide and Conquer?**
   **Чем динамическое программирование отличается от разделяй и властвуй?**

6. **Explain the difference between a Stack and a Queue. Give Android examples.**
   **Объясните разницу между стеком и очередью. Приведите Android примеры.**

7. **What is a Binary Search Tree? What are its advantages and disadvantages?**
   **Что такое бинарное дерево поиска? Каковы его преимущества и недостатки?**

8. **How would you implement an LRU Cache? What data structures would you use?**
   **Как бы вы реализовали LRU Cache? Какие структуры данных использовали бы?**

9. **What is the time complexity of QuickSort in the worst case? Why?**
   **Какова временная сложность QuickSort в худшем случае? Почему?**

10. **Explain memoization vs tabulation in Dynamic Programming. Which is better?**
    **Объясните мемоизацию против табуляции в ДП. Что лучше?**
