---\
name: obsidian-translator
description: >
  Add missing language translations to existing bilingual notes. Identifies
  which language sections (EN or RU) are missing, translates while preserving
  code blocks and links, updates language_tags YAML field, and maintains
  status as draft. Ensures both languages have equivalent content.
---\

# Obsidian Note Translator

## Purpose

Add missing language translations to existing notes:
- Identify missing language sections (EN or RU)
- Translate content while preserving code and links
- Update `language_tags` YAML field
- Maintain bilingual structure consistency
- Keep `status: draft` after translation

## When to Use

Activate this skill when user requests:
- "Add Russian translation to [note]"
- "Translate [note] to English"
- "Complete bilingual content for [note]"
- "Add missing language to [note]"
- When note has only one language section

## Prerequisites

Required context:
- Target note file path
- Understanding of vault bilingual requirements
- Access to translation capabilities

## Process

### Step 1: Read and Analyze Note

1. **Read file** at specified path
2. **Parse YAML** frontmatter
3. **Identify existing language sections**:
   - Check for `# Question (EN)` or `# Вопрос (RU)`
   - Check for `## Answer (EN)` or `## Ответ (RU)`
4. **Determine which language is missing**

**Language Detection**:
```
If has "# Question (EN)" but not "# Вопрос (RU)":
  → Need to add Russian

If has "# Вопрос (RU)" but not "# Question (EN)":
  → Need to add English

If has both:
  → Check if content is substantial (not just placeholders)
```

### Step 2: Translate Missing Sections

#### Question Translation

**English → Russian**:
- Translate question clearly and accurately
- Maintain technical terms in original if widely understood
- Use blockquote format: `> Текст вопроса`

**Russian → English**:
- Translate question clearly and accurately
- Maintain technical terms consistently
- Use blockquote format: `> Question text`

#### Answer Translation

**Translate all answer components**:
- **Approach/Подход**: Main explanation
- **Complexity/Сложность**: Time/Space complexity analysis
- **Code/Код**: Code blocks (usually unchanged, may add language-specific comments)
- **Explanation/Объяснение**: Detailed explanation

**Preservation Requirements**:
- **Code blocks**: Keep code identical (can add translated comments)
- **Links**: Keep wiki-links unchanged `[[note-name]]`
- **Technical terms**: Maintain consistency
- **URLs**: Keep external links unchanged
- **Formatting**: Preserve markdown structure (bold, lists, etc.)

#### Section Translation

**Translate supporting sections**:
- **Follow-ups**: Translate question variations
- **References**: Link text can be translated, URLs unchanged
- **Related Questions**: Translate descriptive text, keep links

### Step 3: Update YAML Frontmatter

After adding translation:

```yaml
# Update language_tags to include both languages
language_tags: [en, ru]

# Update timestamp
updated: YYYY-MM-DD  # Today's date

# IMPORTANT: Keep status as draft
status: draft
```

**Do NOT change**:
- `status` should remain `draft` (if it was draft)
- `created` date
- `id`, `title`, `topic`, or other metadata
- `original_language` (indicates which was written first)

### Step 4: Quality Check

Before finalizing:

**Content Equivalence**:
- [ ] Both languages convey same information
- [ ] Technical accuracy maintained
- [ ] No information lost or added
- [ ] Tone and formality consistent

**Preservation**:
- [ ] Code blocks identical (except optional comments)
- [ ] All links intact and functional
- [ ] Technical terms used consistently
- [ ] Markdown formatting preserved

**Structure**:
- [ ] Both languages have same sections
- [ ] Headers follow pattern (EN: #/##, RU: #/##)
- [ ] Content organization matches

**YAML**:
- [ ] `language_tags: [en, ru]`
- [ ] `updated` set to today
- [ ] `status: draft` maintained

### Step 5: Report Completion

Inform user of changes:
```
Translation complete for [filename]

Added sections:
- # Вопрос (RU)
- ## Ответ (RU)
- Follow-ups (RU)
- Related Questions (RU)

Updated:
- language_tags: [en, ru]
- updated: 2025-11-09

Status: draft (ready for review)
```

## Examples

### Example 1: Add Russian Translation

**Before** (`70-Kotlin/q-coroutine-basics--kotlin--easy.md`):
```markdown
---
language_tags: [en]
status: draft
---

# Question (EN)
> What is a Kotlin coroutine?

## Answer (EN)
A coroutine is a concurrency design pattern...
```

**After**:
```markdown
---
language_tags: [en, ru]
updated: 2025-11-09
status: draft
---

# Question (EN)
> What is a Kotlin coroutine?

# Вопрос (RU)
> Что такое корутина в Kotlin?

---

## Answer (EN)
A coroutine is a concurrency design pattern...

## Ответ (RU)
Корутина — это паттерн проектирования для конкурентности...
```

### Example 2: Add English Translation

**Before** (`40-Android/q-viewmodel-basics--android--easy.md`):
```markdown
---
language_tags: [ru]
original_language: ru
status: draft
---

# Вопрос (RU)
> Что такое ViewModel в Android?

## Ответ (RU)
ViewModel — это компонент архитектуры...
```

**After**:
```markdown
---
language_tags: [en, ru]
original_language: ru
updated: 2025-11-09
status: draft
---

# Question (EN)
> What is ViewModel in Android?

# Вопрос (RU)
> Что такое ViewModel в Android?

---

## Answer (EN)
ViewModel is an architecture component...

## Ответ (RU)
ViewModel — это компонент архитектуры...
```

### Example 3: Code Block Preservation

**English code with English comments**:
```kotlin
fun fibonacci(n: Int): Int {
    // Base cases
    if (n <= 1) return n
    // Recursive case
    return fibonacci(n - 1) + fibonacci(n - 2)
}
```

**Russian translation can add Russian comments**:
```kotlin
fun fibonacci(n: Int): Int {
    // Базовые случаи
    if (n <= 1) return n
    // Рекурсивный случай
    return fibonacci(n - 1) + fibonacci(n - 2)
}
```

**Or keep code identical** (recommended for simple code):
```kotlin
fun fibonacci(n: Int): Int {
    // Base cases
    if (n <= 1) return n
    // Recursive case
    return fibonacci(n - 1) + fibonacci(n - 2)
}
```

## Translation Best Practices

### Technical Terms

**Keep in English when widely understood**:
- `Coroutine`, `Flow`, `ViewModel`, Compose
- Algorithm names (Binary Search, DFS, BFS)
- Data structures (`HashMap`, `ArrayList`)
- Design patterns (MVVM, MVI, Singleton)

**Translate when Russian equivalent is standard**:
- Interface → Интерфейс
- Function → Функция
- Class → Класс
- Method → Метод

### Code Comments

**Option 1 - Keep original** (recommended):
- Simpler and maintains consistency
- Code is universal across languages
- Comments are often self-explanatory

**Option 2 - Translate comments**:
- Better for complex algorithms
- Helps Russian-speaking learners
- Requires more effort

**Choose based on code complexity.**

### Cultural Context

**English style**:
- Direct and concise
- Action-oriented language
- Example: "Use this pattern when..."

**Russian style**:
- Can be more detailed
- May include explanatory context
- Example: "Этот паттерн используется в случаях, когда..."

**Match the tone of existing content in vault.**

## Error Handling

### Both Languages Already Present

**Problem**: Note already has both EN and RU sections

**Solution**:
1. Check if content is substantial (not placeholder)
2. If placeholder: replace with real translation
3. If substantial: inform user note is already bilingual
4. Offer to improve/enhance existing translation if needed

### Incomplete YAML

**Problem**: `language_tags` field missing or incorrect

**Solution**:
1. Add/update `language_tags: [en, ru]` after translation
2. Ensure YAML is valid
3. Report change to user

### Code Block Formatting Issues

**Problem**: Code blocks not properly closed or formatted

**Solution**:
1. Preserve existing formatting as much as possible
2. Ensure triple backticks are matched
3. Keep language specifier (```kotlin, ```python, etc.)

### Link Format Issues

**Problem**: Links might have spaces or special characters

**Solution**:
1. Keep all links exactly as they are
2. Do not modify wiki-link format
3. Do not translate note names in links

## Validation

After translation, verify:

1. **Both languages present**: EN and RU sections exist
2. **Content equivalence**: Information is consistent
3. **Formatting preserved**: Code blocks, links, structure intact
4. **YAML updated**: `language_tags: [en, ru]`, `updated` set
5. **Status maintained**: `status: draft` if it was draft

Optionally run `obsidian-validator` to ensure full compliance.

## Integration with Other Skills

**Common workflows**:

1. **Create English-only note** (faster initial creation)
   → Use `obsidian-qna-creator` with English only
   → Later use `obsidian-translator` to add Russian

2. **Validate after translation**:
   → Use `obsidian-translator`
   → Run `obsidian-validator` to check compliance

3. **Bulk translation**:
   → Identify notes with single language
   → Use `obsidian-translator` for each
   → Validate all with `obsidian-validator`

## Notes

**Efficiency**: Translation allows rapid initial note creation in one language, with bilingual completion as a separate step.

**Quality**: Translations should be accurate and natural, not literal word-for-word.

**Preservation**: Code and links are the most critical elements to preserve unchanged.

**Status**: Always maintain `status: draft` after AI translation. Human reviewers should verify translation quality before setting to `reviewed` or `ready`.

---

**Version**: 1.0
**Last Updated**: 2025-11-09
**Status**: Production Ready
