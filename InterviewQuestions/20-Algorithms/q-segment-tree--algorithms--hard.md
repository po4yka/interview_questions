---
id: algo-segment-tree
title: Segment Tree / Дерево отрезков
aliases:
- Segment Tree
- Range Query Tree
- Interval Tree
- Дерево отрезков
- Дерево интервалов
topic: algorithms
subtopics:
- data-structures
- range-queries
- trees
question_kind: coding
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-algorithms
related:
- q-prefix-sum-range-queries--algorithms--medium
- q-binary-search-trees-bst--algorithms--hard
created: 2026-01-26
updated: 2026-01-26
tags:
- algorithms
- data-structures
- difficulty/hard
- range-queries
- trees
sources:
- https://en.wikipedia.org/wiki/Segment_tree
- https://cp-algorithms.com/data_structures/segment_tree.html
anki_cards:
- slug: algo-segment-tree-0-en
  language: en
  anki_id: 1769404210665
  synced_at: '2026-01-26T09:10:14.440969'
- slug: algo-segment-tree-0-ru
  language: ru
  anki_id: 1769404210690
  synced_at: '2026-01-26T09:10:14.442613'
---
# Вопрос (RU)
> Объясните дерево отрезков. Как оно поддерживает запросы и обновления на отрезках?

# Question (EN)
> Explain Segment Tree. How does it support range queries and updates?

---

## Ответ (RU)

**Что решает дерево отрезков:**
Дерево отрезков - структура данных для эффективных запросов на отрезках (сумма, минимум, максимум) с поддержкой обновлений. Хранит агрегированные значения для сегментов массива.

**Структура дерева:**
- Полное бинарное дерево высотой O(log n)
- Каждый узел хранит агрегат для своего диапазона
- Листья соответствуют элементам исходного массива
- Хранится в массиве размером 4n (или 2n для точного размера)

**Сложность:**
| Операция | Время |
|----------|-------|
| Построение | O(n) |
| Точечный запрос | O(log n) |
| Запрос на отрезке | O(log n) |
| Точечное обновление | O(log n) |
| Обновление отрезка (lazy) | O(log n) |
| Память | O(n) |

**Базовая реализация (сумма):**
```kotlin
class SegmentTree(private val nums: IntArray) {
    private val n = nums.size
    private val tree = IntArray(4 * n)  // Достаточно места для дерева

    init {
        if (n > 0) build(0, 0, n - 1)
    }

    // Построение дерева: O(n)
    private fun build(node: Int, start: Int, end: Int) {
        if (start == end) {
            // Лист - храним значение элемента
            tree[node] = nums[start]
        } else {
            val mid = (start + end) / 2
            val leftChild = 2 * node + 1
            val rightChild = 2 * node + 2

            build(leftChild, start, mid)
            build(rightChild, mid + 1, end)

            // Внутренний узел - агрегат детей
            tree[node] = tree[leftChild] + tree[rightChild]
        }
    }

    // Точечное обновление: O(log n)
    fun update(index: Int, value: Int) {
        update(0, 0, n - 1, index, value)
    }

    private fun update(node: Int, start: Int, end: Int, idx: Int, value: Int) {
        if (start == end) {
            // Нашли лист - обновляем
            nums[idx] = value
            tree[node] = value
        } else {
            val mid = (start + end) / 2
            val leftChild = 2 * node + 1
            val rightChild = 2 * node + 2

            if (idx <= mid) {
                update(leftChild, start, mid, idx, value)
            } else {
                update(rightChild, mid + 1, end, idx, value)
            }

            // Пересчитываем агрегат
            tree[node] = tree[leftChild] + tree[rightChild]
        }
    }

    // Запрос на отрезке [left, right]: O(log n)
    fun query(left: Int, right: Int): Int {
        return query(0, 0, n - 1, left, right)
    }

    private fun query(node: Int, start: Int, end: Int, left: Int, right: Int): Int {
        // Случай 1: Отрезок полностью вне диапазона
        if (right < start || left > end) {
            return 0  // Нейтральный элемент для суммы
        }

        // Случай 2: Отрезок полностью покрывает диапазон
        if (left <= start && end <= right) {
            return tree[node]
        }

        // Случай 3: Частичное пересечение - спрашиваем обоих детей
        val mid = (start + end) / 2
        val leftChild = 2 * node + 1
        val rightChild = 2 * node + 2

        val leftSum = query(leftChild, start, mid, left, right)
        val rightSum = query(rightChild, mid + 1, end, left, right)

        return leftSum + rightSum
    }
}

// Использование
val tree = SegmentTree(intArrayOf(1, 3, 5, 7, 9, 11))
println(tree.query(1, 3))  // 3 + 5 + 7 = 15
tree.update(2, 6)          // Меняем 5 на 6
println(tree.query(1, 3))  // 3 + 6 + 7 = 16
```

**Дерево отрезков для минимума:**
```kotlin
class MinSegmentTree(private val nums: IntArray) {
    private val n = nums.size
    private val tree = IntArray(4 * n) { Int.MAX_VALUE }

    init {
        if (n > 0) build(0, 0, n - 1)
    }

    private fun build(node: Int, start: Int, end: Int) {
        if (start == end) {
            tree[node] = nums[start]
        } else {
            val mid = (start + end) / 2
            build(2 * node + 1, start, mid)
            build(2 * node + 2, mid + 1, end)
            tree[node] = minOf(tree[2 * node + 1], tree[2 * node + 2])
        }
    }

    fun queryMin(left: Int, right: Int): Int {
        return queryMin(0, 0, n - 1, left, right)
    }

    private fun queryMin(node: Int, start: Int, end: Int, left: Int, right: Int): Int {
        if (right < start || left > end) return Int.MAX_VALUE
        if (left <= start && end <= right) return tree[node]

        val mid = (start + end) / 2
        return minOf(
            queryMin(2 * node + 1, start, mid, left, right),
            queryMin(2 * node + 2, mid + 1, end, left, right)
        )
    }
}
```

**Ленивое распространение (Lazy Propagation):**
Для эффективных обновлений на отрезках используется отложенное обновление.

```kotlin
class LazySegmentTree(private val n: Int) {
    private val tree = IntArray(4 * n)
    private val lazy = IntArray(4 * n)  // Отложенные обновления

    // Применить отложенное обновление к узлу
    private fun pushDown(node: Int, start: Int, end: Int) {
        if (lazy[node] != 0) {
            // Применяем к текущему узлу
            tree[node] += lazy[node] * (end - start + 1)

            // Если не лист - передаем детям
            if (start != end) {
                lazy[2 * node + 1] += lazy[node]
                lazy[2 * node + 2] += lazy[node]
            }

            lazy[node] = 0
        }
    }

    // Прибавить value ко всем элементам [left, right]
    fun rangeUpdate(left: Int, right: Int, value: Int) {
        rangeUpdate(0, 0, n - 1, left, right, value)
    }

    private fun rangeUpdate(
        node: Int, start: Int, end: Int,
        left: Int, right: Int, value: Int
    ) {
        pushDown(node, start, end)

        if (right < start || left > end) return

        if (left <= start && end <= right) {
            // Полностью покрыт - помечаем для ленивого обновления
            lazy[node] += value
            pushDown(node, start, end)
            return
        }

        val mid = (start + end) / 2
        rangeUpdate(2 * node + 1, start, mid, left, right, value)
        rangeUpdate(2 * node + 2, mid + 1, end, left, right, value)

        tree[node] = tree[2 * node + 1] + tree[2 * node + 2]
    }

    fun query(left: Int, right: Int): Int {
        return query(0, 0, n - 1, left, right)
    }

    private fun query(node: Int, start: Int, end: Int, left: Int, right: Int): Int {
        pushDown(node, start, end)

        if (right < start || left > end) return 0
        if (left <= start && end <= right) return tree[node]

        val mid = (start + end) / 2
        return query(2 * node + 1, start, mid, left, right) +
               query(2 * node + 2, mid + 1, end, left, right)
    }
}
```

**Сравнение с Fenwick Tree (BIT):**

| Критерий | Segment Tree | Fenwick Tree |
|----------|--------------|--------------|
| Память | O(4n) | O(n) |
| Код | Сложнее | Проще |
| Range update | Да (lazy) | Ограниченно |
| Операции | Любые (min, max, gcd) | Обратимые (sum) |
| Константа | Больше | Меньше |

**Когда использовать Segment Tree:**
- Нужны range min/max/gcd запросы
- Требуются обновления на отрезках
- Нужна гибкость для сложных операций

**Когда использовать Fenwick Tree:**
- Только range sum запросы
- Критична память
- Нужен простой код

**Типичные задачи:**
1. **Range Sum Query - Mutable** (LeetCode 307)
2. **Count of Range Sum** (LeetCode 327)
3. **Count of Smaller Numbers After Self** (LeetCode 315)
4. **Range Minimum Query** (RMQ)
5. **Skyline Problem** (LeetCode 218)

## Answer (EN)

**What Segment Tree Solves:**
A Segment Tree is a data structure for efficient range queries (sum, min, max) with update support. It stores aggregated values for segments of an array.

**Tree Structure:**
- Complete binary tree with height O(log n)
- Each node stores aggregate for its range
- Leaves correspond to original array elements
- Stored in array of size 4n (or 2n for exact size)

**Complexity:**
| Operation | Time |
|-----------|------|
| Build | O(n) |
| Point Query | O(log n) |
| Range Query | O(log n) |
| Point Update | O(log n) |
| Range Update (lazy) | O(log n) |
| Space | O(n) |

**Basic Implementation (Sum):**
```kotlin
class SegmentTree(private val nums: IntArray) {
    private val n = nums.size
    private val tree = IntArray(4 * n)  // Enough space for tree

    init {
        if (n > 0) build(0, 0, n - 1)
    }

    // Build tree: O(n)
    private fun build(node: Int, start: Int, end: Int) {
        if (start == end) {
            // Leaf - store element value
            tree[node] = nums[start]
        } else {
            val mid = (start + end) / 2
            val leftChild = 2 * node + 1
            val rightChild = 2 * node + 2

            build(leftChild, start, mid)
            build(rightChild, mid + 1, end)

            // Internal node - aggregate of children
            tree[node] = tree[leftChild] + tree[rightChild]
        }
    }

    // Point update: O(log n)
    fun update(index: Int, value: Int) {
        update(0, 0, n - 1, index, value)
    }

    private fun update(node: Int, start: Int, end: Int, idx: Int, value: Int) {
        if (start == end) {
            // Found leaf - update
            nums[idx] = value
            tree[node] = value
        } else {
            val mid = (start + end) / 2
            val leftChild = 2 * node + 1
            val rightChild = 2 * node + 2

            if (idx <= mid) {
                update(leftChild, start, mid, idx, value)
            } else {
                update(rightChild, mid + 1, end, idx, value)
            }

            // Recalculate aggregate
            tree[node] = tree[leftChild] + tree[rightChild]
        }
    }

    // Range query [left, right]: O(log n)
    fun query(left: Int, right: Int): Int {
        return query(0, 0, n - 1, left, right)
    }

    private fun query(node: Int, start: Int, end: Int, left: Int, right: Int): Int {
        // Case 1: Range completely outside
        if (right < start || left > end) {
            return 0  // Neutral element for sum
        }

        // Case 2: Range completely covers node
        if (left <= start && end <= right) {
            return tree[node]
        }

        // Case 3: Partial overlap - query both children
        val mid = (start + end) / 2
        val leftChild = 2 * node + 1
        val rightChild = 2 * node + 2

        val leftSum = query(leftChild, start, mid, left, right)
        val rightSum = query(rightChild, mid + 1, end, left, right)

        return leftSum + rightSum
    }
}

// Usage
val tree = SegmentTree(intArrayOf(1, 3, 5, 7, 9, 11))
println(tree.query(1, 3))  // 3 + 5 + 7 = 15
tree.update(2, 6)          // Change 5 to 6
println(tree.query(1, 3))  // 3 + 6 + 7 = 16
```

**Segment Tree for Minimum:**
```kotlin
class MinSegmentTree(private val nums: IntArray) {
    private val n = nums.size
    private val tree = IntArray(4 * n) { Int.MAX_VALUE }

    init {
        if (n > 0) build(0, 0, n - 1)
    }

    private fun build(node: Int, start: Int, end: Int) {
        if (start == end) {
            tree[node] = nums[start]
        } else {
            val mid = (start + end) / 2
            build(2 * node + 1, start, mid)
            build(2 * node + 2, mid + 1, end)
            tree[node] = minOf(tree[2 * node + 1], tree[2 * node + 2])
        }
    }

    fun queryMin(left: Int, right: Int): Int {
        return queryMin(0, 0, n - 1, left, right)
    }

    private fun queryMin(node: Int, start: Int, end: Int, left: Int, right: Int): Int {
        if (right < start || left > end) return Int.MAX_VALUE
        if (left <= start && end <= right) return tree[node]

        val mid = (start + end) / 2
        return minOf(
            queryMin(2 * node + 1, start, mid, left, right),
            queryMin(2 * node + 2, mid + 1, end, left, right)
        )
    }
}
```

**Lazy Propagation:**
For efficient range updates, we use deferred (lazy) updates.

```kotlin
class LazySegmentTree(private val n: Int) {
    private val tree = IntArray(4 * n)
    private val lazy = IntArray(4 * n)  // Deferred updates

    // Apply pending lazy update to node
    private fun pushDown(node: Int, start: Int, end: Int) {
        if (lazy[node] != 0) {
            // Apply to current node
            tree[node] += lazy[node] * (end - start + 1)

            // If not leaf - propagate to children
            if (start != end) {
                lazy[2 * node + 1] += lazy[node]
                lazy[2 * node + 2] += lazy[node]
            }

            lazy[node] = 0
        }
    }

    // Add value to all elements in [left, right]
    fun rangeUpdate(left: Int, right: Int, value: Int) {
        rangeUpdate(0, 0, n - 1, left, right, value)
    }

    private fun rangeUpdate(
        node: Int, start: Int, end: Int,
        left: Int, right: Int, value: Int
    ) {
        pushDown(node, start, end)

        if (right < start || left > end) return

        if (left <= start && end <= right) {
            // Completely covered - mark for lazy update
            lazy[node] += value
            pushDown(node, start, end)
            return
        }

        val mid = (start + end) / 2
        rangeUpdate(2 * node + 1, start, mid, left, right, value)
        rangeUpdate(2 * node + 2, mid + 1, end, left, right, value)

        tree[node] = tree[2 * node + 1] + tree[2 * node + 2]
    }

    fun query(left: Int, right: Int): Int {
        return query(0, 0, n - 1, left, right)
    }

    private fun query(node: Int, start: Int, end: Int, left: Int, right: Int): Int {
        pushDown(node, start, end)

        if (right < start || left > end) return 0
        if (left <= start && end <= right) return tree[node]

        val mid = (start + end) / 2
        return query(2 * node + 1, start, mid, left, right) +
               query(2 * node + 2, mid + 1, end, left, right)
    }
}
```

**Comparison with Fenwick Tree (BIT):**

| Criteria | Segment Tree | Fenwick Tree |
|----------|--------------|--------------|
| Space | O(4n) | O(n) |
| Code | More complex | Simpler |
| Range update | Yes (lazy) | Limited |
| Operations | Any (min, max, gcd) | Invertible (sum) |
| Constant factor | Higher | Lower |

**When to Use Segment Tree:**
- Need range min/max/gcd queries
- Require range updates
- Need flexibility for complex operations

**When to Use Fenwick Tree:**
- Only range sum queries
- Memory is critical
- Need simple code

**Common Problems:**
1. **Range Sum Query - Mutable** (LeetCode 307)
2. **Count of Range Sum** (LeetCode 327)
3. **Count of Smaller Numbers After Self** (LeetCode 315)
4. **Range Minimum Query** (RMQ)
5. **Skyline Problem** (LeetCode 218)

---

## Follow-ups

- How would you implement a 2D Segment Tree?
- Can you extend Segment Tree to support arbitrary associative operations?
- How does persistent Segment Tree work for versioned queries?

## Related Questions

### Prerequisites (Easier)
- [[q-prefix-sum-range-queries--algorithms--medium]] - Prefix sums and range queries
- [[q-binary-search-trees-bst--algorithms--hard]] - Tree fundamentals

### Related (Same Level)
- [[q-advanced-graph-algorithms--algorithms--hard]] - Advanced algorithms
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - DP patterns

### Advanced (Harder)
- Persistent Segment Tree
- Merge Sort Tree
- 2D Segment Tree
