---\
name: code-validator
description: >
  Validate and analyze code examples in interview notes. Checks Kotlin/Java/Python
  syntax validity, verifies code block language tags, detects missing imports,
  checks indentation consistency, and flags potentially broken snippets. Essential
  for maintaining quality code examples in technical interview content.
---\

# Code Validator

## Purpose

Validate code quality in interview question notes:

1. **Syntax Validation**: Check code for syntax errors
2. **Language Tags**: Verify code blocks have language tags
3. **Import Detection**: Find missing or incomplete imports
4. **Style Consistency**: Check indentation and formatting
5. **Completeness**: Detect incomplete or placeholder code
6. **Best Practices**: Flag anti-patterns in examples

## When to Use

Activate this skill when user requests:
- "Validate code in [file]"
- "Check code examples"
- "Find code issues"
- "Verify Kotlin/Java syntax"
- "Code quality check"
- After creating algorithm questions
- During technical content review

## Prerequisites

Required context:
- Access to note files
- Understanding of code block syntax
- Knowledge of common programming patterns

## Supported Languages

### Primary (Full Validation)
- **Kotlin**: Syntax, coroutines, Android patterns
- **Java**: Syntax, Android patterns
- **Python**: Syntax, algorithms

### Secondary (Basic Checks)
- SQL, Gradle, XML, JSON, YAML
- Shell/Bash scripts
- Markdown code blocks

## Process

### Step 1: Extract Code Blocks

Parse markdown for code blocks:

```
Find patterns:
```language
code content
```

Extract:
- Language tag (if present)
- Code content
- Line numbers in file
- Context (EN answer, RU answer, etc.)
```

### Step 2: Validate Language Tags

Check all code blocks have tags:

```markdown
# GOOD
```kotlin
fun example() { }
```

# BAD - Missing tag
```
fun example() { }
```

# BAD - Generic tag
```code
fun example() { }
```
```

### Step 3: Syntax Validation

Check language-specific syntax:

```
Kotlin checks:
- Balanced braces, parentheses, brackets
- Valid keywords and identifiers
- Proper function/class declarations
- String template syntax
- Lambda syntax

Java checks:
- Semicolon placement
- Class structure
- Generic syntax
- Method declarations

Python checks:
- Indentation consistency
- Colon placement
- Valid keywords
```

### Step 4: Import Analysis

Detect missing imports:

```kotlin
// Code uses:
fun example(): Flow<Int> = flow { emit(1) }

// Required imports:
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

// Check if imports mentioned or implied
```

### Step 5: Completeness Check

Detect incomplete code:

```
Flags:
- TODO comments
- "..." or "// ..." placeholders
- Empty function bodies that shouldn't be
- Unfinished statements
- Missing return statements
- Commented-out code

Example issues:
fun calculate(): Int {
    // TODO: implement
}

fun process(data: List<Int>) {
    ...  // Placeholder
}
```

### Step 6: Style Analysis

Check consistency:

```
Style checks:
- Consistent indentation (spaces vs tabs)
- Consistent brace style
- Reasonable line length
- Proper spacing around operators
- Naming conventions

Example issue:
fun badStyle(){  // Missing space before {
return 42}       // Missing newline and space
```

### Step 7: Generate Report

Produce code validation report:

```markdown
# Code Validation Report

**File**: q-coroutine-example--kotlin--medium.md
**Code Blocks Found**: 5
**Issues**: 3

---

## Summary

| Check | Passed | Failed |
|-------|--------|--------|
| Language Tags | 4 | 1 |
| Syntax | 5 | 0 |
| Imports | 3 | 2 |
| Completeness | 4 | 1 |
| Style | 5 | 0 |

---

## Issues Found

### Issue 1: Missing Language Tag (Line 45)

```
// No language tag on this code block
fun example() { }
```

**Fix**: Add `kotlin` language tag

### Issue 2: Missing Import (Line 67)

```kotlin
suspend fun fetchData(): `Flow`<Data> {
    return flow { emit(fetchFromApi()) }
}
```

**Missing imports**:
- `kotlinx.coroutines.flow.Flow`
- `kotlinx.coroutines.flow.flow`

**Fix**: Add import statements or note in text

### Issue 3: Incomplete Code (Line 89)

```kotlin
fun processItems(items: `List`<Item>) {
    // TODO: implement processing
}
```

**Issue**: TODO placeholder in example code

**Fix**: Provide complete implementation

---

## Code Quality Suggestions

1. Consider adding comments explaining key parts
2. Break long functions into smaller examples
3. Show both setup and usage in examples

---

**All syntax checks passed. Fix 3 minor issues for complete compliance.**
```

## Examples

### Example 1: Validate Single File

**User**: "Check code in q-coroutine-scope--kotlin--medium.md"

**Output**:
```markdown
# Code Check: q-coroutine-scope--kotlin--medium.md

Code blocks: 4
Language: All Kotlin

## Results
- Syntax: 4/4 valid
- Language tags: 4/4 present
- Imports: 3/4 clear
- Completeness: 4/4 complete

## Issue
Block 3 (line 78): Uses `CoroutineScope` without import note

Suggestion: Add comment `// import kotlinx.coroutines.CoroutineScope`

Overall: GOOD (1 minor suggestion)
```

### Example 2: Batch Code Validation

**User**: "Validate code in all algorithm notes"

**Output**:
```markdown
# Code Validation: 20-Algorithms/

Files: 9
Code blocks: 47

## Summary
| Status | Count |
|--------|-------|
| Fully valid | 6 |
| Minor issues | 2 |
| Needs attention | 1 |

## Issues by File

### q-binary-search--algorithms--medium.md
- Missing language tag on block 2

### q-merge-sort--algorithms--hard.md
- Python indentation inconsistent
- TODO comment in example

### q-graph-traversal--algorithms--hard.md
- Incomplete BFS implementation

## Statistics
- Most common issue: Missing language tags (3)
- Languages used: Kotlin (28), Python (12), Java (7)
```

### Example 3: Fix Suggestions

**User**: "Find and fix code issues in 70-Kotlin/"

**Output**:
```markdown
# Code Issues: 70-Kotlin/

Files scanned: 358
Files with issues: 23

## Auto-Fixable Issues

### Missing Language Tags (12 files)
Can automatically add `kotlin` tag to unmarked blocks.

Apply fix? [yes/no]

### Style Issues (8 files)
Can fix spacing around braces.

Apply fix? [yes/no]

## Manual Review Required

### Incomplete Examples (3 files)
1. q-flow-custom--kotlin--hard.md (line 45): TODO in code
2. q-channel-select--kotlin--hard.md (line 67): Empty when branch
3. q-dsl-builder--kotlin--hard.md (line 89): Placeholder implementation

Please complete these examples manually.
```

### Example 4: Language-Specific Check

**User**: "Validate all Kotlin code for Android patterns"

**Output**:
```markdown
# Kotlin Android Code Review

## Pattern Checks

### Lifecycle Awareness
- 45 examples use lifecycle correctly
- 3 examples may have lifecycle issues:
  - q-viewmodel-scope--android--medium.md: viewModelScope used correctly
  - q-lifecycle-observer--android--medium.md: Missing null check

### Coroutine Usage
- 67 examples use coroutines
- 2 potential issues:
  - GlobalScope usage (discouraged)
  - Missing exception handling

### Compose Patterns
- 34 Compose examples
- All follow recommended patterns

## Recommendations
1. Replace GlobalScope with structured concurrency
2. Add error handling to suspend functions
3. Consider adding @Preview annotations to Compose examples
```

## Error Handling

### Unparseable Code

**Problem**: Code too malformed to parse

**Solution**:
1. Report as unparseable
2. Show the problematic section
3. Suggest manual review

### Mixed Languages

**Problem**: Code block contains multiple languages

**Solution**:
1. Detect primary language
2. Note mixed content
3. Suggest splitting into separate blocks

### Pseudocode

**Problem**: Code is intentionally pseudocode

**Solution**:
1. Detect pseudocode patterns
2. Accept as valid if tagged correctly
3. Suggest using `pseudocode` or `text` tag

## Validation Levels

### Strict Mode
```
All checks enabled, report all issues.
Best for final review.
```

### Standard Mode (Default)
```
Common issues only.
Skip style nitpicks.
```

### Lenient Mode
```
Only critical issues (syntax errors, missing tags).
For quick checks.
```

## Integration with Other Skills

**Workflow: Content Creation**
1. Create Q&A with `obsidian-qna-creator`
2. Add code examples
3. Run `code-validator`
4. Fix issues before publishing

**Workflow: Content Review**
1. Run `batch-validator` for YAML
2. Run `code-validator` for code
3. Run `translation-auditor` for translations
4. Address all issues

## Validation Options

### By Language
```
--lang kotlin: Only validate Kotlin blocks
--lang python: Only validate Python blocks
```

### By Check Type
```
--syntax-only: Only syntax validation
--tags-only: Only language tag check
--imports: Include import analysis
```

### Auto-Fix
```
--fix: Apply safe automatic fixes
--fix-tags: Only fix language tags
```

## Notes

**Non-Destructive**: Default mode only reports, doesn't modify.

**Language-Aware**: Different rules for different languages.

**`Context`-Sensitive**: Understands interview question context.

**Practical**: Focuses on issues that matter for learning.

**Extensible**: Easy to add new language support.

---

**Version**: 1.0
**Last Updated**: 2025-01-05
**Status**: Production Ready
