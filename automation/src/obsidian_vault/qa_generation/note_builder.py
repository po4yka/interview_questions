"""Utilities for converting generated cards into vault notes."""

from __future__ import annotations

import re
from collections import OrderedDict
from datetime import date
from io import StringIO
from pathlib import Path
from typing import Iterable

from loguru import logger
from ruamel.yaml import YAML

from .models import GeneratedCard, SourceInfo
from obsidian_vault.utils import parse_note


TOPIC_FOLDER_MAP: dict[str, str] = {
    "algorithms": "20-Algorithms",
    "system-design": "30-System-Design",
    "android": "40-Android",
    "backend": "50-Backend",
    "cs": "60-CompSci",
    "kotlin": "70-Kotlin",
    "tools": "80-Tools",
}

TOPIC_ID_PREFIX: dict[str, str] = {
    "algorithms": "algo",
    "system-design": "sd",
    "android": "android",
    "backend": "backend",
    "cs": "cs",
    "kotlin": "kotlin",
    "tools": "tools",
}


def slugify(value: str) -> str:
    """Convert arbitrary text into a filesystem-safe slug."""

    value = value.lower()
    value = re.sub(r"[^a-z0-9\s-]", "", value)
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value.strip("-")


def generate_note_id(topic: str, folder: Path) -> str:
    """Generate the next sequential note identifier for a topic."""

    prefix = TOPIC_ID_PREFIX.get(topic)
    if not prefix:
        raise ValueError(f"Unsupported topic for ID generation: {topic}")

    max_number = 0
    for note_path in folder.rglob("q-*.md"):
        frontmatter, _ = parse_note(note_path)
        note_id = str(frontmatter.get("id", ""))
        if note_id.startswith(prefix + "-"):
            try:
                number = int(note_id.split("-")[-1])
            except ValueError:
                continue
            max_number = max(max_number, number)

    return f"{prefix}-{max_number + 1:03d}"


def render_frontmatter(card: GeneratedCard, *, note_id: str, article_url: str) -> str:
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.indent(mapping=2, sequence=4, offset=2)

    data: OrderedDict[str, object] = OrderedDict()
    data["id"] = note_id
    data["title"] = f"{card.title_en} / {card.title_ru}"
    data["aliases"] = card.aliases
    data["topic"] = card.topic
    if card.subtopics:
        data["subtopics"] = card.subtopics
    data["question_kind"] = card.question_kind
    data["difficulty"] = card.difficulty
    data["original_language"] = card.original_language or "ru"
    data["language_tags"] = ["ru", "en"]
    data["status"] = "draft"
    data["moc"] = f"moc-{card.topic}"
    related = card.related or _default_related(card)
    data["related"] = related
    today = date.today().isoformat()
    data["created"] = today
    data["updated"] = today
    tags = sorted(set(card.tags))
    data["tags"] = tags
    sources = card.sources or [SourceInfo(url=article_url, note="Source article")]
    rendered_sources: list[OrderedDict[str, object]] = []
    for source in sources:
        source_entry: OrderedDict[str, object] = OrderedDict()
        source_entry["url"] = source.url
        if source.note:
            source_entry["note"] = source.note
        rendered_sources.append(source_entry)
    data["sources"] = rendered_sources

    buffer = StringIO()
    yaml.dump(data, buffer)
    return buffer.getvalue().strip()


def _default_related(card: GeneratedCard) -> list[str]:
    if card.related:
        return card.related
    related: list[str] = []
    for subtopic in card.subtopics[:2]:
        related.append(f"c-{slugify(subtopic)}")
    if len(related) < 2:
        related.append(f"moc-{card.topic}")
    if len(related) < 2:
        related.append(f"c-{slugify(card.topic)}")
    deduped: list[str] = []
    seen: set[str] = set()
    for item in related:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    while len(deduped) < 2:
        deduped.append(f"moc-{card.topic}")
    return deduped[:2]


def build_note_body(card: GeneratedCard) -> str:
    sections: list[str] = []
    sections.append("# Вопрос (RU)\n> " + card.question_ru.strip())
    sections.append("# Question (EN)\n> " + card.question_en.strip())
    sections.append("---")
    sections.append("## Ответ (RU)\n\n" + card.answer_ru.strip())
    sections.append("## Answer (EN)\n\n" + card.answer_en.strip())
    sections.append("---")

    follow_sections: list[str] = []
    for lang, followups in card.all_follow_ups():
        if followups:
            heading = "## Follow-ups (RU)" if lang == "ru" else "## Follow-ups (EN)"
            follow_sections.append(heading)
            follow_sections.append("\n".join(f"- {item}" for item in followups))
    if follow_sections:
        sections.extend(follow_sections)
    else:
        sections.append("## Follow-ups (EN)\n- TODO: Add follow-up questions")

    references: list[str] = []
    for source in card.sources:
        if source.note:
            references.append(f"- [{source.note}]({source.url})")
        else:
            references.append(f"- {source.url}")
    if references:
        sections.append("\n## References\n" + "\n".join(references))

    related_links = card.related or _default_related(card)
    if related_links:
        sections.append(
            "\n## Related Questions\n" + "\n".join(f"- [[{link}]]" for link in related_links)
        )

    return "\n\n".join(sections).strip() + "\n"


def build_note_content(card: GeneratedCard, *, note_id: str, article_url: str) -> str:
    frontmatter = render_frontmatter(card, note_id=note_id, article_url=article_url)
    body = build_note_body(card)
    return f"---\n{frontmatter}\n---\n\n{body}"


def ensure_card_defaults(card: GeneratedCard, article_url: str) -> None:
    card.ensure_required_defaults(article_url=article_url)


class NoteWriter:
    """Persist generated cards as markdown files."""

    def __init__(self, vault_root: Path) -> None:
        self.vault_root = vault_root

    def write_card(self, card: GeneratedCard, *, article_url: str) -> Path:
        ensure_card_defaults(card, article_url)
        folder_name = TOPIC_FOLDER_MAP.get(card.topic)
        if not folder_name:
            raise ValueError(f"Unsupported topic folder for card: {card.topic}")

        folder_path = self.vault_root / folder_name
        if not folder_path.exists():
            raise FileNotFoundError(f"Vault folder does not exist: {folder_path}")

        note_id = generate_note_id(card.topic, folder_path)
        filename = f"q-{card.slug}--{card.topic}--{card.difficulty}.md"
        note_path = folder_path / filename
        if note_path.exists():
            raise FileExistsError(f"Note already exists: {note_path}")

        content = build_note_content(card, note_id=note_id, article_url=article_url)
        note_path.write_text(content, encoding="utf-8")
        logger.success("Created note", path=str(note_path))
        return note_path

    def write_cards(self, cards: Iterable[GeneratedCard], *, article_url: str) -> list[Path]:
        created: list[Path] = []
        for card in cards:
            created.append(self.write_card(card, article_url=article_url))
        return created
