---\

## Vault Type

Bilingual (EN/RU) Obsidian vault for technical interview questions organized by topic.

---\

## Core Principles (Non-Negotiable)

### REQUIRED

1. **Both EN and RU in same file** - NEVER split languages
2. **Exactly ONE topic** from TAXONOMY.md
3. **English-only tags** - Russian goes in `aliases` and content only
4. **Status: draft** - ALWAYS use `draft` for AI-created/modified notes
5. **Link to MOC and concepts** - Every Q&A MUST link to ≥1 MOC and ≥2 related items
6. **No emoji** - Use text equivalents: REQUIRED, FORBIDDEN, WARNING, NOTE
7. **Folder matches topic** - File MUST be in folder matching its `topic` field
8. **YAML format**: `moc: moc-name` (no brackets), `related: [file1, file2]` (array format)

### FORBIDDEN

1. Splitting EN/RU into separate files
2. Russian in tags
3. Multiple topics in `topic` field
4. Setting `status: reviewed` or `status: ready` (only humans can)
5. Brackets in YAML `moc` field: `[[moc-name]]` is wrong, `moc-name` is correct
6. `Double` brackets in YAML `related` field: `[[item]]` is wrong, use array `[item1, item2]`
7. Emoji anywhere in vault notes
8. File in wrong folder (not matching topic)

---

## Key Resources

**Controlled Vocabularies**: `00-Administration/Vault-Rules/TAXONOMY.md` (22 valid topics)
**Full Documentation**: `CLAUDE.md` (complete agent guide)
**Detailed Rules**: `AGENTS.md` (comprehensive validation rules)
**Quick Checklist**: `00-Administration/AGENT-CHECKLIST.md`
**Templates**: `_templates/_tpl-qna.md`, `_tpl-concept.md`, `_tpl-moc.md`
**Skills**: `.claude/skills/` (6 specialized workflows)

---

## Folder Structure

```
00-Administration/  # Vault docs (TAXONOMY, rules, etc.)
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
```

---

## File Naming Patterns

### Q&A Notes
```
q-[english-slug]--[topic]--[difficulty].md
```
Example: `q-coroutine-context--kotlin--medium.md`

### Concept Notes
```
c-[concept-name].md
```
Example: `c-coroutines.md`

### MOC Notes
```
moc-[topic].md
```
Example: `moc-kotlin.md`

**Rules**: English only, lowercase, hyphens, NO Cyrillic

---

## YAML Frontmatter Example

```yaml
---
id: kotlin-001
title: Title EN / Заголовок RU
aliases: [Title EN, Заголовок RU]

topic: kotlin                          # ONE from TAXONOMY.md
subtopics: [coroutines, concurrency]   # 1-3 relevant
question_kind: theory                  # coding | theory | system-design | android
difficulty: medium                     # easy | medium | hard

original_language: en                  # en | ru
language_tags: [en, ru]               # Which languages present
status: draft                          # ALWAYS draft for AI

moc: moc-kotlin                        # NO brackets
related: [c-coroutines, q-other--kotlin--hard]  # Array, NO double brackets

created: 2025-11-09
updated: 2025-11-09

tags: [kotlin, coroutines, difficulty/medium]  # English only
---
```

**Critical**: NO brackets in `moc`, NO double brackets in `related`, English-only tags

---

## Android-Specific Rules

When `topic: android`:

1. Subtopics MUST come from Android controlled list in TAXONOMY.md
2. MUST mirror each subtopic to tags as `android/<subtopic>`

Example:
```yaml
topic: android
subtopics: [ui-compose, lifecycle]
tags: [android/ui-compose, android/lifecycle, compose, difficulty/medium]
```

---

## Available Skills

**Priority 1** (most used):
- `obsidian-qna-creator` - Create bilingual Q&A notes
- `obsidian-validator` - Validate notes against rules
- `obsidian-translator` - Add missing translations

**Priority 2**:
- `obsidian-concept-creator` - Create concept notes
- `obsidian-moc-creator` - Create MOCs
- `obsidian-link-analyzer` - Suggest cross-references

Skills automatically activate based on user requests.

---

## Quick Workflows

**Create Q&A**: Determine topic → Generate filename → Use template → Fill YAML → Write bilingual content → Validate

**Validate**: Check YAML → Verify topic → Check folder → Verify content → Check links → Report issues

**Translate**: Read file → Identify missing language → Translate (preserve code/links) → Update YAML

---

## When Uncertain

1. Check TAXONOMY.md for valid topics/subtopics
2. Check templates in `_templates/`
3. `Set` `status: draft` and let human review
4. Ask user if requirements ambiguous
5. Review AGENTS.md for detailed rules
6. Use obsidian-validator skill for validation

**Never guess** - Always validate against vault documentation.

---

**Version**: 1.0
**Last Updated**: 2025-11-09
**Token Count**: ~500 tokens
