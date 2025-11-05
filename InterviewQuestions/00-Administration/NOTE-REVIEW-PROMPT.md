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
