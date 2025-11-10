"""Decision logic for LLM review workflow.

This module contains pure functions for computing workflow decisions, extracted
from the ReviewGraph class for improved testability and maintainability.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from .state import ReviewIssue


Decision = Literal["continue", "qa_verify", "summarize_failures", "done"]


@dataclass
class DecisionContext:
    """Context needed to compute workflow decision.

    This encapsulates all the state needed for decision making in a testable way.
    """

    # State flags
    requires_human_review: bool
    completed: bool
    error: str | None

    # Iteration tracking
    iteration: int
    max_iterations: int

    # Issue tracking
    issues: list[ReviewIssue]
    has_oscillation: bool
    oscillation_explanation: str | None

    # QA tracking
    qa_verification_passed: bool | None

    # Completion mode configuration
    completion_mode: str  # "strict" | "standard" | "permissive"
    completion_thresholds: dict[str, int | float]


def should_issues_block_completion(
    issues: list[ReviewIssue],
    completion_mode: str,
    completion_thresholds: dict[str, int | float],
) -> tuple[bool, str]:
    """Check if issues should block completion based on severity thresholds.

    Args:
        issues: List of current issues
        completion_mode: Current completion mode ("strict", "standard", "permissive")
        completion_thresholds: Dict of {severity: max_allowed_count}

    Returns:
        (should_block, reason) tuple
    """
    if not issues:
        return False, "No issues remaining"

    # Count issues by severity
    severity_counts = Counter(issue.severity for issue in issues)

    # Check if any severity exceeds its threshold
    blocking_severities = []
    for severity, count in severity_counts.items():
        max_allowed = completion_thresholds.get(severity, 0)
        if count > max_allowed:
            blocking_severities.append(f"{severity}:{count}>{max_allowed}")

    if blocking_severities:
        reason = (
            f"Issues exceed {completion_mode} mode thresholds: "
            f"{', '.join(blocking_severities)}"
        )
        return True, reason
    else:
        summary = ", ".join(f"{sev}:{cnt}" for sev, cnt in severity_counts.items())
        reason = f"Issues within {completion_mode} mode thresholds: {summary}"
        return False, reason


def compute_decision(ctx: DecisionContext) -> tuple[Decision, str]:
    """Compute the next step decision and corresponding message.

    Decision logic (in priority order):
    1. If requires_human_review flag set -> summarize_failures
    2. If oscillation detected -> summarize_failures
    3. If max iterations reached AND (issues remain OR QA failed) -> summarize_failures
    4. If max iterations reached AND no issues AND QA passed -> done
    5. If error occurred -> done
    6. If completed flag set -> done
    7. If no validator/parity issues AND QA not run yet -> qa_verify
    8. If no validator/parity issues AND QA passed -> done
    9. If validator/parity issues remain -> continue

    Args:
        ctx: Decision context with all required state

    Returns:
        (decision, message) tuple where decision is one of:
            - "continue": Continue fixing loop
            - "qa_verify": Route to QA verification
            - "summarize_failures": Create failure summary
            - "done": Workflow complete
    """

    # Decision 1: Human review required
    if ctx.requires_human_review:
        message = (
            f"Fix agent could not apply changes - escalating to human review "
            f"(iteration {ctx.iteration}/{ctx.max_iterations}, "
            f"{len(ctx.issues)} unresolved issue(s))"
        )
        return "summarize_failures", message

    # Decision 2: Oscillation detected
    if ctx.has_oscillation:
        message = (
            f"CIRCUIT BREAKER TRIGGERED: Oscillation detected - stopping iteration. "
            f"{ctx.oscillation_explanation}"
        )
        return "summarize_failures", message

    # Decision 3 & 4: Max iterations reached
    if ctx.iteration >= ctx.max_iterations:
        has_unresolved_issues = len(ctx.issues) > 0
        qa_failed = ctx.qa_verification_passed is False

        if has_unresolved_issues or qa_failed:
            message = (
                f"Max iterations ({ctx.max_iterations}) reached with unresolved issues - "
                f"triggering failure summarizer"
            )
            return "summarize_failures", message
        else:
            message = f"Stopping: max iterations ({ctx.max_iterations}) reached"
            return "done", message

    # Decision 5: Error occurred
    if ctx.error:
        message = f"Stopping: error occurred: {ctx.error}"
        return "done", message

    # Decision 6: Completed flag set
    if ctx.completed:
        message = "Stopping: completed flag set"
        return "done", message

    # Decision 7, 8, 9: Check if issues block completion
    should_block, block_reason = should_issues_block_completion(
        ctx.issues, ctx.completion_mode, ctx.completion_thresholds
    )

    if not should_block:
        # No blocking issues
        if ctx.qa_verification_passed is None:
            # QA not run yet - route to QA
            message = (
                f"Issues don't block completion ({block_reason}) - routing to QA verification"
            )
            return "qa_verify", message
        elif ctx.qa_verification_passed:
            # QA passed - workflow complete
            message = f"Stopping: {block_reason} and QA verification passed"
            return "done", message
        else:
            # QA failed - continue fixing
            message = f"Continuing: QA verification found issues to fix (previous: {block_reason})"
            return "continue", message
    else:
        # Blocking issues remain - continue fixing
        message = f"Continuing to iteration {ctx.iteration + 1} ({block_reason})"
        return "continue", message
