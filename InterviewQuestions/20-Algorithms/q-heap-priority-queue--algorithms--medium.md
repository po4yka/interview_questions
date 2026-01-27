---
id: algo-017
title: Heap and Priority Queue / Куча и приоритетная очередь
aliases:
- Heap
- Priority Queue
- Top K Elements
- Куча
- Приоритетная очередь
- Top K элементов
topic: algorithms
subtopics:
- heap
- priority-queue
- top-k
question_kind: coding
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-algorithms
related:
- c-heap
- c-priority-queue
- q-data-structures-overview--algorithms--easy
created: 2026-01-23
updated: 2026-01-23
tags:
- algorithms
- heap
- difficulty/medium
- priority-queue
- top-k
sources:
- https://en.wikipedia.org/wiki/Heap_(data_structure)
- https://en.wikipedia.org/wiki/Priority_queue
anki_cards:
- slug: algo-017-0-en
  language: en
  anki_id: 1769168919869
  synced_at: '2026-01-26T09:10:14.508118'
- slug: algo-017-0-ru
  language: ru
  anki_id: 1769168919896
  synced_at: '2026-01-26T09:10:14.509443'
---
# Вопрос (RU)
> Объясни структуру данных "куча" и приоритетную очередь. Как решать задачи Top K, Merge K Sorted Lists и Median from Data Stream?

# Question (EN)
> Explain the heap data structure and priority queue. How do you solve Top K, Merge K Sorted Lists, and Median from Data Stream problems?

---

## Ответ (RU)

**Теория кучи:**
Куча (heap) - полное бинарное дерево, где каждый узел больше (max-heap) или меньше (min-heap) своих детей. Обеспечивает O(log n) для вставки и извлечения, O(1) для получения min/max.

**Свойства:**
- **Min-Heap**: родитель <= детей (корень = минимум)
- **Max-Heap**: родитель >= детей (корень = максимум)
- Хранится в массиве: дети узла i на позициях 2i+1 и 2i+2

**PriorityQueue в Kotlin/Java:**
```kotlin
// Min-Heap (по умолчанию)
val minHeap = PriorityQueue<Int>()

// Max-Heap
val maxHeap = PriorityQueue<Int>(reverseOrder())

// С компаратором
val customHeap = PriorityQueue<Pair<Int, String>>(compareBy { it.first })
```

**Top K Frequent Elements:**
```kotlin
fun topKFrequent(nums: IntArray, k: Int): IntArray {
    // 1. Подсчёт частот
    val count = mutableMapOf<Int, Int>()
    for (num in nums) {
        count[num] = count.getOrDefault(num, 0) + 1
    }

    // 2. Min-Heap размера k (храним k самых частых)
    val minHeap = PriorityQueue<Int>(compareBy { count[it] })

    for (num in count.keys) {
        minHeap.offer(num)
        if (minHeap.size > k) {
            minHeap.poll()  // Удаляем наименее частый
        }
    }

    return minHeap.toIntArray()
}
```

**Kth Largest Element:**
```kotlin
// Подход 1: Min-Heap размера k
fun findKthLargest(nums: IntArray, k: Int): Int {
    val minHeap = PriorityQueue<Int>()

    for (num in nums) {
        minHeap.offer(num)
        if (minHeap.size > k) {
            minHeap.poll()
        }
    }

    return minHeap.peek()  // k-й по величине
}

// Подход 2: QuickSelect (в среднем O(n))
fun findKthLargestQuickSelect(nums: IntArray, k: Int): Int {
    val targetIndex = nums.size - k

    fun quickSelect(left: Int, right: Int): Int {
        val pivot = nums[right]
        var p = left

        for (i in left until right) {
            if (nums[i] <= pivot) {
                nums[i] = nums[p].also { nums[p] = nums[i] }
                p++
            }
        }
        nums[p] = nums[right].also { nums[right] = nums[p] }

        return when {
            p == targetIndex -> nums[p]
            p < targetIndex -> quickSelect(p + 1, right)
            else -> quickSelect(left, p - 1)
        }
    }

    return quickSelect(0, nums.lastIndex)
}
```

**Merge K Sorted Lists:**
```kotlin
fun mergeKLists(lists: Array<ListNode?>): ListNode? {
    if (lists.isEmpty()) return null

    // Min-Heap по значению узла
    val minHeap = PriorityQueue<ListNode>(compareBy { it.`val` })

    // Добавляем головы всех списков
    for (list in lists) {
        list?.let { minHeap.offer(it) }
    }

    val dummy = ListNode(0)
    var curr = dummy

    while (minHeap.isNotEmpty()) {
        val smallest = minHeap.poll()
        curr.next = smallest
        curr = curr.next!!

        smallest.next?.let { minHeap.offer(it) }
    }

    return dummy.next
}
```

**Median from Data Stream:**
```kotlin
class MedianFinder {
    // Max-Heap для левой половины (меньшие элементы)
    private val maxHeap = PriorityQueue<Int>(reverseOrder())
    // Min-Heap для правой половины (большие элементы)
    private val minHeap = PriorityQueue<Int>()

    fun addNum(num: Int) {
        // Добавляем в левую половину
        maxHeap.offer(num)

        // Балансируем: перемещаем max из левой в правую
        minHeap.offer(maxHeap.poll())

        // Поддерживаем размер: левая >= правой
        if (maxHeap.size < minHeap.size) {
            maxHeap.offer(minHeap.poll())
        }
    }

    fun findMedian(): Double {
        return if (maxHeap.size > minHeap.size) {
            maxHeap.peek().toDouble()
        } else {
            (maxHeap.peek() + minHeap.peek()) / 2.0
        }
    }
}

// Пример: добавляем 1, 2, 3
// add(1): maxHeap=[1], minHeap=[]
// add(2): maxHeap=[1], minHeap=[2]
// add(3): maxHeap=[2,1], minHeap=[3]
// median = (2 + 3) / 2 = 2.5? Нет: maxHeap.size > minHeap.size -> 2
```

**K Closest Points to Origin:**
```kotlin
fun kClosest(points: Array<IntArray>, k: Int): Array<IntArray> {
    // Max-Heap размера k (по расстоянию)
    val maxHeap = PriorityQueue<IntArray>(
        compareByDescending { it[0] * it[0] + it[1] * it[1] }
    )

    for (point in points) {
        maxHeap.offer(point)
        if (maxHeap.size > k) {
            maxHeap.poll()
        }
    }

    return maxHeap.toTypedArray()
}
```

**Task Scheduler:**
```kotlin
fun leastInterval(tasks: CharArray, n: Int): Int {
    // Подсчёт частот
    val count = IntArray(26)
    for (task in tasks) count[task - 'A']++

    // Max-Heap по частоте
    val maxHeap = PriorityQueue<Int>(reverseOrder())
    for (c in count) if (c > 0) maxHeap.offer(c)

    var time = 0

    while (maxHeap.isNotEmpty()) {
        val temp = mutableListOf<Int>()

        // Выполняем до n+1 задач
        for (i in 0..n) {
            if (maxHeap.isNotEmpty()) {
                val freq = maxHeap.poll() - 1
                if (freq > 0) temp.add(freq)
            }
            time++

            if (maxHeap.isEmpty() && temp.isEmpty()) break
        }

        // Возвращаем задачи с уменьшенной частотой
        for (freq in temp) maxHeap.offer(freq)
    }

    return time
}
```

**Сложность операций:**
| Операция | Сложность |
|----------|-----------|
| peek() | O(1) |
| offer() | O(log n) |
| poll() | O(log n) |
| heapify | O(n) |

## Answer (EN)

**Heap Theory:**
A heap is a complete binary tree where each node is greater (max-heap) or smaller (min-heap) than its children. Provides O(log n) for insert and extract, O(1) for min/max access.

**Properties:**
- **Min-Heap**: parent <= children (root = minimum)
- **Max-Heap**: parent >= children (root = maximum)
- Stored in array: children of node i at positions 2i+1 and 2i+2

**PriorityQueue in Kotlin/Java:**
```kotlin
// Min-Heap (default)
val minHeap = PriorityQueue<Int>()

// Max-Heap
val maxHeap = PriorityQueue<Int>(reverseOrder())

// With comparator
val customHeap = PriorityQueue<Pair<Int, String>>(compareBy { it.first })
```

**Top K Frequent Elements:**
```kotlin
fun topKFrequent(nums: IntArray, k: Int): IntArray {
    // 1. Count frequencies
    val count = mutableMapOf<Int, Int>()
    for (num in nums) {
        count[num] = count.getOrDefault(num, 0) + 1
    }

    // 2. Min-Heap of size k (keep k most frequent)
    val minHeap = PriorityQueue<Int>(compareBy { count[it] })

    for (num in count.keys) {
        minHeap.offer(num)
        if (minHeap.size > k) {
            minHeap.poll()  // Remove least frequent
        }
    }

    return minHeap.toIntArray()
}
```

**Kth Largest Element:**
```kotlin
// Approach 1: Min-Heap of size k
fun findKthLargest(nums: IntArray, k: Int): Int {
    val minHeap = PriorityQueue<Int>()

    for (num in nums) {
        minHeap.offer(num)
        if (minHeap.size > k) {
            minHeap.poll()
        }
    }

    return minHeap.peek()  // kth largest
}

// Approach 2: QuickSelect (average O(n))
fun findKthLargestQuickSelect(nums: IntArray, k: Int): Int {
    val targetIndex = nums.size - k

    fun quickSelect(left: Int, right: Int): Int {
        val pivot = nums[right]
        var p = left

        for (i in left until right) {
            if (nums[i] <= pivot) {
                nums[i] = nums[p].also { nums[p] = nums[i] }
                p++
            }
        }
        nums[p] = nums[right].also { nums[right] = nums[p] }

        return when {
            p == targetIndex -> nums[p]
            p < targetIndex -> quickSelect(p + 1, right)
            else -> quickSelect(left, p - 1)
        }
    }

    return quickSelect(0, nums.lastIndex)
}
```

**Merge K Sorted Lists:**
```kotlin
fun mergeKLists(lists: Array<ListNode?>): ListNode? {
    if (lists.isEmpty()) return null

    // Min-Heap by node value
    val minHeap = PriorityQueue<ListNode>(compareBy { it.`val` })

    // Add heads of all lists
    for (list in lists) {
        list?.let { minHeap.offer(it) }
    }

    val dummy = ListNode(0)
    var curr = dummy

    while (minHeap.isNotEmpty()) {
        val smallest = minHeap.poll()
        curr.next = smallest
        curr = curr.next!!

        smallest.next?.let { minHeap.offer(it) }
    }

    return dummy.next
}
```

**Median from Data Stream:**
```kotlin
class MedianFinder {
    // Max-Heap for left half (smaller elements)
    private val maxHeap = PriorityQueue<Int>(reverseOrder())
    // Min-Heap for right half (larger elements)
    private val minHeap = PriorityQueue<Int>()

    fun addNum(num: Int) {
        // Add to left half
        maxHeap.offer(num)

        // Balance: move max from left to right
        minHeap.offer(maxHeap.poll())

        // Maintain size: left >= right
        if (maxHeap.size < minHeap.size) {
            maxHeap.offer(minHeap.poll())
        }
    }

    fun findMedian(): Double {
        return if (maxHeap.size > minHeap.size) {
            maxHeap.peek().toDouble()
        } else {
            (maxHeap.peek() + minHeap.peek()) / 2.0
        }
    }
}

// Example: add 1, 2, 3
// add(1): maxHeap=[1], minHeap=[]
// add(2): maxHeap=[1], minHeap=[2]
// add(3): maxHeap=[2,1], minHeap=[3]
// median = 2 (maxHeap.size > minHeap.size)
```

**K Closest Points to Origin:**
```kotlin
fun kClosest(points: Array<IntArray>, k: Int): Array<IntArray> {
    // Max-Heap of size k (by distance)
    val maxHeap = PriorityQueue<IntArray>(
        compareByDescending { it[0] * it[0] + it[1] * it[1] }
    )

    for (point in points) {
        maxHeap.offer(point)
        if (maxHeap.size > k) {
            maxHeap.poll()
        }
    }

    return maxHeap.toTypedArray()
}
```

**Task Scheduler:**
```kotlin
fun leastInterval(tasks: CharArray, n: Int): Int {
    // Count frequencies
    val count = IntArray(26)
    for (task in tasks) count[task - 'A']++

    // Max-Heap by frequency
    val maxHeap = PriorityQueue<Int>(reverseOrder())
    for (c in count) if (c > 0) maxHeap.offer(c)

    var time = 0

    while (maxHeap.isNotEmpty()) {
        val temp = mutableListOf<Int>()

        // Execute up to n+1 tasks
        for (i in 0..n) {
            if (maxHeap.isNotEmpty()) {
                val freq = maxHeap.poll() - 1
                if (freq > 0) temp.add(freq)
            }
            time++

            if (maxHeap.isEmpty() && temp.isEmpty()) break
        }

        // Return tasks with decreased frequency
        for (freq in temp) maxHeap.offer(freq)
    }

    return time
}
```

**Operation Complexity:**
| Operation | Complexity |
|-----------|------------|
| peek() | O(1) |
| offer() | O(log n) |
| poll() | O(log n) |
| heapify | O(n) |

---

## Follow-ups

- How would you implement a heap from scratch?
- What is the difference between heapify and building a heap by insertion?
- When should you use heap vs sorting for Top K problems?

## Related Questions

### Prerequisites (Easier)
- [[q-data-structures-overview--algorithms--easy]] - Data structures basics
- [[q-sorting-algorithms-comparison--algorithms--medium]] - Sorting algorithms

### Related (Same Level)
- [[q-linked-list-algorithms--algorithms--medium]] - Merge lists
- [[q-binary-search-variants--algorithms--medium]] - Search patterns

### Advanced (Harder)
- [[q-advanced-graph-algorithms--algorithms--hard]] - Dijkstra uses heap
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - DP problems
