"""Unit tests for helper utilities in the card generation agent."""

from obsidian_vault.anki_generation.agent import (
    _format_retry_feedback_text,
    _truncate_text,
)


def test_truncate_text_returns_original_when_within_limit() -> None:
    text = "short text"
    assert _truncate_text(text, 20) == text


def test_truncate_text_appends_suffix_when_exceeding_limit() -> None:
    text = "abcdef"
    result = _truncate_text(text, 3, suffix="...")
    assert result == "abc..."


def test_format_retry_feedback_truncates_previous_output() -> None:
    error = "Missing required field: title_ru"
    previous_output = "{" + "x" * 200 + "}"
    feedback = _format_retry_feedback_text(error, previous_output, max_chars=50)

    assert "Validation error: Missing required field: title_ru" in feedback
    assert "Previous response (truncated):" in feedback
    assert "..." in feedback.splitlines()[-2]
