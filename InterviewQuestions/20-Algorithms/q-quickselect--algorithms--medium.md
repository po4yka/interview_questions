---
id: q-quickselect
title: QuickSelect Algorithm / Алгоритм QuickSelect
aliases:
- QuickSelect Algorithm
- Алгоритм QuickSelect
topic: algorithms
subtopics:
- selection
- divide-and-conquer
- partitioning
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
- q-sorting-algorithms-comparison--algorithms--medium
- q-heap-priority-queue--algorithms--medium
created: 2025-01-26
updated: 2025-01-26
tags:
- algorithms
- selection
- difficulty/medium
- divide-and-conquer
- partitioning
sources:
- https://en.wikipedia.org/wiki/Quickselect
anki_cards:
- slug: q-quickselect-0-en
  language: en
  anki_id: 1769404214119
  synced_at: '2026-01-26T09:10:14.551510'
- slug: q-quickselect-0-ru
  language: ru
  anki_id: 1769404214139
  synced_at: '2026-01-26T09:10:14.553561'
---
# Вопрос (RU)
> Объясните алгоритм QuickSelect для нахождения k-го наименьшего/наибольшего элемента.

# Question (EN)
> Explain QuickSelect algorithm for finding the kth smallest/largest element.

---

## Ответ (RU)

**Задача:**
Найти k-й наименьший (или наибольший) элемент в неотсортированном массиве без полной сортировки.

**Ключевая идея:**
QuickSelect использует тот же принцип разбиения (partition), что и QuickSort, но рекурсивно обрабатывает только одну часть массива вместо обеих.

**Сравнение QuickSelect и QuickSort:**
| Характеристика | QuickSort | QuickSelect |
|----------------|-----------|-------------|
| Цель | Отсортировать весь массив | Найти k-й элемент |
| Рекурсия | Обе части | Только одна часть |
| Среднее время | O(n log n) | O(n) |
| Худшее время | O(n²) | O(n²) |

**Алгоритм:**
1. Выбрать опорный элемент (pivot)
2. Разбить массив: элементы меньше pivot слева, больше — справа
3. Если pivot на позиции k — ответ найден
4. Иначе рекурсивно искать в нужной половине

**Сложность:**
- **Средний случай:** O(n) — на каждом шаге обрабатывается половина массива
- **Худший случай:** O(n²) — когда pivot всегда минимальный/максимальный элемент
- **Память:** O(1) для итеративной версии, O(log n) для рекурсивной

**Оптимизации:**
- **Случайный выбор pivot:** уменьшает вероятность худшего случая
- **Median of Medians:** гарантирует O(n) в худшем случае, но с большей константой

**Реализация:**
```kotlin
// QuickSelect для нахождения k-го наименьшего элемента (0-indexed)
fun quickSelect(arr: IntArray, k: Int): Int {
    return quickSelectHelper(arr, 0, arr.size - 1, k)
}

private fun quickSelectHelper(arr: IntArray, left: Int, right: Int, k: Int): Int {
    if (left == right) return arr[left]

    // Случайный выбор pivot для избежания худшего случая
    val pivotIndex = left + (0..right - left).random()
    val finalPivotIndex = partition(arr, left, right, pivotIndex)

    return when {
        k == finalPivotIndex -> arr[k]
        k < finalPivotIndex -> quickSelectHelper(arr, left, finalPivotIndex - 1, k)
        else -> quickSelectHelper(arr, finalPivotIndex + 1, right, k)
    }
}

private fun partition(arr: IntArray, left: Int, right: Int, pivotIndex: Int): Int {
    val pivotValue = arr[pivotIndex]
    // Перемещаем pivot в конец
    swap(arr, pivotIndex, right)

    var storeIndex = left
    for (i in left until right) {
        if (arr[i] < pivotValue) {
            swap(arr, i, storeIndex)
            storeIndex++
        }
    }
    // Возвращаем pivot на место
    swap(arr, storeIndex, right)
    return storeIndex
}

private fun swap(arr: IntArray, i: Int, j: Int) {
    val temp = arr[i]
    arr[i] = arr[j]
    arr[j] = temp
}
```

**Применения:**
- Нахождение медианы массива
- Top-K элементов (частично отсортировать первые k)
- Статистика порядка (order statistics)
- Алгоритм Introselect в стандартных библиотеках

**Сравнение с подходом на куче:**
| Подход | Время | Память | Когда использовать |
|--------|-------|--------|-------------------|
| QuickSelect | O(n) средн. | O(1) | Единичный запрос k-го элемента |
| Min/Max Heap | O(n log k) | O(k) | Множественные запросы, потоковые данные |
| Полная сортировка | O(n log n) | O(1) | Нужны все элементы в порядке |

## Answer (EN)

**Problem:**
Find the kth smallest (or largest) element in an unsorted array without fully sorting it.

**Key Idea:**
QuickSelect uses the same partition logic as QuickSort, but recursively processes only one partition instead of both.

**QuickSelect vs QuickSort Comparison:**
| Characteristic | QuickSort | QuickSelect |
|----------------|-----------|-------------|
| Goal | Sort entire array | Find kth element |
| Recursion | Both partitions | Only one partition |
| Average time | O(n log n) | O(n) |
| Worst time | O(n²) | O(n²) |

**Algorithm:**
1. Choose a pivot element
2. Partition array: elements smaller than pivot go left, larger go right
3. If pivot is at position k — answer found
4. Otherwise recursively search in the appropriate half

**Complexity:**
- **Average case:** O(n) — each step processes half the remaining elements
- **Worst case:** O(n²) — when pivot is always the min/max element
- **Space:** O(1) for iterative version, O(log n) for recursive

**Optimizations:**
- **Random pivot selection:** reduces probability of worst case
- **Median of Medians:** guarantees O(n) worst case, but with higher constant factor

**Implementation:**
```kotlin
// QuickSelect to find kth smallest element (0-indexed)
fun quickSelect(arr: IntArray, k: Int): Int {
    return quickSelectHelper(arr, 0, arr.size - 1, k)
}

private fun quickSelectHelper(arr: IntArray, left: Int, right: Int, k: Int): Int {
    if (left == right) return arr[left]

    // Random pivot to avoid worst case
    val pivotIndex = left + (0..right - left).random()
    val finalPivotIndex = partition(arr, left, right, pivotIndex)

    return when {
        k == finalPivotIndex -> arr[k]
        k < finalPivotIndex -> quickSelectHelper(arr, left, finalPivotIndex - 1, k)
        else -> quickSelectHelper(arr, finalPivotIndex + 1, right, k)
    }
}

private fun partition(arr: IntArray, left: Int, right: Int, pivotIndex: Int): Int {
    val pivotValue = arr[pivotIndex]
    // Move pivot to end
    swap(arr, pivotIndex, right)

    var storeIndex = left
    for (i in left until right) {
        if (arr[i] < pivotValue) {
            swap(arr, i, storeIndex)
            storeIndex++
        }
    }
    // Move pivot to its final place
    swap(arr, storeIndex, right)
    return storeIndex
}

private fun swap(arr: IntArray, i: Int, j: Int) {
    val temp = arr[i]
    arr[i] = arr[j]
    arr[j] = temp
}
```

**Applications:**
- Finding the median of an array
- Top-K elements (partially sort first k elements)
- Order statistics
- Introselect algorithm in standard libraries

**Comparison with Heap-Based Approach:**
| Approach | Time | Space | When to Use |
|----------|------|-------|-------------|
| QuickSelect | O(n) avg | O(1) | Single query for kth element |
| Min/Max Heap | O(n log k) | O(k) | Multiple queries, streaming data |
| Full Sort | O(n log n) | O(1) | Need all elements in order |

---

## Follow-ups

- How does Median of Medians guarantee O(n) worst case?
- When would you prefer heap-based approach over QuickSelect?
- How to find the kth largest element instead of kth smallest?

## References

- [[c-algorithms]]
- "https://en.wikipedia.org/wiki/Quickselect"

## Related Questions

### Prerequisites (Easier)
- [[q-data-structures-overview--algorithms--easy]] - Data structures basics

### Related (Same Level)
- [[q-sorting-algorithms-comparison--algorithms--medium]] - Sorting algorithms (QuickSort partition)
- [[q-heap-priority-queue--algorithms--medium]] - Heap-based alternative

### Advanced (Harder)
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - DP algorithms

## Дополнительные Вопросы (RU)
- Как алгоритм Median of Medians гарантирует O(n) в худшем случае?
- Когда предпочтительнее использовать подход на куче вместо QuickSelect?
- Как найти k-й наибольший элемент вместо k-го наименьшего?

## Связанные Вопросы (RU)

### Предварительные (проще)
- [[q-data-structures-overview--algorithms--easy]] - Основы структур данных

### Связанные (тот же уровень)
- [[q-sorting-algorithms-comparison--algorithms--medium]] - Алгоритмы сортировки (partition из QuickSort)
- [[q-heap-priority-queue--algorithms--medium]] - Альтернатива на основе кучи

### Продвинутые (сложнее)
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - Динамическое программирование
