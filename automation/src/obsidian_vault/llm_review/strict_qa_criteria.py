"""Stricter QA Criteria - Better quality gate before marking notes complete.

PHASE 3 FIX: This module provides stricter QA verification criteria to prevent
notes with latent issues from being marked as complete.

Problem Example:
- Note has 2 WARNING-level issues remaining
- QA verifier says "technically sound" and passes it
- Note is marked complete despite having fixable issues

Solution:
- Block on any ERROR-level issues (existing behavior)
- Block if issue count increased in last iteration (regression)
- Block if same issue appears in multiple iterations (oscillation)
- Block if required fields are invalid or missing
- Warn on edge cases but allow completion

This ensures QA is the final quality gate, not just a rubber stamp.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from loguru import logger


@dataclass
class QABlockingReason:
    """Reason why QA verification should block completion."""

    category: str  # error, regression, oscillation, missing_field
    message: str
    severity: str  # CRITICAL, ERROR, WARNING


@dataclass
class StrictQAResult:
    """Result of strict QA verification."""

    should_pass: bool  # True if note can be marked complete
    blocking_reasons: list[QABlockingReason]
    warnings: list[str]  # Non-blocking concerns
    summary: str


class StrictQAVerifier:
    """Applies stricter criteria for QA verification.

    This class analyzes the full review history to detect patterns
    that indicate the note should not be marked complete.
    """

    def __init__(self):
        """Initialize strict QA verifier."""
        pass

    def verify(
        self,
        current_issues: list[Any],  # List of ReviewIssue
        history: list[dict[str, Any]],  # Full review history
        issue_history: list[set[str]],  # Issue signatures per iteration
        iteration: int,
    ) -> StrictQAResult:
        """Perform strict QA verification.

        Args:
            current_issues: Current list of issues
            history: Full review history
            issue_history: Issue signatures per iteration
            iteration: Current iteration number

        Returns:
            StrictQAResult with pass/fail determination
        """
        blocking_reasons = []
        warnings = []

        # CRITERION 1: Block on any ERROR-level issues
        error_issues = [
            issue for issue in current_issues if issue.severity in ["CRITICAL", "ERROR"]
        ]
        if error_issues:
            for issue in error_issues:
                blocking_reasons.append(
                    QABlockingReason(
                        category="error",
                        message=f"ERROR-level issue remains: {issue.message}",
                        severity="ERROR",
                    )
                )

        # CRITERION 2: Block if issue count increased in last iteration (regression)
        if len(issue_history) >= 2:
            prev_count = len(issue_history[-2])
            curr_count = len(issue_history[-1])

            if curr_count > prev_count:
                blocking_reasons.append(
                    QABlockingReason(
                        category="regression",
                        message=f"Issue count INCREASED in last iteration: {prev_count} → {curr_count}. "
                        f"This indicates fixes are making things worse!",
                        severity="CRITICAL",
                    )
                )

        # CRITERION 3: Block if same issues appear in multiple iterations (oscillation)
        if len(issue_history) >= 3:
            oscillating_issues = self._detect_oscillating_issues(issue_history)
            if oscillating_issues:
                for issue_sig in oscillating_issues:
                    blocking_reasons.append(
                        QABlockingReason(
                            category="oscillation",
                            message=f"Issue oscillating across iterations: {issue_sig}",
                            severity="ERROR",
                        )
                    )

        # CRITERION 4: Block if timestamps are invalid
        timestamp_issues = [
            issue
            for issue in current_issues
            if (issue.message and "timestamp" in issue.message.lower())
            or (issue.field and "created" in issue.field)
            or (issue.field and "updated" in issue.field)
        ]
        if timestamp_issues:
            for issue in timestamp_issues:
                if issue.severity in ["ERROR", "CRITICAL"]:
                    blocking_reasons.append(
                        QABlockingReason(
                            category="missing_field",
                            message=f"Invalid timestamp: {issue.message}",
                            severity="ERROR",
                        )
                    )

        # CRITERION 5: Block if required YAML fields are missing
        required_field_issues = [
            issue
            for issue in current_issues
            if issue.message
            and "missing" in issue.message.lower()
            and issue.field == "frontmatter"
        ]
        if required_field_issues:
            for issue in required_field_issues:
                blocking_reasons.append(
                    QABlockingReason(
                        category="missing_field",
                        message=f"Required field missing: {issue.message}",
                        severity="ERROR",
                    )
                )

        # NON-BLOCKING WARNINGS
        # Warn if there are WARNING-level issues but don't block
        warning_issues = [issue for issue in current_issues if issue.severity == "WARNING"]
        if warning_issues and len(warning_issues) > 0:
            warnings.append(
                f"{len(warning_issues)} WARNING-level issue(s) remain (non-blocking)"
            )

        # Warn if many iterations were needed
        if iteration > 5:
            warnings.append(
                f"Required {iteration} iterations to complete (may indicate complex issues)"
            )

        # Determine if QA should pass
        should_pass = len(blocking_reasons) == 0

        # Generate summary
        if should_pass:
            if warnings:
                summary = (
                    f"QA PASS with {len(warnings)} warning(s). "
                    f"Note is acceptable for completion."
                )
            else:
                summary = "QA PASS. Note is ready for completion with no issues."
        else:
            summary = (
                f"QA FAIL. {len(blocking_reasons)} blocking issue(s) prevent completion. "
                f"See blocking reasons for details."
            )

        return StrictQAResult(
            should_pass=should_pass,
            blocking_reasons=blocking_reasons,
            warnings=warnings,
            summary=summary,
        )

    def _detect_oscillating_issues(
        self, issue_history: list[set[str]]
    ) -> set[str]:
        """Detect issues that appear in multiple non-consecutive iterations.

        An oscillating issue is one that:
        - Appears in iteration N
        - Disappears in iteration N+1
        - Reappears in iteration N+2

        Args:
            issue_history: Issue signatures per iteration

        Returns:
            Set of oscillating issue signatures
        """
        oscillating = set()

        # Need at least 3 iterations to detect oscillation
        if len(issue_history) < 3:
            return oscillating

        # Check last 3 iterations
        for i in range(len(issue_history) - 2):
            iter_n = issue_history[i]
            iter_n1 = issue_history[i + 1]
            iter_n2 = issue_history[i + 2]

            # Find issues that were in N, not in N+1, but back in N+2
            disappeared = iter_n - iter_n1
            reappeared = disappeared & iter_n2

            if reappeared:
                oscillating.update(reappeared)
                logger.warning(
                    f"Detected {len(reappeared)} oscillating issue(s) "
                    f"between iterations {i}, {i+1}, {i+2}"
                )

        return oscillating

    def format_rules_for_qa_agent(self) -> str:
        """Format QA criteria for inclusion in QA agent prompt.

        Returns:
            Formatted string with strict QA rules
        """
        return """
STRICT QA VERIFICATION CRITERIA (PHASE 3 FIX - APPLY RIGOROUSLY):

You are the FINAL QUALITY GATE before a note is marked complete.
Your job is to be STRICT and catch issues that would embarrass us later.

BLOCKING CRITERIA (Any of these → FAIL QA):

1. ERROR-LEVEL ISSUES REMAIN:
   - ANY issue with severity ERROR or CRITICAL → FAIL
   - This includes: syntax errors, broken links, missing required fields
   - Exception: None (ERROR always blocks)

2. REGRESSION DETECTED:
   - Issue count INCREASED in the last iteration → FAIL
   - Example: Had 3 issues, now have 5 issues → FAIL
   - This means fixes are making things WORSE

3. OSCILLATION DETECTED:
   - Same issue appears, disappears, then reappears → FAIL
   - Example: Iteration 1 has issue X, iteration 2 fixed it, iteration 3 has issue X again
   - This means we're stuck in a loop

4. INVALID TIMESTAMPS:
   - 'created' or 'updated' fields are missing or malformed → FAIL
   - Timestamps in the future → FAIL
   - created > updated → FAIL

5. MISSING REQUIRED FIELDS:
   - Any required YAML field (topic, difficulty, moc, etc.) is missing → FAIL
   - Incomplete bilingual content (missing RU or EN sections) → FAIL

NON-BLOCKING WARNINGS (Warn but allow completion):

1. WARNING-LEVEL ISSUES:
   - Up to 3 WARNING-level issues are OK (within standard threshold)
   - Example: Minor formatting inconsistencies, style suggestions

2. HIGH ITERATION COUNT:
   - If >5 iterations were needed, note complexity for review
   - But don't block completion

RESPONSE FORMAT:

If ANY blocking criterion is true:
{
  "is_acceptable": false,
  "factual_errors": [...],
  "bilingual_parity_issues": [...],
  "quality_concerns": [...],
  "summary": "QA FAILED: [explain blocking reason]. Note requires additional fixes."
}

If NO blocking criteria but have warnings:
{
  "is_acceptable": true,
  "factual_errors": [],
  "bilingual_parity_issues": [],
  "quality_concerns": ["Warning: ...", "Warning: ..."],
  "summary": "QA PASSED with warnings: [list warnings]. Note is acceptable for completion."
}

If NO issues at all:
{
  "is_acceptable": true,
  "factual_errors": [],
  "bilingual_parity_issues": [],
  "quality_concerns": [],
  "summary": "QA PASSED: Note is technically accurate, complete, and ready for use."
}

REMEMBER: You are the last line of defense. Be STRICT!
""".strip()
