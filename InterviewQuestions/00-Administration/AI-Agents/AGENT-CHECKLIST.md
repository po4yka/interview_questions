---
date created: Tuesday, November 25th 2025, 8:21:02 pm
date modified: Tuesday, November 25th 2025, 8:54:04 pm
---

# Agent Quick Reference Checklist

**Purpose**: Fast reference for AI agents creating or editing Q&A notes.
**Last Updated**: 2025-11-25

## Pre-Flight Checks

Before creating/editing a note:

- [ ] Topic is valid (check [[TAXONOMY]])
- [ ] Folder matches topic (see mapping below)
- [ ] Filename follows pattern: `q-<slug>--<topic>--<difficulty>.md`

## YAML Frontmatter Template

```yaml
---
id: <topic>-<number>           # e.g., android-042, kotlin-015
title: "English Title / Zagolovok"
aliases: [English Title, Zagolovok]
topic: <single-topic>          # ONE value from TAXONOMY.md
subtopics: [subtopic1, subtopic2]  # 1-3 values
question_kind: theory          # theory | coding | system-design
difficulty: medium             # easy | medium | hard
original_language: en          # en | ru
language_tags: [en, ru]        # Languages present in content
status: draft                  # draft | reviewed | ready
moc: moc-<topic>              # NO brackets
related: [] # Array format, 2+ items
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [difficulty/<level>, <topic>/<subtopic>]
---
```

### Critical Rules

| Field | Correct | Wrong |
|-------|---------|-------|
| `moc` | `moc: moc-android` | `moc: [[moc-android]]` |
| `related` | `related: [q-a, q-b]` | `related: q-a` |
| `topic` | `topic: android` | `topic: [android, kotlin]` |
| `tags` | `tags: [coroutines]` | `tags: [korutiny]` |

## Topic -> Folder Mapping

| Topic | Folder | MOC |
|-------|--------|-----|
| `android` | `40-Android/` | `moc-android` |
| `kotlin` | `70-Kotlin/` | `moc-kotlin` |
| `programming-languages` | `70-Kotlin/` | `moc-kotlin` |
| `system-design` | `30-System-Design/` | `moc-system-design` |
| `algorithms` | `20-Algorithms/` | `moc-algorithms` |
| `cs` | `60-CompSci/` | `moc-cs` |
| `concurrency` | `60-CompSci/` | `moc-cs` |
| `databases` | `50-Backend/` | `moc-backend` |
| `tools` | `80-Tools/` | `moc-tools` |

## Content Structure (Minimal)

```markdown
# Question (EN)

> [Question text]

# Vopros (RU)

> [Tekst voprosa]

---

## Answer (EN)

[Comprehensive answer with code examples]

## Otvet (RU)

[Polnyy otvet]

## Follow-ups

- Follow-up question 1?
- Follow-up question 2?

## References

- [Official Docs](https://...)

## Related Questions

- [[q-related-note--topic--difficulty]]
```

## Quality Checklist

### Content
- [ ] Technically accurate
- [ ] Code examples compile
- [ ] O-notation for algorithms
- [ ] Trade-offs discussed
- [ ] EN/RU semantically equivalent

### Formatting
- [ ] No emojis
- [ ] Code blocks have language (`kotlin`, `java`, `xml`)
- [ ] Generic types in backticks: `List<String>`
- [ ] No trailing whitespace

## Quick Validation

```bash
# Single file
uv run --project utils python -m utils.validate_note <file.md>

# With auto-fix
uv run --project utils python -m utils.validate_note <file.md> --fix
```

## Reference Documents

| Document | Purpose |
|----------|---------|
| [[TAXONOMY]] | Valid topics, subtopics, tags |
| [[FILE-NAMING-RULES]] | Naming conventions |
| [[NOTE-REVIEW-PROMPT]] | Full review process |
| [[VALIDATION-QUICKSTART]] | Validation commands |
