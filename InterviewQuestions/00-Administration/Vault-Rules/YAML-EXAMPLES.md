---
date created: Tuesday, November 25th 2025, 8:31:43 pm
date modified: Tuesday, November 25th 2025, 8:54:04 pm
---

# YAML Examples by Topic

**Purpose**: Complete YAML frontmatter examples for different note types.
**Last Updated**: 2025-11-25

See [[TAXONOMY]] for field definitions and valid values.

## Algorithm Q&A Example

```yaml
---
id: algo-001
title: Two Sum / Dva slagaemykh
aliases: [Two Sum, Dva slagaemykh]

# Classification
topic: algorithms
subtopics: [arrays, hash-map]
question_kind: coding
difficulty: easy

# Language
original_language: en
language_tags: [en, ru]

# Workflow
status: draft

# Links (WITHOUT brackets)
moc: moc-algorithms
related: [c-hash-map, c-array, q-three-sum--algorithms--medium]

# Timestamps
created: 2025-10-18
updated: 2025-10-18

# Tags (English only)
tags: [leetcode, arrays, hash-map, difficulty/easy]
---
```

## Android Q&A Example

```yaml
---
id: android-001
title: Jetpack Compose State / Sostoyanie v Compose
aliases: [Compose State, Sostoyanie Compose]

# Classification
topic: android
subtopics: [ui-compose, ui-state, architecture-mvvm]
question_kind: android
difficulty: medium

# Language
original_language: en
language_tags: [en, ru]

# Workflow
status: draft

# Links
moc: moc-android
related: [c-compose-state, c-viewmodel, q-compose-recomposition--android--medium]

# Timestamps
created: 2025-10-18
updated: 2025-10-18

# Tags (MUST include android/* mirrors)
tags: [android/ui-compose, android/ui-state, android/architecture-mvvm,
       compose, jetpack, difficulty/medium]
---
```

## System Design Q&A Example

```yaml
---
id: sysdes-001
title: Design URL Shortener / Proektirovanie sokrashchatelya URL
aliases: [URL Shortener Design, Proektirovanie URL Shortener]

# Classification
topic: system-design
subtopics: [scalability, databases, caching]
question_kind: system-design
difficulty: medium

# Language
original_language: en
language_tags: [en, ru]

# Workflow
status: draft

# Links
moc: moc-system-design
related: [c-consistent-hashing, c-load-balancing,
          q-design-pastebin--system-design--medium]

# Timestamps
created: 2025-10-18
updated: 2025-10-18

# Tags
tags: [system-design-primer, scalability, databases, caching,
       difficulty/medium]
---
```

## Kotlin Q&A Example

```yaml
---
id: kotlin-001
title: Kotlin Coroutines Basics / Osnovy korutin Kotlin
aliases: [Coroutines Basics, Osnovy korutin]

# Classification
topic: kotlin
subtopics: [coroutines, concurrency]
question_kind: theory
difficulty: medium

# Language
original_language: en
language_tags: [en, ru]

# Workflow
status: draft

# Links
moc: moc-kotlin
related: [c-coroutines, c-structured-concurrency,
          q-coroutine-context--kotlin--hard]

# Timestamps
created: 2025-10-18
updated: 2025-10-18

# Tags
tags: [kotlin, coroutines, concurrency, lang/kotlin, difficulty/medium]
---
```

## Database Q&A Example

```yaml
---
id: db-001
title: SQL JOIN Types / Tipy SQL JOIN
aliases: [SQL JOINs, Tipy JOIN]

# Classification
topic: databases
subtopics: [sql, query-optimization]
question_kind: theory
difficulty: medium

# Language
original_language: en
language_tags: [en, ru]

# Workflow
status: draft

# Links
moc: moc-backend
related: [c-sql-basics, q-sql-indexing--databases--medium]

# Timestamps
created: 2025-10-18
updated: 2025-10-18

# Tags
tags: [sql, databases, query, difficulty/medium]
---
```

## Concept Note Example

```yaml
---
id: concept-viewmodel
title: ViewModel / ViewModel
aliases: [ViewModel, VyuModel, Android ViewModel]

# Classification
kind: concept
topic: android
subtopics: [lifecycle, architecture-mvvm]
summary: Lifecycle-aware component for UI-related data management

# Language
original_language: en
language_tags: [en, ru]

# Workflow
status: draft

# Links
moc: moc-android
related: [c-livedata, c-savedstatehandle, q-what-is-viewmodel--android--medium]

# Timestamps
created: 2025-10-18
updated: 2025-10-18

# Tags
tags: [concept, android, viewmodel, lifecycle, jetpack]
---
```

## MOC Note Example

```yaml
---
id: moc-android
title: Android - MOC
aliases: [Android MOC, Android Map of Content]

# Classification
kind: moc
topic: android

# Timestamps
created: 2025-10-12
updated: 2025-10-12

# Tags
tags: [moc, topic/android]
---
```

## Common Mistakes

### Multiple Topics (WRONG)

```yaml
topic: [algorithms, data-structures]  # FORBIDDEN - only ONE topic
```

### Brackets in MOC/Related (WRONG)

```yaml
moc: [[moc-algorithms]]               # FORBIDDEN - no brackets
related: [[c-hash-map]], [[c-array]]  # FORBIDDEN - no double brackets
```

### Russian in Tags (WRONG)

```yaml
tags: [massivy, khesh-tablitsa]       # FORBIDDEN - English only
```

### Android Without android/* Tags (WRONG)

```yaml
topic: android
subtopics: [ui-compose, lifecycle]
tags: [compose, lifecycle]            # FORBIDDEN - missing android/* tags
```

### Correct Android Tags

```yaml
topic: android
subtopics: [ui-compose, lifecycle]
tags: [android/ui-compose, android/lifecycle, compose, difficulty/medium]
```

## See Also

- [[TAXONOMY]] - Field definitions and valid values
- [[ANDROID-SUBTOPICS]] - Android subtopics list
- [[FILE-NAMING-RULES]] - File naming conventions
- [[AGENT-CHECKLIST]] - Quick reference for AI agents
