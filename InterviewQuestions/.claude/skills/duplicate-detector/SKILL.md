---
name: duplicate-detector
description: >
  Find duplicate or near-duplicate questions in the vault. Detects exact title
  duplicates, semantically similar questions, and overlapping content. Suggests
  merge candidates and generates deduplication reports. Helps maintain vault
  quality by preventing redundant content.
---

# Duplicate Detector

## Purpose

Find and manage duplicate content in the vault:

1. **Exact Duplicates**: Files with identical titles
2. **Near-Duplicates**: Semantically similar questions
3. **Content Overlap**: Questions covering same material
4. **Merge Suggestions**: Recommend which to keep/merge
5. **Deduplication Report**: Generate cleanup checklist

## When to Use

Activate this skill when user requests:
- "Find duplicate questions"
- "Check for similar notes"
- "Detect redundant content"
- "Are there duplicates in [topic]?"
- "Deduplicate the vault"
- After bulk content imports
- During quarterly vault audits

## Prerequisites

Required context:
- Access to vault files
- Understanding of question semantics
- Topic and subtopic information

## Process

### Step 1: Extract Question Data

For each Q&A note:

```
Collect:
- Title (both EN and RU)
- Question content (EN and RU)
- Topic and subtopics
- Difficulty level
- Key terms and concepts
- File path
```

### Step 2: Exact Duplicate Detection

Find files with identical titles:

```
Check for:
- Exact title match (case-insensitive)
- Same filename (shouldn't happen but check)
- Identical aliases

Example:
File A: "What is a coroutine?"
File B: "What is a Coroutine?"
→ EXACT DUPLICATE
```

### Step 3: Near-Duplicate Detection

Find semantically similar questions:

```
Similarity factors:
1. Title similarity (fuzzy match)
2. Question text overlap
3. Same topic + subtopics
4. Same difficulty
5. Shared key terms

Similarity score: 0-100%
- 90%+: Very likely duplicate
- 70-89%: Possible duplicate, review
- 50-69%: Related but distinct
- <50%: Different questions
```

### Step 4: Content Overlap Analysis

Check for questions covering same material:

```
Overlap indicators:
- Same concepts explained
- Similar code examples
- Answering same interview question differently
- One is subset of another

Categories:
- IDENTICAL: Same question, same answer
- SUBSET: One answer contained in another
- VARIANT: Same question, different angles
- RELATED: Similar topic, different focus
```

### Step 5: Generate Merge Recommendations

For each duplicate group:

```
Recommendation factors:
- Which has more complete answer?
- Which has better translations?
- Which has more related links?
- Which is older (established)?
- Which follows naming convention better?

Actions:
- KEEP: Designate primary file
- MERGE: Combine content from both
- DELETE: Remove redundant file
- REVIEW: Human decision needed
```

### Step 6: Generate Report

Produce deduplication report:

```markdown
# Duplicate Detection Report

**Generated**: 2025-11-15
**Files Scanned**: 972
**Duplicates Found**: 23

---

## Summary

| Type | Count | Action Needed |
|------|-------|---------------|
| Exact Duplicates | 3 | Delete/Merge |
| Near-Duplicates | 12 | Review |
| Content Overlap | 8 | Consolidate |

---

## Exact Duplicates (3 pairs)

### Pair 1
**Files**:
- `q-coroutine-basics--kotlin--easy.md` (created 2025-09-01)
- `q-what-is-coroutine--kotlin--easy.md` (created 2025-10-15)

**Similarity**: 100% (identical titles)

**Recommendation**: MERGE
- Keep: `q-coroutine-basics--kotlin--easy.md` (older, more links)
- Merge content from: `q-what-is-coroutine--kotlin--easy.md`
- Delete after merge

### Pair 2
[... more pairs ...]

---

## Near-Duplicates (12 pairs)

### Pair 1: 87% Similar
**Files**:
- `q-flow-basics--kotlin--medium.md`
- `q-kotlin-flow-introduction--kotlin--easy.md`

**Similarity Analysis**:
- Title: 72% similar
- Content: 91% overlap
- Same subtopics: flow, coroutines

**Recommendation**: REVIEW
- Questions similar but different difficulty
- Consider: Is easy version needed alongside medium?
- Option 1: Keep both (valid progression)
- Option 2: Merge into comprehensive note

### Pair 2: 78% Similar
[... more pairs ...]

---

## Content Overlap (8 groups)

### Group 1: Activity Lifecycle
**Files covering same topic**:
- `q-activity-lifecycle--android--medium.md`
- `q-activity-lifecycle-methods--android--easy.md`
- `q-lifecycle-callbacks--android--medium.md`

**Analysis**:
- All cover Activity lifecycle
- Different difficulty levels
- Significant answer overlap

**Recommendation**: CONSOLIDATE
- Keep all three but differentiate clearly
- Easy: Basic callbacks only
- Medium 1: Deep dive into each callback
- Medium 2: Lifecycle with configuration changes

### Group 2: [...]

---

## Deduplication Checklist

### Must Do (Exact Duplicates)
- [ ] Merge q-coroutine-basics and q-what-is-coroutine
- [ ] Delete q-duplicate-file-2.md
- [ ] Merge q-room-basics pair

### Should Review (Near-Duplicates)
- [ ] Review flow basics pair - decide keep/merge
- [ ] Check if both ViewModel notes needed
- [ ] Review Compose state pair

### Consider (Overlap)
- [ ] Differentiate lifecycle group clearly
- [ ] Consider merging Room query notes
- [ ] Review coroutine exception handlers group

---

## Unique Questions Verified

969 questions confirmed unique (no duplicates).

---

**Run with --auto-merge for safe automatic merges.**
**Run with --interactive for guided deduplication.**
```

## Examples

### Example 1: Full Vault Scan

**User**: "Find all duplicate questions"

**Output**:
```markdown
# Duplicate Scan Results

Files: 972
Duplicates found: 23

## Summary
- 3 exact duplicates (must fix)
- 12 near-duplicates (should review)
- 8 content overlaps (consider)

## Top Priority
1. q-coroutine-basics / q-what-is-coroutine (100% match)
2. q-flow-basics / q-flow-introduction (87% match)
3. q-room-basics / q-room-database-intro (82% match)

Use --details for full report.
```

### Example 2: Topic-Specific Check

**User**: "Check for duplicates in Kotlin notes"

**Output**:
```markdown
# Duplicate Check: kotlin (70-Kotlin/)

Files: 358
Duplicates: 8

## Found

### Exact (1)
- q-coroutine-basics / q-what-is-coroutine

### Near-Duplicate (5)
- q-flow-basics / q-flow-introduction (87%)
- q-suspend-function / q-suspending-functions (79%)
- q-sealed-classes / q-kotlin-sealed-class (75%)
- q-data-class / q-kotlin-data-classes (73%)
- q-extensions / q-extension-functions (71%)

### Overlap (2)
- Collection operators group (3 files)
- Coroutine exception group (2 files)
```

### Example 3: Interactive Deduplication

**User**: "Help me deduplicate interactively"

**Process**:
1. Find first duplicate pair
2. Show comparison
3. Ask user for decision
4. Apply action
5. Move to next

**Output**:
```markdown
## Duplicate Pair 1 of 15

**File A**: q-coroutine-basics--kotlin--easy.md
- Created: 2025-09-01
- Word count: 450
- Related links: 5
- Status: draft

**File B**: q-what-is-coroutine--kotlin--easy.md
- Created: 2025-10-15
- Word count: 380
- Related links: 2
- Status: draft

**Similarity**: 100% (exact title match)

**Recommendation**: Keep File A (older, more complete)

Options:
1. Keep A, delete B
2. Keep B, delete A
3. Merge both into A
4. Keep both (mark as not duplicate)
5. Skip for now

Your choice?
```

### Example 4: Auto-Merge Safe Duplicates

**User**: "Auto-merge obvious duplicates"

**Process**:
1. Find exact duplicates only
2. Apply safe merge rules
3. Report actions taken

**Output**:
```markdown
# Auto-Merge Results

Criteria: Exact title match, same topic, same difficulty

## Merges Performed (3)

1. q-coroutine-basics--kotlin--easy.md
   - Merged from: q-what-is-coroutine--kotlin--easy.md
   - Content combined, better answers kept
   - Original deleted

2. q-room-basics--android--easy.md
   - Merged from: q-room-database-intro--android--easy.md
   - Links updated
   - Original deleted

3. q-viewmodel-basics--android--medium.md
   - Merged from: q-what-is-viewmodel--android--medium.md
   - Content combined
   - Original deleted

## Not Auto-Merged (9)
Near-duplicates require manual review.
Run with --interactive for guided merge.
```

## Error Handling

### Large Dataset

**Problem**: Comparing 1000+ files is slow

**Solution**:
1. Use efficient comparison algorithms
2. Pre-filter by topic (compare within topics first)
3. Cache comparison results
4. Show progress indicators

### False Positives

**Problem**: Similar but intentionally different questions flagged

**Solution**:
1. Use high threshold (70%+) for suggestions
2. Always recommend review, not auto-delete
3. Consider difficulty level differences
4. Check if progression (easy→hard) intended

### Merge Conflicts

**Problem**: Both files have unique valuable content

**Solution**:
1. Suggest combine rather than delete
2. Show content diff for decision
3. Create merged version as new file
4. Keep originals until confirmed

## Similarity Algorithm

```
Title similarity: 40% weight
- Fuzzy string match
- Ignore common words

Content similarity: 40% weight
- Question section overlap
- Answer section overlap
- Code example similarity

Metadata similarity: 20% weight
- Same topic: +10%
- Same subtopics: +5% each
- Same difficulty: +5%

Final score = weighted average
```

## Integration with Other Skills

**Workflow: Post-Import Dedup**
1. Import new content
2. Run `duplicate-detector`
3. Resolve duplicates
4. Run `batch-validator`

**Workflow: Quarterly Cleanup**
1. Run `vault-health-report`
2. Run `duplicate-detector`
3. Merge/delete duplicates
4. Run `link-fixer` to update references

## Detection Options

### Full Scan (Default)
```
Check all duplicate types across vault.
```

### Quick Scan
```
--quick: Only exact duplicates
```

### Topic-Limited
```
--topic kotlin: Only scan kotlin notes
```

### Threshold Adjustment
```
--threshold 80: Only show 80%+ matches
```

## Notes

**Conservative**: Recommends review over auto-deletion.

**Comprehensive**: Checks titles, content, and metadata.

**Actionable**: Provides clear merge recommendations.

**Safe**: Auto-merge only for obvious cases.

**Reversible**: Can undo merges if needed.

---

**Version**: 1.0
**Last Updated**: 2025-01-05
**Status**: Production Ready
