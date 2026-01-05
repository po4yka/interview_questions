---
name: android-enforcer
description: >
  Validate and auto-fix Android-specific vault rules. Checks subtopic-to-tag mirroring,
  validates subtopics against ANDROID-SUBTOPICS.md controlled list, auto-adds missing
  android/* tags, and generates Android-specific compliance reports. Essential for
  maintaining Android note quality.
---

# Android Enforcer

## Purpose

Enforce Android-specific rules that apply to notes with `topic: android`:

1. **Subtopic Validation**: Ensure all subtopics are from the controlled Android subtopics list
2. **Tag Mirroring**: Verify each subtopic is mirrored in tags as `android/<subtopic>`
3. **Auto-Fix**: Automatically add missing `android/*` tags
4. **Compliance Report**: Generate Android-specific validation report

Android notes have stricter requirements than other topics due to the platform's complexity.

## When to Use

Activate this skill when user requests:
- "Check Android notes"
- "Fix Android tag mirroring"
- "Validate Android subtopics"
- "Enforce Android rules on [file]"
- "Add missing Android tags"
- After creating Android Q&A notes
- During Android content audits

## Prerequisites

Required context:
- Target file(s) in `40-Android/` folder
- `00-Administration/Vault-Rules/TAXONOMY.md` for valid Android subtopics
- Understanding of Android subtopic categories

## Android-Specific Rules

### Rule 1: Valid Android Subtopics

All subtopics must be from the controlled list:

```yaml
# UI Subtopics
ui-compose, ui-views, ui-navigation, ui-state, ui-animation,
ui-accessibility, ui-theming, ui-custom-views

# Architecture Subtopics
architecture-mvvm, architecture-mvi, architecture-clean,
architecture-modular, di-hilt, di-dagger, di-koin

# Lifecycle Subtopics
lifecycle, activity, fragment, service, broadcast-receiver,
content-provider, workmanager, foreground-service

# Data Subtopics
room, datastore, files-media, shared-prefs, sqlite,
content-resolver, encryption

# Networking Subtopics
networking-http, networking-retrofit, networking-graphql,
networking-websocket, networking-grpc

# Concurrency Subtopics
coroutines, flow, threads-sync, rxjava, executors

# Testing Subtopics
testing-unit, testing-instrumented, testing-ui,
testing-robolectric, testing-espresso, testing-compose

# Build Subtopics
gradle, build-variants, dependency-management,
proguard-r8, app-bundle, signing

# Performance Subtopics
performance-memory, performance-battery, performance-startup,
performance-rendering, profiling

# Platform Subtopics
notifications, permissions, deep-links, app-widgets,
wear-os, auto, tv
```

### Rule 2: Subtopic-to-Tag Mirroring

**REQUIRED**: Every subtopic must be mirrored to tags with `android/` prefix.

```yaml
# CORRECT
subtopics: [ui-compose, lifecycle, coroutines]
tags: [
  android/ui-compose,    # Mirrors ui-compose
  android/lifecycle,     # Mirrors lifecycle
  android/coroutines,    # Mirrors coroutines
  compose,               # Optional additional tag
  difficulty/medium
]

# WRONG - Missing mirrored tags
subtopics: [ui-compose, lifecycle, coroutines]
tags: [compose, jetpack, difficulty/medium]  # FORBIDDEN: No android/* tags
```

### Rule 3: Tag Format

Android mirrored tags must follow exact format:
- Lowercase
- Prefix: `android/`
- Exact subtopic name (no abbreviations)

```yaml
# CORRECT
android/ui-compose
android/architecture-mvvm
android/testing-unit

# WRONG
Android/ui-compose     # Wrong case
android/compose        # Not full subtopic name
android/ui_compose     # Underscore instead of hyphen
```

## Process

### Step 1: Identify Target Files

Determine scope of enforcement:

```
Options:
- Single file: "40-Android/q-example--android--medium.md"
- All Android notes: "40-Android/*.md"
- Specific subtopic: "all ui-compose notes"
```

### Step 2: Validate Subtopics

For each file, check subtopics against controlled list:

```python
# Pseudocode
valid_subtopics = load_android_subtopics()  # From TAXONOMY.md

for subtopic in note.subtopics:
    if subtopic not in valid_subtopics:
        report_invalid_subtopic(subtopic)
        suggest_closest_match(subtopic)
```

### Step 3: Check Tag Mirroring

Verify each subtopic has corresponding tag:

```python
# Pseudocode
for subtopic in note.subtopics:
    expected_tag = f"android/{subtopic}"
    if expected_tag not in note.tags:
        missing_tags.append(expected_tag)
```

### Step 4: Auto-Fix (if requested)

Add missing mirrored tags:

```yaml
# Before
subtopics: [ui-compose, lifecycle]
tags: [compose, jetpack, difficulty/medium]

# After auto-fix
subtopics: [ui-compose, lifecycle]
tags: [android/ui-compose, android/lifecycle, compose, jetpack, difficulty/medium]
```

### Step 5: Generate Report

Produce Android-specific compliance report:

```markdown
# Android Enforcement Report

**File**: q-compose-state--android--medium.md
**Status**: NEEDS FIXES

---

## Subtopic Validation

| Subtopic | Valid | Notes |
|----------|-------|-------|
| ui-compose | YES | - |
| lifecycle | YES | - |
| ui-state | YES | - |

All subtopics valid.

---

## Tag Mirroring

| Subtopic | Expected Tag | Present |
|----------|--------------|---------|
| ui-compose | android/ui-compose | NO |
| lifecycle | android/lifecycle | NO |
| ui-state | android/ui-state | YES |

**Missing Tags**: 2

---

## Fix Required

Add the following tags:
```yaml
tags: [android/ui-compose, android/lifecycle, ...]
```

---

## Auto-Fix Available

Run with `--fix` to automatically add missing tags.
```

## Examples

### Example 1: Check Single File

**User**: "Check Android rules on q-compose-state--android--medium.md"

**Process**:
1. Read file YAML
2. Validate subtopics
3. Check tag mirroring
4. Report findings

**Output**:
```markdown
# Android Enforcement: q-compose-state--android--medium.md

## Subtopics: VALID
- ui-compose
- lifecycle
- ui-state

## Tag Mirroring: 1 ISSUE
- Missing: android/ui-compose
- Missing: android/lifecycle
- Present: android/ui-state

## Recommendation
Add missing tags to YAML:
- android/ui-compose
- android/lifecycle
```

### Example 2: Fix All Android Notes

**User**: "Fix Android tag mirroring in all notes"

**Process**:
1. Find all files in 40-Android/
2. Check each for mirroring issues
3. Auto-fix missing tags
4. Report summary

**Output**:
```markdown
# Android Enforcement: Batch Fix

Files scanned: 527
Files with issues: 23
Files fixed: 23

## Fixes Applied

| File | Tags Added |
|------|------------|
| q-compose-state--android--medium.md | android/ui-compose, android/lifecycle |
| q-room-basics--android--easy.md | android/room |
| q-hilt-injection--android--hard.md | android/di-hilt |
| ... | ... |

Total tags added: 45

All Android notes now compliant with tag mirroring rules.
```

### Example 3: Validate Subtopics Only

**User**: "Check if Android subtopics are valid"

**Process**:
1. Scan all Android notes
2. Extract subtopics
3. Validate against controlled list
4. Report invalid subtopics

**Output**:
```markdown
# Subtopic Validation Report

Files scanned: 527
Unique subtopics found: 34

## Valid Subtopics (32)
ui-compose, ui-views, lifecycle, activity, fragment, room,
coroutines, flow, testing-unit, architecture-mvvm, ...

## Invalid Subtopics (2)
| Subtopic | Files | Suggestion |
|----------|-------|------------|
| compose-ui | 3 | Use: ui-compose |
| unit-testing | 2 | Use: testing-unit |

## Files to Fix
- q-compose-basics--android--easy.md: compose-ui → ui-compose
- q-testing-intro--android--easy.md: unit-testing → testing-unit
- ...
```

### Example 4: Preview Without Fixing

**User**: "Preview Android fixes without applying"

**Process**:
1. Scan for issues
2. Generate fix preview
3. Do not modify files

**Output**:
```markdown
# Android Fix Preview (Dry Run)

Would fix 23 files with 45 tag additions.

Preview of changes:

## q-compose-state--android--medium.md
Current tags: [compose, jetpack, ui-state, difficulty/medium]
Would add: [android/ui-compose, android/lifecycle]
Result: [android/ui-compose, android/lifecycle, compose, jetpack, ui-state, difficulty/medium]

## q-room-basics--android--easy.md
Current tags: [room, database, difficulty/easy]
Would add: [android/room]
Result: [android/room, room, database, difficulty/easy]

[... more previews ...]

Run with --fix to apply these changes.
```

## Error Handling

### Invalid Subtopic Found

**Problem**: Note contains subtopic not in controlled list

**Solution**:
1. Report the invalid subtopic
2. Search for closest valid match using string similarity
3. Suggest replacement
4. Option to auto-fix if match confidence is high

```
Invalid subtopic: "compose-ui"
Closest match: "ui-compose" (92% similarity)
Suggestion: Replace "compose-ui" with "ui-compose"
```

### Non-Android File

**Problem**: File is not in 40-Android/ or topic != android

**Solution**:
1. Report that file is not an Android note
2. Android rules only apply to Android notes
3. Suggest using regular validator instead

### Partial Fix

**Problem**: Some fixes applied, others failed

**Solution**:
1. Report successful fixes
2. List failed fixes with reasons
3. Provide manual fix instructions for failures

## Integration with Other Skills

**Workflow: Android Note Creation**
1. Create with `obsidian-qna-creator` (topic: android)
2. Run `android-enforcer` to verify/fix tags
3. Use `obsidian-validator` for full validation

**Workflow: Android Audit**
1. Run `vault-health-report` for overview
2. Run `android-enforcer` for Android-specific issues
3. Use `batch-validator` for remaining issues

**Workflow: Bulk Android Import**
1. Import Android notes
2. Run `android-enforcer --fix` to add mirrored tags
3. Run `batch-validator` on 40-Android/
4. Fix remaining issues

## Configuration

### Controlled Subtopics Source

Default: `00-Administration/Vault-Rules/TAXONOMY.md`

Fallback: Built-in list of common Android subtopics

### Fix Behavior

- `--check`: Validation only, no modifications (default)
- `--fix`: Automatically add missing tags
- `--preview`: Show what would be fixed without applying

### Tag Ordering

When adding tags, place `android/*` tags first:
```yaml
tags: [android/ui-compose, android/lifecycle, compose, jetpack, difficulty/medium]
```

## Notes

**Android-Specific**: Only applies to notes with `topic: android`.

**Non-Destructive Check**: Default mode only reports issues.

**Safe Auto-Fix**: Fix mode only adds missing tags, never removes existing.

**Comprehensive**: Validates both subtopic values and tag mirroring.

**Up-to-date**: Uses TAXONOMY.md as source of truth for valid subtopics.

---

**Version**: 1.0
**Last Updated**: 2025-01-05
**Status**: Production Ready
