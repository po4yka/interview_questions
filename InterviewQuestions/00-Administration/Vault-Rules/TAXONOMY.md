---
date created: Tuesday, November 25th 2025, 8:30:06 pm
date modified: Tuesday, November 25th 2025, 8:54:04 pm
---

# Controlled Vocabularies & Taxonomy

**Purpose**: Single source of truth for all YAML frontmatter controlled values.
**Last Updated**: 2025-11-25

**Critical Rules**:
- REQUIRED: Use exact spelling and kebab-case as shown
- REQUIRED: Choose values from this file only
- FORBIDDEN: Creating custom values not listed here
- FORBIDDEN: Using multiple values for single-value fields

## 1. Topic (Single Value Required)

**Field**: `topic`
**Type**: String (single value only)

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

### Topic -> Folder Mapping

| Topic | Folder | MOC |
|-------|--------|-----|
| `algorithms` | `20-Algorithms/` | `moc-algorithms` |
| `data-structures` | `20-Algorithms/` | `moc-algorithms` |
| `system-design` | `30-System-Design/` | `moc-system-design` |
| `android` | `40-Android/` | `moc-android` |
| `databases` | `50-Backend/` | `moc-backend` |
| `networking` | `50-Backend/` | `moc-backend` |
| `operating-systems` | `60-CompSci/` | `moc-cs` |
| `concurrency` | `60-CompSci/` | `moc-cs` |
| `cs` | `60-CompSci/` | `moc-cs` |
| `kotlin` | `70-Kotlin/` | `moc-kotlin` |
| `programming-languages` | `70-Kotlin/` | `moc-kotlin` |
| `tools` | `80-Tools/` | `moc-tools` |

## 2. Subtopics (1-3 Values)

**Field**: `subtopics`
**Type**: Array of strings

### General Subtopics

For non-Android topics, subtopics are flexible:

```yaml
# Algorithm Subtopics
arrays, hash-map, linked-list, trees, graphs, dp, greedy, backtracking,
two-pointers, sliding-window, binary-search, sorting, heap, stack, queue

# System Design Subtopics
scalability, load-balancing, caching, databases, message-queues,
rate-limiting, cdn, sharding, replication, consistency, availability

# Kotlin Subtopics
coroutines, flow, collections, generics, dsl, scope-functions,
type-system, null-safety, delegation, sealed-classes

# Database Subtopics
sql, nosql, indexing, transactions, acid, cap-theorem, normalization,
query-optimization, replication, sharding
```

### Android Subtopics

**For Android notes**, see [[ANDROID-SUBTOPICS]] for the complete controlled list.

**Android Rule**: MUST mirror subtopics to tags as `android/<subtopic>`.

## 3. Difficulty

**Field**: `difficulty`
**Type**: String (single value)

```yaml
easy      # Straightforward, basic concepts, simple implementation
medium    # Moderate complexity, multiple concepts, standard patterns
hard      # Complex, advanced concepts, tricky edge cases
```

**Tag Rule**: MUST include `difficulty/<level>` tag.

## 4. Question Kind

**Field**: `question_kind`
**Type**: String (single value)

```yaml
coding          # Implement algorithm/function, write code solution
theory          # Explain concepts, describe trade-offs
system-design   # Design scalable systems, architecture
android         # Android-specific implementation or theory
```

## 5. Status

**Field**: `status`
**Type**: String (single value)

```yaml
draft      # Created by LLM or human, not yet reviewed
reviewed   # Reviewed by human, minor edits may be needed
ready      # Fully reviewed and approved, production-ready
retired    # Deprecated, moved to archive
```

**LLM Rule**: ALWAYS set `status: draft` for notes you create or modify.

## 6. Language Fields

### Original Language

**Field**: `original_language`
**Type**: String (single value)

```yaml
en    # Originally in English
ru    # Originally in Russian
```

### Language Tags

**Field**: `language_tags`
**Type**: Array of strings

```yaml
[en]        # Only English sections present
[ru]        # Only Russian sections present
[en, ru]    # Both English and Russian sections present (GOAL)
```

## 7. MOC (Single Link)

**Field**: `moc`
**Type**: String (WITHOUT brackets)

```yaml
moc-algorithms        # For algorithms, data-structures topics
moc-system-design     # For system-design, distributed-systems topics
moc-android           # For android topic
moc-kotlin            # For kotlin, programming-languages topics
moc-backend           # For databases, networking topics
moc-cs                # For os, concurrency, cs topics
moc-tools             # For tools topic
```

**Format**:
```yaml
# CORRECT
moc: moc-algorithms

# WRONG
moc: [[moc-algorithms]]
```

## 8. Related (Array of Links)

**Field**: `related`
**Type**: Array of strings (2-5 recommended, WITHOUT brackets)

```yaml
# CORRECT
related: [c-hash-map, c-array, q-three-sum--algorithms--medium]

# WRONG
related: [[c-hash-map]], [[c-array]]
```

## 9. Tags (English Only)

**Field**: `tags`
**Type**: Array of strings

### Required Tags

```yaml
# Difficulty (REQUIRED)
difficulty/easy
difficulty/medium
difficulty/hard

# Android subtopic mirrors (REQUIRED for Android)
android/ui-compose
android/lifecycle
```

### Optional Tags

```yaml
# Platform
platform/android, platform/web, platform/backend

# Technique
two-pointers, sliding-window, binary-search, dp

# Source
leetcode, neetcode, system-design-primer
```

**Critical**: ALL tags MUST be in English.

## Validation Checklist

- [ ] `topic` is exactly ONE value from section 1
- [ ] `subtopics` has 1-3 values
- [ ] `difficulty` is easy | medium | hard
- [ ] `question_kind` is coding | theory | system-design | android
- [ ] `original_language` is en | ru
- [ ] `language_tags` is [en] or [ru] or [en, ru]
- [ ] `status` is draft | reviewed | ready
- [ ] `moc` is single link WITHOUT brackets
- [ ] `related` is array of 2+ links WITHOUT brackets
- [ ] `tags` are English-only
- [ ] `tags` include `difficulty/<level>`
- [ ] For Android: `tags` include `android/<subtopic>`

## See Also

- [[ANDROID-SUBTOPICS]] - Complete Android subtopics list
- [[YAML-EXAMPLES]] - Full YAML examples by topic
- [[FILE-NAMING-RULES]] - File naming conventions
- [[AGENT-CHECKLIST]] - Quick reference for AI agents
