# Interview Questions Knowledge Base

> **Comprehensive bilingual collection** of interview questions for Android, Kotlin, Computer Science, and more. Perfect for interview preparation from Junior to Staff+ levels.

---

## Vault Statistics

### Overall Metrics

```dataview
TABLE WITHOUT ID
    length(rows) as "Total Questions"
FROM "40-Android" OR "70-Kotlin" OR "60-CompSci" OR "20-Algorithms" OR "50-Backend" OR "80-Tools"
WHERE topic
GROUP BY true
```

### By Topic

```dataview
TABLE WITHOUT ID
    topic as "Topic",
    length(rows) as "Count",
    round((length(filter(rows, (r) => r.difficulty = "easy")) / length(rows)) * 100) + "%" as "Easy",
    round((length(filter(rows, (r) => r.difficulty = "medium")) / length(rows)) * 100) + "%" as "Medium",
    round((length(filter(rows, (r) => r.difficulty = "hard")) / length(rows)) * 100) + "%" as "Hard"
FROM "40-Android" OR "70-Kotlin" OR "60-CompSci" OR "20-Algorithms" OR "50-Backend" OR "80-Tools"
WHERE topic
GROUP BY topic
SORT length(rows) DESC
```

### By Difficulty

```dataview
TABLE WITHOUT ID
    difficulty as "Difficulty",
    length(rows) as "Count",
    round((length(rows) / 580) * 100) + "%" as "Percentage"
FROM "40-Android" OR "70-Kotlin" OR "60-CompSci" OR "20-Algorithms" OR "50-Backend" OR "80-Tools"
WHERE difficulty
GROUP BY difficulty
SORT difficulty ASC
```

### By Status

```dataview
TABLE WITHOUT ID
    status as "Status",
    length(rows) as "Count",
    round((length(rows) / 580) * 100) + "%" as "Percentage"
FROM "40-Android" OR "70-Kotlin" OR "60-CompSci" OR "20-Algorithms" OR "50-Backend" OR "80-Tools"
WHERE status
GROUP BY status
SORT length(rows) DESC
```

---

## Quick Navigation by Topic

### Android Development

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty",
    join(list(subtopics)[0], ", ") as "Primary Subtopic"
FROM "40-Android"
WHERE topic = "android"
SORT difficulty ASC, file.name ASC
LIMIT 20
```

[View all Android questions →](40-Android)

---

### Kotlin Language

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty",
    join(list(subtopics)[0], ", ") as "Primary Subtopic"
FROM "70-Kotlin"
WHERE topic = "kotlin"
SORT difficulty ASC, file.name ASC
LIMIT 20
```

[View all Kotlin questions →](70-Kotlin)

---

### Architecture & Design Patterns

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty",
    topic as "Category"
FROM "60-CompSci"
WHERE topic = "architecture-patterns" OR topic = "design-patterns"
SORT difficulty ASC, file.name ASC
```

---

### System Design

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty",
    join(list(subtopics), ", ") as "Topics"
FROM "40-Android"
WHERE topic = "system-design"
SORT file.name ASC
```

---

### Algorithms & Data Structures

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "20-Algorithms"
WHERE topic = "algorithms"
SORT difficulty ASC, file.name ASC
```

---

### Backend & Databases

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty",
    join(list(subtopics), ", ") as "Subtopics"
FROM "50-Backend"
WHERE topic = "backend"
SORT difficulty ASC, file.name ASC
```

---

### Tools & Git

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    difficulty as "Difficulty"
FROM "80-Tools"
WHERE topic = "tools"
SORT difficulty ASC, file.name ASC
```

---

## Advanced Search & Filters

### Recently Added (Last 30 Days)

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    topic as "Topic",
    difficulty as "Difficulty",
    dateformat(file.ctime, "yyyy-MM-dd") as "Created"
FROM "40-Android" OR "70-Kotlin" OR "60-CompSci" OR "20-Algorithms" OR "50-Backend" OR "80-Tools"
WHERE file.ctime >= date(today) - dur(30 days)
SORT file.ctime DESC
LIMIT 30
```

---

### Hard Questions by Topic

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    topic as "Topic",
    join(list(subtopics), ", ") as "Subtopics"
FROM "40-Android" OR "70-Kotlin" OR "60-CompSci" OR "20-Algorithms" OR "50-Backend" OR "80-Tools"
WHERE difficulty = "hard"
SORT topic ASC, file.name ASC
```

---

### Drafts Pending Review

```dataview
TABLE WITHOUT ID
    file.link as "Question",
    topic as "Topic",
    difficulty as "Difficulty",
    dateformat(file.ctime, "yyyy-MM-dd") as "Created"
FROM "40-Android" OR "70-Kotlin" OR "60-CompSci" OR "20-Algorithms" OR "50-Backend" OR "80-Tools"
WHERE status = "draft"
SORT file.ctime DESC
LIMIT 50
```

---

## Study Paths

### Junior Level Track
**Focus**: Easy Android, Kotlin basics, fundamental patterns
- Activity lifecycle, basic coroutines, fundamental design patterns
- Estimated: ~200 easy-level questions

### Mid Level Track
**Focus**: Medium Android/Kotlin, architecture patterns, system design basics
- Jetpack Compose, Flow operators, MVVM/MVI, performance optimization
- Estimated: ~500 medium-level questions

### Senior+ Level Track
**Focus**: Hard Android/Kotlin, system design, advanced patterns
- Multi-module architecture, scalability, complex coroutines, KMP
- Estimated: ~150 hard-level questions

---

## Quick Links

### Documentation
- [Vault Documentation](00-Administration/README.md)
- [File Naming Rules](00-Administration/FILE-NAMING-RULES.md)
- [Import Progress Report](00-Administration/SOURCE-IMPORT-PROGRESS.md)

### Templates
- [Q&A Template](_templates/_tpl-qna.md)
- [Concept Template](_templates/_tpl-concept.md)
- [MOC Template](_templates/_tpl-moc.md)

### Reports
- [Complete Import Summary](00-Administration/COMPLETE-SOURCE-IMPORT-SUMMARY.md)
- [Quality Review Report](00-Administration/QUALITY-REVIEW-REPORT.md)

---

## Language Coverage

**All questions support**:
- English (EN)
- Russian (RU)

```dataview
TABLE WITHOUT ID
    "Bilingual Coverage" as "Metric",
    length(filter(rows, (r) => contains(r.language_tags, "en") AND contains(r.language_tags, "ru"))) as "Questions with EN+RU",
    round((length(filter(rows, (r) => contains(r.language_tags, "en") AND contains(r.language_tags, "ru"))) / length(rows)) * 100) + "%" as "Coverage"
FROM "40-Android" OR "70-Kotlin" OR "60-CompSci" OR "20-Algorithms" OR "50-Backend" OR "80-Tools"
WHERE language_tags
GROUP BY true
```

---

## Progress Tracking

### Completion Rate by Topic

```dataview
TABLE WITHOUT ID
    topic as "Topic",
    length(rows) as "Total",
    length(filter(rows, (r) => r.status = "ready")) as "Ready",
    length(filter(rows, (r) => r.status = "reviewed")) as "Reviewed",
    length(filter(rows, (r) => r.status = "draft")) as "Draft",
    round((length(filter(rows, (r) => r.status = "ready")) / length(rows)) * 100) + "%" as "Completion %"
FROM "40-Android" OR "70-Kotlin" OR "60-CompSci" OR "20-Algorithms" OR "50-Backend" OR "80-Tools"
WHERE topic
GROUP BY topic
SORT length(rows) DESC
```

---

## Vault Highlights

- **Total Questions**: 580+ markdown files (as of 2025-10-06)
- **Topics Covered**: 7 main categories
- **Bilingual**: 100% EN/RU coverage target
- **Difficulty Range**: Easy to Hard (Junior to Staff+)
- **Sources**: Kirchhoff + Amit Shekhar repositories
- **Quality**: Standardized template compliance
- **NEW**: System Design category (12 questions)

---

## Recent Updates

### 2025-10-06
- Completed all source repositories import (167 new questions)
- Executed comprehensive cleanup (242 files cleaned)
- Removed all redundant difficulty tags
- Template compliance achieved
- Created comprehensive Homepage with Dataview analytics

### 2025-10-05
- Imported Kirchhoff repository (111 questions)
- Imported Amit Shekhar repository (56 questions)
- Created System Design category
- Full bilingual coverage with AI translation

---

## Tips for Using This Vault

1. **Search by difficulty**: Use the filters above to focus on your level
2. **Study by topic**: Navigate via Quick Navigation sections
3. **Track progress**: Mark questions as `reviewed` or `ready` after studying
4. **Use tags**: Each question has detailed tags for granular filtering
5. **Bilingual learning**: Switch between EN/RU sections for better understanding
6. **System Design**: Start with easy questions, progress to hard architectural challenges

---

**Last Updated**: 2025-10-06 | **Vault Status**: Production Ready

*This homepage is powered by [Obsidian Dataview](https://blacksmithgu.github.io/obsidian-dataview/)*
