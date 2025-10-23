# Note Validation System

Automated validation for Obsidian Q&A notes in the Interview Questions vault.

## Quick Start

### Setup (First Time Only)

```bash
# Activate virtual environment
source .venv/bin/activate

# Verify installation
python validate_note.py --help
```

### Basic Usage

```bash
# Validate a single file
python validate_note.py 40-Android/q-compose-state--android--medium.md

# Validate all files in a directory
python validate_note.py 40-Android/

# Validate entire vault
python validate_note.py --all

# Generate markdown report
python validate_note.py --all --report validation-report.md

# Quiet mode (summary only)
python validate_note.py 70-Kotlin/ --quiet
```

## What Gets Validated

### ✅ YAML Frontmatter (70+ checks)

- **Required fields**: All 15 required fields present
- **Field formats**: ID (YYYYMMDD-HHmmss), dates (YYYY-MM-DD), title (EN / RU)
- **Enums**: topic, difficulty, question_kind, status, language_tags
- **Topic validation**: Against TAXONOMY.md controlled list
- **MOC mapping**: Correct MOC for each topic
- **Related field**: 2-5 items, no double brackets
- **Tags**: English-only, difficulty tag present
- **Forbidden patterns**: No brackets in moc, no Russian in tags, no emoji

### ✅ Content Structure (10+ checks)

- **Required sections**: Both EN/RU Question and Answer sections
- **Section order**: RU before EN (as specified)
- **No extra blank lines**: After YAML closing ---
- **Code blocks**: Language specification
- **List formatting**: Exactly one space after dash
- **Empty sections**: Detection and warnings
- **Related Questions**: Section presence and content

### ✅ Links & Wikilinks (8+ checks)

- **Concept links**: At least one [[c-*]] in content
- **Wikilink resolution**: All [[links]] resolve to existing files
- **Related field**: All items exist in vault
- **Self-links**: Detection and warning
- **Broken links**: Comprehensive checking

### ✅ Formatting (12+ checks)

- **Filename pattern**: q-[slug]--[topic]--[difficulty].md
- **English-only filename**: No Cyrillic characters
- **Lowercase**: Entire filename
- **Folder placement**: Matches topic field
- **Topic consistency**: Filename topic = YAML topic
- **Trailing whitespace**: Detection
- **Empty References section**: Warning if present but empty

### ✅ Android-Specific (5+ checks)

- **Subtopics**: From controlled Android subtopics list
- **Tag mirroring**: android/<subtopic> for each subtopic
- **MOC**: Must be moc-android
- **Invalid subtopics**: Detection and error

## Validation Output

### Console Report

```
================================================================================
Validation Report: q-compose-state--android--medium.md
================================================================================

Overall Status: ⚠️ WARNINGS (2 total issues)

⚠️ WARNINGS
--------------------------------------------------------------------------------
  • [Line 12] Missing required tag: 'difficulty/medium'
  • [Section: Related Questions] Empty section - add 3-8 items

✅ PASSED CHECKS
--------------------------------------------------------------------------------
  ✓ All required YAML fields present
  ✓ ID format valid
  ✓ Title has bilingual format
  ✓ Topic 'android' is valid
  ✓ Subtopics count valid (2 values)
  ✓ Question kind 'android' is valid
  ✓ Difficulty 'medium' is valid
  ✓ Original language is valid
  ✓ Language tags are valid
  ✓ Status 'draft' is valid
  ... and 18 more

================================================================================
```

### Issue Severity Levels

- **🚨 CRITICAL**: Must fix - breaks required rules (blocks status promotion)
- **❌ ERROR**: Factual issues - broken links, invalid references
- **⚠️ WARNING**: Should fix - missing recommended elements
- **ℹ️ INFO**: Style suggestions - optional improvements

## Markdown Report

Generate detailed reports for batch validation:

```bash
python validate_note.py --all --report validation-report.md
```

**Report includes:**
- Summary statistics
- Files with critical issues
- Files with errors
- Files with warnings
- Grouped by severity

## Integration with Workflow

### Pre-commit Validation

Validate before committing changes:

```bash
# In .git/hooks/pre-commit
#!/bin/bash
source .venv/bin/activate
python validate_note.py $(git diff --cached --name-only | grep 'q-.*\.md$')
```

### Continuous Integration

Add to CI pipeline:

```yaml
# .github/workflows/validate.yml
- name: Validate notes
  run: |
    source .venv/bin/activate
    python validate_note.py --all --report validation-report.md
```

### Manual Review Workflow

1. **Create/Edit note** (human or AI)
2. **Run validation**: `python validate_note.py <file>`
3. **Fix CRITICAL issues** (must fix)
4. **Review WARNINGS** (should fix)
5. **Check PASSED** (verify completeness)
6. **Set status**: `draft` → `reviewed` → `ready`

## Architecture

```
validate_note.py              # Main script
├── validators/
│   ├── yaml_validator.py    # YAML frontmatter validation
│   ├── content_validator.py # Content structure validation
│   ├── link_validator.py    # Wikilink resolution
│   ├── format_validator.py  # Formatting rules
│   └── android_validator.py # Android-specific rules
├── utils/
│   ├── taxonomy_loader.py   # Load TAXONOMY.md
│   └── report_generator.py  # Generate reports
└── config/
    └── validation_rules.yaml # (Future: configurable rules)
```

## Customization

### Adding New Validators

Create a new validator in `validators/`:

```python
from validators.base import BaseValidator, Severity

class MyValidator(BaseValidator):
    def validate(self):
        # Your validation logic
        if some_condition:
            self.add_issue(Severity.WARNING, "Issue message")
        else:
            self.add_passed("Check name")
        return self.issues
```

Register in `validate_note.py`:

```python
validators = [
    # ... existing validators
    MyValidator(content, frontmatter, str(filepath)),
]
```

### Extending Checks

Edit existing validators in `validators/` directory. Each validator is modular and independent.

## Troubleshooting

### "No module named 'validators'"

Ensure virtual environment is activated:
```bash
source .venv/bin/activate
```

### "TAXONOMY.md not found"

Run from vault root directory or check path to `00-Administration/TAXONOMY.md`.

### "Invalid YAML frontmatter"

Check for:
- Opening and closing `---` present
- Valid YAML syntax
- No tabs (use spaces)
- Proper array formatting

### False Positives

If validation incorrectly flags an issue:
1. Check if note follows TAXONOMY.md and rules
2. Update validator logic if rule interpretation is wrong
3. Report issue for review

## Statistics

**Automation Coverage**: ~70% of validation checks

- ✅ **Fully automated**: YAML validation, structure, formatting, links
- ⚠️ **Partially automated**: Code syntax, complexity notation
- ❌ **Manual review needed**: Technical accuracy, translation quality

## Exit Codes

- `0` - All validations passed (or only warnings/info)
- `1` - Critical issues found

Use in scripts:

```bash
if python validate_note.py 40-Android/; then
    echo "Validation passed"
else
    echo "Critical issues found"
    exit 1
fi
```

## Performance

- **Single file**: ~50-100ms
- **Directory (100 files)**: ~5-10 seconds
- **Entire vault (942 files)**: ~30-60 seconds

Optimizations:
- Parallel validation (future)
- Caching taxonomy data
- Incremental validation (only changed files)

## Contributing

To add new validation rules:

1. Identify which validator to modify
2. Add check method (`_check_*`)
3. Call from `validate()` method
4. Add test cases
5. Update documentation

## Support

- **Documentation**: `00-Administration/NOTE-REVIEW-PROMPT.md`
- **Taxonomy**: `00-Administration/TAXONOMY.md`
- **Rules**: `00-Administration/AGENTS.md`
- **Issues**: Report in vault documentation

---

**Version**: 1.0.0
**Last Updated**: 2025-10-23
**Python**: 3.11+
**Dependencies**: pyyaml, rich
