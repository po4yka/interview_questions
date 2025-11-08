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

The automation tools are accessed via a unified `vault` CLI with subcommands:

```bash
# Show available commands
uv run --project automation vault --help

# Validate notes
uv run --project automation vault validate InterviewQuestions/40-Android

# Normalize concept frontmatter
uv run --project automation vault normalize

# Find missing translations
uv run --project automation vault check-translations
```

After installation to your environment, the `vault` command is available directly:

```bash
vault validate InterviewQuestions/40-Android
vault normalize
vault check-translations
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
│       ├── cli.py              # Unified CLI with subcommands
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
│       │   ├── common.py       # Shared utilities (repo discovery, parsing, etc.)
│       │   ├── yaml_loader.py
│       │   ├── taxonomy_loader.py
│       │   └── report_generator.py
│       └── scripts/            # (Deprecated - use CLI instead)
│           └── __init__.py
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

### CLI (cli.py)

Unified command-line interface with three subcommands:

- **vault validate** - Comprehensive note validation with parallel processing support
- **vault normalize** - Normalize concept note frontmatter with dry-run support
- **vault check-translations** - Find notes missing Russian or English translations

All three commands consolidated from individual scripts into a single, maintainable CLI tool.

## Usage Examples

All commands use the `vault` CLI with subcommands. For convenience, prefix with `uv run --project automation`:

### Validate a Single File

```bash
vault validate InterviewQuestions/40-Android/q-compose-state--android--medium.md
```

### Validate a Folder

```bash
vault validate InterviewQuestions/40-Android
```

### Validate Entire Vault

```bash
vault validate --all
```

### Parallel Validation

```bash
# Use 4 workers (default)
vault validate InterviewQuestions/40-Android --parallel

# Use 8 workers
vault validate InterviewQuestions/40-Android --parallel --workers 8
```

### Quiet Mode (CI-friendly)

```bash
vault validate InterviewQuestions/40-Android --quiet
```

### Generate Report

```bash
vault validate InterviewQuestions/40-Android --report report.md
```

### Normalize Concept Notes

```bash
# Preview changes without modifying files
vault normalize --dry-run

# Apply normalization
vault normalize
```

This will:
- Normalize YAML frontmatter
- Infer missing fields from tags
- Set correct MOC references
- Ensure consistent field ordering

### Find Missing Translations

```bash
# Print to stdout
vault check-translations

# Save to file
vault check-translations --output missing.txt
```

Finds notes missing Russian or English content sections.

## Development

### Package Layout

This package follows Python best practices:

- **Proper imports**: No more `sys.path.insert()` hacks
- **Single location**: All automation in one place
- **Clear hierarchy**: validators → utils → cli
- **Unified CLI**: Single entry point with subcommands
- **Extensible**: Easy to add new validators, utils, or CLI commands

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

### Adding a New CLI Command

Add a new subcommand to the unified CLI in `src/obsidian_vault/cli.py`:

1. Create the command function:

```python
def cmd_my_command(args: argparse.Namespace) -> int:
    """My new command implementation."""
    # Implementation
    return 0
```

2. Add the subcommand parser in `main()`:

```python
my_parser = subparsers.add_parser(
    "my-command",
    help="Description of my command",
)
my_parser.add_argument("--option", help="Optional argument")
```

3. Add the command handler:

```python
elif args.command == "my-command":
    return cmd_my_command(args)
```

4. Test it:

```bash
vault my-command --help
```

## Migration from Old Structure

The automation code was previously scattered across three locations:

- `scripts/` - Utility scripts
- `utils/` - Python package with validation utilities
- `validators/` - Validator modules

This has been consolidated into the new `automation/` directory with proper Python packaging.

### Old vs New Usage

**v0.1 (scattered scripts):**
```bash
# Three separate scripts with sys.path hacks
uv run --project utils python -m utils.validate_note InterviewQuestions/40-Android
python scripts/normalize_concepts.py
python scripts/list_missing_ru_sections.py
```

**v0.2 (consolidated directory):**
```bash
# Clean command-line tools, still separate
validate-notes InterviewQuestions/40-Android
normalize-concepts
list-missing-ru
```

**v0.3 (unified CLI) - Current:**
```bash
# Single CLI with subcommands
vault validate InterviewQuestions/40-Android
vault normalize
vault check-translations
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

### 0.3.0 (Current)
- **Consolidated CLI**: Single `vault` command with subcommands
- **Removed duplication**: Eliminated ~400 lines of duplicate code
- **Shared utilities**: Created `utils/common.py` with shared functions
- **Breaking change**: Old individual commands (`validate-notes`, `normalize-concepts`, `list-missing-ru`) replaced with `vault` subcommands

### 0.2.0
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
3. Add to appropriate module:
   - New validators → `validators/`
   - Shared utilities → `utils/common.py`
   - New CLI commands → `cli.py` as subcommands
4. Update documentation (README and docstrings)
5. Use type hints
6. Follow existing code style

## Support

For issues or questions:
1. Check the documentation in this README and validators/README.md
2. Review existing scripts for examples
3. Consult AGENTS.md for vault-specific rules
