# Note Review Prompt (Automation + Senior Review)

Use this playbook when an automation agent must iterate through notes, apply fixes, and hand them back for a senior-level verification.

---

## Operating Mode

1. **Scope definition**: specify the working set up front.
   - Folder: `InterviewQuestions/<FOLDER_NAME>/`
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

Ensure the frontmatter matches the controlled schema:

```yaml
topic: <matches folder mapping below>
aliases: ["English Title", "Русский заголовок"]
question_kind: theory | coding | android | system-design   # pick the accurate value
original_language: en | ru
language_tags: [en, ru]              # match actual languages present
subtopics: [controlled values]       # see TAXONOMY.md
sources: [https://example.com]       # [] if none
updated: 2025-01-25
```

Topic ↔ folder mapping:

- `10-Concepts/` → `topic: cs`
- `20-Algorithms/` → `topic: algorithms`
- `30-System-Design/` → `topic: system-design`
- `40-Android/` → `topic: android`
- `50-Backend/` → `topic: backend`
- `60-CompSci/` → `topic: cs`
- `70-Kotlin/` → `topic: kotlin`
- `80-Tools/` → `topic: tools`

Remove obsolete keys (`date created`, `date modified`, legacy metadata).

---

## Bilingual Structure (RU-first)

Every note must follow the canonical template with semantically equivalent RU/EN content.

```
# Вопрос (RU)
# Question (EN)

## Ответ (RU)
## Answer (EN)

## Follow-ups
## References
## Related Questions
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
- `## Related Questions`
  ```
  ### Prerequisites
  - [[…]]
  ### Related
  - [[…]]
  ### Advanced
  - [[…]]
  ```
  Use descriptive bullets if no existing notes can be linked.

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
- [ ] Content trimmed, technically verified for senior-level accuracy.
- [ ] Follow-ups, References, Related Questions populated as required.
- [ ] Post-change validation passes without critical errors.
- [ ] Progress checklist updated and summary (with any risks or open questions) delivered to the reviewer.

Only proceed to the next note after the reviewer acknowledges completion.
