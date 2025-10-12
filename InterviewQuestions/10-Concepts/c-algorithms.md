---
id: concept-algorithms
title: "Algorithms / Алгоритмы"
type: concept
tags: [concept, algorithms, complexity, sorting, searching, big-o]
created: 2025-10-12
updated: 2025-10-12
---

# Algorithms

## Overview

An algorithm is a step-by-step procedure for solving a problem. Understanding algorithms is crucial for writing efficient code and solving computational problems.

---

## Algorithm Complexity

### Big O Notation

```
O(1)         - Constant time
O(log n)     - Logarithmic
O(n)         - Linear
O(n log n)   - Linearithmic (efficient sorts)
O(n²)        - Quadratic
O(n³)        - Cubic
O(2ⁿ)        - Exponential
O(n!)        - Factorial
```

### Examples

```kotlin
// O(1) - Constant
fun getFirst(list: List<Int>): Int = list[0]

// O(n) - Linear
fun findMax(list: List<Int>): Int {
    var max = list[0]
    for (num in list) {
        if (num > max) max = num
    }
    return max
}

// O(log n) - Binary search
fun binarySearch(list: List<Int>, target: Int): Int {
    var left = 0
    var right = list.size - 1

    while (left <= right) {
        val mid = (left + right) / 2
        when {
            list[mid] == target -> return mid
            list[mid] < target -> left = mid + 1
            else -> right = mid - 1
        }
    }
    return -1
}

// O(n log n) - Merge sort
fun mergeSort(list: List<Int>): List<Int> {
    if (list.size <= 1) return list

    val mid = list.size / 2
    val left = mergeSort(list.subList(0, mid))
    val right = mergeSort(list.subList(mid, list.size))

    return merge(left, right)
}

// O(n²) - Bubble sort
fun bubbleSort(list: MutableList<Int>) {
    for (i in 0 until list.size) {
        for (j in 0 until list.size - i - 1) {
            if (list[j] > list[j + 1]) {
                list[j] = list[j + 1].also { list[j + 1] = list[j] }
            }
        }
    }
}
```

---

## Sorting Algorithms

### Comparison Sorts

**Merge Sort (O(n log n))**
- Divide and conquer
- Stable
- O(n) extra space

**Quick Sort (O(n log n) average, O(n²) worst)**
- Divide and conquer
- Not stable
- O(log n) space

**Heap Sort (O(n log n))**
- Uses binary heap
- Not stable
- O(1) space

### Non-Comparison Sorts

**Counting Sort (O(n + k))**
- For integers in range [0, k]
- Stable
- O(k) space

**Radix Sort (O(nk))**
- Sorts digit by digit
- Stable
- For fixed-length integers/strings

---

## Searching Algorithms

### Linear Search - O(n)
```kotlin
fun linearSearch(list: List<Int>, target: Int): Int {
    return list.indexOfFirst { it == target }
}
```

### Binary Search - O(log n)
```kotlin
fun binarySearch(list: List<Int>, target: Int): Int {
    return list.binarySearch(target)
}
```

---

## Algorithm Design Patterns

### Divide and Conquer
- Merge sort, quick sort, binary search
- Break problem into subproblems
- Solve recursively
- Combine solutions

### Dynamic Programming
- Fibonacci, knapsack, LCS
- Overlapping subproblems
- Optimal substructure
- Memoization or tabulation

### Greedy
- Activity selection, Huffman coding
- Make locally optimal choice
- Hope for global optimum

### Backtracking
- N-Queens, Sudoku solver
- Try all possibilities
- Prune invalid paths

---

## Related Questions

- [[q-data-structures-overview--algorithms--easy]]
- [[q-sql-join-algorithms-complexity--backend--hard]]

## Related Concepts

- [[c-data-structures]]

## MOC Links

- [[moc-algorithms]]
- [[moc-backend]]
