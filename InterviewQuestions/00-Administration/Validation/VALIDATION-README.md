---
---

# Validation System

Automated validation for Interview Questions vault notes.

## Setup
```bash
uv sync --project utils
uv run --project utils python -m utils.validate_note --help
```

## Usage
```bash
# Single file
uv run --project utils python -m utils.validate_note <file>

# Directory
uv run --project utils python -m utils.validate_note <directory>/

# All files
uv run --project utils python -m utils.validate_note --all

# With report
uv run --project utils python -m utils.validate_note --all --report report.md
```

## Validation Checks
- **YAML frontmatter**: Required fields, formats, enums, taxonomy validation
- **Content structure**: Bilingual sections, code formatting, wikilinks
- **File organization**: Correct folders, naming conventions
- **Cross-references**: MOC links, related fields, broken links

