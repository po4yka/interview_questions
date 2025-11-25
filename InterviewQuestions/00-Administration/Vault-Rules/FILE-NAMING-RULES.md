---
date created: Tuesday, November 25th 2025, 8:28:29 pm
date modified: Tuesday, November 25th 2025, 8:54:04 pm
---

# File Naming Rules

**Purpose**: Mandatory file naming conventions for all vault notes.
**Last Updated**: 2025-11-25

**Critical Rule**: ALL filenames MUST use English-only characters.

## Core Principles

### REQUIRED
- English characters only (a-z, 0-9, hyphens)
- Lowercase letters only
- Hyphens (-) as word separators
- Prefix indicating note type (q-, c-, moc-)
- Topic and difficulty in filename (for Q&A notes)
- Descriptive slug (3-8 words)

### FORBIDDEN
- Cyrillic (Russian) characters
- Uppercase letters
- Spaces or underscores
- Special characters (!@#$%^&*etc.)

## File Naming Patterns

### Pattern 1: Question Notes (Q&A)

```
q-[english-slug]--[topic]--[difficulty].md
```

**Examples**:
```
q-what-is-viewmodel--android--medium.md
q-kotlin-coroutine-context--kotlin--medium.md
q-two-sum-problem--algorithms--easy.md
q-design-url-shortener--system-design--hard.md
```

### Pattern 2: Concept Notes

```
c-[english-concept-name].md
```

**Examples**:
```
c-viewmodel.md
c-kotlin-coroutines.md
c-mvvm-architecture.md
c-hash-map.md
```

### Pattern 3: MOC (Map of Content) Notes

```
moc-[english-topic-name].md
```

**Examples**:
```
moc-android.md
moc-kotlin.md
moc-algorithms.md
```

## Topic -> Folder Mapping

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

**Rule**: Filename topic MUST match the folder where the file is stored.

## Difficulty Values

```
easy      # Basic concepts, simple implementation
medium    # Moderate complexity, standard patterns
hard      # Complex, advanced concepts
```

## Slug Creation Guidelines

1. **English Words ONLY** - Translate Russian to English
2. **3-8 Words Maximum** - Keep it concise
3. **Lowercase with Hyphens** - No uppercase or underscores
4. **Be Specific** - Avoid generic slugs like "basics" or "overview"
5. **Standard Terms** - Use official documentation terminology

### Quick Examples

| Russian Question | English Slug |
|------------------|--------------|
| Che takoe ViewModel | what-is-viewmodel |
| Kak sozdat korutinu | how-to-create-coroutine |
| Raznitsa mezhdu MVI i MVVM | difference-between-mvi-mvvm |

## Implementation Checklist

- [ ] Filename uses English characters only (a-z, 0-9, hyphens)
- [ ] Filename is all lowercase
- [ ] Filename follows pattern: `q-[slug]--[topic]--[difficulty].md`
- [ ] Topic matches value from [[TAXONOMY]]
- [ ] Difficulty is `easy` | `medium` | `hard`
- [ ] File is in correct folder matching topic

## See Also

- [[NAMING-EXAMPLES]] - Detailed examples and common patterns
- [[NAMING-VALIDATION]] - Validation scripts and tools
- [[TAXONOMY]] - Valid topic values and controlled vocabularies
- [[AGENT-CHECKLIST]] - Quick reference for AI agents
