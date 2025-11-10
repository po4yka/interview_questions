from pathlib import Path
from types import SimpleNamespace
from typing import Iterable


class DummyGraph:
    """Minimal directed graph stub for testing atomic coverage helpers."""

    def __init__(self, edges: dict[str, Iterable[str]]) -> None:
        self._edges = {source: list(targets) for source, targets in edges.items()}
        self._nodes: set[str] = set(self._edges)
        for targets in self._edges.values():
            self._nodes.update(targets)

    def has_node(self, node: str) -> bool:
        return node in self._nodes

    def in_degree(self, node: str) -> int:
        return sum(1 for targets in self._edges.values() if node in targets)

    def out_degree(self, node: str) -> int:
        return len(self._edges.get(node, []))

    def successors(self, node: str) -> Iterable[str]:
        return list(self._edges.get(node, []))

    def predecessors(self, node: str) -> Iterable[str]:
        for source, targets in self._edges.items():
            if node in targets:
                yield source

import pytest

from obsidian_vault.qa_generation.gap_analysis import (
    AtomicCoveragePoint,
    ExistingNote,
    TopicMemory,
    _build_topic_memories,
    _clean_list,
    _extract_answer,
    _extract_question,
    _format_topic_inventory,
    _load_existing_notes,
    _split_bilingual_title,
    _truncate,
)


def test_split_bilingual_title_handles_separator() -> None:
    title_en, title_ru = _split_bilingual_title("Title EN / Заголовок RU")
    assert title_en == "Title EN"
    assert title_ru == "Заголовок RU"

    fallback_en, fallback_ru = _split_bilingual_title("Single Title")
    assert fallback_en == fallback_ru == "Single Title"


@pytest.mark.parametrize(
    "value,expected",
    [
        ("tag-one", ["tag-one"]),
        (["a", "", "b"], ["a", "b"]),
        ([], []),
    ],
)
def test_clean_list_normalizes_inputs(value: object, expected: list[str]) -> None:
    assert _clean_list(value) == expected


def test_extract_question_returns_first_block() -> None:
    body = """
# Вопрос (RU)
> Что такое Map?

# Question (EN)
> What is a map?

## Ответ (RU)
    """.strip()
    assert _extract_question(body, "Question (EN)") == "What is a map?"
    assert _extract_question(body, "Вопрос (RU)") == "Что такое Map?"


def test_extract_answer_collapses_section() -> None:
    body = """
## Ответ (RU)
Первый абзац.

Второй абзац.

## Answer (EN)
First paragraph.

Second paragraph.
    """.strip()

    assert _extract_answer(body, "Ответ (RU)") == "Первый абзац. Второй абзац."
    assert _extract_answer(body, "Answer (EN)") == "First paragraph. Second paragraph."


def test_build_topic_memories_includes_highlights() -> None:
    vault_root = Path("/vault")
    stateflow_path = vault_root / "20-Android" / "q-stateflow-basics--android--medium.md"
    lifecycle_path = vault_root / "20-Android" / "q-lifecycle-overview--android--easy.md"
    compose_path = vault_root / "20-Android" / "q-compose-state--android--medium.md"
    notes = [
        ExistingNote(
            path=stateflow_path,
            topic="android",
            slug="stateflow-basics",
            difficulty="medium",
            question_kind="theory",
            title_en="StateFlow basics",
            title_ru="Основы StateFlow",
            subtopics=["stateflow", "kotlin-flow"],
            tags=["lang/kotlin", "android/coroutines"],
            question_en="How does StateFlow differ from SharedFlow?",
            question_ru="Чем StateFlow отличается от SharedFlow?",
            answer_en="StateFlow is a hot flow with replay=1 and is ideal for UI state.",
            answer_ru="StateFlow — горячий поток с replay=1, идеально подходит для UI-состояния.",
        ),
        ExistingNote(
            path=lifecycle_path,
            topic="android",
            slug="lifecycle-overview",
            difficulty="easy",
            question_kind="theory",
            title_en="Lifecycle overview",
            title_ru="Жизненный цикл",
            subtopics=["lifecycle"],
            tags=["android/components"],
            question_en="What are the Android lifecycle callbacks?",
            question_ru="Какие методы жизненного цикла Android?",
            answer_en="Describes onCreate, onStart, onResume, onPause, onStop, onDestroy.",
            answer_ru="Описывает onCreate, onStart, onResume, onPause, onStop, onDestroy.",
        ),
        ExistingNote(
            path=compose_path,
            topic="android",
            slug="compose-state",
            difficulty="medium",
            question_kind="theory",
            title_en="Compose state",
            title_ru="Состояние в Compose",
            subtopics=["compose", "stateflow"],
            tags=["android/compose"],
            question_en="How should Compose manage StateFlow state?",
            question_ru="Как Compose работает со StateFlow?",
            answer_en="Discuss collecting StateFlow with lifecycle-aware APIs.",
            answer_ru="Объясняет сбор StateFlow с учётом жизненного цикла.",
        ),
    ]

    taxonomy = SimpleNamespace(android_subtopics={"stateflow", "paging", "lifecycle"})
    graph = DummyGraph(
        {
            "20-Android/q-stateflow-basics--android--medium.md": [
                "20-Android/q-lifecycle-overview--android--easy.md",
                "Concepts/stateflow",
            ],
            "20-Android/q-lifecycle-overview--android--easy.md": [
                "20-Android/q-stateflow-basics--android--medium.md",
            ],
        }
    )
    memories = _build_topic_memories(
        notes,
        max_per_topic=5,
        max_question_chars=50,
        max_answer_chars=40,
        max_highlights=10,
        max_atomic_points=5,
        max_atomic_neighbors=3,
        vault_graph=SimpleNamespace(graph=graph),
        vault_root=vault_root,
        taxonomy=taxonomy,
    )

    assert set(memories) == {"android"}
    memory = memories["android"]
    assert isinstance(memory, TopicMemory)
    assert memory.total_notes == 3
    assert memory.subtopic_counts["stateflow"] == 2
    assert "paging" in memory.taxonomy_gaps
    assert any(highlight["slug"] == "stateflow-basics" for highlight in memory.highlights)
    # Ensure truncation applied
    assert len(memory.highlights[0]["answer_excerpt"]) <= 41
    assert memory.atomic_points
    stateflow_point = next(point for point in memory.atomic_points if point.subtopic == "stateflow")
    assert stateflow_point.note_count == 2
    assert stateflow_point.neighbor_examples[0] in {"lifecycle-overview", "20-Android/q-lifecycle-overview--android--easy.md"}
    compose_point = next(point for point in memory.atomic_points if point.subtopic == "compose")
    assert "compose-state" in compose_point.isolated_slugs


def test_format_topic_inventory_serializes_to_json() -> None:
    memory = TopicMemory(
        topic="android",
        total_notes=2,
        difficulty_distribution={"easy": 1, "medium": 1},
        question_kind_distribution={"theory": 2},
        subtopic_counts={"stateflow": 1, "lifecycle": 1},
        tag_counts={"android/components": 1},
        underrepresented_subtopics=["stateflow"],
        taxonomy_gaps=["compose"],
        highlights=[{"slug": "stateflow-basics", "question_excerpt": "How?", "answer_excerpt": "By…"}],
        atomic_points=[
            AtomicCoveragePoint(
                subtopic="stateflow",
                note_count=2,
                average_inbound=1.0,
                average_outbound=0.5,
                isolated_slugs=["compose-state"],
                neighbor_examples=["lifecycle-overview"],
            )
        ],
    )

    formatted = _format_topic_inventory({"android": memory})
    assert "\"topic\": \"android\"" in formatted
    assert "compose" in formatted
    assert "atomic_points" in formatted


@pytest.mark.parametrize(
    "value,limit,expected",
    [
        ("short text", 10, "short text"),
        ("needs trimming", 5, "needs…"),
        (None, 5, ""),
    ],
)
def test_truncate_behavior(value: str | None, limit: int, expected: str) -> None:
    assert _truncate(value, limit) == expected


def test_load_existing_notes_reads_frontmatter(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    target_folder = vault / "20-Algorithms"
    target_folder.mkdir(parents=True)
    note_path = target_folder / "q-sample--algorithms--easy.md"
    note_path.write_text(
        """
---
id: algo-001
title: Sample / Пример
topic: algorithms
question_kind: coding
difficulty: easy
tags: [leetcode]
---

# Вопрос (RU)
> Что такое пример?

# Question (EN)
> What is a sample?

## Ответ (RU)
Тест

## Answer (EN)
Test
        """.strip(),
        encoding="utf-8",
    )

    notes = list(_load_existing_notes(vault))
    assert len(notes) == 1
    note = notes[0]
    assert note.topic == "algorithms"
    assert note.slug == "sample"
    assert note.question_en == "What is a sample?"
    assert note.answer_en == "Test"
