---
id: algo-009
title: "Dynamic Programming Fundamentals / Основы динамического программирования"
aliases: ["Dynamic Programming", "Основы динамического программирования"]
topic: algorithms
subtopics: [dp, dynamic-programming, memoization]
question_kind: coding
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-algorithms
related: [c-algorithms, q-advanced-graph-algorithms--algorithms--hard]
created: 2025-10-12
updated: 2025-11-11
tags: [algorithms, difficulty/hard, dp, dynamic-programming, memoization, optimization]
sources: ["https://en.wikipedia.org/wiki/Dynamic_programming"]

date created: Saturday, November 1st 2025, 1:24:13 pm
date modified: Tuesday, November 25th 2025, 8:53:47 pm
---

# Вопрос (RU)
> Что такое динамическое программирование? Чем оно отличается от рекурсии? Каковы основные паттерны DP и классические задачи?

# Question (EN)
> What is Dynamic Programming? How does it differ from recursion? What are the main DP patterns and classic problems?

---

## Ответ (RU)

**Теория динамического программирования:**
Динамическое программирование (DP) — техника решения задач (часто оптимизации или подсчёта) путём разбиения их на перекрывающиеся подзадачи и использования оптимальной подструктуры. DP решает каждую уникальную подзадачу один раз и сохраняет результат для повторного использования, избегая экспоненциального взрыва состояний.

Важно: DP может быть реализовано как с рекурсией, так и без неё. Разница не в "наличии рекурсии", а в том, кэшируем ли мы результаты подзадач и переиспользуем ли их.

**Ключевые свойства:**
- **Оптимальная подструктура** — оптимальное решение задачи выражается через оптимальные решения её подзадач.
- **Перекрывающиеся подзадачи** — множество подзадач мало по сравнению с числом их вызовов в наивном решении.

**Два подхода DP:**
- **Top-Down (мемоизация)** — рекурсия с кешированием результатов подзадач.
- **Bottom-Up (табуляция)** — итеративное заполнение таблицы состояний по возрастанию размера подзадач.

**Основные паттерны DP (кратко):**
- 1D DP по индексу (например, Fibonacci, количество способов добраться).
- 2D DP по двум измерениям (например, LCS, редактирующее расстояние).
- Knapsack-подобные задачи (ограничения по ресурсу/весу).
- Coin Change / Unbounded Knapsack (неограниченное количество элементов).
- DP по подотрезкам/подмассивам.
- DP по маскам или состояниям (более продвинутое, для hard-уровня).

**Fibonacci — классический пример:**
```kotlin
// Наивная рекурсия O(2^n) - экспоненциально медленно
fun fibRecursive(n: Int): Long {
    if (n <= 1) return n.toLong()
    return fibRecursive(n - 1) + fibRecursive(n - 2)
}

// Top-Down DP с мемоизацией O(n) по времени и O(n) по памяти
fun fibMemo(n: Int, memo: MutableMap<Int, Long> = mutableMapOf()): Long {
    if (n <= 1) return n.toLong()

    if (n in memo) return memo[n]!!

    val result = fibMemo(n - 1, memo) + fibMemo(n - 2, memo)
    memo[n] = result
    return result
}

// Bottom-Up DP с табуляцией O(n) по времени и памяти
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

// Оптимизированная версия O(1) памяти (всё ещё использует DP-рекуррентное соотношение)
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

**0/1 Knapsack — задача о рюкзаке:**
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

**Coin Change — минимальное количество монет:**
```kotlin
// Найти минимальное количество монет для суммы
// Классический bottom-up для неограниченного количества монет каждого номинала
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

**Maximum Subarray Sum (Алгоритм Кадане):**
```kotlin
// Найти максимальную сумму подмассива
// Можно интерпретировать как DP по префиксу: dp[i] = max(nums[i], dp[i-1] + nums[i])
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

## Answer (EN)

**Dynamic Programming Theory:**
Dynamic Programming (DP) is a technique for solving problems (often optimization or counting) by breaking them into overlapping subproblems and exploiting optimal substructure. DP solves each distinct subproblem once and stores the result for reuse, avoiding exponential blow-up.

Important: DP can be implemented with or without recursion. The key difference from plain recursion is caching and reusing subproblem results, not the presence of recursion itself.

**Key Properties:**
- **Optimal Substructure** - the optimal solution can be expressed via optimal solutions of its subproblems.
- **Overlapping Subproblems** - the set of distinct subproblems is small compared to the number of times they would be recomputed in a naive solution.

**Two DP Approaches:**
- **Top-Down (Memoization)** - recursion with caching of subproblem results.
- **Bottom-Up (Tabulation)** - iterative filling of a state table in order of increasing subproblem size.

**Main DP Patterns (brief):**
- 1D DP over index (e.g., Fibonacci, ways to reach a position).
- 2D DP (e.g., LCS, edit distance).
- Knapsack-style problems (resource/weight constraints).
- Coin Change / Unbounded Knapsack (unlimited items of each type).
- Interval / subarray DP.
- Bitmask / state-based DP (advanced, typical for hard problems).

**Fibonacci - Classic Example:**
```kotlin
// Naive recursion O(2^n) - exponentially slow
fun fibRecursive(n: Int): Long {
    if (n <= 1) return n.toLong()
    return fibRecursive(n - 1) + fibRecursive(n - 2)
}

// Top-Down DP with memoization O(n) time and O(n) space
fun fibMemo(n: Int, memo: MutableMap<Int, Long> = mutableMapOf()): Long {
    if (n <= 1) return n.toLong()

    if (n in memo) return memo[n]!!

    val result = fibMemo(n - 1, memo) + fibMemo(n - 2, memo)
    memo[n] = result
    return result
}

// Bottom-Up DP with tabulation O(n) time and space
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

// Space-optimized version O(1) space (still uses the DP recurrence)
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
// Classic bottom-up solution assuming unlimited coins of each denomination
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
// Can be seen as DP on prefix: dp[i] = max(nums[i], dp[i-1] + nums[i])
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

## References

- [[c-algorithms]]
- "https://en.wikipedia.org/wiki/Dynamic_programming"

## Related Questions

### Prerequisites (Easier)
- [[q-data-structures-overview--algorithms--easy]] - Data structures basics

### Related (Same Level)
- [[q-two-pointers-sliding-window--algorithms--medium]] - Two pointers technique
- [[q-sorting-algorithms-comparison--algorithms--medium]] - Sorting algorithms

### Advanced (Harder)
- [[q-backtracking-algorithms--algorithms--hard]] - Backtracking algorithms

## Дополнительные Вопросы (RU)
- В чем разница между мемоизацией и табуляцией?
- Как определить, что задачу можно решить с помощью DP?
- Каковы основные паттерны DP и когда каждый из них применять?
## Связанные Вопросы (RU)
### Предпосылки (проще)
- [[q-data-structures-overview--algorithms--easy]] - Базовые структуры данных
### Связанные (тот Же уровень)
- [[q-two-pointers-sliding-window--algorithms--medium]] - Техника двух указателей
- [[q-sorting-algorithms-comparison--algorithms--medium]] - Сравнение сортировок
### Продвинутые (сложнее)
- [[q-backtracking-algorithms--algorithms--hard]] - Алгоритмы с возвратом (backtracking)