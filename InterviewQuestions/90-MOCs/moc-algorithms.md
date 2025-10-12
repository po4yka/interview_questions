---
id: ivm-20251012-140300
title: Algorithms — MOC
kind: moc
created: 2025-10-12
updated: 2025-10-12
tags: [moc, topic/algorithms]
---

# Algorithms — Map of Content

## Overview
This MOC covers algorithms, data structures, complexity analysis, algorithm design patterns, sorting and searching algorithms, graph algorithms, dynamic programming, and computational problem-solving techniques.

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
```dataview
TABLE difficulty, status
FROM "20-Algorithms"
WHERE contains(tags, "data-structures") OR contains(subtopics, "data-structures")
SORT difficulty ASC, file.name ASC
```

### Sorting & Searching
```dataview
TABLE difficulty, status
FROM "20-Algorithms"
WHERE contains(tags, "sorting") OR contains(tags, "searching") OR contains(subtopics, "sorting") OR contains(subtopics, "searching")
SORT difficulty ASC, file.name ASC
```

### Graph Algorithms
```dataview
TABLE difficulty, status
FROM "20-Algorithms"
WHERE contains(tags, "graphs") OR contains(tags, "graph-algorithms") OR contains(subtopics, "graphs")
SORT difficulty ASC, file.name ASC
```

### Dynamic Programming
```dataview
TABLE difficulty, status
FROM "20-Algorithms"
WHERE contains(tags, "dynamic-programming") OR contains(tags, "dp") OR contains(subtopics, "dynamic-programming")
SORT difficulty ASC, file.name ASC
```

### Tree Algorithms
```dataview
TABLE difficulty, status
FROM "20-Algorithms"
WHERE contains(tags, "trees") OR contains(tags, "binary-trees") OR contains(subtopics, "trees")
SORT difficulty ASC, file.name ASC
```

### Complexity Analysis
```dataview
TABLE difficulty, status
FROM "20-Algorithms"
WHERE contains(tags, "complexity") OR contains(tags, "big-o") OR contains(tags, "time-complexity") OR contains(tags, "space-complexity")
SORT difficulty ASC, file.name ASC
```

### String Algorithms
```dataview
TABLE difficulty, status
FROM "20-Algorithms"
WHERE contains(tags, "strings") OR contains(tags, "string-algorithms") OR contains(subtopics, "strings")
SORT difficulty ASC, file.name ASC
```

### Greedy Algorithms
```dataview
TABLE difficulty, status
FROM "20-Algorithms"
WHERE contains(tags, "greedy") OR contains(tags, "greedy-algorithms") OR contains(subtopics, "greedy")
SORT difficulty ASC, file.name ASC
```

### Divide & Conquer
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
- [[moc-compSci]]
- [[moc-kotlin]]
