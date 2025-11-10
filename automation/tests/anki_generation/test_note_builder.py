from __future__ import annotations

from pathlib import Path

from obsidian_vault.anki_generation.models import GeneratedCard, SourceInfo
from obsidian_vault.anki_generation.note_builder import (
    NoteWriter,
    build_note_content,
    generate_note_id,
    slugify,
)


def _create_sample_card() -> GeneratedCard:
    return GeneratedCard(
        slug="sample-card",
        topic="algorithms",
        difficulty="medium",
        question_kind="theory",
        title_en="Sample Question",
        title_ru="Пример вопроса",
        question_en="What is sample question?",
        question_ru="Что такое пример вопроса?",
        answer_en="This is an English answer that is sufficiently long to satisfy validation requirements." * 2,
        answer_ru="Это русский ответ с достаточной длиной для прохождения проверок." * 2,
        follow_ups_en=["How would you extend it?"],
        follow_ups_ru=["Как бы вы расширили ответ?"],
        subtopics=["patterns", "analysis"],
        tags=["algorithms", "pattern"],
        aliases=["Sample Question Alias"],
        related=["c-patterns", "q-example"],
        sources=[SourceInfo(url="https://example.com", note="Example source")],
    )


def test_slugify_basic():
    assert slugify("Hello World!") == "hello-world"
    assert slugify("Data Structures & Algorithms") == "data-structures-algorithms"


def test_generate_note_id_increments(tmp_path: Path):
    algorithms_dir = tmp_path / "20-Algorithms"
    algorithms_dir.mkdir()
    existing_note = algorithms_dir / "q-existing--algorithms--medium.md"
    existing_note.write_text(
        "---\nid: algo-001\n---\n# Question (EN)\n> Existing?\n",
        encoding="utf-8",
    )

    note_id = generate_note_id("algorithms", algorithms_dir)
    assert note_id == "algo-002"


def test_note_writer_creates_file(tmp_path: Path):
    algorithms_dir = tmp_path / "20-Algorithms"
    algorithms_dir.mkdir()
    card = _create_sample_card()
    writer = NoteWriter(tmp_path)

    note_path = writer.write_card(card, article_url="https://example.com/article")

    assert note_path.exists()
    content = note_path.read_text(encoding="utf-8")
    assert "algo-001" in content
    assert "Sample Question" in content
    assert "Пример вопроса" in content
    assert "## Ответ (RU)" in content


def test_build_note_content_contains_sections(tmp_path: Path):
    card = _create_sample_card()
    card.ensure_required_defaults(article_url="https://example.com")
    content = build_note_content(card, note_id="algo-010", article_url="https://example.com")

    assert content.startswith("---")
    assert "title: Sample Question / Пример вопроса" in content
    assert "# Вопрос (RU)" in content
    assert "## Answer (EN)" in content
