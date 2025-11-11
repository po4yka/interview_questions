from __future__ import annotations

import asyncio
from pathlib import Path

from obsidian_vault.llm_review.agents.models import TechnicalReviewResult
from obsidian_vault.llm_review.graph import ReviewGraph
from obsidian_vault.llm_review.state import NoteReviewState


class _StubGraph(ReviewGraph):
    """Thin wrapper to instantiate ReviewGraph without heavy dependencies."""

    def __init__(self, tmp_path: Path) -> None:
        # Bypass parent initialisation; only set attributes the test needs
        self.vault_root = tmp_path
        self.taxonomy = None
        self.note_index: set[str] = set()
        self.max_iterations = 1
        self.dry_run = True
        self.analytics = None


def _run(coro):
    """Helper to execute async coroutines in tests without extra plugins."""

    return asyncio.run(coro)


def test_initial_review_rejects_invalid_yaml(monkeypatch, tmp_path):
    """Technical review output with broken YAML should stop the workflow."""

    graph = _StubGraph(tmp_path)

    async def _fake_review(**kwargs):  # type: ignore[no-untyped-def]
        return TechnicalReviewResult(
            has_issues=False,
            issues_found=[],
            revised_text="---\naliases:\n1a1a1a\n---\nbody",
            changes_made=True,
            explanation="invalid list",
        )

    monkeypatch.setattr(
        "obsidian_vault.llm_review.graph.run_technical_review",
        _fake_review,
    )

    original = "---\naliases:\n  - valid\n---\nbody"
    state = NoteReviewState(
        note_path="note.md",
        original_text=original,
        current_text=original,
    ).to_dict()

    result = _run(graph._initial_llm_review(state))

    assert "error" in result
    assert "invalid output" in result["error"]
    assert result["requires_human_review"] is True
    assert result["completed"] is True


def test_initial_review_accepts_valid_yaml(monkeypatch, tmp_path):
    """Technical review output with valid YAML should be applied."""

    graph = _StubGraph(tmp_path)

    async def _fake_review(**kwargs):  # type: ignore[no-untyped-def]
        return TechnicalReviewResult(
            has_issues=False,
            issues_found=[],
            revised_text="---\naliases:\n  - valid\n  - new\n---\nbody",
            changes_made=True,
            explanation="added alias",
        )

    monkeypatch.setattr(
        "obsidian_vault.llm_review.graph.run_technical_review",
        _fake_review,
    )

    original = "---\naliases:\n  - valid\n---\nbody"
    state = NoteReviewState(
        note_path="note.md",
        original_text=original,
        current_text=original,
    ).to_dict()

    result = _run(graph._initial_llm_review(state))

    assert "current_text" in result
    assert result["changed"] is True
    assert "error" not in result
