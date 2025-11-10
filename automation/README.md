# Obsidian Vault Automation

Comprehensive Python automation tools for maintaining the Interview Questions Obsidian vault.

## Overview

This package provides a unified, professional automation framework for:

- **Anki Ingestion**: Generate bilingual interview notes from article URLs with Firecrawl parsing and automated review (NEW)
- **LLM Review**: AI-powered note review, correction, and knowledge-gap filling
  - Technical accuracy review and automated fixing
  - Metadata sanity checks and YAML repair
  - Concept stub enrichment with meaningful content
  - Iterative validation and improvement
- **Validation**: Comprehensive note validation (YAML, content, links, format, code)
- **Normalization**: Automated frontmatter normalization for concept notes
- **Reporting**: Missing translations and quality reports
- **Graph Analytics**: Link/backlink graph analysis, orphan detection, network statistics
- **Modern CLI**: Beautiful terminal UI with typer + rich (tables, colors, progress bars)
- **CI/CD Integration**: GitHub Actions workflows for automated validation and reporting

All automation code is now consolidated in a single, well-organized location with proper Python packaging.

**NEW**: GitHub Actions CI/CD system now available! See [../.github/README.md](../.github/README.md) for automated validation, health reporting, and more.

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

### Development Installation

To install with development dependencies (testing, linting, type checking):

```bash
cd automation
uv sync --extra dev

# Or with pip
pip install -e ".[dev]"
```

This includes:
- **pytest** - Testing framework
- **pytest-cov** - Code coverage reporting
- **ruff** - Fast Python linter and formatter
- **mypy** - Static type checker
- **types-pyyaml** - Type stubs for PyYAML

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

# Analyze vault graph statistics
uv run --project automation vault graph-stats --hubs 10 --authorities 10

# Find orphaned notes
uv run --project automation vault orphans

# Find broken links
uv run --project automation vault broken-links

# Generate link health report
uv run --project automation vault link-report --output report.md

# Export graph for external analysis
uv run --project automation vault graph-export vault-graph.json
```

After installation to your environment, the `vault` command is available directly:

```bash
vault validate InterviewQuestions/40-Android
vault normalize
vault check-translations
vault graph-stats
vault orphans
```

### Modern CLI (Typer + Rich)

The package also includes `vault-app`, a modern CLI with beautiful terminal output:

```bash
# Same commands, enhanced output with tables, colors, and progress bars
uv run --project automation vault-app graph-stats
uv run --project automation vault-app orphans
uv run --project automation vault-app validate --all
uv run --project automation vault-app anki-ingest "https://example.com/article" --dry-run

# After installation
vault-app graph-stats --hubs 10 --authorities 10
vault-app orphans --output orphans.txt
vault-app anki-ingest "https://example.com/article" --max-cards 2
```

**Features:**
- **Rich Tables**: Beautiful formatted tables with box-drawing characters
- **Color Output**: Syntax highlighting and semantic colors
- **Progress Bars**: Visual feedback for long-running operations
- **Auto-documentation**: Help text from type hints
- **Type Validation**: Automatic validation of command arguments

### Using Makefile (Recommended for Development)

For development, a **Makefile** is provided with convenient shortcuts:

```bash
cd automation

# Setup (one-time)
make install-dev       # Install with dev deps + pre-commit hooks

# Daily workflow
make test              # Run tests
make test-cov          # Run tests with coverage
make lint              # Check code style
make format            # Format code
make type-check        # Run type checker
make security          # Security checks
make check-all         # Run all checks

# Quick workflows
make quick-check       # Format + lint + test (fast)
make full-check        # All checks before commit
make ci                # Simulate CI/CD pipeline

# Vault operations
make validate          # Validate all notes
make validate-parallel # Validate with parallel processing
make graph-stats       # Show graph statistics
make orphans           # Find orphaned notes
make normalize         # Normalize concepts (dry-run)

# Utilities
make clean             # Remove cache files
make pre-commit        # Run pre-commit hooks
make help              # Show all available commands
```

**Benefits**:
- 🚀 **Shorter commands**: `make test` vs `uv run pytest tests/ -v`
- 🔄 **Common workflows**: `make quick-check` runs multiple tools
- 📝 **Self-documenting**: `make help` shows all available commands
- ⚡ **Time savings**: 2-3 minutes per command

**See**: [MAKEFILE_GUIDE.md](MAKEFILE_GUIDE.md) for complete documentation.

### Logging

The automation tools use **Loguru** for professional logging with two output levels:

**Console Logging (INFO level):**
- Useful, concise messages shown during command execution
- Operation start/completion messages
- Warnings and errors
- Success confirmations

**File Logging (DEBUG level):**
- Detailed diagnostic information
- Full stack traces for exceptions
- Debug messages with function/line numbers
- Stored in `~/.cache/obsidian-vault/vault.log`
- Automatic rotation (10 MB per file)
- 1 week retention

**Example log file location:**
```bash
# View recent logs
tail -f ~/.cache/obsidian-vault/vault.log

# Check log file
cat ~/.cache/obsidian-vault/vault.log
```

**Log file format:**
```
2025-11-08 10:27:40.390 | INFO     | obsidian_vault.cli_app:orphans:379 | Finding orphaned notes
2025-11-08 10:27:41.523 | DEBUG    | obsidian_vault.utils.graph_analytics:__init__:32 | Building vault graph
2025-11-08 10:27:45.789 | SUCCESS  | obsidian_vault.cli_app:orphans:395 | No orphaned notes found
```

**Programmatic configuration:**
```python
from obsidian_vault.utils import setup_logging

# Configure logging (optional - auto-configured by CLI)
setup_logging(
    console_level="INFO",    # Console output level
    file_level="DEBUG",      # File output level
    log_file=Path("custom.log"),  # Optional custom log file
    rotation="10 MB",        # File rotation size
    retention="1 week"       # Log retention period
)
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
│       ├── cli.py              # Unified CLI with subcommands (argparse)
│       ├── cli_app.py          # Modern CLI (typer + rich)
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
│       │   ├── frontmatter.py  # Robust YAML frontmatter with order/comment preservation
│       │   ├── markdown.py     # AST-based Markdown parsing with marko
│       │   ├── logging_config.py  # Loguru-based logging configuration
│       │   ├── yaml_loader.py
│       │   ├── taxonomy_loader.py
│       │   ├── report_generator.py
│       │   └── graph_analytics.py  # Graph analysis using obsidiantools
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

- `common.py` - Shared utilities (repo discovery, note parsing, file collection, YAML dumping)
- `frontmatter.py` - **Robust frontmatter handling** with python-frontmatter + ruamel.yaml (preserves order and comments)
- `markdown.py` - **AST-based Markdown parsing** with marko (heading extraction, wikilinks, content analysis)
- `logging_config.py` - **Professional logging** with Loguru (console INFO, file DEBUG, rotation, retention)
- `yaml_loader.py` - YAML loading with error handling
- `taxonomy_loader.py` - Taxonomy file loading and parsing
- `report_generator.py` - Validation report generation
- `graph_analytics.py` - Graph analytics using obsidiantools (link graphs, orphans, hubs, authorities)

### CLI (cli.py & cli_app.py)

**Two CLI options available:**

1. **`vault`** (cli.py) - Original argparse-based CLI
2. **`vault-app`** (cli_app.py) - Modern typer + rich CLI with beautiful output

Both provide the same eight subcommands:

**Content Validation:**
- **validate** - Comprehensive note validation with parallel processing support
- **normalize** - Normalize concept note frontmatter with dry-run support
- **check-translations** - Find notes missing Russian or English translations

**Graph Analytics:**
- **graph-stats** - Display vault network statistics and link quality metrics
- **orphans** - Find orphaned notes (no incoming or outgoing links)
- **broken-links** - Find notes with broken links (links to non-existent notes)
- **link-report** - Generate comprehensive markdown link health report
- **graph-export** - Export vault graph to various formats (GEXF, GraphML, JSON, CSV)

The **vault-app** version adds:
- Rich tables with box-drawing characters
- Color-coded output (errors=red, warnings=yellow, info=blue)
- Progress bars for long operations
- Better formatted help text

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

### Analyze Vault Graph

```bash
# Display network statistics
vault graph-stats

# Show top 10 hub notes (most outgoing links)
vault graph-stats --hubs 10

# Show top 10 authority notes (most incoming links)
vault graph-stats --authorities 10

# Show both
vault graph-stats --hubs 10 --authorities 10
```

Example output:
```
================================================================================
Vault Network Statistics
================================================================================

Basic Metrics:
  Total Notes:          1684
  Total Links:          6548
  Average Degree:       7.78
  Network Density:      0.0023
  Connected Components: 33

Link Quality:
  Reciprocal Links:     438
  Unidirectional Links: 5672
  Orphaned Notes:       25 (1.5%)
  Isolated Notes:       217 (12.9%)
```

### Find Orphaned Notes

```bash
# List orphaned notes (no incoming or outgoing links)
vault orphans

# Save to file
vault orphans --output orphans.txt
```

### Check for Broken Links

```bash
# Find and display broken links
vault broken-links

# Save to file
vault broken-links --output broken.txt
```

### Generate Link Health Report

```bash
# Display comprehensive markdown report
vault link-report

# Save to file
vault link-report --output link-health-report.md
```

The report includes:
- Network statistics (nodes, edges, density, components)
- Link quality metrics (reciprocal vs unidirectional links)
- Orphaned notes list
- Top hub notes (most outgoing links)
- Top authority notes (most incoming links)
- Broken links (if any)

### Export Graph for Analysis

```bash
# Export to JSON (auto-detected from extension)
vault graph-export vault-graph.json

# Export to CSV (edge list)
vault graph-export vault-graph.csv

# Export to GEXF (for Gephi visualization)
vault graph-export vault-graph.gexf

# Export to GraphML (for yEd, Cytoscape)
vault graph-export vault-graph.graphml

# Explicit format specification
vault graph-export output.txt --format json
```

Supported formats:
- **GEXF** - Graph Exchange XML Format (for Gephi)
- **GraphML** - Graph Markup Language (for yEd, Cytoscape)
- **JSON** - Node-link data format
- **CSV** - Simple edge list

### Programmatic Frontmatter Editing

The new frontmatter module provides robust YAML handling with order and comment preservation:

```python
from pathlib import Path
from obsidian_vault.utils import (
    load_frontmatter,
    update_frontmatter,
    dump_frontmatter,
    FrontmatterHandler
)

# Load frontmatter and content
note_path = Path("InterviewQuestions/40-Android/q-compose-state--android--medium.md")
frontmatter, content = load_frontmatter(note_path)

# Update specific fields (preserves order and comments)
update_frontmatter(
    note_path,
    updates={"status": "reviewed", "updated": "2025-01-08"},
    remove_keys=["draft"]
)

# Create new note with frontmatter
new_frontmatter = {
    "id": "kotlin-042",
    "title": "Coroutine Context / Контекст корутин",
    "topic": "kotlin",
    "difficulty": "medium",
    "tags": ["kotlin", "coroutines", "difficulty/medium"]
}
new_content = "# Question\n\nWhat is coroutine context?"

markdown = dump_frontmatter(new_frontmatter, new_content)
Path("new-note.md").write_text(markdown)

# Advanced: use FrontmatterHandler for custom YAML configuration
handler = FrontmatterHandler()
fm, body = handler.load(note_path)
handler.dump(fm, body, Path("output.md"))
```

**Key Benefits:**
- **Order Preservation**: Fields stay in the order you define them
- **Comment Preservation**: Comments in YAML frontmatter are maintained
- **Round-trip Safe**: Read → Modify → Write preserves structure
- **Backward Compatible**: Drop-in replacement for existing `parse_note()` function

### Markdown Content Analysis

The new markdown module provides AST-based Markdown parsing for content analysis:

```python
from pathlib import Path
from obsidian_vault.utils import (
    MarkdownAnalyzer,
    parse_markdown,
    parse_markdown_file,
    extract_headings,
    extract_wikilinks,
    has_required_headings
)

# Parse markdown text
markdown_text = """
# Question (EN)
What is a coroutine?

See [[c-coroutines]] for background.

## Answer (EN)
A coroutine is a suspendable function.
"""

analyzer = parse_markdown(markdown_text)

# Extract headings
headings = analyzer.get_headings()
for h in headings:
    print(f"Level {h['level']}: {h['text']}")
# Output:
# Level 1: Question (EN)
# Level 2: Answer (EN)

# Extract Obsidian wikilinks
wikilinks = analyzer.get_wikilinks()
print(wikilinks)  # ['c-coroutines']

# Check for required headings
has_question = analyzer.has_heading("Question (EN)", level=1)
print(has_question)  # True

# Count code blocks
code_blocks = analyzer.count_code_blocks()

# Parse from file
note_path = Path("InterviewQuestions/70-Kotlin/q-coroutine-basics--kotlin--easy.md")
analyzer = parse_markdown_file(note_path)
headings = analyzer.get_headings()
wikilinks = analyzer.get_wikilinks()

# Get text between headings
text = analyzer.get_text_between_headings("Question (EN)", "Answer (EN)")

# Convenience functions
headings = extract_headings(markdown_text)
wikilinks = extract_wikilinks(markdown_text)
result = has_required_headings(markdown_text, ["Question (EN)", "Answer (EN)", "References"])
# {'Question (EN)': True, 'Answer (EN)': True, 'References': False}
```

**Key Features:**
- **AST-based Parsing**: Uses marko for CommonMark-compliant parsing
- **Heading Extraction**: Extract all headings with levels and text
- **Wikilink Support**: Parse Obsidian-style `[[links]]` and `[[link|alias]]`
- **Content Analysis**: Count code blocks, check for required sections
- **Text Extraction**: Get content between headings for validation

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

### Runtime
- Python >= 3.11 (3.11, 3.12, 3.13 supported)
- PyYAML >= 6.0.2
- python-frontmatter >= 1.0.0 (YAML frontmatter extraction/insertion)
- ruamel.yaml >= 0.18.0 (order and comment preservation for YAML)
- marko >= 2.0.0 (AST-based Markdown parsing)
- typer >= 0.12.0 (modern CLI framework with type hints)
- rich >= 13.0.0 (beautiful terminal formatting)
- obsidiantools >= 0.10.0 (graph analytics)
- pandas >= 2.0.0 (data processing for graph analytics)
- networkx >= 3.0 (graph analysis)

### Build
- setuptools >= 75.0.0
- wheel

### Development (Optional)
- pytest >= 8.0.0
- pytest-cov >= 5.0.0
- ruff >= 0.8.0 (linting and formatting)
- mypy >= 1.13.0 (type checking)
- types-pyyaml >= 6.0.12 (type stubs)

## Testing

Tests will be added in the `tests/` directory (future enhancement).

Run linting and type checking:

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type check
uv run mypy src/
```

## Documentation

- **This file**: Overview and usage
- **LLM_REVIEW.md**: LLM-powered review system with knowledge-gap agent (NEW)
- **validators/README.md**: Detailed validator documentation
- **../AGENTS.md**: AI agent instructions for vault maintenance
- **../CLAUDE.md**: Claude Code agent guide

## Version History

### 0.8.0 (Current)
- **Professional Logging**: Integrated Loguru for comprehensive logging
- **Dual-Level Logging**:
  - Console: INFO level with useful, concise messages
  - File: DEBUG level with detailed diagnostic information
- **Automatic Log Management**:
  - File rotation (10 MB per file)
  - 1 week retention
  - Stored in `~/.cache/obsidian-vault/vault.log`
- **Enhanced Error Tracking**: Full stack traces in log files
- **New Logging Module**: Created `utils/logging_config.py` with setup functions
- **New Dependency**: loguru >= 0.7.0
- **CLI Integration**: All commands now use structured logging

### 0.7.0
- **Modern CLI**: Integrated typer + rich for beautiful terminal output
- **New CLI Application**: Created `cli_app.py` with typer-based modern CLI
- **Rich Terminal Features**:
  - Beautiful formatted tables with box-drawing characters
  - Color-coded output (red=errors, yellow=warnings, blue=info)
  - Progress bars and spinners for long operations
  - Auto-generated help from type hints
- **Dual CLI**: Both `vault` (argparse) and `vault-app` (typer+rich) available
- **New Dependencies**: typer >= 0.12.0, rich >= 13.0.0
- **Enhanced UX**: Better error messages, validation, and formatted output

### 0.6.0
- **Markdown Parsing**: Integrated marko for AST-based Markdown analysis
- **New Markdown Module**: Created `utils/markdown.py` with MarkdownAnalyzer class
- **Content Analysis Features**:
  - Extract headings with levels and text
  - Parse Obsidian-style wikilinks `[[note]]` and `[[note|alias]]`
  - Count code blocks and analyze structure
  - Check for required headings
  - Extract text between headings
  - Get standard Markdown links
- **New Convenience Functions**: `extract_headings`, `extract_wikilinks`, `has_required_headings`
- **New Dependency**: marko >= 2.0.0 (CommonMark-compliant parser)

### 0.5.0
- **Robust Frontmatter Handling**: Integrated python-frontmatter + ruamel.yaml
- **Order Preservation**: YAML fields now maintain their original order
- **Comment Preservation**: Comments in frontmatter are preserved during edits
- **New Frontmatter Module**: Created `utils/frontmatter.py` with FrontmatterHandler class
- **Enhanced parse_note**: Updated to use new frontmatter library with fallback
- **New Dependencies**: python-frontmatter >= 1.0.0, ruamel.yaml >= 0.18.0
- **Backward Compatible**: Existing code continues to work seamlessly

### 0.4.0
- **Graph Analytics**: Integrated obsidiantools for advanced vault analysis
- **New CLI Commands**:
  - `vault graph-stats` - Network statistics and link quality metrics
  - `vault orphans` - Find orphaned notes (no links)
  - `vault broken-links` - Detect broken links
  - `vault link-report` - Generate comprehensive link health report
  - `vault graph-export` - Export graph to GEXF, GraphML, JSON, CSV
- **New Dependencies**: obsidiantools >= 0.10.0, pandas >= 2.0.0, networkx >= 3.0
- **Graph Analytics Module**: Created `utils/graph_analytics.py` with VaultGraph class

### 0.3.1
- **Updated dependencies**: PyYAML >= 6.0.2, setuptools >= 75.0.0
- **Python 3.13 support**: Added support for Python 3.13
- **Development tooling**: Added optional dev dependencies (pytest, ruff, mypy)
- **Tool configuration**: Added ruff, mypy, and pytest configuration to pyproject.toml
- **Enhanced build**: Added wheel to build requirements

### 0.3.0
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

## CI/CD Integration

The automation package is integrated with GitHub Actions for continuous validation and reporting:

**Workflows**:
- **Validate Notes** (PR checks) - Validates all changed notes before merge
- **Vault Health Report** (daily) - Generates comprehensive health reports
- **Normalize Concepts** (manual) - Standardizes concept frontmatter
- **Graph Export** (weekly) - Exports vault graph for analysis

**Benefits**:
- Automated quality checks on every PR
- Daily health monitoring
- Historical tracking via separate branches
- Automatic issue creation for critical problems

**Documentation**: See [../.github/README.md](../.github/README.md) for complete CI/CD documentation.

**Quick Reference**: See [../.github/WORKFLOWS-QUICK-REFERENCE.md](../.github/WORKFLOWS-QUICK-REFERENCE.md) for common tasks.

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
7. Consider CI/CD integration for new features

## Support

For issues or questions:
1. Check the documentation in this README and validators/README.md
2. Review existing scripts for examples
3. Consult AGENTS.md for vault-specific rules
