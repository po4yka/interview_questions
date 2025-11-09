# LLM-Review Agent System Issues & Fixes

**Analysis Date**: 2025-11-09
**Based On**: Review logs from `llm-review --dry-run --pattern "InterviewQuestions/70-Kotlin/**/*.md"`

## Executive Summary

The llm-review agent system exhibits several critical issues causing:
- **Oscillation**: Issue counts increase after fixes are applied
- **Inefficiency**: 3-4 iterations per note, 7-15 minutes processing time
- **Instability**: Fixes in one iteration break previously fixed fields
- **Poor convergence**: Validators detect issues that fixer re-introduces

---

## Issue #1: Fix Oscillation (Critical)

### Symptoms
```
[Iteration 2/10] Issues: 2 (was 16, Δ+14, +87.5%)  ← Good reduction
[Iteration 3/10] Issues: 4 (was 5, Δ+1, +20.0%)   ← Issue count INCREASED!
[Iteration 4/10] Issues: 2 (was 10, Δ+8, +80.0%)  ← Oscillating
```

### Evidence from Logs
**q-channel-pipelines--kotlin--hard.md**:
- Iteration 1: 16 total issues (5 validator + 11 parity)
- Iteration 2: 5 total issues (2 validator + 3 parity)
- Iteration 3: 10 total issues (4 validator + 6 parity) ← INCREASED
- Iteration 4: 2 total issues (2 validator + 0 parity)

**q-instant-search-flow-operators--kotlin--medium.md**:
- Iteration 1: 23 issues (10 validator + 13 parity)
- Iteration 2: 9 issues (2 validator + 7 parity) ← Parity issues persist
- Iteration 3: 2 issues (2 validator + 0 parity)

### Root Causes

#### 1.1 Fixer Lacks Context Across Iterations
The fixer agent receives issues to fix but doesn't track:
- Which fields were already fixed
- Which values were considered valid in previous iterations
- Constraints from previous fixes

**Example from logs**:
```
Iteration 2: "Updated timestamps from future dates to realistic past dates (2024-10-12)"
Iteration 3: "Updated 'updated' timestamp to a current valid date (2025-11-09)"
```
The fixer changed timestamps AGAIN in iteration 3, despite fixing them in iteration 2!

#### 1.2 Conflicting Fix Priorities
Different fixes can conflict:

**Example from logs**:
```
Iteration 2: "Added foundational concept links ([[c-kotlin]], [[c-coroutines]]) to 'related' field."
Iteration 3: "Reduced 'related' list to 4 items to stay within recommended 2-5 range."
```

The system:
1. First adds links to fix "missing concepts"
2. Then removes links to fix "too many related items"
3. This could remove the links that were just added!

#### 1.3 Cascading Side Effects
Fixes to one field trigger new issues in related fields:

**Example from logs**:
```
Iteration 2: "Added missing RU sections mirroring EN: Fan-Out with Load Balancing,
             Fan-In with Priority, Real-World Pipeline: Data ETL..."
Iteration 3: "Renamed '### Мониторинг и метрики конвейера (RU)' to
             '### Мониторинг и метрики конвейера' to remove language-specific suffix"
```

Adding RU sections (iteration 2) introduced incorrectly named sections, which then needed fixing (iteration 3).

### Impact
- **Performance**: Extra iterations waste tokens and time
- **Reliability**: System may converge to suboptimal state
- **User Experience**: Notes take 7-15 minutes to process

### Proposed Fixes

#### Fix 1.A: Implement Fix Memory
**Location**: `automation/src/obsidian_vault/llm_review/agents/fixer.py`

Add a `FixMemory` class to track what's been fixed:

```python
@dataclass
class FixMemory:
    """Tracks fields modified across iterations to prevent re-fixing."""
    fixed_fields: Set[str] = field(default_factory=set)
    fixed_values: Dict[str, Any] = field(default_factory=dict)
    iteration_fixes: List[Set[str]] = field(default_factory=list)

    def mark_fixed(self, field_path: str, value: Any, iteration: int):
        """Record that a field was fixed."""
        self.fixed_fields.add(field_path)
        self.fixed_values[field_path] = value

    def is_fixed(self, field_path: str) -> bool:
        """Check if field was already fixed."""
        return field_path in self.fixed_fields

    def get_fixed_value(self, field_path: str) -> Optional[Any]:
        """Get the value that was set when fixing."""
        return self.fixed_values.get(field_path)
```

**Modify fixer prompt to include**:
```
Previously fixed fields (DO NOT MODIFY):
{memory.fixed_fields}

Previously set values:
{memory.fixed_values}

When fixing issues, you MUST NOT modify fields that were already fixed.
If a field appears in both "issues to fix" and "previously fixed",
SKIP that issue and explain why in your reasoning.
```

#### Fix 1.B: Implement Fix Validation
**Location**: `automation/src/obsidian_vault/llm_review/graph.py`

After applying fixes, immediately validate ONLY the changed fields:

```python
def validate_fixes(
    original_content: str,
    fixed_content: str,
    applied_fixes: List[str],
    memory: FixMemory
) -> Tuple[bool, List[str]]:
    """
    Validate that fixes didn't break previously fixed fields.

    Returns:
        (is_valid, list_of_regressions)
    """
    regressions = []

    # Parse both versions
    orig_yaml, orig_body = parse_note(original_content)
    fixed_yaml, fixed_body = parse_note(fixed_content)

    # Check each previously fixed field
    for field_path in memory.fixed_fields:
        expected_value = memory.get_fixed_value(field_path)
        actual_value = get_field(fixed_yaml, field_path)

        if actual_value != expected_value:
            regressions.append(
                f"Field '{field_path}' was changed from '{expected_value}' "
                f"to '{actual_value}', but it was already fixed in a previous iteration"
            )

    return (len(regressions) == 0, regressions)
```

#### Fix 1.C: Add Circuit Breaker for Oscillation
**Location**: `automation/src/obsidian_vault/llm_review/graph.py` in `should_continue_fixing()`

```python
def detect_oscillation(state: AgentState) -> bool:
    """Detect if issue count is oscillating instead of decreasing."""
    if len(state.history) < 3:
        return False

    # Get last 3 issue counts
    counts = [h.total_issues for h in state.history[-3:]]

    # Check if counts are oscillating (up-down-up or down-up-down)
    if counts[0] < counts[1] > counts[2]:  # valley pattern
        return True
    if counts[0] > counts[1] < counts[2]:  # peak pattern
        return True

    # Check if issue count increased for 2 consecutive iterations
    if counts[-2] < counts[-1] and counts[-3] < counts[-2]:
        return True

    return False

def should_continue_fixing(state: AgentState) -> Literal["fix_issues", "qa_verify", "complete"]:
    """Decide next step with oscillation detection."""

    # Existing logic...

    if detect_oscillation(state):
        logger.error(
            f"Oscillation detected in issue counts: "
            f"{[h.total_issues for h in state.history[-3:]]}"
        )
        return "complete"  # Fail-safe: stop iterating

    # ... rest of existing logic
```

---

## Issue #2: Parity Check Adds Issues Late (High Priority)

### Symptoms
```
INFO  | Running validators (iteration 1)
INFO  | Found 5 total issues (2 metadata + 3 structural)
INFO  | Running bilingual parity check (iteration 1)
WARNING | Parity check found 11 new parity issue(s) - total issues: 5 validator + 11 parity = 16
```

Parity check runs AFTER validators, discovering 11 additional issues that should have been caught earlier.

### Evidence from Logs
**q-channel-pipelines--kotlin--hard.md**:
- Validators found 5 issues
- Parity check found 11 MORE issues (5 issues + 6 missing sections)
- Total jumped from 5 → 16

**q-instant-search-flow-operators--kotlin--medium.md**:
- Validators found 10 issues
- Parity check found 13 MORE issues (3 issues + 10 missing sections)
- Total jumped from 10 → 23

### Root Cause
The workflow is sequential:
```
validators → parity_check → fixer
```

Parity issues (missing RU sections, inconsistent structure) aren't caught until AFTER structural validators run. This causes:
1. Fixer fixes structural issues
2. Then parity check discovers bilingual issues
3. Fixer has to run AGAIN
4. This wastes an entire iteration

### Impact
- **Extra Iterations**: Always requires at least 2 iterations (one for structure, one for parity)
- **Wasted Tokens**: Validators re-run on content that will be heavily modified by parity fixes
- **Poor User Experience**: Slow convergence

### Proposed Fixes

#### Fix 2.A: Run Parity Check in Parallel with Validators
**Location**: `automation/src/obsidian_vault/llm_review/graph.py` in `run_validators()`

Change from sequential to parallel execution:

**Current**:
```python
def run_validators(state: AgentState) -> AgentState:
    # Run structural validators first
    issues = []
    issues.extend(run_metadata_validator(state))
    issues.extend(run_structural_validator(state))

    # Then run parity check
    parity_issues = run_parity_check(state)
    issues.extend(parity_issues)

    return state
```

**Proposed**:
```python
def run_validators(state: AgentState) -> AgentState:
    """Run all validators in parallel to catch all issues in one pass."""

    # Run all validators concurrently
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(run_metadata_validator, state): "metadata",
            executor.submit(run_structural_validator, state): "structural",
            executor.submit(run_parity_check, state): "parity",
        }

        all_issues = []
        for future in as_completed(futures):
            validator_name = futures[future]
            try:
                issues = future.result()
                all_issues.extend(issues)
                logger.info(
                    f"{validator_name} validator found {len(issues)} issue(s)"
                )
            except Exception as e:
                logger.error(f"{validator_name} validator failed: {e}")

    # Deduplicate issues (in case validators overlap)
    unique_issues = deduplicate_issues(all_issues)

    state.issues = unique_issues
    return state
```

#### Fix 2.B: Prioritize Parity Issues First
**Location**: `automation/src/obsidian_vault/llm_review/agents/fixer.py`

Modify fixer to handle parity issues BEFORE structural issues:

```python
def prioritize_issues(issues: List[Issue]) -> List[Issue]:
    """
    Sort issues so parity/bilingual issues are fixed first.

    Rationale: Adding missing RU sections affects structure,
    so we should add content before fixing formatting.
    """
    priority_order = {
        "missing_section": 1,      # Missing RU/EN sections
        "parity_mismatch": 2,       # Content differences between langs
        "structural": 3,            # Section ordering, formatting
        "metadata": 4,              # YAML issues
    }

    return sorted(
        issues,
        key=lambda issue: priority_order.get(issue.category, 999)
    )
```

---

## Issue #3: Timestamps Keep Breaking (Medium Priority)

### Symptoms
Timestamps are "fixed" multiple times across iterations, oscillating between valid and invalid values.

### Evidence from Logs
**q-channel-pipelines--kotlin--hard.md**:
```
Iteration 1: "Updated timestamps from future dates to realistic past dates (2024-10-12)"
Iteration 3: "Updated 'updated' timestamp to a current valid date (2025-11-09)"
```

**q-instant-search-flow-operators--kotlin--medium.md**:
```
Iteration 1: "Changed created/updated timestamps from future dates to realistic past dates"
```

### Root Cause Analysis

#### 3.1 Inconsistent Timestamp Generation
The fixer agent generates timestamps without a clear specification:
- Sometimes uses "realistic past dates" (2024-10-12)
- Sometimes uses "current valid date" (2025-11-09)
- No clear policy on whether to preserve existing timestamps

#### 3.2 "Future Date" Detection is Buggy
The logs show warnings about "future dates" but the dates don't look wrong:
```
Updated timestamps from future dates to realistic past dates (2024-10-12)
```

If today is 2025-11-09, then 2024-10-12 is PAST, not future. This suggests:
- The warning message is misleading
- Or there's a bug in future-date detection

### Impact
- Wastes iterations on timestamp "fixes"
- May corrupt valid timestamps
- Confusing to users reviewing changes

### Proposed Fixes

#### Fix 3.A: Strict Timestamp Policy
**Location**: `automation/src/obsidian_vault/llm_review/agents/fixer.py`

Add explicit timestamp handling rules to fixer prompt:

```
TIMESTAMP RULES (CRITICAL - FOLLOW EXACTLY):

1. If timestamp is VALID (YYYY-MM-DD format, <= today), DO NOT MODIFY IT
2. If timestamp is MISSING:
   - For 'created': Use the file creation date from git history
   - For 'updated': Use today's date (2025-11-09)
3. If timestamp is INVALID (future date, bad format):
   - For 'created': Use today's date
   - For 'updated': Use today's date

NEVER generate timestamps in any other way.
NEVER "update" a valid timestamp just because it's old.
```

#### Fix 3.B: Add Timestamp Validator
**Location**: `automation/src/obsidian_vault/llm_review/validators/metadata.py`

Create a dedicated timestamp validator:

```python
def validate_timestamps(note_content: str) -> List[Issue]:
    """
    Validate timestamp fields in YAML frontmatter.

    Rules:
    - Must be in YYYY-MM-DD format
    - Must not be in the future
    - 'created' must be <= 'updated'
    """
    issues = []
    yaml, _ = parse_note(note_content)

    today = datetime.now().date()

    for field in ['created', 'updated']:
        if field not in yaml:
            issues.append(Issue(
                severity='ERROR',
                category='metadata',
                field=field,
                message=f"Missing required timestamp field '{field}'"
            ))
            continue

        try:
            date_value = datetime.strptime(yaml[field], '%Y-%m-%d').date()
        except ValueError:
            issues.append(Issue(
                severity='ERROR',
                category='metadata',
                field=field,
                message=f"Invalid date format in '{field}': {yaml[field]} (expected YYYY-MM-DD)"
            ))
            continue

        if date_value > today:
            issues.append(Issue(
                severity='ERROR',
                category='metadata',
                field=field,
                message=f"Future date in '{field}': {yaml[field]} (today is {today})"
            ))

    # Check created <= updated
    if 'created' in yaml and 'updated' in yaml:
        try:
            created = datetime.strptime(yaml['created'], '%Y-%m-%d').date()
            updated = datetime.strptime(yaml['updated'], '%Y-%m-%d').date()
            if created > updated:
                issues.append(Issue(
                    severity='WARNING',
                    category='metadata',
                    field='created,updated',
                    message=f"'created' ({created}) is after 'updated' ({updated})"
                ))
        except ValueError:
            pass  # Already caught above

    return issues
```

#### Fix 3.C: Mark Timestamps as Fixed
Use Fix Memory (from Issue #1) to prevent re-fixing:

```python
# In fixer agent, after fixing timestamps
memory.mark_fixed('metadata.created', fixed_created_date, iteration)
memory.mark_fixed('metadata.updated', fixed_updated_date, iteration)
```

---

## Issue #4: Excessive Processing Time (Medium Priority)

### Symptoms
- q-channel-pipelines--kotlin--hard.md: **885.36s** (~15 minutes)
- q-instant-search-flow-operators--kotlin--medium.md: **416.02s** (~7 minutes)

For a dry-run with 344 notes, this would take:
```
Average: ~650s/note
Total: 650 × 344 = 223,600s = 62 hours
```

### Root Causes

#### 4.1 Sequential Execution
Notes are processed one at a time (based on logs showing sequential "Processing: ..." entries).

#### 4.2 Multiple LLM Calls Per Iteration
Each iteration involves:
1. Technical review (LLM call)
2. Metadata validator (LLM call)
3. Structural validator (LLM call)
4. Parity checker (LLM call)
5. Fixer (LLM call)
6. QA verifier (LLM call)

For 4 iterations: 4 × 6 = **24 LLM calls per note**

#### 4.3 Large Context per Call
Each LLM call receives:
- Full note content
- Full validation history
- Full taxonomy
- Full examples

This increases latency and cost.

### Impact
- **Impractical for large batches**: 62 hours for full vault review
- **High cost**: 24 LLM calls × 344 notes = 8,256 API calls
- **Poor UX**: User waits 7-15 minutes per note

### Proposed Fixes

#### Fix 4.A: Parallel Note Processing
**Location**: `automation/src/obsidian_vault/llm_review/main.py`

Process multiple notes concurrently:

```python
async def review_notes_parallel(
    notes: List[Path],
    max_concurrent: int = 5
) -> List[ReviewResult]:
    """Process multiple notes in parallel with concurrency limit."""

    semaphore = asyncio.Semaphore(max_concurrent)

    async def review_with_limit(note_path: Path):
        async with semaphore:
            return await review_note(note_path)

    tasks = [review_with_limit(note) for note in notes]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return results
```

**Benefit**: 5× speedup with max_concurrent=5 → 12.4 hours instead of 62 hours

#### Fix 4.B: Reduce LLM Calls with Caching
**Location**: `automation/src/obsidian_vault/llm_review/agents/`

Implement response caching for validators:

```python
from functools import lru_cache
import hashlib

def content_hash(content: str) -> str:
    """Generate hash of note content for caching."""
    return hashlib.sha256(content.encode()).hexdigest()

@lru_cache(maxsize=1000)
def cached_validator(
    content_hash: str,
    validator_name: str,
    content: str  # Not used in cache key, but needed for actual validation
) -> List[Issue]:
    """Cache validator results by content hash."""
    if validator_name == "metadata":
        return run_metadata_validator_impl(content)
    elif validator_name == "structural":
        return run_structural_validator_impl(content)
    # ...
```

**Usage**:
```python
# Before calling validator
content_hash_val = content_hash(note_content)
issues = cached_validator(content_hash_val, "metadata", note_content)
```

**Benefit**: If content doesn't change between iterations, skip LLM call

#### Fix 4.C: Smart Validator Selection
Only run validators relevant to the changes made:

```python
def select_validators(
    prev_content: str,
    current_content: str,
    applied_fixes: List[str]
) -> List[str]:
    """
    Determine which validators need to run based on what changed.

    Returns list of validator names: ["metadata", "structural", "parity"]
    """
    validators_needed = set()

    # Parse changes
    prev_yaml, prev_body = parse_note(prev_content)
    curr_yaml, curr_body = parse_note(current_content)

    # If YAML changed, run metadata validator
    if prev_yaml != curr_yaml:
        validators_needed.add("metadata")

    # If body structure changed, run structural validator
    if get_section_structure(prev_body) != get_section_structure(curr_body):
        validators_needed.add("structural")

    # Always run parity check if either language changed
    if prev_body != curr_body:
        validators_needed.add("parity")

    return list(validators_needed)
```

**Benefit**: Skip unnecessary validators → fewer LLM calls

---

## Issue #5: Related Field Oscillation (Low Priority)

### Symptoms
The `related` field is modified multiple times:
- First adds links to fix "missing concepts"
- Then removes links to fix "too many items"

### Evidence from Logs
```
Iteration 1: "Added foundational concept links ([[c-kotlin]], [[c-coroutines]]) to 'related' field."
Iteration 3: "Reduced 'related' list to 4 items to stay within recommended 2-5 range."
```

### Root Cause
Conflicting validation rules:
1. "Must have at least 2 related links"
2. "Must have at most 5 related links"

When fixing (1), the fixer may overshoot and violate (2).

### Proposed Fix

#### Fix 5.A: Atomic Related Field Fixes
**Location**: `automation/src/obsidian_vault/llm_review/agents/fixer.py`

Add constraint to fixer prompt:

```
When fixing 'related' field:
1. Target exactly 3-4 items (middle of 2-5 range)
2. Prioritize concept links (c-*) over question links (q-*)
3. If adding links, add exactly enough to reach 3 items
4. If removing links, remove exactly enough to reach 4 items
5. Never add AND remove in the same iteration

CORRECT:
  related: [c-kotlin, c-flow]  → Add c-coroutines → [c-kotlin, c-flow, c-coroutines]

INCORRECT:
  related: [c-kotlin, c-flow]  → Add 5 links → Remove 3 links → ...
```

---

## Issue #6: Code Block Naming Changes (Low Priority)

### Symptoms
Fixer renames example classes in code blocks, potentially breaking compilation:

```
"Renamed RU example classes to align with EN naming (removed 'Ru' suffixes)
 while keeping code identical"
```

### Root Cause
Parity checker detects that RU code uses different class names than EN code (e.g., `DataPipelineRu` vs `DataPipeline`) and flags this as a "parity issue."

The fixer then renames classes to achieve "parity," but this:
- Changes semantics (different class names)
- May break if RU example is intentionally localized
- Wastes iteration on cosmetic change

### Impact
- Low severity (doesn't affect correctness)
- Wastes tokens on unnecessary changes

### Proposed Fix

#### Fix 6.A: Exclude Code Identifiers from Parity Check
**Location**: `automation/src/obsidian_vault/llm_review/validators/parity.py`

Modify parity checker to ignore identifier names:

```python
def normalize_code_for_parity(code: str, language: str) -> str:
    """
    Normalize code by replacing identifiers with placeholders.
    This allows comparing code structure while ignoring naming.
    """
    if language == "kotlin":
        # Replace class names: DataPipelineRu → CLASS_1
        code = re.sub(r'\bclass\s+\w+', 'class CLASS', code)
        # Replace function names: procesarDatos → FUNC_1
        code = re.sub(r'\bfun\s+\w+', 'fun FUNC', code)

    return code

def compare_code_blocks(en_code: str, ru_code: str, language: str) -> bool:
    """Check if code blocks are equivalent, ignoring identifier names."""
    en_normalized = normalize_code_for_parity(en_code, language)
    ru_normalized = normalize_code_for_parity(ru_code, language)

    return en_normalized == ru_normalized
```

---

## Issue #7: QA Verification May Pass Broken Notes (Low Priority)

### Symptoms
QA verification passes notes with remaining warnings:

```
INFO  | Issues don't block completion (Issues within standard mode thresholds: WARNING:2)
SUCCESS | QA verification passed: The note is technically sound...
```

Note still has 2 warnings, but QA says it's "technically sound."

### Root Cause
QA verifier is instructed to check "technical accuracy" but may not be checking:
- Completeness of fixes
- Whether warnings should block completion
- Regression from previous iterations

### Impact
- Notes may be marked complete with latent issues
- Human review required to catch these issues

### Proposed Fix

#### Fix 7.A: Stricter QA Criteria
**Location**: `automation/src/obsidian_vault/llm_review/agents/qa.py`

Update QA prompt:

```
You are performing final QA verification. The note must meet ALL criteria:

BLOCKING CRITERIA (Any of these FAIL the QA):
1. Any ERROR-level issues remain
2. Issue count increased in the last iteration (regression)
3. Same issue appears in multiple iterations (oscillation)
4. Timestamps are invalid or missing
5. Required YAML fields missing or malformed

NON-BLOCKING CRITERIA (Warn but don't fail):
1. Fewer than 2 WARNING-level issues remain
2. All warnings are cosmetic (formatting, style)
3. No technical inaccuracies

If ANY blocking criterion is true, respond:
{
  "passed": false,
  "reasoning": "...",
  "blocking_issues": [...]
}
```

---

## Summary of Fixes by Priority

### Critical (Implement First)
1. **Fix 1.A**: Implement Fix Memory - prevents oscillation
2. **Fix 1.B**: Implement Fix Validation - catches regressions
3. **Fix 1.C**: Add Circuit Breaker - stops infinite loops

### High Priority (Implement Second)
4. **Fix 2.A**: Run Parity Check in Parallel - reduces iterations
5. **Fix 3.A**: Strict Timestamp Policy - prevents timestamp thrashing
6. **Fix 3.B**: Add Timestamp Validator - catches timestamp issues early

### Medium Priority (Implement Third)
7. **Fix 4.A**: Parallel Note Processing - reduces total time
8. **Fix 4.B**: Reduce LLM Calls with Caching - reduces cost
9. **Fix 7.A**: Stricter QA Criteria - prevents broken notes

### Low Priority (Nice to Have)
10. **Fix 5.A**: Atomic Related Field Fixes - cleaner related field handling
11. **Fix 6.A**: Exclude Code Identifiers - smarter parity checking

---

## Implementation Roadmap

### Phase 1: Stop the Bleeding (Fixes 1.A-1.C, 2.A)
**Goal**: Eliminate oscillation and reduce iteration count to ≤2

**Estimated Impact**:
- Iteration count: 3-4 → 1-2
- Processing time: 7-15min → 3-7min per note
- Success rate: ~80% → ~95%

**Files to Modify**:
- `automation/src/obsidian_vault/llm_review/graph.py`
- `automation/src/obsidian_vault/llm_review/agents/fixer.py`
- `automation/src/obsidian_vault/llm_review/agents/state.py`

### Phase 2: Optimize Performance (Fixes 3.A-3.B, 4.A-4.C)
**Goal**: Reduce total processing time for full vault review

**Estimated Impact**:
- Per-note time: 3-7min → 2-4min
- Batch time (344 notes): 62hrs → 12hrs (with parallelism)
- API calls: 24/note → 12/note (with caching)

**Files to Modify**:
- `automation/src/obsidian_vault/llm_review/main.py`
- `automation/src/obsidian_vault/llm_review/validators/*.py`

### Phase 3: Polish (Fixes 5.A-7.A)
**Goal**: Handle edge cases and improve QA

**Estimated Impact**:
- Fewer false positives
- Better handling of bilingual code
- Stricter quality bar

**Files to Modify**:
- `automation/src/obsidian_vault/llm_review/agents/fixer.py`
- `automation/src/obsidian_vault/llm_review/agents/qa.py`
- `automation/src/obsidian_vault/llm_review/validators/parity.py`

---

## Metrics to Track

### Before Fixes (Baseline)
- Average iterations per note: **3.5**
- Average time per note: **650s** (10.8 min)
- Average final issues: **2**
- Notes with oscillation: **~30%**
- API calls per note: **~24**

### After Phase 1 (Target)
- Average iterations per note: **≤2**
- Average time per note: **≤400s** (6.7 min)
- Average final issues: **≤1**
- Notes with oscillation: **≤5%**
- API calls per note: **~18**

### After Phase 2 (Target)
- Average iterations per note: **≤2**
- Average time per note: **≤240s** (4 min)
- Average final issues: **≤1**
- Notes with oscillation: **≤5%**
- API calls per note: **≤12**
- Batch processing: **5 notes in parallel**

### After Phase 3 (Target)
- Average iterations per note: **≤2**
- Average time per note: **≤240s**
- Average final issues: **0**
- Notes with oscillation: **0%**
- False positive rate: **≤2%**

---

## Testing Strategy

### Unit Tests
```python
# Test Fix Memory
def test_fix_memory_prevents_refix():
    memory = FixMemory()
    memory.mark_fixed("metadata.created", "2024-10-12", iteration=1)

    assert memory.is_fixed("metadata.created")
    assert memory.get_fixed_value("metadata.created") == "2024-10-12"

# Test Oscillation Detection
def test_oscillation_detection():
    state = AgentState()
    state.history = [
        HistoryEntry(total_issues=10),
        HistoryEntry(total_issues=5),
        HistoryEntry(total_issues=8),  # Oscillation!
    ]

    assert detect_oscillation(state) == True

# Test Timestamp Validator
def test_timestamp_validator_future_date():
    note = """---
created: 2026-01-01
updated: 2025-11-09
---"""

    issues = validate_timestamps(note)
    assert len(issues) == 1
    assert "Future date" in issues[0].message
```

### Integration Tests
```python
# Test Full Workflow with Fix Memory
def test_workflow_with_memory():
    note_path = "test-note.md"

    result = review_note(note_path)

    assert result.iterations <= 2
    assert result.final_issues == 0
    assert not result.oscillated

# Test Parallel Processing
async def test_parallel_processing():
    notes = [f"test-note-{i}.md" for i in range(10)]

    start = time.time()
    results = await review_notes_parallel(notes, max_concurrent=5)
    elapsed = time.time() - start

    # Should be ~2x faster than sequential
    assert elapsed < len(notes) * 60  # Less than 1min per note
```

---

## Monitoring & Alerting

### Metrics to Log
```python
@dataclass
class ReviewMetrics:
    note_id: str
    iterations: int
    total_time_seconds: float
    final_issues: int
    oscillated: bool
    api_calls: int
    fix_regressions: List[str]

    def to_json(self) -> dict:
        return {
            "note_id": self.note_id,
            "iterations": self.iterations,
            "total_time_seconds": self.total_time_seconds,
            "final_issues": self.final_issues,
            "oscillated": self.oscillated,
            "api_calls": self.api_calls,
            "fix_regressions": self.fix_regressions,
        }
```

### Alerts to Set Up
1. **Oscillation Alert**: Trigger if oscillation detected
2. **Timeout Alert**: Trigger if note takes >10min
3. **Regression Alert**: Trigger if fixed field breaks again
4. **High API Usage**: Trigger if >30 calls per note

---

## Conclusion

The llm-review agent system has significant issues with oscillation, inefficiency, and instability. The root causes are:

1. **Lack of fix memory** - agent forgets what it already fixed
2. **Sequential validation** - parity issues caught too late
3. **Weak timestamp handling** - no clear policy
4. **No parallelism** - processes one note at a time
5. **No regression detection** - fixes can break previous fixes

The proposed fixes address these systematically:
- **Phase 1** eliminates oscillation
- **Phase 2** optimizes performance
- **Phase 3** polishes edge cases

**Expected Outcome After All Fixes**:
- ✅ Iteration count: 3.5 → ≤2 (43% reduction)
- ✅ Processing time: 10.8min → 4min (63% reduction)
- ✅ Batch time: 62hrs → 12hrs (81% reduction)
- ✅ Oscillation rate: 30% → 0%
- ✅ Final issues: 2 → 0

This will make llm-review practical for large-scale vault maintenance.
