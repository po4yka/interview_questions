# Validation Quick Start

## Setup (One Time)

```bash
# Activate virtual environment
source .venv/bin/activate
```

## Common Commands

```bash
# Single file
python validate_note.py 40-Android/q-compose-state--android--medium.md

# Directory
python validate_note.py 40-Android/

# Entire vault
python validate_note.py --all

# With report
python validate_note.py --all --report validation-report.md

# Quiet mode (summary only)
python validate_note.py 70-Kotlin/ --quiet
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

- Full docs: `VALIDATION-README.md`
- Review prompt: `00-Administration/NOTE-REVIEW-PROMPT.md`
- Taxonomy: `00-Administration/TAXONOMY.md`
