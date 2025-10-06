---
id: moc-tools-20251006
title: Development Tools — Map of Content
kind: moc
created: 2025-10-06
updated: 2025-10-06
tags: [moc, tools, devtools]
---

# Development Tools — Map of Content

Welcome to the development tools knowledge base! This covers Git, build systems, CI/CD, and other developer tools.

---

## Quick Stats

```dataview
TABLE
    length(rows) as "Count"
FROM "80-Tools"
WHERE file.name != "moc-tools"
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
FROM "80-Tools"
WHERE difficulty = "easy" AND file.name != "moc-tools"
SORT file.name ASC
```

### Medium Questions

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    tags as "Topics"
FROM "80-Tools"
WHERE difficulty = "medium" AND file.name != "moc-tools"
SORT file.name ASC
```

### Hard Questions

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    tags as "Topics"
FROM "80-Tools"
WHERE difficulty = "hard" AND file.name != "moc-tools"
SORT file.name ASC
```

---

## By Category

### Git & Version Control

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "80-Tools"
WHERE contains(tags, "git") OR contains(tags, "version-control")
    AND file.name != "moc-tools"
SORT difficulty ASC
```

### Build Systems

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "80-Tools"
WHERE contains(tags, "gradle") OR contains(tags, "build") OR contains(tags, "maven")
    AND file.name != "moc-tools"
SORT difficulty ASC
```

### CI/CD

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "80-Tools"
WHERE contains(tags, "ci-cd") OR contains(tags, "jenkins") OR contains(tags, "github-actions")
    AND file.name != "moc-tools"
SORT difficulty ASC
```

### IDEs & Editors

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "80-Tools"
WHERE contains(tags, "ide") OR contains(tags, "android-studio") OR contains(tags, "intellij")
    AND file.name != "moc-tools"
SORT difficulty ASC
```

### Static Analysis & Linting

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "80-Tools"
WHERE contains(tags, "lint") OR contains(tags, "static-analysis") OR contains(tags, "detekt")
    AND file.name != "moc-tools"
SORT difficulty ASC
```

### Debugging & Profiling

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "80-Tools"
WHERE contains(tags, "debugging") OR contains(tags, "profiling") OR contains(tags, "adb")
    AND file.name != "moc-tools"
SORT difficulty ASC
```

---

## Recently Added

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty",
    created as "Added"
FROM "80-Tools"
WHERE file.name != "moc-tools"
SORT created DESC
LIMIT 10
```

---

## Related MOCs

- [[moc-android]] - Android development tools (Gradle, Lint, etc.)
- [[moc-kotlin]] - Kotlin tooling

---

**Total Questions**:
```dataview
TABLE length(rows) as "Total"
FROM "80-Tools"
WHERE file.name != "moc-tools"
```
