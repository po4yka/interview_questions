---
id: moc-start-here-20251006
title: Interview Questions Vault — Start Here
kind: moc
created: 2025-10-06
updated: 2025-10-06
tags: [index, moc, start-here]
---

# Interview Questions Vault — Start Here

Welcome to your comprehensive interview questions knowledge base! This vault contains bilingual (EN/RU) questions across multiple topics.

---

## Browse by Topic

### Primary Topics

| Topic | Questions | Focus Area |
|-------|-----------|------------|
| [[moc-android|Android]] | `= length(filter(file.lists.file, (f) => startswith(f.path, "40-Android")))` | Android development, Jetpack, Compose |
| [[moc-kotlin|Kotlin]] | `= length(filter(file.lists.file, (f) => startswith(f.path, "70-Kotlin")))` | Kotlin language, coroutines, Flow |
| [[moc-algorithms|Algorithms]] | `= length(filter(file.lists.file, (f) => startswith(f.path, "20-Algorithms")))` | Data structures, algorithms, coding |
| [[moc-architecture-patterns|Architecture]] | `= length(filter(file.lists.file, (f) => contains(f.path, "60-CompSci")))` | MVVM, MVI, design patterns |
| [[moc-backend|Backend]] | `= length(filter(file.lists.file, (f) => startswith(f.path, "50-Backend")))` | Databases, SQL, APIs |
| [[moc-tools|Tools]] | `= length(filter(file.lists.file, (f) => startswith(f.path, "80-Tools")))` | Git, build tools, CI/CD, IDEs |

---

## Vault Statistics

### Total Questions

```dataview
TABLE
    length(rows) as "Count"
FROM "10-Concepts" OR "20-Algorithms" OR "30-System-Design" OR "40-Android" OR "50-Backend" OR "60-CompSci" OR "70-Kotlin" OR "80-Tools"
WHERE startswith(file.name, "q-") OR startswith(file.name, "c-")
GROUP BY difficulty
SORT difficulty ASC
```

### Questions by Topic

```dataview
TABLE
    length(rows) as "Count",
    round((length(filter(rows, (r) => r.difficulty = "easy")) / length(rows)) * 100, 1) + "%" as "Easy",
    round((length(filter(rows, (r) => r.difficulty = "medium")) / length(rows)) * 100, 1) + "%" as "Medium",
    round((length(filter(rows, (r) => r.difficulty = "hard")) / length(rows)) * 100, 1) + "%" as "Hard"
FROM "10-Concepts" OR "20-Algorithms" OR "30-System-Design" OR "40-Android" OR "50-Backend" OR "60-CompSci" OR "70-Kotlin" OR "80-Tools"
WHERE topic AND (startswith(file.name, "q-") OR startswith(file.name, "c-"))
GROUP BY topic
SORT length(rows) DESC
```

---

## Quick Access

### Recently Added Questions (Last 10)

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    topic as "Topic",
    difficulty as "Difficulty",
    created as "Added"
FROM "10-Concepts" OR "20-Algorithms" OR "30-System-Design" OR "40-Android" OR "50-Backend" OR "60-CompSci" OR "70-Kotlin" OR "80-Tools"
WHERE startswith(file.name, "q-")
SORT created DESC
LIMIT 10
```

### Hard Questions (All Topics)

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    topic as "Topic"
FROM "10-Concepts" OR "20-Algorithms" OR "30-System-Design" OR "40-Android" OR "50-Backend" OR "60-CompSci" OR "70-Kotlin" OR "80-Tools"
WHERE difficulty = "hard" AND startswith(file.name, "q-")
SORT file.name ASC
```

### Draft Status (Needs Review)

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    topic as "Topic",
    difficulty as "Difficulty"
FROM "10-Concepts" OR "20-Algorithms" OR "30-System-Design" OR "40-Android" OR "50-Backend" OR "60-CompSci" OR "70-Kotlin" OR "80-Tools"
WHERE status = "draft" AND startswith(file.name, "q-")
SORT topic ASC, difficulty ASC
LIMIT 20
```

---

## Study Paths

### Junior Developer Path

**Focus**: Fundamentals across all topics

1. **Start with**: [[moc-kotlin#Junior Developer Path|Kotlin Basics]]
2. **Then**: [[moc-android#Junior Android Developer|Android Fundamentals]]
3. **Practice**: [[moc-algorithms#Fundamentals|Basic Algorithms]]
4. **Tools**: [[moc-git#Beginner Git User|Git Basics]]

**Recommended difficulty**: Easy → Medium

### Mid-Level Developer Path

**Focus**: Deep knowledge in specific areas

1. **Core**: [[moc-kotlin#Mid-Level Developer Path|Kotlin Advanced]]
2. **Architecture**: [[moc-android#Mid-Level Android Developer|Android Patterns]]
3. **Patterns**: [[moc-architecture-patterns#Intermediate Path|Design Patterns]]
4. **Backend**: [[moc-backend#Backend Development|APIs & Databases]]

**Recommended difficulty**: Medium → Hard

### Senior Developer Path

**Focus**: System design and leadership

1. **Advanced**: [[moc-kotlin#Senior Developer Path|Kotlin Internals]]
2. **Architecture**: [[moc-android#Senior Android Developer|System Design]]
3. **Scalability**: [[moc-backend#Advanced Backend|Distributed Systems]]
4. **Algorithms**: [[moc-algorithms#Advanced|Complex Problems]]

**Recommended difficulty**: Hard

---

## Search & Filter

### By Language Coverage

**Bilingual (EN + RU)**:
```dataview
TABLE WITHOUT ID
    file.link as "Question",
    topic as "Topic",
    difficulty as "Difficulty"
FROM "10-Concepts" OR "20-Algorithms" OR "30-System-Design" OR "40-Android" OR "50-Backend" OR "60-CompSci" OR "70-Kotlin" OR "80-Tools"
WHERE contains(language_tags, "en") AND contains(language_tags, "ru") AND startswith(file.name, "q-")
SORT topic ASC, difficulty ASC
LIMIT 20
```

### By Question Type

**Coding Challenges**:
```dataview
TABLE WITHOUT ID
    file.link as "Question",
    topic as "Topic",
    difficulty as "Difficulty"
FROM "10-Concepts" OR "20-Algorithms" OR "30-System-Design" OR "40-Android" OR "50-Backend" OR "60-CompSci" OR "70-Kotlin" OR "80-Tools"
WHERE question_kind = "coding" AND startswith(file.name, "q-")
SORT difficulty ASC
LIMIT 15
```

**System Design**:
```dataview
TABLE WITHOUT ID
    file.link as "Question",
    topic as "Topic",
    difficulty as "Difficulty"
FROM "10-Concepts" OR "20-Algorithms" OR "30-System-Design" OR "40-Android" OR "50-Backend" OR "60-CompSci" OR "70-Kotlin" OR "80-Tools"
WHERE question_kind = "system-design" AND startswith(file.name, "q-")
SORT difficulty ASC
```

---

## Templates

Create new content using these templates:

- **Q&A Template**: `_templates/_tpl-qna.md` - For interview questions
- **Concept Template**: `_templates/_tpl-concept.md` - For reusable concepts
- **MOC Template**: `_templates/_tpl-moc.md` - For map of content pages

**See**: [[_templates/README]] for detailed template usage guide

---

## Documentation

- [[00-Administration/Vault-Rules/TAXONOMY]] - Topic and subtopic taxonomy
- [[00-Administration/Vault-Rules/FILE-NAMING-RULES]] - File naming conventions
- [[_templates/README]] - How to use templates

---

## Popular Tags

### Most Used Tags

```dataview
TABLE WITHOUT ID
    length(rows.file.tags) as "Count",
    rows.file.tags as "Tag"
FROM "10-Concepts" OR "20-Algorithms" OR "30-System-Design" OR "40-Android" OR "50-Backend" OR "60-CompSci" OR "70-Kotlin" OR "80-Tools"
WHERE startswith(file.name, "q-")
FLATTEN file.tags as tag
GROUP BY tag
SORT length(rows.file.tags) DESC
LIMIT 20
```

---

## Featured Topics

### Android Jetpack Compose

```dataview
LIST
FROM "40-Android"
WHERE contains(tags, "compose")
SORT difficulty ASC
LIMIT 10
```

### Kotlin Coroutines

```dataview
LIST
FROM "70-Kotlin"
WHERE contains(tags, "coroutines")
SORT difficulty ASC
LIMIT 10
```

### Architecture Patterns

```dataview
LIST
FROM "40-Android" OR "60-CompSci"
WHERE contains(tags, "mvvm") OR contains(tags, "mvi") OR contains(tags, "mvp")
SORT difficulty ASC
LIMIT 10
```

---

## Quick Links

- [[Homepage]] - Dashboard with analytics
- **MOCs**: [[moc-android]] • [[moc-kotlin]] • [[moc-algorithms]] • [[moc-architecture-patterns]]
- **Admin**: [[00-Administration/README]] - Vault administration

---

**Total Questions**:
```dataview
TABLE length(rows) as "Count"
FROM "10-Git" OR "20-Algorithms" OR "40-Android" OR "50-Backend" OR "60-CompSci" OR "70-Kotlin" OR "80-Tools"
WHERE startswith(file.name, "q-") OR startswith(file.name, "c-")
```

**Last Updated**: 2025-10-06
