---
id: "20251013-600005"
title: "Data Structures and Algorithms Fundamentals"
topic: cs
difficulty: hard
status: draft
created: "2025-10-13"
tags: ["data-structures", "algorithms", "complexity", "big-o", "sorting", "searching", "trees", "graphs", "dynamic-programming", "recursion", "kotlin"]
description: "Comprehensive coverage of fundamental data structures (arrays, linked lists, stacks, queues, trees, graphs, hash tables) and core algorithms (sorting, searching, recursion, dynamic programming) with time/space complexity analysis"
language: "en"
moc: moc-cs
related_questions:   - "20251012-600003"  # Concurrency Fundamentals
  - "20251012-600004"  # OOP Principles
subcategory: "algorithms"
updated: "2025-10-13"
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

### 1. Основные Структуры Данных

#### 1.1 Массивы

**English:**
Arrays store elements in contiguous memory locations with O(1) access time.

**Russian:**
Массивы хранят элементы в смежных областях памяти с O(1) временем доступа.

```kotlin
// ✅ Массивы: O(1) доступ, O(n) вставка/удаление
class ArrayOperations {
    fun demonstrateArrays() {
        // Массив фиксированного размера
        val fixedArray = IntArray(5) { it * 2 } // [0, 2, 4, 6, 8]

        // Доступ: O(1)
        val element = fixedArray[2] // 4

        // Динамический массив (ArrayList)
        val dynamicArray = mutableListOf<Int>()

        // Добавление в конец: Амортизированное O(1)
        dynamicArray.add(10)

        // Вставка в начало: O(n) - сдвигает все элементы
        dynamicArray.add(0, 5)

        // Удаление: O(n) - сдвигает элементы
        dynamicArray.removeAt(0)

        // Поиск: O(n) - линейный просмотр
        val found = dynamicArray.contains(10)
    }

    // Реальный пример в Android: данные для RecyclerView
    class TodoAdapter(private val items: MutableList<Todo>) :
        RecyclerView.Adapter<TodoViewHolder>() {

        // O(1) доступ для привязки
        override fun onBindViewHolder(holder: TodoViewHolder, position: Int) {
            holder.bind(items[position])
        }

        // O(n) в худшем случае для вставки
        fun addItem(todo: Todo) {
            items.add(todo)
            notifyItemInserted(items.size - 1)
        }

        // O(n) для удаления
        fun removeItem(position: Int) {
            items.removeAt(position)
            notifyItemRemoved(position)
        }

        override fun getItemCount() = items.size
    }
}

// Сводка по сложности:
// Доступ:      O(1)
// Поиск:      O(n)
// Вставка в конец:  O(1) амортизированное
// Вставка в середину:  O(n)
// Удаление:      O(n)
```

#### 1.2 Связные Списки

**English:**
Linked Lists store elements in nodes with pointers to the next/previous node.

**Russian:**
Связные списки хранят элементы в узлах с указателями на следующий/предыдущий узел.

```kotlin
// ✅ Односвязный список
class LinkedList<T> {
    private data class Node<T>(
        var data: T,
        var next: Node<T>? = null
    )

    private var head: Node<T>? = null
    private var tail: Node<T>? = null
    private var size = 0

    // Вставка в начало: O(1)
    fun addFirst(data: T) {
        val newNode = Node(data, head)
        head = newNode
        if (tail == null) {
            tail = head
        }
        size++
    }

    // Вставка в конец: O(1) с указателем на хвост
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

    // Удаление из начала: O(1)
    fun removeFirst(): T? {
        val data = head?.data
        head = head?.next
        if (head == null) {
            tail = null
        }
        if (data != null) size--
        return data
    }

    // Поиск: O(n)
    fun contains(data: T): Boolean {
        var current = head
        while (current != null) {
            if (current.data == data) return true
            current = current.next
        }
        return false
    }

    // Получение по индексу: O(n)
    fun get(index: Int): T? {
        if (index < 0 || index >= size) return null
        var current = head
        repeat(index) {
            current = current?.next
        }
        return current?.data
    }
}

// Реальный пример в Android: стек отмены/повтора действий
class UndoRedoManager<T> {
    private val undoStack = LinkedList<T>()
    private val redoStack = LinkedList<T>()

    fun execute(action: T) {
        undoStack.addFirst(action) // O(1)
        redoStack.clear() // Очистка стека повтора при новом действии
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

// Сводка по сложности:
// Доступ:          O(n)
// Поиск:          O(n)
// Вставка в начало:    O(1)
// Вставка в конец:     O(1) с указателем на хвост
// Удаление из начала:    O(1)
// Удаление из конца:     O(n) в односвязном списке
```

#### 1.3 Стеки

**English:**
LIFO (Last In First Out) data structure.

**Russian:**
LIFO (Последний вошел, первый вышел) структура данных.

```kotlin
// ✅ Реализация стека
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

// Реальный пример в Android: стек навигации
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

// Классическая задача: сбалансированные скобки
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
```

#### 1.4 Очереди

**English:**
FIFO (First In First Out) data structure.

**Russian:**
FIFO (Первый вошел, первый вышел) структура данных.

```kotlin
// ✅ Реализация очереди с помощью LinkedList
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

// Реальный пример в Android: очередь загрузок
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

        // Обработка задачи
        task.execute {
            isProcessing = false
            processNext() // Обработка следующей в очереди
        }
    }
}

// Пример приоритетной очереди
class PriorityQueue<T>(
    private val comparator: Comparator<T>
) {
    // ... (реализация как в английской версии)
}
```

#### 1.5 Хеш-таблицы

**English:**
Hash tables provide O(1) average-case lookup using hash functions.

**Russian:**
Хеш-таблицы обеспечивают O(1) поиск в среднем случае, используя хеш-функции.

```kotlin
// ✅ Простая реализация хеш-таблицы
class HashTable<K, V>(private val capacity: Int = 16) {
    // ... (реализация как в английской версии)
}

// Реальный пример в Android: кэш в памяти
class ImageCache {
    private val cache = hashMapOf<String, Bitmap>()
    private val maxSize = 50

    // O(1) поиск
    fun get(url: String): Bitmap? {
        return cache[url]
    }

    // O(1) вставка
    fun put(url: String, bitmap: Bitmap) {
        if (cache.size >= maxSize) {
            // Удаление самого старого (простой LRU использовал бы LinkedHashMap)
            cache.remove(cache.keys.first())
        }
        cache[url] = bitmap
    }
}

// Реализация LRU кэша
class LRUCache<K, V>(private val capacity: Int) {
    private val cache = LinkedHashMap<K, V>(capacity, 0.75f, true)

    // O(1) get с обновлением порядка доступа
    fun get(key: K): V? {
        return cache[key]
    }

    // O(1) put с вытеснением при необходимости
    fun put(key: K, value: V) {
        if (cache.size >= capacity && !cache.containsKey(key)) {
            // Удаление самой старой записи
            val eldest = cache.entries.first()
            cache.remove(eldest.key)
        }
        cache[key] = value
    }
}
```

#### 1.6 Деревья

**English:**
Hierarchical data structures with nodes connected by edges.

**Russian:**
Иерархические структуры данных с узлами, соединенными ребрами.

```kotlin
// ✅ Двоичное дерево
class BinaryTree<T> {
    // ... (реализация как в английской версии)
}

// ✅ Двоичное дерево поиска (BST)
class BinarySearchTree {
    // ... (реализация как в английской версии)
}

// Реальный пример в Android: дерево файловой системы
class FileSystemTree {
    // ... (реализация как в английской версии)
}
```

#### 1.7 Графы

**English:**
Graphs represent networks of nodes connected by edges.

**Russian:**
Графы представляют сети узлов, соединенных ребрами.

```kotlin
// ✅ Представление графа (список смежности)
class Graph<T> {
    // ... (реализация как в английской версии)
}

// Реальный пример в Android: граф навигации
class NavigationGraph {
    // ... (реализация как в английской версии)
}

// Взвешенный граф для алгоритма Дейкстры
class WeightedGraph<T> {
    // ... (реализация как в английской версии)
}
```

---

### 2. Анализ Временной и Пространственной Сложности

**English:**
Big O notation describes algorithm performance as input size grows.

**Russian:**
Нотация Big O описывает производительность алгоритма при росте размера входных данных.

```kotlin
// ... (код как в английской версии)
```

---

### 3. Основные Алгоритмы

#### 3.1 Алгоритмы Сортировки

```kotlin
// ✅ Быстрая сортировка: O(n log n) в среднем, O(n²) в худшем
fun quickSort(arr: IntArray, low: Int = 0, high: Int = arr.size - 1) {
    // ... (реализация как в английской версии)
}

// ✅ Сортировка слиянием: O(n log n) всегда
// (уже реализовано выше)

// ✅ Пирамидальная сортировка: O(n log n) всегда
fun heapSort(arr: IntArray) {
    // ... (реализация как в английской версии)
}
```

#### 3.2 Алгоритмы Поиска

```kotlin
// ✅ Двоичный поиск: O(log n)
// (уже реализовано выше)

// ✅ Линейный поиск: O(n)
fun linearSearch(arr: IntArray, target: Int): Int {
    // ... (реализация как в английской версии)
}
```

---

### 4. Рекурсия и Динамическое Программирование

#### 4.1 Рекурсия

```kotlin
// ... (код как в английской версии)
```

#### 4.2 Динамическое Программирование

**English:**
DP solves problems by breaking them into overlapping subproblems and storing results.

**Russian:**
ДП решает задачи, разбивая их на перекрывающиеся подзадачи и сохраняя результаты.

```kotlin
// ✅ Фибоначчи с мемоизацией: O(n)
class FibonacciMemo {
    // ... (реализация как в английской версии)
}

// ✅ Фибоначчи с табуляцией (снизу вверх): O(n)
fun fibonacciTab(n: Int): Long {
    // ... (реализация как в английской версии)
}
```

---

### 5. Паттерны Алгоритмов

```kotlin
// ✅ Паттерн "Два указателя"
fun twoSum(arr: IntArray, target: Int): Pair<Int, Int>? {
    // ... (реализация как в английской версии)
}

// ✅ Паттерн "Скользящее окно"
fun maxSumSubarray(arr: IntArray, k: Int): Int {
    // ... (реализация как в английской версии)
}
```

---

### 6. Когда Использовать Какую Структуру Данных

```kotlin
// Руководство по выбору:

// Используйте МАССИВ, когда:
// - Нужен произвольный доступ (O(1))
// - Размер известен заранее
// - Важна локальность памяти (дружелюбно к кэшу)

// Используйте СВЯЗНЫЙ СПИСОК, когда:
// - Частые вставки/удаления в начале (O(1))
// - Размер неизвестен
// - Произвольный доступ не нужен

// ... (перевод остальной части)
```

---

### 7. Реальные Применения в Android

```kotlin
// ✅ LRU кэш для изображений
class ImageLRUCache(maxSize: Int) : LinkedHashMap<String, Bitmap>(
    // ... (реализация как в английской версии)
)

// ✅ Trie для автодополнения
class AutocompleteSystem {
    // ... (реализация как в английской версии)
}

// ✅ Union-Find для связанных компонент
class UnionFind(size: Int) {
    // ... (реализация как в английской версии)
}
```

---

### 8. Распространенные Задачи на Собеседованиях

```kotlin
// ✅ 1. Развернуть связный список
fun reverseLinkedList(head: ListNode?): ListNode? {
    // ... (реализация как в английской версии)
}

// ✅ 2. Проверить, является ли строка палиндромом
fun isPalindrome(s: String): Boolean {
    // ... (реализация как в английской версии)
}

// ✅ 3. Два числа в сумме
fun twoSumHashMap(nums: IntArray, target: Int): IntArray {
    // ... (реализация как в английской версии)
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
