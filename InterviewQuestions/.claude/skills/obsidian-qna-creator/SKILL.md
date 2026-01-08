---\
name: obsidian-qna-creator
description: >
  Create bilingual (EN/RU) interview Q&A notes for Obsidian vault
  following strict YAML validation rules, controlled vocabularies
  from TAXONOMY.md, and file naming conventions. Handles topic
  classification, folder placement, MOC linking, and bilingual
  content structure.
---\

# Obsidian Q&A Note Creator

## Purpose

Create interview question-and-answer notes that comply with vault rules:
- Bilingual structure (EN + RU in same file)
- Valid YAML frontmatter with controlled vocabularies
- Correct folder placement based on topic
- Proper filename pattern: `q-[slug]--[topic]--[difficulty].md`
- Links to MOC and related notes
- Both language sections complete

## When to Use

Activate this skill when user requests:
- "Create a note about [topic]"
- "Add interview question for [concept]"
- "New Q&A for [subject]"
- Any variant of creating an interview question note

## Prerequisites

Required context (read before proceeding):
- `00-Administration/Vault-Rules/TAXONOMY.md` for valid topics
- `_templates/_tpl-qna.md` for template structure
- Folder → topic mapping from TAXONOMY.md

## Process

### Step 1: Classify the Question

Determine or ask user:
- **Topic**: Exactly ONE from TAXONOMY.md (22 options: algorithms, android, kotlin, system-design, etc.)
- **Difficulty**: easy | medium | hard
- **Question kind**: coding | theory | system-design | android
- **Subtopics**: 1-3 relevant subtopics

### Step 2: Generate Metadata

**Filename Pattern**:
```
q-[english-slug]--[topic]--[difficulty].md
```

**Filename Rules**:
- English only (NO Cyrillic)
- Lowercase, hyphens as separators
- 3-8 words in slug
- Topic MUST be from TAXONOMY.md
- Difficulty: easy | medium | hard

**Examples**:
- `q-coroutine-context--kotlin--medium.md`
- `q-compose-remember--android--medium.md`
- `q-two-sum--algorithms--easy.md`

**Folder Determination** (from TAXONOMY.md):
- `kotlin` → `70-Kotlin/`
- `android` → `40-Android/`
- `algorithms` → `20-Algorithms/`
- `system-design` → `30-System-Design/`
- `databases` → `50-Backend/`
- `operating-systems` → `60-CompSci/`
- `tools` → `80-Tools/`
- (See TAXONOMY.md for complete mapping)

### Step 3: Build YAML Frontmatter

```yaml
---
id: [topic-abbrev]-XXX          # e.g., kotlin-001, android-042, algo-015
title: Title EN / Заголовок RU
aliases: [Title EN, Заголовок RU]

# Classification
topic: [topic]                   # ONE from TAXONOMY.md, NO array, NO brackets
subtopics: [sub1, sub2]         # 1-3 relevant
question_kind: [kind]           # coding | theory | system-design | android
difficulty: [level]             # easy | medium | hard

# Language
original_language: en           # en | ru (which was written first)
language_tags: [en, ru]        # Always both for complete notes

# Workflow
status: draft                   # ALWAYS draft for AI (NEVER reviewed/ready)

# Links (CRITICAL FORMAT)
moc: moc-[topic]                # Single MOC, NO brackets
related: [c-concept1, q-related-question--topic--level]  # Array format, NO double brackets

# Timestamps
created: YYYY-MM-DD
updated: YYYY-MM-DD

# Tags (English only!)
tags: [topic, subtopic1, subtopic2, difficulty/[level]]
---
```

**CRITICAL YAML Rules**:
- `topic`: Single value, NO array, NO brackets
- `moc`: NO brackets (just `moc-kotlin`, NOT `[[moc-kotlin]]`)
- `related`: `Array` WITHOUT double brackets (`[item1, item2]`, NOT `[[item1]], [[item2]]`)
- `tags`: English only, MUST include `difficulty/[level]`
- `status`: ALWAYS `draft` (AI cannot set reviewed/ready)

**Android-Specific**:
If `topic: android`:
- Subtopics MUST come from Android controlled list in TAXONOMY.md
- MUST mirror each subtopic to tags as `android/[subtopic]`

Example:
```yaml
topic: android
subtopics: [ui-compose, lifecycle]
tags: [android/ui-compose, android/lifecycle, compose, jetpack, difficulty/medium]
```

### Step 4: Build Content Structure

Use template pattern from `_templates/_tpl-qna.md`:

```markdown
# Question (EN)
> Clear, concise English version of the question

# Вопрос (RU)
> Точная русская формулировка вопроса

---

## Answer (EN)

**Approach**: Explanation of the solution approach
**Complexity**: Time/Space complexity (for algorithms)
**Code**: (if applicable)

\```kotlin
fun solution() {
    // Implementation
}
\```

**Explanation**: Step-by-step explanation of the solution

## Ответ (RU)

**Подход**: Объяснение подхода к решению
**Сложность**: Временная/пространственная сложность
**Код**: (same code, can add Russian comments if helpful)

**Объяснение**: Пошаговое объяснение решения

---

## Follow-ups

- Edge case questions
- Variations on the problem
- Optimization opportunities

## References

- [[c-related-concept]]
- [[c-another-concept]]
- https://external-link.com

## Related Questions

### Prerequisites (Easier)
- [[q-easier-question--topic--easy]]

### Related (Same Level)
- [[q-similar-question--topic--medium]]

### Advanced (Harder)
- [[q-harder-question--topic--hard]]
```

**Content Requirements**:
- Both EN and RU sections MUST have equivalent content
- Code examples should be identical (can add language-specific comments)
- Links must use Obsidian wiki-link format: `[[note-name]]`
- Preserve technical terms in original language when appropriate
- Maintain professional, educational tone

### Step 5: Validation Checklist

Before finalizing, verify:

**REQUIRED** ✅ (Must pass all):
- [ ] Both `# Question (EN)` and `# Вопрос (RU)` sections present
- [ ] Both `## Answer (EN)` and `## Ответ (RU)` sections present
- [ ] Exactly ONE topic from TAXONOMY.md
- [ ] Folder matches topic
- [ ] Filename follows pattern `q-[slug]--[topic]--[difficulty].md`
- [ ] YAML complete with all required fields
- [ ] `moc` field present with NO brackets
- [ ] `related` field has ≥2 items in array format (NO double brackets)
- [ ] `tags` are English-only
- [ ] `tags` include `difficulty/[level]`
- [ ] `status: draft`

**FORBIDDEN** ❌ (Must pass all):
- [ ] NO multiple topics (no arrays in topic field)
- [ ] NO Russian in tags (tags field)
- [ ] NO brackets in moc field (not `[[moc-name]]`)
- [ ] NO double brackets in related field (not `[[item]]`)
- [ ] NO emoji anywhere in file
- [ ] NO `status: reviewed` or `status: ready`
- [ ] NO file in wrong folder (folder must match topic)

**Android-specific** (if topic=android):
- [ ] Subtopics from Android controlled list in TAXONOMY.md
- [ ] Each subtopic mirrored to tags as `android/[subtopic]`

### Step 6: Create File and Confirm

1. **Create file** at correct path: `[folder]/q-[slug]--[topic]--[difficulty].md`
2. **Write complete content** (YAML + bilingual structure)
3. **Report to user**:
   - Filename
   - Folder location
   - Topic and difficulty
   - MOC linked
   - Number of related links
   - Validation status (all checks passed)

## Examples

### Example 1: Kotlin Coroutine Question

**User `Request`**: "Create a note about Kotlin coroutine context"

**Classification**:
- Topic: `kotlin`
- Difficulty: `medium`
- Question kind: `theory`
- Subtopics: `[coroutines, concurrency]`

**Generated**:
- Filename: `q-coroutine-context--kotlin--medium.md`
- Folder: `70-Kotlin/`
- MOC: `moc-kotlin`
- Related: `[c-coroutines, c-coroutine-scope, q-coroutine-scope--kotlin--medium]`

**YAML**:
```yaml
---
id: kotlin-015
title: Coroutine Context / Контекст корутин
aliases: [Coroutine Context, Контекст корутин, CoroutineContext]

topic: kotlin
subtopics: [coroutines, concurrency]
question_kind: theory
difficulty: medium

original_language: en
language_tags: [en, ru]
status: draft

moc: moc-kotlin
related: [c-coroutines, c-coroutine-scope, q-coroutine-scope--kotlin--medium]

created: 2025-11-09
updated: 2025-11-09

tags: [kotlin, coroutines, concurrency, coroutine-context, difficulty/medium]
---
```

### Example 2: Android Compose Question

**User `Request`**: "Create a note about remember in Compose"

**Classification**:
- Topic: `android`
- Difficulty: `medium`
- Question kind: `android`
- Subtopics: `[ui-compose, ui-state]`

**Generated**:
- Filename: `q-compose-remember--android--medium.md`
- Folder: `40-Android/`
- MOC: `moc-android`
- Related: `[c-compose-state, c-recomposition, q-state-hoisting--android--medium]`

**YAML**:
```yaml
---
id: android-127
title: Remember in Compose / Remember в Compose
aliases: [Compose Remember, Remember в Compose, State Management, remember()]

topic: android
subtopics: [ui-compose, ui-state]
question_kind: android
difficulty: medium

original_language: en
language_tags: [en, ru]
status: draft

moc: moc-android
related: [c-compose-state, c-recomposition, q-state-hoisting--android--medium]

created: 2025-11-09
updated: 2025-11-09

tags: [android/ui-compose, android/ui-state, compose, state-management, jetpack, difficulty/medium]
---
```

**Note**: Android-specific tags `android/ui-compose` and `android/ui-state` mirror the subtopics.

### Example 3: Algorithm Question

**User `Request`**: "Create note for Two Sum problem"

**Classification**:
- Topic: `algorithms`
- Difficulty: `easy`
- Question kind: `coding`
- Subtopics: `[arrays, hash-map]`

**Generated**:
- Filename: `q-two-sum--algorithms--easy.md`
- Folder: `20-Algorithms/`
- MOC: `moc-algorithms`
- Related: `[c-hash-map, c-array, q-three-sum--algorithms--medium]`

**YAML**:
```yaml
---
id: algo-001
title: Two Sum / Два числа с заданной суммой
aliases: [Two Sum, Два числа, LeetCode 1]

topic: algorithms
subtopics: [arrays, hash-map]
question_kind: coding
difficulty: easy

original_language: en
language_tags: [en, ru]
status: draft

moc: moc-algorithms
related: [c-hash-map, c-array, q-three-sum--algorithms--medium]

created: 2025-11-09
updated: 2025-11-09

tags: [algorithms, arrays, hash-map, leetcode, difficulty/easy]
---
```

## Error Handling

### Invalid Topic

**Problem**: User requests topic not in TAXONOMY.md

**Solution**:
1. Report the error
2. `List` similar valid topics from TAXONOMY.md
3. Ask user to confirm or choose different topic
4. Do NOT proceed until valid topic confirmed

### Ambiguous Classification

**Problem**: Difficulty or question_kind unclear

**Solution**:
1. Ask user for clarification
2. Provide examples of each level/kind
3. For difficulty: describe easy/medium/hard criteria
4. Wait for confirmation before proceeding

### Missing Related Notes

**Problem**: Cannot find good related links in vault

**Solution**:
1. Create note with minimal related links (just related concepts if available)
2. Link to MOC (always required)
3. Note in file that more links should be added
4. Suggest user run `obsidian-link-analyzer` skill later to enhance links

### Duplicate Filename

**Problem**: Generated filename already exists

**Solution**:
1. Check if existing note covers the same content
2. If yes: suggest updating existing note instead
3. If no: adjust slug to differentiate (add variant, more specific terms)
4. Confirm with user before proceeding

## Validation

After creation, automatically perform these checks:

1. **File exists** in correct folder
2. **Filename matches** pattern
3. **YAML parses** correctly (no syntax errors)
4. **All required fields** present in YAML
5. **Topic valid** (exists in TAXONOMY.md)
6. **Both EN/RU sections** present
7. **No FORBIDDEN violations** (Russian in tags, brackets in moc, etc.)

If validation fails:
- Report specific issues
- Offer to fix automatically if possible
- If cannot fix: explain what needs manual correction

## Integration with Other Skills

**Recommended workflow**:
1. Use `obsidian-qna-creator` to create note
2. Use `obsidian-validator` for comprehensive validation
3. If needed, use `obsidian-translator` to enhance translations
4. Later, use `obsidian-link-analyzer` to add more cross-references

**Related Skills**:
- `obsidian-validator`: Full validation after creation
- `obsidian-translator`: Add/improve translations
- `obsidian-link-analyzer`: Enhance related links

## Notes

**Token Efficiency**: This skill loads ~3,000 tokens only when creating Q&A notes. At session start, only the 100-token description is loaded.

**Reusability**: This skill can be adapted for any bilingual Obsidian vault with controlled vocabularies and strict formatting requirements.

**Updates**: When TAXONOMY.md is updated with new topics/subtopics, this skill automatically references the latest version.

**Quality**: Following this skill's process ensures 100% compliance with vault rules and eliminates common validation errors.

---

**Version**: 1.0
**Last Updated**: 2025-11-09
**Status**: Production Ready
