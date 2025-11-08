# QA/Critic Agent Implementation

**Date**: 2025-11-08
**Feature**: Post-fix QA/Critic Agent for Exit Condition Guarding

## Overview

Added a final QA/critic agent that runs AFTER all validator issues are resolved and BEFORE marking a note as complete. This ensures that the iterative fix process didn't introduce new factual errors or break bilingual parity.

## Problem Solved

Previously, the workflow would exit when validator issues were gone or iteration limits were hit, with no LLM re-check to ensure:
- Fixes didn't introduce new factual errors
- Bilingual parity (EN/RU semantic equivalence) is maintained
- Overall technical quality is acceptable

## Implementation

### 1. New Agent (`agents.py`)

**Added `QAVerificationResult` model:**
- `is_acceptable: bool` - Pass/fail decision
- `factual_errors: list[str]` - Critical technical errors
- `bilingual_parity_issues: list[str]` - EN/RU semantic mismatches
- `quality_concerns: list[str]` - Non-critical improvements
- `summary: str` - Brief verification summary

**Added `QA_VERIFICATION_PROMPT`:**
- Focused on factual accuracy, bilingual parity, and content quality
- Does NOT re-check detailed YAML validation (validators already did this)
- Pragmatic: blocks completion only for serious issues

**Added `run_qa_verification()` function:**
- Async function that runs the QA agent
- Takes note text, path, and iteration count
- Returns pass/fail decision with detailed findings

### 2. Updated State (`state.py`)

**Added to `NoteReviewState` and `NoteReviewStateDict`:**
- `qa_verification_passed: bool | None` - QA result
- `qa_verification_summary: str | None` - Summary message

### 3. Updated Workflow (`graph.py`)

**New workflow flow:**
```
initial_llm_review → metadata_sanity_check → run_validators
                                                   ↓
                                    [Has validator issues?]
                                                   ↓
                        YES: llm_fix_issues ←──────┴──────→ NO: qa_verification
                              ↓                                      ↓
                              └──────────────────────────────→ [QA passed?]
                                                                     ↓
                                                   YES: END ←────────┴──────→ NO: llm_fix_issues
```

**Added `_qa_verification` node:**
- Runs QA verification check
- If QA passes: marks as complete, returns "done"
- If QA fails: converts QA findings to ReviewIssues, routes to fix loop

**Updated `_compute_decision` logic:**
1. Max iterations reached → done
2. Error occurred → done
3. Completed flag set → done
4. **No validator issues AND QA not run yet → qa_verify** ⭐ NEW
5. **No validator issues AND QA passed → done** ⭐ NEW
6. Validator issues remain → continue

**Added `_should_continue_after_qa` router:**
- Routes to "done" if QA passed
- Routes to "continue" (back to fix loop) if QA failed

## Benefits

1. **Prevents factual regressions**: Catches technical errors introduced during fixes
2. **Ensures bilingual quality**: Verifies EN/RU semantic equivalence
3. **Reduces false positives**: Only blocks completion for serious issues
4. **Provides transparency**: QA summary logged in history for debugging
5. **Maintains iteration limit**: QA issues count toward max_iterations, preventing infinite loops

## Usage

No changes needed for end users. The QA verification runs automatically when:
- All validator issues are resolved
- Before marking the note as complete

The QA verification result is:
- Logged to history
- Stored in state (`qa_verification_passed`, `qa_verification_summary`)
- Used to decide whether to complete or continue fixing

## Testing

To test the QA verification:
1. Run the LLM review workflow on a note
2. Check the logs for "Running final QA verification"
3. Verify the QA result is logged (passed or failed)
4. If failed, verify QA issues are converted to ReviewIssues for fixing

## Configuration

QA verification uses the same OpenRouter configuration as other agents:
- Model: `OPENROUTER_MODEL` (default: anthropic/claude-sonnet-4)
- Temperature: `OPENROUTER_TEMPERATURE` (default: 0.2)
- Timeout: `OPENROUTER_TIMEOUT` (default: 60.0)

## Files Modified

1. `automation/src/obsidian_vault/llm_review/agents.py` - Added QA agent
2. `automation/src/obsidian_vault/llm_review/state.py` - Added QA tracking fields
3. `automation/src/obsidian_vault/llm_review/graph.py` - Integrated QA into workflow

## Future Enhancements

Potential improvements:
1. Add configurable QA strictness levels (strict/normal/lenient)
2. Track QA verification metrics (pass rate, common issues)
3. Add QA cache to avoid re-verifying unchanged content
4. Support QA-only mode (skip validators, run QA only)
