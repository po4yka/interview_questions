---
name: vault-health-report
description: >
  Generate comprehensive vault health report with statistics and issue detection.
  Counts notes by topic, difficulty, status. Identifies YAML issues, orphaned notes,
  broken links, and translation coverage. Produces actionable markdown summary for
  vault maintenance and quality monitoring.
---

# Vault Health Report

## Purpose

Generate a comprehensive health report for the interview questions vault:
- Count notes by topic, difficulty, and status
- Identify YAML validation issues across all notes
- Find orphaned notes (no incoming links)
- Detect broken wiki-links
- Report bilingual translation coverage
- Calculate overall vault health score
- Generate actionable markdown summary

## When to Use

Activate this skill when user requests:
- "Generate vault health report"
- "Show vault statistics"
- "How healthy is my vault?"
- "What issues exist in the vault?"
- "Give me a vault overview"
- "Audit the vault"
- Weekly/monthly vault maintenance
- Before major content updates

## Prerequisites

Required context:
- Access to `InterviewQuestions/` directory
- `00-Administration/Vault-Rules/TAXONOMY.md` for valid topics
- Understanding of vault folder structure

## Process

### Step 1: Collect Vault Statistics

Scan and count all markdown files:

```
1. Q&A Notes (q-*.md):
   - Count by folder/topic
   - Count by difficulty (easy/medium/hard)
   - Count by status (draft/reviewed/ready/retired)

2. Concept Notes (c-*.md):
   - Total count in 10-Concepts/
   - Most linked concepts

3. MOC Files (moc-*.md):
   - Total count in 90-MOCs/
   - Coverage per topic

4. Templates:
   - Verify all templates exist in _templates/
```

### Step 2: YAML Validation Scan

Check all Q&A notes for common YAML issues:

```yaml
# Check for:
- Missing required fields (id, title, topic, difficulty, etc.)
- Invalid topic values (not in TAXONOMY.md)
- Multiple topics (should be single value)
- Incorrect moc format (brackets present)
- Incorrect related format (double brackets)
- Russian in tags (should be English-only)
- Missing difficulty tag
- Status violations (reviewed/ready set by AI)
- Android subtopic mirroring issues
```

Count issues by severity:
- CRITICAL: FORBIDDEN violations
- ERROR: Missing REQUIRED fields
- WARNING: Missing recommended fields
- INFO: Improvement suggestions

### Step 3: Link Health Analysis

Analyze link integrity across vault:

```
1. Orphaned Notes:
   - Find notes with zero incoming links
   - Exclude MOCs and index files
   - Prioritize by age and importance

2. Broken Links:
   - Find [[wiki-links]] pointing to non-existent files
   - Check both content and YAML related fields
   - Report broken link count per file

3. Missing MOC Links:
   - Q&A notes without moc field
   - Notes not linked from their topic's MOC

4. Weak Connectivity:
   - Notes with fewer than 2 related links
   - Isolated topic clusters
```

### Step 4: Translation Coverage

Analyze bilingual content completeness:

```
For each Q&A note, check:
- language_tags field value
- Presence of # Question (EN) section
- Presence of # Вопрос (RU) section
- Presence of ## Answer (EN) section
- Presence of ## Ответ (RU) section

Calculate:
- Notes with both languages: X (Y%)
- Notes with EN only: X (Y%)
- Notes with RU only: X (Y%)
- Notes with partial translation: X (Y%)
```

### Step 5: Calculate Health Score

Compute overall vault health (0-100):

```
Health Score Components:
- YAML Compliance: 30 points
  - Deduct points for each CRITICAL/ERROR issue

- Link Health: 25 points
  - Orphaned notes penalty
  - Broken links penalty
  - Low connectivity penalty

- Translation Coverage: 20 points
  - Percentage of fully bilingual notes

- Content Distribution: 15 points
  - Balanced difficulty distribution
  - Topic coverage breadth

- Status Progress: 10 points
  - Percentage moved beyond draft status
```

### Step 6: Generate Report

Create comprehensive markdown report:

```markdown
# Vault Health Report

**Generated**: YYYY-MM-DD HH:MM
**Health Score**: XX/100

---

## Summary

| Metric | Count | Status |
|--------|-------|--------|
| Total Q&A Notes | XXX | - |
| Concept Notes | XXX | - |
| MOCs | XX | - |
| YAML Issues | XX | WARNING |
| Orphaned Notes | XX | WARNING |
| Broken Links | XX | ERROR |
| Translation Coverage | XX% | OK |

---

## Content Distribution

### By Topic
| Topic | Count | Easy | Medium | Hard |
|-------|-------|------|--------|------|
| android | 527 | 89 | 312 | 126 |
| kotlin | 358 | 45 | 201 | 112 |
| ... | ... | ... | ... | ... |

### By Status
| Status | Count | Percentage |
|--------|-------|------------|
| draft | XXX | XX% |
| reviewed | XX | X% |
| ready | XX | X% |

---

## Issues Found

### CRITICAL Issues (Must Fix)
- [filename]: [issue description]
- ...

### ERROR Issues (Should Fix)
- [filename]: [issue description]
- ...

### WARNING Issues (Recommended)
- [filename]: [issue description]
- ...

---

## Link Health

### Orphaned Notes (X total)
Files with no incoming links:
- 70-Kotlin/q-example--kotlin--easy.md
- ...

### Broken Links (X total)
Files with broken wiki-links:
- 40-Android/q-test--android--medium.md: [[missing-note]]
- ...

### Weak Connectivity (X total)
Files with fewer than 2 related links:
- ...

---

## Translation Status

| Language | Count | Percentage |
|----------|-------|------------|
| Both EN+RU | XXX | XX% |
| EN only | XX | X% |
| RU only | X | X% |
| Partial | XX | X% |

### Files Needing Translation
- 70-Kotlin/q-new-feature--kotlin--medium.md (EN only)
- ...

---

## Recommendations

1. **Priority 1**: Fix X CRITICAL issues
   - [specific actionable items]

2. **Priority 2**: Address broken links
   - [specific files to fix]

3. **Priority 3**: Add translations to X notes
   - [list of files]

4. **Priority 4**: Improve link connectivity
   - [suggestions]

---

## Health Score Breakdown

| Component | Score | Max | Notes |
|-----------|-------|-----|-------|
| YAML Compliance | XX | 30 | -X for critical issues |
| Link Health | XX | 25 | -X for orphans |
| Translation | XX | 20 | XX% coverage |
| Distribution | XX | 15 | Good balance |
| Status Progress | XX | 10 | X% beyond draft |
| **Total** | **XX** | **100** | |

---

**Report generated by vault-health-report skill**
```

## Examples

### Example 1: Healthy Vault

**User**: "Generate vault health report"

**Report Output**:
```markdown
# Vault Health Report

**Generated**: 2025-11-15 14:30
**Health Score**: 92/100

## Summary
| Metric | Count | Status |
|--------|-------|--------|
| Total Q&A Notes | 972 | OK |
| YAML Issues | 3 | OK |
| Orphaned Notes | 5 | OK |
| Broken Links | 0 | OK |
| Translation Coverage | 98% | OK |

## Recommendations
1. Fix 3 minor YAML issues (missing aliases)
2. Add links to 5 orphaned notes
```

### Example 2: Vault Needing Attention

**User**: "Audit the vault"

**Report Output**:
```markdown
# Vault Health Report

**Generated**: 2025-11-15 14:30
**Health Score**: 67/100

## Summary
| Metric | Count | Status |
|--------|-------|--------|
| Total Q&A Notes | 972 | - |
| YAML Issues | 47 | ERROR |
| Orphaned Notes | 23 | WARNING |
| Broken Links | 12 | ERROR |
| Translation Coverage | 74% | WARNING |

## CRITICAL Issues (Must Fix)
- 40-Android/q-compose-issue--android--medium.md: status set to 'reviewed' by AI
- 70-Kotlin/q-flow--kotlin--hard.md: Russian in tags
...

## Recommendations
1. **URGENT**: Fix 5 CRITICAL YAML issues
2. **HIGH**: Repair 12 broken links
3. **MEDIUM**: Translate 253 notes missing RU content
```

## Error Handling

### Large Vault Performance

**Problem**: Scanning thousands of files is slow

**Solution**:
1. Use efficient glob patterns
2. Cache results where possible
3. Show progress indicators for long operations
4. Option to scan specific folders only

### File Access Errors

**Problem**: Cannot read certain files

**Solution**:
1. Log inaccessible files in report
2. Continue scanning other files
3. Report file access issues in summary

### Incomplete YAML

**Problem**: Some files have malformed YAML

**Solution**:
1. Catch parse errors gracefully
2. Report files with YAML errors separately
3. Still extract what information is possible

## Integration with Other Skills

**Recommended Workflow**:

1. Run `vault-health-report` to identify issues
2. Use `batch-validator` for detailed file validation
3. Use `link-fixer` to repair broken links
4. Use `translation-auditor` for translation issues
5. Use `bulk-normalizer` for YAML fixes

**Periodic Maintenance**:
- Run weekly for ongoing monitoring
- Run before major content releases
- Run after bulk content imports

## Output Options

### Inline Report
Display report directly in chat (default)

### File Output
Save report to file:
- Path: `00-Administration/Reports/vault-health-YYYY-MM-DD.md`
- Creates dated snapshot for tracking trends

### Summary Only
Brief summary for quick checks:
```
Vault Health: 92/100
- 972 Q&As, 359 concepts, 13 MOCs
- 3 issues found (0 critical)
- 98% translated
```

## Notes

**Comprehensive**: Covers all aspects of vault health in one report.

**Actionable**: All issues come with specific fix recommendations.

**Trackable**: Save reports to track vault health over time.

**Efficient**: Designed to scan large vaults quickly.

**Non-destructive**: Read-only operation, does not modify any files.

---

**Version**: 1.0
**Last Updated**: 2025-01-05
**Status**: Production Ready
