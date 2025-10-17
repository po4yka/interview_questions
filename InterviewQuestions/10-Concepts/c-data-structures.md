---
id: concept-data-structures
title: "Data Structures / Структуры данных"
type: concept
tags: [concept, data-structures, arrays, lists, trees, graphs, hash-tables]
created: 2025-10-12
updated: 2025-10-12
---

# Summary (EN)

Data structures are ways to organize and store data efficiently. Choosing the right data structure is crucial for algorithm performance. Common structures include linear structures (arrays, linked lists, stacks, queues), trees (binary trees, BSTs), hash tables for fast lookups, and graphs for representing relationships.

# Сводка (RU)

Структуры данных - это способы организации и эффективного хранения данных. Выбор правильной структуры данных критически важен для производительности алгоритма. Распространенные структуры включают линейные структуры (массивы, связные списки, стеки, очереди), деревья (бинарные деревья, BST), хеш-таблицы для быстрого поиска и графы для представления отношений.

## Use Cases / Trade-offs

**Use Cases:**
- Arrays: Random access, fixed collections
- Linked Lists: Dynamic size, frequent insertions/deletions
- Stacks: LIFO operations, function calls, undo
- Queues: FIFO operations, task scheduling, BFS
- Hash Tables: Fast key-value lookups, caching
- Trees: Hierarchical data, sorted data (BST)
- Graphs: Networks, relationships, dependencies

**Trade-offs:**
- **Arrays vs Linked Lists:** Fast access (O(1)) vs. fast insertion/deletion at known positions
- **Hash Tables:** O(1) average lookups vs. O(n) worst case and no ordering
- **Trees:** Balanced (O(log n)) vs. unbalanced (O(n)) operations
- **Space vs Time:** More memory for faster operations (e.g., hash tables)

## Overview

Data structures are ways to organize and store data efficiently. Choosing the right data structure is crucial for algorithm performance.

---

## Linear Data Structures

### Arrays
```kotlin
val array = arrayOf(1, 2, 3, 4, 5)

// Access: O(1)
val element = array[0]

// Insert/Delete: O(n) - requires shifting
// Search: O(n) unsorted, O(log n) sorted
```

**Use when:**
- Fixed size known
- Random access needed
- Cache-friendly operations

### Linked Lists
```kotlin
class Node<T>(
    var data: T,
    var next: Node<T>? = null
)

class LinkedList<T> {
    var head: Node<T>? = null

    // Insert at head: O(1)
    fun insertAtHead(data: T) {
        val newNode = Node(data)
        newNode.next = head
        head = newNode
    }

    // Delete: O(1) if node known, O(n) to find
    // Access: O(n)
}
```

**Use when:**
- Size changes frequently
- Insertions/deletions at known positions
- No random access needed

### Stacks
```kotlin
class Stack<T> {
    private val list = mutableListOf<T>()

    // Push: O(1)
    fun push(item: T) = list.add(item)

    // Pop: O(1)
    fun pop(): T? = if (list.isNotEmpty()) list.removeLast() else null

    // Peek: O(1)
    fun peek(): T? = list.lastOrNull()
}
```

**Use for:**
- Function call stack
- Undo operations
- Expression evaluation
- DFS traversal

### Queues
```kotlin
class Queue<T> {
    private val list = mutableListOf<T>()

    // Enqueue: O(1)
    fun enqueue(item: T) = list.add(item)

    // Dequeue: O(1) with LinkedList, O(n) with ArrayList
    fun dequeue(): T? = if (list.isNotEmpty()) list.removeFirst() else null
}
```

**Use for:**
- Task scheduling
- BFS traversal
- Request handling

---

## Trees

### Binary Tree
```kotlin
class TreeNode<T>(
    var data: T,
    var left: TreeNode<T>? = null,
    var right: TreeNode<T>? = null
)
```

### Binary Search Tree
```kotlin
class BST<T : Comparable<T>> {
    var root: TreeNode<T>? = null

    // Insert: O(log n) average, O(n) worst
    fun insert(data: T) {
        root = insertRec(root, data)
    }

    private fun insertRec(node: TreeNode<T>?, data: T): TreeNode<T> {
        if (node == null) return TreeNode(data)

        when {
            data < node.data -> node.left = insertRec(node.left, data)
            data > node.data -> node.right = insertRec(node.right, data)
        }
        return node
    }

    // Search: O(log n) average, O(n) worst
    fun search(data: T): Boolean {
        return searchRec(root, data)
    }

    private fun searchRec(node: TreeNode<T>?, data: T): Boolean {
        if (node == null) return false
        if (node.data == data) return true

        return if (data < node.data)
            searchRec(node.left, data)
        else
            searchRec(node.right, data)
    }
}
```

---

## Hash Tables

```kotlin
class HashTable<K, V> {
    private val buckets = Array<MutableList<Pair<K, V>>>(16) { mutableListOf() }

    // Insert/Access/Delete: O(1) average, O(n) worst
    fun put(key: K, value: V) {
        val index = key.hashCode() % buckets.size
        val bucket = buckets[index]

        // Update if exists
        bucket.find { it.first == key }?.let {
            bucket.remove(it)
        }

        bucket.add(Pair(key, value))
    }

    fun get(key: K): V? {
        val index = key.hashCode() % buckets.size
        return buckets[index].find { it.first == key }?.second
    }
}
```

**Use when:**
- Fast lookups needed (O(1))
- Key-value associations
- Caching
- Deduplication

---

## Graphs

```kotlin
// Adjacency List representation
class Graph {
    private val adjacencyList = mutableMapOf<Int, MutableList<Int>>()

    fun addEdge(from: Int, to: Int) {
        adjacencyList.getOrPut(from) { mutableListOf() }.add(to)
    }

    // DFS: O(V + E)
    fun dfs(start: Int, visited: MutableSet<Int> = mutableSetOf()) {
        if (start in visited) return
        visited.add(start)
        println(start)

        adjacencyList[start]?.forEach { neighbor ->
            dfs(neighbor, visited)
        }
    }

    // BFS: O(V + E)
    fun bfs(start: Int) {
        val visited = mutableSetOf<Int>()
        val queue = ArrayDeque<Int>()

        queue.add(start)
        visited.add(start)

        while (queue.isNotEmpty()) {
            val node = queue.removeFirst()
            println(node)

            adjacencyList[node]?.forEach { neighbor ->
                if (neighbor !in visited) {
                    visited.add(neighbor)
                    queue.add(neighbor)
                }
            }
        }
    }
}
```

---

## Complexity Comparison

| Data Structure | Access | Search | Insert | Delete | Space |
|----------------|--------|--------|--------|--------|-------|
| Array          | O(1)   | O(n)   | O(n)   | O(n)   | O(n)  |
| Linked List    | O(n)   | O(n)   | O(1)*  | O(1)*  | O(n)  |
| Stack          | O(n)   | O(n)   | O(1)   | O(1)   | O(n)  |
| Queue          | O(n)   | O(n)   | O(1)   | O(1)   | O(n)  |
| Hash Table     | O(1)†  | O(1)†  | O(1)†  | O(1)†  | O(n)  |
| BST            | O(log n)† | O(log n)† | O(log n)† | O(log n)† | O(n) |

\* At known position  
† Average case

---

## Related Questions

- [[q-data-structures-overview--algorithms--easy]]

## Related Concepts

- [[c-algorithms]]

## References

- "Data Structures and Algorithms in Java" by Robert Lafore
- [VisuAlgo - Data Structure Visualizations](https://visualgo.net/)
- [Big-O Cheat Sheet](https://www.bigocheatsheet.com/)
- "Grokking Algorithms" by Aditya Bhargava

## MOC Links

- [[moc-algorithms]]
- [[moc-kotlin]]
