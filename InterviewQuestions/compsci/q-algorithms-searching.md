---
id: cs-algo-searching
title: Searching Algorithms
topic: algorithms
difficulty: medium
tags:
- cs_algorithms
- searching
anki_cards:
- slug: cs-algo-searching-0-en
  language: en
  anki_id: 1769160674124
  synced_at: '2026-01-23T13:31:18.796428'
- slug: cs-algo-searching-0-ru
  language: ru
  anki_id: 1769160674150
  synced_at: '2026-01-23T13:31:18.798297'
- slug: cs-algo-searching-1-en
  language: en
  anki_id: 1769160674174
  synced_at: '2026-01-23T13:31:18.800495'
- slug: cs-algo-searching-1-ru
  language: ru
  anki_id: 1769160674199
  synced_at: '2026-01-23T13:31:18.802312'
- slug: cs-algo-searching-2-en
  language: en
  anki_id: 1769160674225
  synced_at: '2026-01-23T13:31:18.803605'
- slug: cs-algo-searching-2-ru
  language: ru
  anki_id: 1769160674250
  synced_at: '2026-01-23T13:31:18.807013'
- slug: cs-algo-searching-3-en
  language: en
  anki_id: 1769160674275
  synced_at: '2026-01-23T13:31:18.808839'
- slug: cs-algo-searching-3-ru
  language: ru
  anki_id: 1769160674299
  synced_at: '2026-01-23T13:31:18.810848'
---
# Searching Algorithms

## Linear Search

**Mechanism**: Check each element sequentially until target found or end reached.

**Complexity**:
- Time: O(n)
- Space: O(1)

**When to use**:
- Unsorted data
- Small datasets
- Single search in unsorted collection

```python
def linear_search(arr, target):
    for i, val in enumerate(arr):
        if val == target:
            return i
    return -1
```

## Binary Search

**Mechanism**: Repeatedly divide sorted array in half, comparing target with middle element.

**Complexity**:
- Time: O(log n)
- Space: O(1) iterative, O(log n) recursive

**Prerequisites**: Array must be sorted.

```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = left + (right - left) // 2  # Avoids overflow
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

### Binary Search Variants

**Find first occurrence**:
```python
def find_first(arr, target):
    left, right = 0, len(arr) - 1
    result = -1
    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            result = mid
            right = mid - 1  # Continue searching left
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return result
```

**Find insertion point** (lower bound):
```python
def lower_bound(arr, target):
    left, right = 0, len(arr)
    while left < right:
        mid = left + (right - left) // 2
        if arr[mid] < target:
            left = mid + 1
        else:
            right = mid
    return left
```

**Search in rotated sorted array**:
```python
def search_rotated(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            return mid
        # Left half is sorted
        if arr[left] <= arr[mid]:
            if arr[left] <= target < arr[mid]:
                right = mid - 1
            else:
                left = mid + 1
        # Right half is sorted
        else:
            if arr[mid] < target <= arr[right]:
                left = mid + 1
            else:
                right = mid - 1
    return -1
```

## Interpolation Search

**Mechanism**: Estimates position based on value distribution (like searching a dictionary).

**Complexity**:
- Average: O(log log n) for uniformly distributed data
- Worst: O(n) for non-uniform distribution

**Best for**: Uniformly distributed sorted data.

```python
def interpolation_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right and arr[left] <= target <= arr[right]:
        if arr[left] == arr[right]:
            return left if arr[left] == target else -1
        # Estimate position
        pos = left + ((target - arr[left]) * (right - left)) // (arr[right] - arr[left])
        if arr[pos] == target:
            return pos
        elif arr[pos] < target:
            left = pos + 1
        else:
            right = pos - 1
    return -1
```

## Exponential Search

**Mechanism**: Find range where element exists, then binary search within that range.

**Complexity**: O(log n)

**Best for**: Unbounded/infinite arrays or when element is near the beginning.

```python
def exponential_search(arr, target):
    if arr[0] == target:
        return 0

    # Find range
    bound = 1
    while bound < len(arr) and arr[bound] <= target:
        bound *= 2

    # Binary search in range
    left = bound // 2
    right = min(bound, len(arr) - 1)
    return binary_search_range(arr, target, left, right)
```

## Jump Search

**Mechanism**: Jump ahead by fixed steps, then linear search within block.

**Complexity**: O(sqrt(n))

**Best for**: When binary search is too complex or data is on slow media.

```python
import math

def jump_search(arr, target):
    n = len(arr)
    step = int(math.sqrt(n))
    prev = 0

    # Jump to find block
    while arr[min(step, n) - 1] < target:
        prev = step
        step += int(math.sqrt(n))
        if prev >= n:
            return -1

    # Linear search in block
    while arr[prev] < target:
        prev += 1
        if prev == min(step, n):
            return -1

    return prev if arr[prev] == target else -1
```

## Ternary Search

**Mechanism**: Divide array into three parts instead of two.

**Complexity**: O(log3 n) - actually slower than binary search due to more comparisons.

**Use case**: Finding maximum/minimum of unimodal function.

```python
def ternary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid1 = left + (right - left) // 3
        mid2 = right - (right - left) // 3
        if arr[mid1] == target:
            return mid1
        if arr[mid2] == target:
            return mid2
        if target < arr[mid1]:
            right = mid1 - 1
        elif target > arr[mid2]:
            left = mid2 + 1
        else:
            left = mid1 + 1
            right = mid2 - 1
    return -1
```

## Comparison Table

| Algorithm | Time | Space | Sorted Required | Best Use Case |
|-----------|------|-------|-----------------|---------------|
| Linear | O(n) | O(1) | No | Unsorted, small data |
| Binary | O(log n) | O(1) | Yes | General sorted search |
| Interpolation | O(log log n) | O(1) | Yes | Uniform distribution |
| Exponential | O(log n) | O(1) | Yes | Unbounded arrays |
| Jump | O(sqrt n) | O(1) | Yes | Slow random access |
| Ternary | O(log n) | O(1) | Yes | Unimodal functions |

## Common Interview Patterns

1. **Binary search on answer**: Search for optimal value (min/max) that satisfies condition
2. **Two pointers**: Search for pair with given sum
3. **Matrix search**: Search in row-wise and column-wise sorted matrix
4. **Peak finding**: Find local maximum in array
5. **Minimum in rotated array**: Find rotation point
