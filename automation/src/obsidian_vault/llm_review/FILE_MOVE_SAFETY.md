# Oscillation Fixer - File Move Safety

## Overview

The OscillationFixer can detect when files need to be moved to correct folders based on their `topic` field. However, automatic file moving is **disabled by default** for safety.

## Safety Features

### 1. **Opt-in File Moves** (Default: Disabled)
```python
# File moves DISABLED (default - safe)
graph = ReviewGraph(
    vault_root=vault_root,
    taxonomy=taxonomy,
    note_index=note_index,
    # allow_file_moves defaults to False
)

# File moves ENABLED (requires explicit opt-in)
graph = ReviewGraph(
    vault_root=vault_root,
    taxonomy=taxonomy,
    note_index=note_index,
    allow_file_moves=True,  # Explicit permission required
)
```

### 2. **Git-Aware Moves**
When file moves are enabled, the system uses `git mv` to preserve history:
- ✅ Git tracks the move as a rename (not delete + add)
- ✅ File history is preserved
- ✅ Git blame continues to work
- ✅ Merge conflicts are minimized
- ⚠️ Fallback to `Path.rename()` if `git mv` fails (not in a repo, etc.)

### 3. **Dry Run Mode**
Dry run mode prevents ALL file operations:
```python
graph = ReviewGraph(
    vault_root=vault_root,
    taxonomy=taxonomy,
    note_index=note_index,
    dry_run=True,  # No files written or moved
    allow_file_moves=True,  # Ignored when dry_run=True
)
```

### 4. **Logging and Audit Trail**
All file move attempts are logged:
```python
# When moves are disabled (default):
logger.warning("⚠ File should be moved: old/path.md -> new/path.md")
logger.warning("  File moves are disabled. To enable: ReviewGraph(allow_file_moves=True)")

# When moves are enabled:
logger.info("✓ Moved file via git: old/path.md -> new/path.md")
```

## Behavior Matrix

| `allow_file_moves` | `dry_run` | File Move Behavior |
|-------------------|-----------|-------------------|
| `False` (default) | `False`   | ❌ No move, log recommendation, require human review |
| `False` (default) | `True`    | ❌ No move, log recommendation |
| `True`            | `False`   | ✅ Move via `git mv` (or `rename()` fallback) |
| `True`            | `True`    | ❌ No move (dry run prevents all file ops) |

## When File Moves Happen

File moves are only triggered when:
1. ✅ Oscillation is detected (fixer reversing its own changes)
2. ✅ Issue is "File should be located in folder 'X' for topic 'Y'"
3. ✅ `allow_file_moves=True` is set
4. ✅ `dry_run=False`
5. ✅ OscillationFixer successfully validates the move

## Recommendations

### For Automated Workflows (CI/CD)
```python
# Safer: disable file moves, let humans handle location issues
graph = ReviewGraph(
    vault_root=vault_root,
    taxonomy=taxonomy,
    note_index=note_index,
    allow_file_moves=False,  # Default - safe
)
```

### For Interactive Use
```python
# Can enable if you want automation to fix location issues
graph = ReviewGraph(
    vault_root=vault_root,
    taxonomy=taxonomy,
    note_index=note_index,
    allow_file_moves=True,  # Opt-in to auto-moves
)
# Git will track the move properly via `git mv`
```

### For Testing/Development
```python
# Use dry run to preview what would happen
graph = ReviewGraph(
    vault_root=vault_root,
    taxonomy=taxonomy,
    note_index=note_index,
    dry_run=True,  # See what would happen, no changes made
    allow_file_moves=True,
)
```

## Error Handling

If `git mv` fails (e.g., file not in git, uncommitted changes), the system:
1. Logs the `git mv` error
2. Falls back to `Path.rename()`
3. Logs which method was used for the move
4. Continues the workflow

## Manual Move Alternative

If you prefer manual control:
1. Keep `allow_file_moves=False` (default)
2. Review the logs for file move recommendations
3. Manually move files using `git mv`:
   ```bash
   git mv old/path.md new/path.md
   git commit -m "Move file to correct folder"
   ```

## Security Considerations

- ✅ File moves are opt-in (not automatic by default)
- ✅ Uses `git mv` to preserve history
- ✅ All operations logged with full paths
- ✅ Dry run mode available for testing
- ✅ Creates target directories safely
- ⚠️ No backup is created (git history serves as backup)
- ⚠️ Moving large numbers of files may require review
