# HTML Tag Checker - Quick Reference

## Purpose

This tool checks your Obsidian vault for unclosed HTML tags, orphaned closing tags, and HTML comments in markdown content.

## Usage

Run the verification script from the vault root:

```bash
python3 final_html_verification.py
```

## What It Checks

1. **Unclosed Opening Tags** - HTML tags that are opened but never closed
   - Example: `<div>` without a matching `</div>`

2. **Orphaned Closing Tags** - Closing tags without matching opening tags
   - Example: `</div>` without a preceding `<div>`

3. **HTML Comments** - HTML comment syntax in markdown
   - Example: `<!-- comment -->`

## What It Ignores

The script intelligently excludes:
- Content inside code blocks (between ``` or ~~~)
- Content inside inline code (between single backticks)
- Self-closing tags (br, hr, img, etc.)
- Generic type parameters (List<String>, etc.) - these are not HTML tags
- Android/XML tags inside code examples

## HTML Tags It Monitors

Common HTML tags that should not appear unclosed in markdown:
- Layout: div, span, section, article, header, footer, nav, main, aside
- Text: p, h1-h6, strong, em, b, i, u, mark, del, ins, small
- Lists: ul, ol, li, dl, dt, dd
- Tables: table, tr, td, th, thead, tbody, tfoot, caption
- Forms: form, input, button, select, option, textarea, label
- Interactive: details, summary, a
- Media: video, audio, canvas, svg, figure, figcaption
- Other: blockquote, code, pre, iframe, script, style

## Output

### Clean Vault
```
✓ NO HTML ISSUES FOUND!

The vault is clean:
  - No unclosed opening tags
  - No orphaned closing tags
  - No HTML comments
```

### Issues Found
```
Found issues in X files:
  - Unclosed opening tags: X
  - Orphaned closing tags: X
  - HTML comments: X

[Detailed list of issues with file paths and line numbers]
```

## Common False Positives

These are NOT HTML tags and should be in backticks in your markdown:

### Generic Types
```
List<String>     → `List<String>`
Map<K, V>        → `Map<K, V>`
StateFlow<Int>   → `StateFlow<Int>`
```

### Placeholders
```
<topic>          → `<topic>`
<path>           → `<path>`
<file>           → `<file>`
```

### XML in Code Blocks
XML/Android tags inside code blocks are intentional and ignored:
````markdown
```xml
<manifest>
    <application>
        <activity />
    </application>
</manifest>
```
````

## Script Location

`/Users/npochaev/Documents/InterviewQuestions/final_html_verification.py`

## Last Verification

**Date**: 2025-12-03
**Result**: ✓ Clean (0 issues found in 1,368 files)

## Re-run Verification

You can run this script anytime to verify the vault's HTML integrity, especially:
- After bulk edits
- After importing new notes
- Before publishing or exporting
- As part of automated CI/CD checks
