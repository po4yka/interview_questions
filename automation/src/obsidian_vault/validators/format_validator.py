"""Validate filename conventions and placement."""

from __future__ import annotations

from pathlib import Path

from .base import BaseValidator, Severity
from .config import (
    CONCEPT_PREFIX,
    CONCEPTS_FOLDER,
    FILENAME_PATTERN,
    MOC_PREFIX,
    MOCS_FOLDER,
    TOPIC_TO_FOLDER_MAPPING,
)
from .registry import ValidatorRegistry


@ValidatorRegistry.register
class FormatValidator(BaseValidator):
    """Check filename conventions and folder alignment with topic."""

    def __init__(self, *, content: str, frontmatter: dict, path: str, taxonomy, vault_root: Path):
        super().__init__(content=content, frontmatter=frontmatter, path=path, taxonomy=taxonomy)
        self.vault_root = vault_root

    def validate(self):
        self._check_filename_pattern()
        self._check_folder_matches_topic()
        return self._summary

    def _check_filename_pattern(self) -> None:
        filename = Path(self.path).name
        if filename.startswith(CONCEPT_PREFIX) and filename.endswith(".md"):
            self.add_passed("Concept filename pattern accepted")
            return
        if filename.startswith(MOC_PREFIX) and filename.endswith(".md"):
            self.add_passed("MOC filename pattern accepted")
            return
        if not FILENAME_PATTERN.match(filename):
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
        filename = Path(self.path).name
        if filename.startswith(CONCEPT_PREFIX):
            if CONCEPTS_FOLDER not in actual.parts:
                self.add_issue(
                    Severity.ERROR,
                    f"Concept notes must reside in {CONCEPTS_FOLDER}/",
                )
            else:
                self.add_passed("Concept folder placement valid")
            return
        if filename.startswith(MOC_PREFIX):
            if MOCS_FOLDER not in actual.parts:
                self.add_issue(
                    Severity.ERROR,
                    f"MOCs must reside in {MOCS_FOLDER}/",
                )
            else:
                self.add_passed("MOC folder placement valid")
            return
        if expected_folder and expected_folder not in actual.parts:
            self.add_issue(
                Severity.ERROR,
                f"File should be located in folder '{expected_folder}' for topic '{topic}'",
            )
        else:
            self.add_passed("Folder placement matches topic")

    def _expected_folder_for_topic(self, topic: str) -> str | None:
        return TOPIC_TO_FOLDER_MAPPING.get(topic)
