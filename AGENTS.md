# AI Agents Guide for Obsidian Interview Vault

This guide provides specific instructions for AI coding agents working with this Obsidian interview vault project.

## Project Overview & Purpose

This repository contains a **personal** Obsidian vault designed for building and maintaining a bilingual (Russian/English) interview Q&A knowledge base across **Computer Science**, **Algorithms/LeetCode**, **Android**, **System Design**, and related topics.

**Key Goals:**
- Maintain bilingual interview questions and answers in a single note
- Organize content using folders, YAML metadata, and tags
- Enable rich linking between concepts, MOCs (Maps of Content), and related questions
- Support automated queries and content discovery via Dataview

## Core Technologies & Stack

- **Primary Format**: Markdown files with YAML frontmatter
- **Note-taking System**: Obsidian vault
- **Query Engine**: Dataview plugin for dynamic content queries
- **Templating**: Templater plugin for consistent note creation
- **Version Control**: Git for backup and synchronization
- **Languages**: Bilingual content (Russian + English)

## File Structure & Organization

```
📄 README.md (root level)
📁 InterviewQuestions/    # Main content directory
    ├─ Algorithms/     # coding interview problems, LeetCode-style
    ├─ Android/        # platform, APIs, patterns, pitfalls
    ├─ Behavioural/    # non-technical interview questions
    ├─ CompSci/        # computer science concepts
    ├─ Data Structures/ # data structure implementations
    └─ System Design/  # scenarios, components, trade-offs
```

**Critical Rules:**
- Files belong to **exactly one topic folder**
- Use tags/links for cross-cutting concerns
- Keep hierarchy shallow - rely on YAML/tags/links for fine-grained organization

## File Naming Conventions

**MUST FOLLOW these patterns:**
- **Questions (Q&A)**: `q-<slug>--<short-topic>--<difficulty>.md`
  - Example: `q-two-sum--algorithms--easy.md`
- **Concepts**: `c-<slug>.md` → `c-hash-map.md`
- **MOCs**: `moc-<topic>.md` → `moc-algorithms.md`

**Rules:**
- Keep filenames **English, kebab-case**, short and stable
- Language variants are handled inside the note via `aliases`
- Never use numbers in folder names

## YAML Frontmatter Schema (REQUIRED)

Every note MUST include this YAML structure:

```yaml
---
# Identity
id: iv-2025-0001           # unique id (string)
title: Two Sum / Два слагаемых
aliases:                   # all common titles; EN & RU recommended
  - Two Sum
  - Два слагаемых

# Classification
topic: algorithms          # one of: algorithms | system-design | android | cs | behavioral
subtopics: [arrays, hash-map]  # optional, small set
question_kind: coding      # coding | theory | system-design | android
difficulty: easy           # easy | medium | hard

# Language & provenance
original_language: ru      # ru | en (Russian is now primary)
language_tags: [ru, en]    # which languages exist in this note
sources:
  - url: https://leetcode.com/problems/two-sum/
    note: Original statement

# Workflow & relations
status: draft              # draft | reviewed | ready
moc: [[moc-algorithms]]    # link to Map of Content
related:                   # optional cross-links
  - [[c-hash-map]]
  - [[q-three-sum--algorithms--medium]]

# Timestamps (ISO8601)
created: 2025-09-28
updated: 2025-09-28

# Tags (English only; no leading # in YAML)
tags: [leetcode, arrays, hash-map, difficulty/easy]
---
```

**Critical YAML Rules:**
- `topic` must match exactly one folder name
- `tags` must be English, descriptive, reusable
- Use namespaces for controlled vocabularies: `difficulty/easy`, `lang/kotlin`, `platform/android`
- Always update `updated` timestamp when modifying content

## Note Body Template (Bilingual Structure)

**IMPORTANT: Russian content comes FIRST, English SECOND**

```markdown
# Вопрос (RU)
> Точная русская формулировка задачи.

# Question (EN)
> Clear, concise English version of the prompt.

---

## Ответ (RU)
Подробное объяснение на русском. Код при необходимости.

## Answer (EN)
Explain approach, complexity, trade-offs, pitfalls. Include code when relevant.

---

## Follow-ups
- Variation A …
- Edge cases …

## References
- [[c-hash-map]]
- Link(s) to external sources (also listed in YAML `sources`).

## Related Questions
- [[q-three-sum--algorithms--medium]]
```

**Content Rules:**
- Keep **both languages side by side**; they must be semantically equivalent
- Prefer **EN code identifiers/comments**; RU comments optional
- Keep answers **complete yet skimmable** with headings and lists

## Tagging Rules

- Tags are **English only**; keep them short and reusable
- Examples: `arrays`, `hash-map`, `two-pointers`, `greedy`, `dp`, `graphs`, `kotlin`, `android/compose`
- Use **namespaces** for controlled vocabularies: `difficulty/easy`, `lang/kotlin`, `platform/android`
- Do **not** duplicate the folder name as a tag unless useful for search

## Linking Rules

**CRITICAL for AI agents:**
- Every Q&A **SHOULD** link to at least one **Concept** (`c-*`) and one **MOC** (`moc-*`)
- Use concept notes for reusable theory (e.g., `c-binary-tree`, `c-consistent-hashing`)
- MOCs act as human-curated hubs per topic
- For sequencing, link forward/back and optionally add `related` in YAML

## MOCs (Maps of Content)

- **Location**: `MOCs/` folder (not yet created in current structure)
- **Name**: `moc-<topic>.md` → `moc-android.md`
- **Content**: brief overview, manual list of key notes, and auto lists via Dataview

## Dataview Queries

Common query patterns for AI agents:

```dataview
# All LeetCode by difficulty
TABLE difficulty, subtopics, status
FROM ""
WHERE topic = "algorithms" AND startswith(file.name, "q-") AND contains(tags, "leetcode")
SORT difficulty ASC, file.name ASC

# Android questions touching Compose
LIST file.link
FROM ""
WHERE topic = "android" AND startswith(file.name, "q-") AND contains(tags, "android/compose")

# Recently Updated
TABLE updated, topic, difficulty
FROM ""
WHERE updated >= date(today) - dur(30 days)
SORT updated DESC
```

## Development Commands

**No build process required** - this is a static Obsidian vault.

**Setup:**
1. Clone repository
2. Open in Obsidian
3. Install plugins: Dataview, Templater (optional: MetaEdit, Tag Wrangler, Breadcrumbs)

## Code Style and Conventions

**File Operations:**
- Always preserve exact indentation (tabs/spaces)
- Use absolute paths when possible
- Prefer editing existing files over creating new ones
- Never create documentation files unless explicitly requested

**Content Creation:**
- Follow the bilingual template structure exactly
- Ensure YAML frontmatter is complete and valid
- Use English for code, comments, and technical terms
- Maintain semantic equivalence between Russian and English content

## Security Considerations

- No sensitive data should be stored in the vault
- Use Git for version control and backup
- Consider excluding heavy caches from version control
- Keep `.obsidian` folder to preserve plugin settings

## AI Agent Specific Instructions

**When creating new content:**
1. Use the provided YAML template structure
2. Ensure Russian content comes before English content
3. Include proper cross-links to concepts and MOCs
4. Tag appropriately with English tags
5. Set appropriate difficulty and topic classifications

**When modifying existing content:**
1. Always update the `updated` timestamp in YAML
2. Preserve the bilingual structure
3. Maintain semantic equivalence between languages
4. Update related links if content changes significantly

**When searching or querying:**
1. Use Dataview syntax for dynamic queries
2. Reference folder names without numbers (e.g., "Algorithms", not "20-Algorithms")
3. Use English tags for filtering
4. Consider both topic folders and cross-cutting tag relationships

**File Management:**
- Respect the one-folder-per-file rule
- Use proper naming conventions
- Maintain consistent kebab-case for filenames
- Never add numbers to folder names

## Maintenance & Hygiene

**Status Workflow:**
- `draft` → `reviewed` → `ready`
- Always bump `updated` in YAML when modifying
- Prefer adding aliases over renaming filenames
- Move outdated/duplicate notes to archive and mark `status: retired`

**Tag Health:**
- Periodically audit and merge near-duplicates (e.g., `hashmap` vs `hash-map`)
- Use consistent naming patterns
- Maintain controlled vocabularies with namespaces
