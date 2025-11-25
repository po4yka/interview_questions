---
date created: Tuesday, November 25th 2025, 8:28:55 pm
date modified: Tuesday, November 25th 2025, 8:54:04 pm
---

# Naming Examples and Patterns

**Purpose**: Detailed examples and common naming patterns.
**Last Updated**: 2025-11-25

See [[FILE-NAMING-RULES]] for core rules.

## Question Type Patterns

### What/Who/Why Questions

```
q-what-is-viewmodel--android--medium.md
q-what-are-coroutines--kotlin--easy.md
q-why-use-fragments--android--medium.md
```

### How Questions

```
q-how-to-create-coroutine--kotlin--easy.md
q-how-viewmodel-survives-rotation--android--medium.md
q-how-to-optimize-compose--android--hard.md
```

### Comparison Questions

```
q-recyclerview-vs-listview--android--easy.md
q-mvvm-vs-mvi--android--hard.md
q-flow-vs-livedata--android--medium.md
q-git-merge-vs-rebase--tools--medium.md
```

### Implementation Questions

```
q-implement-binary-search--algorithms--easy.md
q-create-custom-view--android--hard.md
q-design-url-shortener--system-design--hard.md
```

### Theory Questions

```
q-solid-principles--programming-languages--medium.md
q-design-patterns-overview--architecture-patterns--medium.md
q-acid-properties--databases--medium.md
```

## Language Handling

| Aspect | Language | Example |
|--------|----------|---------|
| **Filename** | English ONLY | `q-what-is-viewmodel--android--medium.md` |
| **YAML title** | Bilingual | `title: What is ViewModel / Chto takoe ViewModel` |
| **YAML aliases** | Bilingual | `aliases: [ViewModel, VyuModel]` |
| **Content headings** | Bilingual | `# Question (EN)` and `# Vopros (RU)` |
| **YAML tags** | English ONLY | `tags: [android, viewmodel]` |

## Complete Note Example

**Filename**: `q-what-is-viewmodel--android--medium.md`

```yaml
---
id: android-001
title: What is ViewModel / Chto takoe ViewModel
aliases: [ViewModel, VyuModel, Android ViewModel]

topic: android
subtopics: [lifecycle, architecture-mvvm]
question_kind: theory
difficulty: medium

original_language: ru
language_tags: [en, ru]

status: draft
moc: moc-android
related: [c-viewmodel, c-mvvm-pattern, q-viewmodel-vs-savedstate--android--medium]

created: 2025-10-18
updated: 2025-10-18
tags: [android, viewmodel, lifecycle, architecture, difficulty/medium]
---

# Question (EN)
> What is ViewModel and why is it used in Android?

# Vopros (RU)
> Chto takoe ViewModel i dlya chego ispolzuetsya v Android?

---

## Answer (EN)
[English answer content...]

## Otvet (RU)
[Russian answer content...]
```

## Common Mistakes

### Russian Characters in Filename

```
# WRONG
q-chto-takoe-viewmodel--android--medium.md

# CORRECT
q-what-is-viewmodel--android--medium.md
```

### Uppercase Letters

```
# WRONG
q-ViewModel-Basics--android--easy.md

# CORRECT
q-viewmodel-basics--android--easy.md
```

### Spaces or Underscores

```
# WRONG
q-what is viewmodel--android--medium.md
q-what_is_viewmodel--android--medium.md

# CORRECT
q-what-is-viewmodel--android--medium.md
```

### Invalid Topic

```
# WRONG
q-coroutine-basics--programming--easy.md

# CORRECT (use valid topic from TAXONOMY)
q-coroutine-basics--kotlin--easy.md
```

### Missing Difficulty

```
# WRONG
q-viewmodel-basics--android.md

# CORRECT
q-viewmodel-basics--android--easy.md
```

### Too Generic Slug

```
# WRONG
q-question-1--android--medium.md
q-android-basics--android--easy.md

# CORRECT
q-viewmodel-lifecycle--android--medium.md
q-activity-lifecycle--android--easy.md
```

### Too Long Slug

```
# WRONG (too long)
q-how-to-optimize-recyclerview-for-better-performance--android--medium.md

# CORRECT (concise)
q-recyclerview-optimization--android--medium.md
```

## Why English-Only Filenames?

### Technical Reasons

1. **Cross-platform compatibility** - Windows, macOS, Linux handle ASCII consistently
2. **Git compatibility** - Fewer encoding issues in diffs and logs
3. **URL safety** - Can be used in web URLs without encoding
4. **Command-line friendly** - Works with all shell commands
5. **Tool compatibility** - Works with all IDEs and build tools

### Practical Reasons

1. **Search efficiency** - Easier to search and grep
2. **Consistency** - Uniform naming across knowledge base
3. **Accessibility** - Works in all keyboard layouts
4. **Obsidian compatibility** - Wikilinks and Dataview work correctly

## See Also

- [[FILE-NAMING-RULES]] - Core naming rules
- [[NAMING-VALIDATION]] - Validation scripts
- [[TAXONOMY]] - Valid topic values
