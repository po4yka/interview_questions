---
id: ivm-20251012-140100
title: Computer Science — MOC
kind: moc
created: 2025-10-12
updated: 2025-10-12
tags: [moc, topic/cs]
date created: Saturday, October 18th 2025, 2:45:17 pm
date modified: Tuesday, November 25th 2025, 8:53:47 pm
---

# Computer Science — Map of Content

## Overview
This MOC covers fundamental computer science concepts including design patterns, architecture patterns, object-oriented programming (OOP), software design principles, programming language concepts, data structures, algorithms, and theoretical foundations.

## By Difficulty

### Easy
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM "60-CompSci"
WHERE difficulty = "easy"
SORT file.name ASC
LIMIT 100
```

### Medium
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM "60-CompSci"
WHERE difficulty = "medium"
SORT file.name ASC
LIMIT 100
```

### Hard
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM "60-CompSci"
WHERE difficulty = "hard"
SORT file.name ASC
LIMIT 100
```

## By Subtopic

### Design Patterns
```dataview
TABLE difficulty, status
FROM "60-CompSci"
WHERE contains(topic, "design-patterns") OR contains(tags, "design-patterns") OR contains(tags, "gof-patterns")
SORT difficulty ASC, file.name ASC
```

### Architecture Patterns
```dataview
TABLE difficulty, status
FROM "60-CompSci"
WHERE contains(topic, "architecture-patterns") OR contains(tags, "architecture-patterns") OR contains(tags, "mvvm") OR contains(tags, "mvi") OR contains(tags, "clean-architecture")
SORT difficulty ASC, file.name ASC
```

### Object-Oriented Programming (OOP)
```dataview
TABLE difficulty, status
FROM "60-CompSci"
WHERE contains(topic, "oop") OR contains(tags, "oop") OR contains(tags, "inheritance") OR contains(tags, "encapsulation") OR contains(tags, "polymorphism")
SORT difficulty ASC, file.name ASC
```

### Software Design & Principles
```dataview
TABLE difficulty, status
FROM "60-CompSci"
WHERE contains(topic, "software-design") OR contains(tags, "software-design") OR contains(tags, "solid") OR contains(tags, "design-principles")
SORT difficulty ASC, file.name ASC
```

### Programming Languages Concepts
```dataview
TABLE difficulty, status
FROM "60-CompSci"
WHERE contains(topic, "programming-languages") OR contains(tags, "programming-languages") OR contains(tags, "type-systems") OR contains(tags, "memory-management")
SORT difficulty ASC, file.name ASC
```

### Data Structures & Algorithms
```dataview
TABLE difficulty, status
FROM "60-CompSci"
WHERE contains(tags, "data-structures") OR contains(tags, "algorithms") OR contains(tags, "complexity") OR contains(tags, "big-o")
SORT difficulty ASC, file.name ASC
```

### Concurrency & Asynchronous Programming
```dataview
TABLE difficulty, status
FROM "60-CompSci"
WHERE contains(tags, "concurrency") OR contains(tags, "async") OR contains(tags, "threading") OR contains(tags, "parallelism")
SORT difficulty ASC, file.name ASC
```

### Functional Programming
```dataview
TABLE difficulty, status
FROM "60-CompSci"
WHERE contains(tags, "functional-programming") OR contains(tags, "fp") OR contains(tags, "immutability") OR contains(tags, "pure-functions")
SORT difficulty ASC, file.name ASC
```

## All Questions
```dataview
TABLE difficulty, topic, subtopics, status
FROM "60-CompSci"
SORT difficulty ASC, file.name ASC
```

## Statistics
```dataview
TABLE length(rows) as "Count"
FROM "60-CompSci"
GROUP BY difficulty
SORT difficulty ASC
```

## Related MOCs
- [[moc-algorithms]]
- [[moc-kotlin]]
- [[moc-android]]
