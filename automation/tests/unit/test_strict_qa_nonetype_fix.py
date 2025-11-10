"""Test fix for NoneType error in strict QA verification.

This test verifies that the QA verification handles ReviewIssue objects
with None field/message values without throwing 'NoneType is not iterable' errors.

Issue: https://github.com/po4yka/interview_questions/issues/...
Error: "argument of type 'NoneType' is not iterable"
"""

import pytest

from obsidian_vault.llm_review.state import ReviewIssue
from obsidian_vault.llm_review.strict_qa_criteria import StrictQAVerifier


class TestStrictQANoneTypeFix:
    """Test that strict QA handles None values in ReviewIssue fields."""

    def test_handles_none_field_in_timestamp_check(self):
        """Test that timestamp check handles None field without error."""
        verifier = StrictQAVerifier()

        # Create issues with None field (simulates real-world edge case)
        issues = [
            ReviewIssue(
                severity="ERROR",
                message="timestamp is invalid",
                field=None,  # This was causing NoneType error
            ),
            ReviewIssue(
                severity="ERROR",
                message="Some other error",
                field="content",
            ),
        ]

        # This should not raise "argument of type 'NoneType' is not iterable"
        result = verifier.verify(
            current_issues=issues,
            history=[],
            issue_history=[],
            iteration=1,
        )

        # Should fail QA due to ERROR-level issues
        assert not result.should_pass
        assert len(result.blocking_reasons) > 0

    def test_handles_none_message_in_missing_field_check(self):
        """Test that missing field check handles None message without error."""
        verifier = StrictQAVerifier()

        # Create issues with None message (edge case)
        issues = [
            ReviewIssue(
                severity="ERROR",
                message=None,  # Edge case: None message
                field="frontmatter",
            ),
        ]

        # This should not raise "argument of type 'NoneType' is not iterable"
        result = verifier.verify(
            current_issues=issues,
            history=[],
            issue_history=[],
            iteration=1,
        )

        # Should fail QA due to ERROR-level issues
        assert not result.should_pass

    def test_handles_field_with_created_or_updated_keywords(self):
        """Test that field checks work correctly when field contains keywords."""
        verifier = StrictQAVerifier()

        # Create issues with "created" or "updated" in field
        issues = [
            ReviewIssue(
                severity="ERROR",
                message="Invalid timestamp format",
                field="created",
            ),
            ReviewIssue(
                severity="ERROR",
                message="Timestamp in future",
                field="updated",
            ),
        ]

        # Should handle these without error
        result = verifier.verify(
            current_issues=issues,
            history=[],
            issue_history=[],
            iteration=1,
        )

        # Should fail QA and identify timestamp issues
        assert not result.should_pass
        assert any(
            "timestamp" in reason.message.lower() or "Invalid timestamp" in reason.message
            for reason in result.blocking_reasons
        )

    def test_passes_qa_with_no_issues(self):
        """Test that QA passes when there are no issues."""
        verifier = StrictQAVerifier()

        result = verifier.verify(
            current_issues=[],
            history=[],
            issue_history=[],
            iteration=1,
        )

        assert result.should_pass
        assert len(result.blocking_reasons) == 0

    def test_blocks_on_error_level_issues(self):
        """Test that ERROR-level issues block completion."""
        verifier = StrictQAVerifier()

        issues = [
            ReviewIssue(
                severity="ERROR",
                message="Critical validation error",
                field="content",
            ),
        ]

        result = verifier.verify(
            current_issues=issues,
            history=[],
            issue_history=[],
            iteration=1,
        )

        assert not result.should_pass
        assert any(
            reason.category == "error" for reason in result.blocking_reasons
        )

    def test_allows_warnings_without_blocking(self):
        """Test that WARNING-level issues don't block completion."""
        verifier = StrictQAVerifier()

        issues = [
            ReviewIssue(
                severity="WARNING",
                message="Minor formatting issue",
                field="content",
            ),
        ]

        result = verifier.verify(
            current_issues=issues,
            history=[],
            issue_history=[],
            iteration=1,
        )

        # Should pass despite warnings
        assert result.should_pass
        assert len(result.warnings) > 0

    def test_warning_history_does_not_trigger_oscillation_block(self):
        """Warnings repeating across iterations should not fail strict QA."""

        verifier = StrictQAVerifier()

        issues = [
            ReviewIssue(
                severity="WARNING",
                message="[Metadata] created timestamp is in the future",
                field="frontmatter",
            )
        ]

        issue_history = [
            {"WARNING:[Metadata] created timestamp is in the future"},
            {"WARNING:[Metadata] created timestamp is in the future"},
            {"WARNING:[Metadata] created timestamp is in the future"},
        ]

        result = verifier.verify(
            current_issues=issues,
            history=[],
            issue_history=issue_history,
            iteration=3,
        )

        assert result.should_pass
        assert not result.blocking_reasons
