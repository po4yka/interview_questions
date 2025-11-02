---
date created: Saturday, October 18th 2025, 1:36:05 pm
date modified: Saturday, November 1st 2025, 5:43:38 pm
---

# Controlled Vocabularies & Taxonomy

**Purpose**: Single source of truth for all controlled vocabularies used in YAML frontmatter across the vault.

**Last Updated**: 2025-10-18

---

## Overview

This document defines all valid values for YAML frontmatter fields in Q&A notes, Concept notes, and MOC notes. All LLM agents and human editors MUST use only these controlled values to ensure consistency and enable automated queries.

**Critical Rules**:
- REQUIRED: Use exact spelling and kebab-case as shown
- REQUIRED: Choose values from this file only
- FORBIDDEN: Creating custom values not listed here
- FORBIDDEN: Using multiple values for single-value fields (e.g., `topic`)

---

## 1. Topic (Single Value Required)

**Field**: `topic`
**Type**: String (single value only)
**Rule**: MUST choose exactly ONE topic from this list

### Valid Topics

```yaml
# Core Technical Topics
algorithms                  # Coding problems, data structure manipulation
data-structures            # Theory and implementation of data structures
system-design              # Scalability, architecture, distributed systems
android                    # Android platform, framework, Jetpack
kotlin                     # Kotlin language features and stdlib
programming-languages      # Language comparisons, paradigms, general PL theory

# Architecture & Patterns
architecture-patterns      # Design patterns, SOLID, architectural styles
concurrency               # Multithreading, synchronization, parallel computing
distributed-systems       # CAP, consensus, replication, partitioning
databases                 # SQL, NoSQL, indexing, transactions

# Infrastructure & Systems
networking                # HTTP, TCP/IP, protocols, APIs
operating-systems         # OS concepts, processes, memory management
security                  # Authentication, encryption, vulnerabilities
performance              # Optimization, profiling, benchmarking
cloud                    # AWS, GCP, Azure, cloud-native patterns

# Development Practices
testing                  # Unit, integration, E2E testing
devops-ci-cd            # CI/CD pipelines, deployment, automation
tools                   # Git, build systems, IDEs, productivity tools
debugging               # Debugging techniques, tools, strategies

# Other
ui-ux-accessibility     # User interface, user experience, accessibility
behavioral              # Non-technical interview questions
cs                      # General computer science fundamentals
```

### Topic → Folder Mapping

| Topic                  | Folder              | Notes                          |
|------------------------|---------------------|--------------------------------|
| `algorithms`           | `20-Algorithms/`    | Coding problems, LeetCode      |
| `data-structures`      | `20-Algorithms/`    | Can also go to 60-CompSci/     |
| `system-design`        | `30-System-Design/` | Design questions               |
| `android`              | `40-Android/`       | Android platform questions     |
| `kotlin`               | `70-Kotlin/`        | Kotlin language questions      |
| `programming-languages`| `70-Kotlin/`        | Language theory, comparisons   |
| `databases`            | `50-Backend/`       | Database questions             |
| `networking`           | `50-Backend/`       | Can also go to 60-CompSci/     |
| `operating-systems`    | `60-CompSci/`       | OS fundamentals                |
| `concurrency`          | `60-CompSci/`       | Or 70-Kotlin/ if Kotlin-specific |
| `distributed-systems`  | `30-System-Design/` | Or 60-CompSci/                 |
| `tools`                | `80-Tools/`         | Git, build systems, etc.       |
| `testing`              | `60-CompSci/`       | General testing theory         |
| `security`             | `60-CompSci/`       | Or 40-Android/ if Android-specific |
| `performance`          | `60-CompSci/`       | Or 40-Android/ if Android-specific |
| `cs`                   | `60-CompSci/`       | General CS topics              |

**Rule**: File MUST be placed in folder matching its primary topic.

---

## 2. Subtopics (1-3 Values)

**Field**: `subtopics`
**Type**: Array of strings
**Rule**: Choose 1-3 subtopics relevant to the note

### General Subtopics (All Topics)

For non-Android topics, subtopics are flexible but should be descriptive and consistent:

```yaml
# Algorithm Subtopics (examples)
arrays, hash-map, linked-list, trees, graphs, dp, greedy, backtracking,
two-pointers, sliding-window, binary-search, sorting, heap, stack, queue

# System Design Subtopics (examples)
scalability, load-balancing, caching, databases, message-queues,
rate-limiting, cdn, sharding, replication, consistency, availability

# Kotlin Subtopics (examples)
coroutines, flow, collections, generics, dsl, scope-functions,
type-system, null-safety, delegation, sealed-classes

# Database Subtopics (examples)
sql, nosql, indexing, transactions, acid, cap-theorem, normalization,
query-optimization, replication, sharding
```

### Android Subtopics (When topic=android)

**CRITICAL**: For Android notes, subtopics MUST come from this controlled list and MUST be mirrored to tags as `android/<subtopic>`.

```yaml
# UI & Compose
ui-compose, ui-views, ui-navigation, ui-state, ui-animation, ui-theming,
ui-accessibility, ui-graphics, ui-widgets

# Architecture
architecture-mvvm, architecture-mvi, architecture-clean,
architecture-modularization, di-hilt, di-koin,
feature-flags-remote-config

# Lifecycle & Components
lifecycle, activity, fragment, service, broadcast-receiver,
content-provider, app-startup, processes

# Concurrency
coroutines, flow, threads-sync, background-execution

# Data & Storage
room, sqldelight, datastore, files-media, serialization, cache-offline

# Networking
networking-http, websockets, grpc, graphql, connectivity-caching

# Performance
performance-startup, performance-rendering, performance-memory,
performance-battery, strictmode-anr, profiling

# Testing
testing-unit, testing-instrumented, testing-ui, testing-screenshot,
testing-benchmark, testing-mocks

# Build & Tooling
gradle, build-variants, dependency-management, static-analysis,
ci-cd, versioning

# Distribution
app-bundle, play-console, in-app-updates, in-app-review,
billing, instant-apps

# Security
permissions, keystore-crypto, obfuscation, network-security-config,
privacy-sdks

# Device Features
camera, media, location, bluetooth, nfc, sensors, notifications,
intents-deeplinks, shortcuts-widgets

# Localization
i18n-l10n, a11y

# Multiplatform
kmp, compose-multiplatform

# Form Factors
wear, tv, auto, foldables-chromeos

# Monitoring
analytics, logging-tracing, crash-reporting, monitoring-slo

# Engagement
ads, engagement-retention, ab-testing
```

**Android Rule**: MUST mirror subtopics to tags like this:

```yaml
# CORRECT
topic: android
subtopics: [ui-compose, lifecycle, coroutines]
tags: [android/ui-compose, android/lifecycle, android/coroutines, difficulty/medium]

# WRONG - Missing android/* tags
topic: android
subtopics: [ui-compose, lifecycle]
tags: [compose, lifecycle, difficulty/medium]
```

---

## 3. Difficulty

**Field**: `difficulty`
**Type**: String (single value)
**Rule**: MUST choose exactly ONE difficulty level

### Valid Difficulty Levels

```yaml
easy      # Straightforward, basic concepts, simple implementation
medium    # Moderate complexity, multiple concepts, standard patterns
hard      # Complex, advanced concepts, tricky edge cases
```

**Tag Rule**: MUST include `difficulty/<level>` tag:

```yaml
difficulty: medium
tags: [difficulty/medium, ...]
```

---

## 4. Question Kind

**Field**: `question_kind`
**Type**: String (single value)
**Rule**: MUST choose exactly ONE question type

### Valid Question Kinds

```yaml
coding          # Implement algorithm/function, write code solution
theory          # Explain concepts, describe trade-offs
system-design   # Design scalable systems, architecture
android         # Android-specific implementation or theory
```

### Question Kind Selection Guide

| Topic                  | Typical question_kind | Notes                              |
|------------------------|-----------------------|------------------------------------|
| `algorithms`           | `coding`              | Algorithm implementation           |
| `data-structures`      | `coding` or `theory`  | Depends on question                |
| `system-design`        | `system-design`       | Almost always system-design        |
| `android`              | `android` or `theory` | android if implementation-focused  |
| `kotlin`               | `coding` or `theory`  | Depends on question                |
| `programming-languages`| `theory`              | Usually conceptual                 |
| `databases`            | `theory`              | SQL queries can be `coding`        |
| `operating-systems`    | `theory`              | Usually conceptual                 |
| `tools`                | `theory`              | Usually conceptual                 |

---

## 5. Status

**Field**: `status`
**Type**: String (single value)
**Rule**: Indicates review/completion status

### Valid Status Values

```yaml
draft      # Created by LLM or human, not yet reviewed
reviewed   # Reviewed by human, minor edits may be needed
ready      # Fully reviewed and approved, production-ready
retired    # Deprecated, moved to 99-Archive/ (if exists)
```

**LLM Agent Rule**: ALWAYS set `status: draft` for notes you create or modify. Only humans can promote to `reviewed` or `ready`.

---

## 6. Original Language

**Field**: `original_language`
**Type**: String (single value)
**Rule**: Indicates which language the question was originally written in

### Valid Original Language Values

```yaml
en    # Originally in English
ru    # Originally in Russian
```

---

## 7. Language Tags

**Field**: `language_tags`
**Type**: Array of strings
**Rule**: Indicates which languages are present in the note

### Valid Language Tag Values

```yaml
[en]        # Only English sections present
[ru]        # Only Russian sections present
[en, ru]    # Both English and Russian sections present (GOAL)
```

**Target**: All notes should eventually have `[en, ru]`.

---

## 8. Tags (Flexible, English-Only)

**Field**: `tags`
**Type**: Array of strings
**Rule**: English-only, namespaced where appropriate

### Tag Categories & Examples

#### Required Tags

```yaml
# Difficulty (REQUIRED for all Q&A notes)
difficulty/easy
difficulty/medium
difficulty/hard

# Android subtopic mirrors (REQUIRED for Android notes)
android/ui-compose
android/lifecycle
android/coroutines
# ... etc.
```

#### Recommended Namespace Tags

```yaml
# Language tags (for code examples)
lang/en, lang/ru, lang/kotlin, lang/java, lang/python, lang/sql

# Platform tags
platform/android, platform/web, platform/backend, platform/ios

# Topic tags (redundant with topic field, but useful for queries)
topic/algorithms, topic/android, topic/system-design

# Source tags
leetcode, neetcode, hackerrank, system-design-primer, cracking-coding-interview
```

#### Technique & Concept Tags (Flexible)

```yaml
# Algorithm techniques
two-pointers, sliding-window, binary-search, dp, greedy, backtracking,
dfs, bfs, union-find, topological-sort, bit-manipulation

# Data structures
arrays, hash-map, linked-list, trees, graphs, heap, stack, queue, trie

# System design concepts
scalability, load-balancing, caching, sharding, replication,
rate-limiting, cdn, message-queue, microservices

# Android concepts
compose, jetpack, viewmodel, livedata, room, retrofit, coroutines, flow

# General concepts
concurrency, multithreading, recursion, immutability, polymorphism
```

**Critical Rule**: ALL tags MUST be in English. Russian text goes in `aliases` field and content sections only.

```yaml
# CORRECT
tags: [leetcode, arrays, hash-map, difficulty/easy]

# WRONG - Russian in tags
tags: [leetcode, массивы, хеш-таблица, difficulty/easy]
```

---

## 9. MOC (Single Link Required)

**Field**: `moc`
**Type**: String (single MOC link WITHOUT brackets)
**Rule**: Link to at least one Map of Content

### Available MOCs

```yaml
moc-algorithms        # For algorithms, data-structures topics
moc-system-design     # For system-design, distributed-systems topics
moc-android           # For android topic
moc-kotlin            # For kotlin, programming-languages topics
moc-backend           # For databases, networking (backend) topics
moc-cs                # For os, concurrency, cs topics
moc-tools             # For tools topic
```

**Format**: WITHOUT brackets in YAML

```yaml
# CORRECT
moc: moc-algorithms

# WRONG
moc: [[moc-algorithms]]
moc: [moc-algorithms]
```

---

## 10. Related (Array of Links)

**Field**: `related`
**Type**: Array of strings (2-5 recommended)
**Rule**: Links to related concepts and questions WITHOUT brackets

### Format

```yaml
# CORRECT
related: [c-hash-map, c-array, q-three-sum--algorithms--medium]

# WRONG - Using brackets around each item
related: [[c-hash-map]], [[c-array]]

# WRONG - Empty
related: []
```

### Related Link Types

```yaml
# Concept links (c-<slug>)
c-hash-map, c-binary-tree, c-mvvm-pattern, c-coroutines

# Question links (q-<slug>--<topic>--<difficulty>)
q-two-sum--algorithms--easy
q-design-url-shortener--system-design--medium
q-jetpack-compose-state--android--medium

# MOC links (moc-<topic>)
moc-algorithms, moc-android
```

**Recommendation**: Include 2-3 concept links and 2-3 question links for good cross-referencing.

---

## Examples by Topic

### Example 1: Algorithm Q&A

```yaml
---
id: 20251018-120000
title: Two Sum / Два слагаемых
aliases: [Two Sum, Два слагаемых]

# Classification
topic: algorithms                      # ONE from list above
subtopics: [arrays, hash-map]         # 1-3 relevant subtopics
question_kind: coding                  # Type of question
difficulty: easy                       # easy | medium | hard

# Language
original_language: en                  # en | ru
language_tags: [en, ru]               # Which languages present

# Workflow
status: draft                          # draft | reviewed | ready

# Links (WITHOUT brackets in YAML)
moc: moc-algorithms
related: [c-hash-map, c-array, q-three-sum--algorithms--medium]

# Timestamps
created: 2025-10-18
updated: 2025-10-18

# Tags (English only, include difficulty/)
tags: [leetcode, arrays, hash-map, difficulty/easy]
---
```

### Example 2: Android Q&A

```yaml
---
id: 20251018-120100
title: Jetpack Compose State / Состояние в Compose
aliases: [Compose State, Состояние Compose]

# Classification
topic: android                         # Android topic
subtopics: [ui-compose, ui-state, architecture-mvvm]  # Android subtopics
question_kind: android                 # Android implementation
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

### Example 3: System Design Q&A

```yaml
---
id: 20251018-120200
title: Design URL Shortener / Проектирование сокращателя URL
aliases: [URL Shortener Design, Проектирование URL Shortener]

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

### Example 4: Kotlin Q&A

```yaml
---
id: 20251018-120300
title: Kotlin Coroutines Basics / Основы корутин Kotlin
aliases: [Coroutines Basics, Основы корутин]

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

---

## Validation Checklist

Before finalizing any note, verify:

- [ ] `topic` is exactly ONE value from section 1
- [ ] `subtopics` has 1-3 values (Android: from Android list)
- [ ] `difficulty` is easy | medium | hard
- [ ] `question_kind` is coding | theory | system-design | android
- [ ] `original_language` is en | ru
- [ ] `language_tags` is [en] or [ru] or [en, ru]
- [ ] `status` is draft | reviewed | ready
- [ ] `moc` is single link WITHOUT brackets
- [ ] `related` is array of 2+ links WITHOUT brackets
- [ ] `tags` are English-only
- [ ] `tags` include `difficulty/<level>`
- [ ] For Android: `tags` include `android/<subtopic>` for each subtopic
- [ ] File is in folder matching `topic`

---

## Common Mistakes

### WRONG: Multiple Topics
```yaml
topic: [algorithms, data-structures]  # FORBIDDEN - only ONE topic
```

### WRONG: Brackets in moc/related
```yaml
moc: [[moc-algorithms]]               # FORBIDDEN - no brackets
related: [[c-hash-map]], [[c-array]]  # FORBIDDEN - array without double brackets
```

### WRONG: Russian in Tags
```yaml
tags: [массивы, хеш-таблица]          # FORBIDDEN - English only
```

### WRONG: Android without android/* Tags
```yaml
topic: android
subtopics: [ui-compose, lifecycle]
tags: [compose, lifecycle]            # FORBIDDEN - missing android/* tags
```

### CORRECT: Proper Android Note
```yaml
topic: android
subtopics: [ui-compose, lifecycle]
tags: [android/ui-compose, android/lifecycle, compose, difficulty/medium]
```

---

## References

- **Full vault rules**: `00-Administration/README.md`
- **Agent instructions**: `00-Administration/AGENTS.md`
- **Quick checklist**: `00-Administration/AGENT-CHECKLIST.md`
- **Link health monitoring**: `00-Administration/LINK-HEALTH-DASHBOARD.md`
- **Templates**: `_templates/_tpl-qna.md`, `_tpl-concept.md`, `_tpl-moc.md`
- **Cursor AI rules**: `.cursor/rules/` (modern MDC format)
- **Claude Code**: `.claude/README.md`, `.claude/custom_instructions.md`
- **Gemini CLI guide**: `GEMINI.md`

---

**Last Updated**: 2025-10-18
**Maintained By**: Vault administrators and LLM agents
**Version**: 2.0 (Expanded and optimized)
