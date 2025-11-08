---
---

# Claude Code Agent Guide

**Quick reference for using Claude Code with this Obsidian Interview Vault.**

This guide provides workflows, slash commands, and best practices for vault maintenance using Claude Code.

**Last Updated**: 2025-10-18

---

## Quick Start

**System Context** (auto-loaded from `.claude/custom_instructions.md`):

Claude Code automatically loads custom instructions from `.claude/custom_instructions.md` when you start a session in this directory. The instructions include:

- Bilingual (EN/RU) vault structure
- YAML frontmatter requirements
- File naming conventions
- Controlled vocabularies from Vault-Rules/TAXONOMY.md
- Linking requirements
- No emoji rule

**Key Files**:
- **Full rules**: `AGENTS.md`
- **Quick checklist**: `00-Administration/AGENT-CHECKLIST.md`
- **Controlled vocabularies**: `00-Administration/Vault-Rules/TAXONOMY.md`
- **File naming rules**: `00-Administration/Vault-Rules/FILE-NAMING-RULES.md`
- **Linking strategy**: `00-Administration/Linking-System/LINKING-STRATEGY.md`
- **Templates**: `_templates/_tpl-qna.md`, `_tpl-concept.md`, `_tpl-moc.md`
- **Claude Code setup**: `.claude/README.md`
- **Slash commands**: `.claude/commands/*.md`

---

## Core Principles (Non-Negotiable)

### REQUIRED Rules

1. **Both EN and RU in same file** - NEVER split languages into separate files
2. **Exactly ONE topic** from TAXONOMY.md - NEVER use multiple topics
3. **English-only tags** - Russian goes in `aliases` and content only
4. **Status: draft** - ALWAYS use `draft` for AI-created/modified notes
5. **Link to MOC and concepts** - Every Q&A MUST link to ≥1 MOC and ≥2 related items
6. **No emoji** - Use text equivalents: REQUIRED, FORBIDDEN, WARNING, NOTE
7. **Folder matches topic** - File MUST be in folder matching its `topic` field
8. **YAML format**: `moc: moc-name` (no brackets), `related: [file1, file2]` (array, no double brackets)

### FORBIDDEN Rules

- FORBIDDEN: Splitting EN/RU into separate files
- FORBIDDEN: Russian in tags
- FORBIDDEN: Multiple topics in `topic` field
- FORBIDDEN: Setting `status: reviewed` or `status: ready` (only humans can)
- FORBIDDEN: Brackets in YAML `moc` field
- FORBIDDEN: Double brackets in YAML `related` field
- FORBIDDEN: Emoji anywhere in vault notes
- FORBIDDEN: File in wrong folder (not matching topic)

---

## Folder Structure

```
00-Administration/  # Vault docs (README, TAXONOMY, AGENTS, etc.)
10-Concepts/        # Reusable theory notes (c-<slug>.md)
20-Algorithms/      # Coding problems (q-<slug>--algorithms--<difficulty>.md)
30-System-Design/   # Design questions (q-<slug>--system-design--<difficulty>.md)
40-Android/         # Android Q&As (q-<slug>--android--<difficulty>.md)
50-Backend/         # Backend/database questions (q-<slug>--databases--<difficulty>.md)
60-CompSci/         # CS fundamentals (OS, networking, etc.)
70-Kotlin/          # Kotlin language questions (q-<slug>--kotlin--<difficulty>.md)
80-Tools/           # Development tools (q-<slug>--tools--<difficulty>.md)
90-MOCs/            # Maps of Content (moc-<topic>.md)
_templates/         # Templater templates
.claude/            # Claude Code configuration
```

---

## Slash Commands

Claude Code provides custom slash commands in `.claude/commands/`:

### /create-qna
Create a new Q&A note with full validation.

**Usage**:
```
/create-qna Create a note about coroutine context
Topic: kotlin
Difficulty: medium
```

**What it does**:
1. Determines correct folder (70-Kotlin/)
2. Generates filename (q-coroutine-context--kotlin--medium.md)
3. Uses template from `_templates/_tpl-qna.md`
4. Fills YAML with all required fields
5. Sets `status: draft`
6. Adds MOC and related links
7. Creates bilingual content structure

### /create-concept
Create a new concept note.

**Usage**:
```
/create-concept Create concept for MVVM pattern
```

**What it does**:
1. Places in `10-Concepts/`
2. Uses template from `_templates/_tpl-concept.md`
3. Creates c-mvvm-pattern.md
4. Includes EN/RU summary sections

### /create-moc
Create a new MOC (Map of Content) to organize related Q&As.

**Usage**:
```
/create-moc Create MOC for Kotlin topic
```

**What it does**:
1. Places in `90-MOCs/`
2. Uses template from `_templates/_tpl-moc.md`
3. Creates moc-kotlin.md
4. Includes study paths and Dataview queries
5. Organizes content by difficulty and subtopic

### /translate
Add missing language to an existing note.

**Usage**:
```
/translate Add Russian translation to q-coroutine-basics--kotlin--easy.md
```

**What it does**:
1. Reads the file
2. Identifies missing language sections
3. Translates while preserving code and links
4. Updates `language_tags` to `[en, ru]`
5. Keeps `status: draft`

### /validate
Comprehensive validation of a note against vault rules.

**Usage**:
```
/validate 40-Android/q-compose-state--android--medium.md
```

**What it does**:
1. Checks YAML completeness
2. Validates topic against TAXONOMY.md
3. Checks tags (English-only, includes difficulty/*)
4. Verifies Android subtopic mirroring
5. Checks folder placement
6. Validates links (MOC, related)
7. Checks content structure (both languages)
8. Reports issues with severity levels

### /link-concepts
Suggest and add cross-references between notes.

**Usage**:
```
/link-concepts q-coroutine-scope--kotlin--medium.md
```

**What it does**:
1. Analyzes the note
2. Searches vault for related concepts and questions
3. Suggests 3-5 relevant links
4. Adds to `related` field and content sections

---

## Common Workflows

### Workflow 1: Create New Q&A Note

**User request**: "Create a note about Kotlin coroutine context"

**Agent actions**:
1. Determine classification:
   - Topic: `kotlin`
   - Difficulty: `medium`
   - Question kind: `theory`
2. Generate filename: `q-coroutine-context--kotlin--medium.md`
3. Determine folder: `70-Kotlin/`
4. Use template: `_templates/_tpl-qna.md`
5. Fill YAML:
   ```yaml
   id: kotlin-001
   title: Coroutine Context / Контекст корутин
   aliases: [Coroutine Context, Контекст корутин]
   topic: kotlin
   subtopics: [coroutines, concurrency]
   question_kind: theory
   difficulty: medium
   original_language: en
   language_tags: [en, ru]
   status: draft
   moc: moc-kotlin
   related: [c-coroutines, c-coroutine-scope, q-coroutine-scope--kotlin--medium]
   created: 2025-10-18
   updated: 2025-10-18
   tags: [kotlin, coroutines, concurrency, difficulty/medium]
   ```
6. Write content in both EN and RU
7. Validate using checklist
8. Confirm with user

**Can use slash command**: `/create-qna`

---

### Workflow 2: Translate Existing Note

**User request**: "Add Russian translation to q-coroutine-basics--kotlin--easy.md"

**Agent actions**:
1. Read the file
2. Check for existing sections (has EN, missing RU)
3. Translate:
   - `# Question (EN)` → add `# Вопрос (RU)`
   - `## Answer (EN)` → add `## Ответ (RU)`
   - Preserve code examples (same in both)
   - Preserve all links
4. Update YAML:
   - `language_tags: [en, ru]`
   - `updated: 2025-10-18`
   - Keep `status: draft`
5. Confirm translation accuracy with user

**Can use slash command**: `/translate`

---

### Workflow 3: Validate Note

**User request**: "Validate 40-Android/q-compose-state--android--medium.md"

**Agent actions**:
1. Read the file
2. Check YAML frontmatter:
   - All required fields present
   - `topic: android` (valid from TAXONOMY.md)
   - `subtopics: [ui-compose, ui-state]` (valid Android subtopics)
   - `tags` include `android/ui-compose`, `android/ui-state` (mirrored)
   - `tags` include `difficulty/medium`
   - `moc: moc-android` (valid, no brackets)
   - `related: [c-compose-state, c-viewmodel]` (valid, array)
3. Check file organization:
   - File in `40-Android/` (matches topic)
   - Filename follows pattern
4. Check content structure:
   - `# Question (EN)` present
   - `# Вопрос (RU)` present
   - `## Answer (EN)` present
   - `## Ответ (RU)` present
5. Report findings with severity levels
6. Offer to fix issues if found

**Can use slash command**: `/validate`

---

### Workflow 4: Create Concept Note

**User request**: "Create a concept note for MVVM pattern"

**Agent actions**:
1. Filename: `c-mvvm-pattern.md`
2. Folder: `10-Concepts/`
3. Use template: `_templates/_tpl-concept.md`
4. Fill YAML:
   ```yaml
   id: concept-001
   title: MVVM Pattern / Паттерн MVVM
   aliases: [MVVM, Model-View-ViewModel, MVVM паттерн]
   summary: Architectural pattern separating UI from business logic
   tags: [concept, architecture-patterns, mvvm, android]
   ```
5. Write content:
   - Summary (EN/RU)
   - Use cases
   - Trade-offs
   - References
6. Link to related Q&As

**Can use slash command**: `/create-concept`

---

### Workflow 5: Add Cross-References

**User request**: "Suggest related questions for q-coroutine-scope--kotlin--medium.md"

**Agent actions**:
1. Read the note
2. Analyze metadata (topic, subtopics, difficulty)
3. Search vault for related notes:
   - Same topic (`kotlin`)
   - Shared subtopics (`coroutines`, `concurrency`)
   - Adjacent difficulty levels
4. Suggest 3-5 relevant links:
   - Easier: `q-what-is-coroutine--kotlin--easy`
   - Same level: `q-coroutine-context--kotlin--medium`
   - Harder: `q-structured-concurrency--kotlin--hard`
5. Add to YAML `related` field
6. Add to "Related Questions" content section

**Can use slash command**: `/link-concepts`

---

## File Naming Patterns

### Question Notes
```
q-[english-slug]--[topic]--[difficulty].md
```

**Examples**:
```
q-what-is-viewmodel--android--medium.md
q-coroutine-context--kotlin--medium.md
q-two-sum--algorithms--easy.md
q-design-url-shortener--system-design--hard.md
```

**Rules**:
- English only (NO Cyrillic)
- Lowercase, hyphens as separators
- 3-8 words in slug
- Topic from TAXONOMY.md
- Difficulty: easy | medium | hard

### Concept Notes
```
c-[english-concept-name].md
```

**Examples**:
```
c-viewmodel.md
c-coroutines.md
c-mvvm-pattern.md
c-hash-map.md
```

### MOC Notes
```
moc-[english-topic-name].md
```

**Examples**:
```
moc-android.md
moc-kotlin.md
moc-algorithms.md
```

**See**: `00-Administration/Vault-Rules/FILE-NAMING-RULES.md` for complete rules

---

## Controlled Vocabularies

### Topics (Choose Exactly ONE)

**CRITICAL**: MUST match value from `00-Administration/Vault-Rules/TAXONOMY.md`

```yaml
# Core Technical
algorithms, data-structures, system-design, android, kotlin, programming-languages

# Architecture & Patterns
architecture-patterns, concurrency, distributed-systems, databases

# Infrastructure
networking, operating-systems, security, performance, cloud

# Development
testing, devops-ci-cd, tools, debugging

# Other
ui-ux-accessibility, behavioral, cs
```

**Total**: 22 valid topics

### Other Controlled Values

```yaml
difficulty: easy | medium | hard
question_kind: coding | theory | system-design | android
original_language: en | ru
language_tags: [en] | [ru] | [en, ru]
status: draft | reviewed | ready | retired  # AI uses draft only
```

**See**: `00-Administration/Vault-Rules/TAXONOMY.md` for complete lists

---

## Android-Specific Rules

When `topic: android`, you MUST:

1. **Use Android subtopics** from TAXONOMY.md controlled list
2. **Mirror subtopics to tags** with `android/` prefix

**Example**:
```yaml
topic: android
subtopics: [ui-compose, lifecycle, coroutines]
tags: [
  android/ui-compose,     # REQUIRED - mirrored from subtopics
  android/lifecycle,      # REQUIRED - mirrored from subtopics
  android/coroutines,     # REQUIRED - mirrored from subtopics
  compose,                # Optional additional tags
  jetpack,
  difficulty/medium
]
```

**Android Subtopics** (examples from TAXONOMY.md):
```
ui-compose, ui-views, ui-navigation, ui-state, ui-animation,
architecture-mvvm, architecture-mvi, architecture-clean,
lifecycle, activity, fragment, service,
coroutines, flow, threads-sync,
room, datastore, files-media,
testing-unit, testing-instrumented, testing-ui,
gradle, build-variants, dependency-management
```

**See**: `00-Administration/Vault-Rules/TAXONOMY.md` for complete Android subtopics list

---

## YAML Frontmatter Template

### Complete Q&A YAML Example

```yaml
---
id: kotlin-001                         # <subject>-<serial> (e.g., algo-001, android-134)
title: Question Title EN / Заголовок RU
aliases: [Title EN, Заголовок RU]

# Classification
topic: kotlin                          # ONE from TAXONOMY.md
subtopics: [coroutines, concurrency]   # 1-3 relevant subtopics
question_kind: theory                  # coding | theory | system-design | android
difficulty: medium                     # easy | medium | hard

# Language
original_language: en                  # en | ru
language_tags: [en, ru]               # Which languages present

# Workflow
status: draft                          # ALWAYS draft for AI

# Links (WITHOUT brackets in YAML!)
moc: moc-kotlin                        # Single MOC, NO brackets
related: [c-coroutines, c-scope, q-coroutine-context--kotlin--hard]  # Array, NO double brackets

# Timestamps
created: 2025-10-18                    # YYYY-MM-DD
updated: 2025-10-18                    # YYYY-MM-DD

# Tags (English only!)
tags: [kotlin, coroutines, concurrency, difficulty/medium]
---
```

### YAML Format Rules

**CORRECT**:
```yaml
moc: moc-algorithms                    # NO brackets
related: [c-hash-map, c-array]         # Array WITHOUT double brackets
tags: [leetcode, arrays, difficulty/easy]  # English only
```

**WRONG**:
```yaml
moc: [[moc-algorithms]]                # FORBIDDEN - has brackets
related: [[c-hash-map]], [[c-array]]   # FORBIDDEN - double brackets
tags: [leetcode, массивы]              # FORBIDDEN - Russian in tags
```

---

## Content Structure Template

### Q&A Note Structure

```markdown
# Question (EN)
> Clear, concise English version of the question

# Вопрос (RU)
> Точная русская формулировка вопроса

---

## Answer (EN)

**Approach**: Explanation of the solution approach
**Complexity**: Time O(n), Space O(1)
**Code**:

\```kotlin
fun solution(input: List<Int>): Int {
    // Implementation
    return result
}
\```

**Explanation**: Step-by-step explanation of the solution

## Ответ (RU)

**Подход**: Объяснение подхода к решению
**Сложность**: Время O(n), Память O(1)
**Код**: (same code, can add Russian comments)

**Объяснение**: Пошаговое объяснение решения

---

## Follow-ups

- What if input is empty?
- How to handle negative numbers?
- Can we optimize further?

## References

- [[c-coroutines]]
- [[c-concurrency]]
- https://kotlinlang.org/docs/coroutines-basics.html

## Related Questions

### Prerequisites (Easier)
- [[q-what-is-coroutine--kotlin--easy]]

### Related (Same Level)
- [[q-coroutine-context--kotlin--medium]]
- [[q-coroutine-scope--kotlin--medium]]

### Advanced (Harder)
- [[q-structured-concurrency--kotlin--hard]]
```

---

## Tag Conventions

### Required Tags

```yaml
# REQUIRED for all Q&A notes
difficulty/easy | difficulty/medium | difficulty/hard

# REQUIRED for Android notes (mirror subtopics)
android/<subtopic>  # For each subtopic in YAML
```

### Recommended Namespace Tags

```yaml
# Language tags (for code examples)
lang/kotlin, lang/java, lang/python, lang/sql

# Platform tags
platform/android, platform/backend, platform/web

# Source tags
leetcode, neetcode, hackerrank, system-design-primer

# Technique tags (algorithms)
two-pointers, dp, binary-search, sliding-window, greedy

# Concept tags (general)
concurrency, multithreading, recursion, immutability
```

### Tag Rules

- REQUIRED: ALL tags in English (NO Cyrillic)
- REQUIRED: Include `difficulty/<level>`
- REQUIRED: For Android, mirror subtopics as `android/<subtopic>`
- RECOMMENDED: Use namespaced tags (difficulty/, android/, lang/, etc.)
- FORBIDDEN: Russian in tags

---

## Quality Checklist

Before finalizing any note, verify:

### YAML Validation
- [ ] `id` present (YYYYMMDD-HHmmss format)
- [ ] `title` includes both EN and RU
- [ ] `topic` is exactly ONE value from TAXONOMY.md
- [ ] `subtopics` has 1-3 values
- [ ] `difficulty` is easy | medium | hard
- [ ] `question_kind` is coding | theory | system-design | android
- [ ] `status` is draft (NEVER reviewed/ready for AI)
- [ ] `moc` field present (single value, NO brackets)
- [ ] `related` field has 2+ items (array, NO double brackets)
- [ ] `tags` are English-only
- [ ] `tags` include `difficulty/<level>`
- [ ] For Android: `tags` include `android/<subtopic>` for each subtopic

### Content Validation
- [ ] `# Question (EN)` section present
- [ ] `# Вопрос (RU)` section present
- [ ] `## Answer (EN)` section present
- [ ] `## Ответ (RU)` section present
- [ ] Both languages have equivalent content
- [ ] Code examples valid (if applicable)
- [ ] Links use correct format `[[note-name]]`

### File Organization
- [ ] File in correct folder (matches `topic` field)
- [ ] Filename follows pattern: `q-[slug]--[topic]--[difficulty].md`
- [ ] Filename is English-only, lowercase, hyphenated
- [ ] No emoji anywhere in file

---

## Common Mistakes to Avoid

### MISTAKE 1: Multiple Topics
```yaml
# WRONG
topic: [algorithms, data-structures]

# CORRECT
topic: algorithms
```

### MISTAKE 2: Brackets in YAML Links
```yaml
# WRONG
moc: [[moc-algorithms]]
related: [[c-hash-map]], [[c-array]]

# CORRECT
moc: moc-algorithms
related: [c-hash-map, c-array]
```

### MISTAKE 3: Russian in Tags
```yaml
# WRONG
tags: [kotlin, корутины, сложность/средняя]

# CORRECT
tags: [kotlin, coroutines, difficulty/medium]
aliases: [Coroutines, Корутины]  # Russian goes here
```

### MISTAKE 4: Android Without Mirrored Tags
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

### MISTAKE 5: Setting Status to reviewed/ready
```yaml
# WRONG - AI must never set these
status: reviewed
status: ready

# CORRECT - Always use draft
status: draft
```

### MISTAKE 6: Splitting Languages
```
# WRONG - Don't create separate files
q-coroutine-basics-en.md
q-coroutine-basics-ru.md

# CORRECT - One file with both languages
q-coroutine-basics--kotlin--easy.md
  # Question (EN)
  # Вопрос (RU)
```

### MISTAKE 7: File in Wrong Folder
```
# WRONG - kotlin note in android folder
40-Android/q-coroutine-basics--kotlin--easy.md

# CORRECT - kotlin note in kotlin folder
70-Kotlin/q-coroutine-basics--kotlin--easy.md
```

---

## Quick Reference Commands

### Check Vault Health
Use the link health dashboard in Obsidian:
```
Open: 00-Administration/Linking-System/LINK-HEALTH-DASHBOARD.md
```

This dashboard shows:
- Overall health score
- Link integrity
- Orphan files
- Broken links
- Missing cross-references

### Validate Multiple Files
When creating multiple files, validate each one:
```
For each file:
  1. Check YAML completeness
  2. Verify topic from TAXONOMY.md
  3. Check folder placement
  4. Verify tags (English-only, difficulty/*)
  5. Check links (MOC, related)
```

### Find Examples
Look for similar notes as examples:
```
Similar algorithm note: 20-Algorithms/q-two-sum--algorithms--easy.md
Similar Android note: 40-Android/q-compose-state--android--medium.md
Similar Kotlin note: 70-Kotlin/q-coroutine-basics--kotlin--easy.md
```

---

## Folder → Topic → MOC Mapping

| Folder | Topic | MOC | Example |
|--------|-------|-----|---------|
| 20-Algorithms/ | algorithms | moc-algorithms | q-binary-search--algorithms--easy.md |
| 30-System-Design/ | system-design | moc-system-design | q-design-cache--system-design--hard.md |
| 40-Android/ | android | moc-android | q-compose-state--android--medium.md |
| 50-Backend/ | databases | moc-backend | q-sql-joins--databases--medium.md |
| 60-CompSci/ | operating-systems | moc-cs | q-process-vs-thread--operating-systems--medium.md |
| 70-Kotlin/ | kotlin | moc-kotlin | q-coroutine-basics--kotlin--easy.md |
| 80-Tools/ | tools | moc-tools | q-git-rebase--tools--medium.md |

**Rule**: Folder MUST match topic, MOC MUST be appropriate for topic.

---

## When Uncertain

1. **Check TAXONOMY.md** for valid topic/subtopic/difficulty values
2. **Check templates** in `_templates/` for correct structure
3. **Set status: draft** and let human decide
4. **Ask the user** if requirements are ambiguous
5. **Review AGENTS.md** for detailed instructions
6. **Check AGENT-CHECKLIST.md** for quick validation

**Never Guess**: Always validate against vault documentation.

---

## Error Prevention

### Before Creating a Note
1. Validate topic against TAXONOMY.md
2. Determine correct folder
3. Check for similar existing notes
4. Use appropriate template

### Before Saving
1. Run through quality checklist
2. Verify YAML completeness
3. Check both languages present
4. Validate all links
5. Confirm `status: draft`

### After Creating
1. Verify file created in correct location
2. Check filename follows pattern
3. Confirm YAML valid
4. Test links if possible

---

## Resources

### Vault Documentation
- **Agent instructions**: `AGENTS.md`
- **Quick checklist**: `00-Administration/AGENT-CHECKLIST.md`
- **Controlled vocabularies**: `00-Administration/Vault-Rules/TAXONOMY.md`
- **File naming rules**: `00-Administration/Vault-Rules/FILE-NAMING-RULES.md`
- **Linking strategy**: `00-Administration/Linking-System/LINKING-STRATEGY.md`
- **Link health**: `00-Administration/Linking-System/LINK-HEALTH-DASHBOARD.md`

### Templates
- **Q&A template**: `_templates/_tpl-qna.md`
- **Concept template**: `_templates/_tpl-concept.md`
- **MOC template**: `_templates/_tpl-moc.md`

### Claude Code Configuration
- **Setup guide**: `.claude/README.md`
- **Auto-loaded context**: `.claude/custom_instructions.md`
- **Slash commands**: `.claude/commands/` (6 commands available)
- **Permissions**: `.claude/settings.local.json`

### Other AI Tools
- **Cursor AI rules**: `.cursor/rules/` (modern MDC format)
- **Gemini CLI guide**: `GEMINI.md`
- **AI tools comparison**: `00-Administration/AI-TOOLS.md`

---

## Example Sessions

### Session 1: Create Single Note
```
User: Create a note about Kotlin coroutine scope

Agent: I'll create a Q&A note about coroutine scope.

1. Classification: topic=kotlin, difficulty=medium, question_kind=theory
2. Filename: q-coroutine-scope--kotlin--medium.md
3. Folder: 70-Kotlin/
4. Using template: _templates/_tpl-qna.md

[Creates file with complete YAML and bilingual content]

Done! Created q-coroutine-scope--kotlin--medium.md in 70-Kotlin/
- Status: draft
- MOC: moc-kotlin
- Related: c-coroutines, c-structured-concurrency
- Both EN and RU sections complete
```

### Session 2: Translate Existing Note
```
User: Add Russian translation to q-coroutine-basics--kotlin--easy.md

Agent: I'll add Russian translation to the note.

[Reads file, identifies missing RU sections]

Adding translations:
- # Вопрос (RU) - translated from English question
- ## Ответ (RU) - translated from English answer
- Preserved all code examples and links
- Updated language_tags to [en, ru]
- Kept status: draft

Translation complete! Ready for review.
```

### Session 3: Validate Note
```
User: Validate 40-Android/q-compose-state--android--medium.md

Agent: Running validation...

REQUIRED: PASSED (12 checks)
- YAML complete
- Both EN/RU present
- Folder matches topic
- MOC and related links present

FORBIDDEN: PASSED (no critical issues)

WARNING: 1 issue
- Missing "Follow-ups" section
  Suggestion: Add common variations and edge cases

NOTE: 1 suggestion
- Could add more related links (currently 2, recommend 3-5)

Summary: Ready for review with minor improvements recommended.
```

---

## Summary

Claude Code is configured to work seamlessly with this vault:

**Auto-loaded**: Custom instructions from `.claude/custom_instructions.md`
**Slash commands**: 6 specialized commands for common tasks
**Validation**: Built-in quality checks and checklists
**Documentation**: Complete reference in `.claude/README.md`

**Key Reminders**:
- Always use `status: draft`
- Both languages in same file
- English-only tags
- Link to MOC and concepts
- No emoji in notes
- Validate against TAXONOMY.md

**For Help**: Check `.claude/README.md` or `AGENTS.md`

---

**Version**: 1.0
**Last Updated**: 2025-10-18
**Status**: Production Ready
**Auto-loads from**: `.claude/custom_instructions.md`
