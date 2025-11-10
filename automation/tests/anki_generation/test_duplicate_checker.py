from __future__ import annotations

from pathlib import Path

from obsidian_vault.anki_generation.duplicate_checker import DuplicateChecker
from obsidian_vault.anki_generation.models import GeneratedCard


def _make_card(question: str, slug: str = "new-card") -> GeneratedCard:
    return GeneratedCard(
        slug=slug,
        topic="algorithms",
        difficulty="easy",
        question_kind="theory",
        title_en="Sample",
        title_ru="Пример",
        question_en=question,
        question_ru="Вопрос?",
        answer_en="English answer long enough." * 4,
        answer_ru="Русский ответ достаточно длинный." * 4,
    )


def test_duplicate_checker_skips_existing_question(tmp_path: Path):
    vault_root = tmp_path
    algorithms = vault_root / "20-Algorithms"
    algorithms.mkdir()
    existing = algorithms / "q-existing--algorithms--easy.md"
    existing.write_text(
        "---\nid: algo-001\n---\n# Question (EN)\n> What is a hash map?\n",
        encoding="utf-8",
    )

    checker = DuplicateChecker(vault_root)
    cards, duplicates = checker.filter_new_cards([_make_card("What is a hash map?")])

    assert not cards
    assert duplicates == ["new-card"]


def test_duplicate_checker_allows_unique_cards(tmp_path: Path):
    vault_root = tmp_path
    (vault_root / "20-Algorithms").mkdir()
    checker = DuplicateChecker(vault_root)

    cards, duplicates = checker.filter_new_cards([_make_card("Explain binary search", slug="binary-search")])

    assert len(cards) == 1
    assert not duplicates
