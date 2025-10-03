# YAML Format Fix - Wikilinks in Frontmatter

**Issue**: Obsidian's YAML parser doesn't handle wikilinks `[[...]]` properly in frontmatter fields.

**Date Fixed**: 2025-10-03

---

## Problem

When using wikilinks in YAML frontmatter fields like `moc` and `related`, Obsidian displays them incorrectly:

```yaml
# ❌ WRONG - Causes parsing issues
moc: [[moc-android]]
related: [[c-jetpack-compose], [c-lazy-lists]]
```

**Displays as**: `"[["moc-android"]]"` or mangled text

---

## Solution

Use **plain text** (without wikilink brackets) in YAML frontmatter:

```yaml
# ✅ CORRECT - Proper YAML format
moc: moc-android
related:
  - c-jetpack-compose
  - c-lazy-lists
  - c-recyclerview
```

**Displays correctly** in Obsidian properties panel.

---

## Where to Use Wikilinks

### In YAML Frontmatter (NO brackets)
```yaml
moc: moc-android
related:
  - c-concept-name
  - q-other-question
```

### In Content (YES brackets)
```markdown
## References
- [[c-jetpack-compose]]
- [[c-lazy-lists]]
- [[moc-android]]

## Related Questions
- [[q-recyclerview-basics--android--easy]]
```

---

## Updated Files

All documentation and templates updated to use correct format:

1. ✅ `_templates/_tpl-qna.md` - Template fixed
2. ✅ `00-Administration/README.md` - Example fixed
3. ✅ `00-Administration/AGENTS.md` - Examples fixed
4. ✅ `.cursorrules` - Example fixed
5. ✅ `00-Administration/IMPORT-STRATEGY.md` - Examples fixed
6. ✅ Sample notes - All 3 fixed

---

## Correct YAML Schema (Updated)

```yaml
---
# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://example.com/question    # Simple string for URL
source_note: Description of source      # Simple string for note

# Workflow & relations
status: draft
moc: moc-topic-name                    # Plain text, no [[]]
related:                               # YAML list, no [[]]
  - c-concept-one
  - c-concept-two
  - q-related-question--topic--difficulty
---
```

---

## Implementation for Import Script

When generating notes programmatically:

```python
# Generate YAML
moc_value = "moc-android"  # No brackets
related_list = ["c-viewmodel", "c-lifecycle", "c-activity"]

yaml_content = f"""
moc: {moc_value}
related:
{chr(10).join(f'  - {item}' for item in related_list)}
"""
```

---

## Why This Matters

1. **Obsidian compatibility**: YAML parser expects standard YAML syntax
2. **Dataview queries**: Can properly query these fields
3. **Properties panel**: Displays correctly in Obsidian UI
4. **Graph view**: Still creates connections (Obsidian infers links)

---

**All sample notes have been corrected and are ready for review.**
