---
id: algo-018
title: Prefix Sum and Range Queries / Префиксные суммы и диапазонные запросы
aliases:
- Prefix Sum
- Cumulative Sum
- Range Queries
- Префиксные суммы
- Кумулятивные суммы
- Диапазонные запросы
topic: algorithms
subtopics:
- prefix-sum
- range-query
- subarray
question_kind: coding
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-algorithms
related:
- c-prefix-sum
- c-range-query
- q-hash-table-applications--algorithms--easy
created: 2026-01-23
updated: 2026-01-23
tags:
- algorithms
- prefix-sum
- difficulty/medium
- range-query
- subarray
sources:
- https://en.wikipedia.org/wiki/Prefix_sum
anki_cards:
- slug: algo-018-0-en
  language: en
  anki_id: 1769168918176
  synced_at: '2026-01-23T15:48:41.071054'
- slug: algo-018-0-ru
  language: ru
  anki_id: 1769168918196
  synced_at: '2026-01-23T15:48:41.074465'
---
# Вопрос (RU)
> Что такое префиксные суммы? Как использовать их для эффективных диапазонных запросов? Объясни задачу "Subarray Sum Equals K".

# Question (EN)
> What are prefix sums? How do you use them for efficient range queries? Explain the "Subarray Sum Equals K" problem.

---

## Ответ (RU)

**Теория префиксных сумм:**
Префиксная сумма - массив, где prefix[i] = sum(arr[0..i-1]). Позволяет вычислить сумму любого диапазона за O(1) после O(n) предобработки.

**Базовая идея:**
```kotlin
// Построение префиксной суммы
fun buildPrefixSum(nums: IntArray): IntArray {
    val n = nums.size
    val prefix = IntArray(n + 1)  // prefix[0] = 0

    for (i in nums.indices) {
        prefix[i + 1] = prefix[i] + nums[i]
    }

    return prefix
}

// Сумма диапазона [left, right]
fun rangeSum(prefix: IntArray, left: Int, right: Int): Int {
    return prefix[right + 1] - prefix[left]
}

// Пример: nums = [1, 2, 3, 4, 5]
// prefix = [0, 1, 3, 6, 10, 15]
// sum(1, 3) = prefix[4] - prefix[1] = 10 - 1 = 9 (2 + 3 + 4)
```

**Subarray Sum Equals K:**
```kotlin
// Количество подмассивов с суммой k
fun subarraySum(nums: IntArray, k: Int): Int {
    // Хранит count префиксных сумм
    val prefixCount = mutableMapOf<Int, Int>()
    prefixCount[0] = 1  // Пустой префикс

    var sum = 0
    var count = 0

    for (num in nums) {
        sum += num

        // Если существует prefix = sum - k,
        // то подмассив [prefix+1, current] имеет сумму k
        if ((sum - k) in prefixCount) {
            count += prefixCount[sum - k]!!
        }

        prefixCount[sum] = prefixCount.getOrDefault(sum, 0) + 1
    }

    return count
}

// Пример: nums = [1, 1, 1], k = 2
// i=0: sum=1, 1-2=-1 not in map, map={0:1, 1:1}
// i=1: sum=2, 2-2=0 in map! count=1, map={0:1, 1:1, 2:1}
// i=2: sum=3, 3-2=1 in map! count=2, map={0:1, 1:1, 2:1, 3:1}
// Результат: 2 (подмассивы [0,1] и [1,2])
```

**Maximum Subarray (Kadane's Algorithm):**
```kotlin
fun maxSubArray(nums: IntArray): Int {
    var maxSum = nums[0]
    var currentSum = nums[0]

    for (i in 1 until nums.size) {
        // Либо начинаем новый подмассив, либо продолжаем текущий
        currentSum = maxOf(nums[i], currentSum + nums[i])
        maxSum = maxOf(maxSum, currentSum)
    }

    return maxSum
}
```

**Product of Array Except Self:**
```kotlin
fun productExceptSelf(nums: IntArray): IntArray {
    val n = nums.size
    val result = IntArray(n)

    // Левые произведения
    var leftProduct = 1
    for (i in nums.indices) {
        result[i] = leftProduct
        leftProduct *= nums[i]
    }

    // Правые произведения
    var rightProduct = 1
    for (i in n - 1 downTo 0) {
        result[i] *= rightProduct
        rightProduct *= nums[i]
    }

    return result
}

// nums = [1, 2, 3, 4]
// Левые: [1, 1, 2, 6]
// Правые: [24, 12, 4, 1]
// Результат: [24, 12, 8, 6]
```

**2D Prefix Sum:**
```kotlin
class NumMatrix(matrix: Array<IntArray>) {
    private val prefix: Array<IntArray>

    init {
        val m = matrix.size
        val n = if (m > 0) matrix[0].size else 0
        prefix = Array(m + 1) { IntArray(n + 1) }

        for (i in 0 until m) {
            for (j in 0 until n) {
                prefix[i + 1][j + 1] = matrix[i][j] +
                    prefix[i][j + 1] + prefix[i + 1][j] - prefix[i][j]
            }
        }
    }

    // Сумма прямоугольника от (r1, c1) до (r2, c2)
    fun sumRegion(r1: Int, c1: Int, r2: Int, c2: Int): Int {
        return prefix[r2 + 1][c2 + 1] - prefix[r1][c2 + 1] -
               prefix[r2 + 1][c1] + prefix[r1][c1]
    }
}
```

**Continuous Subarray Sum (сумма кратна k):**
```kotlin
fun checkSubarraySum(nums: IntArray, k: Int): Boolean {
    // Хранит первый индекс для каждого остатка
    val remainderIndex = mutableMapOf<Int, Int>()
    remainderIndex[0] = -1  // Для случая, когда весь подмассив от 0

    var sum = 0

    for (i in nums.indices) {
        sum += nums[i]
        val remainder = if (k != 0) sum % k else sum

        if (remainder in remainderIndex) {
            // Подмассив длиной >= 2
            if (i - remainderIndex[remainder]!! >= 2) {
                return true
            }
        } else {
            remainderIndex[remainder] = i
        }
    }

    return false
}
```

**Minimum Size Subarray Sum:**
```kotlin
// Минимальная длина подмассива с суммой >= target
fun minSubArrayLen(target: Int, nums: IntArray): Int {
    var minLen = Int.MAX_VALUE
    var sum = 0
    var left = 0

    for (right in nums.indices) {
        sum += nums[right]

        while (sum >= target) {
            minLen = minOf(minLen, right - left + 1)
            sum -= nums[left]
            left++
        }
    }

    return if (minLen == Int.MAX_VALUE) 0 else minLen
}
```

**Range Sum Query - Mutable (с Fenwick Tree):**
```kotlin
class NumArray(nums: IntArray) {
    private val n = nums.size
    private val arr = nums.copyOf()
    private val tree = IntArray(n + 1)

    init {
        for (i in nums.indices) {
            updateTree(i, nums[i])
        }
    }

    private fun updateTree(i: Int, delta: Int) {
        var idx = i + 1
        while (idx <= n) {
            tree[idx] += delta
            idx += idx and (-idx)  // Добавляем наименьший бит
        }
    }

    fun update(index: Int, `val`: Int) {
        val delta = `val` - arr[index]
        arr[index] = `val`
        updateTree(index, delta)
    }

    fun sumRange(left: Int, right: Int): Int {
        return prefixSum(right) - prefixSum(left - 1)
    }

    private fun prefixSum(i: Int): Int {
        var sum = 0
        var idx = i + 1
        while (idx > 0) {
            sum += tree[idx]
            idx -= idx and (-idx)  // Убираем наименьший бит
        }
        return sum
    }
}
```

## Answer (EN)

**Prefix Sum Theory:**
A prefix sum is an array where prefix[i] = sum(arr[0..i-1]). Allows computing any range sum in O(1) after O(n) preprocessing.

**Basic Idea:**
```kotlin
// Build prefix sum
fun buildPrefixSum(nums: IntArray): IntArray {
    val n = nums.size
    val prefix = IntArray(n + 1)  // prefix[0] = 0

    for (i in nums.indices) {
        prefix[i + 1] = prefix[i] + nums[i]
    }

    return prefix
}

// Range sum [left, right]
fun rangeSum(prefix: IntArray, left: Int, right: Int): Int {
    return prefix[right + 1] - prefix[left]
}

// Example: nums = [1, 2, 3, 4, 5]
// prefix = [0, 1, 3, 6, 10, 15]
// sum(1, 3) = prefix[4] - prefix[1] = 10 - 1 = 9 (2 + 3 + 4)
```

**Subarray Sum Equals K:**
```kotlin
// Count subarrays with sum k
fun subarraySum(nums: IntArray, k: Int): Int {
    // Store count of prefix sums
    val prefixCount = mutableMapOf<Int, Int>()
    prefixCount[0] = 1  // Empty prefix

    var sum = 0
    var count = 0

    for (num in nums) {
        sum += num

        // If prefix = sum - k exists,
        // then subarray [prefix+1, current] has sum k
        if ((sum - k) in prefixCount) {
            count += prefixCount[sum - k]!!
        }

        prefixCount[sum] = prefixCount.getOrDefault(sum, 0) + 1
    }

    return count
}

// Example: nums = [1, 1, 1], k = 2
// i=0: sum=1, 1-2=-1 not in map, map={0:1, 1:1}
// i=1: sum=2, 2-2=0 in map! count=1, map={0:1, 1:1, 2:1}
// i=2: sum=3, 3-2=1 in map! count=2, map={0:1, 1:1, 2:1, 3:1}
// Result: 2 (subarrays [0,1] and [1,2])
```

**Maximum Subarray (Kadane's Algorithm):**
```kotlin
fun maxSubArray(nums: IntArray): Int {
    var maxSum = nums[0]
    var currentSum = nums[0]

    for (i in 1 until nums.size) {
        // Either start new subarray or continue current
        currentSum = maxOf(nums[i], currentSum + nums[i])
        maxSum = maxOf(maxSum, currentSum)
    }

    return maxSum
}
```

**Product of Array Except Self:**
```kotlin
fun productExceptSelf(nums: IntArray): IntArray {
    val n = nums.size
    val result = IntArray(n)

    // Left products
    var leftProduct = 1
    for (i in nums.indices) {
        result[i] = leftProduct
        leftProduct *= nums[i]
    }

    // Right products
    var rightProduct = 1
    for (i in n - 1 downTo 0) {
        result[i] *= rightProduct
        rightProduct *= nums[i]
    }

    return result
}

// nums = [1, 2, 3, 4]
// Left: [1, 1, 2, 6]
// Right: [24, 12, 4, 1]
// Result: [24, 12, 8, 6]
```

**2D Prefix Sum:**
```kotlin
class NumMatrix(matrix: Array<IntArray>) {
    private val prefix: Array<IntArray>

    init {
        val m = matrix.size
        val n = if (m > 0) matrix[0].size else 0
        prefix = Array(m + 1) { IntArray(n + 1) }

        for (i in 0 until m) {
            for (j in 0 until n) {
                prefix[i + 1][j + 1] = matrix[i][j] +
                    prefix[i][j + 1] + prefix[i + 1][j] - prefix[i][j]
            }
        }
    }

    // Sum of rectangle from (r1, c1) to (r2, c2)
    fun sumRegion(r1: Int, c1: Int, r2: Int, c2: Int): Int {
        return prefix[r2 + 1][c2 + 1] - prefix[r1][c2 + 1] -
               prefix[r2 + 1][c1] + prefix[r1][c1]
    }
}
```

**Continuous Subarray Sum (sum divisible by k):**
```kotlin
fun checkSubarraySum(nums: IntArray, k: Int): Boolean {
    // Store first index for each remainder
    val remainderIndex = mutableMapOf<Int, Int>()
    remainderIndex[0] = -1  // For case when entire subarray from 0

    var sum = 0

    for (i in nums.indices) {
        sum += nums[i]
        val remainder = if (k != 0) sum % k else sum

        if (remainder in remainderIndex) {
            // Subarray length >= 2
            if (i - remainderIndex[remainder]!! >= 2) {
                return true
            }
        } else {
            remainderIndex[remainder] = i
        }
    }

    return false
}
```

**Minimum Size Subarray Sum:**
```kotlin
// Minimum length subarray with sum >= target
fun minSubArrayLen(target: Int, nums: IntArray): Int {
    var minLen = Int.MAX_VALUE
    var sum = 0
    var left = 0

    for (right in nums.indices) {
        sum += nums[right]

        while (sum >= target) {
            minLen = minOf(minLen, right - left + 1)
            sum -= nums[left]
            left++
        }
    }

    return if (minLen == Int.MAX_VALUE) 0 else minLen
}
```

**Range Sum Query - Mutable (with Fenwick Tree):**
```kotlin
class NumArray(nums: IntArray) {
    private val n = nums.size
    private val arr = nums.copyOf()
    private val tree = IntArray(n + 1)

    init {
        for (i in nums.indices) {
            updateTree(i, nums[i])
        }
    }

    private fun updateTree(i: Int, delta: Int) {
        var idx = i + 1
        while (idx <= n) {
            tree[idx] += delta
            idx += idx and (-idx)  // Add lowest bit
        }
    }

    fun update(index: Int, `val`: Int) {
        val delta = `val` - arr[index]
        arr[index] = `val`
        updateTree(index, delta)
    }

    fun sumRange(left: Int, right: Int): Int {
        return prefixSum(right) - prefixSum(left - 1)
    }

    private fun prefixSum(i: Int): Int {
        var sum = 0
        var idx = i + 1
        while (idx > 0) {
            sum += tree[idx]
            idx -= idx and (-idx)  // Remove lowest bit
        }
        return sum
    }
}
```

---

## Follow-ups

- How do you handle negative numbers in prefix sum problems?
- What is the difference between Fenwick Tree and Segment Tree?
- How would you find the subarray with maximum sum in a circular array?

## Related Questions

### Prerequisites (Easier)
- [[q-hash-table-applications--algorithms--easy]] - Hash table patterns
- [[q-data-structures-overview--algorithms--easy]] - Data structures

### Related (Same Level)
- [[q-two-pointers-sliding-window--algorithms--medium]] - Sliding window
- [[q-matrix-grid-problems--algorithms--medium]] - 2D arrays

### Advanced (Harder)
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - DP
- [[q-binary-search-variants--algorithms--medium]] - Binary search
