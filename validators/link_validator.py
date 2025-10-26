"""Validate wikilinks and related YAML references."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Set

from .base import BaseValidator, Severity


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

    def _check_concept_link_presence(self) -> None:
        if not self.content:
            return
        if "[[c-" not in self.content:
            self.add_issue(
                Severity.WARNING,
                "Note should include at least one concept link ([[c-...]])",
            )

    def _link_exists(self, note_id: str) -> bool:
        note_name = f"{note_id}.md" if not note_id.endswith(".md") else note_id
        return note_name in self.index
