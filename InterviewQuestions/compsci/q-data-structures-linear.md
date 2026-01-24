---
id: cs-ds-linear
title: Linear Data Structures
topic: data_structures
difficulty: medium
tags:
- cs_data_structures
- arrays
- linked_lists
- stacks
- queues
anki_cards:
- slug: cs-ds-linear-0-en
  language: en
  anki_id: 1769160676124
  synced_at: '2026-01-23T13:31:18.914381'
- slug: cs-ds-linear-0-ru
  language: ru
  anki_id: 1769160676150
  synced_at: '2026-01-23T13:31:18.915966'
- slug: cs-ds-linear-1-en
  language: en
  anki_id: 1769160676174
  synced_at: '2026-01-23T13:31:18.917417'
- slug: cs-ds-linear-1-ru
  language: ru
  anki_id: 1769160676200
  synced_at: '2026-01-23T13:31:18.918849'
- slug: cs-ds-linear-2-en
  language: en
  anki_id: 1769160676224
  synced_at: '2026-01-23T13:31:18.921846'
- slug: cs-ds-linear-2-ru
  language: ru
  anki_id: 1769160676250
  synced_at: '2026-01-23T13:31:18.923238'
- slug: cs-ds-linear-3-en
  language: en
  anki_id: 1769160676275
  synced_at: '2026-01-23T13:31:18.924577'
- slug: cs-ds-linear-3-ru
  language: ru
  anki_id: 1769160676299
  synced_at: '2026-01-23T13:31:18.927267'
---
# Linear Data Structures

## Arrays

### Static Arrays

Fixed-size contiguous memory block.

**Complexity**:
| Operation | Time |
|-----------|------|
| Access | O(1) |
| Search | O(n) |
| Insert/Delete at end | O(1) |
| Insert/Delete at arbitrary | O(n) |

**Memory**: Contiguous allocation enables cache-friendly access.

### Dynamic Arrays (ArrayList, Vector)

Resizable array that grows when capacity exceeded.

**Growth strategy**: Typically doubles capacity (amortized O(1) append).

```python
class DynamicArray:
    def __init__(self):
        self.capacity = 1
        self.size = 0
        self.data = [None] * self.capacity

    def append(self, item):
        if self.size == self.capacity:
            self._resize(2 * self.capacity)
        self.data[self.size] = item
        self.size += 1

    def _resize(self, new_capacity):
        new_data = [None] * new_capacity
        for i in range(self.size):
            new_data[i] = self.data[i]
        self.data = new_data
        self.capacity = new_capacity
```

**Amortized analysis**: n appends cost O(n) total, so O(1) per append.

## Linked Lists

### Singly Linked List

Each node points to next node.

```python
class Node:
    def __init__(self, val):
        self.val = val
        self.next = None

class SinglyLinkedList:
    def __init__(self):
        self.head = None

    def prepend(self, val):  # O(1)
        node = Node(val)
        node.next = self.head
        self.head = node

    def append(self, val):  # O(n) without tail pointer
        node = Node(val)
        if not self.head:
            self.head = node
            return
        curr = self.head
        while curr.next:
            curr = curr.next
        curr.next = node

    def delete(self, val):  # O(n)
        if not self.head:
            return
        if self.head.val == val:
            self.head = self.head.next
            return
        curr = self.head
        while curr.next and curr.next.val != val:
            curr = curr.next
        if curr.next:
            curr.next = curr.next.next
```

### Doubly Linked List

Each node points to both next and previous.

```python
class DNode:
    def __init__(self, val):
        self.val = val
        self.prev = None
        self.next = None

class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def append(self, val):  # O(1) with tail pointer
        node = DNode(val)
        if not self.tail:
            self.head = self.tail = node
        else:
            node.prev = self.tail
            self.tail.next = node
            self.tail = node

    def delete(self, node):  # O(1) given node reference
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
```

### Circular Linked List

Last node points back to first node.

**Use cases**: Round-robin scheduling, circular buffers.

### Array vs Linked List

| Operation | Array | Linked List |
|-----------|-------|-------------|
| Access by index | O(1) | O(n) |
| Insert at beginning | O(n) | O(1) |
| Insert at end | O(1)* | O(1)** |
| Insert at middle | O(n) | O(1)*** |
| Memory | Contiguous | Scattered |
| Cache performance | Good | Poor |

*Amortized for dynamic array
**With tail pointer
***Given node reference

## Stacks

**LIFO** (Last In, First Out) structure.

### Operations

| Operation | Description | Time |
|-----------|-------------|------|
| push(x) | Add to top | O(1) |
| pop() | Remove from top | O(1) |
| peek/top() | View top element | O(1) |
| isEmpty() | Check if empty | O(1) |

### Implementation

```python
class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if self.is_empty():
            raise IndexError("Stack empty")
        return self.items.pop()

    def peek(self):
        if self.is_empty():
            raise IndexError("Stack empty")
        return self.items[-1]

    def is_empty(self):
        return len(self.items) == 0
```

### Applications

1. **Function call stack**: Recursion, local variables
2. **Expression evaluation**: Infix to postfix, calculator
3. **Parentheses matching**: Valid brackets problem
4. **Undo mechanism**: Text editors
5. **DFS traversal**: Graph/tree exploration
6. **Backtracking**: Maze solving, N-queens

### Monotonic Stack

Stack maintaining monotonic order (increasing or decreasing).

**Use case**: Next greater element problem.

```python
def next_greater_element(nums):
    n = len(nums)
    result = [-1] * n
    stack = []  # Stores indices

    for i in range(n):
        while stack and nums[i] > nums[stack[-1]]:
            idx = stack.pop()
            result[idx] = nums[i]
        stack.append(i)

    return result
```

## Queues

**FIFO** (First In, First Out) structure.

### Operations

| Operation | Description | Time |
|-----------|-------------|------|
| enqueue(x) | Add to back | O(1) |
| dequeue() | Remove from front | O(1) |
| front/peek() | View front element | O(1) |
| isEmpty() | Check if empty | O(1) |

### Implementation with Circular Array

```python
class CircularQueue:
    def __init__(self, capacity):
        self.data = [None] * capacity
        self.capacity = capacity
        self.front = 0
        self.size = 0

    def enqueue(self, item):
        if self.size == self.capacity:
            raise OverflowError("Queue full")
        rear = (self.front + self.size) % self.capacity
        self.data[rear] = item
        self.size += 1

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Queue empty")
        item = self.data[self.front]
        self.front = (self.front + 1) % self.capacity
        self.size -= 1
        return item

    def is_empty(self):
        return self.size == 0
```

### Applications

1. **BFS traversal**: Level-order, shortest path
2. **Task scheduling**: Job queues, print spooler
3. **Buffering**: I/O buffers, streaming
4. **Message queues**: Producer-consumer pattern

## Deque (Double-Ended Queue)

Insert and remove from both ends in O(1).

```python
from collections import deque

d = deque()
d.append(1)       # Add to right
d.appendleft(2)   # Add to left
d.pop()           # Remove from right
d.popleft()       # Remove from left
```

**Use cases**: Sliding window problems, palindrome check.

## Priority Queue

Elements have priorities; highest priority dequeued first.

**Implementation**: Typically uses heap (covered in heaps section).

| Operation | Time |
|-----------|------|
| Insert | O(log n) |
| Extract max/min | O(log n) |
| Peek max/min | O(1) |

## Comparison Summary

| Structure | Access | Insert | Delete | Use Case |
|-----------|--------|--------|--------|----------|
| Array | O(1) | O(n) | O(n) | Random access |
| Linked List | O(n) | O(1)* | O(1)* | Frequent insert/delete |
| Stack | O(n) | O(1) | O(1) | LIFO operations |
| Queue | O(n) | O(1) | O(1) | FIFO operations |
| Deque | O(n) | O(1) | O(1) | Both ends access |

*With reference to node
