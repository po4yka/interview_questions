"""Tools for detecting duplicate questions in the vault."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from loguru import logger

from obsidian_vault.anki_generation.models import GeneratedCard
from obsidian_vault.utils import build_note_index


def _normalize_question(text: str) -> str:
    normalized = text.strip().lower()
    normalized = re.sub(r"[^a-z0-9а-яё\s]", "", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def _extract_question_en(note_path: Path) -> str | None:
    try:
        text = note_path.read_text(encoding="utf-8")
    except OSError:
        logger.warning("Unable to read note while building duplicate index", path=note_path)
        return None

    pattern = re.compile(r"# Question \(EN\)\s*>\s*(.+)")
    match = pattern.search(text)
    if match:
        return match.group(1).strip()
    return None


@dataclass(slots=True)
class DuplicateChecker:
    """Detect duplicates against existing vault questions."""

    vault_root: Path

    def __post_init__(self) -> None:
        self._existing_questions = self._load_existing_questions()
        self._existing_files = build_note_index(self.vault_root)

    def _load_existing_questions(self) -> set[str]:
        normalized_questions: set[str] = set()
        for note_path in self.vault_root.rglob("q-*.md"):
            question = _extract_question_en(note_path)
            if question:
                normalized_questions.add(_normalize_question(question))
        logger.debug("Loaded {} existing questions for duplicate detection", len(normalized_questions))
        return normalized_questions

    def is_duplicate_question(self, question_en: str) -> bool:
        if not question_en:
            return False
        normalized = _normalize_question(question_en)
        return normalized in self._existing_questions

    def is_duplicate_slug(self, filename: str) -> bool:
        return filename in self._existing_files

    def filter_new_cards(self, cards: Iterable[GeneratedCard]) -> tuple[list[GeneratedCard], list[str]]:
        unique_cards: list[GeneratedCard] = []
        duplicates: list[str] = []
        seen_questions: set[str] = set()

        for card in cards:
            normalized_question = _normalize_question(card.question_en)
            if normalized_question in self._existing_questions:
                logger.info("Skipping duplicate card", slug=card.slug)
                duplicates.append(card.slug)
                continue
            if normalized_question in seen_questions:
                logger.info("Skipping duplicate card generated in current batch", slug=card.slug)
                duplicates.append(card.slug)
                continue

            filename = f"q-{card.slug}--{card.topic}--{card.difficulty}.md"
            if filename in self._existing_files:
                logger.info("Skipping card because filename already exists", filename=filename)
                duplicates.append(card.slug)
                continue

            seen_questions.add(normalized_question)
            unique_cards.append(card)

        return unique_cards, duplicates
