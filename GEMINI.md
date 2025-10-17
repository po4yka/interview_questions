# Gemini AI Guide for Obsidian Interview Vault

This file provides specific instructions for Google Gemini AI when working with this bilingual Obsidian interview vault project. **This file takes precedence over AGENTS.md when both are present.**

## Project Context & Mission

You are working with a **personal Obsidian vault** designed to build and maintain a comprehensive bilingual (Russian/English) interview preparation knowledge base. The vault focuses on technical interview topics including Computer Science, Algorithms/LeetCode, Android development, and System Design.

**Primary Objectives:**
- Create and maintain high-quality bilingual interview Q&A content
- Ensure consistent formatting and metadata across all notes
- Build a rich network of cross-references between related concepts
- Support efficient content discovery and review workflows

## Critical Behavioral Guidelines

### Language Priority & Structure
- **Russian content ALWAYS comes first, English second** in all notes
- Maintain semantic equivalence between Russian and English sections
- Use English for technical terms, code, and metadata (tags, filenames)
- Russian translations should be natural and contextually appropriate

### Content Creation Standards
- Every note must include complete YAML frontmatter
- Follow the exact bilingual template structure provided
- Ensure all cross-references use proper Obsidian link syntax `[[note-name]]`
- Maintain consistent difficulty ratings and topic classifications

## File Structure & Naming Rules

### Current Directory Structure
```
📄 README.md (root level)
📁 InterviewQuestions/    # Main content directory
    ├─ Algorithms/     # LeetCode-style coding problems
    ├─ Android/        # Android platform questions
    ├─ Behavioural/    # Non-technical interview questions
    ├─ CompSci/        # Computer science theory
    ├─ Data Structures/ # Data structure implementations
    └─ System Design/  # System design scenarios
```

### File Naming Conventions (MANDATORY)
- **Questions**: `q-<slug>--<topic>--<difficulty>.md`
  - Example: `q-two-sum--algorithms--easy.md`
- **Concepts**: `c-<slug>.md`
  - Example: `c-hash-map.md`
- **MOCs**: `moc-<topic>.md`
  - Example: `moc-algorithms.md`

**Critical Rules:**
- Use kebab-case for all filenames
- Keep filenames short and stable
- Never include numbers in folder names
- Always use English for filenames

## YAML Frontmatter Template (REQUIRED)

Every note you create or modify MUST include this complete YAML structure:

```yaml
---
# Identity
id: iv-2025-XXXX           # unique identifier
title: Title EN / Title RU
aliases:                   # alternative titles
  - English Title
  - Русский заголовок

# Classification
topic: algorithms          # EXACT folder name match
subtopics: [array, list]   # relevant subtopics
question_kind: coding      # coding | theory | system-design | android
difficulty: easy           # easy | medium | hard

# Language & provenance
original_language: ru      # ru | en (Russian is primary)
language_tags: [ru, en]    # languages present in note
sources:
  - url: https://example.com
    note: Source description

# Workflow & relations
status: draft              # draft | reviewed | ready
moc: [[moc-topic]]         # link to Map of Content
related:                   # cross-references
  - [[related-note-1]]
  - [[related-note-2]]

# Timestamps (ISO8601 format)
created: 2025-01-XX
updated: 2025-01-XX

# Tags (English only, no # prefix)
tags: [tag1, tag2, namespace/value]
---
```

## Note Content Template (MANDATORY STRUCTURE)

**ALWAYS follow this exact structure with Russian content first:**

```markdown
# Вопрос (RU)
> Точная и понятная русская формулировка задачи или вопроса.

# Question (EN)
> Clear and concise English version of the prompt.

---

## Ответ (RU)
Подробное объяснение решения на русском языке.
- Включите код при необходимости
- Объясните сложность алгоритма
- Укажите основные моменты и подводные камни

## Answer (EN)
Comprehensive explanation of the solution in English.
- Include code when relevant
- Explain time/space complexity
- Highlight key insights and potential pitfalls

---

## Follow-ups
- Variation A: Additional question or modification
- Edge cases: Special scenarios to consider
- Related problems: Similar challenges

## References
- [[c-concept-note]] - Link to relevant concept notes
- External sources (also listed in YAML sources)

## Related Questions
- [[q-related-question--topic--difficulty]]
- [[q-another-related--topic--difficulty]]
```

## Tagging System & Rules

### Tag Categories
- **Technical**: `arrays`, `hash-map`, `two-pointers`, `greedy`, `dp`, `graphs`
- **Platform**: `android/compose`, `android/lifecycle`, `android/architecture`
- **Difficulty**: `difficulty/easy`, `difficulty/medium`, `difficulty/hard`
- **Language**: `lang/kotlin`, `lang/java`, `lang/python`
- **Source**: `leetcode`, `interviewbit`, `system-design`

### Tagging Rules
- Use **English only** for all tags
- Keep tags short and descriptive
- Use namespaces for controlled vocabularies
- Avoid duplicating folder names as tags
- Be consistent with existing tag usage

## Content Quality Standards

### Russian Translation Guidelines
- Provide natural, fluent Russian translations
- Maintain technical accuracy
- Use appropriate Russian terminology for technical concepts
- Ensure cultural context is appropriate for Russian speakers

### English Content Standards
- Write clear, professional English
- Use standard interview terminology
- Include code examples when relevant
- Explain concepts at an appropriate technical level

### Code Standards
- Use English for all code identifiers and comments
- Include Russian comments only when they add significant value
- Provide clean, readable code examples
- Include complexity analysis (Big O notation)

## Cross-Reference & Linking Strategy

### Required Links
Every Q&A note should link to:
- At least one **Concept note** (`c-*`)
- At least one **MOC** (`moc-*`)
- Related questions in the `related` YAML field

### Link Types
- **Concept links**: `[[c-binary-tree]]`, `[[c-hash-map]]`
- **Question links**: `[[q-three-sum--algorithms--medium]]`
- **MOC links**: `[[moc-algorithms]]`, `[[moc-android]]`

### Link Maintenance
- Always use proper Obsidian link syntax
- Update related links when content changes significantly
- Maintain bidirectional relationships where appropriate

## Workflow & Status Management

### Status Progression
- `draft` → `reviewed` → `ready`
- Always update `updated` timestamp when modifying content
- Mark content as `reviewed` only after human verification

### Content Lifecycle
- Create new notes with `draft` status
- Update status to `reviewed` after quality check
- Mark as `ready` for production use
- Archive outdated content to `99-Archive/` with `status: retired`

## Dataview Query Patterns

When working with existing content, use these query patterns:

```dataview
# Find all questions by topic and difficulty
TABLE difficulty, status, updated
FROM ""
WHERE topic = "algorithms" AND startswith(file.name, "q-")
SORT difficulty ASC, updated DESC

# Find questions needing review
LIST file.link, updated
FROM ""
WHERE status = "draft"
SORT updated ASC

# Find questions by tags
LIST file.link, difficulty
FROM ""
WHERE contains(tags, "leetcode")
SORT difficulty ASC
```

## Error Prevention & Validation

### Before Creating/Modifying Notes
1. Verify the target folder exists and matches the `topic` field
2. Ensure YAML frontmatter is complete and valid
3. Check that Russian content comes before English content
4. Validate all internal links use proper syntax
5. Confirm tags are English-only and follow naming conventions

### Quality Checks
- Semantic equivalence between Russian and English content
- Proper cross-referencing to concepts and MOCs
- Appropriate difficulty classification
- Complete and accurate YAML metadata
- Consistent formatting throughout

## Special Instructions for Gemini

### When Creating New Content
1. Start with the complete YAML template
2. Generate high-quality Russian content first
3. Provide accurate English translation
4. Include relevant code examples
5. Add appropriate cross-references
6. Tag comprehensively with English tags

### When Modifying Existing Content
1. Preserve the bilingual structure
2. Update the `updated` timestamp
3. Maintain semantic equivalence
4. Update related links if content changes
5. Keep status appropriate to content quality

### When Searching or Analyzing
1. Use folder names without numbers
2. Consider both topic-based and tag-based organization
3. Respect the bilingual nature of the content
4. Account for the cross-reference network
5. Use Dataview syntax for dynamic queries

## Emergency Procedures

If you encounter:
- **Missing folders**: Create them following the exact naming convention
- **Broken links**: Fix using proper Obsidian syntax `[[note-name]]`
- **Invalid YAML**: Use the provided template as reference
- **Language order issues**: Ensure Russian always comes first
- **Inconsistent tags**: Follow the English-only, namespaced approach

Remember: This is a personal knowledge base designed for interview preparation. Focus on creating high-quality, well-organized content that supports effective learning and review.
