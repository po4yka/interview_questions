---
name: link-fixer
description: >
  Bulk fix link-related issues across the vault. Finds and repairs orphaned notes,
  adds missing related links based on topic/subtopic similarity, removes broken links,
  updates MOC references, and suggests bidirectional links. Essential for maintaining
  healthy knowledge graph connectivity.
---

# Link Fixer

## Purpose

Repair and enhance link connectivity across the vault:

1. **Orphan Detection**: Find notes with no incoming links
2. **Orphan Repair**: Add links to connect orphaned notes
3. **Broken Link Repair**: Fix or remove links to non-existent files
4. **Related Links**: Add missing `related` field entries based on similarity
5. **Bidirectional Links**: Ensure links go both ways
6. **MOC Integration**: Connect notes to appropriate MOCs

## When to Use

Activate this skill when user requests:
- "Fix orphaned notes"
- "Find broken links"
- "Add missing related links"
- "Improve link connectivity"
- "Connect isolated notes"
- "Fix links in [folder]"
- During vault maintenance
- After bulk content imports

## Prerequisites

Required context:
- Access to full vault for link analysis
- Understanding of topic relationships
- MOC structure knowledge

## Process

### Step 1: Build Link Graph

Analyze all wiki-links in vault:

```
1. Scan all markdown files
2. Extract wiki-links from:
   - Content: [[note-name]]
   - YAML related: [note1, note2]
   - YAML moc: moc-name

3. Build graph:
   - Nodes: All markdown files
   - Edges: Links between files
   - Direction: Source → Target
```

### Step 2: Identify Orphans

Find notes with no incoming links:

```
Orphan criteria:
- Zero incoming wiki-links from content
- Not referenced in any related field
- Exclude MOCs and index files
- Exclude templates and admin docs

Report orphan statistics:
- Total orphans found
- Orphans by topic/folder
- Age of orphans (oldest first)
```

### Step 3: Find Broken Links

Detect links to non-existent files:

```
For each wiki-link [[target]]:
1. Resolve target file path
2. Check if file exists
3. If not found:
   - Record broken link
   - Note source file and line
   - Suggest possible corrections
```

### Step 4: Analyze Connectivity

Assess link health metrics:

```
Metrics:
- Average links per note
- Notes with < 2 related links
- Isolated clusters (disconnected subgraphs)
- Most connected notes (hubs)
- Least connected notes
```

### Step 5: Generate Fix Suggestions

For orphans, suggest connections based on:

```
Similarity factors:
1. Same topic (highest weight)
2. Shared subtopics
3. Same difficulty level
4. Related concepts
5. Title/content similarity

Suggestion format:
Orphan: q-coroutine-scope--kotlin--medium.md
Suggested links:
  - q-coroutine-context--kotlin--medium.md (same topic, same difficulty)
  - q-structured-concurrency--kotlin--hard.md (shared subtopics)
  - c-coroutines.md (related concept)
```

### Step 6: Apply Fixes

Repair options:

```
1. Add to related field:
   related: [existing1, suggested1, suggested2]

2. Add to content Related Questions section:
   ## Related Questions
   - [[suggested1]]
   - [[suggested2]]

3. Update MOC if missing:
   moc: moc-kotlin

4. Remove broken links:
   - Delete from related array
   - Comment out or remove from content
```

### Step 7: Generate Report

Produce link health report:

```markdown
# Link Fixer Report

**Scope**: Full Vault
**Generated**: 2025-11-15

---

## Summary

| Metric | Count | Status |
|--------|-------|--------|
| Total Notes | 972 | - |
| Orphaned Notes | 15 | NEEDS FIX |
| Broken Links | 8 | NEEDS FIX |
| Weak Connectivity | 45 | WARNING |

---

## Orphaned Notes (15)

Notes with no incoming links:

| File | Topic | Age | Suggested Links |
|------|-------|-----|-----------------|
| q-new-feature--kotlin--hard.md | kotlin | 3 days | q-related1, q-related2 |
| q-old-note--android--easy.md | android | 30 days | q-similar, c-concept |
| ... | ... | ... | ... |

### Fix Recommendations

1. **q-new-feature--kotlin--hard.md**
   - Add to related in q-coroutine-basics--kotlin--easy.md
   - Add to moc-kotlin.md study path
   - Link from c-coroutines.md

[... more recommendations ...]

---

## Broken Links (8)

| Source File | Broken Link | Suggestion |
|-------------|-------------|------------|
| q-example--kotlin--medium.md | [[c-missing-concept]] | Remove or create c-missing-concept.md |
| q-test--android--easy.md | [[old-note-deleted]] | Remove link |
| ... | ... | ... |

---

## Weak Connectivity (45)

Notes with fewer than 2 related links:

| File | Current Links | Suggested Additions |
|------|---------------|---------------------|
| q-basics--kotlin--easy.md | 1 | q-intro, c-kotlin |
| ... | ... | ... |

---

## Fix Actions

### Automatic Fixes Available
- [ ] Add 15 orphans to related fields (32 links)
- [ ] Remove 8 broken links
- [ ] Add 67 related links to weak notes

### Manual Review Required
- 3 orphans with no clear connections
- 2 broken links might need file creation

---

## Apply Fixes?

Run with `--fix` to apply automatic fixes.
Run with `--preview` to see detailed changes.
```

## Examples

### Example 1: Fix All Orphans

**User**: "Fix all orphaned notes"

**Process**:
1. Build link graph
2. Find 15 orphans
3. Generate suggestions for each
4. Apply fixes

**Output**:
```markdown
# Orphan Fix Results

Found: 15 orphaned notes
Fixed: 12 notes
Manual review needed: 3 notes

## Fixes Applied

| Orphan | Added To |
|--------|----------|
| q-flow-operators--kotlin--hard.md | q-flow-basics--kotlin--medium.md, moc-kotlin.md |
| q-room-migrations--android--hard.md | q-room-basics--android--easy.md, c-room.md |
| ... | ... |

## Needs Manual Review

- q-obscure-topic--kotlin--hard.md (no similar notes found)
- q-deprecated-api--android--easy.md (topic may be outdated)
- q-edge-case--algorithms--hard.md (unique topic)

These notes may need content review or deletion.
```

### Example 2: Fix Broken Links

**User**: "Find and fix broken links"

**Process**:
1. Scan all wiki-links
2. Verify each target exists
3. Report and fix

**Output**:
```markdown
# Broken Link Report

Found: 8 broken links in 6 files

## Broken Links

| File | Link | Action |
|------|------|--------|
| q-old--kotlin--easy.md | [[c-deleted-concept]] | Removed |
| q-test--android--medium.md | [[typo-in-name]] | Fixed to [[correct-name]] |
| ... | ... | ... |

## Summary
- Removed: 5 broken links
- Corrected: 2 typos
- Needs creation: 1 (c-new-concept.md suggested)

All fixable broken links resolved.
```

### Example 3: Improve Connectivity

**User**: "Add related links to weakly connected notes"

**Process**:
1. Find notes with < 2 related links
2. Suggest connections
3. Apply additions

**Output**:
```markdown
# Connectivity Improvement

Notes with weak connectivity: 45
Links added: 89

## Before/After

| File | Before | After |
|------|--------|-------|
| q-basics--kotlin--easy.md | 1 link | 3 links |
| q-intro--android--easy.md | 0 links | 2 links |
| ... | ... | ... |

Average connectivity improved from 1.8 to 3.2 links per note.
```

### Example 4: Fix Links in Folder

**User**: "Fix links in 70-Kotlin/"

**Process**:
1. Analyze only 70-Kotlin/ files
2. Fix orphans, broken links, weak connectivity
3. Report folder-specific results

**Output**:
```markdown
# Link Fix: 70-Kotlin/

Files analyzed: 358

## Results
- Orphans fixed: 5
- Broken links removed: 2
- Related links added: 34

## Changes Applied
[Detailed list of changes...]

Kotlin folder link health improved by 23%.
```

## Error Handling

### Circular Link Detection

**Problem**: Adding link would create circular reference

**Solution**:
1. Detect potential circles before adding
2. Skip links that would create tight loops
3. Report skipped suggestions

### Ambiguous Link Targets

**Problem**: Multiple files could match [[partial-name]]

**Solution**:
1. Use full filename for disambiguation
2. Report ambiguous links for manual review
3. Suggest specific full paths

### Large Vault Performance

**Problem**: Link analysis slow on 1000+ files

**Solution**:
1. Cache link graph
2. Incremental updates
3. Progress indicators
4. Option to analyze subsets

## Fix Modes

### Check Only (Default)
```
Report issues without modifying files.
```

### Preview Mode
```
Show exactly what changes would be made.
Allows review before applying.
```

### Auto-Fix Mode
```
Apply safe automatic fixes:
- Add missing related links
- Remove clearly broken links
- Update MOC references
```

### Interactive Mode
```
Prompt for confirmation on each fix.
Best for careful review.
```

## Integration with Other Skills

**Workflow: New Content Integration**
1. Create notes with `obsidian-qna-creator`
2. Run `link-fixer` to connect new notes
3. Verify with `obsidian-validator`

**Workflow: Vault Maintenance**
1. Run `vault-health-report` for overview
2. Use `link-fixer` for connectivity issues
3. Run `batch-validator` for other issues

**Workflow: Content Reorganization**
1. Move/rename files
2. Run `link-fixer` to repair broken links
3. Update MOC references

## Link Suggestion Algorithm

```
Score calculation for link suggestions:

same_topic: +5 points
shared_subtopic: +3 points per subtopic
same_difficulty: +2 points
related_concept: +4 points
title_similarity > 0.5: +2 points
already_linked_to_common: +1 point

Threshold for suggestion: 5+ points
Maximum suggestions per orphan: 5
```

## Notes

**Non-Destructive Default**: Check-only mode reports without changes.

**Smart Suggestions**: Uses multiple factors for relevant link suggestions.

**Bidirectional**: Ensures links work both ways where appropriate.

**Incremental**: Can fix specific folders or full vault.

**Reversible**: All changes can be manually undone if needed.

---

**Version**: 1.0
**Last Updated**: 2025-01-05
**Status**: Production Ready
