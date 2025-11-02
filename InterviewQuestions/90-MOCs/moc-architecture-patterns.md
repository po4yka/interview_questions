---
id: moc-architecture-patterns-20251006
title: Architecture Patterns — Map of Content
kind: moc
created: 2025-10-06
updated: 2025-10-06
tags: [architecture-patterns, design-patterns, moc]
date created: Monday, October 6th 2025, 1:57:31 pm
date modified: Saturday, November 1st 2025, 5:43:22 pm
---

# Architecture Patterns & Design Patterns — Map of Content

Welcome to the architecture and design patterns knowledge base! This page covers both general software architecture patterns and platform-specific implementations.

---

## Quick Stats

```dataview
TABLE
    length(rows) as "Count"
FROM "60-CompSci"
WHERE (topic = "architecture-patterns" OR topic = "design-patterns") AND file.name != "moc-architecture-patterns"
GROUP BY difficulty
SORT difficulty ASC
```

---

## Start Here — By Difficulty

### Easy Questions

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    topic as "Topic"
FROM "60-CompSci"
WHERE (topic = "architecture-patterns" OR topic = "design-patterns")
    AND difficulty = "easy"
    AND file.name != "moc-architecture-patterns"
SORT file.name ASC
```

### Medium Questions

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    topic as "Topic"
FROM "60-CompSci"
WHERE (topic = "architecture-patterns" OR topic = "design-patterns")
    AND difficulty = "medium"
    AND file.name != "moc-architecture-patterns"
SORT file.name ASC
```

### Hard Questions

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    topic as "Topic"
FROM "60-CompSci"
WHERE (topic = "architecture-patterns" OR topic = "design-patterns")
    AND difficulty = "hard"
    AND file.name != "moc-architecture-patterns"
SORT file.name ASC
```

---

## By Pattern Type

### Architectural Patterns

**Presentation Layer Patterns**:

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "60-CompSci"
WHERE contains(tags, "mvvm") OR contains(tags, "mvi") OR contains(tags, "mvp")
    AND file.name != "moc-architecture-patterns"
SORT difficulty ASC
```

**Service Layer Patterns**:

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "60-CompSci"
WHERE contains(tags, "service-locator") OR contains(tags, "repository")
    AND file.name != "moc-architecture-patterns"
SORT difficulty ASC
```

### Creational Patterns

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "60-CompSci"
WHERE contains(tags, "singleton") OR contains(tags, "factory") OR contains(tags, "builder")
    AND file.name != "moc-architecture-patterns"
SORT difficulty ASC
```

### Structural Patterns

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "60-CompSci"
WHERE contains(tags, "adapter") OR contains(tags, "decorator") OR contains(tags, "facade")
    AND file.name != "moc-architecture-patterns"
SORT difficulty ASC
```

### Behavioral Patterns

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "60-CompSci"
WHERE contains(tags, "observer") OR contains(tags, "strategy") OR contains(tags, "state")
    AND file.name != "moc-architecture-patterns"
SORT difficulty ASC
```

---

## Platform-Specific Implementations

### Android Architecture

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "40-Android"
WHERE contains(tags, "architecture") OR contains(tags, "mvvm") OR contains(tags, "mvi")
SORT difficulty ASC
LIMIT 20
```

### General Programming

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "60-CompSci"
WHERE topic = "architecture-patterns" OR topic = "design-patterns"
    AND file.name != "moc-architecture-patterns"
SORT difficulty ASC
```

---

## Key Concepts

### MVVM (Model-View-ViewModel)

```dataview
LIST
FROM "40-Android" OR "60-CompSci"
WHERE contains(tags, "mvvm")
SORT file.name ASC
```

### MVI (Model-View-Intent)

```dataview
LIST
FROM "40-Android" OR "60-CompSci"
WHERE contains(tags, "mvi")
SORT file.name ASC
```

### MVP (Model-View-Presenter)

```dataview
LIST
FROM "40-Android" OR "60-CompSci"
WHERE contains(tags, "mvp")
SORT file.name ASC
```

### Clean Architecture

```dataview
LIST
FROM "40-Android"
WHERE contains(tags, "clean-architecture")
SORT file.name ASC
```

---

## Recently Added

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty",
    created as "Added"
FROM "60-CompSci"
WHERE (topic = "architecture-patterns" OR topic = "design-patterns")
    AND file.name != "moc-architecture-patterns"
SORT created DESC
LIMIT 10
```

---

## Study Path

### Beginner Path

Understanding basic patterns:

1. **Start with**: MVC, MVP basics
2. **Then learn**: Observer pattern, Strategy pattern
3. **Finally**: MVVM fundamentals

### Intermediate Path

Platform-specific implementations:

1. **Android MVVM**: with Jetpack components
2. **Android MVI**: unidirectional data flow
3. **Repository Pattern**: data layer abstraction
4. **Dependency Injection**: Hilt/Koin

### Advanced Path

Complex architectures:

1. **Clean Architecture**: multi-layer design
2. **Modularization**: feature modules, shared modules
3. **Multi-platform**: shared architecture across platforms
4. **Microservices**: distributed system patterns

---

## Related MOCs

- [[moc-android]] - Android-specific implementations
- [[moc-kotlin]] - Kotlin language features
- [[moc-backend]] - Backend architecture patterns

---

**Total Questions**:
```dataview
TABLE length(rows) as "Total"
FROM "60-CompSci"
WHERE (topic = "architecture-patterns" OR topic = "design-patterns")
    AND file.name != "moc-architecture-patterns"
```
