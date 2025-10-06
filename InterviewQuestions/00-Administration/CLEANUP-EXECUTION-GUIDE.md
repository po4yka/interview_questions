# Cleanup Execution Guide

## Overview

This guide provides instructions for running the comprehensive cleanup of all 167 imported interview question files.

## Prepared Cleanup Scripts

Three cleanup scripts have been created in the root directory:

1. **`cleanup.js`** - Node.js version (RECOMMENDED)
2. **`batch_cleanup.py`** - Python 3 version
3. **`cleanup_script.py`** - Alternative Python 3 version

## How to Run

### Option 1: Node.js Script (Recommended)

```bash
cd /Users/npochaev/Documents/InterviewQuestions
node cleanup.js
```

**Requirements**: Node.js installed (built-in `fs` and `path` modules)

### Option 2: Python Script

```bash
cd /Users/npochaev/Documents/InterviewQuestions
python3 batch_cleanup.py
```

**Requirements**: Python 3.6+

### Option 3: Manual Python Script

```bash
cd /Users/npochaev/Documents/InterviewQuestions
python3 cleanup_script.py
```

## What Will Be Fixed

### 1. Redundant Difficulty Tags (CRITICAL)
- Removes: `easy_kotlin`, `medium_kotlin`, `hard_kotlin`
- Removes: `easy_android`, `medium_android`, `hard_android`
- These duplicate the `difficulty:` YAML field

### 2. Redundant Platform Tags
- Removes: `platform/android`, `platform/kotlin`, `platform/java`
- These duplicate the `topic:` field

### 3. Slash-Prefixed Tags
- Converts: `android/di-hilt` → `di-hilt`
- Converts: `kotlin/coroutines` → `coroutines`
- Removes redundant namespace prefixes

### 4. Code Block Language Tags
- Adds `kotlin` to Kotlin code blocks
- Adds `xml` to XML code blocks
- Adds `json` to JSON code blocks
- Adds `gradle` to Gradle code blocks

### 5. Whitespace Cleanup
- Removes trailing spaces at end of lines
- Normalizes multiple blank lines (max 2 consecutive)
- Ensures file ends with single newline

### 6. Tag Formatting
- Converts all tags to lowercase
- Replaces spaces with hyphens
- Removes duplicate tags
- Sorts tags alphabetically

## Expected Results

Based on initial analysis:

- **Android directory** (`40-Android/`): ~123 files need fixing
- **Kotlin directory** (`70-Kotlin/`): ~0 files need fixing (already clean!)
- **CompSci directory** (`60-CompSci/`): ~129 files need fixing

**Total**: Approximately 250+ fixes across all files

## Output

After running, you will see:

1. **Console output** with progress and statistics
2. **Cleanup report** generated at: `00-Administration/CLEANUP-REPORT.md`

## Sample Manual Fix

If you prefer to manually verify the approach, here's an example:

**Before** (`q-android-architectural-patterns--android--medium.md`):
```yaml
tags:
  - android
  - architecture-patterns
  - mvc
  - mvp
  - mvvm
  - clean-architecture
  - component-based
  - easy_kotlin                    # ← REMOVE (redundant difficulty tag)
  - android/architecture-patterns  # ← REMOVE (redundant slash tag)
difficulty: medium
```

**After**:
```yaml
tags:
  - android
  - architecture-patterns
  - clean-architecture
  - component-based
  - mvc
  - mvp
  - mvvm
difficulty: medium
```

## Files Already Fixed

The following files have been manually fixed as examples:

1. `/Users/npochaev/Documents/InterviewQuestions/40-Android/q-android-architectural-patterns--android--medium.md`
2. `/Users/npochaev/Documents/InterviewQuestions/60-CompSci/q-solid-principles--software-design--medium.md`

## Verification After Cleanup

Run these commands to verify all issues are fixed:

```bash
# Change to project directory
cd /Users/npochaev/Documents/InterviewQuestions

# Check for redundant difficulty tags (should return no results)
grep -r "easy_kotlin\|medium_android\|hard_android" 40-Android/ 70-Kotlin/ 60-CompSci/

# Check for platform tags (should return no results)
grep -r "platform/" 40-Android/ 70-Kotlin/ 60-CompSci/

# Check for slash tags (should return no results)
grep -r "android/\|kotlin/" 40-Android/ 70-Kotlin/ 60-CompSci/ | grep "tags:"

# Check for bare code blocks (should be minimal or none)
grep -n "^```$" 40-Android/*.md 70-Kotlin/*.md 60-CompSci/*.md | wc -l

# Check for trailing whitespace (should return no results)
grep -l " $" 40-Android/*.md 70-Kotlin/*.md 60-CompSci/*.md

# Count total files
find 40-Android 70-Kotlin 60-CompSci -name "*.md" | wc -l
```

## Troubleshooting

### Script Won't Run

**Node.js script**:
- Ensure Node.js is installed: `node --version`
- Check file permissions: `chmod +x cleanup.js`

**Python script**:
- Ensure Python 3 is installed: `python3 --version`
- Check file permissions: `chmod +x batch_cleanup.py`

### Script Errors

If you encounter errors:
1. Check that all directories exist
2. Ensure files are not open in other applications
3. Verify you have write permissions
4. Check file encodings (should be UTF-8)

## Rollback

Before running the cleanup, you may want to create a backup:

```bash
cd /Users/npochaev/Documents/InterviewQuestions
cp -r 40-Android 40-Android.backup
cp -r 70-Kotlin 70-Kotlin.backup
cp -r 60-CompSci 60-CompSci.backup
```

To rollback if needed:

```bash
rm -rf 40-Android 70-Kotlin 60-CompSci
mv 40-Android.backup 40-Android
mv 70-Kotlin.backup 70-Kotlin
mv 60-CompSci.backup 60-CompSci
```

## Next Steps After Cleanup

1. Review the generated `CLEANUP-REPORT.md`
2. Run verification commands to confirm all issues are fixed
3. Review a sample of modified files manually
4. Commit changes to version control if applicable
5. Delete backup directories if satisfied

## Support

If you encounter any issues, review the script logs and the generated report for details on what was modified.

---

*This guide was created as part of the comprehensive cleanup process for interview question files.*
