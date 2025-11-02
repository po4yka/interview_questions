---
id: algo-009
title: "Dynamic Programming Fundamentals / Основы динамического программирования"
aliases: ["Dynamic Programming", "Основы динамического программирования"]
topic: algorithms
subtopics: [dp, dynamic-programming, memoization, tabulation]
question_kind: coding
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-algorithms
related: [c-dynamic-programming]
created: 2025-10-12
updated: 2025-01-25
tags: [algorithms, difficulty/hard, dp, dynamic-programming, memoization, optimization]
sources: [https://en.wikipedia.org/wiki/Dynamic_programming]
date created: Sunday, October 12th 2025, 9:42:52 pm
date modified: Saturday, November 1st 2025, 5:43:37 pm
---

# Вопрос (RU)
> Что такое динамическое программирование? Чем оно отличается от рекурсии? Каковы основные паттерны DP и классические задачи?

# Question (EN)
> What is Dynamic Programming? How does it differ from recursion? What are the main DP patterns and classic problems?

---

## Ответ (RU)

**Теория динамического программирования:**
Динамическое программирование (DP) - мощная техника для решения задач оптимизации путём разбиения на перекрывающиеся подзадачи. DP решает каждую подзадачу один раз и сохраняет результат для повторного использования.

**Ключевые свойства:**
- **Оптимальная подструктура** - оптимальное решение содержит оптимальные решения подзадач
- **Перекрывающиеся подзадачи** - одни и те же подзадачи решаются многократно

**Два подхода DP:**
- **Top-Down (мемоизация)** - рекурсия с сохранением результатов
- **Bottom-Up (табуляция)** - итеративное заполнение таблицы

**Fibonacci - классический пример:**
```kotlin
// Наивная рекурсия O(2^n) - экспоненциально медленно
fun fibRecursive(n: Int): Long {
    if (n <= 1) return n.toLong()
    return fibRecursive(n - 1) + fibRecursive(n - 2)
}

// Top-Down DP с мемоизацией O(n)
fun fibMemo(n: Int, memo: MutableMap<Int, Long> = mutableMapOf()): Long {
    if (n <= 1) return n.toLong()

    if (n in memo) return memo[n]!!

    val result = fibMemo(n - 1, memo) + fibMemo(n - 2, memo)
    memo[n] = result
    return result
}

// Bottom-Up DP с табуляцией O(n)
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

// Оптимизированная версия O(1) памяти
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
```

**0/1 Knapsack - задача о рюкзаке:**
```kotlin
// Максимальная ценность при ограничении веса
fun knapsack(weights: IntArray, values: IntArray, capacity: Int): Int {
    val n = weights.size
    val dp = Array(n + 1) { IntArray(capacity + 1) }

    for (i in 1..n) {
        for (w in 1..capacity) {
            if (weights[i - 1] <= w) {
                // Можем взять предмет i
                dp[i][w] = maxOf(
                    dp[i - 1][w],  // Не берём
                    dp[i - 1][w - weights[i - 1]] + values[i - 1]  // Берём
                )
            } else {
                // Не можем взять (слишком тяжёлый)
                dp[i][w] = dp[i - 1][w]
            }
        }
    }

    return dp[n][capacity]
}
```

**Longest Common Subsequence (LCS):**
```kotlin
// Найти длину наибольшей общей подпоследовательности
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
```

**Coin Change - минимальное количество монет:**
```kotlin
// Найти минимальное количество монет для суммы
fun coinChange(coins: IntArray, amount: Int): Int {
    val dp = IntArray(amount + 1) { amount + 1 }
    dp[0] = 0  // 0 монет для суммы 0

    for (i in 1..amount) {
        for (coin in coins) {
            if (coin <= i) {
                dp[i] = minOf(dp[i], dp[i - coin] + 1)
            }
        }
    }

    return if (dp[amount] > amount) -1 else dp[amount]
}
```

**Maximum Subarray Sum (Kadane's Algorithm):**
```kotlin
// Найти максимальную сумму подмассива
fun maxSubArray(nums: IntArray): Int {
    var maxSoFar = nums[0]
    var maxEndingHere = nums[0]

    for (i in 1 until nums.size) {
        maxEndingHere = maxOf(nums[i], maxEndingHere + nums[i])
        maxSoFar = maxOf(maxSoFar, maxEndingHere)
    }

    return maxSoFar
}
```

## Answer (EN)

**Dynamic Programming Theory:**
Dynamic Programming (DP) is a powerful technique for solving optimization problems by breaking them into overlapping subproblems. DP solves each subproblem once and stores the result for reuse.

**Key Properties:**
- **Optimal Substructure** - optimal solution contains optimal solutions to subproblems
- **Overlapping Subproblems** - same subproblems solved multiple times

**Two DP Approaches:**
- **Top-Down (Memoization)** - recursion with result storage
- **Bottom-Up (Tabulation)** - iterative table filling

**Fibonacci - Classic Example:**
```kotlin
// Naive recursion O(2^n) - exponentially slow
fun fibRecursive(n: Int): Long {
    if (n <= 1) return n.toLong()
    return fibRecursive(n - 1) + fibRecursive(n - 2)
}

// Top-Down DP with memoization O(n)
fun fibMemo(n: Int, memo: MutableMap<Int, Long> = mutableMapOf()): Long {
    if (n <= 1) return n.toLong()

    if (n in memo) return memo[n]!!

    val result = fibMemo(n - 1, memo) + fibMemo(n - 2, memo)
    memo[n] = result
    return result
}

// Bottom-Up DP with tabulation O(n)
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

// Space-optimized version O(1) memory
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
```

**0/1 Knapsack Problem:**
```kotlin
// Maximum value with weight constraint
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
```

**Longest Common Subsequence (LCS):**
```kotlin
// Find length of longest common subsequence
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
```

**Coin Change - Minimum Coins:**
```kotlin
// Find minimum number of coins for amount
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
```

**Maximum Subarray Sum (Kadane's Algorithm):**
```kotlin
// Find maximum sum of subarray
fun maxSubArray(nums: IntArray): Int {
    var maxSoFar = nums[0]
    var maxEndingHere = nums[0]

    for (i in 1 until nums.size) {
        maxEndingHere = maxOf(nums[i], maxEndingHere + nums[i])
        maxSoFar = maxOf(maxSoFar, maxEndingHere)
    }

    return maxSoFar
}
```

---

## Follow-ups

- What is the difference between memoization and tabulation?
- How do you identify if a problem can be solved with DP?
- What are the main DP patterns and when to use each?

## Related Questions

### Prerequisites (Easier)
- [[q-data-structures-overview--algorithms--easy]] - Data structures basics

### Related (Same Level)
- [[q-two-pointers-sliding-window--algorithms--medium]] - Two pointers technique
- [[q-sorting-algorithms-comparison--algorithms--medium]] - Sorting algorithms

### Advanced (Harder)
- [[q-backtracking-algorithms--algorithms--hard]] - Backtracking algorithms
