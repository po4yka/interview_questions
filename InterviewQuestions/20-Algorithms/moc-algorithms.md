---
id: moc-algorithms-20251006
title: Algorithms & Data Structures — Map of Content
kind: moc
created: 2025-10-06
updated: 2025-10-06
tags: [moc, algorithms, data-structures]
---

# Algorithms & Data Structures — Map of Content

Welcome to the algorithms and data structures knowledge base! This covers fundamental CS concepts, coding problems, and algorithmic thinking.

---

## Quick Stats

```dataview
TABLE
    length(rows) as "Count"
FROM "20-Algorithms"
WHERE file.name != "moc-algorithms"
GROUP BY difficulty
SORT difficulty ASC
```

---

## All Questions

### Easy Questions

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    tags as "Topics"
FROM "20-Algorithms"
WHERE difficulty = "easy" AND file.name != "moc-algorithms"
SORT file.name ASC
```

### Medium Questions

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    tags as "Topics"
FROM "20-Algorithms"
WHERE difficulty = "medium" AND file.name != "moc-algorithms"
SORT file.name ASC
```

### Hard Questions

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    tags as "Topics"
FROM "20-Algorithms"
WHERE difficulty = "hard" AND file.name != "moc-algorithms"
SORT file.name ASC
```

---

## By Category

### Data Structures

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "20-Algorithms"
WHERE contains(tags, "array") OR contains(tags, "linked-list") OR contains(tags, "tree") OR contains(tags, "graph") OR contains(tags, "hash-table") OR contains(tags, "stack") OR contains(tags, "queue")
    AND file.name != "moc-algorithms"
SORT difficulty ASC
```

### Searching Algorithms

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "20-Algorithms"
WHERE contains(tags, "search") OR contains(tags, "binary-search") OR contains(tags, "dfs") OR contains(tags, "bfs")
    AND file.name != "moc-algorithms"
SORT difficulty ASC
```

### Sorting Algorithms

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "20-Algorithms"
WHERE contains(tags, "sorting") OR contains(tags, "quicksort") OR contains(tags, "mergesort")
    AND file.name != "moc-algorithms"
SORT difficulty ASC
```

### Dynamic Programming

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "20-Algorithms"
WHERE contains(tags, "dynamic-programming") OR contains(tags, "dp") OR contains(tags, "memoization")
    AND file.name != "moc-algorithms"
SORT difficulty ASC
```

### Greedy Algorithms

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "20-Algorithms"
WHERE contains(tags, "greedy")
    AND file.name != "moc-algorithms"
SORT difficulty ASC
```

### Graph Algorithms

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "20-Algorithms"
WHERE contains(tags, "graph") OR contains(tags, "dijkstra") OR contains(tags, "topological-sort")
    AND file.name != "moc-algorithms"
SORT difficulty ASC
```

### Complexity Analysis

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "20-Algorithms"
WHERE contains(tags, "complexity") OR contains(tags, "big-o") OR contains(tags, "time-complexity") OR contains(tags, "space-complexity")
    AND file.name != "moc-algorithms"
SORT difficulty ASC
```

---

## Recently Added

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty",
    created as "Added"
FROM "20-Algorithms"
WHERE file.name != "moc-algorithms"
SORT created DESC
LIMIT 10
```

---

## Study Path

### Fundamentals

Essential CS fundamentals:

1. **Arrays & Strings**: Basic operations, two pointers
2. **Linked Lists**: Traversal, reversal, cycle detection
3. **Stacks & Queues**: Implementation and applications
4. **Hash Tables**: Hashing, collision resolution

### Intermediate

Common interview topics:

1. **Trees**: Binary trees, BST, traversals
2. **Sorting & Searching**: Binary search, merge sort, quick sort
3. **Recursion**: Base cases, recursive thinking
4. **Basic DP**: Fibonacci, coin change

### Advanced

Complex algorithmic problems:

1. **Graph Algorithms**: BFS, DFS, shortest paths
2. **Advanced DP**: 2D DP, optimization
3. **Advanced Trees**: Segment trees, tries
4. **Hard Problems**: Competitive programming level

---

## Problem Types

### Coding Interview Problems

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "20-Algorithms"
WHERE question_kind = "coding" AND file.name != "moc-algorithms"
SORT difficulty ASC
```

### Theoretical Questions

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "20-Algorithms"
WHERE question_kind = "theory" AND file.name != "moc-algorithms"
SORT difficulty ASC
```

---

## Related MOCs

- [[moc-kotlin]] - Kotlin implementations of algorithms
- [[moc-android]] - Android-specific optimizations

---

**Total Questions**:
```dataview
TABLE length(rows) as "Total"
FROM "20-Algorithms"
WHERE file.name != "moc-algorithms"
```
