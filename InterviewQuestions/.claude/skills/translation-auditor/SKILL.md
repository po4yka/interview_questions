---
name: translation-auditor
description: >
  Audit bilingual content quality and translation completeness. Finds partially
  translated sections, checks EN/RU content parity, identifies missing translations
  by folder, reports translation completeness percentage, and flags inconsistent
  terminology. Essential for maintaining bilingual vault quality.
---

# Translation Auditor

## Purpose

Audit and improve bilingual (EN/RU) content quality:

1. **Completeness Check**: Find notes missing EN or RU sections
2. **Partial Translation**: Detect partially translated content
3. **Parity Analysis**: Check if EN and RU have equivalent content
4. **Terminology Consistency**: Flag inconsistent term translations
5. **Coverage Report**: Calculate translation percentage by folder
6. **Priority List**: Generate list of notes needing translation

## When to Use

Activate this skill when user requests:
- "Audit translations"
- "Find untranslated notes"
- "Check translation quality"
- "What needs translation?"
- "Translation coverage report"
- "Check EN/RU parity"
- During localization reviews
- Before content releases

## Prerequisites

Required context:
- Access to vault files
- Understanding of bilingual structure
- Section header patterns (EN/RU)

## Bilingual Structure

### Required Sections (Q&A Notes)

```markdown
# Question (EN)
[English question text]

# Вопрос (RU)
[Russian question text]

## Answer (EN)
[English answer content]

## Ответ (RU)
[Russian answer content]
```

### Language Tags

```yaml
language_tags: [en, ru]  # Both present
language_tags: [en]      # English only
language_tags: [ru]      # Russian only
```

## Process

### Step 1: Scan Files

For each Q&A note:

```
1. Read file content
2. Extract language_tags from YAML
3. Find section headers:
   - # Question (EN)
   - # Вопрос (RU)
   - ## Answer (EN)
   - ## Ответ (RU)
4. Extract content for each section
5. Calculate section lengths
```

### Step 2: Classify Translation Status

Determine status for each file:

```
COMPLETE: All 4 sections present with substantial content
EN_ONLY: Only English sections present
RU_ONLY: Only Russian sections present
PARTIAL_EN: Has EN sections, RU sections empty/short
PARTIAL_RU: Has RU sections, EN sections empty/short
MISMATCH: Sections present but content lengths very different
```

### Step 3: Check Content Parity

Compare EN and RU content:

```
Parity indicators:
- Section length ratio (EN vs RU)
- Code block count matches
- Link count matches
- List item count matches
- Heading count matches

Parity score: 0-100%
- 90-100%: Excellent parity
- 70-89%: Good parity
- 50-69%: Needs review
- <50%: Significant mismatch
```

### Step 4: Terminology Analysis

Check for consistent translations:

```
Common terms to verify:
- Technical terms (coroutine, flow, suspend)
- Framework names (Compose, Hilt, Room)
- Concepts (lifecycle, dependency injection)

Flag inconsistencies:
- "coroutine" → "корутина" vs "сопрограмма"
- "dependency injection" → "внедрение зависимостей" vs "DI"
```

### Step 5: Generate Statistics

Calculate coverage metrics:

```
By Folder:
| Folder | Total | Complete | EN Only | RU Only | Partial |
|--------|-------|----------|---------|---------|---------|
| 70-Kotlin | 358 | 340 | 12 | 0 | 6 |
| 40-Android | 527 | 495 | 25 | 2 | 5 |

Overall:
- Total Q&A notes: 972
- Fully translated: 912 (93.8%)
- English only: 45 (4.6%)
- Russian only: 3 (0.3%)
- Partial: 12 (1.2%)
```

### Step 6: Generate Report

Produce comprehensive translation audit:

```markdown
# Translation Audit Report

**Generated**: 2025-11-15
**Total Q&As**: 972

---

## Summary

| Status | Count | Percentage |
|--------|-------|------------|
| Complete (EN+RU) | 912 | 93.8% |
| English Only | 45 | 4.6% |
| Russian Only | 3 | 0.3% |
| Partial | 12 | 1.2% |

**Overall Translation Coverage**: 93.8%

---

## Coverage by Folder

| Folder | Complete | Missing RU | Missing EN | Partial |
|--------|----------|------------|------------|---------|
| 40-Android | 495 (93.9%) | 25 | 2 | 5 |
| 70-Kotlin | 340 (95.0%) | 12 | 0 | 6 |
| 60-CompSci | 48 (85.7%) | 7 | 0 | 1 |
| 20-Algorithms | 9 (100%) | 0 | 0 | 0 |
| ... | ... | ... | ... | ... |

---

## Files Needing Translation

### English Only (45 files)

Priority: Add Russian translation

| File | Word Count (EN) | Age |
|------|-----------------|-----|
| q-new-feature--kotlin--hard.md | 450 | 3 days |
| q-compose-update--android--medium.md | 380 | 5 days |
| ... | ... | ... |

### Russian Only (3 files)

Priority: Add English translation

| File | Word Count (RU) |
|------|-----------------|
| q-android-specific--android--easy.md | 200 |
| ... | ... |

### Partial Translation (12 files)

Priority: Complete missing sections

| File | Status | Missing |
|------|--------|---------|
| q-flow-basics--kotlin--easy.md | EN complete, RU short | Expand RU answer |
| q-room-relations--android--medium.md | RU missing answer | Add ## Ответ (RU) |
| ... | ... | ... |

---

## Content Parity Analysis

### Low Parity Files (< 70%)

Files where EN and RU content differs significantly:

| File | EN Length | RU Length | Parity |
|------|-----------|-----------|--------|
| q-coroutine-advanced--kotlin--hard.md | 850 | 320 | 38% |
| q-compose-animation--android--medium.md | 620 | 410 | 66% |

**Recommendation**: Review and expand shorter version.

### Parity Distribution

| Parity Range | Files |
|--------------|-------|
| 90-100% | 845 |
| 70-89% | 52 |
| 50-69% | 12 |
| <50% | 3 |

---

## Terminology Consistency

### Inconsistent Translations Found

| English Term | Translation 1 | Translation 2 | Files |
|--------------|---------------|---------------|-------|
| coroutine | корутина | сопрограмма | 5 |
| dependency injection | внедрение зависимостей | DI | 3 |

**Recommendation**: Standardize terminology across vault.

---

## Translation Priority Queue

### High Priority (Add ASAP)
1. q-new-feature--kotlin--hard.md (EN only, 3 days old)
2. q-compose-update--android--medium.md (EN only, 5 days old)
3. q-coroutine-advanced--kotlin--hard.md (low parity)

### Medium Priority (This Week)
4. q-flow-basics--kotlin--easy.md (partial RU)
5. q-room-relations--android--medium.md (missing RU answer)
[... more items ...]

### Low Priority (When Possible)
[... remaining items ...]

---

## Recommendations

1. **Immediate**: Translate 10 newest EN-only files
2. **This Week**: Complete 12 partial translations
3. **Review**: Check 3 low-parity files for content accuracy
4. **Ongoing**: Standardize terminology translations

---

**Use `obsidian-translator` skill to add missing translations.**
```

## Examples

### Example 1: Full Vault Audit

**User**: "Audit translations in the vault"

**Output**:
```markdown
# Translation Audit

Total: 972 Q&As
Complete: 912 (93.8%)
Needs work: 60 files

## Priority Files
1. 45 files need Russian translation
2. 3 files need English translation
3. 12 files have partial translations

Top 5 to translate:
1. q-new-feature--kotlin--hard.md
2. q-compose-update--android--medium.md
3. q-flow-advanced--kotlin--hard.md
4. q-room-migration--android--medium.md
5. q-coroutine-exception--kotlin--medium.md
```

### Example 2: Folder-Specific Audit

**User**: "Check translations in 70-Kotlin/"

**Output**:
```markdown
# Translation Audit: 70-Kotlin/

Files: 358
Complete: 340 (95.0%)
EN only: 12
Partial: 6

## Files Needing Translation

### English Only
1. q-ksp-basics--kotlin--medium.md
2. q-context-receivers--kotlin--hard.md
[... more ...]

### Partial
1. q-flow-testing--kotlin--medium.md (RU answer short)
2. q-channel-select--kotlin--hard.md (missing RU sections)
[... more ...]
```

### Example 3: Check Parity

**User**: "Check EN/RU parity for Kotlin notes"

**Output**:
```markdown
# Parity Analysis: 70-Kotlin/

## Parity Distribution
- Excellent (90%+): 312 files
- Good (70-89%): 28 files
- Needs Review (50-69%): 14 files
- Low (<50%): 4 files

## Low Parity Files (Needs Review)

| File | Parity | Issue |
|------|--------|-------|
| q-dsl-advanced--kotlin--hard.md | 42% | RU much shorter |
| q-inline-classes--kotlin--medium.md | 48% | EN has more examples |
| q-contracts--kotlin--hard.md | 45% | RU missing sections |
| q-multiplatform--kotlin--medium.md | 38% | RU incomplete |

Recommendation: Expand shorter versions to match.
```

### Example 4: Terminology Check

**User**: "Check translation terminology consistency"

**Output**:
```markdown
# Terminology Consistency Report

## Inconsistencies Found

### "coroutine"
- "корутина" (287 uses) - STANDARD
- "сопрограмма" (5 uses) - NON-STANDARD

Files with non-standard:
1. q-coroutine-intro--kotlin--easy.md
2. q-suspend-function--kotlin--medium.md
[... more ...]

### "dependency injection"
- "внедрение зависимостей" (45 uses) - STANDARD
- "DI" (12 uses) - ACCEPTABLE (abbreviation)

No action needed for abbreviations.

## Recommendation
Standardize "корутина" across all 5 files.
```

## Error Handling

### Malformed Sections

**Problem**: Section headers don't match expected pattern

**Solution**:
1. Try alternate patterns (case variations)
2. Report as "unclear structure"
3. Suggest manual review

### Empty Sections

**Problem**: Section exists but has no content

**Solution**:
1. Mark as partial translation
2. Report in audit
3. Add to translation queue

### Encoding Issues

**Problem**: Russian text has encoding problems

**Solution**:
1. Detect encoding issues
2. Report affected files
3. Suggest file encoding fix

## Integration with Other Skills

**Workflow: Translation Sprint**
1. Run `translation-auditor` for priority list
2. Use `obsidian-translator` for each file
3. Run `obsidian-validator` to verify
4. Re-audit to confirm completion

**Workflow: Quality Review**
1. Run `translation-auditor` with parity check
2. Review low-parity files manually
3. Update as needed
4. Re-audit to verify

## Audit Options

### Full Audit (Default)
```
Check all aspects:
- Completeness
- Parity
- Terminology
- Statistics
```

### Quick Check
```
--quick: Only check completeness, skip parity analysis
```

### Parity Only
```
--parity: Only check content parity for already-translated files
```

### Terminology Only
```
--terminology: Only check term consistency
```

## Notes

**Comprehensive**: Covers completeness, parity, and terminology.

**Prioritized**: Generates actionable priority queue.

**Statistical**: Provides coverage metrics by folder.

**Non-Destructive**: Read-only audit, no modifications.

**Integrates**: Works with `obsidian-translator` for fixes.

---

**Version**: 1.0
**Last Updated**: 2025-01-05
**Status**: Production Ready
