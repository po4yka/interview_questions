# Obsidian Vault Automation

Comprehensive Python automation tools for maintaining the Interview Questions Obsidian vault.

## Overview

This package provides a unified, professional automation framework for:

- **Validation**: Comprehensive note validation (YAML, content, links, format, code)
- **Normalization**: Automated frontmatter normalization for concept notes
- **Reporting**: Missing translations and quality reports

All automation code is now consolidated in a single, well-organized location with proper Python packaging.

## Installation

### Using uv (Recommended)

```bash
cd automation
uv sync
```

### Using pip

```bash
cd automation
pip install -e .
```

## Quick Start

After installation, you can use the command-line tools directly:

```bash
# Validate notes
validate-notes InterviewQuestions/40-Android

# Normalize concept notes
normalize-concepts

# Find missing Russian translations
list-missing-ru
```

Or use the Python module directly:

```bash
# Validate notes
uv run --project automation python -m obsidian_vault.scripts.validate_note InterviewQuestions/40-Android

# Normalize concepts
uv run --project automation python -m obsidian_vault.scripts.normalize_concepts

# List missing translations
uv run --project automation python -m obsidian_vault.scripts.list_missing_ru_sections
```

## Structure

```
automation/
├── README.md                   # This file
├── pyproject.toml              # Package configuration
├── uv.lock                     # Dependency lock file
├── src/
│   └── obsidian_vault/         # Main package
│       ├── __init__.py
│       ├── validators/         # Validation framework
│       │   ├── __init__.py
│       │   ├── base.py         # Base validator class
│       │   ├── registry.py     # Auto-discovery registry
│       │   ├── config.py       # Shared constants
│       │   ├── yaml_validator.py
│       │   ├── content_validator.py
│       │   ├── link_validator.py
│       │   ├── format_validator.py
│       │   ├── code_format_validator.py
│       │   ├── android_validator.py
│       │   ├── system_design_validator.py
│       │   └── README.md       # Validator documentation
│       ├── utils/              # Utility helpers
│       │   ├── __init__.py
│       │   ├── yaml_loader.py
│       │   ├── taxonomy_loader.py
│       │   └── report_generator.py
│       └── scripts/            # Executable scripts
│           ├── __init__.py
│           ├── validate_note.py
│           ├── normalize_concepts.py
│           └── list_missing_ru_sections.py
└── tests/                      # Tests (future)
    └── __init__.py
```

## Components

### Validators

Comprehensive validation framework with auto-discovery registry. See `src/obsidian_vault/validators/README.md` for detailed documentation.

**Available validators:**
- `YAMLValidator` - Frontmatter structure and field types
- `ContentValidator` - Bilingual content structure
- `LinkValidator` - Wikilink resolution and quality
- `FormatValidator` - Filename and folder conventions
- `CodeFormatValidator` - Code formatting rules
- `AndroidValidator` - Android-specific taxonomy
- `SystemDesignValidator` - System design patterns

### Utils

Utility helpers used across scripts and validators:

- `yaml_loader.py` - YAML loading with error handling
- `taxonomy_loader.py` - Taxonomy file loading and parsing
- `report_generator.py` - Validation report generation

### Scripts

Executable automation scripts:

- `validate_note.py` - Main validation orchestrator with parallel processing
- `normalize_concepts.py` - Normalize concept note frontmatter
- `list_missing_ru_sections.py` - Find notes missing translations

## Usage Examples

### Validate a Single File

```bash
validate-notes InterviewQuestions/40-Android/q-compose-state--android--medium.md
```

### Validate a Folder

```bash
validate-notes InterviewQuestions/40-Android
```

### Validate Entire Vault

```bash
validate-notes --all
```

### Parallel Validation

```bash
# Use 4 workers (default)
validate-notes InterviewQuestions/40-Android --parallel

# Use 8 workers
validate-notes InterviewQuestions/40-Android --parallel --workers 8
```

### Quiet Mode (CI-friendly)

```bash
validate-notes InterviewQuestions/40-Android --quiet
```

### Generate Report

```bash
validate-notes InterviewQuestions/40-Android --report report.md
```

### Normalize Concept Notes

```bash
normalize-concepts
```

This will:
- Normalize YAML frontmatter
- Infer missing fields from tags
- Set correct MOC references
- Ensure consistent field ordering

### Find Missing Translations

```bash
list-missing-ru
```

Outputs a list of notes missing Russian or English sections to `missing_ru_sections.txt`.

## Development

### Package Layout

This package follows Python best practices:

- **Proper imports**: No more `sys.path.insert()` hacks
- **Single location**: All automation in one place
- **Clear hierarchy**: validators → utils → scripts
- **Entry points**: Command-line tools via `[project.scripts]`
- **Extensible**: Easy to add new validators, utils, or scripts

### Adding a New Validator

1. Create a new file in `src/obsidian_vault/validators/`:

```python
from __future__ import annotations
from .base import BaseValidator, Severity
from .registry import ValidatorRegistry

@ValidatorRegistry.register
class MyNewValidator(BaseValidator):
    """Validate custom rules."""

    def validate(self):
        self._check_something()
        return self._summary

    def _check_something(self) -> None:
        if condition:
            self.add_issue(Severity.ERROR, "Error message")
        else:
            self.add_passed("Check passed")
```

2. Import in `src/obsidian_vault/validators/__init__.py`:

```python
from .my_new_validator import MyNewValidator  # noqa: F401

__all__ = [
    ...,
    "MyNewValidator",
]
```

3. Done! The validator will be auto-discovered via the registry.

### Adding a New Script

1. Create a new file in `src/obsidian_vault/scripts/`:

```python
def main():
    """Script description."""
    # Implementation
    pass

if __name__ == '__main__':
    main()
```

2. Add entry point in `pyproject.toml`:

```toml
[project.scripts]
my-script = "obsidian_vault.scripts.my_script:main"
```

3. Reinstall package:

```bash
uv sync
```

## Migration from Old Structure

The automation code was previously scattered across three locations:

- `scripts/` - Utility scripts
- `utils/` - Python package with validation utilities
- `validators/` - Validator modules

This has been consolidated into the new `automation/` directory with proper Python packaging.

### Old vs New Usage

**Old:**
```bash
# Had to use complex paths and sys.path hacks
uv run --project utils python -m utils.validate_note InterviewQuestions/40-Android
python scripts/normalize_concepts.py
python scripts/list_missing_ru_sections.py
```

**New:**
```bash
# Clean command-line tools
validate-notes InterviewQuestions/40-Android
normalize-concepts
list-missing-ru

# Or via Python module
uv run --project automation python -m obsidian_vault.scripts.validate_note InterviewQuestions/40-Android
```

## Requirements

- Python >= 3.11
- PyYAML >= 6.0

## Testing

Tests will be added in the `tests/` directory (future enhancement).

## Documentation

- **This file**: Overview and usage
- **validators/README.md**: Detailed validator documentation
- **../AGENTS.md**: AI agent instructions for vault maintenance
- **../CLAUDE.md**: Claude Code agent guide

## Version History

### 0.2.0 (Current)
- Reorganized into unified `automation/` directory
- Proper Python package structure
- Command-line entry points
- No more sys.path hacks
- Clear module hierarchy

### 0.1.0 (Legacy)
- Original scattered structure across `scripts/`, `utils/`, `validators/`

## License

See LICENSE file in repository root.

## Contributing

When adding new automation:

1. Follow the package structure
2. Use proper imports (no sys.path hacks)
3. Add to appropriate module (validators/utils/scripts)
4. Update documentation
5. Use type hints
6. Follow existing code style

## Support

For issues or questions:
1. Check the documentation in this README and validators/README.md
2. Review existing scripts for examples
3. Consult AGENTS.md for vault-specific rules
