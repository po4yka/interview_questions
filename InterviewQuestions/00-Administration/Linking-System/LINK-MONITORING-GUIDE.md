---
date created: Tuesday, November 25th 2025, 8:20:27 pm
date modified: Tuesday, November 25th 2025, 8:54:04 pm
---

# Link Monitoring System Guide

**Purpose**: Automated link health monitoring for Obsidian vault
**Last Updated**: 2025-11-25

## Overview

The vault has an automated link monitoring system built with **Dataview** and **DataviewJS**. This system detects broken links, orphan files, missing cross-references, and structural issues.

## Monitoring Tools

### 1. LINK-HEALTH-DASHBOARD.md (Primary Tool)

**Location**: `00-Administration/Linking-System/`
**Purpose**: Comprehensive health analysis

**Shows**:
- Overall health score (weighted calculation)
- All key metrics with status indicators
- Detailed broken links by file and target
- Orphan files grouped by topic
- Missing cross-references by relevance
- Prioritized action items

**Best for**: Weekly reviews and planning improvements

### 2. Homepage.md (Integrated Monitoring)

**Location**: Vault root
**Purpose**: Link health section in daily navigation

**Shows**:
- Broken links detection with top files
- Missing cross-references
- Orphan files (first 20)
- Files without Related Questions section

**Best for**: Daily quick checks during regular workflow

## How to Use

### Daily Workflow

1. Open **Homepage.md**
2. Scroll to "Link Health Monitor" section
3. Check if any issues appear
4. Note the overall health percentage

### Weekly Maintenance

1. Open **LINK-HEALTH-DASHBOARD.md**
2. Review overall health score
3. Check "Action Items" section
4. Fix issues in priority order:
   - Priority 1: Broken links
   - Priority 2: Cross-references
   - Priority 3: Orphans

## Understanding Health Metrics

### Overall Health Score (0-100%)

**Calculation**:
```
Overall Health = (Link Integrity x 50%) +
                 (Structure Quality x 25%) +
                 (Connectivity x 25%)
```

**Ranges**:
- 90-100%: Excellent - Vault is in great shape
- 70-89%: Good - Minor improvements needed
- Below 70%: Needs Work - Focus on broken links

### Link Integrity

**Measures**: Percentage of valid links vs broken links
**Target**: 95%+

**How to improve**:
- Create missing files
- Fix naming inconsistencies
- Remove or update broken links

### Structure Quality

**Measures**: Percentage of files with proper structure (Related Questions, References, Tags)
**Target**: 90%+

**How to improve**:
- Add "Related Questions" sections
- Include references to documentation
- Add relevant tags and subtopics

### Connectivity

**Measures**: Percentage of files with incoming links (not orphans)
**Target**: 95%+

**How to improve**:
- Link orphan files from related questions
- Create MOC files that link to categories
- Add cross-references between related topics

## What Gets Detected

### Broken Links (Priority: High)

**Definition**: Wikilinks `[[target]]` pointing to non-existent files

**Example**:
```markdown
## Related Questions
- [[q-nonexistent-note]]  <-- File doesn't exist
```

**Detection**: Checks all `[[...]]` patterns and verifies target exists

### Orphan Files (Priority: Medium)

**Definition**: Files that exist but no other file links to them

**Example**:
- `q-some-topic.md` exists
- No other file has `[[q-some-topic]]`
- File is isolated/undiscoverable

**Why it matters**: Users can't discover these files through navigation

### Missing Cross-References (Priority: Medium)

**Definition**: Files with overlapping topics that should link to each other

**Example**:
- `q-flow-basics.md` has subtopics: [flow, coroutines]
- `q-flow-operators.md` has subtopics: [flow, operators]
- They share topics but don't link to each other

### Missing Structure (Priority: Low)

**Definition**: Files lacking standard sections (Related Questions, References)

## Best Practices

### When Creating New Files

- Add "Related Questions" section with at least 2-3 links
- Link from at least one existing file
- Include proper frontmatter (topic, subtopics, tags)
- Add references to documentation

### When Renaming Files

- Check for incoming links first
- Update all references
- Re-run health check after

### Fix Issues in Priority Order

```
Priority 1: Broken links     -> Creates immediate user frustration
Priority 2: Cross-references -> Improves learning
Priority 3: Orphans          -> Improves discoverability
Priority 4: Structure        -> Enhances quality
```

## Troubleshooting

### Dataview Queries Not Showing

**Cause**: Dataview plugin not enabled

**Fix**:
1. Settings -> Community Plugins
2. Enable "Dataview"
3. Ensure "Enable JavaScript Queries" is ON
4. Restart Obsidian

### Health Score Seems Wrong

**Cause**: Cache issue

**Fix**:
1. Close the monitoring file
2. Wait 2-3 seconds
3. Reopen the file
4. Dataview will re-scan

### Some Broken Links Not Detected

**Current limitation**: Only wikilinks `[[link]]` are detected, not markdown links `[text](url)`

**Workaround**: Use wikilinks for internal references

## Maintenance Checklist

### Monthly

- [ ] Review LINK-HEALTH-DASHBOARD.md
- [ ] Take health score screenshot
- [ ] Fix top 10 broken links
- [ ] Add 10 cross-references
- [ ] Connect 5 orphan files

### Quarterly

- [ ] Compare health scores over 3 months
- [ ] Review and archive fixed issues

## Quick Reference

| Need | Open This |
|------|-----------|
| Full analysis | [[LINK-HEALTH-DASHBOARD]] |
| Daily navigation | [[Homepage]] |
| Linking rules | [[LINKING-STRATEGY]] |

## See Also

- **[[LINKING-STRATEGY]]** - MOC linking rules
- **[[LINK-HEALTH-DASHBOARD]]** - Detailed analysis dashboard
- **[[TAXONOMY]]** - Controlled vocabularies
