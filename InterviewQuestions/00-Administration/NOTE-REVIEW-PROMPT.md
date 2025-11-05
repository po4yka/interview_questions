# Note Review Prompt (Automation + Senior Review)

Use this playbook when an automation agent must iterate through notes, apply fixes, and hand them back for a senior-level verification.

---

## Operating Mode

1. **Scope definition**: specify the working set up front.
   - Folder: `InterviewQuestions/<FOLDER>/` (e.g., `20-Algorithms/`, `40-Android/`)
   - Files: explicit list or `ALL`
2. **Single-note flow**: for each file run validation → edit → re-run validation → present results → wait for reviewer confirmation before touching the next note.
3. **Progress tracking**: maintain a running checklist using `☐` (pending) and `☑` (completed).

---

## Automation Requirements

### Validation Loop

Run the validator before and after every edit, capturing the output summary.

```bash
uv sync --project utils  # first run only
uv run --project utils python -m utils.validate_note <relative-path>
```

### Folder Awareness

If the note appears to be in the wrong folder relative to its topic, flag it in the report but do **not** move the file automatically.

### Validator Output Guide

The validator produces structured output. Learn to interpret results and fix common issues.

#### Successful Validation

```
✓ YAML frontmatter valid
✓ All required fields present
✓ Topic value valid: 'android'
✓ Subtopics valid: ['ui-compose', 'lifecycle']
✓ ID format valid: 'android-134'
✓ Questions use blockquote syntax (>) in both RU and EN
✓ Code formatting: all types wrapped in backticks
✓ No broken wikilinks found
✓ File in correct folder: 40-Android/ matches topic 'android'

VALIDATION PASSED (0 errors, 0 warnings)
```

#### Common Validation Errors

**Error 1: Missing Required Field**
```
✗ ERROR: Missing required field 'moc' in YAML frontmatter
```
**Fix**: Add `moc: moc-<topic>` to frontmatter (e.g., `moc: moc-algorithms`)

**Error 2: Invalid Topic Value**
```
✗ ERROR: Invalid topic 'programming'. Must be one of: algorithms, android, kotlin, ...
```
**Fix**: Check TAXONOMY.md for valid topics. Replace with correct value.

**Error 3: Question Missing Blockquote**
```
✗ ERROR: Question not formatted with blockquote syntax
  Line 15: # Вопрос (RU)
  Line 16: Что такое ViewModel?
  Expected: > Что такое ViewModel?
```
**Fix**: Add `>` before question text:
```markdown
# Вопрос (RU)
> Что такое ViewModel?
```

**Error 4: Code Formatting - Unescaped Generics**
```
✗ ERROR: Generic type not wrapped in backticks
  Line 45: ArrayList<String> will be interpreted as HTML
```
**Fix**: Wrap in backticks: `` `ArrayList<String>` ``

**Error 5: Broken Wikilink**
```
✗ ERROR: Broken wikilink [[c-hash-map]] - target file not found
```
**Fix**: Either create `c-hash-map.md` or remove the link

**Error 6: File in Wrong Folder**
```
⚠ WARNING: File location mismatch
  Current: 40-Android/q-coroutines-basics--kotlin--easy.md
  Expected: 70-Kotlin/ (topic is 'kotlin')
```
**Fix**: Flag for human review; do NOT move automatically

**Error 7: Invalid Subtopic**
```
✗ ERROR: Invalid Android subtopic 'compose'
  Valid options: ui-compose, ui-state, ui-navigation, ...
```
**Fix**: Check TAXONOMY.md Android subtopics list. Use `ui-compose` not `compose`.

**Error 8: Missing Difficulty Tag**
```
✗ ERROR: Tags missing required 'difficulty/<level>' tag
  Current tags: [android, viewmodel, lifecycle]
```
**Fix**: Add difficulty tag: `tags: [android, viewmodel, lifecycle, difficulty/medium]`

**Error 9: Brackets in YAML Links**
```
✗ ERROR: YAML field 'moc' contains brackets: [[moc-algorithms]]
```
**Fix**: Remove brackets: `moc: moc-algorithms`

#### Validation Warnings

Warnings indicate issues that should be fixed but won't block progress:

```
⚠ WARNING: Note is 650 lines (target: 200-400)
⚠ WARNING: Code snippet on line 125 is 28 lines (target: 5-15)
⚠ WARNING: Only 1 related link found (recommended: 2-5)
⚠ WARNING: 'References' section empty; consider removing or populating
```

### Error Recovery Workflow

When validation fails or issues arise, follow these decision trees:

#### Scenario 1: Validation Fails After Edits

**Decision Tree**:
```
Validation failed?
├─ Yes → Review validator output
│   ├─ Missing required field?
│   │   └─ Add field from TAXONOMY.md → Re-run validation
│   ├─ Invalid value?
│   │   └─ Check TAXONOMY.md → Use valid value → Re-run validation
│   ├─ Syntax error?
│   │   └─ Fix YAML syntax (no tabs, proper spacing) → Re-run validation
│   ├─ Formatting error?
│   │   └─ Apply formatting rules (blockquotes, backticks) → Re-run validation
│   └─ Still failing after 3 attempts?
│       └─ Flag for human review with error details
└─ No → Continue to next step
```

**Example Recovery**:
```markdown
1. Run validation: `uv run --project utils python -m utils.validate_note 40-Android/q-compose-state--android--medium.md`
2. Error: Missing required field 'moc'
3. Fix: Add `moc: moc-android` to frontmatter
4. Re-run validation: PASSED
5. Continue with edits
```

#### Scenario 2: Note in Wrong Folder

**Decision Tree**:
```
Validator warns: File in wrong folder?
├─ Confirm mismatch:
│   ├─ Current: 40-Android/q-coroutines--kotlin--easy.md
│   └─ Topic: kotlin → Should be in 70-Kotlin/
├─ Document in report:
│   ├─ "NOTE: File location mismatch detected"
│   ├─ "Current location: 40-Android/"
│   ├─ "Topic in YAML: kotlin"
│   ├─ "Recommended location: 70-Kotlin/"
│   └─ "Action: Flagged for human review (DO NOT MOVE)"
└─ Continue validation and editing
    └─ Do NOT move file automatically
```

**Why not move automatically?**
- File may have legitimate reason to be where it is
- Wikilinks from other notes would break
- Human should decide and update links accordingly

#### Scenario 3: Broken Wikilinks

**Decision Tree**:
```
Validator reports broken links?
├─ Identify broken link: [[c-hash-map]]
├─ Check if file should exist:
│   ├─ Is it a core concept? (c-hash-map, c-binary-tree, etc.)
│   │   ├─ Yes → Add to "needs creation" list in report
│   │   └─ No → Consider removing link
│   ├─ Is filename misspelled?
│   │   └─ Search vault: find c-hashmap.md (different spelling)
│   │       └─ Fix: [[c-hashmap]] or [[c-hash-map|hash map]]
│   └─ Is link outdated?
│       └─ File was moved/renamed → Update to correct name
└─ Document decision in report
```

**Recovery Actions**:
1. **Minor typo** → Fix immediately and re-validate
2. **Missing concept note** → Document in report: "Suggests creating [[c-hash-map]]"
3. **File renamed** → Update link to new name
4. **Link unnecessary** → Remove and re-validate

#### Scenario 4: Content Too Long/Short

**Decision Tree**:
```
Note exceeds target length (200-400 lines)?
├─ Current length: 650 lines
├─ Analyze content:
│   ├─ Excessive explanation?
│   │   └─ Trim to essential points (aim for 40-70% reduction)
│   ├─ Too many code examples? (>5)
│   │   └─ Keep 3-5 most illustrative examples
│   ├─ Too many follow-ups? (>8)
│   │   └─ Keep 3-5 most relevant follow-ups
│   └─ Redundant sections?
│       └─ Remove or consolidate
├─ Target: 200-400 lines total
└─ If still too long after trimming:
    └─ Flag for human review: "Content very dense, may need split"

Note too short (<150 lines)?
├─ Check if answer is complete:
│   ├─ Missing complexity analysis? → Add
│   ├─ Missing trade-offs? → Add
│   ├─ Missing code examples? → Add 1-2 examples
│   └─ Missing follow-ups? → Add 3-5 questions
└─ If genuinely simple topic:
    └─ Accept shorter length if complete
```

#### Scenario 5: Translation Mismatch

**Decision Tree**:
```
RU and EN sections don't match semantically?
├─ Identify which is more complete:
│   ├─ RU more detailed? → Expand EN to match
│   └─ EN more detailed? → Expand RU to match
├─ Check specific mismatches:
│   ├─ Code examples different?
│   │   └─ Use identical code in both sections
│   ├─ Different number of points?
│   │   └─ Ensure same structure and point count
│   └─ One has complexity analysis, other doesn't?
│       └─ Add to both sections
└─ After fixing: Flag for human review of translation quality
```

#### Scenario 6: Multiple Errors (>5)

**Decision Tree**:
```
Validator reports >5 errors?
├─ Triage by severity:
│   ├─ Critical (blocks validation):
│   │   ├─ Missing required fields
│   │   ├─ Invalid topic/subtopic values
│   │   └─ YAML syntax errors
│   │       → Fix these FIRST, then re-run validation
│   ├─ High (formatting):
│   │   ├─ Missing blockquotes
│   │   ├─ Unescaped generics
│   │   └─ Broken wikilinks
│   │       → Fix after critical issues
│   └─ Medium (quality):
│       ├─ Length issues
│       ├─ Missing tags
│       └─ Few related links
│           → Fix after high-priority issues
├─ Fix in priority order
├─ Re-run validation after each group
└─ If >3 validation cycles needed:
    └─ Flag for human review: "Note needs significant rework"
```

#### Recovery Success Checklist

After error recovery, verify:
- [ ] Validation passes without critical errors
- [ ] All required YAML fields present and valid
- [ ] Questions use blockquote syntax (both RU and EN)
- [ ] Code formatting correct (backticks for types/generics)
- [ ] No broken wikilinks (or documented for creation)
- [ ] File location matches topic (or flagged if mismatch)
- [ ] Length within acceptable range (200-400 lines ideal)
- [ ] RU and EN sections semantically equivalent
- [ ] Changes documented in progress tracker

---

## YAML Standardization

Ensure the frontmatter matches the controlled schema. The `id` must follow the `<subject>-<serial>` convention (e.g., `algo-001`, `android-134`) and stay unique within the vault. Use the stable subject slug reflecting the note's domain and a zero-padded serial number:

```yaml
id: algo-001
title: Example Title / Пример названия
aliases:
  - Example Title
  - Пример названия
topic: <matches folder mapping below>
subtopics: [controlled values]       # see TAXONOMY.md
question_kind: theory | coding | android | system-design   # pick the accurate value
difficulty: easy | medium | hard
original_language: en | ru
language_tags: [en, ru]              # match actual languages present
sources:
  - url: https://example.com
    note: Official statement
status: draft | reviewed | ready
moc: [[moc-topic]]
related:
  - [[c-concept]]
created: 2025-01-20
updated: 2025-01-25
tags: [leetcode, arrays, hash-map, difficulty/easy]
```

Topic ↔ folder mapping (actual folders):

- `20-Algorithms/` → `topic: algorithms` or `data-structures`
- `30-System-Design/` → `topic: system-design` or `distributed-systems`
- `40-Android/` → `topic: android`
- `50-Backend/` → `topic: databases` or `networking`
- `60-CompSci/` → `topic: cs`, `operating-systems`, `concurrency`, etc.
- `70-Kotlin/` → `topic: kotlin` or `programming-languages`
- `80-Tools/` → `topic: tools` or `debugging`
- `90-MOCs/` → Maps of Content; topic varies per note

Remove obsolete keys (`date created`, `date modified`, legacy metadata).

---

## Bilingual Structure (RU-first)

Every note must follow the canonical template with semantically equivalent RU/EN content.

```
# Вопрос (RU)
> Русская формулировка задачи

# Question (EN)
> English version of the prompt

---

### Question Formatting Rule

**CRITICAL**: All questions (both RU and EN) MUST be formatted using the blockquote syntax (`>`) to clearly distinguish the question from explanatory content.

**REQUIRED FORMAT**:
```markdown
# Вопрос (RU)
> Вопрос на русском языке

# Question (EN)
> Question in English

---
```

**CORRECT**:
```markdown
# Вопрос (RU)
> Чем жизненный цикл Fragment отличается от жизненного цикла Activity?

# Question (EN)
> How does the Fragment lifecycle differ from the Activity lifecycle?
```

**FORBIDDEN**:
```markdown
# Вопрос (RU)
Чем жизненный цикл Fragment отличается от жизненного цикла Activity?

# Question (EN)
How does the Fragment lifecycle differ from the Activity lifecycle?
```

---

## Ответ (RU)
Подробное объяснение, при необходимости код.

## Answer (EN)
Mirror content in English; reuse the same structure.

---

## Follow-ups
- …

## References
- [[c-example]]

## Related Questions
- [[q-example--algorithms--medium]]
```

---

## Content Quality (Senior Developer Standard)

- Validate every statement for **technical and factual accuracy** suitable for a Senior Developer interview.
- Trim verbosity by roughly **40–70 %**, targeting 200–400 total lines.
- Lead with conceptual clarity; code is illustrative only.
- Limit code to **3–5 snippets**, each **5–15 lines**, and use `✅`/`❌` markers inside comments to highlight best/worst practices.
- Never include dependency version numbers.

### Mandatory Sections

- `## Follow-ups` — add meaningful follow-on questions.
- `## References` — include concept notes or reliable sources; omit the section only if truly empty.
- `## Related Questions` — include at least one forward/backward link; use descriptive placeholders if no note exists yet.

---

## Code Formatting Rules

**CRITICAL**: All code references in regular text (outside code blocks) must be properly formatted to prevent HTML/XML interpretation and ensure correct rendering.

### Required Formatting

1. **Type names and class names**: Wrap all type names, class names, interface names in backticks.
   - ✅ `String`, `Int`, `ArrayList`, `Parcelable`, `Bundle`
   - ❌ String, Int, ArrayList, Parcelable

2. **Generic types**: Generic types with angle brackets MUST be wrapped in backticks.
   - ✅ `ArrayList<String>`, `SparseArray<Parcelable>`, `Map<String, Int>`
   - ❌ ArrayList<String>, SparseArray<Parcelable> (will be interpreted as HTML tags)

3. **Method names and API references**: Wrap method names, API references, exception names in backticks.
   - ✅ `putString()`, `getInt()`, `put*/get*`, `TransactionTooLargeException`
   - ✅ `Binder`, `IPC`, `ViewModel`
   - ❌ putString(), getInt() (may render incorrectly)

4. **Code blocks**: Code inside fenced code blocks (```) does NOT need escaping—backticks and angle brackets are safe inside code blocks.

5. **Special characters**: Characters `<`, `>`, and backticks in regular text referring to code must be handled via backticks:
   - ✅ `` `ArrayList<String>` `` (wrapped in backticks)
   - ❌ `ArrayList<String>` without backticks (will break markdown or render as HTML)

### Examples

**In lists**:
```markdown
- Collections: `ArrayList<String>`, `ArrayList<Int>`, `ArrayList<Parcelable>`
- Objects: `Parcelable`, `Serializable`
- Special: `Bundle` (nested), `SparseArray<Parcelable>`
```

**In paragraphs**:
```markdown
Bundle is built on `Parcel`, uses type-safe `put*/get*` methods.
```

**In code blocks** (no changes needed):
```kotlin
val list: ArrayList<String> = arrayListOf()
bundle.putParcelable("profile", Profile("1", "Alice"))
```

### Validation Checklist

- [ ] All type names in lists wrapped in backticks
- [ ] Generic types with `<` and `>` wrapped in backticks
- [ ] Method names and API references formatted with backticks
- [ ] No unescaped angle brackets in regular text (outside code blocks)

---

## Manual Review Focus

After automation, the human reviewer should scrutinize:

1. **Technical accuracy** — algorithms, architectural trade-offs, platform details, complexity analysis.
2. **Factual correctness** — statements align with current best practices and sources.
3. **Translation fidelity** — RU and EN sections mirror each other in meaning and structure.
4. **Depth & tone** — content is concise yet authoritative for a Senior Developer audience.

---

## Completion Checklist (per note)

- [ ] Pre-change validation executed; key findings noted.
- [ ] YAML normalized to the controlled schema.
- [ ] RU-first template satisfied; RU/EN content aligned.
- [ ] Questions formatted with blockquote syntax (`>`) for both RU and EN.
- [ ] Code formatting rules applied (backticks for types, generics, API references).
- [ ] Content trimmed, technically verified for senior-level accuracy.
- [ ] Follow-ups, References, Related Questions populated as required.
- [ ] Post-change validation passes without critical errors.
- [ ] Progress checklist updated and summary (with any risks or open questions) delivered to the reviewer.

Only proceed to the next note after the reviewer acknowledges completion.
