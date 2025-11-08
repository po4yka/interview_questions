---
---

# Validation Quick Start

## Setup (One Time)

```bash
# Sync uv environment (runs against utils/pyproject.toml)
uv sync --project utils
```

## Common Commands

```bash
# Single file
uv run --project utils python -m utils.validate_note 40-Android/q-compose-state--android--medium.md

# Directory
uv run --project utils python -m utils.validate_note 40-Android/

# Entire vault
uv run --project utils python -m utils.validate_note --all

# With report
uv run --project utils python -m utils.validate_note --all --report validation-report.md

# Quiet mode (summary only)
uv run --project utils python -m utils.validate_note 70-Kotlin/ --quiet
```

## What Gets Validated

**Automated (70%)**
- YAML fields and formats
- Content structure
- Links and references
- File naming and placement
- Android-specific rules

**Manual (30%)**
- Technical accuracy
- Content quality
- Translation equivalence

## Severity Levels

- **CRITICAL** - Must fix (blocks promotion)
- **ERROR** - Broken links, invalid refs
- **WARNING** - Should fix
- **INFO** - Optional improvements

## Exit Codes

- `0` - Passed (or warnings only)
- `1` - Critical issues found

## See Also

- Full docs: `Validation/VALIDATION-README.md`
- Review prompt: `00-Administration/AI-Agents/NOTE-REVIEW-PROMPT.md`
- Taxonomy: `00-Administration/Vault-Rules/TAXONOMY.md`
