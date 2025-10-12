---
id: ivm-20251012-140000
title: Android — MOC
kind: moc
created: 2025-10-12
updated: 2025-10-12
tags: [moc, topic/android]
---

# Android — Map of Content

## Overview
This MOC covers Android development topics including framework fundamentals, Jetpack Compose, architecture components, dependency injection, testing, performance optimization, security, and best practices for building Android applications.

## By Difficulty

### Easy
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM "40-Android"
WHERE difficulty = "easy"
SORT file.name ASC
LIMIT 100
```

### Medium
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM "40-Android"
WHERE difficulty = "medium"
SORT file.name ASC
LIMIT 100
```

### Hard
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
FROM "40-Android"
WHERE difficulty = "hard"
SORT file.name ASC
LIMIT 100
```

## By Subtopic

### Jetpack Compose
```dataview
TABLE difficulty, status
FROM "40-Android"
WHERE contains(file.name, "compose") OR contains(tags, "jetpack-compose") OR contains(tags, "compose")
SORT difficulty ASC, file.name ASC
```

### Dependency Injection
```dataview
TABLE difficulty, status
FROM "40-Android"
WHERE contains(file.name, "dagger") OR contains(file.name, "hilt") OR contains(tags, "dagger") OR contains(tags, "hilt") OR contains(tags, "dependency-injection")
SORT difficulty ASC, file.name ASC
```

### Testing
```dataview
TABLE difficulty, status
FROM "40-Android"
WHERE contains(file.name, "testing") OR contains(file.name, "test") OR contains(tags, "testing") OR topic = "testing"
SORT difficulty ASC, file.name ASC
```

### Architecture & Design Patterns
```dataview
TABLE difficulty, status
FROM "40-Android"
WHERE contains(tags, "architecture") OR contains(tags, "mvvm") OR contains(tags, "mvi") OR contains(file.name, "architecture")
SORT difficulty ASC, file.name ASC
```

### Multiplatform (KMM)
```dataview
TABLE difficulty, status
FROM "40-Android"
WHERE contains(file.name, "kmm") OR contains(file.name, "multiplatform") OR contains(tags, "multiplatform")
SORT difficulty ASC, file.name ASC
```

### Performance & Optimization
```dataview
TABLE difficulty, status
FROM "40-Android"
WHERE contains(tags, "performance") OR contains(tags, "optimization") OR contains(file.name, "performance")
SORT difficulty ASC, file.name ASC
```

### Security
```dataview
TABLE difficulty, status
FROM "40-Android"
WHERE contains(tags, "security") OR topic = "security" OR contains(file.name, "security")
SORT difficulty ASC, file.name ASC
```

### Fragments & Activities
```dataview
TABLE difficulty, status
FROM "40-Android"
WHERE contains(file.name, "fragment") OR contains(file.name, "activity") OR contains(tags, "fragments") OR contains(tags, "activities")
SORT difficulty ASC, file.name ASC
```

### Data & Networking
```dataview
TABLE difficulty, status
FROM "40-Android"
WHERE contains(tags, "networking") OR contains(tags, "retrofit") OR contains(tags, "data-sync") OR contains(file.name, "network") OR contains(file.name, "sync")
SORT difficulty ASC, file.name ASC
```

## All Questions
```dataview
TABLE difficulty, subtopics, status, tags
FROM "40-Android"
SORT difficulty ASC, file.name ASC
```

## Statistics
```dataview
TABLE length(rows) as "Count"
FROM "40-Android"
GROUP BY difficulty
SORT difficulty ASC
```

## Related MOCs
- [[moc-kotlin]]
- [[moc-compSci]]
- [[moc-tools]]
