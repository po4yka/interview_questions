---\
name: obsidian-validator
description: >
  Comprehensive validation of Obsidian interview notes against vault rules.
  Checks YAML completeness, topic validity, folder placement, content structure,
  linking requirements, and Android-specific rules. Reports issues with severity
  levels (REQUIRED, FORBIDDEN, WARNING, NOTE) and provides actionable suggestions.
---\

# Obsidian Note Validator

## Purpose

Validate interview question notes against strict vault rules:
- YAML frontmatter completeness and correctness
- Topic and subtopic validation against TAXONOMY.md
- File organization (folder placement, filename pattern)
- Bilingual content structure
- Link requirements (MOC, related notes)
- Android-specific rules (subtopic mirroring)
- Tag conventions

Reports findings with severity levels and actionable recommendations.

## When to Use

Activate this skill when user requests:
- "Validate [filename]"
- "Check this note"
- "Is this note correct?"
- "Review [note] for errors"
- After creating/editing notes
- Before committing changes

## Prerequisites

Required context:
- Target note file path
- `00-Administration/Vault-Rules/TAXONOMY.md` for valid values
- Vault rules from `AGENTS.md` or `custom_instructions.md`

## Process

### Step 1: Read and Parse Note

1. **Read file** at specified path
2. **Parse YAML** frontmatter
3. **Extract content** sections
4. **Identify** note type (Q&A, concept, MOC)

If file doesn't exist or YAML parsing fails, report error and stop.

### Step 2: REQUIRED Validations

These checks MUST pass for note to be valid:

#### YAML Completeness
- [ ] `id` field present
- [ ] `title` field present (should include both EN / RU)
- [ ] `aliases` field present (array)
- [ ] `topic` field present (single value)
- [ ] `subtopics` field present (array with 1-3 items)
- [ ] `question_kind` field present (for Q&A notes)
- [ ] `difficulty` field present
- [ ] `original_language` field present
- [ ] `language_tags` field present (array)
- [ ] `status` field present
- [ ] `moc` field present (single value, NO brackets)
- [ ] `related` field present (array with ≥2 items)
- [ ] `created` field present (YYYY-MM-DD format)
- [ ] `updated` field present (YYYY-MM-DD format)
- [ ] `tags` field present (array)

#### Topic Validation
- [ ] `topic` value exists in TAXONOMY.md
- [ ] `topic` is single value (not array)
- [ ] `difficulty` is one of: easy, medium, hard
- [ ] `question_kind` is one of: coding, theory, system-design, android
- [ ] `status` is one of: draft, reviewed, ready, retired
- [ ] If created by AI: `status` is `draft` (NEVER reviewed/ready)

#### Folder Placement
- [ ] File is in folder matching `topic` field
- [ ] Folder → topic mapping correct per TAXONOMY.md

Examples:
- `topic: kotlin` → file in `70-Kotlin/`
- `topic: android` → file in `40-Android/`
- `topic: algorithms` → file in `20-Algorithms/`

#### Content Structure (Q&A notes)
- [ ] `# Question (EN)` section present
- [ ] `# Вопрос (RU)` section present
- [ ] `## Answer (EN)` section present
- [ ] `## Ответ (RU)` section present
- [ ] Both languages have substantial content (not just placeholders)

#### Link Requirements
- [ ] `moc` field links to valid MOC (format: `moc-[topic]`)
- [ ] `related` field has ≥2 items
- [ ] Links in content use proper wiki-link format: `[[note-name]]`

#### Tag Requirements
- [ ] `tags` array is not empty
- [ ] ALL tags are in English (NO Cyrillic characters)
- [ ] `difficulty/[level]` tag present
- [ ] Tags match controlled vocabularies where applicable

### Step 3: FORBIDDEN Validations

These violations MUST NOT occur:

#### Multiple Topics
- [ ] `topic` field is NOT an array
- [ ] Only ONE topic value present

#### Language Violations
- [ ] NO Russian in `tags` field (tags must be English-only)
- [ ] Russian only in `aliases` and content sections

#### YAML Format Violations
- [ ] NO brackets in `moc` field (not `[[moc-name]]`, just `moc-name`)
- [ ] NO double brackets in `related` array (not `[[item]]`, use `[item1, item2]`)
- [ ] `related` is array format, not string

#### Content Violations
- [ ] NO emoji anywhere in file
- [ ] NO separate language files (must be one file with both languages)

#### Status Violations (for AI-created notes)
- [ ] `status` is NOT `reviewed` (only humans can set)
- [ ] `status` is NOT `ready` (only humans can set)
- [ ] AI-created notes MUST have `status: draft`

#### File Organization Violations
- [ ] File NOT in wrong folder (folder must match topic)
- [ ] Filename follows pattern (Q&A: `q-[slug]--[topic]--[difficulty].md`)

### Step 4: Android-Specific Validations

If `topic: android`, additional REQUIRED checks:

#### Subtopic Validation
- [ ] All subtopics from Android controlled list in TAXONOMY.md
- [ ] Subtopics are relevant to Android platform

Valid Android subtopics include:
- UI: `ui-compose`, `ui-views`, `ui-navigation`, `ui-state`, etc.
- Architecture: `architecture-mvvm`, `architecture-mvi`, `di-hilt`, etc.
- `Lifecycle`: `lifecycle`, `activity`, `fragment`, `service`, etc.
- Data: `room`, `datastore`, `files-media`, etc.
- Testing: `testing-unit`, `testing-instrumented`, `testing-ui`, etc.

#### Tag Mirroring
- [ ] Each subtopic mirrored to tags as `android/[subtopic]`

Example:
```yaml
topic: android
subtopics: [ui-compose, lifecycle, coroutines]
tags: [
  android/ui-compose,     # REQUIRED - mirrors ui-compose
  android/lifecycle,      # REQUIRED - mirrors lifecycle
  android/coroutines,     # REQUIRED - mirrors coroutines
  compose,                # Optional additional tags
  jetpack,
  difficulty/medium
]
```

### Step 5: WARNING Validations

Non-critical issues that should be addressed:

- [ ] Missing `## Follow-ups` section
- [ ] Fewer than 3 related links (recommend 3-5)
- [ ] Missing `## References` section
- [ ] Missing `## Related Questions` section
- [ ] Code examples lack comments
- [ ] Very short answer sections (< 100 words)
- [ ] No external references provided

### Step 6: NOTE Validations

Suggestions for improvement:

- [ ] Could add more aliases (recommend 3-5)
- [ ] Could add more cross-references
- [ ] Consider adding code examples (for theory questions)
- [ ] Consider adding diagrams/visualizations
- [ ] Could expand Follow-ups section
- [ ] Tags could be more specific (use namespaced tags)

### Step 7: Generate Report

**Report Format**:

```markdown
# Validation Report: [filename]

**Status**: PASSED | FAILED | PASSED_WITH_WARNINGS

---

## REQUIRED Checks: [X/Y passed]

✅ YAML Completeness (15/15)
✅ Topic Validation (5/5)
✅ Folder Placement (2/2)
✅ Content Structure (4/4)
✅ Link Requirements (3/3)
✅ Tag Requirements (4/4)

**Result**: All REQUIRED checks passed

---

## FORBIDDEN Checks: [X/Y passed]

✅ No multiple topics
✅ No Russian in tags
✅ No YAML format violations
✅ No emoji in content
✅ No status violations
✅ File in correct folder

**Result**: No FORBIDDEN violations

---

## Android-Specific Checks: [X/Y passed]

(Only if topic=android)

✅ Subtopics from controlled list
✅ Subtopics mirrored to tags

**Result**: All Android checks passed

---

## WARNINGS: [X issues]

⚠️ Missing Follow-ups section
   Suggestion: Add common edge cases and variations

⚠️ Only 2 related links (recommend 3-5)
   Suggestion: Add [[q-similar-question--topic--level]]

---

## NOTES: [X suggestions]

💡 Could add more aliases (currently 2, recommend 3-5)
   Example: Add common alternative terms

💡 Consider adding code examples
   Theory questions benefit from practical demonstrations

---

## Summary

**Overall**: Ready for review with minor improvements recommended

**Critical Issues**: 0
**Warnings**: 2
**Suggestions**: 2

**Recommendation**: Note is valid but could be enhanced with suggested improvements.
```

## Examples

### Example 1: Valid Kotlin Note

**File**: `70-Kotlin/q-coroutine-context--kotlin--medium.md`

**Report**:
```
# Validation Report: q-coroutine-context--kotlin--medium.md

**Status**: PASSED

REQUIRED Checks: 33/33 ✅
FORBIDDEN Checks: 6/6 ✅
WARNINGS: 0
NOTES: 1

Summary: Note is fully compliant. Consider adding more related links.
```

### Example 2: Invalid Note (Multiple Issues)

**File**: `40-Android/q-bad-example--android--medium.md`

**Report**:
```
# Validation Report: q-bad-example--android--medium.md

**Status**: FAILED

REQUIRED Checks: 28/33 ❌
- Missing: language_tags field
- Missing: ## Ответ (RU) section
- Missing: related field (only 1 item, need ≥2)
- Invalid: topic not in TAXONOMY.md
- Invalid: difficulty value "средняя" (must be: easy, medium, hard)

FORBIDDEN Checks: 3/6 ❌
- FORBIDDEN: Russian in tags (found: сложность/средняя)
- FORBIDDEN: Brackets in moc field ([[moc-android]])
- FORBIDDEN: Emoji in content (found: 🎯, 📱)

Android Checks: 1/2 ❌
- Subtopics NOT mirrored to tags

WARNINGS: 3
NOTES: 2

Summary: CRITICAL ISSUES FOUND - Note requires fixes before approval.
```

### Example 3: Warning-Level Issues

**File**: `70-Kotlin/q-flow-basics--kotlin--easy.md`

**Report**:
```
# Validation Report: q-flow-basics--kotlin--easy.md

**Status**: PASSED_WITH_WARNINGS

REQUIRED Checks: 33/33 ✅
FORBIDDEN Checks: 6/6 ✅

WARNINGS: 2
⚠️ Missing Follow-ups section
⚠️ Answer sections are short (< 100 words each)

NOTES: 2
💡 Could add code examples demonstrating flow operators
💡 Consider adding more aliases

Summary: Note is valid but incomplete. Recommended improvements listed above.
```

## Error Handling

### File Not Found

**Problem**: Specified file doesn't exist

**Solution**:
1. Report error with exact path attempted
2. Suggest checking filename/path
3. Offer to list similar files in target folder

### YAML Parse Error

**Problem**: YAML frontmatter has syntax errors

**Solution**:
1. Report line number of syntax error if possible
2. Show example of correct YAML format
3. Common issues: missing colons, incorrect indentation, unescaped characters

### Topic Not in TAXONOMY.md

**Problem**: Topic value not found in controlled list

**Solution**:
1. Report invalid topic value
2. `List` all valid topics from TAXONOMY.md
3. Suggest closest matches (by string similarity)
4. Offer to update topic if user confirms

### Android Subtopic Issues

**Problem**: Android subtopics not from controlled list

**Solution**:
1. Report invalid subtopics
2. `List` valid Android subtopics from TAXONOMY.md
3. Suggest closest matches
4. Remind about tag mirroring requirement

## Validation Levels

### PASSED
- All REQUIRED checks pass
- No FORBIDDEN violations
- No WARNING issues

**Action**: Note is ready for human review

### PASSED_WITH_WARNINGS
- All REQUIRED checks pass
- No FORBIDDEN violations
- Some WARNING issues present

**Action**: Note is valid but should be improved before final approval

### FAILED
- One or more REQUIRED checks fail
- OR any FORBIDDEN violation present

**Action**: Note MUST be fixed before it can be approved

## Integration with Other Skills

**Recommended workflow**:
1. Create note with `obsidian-qna-creator`
2. Immediately validate with `obsidian-validator`
3. If issues found, fix and re-validate
4. If passed, optionally enhance with `obsidian-link-analyzer`

**Auto-validation**: Consider running validator automatically after note creation.

## Notes

**Comprehensive**: This validator checks 50+ rules across all vault requirements.

**Severity Levels**: Clear distinction between critical issues (REQUIRED/FORBIDDEN) and improvements (WARNING/NOTE).

**Actionable**: All issues reported with specific suggestions for fixes.

**Fast**: Most checks are simple field/format validations that execute quickly.

**Extensible**: Easy to add new validation rules as vault requirements evolve.

---

**Version**: 1.0
**Last Updated**: 2025-11-09
**Status**: Production Ready
