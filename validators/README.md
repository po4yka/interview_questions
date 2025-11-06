# Validators Package

Comprehensive validation framework for the Obsidian Interview Questions vault. This package ensures all notes follow consistent structure, formatting, and quality standards.

## Overview

The validators package provides a modular, extensible validation system with:
- **Auto-discovery registry** for validators
- **Shared configuration** for consistency
- **Parallel processing** support
- **Severity-based issue tracking** (CRITICAL, ERROR, WARNING, INFO)

## Architecture

```
validators/
├── base.py                     # BaseValidator + Severity definitions
├── registry.py                 # ValidatorRegistry for auto-discovery
├── config.py                   # Shared constants and patterns
├── __init__.py                 # Package exports
├── yaml_validator.py           # YAML frontmatter validation
├── content_validator.py        # Bilingual content structure
├── link_validator.py           # Wikilink resolution and quality
├── format_validator.py         # Filename and folder conventions
├── code_format_validator.py    # Code formatting rules
├── android_validator.py        # Android-specific taxonomy
├── system_design_validator.py  # System design patterns
└── README.md                   # This file
```

## Validators

### Core Validators

#### 1. YAMLValidator (`yaml_validator.py`)
**Purpose**: Validates YAML frontmatter structure and field types

**Checks**:
- Required fields (15 total): id, title, aliases, topic, subtopics, tags, difficulty, etc.
- Field types (strings, lists, dates)
- Date formats (created_at, updated_at)
- Difficulty values (easy, medium, hard)
- Question kinds (behavioral, coding, system-design, android)

**Severity**: Mostly ERROR for missing/invalid fields

#### 2. ContentValidator (`content_validator.py`)
**Purpose**: Validates bilingual (RU/EN) content structure

**Checks**:
- Required headings for Q&A and concept notes
- Heading order (RU question → EN question → RU answer → EN answer)
- Section body presence
- Blockquote syntax for questions (`>`)
- Follow-ups quality (3-5 questions, no generic patterns)
- Optional question versions (Short/Detailed) for system design
- Subsection content length (>50 chars)

**Severity**: CRITICAL for missing headings, ERROR for blockquotes, WARNING/INFO for quality

#### 3. LinkValidator (`link_validator.py`)
**Purpose**: Validates internal wikilinks and cross-references

**Checks**:
- Wikilink resolution (`[[note-id]]`)
- Related links quality (2-5 recommended)
- Concept link presence (c-* notes)
- Cross-reference balance

**Severity**: ERROR for broken links, WARNING/INFO for quality

#### 4. FormatValidator (`format_validator.py`)
**Purpose**: Validates filename conventions and folder placement

**Checks**:
- Filename patterns:
  - Questions: `q-<slug>--<topic>--<difficulty>.md`
  - Concepts: `c-<slug>.md`
  - MOCs: `moc-<name>.md`
- Folder alignment with topic (e.g., android → `40-Android/`)
- Special folder placement (concepts → `10-Concepts/`, MOCs → `90-MOCs/`)

**Severity**: ERROR for invalid patterns/placement

#### 5. CodeFormatValidator (`code_format_validator.py`)
**Purpose**: Validates code formatting rules

**Checks**:
- Unescaped generic types (e.g., `ArrayList<String>` → should be `` `ArrayList<String>` ``)
- Common type names without backticks (String, Int, ViewModel, etc.)
- Prevents HTML interpretation issues

**Severity**: ERROR for generics (breaks rendering), WARNING for type names

### Domain-Specific Validators

#### 6. AndroidValidator (`android_validator.py`)
**Purpose**: Android-specific taxonomy validation

**Checks**:
- Android subtopics (from taxonomy)
- Tag mirroring (subtopics must appear in tags as `android/<subtopic>`)
- MOC reference (`moc-android`)

**Severity**: ERROR for invalid taxonomy

#### 7. SystemDesignValidator (`system_design_validator.py`)
**Purpose**: System design question patterns and best practices

**Checks**:
- Optional Short/Detailed versions (recommended for hard questions)
- Requirements subsection (Functional/Non-functional)
- Architecture subsection (components, data flow)
- Bilingual alignment for subsections

**Severity**: INFO for recommendations, WARNING for misalignment

## Configuration (`config.py`)

Shared constants used across validators:

### Content Structure
- `STRUCTURED_REQUIRED_HEADINGS`: Required headings for Q&A and concept notes
- `GENERIC_FOLLOWUP_PATTERNS`: Patterns to detect low-quality follow-ups
- `FOLLOWUP_MIN_RECOMMENDED`: 3 (recommended minimum)
- `FOLLOWUP_MAX_RECOMMENDED`: 7 (recommended maximum)
- `MIN_SUBSECTION_CONTENT_LENGTH`: 50 chars
- `MIN_FOLLOWUP_QUESTION_LENGTH`: 20 chars

### File Format
- `FILENAME_PATTERN`: Regex for question filename validation
- `TOPIC_TO_FOLDER_MAPPING`: Topic → folder mapping (8 topics)
- `CONCEPTS_FOLDER`: "10-Concepts"
- `MOCS_FOLDER`: "90-MOCs"
- `CONCEPT_PREFIX`: "c-"
- `MOC_PREFIX`: "moc-"
- `QUESTION_PREFIX`: "q-"

### Code Format
- `COMMON_TYPE_NAMES`: 60+ common types that should be in backticks
- `UNESCAPED_GENERIC_PATTERN`: Regex for detecting unescaped generics

### System Design
- `SYSTEM_DESIGN_SUBSECTIONS`: Requirements/Architecture headings (RU/EN)
- `OPTIONAL_VERSION_SUBSECTIONS`: Short/Detailed version headings (RU/EN)

## Registry System (`registry.py`)

### ValidatorRegistry

Auto-discovery system for validators using decorator pattern.

**Usage**:

```python
from validators.registry import ValidatorRegistry
from validators.base import BaseValidator

@ValidatorRegistry.register
class MyValidator(BaseValidator):
    def validate(self):
        # validation logic
        return self._summary
```

**Key Methods**:

- `register(validator_class)`: Decorator to register validators
- `get_all_validators()`: Get list of all registered validators
- `create_validators(...)`: Instantiate all validators with appropriate parameters

**Benefits**:
- No manual validator list maintenance
- Automatic instantiation with correct parameters
- Supports validators with different constructor signatures (FormatValidator needs vault_root, LinkValidator needs note_index)

## Usage

### Basic Validation

```python
from validators import ValidatorRegistry
from utils.taxonomy_loader import TaxonomyLoader

# Load taxonomy and note index
taxonomy = TaxonomyLoader.load()
note_index = set(...)  # Set of all note IDs

# Create all validators
validators = ValidatorRegistry.create_validators(
    content=body,
    frontmatter=frontmatter,
    path=str(file_path),
    taxonomy=taxonomy,
    vault_root=vault_dir,
    note_index=note_index,
)

# Run validation
for validator in validators:
    summary = validator.validate()
    for issue in summary.issues:
        print(f"{issue.severity}: {issue.message}")
```

### Adding a New Validator

1. Create new file in `validators/`:

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

2. Import in `__init__.py`:

```python
from .my_new_validator import MyNewValidator  # noqa: F401

__all__ = [
    ...,
    "MyNewValidator",
]
```

3. That's it! The validator will be auto-discovered via the registry.

### Parallel Processing

The validation system supports parallel processing for large vaults:

```bash
# Sequential (default)
uv run --project utils python -m utils.validate_note InterviewQuestions/40-Android

# Parallel with 4 workers
uv run --project utils python -m utils.validate_note InterviewQuestions/40-Android --parallel

# Parallel with 8 workers
uv run --project utils python -m utils.validate_note InterviewQuestions/40-Android --parallel --workers 8
```

**Note**: Due to Python's GIL, parallel processing may not be faster for I/O-bound validation. The infrastructure is in place for future CPU-intensive validators (LLM-based checks, AST parsing, etc.).

## Severity Levels

- **CRITICAL**: Structural issues preventing note processing (missing headings, invalid YAML)
- **ERROR**: Serious problems requiring immediate fix (broken links, invalid filenames, missing blockquotes)
- **WARNING**: Issues that should be addressed (low-quality follow-ups, missing concept links)
- **INFO**: Recommendations and best practices (consider adding versions, improve content length)

## Testing

Run validators on specific files or folders:

```bash
# Single file
uv run --project utils python -m utils.validate_note InterviewQuestions/40-Android/q-design-uber-app--android--hard.md

# Entire folder
uv run --project utils python -m utils.validate_note InterviewQuestions/40-Android

# Quiet mode (only show issues)
uv run --project utils python -m utils.validate_note InterviewQuestions/40-Android --quiet

# Generate detailed report
uv run --project utils python -m utils.validate_note InterviewQuestions/40-Android > report.txt
```

## Recent Improvements

### January 2025
- **Registry system**: Auto-discovery for validators (eliminates manual imports)
- **Shared config**: Extracted constants to `config.py` (150+ lines of duplication eliminated)
- **Follow-ups quality**: Detects generic questions, checks count (3-5 recommended)
- **Parallel processing**: ThreadPoolExecutor support (infrastructure for future CPU-bound validators)
- **Code formatting**: Detects unescaped generics and type names
- **Optional versions**: Support for Short/Detailed question versions in system design
- **Blockquote syntax**: Enforces `>` syntax for questions (prevents rendering issues)
- **Related links quality**: Recommends 2-5 links with concept link presence

## Future Enhancements

Potential improvements identified:
- Content length validator (200-400 lines target)
- Code snippet validator (3-5 snippets, 5-15 lines each)
- Complexity analysis validator (O(n) notation for algorithms)
- Translation balance checker (warn if RU/EN differ >30%)
- Smart link suggestions (fuzzy matching for broken links)
- Duplicate detection (similar content across notes)
- Auto-fix capabilities (safe automated corrections)

## Contributing

When adding validators:
1. Follow the decorator pattern (`@ValidatorRegistry.register`)
2. Use shared constants from `config.py`
3. Add clear docstrings explaining checks
4. Use appropriate severity levels
5. Provide helpful error messages with fix suggestions
6. Update this README with new validator documentation

## References

- **NOTE-REVIEW-PROMPT.md**: Comprehensive automation playbook (source of truth for validation rules)
- **taxonomy.yaml**: Android subtopics and topic definitions
- **validate_note.py**: Main validation orchestrator
