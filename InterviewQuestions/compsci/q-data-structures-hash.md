---
id: cs-ds-hash
title: Hash Tables
topic: data_structures
difficulty: medium
tags:
- cs_data_structures
- hash_tables
anki_cards:
- slug: cs-ds-hash-0-en
  language: en
  anki_id: 1769160673678
  synced_at: '2026-01-23T13:31:18.752856'
- slug: cs-ds-hash-0-ru
  language: ru
  anki_id: 1769160673700
  synced_at: '2026-01-23T13:31:18.756822'
- slug: cs-ds-hash-1-en
  language: en
  anki_id: 1769160673724
  synced_at: '2026-01-23T13:31:18.758621'
- slug: cs-ds-hash-1-ru
  language: ru
  anki_id: 1769160673749
  synced_at: '2026-01-23T13:31:18.759982'
- slug: cs-ds-hash-2-en
  language: en
  anki_id: 1769160673774
  synced_at: '2026-01-23T13:31:18.761448'
- slug: cs-ds-hash-2-ru
  language: ru
  anki_id: 1769160673799
  synced_at: '2026-01-23T13:31:18.764481'
---
# Hash Tables

## Overview

**Hash table** (hash map) stores key-value pairs with O(1) average access using a hash function.

**Components**:
1. **Array**: Stores values (or buckets)
2. **Hash function**: Maps keys to array indices
3. **Collision resolution**: Handles when keys map to same index

## Hash Functions

**Goal**: Uniformly distribute keys across array indices.

**Properties of good hash function**:
- Deterministic (same key = same hash)
- Uniform distribution
- Fast to compute
- Minimize collisions

### Common Hash Functions

**Division method**: h(k) = k mod m

```python
def hash_division(key, table_size):
    return key % table_size
```

**Multiplication method**: h(k) = floor(m * (k*A mod 1)) where 0 < A < 1

**String hashing** (polynomial rolling hash):

```python
def hash_string(s, table_size):
    hash_val = 0
    base = 31
    for char in s:
        hash_val = (hash_val * base + ord(char)) % table_size
    return hash_val
```

### Table Size

Prime numbers reduce clustering. Common choices: 31, 61, 127, 8191.

## Collision Resolution

### 1. Chaining (Separate Chaining)

Each bucket contains a linked list of entries.

```python
class HashTableChaining:
    def __init__(self, size=101):
        self.size = size
        self.table = [[] for _ in range(size)]

    def _hash(self, key):
        return hash(key) % self.size

    def put(self, key, value):
        idx = self._hash(key)
        for i, (k, v) in enumerate(self.table[idx]):
            if k == key:
                self.table[idx][i] = (key, value)
                return
        self.table[idx].append((key, value))

    def get(self, key):
        idx = self._hash(key)
        for k, v in self.table[idx]:
            if k == key:
                return v
        raise KeyError(key)

    def delete(self, key):
        idx = self._hash(key)
        for i, (k, v) in enumerate(self.table[idx]):
            if k == key:
                del self.table[idx][i]
                return
        raise KeyError(key)
```

**Pros**: Simple, handles high load factor
**Cons**: Extra memory for links, poor cache locality

### 2. Open Addressing

All entries stored in array itself. Probe for next available slot on collision.

**Linear probing**: h(k, i) = (h(k) + i) mod m

```python
class HashTableLinearProbing:
    def __init__(self, size=101):
        self.size = size
        self.keys = [None] * size
        self.values = [None] * size
        self.deleted = [False] * size

    def _hash(self, key):
        return hash(key) % self.size

    def put(self, key, value):
        idx = self._hash(key)
        start = idx
        while self.keys[idx] is not None and self.keys[idx] != key:
            if self.deleted[idx]:
                break
            idx = (idx + 1) % self.size
            if idx == start:
                raise OverflowError("Hash table full")
        self.keys[idx] = key
        self.values[idx] = value
        self.deleted[idx] = False

    def get(self, key):
        idx = self._hash(key)
        start = idx
        while self.keys[idx] is not None or self.deleted[idx]:
            if self.keys[idx] == key and not self.deleted[idx]:
                return self.values[idx]
            idx = (idx + 1) % self.size
            if idx == start:
                break
        raise KeyError(key)

    def delete(self, key):
        idx = self._hash(key)
        start = idx
        while self.keys[idx] is not None or self.deleted[idx]:
            if self.keys[idx] == key and not self.deleted[idx]:
                self.deleted[idx] = True
                return
            idx = (idx + 1) % self.size
            if idx == start:
                break
        raise KeyError(key)
```

**Problem**: Primary clustering (long runs of occupied slots).

**Quadratic probing**: h(k, i) = (h(k) + c1*i + c2*i^2) mod m

Reduces primary clustering but can cause secondary clustering.

**Double hashing**: h(k, i) = (h1(k) + i*h2(k)) mod m

Best distribution but more computation.

### Comparison

| Method | Search | Insert | Delete | Space |
|--------|--------|--------|--------|-------|
| Chaining | O(1 + alpha) | O(1) | O(1 + alpha) | O(n + m) |
| Linear probing | O(1/(1-alpha)) | O(1/(1-alpha)) | Complex | O(m) |
| Double hashing | O(1/(1-alpha)) | O(1/(1-alpha)) | Complex | O(m) |

alpha = load factor = n/m

## Load Factor and Resizing

**Load factor**: alpha = number of entries / table size

**Thresholds**:
- Chaining: Resize when alpha > 0.75-1.0
- Open addressing: Resize when alpha > 0.5-0.7

**Resizing**: Create new array (typically 2x), rehash all entries.

```python
def _resize(self, new_size):
    old_table = self.table
    self.size = new_size
    self.table = [[] for _ in range(new_size)]
    for bucket in old_table:
        for key, value in bucket:
            self.put(key, value)
```

## Complexity Analysis

| Operation | Average | Worst Case |
|-----------|---------|------------|
| Insert | O(1) | O(n) |
| Search | O(1) | O(n) |
| Delete | O(1) | O(n) |

Worst case occurs with poor hash function or many collisions.

## Hash Set

Hash table storing only keys (no values).

```python
class HashSet:
    def __init__(self):
        self.map = {}

    def add(self, key):
        self.map[key] = True

    def contains(self, key):
        return key in self.map

    def remove(self, key):
        if key in self.map:
            del self.map[key]
```

## Common Applications

1. **Dictionaries/Maps**: Key-value storage
2. **Caches**: LRU cache (hash map + doubly linked list)
3. **Deduplication**: Remove duplicates
4. **Counting**: Frequency maps
5. **Symbol tables**: Compilers, interpreters
6. **Database indexes**: Hash indexes

## Interview Patterns

### Two Sum

```python
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
```

### Group Anagrams

```python
def group_anagrams(strs):
    groups = {}
    for s in strs:
        key = tuple(sorted(s))
        groups.setdefault(key, []).append(s)
    return list(groups.values())
```

### LRU Cache

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
```

## Hash Table vs Other Structures

| Structure | Search | Insert | Ordered | Use Case |
|-----------|--------|--------|---------|----------|
| Hash Table | O(1) | O(1) | No | Fast lookup |
| BST | O(log n) | O(log n) | Yes | Sorted data |
| Array | O(n) | O(n) | Yes | Sequential access |
| Sorted Array | O(log n) | O(n) | Yes | Static data |

## Common Mistakes

1. **Mutable keys**: Using mutable objects as keys (lists, dicts)
2. **Poor hash function**: Causes clustering and O(n) performance
3. **Ignoring load factor**: Not resizing when table gets full
4. **Thread safety**: Hash tables not thread-safe by default
