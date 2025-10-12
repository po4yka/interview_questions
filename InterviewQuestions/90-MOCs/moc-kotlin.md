---
id: ivm-20251012-140200
title: Kotlin — MOC
kind: moc
created: 2025-10-12
updated: 2025-10-12
tags: [moc, topic/kotlin]
---

# Kotlin — Map of Content

## Overview
This MOC covers Kotlin language features, syntax, coroutines, Flow, collection operations, advanced language features, standard library functions, interoperability with Java, and best practices for Kotlin development.

## By Difficulty

### Easy
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM "70-Kotlin"
WHERE difficulty = "easy"
SORT file.name ASC
LIMIT 100
```

### Medium
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM "70-Kotlin"
WHERE difficulty = "medium"
SORT file.name ASC
LIMIT 100
```

### Hard
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM "70-Kotlin"
WHERE difficulty = "hard"
SORT file.name ASC
LIMIT 100
```

## By Subtopic

### Coroutines
```dataview
TABLE difficulty, status
FROM "70-Kotlin"
WHERE contains(tags, "coroutines") OR contains(subtopics, "coroutines") OR contains(file.name, "coroutine")
SORT difficulty ASC, file.name ASC
```

### Flow & Reactive Programming
```dataview
TABLE difficulty, status
FROM "70-Kotlin"
WHERE contains(tags, "flow") OR contains(subtopics, "flow") OR contains(file.name, "flow") OR contains(tags, "reactive")
SORT difficulty ASC, file.name ASC
```

### Collections & Sequences
```dataview
TABLE difficulty, status
FROM "70-Kotlin"
WHERE contains(tags, "collections") OR contains(tags, "sequences") OR contains(subtopics, "collections") OR contains(file.name, "collection") OR contains(file.name, "sequence")
SORT difficulty ASC, file.name ASC
```

### Language Features & Syntax
```dataview
TABLE difficulty, status
FROM "70-Kotlin"
WHERE contains(tags, "language-features") OR contains(tags, "syntax") OR contains(tags, "inline") OR contains(tags, "lambdas") OR contains(tags, "extensions")
SORT difficulty ASC, file.name ASC
```

### Object-Oriented Features
```dataview
TABLE difficulty, status
FROM "70-Kotlin"
WHERE contains(tags, "oop") OR contains(tags, "inheritance") OR contains(tags, "abstract-class") OR contains(tags, "interface") OR contains(file.name, "object") OR contains(file.name, "class")
SORT difficulty ASC, file.name ASC
```

### Functional Programming
```dataview
TABLE difficulty, status
FROM "70-Kotlin"
WHERE contains(tags, "functional-programming") OR contains(tags, "higher-order-functions") OR contains(tags, "pure-functions") OR contains(tags, "immutability")
SORT difficulty ASC, file.name ASC
```

### Standard Library & Operators
```dataview
TABLE difficulty, status
FROM "70-Kotlin"
WHERE contains(tags, "stdlib") OR contains(tags, "operators") OR contains(tags, "scope-functions") OR contains(file.name, "operator")
SORT difficulty ASC, file.name ASC
```

### Concurrency & Async Programming
```dataview
TABLE difficulty, status
FROM "70-Kotlin"
WHERE contains(tags, "async") OR contains(tags, "concurrency") OR contains(tags, "channels") OR contains(tags, "dispatchers") OR contains(tags, "cancellation")
SORT difficulty ASC, file.name ASC
```

### Serialization & Data Processing
```dataview
TABLE difficulty, status
FROM "70-Kotlin"
WHERE contains(tags, "serialization") OR contains(tags, "json") OR contains(tags, "parsing") OR contains(file.name, "serialization")
SORT difficulty ASC, file.name ASC
```

### Error Handling & Exceptions
```dataview
TABLE difficulty, status
FROM "70-Kotlin"
WHERE contains(tags, "error-handling") OR contains(tags, "exceptions") OR contains(tags, "result") OR contains(file.name, "exception")
SORT difficulty ASC, file.name ASC
```

### Interoperability
```dataview
TABLE difficulty, status
FROM "70-Kotlin"
WHERE contains(tags, "java-interop") OR contains(tags, "jvm") OR contains(file.name, "java")
SORT difficulty ASC, file.name ASC
```

## All Questions
```dataview
TABLE difficulty, subtopics, status, tags
FROM "70-Kotlin"
SORT difficulty ASC, file.name ASC
```

## Statistics
```dataview
TABLE length(rows) as "Count"
FROM "70-Kotlin"
GROUP BY difficulty
SORT difficulty ASC
```

## Related MOCs
- [[moc-android]]
- [[moc-compSci]]
- [[moc-backend]]
