---
id: cs-algo-dp
title: Dynamic Programming
topic: algorithms
difficulty: hard
tags:
- cs_algorithms
- dynamic_programming
anki_cards:
- slug: cs-algo-dp-0-en
  language: en
  anki_id: 1769160678325
  synced_at: '2026-01-23T13:31:19.061529'
- slug: cs-algo-dp-0-ru
  language: ru
  anki_id: 1769160678349
  synced_at: '2026-01-23T13:31:19.063875'
- slug: cs-algo-dp-1-en
  language: en
  anki_id: 1769160678374
  synced_at: '2026-01-23T13:31:19.065695'
- slug: cs-algo-dp-1-ru
  language: ru
  anki_id: 1769160678400
  synced_at: '2026-01-23T13:31:19.067906'
- slug: cs-algo-dp-2-en
  language: en
  anki_id: 1769160678424
  synced_at: '2026-01-23T13:31:19.069947'
- slug: cs-algo-dp-2-ru
  language: ru
  anki_id: 1769160678450
  synced_at: '2026-01-23T13:31:19.072700'
- slug: cs-algo-dp-3-en
  language: en
  anki_id: 1769160678475
  synced_at: '2026-01-23T13:31:19.075155'
- slug: cs-algo-dp-3-ru
  language: ru
  anki_id: 1769160678499
  synced_at: '2026-01-23T13:31:19.077212'
---
# Dynamic Programming

## Core Concepts

**Dynamic Programming (DP)** solves problems by breaking them into overlapping subproblems and storing solutions to avoid redundant computation.

### Two Key Properties

1. **Optimal Substructure**: Optimal solution contains optimal solutions to subproblems.
2. **Overlapping Subproblems**: Same subproblems are solved multiple times.

### Two Approaches

| Approach | Direction | Method | Memory |
|----------|-----------|--------|--------|
| **Top-Down (Memoization)** | Start from main problem | Recursion + cache | O(n) call stack |
| **Bottom-Up (Tabulation)** | Start from base cases | Iteration + table | No stack overhead |

## Classic Problems

### 1. Fibonacci Numbers

**Problem**: Find nth Fibonacci number.

**Naive recursive**: O(2^n) time, O(n) space

```python
def fib_naive(n):
    if n <= 1:
        return n
    return fib_naive(n-1) + fib_naive(n-2)
```

**Memoization**: O(n) time, O(n) space

```python
def fib_memo(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fib_memo(n-1, memo) + fib_memo(n-2, memo)
    return memo[n]
```

**Tabulation**: O(n) time, O(n) space

```python
def fib_tab(n):
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]
```

**Space optimized**: O(n) time, O(1) space

```python
def fib_optimized(n):
    if n <= 1:
        return n
    prev2, prev1 = 0, 1
    for _ in range(2, n + 1):
        curr = prev1 + prev2
        prev2, prev1 = prev1, curr
    return prev1
```

### 2. Climbing Stairs

**Problem**: n stairs, can climb 1 or 2 steps. Count ways to reach top.

**Recurrence**: dp[i] = dp[i-1] + dp[i-2]

```python
def climb_stairs(n):
    if n <= 2:
        return n
    prev2, prev1 = 1, 2
    for _ in range(3, n + 1):
        curr = prev1 + prev2
        prev2, prev1 = prev1, curr
    return prev1
```

### 3. 0/1 Knapsack

**Problem**: Given weights and values, maximize value within capacity W.

**Recurrence**: dp[i][w] = max(dp[i-1][w], dp[i-1][w-weight[i]] + value[i])

```python
def knapsack(weights, values, W):
    n = len(weights)
    dp = [[0] * (W + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(W + 1):
            # Don't take item i
            dp[i][w] = dp[i-1][w]
            # Take item i (if possible)
            if weights[i-1] <= w:
                dp[i][w] = max(dp[i][w],
                    dp[i-1][w - weights[i-1]] + values[i-1])

    return dp[n][W]
```

**Space optimized**: O(W) space

```python
def knapsack_optimized(weights, values, W):
    dp = [0] * (W + 1)
    for i in range(len(weights)):
        for w in range(W, weights[i] - 1, -1):  # Reverse to avoid reuse
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])
    return dp[W]
```

### 4. Longest Common Subsequence (LCS)

**Problem**: Find longest subsequence common to two strings.

**Recurrence**:
- If s1[i] == s2[j]: dp[i][j] = dp[i-1][j-1] + 1
- Else: dp[i][j] = max(dp[i-1][j], dp[i][j-1])

```python
def lcs(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    return dp[m][n]
```

### 5. Longest Increasing Subsequence (LIS)

**Problem**: Find length of longest strictly increasing subsequence.

**O(n^2) solution**:

```python
def lis_n2(nums):
    n = len(nums)
    dp = [1] * n

    for i in range(1, n):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)

    return max(dp)
```

**O(n log n) solution** (binary search):

```python
import bisect

def lis_nlogn(nums):
    tails = []
    for num in nums:
        pos = bisect.bisect_left(tails, num)
        if pos == len(tails):
            tails.append(num)
        else:
            tails[pos] = num
    return len(tails)
```

### 6. Coin Change

**Problem**: Minimum coins to make amount.

**Recurrence**: dp[amount] = min(dp[amount - coin] + 1) for all coins

```python
def coin_change(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0

    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i and dp[i - coin] != float('inf'):
                dp[i] = min(dp[i], dp[i - coin] + 1)

    return dp[amount] if dp[amount] != float('inf') else -1
```

### 7. Edit Distance (Levenshtein)

**Problem**: Minimum operations (insert, delete, replace) to convert s1 to s2.

```python
def edit_distance(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Base cases
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j],    # Delete
                    dp[i][j-1],    # Insert
                    dp[i-1][j-1]   # Replace
                )

    return dp[m][n]
```

### 8. Matrix Chain Multiplication

**Problem**: Find optimal parenthesization for matrix chain.

```python
def matrix_chain(dims):
    n = len(dims) - 1
    dp = [[0] * n for _ in range(n)]

    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = float('inf')
            for k in range(i, j):
                cost = dp[i][k] + dp[k+1][j] + dims[i]*dims[k+1]*dims[j+1]
                dp[i][j] = min(dp[i][j], cost)

    return dp[0][n-1]
```

## DP Patterns

### 1. Linear DP

One-dimensional state (dp[i]).
Examples: Fibonacci, climbing stairs, house robber.

### 2. Grid DP

Two-dimensional state (dp[i][j]).
Examples: Unique paths, minimum path sum.

### 3. String DP

Compare/transform strings.
Examples: LCS, edit distance, palindrome.

### 4. Interval DP

Subproblems are intervals.
Examples: Matrix chain, burst balloons.

### 5. Subset DP (Bitmask)

State represents subset using bitmask.
Examples: TSP, assignment problem.

## Problem-Solving Framework

1. **Define state**: What does dp[i] (or dp[i][j]) represent?
2. **Find recurrence**: How does dp[i] relate to smaller subproblems?
3. **Identify base cases**: What are the trivial solutions?
4. **Determine order**: Which direction to fill the table?
5. **Optimize space**: Can we reduce from O(n^2) to O(n)?

## Common Mistakes

1. **Off-by-one errors**: Index carefully, especially with 1-indexed recurrences.
2. **Missing base cases**: Initialize dp array correctly.
3. **Wrong iteration order**: Bottom-up must solve subproblems first.
4. **Forgetting memoization**: Top-down without cache = exponential time.
