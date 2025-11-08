"""Android-specific validation rules."""

from __future__ import annotations

from pathlib import Path

from .base import BaseValidator, Severity
from .registry import ValidatorRegistry


@ValidatorRegistry.register
class AndroidValidator(BaseValidator):
    """Apply Android specific taxonomy checks."""

    def validate(self):
        if self.frontmatter.get("topic") != "android":
            return self._summary
        filename = Path(self.path).name
        if filename.startswith("c-"):
            return self._summary
        self._check_subtopics()
        self._check_tag_mirroring()
        self._check_moc()
        return self._summary

    def _check_subtopics(self) -> None:
        subtopics = self.frontmatter.get("subtopics") or []
        allowed = self.taxonomy.android_subtopics
        invalid = [item for item in subtopics if item not in allowed]
        if invalid:
            self.add_issue(
                Severity.ERROR,
                f"Invalid Android subtopics: {', '.join(invalid)}",
                field="subtopics",
            )
        else:
            self.add_passed("Android subtopics valid")

    def _check_tag_mirroring(self) -> None:
        tags = self.frontmatter.get("tags") or []
        subtopics = self.frontmatter.get("subtopics") or []
        missing = [f"android/{sub}" for sub in subtopics if f"android/{sub}" not in tags]
        if missing:
            self.add_issue(
                Severity.ERROR,
                "Android tags must mirror subtopics: missing " + ", ".join(missing),
                field="tags",
            )
        else:
            self.add_passed("Android tags mirror subtopics")

    def _check_moc(self) -> None:
        moc = self.frontmatter.get("moc")
        if moc != "moc-android":
            self.add_issue(
                Severity.ERROR,
                "Android notes must use moc-android",
                field="moc",
            )
