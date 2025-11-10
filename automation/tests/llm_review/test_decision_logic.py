"""Unit tests for decision logic module.

This test suite provides comprehensive coverage of the decision logic,
ensuring all decision paths and edge cases are tested.
"""

import pytest

from obsidian_vault.llm_review.decision_logic import (
    DecisionContext,
    compute_decision,
    should_issues_block_completion,
)
from obsidian_vault.llm_review.state import ReviewIssue


# Test fixtures for completion thresholds
STRICT_THRESHOLDS = {
    "CRITICAL": 0,
    "ERROR": 0,
    "WARNING": 0,
    "INFO": float("inf"),
}

STANDARD_THRESHOLDS = {
    "CRITICAL": 0,
    "ERROR": 0,
    "WARNING": 3,
    "INFO": float("inf"),
}

PERMISSIVE_THRESHOLDS = {
    "CRITICAL": 0,
    "ERROR": 2,
    "WARNING": 10,
    "INFO": float("inf"),
}


class TestShouldIssuesBlockCompletion:
    """Test suite for should_issues_block_completion function."""

    def test_no_issues_does_not_block(self):
        """Test that no issues doesn't block completion."""
        should_block, reason = should_issues_block_completion(
            issues=[],
            completion_mode="standard",
            completion_thresholds=STANDARD_THRESHOLDS,
        )

        assert should_block is False
        assert reason == "No issues remaining"

    def test_warnings_below_threshold_standard_mode(self):
        """Test warnings below threshold don't block in standard mode."""
        issues = [
            ReviewIssue(severity="WARNING", message="Warning 1"),
            ReviewIssue(severity="WARNING", message="Warning 2"),
        ]

        should_block, reason = should_issues_block_completion(
            issues=issues,
            completion_mode="standard",
            completion_thresholds=STANDARD_THRESHOLDS,
        )

        assert should_block is False
        assert "WARNING:2" in reason
        assert "within standard mode thresholds" in reason

    def test_warnings_at_threshold_standard_mode(self):
        """Test warnings at threshold don't block in standard mode."""
        issues = [
            ReviewIssue(severity="WARNING", message="Warning 1"),
            ReviewIssue(severity="WARNING", message="Warning 2"),
            ReviewIssue(severity="WARNING", message="Warning 3"),
        ]

        should_block, reason = should_issues_block_completion(
            issues=issues,
            completion_mode="standard",
            completion_thresholds=STANDARD_THRESHOLDS,
        )

        assert should_block is False
        assert "WARNING:3" in reason

    def test_warnings_above_threshold_blocks(self):
        """Test warnings above threshold block completion."""
        issues = [
            ReviewIssue(severity="WARNING", message="Warning 1"),
            ReviewIssue(severity="WARNING", message="Warning 2"),
            ReviewIssue(severity="WARNING", message="Warning 3"),
            ReviewIssue(severity="WARNING", message="Warning 4"),
        ]

        should_block, reason = should_issues_block_completion(
            issues=issues,
            completion_mode="standard",
            completion_thresholds=STANDARD_THRESHOLDS,
        )

        assert should_block is True
        assert "WARNING:4>3" in reason
        assert "exceed standard mode thresholds" in reason

    def test_single_error_blocks_standard_mode(self):
        """Test single error blocks in standard mode."""
        issues = [
            ReviewIssue(severity="ERROR", message="Error 1"),
        ]

        should_block, reason = should_issues_block_completion(
            issues=issues,
            completion_mode="standard",
            completion_thresholds=STANDARD_THRESHOLDS,
        )

        assert should_block is True
        assert "ERROR:1>0" in reason

    def test_single_critical_always_blocks(self):
        """Test single critical issue always blocks."""
        issues = [
            ReviewIssue(severity="CRITICAL", message="Critical issue"),
        ]

        should_block, reason = should_issues_block_completion(
            issues=issues,
            completion_mode="permissive",
            completion_thresholds=PERMISSIVE_THRESHOLDS,
        )

        assert should_block is True
        assert "CRITICAL:1>0" in reason

    def test_info_issues_never_block(self):
        """Test INFO issues never block completion."""
        issues = [
            ReviewIssue(severity="INFO", message=f"Info {i}") for i in range(100)
        ]

        should_block, reason = should_issues_block_completion(
            issues=issues,
            completion_mode="strict",
            completion_thresholds=STRICT_THRESHOLDS,
        )

        assert should_block is False
        assert "INFO:100" in reason

    def test_mixed_severities_blocks_on_any_exceeding(self):
        """Test mixed severities block if any exceeds threshold."""
        issues = [
            ReviewIssue(severity="WARNING", message="Warning 1"),
            ReviewIssue(severity="WARNING", message="Warning 2"),
            ReviewIssue(severity="ERROR", message="Error 1"),  # Exceeds threshold
            ReviewIssue(severity="INFO", message="Info 1"),
        ]

        should_block, reason = should_issues_block_completion(
            issues=issues,
            completion_mode="standard",
            completion_thresholds=STANDARD_THRESHOLDS,
        )

        assert should_block is True
        assert "ERROR:1>0" in reason

    def test_permissive_mode_allows_some_errors(self):
        """Test permissive mode allows errors below threshold."""
        issues = [
            ReviewIssue(severity="ERROR", message="Error 1"),
            ReviewIssue(severity="ERROR", message="Error 2"),
        ]

        should_block, reason = should_issues_block_completion(
            issues=issues,
            completion_mode="permissive",
            completion_thresholds=PERMISSIVE_THRESHOLDS,
        )

        assert should_block is False
        assert "ERROR:2" in reason
        assert "within permissive mode thresholds" in reason

    def test_permissive_mode_blocks_on_too_many_errors(self):
        """Test permissive mode blocks when errors exceed threshold."""
        issues = [
            ReviewIssue(severity="ERROR", message=f"Error {i}") for i in range(3)
        ]

        should_block, reason = should_issues_block_completion(
            issues=issues,
            completion_mode="permissive",
            completion_thresholds=PERMISSIVE_THRESHOLDS,
        )

        assert should_block is True
        assert "ERROR:3>2" in reason


class TestComputeDecision:
    """Test suite for compute_decision function."""

    def _make_context(self, **overrides) -> DecisionContext:
        """Helper to create DecisionContext with defaults."""
        defaults = {
            "requires_human_review": False,
            "completed": False,
            "error": None,
            "iteration": 1,
            "max_iterations": 5,
            "issues": [],
            "has_oscillation": False,
            "oscillation_explanation": None,
            "qa_verification_passed": None,
            "completion_mode": "standard",
            "completion_thresholds": STANDARD_THRESHOLDS,
        }
        defaults.update(overrides)
        return DecisionContext(**defaults)

    # DECISION 1: Human review required
    def test_decision_human_review_required(self):
        """Test decision when human review is required."""
        ctx = self._make_context(
            requires_human_review=True,
            iteration=2,
            max_iterations=5,
            issues=[ReviewIssue(severity="ERROR", message="Some error")],
        )

        decision, message = compute_decision(ctx)

        assert decision == "summarize_failures"
        assert "escalating to human review" in message
        assert "iteration 2/5" in message
        assert "1 unresolved issue(s)" in message

    # DECISION 2: Oscillation detected
    def test_decision_oscillation_detected(self):
        """Test decision when oscillation is detected."""
        ctx = self._make_context(
            has_oscillation=True,
            oscillation_explanation="Same issues repeating",
        )

        decision, message = compute_decision(ctx)

        assert decision == "summarize_failures"
        assert "CIRCUIT BREAKER TRIGGERED" in message
        assert "Same issues repeating" in message

    # DECISION 3: Max iterations with issues
    def test_decision_max_iterations_with_issues(self):
        """Test decision when max iterations reached with unresolved issues."""
        ctx = self._make_context(
            iteration=5,
            max_iterations=5,
            issues=[ReviewIssue(severity="ERROR", message="Unresolved error")],
        )

        decision, message = compute_decision(ctx)

        assert decision == "summarize_failures"
        assert "Max iterations (5) reached" in message
        assert "unresolved issues" in message

    def test_decision_max_iterations_with_qa_failed(self):
        """Test decision when max iterations reached with QA failed."""
        ctx = self._make_context(
            iteration=5,
            max_iterations=5,
            issues=[],
            qa_verification_passed=False,
        )

        decision, message = compute_decision(ctx)

        assert decision == "summarize_failures"
        assert "Max iterations (5) reached" in message

    # DECISION 4: Max iterations without issues
    def test_decision_max_iterations_clean(self):
        """Test decision when max iterations reached with no issues."""
        ctx = self._make_context(
            iteration=5,
            max_iterations=5,
            issues=[],
            qa_verification_passed=True,
        )

        decision, message = compute_decision(ctx)

        assert decision == "done"
        assert "max iterations (5) reached" in message

    # DECISION 5: Error occurred
    def test_decision_error_occurred(self):
        """Test decision when error occurred."""
        ctx = self._make_context(
            error="Something went wrong",
        )

        decision, message = compute_decision(ctx)

        assert decision == "done"
        assert "error occurred" in message
        assert "Something went wrong" in message

    # DECISION 6: Completed flag set
    def test_decision_completed_flag(self):
        """Test decision when completed flag is set."""
        ctx = self._make_context(
            completed=True,
        )

        decision, message = compute_decision(ctx)

        assert decision == "done"
        assert "completed flag set" in message

    # DECISION 7: Route to QA verification
    def test_decision_route_to_qa_no_blocking_issues(self):
        """Test decision routes to QA when no blocking issues."""
        ctx = self._make_context(
            iteration=2,
            issues=[],  # No issues
            qa_verification_passed=None,  # QA not run yet
        )

        decision, message = compute_decision(ctx)

        assert decision == "qa_verify"
        assert "routing to QA verification" in message
        assert "No issues remaining" in message

    def test_decision_route_to_qa_with_allowed_warnings(self):
        """Test decision routes to QA with warnings below threshold."""
        ctx = self._make_context(
            iteration=2,
            issues=[
                ReviewIssue(severity="WARNING", message="Warning 1"),
                ReviewIssue(severity="WARNING", message="Warning 2"),
            ],
            qa_verification_passed=None,
        )

        decision, message = compute_decision(ctx)

        assert decision == "qa_verify"
        assert "routing to QA verification" in message
        assert "within standard mode thresholds" in message

    # DECISION 8: Workflow complete (QA passed)
    def test_decision_done_qa_passed(self):
        """Test decision when QA verification passed."""
        ctx = self._make_context(
            iteration=2,
            issues=[],
            qa_verification_passed=True,
        )

        decision, message = compute_decision(ctx)

        assert decision == "done"
        assert "QA verification passed" in message

    # DECISION 9: Continue fixing (blocking issues)
    def test_decision_continue_with_blocking_issues(self):
        """Test decision continues when blocking issues remain."""
        ctx = self._make_context(
            iteration=2,
            issues=[
                ReviewIssue(severity="ERROR", message="Error 1"),
            ],
        )

        decision, message = compute_decision(ctx)

        assert decision == "continue"
        assert "Continuing to iteration 3" in message
        assert "ERROR:1>0" in message

    def test_decision_continue_after_qa_failed(self):
        """Test decision continues after QA verification failed."""
        ctx = self._make_context(
            iteration=2,
            issues=[],  # No validator issues
            qa_verification_passed=False,  # But QA found issues
        )

        decision, message = compute_decision(ctx)

        assert decision == "continue"
        assert "QA verification found issues to fix" in message

    # EDGE CASES AND PRIORITY TESTS
    def test_decision_priority_human_review_over_oscillation(self):
        """Test human review flag takes priority over oscillation."""
        ctx = self._make_context(
            requires_human_review=True,
            has_oscillation=True,
            oscillation_explanation="Oscillating",
        )

        decision, message = compute_decision(ctx)

        assert decision == "summarize_failures"
        assert "escalating to human review" in message
        # Should not mention oscillation
        assert "CIRCUIT BREAKER" not in message

    def test_decision_priority_oscillation_over_max_iterations(self):
        """Test oscillation takes priority over max iterations."""
        ctx = self._make_context(
            has_oscillation=True,
            oscillation_explanation="Oscillating",
            iteration=5,
            max_iterations=5,
        )

        decision, message = compute_decision(ctx)

        assert decision == "summarize_failures"
        assert "CIRCUIT BREAKER" in message
        assert "max iterations" not in message

    def test_decision_priority_max_iterations_over_error(self):
        """Test max iterations takes priority over error flag."""
        ctx = self._make_context(
            iteration=5,
            max_iterations=5,
            error="Some error",
            issues=[],
        )

        decision, message = compute_decision(ctx)

        assert decision == "done"
        assert "max iterations" in message
        # Error is checked but max iterations is evaluated first

    def test_decision_priority_error_over_completed(self):
        """Test error flag takes priority over completed flag."""
        ctx = self._make_context(
            error="Some error",
            completed=True,
        )

        decision, message = compute_decision(ctx)

        assert decision == "done"
        assert "error occurred" in message
        assert "completed flag" not in message

    def test_decision_iteration_zero_with_issues(self):
        """Test decision at iteration 0 with issues continues."""
        ctx = self._make_context(
            iteration=0,
            max_iterations=5,
            issues=[ReviewIssue(severity="ERROR", message="Error")],
        )

        decision, message = compute_decision(ctx)

        assert decision == "continue"
        assert "Continuing to iteration 1" in message

    def test_decision_exactly_at_max_iterations(self):
        """Test decision when iteration equals max_iterations."""
        ctx = self._make_context(
            iteration=5,
            max_iterations=5,
            issues=[],
            qa_verification_passed=None,
        )

        decision, message = compute_decision(ctx)

        assert decision == "done"
        assert "max iterations" in message

    def test_decision_one_below_max_iterations(self):
        """Test decision one iteration below max continues."""
        ctx = self._make_context(
            iteration=4,
            max_iterations=5,
            issues=[ReviewIssue(severity="ERROR", message="Error")],
        )

        decision, message = compute_decision(ctx)

        assert decision == "continue"
        assert "iteration 5" in message


class TestDecisionLogicIntegration:
    """Integration tests for complete decision flow scenarios."""

    def test_happy_path_quick_fix(self):
        """Test happy path: issue found, fixed, QA passes."""
        thresholds = STANDARD_THRESHOLDS

        # Iteration 1: Issues found
        ctx1 = DecisionContext(
            requires_human_review=False,
            completed=False,
            error=None,
            iteration=1,
            max_iterations=5,
            issues=[ReviewIssue(severity="ERROR", message="Error")],
            has_oscillation=False,
            oscillation_explanation=None,
            qa_verification_passed=None,
            completion_mode="standard",
            completion_thresholds=thresholds,
        )
        decision1, _ = compute_decision(ctx1)
        assert decision1 == "continue"

        # Iteration 2: Issues fixed, route to QA
        ctx2 = DecisionContext(
            requires_human_review=False,
            completed=False,
            error=None,
            iteration=2,
            max_iterations=5,
            issues=[],
            has_oscillation=False,
            oscillation_explanation=None,
            qa_verification_passed=None,
            completion_mode="standard",
            completion_thresholds=thresholds,
        )
        decision2, _ = compute_decision(ctx2)
        assert decision2 == "qa_verify"

        # Iteration 3: QA passes, done
        ctx3 = DecisionContext(
            requires_human_review=False,
            completed=False,
            error=None,
            iteration=2,
            max_iterations=5,
            issues=[],
            has_oscillation=False,
            oscillation_explanation=None,
            qa_verification_passed=True,
            completion_mode="standard",
            completion_thresholds=thresholds,
        )
        decision3, _ = compute_decision(ctx3)
        assert decision3 == "done"

    def test_qa_failure_recovery(self):
        """Test scenario: QA fails, fix applied, QA passes."""
        thresholds = STANDARD_THRESHOLDS

        # QA failed - continue
        ctx1 = DecisionContext(
            requires_human_review=False,
            completed=False,
            error=None,
            iteration=2,
            max_iterations=5,
            issues=[],
            has_oscillation=False,
            oscillation_explanation=None,
            qa_verification_passed=False,
            completion_mode="standard",
            completion_thresholds=thresholds,
        )
        decision1, _ = compute_decision(ctx1)
        assert decision1 == "continue"

        # After fix, route to QA again
        ctx2 = DecisionContext(
            requires_human_review=False,
            completed=False,
            error=None,
            iteration=3,
            max_iterations=5,
            issues=[],
            has_oscillation=False,
            oscillation_explanation=None,
            qa_verification_passed=None,  # Reset for new QA run
            completion_mode="standard",
            completion_thresholds=thresholds,
        )
        decision2, _ = compute_decision(ctx2)
        assert decision2 == "qa_verify"

    def test_max_iterations_exhausted_scenario(self):
        """Test scenario: max iterations reached with issues."""
        thresholds = STANDARD_THRESHOLDS

        ctx = DecisionContext(
            requires_human_review=False,
            completed=False,
            error=None,
            iteration=5,
            max_iterations=5,
            issues=[ReviewIssue(severity="ERROR", message="Stubborn error")],
            has_oscillation=False,
            oscillation_explanation=None,
            qa_verification_passed=None,
            completion_mode="standard",
            completion_thresholds=thresholds,
        )
        decision, message = compute_decision(ctx)

        assert decision == "summarize_failures"
        assert "Max iterations" in message

    def test_oscillation_detection_scenario(self):
        """Test scenario: oscillation detected mid-workflow."""
        thresholds = STANDARD_THRESHOLDS

        ctx = DecisionContext(
            requires_human_review=False,
            completed=False,
            error=None,
            iteration=3,
            max_iterations=5,
            issues=[ReviewIssue(severity="ERROR", message="Oscillating error")],
            has_oscillation=True,
            oscillation_explanation="Issue count stuck at 1 for 3 iterations",
            qa_verification_passed=None,
            completion_mode="standard",
            completion_thresholds=thresholds,
        )
        decision, message = compute_decision(ctx)

        assert decision == "summarize_failures"
        assert "CIRCUIT BREAKER" in message
