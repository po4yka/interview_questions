"""Tests for OscillationFixer - handling recurring issues that cause oscillation."""

from pathlib import Path

import pytest

from obsidian_vault.llm_review.oscillation_fixer import OscillationFixer
from obsidian_vault.llm_review.state import ReviewIssue


@pytest.fixture
def vault_root(tmp_path):
    """Create a temporary vault root."""
    return tmp_path


@pytest.fixture
def oscillation_fixer(vault_root):
    """Create an oscillation fixer instance."""
    return OscillationFixer(vault_root)


@pytest.fixture
def sample_note_text():
    """Sample Q&A note with correct structure."""
    return """---
id: kotlin-001
title: Test Question / Тестовый вопрос
topic: kotlin
difficulty: medium
---

# Question (EN)

> What is a coroutine?

## Answer (EN)

A coroutine is a concurrency design pattern.

# Вопрос (RU)

> Что такое корутина?

## Ответ (RU)

Корутина - это паттерн конкурентного программирования.

## Follow-ups

- How do coroutines differ from threads?

## References

- [[c-coroutines]]

## Related Questions

- [[q-coroutine-scope--kotlin--medium]]
"""


@pytest.fixture
def note_with_wrong_heading_order():
    """Sample note with headings in wrong order."""
    return """---
id: kotlin-001
title: Test Question / Тестовый вопрос
topic: kotlin
difficulty: medium
---

# Question (EN)

> What is a coroutine?

# Вопрос (RU)

> Что такое корутина?

## Answer (EN)

A coroutine is a concurrency design pattern.

## Ответ (RU)

Корутина - это паттерн конкурентного программирования.

## Follow-ups

- How do coroutines differ from threads?

## References

- [[c-coroutines]]

## Related Questions

- [[q-coroutine-scope--kotlin--medium]]
"""


class TestOscillationFixer:
    """Tests for OscillationFixer class."""

    def test_can_fix_file_location_issue(self, oscillation_fixer):
        """Test detection of file location issues."""
        issues = [
            ReviewIssue(
                severity="ERROR",
                message="File should be located in folder '70-Kotlin' for topic 'kotlin'",
            )
        ]
        assert oscillation_fixer.can_fix(issues) is True

    def test_can_fix_heading_order_issue(self, oscillation_fixer):
        """Test detection of heading order issues."""
        issues = [
            ReviewIssue(
                severity="ERROR",
                message="Headings appear out of expected order (should be: RU question → EN question → RU answer → EN answer)",
            )
        ]
        assert oscillation_fixer.can_fix(issues) is True

    def test_cannot_fix_unrelated_issue(self, oscillation_fixer):
        """Test that fixer ignores unrelated issues."""
        issues = [
            ReviewIssue(
                severity="ERROR",
                message="Missing required field 'moc'",
            )
        ]
        assert oscillation_fixer.can_fix(issues) is False

    def test_fix_heading_order(self, oscillation_fixer, note_with_wrong_heading_order, vault_root):
        """Test fixing heading order issue."""
        issues = [
            ReviewIssue(
                severity="ERROR",
                message="Headings appear out of expected order (should be: RU question → EN question → RU answer → EN answer)",
            )
        ]

        result = oscillation_fixer.fix(
            note_text=note_with_wrong_heading_order,
            issues=issues,
            note_path=vault_root / "test.md",
        )

        assert result.changes_made is True
        assert len(result.fixes_applied) > 0
        assert "Reordered headings" in result.fixes_applied[0]
        assert len(result.issues_fixed) == 1

        # Check that the order is now correct (RU question before EN question)
        ru_question_pos = result.revised_text.find("# Вопрос (RU)")
        en_question_pos = result.revised_text.find("# Question (EN)")
        ru_answer_pos = result.revised_text.find("## Ответ (RU)")
        en_answer_pos = result.revised_text.find("## Answer (EN)")

        assert ru_question_pos < en_question_pos
        assert en_question_pos < ru_answer_pos
        assert ru_answer_pos < en_answer_pos

    def test_fix_file_location_issue(self, oscillation_fixer, sample_note_text, vault_root):
        """Test handling file location issue (flags for move)."""
        issues = [
            ReviewIssue(
                severity="ERROR",
                message="File should be located in folder '70-Kotlin' for topic 'kotlin'",
            )
        ]

        # Create a test note in wrong location
        wrong_folder = vault_root / "60-CompSci"
        wrong_folder.mkdir(parents=True)
        note_path = wrong_folder / "test.md"

        result = oscillation_fixer.fix(
            note_text=sample_note_text,
            issues=issues,
            note_path=note_path,
        )

        assert result.changes_made is True
        assert result.file_moved is True
        assert result.new_file_path is not None
        assert "70-Kotlin" in result.new_file_path
        assert len(result.issues_fixed) == 1

    def test_get_fixable_issue_count(self, oscillation_fixer):
        """Test counting fixable issues."""
        issues = [
            ReviewIssue(
                severity="ERROR",
                message="File should be located in folder '70-Kotlin' for topic 'kotlin'",
            ),
            ReviewIssue(
                severity="ERROR",
                message="Headings appear out of expected order (should be: RU question → EN question → RU answer → EN answer)",
            ),
            ReviewIssue(
                severity="ERROR",
                message="Missing required field 'moc'",
            ),
        ]

        count = oscillation_fixer.get_fixable_issue_count(issues)
        assert count == 2  # Only first two are fixable

    def test_get_summary(self, oscillation_fixer):
        """Test summary generation."""
        issues = [
            ReviewIssue(
                severity="ERROR",
                message="File should be located in folder '70-Kotlin' for topic 'kotlin'",
            ),
            ReviewIssue(
                severity="ERROR",
                message="Missing required field 'moc'",
            ),
        ]

        summary = oscillation_fixer.get_summary(issues)
        assert "1/2" in summary
        assert "oscillation" in summary.lower()

    def test_no_changes_when_no_fixable_issues(
        self, oscillation_fixer, sample_note_text, vault_root
    ):
        """Test that fixer makes no changes for unfixable issues."""
        issues = [
            ReviewIssue(
                severity="ERROR",
                message="Missing required field 'moc'",
            )
        ]

        result = oscillation_fixer.fix(
            note_text=sample_note_text,
            issues=issues,
            note_path=vault_root / "test.md",
        )

        assert result.changes_made is False
        assert len(result.fixes_applied) == 0
        assert len(result.issues_fixed) == 0
