---
id: cs-ds-heaps
title: Heaps and Priority Queues
topic: data_structures
difficulty: medium
tags:
- cs_data_structures
- heaps
- priority_queue
anki_cards:
- slug: cs-ds-heaps-0-en
  language: en
  anki_id: 1769160678526
  synced_at: '2026-01-23T13:31:19.079421'
- slug: cs-ds-heaps-0-ru
  language: ru
  anki_id: 1769160678549
  synced_at: '2026-01-23T13:31:19.081758'
- slug: cs-ds-heaps-1-en
  language: en
  anki_id: 1769160678576
  synced_at: '2026-01-23T13:31:19.085385'
- slug: cs-ds-heaps-1-ru
  language: ru
  anki_id: 1769160678599
  synced_at: '2026-01-23T13:31:19.088412'
- slug: cs-ds-heaps-2-en
  language: en
  anki_id: 1769160678624
  synced_at: '2026-01-23T13:31:19.090503'
- slug: cs-ds-heaps-2-ru
  language: ru
  anki_id: 1769160678649
  synced_at: '2026-01-23T13:31:19.092688'
---
# Heaps and Priority Queues

## Heap Basics

**Heap**: Complete binary tree satisfying heap property.

**Types**:
- **Max-heap**: Parent >= children (root is maximum)
- **Min-heap**: Parent <= children (root is minimum)

**Complete binary tree**: All levels filled except possibly last, which is filled left to right.

### Array Representation

For node at index i:
- Parent: (i - 1) // 2
- Left child: 2*i + 1
- Right child: 2*i + 2

```
        10 (index 0)
       /  \
      5    3 (indices 1, 2)
     / \   /
    2   4 1 (indices 3, 4, 5)

Array: [10, 5, 3, 2, 4, 1]
```

## Heap Operations

### Min-Heap Implementation

```python
class MinHeap:
    def __init__(self):
        self.heap = []

    def parent(self, i):
        return (i - 1) // 2

    def left_child(self, i):
        return 2 * i + 1

    def right_child(self, i):
        return 2 * i + 2

    def swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]

    def insert(self, val):
        self.heap.append(val)
        self._sift_up(len(self.heap) - 1)

    def _sift_up(self, i):
        while i > 0 and self.heap[self.parent(i)] > self.heap[i]:
            self.swap(i, self.parent(i))
            i = self.parent(i)

    def extract_min(self):
        if not self.heap:
            raise IndexError("Heap empty")
        min_val = self.heap[0]
        self.heap[0] = self.heap[-1]
        self.heap.pop()
        if self.heap:
            self._sift_down(0)
        return min_val

    def _sift_down(self, i):
        min_idx = i
        left = self.left_child(i)
        right = self.right_child(i)

        if left < len(self.heap) and self.heap[left] < self.heap[min_idx]:
            min_idx = left
        if right < len(self.heap) and self.heap[right] < self.heap[min_idx]:
            min_idx = right

        if min_idx != i:
            self.swap(i, min_idx)
            self._sift_down(min_idx)

    def peek(self):
        if not self.heap:
            raise IndexError("Heap empty")
        return self.heap[0]

    def __len__(self):
        return len(self.heap)
```

### Complexity

| Operation | Time |
|-----------|------|
| Insert | O(log n) |
| Extract min/max | O(log n) |
| Peek | O(1) |
| Build heap | O(n) |
| Delete arbitrary | O(log n)* |

*With index tracking

## Build Heap (Heapify)

Convert array to heap in O(n) time.

```python
def heapify(arr):
    n = len(arr)
    # Start from last non-leaf node
    for i in range(n // 2 - 1, -1, -1):
        sift_down(arr, n, i)

def sift_down(arr, n, i):
    smallest = i
    left = 2 * i + 1
    right = 2 * i + 2

    if left < n and arr[left] < arr[smallest]:
        smallest = left
    if right < n and arr[right] < arr[smallest]:
        smallest = right

    if smallest != i:
        arr[i], arr[smallest] = arr[smallest], arr[i]
        sift_down(arr, n, smallest)
```

**Why O(n)?** Most nodes are near bottom with short sift paths.

## Python heapq Module

```python
import heapq

# Create heap from list
nums = [3, 1, 4, 1, 5, 9]
heapq.heapify(nums)  # In-place, O(n)

# Insert
heapq.heappush(nums, 2)  # O(log n)

# Extract minimum
min_val = heapq.heappop(nums)  # O(log n)

# Peek minimum
min_val = nums[0]  # O(1)

# Push and pop in one operation
result = heapq.heappushpop(nums, 6)  # More efficient

# Pop and push
result = heapq.heapreplace(nums, 6)  # Pop first, then push

# Get k smallest/largest
smallest = heapq.nsmallest(3, nums)  # O(n + k log n)
largest = heapq.nlargest(3, nums)
```

### Max-Heap in Python

Python's heapq is min-heap only. Negate values for max-heap:

```python
import heapq

class MaxHeap:
    def __init__(self):
        self.heap = []

    def push(self, val):
        heapq.heappush(self.heap, -val)

    def pop(self):
        return -heapq.heappop(self.heap)

    def peek(self):
        return -self.heap[0]
```

### Heap with Custom Objects

Use tuples (priority, item) or implement __lt__:

```python
import heapq

# Tuple approach
tasks = []
heapq.heappush(tasks, (1, "low priority"))
heapq.heappush(tasks, (0, "high priority"))

# Class approach
class Task:
    def __init__(self, priority, name):
        self.priority = priority
        self.name = name

    def __lt__(self, other):
        return self.priority < other.priority
```

## Priority Queue

ADT that dequeues elements by priority rather than arrival order.

**Implementation options**:
| Implementation | Insert | Extract | Peek |
|----------------|--------|---------|------|
| Unsorted array | O(1) | O(n) | O(n) |
| Sorted array | O(n) | O(1) | O(1) |
| Heap | O(log n) | O(log n) | O(1) |

Heap is best for balanced operations.

## Common Applications

### 1. HeapSort

```python
def heapsort(arr):
    heapq.heapify(arr)
    return [heapq.heappop(arr) for _ in range(len(arr))]
```

Time: O(n log n), Space: O(1) if in-place.

### 2. K Largest/Smallest Elements

```python
def k_largest(nums, k):
    # Use min-heap of size k
    heap = nums[:k]
    heapq.heapify(heap)

    for num in nums[k:]:
        if num > heap[0]:
            heapq.heapreplace(heap, num)

    return heap
```

Time: O(n log k).

### 3. Merge K Sorted Lists

```python
def merge_k_lists(lists):
    heap = []
    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst[0], i, 0))

    result = []
    while heap:
        val, list_idx, elem_idx = heapq.heappop(heap)
        result.append(val)

        if elem_idx + 1 < len(lists[list_idx]):
            next_val = lists[list_idx][elem_idx + 1]
            heapq.heappush(heap, (next_val, list_idx, elem_idx + 1))

    return result
```

Time: O(n log k) where n is total elements, k is number of lists.

### 4. Median Finder (Two Heaps)

```python
class MedianFinder:
    def __init__(self):
        self.small = []  # Max-heap (negated)
        self.large = []  # Min-heap

    def add_num(self, num):
        heapq.heappush(self.small, -num)
        heapq.heappush(self.large, -heapq.heappop(self.small))

        if len(self.large) > len(self.small):
            heapq.heappush(self.small, -heapq.heappop(self.large))

    def find_median(self):
        if len(self.small) > len(self.large):
            return -self.small[0]
        return (-self.small[0] + self.large[0]) / 2
```

### 5. Dijkstra's Algorithm

Priority queue for selecting minimum distance vertex.

### 6. Task Scheduling

```python
def schedule_tasks(tasks, cooldown):
    freq = {}
    for task in tasks:
        freq[task] = freq.get(task, 0) + 1

    heap = [-count for count in freq.values()]
    heapq.heapify(heap)

    time = 0
    while heap:
        cycle = []
        for _ in range(cooldown + 1):
            if heap:
                cycle.append(heapq.heappop(heap))
            time += 1
            if not heap and not any(c < -1 for c in cycle):
                break

        for count in cycle:
            if count < -1:
                heapq.heappush(heap, count + 1)

    return time
```

## Heap vs BST

| Aspect | Heap | BST |
|--------|------|-----|
| Find min/max | O(1) | O(log n) |
| Insert | O(log n) | O(log n) |
| Delete min/max | O(log n) | O(log n) |
| Search arbitrary | O(n) | O(log n) |
| Memory | Array | Pointers |
| Cache locality | Better | Worse |

**Use heap when** only need min/max operations.
**Use BST when** need to search for arbitrary elements.

## Advanced Heap Variants

### Fibonacci Heap

- Decrease key: O(1) amortized
- Used in optimal Dijkstra's algorithm

### Binomial Heap

- Merge: O(log n)
- Useful when frequent merging needed
