---
date created: Sunday, October 19th 2025, 11:19:33 am
date modified: Saturday, November 1st 2025, 5:43:56 pm
---

# Gemini CLI Agent Guide

**Quick reference for using `gemini-cli` with this Obsidian Interview Vault.**

This guide assumes you're using `gemini-cli` (or similar CLI tool) to interact with Gemini models for vault maintenance tasks.

---

## Quick Start

**System Context** (use at start of session):

```
You are helping maintain a bilingual (EN/RU) Obsidian vault for technical interview preparation.

Key rules:
- One note = one Q&A with BOTH English and Russian in the SAME file
- Use YAML frontmatter with controlled vocabularies from TAXONOMY.md
- All tags are English-only (Russian goes in content and aliases)
- Pick exactly ONE topic from TAXONOMY.md
- Always set status: draft for notes you create/modify
- Link every Q&A to ≥1 Concept and ≥1 MOC

Files:
- Full rules: 00-Administration/README.md
- Agent tasks: 00-Administration/AGENTS.md
- Quick checklist: 00-Administration/AGENT-CHECKLIST.md
- Valid topics/subtopics: 00-Administration/TAXONOMY.md
- Templates: _templates/_tpl-qna.md, _tpl-concept.md, _tpl-moc.md

Folders:
- 20-Algorithms/ - coding problems
- 30-System-Design/ - design questions
- 40-Android/ - Android Q&As
- 50-Backend/ - backend/database questions
- 60-CompSci/ - CS fundamentals
- 70-Kotlin/ - Kotlin language questions
- 80-Tools/ - development tools (Git, etc.)
- 10-Concepts/ - theory notes
- 90-MOCs/ - hub pages
```

---

## Common Workflows

### 1. Create New Q&A Note

**Command pattern:**
```bash
gemini "Create a Q&A note about [TOPIC].
Original question: [PASTE QUESTION]
Topic: [algorithms|system-design|android|etc]
Difficulty: [easy|medium|hard]
Include both EN and RU versions."
```

**Example:**
```bash
gemini "Create a Q&A note about Binary Search.
Original question: Implement binary search to find target in sorted array.
Topic: algorithms
Difficulty: easy
Include both EN and RU versions."
```

**What Gemini should do:**
1. Choose filename: `q-binary-search--algorithms--easy.md`
2. Place in: `20-Algorithms/`
3. Use template: `_templates/_tpl-qna.md`
4. Fill YAML with proper values from TAXONOMY.md
5. Write EN and RU sections
6. Set `status: draft`
7. Link to MOC and concepts

### 2. Translate Existing Note

**Command pattern:**
```bash
gemini "Translate [FILE] to [Russian|English].
Keep existing content, add missing language section.
Maintain technical accuracy and code examples."
```

**Example:**
```bash
gemini "Translate 20-Algorithms/q-two-sum--algorithms--easy.md to Russian.
Add 'Вопрос (RU)' and 'Ответ (RU)' sections."
```

### 3. Validate/Fix Note

**Command pattern:**
```bash
gemini "Validate and fix [FILE] according to vault rules.
Check: YAML completeness, tags (EN-only), links to concepts/MOCs,
folder placement, topic from TAXONOMY.md.
List issues and apply fixes."
```

**Example:**
```bash
gemini "Validate 40-Android/q-jetpack-compose--android--medium.md.
Ensure Android subtopics are mirrored to android/* tags."
```

### 4. Create Concept Note

**Command pattern:**
```bash
gemini "Create a Concept note for [CONCEPT_NAME].
Include: EN/RU summaries, use cases, trade-offs, references.
Place in 10-Concepts/."
```

**Example:**
```bash
gemini "Create a Concept note for Hash Map.
Cover: O(1) lookups, collision handling, use cases.
Both EN and RU."
```

### 5. Suggest Cross-Links

**Command pattern:**
```bash
gemini "Analyze [FILE] and suggest 3-5 related concepts and questions.
Add to YAML 'related' field and References section."
```

**Example:**
```bash
gemini "Analyze 20-Algorithms/q-two-sum--algorithms--easy.md.
Suggest related: concepts (hash-map, arrays),
questions (three-sum, pair-sum variations)."
```

### 6. Batch Operations

**Generate multiple notes from list:**
```bash
gemini "Create Q&A notes for these LeetCode problems:
1. Two Sum (easy)
2. Three Sum (medium)
3. Container With Most Water (medium)

For each: topic=algorithms, include EN/RU, proper YAML, status=draft."
```

**Validate multiple files:**
```bash
gemini "Validate all files in 40-Android/.
Check: topic=android, Android subtopics valid, android/* tags present.
List issues by file."
```

---

## File Reading/Writing

### Read Vault Documentation
```bash
gemini "Read 00-Administration/README.md and summarize YAML schema for Q&A notes."
gemini "List all valid topics from 00-Administration/TAXONOMY.md."
gemini "Show Android subtopics from TAXONOMY.md."
```

### Read Templates
```bash
gemini "Show the Q&A template structure from _templates/_tpl-qna.md."
```

### Read/analyze Notes
```bash
gemini "Read 20-Algorithms/q-two-sum--algorithms--easy.md and check if it follows all rules."
gemini "List all notes in 40-Android/ with status=draft."
```

---

## Critical Rules (Always Follow)

### 0. No Emoji in Content
```yaml
# FORBIDDEN: Do not use emoji in vault notes
# Use text equivalents: REQUIRED, FORBIDDEN, WARNING, NOTE
# This applies to ALL content - English, Russian, and code comments
```

### 1. Bilingual = Same File
```yaml
# CORRECT
# File: q-two-sum--algorithms--easy.md
# Question (EN)
Given an array...

# Вопрос (RU)
Дан массив...

# WRONG - Don't create separate files
# q-two-sum-en.md and q-two-sum-ru.md
```

### 2. Tags = English Only
```yaml
# CORRECT
tags: [leetcode, arrays, hash-map, difficulty/easy]

# WRONG
tags: [leetcode, массивы, хеш-таблица]
```

### 3. Topic = Exactly One from TAXONOMY.md
```yaml
# CORRECT
topic: algorithms

# WRONG
topic: [algorithms, data-structures]  # Only ONE
topic: coding  # Invalid - not in TAXONOMY.md
```

### 4. Android Subtopics → Tags
```yaml
# CORRECT (for Android notes)
topic: android
subtopics: [ui-compose, lifecycle]
tags: [android/ui-compose, android/lifecycle, difficulty/medium]

# WRONG
# Missing android/* tags
```

### 5. Status = Draft (for agent-created)
```yaml
# CORRECT
status: draft  # Always for Gemini-created/modified notes

# WRONG
status: ready  # Only humans set this
```

### 6. Links Required
```yaml
# CORRECT
moc: moc-algorithms  # WITHOUT brackets
related: [c-hash-map, c-array, q-three-sum--algorithms--medium]  # Array WITHOUT brackets

# WRONG
moc: []  # Must link to MOC
related: []  # Should link to concepts
moc: [[moc-algorithms]]  # Don't use brackets in YAML
```

### 7. No Emoji
```yaml
# FORBIDDEN: Do not use emoji in notes
# Use text equivalents: REQUIRED, FORBIDDEN, WARNING, NOTE
```

---

## Folder → Topic Mapping

| Folder | Topic Value | Question Kind |
|--------|-------------|---------------|
| `20-Algorithms/` | `algorithms` | `coding` |
| `30-System-Design/` | `system-design` | `system-design` |
| `40-Android/` | `android` | `android` or `theory` |
| `50-Backend/` | `databases` or related | `theory` |
| `60-CompSci/` | Match specific (see TAXONOMY.md) | `theory` |
| `70-Kotlin/` | `kotlin` | `coding` or `theory` |
| `80-Tools/` | `tools` | `theory` |
| `10-Concepts/` | N/A (concepts) | N/A |
| `90-MOCs/` | N/A (MOCs) | N/A |

---

## File Naming Patterns

```bash
# Q&A notes
q-<slug>--<topic>--<difficulty>.md

Examples:
q-two-sum--algorithms--easy.md
q-design-url-shortener--system-design--medium.md
q-jetpack-compose-state--android--medium.md

# Concept notes
c-<slug>.md

Examples:
c-hash-map.md
c-binary-tree.md
c-mvvm-pattern.md

# MOC notes
moc-<topic>.md

Examples:
moc-algorithms.md
moc-android.md
moc-system-design.md
```

---

## Controlled Vocabularies (Quick Reference)

### Topics (choose ONE)
```
algorithms, data-structures, system-design, android, kotlin,
programming-languages, architecture-patterns, concurrency,
distributed-systems, databases, networking, operating-systems,
security, performance, testing, devops-ci-cd, cloud, debugging,
ui-ux-accessibility, behavioral, tools, cs
```

### Difficulty
```
easy | medium | hard
```

### Question Kind
```
coding | theory | system-design | android
```

### Original Language
```
en | ru
```

### Status (Gemini Always uses)
```
draft
```

### Android Subtopics (when topic=android)
See `00-Administration/TAXONOMY.md` for full list. Examples:
```
ui-compose, ui-views, lifecycle, activity, fragment,
coroutines, flow, room, testing-unit, gradle, performance-startup
```

**Rule**: Mirror to tags as `android/<subtopic>`.

---

## YAML Template (Q&A)

```yaml
---
id: 20251003-143500                    # YYYYMMDD-HHmmss
title: Question Title EN / Заголовок RU
aliases: [Title EN, Заголовок RU]

# Classification
topic: algorithms                       # ONE from TAXONOMY.md
subtopics: [arrays, hash-map]          # 1-3; Android: use Android list
question_kind: coding                   # coding | theory | system-design | android
difficulty: easy                        # easy | medium | hard

# Language & provenance
original_language: en                   # en | ru
language_tags: [en, ru]                # which languages present
sources:
  - url: https://leetcode.com/...
    note: Original problem

# Workflow & relations
status: draft                           # ALWAYS draft for Gemini
moc: moc-algorithms                     # Link to ≥1 MOC (WITHOUT brackets)
related: [c-hash-map, c-array]          # Array of links (WITHOUT brackets)

# Timestamps
created: 2025-10-03                     # YYYY-MM-DD
updated: 2025-10-03                     # YYYY-MM-DD

# Tags (English only!)
tags: [leetcode, arrays, hash-map, difficulty/easy]
---
```

---

## Content Template (Q&A)

```markdown
# Question (EN)
> Clear, concise English statement.

# Вопрос (RU)
> Точная русская формулировка.

---

## Answer (EN)
**Approach**: ...
**Complexity**: Time O(n), Space O(n)
**Code**:
\```kotlin
fun solution() { ... }
\```

## Ответ (RU)
**Подход**: ...
**Сложность**: Время O(n), Память O(n)
**Код**:
\```kotlin
fun solution() { ... }
\```

---

## Follow-ups
- Variation: ...
- Edge case: ...

## References
- [[c-hash-map]]
- [[c-array]]
- https://en.wikipedia.org/...

## Related Questions
- [[q-three-sum--algorithms--medium]]
```

---

## Common Gemini Commands

### Setup
```bash
# Read vault rules
gemini "Summarize the rules from 00-Administration/AGENTS.md"

# Check taxonomy
gemini "List all valid topics from TAXONOMY.md"
gemini "List Android subtopics from TAXONOMY.md"
```

### Create
```bash
# Single note
gemini "Create q-merge-sort--algorithms--medium.md with EN/RU"

# Batch
gemini "Create 5 easy algorithm Q&As from LeetCode Top 100"
```

### Translate
```bash
# Add missing language
gemini "Add Russian translation to [FILE]"
gemini "Add English translation to [FILE]"

# Batch translate
gemini "Translate all notes in 20-Algorithms/ to have both EN and RU"
```

### Validate
```bash
# Single file
gemini "Validate [FILE] against vault rules"

# Folder
gemini "Check all notes in 40-Android/ for proper Android subtopic tags"

# Specific check
gemini "Verify all notes have status=draft or reviewed or ready"
```

### Maintenance
```bash
# Find drafts
gemini "List all notes with status=draft"

# Find missing links
gemini "Find Q&A notes without MOC links"

# Tag audit
gemini "Find notes with Russian in tags (should be English only)"
```

---

## Error Prevention

### Before Creating Note:
1.  Check TAXONOMY.md for valid topic
2.  Determine correct folder (matches topic)
3.  Use kebab-case English filename
4.  Include both EN and RU sections
5.  Set status: draft
6.  Add MOC and concept links

### Before Submitting:
1.  YAML complete and valid
2.  Tags are English-only
3.  For Android: subtopics → android/* tags
4.  File in correct folder
5.  Both languages present
6.  Links to ≥1 concept, ≥1 MOC

---

## Quick Checklist

**Every Q&A note must have:**
-  Both `# Question (EN)` and `# Вопрос (RU)`
-  Both `## Answer (EN)` and `## Ответ (RU)`
-  Valid `topic` from TAXONOMY.md
-  `status: draft`
-  English-only tags
-  `moc: moc-<topic>` (WITHOUT brackets)
-  `related: [c-..., ...]` (array WITHOUT double brackets)
-  For Android: `android/<subtopic>` tags matching `subtopics`
-  File in correct folder matching `topic`

---

## References

- **Full vault rules**: `00-Administration/README.md`
- **Agent tasks**: `00-Administration/AGENTS.md`
- **Quick checklist**: `00-Administration/AGENT-CHECKLIST.md`
- **AI tools comparison**: `00-Administration/AI-TOOLS.md`
- **Valid topics/subtopics**: `00-Administration/TAXONOMY.md`
- **Templates**: `_templates/_tpl-qna.md`, `_tpl-concept.md`, `_tpl-moc.md`
- **Cursor AI rules**: `.cursor/rules/` (modern MDC format) and `.cursorrules` (legacy)
- **Claude Code settings**: `.claude/settings.local.json`

---

## Example Session

```bash
# 1. Start session with context
gemini "Load vault context from 00-Administration/AGENTS.md.
I'll be creating algorithm Q&A notes today."

# 2. Check valid values
gemini "What subtopics are available for topic=algorithms?"

# 3. Create note
gemini "Create Q&A for 'Reverse Linked List' problem.
Topic: algorithms, Difficulty: easy
Include EN and RU, link to moc-algorithms and c-linked-list."

# 4. Validate
gemini "Validate the note you just created. Check all rules."

# 5. Batch create
gemini "Create Q&As for these 3 problems:
- Merge Two Sorted Lists (easy)
- Add Two Numbers (medium)
- Remove Nth Node (medium)
All should have EN/RU, proper YAML, status=draft."
```

---

**Remember**: When uncertain, check TAXONOMY.md, set `status: draft`, and ask the user.

**Emoji Rule**: Do not use emoji anywhere in vault notes. Use text equivalents: REQUIRED, FORBIDDEN, WARNING, NOTE.
