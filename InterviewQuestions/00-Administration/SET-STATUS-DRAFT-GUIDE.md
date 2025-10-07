# Set Status to Draft — Execution Guide

## Purpose

This script ensures all Q&A files in the vault have `status: draft` in their frontmatter.

## Background

- **Total Q&A files**: ~669 files
- **Files with status field**: ~120 files
- **Files needing update**: ~549 files

## What the Script Does

1. **Finds all Q&A files** (files starting with `q-*.md`) in topic folders
2. **Adds `status: draft`** if the field is missing
3. **Updates existing status** to `draft` if it's set to something else
4. **Preserves all other content** and frontmatter fields
5. **Skips files** without proper YAML frontmatter

## Affected Folders

- `20-Algorithms`
- `30-System-Design`
- `40-Android`
- `50-Backend`
- `50-Behavioral`
- `60-CompSci`
- `70-Kotlin`
- `80-Tools`

## How to Run

### Step 1: Review the Script

```bash
cat /Users/npochaev/Documents/InterviewQuestions/sources/set_status_draft.py
```

### Step 2: Make It Executable

```bash
chmod +x /Users/npochaev/Documents/InterviewQuestions/sources/set_status_draft.py
```

### Step 3: Run the Script

```bash
cd /Users/npochaev/Documents/InterviewQuestions
python3 sources/set_status_draft.py
```

## Expected Output

```
=== Setting status: draft for all Q&A files ===

Processing 20-Algorithms...
  ✓ Added status to q-two-sum--algorithms--easy.md

Processing 40-Android...
  ✓ Added status to q-viewmodel-lifecycle--android--medium.md
  ✓ Added status to q-compose-recomposition--android--hard.md
  ...

Processing 70-Kotlin...
  ✓ Added status to q-coroutine-context--kotlin--medium.md
  ✓ Updated status in q-flow-operators--kotlin--hard.md
  ...

=== Summary ===
Status added:     549
Status updated:   0
Already draft:    120
Skipped:          0
Total processed:  669

✓ All Q&A files now have status: draft
```

## What Changes in Files

### Before (Missing Status)

```yaml
---
id: example-123
title: What is ViewModel / Что такое ViewModel
topic: android
difficulty: medium
tags:
  - android
  - architecture
---
```

### After (Status Added)

```yaml
---
id: example-123
title: What is ViewModel / Что такое ViewModel
topic: android
difficulty: medium
status: draft
tags:
  - android
  - architecture
---
```

### Before (Different Status)

```yaml
---
status: reviewed
title: Example Question
---
```

### After (Status Updated)

```yaml
---
status: draft
title: Example Question
---
```

## Verification Steps

### 1. Check Total Files with Status

```bash
# Should return 669 (all Q&A files)
grep -l "^status:" /Users/npochaev/Documents/InterviewQuestions/*/q-*.md | wc -l
```

### 2. Check All Have Draft Status

```bash
# Should return 669
grep -l "^status: draft" /Users/npochaev/Documents/InterviewQuestions/*/q-*.md | wc -l
```

### 3. Find Any Non-Draft Status

```bash
# Should return nothing
find /Users/npochaev/Documents/InterviewQuestions -name "q-*.md" -exec grep "^status:" {} + | grep -v "status: draft"
```

### 4. Check Sample Files

```bash
# Check a few random files
head -20 /Users/npochaev/Documents/InterviewQuestions/70-Kotlin/q-coroutine-context--kotlin--medium.md
head -20 /Users/npochaev/Documents/InterviewQuestions/40-Android/q-compose-state--android--easy.md
```

## Rollback (If Needed)

If you need to undo changes:

```bash
# If using git
git checkout 20-Algorithms/
git checkout 40-Android/
git checkout 60-CompSci/
git checkout 70-Kotlin/
# ... etc for all folders

# Or restore from backup if created
```

## Troubleshooting

### Error: "No frontmatter"

Some files might not have proper YAML frontmatter. These will be skipped and reported.

**To fix manually**:
1. Find the file
2. Add frontmatter at the top:
```yaml
---
status: draft
---
```

### Error: "Malformed frontmatter"

File has `---` but frontmatter is not properly structured.

**To fix**: Review the file and ensure frontmatter has opening and closing `---`

### Files Still Missing Status

Check if files are in folders not included in the script:

```bash
# Find Q&A files outside standard folders
find /Users/npochaev/Documents/InterviewQuestions -name "q-*.md" -type f | grep -v -E "(20-Algorithms|30-System-Design|40-Android|50-Backend|50-Behavioral|60-CompSci|70-Kotlin|80-Tools)"
```

## Status Field Purpose

The `status` field tracks the review lifecycle of questions:

- **`draft`** — Initial state, needs review
- **`reviewed`** — Content has been reviewed for accuracy
- **`ready`** — Ready for interview prep use
- **`retired`** — Deprecated/archived content

## After Running

1. ✅ Verify all Q&A files have `status: draft`
2. ✅ Check a few files manually to ensure content preserved
3. ✅ Open Obsidian and verify notes display correctly
4. ✅ Commit changes if using git
5. ✅ Begin review process to promote files from `draft` to `reviewed`

## Next Steps

After setting all files to `draft`, you can:

1. **Review questions systematically** and update status to `reviewed`
2. **Use Dataview to track review progress**:
   ```dataview
   TABLE status
   FROM "40-Android" OR "70-Kotlin"
   WHERE startswith(file.name, "q-")
   GROUP BY status
   ```
3. **Create review workflow** to gradually promote questions through stages

---

**Created**: 2025-10-06
**Script**: `sources/set_status_draft.py`
**Estimated files to update**: ~549 files
