"""Validate bilingual content structure for notes."""

from __future__ import annotations

import re
from pathlib import Path

from .base import BaseValidator, Severity


class ContentValidator(BaseValidator):
    STRUCTURED_REQUIRED_HEADINGS = {
        "qna": [
            "# Вопрос (RU)",
            "# Question (EN)",
            "## Ответ (RU)",
            "## Answer (EN)",
            "## Follow-ups",
            "## References",
            "## Related Questions",
        ],
        "concept": [
            "# Summary (EN)",
            "## Summary (RU)",
        ],
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        topic = self.frontmatter.get("topic")
        filename = Path(self.path).name
        if filename.startswith("c-"):
            self.required_headings = self.STRUCTURED_REQUIRED_HEADINGS["concept"]
        else:
            self.required_headings = self.STRUCTURED_REQUIRED_HEADINGS["qna"]
    """Ensure content follows the bilingual template."""

    REQUIRED_HEADINGS = [
        "# Вопрос (RU)",
        "# Question (EN)",
        "## Ответ (RU)",
        "## Answer (EN)",
        "## Follow-ups",
        "## References",
        "## Related Questions",
    ]

    def validate(self):
        filename = Path(self.path).name
        if filename.startswith("c-"):
            return self._summary

        content = self.content
        if content is None:
            self.add_issue(Severity.CRITICAL, "File body missing")
            return self._summary

        positions = self._check_required_headings(content)
        if positions is not None:
            self._check_heading_order(positions)
            self._check_section_body(content, "# Вопрос (RU)", "# Question (EN)")
            self._check_section_body(content, "# Question (EN)", "## Ответ (RU)")
            self._check_section_body(content, "## Ответ (RU)", "## Answer (EN)")
            self._check_section_body(content, "## Answer (EN)", "## Follow-ups")
        self._check_references(content)
        return self._summary

    def _check_required_headings(self, content: str):
        positions = {}
        for heading in self.REQUIRED_HEADINGS:
            index = content.find(heading)
            if index == -1:
                self.add_issue(
                    Severity.CRITICAL,
                    f"Missing required heading '{heading}'",
                )
            else:
                positions[heading] = index
        if len(positions) == len(self.REQUIRED_HEADINGS):
            self.add_passed("All required headings present")
            return positions
        return None

    def _check_heading_order(self, positions: dict) -> None:
        ordered = [positions[h] for h in self.REQUIRED_HEADINGS]
        if ordered != sorted(ordered):
            self.add_issue(
                Severity.ERROR,
                "Headings appear out of expected order (should be: RU question → EN question → RU answer → EN answer)",
            )
        else:
            self.add_passed("Heading order valid")

    def _check_section_body(self, content: str, start: str, end: str) -> None:
        pattern = re.compile(
            rf"{re.escape(start)}\s*(.*?)\s*{re.escape(end)}", re.DOTALL
        )
        match = pattern.search(content)
        if not match:
            # Already reported missing headings; avoid duplicate errors.
            return
        text = match.group(1).strip()
        if not text:
            self.add_issue(
                Severity.WARNING,
                f"Section '{start}' should contain explanatory text",
            )

    def _check_references(self, content: str) -> None:
        references_section = self._extract_section(content, "## References")
        if references_section and "[[" not in references_section and "http" not in references_section:
            self.add_issue(
                Severity.INFO,
                "References section is present but contains no links",
            )

    @staticmethod
    def _extract_section(content: str, heading: str) -> str:
        pattern = re.compile(
            rf"{re.escape(heading)}\s*(.*?)(\n## |\Z)", re.DOTALL
        )
        match = pattern.search(content)
        return match.group(1).strip() if match else ""
