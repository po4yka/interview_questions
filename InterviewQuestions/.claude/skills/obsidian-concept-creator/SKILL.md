---
name: obsidian-concept-creator
description: >
  Create reusable concept notes in 10-Concepts/ directory. Generates
  bilingual concept documentation with summary, use cases, trade-offs,
  and references. Uses c-[concept-name].md naming pattern and
  _tpl-concept.md template structure.
---

# Obsidian Concept Note Creator

## Purpose

Create concept notes for fundamental technical concepts:
- Reusable reference documentation
- Bilingual summaries (EN/RU)
- Use cases and trade-offs
- Links to related Q&As
- Placed in `10-Concepts/` directory

Concept notes serve as building blocks referenced by multiple Q&A notes.

## When to Use

Activate this skill when user requests:
- "Create concept note for [concept]"
- "Document [concept] as a concept"
- "Add concept about [topic]"
- When creating fundamental building block content
- When multiple Q&As reference the same concept

## Prerequisites

Required context:
- Concept name/topic
- Understanding of the concept to document
- `_templates/_tpl-concept.md` template structure

## Process

### Step 1: Identify Concept

Determine:
- **Concept name**: Clear, specific name (e.g., "ViewModel", "Coroutines", "MVVM Pattern")
- **Topic area**: Which domain (Android, Kotlin, algorithms, etc.)
- **Scope**: What the concept covers and what it doesn't

Good concept candidates:
- Architectural patterns (MVVM, MVI, Clean Architecture)
- Language features (Coroutines, Flow, Generics)
- Data structures (HashMap, Binary Tree, Graph)
- Android components (ViewModel, LiveData, Compose State)
- Algorithms (Binary Search, DFS, Dynamic Programming)

### Step 2: Generate Metadata

**Filename Pattern**:
```
c-[english-concept-name].md
```

**Filename Rules**:
- Prefix with `c-` (for "concept")
- English only (NO Cyrillic)
- Lowercase, hyphens as separators
- 1-4 words typically
- Descriptive and searchable

**Examples**:
- `c-viewmodel.md`
- `c-coroutines.md`
- `c-mvvm-pattern.md`
- `c-hash-map.md`
- `c-binary-search.md`
- `c-compose-state.md`

**Folder**: Always `10-Concepts/`

### Step 3: Build YAML Frontmatter

```yaml
---
id: concept-XXX                 # Sequential ID
title: Concept Name / Название концепции
aliases: [Name EN, Alternative EN, Название RU, Альтернатива RU]
summary: Brief one-sentence description of the concept
tags: [concept, topic-area, related-tags]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

**YAML Fields**:
- `id`: Format `concept-XXX` (e.g., concept-001, concept-042)
- `title`: Bilingual (EN / RU)
- `aliases`: List alternative names, acronyms, translations (4-8 items recommended)
- `summary`: One-sentence English description (for quick reference)
- `tags`: Start with `concept`, add topic areas (e.g., kotlin, android, algorithms)
- `created`/`updated`: YYYY-MM-DD format

**Note**: Concept notes don't use `status` field (not interview questions).

### Step 4: Build Content Structure

Use template pattern from `_templates/_tpl-concept.md`:

```markdown
# Concept Name / Название концепции

## Summary (EN)

Brief 2-3 paragraph explanation of the concept:
- What it is
- Why it exists
- Key characteristics

## Summary (RU)

Краткое объяснение концепции в 2-3 абзацах:
- Что это такое
- Зачем существует
- Ключевые характеристики

---

## Key Characteristics

- **Characteristic 1**: Explanation
- **Characteristic 2**: Explanation
- **Characteristic 3**: Explanation

---

## Use Cases

**When to use this concept**:
1. Scenario 1 with explanation
2. Scenario 2 with explanation
3. Scenario 3 with explanation

**Examples**:
- Practical example 1
- Practical example 2

---

## Trade-offs

### Advantages
- ✓ Benefit 1
- ✓ Benefit 2
- ✓ Benefit 3

### Disadvantages
- ✗ Limitation 1
- ✗ Limitation 2
- ✗ Limitation 3

---

## Code Example (Optional)

\```kotlin
// Simple demonstration of the concept
fun example() {
    // Implementation
}
\```

---

## Related Concepts

- [[c-related-concept-1]] - How it relates
- [[c-related-concept-2]] - How it relates
- [[c-related-concept-3]] - How it relates

---

## Questions Using This Concept

- [[q-question-1--topic--difficulty]] - Brief description
- [[q-question-2--topic--difficulty]] - Brief description
- [[q-question-3--topic--difficulty]] - Brief description

---

## References

### Internal
- [[moc-topic]] - Main MOC

### External
- [Official Documentation](https://url)
- [Tutorial or Article](https://url)
- [Video Resource](https://url)
```

**Content Requirements**:
- Both EN and RU summaries (substantial, not placeholder)
- At least 3 key characteristics
- At least 2 use cases
- Balanced trade-offs (advantages and disadvantages)
- Links to 2-3 related concepts (if available)
- Links to 3-5 Q&As using this concept (if available)

### Step 5: Quality Check

Before finalizing:

**Structure**:
- [ ] Both EN and RU summaries present
- [ ] Key characteristics section complete
- [ ] Use cases section complete
- [ ] Trade-offs section complete (both advantages and disadvantages)
- [ ] Related concepts linked (2+ items)
- [ ] References section present

**Content**:
- [ ] Summaries are clear and accurate
- [ ] Concept is well-defined
- [ ] Use cases are practical
- [ ] Trade-offs are balanced
- [ ] Links are valid

**YAML**:
- [ ] All required fields present
- [ ] Title is bilingual
- [ ] Aliases include translations (4+ items)
- [ ] Tags include "concept" and topic area

**File Organization**:
- [ ] File in `10-Concepts/` directory
- [ ] Filename follows `c-[name].md` pattern
- [ ] Filename is English-only, lowercase, hyphenated

### Step 6: Create File and Confirm

1. **Create file** at `10-Concepts/c-[concept-name].md`
2. **Write complete content**
3. **Report to user**:
   - Filename
   - Concept name
   - Topic area
   - Number of related concepts linked
   - Number of Q&As linked

## Examples

### Example 1: Android ViewModel Concept

**User Request**: "Create concept note for Android ViewModel"

**Generated**:
- Filename: `c-viewmodel.md`
- Folder: `10-Concepts/`

**YAML**:
```yaml
---
id: concept-015
title: ViewModel / ViewModel (Модель представления)
aliases: [ViewModel, ViewModels, Модель представления, AndroidX ViewModel]
summary: Architecture component that stores and manages UI-related data in a lifecycle-conscious way
tags: [concept, android, architecture-patterns, jetpack, lifecycle]
created: 2025-11-09
updated: 2025-11-09
---
```

**Content** (excerpt):
```markdown
# ViewModel / ViewModel (Модель представления)

## Summary (EN)

ViewModel is an Android Architecture Component designed to store and manage
UI-related data in a lifecycle-conscious way. It survives configuration
changes like screen rotations and provides a clean separation between
UI controllers and business logic.

## Summary (RU)

ViewModel — это компонент архитектуры Android, предназначенный для хранения
и управления данными UI с учётом жизненного цикла. Он переживает изменения
конфигурации, такие как поворот экрана, и обеспечивает чёткое разделение
между UI-контроллерами и бизнес-логикой.

---

## Key Characteristics

- **Lifecycle-aware**: Survives configuration changes
- **UI-independent**: No references to Views or Activities
- **Scoped**: Tied to Activity, Fragment, or Navigation graph
- **Data holder**: Stores UI state and exposes via LiveData or Flow

---

## Use Cases

**When to use ViewModel**:
1. Store UI state that should survive configuration changes
2. Separate business logic from UI controllers
3. Share data between Fragments in the same Activity
4. Perform background operations with lifecycle awareness

---

## Trade-offs

### Advantages
- ✓ Survives configuration changes automatically
- ✓ Clear separation of concerns
- ✓ Testable business logic
- ✓ Integrated with Jetpack components

### Disadvantages
- ✗ Cannot hold Context references (risk of leaks)
- ✗ Requires learning lifecycle concepts
- ✗ Adds architectural complexity for simple screens

---

## Related Concepts

- [[c-livedata]] - Observable data holder often used with ViewModel
- [[c-mvvm-pattern]] - Architecture pattern using ViewModel
- [[c-lifecycle]] - Android lifecycle that ViewModel respects

---

## Questions Using This Concept

- [[q-viewmodel-basics--android--easy]]
- [[q-viewmodel-factory--android--medium]]
- [[q-viewmodel-vs-savedstatehandle--android--hard]]

---

## References

### External
- [Android Developers: ViewModel](https://developer.android.com/topic/libraries/architecture/viewmodel)
- [Android Architecture Guide](https://developer.android.com/jetpack/guide)
```

### Example 2: Kotlin Coroutines Concept

**User Request**: "Create concept for Kotlin coroutines"

**Generated**:
- Filename: `c-coroutines.md`
- Folder: `10-Concepts/`

**YAML**:
```yaml
---
id: concept-008
title: Coroutines / Корутины
aliases: [Coroutines, Kotlin Coroutines, Корутины, Сопрограммы, Suspend Functions]
summary: Lightweight concurrency framework for asynchronous programming in Kotlin
tags: [concept, kotlin, concurrency, async, coroutines]
created: 2025-11-09
updated: 2025-11-09
---
```

### Example 3: Algorithm Concept (Binary Search)

**Generated**:
- Filename: `c-binary-search.md`
- Folder: `10-Concepts/`

**YAML**:
```yaml
---
id: concept-023
title: Binary Search / Бинарный поиск
aliases: [Binary Search, Двоичный поиск, Бинарный поиск, Logarithmic Search]
summary: Efficient search algorithm that finds target in sorted array using divide-and-conquer
tags: [concept, algorithms, search, divide-and-conquer, logarithmic]
created: 2025-11-09
updated: 2025-11-09
---
```

## Error Handling

### Concept Already Exists

**Problem**: Concept file with same name already exists

**Solution**:
1. Read existing file
2. Inform user it already exists
3. Offer to update/enhance existing concept instead
4. If truly different, adjust name to differentiate

### Ambiguous Concept Scope

**Problem**: Concept name could mean different things

**Solution**:
1. Ask user for clarification
2. Provide examples of each interpretation
3. Suggest more specific names if needed
4. Wait for confirmation before proceeding

### Limited Related Content

**Problem**: No existing Q&As or concepts to link to

**Solution**:
1. Create concept with minimal links
2. Note that links should be added as content grows
3. Mark "Questions Using This Concept" as TBD
4. Concept can still be valuable for future reference

## Integration with Other Skills

**Common workflows**:

1. **Create concept first, then Q&As**:
   → Use `obsidian-concept-creator` for foundational concept
   → Use `obsidian-qna-creator` for questions, linking to concept

2. **Extract concept from Q&A**:
   → Identify repeated explanation in multiple Q&As
   → Use `obsidian-concept-creator` to document concept
   → Update Q&As to link to concept
   → Use `obsidian-link-analyzer` to find more Q&As to link

3. **Build concept library**:
   → Create multiple related concepts
   → Cross-link concepts using "Related Concepts" section
   → Update MOCs to reference concept collection

## Notes

**Purpose**: Concept notes reduce duplication and provide authoritative reference for fundamental ideas.

**Reusability**: One concept note can be referenced by many Q&A notes, making vault more maintainable.

**Depth**: Concepts should be thorough but concise - detailed enough to be useful, brief enough to be readable.

**Updates**: As understanding deepens, concept notes can be enhanced over time (update `updated` date).

---

**Version**: 1.0
**Last Updated**: 2025-11-09
**Status**: Production Ready
