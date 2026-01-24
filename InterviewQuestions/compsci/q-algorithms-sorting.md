---
id: cs-algo-sorting
title: Sorting Algorithms
topic: algorithms
difficulty: medium
tags:
- cs_algorithms
- sorting
anki_cards:
- slug: cs-algo-sorting-0-en
  language: en
  anki_id: 1769160104101
  synced_at: '2026-01-23T13:31:18.839211'
- slug: cs-algo-sorting-0-ru
  language: ru
  anki_id: 1769160104123
  synced_at: '2026-01-23T13:31:18.840537'
- slug: cs-algo-sorting-1-en
  language: en
  anki_id: 1769160104147
  synced_at: '2026-01-23T13:31:18.841866'
- slug: cs-algo-sorting-1-ru
  language: ru
  anki_id: 1769160104172
  synced_at: '2026-01-23T13:31:18.843379'
- slug: cs-algo-sorting-2-en
  language: en
  anki_id: 1769160104197
  synced_at: '2026-01-23T13:31:18.844834'
- slug: cs-algo-sorting-2-ru
  language: ru
  anki_id: 1769160104222
  synced_at: '2026-01-23T13:31:18.847526'
- slug: cs-algo-sorting-3-en
  language: en
  anki_id: 1769160104247
  synced_at: '2026-01-23T13:31:18.848836'
- slug: cs-algo-sorting-3-ru
  language: ru
  anki_id: 1769160104272
  synced_at: '2026-01-23T13:31:18.850111'
- slug: cs-algo-sorting-4-en
  language: en
  anki_id: 1769160104297
  synced_at: '2026-01-23T13:31:18.851320'
- slug: cs-algo-sorting-4-ru
  language: ru
  anki_id: 1769160104322
  synced_at: '2026-01-23T13:31:18.852575'
- slug: cs-algo-sorting-5-en
  language: en
  anki_id: 1769160104347
  synced_at: '2026-01-23T13:31:18.855287'
- slug: cs-algo-sorting-5-ru
  language: ru
  anki_id: 1769160104371
  synced_at: '2026-01-23T13:31:18.856620'
---
# Sorting Algorithms - Comprehensive Guide

## Overview

Sorting algorithms arrange elements in a specific order. Understanding their trade-offs is essential for algorithm design and interviews.

## Comparison-Based Sorting

### QuickSort

**Mechanism**: Divide-and-conquer using pivot selection. Partitions array around pivot, recursively sorts subarrays.

**Complexity**:
- Average: O(n log n)
- Worst: O(n^2) - when pivot is smallest/largest element
- Space: O(log n) for recursion stack

**Key characteristics**:
- In-place (no extra array needed)
- Unstable (equal elements may reorder)
- Cache-friendly due to sequential access

```python
def quicksort(arr, low, high):
    if low < high:
        pi = partition(arr, low, high)
        quicksort(arr, low, pi - 1)
        quicksort(arr, pi + 1, high)

def partition(arr, low, high):
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1
```

### MergeSort

**Mechanism**: Divide array in half, recursively sort each half, merge sorted halves.

**Complexity**:
- All cases: O(n log n)
- Space: O(n) for temporary arrays

**Key characteristics**:
- Stable (preserves order of equal elements)
- Not in-place (requires extra memory)
- Good for linked lists
- Predictable performance

```python
def mergesort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = mergesort(arr[:mid])
    right = mergesort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
```

### HeapSort

**Mechanism**: Build max-heap, repeatedly extract maximum and place at end.

**Complexity**:
- All cases: O(n log n)
- Space: O(1) in-place

**Key characteristics**:
- In-place
- Unstable
- Poor cache locality
- Good when memory is constrained

```python
def heapsort(arr):
    n = len(arr)
    # Build max heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)
    # Extract elements
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        heapify(arr, i, 0)

def heapify(arr, n, i):
    largest = i
    left = 2 * i + 1
    right = 2 * i + 2
    if left < n and arr[left] > arr[largest]:
        largest = left
    if right < n and arr[right] > arr[largest]:
        largest = right
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        heapify(arr, n, largest)
```

## Non-Comparison Sorting

### Counting Sort

**Mechanism**: Count occurrences of each element, compute positions, place elements.

**Complexity**:
- Time: O(n + k) where k is range of input
- Space: O(k)

**Key characteristics**:
- Stable
- Only works for integers in known range
- Very fast when k is small

### Radix Sort

**Mechanism**: Sort by individual digits, from least to most significant.

**Complexity**:
- Time: O(d * (n + k)) where d is number of digits
- Space: O(n + k)

**Key characteristics**:
- Stable (uses counting sort as subroutine)
- Works for integers and strings
- Efficient for fixed-length keys

### Bucket Sort

**Mechanism**: Distribute elements into buckets, sort each bucket, concatenate.

**Complexity**:
- Average: O(n + k)
- Worst: O(n^2) if all elements in one bucket
- Space: O(n + k)

**Key characteristics**:
- Works well for uniformly distributed data
- Stable if using stable sort for buckets

## Comparison Table

| Algorithm | Best | Average | Worst | Space | Stable |
|-----------|------|---------|-------|-------|--------|
| QuickSort | O(n log n) | O(n log n) | O(n^2) | O(log n) | No |
| MergeSort | O(n log n) | O(n log n) | O(n log n) | O(n) | Yes |
| HeapSort | O(n log n) | O(n log n) | O(n log n) | O(1) | No |
| Counting | O(n + k) | O(n + k) | O(n + k) | O(k) | Yes |
| Radix | O(d*n) | O(d*n) | O(d*n) | O(n + k) | Yes |

## When to Use Which

- **QuickSort**: General-purpose, large datasets, when average performance matters
- **MergeSort**: Stable sort needed, linked lists, external sorting
- **HeapSort**: Memory constrained, need guaranteed O(n log n)
- **Counting Sort**: Small integer range, need linear time
- **Radix Sort**: Fixed-length integers or strings
- **Bucket Sort**: Uniformly distributed floating-point numbers

## Interview Tips

1. **Stability matters** when sorting objects by multiple keys
2. **QuickSort pivot selection** affects worst-case (use median-of-three or random)
3. **Hybrid approaches** (e.g., IntroSort = QuickSort + HeapSort + InsertionSort)
4. **External sorting** uses MergeSort for disk-based data
