"""Validate filename conventions and placement."""

from __future__ import annotations

import os
import re
from pathlib import Path

from .base import BaseValidator, Severity


class FormatValidator(BaseValidator):
    """Check filename conventions and folder alignment with topic."""

    FILENAME_PATTERN = re.compile(
        r"^q-[a-z0-9-]+--[a-z0-9-]+--(easy|medium|hard)\.md$"
    )

    def __init__(self, *, content: str, frontmatter: dict, path: str, taxonomy, vault_root: Path):
        super().__init__(content=content, frontmatter=frontmatter, path=path, taxonomy=taxonomy)
        self.vault_root = vault_root

    def validate(self):
        self._check_filename_pattern()
        self._check_folder_matches_topic()
        return self._summary

    def _check_filename_pattern(self) -> None:
        filename = Path(self.path).name
        if not self.FILENAME_PATTERN.match(filename):
            self.add_issue(
                Severity.ERROR,
                "Filename must follow q-<slug>--<topic>--<difficulty>.md",
            )
        else:
            self.add_passed("Filename pattern valid")

    def _check_folder_matches_topic(self) -> None:
        topic = self.frontmatter.get("topic")
        if not topic:
            return
        expected_folder = self._expected_folder_for_topic(topic)
        actual = Path(self.path).parent
        if expected_folder and expected_folder not in actual.parts:
            self.add_issue(
                Severity.ERROR,
                f"File should be located in folder '{expected_folder}' for topic '{topic}'",
            )
        else:
            self.add_passed("Folder placement matches topic")

    def _expected_folder_for_topic(self, topic: str) -> str | None:
        mapping = {
            "algorithms": "20-Algorithms",
            "system-design": "30-System-Design",
            "android": "40-Android",
            "backend": "50-Backend",
            "cs": "60-CompSci",
            "kotlin": "70-Kotlin",
            "tools": "80-Tools",
            "behavioral": "00-Behavioural",
        }
        return mapping.get(topic)
