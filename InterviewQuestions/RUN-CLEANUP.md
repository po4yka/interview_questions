# Quick Start: Run Cleanup

## TL;DR

Run this command to clean up all 167 files:

```bash
node /Users/npochaev/Documents/InterviewQuestions/cleanup.js
```

**OR** if you prefer Python:

```bash
python3 /Users/npochaev/Documents/InterviewQuestions/batch_cleanup.py
```

## What It Does

Fixes these issues across all 167 imported question files:

1. ❌ Removes redundant tags: `easy_kotlin`, `medium_android`, `hard_android`, etc.
2. ❌ Removes platform tags: `platform/android`, `platform/kotlin`
3. ❌ Removes slash tags: `android/di-hilt` → `di-hilt`
4. ✅ Adds language to code blocks: ` ``` ` → ` ```kotlin `
5. ✅ Removes trailing whitespace
6. ✅ Normalizes blank lines
7. ✅ Sorts and formats tags

## Expected Results

- **~150 files** will be modified
- **~250+ redundant tags** removed
- **~50-100 code blocks** enhanced
- **All files** cleaned of whitespace issues

## Verification

After running, check that all issues are fixed:

```bash
# Should return no results:
grep -r "easy_kotlin\|medium_android\|hard_android" 40-Android/ 70-Kotlin/ 60-CompSci/
grep -r "platform/" 40-Android/ 70-Kotlin/ 60-CompSci/
grep -l " $" 40-Android/*.md 70-Kotlin/*.md 60-CompSci/*.md
```

## Report

A detailed report will be generated at:
`00-Administration/CLEANUP-REPORT.md`

## More Information

- **Detailed guide**: `00-Administration/CLEANUP-EXECUTION-GUIDE.md`
- **Full summary**: `00-Administration/CLEANUP-SUMMARY.md`

---

**Ready? Just run the command above!** ⬆️
