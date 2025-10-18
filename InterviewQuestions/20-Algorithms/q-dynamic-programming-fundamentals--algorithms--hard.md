---
id: 20251012-200003
title: "Dynamic Programming Fundamentals / Основы динамического программирования"
topic: algorithms
difficulty: hard
status: draft
created: 2025-10-12
tags:
  - algorithms
  - dynamic-programming
  - dp
  - optimization
  - memoization
moc: moc-algorithms
related: [q-two-pointers-sliding-window--algorithms--medium, q-backtracking-algorithms--algorithms--hard, q-sorting-algorithms-comparison--algorithms--medium]
  - q-recursion-vs-iteration--algorithms--medium
  - q-backtracking-algorithms--algorithms--hard
subtopics:
  - dynamic-programming
  - dp
  - memoization
  - tabulation
  - optimization
---
# Question (EN)
> What is Dynamic Programming? How does it differ from recursion? What are the main DP patterns and classic problems?

# Вопрос (RU)
> Что такое динамическое программирование? Чем оно отличается от рекурсии? Каковы основные паттерны DP и классические задачи?

---

## Answer (EN)

Dynamic Programming (DP) is a powerful technique for solving optimization problems by breaking them into overlapping subproblems. Understanding DP is crucial for technical interviews and real-world optimization challenges.



### What is Dynamic Programming?

**Dynamic Programming** = Optimization technique that solves problems by:
1. Breaking into **overlapping subproblems**
2. Solving each subproblem **once**
3. **Storing results** (memoization/tabulation)
4. Reusing stored results

**Key Properties:**
-  **Optimal Substructure** - optimal solution contains optimal solutions to subproblems
-  **Overlapping Subproblems** - same subproblems solved multiple times

---

### 1. Fibonacci - Classic Example

**Problem:** Find nth Fibonacci number
```
F(0) = 0
F(1) = 1
F(n) = F(n-1) + F(n-2)
```

### Naive Recursion (Exponential - O(2^n))

```kotlin
fun fibRecursive(n: Int): Long {
    if (n <= 1) return n.toLong()
    return fibRecursive(n - 1) + fibRecursive(n - 2)
}

// Time: O(2^n) - exponential!
// Space: O(n) - recursion stack

// Example:
println(fibRecursive(5))  // 5
println(fibRecursive(40)) // Takes forever!
```

**Why so slow?**
```
fib(5)
 fib(4)
   fib(3)
     fib(2)
       fib(1)
       fib(0)
     fib(1)
   fib(2)  ← Recalculated!
      fib(1)
      fib(0)
 fib(3)  ← Recalculated!
    fib(2)
      fib(1)
      fib(0)
    fib(1)

fib(2) calculated 3 times!
fib(3) calculated 2 times!
```

### Top-Down DP: Memoization (O(n))

```kotlin
fun fibMemo(n: Int, memo: MutableMap<Int, Long> = mutableMapOf()): Long {
    if (n <= 1) return n.toLong()
    
    // Check if already calculated
    if (n in memo) return memo[n]!!
    
    // Calculate and store
    val result = fibMemo(n - 1, memo) + fibMemo(n - 2, memo)
    memo[n] = result
    
    return result
}

// Time: O(n) - each subproblem solved once
// Space: O(n) - memo + recursion stack

// Example:
println(fibMemo(40))  // Instant!
println(fibMemo(100)) // Still fast!
```

### Bottom-Up DP: Tabulation (O(n))

```kotlin
fun fibTabulation(n: Int): Long {
    if (n <= 1) return n.toLong()
    
    val dp = LongArray(n + 1)
    dp[0] = 0
    dp[1] = 1
    
    for (i in 2..n) {
        dp[i] = dp[i - 1] + dp[i - 2]
    }
    
    return dp[n]
}

// Time: O(n)
// Space: O(n)

// Example:
println(fibTabulation(100))
```

### Space-Optimized (O(1))

```kotlin
fun fibOptimized(n: Int): Long {
    if (n <= 1) return n.toLong()
    
    var prev2 = 0L
    var prev1 = 1L
    
    for (i in 2..n) {
        val curr = prev1 + prev2
        prev2 = prev1
        prev1 = curr
    }
    
    return prev1
}

// Time: O(n)
// Space: O(1) - only 2 variables!
```

---

### 2. Climbing Stairs

**Problem:** You can climb 1 or 2 steps. How many ways to reach step n?

```kotlin
fun climbStairs(n: Int): Int {
    if (n <= 2) return n
    
    val dp = IntArray(n + 1)
    dp[1] = 1  // 1 way to reach step 1
    dp[2] = 2  // 2 ways to reach step 2 (1+1 or 2)
    
    for (i in 3..n) {
        dp[i] = dp[i - 1] + dp[i - 2]
    }
    
    return dp[n]
}

// Example:
println(climbStairs(3))  // 3 ways: (1+1+1), (1+2), (2+1)
println(climbStairs(4))  // 5 ways
```

**Recurrence:**
```
dp[i] = dp[i-1] + dp[i-2]
       (from i-1  (from i-2
        with 1    with 2
        step)     steps)
```

---

### 3. Coin Change - Minimum Coins

**Problem:** Given coins [1,2,5], find minimum coins to make amount.

```kotlin
fun coinChange(coins: IntArray, amount: Int): Int {
    val dp = IntArray(amount + 1) { amount + 1 }
    dp[0] = 0  // 0 coins for amount 0
    
    for (i in 1..amount) {
        for (coin in coins) {
            if (coin <= i) {
                dp[i] = minOf(dp[i], dp[i - coin] + 1)
            }
        }
    }
    
    return if (dp[amount] > amount) -1 else dp[amount]
}

// Example:
val coins = intArrayOf(1, 2, 5)
println(coinChange(coins, 11))  // 3 (5+5+1)
println(coinChange(coins, 3))   // 2 (2+1)
```

**How it works:**
```
coins = [1, 2, 5], amount = 11

dp[0] = 0
dp[1] = 1  (1)
dp[2] = 1  (2)
dp[3] = 2  (2+1)
dp[4] = 2  (2+2)
dp[5] = 1  (5)
dp[6] = 2  (5+1)
dp[7] = 2  (5+2)
dp[8] = 3  (5+2+1)
dp[9] = 3  (5+2+2)
dp[10] = 2 (5+5)
dp[11] = 3 (5+5+1)
```

---

### 4. 0/1 Knapsack

**Problem:** Items with weight and value. Max value with weight limit.

```kotlin
fun knapsack(weights: IntArray, values: IntArray, capacity: Int): Int {
    val n = weights.size
    val dp = Array(n + 1) { IntArray(capacity + 1) }
    
    for (i in 1..n) {
        for (w in 1..capacity) {
            if (weights[i - 1] <= w) {
                // Can include item i
                dp[i][w] = maxOf(
                    dp[i - 1][w],  // Don't take
                    dp[i - 1][w - weights[i - 1]] + values[i - 1]  // Take
                )
            } else {
                // Can't include (too heavy)
                dp[i][w] = dp[i - 1][w]
            }
        }
    }
    
    return dp[n][capacity]
}

// Example:
val weights = intArrayOf(1, 3, 4, 5)
val values = intArrayOf(1, 4, 5, 7)
val capacity = 7
println(knapsack(weights, values, capacity))  // 9 (items 2 and 3)
```

**DP Table:**
```
      w=0  1  2  3  4  5  6  7
i=0    0  0  0  0  0  0  0  0
i=1    0  1  1  1  1  1  1  1  (w=1,v=1)
i=2    0  1  1  4  5  5  5  5  (w=3,v=4)
i=3    0  1  1  4  5  6  6  9  (w=4,v=5)
i=4    0  1  1  4  5  7  7  9  (w=5,v=7)
```

---

### 5. Longest Common Subsequence (LCS)

**Problem:** Find longest subsequence common to both strings.

```kotlin
fun longestCommonSubsequence(text1: String, text2: String): Int {
    val m = text1.length
    val n = text2.length
    val dp = Array(m + 1) { IntArray(n + 1) }
    
    for (i in 1..m) {
        for (j in 1..n) {
            if (text1[i - 1] == text2[j - 1]) {
                dp[i][j] = dp[i - 1][j - 1] + 1
            } else {
                dp[i][j] = maxOf(dp[i - 1][j], dp[i][j - 1])
            }
        }
    }
    
    return dp[m][n]
}

// Example:
println(longestCommonSubsequence("abcde", "ace"))  // 3 ("ace")
println(longestCommonSubsequence("abc", "abc"))    // 3
println(longestCommonSubsequence("abc", "def"))    // 0
```

**DP Table for "abcde" vs "ace":**
```
      ""  a  c  e
""     0  0  0  0
a      0  1  1  1
b      0  1  1  1
c      0  1  2  2
d      0  1  2  2
e      0  1  2  3
```

---

### 6. Longest Increasing Subsequence (LIS)

**Problem:** Find longest strictly increasing subsequence.

```kotlin
fun lengthOfLIS(nums: IntArray): Int {
    if (nums.isEmpty()) return 0
    
    val dp = IntArray(nums.size) { 1 }  // Each element is LIS of length 1
    
    for (i in nums.indices) {
        for (j in 0 until i) {
            if (nums[j] < nums[i]) {
                dp[i] = maxOf(dp[i], dp[j] + 1)
            }
        }
    }
    
    return dp.maxOrNull()!!
}

// Example:
println(lengthOfLIS(intArrayOf(10, 9, 2, 5, 3, 7, 101, 18)))  // 4 ([2,3,7,101])
```

**How it works:**
```
nums = [10, 9, 2, 5, 3, 7, 101, 18]
dp   = [ 1, 1, 1, 2, 2, 3,   4,  4]

dp[i] = length of LIS ending at index i

dp[3] = 2 because [2,5] is LIS ending at index 3
dp[5] = 3 because [2,3,7] is LIS ending at index 5
dp[6] = 4 because [2,3,7,101] is LIS ending at index 6
```

---

### 7. House Robber

**Problem:** Houses in a row with money. Can't rob adjacent houses.

```kotlin
fun rob(nums: IntArray): Int {
    if (nums.isEmpty()) return 0
    if (nums.size == 1) return nums[0]
    
    val dp = IntArray(nums.size)
    dp[0] = nums[0]
    dp[1] = maxOf(nums[0], nums[1])
    
    for (i in 2 until nums.size) {
        dp[i] = maxOf(
            dp[i - 1],              // Don't rob house i
            dp[i - 2] + nums[i]     // Rob house i
        )
    }
    
    return dp[nums.size - 1]
}

// Example:
println(rob(intArrayOf(1, 2, 3, 1)))      // 4 (rob house 0 and 2)
println(rob(intArrayOf(2, 7, 9, 3, 1)))   // 12 (rob house 0, 2, 4)
```

**Space-optimized:**
```kotlin
fun robOptimized(nums: IntArray): Int {
    if (nums.isEmpty()) return 0
    
    var prev2 = 0
    var prev1 = 0
    
    for (num in nums) {
        val curr = maxOf(prev1, prev2 + num)
        prev2 = prev1
        prev1 = curr
    }
    
    return prev1
}
```

---

### 8. Edit Distance (Levenshtein Distance)

**Problem:** Minimum operations to convert string1 to string2.

```kotlin
fun minDistance(word1: String, word2: String): Int {
    val m = word1.length
    val n = word2.length
    val dp = Array(m + 1) { IntArray(n + 1) }
    
    // Base cases
    for (i in 0..m) dp[i][0] = i  // Delete all
    for (j in 0..n) dp[0][j] = j  // Insert all
    
    for (i in 1..m) {
        for (j in 1..n) {
            if (word1[i - 1] == word2[j - 1]) {
                dp[i][j] = dp[i - 1][j - 1]  // No operation
            } else {
                dp[i][j] = 1 + minOf(
                    dp[i - 1][j],      // Delete
                    dp[i][j - 1],      // Insert
                    dp[i - 1][j - 1]   // Replace
                )
            }
        }
    }
    
    return dp[m][n]
}

// Example:
println(minDistance("horse", "ros"))  // 3 (replace, delete, delete)
println(minDistance("intention", "execution"))  // 5
```

---

### 9. Maximum Subarray Sum (Kadane's Algorithm)

**Problem:** Find contiguous subarray with maximum sum.

```kotlin
fun maxSubArray(nums: IntArray): Int {
    var maxSoFar = nums[0]
    var maxEndingHere = nums[0]
    
    for (i in 1 until nums.size) {
        maxEndingHere = maxOf(nums[i], maxEndingHere + nums[i])
        maxSoFar = maxOf(maxSoFar, maxEndingHere)
    }
    
    return maxSoFar
}

// Example:
println(maxSubArray(intArrayOf(-2, 1, -3, 4, -1, 2, 1, -5, 4)))  // 6 ([4,-1,2,1])
```

---

### 10. Partition Equal Subset Sum

**Problem:** Can array be partitioned into two equal sum subsets?

```kotlin
fun canPartition(nums: IntArray): Boolean {
    val sum = nums.sum()
    if (sum % 2 != 0) return false
    
    val target = sum / 2
    val dp = BooleanArray(target + 1)
    dp[0] = true  // Can make sum 0 with empty subset
    
    for (num in nums) {
        for (j in target downTo num) {
            dp[j] = dp[j] || dp[j - num]
        }
    }
    
    return dp[target]
}

// Example:
println(canPartition(intArrayOf(1, 5, 11, 5)))  // true ([1,5,5] and [11])
println(canPartition(intArrayOf(1, 2, 3, 5)))   // false
```

---

### DP Patterns Summary

### 1. Linear DP
- Fibonacci, Climbing Stairs, House Robber
- **Pattern:** `dp[i] depends on dp[i-1], dp[i-2], ...`

### 2. Grid/2D DP
- Knapsack, LCS, Edit Distance
- **Pattern:** `dp[i][j] depends on dp[i-1][j], dp[i][j-1], dp[i-1][j-1]`

### 3. Interval DP
- Longest Palindromic Substring
- **Pattern:** `dp[i][j] depends on dp[i+1][j-1]`

### 4. DP on Subsets
- Traveling Salesman, Bitmask DP
- **Pattern:** Use bitmask to represent state

---

### Top-Down vs Bottom-Up

**Top-Down (Memoization):**
```kotlin
fun dpTopDown(n: Int, memo: MutableMap<Int, Int> = mutableMapOf()): Int {
    if (n <= 1) return n
    if (n in memo) return memo[n]!!
    
    val result = dpTopDown(n - 1, memo) + dpTopDown(n - 2, memo)
    memo[n] = result
    return result
}

//  Pros: Intuitive, only computes needed states
//  Cons: Recursion overhead, stack overflow risk
```

**Bottom-Up (Tabulation):**
```kotlin
fun dpBottomUp(n: Int): Int {
    if (n <= 1) return n
    
    val dp = IntArray(n + 1)
    dp[0] = 0
    dp[1] = 1
    
    for (i in 2..n) {
        dp[i] = dp[i - 1] + dp[i - 2]
    }
    
    return dp[n]
}

//  Pros: No recursion, better performance
//  Cons: Computes all states, less intuitive
```

---

### Real-World Android Example

```kotlin
// Text prediction: Levenshtein distance for autocorrect
class SpellChecker {
    fun suggestCorrections(input: String, dictionary: List<String>): List<String> {
        return dictionary
            .map { it to editDistance(input, it) }
            .filter { it.second <= 2 }  // Max 2 edits
            .sortedBy { it.second }
            .take(5)
            .map { it.first }
    }
    
    private fun editDistance(s1: String, s2: String): Int {
        val m = s1.length
        val n = s2.length
        val dp = Array(m + 1) { IntArray(n + 1) }
        
        for (i in 0..m) dp[i][0] = i
        for (j in 0..n) dp[0][j] = j
        
        for (i in 1..m) {
            for (j in 1..n) {
                if (s1[i - 1] == s2[j - 1]) {
                    dp[i][j] = dp[i - 1][j - 1]
                } else {
                    dp[i][j] = 1 + minOf(
                        dp[i - 1][j],
                        dp[i][j - 1],
                        dp[i - 1][j - 1]
                    )
                }
            }
        }
        
        return dp[m][n]
    }
}
```

---

### Key Takeaways

1. **DP** = Break problem into overlapping subproblems
2. **Two approaches:** Top-down (memoization) vs Bottom-up (tabulation)
3. **Optimal substructure** + **Overlapping subproblems** = Use DP
4. **Fibonacci** - Classic DP introduction
5. **Knapsack** - 2D DP, include/exclude pattern
6. **LCS/LIS** - String/sequence problems
7. **Kadane's** - Maximum subarray (1D DP)
8. **Space optimization** - Often can reduce from O(n) to O(1)
9. **Start with recursion** → Add memoization → Convert to tabulation
10. **Practice** - DP requires solving many problems to recognize patterns

---

## Ответ (RU)

Динамическое программирование (DP) - мощная техника для решения задач оптимизации путём разбиения на перекрывающиеся подзадачи.



### Что такое динамическое программирование?

**Динамическое программирование** = Техника оптимизации, которая решает задачи путём:
1. Разбиения на **перекрывающиеся подзадачи**
2. Решения каждой подзадачи **один раз**
3. **Сохранения результатов** (мемоизация/табуляция)
4. Повторного использования сохранённых результатов

### Ключевые выводы

1. **DP** = Разбиение задачи на перекрывающиеся подзадачи
2. **Два подхода:** Top-down (мемоизация) vs Bottom-up (табуляция)
3. **Fibonacci** - Классическое введение в DP
4. **Knapsack** - 2D DP, паттерн включить/исключить
5. **LCS/LIS** - Задачи со строками/последовательностями
6. **Оптимизация памяти** - Часто можно сократить с O(n) до O(1)
7. **Начинайте с рекурсии** → Добавьте мемоизацию → Конвертируйте в табуляцию
8. **Практика** - DP требует решения многих задач для распознавания паттернов

## Follow-ups

1. What is the difference between memoization and tabulation?
2. How do you identify if a problem can be solved with DP?
3. What is the time complexity of solving Fibonacci with DP?
4. How do you reconstruct the solution path in DP problems?
5. What is the difference between 0/1 Knapsack and Unbounded Knapsack?
6. How do you optimize space complexity in DP solutions?
7. What is matrix chain multiplication problem?
8. How does DP differ from divide-and-conquer?
9. What is the longest palindromic subsequence problem?
10. How do you solve the coin change problem with unlimited coins?

## Related Questions

- [[q-two-pointers-sliding-window--algorithms--medium]]
- [[q-backtracking-algorithms--algorithms--hard]]
- [[q-sorting-algorithms-comparison--algorithms--medium]]
