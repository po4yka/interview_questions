---
date created: Saturday, October 18th 2025, 2:02:21 pm
date modified: Saturday, November 1st 2025, 5:43:39 pm
---

# File Naming Rules

**Date Established**: 2025-10-03
**Last Updated**: 2025-10-18
**Status**: Enforced - All files comply

---

## Overview

This document defines **mandatory** file naming conventions for all notes in the vault. These rules ensure cross-platform compatibility, searchability, and consistency across 942+ bilingual interview preparation notes.

**Critical Rule**: ALL filenames MUST use English-only characters, regardless of content language.

---

## Core Principles

### REQUIRED Rules

- REQUIRED: English characters only (a-z, 0-9, hyphens)
- REQUIRED: Lowercase letters only
- REQUIRED: Hyphens (-) as word separators
- REQUIRED: Prefix indicating note type (q-, c-, moc-)
- REQUIRED: Topic and difficulty in filename (for Q&A notes)
- REQUIRED: Descriptive slug (3-8 words)

### FORBIDDEN Rules

- FORBIDDEN: Cyrillic (Russian) characters in filenames
- FORBIDDEN: Uppercase letters
- FORBIDDEN: Spaces in filenames
- FORBIDDEN: Underscores (_) as separators
- FORBIDDEN: Special characters (!@#$%^&*()+={}[]|\\:;"'<>,.?/)
- FORBIDDEN: Unicode characters beyond ASCII
- FORBIDDEN: Ambiguous or generic slugs

---

## File Naming Patterns

### Pattern 1: Question Notes (Q&A)

**Format**:
```
q-[english-slug]--[topic]--[difficulty].md
```

**Components**:
- `q-` - Prefix for question/Q&A notes (REQUIRED)
- `[english-slug]` - Descriptive phrase in English (3-8 words, lowercase, hyphenated)
- `--[topic]--` - Topic from TAXONOMY.md (see section below)
- `--[difficulty]` - Difficulty level: `easy` | `medium` | `hard`
- `.md` - Markdown extension (REQUIRED)

**Examples**:
```
q-what-is-viewmodel--android--medium.md
q-kotlin-coroutine-context--kotlin--medium.md
q-two-sum-problem--algorithms--easy.md
q-design-url-shortener--system-design--hard.md
q-sql-join-types--databases--medium.md
q-git-merge-vs-rebase--tools--medium.md
q-mutex-vs-semaphore--operating-systems--medium.md
q-binary-search-implementation--algorithms--easy.md
```

---

### Pattern 2: Concept Notes

**Format**:
```
c-[english-concept-name].md
```

**Components**:
- `c-` - Prefix for concept notes (REQUIRED)
- `[english-concept-name]` - Descriptive name in English (lowercase, hyphenated)
- `.md` - Markdown extension (REQUIRED)

**Examples**:
```
c-viewmodel.md
c-kotlin-coroutines.md
c-mvvm-architecture.md
c-hash-map.md
c-binary-tree.md
c-dependency-injection.md
c-compose-state.md
c-solid-principles.md
```

---

### Pattern 3: MOC (Map of Content) Notes

**Format**:
```
moc-[english-topic-name].md
```

**Components**:
- `moc-` - Prefix for Map of Content hub pages (REQUIRED)
- `[english-topic-name]` - Topic name in English (lowercase, hyphenated)
- `.md` - Markdown extension (REQUIRED)

**Examples**:
```
moc-android.md
moc-kotlin.md
moc-algorithms.md
moc-system-design.md
moc-backend.md
moc-cs.md
moc-tools.md
```

---

## Valid Topic Values

**CRITICAL**: Topic in filename MUST match one of the values from TAXONOMY.md.

### All Valid Topics (22 total)

```
# Core Technical Topics
algorithms
data-structures
system-design
android
kotlin
programming-languages

# Architecture & Patterns
architecture-patterns
concurrency
distributed-systems
databases

# Infrastructure & Systems
networking
operating-systems
security
performance
cloud

# Development Practices
testing
devops-ci-cd
tools
debugging

# Other
ui-ux-accessibility
behavioral
cs
```

**Reference**: See `00-Administration/TAXONOMY.md` for complete list and definitions.

### Topic → Folder Mapping

| Topic | Folder | Example Filename |
|-------|--------|------------------|
| `algorithms` | `20-Algorithms/` | q-binary-search--algorithms--easy.md |
| `data-structures` | `20-Algorithms/` | q-hash-map-implementation--data-structures--medium.md |
| `system-design` | `30-System-Design/` | q-design-cache--system-design--hard.md |
| `android` | `40-Android/` | q-compose-state--android--medium.md |
| `databases` | `50-Backend/` | q-sql-indexing--databases--medium.md |
| `networking` | `50-Backend/` | q-http-vs-https--networking--easy.md |
| `operating-systems` | `60-CompSci/` | q-process-vs-thread--operating-systems--medium.md |
| `concurrency` | `60-CompSci/` | q-deadlock-prevention--concurrency--hard.md |
| `kotlin` | `70-Kotlin/` | q-coroutine-basics--kotlin--easy.md |
| `programming-languages` | `70-Kotlin/` | q-oop-principles--programming-languages--medium.md |
| `tools` | `80-Tools/` | q-git-rebase--tools--medium.md |

**Rule**: Filename topic MUST match the folder where the file is stored.

---

## Valid Difficulty Values

**REQUIRED**: All Q&A filenames MUST include exactly ONE difficulty level.

### Difficulty Levels (3 total)

```
easy      # Straightforward, basic concepts, simple implementation
medium    # Moderate complexity, multiple concepts, standard patterns
hard      # Complex, advanced concepts, tricky edge cases
```

**Examples**:
```
q-what-is-variable--kotlin--easy.md           # Easy: Basic concept
q-coroutine-context--kotlin--medium.md        # Medium: Intermediate concept
q-structured-concurrency--kotlin--hard.md     # Hard: Advanced concept
```

---

## Slug Creation Guidelines

### 1. Use English Words ONLY

**REQUIRED**: Translate or transliterate Russian to English.

| Russian Question | English Slug | Full Filename |
|------------------|--------------|---------------|
| Что такое ViewModel | what-is-viewmodel | q-what-is-viewmodel--android--medium.md |
| Как создать корутину | how-to-create-coroutine | q-how-to-create-coroutine--kotlin--easy.md |
| Для чего нужны фрагменты | why-are-fragments-needed | q-why-are-fragments-needed--android--medium.md |
| Разница между MVI и MVVM | difference-between-mvi-mvvm | q-difference-between-mvi-mvvm--android--hard.md |

### 2. Keep It Concise

**REQUIRED**: 3-8 words maximum in the slug.

**Guidelines**:
- Remove articles (a, an, the) when possible
- Use abbreviations for well-known terms (SQL, HTTP, API, JVM, etc.)
- Focus on key concepts, not full sentences

**Examples**:

```
# CORRECT - Concise
q-recyclerview-optimization--android--medium.md
q-sql-join-types--databases--medium.md
q-mvvm-vs-mvi--android--hard.md

# WRONG - Too long
q-how-to-optimize-recyclerview-for-better-performance--android--medium.md
q-what-are-all-the-different-types-of-sql-joins--databases--medium.md
q-what-is-the-difference-between-mvvm-and-mvi-architecture-patterns--android--hard.md
```

### 3. Lowercase with Hyphens

**REQUIRED**: All lowercase, hyphens as separators.

**Examples**:

```
# CORRECT
q-viewmodel-vs-savedstate--android--medium.md
q-kotlin-null-safety--kotlin--easy.md
q-http-status-codes--networking--easy.md

# WRONG - Uppercase
q-ViewModel-vs-SavedState--android--medium.md
q-Kotlin-Null-Safety--kotlin--easy.md

# WRONG - Underscores
q-viewmodel_vs_savedstate--android--medium.md
q-kotlin_null_safety--kotlin--easy.md

# WRONG - Spaces
q-viewmodel vs savedstate--android--medium.md
q-kotlin null safety--kotlin--easy.md
```

### 4. Be Descriptive and Specific

**REQUIRED**: Slug should clearly indicate the question content.

**Examples**:

```
# CORRECT - Specific
q-kotlin-null-safety-operators--kotlin--easy.md
q-recyclerview-diffutil-usage--android--medium.md
q-coroutine-context-dispatchers--kotlin--medium.md
q-git-merge-vs-rebase--tools--medium.md

# WRONG - Too generic
q-kotlin-operators--kotlin--easy.md
q-list-optimization--android--medium.md
q-coroutine-basics--kotlin--medium.md
q-git-commands--tools--medium.md
```

### 5. Use Common Technical Terms

**REQUIRED**: Use standard terminology from official documentation.

**Examples**:

```
# CORRECT - Standard terms
q-viewmodel-lifecycle--android--medium.md
q-coroutine-scope--kotlin--medium.md
q-dependency-injection--android--hard.md
q-binary-search-tree--algorithms--medium.md

# WRONG - Non-standard terms
q-view-model-life-cycle--android--medium.md      # viewmodel is one word
q-co-routine-scope--kotlin--medium.md            # coroutine is one word
q-dependency-injector--android--hard.md          # injection, not injector
q-binary-search-tree-structure--algorithms--medium.md  # redundant
```

---

## Language Handling

### Content Vs Filename

| Aspect | Language | Rule | Example |
|--------|----------|------|---------|
| **Filename** | English ONLY | REQUIRED | `q-what-is-viewmodel--android--medium.md` |
| **YAML title** | Bilingual | REQUIRED | `title: What is ViewModel / Что такое ViewModel` |
| **YAML aliases** | Bilingual | REQUIRED | `aliases: [ViewModel, ВьюМодель]` |
| **Content headings** | Bilingual | REQUIRED | `# Question (EN)` and `# Вопрос (RU)` |
| **Content body** | Bilingual | REQUIRED | Both EN and RU sections |
| **YAML tags** | English ONLY | REQUIRED | `tags: [android, viewmodel, difficulty/medium]` |

### Example Note Structure

**Filename**: `q-what-is-viewmodel--android--medium.md`

```yaml
---
id: 20251018-120000
title: What is ViewModel / Что такое ViewModel
aliases: [ViewModel, ВьюМодель, Android ViewModel]

# Classification
topic: android
subtopics: [lifecycle, architecture-mvvm]
question_kind: theory
difficulty: medium

# Language
original_language: ru
language_tags: [en, ru]

# Workflow
status: draft

# Links (WITHOUT brackets in YAML)
moc: moc-android
related: [c-viewmodel, c-mvvm-pattern, q-viewmodel-vs-savedstate--android--medium]

# Timestamps
created: 2025-10-18
updated: 2025-10-18

# Tags (English only)
tags: [android, viewmodel, lifecycle, architecture, difficulty/medium]
---

# Question (EN)
> What is ViewModel and why is it used in Android?

# Вопрос (RU)
> Что такое ViewModel и для чего используется в Android?

---

## Answer (EN)
[English answer content...]

## Ответ (RU)
[Russian answer content...]
```

---

## Common Naming Patterns

### Question Types

#### What/Who/Why Questions
```
q-what-is-viewmodel--android--medium.md
q-what-are-coroutines--kotlin--easy.md
q-why-use-fragments--android--medium.md
q-who-uses-dependency-injection--android--hard.md
```

#### How Questions
```
q-how-to-create-coroutine--kotlin--easy.md
q-how-viewmodel-survives-rotation--android--medium.md
q-how-to-optimize-compose--android--hard.md
```

#### Comparison Questions
```
q-recyclerview-vs-listview--android--easy.md
q-mvvm-vs-mvi--android--hard.md
q-flow-vs-livedata--android--medium.md
q-git-merge-vs-rebase--tools--medium.md
```

#### Implementation Questions
```
q-implement-binary-search--algorithms--easy.md
q-create-custom-view--android--hard.md
q-design-url-shortener--system-design--hard.md
```

#### Theory Questions
```
q-solid-principles--programming-languages--medium.md
q-design-patterns-overview--architecture-patterns--medium.md
q-acid-properties--databases--medium.md
```

---

## Vault Statistics (Current)

**As of 2025-10-18**: 942 Q&A files total

### Files by Directory

| Directory | Count | Example Filename |
|-----------|-------|------------------|
| **20-Algorithms/** | ~200 | q-two-sum--algorithms--easy.md |
| **30-System-Design/** | ~5 | q-design-cache--system-design--hard.md |
| **40-Android/** | ~495 | q-compose-state--android--medium.md |
| **50-Backend/** | ~30 | q-sql-joins--databases--medium.md |
| **60-CompSci/** | ~163 | q-process-vs-thread--operating-systems--medium.md |
| **70-Kotlin/** | ~243 | q-coroutine-basics--kotlin--easy.md |
| **80-Tools/** | ~6 | q-git-rebase--tools--medium.md |

**Compliance**: All 942 files follow English-only naming convention.

### Files by Difficulty

| Difficulty | Estimated Count | Percentage |
|------------|----------------|------------|
| **easy** | ~250 | 27% |
| **medium** | ~550 | 58% |
| **hard** | ~142 | 15% |

---

## Implementation Checklist

When creating new notes, verify:

### Filename Requirements
- [ ] Filename uses English characters only (a-z, 0-9, hyphens)
- [ ] Filename is all lowercase
- [ ] Filename follows pattern: `q-[slug]--[topic]--[difficulty].md`
- [ ] Topic matches value from TAXONOMY.md
- [ ] Difficulty is `easy` | `medium` | `hard`
- [ ] Slug is 3-8 words, descriptive and specific
- [ ] No spaces, underscores, or special characters
- [ ] No Russian/Cyrillic characters in filename

### Content Requirements
- [ ] YAML title includes both EN and RU
- [ ] YAML aliases includes both languages
- [ ] Content has `# Question (EN)` section
- [ ] Content has `# Вопрос (RU)` section
- [ ] Content has `## Answer (EN)` section
- [ ] Content has `## Ответ (RU)` section
- [ ] YAML tags are English-only

### File Placement
- [ ] File is in correct folder matching topic
- [ ] Topic in filename matches folder
- [ ] Topic in YAML matches filename

---

## Validation Tools

### Check for Russian Filenames

```bash
# Find any files with Cyrillic characters
find . -name "*.md" -type f | grep -E '[а-яА-ЯёЁ]'

# Should return nothing if all files are properly named
```

### Check for Uppercase in Filenames

```bash
# Find files with uppercase letters
find . -name "*.md" -type f | grep -E '[A-Z]'

# Should return nothing (except 00-Administration files)
```

### Check for Spaces in Filenames

```bash
# Find files with spaces
find . -name "* *.md" -type f

# Should return nothing
```

### Check Filename Pattern Compliance

```bash
# Check Q&A files follow pattern
find 20-Algorithms 30-System-Design 40-Android 50-Backend 60-CompSci 70-Kotlin 80-Tools \
  -name "q-*.md" | grep -v -E '^[0-9]+-[A-Za-z]+/q-[a-z0-9-]+--[a-z-]+--[a-z]+\.md$'

# Should return nothing if all files follow pattern
```

### Batch Rename Script (If Needed)

```python
#!/usr/bin/env python3
"""
Rename files to follow naming convention.
Extract title from YAML frontmatter and generate proper filename.
"""

import os
import re
import yaml

def extract_title_from_file(filepath):
    """Extract English title from YAML frontmatter."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract YAML frontmatter
    match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None

    frontmatter = yaml.safe_load(match.group(1))
    title = frontmatter.get('title', '')

    # Extract English part (before " / ")
    if ' / ' in title:
        title = title.split(' / ')[0]

    return title

def title_to_slug(title):
    """Convert title to filename slug."""
    # Convert to lowercase
    slug = title.lower()
    # Replace spaces with hyphens
    slug = slug.replace(' ', '-')
    # Remove special characters
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    # Remove multiple hyphens
    slug = re.sub(r'-+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')

    return slug

# Use at your own risk - test on a copy first!
```

---

## Why English-Only Filenames?

### Technical Reasons

1. **Cross-platform compatibility**
   - Windows, macOS, Linux handle ASCII filenames consistently
   - Unicode filenames can cause issues on some systems

2. **Git compatibility**
   - Better handling in version control
   - Fewer encoding issues in diffs and logs
   - Easier code review across different locales

3. **URL safety**
   - Can be used in web URLs without percent-encoding
   - Direct linking from documentation and wikis

4. **Command-line friendly**
   - Works with all shell commands and scripts
   - No need for quoting or escaping
   - Easier tab completion

5. **Tool compatibility**
   - Works with all IDEs, editors, and development tools
   - No encoding issues in CI/CD pipelines
   - Compatible with all static site generators

### Practical Reasons

1. **Search efficiency**
   - Easier to search and reference in English
   - Works with all search tools and grep
   - Consistent with technical documentation

2. **Consistency**
   - Maintains uniform naming across knowledge base
   - Easier to write scripts and automation
   - Clear conventions for all contributors

3. **Accessibility**
   - Easier for international collaboration
   - Works in all keyboard layouts
   - Standard in technical documentation worldwide

4. **Obsidian compatibility**
   - Wikilinks work consistently
   - Graph view displays properly
   - Dataview queries work correctly

---

## Common Mistakes to Avoid

### WRONG: Russian Characters in Filename
```
# WRONG
q-что-такое-viewmodel--android--medium.md

# CORRECT
q-what-is-viewmodel--android--medium.md
```

### WRONG: Uppercase Letters
```
# WRONG
q-ViewModel-Basics--android--easy.md

# CORRECT
q-viewmodel-basics--android--easy.md
```

### WRONG: Spaces Instead of Hyphens
```
# WRONG
q-what is viewmodel--android--medium.md

# CORRECT
q-what-is-viewmodel--android--medium.md
```

### WRONG: Underscores Instead of Hyphens
```
# WRONG
q-what_is_viewmodel--android--medium.md

# CORRECT
q-what-is-viewmodel--android--medium.md
```

### WRONG: Invalid Topic
```
# WRONG
q-coroutine-basics--programming--easy.md

# CORRECT (use valid topic from TAXONOMY.md)
q-coroutine-basics--kotlin--easy.md
```

### WRONG: Missing Difficulty
```
# WRONG
q-viewmodel-basics--android.md

# CORRECT
q-viewmodel-basics--android--easy.md
```

### WRONG: Too Generic Slug
```
# WRONG
q-question-1--android--medium.md
q-android-basics--android--easy.md

# CORRECT
q-viewmodel-lifecycle--android--medium.md
q-activity-lifecycle--android--easy.md
```

---

## References

### Related Documents
- **Controlled vocabularies**: `00-Administration/TAXONOMY.md`
- **Agent instructions**: `00-Administration/AGENTS.md`
- **Quick checklist**: `00-Administration/AGENT-CHECKLIST.md`
- **Linking strategy**: `00-Administration/LINKING-STRATEGY.md`
- **Templates**: `_templates/_tpl-qna.md`, `_tpl-concept.md`, `_tpl-moc.md`
- **Claude Code setup**: `.claude/README.md`
- **Cursor AI rules**: `.cursor/rules/`
- **Gemini CLI guide**: `GEMINI.md`

### External Resources
- [Obsidian File Management](https://help.obsidian.md/Files+and+folders/Manage+notes)
- [Markdown Filename Best Practices](https://github.com/github/renaming)
- [Cross-Platform File Naming](https://en.wikipedia.org/wiki/Filename)

---

## Enforcement

**This rule is MANDATORY for all new notes.**

- **LLM Agents**: MUST follow these rules when creating files
- **Import Scripts**: MUST validate and normalize filenames
- **Manual Creation**: MUST comply with these rules
- **Pre-Commit Hooks**: MAY be added to enforce compliance

**Violations**: Files with non-compliant names will be flagged for renaming.

---

**Version**: 2.0 (Updated and expanded)
**Last Updated**: 2025-10-18
**Status**: Enforced across all 942 files
**Compliance**: 100%
