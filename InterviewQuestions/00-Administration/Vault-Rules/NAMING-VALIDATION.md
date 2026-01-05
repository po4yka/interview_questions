---
---

# Naming Validation Scripts

**Purpose**: Scripts and tools for validating file naming conventions.
**Last Updated**: 2025-11-25

See [[FILE-NAMING-RULES]] for core rules.

## Quick Validation Commands

### Check for Cyrillic Characters in Filenames

```bash
# Find any files with Cyrillic characters
find . -name "*.md" -type f | grep -E '[a-ya-YA-YayoYo]'

# Should return nothing if all files are properly named
```

### Check for Uppercase in Filenames

```bash
# Find files with uppercase letters
find . -name "*.md" -type f | grep -E '[A-Z]'

# Should return nothing (except 00-Administration files)
```

### Check for Spaces in Filenames

```bash
# Find files with spaces
find . -name "* *.md" -type f

# Should return nothing
```

### Check Q&A Filename Pattern

```bash
# Check Q&A files follow pattern
find 20-Algorithms 30-System-Design 40-Android 50-Backend 60-CompSci 70-Kotlin 80-Tools \
  -name "q-*.md" | grep -v -E '^[0-9]+-[A-Za-z]+/q-[a-z0-9-]+--[a-z-]+--[a-z]+\.md$'

# Should return nothing if all files follow pattern
```

## Using the Vault Validator

```bash
# Validate single file
uv run --project utils python -m utils.validate_note <file.md>

# Validate directory
uv run --project utils python -m utils.validate_note 40-Android/

# Validate entire vault
uv run --project utils python -m utils.validate_note --all
```

## Batch Rename Script

Use this script to extract title from YAML and generate proper filename:

```python
#!/usr/bin/env python3
"""
Rename files to follow naming convention.
Extract title from YAML frontmatter and generate proper filename.
"""

import os
import re
import yaml

def extract_title_from_file(filepath):
    """Extract English title from YAML frontmatter."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract YAML frontmatter
    match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None

    frontmatter = yaml.safe_load(match.group(1))
    title = frontmatter.get('title', '')

    # Extract English part (before " / ")
    if ' / ' in title:
        title = title.split(' / ')[0]

    return title

def title_to_slug(title):
    """Convert title to filename slug."""
    # Convert to lowercase
    slug = title.lower()
    # Replace spaces with hyphens
    slug = slug.replace(' ', '-')
    # Remove special characters
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    # Remove multiple hyphens
    slug = re.sub(r'-+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')

    return slug

# Usage example:
# title = extract_title_from_file('path/to/file.md')
# slug = title_to_slug(title)
# print(f"q-{slug}--topic--difficulty.md")
```

## Vault Statistics

**Current Count**: ~1300+ Q&A files

| Directory | Approx Count |
|-----------|-------------|
| `20-Algorithms/` | ~200 |
| `30-System-Design/` | ~10 |
| `40-Android/` | ~530 |
| `50-Backend/` | ~30 |
| `60-CompSci/` | ~170 |
| `70-Kotlin/` | ~350 |
| `80-Tools/` | ~10 |

## Enforcement

**This rule is MANDATORY for all new notes.**

- **LLM Agents**: MUST follow these rules when creating files
- **Import Scripts**: MUST validate and normalize filenames
- **Manual Creation**: MUST comply with these rules
- **Validation**: Run `validate_note` before committing

**Violations**: Files with non-compliant names will be flagged for renaming.

## See Also

- [[FILE-NAMING-RULES]] - Core naming rules
- [[NAMING-EXAMPLES]] - Detailed examples
- [[VALIDATION-QUICKSTART]] - Full validation system
