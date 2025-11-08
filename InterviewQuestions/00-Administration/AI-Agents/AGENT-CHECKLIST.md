---
---

# Quick Agent Checklist

**Purpose**: Fast reference checklist for creating and validating vault notes.

**For detailed instructions**: See AGENTS.md
**For controlled vocabularies**: See Vault-Rules/TAXONOMY.md

**Last Updated**: 2025-10-18

---

## Critical Rules (Always Follow)

-   REQUIRED: Both EN and RU in same file
-   REQUIRED: Exactly ONE topic from Vault-Rules/TAXONOMY.md
-   REQUIRED: Tags are English-only (Russian in aliases/content only)
-   REQUIRED: Set status: draft (never reviewed/ready)
-   REQUIRED: Link to ≥1 MOC and ≥2 related items
-   FORBIDDEN: Emoji in notes (use text: REQUIRED, FORBIDDEN, WARNING, NOTE)
-   FORBIDDEN: Brackets in YAML moc/related fields
-   FORBIDDEN: Russian in tags
-   FORBIDDEN: Multiple topics

---

## Before Creating a Note

### 1. Preparation

-   [ ] Read Vault-Rules/TAXONOMY.md for valid `topic` and `subtopics`
-   [ ] Determine correct folder (MUST match `topic`)
-   [ ] Choose correct template:
    -   Q&A: `_templates/_tpl-qna.md`
    -   Concept: `_templates/_tpl-concept.md`
    -   MOC: `_templates/_tpl-moc.md`

### 2. File Naming

-   [ ] Q&A: `q-<slug>--<topic>--<difficulty>.md`
-   [ ] Concept: `c-<slug>.md`
-   [ ] MOC: `moc-<topic>.md`
-   [ ] Use English kebab-case for slug
-   [ ] Verify folder matches topic

---

## YAML Frontmatter Checklist

### Required Fields (All Q&A Notes)

```yaml
# REQUIRED: Identification
- [ ] id: <subject>-<serial> (e.g., algo-001, android-134)
- [ ] title: "EN Title / RU Заголовок" (both languages)
- [ ] aliases: [EN Title, RU Заголовок] (array with both)

# REQUIRED: Classification
- [ ] topic: <value> (exactly ONE from Vault-Rules/TAXONOMY.md)
- [ ] subtopics: [value1, value2] (1-3 values, Android: controlled list)
- [ ] question_kind: coding | theory | system-design | android
- [ ] difficulty: easy | medium | hard

# REQUIRED: Language
- [ ] original_language: en | ru
- [ ] language_tags: [en] or [ru] or [en, ru]

# REQUIRED: Workflow
- [ ] status: draft (ALWAYS draft for agents)

# REQUIRED: Links (WITHOUT brackets in YAML!)
- [ ] moc: moc-<topic> (single value, NO brackets)
- [ ] related: [item1, item2, item3] (array 2-5 items, NO double brackets)

# REQUIRED: Timestamps
- [ ] created: YYYY-MM-DD
- [ ] updated: YYYY-MM-DD

# REQUIRED: Tags
- [ ] tags: [...] (English only, include difficulty/<level>)
```

### YAML Format Examples

**CORRECT Format**:

```yaml
moc: moc-algorithms # NO brackets
related: [c-hash-map, c-array] # Array WITHOUT double brackets
tags: [leetcode, arrays, difficulty/easy] # English only
```

**WRONG Format**:

```yaml
moc: [[moc-algorithms]]                # FORBIDDEN - has brackets
related: [[c-hash-map]], [[c-array]]   # FORBIDDEN - double brackets
tags: [leetcode, массивы]              # FORBIDDEN - Russian in tags
```

### Optional Fields

```yaml
- [ ] sources: (array of {url, note} objects if applicable)
- [ ] description: (brief summary if needed)
```

---

## Content Structure Checklist

### Q&A Notes (All Required)

```markdown
-   [ ] # Question (EN) - Clear English version
-   [ ] # Вопрос (RU) - Clear Russian version
-   [ ] ***
-   [ ] ## Answer (EN) - Approach, complexity, code examples
-   [ ] ## Ответ (RU) - Same content in Russian
-   [ ] ***
-   [ ] ## Follow-ups - Variations, edge cases, extensions
-   [ ] ## References - Include only if there are actual references; omit otherwise
-   [ ] ## Related Questions - Links to related Q&As; if none exist, use descriptive bullets
```

### Content Rules

-   [ ] Both languages have equivalent content
-   [ ] Code examples are identical in EN/RU (only comments translated)
-   [ ] All wikilinks use format `[[note-name]]`
-   [ ] Complexity analysis included (Time/Space)
-   [ ] Trade-offs explained where relevant

---

## Tags Checklist

### Required Tags

```yaml
# REQUIRED for all Q&A notes
- [ ] difficulty/easy | difficulty/medium | difficulty/hard

# REQUIRED for Android notes (mirror subtopics)
- [ ] android/<subtopic> for EACH subtopic in YAML
      Example: subtopics: [ui-compose, lifecycle]
               tags: [android/ui-compose, android/lifecycle, ...]
```

### Recommended Tags

```yaml
# Source tags (if applicable)
- [ ] leetcode, neetcode, hackerrank, system-design-primer, etc.

# Technique tags
- [ ] two-pointers, dp, sliding-window, binary-search, etc.

# Namespace tags (recommended)
- [ ] lang/kotlin, lang/java, lang/python (for code language)
- [ ] platform/android, platform/backend, platform/web
- [ ] topic/algorithms, topic/android (redundant but useful)
```

### Tag Rules

-   [ ] ALL tags in English (NO Cyrillic characters)
-   [ ] Use kebab-case for multi-word tags
-   [ ] Use namespaces where appropriate (difficulty/, android/, lang/, etc.)
-   [ ] Russian text goes ONLY in aliases and content sections

---

## Links Checklist

### YAML Links (Required)

```yaml
# MOC link (exactly one, no brackets)
- [ ] moc: moc-<topic>
      Valid: moc-algorithms, moc-android, moc-kotlin, moc-system-design,
             moc-backend, moc-cs, moc-tools

# Related links (2-5 recommended, array without double brackets)
- [ ] related: [c-concept1, c-concept2, q-question1--topic--difficulty]
      Include: 2-3 concept links (c-<slug>)
               2-3 question links (q-<slug>--<topic>--<difficulty>)
```

### Content Links (Recommended)

```markdown
-   [ ] Inline concept links in answer: [[c-hash-map]], [[c-binary-tree]]
-   [ ] Related questions section with categorized links
-   [ ] External references (documentation, articles, papers)
```

### Link Format Rules

-   [ ] Use `[[note-name]]` for wikilinks
-   [ ] In YAML: moc WITHOUT brackets
-   [ ] In YAML: related as array WITHOUT double brackets
-   [ ] In content: use double brackets `[[name]]`
-   [ ] All linked files exist or will be created

---

## Android-Specific Checklist

**When topic=android, MUST follow these rules:**

```yaml
# REQUIRED: Controlled subtopics
- [ ] subtopics: [value1, value2, value3]
      MUST choose from Android subtopics list in Vault-Rules/TAXONOMY.md
      Examples: ui-compose, lifecycle, coroutines, room, testing-unit, etc.

# REQUIRED: Mirror to tags
- [ ] For EACH subtopic, add android/<subtopic> tag
      Example: subtopics: [ui-compose, lifecycle]
               tags: [android/ui-compose, android/lifecycle, ...]

# REQUIRED: MOC link
- [ ] moc: moc-android

# RECOMMENDED: Question kind
- [ ] question_kind: android (for implementation questions)
      OR question_kind: theory (for conceptual questions)
```

### Android Example

```yaml
topic: android
subtopics: [ui-compose, ui-state, lifecycle]
tags:
    [
        android/ui-compose,
        android/ui-state,
        android/lifecycle,
        compose,
        jetpack,
        difficulty/medium,
    ]
moc: moc-android
```

---

## Final Validation Checklist

### File Organization

-   [ ] File in correct folder matching `topic` field
    -   algorithms → 20-Algorithms/
    -   system-design → 30-System-Design/
    -   android → 40-Android/
    -   databases/networking (backend) → 50-Backend/
    -   cs/os/concurrency → 60-CompSci/
    -   kotlin/programming-languages → 70-Kotlin/
    -   tools → 80-Tools/
-   [ ] Filename follows convention (q-/c-/moc- prefix, kebab-case)
-   [ ] No spaces in filename

### Content Quality

-   [ ] Both `# Question (EN)` and `# Вопрос (RU)` present
-   [ ] Both `## Answer (EN)` and `## Ответ (RU)` present
-   [ ] Content in both languages is equivalent
-   [ ] Code examples are valid and tested (if applicable)
-   [ ] Complexity analysis included (Time/Space)
-   [ ] No placeholder text (TODO, XXX, etc.)

### Metadata Quality

-   [ ] All required YAML fields present
-   [ ] topic is valid (from Vault-Rules/TAXONOMY.md)
-   [ ] subtopics are valid (Android: from Android list)
-   [ ] difficulty is easy|medium|hard
-   [ ] status is draft (NEVER reviewed/ready for agents)
-   [ ] Tags are English-only (no Russian)
-   [ ] Tags include difficulty/<level>
-   [ ] Android notes have android/\* tags

### Links Quality

-   [ ] moc field has valid MOC (without brackets)
-   [ ] related field has 2+ items (array without double brackets)
-   [ ] All wikilinks use correct format [[name]]
-   [ ] No broken links (all referenced files exist or will be created)
-   [ ] At least 1 concept link in related field
-   [ ] At least 1 MOC link in moc field
-   [ ] Related Questions: only link existing notes; if none exist, use descriptive bullets (no wikilinks)

### Format Quality

-   [ ] No emoji anywhere in the note
-   [ ] Proper Markdown formatting
-   [ ] Code blocks have language specified
-   [ ] Tables are properly formatted (if applicable)
-   [ ] No trailing whitespace
-   [ ] Lists use exactly one space after dash (`- Item`), never `-  Item`
-   [ ] No blank line between closing YAML `---` and the first heading

---

## Common Mistakes to Avoid

### FORBIDDEN: Multiple Topics

```yaml
# WRONG
topic: [algorithms, data-structures]

# CORRECT
topic: algorithms
```

### FORBIDDEN: Brackets in YAML Links

```yaml
# WRONG
moc: [[moc-algorithms]]
related: [[c-hash-map]], [[c-array]]

# CORRECT
moc: moc-algorithms
related: [c-hash-map, c-array]
```

### FORBIDDEN: Russian in Tags

```yaml
# WRONG
tags: [leetcode, массивы, хеш-таблица]

# CORRECT
tags: [leetcode, arrays, hash-map]
aliases: [Two Sum, Два слагаемых]  # Russian goes here
```

### FORBIDDEN: Android Without android/\* Tags

```yaml
# WRONG
topic: android
subtopics: [ui-compose, lifecycle]
tags: [compose, lifecycle, difficulty/medium]

# CORRECT
topic: android
subtopics: [ui-compose, lifecycle]
tags: [android/ui-compose, android/lifecycle, compose, difficulty/medium]
```

### FORBIDDEN: Setting Status to reviewed/ready

```yaml
# WRONG - Agents must never set these
status: reviewed
status: ready

# CORRECT - Always use draft
status: draft
```

### FORBIDDEN: Emoji in Content

```markdown
# WRONG

✅ Correct approach
❌ Wrong approach

# CORRECT

CORRECT: Proper approach
WRONG: Incorrect approach
```

### FORBIDDEN: Separate Files for Languages

```
# WRONG - Don't create separate files
q-two-sum-en.md
q-two-sum-ru.md

# CORRECT - One file with both languages
q-two-sum--algorithms--easy.md
  # Question (EN)
  # Вопрос (RU)
```

---

## Quick Reference Values

### Topics (Pick Exactly ONE)

```
Core Technical:
  algorithms, data-structures, system-design, android, kotlin,
  programming-languages

Architecture & Patterns:
  architecture-patterns, concurrency, distributed-systems, databases

Infrastructure:
  networking, operating-systems, security, performance, cloud

Development:
  testing, devops-ci-cd, tools, debugging

Other:
  ui-ux-accessibility, behavioral, cs
```

### Other Fields

```yaml
difficulty: easy | medium | hard

question_kind: coding | theory | system-design | android

status: draft  # ALWAYS draft for agents

original_language: en | ru

language_tags: [en] | [ru] | [en, ru]  # Goal: [en, ru]
```

### Available MOCs

```
moc-algorithms        # For algorithms, data-structures
moc-system-design     # For system-design, distributed-systems
moc-android           # For android
moc-kotlin            # For kotlin, programming-languages
moc-backend           # For databases, networking (backend)
moc-cs                # For os, concurrency, cs fundamentals
moc-tools             # For tools, debugging
```

### Folder Structure

```
20-Algorithms/      # Coding problems, LeetCode, data structures
30-System-Design/   # Design questions, scalability
40-Android/         # Android platform, Jetpack, Compose
50-Backend/         # Databases, backend networking
60-CompSci/         # OS, CS fundamentals, theory
70-Kotlin/          # Kotlin language, programming languages
80-Tools/           # Git, build systems, IDEs, productivity
10-Concepts/        # Reusable theory notes (c-<slug>.md)
90-MOCs/            # Maps of Content (moc-<topic>.md)
```

---

## Quick Examples

### Minimal Valid Q&A YAML

```yaml
---
id: algo-001
title: Two Sum / Два слагаемых
aliases: [Two Sum, Два слагаемых]
topic: algorithms
subtopics: [arrays, hash-map]
question_kind: coding
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-algorithms
related: [c-hash-map, c-array]
created: 2025-10-18
updated: 2025-10-18
tags: [leetcode, arrays, hash-map, difficulty/easy]
---
```

### Minimal Valid Android YAML

```yaml
---
id: android-001
title: Compose State / Состояние Compose
aliases: [Compose State, Состояние Compose]
topic: android
subtopics: [ui-compose, ui-state]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-compose-state, c-viewmodel]
created: 2025-10-18
updated: 2025-10-18
tags: [android/ui-compose, android/ui-state, compose, difficulty/medium]
---
```

---

## When Uncertain

1. **Check Vault-Rules/TAXONOMY.md** for valid topic/subtopic/difficulty values
2. **Check templates** in `_templates/` for correct structure
3. **Set status: draft** and let human decide
4. **Ask the user** if requirements are ambiguous
5. **Review AGENTS.md** for detailed instructions

---

## References

-   **Controlled vocabularies**: `00-Administration/Vault-Rules/TAXONOMY.md`
-   **Detailed agent instructions**: `AGENTS.md`
-   **Full vault rules**: `00-Administration/README.md`
-   **Link health dashboard**: `00-Administration/Linking-System/LINK-HEALTH-DASHBOARD.md`
-   **Templates**: `_templates/_tpl-qna.md`, `_tpl-concept.md`, `_tpl-moc.md`
-   **Claude Code setup**: `.claude/README.md`, `.claude/custom_instructions.md`
-   **Claude Code commands**: `.claude/commands/` (create-qna, validate, translate, etc.)
-   **Cursor AI rules**: `.cursor/rules/` (modern MDC format)
-   **Gemini CLI guide**: `GEMINI.md`
-   **AI tools comparison**: `00-Administration/AI-TOOLS.md`

---

**Version**: 2.0 (Expanded and optimized)
**Last Updated**: 2025-10-18
**Use this before every note creation or modification**
