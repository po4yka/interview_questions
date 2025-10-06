---
id: moc-android-20251006
title: Android — Map of Content
kind: moc
created: 2025-10-06
updated: 2025-10-06
tags: [moc, android]
---

# Android Interview Questions — Map of Content

Welcome to the Android knowledge base! This page provides organized access to all Android-related interview questions.

---

## Quick Stats

```dataview
TABLE
    length(rows) as "Count"
FROM "40-Android"
WHERE file.name != "moc-android"
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
FROM "40-Android"
WHERE difficulty = "easy" AND file.name != "moc-android"
SORT file.name ASC
```

### Medium Questions

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    subtopics as "Topics"
FROM "40-Android"
WHERE difficulty = "medium" AND file.name != "moc-android"
SORT file.name ASC
```

### Hard Questions

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    subtopics as "Topics"
FROM "40-Android"
WHERE difficulty = "hard" AND file.name != "moc-android"
SORT file.name ASC
```

---

## By Category

### UI — Jetpack Compose

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "40-Android"
WHERE contains(subtopics, "ui-compose") OR contains(tags, "compose") AND file.name != "moc-android"
SORT difficulty ASC, file.name ASC
```

### UI — Views & Layouts

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "40-Android"
WHERE contains(subtopics, "ui-views") OR contains(subtopics, "ui-widgets") OR contains(tags, "views") AND file.name != "moc-android"
SORT difficulty ASC, file.name ASC
```

### Architecture — MVVM, MVI, Clean

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "40-Android"
WHERE contains(subtopics, "architecture-mvvm")
    OR contains(subtopics, "architecture-mvi")
    OR contains(subtopics, "architecture-clean")
    OR contains(tags, "architecture")
AND file.name != "moc-android"
SORT difficulty ASC, file.name ASC
```

### Lifecycle & Components

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "40-Android"
WHERE contains(subtopics, "lifecycle")
    OR contains(subtopics, "activity")
    OR contains(subtopics, "fragment")
    OR contains(subtopics, "service")
AND file.name != "moc-android"
SORT difficulty ASC, file.name ASC
```

### Coroutines & Background Work

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "40-Android"
WHERE contains(subtopics, "coroutines")
    OR contains(subtopics, "flow")
    OR contains(subtopics, "background-execution")
    OR contains(tags, "workmanager")
AND file.name != "moc-android"
SORT difficulty ASC, file.name ASC
```

### Data & Persistence

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "40-Android"
WHERE contains(subtopics, "room")
    OR contains(subtopics, "datastore")
    OR contains(subtopics, "files-media")
    OR contains(tags, "database")
    OR contains(tags, "sharedpreferences")
AND file.name != "moc-android"
SORT difficulty ASC, file.name ASC
```

### Networking

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "40-Android"
WHERE contains(subtopics, "networking-http")
    OR contains(tags, "networking")
    OR contains(tags, "retrofit")
AND file.name != "moc-android"
SORT difficulty ASC, file.name ASC
```

### Performance & Optimization

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "40-Android"
WHERE contains(subtopics, "performance-startup")
    OR contains(subtopics, "performance-rendering")
    OR contains(subtopics, "performance-memory")
    OR contains(tags, "performance")
    OR contains(tags, "optimization")
AND file.name != "moc-android"
SORT difficulty ASC, file.name ASC
```

### Testing

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "40-Android"
WHERE contains(subtopics, "testing-unit")
    OR contains(subtopics, "testing-instrumented")
    OR contains(subtopics, "testing-ui")
    OR contains(tags, "testing")
AND file.name != "moc-android"
SORT difficulty ASC, file.name ASC
```

### Gradle & Build

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "40-Android"
WHERE contains(subtopics, "gradle")
    OR contains(subtopics, "build-variants")
    OR contains(tags, "gradle")
    OR contains(tags, "build")
AND file.name != "moc-android"
SORT difficulty ASC, file.name ASC
```

### Security

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "40-Android"
WHERE contains(subtopics, "permissions")
    OR contains(subtopics, "keystore-crypto")
    OR contains(subtopics, "obfuscation")
    OR contains(tags, "security")
AND file.name != "moc-android"
SORT difficulty ASC, file.name ASC
```

### Dependency Injection

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "40-Android"
WHERE contains(subtopics, "di-hilt")
    OR contains(subtopics, "di-koin")
    OR contains(tags, "hilt")
    OR contains(tags, "dagger")
AND file.name != "moc-android"
SORT difficulty ASC, file.name ASC
```

---

## System Design Questions

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "40-Android"
WHERE contains(tags, "system-design") OR question_kind = "system-design" AND file.name != "moc-android"
SORT difficulty ASC
```

---

## Recently Added

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty",
    created as "Added"
FROM "40-Android"
WHERE file.name != "moc-android"
SORT created DESC
LIMIT 10
```

---

## Study Paths

### Junior Android Developer

Focus areas for entry-level positions:

1. **Basics**: Activity lifecycle, Fragments, Views
2. **UI**: Layouts, RecyclerView, basic Compose
3. **Data**: SharedPreferences, basic Room
4. **Async**: Basic coroutines, background work

```dataview
LIST
FROM "40-Android"
WHERE difficulty = "easy" AND file.name != "moc-android"
SORT file.name ASC
LIMIT 20
```

### Mid-Level Android Developer

For experienced Android developers:

1. **Architecture**: MVVM, MVI, Repository pattern
2. **Jetpack Compose**: Advanced composables, state management
3. **Coroutines & Flow**: Structured concurrency, operators
4. **Testing**: Unit tests, UI tests, test strategies
5. **Performance**: Memory optimization, rendering

```dataview
LIST
FROM "40-Android"
WHERE difficulty = "medium" AND file.name != "moc-android"
SORT file.name ASC
LIMIT 30
```

### Senior Android Developer

Deep knowledge and leadership:

1. **System Design**: App architecture, scalability
2. **Advanced Compose**: Performance, custom layouts
3. **Modularization**: Multi-module apps, dependency management
4. **Complex Features**: Real-time sync, offline-first, etc.

```dataview
LIST
FROM "40-Android"
WHERE difficulty = "hard" AND file.name != "moc-android"
SORT file.name ASC
```

---

## Related MOCs

- [[moc-kotlin]] - Kotlin language questions
- [[moc-architecture-patterns]] - Architecture and design patterns
- [[moc-tools]] - Development tools (Git, Gradle, etc.)

---

**Total Questions**:
```dataview
TABLE length(rows) as "Total"
FROM "40-Android"
WHERE file.name != "moc-android"
```
