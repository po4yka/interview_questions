---
id: q-fenwick-tree
title: Fenwick Tree (Binary Indexed Tree) / Дерево Фенвика
aliases:
- Fenwick Tree
- Binary Indexed Tree
- BIT
- Дерево Фенвика
- Двоичное индексированное дерево
topic: algorithms
subtopics:
- data-structures
- range-queries
- bit-manipulation
question_kind: coding
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-algorithms
related:
- q-prefix-sum-range-queries--algorithms--medium
- q-bit-manipulation--algorithms--medium
created: 2026-01-26
updated: 2026-01-26
tags:
- algorithms
- data-structures
- difficulty/medium
- range-queries
- bit-manipulation
sources:
- https://en.wikipedia.org/wiki/Fenwick_tree
- https://cp-algorithms.com/data_structures/fenwick.html
anki_cards:
- slug: q-fenwick-tree-0-en
  language: en
  anki_id: 1769404210965
  synced_at: '2026-01-26T09:10:14.452276'
- slug: q-fenwick-tree-0-ru
  language: ru
  anki_id: 1769404210990
  synced_at: '2026-01-26T09:10:14.453835'
---
# Вопрос (RU)
> Объясните дерево Фенвика (BIT). Как оно работает и когда предпочтительнее дерева отрезков?

# Question (EN)
> Explain Fenwick Tree (BIT). How does it work and when is it preferred over Segment Tree?

---

## Ответ (RU)

**Что такое дерево Фенвика:**
Дерево Фенвика (Binary Indexed Tree, BIT) - структура данных для эффективного вычисления **префиксных сумм** и **точечных обновлений** за O(log n). Использует битовые операции для навигации по дереву.

**Ключевая идея - lowbit:**
```kotlin
// Получить младший установленный бит числа
fun lowbit(x: Int): Int = x and (-x)

// Примеры:
// lowbit(6)  = lowbit(0110) = 2 (0010)
// lowbit(12) = lowbit(1100) = 4 (0100)
// lowbit(8)  = lowbit(1000) = 8 (1000)
```

**Структура дерева:**
```
Индекс i отвечает за диапазон [i - lowbit(i) + 1, i]

tree[1]  -> отвечает за arr[1]           (lowbit=1, диапазон 1)
tree[2]  -> отвечает за arr[1..2]        (lowbit=2, диапазон 2)
tree[3]  -> отвечает за arr[3]           (lowbit=1, диапазон 1)
tree[4]  -> отвечает за arr[1..4]        (lowbit=4, диапазон 4)
tree[5]  -> отвечает за arr[5]           (lowbit=1, диапазон 1)
tree[6]  -> отвечает за arr[5..6]        (lowbit=2, диапазон 2)
tree[7]  -> отвечает за arr[7]           (lowbit=1, диапазон 1)
tree[8]  -> отвечает за arr[1..8]        (lowbit=8, диапазон 8)
```

**Реализация:**
```kotlin
class FenwickTree(private val n: Int) {
    private val tree = IntArray(n + 1)

    // Добавить delta к элементу с индексом i (1-indexed)
    // O(log n)
    fun update(i: Int, delta: Int) {
        var idx = i
        while (idx <= n) {
            tree[idx] += delta
            idx += idx and (-idx)  // Переход к родителю
        }
    }

    // Префиксная сумма [1, i]
    // O(log n)
    fun prefixSum(i: Int): Int {
        var sum = 0
        var idx = i
        while (idx > 0) {
            sum += tree[idx]
            idx -= idx and (-idx)  // Переход к предыдущему диапазону
        }
        return sum
    }

    // Сумма диапазона [left, right]
    fun rangeSum(left: Int, right: Int): Int {
        return prefixSum(right) - prefixSum(left - 1)
    }
}
```

**Построение из массива:**
```kotlin
// Способ 1: Последовательные обновления - O(n log n)
fun buildNaive(arr: IntArray): FenwickTree {
    val bit = FenwickTree(arr.size)
    for (i in arr.indices) {
        bit.update(i + 1, arr[i])
    }
    return bit
}

// Способ 2: Линейное построение - O(n)
fun buildLinear(arr: IntArray): IntArray {
    val n = arr.size
    val tree = IntArray(n + 1)

    // Копируем значения
    for (i in arr.indices) {
        tree[i + 1] = arr[i]
    }

    // Распространяем значения вверх
    for (i in 1..n) {
        val parent = i + (i and (-i))
        if (parent <= n) {
            tree[parent] += tree[i]
        }
    }

    return tree
}
```

**Сравнение с деревом отрезков:**

| Критерий | Дерево Фенвика | Дерево отрезков |
|----------|---------------|-----------------|
| Память | O(n) | O(2n) или O(4n) |
| Код | ~20 строк | ~50+ строк |
| Операции | Только +/XOR | Любая ассоциативная |
| Запросы | Только префиксы | Любые диапазоны |
| Константа | Меньше | Больше |

**Когда использовать Fenwick Tree:**
- Префиксные суммы с обновлениями
- Подсчёт инверсий в массиве
- Частотный анализ (counting sort)
- Когда важна простота кода и память

**Когда использовать Segment Tree:**
- Нужен min/max на диапазоне
- Сложные операции (не коммутативные)
- Range update + range query
- Ленивое распространение

**Подсчёт инверсий:**
```kotlin
// Количество пар (i, j) где i < j и arr[i] > arr[j]
fun countInversions(arr: IntArray): Long {
    // Координатная компрессия
    val sorted = arr.sorted().distinct()
    val rank = sorted.withIndex().associate { it.value to it.index + 1 }

    val bit = FenwickTree(sorted.size)
    var inversions = 0L

    // Обрабатываем справа налево
    for (i in arr.indices.reversed()) {
        val r = rank[arr[i]]!!
        // Сколько элементов < arr[i] уже справа
        inversions += bit.prefixSum(r - 1)
        bit.update(r, 1)
    }

    return inversions
}
```

**2D Fenwick Tree:**
```kotlin
class FenwickTree2D(private val n: Int, private val m: Int) {
    private val tree = Array(n + 1) { IntArray(m + 1) }

    fun update(x: Int, y: Int, delta: Int) {
        var i = x
        while (i <= n) {
            var j = y
            while (j <= m) {
                tree[i][j] += delta
                j += j and (-j)
            }
            i += i and (-i)
        }
    }

    fun prefixSum(x: Int, y: Int): Int {
        var sum = 0
        var i = x
        while (i > 0) {
            var j = y
            while (j > 0) {
                sum += tree[i][j]
                j -= j and (-j)
            }
            i -= i and (-i)
        }
        return sum
    }

    // Сумма прямоугольника (x1,y1) до (x2,y2)
    fun rangeSum(x1: Int, y1: Int, x2: Int, y2: Int): Int {
        return prefixSum(x2, y2) - prefixSum(x1 - 1, y2) -
               prefixSum(x2, y1 - 1) + prefixSum(x1 - 1, y1 - 1)
    }
}
```

**Сложность:**
- **Update**: O(log n)
- **Query (prefix sum)**: O(log n)
- **Build**: O(n) оптимальное, O(n log n) наивное
- **Память**: O(n)

## Answer (EN)

**What is Fenwick Tree:**
Fenwick Tree (Binary Indexed Tree, BIT) is a data structure for efficient **prefix sum queries** and **point updates** in O(log n). Uses bitwise operations for tree navigation.

**Key idea - lowbit:**
```kotlin
// Get lowest set bit of a number
fun lowbit(x: Int): Int = x and (-x)

// Examples:
// lowbit(6)  = lowbit(0110) = 2 (0010)
// lowbit(12) = lowbit(1100) = 4 (0100)
// lowbit(8)  = lowbit(1000) = 8 (1000)
```

**Tree structure:**
```
Index i is responsible for range [i - lowbit(i) + 1, i]

tree[1]  -> covers arr[1]           (lowbit=1, range 1)
tree[2]  -> covers arr[1..2]        (lowbit=2, range 2)
tree[3]  -> covers arr[3]           (lowbit=1, range 1)
tree[4]  -> covers arr[1..4]        (lowbit=4, range 4)
tree[5]  -> covers arr[5]           (lowbit=1, range 1)
tree[6]  -> covers arr[5..6]        (lowbit=2, range 2)
tree[7]  -> covers arr[7]           (lowbit=1, range 1)
tree[8]  -> covers arr[1..8]        (lowbit=8, range 8)
```

**Implementation:**
```kotlin
class FenwickTree(private val n: Int) {
    private val tree = IntArray(n + 1)

    // Add delta to element at index i (1-indexed)
    // O(log n)
    fun update(i: Int, delta: Int) {
        var idx = i
        while (idx <= n) {
            tree[idx] += delta
            idx += idx and (-idx)  // Move to parent
        }
    }

    // Prefix sum [1, i]
    // O(log n)
    fun prefixSum(i: Int): Int {
        var sum = 0
        var idx = i
        while (idx > 0) {
            sum += tree[idx]
            idx -= idx and (-idx)  // Move to previous range
        }
        return sum
    }

    // Range sum [left, right]
    fun rangeSum(left: Int, right: Int): Int {
        return prefixSum(right) - prefixSum(left - 1)
    }
}
```

**Building from array:**
```kotlin
// Method 1: Sequential updates - O(n log n)
fun buildNaive(arr: IntArray): FenwickTree {
    val bit = FenwickTree(arr.size)
    for (i in arr.indices) {
        bit.update(i + 1, arr[i])
    }
    return bit
}

// Method 2: Linear construction - O(n)
fun buildLinear(arr: IntArray): IntArray {
    val n = arr.size
    val tree = IntArray(n + 1)

    // Copy values
    for (i in arr.indices) {
        tree[i + 1] = arr[i]
    }

    // Propagate values upward
    for (i in 1..n) {
        val parent = i + (i and (-i))
        if (parent <= n) {
            tree[parent] += tree[i]
        }
    }

    return tree
}
```

**Comparison with Segment Tree:**

| Criterion | Fenwick Tree | Segment Tree |
|-----------|-------------|--------------|
| Memory | O(n) | O(2n) or O(4n) |
| Code | ~20 lines | ~50+ lines |
| Operations | Only +/XOR | Any associative |
| Queries | Prefix only | Any range |
| Constant factor | Lower | Higher |

**When to use Fenwick Tree:**
- Prefix sums with updates
- Counting inversions
- Frequency analysis (counting sort)
- When code simplicity and memory matter

**When to use Segment Tree:**
- Need min/max on range
- Complex operations (non-commutative)
- Range update + range query
- Lazy propagation needed

**Counting inversions:**
```kotlin
// Count pairs (i, j) where i < j and arr[i] > arr[j]
fun countInversions(arr: IntArray): Long {
    // Coordinate compression
    val sorted = arr.sorted().distinct()
    val rank = sorted.withIndex().associate { it.value to it.index + 1 }

    val bit = FenwickTree(sorted.size)
    var inversions = 0L

    // Process right to left
    for (i in arr.indices.reversed()) {
        val r = rank[arr[i]]!!
        // How many elements < arr[i] are already to the right
        inversions += bit.prefixSum(r - 1)
        bit.update(r, 1)
    }

    return inversions
}
```

**2D Fenwick Tree:**
```kotlin
class FenwickTree2D(private val n: Int, private val m: Int) {
    private val tree = Array(n + 1) { IntArray(m + 1) }

    fun update(x: Int, y: Int, delta: Int) {
        var i = x
        while (i <= n) {
            var j = y
            while (j <= m) {
                tree[i][j] += delta
                j += j and (-j)
            }
            i += i and (-i)
        }
    }

    fun prefixSum(x: Int, y: Int): Int {
        var sum = 0
        var i = x
        while (i > 0) {
            var j = y
            while (j > 0) {
                sum += tree[i][j]
                j -= j and (-j)
            }
            i -= i and (-i)
        }
        return sum
    }

    // Sum of rectangle from (x1,y1) to (x2,y2)
    fun rangeSum(x1: Int, y1: Int, x2: Int, y2: Int): Int {
        return prefixSum(x2, y2) - prefixSum(x1 - 1, y2) -
               prefixSum(x2, y1 - 1) + prefixSum(x1 - 1, y1 - 1)
    }
}
```

**Complexity:**
- **Update**: O(log n)
- **Query (prefix sum)**: O(log n)
- **Build**: O(n) optimal, O(n log n) naive
- **Space**: O(n)

---

## Follow-ups

- How would you implement range update with point query using Fenwick Tree?
- Can Fenwick Tree support range minimum queries? Why or why not?
- How do you extend Fenwick Tree for range updates AND range queries?
- What modifications are needed to support negative numbers and arbitrary starting values?

## Related Questions

### Prerequisites (Easier)
- [[q-prefix-sum-range-queries--algorithms--medium]] - Prefix sum fundamentals
- [[q-bit-manipulation--algorithms--medium]] - Bitwise operations
- [[q-data-structures-overview--algorithms--easy]] - Data structures basics

### Related (Same Level)
- [[q-binary-search-variants--algorithms--medium]] - Binary search patterns

### Advanced (Harder)
- [[q-advanced-graph-algorithms--algorithms--hard]] - Advanced data structures
