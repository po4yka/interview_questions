---
date created: Tuesday, November 25th 2025, 8:19:24 pm
date modified: Tuesday, November 25th 2025, 8:54:04 pm
---

# Validation System

**Automated validation for Interview Questions vault notes**

**Last Updated**: 2025-11-25

## Setup (One Time)

```bash
# Sync uv environment
uv sync --project utils
```

## Common Commands

```bash
# Single file
uv run --project utils python -m utils.validate_note <file.md>

# Directory
uv run --project utils python -m utils.validate_note 40-Android/

# Entire vault
uv run --project utils python -m utils.validate_note --all

# With report output
uv run --project utils python -m utils.validate_note --all --report validation-report.md

# Quiet mode (summary only)
uv run --project utils python -m utils.validate_note 70-Kotlin/ --quiet

# Help
uv run --project utils python -m utils.validate_note --help
```

## What Gets Validated

### Automated Checks (70%)

**YAML Frontmatter**
- Required fields present (id, title, topic, difficulty, etc.)
- Field formats correct (dates, arrays, strings)
- Enum values valid (difficulty: easy/medium/hard)
- Taxonomy compliance (topics match controlled vocabulary)

**Content Structure**
- Bilingual sections present (EN and RU)
- Code blocks properly formatted
- Wikilinks syntax correct
- Headers follow expected pattern

**File Organization**
- Filename matches pattern (q-*, c-*, moc-*)
- File in correct folder for topic
- No duplicate IDs

**Cross-References**
- MOC field matches topic
- Related field contains valid references
- No broken wikilinks

### Manual Review Required (30%)

- Technical accuracy of content
- Translation quality and equivalence
- Code example correctness
- Completeness of answers

## Severity Levels

| Level | Meaning | Action |
|-------|---------|--------|
| **CRITICAL** | Blocks note promotion | Must fix immediately |
| **ERROR** | Broken links, invalid refs | Fix before review |
| **WARNING** | Should fix | Fix when possible |
| **INFO** | Optional improvements | Consider fixing |

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Passed (or warnings only) |
| `1` | Critical or error issues found |

## Common Issues and Fixes

### Missing Required Field

```
CRITICAL: Missing required field: topic
```

**Fix**: Add the field to YAML frontmatter.

### Invalid Enum Value

```
ERROR: Invalid difficulty: 'hard'. Expected: easy, medium, hard
```

**Fix**: Use exact spelling from TAXONOMY.md.

### Wrong Folder

```
WARNING: File topic 'kotlin' but in folder '40-Android'
```

**Fix**: Move file to correct folder (70-Kotlin/).

### Broken Wikilink

```
ERROR: Broken link: [[q-nonexistent-note]]
```

**Fix**: Remove or correct the wikilink.

## Integration with AI Translation

Combine validation with AI translation:

```bash
# Validate and translate
uv run --project utils python -m utils.validate_note <path> --ai-translate --fix
```

See **[[LM-STUDIO-QUICKSTART]]** for AI setup.

## See Also

- **[[TAXONOMY]]** - Controlled vocabularies for all YAML fields
- **[[FILE-NAMING-RULES]]** - File naming conventions
- **[[AGENT-CHECKLIST]]** - AI agent pre-flight checklist
- **[[NOTE-REVIEW-PROMPT]]** - Full review prompt for AI agents
