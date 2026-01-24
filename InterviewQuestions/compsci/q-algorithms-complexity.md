---
id: cs-algo-complexity
title: Algorithm Complexity Analysis
topic: algorithms
difficulty: medium
tags:
- cs_algorithms
- complexity
anki_cards:
- slug: cs-algo-complexity-0-en
  language: en
  anki_id: 1769160675425
  synced_at: '2026-01-23T13:31:18.866702'
- slug: cs-algo-complexity-0-ru
  language: ru
  anki_id: 1769160675449
  synced_at: '2026-01-23T13:31:18.867959'
- slug: cs-algo-complexity-1-en
  language: en
  anki_id: 1769160675474
  synced_at: '2026-01-23T13:31:18.869198'
- slug: cs-algo-complexity-1-ru
  language: ru
  anki_id: 1769160675500
  synced_at: '2026-01-23T13:31:18.872309'
- slug: cs-algo-complexity-2-en
  language: en
  anki_id: 1769160675524
  synced_at: '2026-01-23T13:31:18.873580'
- slug: cs-algo-complexity-2-ru
  language: ru
  anki_id: 1769160675550
  synced_at: '2026-01-23T13:31:18.879465'
- slug: cs-algo-complexity-3-en
  language: en
  anki_id: 1769160675575
  synced_at: '2026-01-23T13:31:18.881094'
- slug: cs-algo-complexity-3-ru
  language: ru
  anki_id: 1769160675600
  synced_at: '2026-01-23T13:31:18.882578'
---
# Algorithm Complexity Analysis

## Big-O Notation

Big-O describes the **upper bound** of algorithm growth rate as input size approaches infinity.

**Formal definition**: f(n) = O(g(n)) if there exist constants c > 0 and n0 such that f(n) <= c * g(n) for all n >= n0.

### Common Complexities (Slowest to Fastest)

| Complexity | Name | Example |
|------------|------|---------|
| O(1) | Constant | Array access, hash lookup |
| O(log n) | Logarithmic | Binary search |
| O(n) | Linear | Linear search, single loop |
| O(n log n) | Linearithmic | MergeSort, QuickSort (avg) |
| O(n^2) | Quadratic | Nested loops, bubble sort |
| O(n^3) | Cubic | Matrix multiplication (naive) |
| O(2^n) | Exponential | Recursive Fibonacci, subsets |
| O(n!) | Factorial | Permutations, TSP brute force |

### Growth Rate Comparison

For n = 1000:
- O(1): 1 operation
- O(log n): ~10 operations
- O(n): 1,000 operations
- O(n log n): ~10,000 operations
- O(n^2): 1,000,000 operations
- O(2^n): More than atoms in universe

## Big-Omega and Big-Theta

**Big-Omega (lower bound)**: f(n) = Omega(g(n)) means f grows at least as fast as g.

**Big-Theta (tight bound)**: f(n) = Theta(g(n)) means f grows exactly as fast as g.

**Interview tip**: Big-O is most commonly asked, but understand all three.

## Time vs Space Complexity

**Time complexity**: How execution time grows with input size.
**Space complexity**: How memory usage grows with input size.

### Trade-offs

| Scenario | Time | Space | Example |
|----------|------|-------|---------|
| Memoization | Better | Worse | Dynamic programming |
| In-place algo | Same | Better | QuickSort vs MergeSort |
| Hash table | Better (lookup) | Worse | O(1) vs O(n) search |

## Amortized Analysis

**Purpose**: Analyze average cost per operation over worst-case sequence.

### Example: Dynamic Array (ArrayList)

- Single append: O(1) normally, O(n) when resizing
- Amortized append: O(1) because resizing is rare

**Accounting method**: Each O(1) operation "pays" for future resizing.

```
Array size: 1 -> 2 -> 4 -> 8 -> 16
Copies:     1 +  2 +  4 +  8 = 15 copies for 16 elements
Amortized: 15/16 < 2 copies per element = O(1)
```

### Common Amortized O(1) Operations

- Dynamic array append
- Hash table insert (with good hash function)
- Splay tree access (over sequence)
- Union-Find with path compression

## Analyzing Recursive Algorithms

### Recurrence Relations

**Pattern**: T(n) = a * T(n/b) + f(n)

**Master Theorem** (simplified):
- If f(n) = O(n^c) where c < log_b(a): T(n) = O(n^log_b(a))
- If f(n) = O(n^c) where c = log_b(a): T(n) = O(n^c * log n)
- If f(n) = O(n^c) where c > log_b(a): T(n) = O(f(n))

### Common Examples

| Algorithm | Recurrence | Complexity |
|-----------|------------|------------|
| Binary search | T(n) = T(n/2) + O(1) | O(log n) |
| MergeSort | T(n) = 2T(n/2) + O(n) | O(n log n) |
| Naive Fibonacci | T(n) = T(n-1) + T(n-2) | O(2^n) |
| Strassen matrix | T(n) = 7T(n/2) + O(n^2) | O(n^2.81) |

## Space Complexity Considerations

### Stack Space (Recursion)

```python
# O(n) space due to call stack
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

# O(1) space - iterative
def factorial_iter(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
```

### Tail Recursion

Tail recursive functions can be optimized to O(1) space by some compilers:

```python
# Tail recursive (optimizable)
def factorial_tail(n, acc=1):
    if n <= 1:
        return acc
    return factorial_tail(n - 1, n * acc)
```

## Complexity Analysis Techniques

### 1. Count Operations

```python
def example(n):
    total = 0           # O(1)
    for i in range(n):  # O(n)
        for j in range(n):  # O(n)
            total += 1  # O(1)
    return total
# Total: O(n^2)
```

### 2. Identify Dominant Term

O(n^2 + n + 1) = O(n^2) - lower terms are dropped.

### 3. Nested Loops

- Independent loops: multiply (O(n) * O(m) = O(nm))
- Sequential loops: add (O(n) + O(m) = O(n + m))

### 4. Logarithmic Patterns

When input is halved each iteration:
```python
while n > 0:
    n = n // 2  # O(log n)
```

## Common Mistakes

1. **Confusing O(1) with "fast"**: O(1) with large constant can be slower than O(n) for small n.

2. **Ignoring hidden costs**: String concatenation in loop = O(n^2), not O(n).

3. **Hash table assumptions**: Hash operations are O(1) average, O(n) worst case.

4. **Recursion depth**: Python default limit is ~1000. Deep recursion = stack overflow.

## Interview Questions

1. **What's the complexity of this code?** - Walk through step by step.
2. **Can you optimize this?** - Consider time-space trade-offs.
3. **What's best/worst/average case?** - Identify different scenarios.
4. **How does it scale?** - Explain behavior with large inputs.
