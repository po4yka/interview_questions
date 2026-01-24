---
id: cs-ds-trees
title: Tree Data Structures
topic: data_structures
difficulty: hard
tags:
- cs_data_structures
- trees
- bst
anki_cards:
- slug: cs-ds-trees-0-en
  language: en
  anki_id: 1769160677425
  synced_at: '2026-01-23T13:31:19.007610'
- slug: cs-ds-trees-0-ru
  language: ru
  anki_id: 1769160677450
  synced_at: '2026-01-23T13:31:19.009040'
- slug: cs-ds-trees-1-en
  language: en
  anki_id: 1769160677475
  synced_at: '2026-01-23T13:31:19.010208'
- slug: cs-ds-trees-1-ru
  language: ru
  anki_id: 1769160677500
  synced_at: '2026-01-23T13:31:19.011441'
- slug: cs-ds-trees-2-en
  language: en
  anki_id: 1769160677525
  synced_at: '2026-01-23T13:31:19.012731'
- slug: cs-ds-trees-2-ru
  language: ru
  anki_id: 1769160677549
  synced_at: '2026-01-23T13:31:19.014083'
- slug: cs-ds-trees-3-en
  language: en
  anki_id: 1769160677574
  synced_at: '2026-01-23T13:31:19.015523'
- slug: cs-ds-trees-3-ru
  language: ru
  anki_id: 1769160677600
  synced_at: '2026-01-23T13:31:19.016997'
---
# Tree Data Structures

## Tree Basics

**Tree**: Hierarchical structure with nodes connected by edges.

**Terminology**:
- **Root**: Top node (no parent)
- **Leaf**: Node with no children
- **Height**: Longest path from node to leaf
- **Depth**: Distance from root to node
- **Subtree**: Tree formed by node and descendants

## Binary Trees

Each node has at most two children (left and right).

```python
class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None
```

### Tree Traversals

**Depth-First Traversals**:

```python
# Inorder (Left, Root, Right) - BST gives sorted order
def inorder(root):
    if root:
        inorder(root.left)
        print(root.val)
        inorder(root.right)

# Preorder (Root, Left, Right) - Copy tree
def preorder(root):
    if root:
        print(root.val)
        preorder(root.left)
        preorder(root.right)

# Postorder (Left, Right, Root) - Delete tree
def postorder(root):
    if root:
        postorder(root.left)
        postorder(root.right)
        print(root.val)
```

**Breadth-First (Level Order)**:

```python
from collections import deque

def level_order(root):
    if not root:
        return []
    result = []
    queue = deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)
    return result
```

## Binary Search Tree (BST)

**Property**: For every node, left subtree values < node value < right subtree values.

### Operations

```python
class BST:
    def __init__(self):
        self.root = None

    def insert(self, val):
        self.root = self._insert(self.root, val)

    def _insert(self, node, val):
        if not node:
            return TreeNode(val)
        if val < node.val:
            node.left = self._insert(node.left, val)
        else:
            node.right = self._insert(node.right, val)
        return node

    def search(self, val):
        return self._search(self.root, val)

    def _search(self, node, val):
        if not node or node.val == val:
            return node
        if val < node.val:
            return self._search(node.left, val)
        return self._search(node.right, val)

    def delete(self, val):
        self.root = self._delete(self.root, val)

    def _delete(self, node, val):
        if not node:
            return None
        if val < node.val:
            node.left = self._delete(node.left, val)
        elif val > node.val:
            node.right = self._delete(node.right, val)
        else:
            # Node found
            if not node.left:
                return node.right
            if not node.right:
                return node.left
            # Two children: replace with inorder successor
            successor = self._min_node(node.right)
            node.val = successor.val
            node.right = self._delete(node.right, successor.val)
        return node

    def _min_node(self, node):
        while node.left:
            node = node.left
        return node
```

### BST Complexity

| Operation | Average | Worst (unbalanced) |
|-----------|---------|-------------------|
| Search | O(log n) | O(n) |
| Insert | O(log n) | O(n) |
| Delete | O(log n) | O(n) |

## Self-Balancing BSTs

### AVL Tree

**Property**: Heights of left and right subtrees differ by at most 1.

**Balance factor** = height(left) - height(right), must be in {-1, 0, 1}.

**Rotations**:
- **Left rotation**: Right child becomes parent
- **Right rotation**: Left child becomes parent
- **Left-Right**: Left rotation on left child, then right rotation
- **Right-Left**: Right rotation on right child, then left rotation

**Complexity**: All operations O(log n) guaranteed.

### Red-Black Tree

**Properties**:
1. Every node is red or black
2. Root is black
3. Leaves (NIL) are black
4. Red node children are black
5. All paths from node to leaves have same black count

**Advantage over AVL**: Fewer rotations on insert/delete.

**Use cases**: Java TreeMap, C++ map/set.

### Comparison

| Tree | Balance | Rotations | Use Case |
|------|---------|-----------|----------|
| AVL | Strict | More | Frequent reads |
| Red-Black | Relaxed | Fewer | Frequent writes |

## B-Trees and B+ Trees

### B-Tree

**Properties**:
- Node can have M children (M = order)
- Internal nodes have ceil(M/2) to M children
- All leaves at same depth
- Keys in node are sorted

**Complexity**: O(log n) for all operations.

**Use case**: Databases, file systems (minimize disk I/O).

### B+ Tree

**Difference from B-tree**:
- All data in leaf nodes
- Leaf nodes linked (efficient range queries)
- Internal nodes only store keys

**Use case**: Database indexes, sequential access patterns.

## Trie (Prefix Tree)

Tree for storing strings where each node represents a character.

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True

    def search(self, word):
        node = self._find_node(word)
        return node is not None and node.is_end

    def starts_with(self, prefix):
        return self._find_node(prefix) is not None

    def _find_node(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node
```

**Complexity**:
- Insert: O(m) where m is word length
- Search: O(m)
- Space: O(alphabet_size * m * n) where n is number of words

**Use cases**: Autocomplete, spell checking, IP routing (longest prefix match).

## Segment Tree

Tree for range queries and point updates.

```python
class SegmentTree:
    def __init__(self, arr):
        self.n = len(arr)
        self.tree = [0] * (4 * self.n)
        self._build(arr, 0, 0, self.n - 1)

    def _build(self, arr, node, start, end):
        if start == end:
            self.tree[node] = arr[start]
        else:
            mid = (start + end) // 2
            self._build(arr, 2*node+1, start, mid)
            self._build(arr, 2*node+2, mid+1, end)
            self.tree[node] = self.tree[2*node+1] + self.tree[2*node+2]

    def update(self, idx, val):
        self._update(0, 0, self.n-1, idx, val)

    def _update(self, node, start, end, idx, val):
        if start == end:
            self.tree[node] = val
        else:
            mid = (start + end) // 2
            if idx <= mid:
                self._update(2*node+1, start, mid, idx, val)
            else:
                self._update(2*node+2, mid+1, end, idx, val)
            self.tree[node] = self.tree[2*node+1] + self.tree[2*node+2]

    def query(self, left, right):
        return self._query(0, 0, self.n-1, left, right)

    def _query(self, node, start, end, left, right):
        if right < start or end < left:
            return 0
        if left <= start and end <= right:
            return self.tree[node]
        mid = (start + end) // 2
        return (self._query(2*node+1, start, mid, left, right) +
                self._query(2*node+2, mid+1, end, left, right))
```

**Complexity**: O(log n) for query and update.

**Use cases**: Range sum/min/max queries, interval scheduling.

## Fenwick Tree (Binary Indexed Tree)

Space-efficient structure for prefix sums and point updates.

```python
class FenwickTree:
    def __init__(self, n):
        self.n = n
        self.tree = [0] * (n + 1)

    def update(self, i, delta):
        i += 1  # 1-indexed
        while i <= self.n:
            self.tree[i] += delta
            i += i & (-i)  # Add LSB

    def prefix_sum(self, i):
        i += 1
        total = 0
        while i > 0:
            total += self.tree[i]
            i -= i & (-i)  # Remove LSB
        return total

    def range_sum(self, left, right):
        return self.prefix_sum(right) - self.prefix_sum(left - 1)
```

**Complexity**: O(log n) for update and query.

**Advantage over Segment Tree**: Less memory, simpler code.

## Tree Selection Guide

| Structure | Use Case |
|-----------|----------|
| BST | General ordered operations |
| AVL | Frequent lookups |
| Red-Black | Frequent insertions/deletions |
| B-Tree | Database indexes |
| Trie | String operations |
| Segment Tree | Range queries |
| Fenwick Tree | Prefix sums |
