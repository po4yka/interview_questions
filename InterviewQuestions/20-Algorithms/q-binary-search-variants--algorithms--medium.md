---
id: 20251012-200002
title: "Binary Search and Variants / Бинарный поиск и варианты"
topic: algorithms
difficulty: medium
status: draft
created: 2025-10-12
tags: - algorithms
  - binary-search
  - searching
  - log-n
date_created: 2025-10-12
date_updated: 2025-10-12
moc: moc-algorithms
related_questions:   - q-sorting-algorithms-comparison--algorithms--medium
  - q-two-pointers-technique--algorithms--medium
slug: binary-search-variants-algorithms-medium
subtopics:   - binary-search
  - searching
  - divide-and-conquer
  - logarithmic
---
# Binary Search and Variants

## English Version

### Problem Statement

Binary search is one of the most important algorithms with O(log n) time complexity. Understanding binary search and its variants is crucial for solving many interview problems efficiently.

**The Question:** How does binary search work? What are common variants and edge cases?

### Detailed Answer

#### 1. Classic Binary Search

**Find target in sorted array.**

```kotlin
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

// Example:
val arr = intArrayOf(1, 3, 5, 7, 9, 11, 13)
println(binarySearch(arr, 7))   // 3
println(binarySearch(arr, 6))   // -1
```

**How it works:**
```
Array: [1, 3, 5, 7, 9, 11, 13]  Target: 7

Step 1: left=0, right=6, mid=3
        arr[3]=7 == target   Found!

Array: [1, 3, 5, 7, 9, 11, 13]  Target: 6

Step 1: left=0, right=6, mid=3
        arr[3]=7 > 6, search left
Step 2: left=0, right=2, mid=1
        arr[1]=3 < 6, search right
Step 3: left=2, right=2, mid=2
        arr[2]=5 < 6, search right
Step 4: left=3, right=2
        left > right, not found!
```

**Complexity:**
- **Time:** O(log n)
- **Space:** O(1)

---

#### 2. Find First Occurrence

**Find leftmost occurrence of target.**

```kotlin
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

// Example:
val arr = intArrayOf(1, 2, 2, 2, 3, 4, 5)
println(findFirst(arr, 2))  // 1 (first occurrence)
```

---

#### 3. Find Last Occurrence

**Find rightmost occurrence of target.**

```kotlin
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

// Example:
val arr = intArrayOf(1, 2, 2, 2, 3, 4, 5)
println(findLast(arr, 2))  // 3 (last occurrence)
```

---

#### 4. Find Insertion Position

**Find where to insert target to maintain sorted order.**

```kotlin
fun searchInsert(arr: IntArray, target: Int): Int {
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
    
    return left  // Insertion position
}

// Example:
val arr = intArrayOf(1, 3, 5, 6)
println(searchInsert(arr, 5))  // 2
println(searchInsert(arr, 2))  // 1
println(searchInsert(arr, 7))  // 4
```

---

#### 5. Search in Rotated Sorted Array

**Array rotated at pivot: [4,5,6,7,0,1,2]**

```kotlin
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

// Example:
val arr = intArrayOf(4, 5, 6, 7, 0, 1, 2)
println(searchRotated(arr, 0))  // 4
println(searchRotated(arr, 3))  // -1
```

---

#### 6. Find Peak Element

**Find any peak (element greater than neighbors).**

```kotlin
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

// Example:
val arr = intArrayOf(1, 2, 3, 1)
println(findPeakElement(arr))  // 2 (value 3 is peak)
```

---

#### 7. Square Root (Integer)

**Find floor(sqrt(x)) using binary search.**

```kotlin
fun mySqrt(x: Int): Int {
    if (x < 2) return x
    
    var left = 2
    var right = x / 2
    
    while (left <= right) {
        val mid = left + (right - left) / 2
        val squared = mid.toLong() * mid
        
        when {
            squared == x.toLong() -> return mid
            squared < x -> left = mid + 1
            else -> right = mid - 1
        }
    }
    
    return right
}

// Example:
println(mySqrt(8))   // 2
println(mySqrt(16))  // 4
```

---

#### 8. Search in 2D Matrix

**Matrix: rows and columns sorted.**

```kotlin
fun searchMatrix(matrix: Array<IntArray>, target: Int): Boolean {
    if (matrix.isEmpty() || matrix[0].isEmpty()) return false
    
    val m = matrix.size
    val n = matrix[0].size
    var left = 0
    var right = m * n - 1
    
    while (left <= right) {
        val mid = left + (right - left) / 2
        val row = mid / n
        val col = mid % n
        val value = matrix[row][col]
        
        when {
            value == target -> return true
            value < target -> left = mid + 1
            else -> right = mid - 1
        }
    }
    
    return false
}

// Example:
val matrix = arrayOf(
    intArrayOf(1, 3, 5, 7),
    intArrayOf(10, 11, 16, 20),
    intArrayOf(23, 30, 34, 60)
)
println(searchMatrix(matrix, 3))   // true
println(searchMatrix(matrix, 13))  // false
```

---

#### 9. Find Minimum in Rotated Sorted Array

```kotlin
fun findMin(nums: IntArray): Int {
    var left = 0
    var right = nums.size - 1
    
    while (left < right) {
        val mid = left + (right - left) / 2
        
        if (nums[mid] > nums[right]) {
            // Minimum is in right half
            left = mid + 1
        } else {
            // Minimum is in left half or at mid
            right = mid
        }
    }
    
    return nums[left]
}

// Example:
val arr = intArrayOf(4, 5, 6, 7, 0, 1, 2)
println(findMin(arr))  // 0
```

---

#### 10. Koko Eating Bananas (Binary Search on Answer)

**Find minimum eating speed to finish all bananas in h hours.**

```kotlin
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

// Example:
val piles = intArrayOf(3, 6, 7, 11)
val h = 8
println(minEatingSpeed(piles, h))  // 4
```

---

### Common Binary Search Patterns

#### Pattern 1: Exact Match
```kotlin
while (left <= right) {
    // ... find exact target
}
return -1  // Not found
```

#### Pattern 2: Find Boundary (First/Last occurrence)
```kotlin
while (left <= right) {
    if (condition) {
        result = mid
        // Keep searching (left or right)
    }
}
return result
```

#### Pattern 3: Minimize/Maximize
```kotlin
while (left < right) {
    if (canAchieve(mid)) {
        right = mid  // Try smaller
    } else {
        left = mid + 1  // Need larger
    }
}
return left
```

---

### Edge Cases to Consider

```kotlin
// 1. Empty array
if (arr.isEmpty()) return -1

// 2. Single element
if (arr.size == 1) return if (arr[0] == target) 0 else -1

// 3. Overflow in mid calculation
//  Bad: val mid = (left + right) / 2  // Overflow possible
//  Good: val mid = left + (right - left) / 2

// 4. Off-by-one errors
// Use left <= right (not left < right) for exact match
// Use left < right for boundary problems

// 5. Integer overflow in calculations
val squared = mid.toLong() * mid  // Use Long for intermediate
```

---

### Real-World Android Example

```kotlin
// Find user in sorted list
data class User(val id: Int, val name: String)

fun findUserById(users: List<User>, targetId: Int): User? {
    var left = 0
    var right = users.size - 1
    
    while (left <= right) {
        val mid = left + (right - left) / 2
        
        when {
            users[mid].id == targetId -> return users[mid]
            users[mid].id < targetId -> left = mid + 1
            else -> right = mid - 1
        }
    }
    
    return null
}

// Usage
val users = listOf(
    User(1, "Alice"),
    User(3, "Bob"),
    User(5, "Charlie"),
    User(7, "Dave")
)
val found = findUserById(users, 5)  // User(5, "Charlie")
```

---

### Key Takeaways

1. **Binary search** requires **sorted** array
2. **Time:** O(log n) - extremely fast
3. **Mid calculation:** `left + (right - left) / 2` to avoid overflow
4. **While condition:** `left <= right` for exact match, `left < right` for boundaries
5. **Find first:** Keep searching left after finding
6. **Find last:** Keep searching right after finding
7. **Rotated array:** Determine which half is sorted
8. **Binary search on answer:** Apply to optimization problems
9. **Edge cases:** Empty array, single element, overflow
10. **Applications:** Searching, finding boundaries, optimization

---

## Russian Version

### Постановка задачи

Бинарный поиск - один из важнейших алгоритмов со сложностью O(log n). Понимание бинарного поиска и его вариантов критично для эффективного решения многих задач на интервью.

**Вопрос:** Как работает бинарный поиск? Каковы распространённые варианты и граничные случаи?

### Детальный ответ

#### Классический бинарный поиск

**Найти target в отсортированном массиве.**

**Сложность:**
- **Время:** O(log n)
- **Память:** O(1)

### Ключевые выводы

1. **Бинарный поиск** требует **отсортированный** массив
2. **Время:** O(log n) - чрезвычайно быстро
3. **Вычисление mid:** `left + (right - left) / 2` для избежания overflow
4. **Условие while:** `left <= right` для точного совпадения
5. **Найти первый:** Продолжать искать влево после нахождения
6. **Найти последний:** Продолжать искать вправо после нахождения
7. **Повёрнутый массив:** Определить какая половина отсортирована
8. **Бинарный поиск по ответу:** Применить к задачам оптимизации
9. **Граничные случаи:** Пустой массив, один элемент, overflow

## Follow-ups

1. How do you implement binary search recursively?
2. What is exponential search and when is it useful?
3. How do you find the square root with decimal precision?
4. What is ternary search and when is it better than binary?
5. How do you search in a matrix with sorted rows and columns?
6. What is the difference between lower_bound and upper_bound?
7. How do you find the median of two sorted arrays?
8. How do you implement binary search on a linked list?
9. What is interpolation search and its complexity?
10. How do you find the kth smallest element in sorted matrix?

---

## Related Questions

### Advanced (Harder)
- [[q-binary-search-trees-bst--algorithms--hard]] - binary search trees bst 
### Advanced (Harder)
- [[q-binary-search-trees-bst--algorithms--hard]] - binary search trees bst 
### Advanced (Harder)
- [[q-binary-search-trees-bst--algorithms--hard]] - binary search trees bst 
