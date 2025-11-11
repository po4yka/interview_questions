"""Tests for ReviewGraph fix memory helpers."""

from collections import OrderedDict

from obsidian_vault.llm_review.fix_memory import FixMemory
from obsidian_vault.llm_review.graph import ReviewGraph


def _make_graph_stub() -> ReviewGraph:
    """Create a ReviewGraph instance without running __init__."""

    graph = ReviewGraph.__new__(ReviewGraph)
    graph.fix_memory = OrderedDict()
    return graph


def test_ensure_fix_memory_returns_single_instance():
    """_ensure_fix_memory should reuse cached FixMemory instances."""

    graph = _make_graph_stub()
    note_key = "InterviewQuestions/foo.md"

    assert graph._get_fix_memory(note_key) is None

    first = graph._ensure_fix_memory(note_key)
    assert isinstance(first, FixMemory)
    assert graph._get_fix_memory(note_key) is first

    second = graph._ensure_fix_memory(note_key)
    assert second is first, "Expected cached FixMemory instance to be reused"
