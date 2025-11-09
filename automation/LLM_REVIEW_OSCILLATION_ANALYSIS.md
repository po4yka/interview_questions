# LLM Review Oscillation Detection - Root Cause Analysis

**Date**: 2025-11-09
**Issue**: False oscillation detection preventing fixes from being applied
**Severity**: HIGH - Blocks automated review workflow

---

## Executive Summary

The LLM review agent is triggering false oscillation detection on the **first iteration**, preventing the fixer agent from ever running. The root cause is that issue signatures are being recorded twice without any intervening fix attempts, creating the appearance of oscillation when no fixes have been attempted yet.

---

## Reproduction Case

### Test File
`InterviewQuestions/70-Kotlin/q-abstract-class-vs-interface--kotlin--medium.md`

### Command
```bash
uv run vault-app llm-review --dry-run --pattern "InterviewQuestions/70-Kotlin/q-abstract-class-vs-interface--kotlin--medium.md"
```

### Observed Behavior
```
INFO     | Running initial technical review
INFO     | Technical review made changes: [Kotlin technical corrections]
INFO     | Running validators (iteration 1)
INFO     | Found 4 total issues (2 metadata + 2 structural + 0 parity)
ERROR    | CIRCUIT BREAKER TRIGGERED: Oscillation detected - stopping iteration.
         | Oscillation detected: All 4 issue(s) from iteration 0 reappeared in iteration 1.
         | Fixer likely reversed its own changes.
```

### Actual Issues Found
1. **ERROR**: `updated` date (2025-01-25) is earlier than `created` date (2025-10-05)
2. **ERROR**: Wikilink `[[c-oop-fundamentals]]` does not match any note filename
3. **WARNING**: Related field should include at least 1 concept link (c-...)
4. **(Implied)**: Source URL should be quoted in YAML

---

## Root Cause Analysis

### Issue 1: Double Recording of Issue Signatures

**Location**: `automation/src/obsidian_vault/llm_review/graph.py`

The workflow records issues **twice** in the same iteration:

1. **First recording** - In `_run_validators()` (line 542):
```python
# STEP 5: Record issues for oscillation detection
next_state.record_current_issues()

# STEP 6: Check for oscillation
is_oscillating, oscillation_msg = next_state.detect_oscillation()
```

2. **Second recording** - In `_check_bilingual_parity()` (line 614):
```python
# PHASE 1 FIX: Record current issues for oscillation detection
state_obj.record_current_issues()
```

**Result**: `issue_history` contains duplicate entries:
```python
issue_history = [
    {issue1, issue2, issue3, issue4},  # From run_validators
    {issue1, issue2, issue3, issue4},  # From check_bilingual_parity (DUPLICATE)
]
```

### Issue 2: Oscillation Detection Logic

**Location**: `automation/src/obsidian_vault/llm_review/state.py` (lines 240-256)

```python
if len(self.issue_history) >= 2:
    current_issues = self.issue_history[-1]
    previous_issues = self.issue_history[-2]

    reverted_issues = current_issues & previous_issues

    if len(reverted_issues) > 0 and len(reverted_issues) == len(current_issues):
        # ALL current issues are from previous iteration = oscillation
        explanation = (
            f"Oscillation detected: All {len(reverted_issues)} issue(s) from "
            f"iteration {self.iteration - 1} reappeared in iteration {self.iteration}. "
            f"Fixer likely reversed its own changes."
        )
        return True, explanation
```

**Problem**: The logic correctly detects that all issues from the previous snapshot match the current snapshot. However, it incorrectly assumes this means the fixer reversed its changes, when in fact **the fixer never ran at all**.

### Issue 3: Premature Oscillation Check

**Location**: Workflow decision logic in `_compute_decision()` (line 1495)

```python
# PHASE 1 FIX: Circuit breaker for oscillation detection
is_oscillating, oscillation_explanation = state.detect_oscillation()
if is_oscillating:
    message = (...)
    return "summarize_failures", message
```

**Problem**: Oscillation is checked **before** the fixer has had a chance to run even once. The workflow is:

```
initial_llm_review → run_validators → check_bilingual_parity → [DECISION] → llm_fix_issues
                                                                      ↑
                                                                 Oscillation check
                                                                 blocks progression!
```

---

## Why the Fixer Never Runs

### Workflow Sequence

1. **`initial_llm_review`** (iteration 0):
   - Makes technical content corrections
   - Does NOT address metadata/structural issues
   - State: `iteration=0, issue_history=[]`

2. **`run_validators`** (increments to iteration 1):
   - Finds 4 metadata/structural issues
   - Records issues: `issue_history = [{4 issues}]`
   - State: `iteration=1, issue_history=[{4 issues}]`

3. **`check_bilingual_parity`**:
   - Records issues AGAIN: `issue_history = [{4 issues}, {4 issues}]`
   - Calls `_compute_decision()`
   - `detect_oscillation()` sees duplicate entries → **FALSE POSITIVE**
   - Decision: `"summarize_failures"` (circuit breaker)
   - Workflow: `END` ❌ (never reaches `llm_fix_issues`)

### Expected Workflow

The correct flow should be:
```
initial_llm_review → run_validators → check_bilingual_parity → llm_fix_issues → run_validators (iteration 2)
                                                                      ↓
                                                              First fix attempt
```

Only AFTER the fixer runs should oscillation detection be meaningful.

---

## Impact Assessment

### Critical Impact
- **Fixer never executes**: Simple metadata fixes (dates, links, quotes) are never attempted
- **All notes fail QA**: Even notes with trivial fixable issues are marked as requiring human review
- **Workflow paralysis**: Automation is effectively disabled for any note with validation issues

### False Negatives
The technical review agent correctly identified and fixed Kotlin content issues, proving the agent works. But metadata issues are **never given to the fixer**.

### User Experience
From the output:
```
WARNING  | Automated review failed for InterviewQuestions/70-Kotlin/q-abstract-class-vs-interface--kotlin--medium.md:
The automated workflow halted early due to oscillation: after one validator pass,
the same four metadata/link issues remained unchanged, so the system stopped instead of looping.
```

This message is **misleading** - it suggests the fixer tried and failed, when in reality the fixer was never invoked.

---

## Proposed Solutions

### Solution 1: Remove Duplicate Recording (RECOMMENDED)

**Change**: Remove the second `record_current_issues()` call from `check_bilingual_parity()`

**File**: `automation/src/obsidian_vault/llm_review/graph.py`, line 614

**Rationale**:
- Issue recording should happen once per iteration
- Recording belongs in `run_validators()` after issues are found
- `check_bilingual_parity()` is just a decision node, not a validation node

**Implementation**:
```python
# In _check_bilingual_parity()
# REMOVE THIS:
# state_obj.record_current_issues()

# Keep only decision logic:
decision, decision_message = self._compute_decision(state_obj)
```

### Solution 2: Delay Oscillation Detection Until After First Fix

**Change**: Only enable oscillation detection after iteration 2 (after fixer has run at least once)

**File**: `automation/src/obsidian_vault/llm_review/state.py`, line 227

**Implementation**:
```python
def detect_oscillation(self) -> tuple[bool, str | None]:
    """Detect if the same issues are reappearing across iterations."""

    # Don't check for oscillation until after first fix attempt
    # Iteration 1: Initial validation finds issues
    # Iteration 2: After first fix attempt - now oscillation is meaningful
    if self.iteration < 2:
        return False, None

    # STRATEGY 1: Immediate reversal detection
    if len(self.issue_history) >= 2:
        # ... existing logic ...
```

**Rationale**:
- Oscillation only makes sense after a fix attempt
- Iteration 1 is always the "baseline" of issues
- Iteration 2+ is where we check if fixes worked

### Solution 3: Separate Initial Issues from Fix Iterations

**Change**: Track "initial issues" separately from "post-fix issues"

**File**: `automation/src/obsidian_vault/llm_review/state.py`

**Implementation**:
```python
@dataclass
class NoteReviewState:
    initial_issues: set[str] | None = None  # First validation pass
    issue_history: list[set[str]] = field(default_factory=list)  # Post-fix iterations

    def record_current_issues(self) -> None:
        """Record current issues for oscillation detection."""
        current_signatures = {
            f"{issue.severity}:{issue.message}" for issue in self.issues
        }

        # First recording establishes baseline
        if self.initial_issues is None:
            self.initial_issues = current_signatures
            logger.debug("Recorded initial issues (baseline)")
        else:
            self.issue_history.append(current_signatures)
            logger.debug(f"Recorded issues after fix attempt (history: {len(self.issue_history)})")

    def detect_oscillation(self) -> tuple[bool, str | None]:
        """Detect oscillation only after fix attempts."""
        # Need at least one fix attempt (issue_history has post-fix snapshots)
        if len(self.issue_history) < 1:
            return False, None

        # Compare fix attempts (not including initial baseline)
        if len(self.issue_history) >= 2:
            current = self.issue_history[-1]
            previous = self.issue_history[-2]
            # ... oscillation logic ...
```

**Rationale**:
- Clearly separates "what issues were found" from "what issues remain after fixes"
- Makes oscillation detection semantically correct
- Prevents false positives from comparing pre-fix to pre-fix states

---

## Recommended Fix (Minimal Change)

**Primary Fix**: Solution 1 (Remove duplicate recording)

**Validation**: Add logging to show when issues are recorded:

```python
# In run_validators()
logger.info(f"Recording issue state after validation (iteration {next_state.iteration})")
next_state.record_current_issues()
logger.debug(f"Issue history: {len(next_state.issue_history)} snapshot(s)")

# In check_bilingual_parity()
# Remove: state_obj.record_current_issues()
# Add instead:
logger.debug(f"Using existing issue recording from validators (history: {len(state_obj.issue_history)})")
```

**Testing**:
1. Re-run the test case with fix applied
2. Verify fixer runs at least once before oscillation can be detected
3. Verify actual oscillation (repeated failed fixes) is still caught

---

## Secondary Issues Identified

### Issue A: Technical Review vs Metadata Fixes

**Problem**: The `initial_llm_review` agent focuses on technical content, not metadata issues.

**Example**: In the test case, it fixed Kotlin technical details but ignored:
- Invalid dates
- Missing wikilinks
- Malformed YAML

**Root Cause**: Different LLM prompts for technical vs structural fixes.

**Impact**: Two-phase workflow required (technical → structural), adding iteration overhead.

**Recommendation**:
1. Keep separation (technical review is complex, metadata fixes are simple)
2. Ensure fixer agent has clear instructions for metadata fixes
3. Consider: Can initial review skip if only metadata issues exist?

### Issue B: Misleading Error Messages

**Current Message**:
```
"after one validator pass, the same four metadata/link issues remained unchanged"
```

**Problem**: Implies fixer tried and failed. Actually, fixer never ran.

**Recommendation**:
```
"Workflow halted: Oscillation detected before fix agent could run.
This is likely a false positive. Issues found: [list issues]
Recommended action: Run with --max-iterations 3 to allow fix attempts."
```

### Issue C: Issue Recording Semantics

**Current**: `record_current_issues()` is called in multiple nodes

**Problem**: Unclear ownership - who is responsible for recording?

**Recommendation**:
- Recording should be ownership of `run_validators` only
- Other nodes should only READ from issue_history
- Add assertion: "Issue recording must happen exactly once per validation pass"

---

## Test Plan

### Unit Test: No False Positives
```python
def test_no_oscillation_before_fix_attempt():
    state = NoteReviewState(...)

    # Iteration 1: Find issues
    state.issues = [issue1, issue2, issue3, issue4]
    state.record_current_issues()

    # Should NOT detect oscillation (no fix attempted yet)
    is_oscillating, msg = state.detect_oscillation()
    assert not is_oscillating, "False positive: oscillation detected before any fix attempt"
```

### Integration Test: Real Oscillation Detected
```python
def test_real_oscillation_detected():
    state = NoteReviewState(...)

    # Iteration 1: Find issues
    state.issues = [issue1, issue2]
    state.record_current_issues()

    # Iteration 2: After fix, same issues remain
    state.issues = [issue1, issue2]
    state.record_current_issues()

    # NOW oscillation should be detected
    is_oscillating, msg = state.detect_oscillation()
    assert is_oscillating, "Real oscillation not detected"
```

### End-to-End Test: Successful Fix
```bash
# Test with the problematic note
uv run vault-app llm-review --dry-run \
  --pattern "InterviewQuestions/70-Kotlin/q-abstract-class-vs-interface--kotlin--medium.md"

# Expected outcome:
# ✓ Iteration 1: 4 issues found
# ✓ Fix agent runs
# ✓ Iteration 2: Issues reduced (dates fixed, links added)
# ✓ Fix agent runs again
# ✓ Iteration 3: All issues resolved OR legitimate oscillation detected
```

---

## Additional Recommendations

### 1. Agent Instructions - Fixer Scope

**Current**: Fixer agent focuses on structural and formatting issues

**Problem**: May not be prompted to fix simple metadata issues like dates

**Recommendation**: Enhance fixer prompt with explicit metadata fix examples:

```markdown
COMMON METADATA FIXES:

1. **Date Consistency**: If 'updated' < 'created', set updated = created
2. **Missing Links**: If [[c-foo]] is referenced but doesn't exist, remove it or create stub
3. **YAML Formatting**: Ensure sources are quoted: `sources: ["https://..."]`
4. **Related Field**: Ensure at least 1 concept link (c-*) is present
```

### 2. Iteration Budget Awareness

**Current**: Max iterations = 10 (default)

**Problem**: False oscillation wastes iterations

**Recommendation**:
- Reserve iterations for actual fixes, not false positives
- Add budget tracking: "Used 1 of 10 iterations for validation, 0 for fixes"
- Warn if too many iterations spent on validation vs fixing

### 3. Separate Validation from Decision

**Current**: `check_bilingual_parity()` does both validation AND decision

**Recommendation**: Split into two nodes:
- `record_issues`: Pure recording, no decision
- `decide_next_action`: Pure decision, no state modification

**Benefits**:
- Clearer separation of concerns
- Easier to test
- Less chance of duplicate operations

### 4. Fix Memory Integration

**Observed**: Fix Memory system exists to prevent re-modifying fixed fields

**Question**: Is Fix Memory being used correctly in this case?

**Action**: Verify that Fix Memory:
1. Tracks when 'updated' field is fixed (date correction)
2. Prevents fixer from changing 'updated' again
3. Allows targeted fixes to other fields

---

## Conclusion

The false oscillation detection is caused by recording the same issue state twice before any fix attempt occurs. The recommended fix is to remove the duplicate recording in `check_bilingual_parity()` and ensure issue recording happens exactly once per validation pass in `run_validators()`.

**Priority**: HIGH - This blocks all automated reviews
**Complexity**: LOW - Single line removal + verification
**Risk**: LOW - Improves correctness, no functionality loss

**Next Steps**:
1. Apply Solution 1 (remove duplicate recording)
2. Add logging to track issue recording
3. Run test case to verify fixer executes
4. Monitor for legitimate oscillation detection in future runs

---

## Appendix: Code Locations

### Key Files
- **Workflow**: `automation/src/obsidian_vault/llm_review/graph.py`
- **State**: `automation/src/obsidian_vault/llm_review/state.py`
- **Validators**: `automation/src/obsidian_vault/validators/*.py`

### Critical Functions
- `_run_validators()` - Line 288-587
- `_check_bilingual_parity()` - Line 589-665
- `_compute_decision()` - Line 1457-1550
- `detect_oscillation()` - Line 227-298
- `record_current_issues()` - Line 219-225

### Workflow Graph
```
START
  ↓
initial_llm_review (technical content)
  ↓
run_validators (finds 4 issues, records them, iteration=1)
  ↓
check_bilingual_parity (records AGAIN → false oscillation!)
  ↓
[DECISION: summarize_failures] ← STOPS HERE
  ↓
❌ llm_fix_issues (NEVER REACHED)
```

**Expected Graph**:
```
START → initial_llm_review → run_validators → check_bilingual_parity
  → llm_fix_issues → run_validators (iteration 2) → check_bilingual_parity
  → [DECISION: continue or done]
```
