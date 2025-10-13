---
id: 20251012-200006
title: "Two Pointers and Sliding Window Patterns / Паттерны двух указателей и скользящего окна"
slug: two-pointers-sliding-window-algorithms-medium
topic: algorithms
subtopics:
  - two-pointers
  - sliding-window
  - array
  - string
  - optimization
status: draft
difficulty: medium
moc: moc-algorithms
date_created: 2025-10-12
date_updated: 2025-10-12
related_questions:
  - q-binary-search-variants--algorithms--medium
  - q-sorting-algorithms-comparison--algorithms--medium
tags:
  - algorithms
  - two-pointers
  - sliding-window
  - array
  - optimization
---

# Two Pointers and Sliding Window Patterns

## English Version

### Problem Statement

Two Pointers and Sliding Window are powerful techniques for solving array and string problems efficiently. These patterns can often reduce time complexity from O(n²) to O(n).

**The Question:** What are Two Pointers and Sliding Window techniques? When should you use them? What are common problem patterns?

### Detailed Answer

---

### TWO POINTERS TECHNIQUE

#### Pattern 1: Opposite Ends

**Two pointers start at opposite ends, move toward center.**

**Problem: Two Sum II (Sorted Array)**
```kotlin
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

// Example:
val nums = intArrayOf(2, 7, 11, 15)
println(twoSum(nums, 9).contentToString())  // [1, 2]

// Time: O(n)
// Space: O(1)
```

**How it works:**
```
Array: [2, 7, 11, 15]  Target: 9
        ↑          ↑
        L          R

Step 1: 2 + 15 = 17 > 9  → R--
Step 2: 2 + 11 = 13 > 9  → R--
Step 3: 2 + 7 = 9       → Found!
```

---

**Problem: Container With Most Water**
```kotlin
fun maxArea(height: IntArray): Int {
    var left = 0
    var right = height.size - 1
    var maxArea = 0
    
    while (left < right) {
        val width = right - left
        val minHeight = minOf(height[left], height[right])
        val area = width * minHeight
        
        maxArea = maxOf(maxArea, area)
        
        // Move pointer with smaller height
        if (height[left] < height[right]) {
            left++
        } else {
            right--
        }
    }
    
    return maxArea
}

// Example:
val heights = intArrayOf(1, 8, 6, 2, 5, 4, 8, 3, 7)
println(maxArea(heights))  // 49

// Time: O(n)
// Space: O(1)
```

---

**Problem: Valid Palindrome**
```kotlin
fun isPalindrome(s: String): Boolean {
    var left = 0
    var right = s.length - 1
    
    while (left < right) {
        // Skip non-alphanumeric
        while (left < right && !s[left].isLetterOrDigit()) left++
        while (left < right && !s[right].isLetterOrDigit()) right--
        
        if (s[left].lowercaseChar() != s[right].lowercaseChar()) {
            return false
        }
        
        left++
        right--
    }
    
    return true
}

// Example:
println(isPalindrome("A man, a plan, a canal: Panama"))  // true
```

---

#### Pattern 2: Same Direction (Fast & Slow)

**Two pointers move in same direction at different speeds.**

**Problem: Remove Duplicates from Sorted Array**
```kotlin
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

// Example:
val nums = intArrayOf(1, 1, 2, 2, 3, 4, 4)
val len = removeDuplicates(nums)
println(nums.take(len))  // [1, 2, 3, 4]

// Time: O(n)
// Space: O(1)
```

**How it works:**
```
[1, 1, 2, 2, 3, 4, 4]
 ↑  ↑
 S  F

Step 1: nums[F]=1 == nums[S]=1 → F++
Step 2: nums[F]=2 != nums[S]=1 → S++, nums[S]=2, F++
Step 3: nums[F]=2 == nums[S]=2 → F++
...

Result: [1, 2, 3, 4, ...]
            ↑
            S
```

---

**Problem: Move Zeroes**
```kotlin
fun moveZeroes(nums: IntArray) {
    var slow = 0  // Position for next non-zero
    
    for (fast in nums.indices) {
        if (nums[fast] != 0) {
            nums[slow] = nums[fast]
            slow++
        }
    }
    
    // Fill remaining with zeroes
    for (i in slow until nums.size) {
        nums[i] = 0
    }
}

// Example:
val nums = intArrayOf(0, 1, 0, 3, 12)
moveZeroes(nums)
println(nums.contentToString())  // [1, 3, 12, 0, 0]
```

---

**Problem: Linked List Cycle (Floyd's Cycle Detection)**
```kotlin
class ListNode(var `val`: Int) {
    var next: ListNode? = null
}

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

// If there's a cycle, fast will eventually catch up to slow
// Time: O(n)
// Space: O(1)
```

---

### SLIDING WINDOW TECHNIQUE

**Maintain a window of elements, slide it to find solution.**

#### Fixed-Size Window

**Problem: Maximum Sum Subarray of Size K**
```kotlin
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

// Example:
val arr = intArrayOf(2, 1, 5, 1, 3, 2)
println(maxSumSubarray(arr, 3))  // 9 (5+1+3)

// Time: O(n)
// Space: O(1)
```

**How it works:**
```
Array: [2, 1, 5, 1, 3, 2]  k=3

Window 1: [2, 1, 5] → sum = 8
Window 2:    [1, 5, 1] → sum = 7  (add 1, remove 2)
Window 3:       [5, 1, 3] → sum = 9  (add 3, remove 1)
Window 4:          [1, 3, 2] → sum = 6  (add 2, remove 5)

Max = 9
```

---

#### Variable-Size Window

**Problem: Longest Substring Without Repeating Characters**
```kotlin
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

// Example:
println(lengthOfLongestSubstring("abcabcbb"))  // 3 ("abc")
println(lengthOfLongestSubstring("bbbbb"))     // 1 ("b")
println(lengthOfLongestSubstring("pwwkew"))    // 3 ("wke")

// Time: O(n)
// Space: O(min(n, m)) where m = charset size
```

**How it works:**
```
String: "abcabcbb"

Window: "a"     → length = 1
Window: "ab"    → length = 2
Window: "abc"   → length = 3 
Window: "abca"  → Duplicate 'a'! Shrink: "bca"
Window: "bcab"  → Duplicate 'b'! Shrink: "cab"
...
```

---

**Problem: Minimum Window Substring**
```kotlin
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
            // Update result
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

// Example:
println(minWindow("ADOBECODEBANC", "ABC"))  // "BANC"
```

---

**Problem: Longest Subarray with Sum ≤ K**
```kotlin
fun longestSubarrayWithSumK(arr: IntArray, k: Int): Int {
    var left = 0
    var sum = 0
    var maxLength = 0
    
    for (right in arr.indices) {
        sum += arr[right]
        
        // Shrink window while sum > k
        while (sum > k && left <= right) {
            sum -= arr[left]
            left++
        }
        
        maxLength = maxOf(maxLength, right - left + 1)
    }
    
    return maxLength
}

// Example:
val arr = intArrayOf(1, 2, 3, 4, 5)
println(longestSubarrayWithSumK(arr, 8))  // 3 ([1,2,3] or [3,4] but we want longest)
```

---

**Problem: Fruits Into Baskets (Max 2 Types)**
```kotlin
fun totalFruit(fruits: IntArray): Int {
    val basket = mutableMapOf<Int, Int>()
    var left = 0
    var maxFruits = 0
    
    for (right in fruits.indices) {
        val fruit = fruits[right]
        basket[fruit] = basket.getOrDefault(fruit, 0) + 1
        
        // Shrink window if more than 2 types
        while (basket.size > 2) {
            val leftFruit = fruits[left]
            basket[leftFruit] = basket[leftFruit]!! - 1
            if (basket[leftFruit] == 0) {
                basket.remove(leftFruit)
            }
            left++
        }
        
        maxFruits = maxOf(maxFruits, right - left + 1)
    }
    
    return maxFruits
}

// Example:
val fruits = intArrayOf(1, 2, 1, 2, 3, 2, 2)
println(totalFruit(fruits))  // 5 ([2,3,2,2] or [1,2,1,2])
```

---

### Pattern Recognition

**Use Two Pointers when:**
-  Array/string is sorted
-  Need to find pair with target sum
-  Removing duplicates in-place
-  Reversing/palindrome checking
-  Cycle detection

**Use Sliding Window when:**
-  Finding substring/subarray with condition
-  "Longest/Shortest/Maximum" subarray problems
-  "Contains all of" problems
-  Fixed or variable window size
-  Consecutive elements matter

---

### Time Complexity Comparison

```kotlin
// Brute force: Check all subarrays of size k
fun maxSumBruteForce(arr: IntArray, k: Int): Int {
    var maxSum = 0
    
    for (i in 0..arr.size - k) {
        var sum = 0
        for (j in i until i + k) {
            sum += arr[j]
        }
        maxSum = maxOf(maxSum, sum)
    }
    
    return maxSum
}
// Time: O(n*k) 

// Sliding window
fun maxSumOptimized(arr: IntArray, k: Int): Int {
    var windowSum = arr.take(k).sum()
    var maxSum = windowSum
    
    for (i in k until arr.size) {
        windowSum += arr[i] - arr[i - k]
        maxSum = maxOf(maxSum, windowSum)
    }
    
    return maxSum
}
// Time: O(n) 
```

---

### Real-World Android Example

```kotlin
// Network request rate limiting (Sliding Window)
class RateLimiter(
    private val maxRequests: Int,
    private val windowMs: Long
) {
    private val timestamps = LinkedList<Long>()
    
    fun allowRequest(): Boolean {
        val now = System.currentTimeMillis()
        
        // Remove old timestamps outside window
        while (timestamps.isNotEmpty() && 
               now - timestamps.first() > windowMs) {
            timestamps.removeFirst()
        }
        
        return if (timestamps.size < maxRequests) {
            timestamps.addLast(now)
            true
        } else {
            false
        }
    }
}

// Usage: Max 10 requests per second
val limiter = RateLimiter(maxRequests = 10, windowMs = 1000)

fun makeRequest() {
    if (limiter.allowRequest()) {
        // Make API call
    } else {
        // Rate limited - wait
    }
}
```

---

### Key Takeaways

1. **Two Pointers** reduces O(n²) to O(n) for many problems
2. **Opposite ends** pattern for sorted arrays (Two Sum, Palindrome)
3. **Same direction** pattern for in-place modifications (Remove Duplicates)
4. **Fast & Slow** pointers for cycle detection
5. **Sliding Window** for substring/subarray problems
6. **Fixed window** for "size k" problems
7. **Variable window** for "longest/shortest" problems
8. **Expand window** until condition violated
9. **Shrink window** to restore condition
10. **Both patterns:** O(n) time, O(1) space typically

---

## Russian Version

### Постановка задачи

Два указателя и скользящее окно - мощные техники для эффективного решения задач с массивами и строками. Эти паттерны часто могут сократить временную сложность с O(n²) до O(n).

**Вопрос:** Что такое техники двух указателей и скользящего окна? Когда их следует использовать? Каковы распространённые паттерны задач?

### Ключевые выводы

1. **Два указателя** сокращают O(n²) до O(n) для многих задач
2. **Opposite ends** паттерн для отсортированных массивов
3. **Same direction** паттерн для in-place модификаций
4. **Fast & Slow** указатели для обнаружения циклов
5. **Скользящее окно** для задач подстрок/подмассивов
6. **Фиксированное окно** для задач "размер k"
7. **Переменное окно** для задач "самый длинный/короткий"
8. **Расширять окно** пока условие не нарушено
9. **Сжимать окно** чтобы восстановить условие
10. **Оба паттерна:** O(n) время, O(1) память обычно

## Follow-ups

1. How do you solve 3Sum problem with two pointers?
2. What is the difference between fixed and variable sliding window?
3. How do you find the smallest subarray with sum ≥ target?
4. What is the maximum number of vowels in substring of length k?
5. How do you detect the start of a cycle in linked list?
6. What is the longest substring with at most k distinct characters?
7. How do you implement a deque for sliding window maximum?
8. What is the trapping rain water problem solution?
9. How do you find all anagrams in a string?
10. What is the maximum consecutive ones with at most k flips?
