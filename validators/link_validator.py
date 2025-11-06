"""Validate wikilinks and related YAML references."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Set

from .base import BaseValidator, Severity
from .config import (
    RELATED_LINKS_MIN_RECOMMENDED,
    RELATED_LINKS_MAX_RECOMMENDED,
    CONCEPT_PREFIX,
    QUESTION_PREFIX,
)
from .registry import ValidatorRegistry


@ValidatorRegistry.register
class LinkValidator(BaseValidator):
    """Ensure internal links resolve and concept references exist."""

    WIKILINK_PATTERN = re.compile(r"\[\[([^\]]+)\]\]")

    def __init__(
        self,
        *,
        content: str,
        frontmatter: dict,
        path: str,
        taxonomy,
        index: Set[str],
    ):
        super().__init__(content=content, frontmatter=frontmatter, path=path, taxonomy=taxonomy)
        self.index = index

    def validate(self):
        self._check_moc_exists()
        self._check_related_links()
        self._check_related_links_quality()
        self._check_wikilinks()
        self._check_concept_link_presence()
        return self._summary

    def _check_moc_exists(self) -> None:
        moc = self.frontmatter.get("moc")
        if moc:
            if not self._link_exists(moc):
                self.add_issue(
                    Severity.ERROR,
                    f"moc '{moc}' does not match any note filename",
                    field="moc",
                )
            else:
                self.add_passed("moc link resolves")

    def _check_related_links(self) -> None:
        related = self.frontmatter.get("related") or []
        for item in related:
            if not isinstance(item, str):
                self.add_issue(
                    Severity.ERROR,
                    "related entries must be strings",
                    field="related",
                )
                continue
            if self._link_exists(item):
                continue
            self.add_issue(
                Severity.ERROR,
                f"related link '{item}' cannot be resolved",
                field="related",
            )

    def _check_wikilinks(self) -> None:
        if not self.content:
            return
        for match in self.WIKILINK_PATTERN.finditer(self.content):
            target = match.group(1).strip()
            if "|" in target:
                target = target.split("|", 1)[0]
            if not self._link_exists(target):
                self.add_issue(
                    Severity.ERROR,
                    f"Wikilink [[{target}]] does not match any note filename",
                )

    def _check_related_links_quality(self) -> None:
        """Check quality of related links in YAML frontmatter."""
        related = self.frontmatter.get("related") or []

        # Skip if not a list or empty (already reported by _check_related_links)
        if not isinstance(related, list):
            return

        # Check minimum count
        if len(related) < RELATED_LINKS_MIN_RECOMMENDED:
            self.add_issue(
                Severity.WARNING,
                f"Related field has {len(related)} item(s). "
                f"Recommended: {RELATED_LINKS_MIN_RECOMMENDED}-{RELATED_LINKS_MAX_RECOMMENDED} items "
                "(mix of concept links c-... and question links q-...)",
                field="related",
            )
        elif len(related) > RELATED_LINKS_MAX_RECOMMENDED:
            self.add_issue(
                Severity.INFO,
                f"Related field has {len(related)} items. "
                f"Recommended: {RELATED_LINKS_MIN_RECOMMENDED}-{RELATED_LINKS_MAX_RECOMMENDED} items "
                "for focused cross-referencing",
                field="related",
            )
        else:
            self.add_passed(f"Related field has {len(related)} items (optimal range)")

        # Check for concept links
        concept_links = [r for r in related if isinstance(r, str) and r.startswith(CONCEPT_PREFIX)]
        question_links = [r for r in related if isinstance(r, str) and r.startswith(QUESTION_PREFIX)]

        if not concept_links:
            self.add_issue(
                Severity.WARNING,
                "Related field should include at least 1 concept link (c-...) "
                "for foundational knowledge",
                field="related",
            )
        else:
            self.add_passed(f"Related field includes {len(concept_links)} concept link(s)")

        # Informational: mention question links
        if question_links:
            self.add_passed(f"Related field includes {len(question_links)} question link(s)")

    def _check_concept_link_presence(self) -> None:
        if not self.content:
            return
        if "[[c-" not in self.content:
            self.add_issue(
                Severity.WARNING,
                "Note should include at least one concept link ([[c-...]]) in content body",
            )

    def _link_exists(self, note_id: str) -> bool:
        note_name = f"{note_id}.md" if not note_id.endswith(".md") else note_id
        return note_name in self.index
