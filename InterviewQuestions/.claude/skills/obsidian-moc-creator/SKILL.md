---
name: obsidian-moc-creator
description: >
  Create Maps of Content (MOCs) to organize related interview questions by topic.
  Generates study paths organized by difficulty, subtopic groupings, and Dataview
  queries for dynamic content. Uses moc-[topic].md naming pattern and places in
  90-MOCs/ directory.
---

# Obsidian MOC Creator

## Purpose

Create Maps of Content (MOCs) to organize interview questions:
- Topic-based navigation structure
- Study paths organized by difficulty (easy → medium → hard)
- Subtopic groupings for focused learning
- Dataview queries for dynamic content
- Quick reference for vault sections

MOCs serve as entry points and navigation hubs for each topic area.

## When to Use

Activate this skill when user requests:
- "Create MOC for [topic]"
- "Build study guide for [topic]"
- "Organize [topic] questions"
- When starting a new topic area in vault
- When topic has enough content to warrant organization (5+ notes)

## Prerequisites

Required context:
- Topic name (from TAXONOMY.md)
- Understanding of vault topic structure
- `_templates/_tpl-moc.md` template (if available)
- Access to scan existing notes for the topic

## Process

### Step 1: Identify Topic

Determine:
- **Topic name**: Must be valid topic from TAXONOMY.md
- **Scope**: What content this MOC will cover
- **Existing content**: Scan vault for notes with this topic

Valid topics for MOCs (from TAXONOMY.md):
- algorithms, android, kotlin, system-design
- databases, networking, operating-systems
- architecture-patterns, concurrency
- testing, tools, debugging
- etc. (22 total valid topics)

### Step 2: Generate Metadata

**Filename Pattern**:
```
moc-[topic-name].md
```

**Filename Rules**:
- Prefix with `moc-` (for "Map of Content")
- English only (NO Cyrillic)
- Lowercase, hyphens as separators
- Match exact topic name from TAXONOMY.md

**Examples**:
- `moc-kotlin.md`
- `moc-android.md`
- `moc-algorithms.md`
- `moc-system-design.md`
- `moc-architecture-patterns.md`

**Folder**: Always `90-MOCs/`

### Step 3: Build YAML Frontmatter

```yaml
---
title: [Topic] Study Guide / Учебное руководство по [Topic]
aliases: [[Topic] MOC, [Topic] Map, [Topic] Guide]
tags: [moc, topic-name]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

**YAML Fields**:
- `title`: Bilingual title with "Study Guide"
- `aliases`: Alternative names for the MOC
- `tags`: Include `moc` and the topic name
- `created`/`updated`: YYYY-MM-DD format

**Note**: MOCs don't use `id` or `status` fields.

### Step 4: Scan Existing Content

Before building MOC structure:

1. **Search vault** for notes with this topic:
   ```
   Search: topic: [topic-name]
   ```

2. **Group by difficulty**:
   - Easy notes
   - Medium notes
   - Hard notes

3. **Group by subtopic** (if applicable):
   - Identify common subtopics
   - Group related questions

4. **Identify key concepts**:
   - Find concept notes (`c-*.md`) related to this topic
   - List them for "Core Concepts" section

### Step 5: Build Content Structure

```markdown
# [Topic] Study Guide / Учебное руководство по [Topic]

## Overview / Обзор

**English**: Brief description of this topic area, what it covers, and why it's important.

**Russian**: Краткое описание области темы, что она охватывает и почему это важно.

---

## Core Concepts / Основные концепции

Fundamental concepts to understand before tackling questions:

- [[c-concept-1]] - Brief description
- [[c-concept-2]] - Brief description
- [[c-concept-3]] - Brief description

---

## Study Path / Путь обучения

### Beginner Path (Easy) / Путь для начинающих (Легкий)

Start here if new to this topic:

- [[q-question-1--topic--easy]] - Description
- [[q-question-2--topic--easy]] - Description
- [[q-question-3--topic--easy]] - Description

**Estimated time**: X hours

### Intermediate Path (Medium) / Средний уровень

Build on fundamentals with these questions:

- [[q-question-1--topic--medium]] - Description
- [[q-question-2--topic--medium]] - Description
- [[q-question-3--topic--medium]] - Description

**Estimated time**: Y hours

### Advanced Path (Hard) / Продвинутый уровень (Сложный)

Challenge yourself with advanced topics:

- [[q-question-1--topic--hard]] - Description
- [[q-question-2--topic--hard]] - Description

**Estimated time**: Z hours

---

## By Subtopic / По подтемам

### Subtopic 1

- [[q-question-a--topic--easy]]
- [[q-question-b--topic--medium]]
- [[q-question-c--topic--hard]]

### Subtopic 2

- [[q-question-d--topic--easy]]
- [[q-question-e--topic--medium]]

### Subtopic 3

- [[q-question-f--topic--medium]]
- [[q-question-g--topic--hard]]

---

## Quick Reference / Быстрый справочник

### Common Patterns

- Pattern 1: When to use, example
- Pattern 2: When to use, example
- Pattern 3: When to use, example

### Common Pitfalls

- Pitfall 1 and how to avoid
- Pitfall 2 and how to avoid

---

## Statistics / Статистика

\```dataview
TABLE difficulty, status, subtopics
FROM "XX-[Topic]"
WHERE topic = "[topic]"
SORT difficulty ASC, created DESC
\```

**Total questions**: `= length(filter(file.lists.all, (x) => contains(x.topic, "[topic]")))`
**By difficulty**:
- Easy: `= length(filter(file.lists.all, (x) => contains(x.topic, "[topic]") and x.difficulty = "easy"))`
- Medium: `= length(filter(file.lists.all, (x) => contains(x.topic, "[topic]") and x.difficulty = "medium"))`
- Hard: `= length(filter(file.lists.all, (x) => contains(x.topic, "[topic]") and x.difficulty = "hard"))`

---

## Progress Tracking / Отслеживание прогресса

\```dataview
TASK
FROM "XX-[Topic]"
WHERE topic = "[topic]"
\```

---

## Related Topics / Связанные темы

- [[moc-related-topic-1]] - How it relates
- [[moc-related-topic-2]] - How it relates

---

## Resources / Ресурсы

### Official Documentation
- [Official Docs](https://url)
- [API Reference](https://url)

### Tutorials
- [Tutorial 1](https://url)
- [Tutorial 2](https://url)

### Books
- Book Title by Author

### Video Courses
- [Course 1](https://url)
- [Course 2](https://url)

---

## Notes / Примечания

Additional information, study tips, or recommendations for this topic.
```

### Step 6: Quality Check

Before finalizing:

**Structure**:
- [ ] Overview section (bilingual)
- [ ] Core Concepts section with links
- [ ] Study Path organized by difficulty
- [ ] By Subtopic groupings (if applicable)
- [ ] Dataview queries for statistics
- [ ] Related topics linked
- [ ] Resources section populated

**Content**:
- [ ] All linked notes exist
- [ ] Descriptions are helpful and accurate
- [ ] Difficulty progression is logical
- [ ] Subtopic groupings make sense
- [ ] Dataview queries are correct

**YAML**:
- [ ] Title is bilingual
- [ ] Tags include `moc` and topic name
- [ ] Aliases provided

**File Organization**:
- [ ] File in `90-MOCs/` directory
- [ ] Filename follows `moc-[topic].md` pattern
- [ ] Filename matches topic from TAXONOMY.md

### Step 7: Create File and Confirm

1. **Create file** at `90-MOCs/moc-[topic].md`
2. **Write complete content**
3. **Report to user**:
   - Filename
   - Topic covered
   - Number of questions organized
   - Number of concepts linked
   - Study path structure

## Examples

### Example 1: Kotlin MOC

**User Request**: "Create MOC for Kotlin"

**Generated**:
- Filename: `moc-kotlin.md`
- Folder: `90-MOCs/`

**YAML**:
```yaml
---
title: Kotlin Study Guide / Учебное руководство по Kotlin
aliases: [Kotlin MOC, Kotlin Map, Kotlin Guide, Kotlin Questions]
tags: [moc, kotlin]
created: 2025-11-09
updated: 2025-11-09
---
```

**Content** (excerpt):
```markdown
# Kotlin Study Guide / Учебное руководство по Kotlin

## Overview / Обзор

**English**: This guide organizes Kotlin language questions covering coroutines,
flow, type system, collections, and language features. Start with easy questions
to build fundamentals, then progress to advanced concurrency and DSL topics.

**Russian**: Это руководство организует вопросы по языку Kotlin, охватывающие
корутины, flow, систему типов, коллекции и возможности языка.

---

## Core Concepts / Основные концепции

- [[c-coroutines]] - Asynchronous programming in Kotlin
- [[c-flow]] - Reactive streams for Kotlin
- [[c-null-safety]] - Kotlin's approach to null handling
- [[c-extension-functions]] - Extending classes without inheritance

---

## Study Path / Путь обучения

### Beginner Path (Easy)

- [[q-what-is-coroutine--kotlin--easy]] - Introduction to coroutines
- [[q-null-safety-basics--kotlin--easy]] - Understanding null safety
- [[q-extension-functions--kotlin--easy]] - Basic extension functions

**Estimated time**: 4-6 hours

### Intermediate Path (Medium)

- [[q-coroutine-context--kotlin--medium]] - Understanding context
- [[q-flow-operators--kotlin--medium]] - Working with Flow
- [[q-generics-reified--kotlin--medium]] - Advanced type system

**Estimated time**: 8-10 hours

### Advanced Path (Hard)

- [[q-structured-concurrency--kotlin--hard]] - Complex concurrency
- [[q-dsl-design--kotlin--hard]] - Building type-safe DSLs

**Estimated time**: 6-8 hours

---

## By Subtopic / По подтемам

### Coroutines & Concurrency

- [[q-what-is-coroutine--kotlin--easy]]
- [[q-coroutine-context--kotlin--medium]]
- [[q-structured-concurrency--kotlin--hard]]

### Flow & Reactive

- [[q-flow-basics--kotlin--easy]]
- [[q-flow-operators--kotlin--medium]]
- [[q-stateflow-vs-sharedflow--kotlin--hard]]

### Type System

- [[q-null-safety-basics--kotlin--easy]]
- [[q-generics-reified--kotlin--medium]]

---

## Statistics / Статистика

\```dataview
TABLE difficulty, status, subtopics
FROM "70-Kotlin"
WHERE topic = "kotlin"
SORT difficulty ASC, created DESC
\```
```

### Example 2: Android MOC

**Generated**:
- Filename: `moc-android.md`
- Folder: `90-MOCs/`

**YAML**:
```yaml
---
title: Android Study Guide / Учебное руководство по Android
aliases: [Android MOC, Android Map, Android Questions, Android Interview Prep]
tags: [moc, android]
created: 2025-11-09
updated: 2025-11-09
---
```

**By Subtopic** (excerpt):
```markdown
## By Subtopic / По подтемам

### Jetpack Compose

- [[q-compose-basics--android--easy]]
- [[q-compose-remember--android--medium]]
- [[q-compose-recomposition--android--hard]]

### Architecture (MVVM/MVI)

- [[q-viewmodel-basics--android--easy]]
- [[q-viewmodel-factory--android--medium]]
- [[q-mvi-vs-mvvm--android--hard]]

### Lifecycle

- [[q-activity-lifecycle--android--easy]]
- [[q-fragment-lifecycle--android--medium]]
- [[q-process-death-handling--android--hard]]
```

### Example 3: Algorithms MOC

**Generated**:
- Filename: `moc-algorithms.md`
- Folder: `90-MOCs/`

**By Subtopic** (excerpt):
```markdown
## By Subtopic / По подтемам

### Arrays & Hash Maps

- [[q-two-sum--algorithms--easy]]
- [[q-three-sum--algorithms--medium]]
- [[q-four-sum--algorithms--hard]]

### Binary Search

- [[q-binary-search--algorithms--easy]]
- [[q-search-rotated-array--algorithms--medium]]
- [[q-median-sorted-arrays--algorithms--hard]]

### Dynamic Programming

- [[q-fibonacci--algorithms--easy]]
- [[q-coin-change--algorithms--medium]]
- [[q-longest-increasing-subsequence--algorithms--hard]]
```

## Error Handling

### Invalid Topic

**Problem**: Topic not in TAXONOMY.md

**Solution**:
1. Report error
2. List valid topics from TAXONOMY.md
3. Ask user to choose valid topic
4. Do NOT proceed with invalid topic

### No Content for Topic

**Problem**: No existing notes for this topic

**Solution**:
1. Create MOC with empty/placeholder sections
2. Note that content should be added as notes are created
3. Include instructions for populating MOC
4. Still valuable as placeholder for future content

### MOC Already Exists

**Problem**: MOC for this topic already exists

**Solution**:
1. Read existing MOC
2. Inform user it exists
3. Offer to update/enhance existing MOC
4. Add newly created notes if user confirms

## Integration with Other Skills

**Common workflows**:

1. **Create MOC when starting new topic**:
   → Use `obsidian-moc-creator` to create structure
   → Use `obsidian-qna-creator` to add questions
   → Update MOC periodically with new questions

2. **Update MOC after bulk creation**:
   → Create multiple Q&As with `obsidian-qna-creator`
   → Regenerate or update MOC to include new notes
   → Organize by subtopic and difficulty

3. **Use MOC for study planning**:
   → Review MOC study paths
   → Create questions based on gaps
   → Use Dataview stats to track progress

## Notes

**Navigation**: MOCs are primary navigation structure for vault. Each topic should have one MOC.

**Maintenance**: MOCs should be updated as content grows. Use Dataview queries for automatic updates where possible.

**Study Guide**: MOCs serve as study guides, organizing content by difficulty and subtopic for learners.

**Flexibility**: MOC structure can be adapted to topic needs - some topics benefit from more granular subtopic organization.

---

**Version**: 1.0
**Last Updated**: 2025-11-09
**Status**: Production Ready
