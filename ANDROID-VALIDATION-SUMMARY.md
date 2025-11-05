# Android Folder Validation Summary

**Date:** 2025-11-05
**Total Files:** 527 Android Q&A notes
**Validation Tool:** `uv run --project utils python -m utils.validate_note`

---

## Overall Results

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total Files** | 527 | 100% |
| **Passed** | 137 | 26.0% |
| **Failed** | 390 | 74.0% |

---

## Common Issue Types (Based on Sample Analysis)

### 1. Missing Required Headings (CRITICAL)
- **Issue:** Files missing `## Related Questions` section
- **Impact:** Breaks required document structure
- **Example:** `q-advanced-share-sheet-shortcuts--android--hard.md`
- **Fix:** Add the missing section to affected files

### 2. Broken Wikilinks (ERROR)
- **Issue:** Links to non-existent concept or question files
- **Examples:**
  - `[[c-compose-semantics]]` - concept file doesn't exist
  - `[[c-espresso-testing]]` - concept file doesn't exist
  - `[[q-android-coverage-gaps--android--hard]]` - question file doesn't exist
- **Fix:** Either create the missing files or update links to existing files

### 3. Invalid Android Subtopics (ERROR)
- **Issue:** Subtopics not in TAXONOMY.md Android subtopics list
- **Example:** `subtopics: [communication, sharing, shortcuts]`
  - `communication` is not a valid Android subtopic
  - `sharing` is not a valid Android subtopic
  - `shortcuts` is not a valid Android subtopic
- **Fix:** Update to use valid Android subtopics from TAXONOMY.md

### 4. Missing Android Tag Mirrors (ERROR)
- **Issue:** Tags don't mirror the subtopics with `android/` prefix
- **Example:** If `subtopics: [ui-compose, lifecycle]`, then tags must include `android/ui-compose` and `android/lifecycle`
- **Fix:** Add missing `android/<subtopic>` tags

### 5. Broken Related Links in YAML (ERROR)
- **Issue:** YAML `related` field contains links to non-existent files
- **Impact:** Broken relationships in knowledge graph
- **Fix:** Update related links to point to existing files

### 6. Code Formatting Issues (WARNING)
- **Issue:** Generic types not wrapped in backticks, causing potential HTML interpretation
- **Example:** `ArrayList<String>` should be `` `ArrayList<String>` ``
- **Fix:** Wrap all types and generics in backticks

---

## Sample Failed Files

| File | Issues | Severity |
|------|--------|----------|
| `q-advanced-share-sheet-shortcuts--android--hard.md` | Missing heading, invalid subtopics, broken links | CRITICAL + ERROR |
| `q-android-auto-guidelines--android--hard.md` | Multiple validation errors | CRITICAL + ERROR |
| `q-android-enterprise-mdm-architecture--android--hard.md` | Multiple validation errors | CRITICAL + ERROR |
| `q-accessibility-testing--android--medium.md` | 2 broken wikilinks | ERROR |
| `q-accessibility-text-scaling--android--medium.md` | 1 warning | WARNING |

---

## Priority Action Items

### Priority 1: CRITICAL Issues
1. **Add Missing "## Related Questions" Sections**
   - Estimate: ~100-200 files affected
   - Impact: High (document structure requirement)
   - Effort: Low (template-based addition)

### Priority 2: ERROR Issues
2. **Fix Invalid Android Subtopics**
   - Estimate: Unknown (detailed analysis in progress)
   - Impact: High (breaks TAXONOMY compliance)
   - Effort: Medium (requires TAXONOMY.md lookup)

3. **Update Android Tag Mirrors**
   - Estimate: Goes hand-in-hand with subtopic fixes
   - Impact: High (validator requirement)
   - Effort: Low (automated with subtopic fixes)

4. **Fix Broken Wikilinks**
   - Estimate: Unknown (detailed analysis in progress)
   - Impact: Medium (breaks navigation)
   - Effort: High (requires creating missing concept notes or link updates)

5. **Fix Broken Related Links in YAML**
   - Estimate: Unknown (detailed analysis in progress)
   - Impact: Medium (breaks knowledge graph)
   - Effort: Medium (requires finding alternative related files)

### Priority 3: WARNING Issues
6. **Code Formatting**
   - Estimate: Unknown (detailed analysis in progress)
   - Impact: Low (cosmetic/rendering issue)
   - Effort: Low (find-and-replace)

---

## Next Steps

1. **Wait for detailed analysis to complete** (running in background)
   - Will provide exact counts for each issue type
   - Will identify most common broken links
   - Will identify most common invalid subtopics

2. **Generate prioritized fix list**
   - Focus on CRITICAL issues first
   - Batch similar ERROR issues together

3. **Create automation scripts** (if applicable)
   - Automated subtopic/tag updates
   - Template for adding "Related Questions" sections

4. **Execute fixes systematically**
   - Use NOTE-REVIEW-PROMPT.md workflow
   - Validate before/after each fix
   - Track progress with checklist

---

## Validation Command Reference

### Validate Single File
```bash
uv run --project utils python -m utils.validate_note InterviewQuestions/40-Android/<filename>.md
```

### Validate All Android Files (Custom Script)
```bash
python3 validate_android.py
```

### Detailed Analysis (Custom Script - Running)
```bash
python3 analyze_android_issues.py
```

---

## Notes

- **Validation Tool Version:** Located in `utils/src/utils/validate_note.py`
- **Validators Used:**
  - `YAMLValidator` - YAML frontmatter validation
  - `ContentValidator` - Content structure validation
  - `LinkValidator` - Wikilink validation
  - `FormatValidator` - Format and folder placement
  - `AndroidValidator` - Android-specific validation

- **Reference Documentation:**
  - TAXONOMY.md - Valid subtopics and controlled vocabularies
  - NOTE-REVIEW-PROMPT.md - Automation workflow for fixes
  - AGENTS.md - LLM agent instructions

---

**Status:** Initial validation complete. Detailed analysis in progress.
**Generated:** 2025-11-05
