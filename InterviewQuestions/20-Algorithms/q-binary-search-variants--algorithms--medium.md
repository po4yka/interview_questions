---
id: algo-005
title: "Binary Search and Variants / Бинарный поиск и варианты"
aliases: ["Binary Search", "Бинарный поиск"]
topic: algorithms
subtopics: [binary-search, divide-and-conquer, searching]
question_kind: coding
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-algorithms
related: [c-algorithms, q-binary-search-trees-bst--algorithms--hard, q-two-pointers-sliding-window--algorithms--medium]
created: 2025-10-12
updated: 2025-11-11
tags: [algorithms, binary-search, difficulty/medium, log-n, searching]
sources: ["https://en.wikipedia.org/wiki/Binary_search_algorithm"]

---
# Вопрос (RU)
> Как работает бинарный поиск? Каковы распространённые варианты и граничные случаи?

# Question (EN)
> How does binary search work? What are common variants and edge cases?

---

## Ответ (RU)

**Теория бинарного поиска:**
Бинарный поиск — алгоритм поиска в отсортированном массиве со сложностью O(log n). Он работает путём деления поискового пространства пополам на каждой итерации, исключая половину элементов.

**Основные принципы:**
- Требует отсортированный массив
- Время: O(log n) — очень быстро
- Память: O(1) — константная
- Ключевая формула: `mid = left + (right - left) / 2` (избегает overflow)

См. также: [[c-algorithms]]

**Классический бинарный поиск:**
```kotlin
// Найти target в отсортированном массиве
fun binarySearch(arr: IntArray, target: Int): Int {
    var left = 0
    var right = arr.size - 1

    while (left <= right) {
        val mid = left + (right - left) / 2  // Избегаем overflow

        when {
            arr[mid] == target -> return mid
            arr[mid] < target -> left = mid + 1
            else -> right = mid - 1
        }
    }

    return -1  // Не найдено
}
```

**Найти первое вхождение:**
```kotlin
// Найти левое вхождение target (для массивов с дубликатами)
fun findFirst(arr: IntArray, target: Int): Int {
    var left = 0
    var right = arr.size - 1
    var result = -1

    while (left <= right) {
        val mid = left + (right - left) / 2

        when {
            arr[mid] == target -> {
                result = mid         // Найдено, но продолжаем искать влево
                right = mid - 1
            }
            arr[mid] < target -> left = mid + 1
            else -> right = mid - 1
        }
    }

    return result
}
```

**Найти последнее вхождение:**
```kotlin
// Найти правое вхождение target
fun findLast(arr: IntArray, target: Int): Int {
    var left = 0
    var right = arr.size - 1
    var result = -1

    while (left <= right) {
        val mid = left + (right - left) / 2

        when {
            arr[mid] == target -> {
                result = mid         // Найдено, но продолжаем искать вправо
                left = mid + 1
            }
            arr[mid] < target -> left = mid + 1
            else -> right = mid - 1
        }
    }

    return result
}
```

**Поиск в повёрнутом массиве:**
```kotlin
// Массив повёрнут в точке: [4,5,6,7,0,1,2]
fun searchRotated(nums: IntArray, target: Int): Int {
    var left = 0
    var right = nums.size - 1

    while (left <= right) {
        val mid = left + (right - left) / 2

        if (nums[mid] == target) return mid

        // Определяем, какая половина отсортирована
        if (nums[left] <= nums[mid]) {
            // Левая половина отсортирована
            if (target >= nums[left] && target < nums[mid]) {
                right = mid - 1  // Target в левой половине
            } else {
                left = mid + 1   // Target в правой половине
            }
        } else {
            // Правая половина отсортирована
            if (target > nums[mid] && target <= nums[right]) {
                left = mid + 1   // Target в правой половине
            } else {
                right = mid - 1  // Target в левой половине
            }
        }
    }

    return -1
}
```

**Найти пиковый элемент:**
```kotlin
// Найти любой пик (элемент больше соседей)
fun findPeakElement(nums: IntArray): Int {
    var left = 0
    var right = nums.size - 1

    while (left < right) {
        val mid = left + (right - left) / 2

        if (nums[mid] < nums[mid + 1]) {
            // Пик справа
            left = mid + 1
        } else {
            // Пик слева или в mid
            right = mid
        }
    }

    return left
}
```

**Бинарный поиск по ответу:**
```kotlin
// Найти минимальную скорость поедания бананов за h часов
fun minEatingSpeed(piles: IntArray, h: Int): Int {
    var left = 1
    var right = piles.maxOrNull()!!

    while (left < right) {
        val mid = left + (right - left) / 2
        val hoursNeeded = piles.sumOf { (it + mid - 1) / mid }

        if (hoursNeeded <= h) {
            right = mid  // Можем есть медленнее
        } else {
            left = mid + 1  // Нужно есть быстрее
        }
    }

    return left
}
```

## Answer (EN)

**Binary Search Theory:**
Binary search is a search algorithm for sorted arrays with O(log n) complexity. It works by dividing the search space in half on each iteration, eliminating half the elements.

**Main principles:**
- Requires sorted array
- Time: O(log n) - extremely fast
- Space: O(1) - constant
- Key formula: `mid = left + (right - left) / 2` (avoids overflow)

See also: [[c-algorithms]]

**Classic Binary Search:**
```kotlin
// Find target in sorted array
fun binarySearch(arr: IntArray, target: Int): Int {
    var left = 0
    var right = arr.size - 1

    while (left <= right) {
        val mid = left + (right - left) / 2  // Avoid overflow

        when {
            arr[mid] == target -> return mid
            arr[mid] < target -> left = mid + 1
            else -> right = mid - 1
        }
    }

    return -1  // Not found
}
```

**Find First Occurrence:**
```kotlin
// Find leftmost occurrence of target (for arrays with duplicates)
fun findFirst(arr: IntArray, target: Int): Int {
    var left = 0
    var right = arr.size - 1
    var result = -1

    while (left <= right) {
        val mid = left + (right - left) / 2

        when {
            arr[mid] == target -> {
                result = mid         // Found, but keep searching left
                right = mid - 1
            }
            arr[mid] < target -> left = mid + 1
            else -> right = mid - 1
        }
    }

    return result
}
```

**Find Last Occurrence:**
```kotlin
// Find rightmost occurrence of target
fun findLast(arr: IntArray, target: Int): Int {
    var left = 0
    var right = arr.size - 1
    var result = -1

    while (left <= right) {
        val mid = left + (right - left) / 2

        when {
            arr[mid] == target -> {
                result = mid         // Found, but keep searching right
                left = mid + 1
            }
            arr[mid] < target -> left = mid + 1
            else -> right = mid - 1
        }
    }

    return result
}
```

**Search in Rotated Array:**
```kotlin
// Array rotated at pivot: [4,5,6,7,0,1,2]
fun searchRotated(nums: IntArray, target: Int): Int {
    var left = 0
    var right = nums.size - 1

    while (left <= right) {
        val mid = left + (right - left) / 2

        if (nums[mid] == target) return mid

        // Determine which half is sorted
        if (nums[left] <= nums[mid]) {
            // Left half is sorted
            if (target >= nums[left] && target < nums[mid]) {
                right = mid - 1  // Target in left half
            } else {
                left = mid + 1   // Target in right half
            }
        } else {
            // Right half is sorted
            if (target > nums[mid] && target <= nums[right]) {
                left = mid + 1   // Target in right half
            } else {
                right = mid - 1  // Target in left half
            }
        }
    }

    return -1
}
```

**Find Peak Element:**
```kotlin
// Find any peak (element greater than neighbors)
fun findPeakElement(nums: IntArray): Int {
    var left = 0
    var right = nums.size - 1

    while (left < right) {
        val mid = left + (right - left) / 2

        if (nums[mid] < nums[mid + 1]) {
            // Peak is on the right
            left = mid + 1
        } else {
            // Peak is on the left or at mid
            right = mid
        }
    }

    return left
}
```

**Binary Search on Answer:**
```kotlin
// Find minimum eating speed to finish all bananas in h hours
fun minEatingSpeed(piles: IntArray, h: Int): Int {
    var left = 1
    var right = piles.maxOrNull()!!

    while (left < right) {
        val mid = left + (right - left) / 2
        val hoursNeeded = piles.sumOf { (it + mid - 1) / mid }

        if (hoursNeeded <= h) {
            right = mid  // Can eat slower
        } else {
            left = mid + 1  // Must eat faster
        }
    }

    return left
}
```

---

## Дополнительные Вопросы (RU)

- Как реализовать бинарный поиск рекурсивно?
- В чём разница между `lower_bound` и `upper_bound`?
- Как найти медиану двух отсортированных массивов?

## Follow-ups

- How do you implement binary search recursively?
- What is the difference between lower_bound and upper_bound?
- How do you find the median of two sorted arrays?

## Ссылки (RU)

- [[c-algorithms]]
- "https://en.wikipedia.org/wiki/Binary_search_algorithm"

## References

- [[c-algorithms]]
- "https://en.wikipedia.org/wiki/Binary_search_algorithm"

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-data-structures-overview--algorithms--easy]] - Базовые структуры данных
- [[q-sorting-algorithms-comparison--algorithms--medium]] - Концепции сортировки

### Связанные (тот Же уровень)
- [[q-two-pointers-sliding-window--algorithms--medium]] - Техника двух указателей
- [[q-backtracking-algorithms--algorithms--hard]] - Алгоритмы с возвратом (backtracking)

### Продвинутые (сложнее)
- [[q-binary-search-trees-bst--algorithms--hard]] - Реализация деревьев поиска (BST)

## Related Questions

### Prerequisites (Easier)
- [[q-data-structures-overview--algorithms--easy]] - Data structures basics
- [[q-sorting-algorithms-comparison--algorithms--medium]] - Sorting concepts

### Related (Same Level)
- [[q-two-pointers-sliding-window--algorithms--medium]] - Two pointers technique
- [[q-backtracking-algorithms--algorithms--hard]] - Backtracking algorithms

### Advanced (Harder)
- [[q-binary-search-trees-bst--algorithms--hard]] - BST implementation
