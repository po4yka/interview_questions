from __future__ import annotations

from obsidian_vault.llm_review.state import NoteReviewState, ReviewIssue
from obsidian_vault.validators.base import Severity


def _make_state() -> NoteReviewState:
    """Helper to create a minimal note review state for oscillation tests."""

    text = "---\ntitle: Test\n---\n# Question (EN)\n# Вопрос (RU)\n"
    return NoteReviewState(
        note_path="note.md",
        original_text=text,
        current_text=text,
    )


def test_warning_only_issues_do_not_trigger_oscillation():
    """Repeated WARNING issues should not trip the oscillation circuit breaker."""

    state = _make_state()

    warning_issue = ReviewIssue(
        severity="WARNING",
        message="[Metadata] created timestamp is in the future",
        field="frontmatter",
    )

    for iteration in range(3):
        state.iteration = iteration
        state.issues = [warning_issue]
        state.record_current_issues()

    is_oscillating, explanation = state.detect_oscillation()

    assert not is_oscillating
    assert explanation is None
    # The raw history still records the warnings for analytics.
    assert all(
        entry == {"WARNING:[Metadata] created timestamp is in the future"}
        for entry in state.issue_history
    )


def test_enum_severity_warnings_stay_non_blocking():
    """Enum severities should normalize to non-blocking WARNING signatures."""

    state = _make_state()

    warning_issue = ReviewIssue(
        severity=Severity.WARNING,
        message="Note should include at least one concept link ([[c-...]]) in content body",
        field="content",
    )

    for iteration in range(2):
        state.iteration = iteration
        state.issues = [warning_issue]
        state.record_current_issues()

    is_oscillating, explanation = state.detect_oscillation()

    assert not is_oscillating
    assert explanation is None
    assert all(
        entry
        == {"WARNING:Note should include at least one concept link ([[c-...]]) in content body"}
        for entry in state.issue_history
    )


def test_error_reappearing_still_detects_oscillation():
    """ERROR-level issues that oscillate should continue to be detected."""

    state = _make_state()

    error_issue = ReviewIssue(
        severity="ERROR",
        message="[Metadata] missing required concept link",
        field="frontmatter",
    )

    # Iteration 0: issue present
    state.iteration = 0
    state.issues = [error_issue]
    state.record_current_issues()

    # Iteration 1: issue resolved
    state.iteration = 1
    state.issues = []
    state.record_current_issues()

    # Iteration 2: issue reappears (oscillation)
    state.iteration = 2
    state.issues = [error_issue]
    state.record_current_issues()

    state.iteration = 2
    is_oscillating, explanation = state.detect_oscillation()

    assert is_oscillating
    assert explanation is not None
    assert "missing required concept link" in explanation
