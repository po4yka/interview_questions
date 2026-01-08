"""Helpers to load controlled vocabularies from TAXONOMY.md."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Taxonomy:
    topics: set[str] = field(default_factory=set)
    android_subtopics: set[str] = field(default_factory=set)


class TaxonomyLoader:
    """Parses TAXONOMY.md to expose controlled vocabularies."""

    def __init__(self, vault_root: Path):
        self.vault_root = vault_root
        self.taxonomy_path = vault_root / "InterviewQuestions" / "00-Administration" / "Vault-Rules" / "TAXONOMY.md"
        self.android_subtopics_path = vault_root / "InterviewQuestions" / "00-Administration" / "Vault-Rules" / "ANDROID-SUBTOPICS.md"

    def load(self) -> Taxonomy:
        taxonomy = Taxonomy()
        if not self.taxonomy_path.exists():
            return taxonomy

        # Load main taxonomy
        text = self.taxonomy_path.read_text(encoding="utf-8")
        taxonomy.topics = self._parse_topics(text)

        # Load Android subtopics
        if self.android_subtopics_path.exists():
            android_text = self.android_subtopics_path.read_text(encoding="utf-8")
            taxonomy.android_subtopics = self._parse_android_subtopics(android_text)

        return taxonomy

    def _parse_topics(self, text: str) -> set[str]:
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

    def _parse_android_subtopics(self, text: str) -> set[str]:
        # Find all YAML blocks in the file
        pattern = re.compile(r"```yaml(.*?)```", re.DOTALL)
        matches = pattern.findall(text)

        values = set()
        for block in matches:
            for line in block.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # Handle "key: value" (ignore) or just "value" list items
                # The format in ANDROID-SUBTOPICS.md is "key   # comment"
                token = line.split("#", 1)[0].strip()
                if token and ":" not in token: # Simple check to avoid key-value pairs if any
                    values.add(token)
        return values
