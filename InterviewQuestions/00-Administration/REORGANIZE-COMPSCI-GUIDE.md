# Reorganize 60-CompSci Questions — Execution Guide

## Purpose

This script moves misplaced questions from `60-CompSci` folder to their appropriate topic folders:
- **Kotlin questions** → `70-Kotlin` (topic: kotlin)
- **Android questions** → `40-Android` (topic: android)
- **Design patterns & architecture** → Stay in `60-CompSci`

## What Will Change

### Files to Move to 70-Kotlin (42 files)

Kotlin language features, coroutines, Flow, collections, etc.:
- All data class, sealed class, object keyword questions
- Coroutines, Flow, StateFlow questions
- Kotlin collections, generics, serialization
- Kotlin-specific features (lazy, extensions, etc.)

### Files to Move to 40-Android (29 files)

Android UI, Views, Compose, Fragments, etc.:
- Jetpack Compose questions
- RecyclerView, Fragments, Activities
- Android Views, Layouts, Navigation
- Android-specific APIs (PendingIntent, LayoutInflater, etc.)

### Files Staying in 60-CompSci

- All design pattern questions (Singleton, Factory, Observer, etc.)
- Architecture patterns (MVVM, MVI, MVP)
- OOP principles and SOLID principles
- General software design concepts

## What the Script Does

1. **Moves files** from `60-CompSci` to appropriate folders
2. **Updates `topic` field** in frontmatter:
   - Kotlin questions: `topic: kotlin`
   - Android questions: `topic: android`
3. **Adds topic to tags** if not already present
4. **Preserves all other metadata** and content

## How to Run

### Step 1: Review the Script

```bash
cat /Users/npochaev/Documents/InterviewQuestions/sources/reorganize_compsci.py
```

### Step 2: Make It Executable

```bash
chmod +x /Users/npochaev/Documents/InterviewQuestions/sources/reorganize_compsci.py
```

### Step 3: Run the Script

```bash
cd /Users/npochaev/Documents/InterviewQuestions
python3 sources/reorganize_compsci.py
```

### Step 4: Verify Results

Check the moved files:

```bash
# Check Kotlin folder
ls -la 70-Kotlin/ | grep "q-data-class"
ls -la 70-Kotlin/ | grep "q-coroutines"

# Check Android folder
ls -la 40-Android/ | grep "compose"
ls -la 40-Android/ | grep "recyclerview"

# Check what remains in CompSci
ls -la 60-CompSci/ | grep "pattern"
```

## Expected Output

```
=== Reorganizing 60-CompSci questions ===

Moving Kotlin questions to 70-Kotlin...
✓ Moved q-data-class-requirements--programming-languages--medium.md to 70-Kotlin
✓ Moved q-by-keyword-function-call--programming-languages--easy.md to 70-Kotlin
...
Moved 42 Kotlin questions

Moving Android questions to 40-Android...
✓ Moved q-kak-rabotaet-jetpackcompose--programming-languages--medium.md to 40-Android
✓ Moved q-zachem-nuzhen-diffutil--programming-languages--medium.md to 40-Android
...
Moved 29 Android questions

=== Summary ===
Total Kotlin questions moved: 42
Total Android questions moved: 29

✓ Reorganization complete!
```

## Verification Steps

### 1. Check File Counts

```bash
# Count questions in each folder
find 70-Kotlin -name "q-*.md" | wc -l
find 40-Android -name "q-*.md" | wc -l
find 60-CompSci -name "q-*.md" | wc -l
```

### 2. Verify Topic Fields

```bash
# Check Kotlin files have topic: kotlin
grep -r "^topic: kotlin" 70-Kotlin/q-data-class*.md

# Check Android files have topic: android
grep -r "^topic: android" 40-Android/q-kak-rabotaet-jetpackcompose*.md

# Check CompSci files have appropriate topics
grep -r "^topic:" 60-CompSci/q-singleton-pattern*.md
```

### 3. Check Dataview Queries

Open Obsidian and check that MOCs update correctly:
- `70-Kotlin/moc-kotlin.md` - Should show new Kotlin questions
- `40-Android/moc-android.md` - Should show new Android questions
- `60-CompSci/moc-architecture-patterns.md` - Should only show design/architecture patterns

## Rollback (If Needed)

If something goes wrong, you can restore from git:

```bash
# If in git repository
git checkout 60-CompSci/
git checkout 70-Kotlin/
git checkout 40-Android/

# Or manually move files back
# (Script keeps topic unchanged in source before moving, so you can reverse)
```

## Troubleshooting

### Error: "Source file not found"

- File might have been moved already
- Check if file exists in destination folder
- Script will list all missing files in errors section

### Error: Permission denied

```bash
# Make sure you have write permissions
chmod +w 60-CompSci/*.md
chmod +w 70-Kotlin/*.md
chmod +w 40-Android/*.md
```

### Wrong topic assigned

Edit the file manually to fix:

```yaml
---
topic: correct-topic  # Change this
---
```

## Notes

- **Backup recommended**: Consider backing up your vault before running
- **Git users**: Commit before running, makes rollback easy
- **Dataview**: MOC queries will update automatically after moving
- **Links**: Internal links remain valid (Obsidian uses filenames, not paths)

## After Running

1. ✅ Open Obsidian and let it reindex
2. ✅ Check MOCs update correctly with Dataview queries
3. ✅ Verify no broken links
4. ✅ Review a few moved files to ensure topic field updated
5. ✅ Commit changes if using git

---

**Created**: 2025-10-06
**Script**: `sources/reorganize_compsci.py`
