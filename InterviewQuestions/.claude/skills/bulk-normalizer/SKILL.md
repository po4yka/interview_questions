---\
name: bulk-normalizer
description: >
  Batch normalize YAML frontmatter across multiple files. Standardizes field ordering,
  fixes array formatting to single-line, updates timestamps, removes duplicate fields,
  and previews changes before applying. Essential for monthly maintenance and ensuring
  consistent metadata structure across the vault.
---\

# Bulk Normalizer

## Purpose

Standardize YAML frontmatter across multiple files:

1. **Field Ordering**: Enforce consistent field order in YAML
2. **`Array` Formatting**: Convert multi-line arrays to single-line `[a, b, c]`
3. **Timestamp Updates**: Update `updated` field to current date
4. **Duplicate Removal**: Remove redundant/duplicate fields
5. **Format Cleanup**: Fix spacing, quoting, and formatting issues
6. **Preview Mode**: Show changes before applying

## When to Use

Activate this skill when user requests:
- "Normalize YAML in [folder]"
- "Fix YAML formatting"
- "Standardize metadata"
- "Clean up frontmatter"
- "Update timestamps"
- "Remove duplicate fields"
- During monthly maintenance
- After bulk content imports

## Prerequisites

Required context:
- Target folder or file pattern
- Understanding of vault YAML conventions
- Standard field ordering reference

## Standard YAML Format

### Field Order

```yaml
---
id: kotlin-001
title: Question Title EN / Заголовок RU
aliases: [Alias1, Alias2, Псевдоним]

# Classification
topic: kotlin
subtopics: [coroutines, concurrency]
question_kind: theory
difficulty: medium

# Language
original_language: en
language_tags: [en, ru]

# Workflow
status: draft

# Links
moc: moc-kotlin
related: [c-coroutines, q-related-question--kotlin--medium]

# Timestamps
created: 2025-10-15
updated: 2025-11-15

# Tags
tags: [kotlin, coroutines, difficulty/medium]
---
```

### Array Formatting Rules

**Correct (single-line)**:
```yaml
subtopics: [coroutines, concurrency]
related: [c-coroutines, q-other]
tags: [kotlin, difficulty/medium]
```

**Incorrect (multi-line)**:
```yaml
subtopics:
  - coroutines
  - concurrency
related:
  - c-coroutines
  - q-other
```

## Process

### Step 1: Identify Target Files

Determine scope:

```
Options:
- Single file: "70-Kotlin/q-example.md"
- Folder: "70-Kotlin/"
- Pattern: "all kotlin notes"
- Full vault: "entire vault"
```

### Step 2: Parse Current YAML

For each file:

```
1. Read file content
2. Extract YAML frontmatter
3. Parse into structured data
4. Identify issues:
   - Wrong field order
   - Multi-line arrays
   - Missing fields
   - Duplicate fields
   - Incorrect formatting
```

### Step 3: Generate Normalized YAML

Apply normalization rules:

```python
# Pseudocode
def normalize_yaml(yaml_data):
    normalized = {}

    # 1. Reorder fields
    for field in STANDARD_FIELD_ORDER:
        if field in yaml_data:
            normalized[field] = yaml_data[field]

    # 2. Convert arrays to single-line
    for array_field in ['subtopics', 'related', 'tags', 'aliases', 'language_tags']:
        if array_field in normalized:
            normalized[array_field] = format_single_line(normalized[array_field])

    # 3. Update timestamp
    normalized['updated'] = today()

    # 4. Remove duplicates
    remove_duplicate_fields(normalized)

    return normalized
```

### Step 4: Preview Changes

Show diff before applying:

```markdown
## Preview: q-example--kotlin--medium.md

### Before:
```yaml
subtopics:
  - coroutines
  - flow
tags:
  - kotlin
  - difficulty/medium
updated: 2025-10-01
id: kotlin-005
title: Example Question
```

### After:
```yaml
id: kotlin-005
title: Example Question
subtopics: [coroutines, flow]
tags: [kotlin, difficulty/medium]
updated: 2025-11-15
```

### Changes:
- Reordered fields (id, title first)
- Converted subtopics to single-line
- Converted tags to single-line
- Updated timestamp (2025-10-01 → 2025-11-15)
```

### Step 5: Apply Changes

With user confirmation:

```
1. Create backup (optional)
2. Write normalized YAML to file
3. Preserve content after YAML
4. Report success/failure
```

### Step 6: Generate Report

Summary of all normalizations:

```markdown
# Bulk Normalization Report

**Scope**: 70-Kotlin/
**Files Processed**: 358
**Files Modified**: 45

---

## Summary

| Change Type | Files | Occurrences |
|-------------|-------|-------------|
| Field Reordering | 23 | 23 |
| Array Formatting | 42 | 89 |
| Timestamp Update | 45 | 45 |
| Duplicate Removal | 3 | 5 |

---

## Files Modified

| File | Changes Applied |
|------|-----------------|
| q-coroutine-basics--kotlin--easy.md | Array formatting, timestamp |
| q-flow-operators--kotlin--hard.md | Field reorder, arrays |
| ... | ... |

---

## Files Unchanged

313 files already compliant with standards.

---

**Normalization complete.**
```

## Examples

### Example 1: Normalize Folder

**User**: "Normalize YAML in 70-Kotlin/"

**Process**:
1. Find 358 files in folder
2. Parse each YAML
3. Apply normalization
4. Report changes

**Output**:
```markdown
# Normalization: 70-Kotlin/

Files: 358
Modified: 45 (12.6%)
Already compliant: 313 (87.4%)

## Changes Applied
- 89 arrays converted to single-line format
- 45 timestamps updated
- 23 files reordered

All files now compliant with YAML standards.
```

### Example 2: Fix Arrays Only

**User**: "Fix multi-line arrays in all files"

**Process**:
1. Scan all Q&A files
2. Find multi-line arrays
3. Convert to single-line
4. Report changes

**Output**:
```markdown
# Array Normalization

Files scanned: 972
Files with multi-line arrays: 156
Arrays converted: 312

## Examples of Conversions

Before:
```yaml
subtopics:
  - coroutines
  - flow
```

After:
```yaml
subtopics: [coroutines, flow]
```

All arrays now in single-line format.
```

### Example 3: Preview Without Applying

**User**: "Preview YAML normalization for 40-Android/"

**Process**:
1. Scan folder
2. Generate diffs
3. Show preview only
4. Do not modify files

**Output**:
```markdown
# Normalization Preview: 40-Android/

Would modify 78 of 527 files.

## Sample Changes

### q-compose-state--android--medium.md
- Convert subtopics to single-line
- Convert tags to single-line
- Update timestamp

### q-room-basics--android--easy.md
- Reorder fields
- Update timestamp

[... more previews ...]

Run with --apply to make these changes.
```

### Example 4: Update Timestamps Only

**User**: "Update all timestamps in 70-Kotlin/"

**Process**:
1. Find files in folder
2. Update only `updated` field
3. Preserve everything else

**Output**:
```markdown
# Timestamp Update: 70-Kotlin/

Files updated: 358
New timestamp: 2025-11-15

All files now have current `updated` date.
```

### Example 5: Remove Duplicate Fields

**User**: "Find and remove duplicate YAML fields"

**Process**:
1. Scan all files
2. Detect duplicate fields
3. Remove duplicates (keep first)
4. Report changes

**Output**:
```markdown
# Duplicate Field Removal

Files scanned: 972
Files with duplicates: 12

## Duplicates Found and Removed

| File | Duplicate Field | Action |
|------|-----------------|--------|
| q-example1.md | date created | Removed (kept created) |
| q-example2.md | date modified | Removed (kept updated) |
| q-test.md | tags (2x) | Merged into single |

12 duplicate fields removed from 12 files.
```

## Error Handling

### YAML Parse Error

**Problem**: File has malformed YAML

**Solution**:
1. Log file as unparseable
2. Skip file in batch
3. Report in summary
4. Suggest manual review

### Field Type Mismatch

**Problem**: Expected array but found string

**Solution**:
1. Convert string to single-item array
2. Log the conversion
3. Continue processing

### Large Files

**Problem**: File too large to process efficiently

**Solution**:
1. Process in chunks
2. Show progress
3. Option to skip large files

## Normalization Options

### Full Normalization (Default)
```
- Reorder all fields
- Convert all arrays
- Update timestamps
- Remove duplicates
```

### Selective Normalization
```
--arrays-only: Only fix array formatting
--timestamps-only: Only update timestamps
--reorder-only: Only reorder fields
--duplicates-only: Only remove duplicates
```

### Dry Run
```
--preview: Show changes without applying
--diff: Show detailed diffs
```

### Backup
```
--backup: Create .bak files before modifying
```

## Integration with Other Skills

**Workflow: Post-Import Cleanup**
1. Import new content
2. Run `bulk-normalizer` to standardize
3. Run `batch-validator` to verify
4. Fix remaining issues

**Workflow: Monthly Maintenance**
1. Run `vault-health-report` for overview
2. Use `bulk-normalizer` for formatting
3. Use `link-fixer` for connectivity
4. Run `batch-validator` for final check

**Workflow: Pre-Commit**
1. Run `bulk-normalizer --preview` on changes
2. Apply if changes look good
3. Commit standardized files

## Standard Field Order Reference

```yaml
# Identity
id
title
aliases

# Classification
topic
subtopics
question_kind
difficulty

# Language
original_language
language_tags

# Workflow
status

# Links
moc
related

# Timestamps
created
updated

# Discovery
tags
sources
```

## Notes

**Non-Destructive Preview**: Default shows changes without applying.

**Idempotent**: Running multiple times produces same result.

**Content Preservation**: Only modifies YAML, never touches content.

**Batch Efficient**: Processes hundreds of files quickly.

**Reversible**: With backup option, changes can be undone.

---

**Version**: 1.0
**Last Updated**: 2025-01-05
**Status**: Production Ready
