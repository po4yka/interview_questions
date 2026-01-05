---
name: study-path-builder
description: >
  Create learning progressions and study paths. Builds easy-to-medium-to-hard
  chains, suggests prerequisite relationships, generates study guides, and creates
  progression MOCs. Helps users navigate the vault in a structured learning sequence
  rather than random access.
---

# Study Path Builder

## Purpose

Create structured learning progressions through the vault:

1. **Difficulty Chains**: Build easy → medium → hard sequences
2. **Prerequisite Mapping**: Define what to learn before what
3. **Study Guides**: Generate ordered learning plans
4. **Progression MOCs**: Create navigation-focused MOCs
5. **Custom Paths**: Build paths for specific learning goals

## When to Use

Activate this skill when user requests:
- "Create a learning path for [topic]"
- "Build study progression"
- "What should I learn first?"
- "Order these topics by difficulty"
- "Create a study guide"
- "What's the best learning sequence?"
- When organizing content for learners
- When creating course-like structures

## Prerequisites

Required context:
- Vault content with difficulty levels
- Topic and subtopic relationships
- Understanding of concept dependencies

## Process

### Step 1: Analyze Available Content

Map content by topic and difficulty:

```
Topic: kotlin
├── easy (45 questions)
│   ├── basics
│   ├── null-safety
│   └── functions
├── medium (201 questions)
│   ├── coroutines
│   ├── collections
│   └── generics
└── hard (112 questions)
    ├── advanced-coroutines
    ├── DSL
    └── compiler-plugins
```

### Step 2: Identify Prerequisites

Determine concept dependencies:

```
Prerequisite mapping:
- coroutines requires: basics, functions, lambdas
- flow requires: coroutines, collections
- channels requires: coroutines, concurrency
- advanced-coroutines requires: coroutines, flow, channels

Dependency graph:
basics → functions → lambdas → coroutines → flow
                              ↓
                           channels → advanced-coroutines
```

### Step 3: Build Progression Chains

Create ordered sequences:

```
Kotlin Coroutines Path:
1. [EASY] What is Kotlin? (basics)
2. [EASY] Functions in Kotlin (functions)
3. [EASY] Lambda expressions (lambdas)
4. [EASY] What is a coroutine? (coroutines-intro)
5. [MEDIUM] Coroutine context and dispatchers
6. [MEDIUM] Structured concurrency
7. [MEDIUM] Coroutine scope
8. [MEDIUM] Flow basics
9. [HARD] Flow operators deep dive
10. [HARD] Channel patterns
11. [HARD] Exception handling in coroutines
```

### Step 4: Group by Learning Phase

Organize into study phases:

```
Phase 1: Foundations (Week 1)
- 5 easy questions covering basics
- Goal: Understand Kotlin fundamentals

Phase 2: Core Concepts (Week 2-3)
- 8 medium questions on coroutines
- Goal: Working knowledge of async

Phase 3: Advanced Topics (Week 4)
- 5 hard questions on advanced patterns
- Goal: Expert-level understanding

Phase 4: Practice & Review
- Mixed difficulty review questions
- Goal: Solidify knowledge
```

### Step 5: Generate Study Guide

Create comprehensive learning plan:

```markdown
# Kotlin Coroutines Study Guide

## Overview
This guide takes you from Kotlin basics to advanced coroutine patterns.

**Duration**: 4 weeks
**Prerequisites**: Basic programming knowledge
**Goal**: Master Kotlin coroutines for Android development

---

## Phase 1: Foundations (5 questions)

### Learning Objectives
- Understand Kotlin syntax basics
- Write simple functions
- Use lambda expressions

### Questions to Study

1. **[[q-kotlin-basics--kotlin--easy]]**
   - What is Kotlin and why use it?
   - Time: 15 min

2. **[[q-kotlin-functions--kotlin--easy]]**
   - Function syntax and parameters
   - Time: 20 min

3. **[[q-null-safety--kotlin--easy]]**
   - Nullable types and safe calls
   - Time: 25 min

4. **[[q-lambdas-intro--kotlin--easy]]**
   - Lambda syntax and usage
   - Time: 20 min

5. **[[q-higher-order-functions--kotlin--easy]]**
   - Functions as parameters
   - Time: 25 min

### Checkpoint
After Phase 1, you should be able to:
- [ ] Write basic Kotlin functions
- [ ] Handle nullable types safely
- [ ] Use lambda expressions

---

## Phase 2: Core Coroutines (8 questions)

### Learning Objectives
- Understand coroutine basics
- Use suspending functions
- Apply structured concurrency

### Questions to Study

6. **[[q-what-is-coroutine--kotlin--easy]]**
   - Introduction to coroutines
   - Time: 30 min
   - Prerequisite: q-lambdas-intro

7. **[[q-coroutine-context--kotlin--medium]]**
   - Context and dispatchers
   - Time: 45 min
   - Prerequisite: q-what-is-coroutine

[... continues ...]

---

## Phase 3: Advanced Patterns (5 questions)

[... advanced content ...]

---

## Phase 4: Review & Practice

### Review Questions
Mixed selection for comprehensive review:
1. [[q-coroutine-review-1--kotlin--medium]]
2. [[q-flow-review--kotlin--medium]]
3. [[q-channels-practice--kotlin--hard]]

### Self-Assessment
- [ ] Can explain coroutine lifecycle
- [ ] Can implement Flow collectors
- [ ] Can handle exceptions properly
- [ ] Can choose appropriate dispatcher

---

## Additional Resources

### Related Concepts
- [[c-coroutines]]
- [[c-structured-concurrency]]
- [[c-flow]]

### External Resources
- Kotlin Coroutines Guide (official docs)
- Android Coroutines Codelab

---

**Estimated Total Time**: 15-20 hours
**Recommended Pace**: 1 hour/day for 3 weeks
```

### Step 6: Create Progression MOC

Generate MOC focused on learning order:

```markdown
# MOC: Kotlin Coroutines Learning Path

> Structured progression from basics to advanced coroutine patterns.

## Quick Navigation

| Phase | Focus | Questions |
|-------|-------|-----------|
| 1 | Foundations | 5 easy |
| 2 | Core Concepts | 8 medium |
| 3 | Advanced | 5 hard |
| 4 | Review | 5 mixed |

---

## Phase 1: Foundations

```dataview
TABLE difficulty, question_kind
FROM "70-Kotlin"
WHERE contains(subtopics, "basics") OR contains(subtopics, "functions")
WHERE difficulty = "easy"
SORT file.name ASC
```

### Recommended Order
1. [[q-kotlin-basics--kotlin--easy]] - Start here
2. [[q-kotlin-functions--kotlin--easy]]
3. [[q-null-safety--kotlin--easy]]
4. [[q-lambdas-intro--kotlin--easy]]
5. [[q-higher-order-functions--kotlin--easy]]

---

## Phase 2: Core Concepts

[... structured content ...]

---

## Progress Tracker

- [ ] Phase 1 Complete
- [ ] Phase 2 Complete
- [ ] Phase 3 Complete
- [ ] Phase 4 Complete

---

**Path maintained by study-path-builder skill**
```

## Examples

### Example 1: Build Topic Path

**User**: "Create a learning path for Kotlin coroutines"

**Output**:
```markdown
# Kotlin Coroutines Learning Path

## Summary
18 questions across 4 phases
Estimated time: 15 hours

## Path Overview

### Phase 1: Foundations (5 questions, 2 hours)
1. [EASY] Kotlin basics
2. [EASY] Functions and lambdas
3. [EASY] Higher-order functions
4. [EASY] What is a coroutine?
5. [EASY] Suspending functions

### Phase 2: Core (8 questions, 6 hours)
6. [MEDIUM] Coroutine context
7. [MEDIUM] Dispatchers
8. [MEDIUM] Coroutine scope
9. [MEDIUM] Structured concurrency
10. [MEDIUM] Flow basics
11. [MEDIUM] Flow operators
12. [MEDIUM] StateFlow and SharedFlow
13. [MEDIUM] Exception handling

### Phase 3: Advanced (5 questions, 5 hours)
14. [HARD] Channel patterns
15. [HARD] Custom Flow operators
16. [HARD] Testing coroutines
17. [HARD] Performance optimization
18. [HARD] Complex async patterns

Full study guide created: moc-kotlin-coroutines-path.md
```

### Example 2: Prerequisite Analysis

**User**: "What should I learn before Flow?"

**Output**:
```markdown
# Prerequisites for Kotlin Flow

## Required Knowledge (Must Learn First)

### 1. Kotlin Basics
- [[q-kotlin-basics--kotlin--easy]]
- [[q-kotlin-functions--kotlin--easy]]

### 2. Lambda Expressions
- [[q-lambdas-intro--kotlin--easy]]
- [[q-higher-order-functions--kotlin--easy]]

### 3. Coroutine Fundamentals
- [[q-what-is-coroutine--kotlin--easy]]
- [[q-coroutine-context--kotlin--medium]]
- [[q-suspending-functions--kotlin--medium]]

## Recommended Order
1. Kotlin basics → 2. Lambdas → 3. Coroutines → 4. Flow

## Time to Reach Flow
- If starting from scratch: ~8 hours
- If know Kotlin basics: ~4 hours
- If know coroutines: Ready now
```

### Example 3: Custom Goal Path

**User**: "Create a path for Android interviews focusing on architecture"

**Output**:
```markdown
# Android Architecture Interview Path

## Goal
Prepare for senior Android developer interviews with focus on architecture.

## Path (25 questions, 20 hours)

### Week 1: Architecture Fundamentals
1. [EASY] Android app components
2. [EASY] Activity lifecycle
3. [MEDIUM] ViewModel basics
4. [MEDIUM] LiveData vs StateFlow
5. [MEDIUM] MVVM pattern

### Week 2: Clean Architecture
6. [MEDIUM] Clean architecture layers
7. [MEDIUM] Use cases / Interactors
8. [MEDIUM] Repository pattern
9. [HARD] Domain layer design
10. [HARD] Modularization

### Week 3: Dependency Injection
11. [EASY] Why DI?
12. [MEDIUM] Hilt basics
13. [MEDIUM] Scopes and components
14. [HARD] Custom Hilt modules
15. [HARD] Testing with DI

### Week 4: Advanced & Review
16. [HARD] MVI pattern
17. [HARD] Multi-module navigation
18. [HARD] Architecture for scale
19-25. Review questions

## Interview Prep Tips
- Focus on "why" not just "how"
- Be ready to draw diagrams
- Know trade-offs of each pattern
```

### Example 4: Difficulty Progression

**User**: "Order all Android Compose questions by learning difficulty"

**Output**:
```markdown
# Compose Learning Progression

Total: 87 questions

## Level 1: Getting Started (15 questions)
- Composable basics
- Column/Row/Box
- Modifiers intro
- Text and images
- Basic state

## Level 2: Building UIs (25 questions)
- Lists and lazy components
- Input handling
- Navigation basics
- Theming
- Preview

## Level 3: State Management (20 questions)
- remember and rememberSaveable
- State hoisting
- ViewModel integration
- Side effects
- CompositionLocal

## Level 4: Advanced (17 questions)
- Custom layouts
- Animation
- Performance
- Testing Compose
- Interop with Views

## Level 5: Expert (10 questions)
- Custom modifiers
- Advanced animations
- Semantics
- Compiler internals
- Large app architecture

Study guide: moc-compose-progression.md
```

## Error Handling

### Insufficient Content

**Problem**: Not enough questions for complete path

**Solution**:
1. Use available content
2. Note gaps in progression
3. Suggest creating missing questions
4. Link to external resources if needed

### Circular Dependencies

**Problem**: A requires B, B requires A

**Solution**:
1. Detect cycles in prerequisite graph
2. Break cycle at most logical point
3. Note co-requisites (learn together)

### Missing Difficulty Levels

**Problem**: Topic has no easy questions

**Solution**:
1. Note missing level
2. Suggest starting from available level
3. Recommend creating entry-level content

## Integration with Other Skills

**Workflow: Course Creation**
1. Use `gap-analyzer` to check coverage
2. Create missing content with `obsidian-qna-creator`
3. Build path with `study-path-builder`
4. Create MOC with `obsidian-moc-creator`

**Workflow: Learner Guidance**
1. User asks "where to start?"
2. Run `study-path-builder` for topic
3. Provide structured progression
4. Track progress through path

## Path Options

### Auto Path (Default)
```
Automatically determine best order based on
difficulty and inferred prerequisites.
```

### Custom Prerequisites
```
Allow manual prerequisite definitions for
more accurate ordering.
```

### Goal-Oriented
```
--goal "Android interview prep"
Build path optimized for specific goal.
```

### Time-Limited
```
--hours 10
Build path fitting within time budget.
```

## Notes

**Pedagogical**: Designed for effective learning sequences.

**Flexible**: Can build paths for any topic or goal.

**Connected**: Creates links between related questions.

**Progressive**: Respects difficulty and prerequisite chains.

**Maintainable**: Paths update as content changes.

---

**Version**: 1.0
**Last Updated**: 2025-01-05
**Status**: Production Ready
