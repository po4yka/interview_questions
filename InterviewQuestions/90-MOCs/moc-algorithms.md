---
id: ivm-20251012-140300
title: Algorithms — MOC
kind: moc
created: 2025-10-12
updated: 2025-10-18
tags: [moc, topic/algorithms]
date created: Saturday, October 18th 2025, 2:47:07 pm
date modified: Tuesday, November 25th 2025, 8:53:48 pm
---

# Algorithms — Map of Content

## Overview
This MOC covers algorithms, data structures, complexity analysis, algorithm design patterns, sorting and searching algorithms, graph algorithms, dynamic programming, and computational problem-solving techniques.

---

## Study Paths

### Beginner Path: Foundation Building

**Start here if:** You're new to algorithms or need to refresh fundamentals.

**Learning sequence:**

1. **Data Structures Overview** (Easy)
   - [[q-data-structures-overview--algorithms--easy]]
   - Understand arrays, lists, stacks, queues, trees, graphs, hash tables

2. **Arrays and Two Pointers** (Medium)
   - [[q-two-pointers-sliding-window--algorithms--medium]]
   - Master opposite ends, same direction, fast/slow patterns
   - Learn sliding window for substring/subarray problems

3. **Binary Search** (Medium)
   - [[q-binary-search-variants--algorithms--medium]]
   - Classic search, first/last occurrence, rotated arrays
   - Binary search on answer pattern

4. **Basic Sorting** (Medium)
   - [[q-sorting-algorithms-comparison--algorithms--medium]]
   - Quick Sort, Merge Sort, Insertion Sort
   - Understand time/space complexity trade-offs

**Goal:** Build intuition for O(n), O(log n), and O(n log n) algorithms. Recognize when to use each pattern.

---

### Intermediate Path: Advanced Techniques

**Prerequisites:** Comfortable with basic data structures and Big-O notation.

**Learning sequence:**

1. **Tree Algorithms** (Hard)
   - [[q-binary-search-trees-bst--algorithms--hard]]
   - BST operations, traversals (in-order, pre-order, post-order)
   - Balanced trees (AVL, Red-Black)

2. **Graph Fundamentals** (Hard)
   - [[q-graph-algorithms-bfs-dfs--algorithms--hard]]
   - BFS for shortest path, level-order traversal
   - DFS for topological sort, cycle detection
   - Dijkstra's algorithm for weighted graphs

3. **Dynamic Programming Basics** (Hard)
   - [[q-dynamic-programming-fundamentals--algorithms--hard]]
   - Fibonacci, climbing stairs, coin change
   - Top-down (memoization) vs bottom-up (tabulation)
   - 1D and 2D DP patterns

4. **Advanced Sorting** (Medium)
   - [[q-sorting-algorithms-comparison--algorithms--medium]]
   - Heap Sort, Counting Sort, Radix Sort
   - When to use non-comparison sorts

**Goal:** Master divide-and-conquer, recognize overlapping subproblems, understand graph representations.

---

### Advanced Path: Complex Algorithms

**Prerequisites:** Solid understanding of DP, graphs, and common patterns.

**Learning sequence:**

1. **Backtracking** (Hard)
   - [[q-backtracking-algorithms--algorithms--hard]]
   - N-Queens, Sudoku Solver, permutations, combinations
   - Constraint satisfaction problems
   - Optimization techniques: pruning, early termination

2. **Advanced Graph Algorithms** (Hard)
   - [[q-advanced-graph-algorithms--algorithms--hard]]
   - Strongly connected components
   - Minimum spanning trees (Kruskal, Prim)
   - Network flow algorithms

3. **Complex DP Patterns** (Hard)
   - [[q-dynamic-programming-fundamentals--algorithms--hard]]
   - 0/1 Knapsack, longest common subsequence (LCS)
   - Longest increasing subsequence (LIS)
   - Edit distance, interval DP

4. **Advanced Tree Structures** (Hard)
   - [[q-binary-search-trees-bst--algorithms--hard]]
   - Segment trees, Fenwick trees
   - Tries for string problems

**Goal:** Solve constraint satisfaction problems, design optimal solutions, handle complex state spaces.

---

## Common Algorithmic Patterns

### Pattern 1: Two Pointers

**When to use:**
- Array/string is sorted
- Finding pairs with target sum
- Removing duplicates in-place
- Palindrome checking
- Cycle detection in linked lists

**Time:** O(n) | **Space:** O(1)

**Key Problems:**
- [[q-two-pointers-sliding-window--algorithms--medium]]

**Variations:**
- Opposite ends: Two Sum II, Container with Most Water
- Same direction (fast/slow): Remove duplicates, move zeroes, Floyd's cycle detection

---

### Pattern 2: Sliding Window

**When to use:**
- Finding substring/subarray with condition
- "Longest/shortest/maximum" subarray problems
- "Contains all of" problems
- Consecutive elements matter

**Time:** O(n) | **Space:** O(k) for window state

**Key Problems:**
- [[q-two-pointers-sliding-window--algorithms--medium]]

**Variations:**
- Fixed-size window: Maximum sum subarray of size k
- Variable-size window: Longest substring without repeating characters, minimum window substring

---

### Pattern 3: Binary Search

**When to use:**
- Sorted array/list
- Finding target, first/last occurrence
- Search in rotated array
- Binary search on answer (min/max optimization)

**Time:** O(log n) | **Space:** O(1)

**Key Problems:**
- [[q-binary-search-variants--algorithms--medium]]

**Variations:**
- Classic search, first/last occurrence, insertion position
- Rotated sorted array, peak element
- Square root, search in 2D matrix
- Minimize/maximize pattern (Koko eating bananas)

---

### Pattern 4: BFS (Breadth-First Search)

**When to use:**
- Shortest path in unweighted graph
- Level-order traversal
- Connected components
- Layer-by-layer exploration

**Time:** O(V + E) | **Space:** O(V)

**Key Problems:**
- [[q-graph-algorithms-bfs-dfs--algorithms--hard]]

**Common applications:**
- Shortest path, word ladder, number of islands
- Social network connections, minimum jumps

---

### Pattern 5: DFS (Depth-First Search)

**When to use:**
- Topological sort
- Cycle detection
- Path finding (not necessarily shortest)
- Connected components
- Backtracking problems

**Time:** O(V + E) | **Space:** O(V) for recursion stack

**Key Problems:**
- [[q-graph-algorithms-bfs-dfs--algorithms--hard]]

**Common applications:**
- Course schedule, clone graph, word search
- Tree traversals, island counting

---

### Pattern 6: Dynamic Programming

**When to use:**
- Optimal substructure (optimal solution contains optimal subsolutions)
- Overlapping subproblems (same subproblems solved multiple times)
- Counting/optimization problems

**Time:** Varies (often O(n²) or O(n*m)) | **Space:** O(n) or O(n*m)

**Key Problems:**
- [[q-dynamic-programming-fundamentals--algorithms--hard]]

**Common patterns:**
- Linear DP: Fibonacci, climbing stairs, house robber
- Grid/2D DP: Knapsack, LCS, edit distance
- Interval DP: Longest palindromic substring
- State machine DP: Buy/sell stock problems

---

### Pattern 7: Backtracking

**When to use:**
- Generate all permutations/combinations/subsets
- Constraint satisfaction (N-Queens, Sudoku)
- Path finding with constraints
- Combinatorial search

**Time:** O(2^n) or O(n!) typically | **Space:** O(n) for recursion

**Key Problems:**
- [[q-backtracking-algorithms--algorithms--hard]]

**Template:** Make choice → Recurse → Backtrack (undo choice)

**Common applications:**
- Permutations, combinations, subsets, power set
- N-Queens, Sudoku Solver, word search
- Generate parentheses, palindrome partitioning

---

### Pattern 8: Sorting Algorithms

**When to use:** Depends on data characteristics

**Key Problems:**
- [[q-sorting-algorithms-comparison--algorithms--medium]]

**Decision guide:**
- Small array (< 20): Insertion Sort
- Nearly sorted: Insertion Sort (O(n) best case)
- Need stable + guaranteed O(n log n): Merge Sort
- General purpose: Quick Sort (average O(n log n))
- Limited space: Heap Sort (O(1) space)
- Integers with small range: Counting Sort (O(n + k))

---

### Pattern 9: Tree Traversal

**When to use:** Processing tree/binary tree nodes

**Key Problems:**
- [[q-binary-search-trees-bst--algorithms--hard]]

**Methods:**
- In-order (left, root, right): BST sorted order
- Pre-order (root, left, right): Copy tree structure
- Post-order (left, right, root): Delete tree, evaluate expression
- Level-order (BFS): Level-by-level processing

---

### Pattern 10: Greedy Algorithms

**When to use:**
- Local optimal choice leads to global optimum
- Activity selection, interval scheduling
- Huffman coding, Dijkstra's algorithm

**Time:** Varies | **Space:** O(1) typically

**Key Problems:**
- [[q-advanced-graph-algorithms--algorithms--hard]]

**Note:** Greedy doesn't always work - verify correctness!

---

## LeetCode Pattern Mapping

### Arrays & Hashing
- Two Sum, Contains Duplicate → Hash tables O(1) lookup
- [[q-two-pointers-sliding-window--algorithms--medium]]

### Two Pointers
- Two Sum II, 3Sum, Container with Most Water
- [[q-two-pointers-sliding-window--algorithms--medium]]

### Sliding Window
- Longest Substring Without Repeating, Minimum Window Substring
- [[q-two-pointers-sliding-window--algorithms--medium]]

### Binary Search
- Search in Rotated Array, Find Peak Element, Koko Eating Bananas
- [[q-binary-search-variants--algorithms--medium]]

### Stack
- Valid Parentheses, Daily Temperatures
- [[q-data-structures-overview--algorithms--easy]]

### Trees
- Invert Tree, Max Depth, Lowest Common Ancestor
- [[q-binary-search-trees-bst--algorithms--hard]]

### Graphs
- Number of Islands, Clone Graph, Course Schedule
- [[q-graph-algorithms-bfs-dfs--algorithms--hard]]

### Dynamic Programming
- Climbing Stairs, House Robber, Coin Change, LCS
- [[q-dynamic-programming-fundamentals--algorithms--hard]]

### Backtracking
- Subsets, Permutations, N-Queens, Word Search
- [[q-backtracking-algorithms--algorithms--hard]]

### Heap / Priority Queue
- Kth Largest Element, Merge K Sorted Lists
- [[q-sorting-algorithms-comparison--algorithms--medium]]

---

## By Difficulty

### Easy
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM "20-Algorithms"
WHERE difficulty = "easy"
SORT file.name ASC
LIMIT 50
```

### Medium
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM "20-Algorithms"
WHERE difficulty = "medium"
SORT file.name ASC
LIMIT 50
```

### Hard
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM "20-Algorithms"
WHERE difficulty = "hard"
SORT file.name ASC
LIMIT 50
```

## By Subtopic

### Data Structures

**Key Questions**:

#### Data Structures Fundamentals
- [[q-data-structures-overview--algorithms--easy]] - Comprehensive overview of arrays, lists, trees, graphs, heaps

**Core Concepts:**
- Arrays: O(1) access, O(n) insertion/deletion
- Linked Lists: O(1) insertion/deletion, O(n) access
- Stacks: LIFO, used for DFS, undo operations, expression evaluation
- Queues: FIFO, used for BFS, task scheduling
- Trees: Hierarchical data, BST provides O(log n) operations
- Graphs: Vertex-edge relationships, adjacency list/matrix
- Heaps: Priority queue, O(log n) insert/delete, O(1) min/max

**All Data Structure Questions:**
```dataview
TABLE difficulty, status
FROM "20-Algorithms"
WHERE contains(tags, "data-structures") OR contains(subtopics, "data-structures")
SORT difficulty ASC, file.name ASC
```

---

### Two Pointers & Sliding Window

**Key Questions**:
- [[q-two-pointers-sliding-window--algorithms--medium]] - Comprehensive guide to both patterns

**When to use Two Pointers:**
- Sorted array problems (Two Sum II)
- Palindrome checking (opposite ends)
- In-place modifications (remove duplicates)
- Cycle detection (fast & slow pointers)

**When to use Sliding Window:**
- Substring/subarray problems
- Fixed or variable window size
- "Longest/shortest/maximum" problems

**Complexity:** O(n) time, O(1) space typically

**All Questions:**
```dataview
TABLE difficulty, status
FROM "20-Algorithms"
WHERE contains(tags, "two-pointers") OR contains(tags, "sliding-window") OR contains(subtopics, "two-pointers") OR contains(subtopics, "sliding-window")
SORT difficulty ASC, file.name ASC
```

---

### Binary Search & Searching

**Key Questions**:
- [[q-binary-search-variants--algorithms--medium]] - All binary search patterns and variants

**Core Variants:**
1. Classic binary search (find exact target)
2. Find first/last occurrence (boundary search)
3. Search in rotated sorted array
4. Binary search on answer (optimization problems)
5. Peak element, square root

**Template patterns:**
- Exact match: `while (left <= right)`
- Find boundary: `while (left <= right)` + save result
- Minimize/maximize: `while (left < right)`

**Complexity:** O(log n) time, O(1) space

**All Searching Questions:**
```dataview
TABLE difficulty, status
FROM "20-Algorithms"
WHERE contains(tags, "binary-search") OR contains(tags, "searching") OR contains(subtopics, "searching")
SORT difficulty ASC, file.name ASC
```

---

### Sorting Algorithms

**Key Questions**:
- [[q-sorting-algorithms-comparison--algorithms--medium]] - Complete comparison of all major sorting algorithms

**Quick Reference:**
- Quick Sort: O(n log n) average, in-place, not stable
- Merge Sort: O(n log n) guaranteed, stable, O(n) space
- Heap Sort: O(n log n) guaranteed, in-place, not stable
- Insertion Sort: O(n²), best for small/nearly-sorted arrays
- Counting Sort: O(n+k) for limited integer ranges
- Radix Sort: O(nk) for fixed-length integers

**Decision tree:**
```
Small array → Insertion Sort
Nearly sorted → Insertion Sort
Need stable → Merge Sort or TimSort
General purpose → Quick Sort
Space limited → Heap Sort
Limited range integers → Counting Sort
```

**All Sorting Questions:**
```dataview
TABLE difficulty, status
FROM "20-Algorithms"
WHERE contains(tags, "sorting") OR contains(subtopics, "sorting")
SORT difficulty ASC, file.name ASC
```

---

### Graph Algorithms

**Key Questions**:
- [[q-graph-algorithms-bfs-dfs--algorithms--hard]] - BFS, DFS, and fundamental graph traversal
- [[q-advanced-graph-algorithms--algorithms--hard]] - Advanced techniques (MST, SCC, network flow)

**BFS (Breadth-First Search):**
- Use queue
- Level-by-level exploration
- Shortest path in unweighted graph
- Time: O(V + E), Space: O(V)

**DFS (Depth-First Search):**
- Use stack/recursion
- Go deep first
- Topological sort, cycle detection
- Time: O(V + E), Space: O(V)

**Advanced algorithms:**
- Dijkstra: Shortest path with weights
- Kruskal/Prim: Minimum spanning tree
- Topological sort: DAG ordering
- Kosaraju/Tarjan: Strongly connected components

**All Graph Questions:**
```dataview
TABLE difficulty, status
FROM "20-Algorithms"
WHERE contains(tags, "graphs") OR contains(tags, "bfs") OR contains(tags, "dfs") OR contains(subtopics, "graphs")
SORT difficulty ASC, file.name ASC
```

---

### Dynamic Programming

**Key Questions**:
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - Complete DP guide with all major patterns

**When to use DP:**
- Optimal substructure (optimal solution contains optimal subsolutions)
- Overlapping subproblems (same subproblems solved repeatedly)

**Common patterns:**
1. **Linear DP:** Fibonacci, climbing stairs, house robber
2. **Grid/2D DP:** Knapsack, LCS, edit distance
3. **Interval DP:** Longest palindromic substring
4. **State machine DP:** Buy/sell stock problems

**Approaches:**
- Top-down (memoization): Recursive with cache
- Bottom-up (tabulation): Iterative, fill table

**Classic problems:**
- Fibonacci, coin change, knapsack
- Longest common subsequence (LCS)
- Longest increasing subsequence (LIS)
- Edit distance, maximum subarray (Kadane)

**All DP Questions:**
```dataview
TABLE difficulty, status
FROM "20-Algorithms"
WHERE contains(tags, "dynamic-programming") OR contains(tags, "dp") OR contains(subtopics, "dynamic-programming")
SORT difficulty ASC, file.name ASC
```

---

### Tree Algorithms

**Key Questions**:
- [[q-binary-search-trees-bst--algorithms--hard]] - BST operations, traversals, balanced trees

**Tree Traversals:**
- In-order (left, root, right): BST gives sorted order
- Pre-order (root, left, right): Copy tree structure
- Post-order (left, right, root): Delete tree, evaluate expression
- Level-order (BFS): Process level by level

**Binary Search Tree:**
- Left < Root < Right property
- Search/Insert/Delete: O(log n) average, O(n) worst
- Balanced trees (AVL, Red-Black): O(log n) guaranteed

**Advanced structures:**
- Segment trees: Range queries
- Fenwick trees: Prefix sums
- Tries: String prefix matching

**All Tree Questions:**
```dataview
TABLE difficulty, status
FROM "20-Algorithms"
WHERE contains(tags, "trees") OR contains(tags, "binary-trees") OR contains(tags, "bst") OR contains(subtopics, "trees")
SORT difficulty ASC, file.name ASC
```

---

### Backtracking

**Key Questions**:
- [[q-backtracking-algorithms--algorithms--hard]] - N-Queens, Sudoku, permutations, combinations, subsets

**Template:**
```
1. Make choice
2. Recurse
3. Backtrack (undo choice)
```

**Common applications:**
- Generate all permutations/combinations/subsets
- Constraint satisfaction (N-Queens, Sudoku)
- Path finding with constraints (word search)
- Combinatorial optimization

**Time complexity:** Often O(2^n) or O(n!)
**Space complexity:** O(n) for recursion stack

**Optimization techniques:**
- Early termination
- Pruning with constraints
- Memoization

**All Backtracking Questions:**
```dataview
TABLE difficulty, status
FROM "20-Algorithms"
WHERE contains(tags, "backtracking") OR contains(subtopics, "backtracking")
SORT difficulty ASC, file.name ASC
```

---

### Complexity Analysis

**Understanding Big-O:**
- O(1): Constant - hash table access
- O(log n): Logarithmic - binary search
- O(n): Linear - single pass through array
- O(n log n): Linearithmic - merge sort, quick sort
- O(n²): Quadratic - nested loops, bubble sort
- O(2^n): Exponential - subsets, naive recursion
- O(n!): Factorial - permutations

**Space complexity:**
- In-place: O(1) extra space
- Recursive: O(depth) for call stack
- Memoization: O(states) for cache

**All Complexity Questions:**
```dataview
TABLE difficulty, status
FROM "20-Algorithms"
WHERE contains(tags, "complexity") OR contains(tags, "big-o") OR contains(tags, "time-complexity") OR contains(tags, "space-complexity")
SORT difficulty ASC, file.name ASC
```

---

### String Algorithms

**Common patterns:**
- Two pointers for palindromes
- Sliding window for substrings
- Hash map for character frequency
- Trie for prefix matching
- KMP for pattern matching

**All String Questions:**
```dataview
TABLE difficulty, status
FROM "20-Algorithms"
WHERE contains(tags, "strings") OR contains(tags, "string-algorithms") OR contains(subtopics, "strings")
SORT difficulty ASC, file.name ASC
```

---

### Greedy Algorithms

**Key Questions**:
- [[q-advanced-graph-algorithms--algorithms--hard]] - Includes greedy algorithms like Dijkstra, MST

**When to use:**
- Local optimal choice leads to global optimum
- Activity selection, interval scheduling
- Huffman coding

**Warning:** Greedy doesn't always work - verify correctness!

**All Greedy Questions:**
```dataview
TABLE difficulty, status
FROM "20-Algorithms"
WHERE contains(tags, "greedy") OR contains(tags, "greedy-algorithms") OR contains(subtopics, "greedy")
SORT difficulty ASC, file.name ASC
```

---

### Divide & Conquer

**Pattern:**
1. Divide problem into smaller subproblems
2. Conquer subproblems recursively
3. Combine solutions

**Examples:**
- Merge Sort: O(n log n)
- Quick Sort: O(n log n) average
- Binary Search: O(log n)

**All Divide & Conquer Questions:**
```dataview
TABLE difficulty, status
FROM "20-Algorithms"
WHERE contains(tags, "divide-and-conquer") OR contains(subtopics, "divide-and-conquer")
SORT difficulty ASC, file.name ASC
```

## All Questions
```dataview
TABLE difficulty, subtopics, status, tags
FROM "20-Algorithms"
SORT difficulty ASC, file.name ASC
```

## Statistics
```dataview
TABLE length(rows) as "Count"
FROM "20-Algorithms"
GROUP BY difficulty
SORT difficulty ASC
```

## Related MOCs
- [[moc-cs]]
- [[moc-kotlin]]
