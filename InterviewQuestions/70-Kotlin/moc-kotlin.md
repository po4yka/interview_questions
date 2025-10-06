---
id: moc-kotlin-20251006
title: Kotlin — Map of Content
kind: moc
created: 2025-10-06
updated: 2025-10-06
tags: [moc, kotlin]
---

# Kotlin Interview Questions — Map of Content

Welcome to the Kotlin knowledge base! This page provides organized access to all Kotlin-related interview questions.

---

## Quick Stats

```dataview
TABLE
    length(rows) as "Count"
FROM "70-Kotlin"
WHERE file.name != "moc-kotlin"
GROUP BY difficulty
SORT difficulty ASC
```

---

## Start Here — By Difficulty

### Easy Questions

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    subtopics as "Topics"
FROM "70-Kotlin"
WHERE difficulty = "easy" AND file.name != "moc-kotlin"
SORT file.name ASC
```

### Medium Questions

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    subtopics as "Topics"
FROM "70-Kotlin"
WHERE difficulty = "medium" AND file.name != "moc-kotlin"
SORT file.name ASC
```

### Hard Questions

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    subtopics as "Topics"
FROM "70-Kotlin"
WHERE difficulty = "hard" AND file.name != "moc-kotlin"
SORT file.name ASC
```

---

## By Category

### Coroutines & Concurrency

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "70-Kotlin"
WHERE contains(subtopics, "coroutines") OR contains(tags, "coroutines") AND file.name != "moc-kotlin"
SORT difficulty ASC, file.name ASC
```

### Flow & Reactive Streams

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "70-Kotlin"
WHERE contains(subtopics, "flow") OR contains(tags, "flow") AND file.name != "moc-kotlin"
SORT difficulty ASC, file.name ASC
```

### Language Features

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty",
    subtopics as "Topics"
FROM "70-Kotlin"
WHERE !contains(subtopics, "coroutines")
    AND !contains(subtopics, "flow")
    AND file.name != "moc-kotlin"
SORT difficulty ASC, file.name ASC
```

---

## By Topic

### Collections & Data Structures

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "70-Kotlin"
WHERE contains(tags, "collections") OR contains(tags, "sequences") AND file.name != "moc-kotlin"
SORT difficulty ASC
```

### Type System & Generics

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "70-Kotlin"
WHERE contains(tags, "generics") OR contains(tags, "type-system") OR contains(tags, "null-safety") AND file.name != "moc-kotlin"
SORT difficulty ASC
```

### Functional Programming

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "70-Kotlin"
WHERE contains(tags, "lambda") OR contains(tags, "higher-order") OR contains(tags, "scope-functions") AND file.name != "moc-kotlin"
SORT difficulty ASC
```

---

## Recently Added

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty",
    created as "Added"
FROM "70-Kotlin"
WHERE file.name != "moc-kotlin"
SORT created DESC
LIMIT 10
```

---

## Study Paths

### Junior Developer Path

Recommended order for beginners:

1. **Basics**: Collections, null safety, visibility modifiers
2. **Classes**: Data classes, sealed classes, enum classes
3. **Functions**: Extension functions, scope functions, lambdas
4. **Coroutines Intro**: What are coroutines, suspend functions

```dataview
LIST
FROM "70-Kotlin"
WHERE difficulty = "easy" AND file.name != "moc-kotlin"
SORT file.name ASC
```

### Mid-Level Developer Path

For experienced developers learning Kotlin:

1. **Coroutines**: Structured concurrency, cancellation, dispatchers
2. **Flow**: Basics, operators, StateFlow/SharedFlow
3. **Advanced Types**: Generics, type system, delegation
4. **Best Practices**: Scope functions, higher-order functions

```dataview
LIST
FROM "70-Kotlin"
WHERE difficulty = "medium" AND contains(tags, "coroutines") AND file.name != "moc-kotlin"
SORT file.name ASC
```

### Senior Developer Path

Deep dives and advanced topics:

1. **Coroutine Internals**: Context, exception handling, supervisors
2. **Flow Advanced**: Operators, backpressure, testing
3. **Type System**: Variance, generics, projections
4. **Multiplatform**: KMM overview and patterns

```dataview
LIST
FROM "70-Kotlin"
WHERE difficulty = "hard" AND file.name != "moc-kotlin"
SORT file.name ASC
```

---

## Related MOCs

- [[moc-android]] - Android development questions
- [[moc-architecture-patterns]] - Design patterns and architecture

---

**Total Questions**:
```dataview
TABLE length(rows) as "Total"
FROM "70-Kotlin"
WHERE file.name != "moc-kotlin"
```
