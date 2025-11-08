"""Helpers to load controlled vocabularies from TAXONOMY.md."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Set


@dataclass
class Taxonomy:
    topics: Set[str] = field(default_factory=set)
    android_subtopics: Set[str] = field(default_factory=set)


class TaxonomyLoader:
    """Parses TAXONOMY.md to expose controlled vocabularies."""

    def __init__(self, vault_root: Path):
        self.vault_root = vault_root
        self.taxonomy_path = vault_root / "InterviewQuestions" / "00-Administration" / "TAXONOMY.md"

    def load(self) -> Taxonomy:
        taxonomy = Taxonomy()
        if not self.taxonomy_path.exists():
            return taxonomy
        text = self.taxonomy_path.read_text(encoding="utf-8")
        taxonomy.topics = self._parse_topics(text)
        taxonomy.android_subtopics = self._parse_android_subtopics(text)
        return taxonomy

    def _parse_topics(self, text: str) -> Set[str]:
        pattern = re.compile(r"### Valid Topics.*?```yaml(.*?)```", re.DOTALL)
        match = pattern.search(text)
        if not match:
            return set()
        block = match.group(1)
        topics = set()
        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            token = line.split("#", 1)[0].strip()
            if token:
                topics.add(token)
        return topics

    def _parse_android_subtopics(self, text: str) -> Set[str]:
        pattern = re.compile(
            r"### Android Subtopics.*?```yaml(.*?)```", re.DOTALL
        )
        match = pattern.search(text)
        if not match:
            return set()
        block = match.group(1)
        values = set()
        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            for token in line.split(","):
                token = token.strip()
                if token:
                    values.add(token)
        return values
