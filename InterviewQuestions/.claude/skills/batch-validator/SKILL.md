---
name: batch-validator
description: >
  Validate multiple files at once with aggregated reporting. Extends obsidian-validator
  to work on entire folders or topics. Groups issues by severity, generates fix
  suggestions, supports dry-run mode, and creates actionable checklists for bulk
  remediation workflows.
---

# Batch Validator

## Purpose

Validate multiple interview question notes simultaneously:
- Validate all notes in a specific folder
- Validate by topic (all kotlin notes, all android notes)
- Group issues by severity (CRITICAL, ERROR, WARNING, NOTE)
- Generate aggregated statistics
- Create actionable fix checklists
- Support dry-run analysis mode

Extends `obsidian-validator` for bulk operations.

## When to Use

Activate this skill when user requests:
- "Validate all notes in [folder]"
- "Check all kotlin/android/etc. notes"
- "Batch validate [topic]"
- "Find all issues in 40-Android/"
- "Validate the entire vault"
- After bulk content creation
- Before committing multiple changes
- During periodic quality audits

## Prerequisites

Required context:
- Target folder path or topic name
- `00-Administration/Vault-Rules/TAXONOMY.md` for validation rules
- Understanding of folder-topic mapping

## Process

### Step 1: Determine Scope

Parse user request to identify target:

```
Input formats supported:
- Folder path: "40-Android/", "70-Kotlin/"
- Topic name: "kotlin", "android", "algorithms"
- Pattern: "all Q&A notes", "all hard questions"
- Full vault: "entire vault", "all notes"
```

Map input to file glob pattern:
- `40-Android/` → `InterviewQuestions/40-Android/q-*.md`
- `kotlin` → `InterviewQuestions/70-Kotlin/q-*.md`
- `all hard` → `InterviewQuestions/*/q-*--hard.md`
- `entire vault` → `InterviewQuestions/*/q-*.md`

### Step 2: Collect Files

Gather all matching files:

```
1. Run glob pattern to find files
2. Count total files to process
3. Report scope to user:
   "Found 358 Q&A notes in 70-Kotlin/ to validate"
4. Confirm if > 100 files (optional)
```

### Step 3: Validate Each File

For each file, run full validation (from obsidian-validator):

```
Validation Categories:
1. YAML Completeness (15 checks)
2. Topic Validation (6 checks)
3. Folder Placement (2 checks)
4. Content Structure (4 checks)
5. Link Requirements (3 checks)
6. Tag Requirements (4 checks)
7. FORBIDDEN Checks (8 checks)
8. Android-Specific (if applicable, 2 checks)
```

Track results:
- Files with no issues
- Files with warnings only
- Files with errors
- Files with critical issues

### Step 4: Aggregate Results

Compile validation results:

```
Statistics:
- Total files validated: X
- Passed (no issues): X (Y%)
- Passed with warnings: X (Y%)
- Failed (errors): X (Y%)
- Critical failures: X (Y%)

Issue Distribution:
- CRITICAL: X issues across Y files
- ERROR: X issues across Y files
- WARNING: X issues across Y files
- NOTE: X suggestions across Y files

Most Common Issues:
1. Missing related links (X files)
2. Status violations (X files)
3. Missing translations (X files)
```

### Step 5: Group Issues

Organize issues for efficient fixing:

```markdown
## Issues by Type

### Missing YAML Fields (12 files)
- q-example1.md: missing `language_tags`
- q-example2.md: missing `moc`, `related`
- ...

### Status Violations (5 files)
- q-reviewed-note.md: status='reviewed' (should be 'draft')
- ...

### Tag Issues (8 files)
- q-russian-tags.md: Russian in tags (found: корутины)
- ...

### Android Mirroring (15 files)
- q-compose.md: subtopics not mirrored to tags
- ...
```

### Step 6: Generate Fix Checklist

Create actionable checklist:

```markdown
## Fix Checklist

### CRITICAL (Must Fix) - 5 items
- [ ] Fix status violation in q-reviewed-note.md
- [ ] Remove Russian from tags in q-russian-tags.md
- [ ] Fix moc brackets in q-brackets.md
- ...

### ERROR (Should Fix) - 12 items
- [ ] Add language_tags to q-example1.md
- [ ] Add moc and related to q-example2.md
- ...

### WARNING (Recommended) - 23 items
- [ ] Add Follow-ups section to q-short.md
- [ ] Increase related links in q-isolated.md
- ...
```

### Step 7: Generate Report

Produce comprehensive batch validation report:

```markdown
# Batch Validation Report

**Scope**: 70-Kotlin/
**Files Validated**: 358
**Generated**: 2025-11-15 14:30

---

## Summary

| Result | Count | Percentage |
|--------|-------|------------|
| Passed | 312 | 87.2% |
| Warnings Only | 28 | 7.8% |
| Errors | 15 | 4.2% |
| Critical | 3 | 0.8% |

**Overall Status**: NEEDS ATTENTION

---

## Issue Statistics

| Severity | Issues | Files Affected |
|----------|--------|----------------|
| CRITICAL | 5 | 3 |
| ERROR | 23 | 15 |
| WARNING | 67 | 28 |
| NOTE | 45 | 31 |

---

## Most Common Issues

1. **Missing related links** (23 files)
   - Files have fewer than 2 related items
   - Fix: Add relevant cross-references

2. **Status violations** (5 files)
   - AI-created notes with status != draft
   - Fix: Change status to draft

3. **Short answer sections** (18 files)
   - Answer sections under 100 words
   - Fix: Expand content with details

---

## Issues by File

### CRITICAL Issues

**q-reviewed-wrongly--kotlin--medium.md**
- FORBIDDEN: status='reviewed' (must be 'draft' for AI notes)
- Action: Change to `status: draft`

**q-bad-tags--kotlin--easy.md**
- FORBIDDEN: Russian in tags (found: корутины, функции)
- Action: Replace with English equivalents

### ERROR Issues

**q-missing-fields--kotlin--hard.md**
- REQUIRED: Missing `language_tags` field
- REQUIRED: Missing `moc` field
- Action: Add required YAML fields

[... more files ...]

---

## Fix Checklist

### CRITICAL (3 files, 5 issues)
- [ ] q-reviewed-wrongly--kotlin--medium.md: Fix status
- [ ] q-bad-tags--kotlin--easy.md: Fix Russian tags
- [ ] q-brackets--kotlin--medium.md: Remove moc brackets

### ERROR (15 files, 23 issues)
- [ ] q-missing-fields--kotlin--hard.md: Add language_tags, moc
[... more items ...]

---

## Recommendations

1. **Immediate**: Fix 3 CRITICAL issues (blocks quality)
2. **Today**: Address 15 ERROR files (improves compliance)
3. **This Week**: Handle 28 WARNING files (enhances quality)

---

**Validation complete. Use checklist above to systematically fix issues.**
```

## Examples

### Example 1: Validate Folder

**User**: "Validate all notes in 40-Android/"

**Process**:
1. Find 527 Q&A notes in 40-Android/
2. Validate each file
3. Generate aggregated report

**Output**:
```markdown
# Batch Validation: 40-Android/

Files: 527 | Passed: 489 (92.8%) | Issues: 38 files

CRITICAL: 2 files (status violations)
ERROR: 12 files (missing fields)
WARNING: 24 files (short content)

Top Issue: Android subtopic mirroring (15 files)

[Full checklist follows...]
```

### Example 2: Validate by Topic

**User**: "Check all kotlin notes"

**Process**:
1. Map topic to folder: kotlin → 70-Kotlin/
2. Find 358 Q&A notes
3. Validate and aggregate

**Output**:
```markdown
# Batch Validation: kotlin (70-Kotlin/)

Files: 358 | Passed: 341 (95.3%) | Issues: 17 files

All checks passed for 95% of notes!

Issues found:
- 8 files missing Follow-ups section
- 5 files with weak related links
- 4 files with short answers

[Checklist follows...]
```

### Example 3: Full Vault Scan

**User**: "Validate entire vault"

**Process**:
1. Find all Q&A notes across all folders
2. Validate 972 files
3. Generate comprehensive report

**Output**:
```markdown
# Full Vault Validation

Total Files: 972 across 7 topics

| Topic | Files | Passed | Issues |
|-------|-------|--------|--------|
| android | 527 | 489 | 38 |
| kotlin | 358 | 341 | 17 |
| algorithms | 9 | 9 | 0 |
| system-design | 10 | 8 | 2 |
| backend | 9 | 9 | 0 |
| compsci | 56 | 52 | 4 |
| tools | 3 | 3 | 0 |

Overall: 911/972 passed (93.7%)

[Full breakdown and checklist follows...]
```

## Error Handling

### Too Many Files

**Problem**: User requests validation of 1000+ files

**Solution**:
1. Warn about processing time
2. Offer to validate in batches
3. Provide progress updates during scan
4. Generate partial reports if interrupted

### Mixed Results

**Problem**: Some files fail to parse

**Solution**:
1. Log parse failures separately
2. Continue validating other files
3. Report unparseable files in summary
4. Suggest manual review for failed files

### No Files Found

**Problem**: Glob pattern matches no files

**Solution**:
1. Report zero files found
2. Suggest alternative paths/patterns
3. List available folders for reference

## Dry-Run Mode

For previewing without detailed validation:

```
User: "Dry-run validate 70-Kotlin/"

Output:
Dry-run mode: Would validate 358 files in 70-Kotlin/

File types found:
- Q&A notes: 358
- Concept notes: 0
- MOC files: 0

Estimated time: ~30 seconds

Proceed with full validation? (yes/no)
```

## Integration with Other Skills

**Workflow: Post-Creation Validation**
1. Create notes with `obsidian-qna-creator`
2. Run `batch-validator` on folder
3. Fix issues using checklist
4. Re-validate to confirm fixes

**Workflow: Periodic Maintenance**
1. Run `vault-health-report` for overview
2. Use `batch-validator` on problem areas
3. Apply `bulk-normalizer` for YAML fixes
4. Use `link-fixer` for connectivity issues

**Workflow: Pre-Commit Check**
1. Before committing: `batch-validator` on changed files
2. Fix any CRITICAL/ERROR issues
3. Commit with confidence

## Performance Notes

- Validates ~50 files/second on typical hardware
- Full vault (1000 files) takes ~20 seconds
- Results cached for repeated queries
- Progress shown for large batches

## Notes

**Comprehensive**: Full validation rules applied to every file.

**Aggregated**: Issues grouped for efficient bulk fixing.

**Actionable**: Generates ready-to-use fix checklists.

**Scalable**: Handles vaults of any size with progress feedback.

**Non-destructive**: Read-only validation, no files modified.

---

**Version**: 1.0
**Last Updated**: 2025-01-05
**Status**: Production Ready
