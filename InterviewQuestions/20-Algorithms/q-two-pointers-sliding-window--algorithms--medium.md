---
id: 20251012-200006
title: "Two Pointers and Sliding Window Patterns / Паттерны двух указателей и скользящего окна"
aliases: ["Two Pointers", "Sliding Window", "Два указателя", "Скользящее окно"]
topic: algorithms
subtopics: [two-pointers, sliding-window, array, string]
question_kind: coding
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-algorithms
related: [c-two-pointers, c-sliding-window, q-sorting-algorithms-comparison--algorithms--medium]
created: 2025-10-12
updated: 2025-01-25
tags: [algorithms, two-pointers, sliding-window, array, optimization, difficulty/medium]
sources: [https://en.wikipedia.org/wiki/Two_pointer_technique]
---

# Вопрос (RU)
> Что такое техники двух указателей и скользящего окна? Когда их следует использовать? Каковы распространённые паттерны задач?

# Question (EN)
> What are Two Pointers and Sliding Window techniques? When should you use them? What are common problem patterns?

---

## Ответ (RU)

**Теория паттернов двух указателей и скользящего окна:**
Эти техники позволяют эффективно решать задачи с массивами и строками, часто сокращая сложность с O(n²) до O(n). Два указателя используют два индекса для обхода данных, а скользящее окно поддерживает динамический диапазон элементов.

**Два указателя - противоположные концы:**
```kotlin
// Два указателя начинаются с противоположных концов и движутся к центру
fun twoSum(numbers: IntArray, target: Int): IntArray {
    var left = 0
    var right = numbers.size - 1

    while (left < right) {
        val sum = numbers[left] + numbers[right]

        when {
            sum == target -> return intArrayOf(left + 1, right + 1)
            sum < target -> left++     // Нужна большая сумма
            else -> right--            // Нужна меньшая сумма
        }
    }

    return intArrayOf(-1, -1)
}
```

**Два указателя - одинаковое направление:**
```kotlin
// Два указателя движутся в одном направлении с разной скоростью
fun removeDuplicates(nums: IntArray): Int {
    if (nums.isEmpty()) return 0

    var slow = 0  // Позиция для следующего уникального элемента

    for (fast in 1 until nums.size) {
        if (nums[fast] != nums[slow]) {
            slow++
            nums[slow] = nums[fast]
        }
    }

    return slow + 1  // Длина уникальных элементов
}

// Обнаружение цикла в связанном списке (Floyd's Cycle Detection)
fun hasCycle(head: ListNode?): Boolean {
    var slow = head
    var fast = head

    while (fast?.next != null) {
        slow = slow?.next       // Движение на 1 шаг
        fast = fast.next?.next  // Движение на 2 шага

        if (slow == fast) return true  // Цикл обнаружен!
    }

    return false
}
```

**Скользящее окно - фиксированный размер:**
```kotlin
// Поддержание окна фиксированного размера
fun maxSumSubarray(arr: IntArray, k: Int): Int {
    var windowSum = 0
    var maxSum = 0

    // Начальное окно
    for (i in 0 until k) {
        windowSum += arr[i]
    }
    maxSum = windowSum

    // Скольжение окна
    for (i in k until arr.size) {
        windowSum += arr[i]        // Добавляем новый элемент
        windowSum -= arr[i - k]    // Удаляем старый элемент
        maxSum = maxOf(maxSum, windowSum)
    }

    return maxSum
}
```

**Скользящее окно - переменный размер:**
```kotlin
// Поддержание окна переменного размера с условием
fun lengthOfLongestSubstring(s: String): Int {
    val charSet = mutableSetOf<Char>()
    var left = 0
    var maxLength = 0

    for (right in s.indices) {
        // Сжимаем окно пока есть дубликаты
        while (s[right] in charSet) {
            charSet.remove(s[left])
            left++
        }

        charSet.add(s[right])
        maxLength = maxOf(maxLength, right - left + 1)
    }

    return maxLength
}

// Минимальное окно подстроки
fun minWindow(s: String, t: String): String {
    if (s.isEmpty() || t.isEmpty()) return ""

    val targetCount = mutableMapOf<Char, Int>()
    for (c in t) {
        targetCount[c] = targetCount.getOrDefault(c, 0) + 1
    }

    var left = 0
    var minLeft = 0
    var minLen = Int.MAX_VALUE
    var required = targetCount.size
    var formed = 0

    val windowCount = mutableMapOf<Char, Int>()

    for (right in s.indices) {
        val c = s[right]
        windowCount[c] = windowCount.getOrDefault(c, 0) + 1

        if (c in targetCount && windowCount[c] == targetCount[c]) {
            formed++
        }

        // Сжимаем окно
        while (formed == required && left <= right) {
            if (right - left + 1 < minLen) {
                minLen = right - left + 1
                minLeft = left
            }

            val leftChar = s[left]
            windowCount[leftChar] = windowCount[leftChar]!! - 1
            if (leftChar in targetCount &&
                windowCount[leftChar]!! < targetCount[leftChar]!!) {
                formed--
            }

            left++
        }
    }

    return if (minLen == Int.MAX_VALUE) "" else s.substring(minLeft, minLeft + minLen)
}
```

## Answer (EN)

**Two Pointers and Sliding Window Theory:**
These techniques efficiently solve array and string problems, often reducing complexity from O(n²) to O(n). Two pointers use two indices to traverse data, while sliding window maintains a dynamic range of elements.

**Two Pointers - Opposite Ends:**
```kotlin
// Two pointers start at opposite ends and move toward center
fun twoSum(numbers: IntArray, target: Int): IntArray {
    var left = 0
    var right = numbers.size - 1

    while (left < right) {
        val sum = numbers[left] + numbers[right]

        when {
            sum == target -> return intArrayOf(left + 1, right + 1)
            sum < target -> left++     // Need larger sum
            else -> right--            // Need smaller sum
        }
    }

    return intArrayOf(-1, -1)
}
```

**Two Pointers - Same Direction:**
```kotlin
// Two pointers move in same direction at different speeds
fun removeDuplicates(nums: IntArray): Int {
    if (nums.isEmpty()) return 0

    var slow = 0  // Position for next unique element

    for (fast in 1 until nums.size) {
        if (nums[fast] != nums[slow]) {
            slow++
            nums[slow] = nums[fast]
        }
    }

    return slow + 1  // Length of unique elements
}

// Linked list cycle detection (Floyd's Cycle Detection)
fun hasCycle(head: ListNode?): Boolean {
    var slow = head
    var fast = head

    while (fast?.next != null) {
        slow = slow?.next       // Move 1 step
        fast = fast.next?.next  // Move 2 steps

        if (slow == fast) return true  // Cycle detected!
    }

    return false
}
```

**Sliding Window - Fixed Size:**
```kotlin
// Maintain a window of fixed size
fun maxSumSubarray(arr: IntArray, k: Int): Int {
    var windowSum = 0
    var maxSum = 0

    // Initial window
    for (i in 0 until k) {
        windowSum += arr[i]
    }
    maxSum = windowSum

    // Slide window
    for (i in k until arr.size) {
        windowSum += arr[i]        // Add new element
        windowSum -= arr[i - k]    // Remove old element
        maxSum = maxOf(maxSum, windowSum)
    }

    return maxSum
}
```

**Sliding Window - Variable Size:**
```kotlin
// Maintain a window of variable size with condition
fun lengthOfLongestSubstring(s: String): Int {
    val charSet = mutableSetOf<Char>()
    var left = 0
    var maxLength = 0

    for (right in s.indices) {
        // Shrink window until no duplicates
        while (s[right] in charSet) {
            charSet.remove(s[left])
            left++
        }

        charSet.add(s[right])
        maxLength = maxOf(maxLength, right - left + 1)
    }

    return maxLength
}

// Minimum window substring
fun minWindow(s: String, t: String): String {
    if (s.isEmpty() || t.isEmpty()) return ""

    val targetCount = mutableMapOf<Char, Int>()
    for (c in t) {
        targetCount[c] = targetCount.getOrDefault(c, 0) + 1
    }

    var left = 0
    var minLeft = 0
    var minLen = Int.MAX_VALUE
    var required = targetCount.size
    var formed = 0

    val windowCount = mutableMapOf<Char, Int>()

    for (right in s.indices) {
        val c = s[right]
        windowCount[c] = windowCount.getOrDefault(c, 0) + 1

        if (c in targetCount && windowCount[c] == targetCount[c]) {
            formed++
        }

        // Shrink window
        while (formed == required && left <= right) {
            if (right - left + 1 < minLen) {
                minLen = right - left + 1
                minLeft = left
            }

            val leftChar = s[left]
            windowCount[leftChar] = windowCount[leftChar]!! - 1
            if (leftChar in targetCount &&
                windowCount[leftChar]!! < targetCount[leftChar]!!) {
                formed--
            }

            left++
        }
    }

    return if (minLen == Int.MAX_VALUE) "" else s.substring(minLeft, minLeft + minLen)
}
```

---

## Follow-ups

- How do you solve 3Sum problem with two pointers?
- What is the difference between fixed and variable sliding window?
- How do you find the smallest subarray with sum ≥ target?

## Related Questions

### Prerequisites (Easier)
- [[q-data-structures-overview--algorithms--easy]] - Data structures basics
- [[q-array-basics--algorithms--easy]] - Array fundamentals

### Related (Same Level)
- [[q-sorting-algorithms-comparison--algorithms--medium]] - Sorting algorithms
- [[q-binary-search-variants--algorithms--medium]] - Search algorithms

### Advanced (Harder)
- [[q-graph-algorithms-bfs-dfs--algorithms--hard]] - Graph algorithms
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - DP algorithms
