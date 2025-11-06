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
        self._check_question_blockquote_syntax(content)
        self._check_references(content)
        self._check_optional_question_versions(content)
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

    def _check_question_blockquote_syntax(self, content: str) -> None:
        """Ensure questions use blockquote syntax (>) as required by NOTE-REVIEW-PROMPT.md."""

        # Pattern: heading followed by optional blank lines, then check for blockquote
        patterns = [
            (r"# Вопрос \(RU\)\s*\n(?:\s*\n)*((?!>)[^\n])", "Russian question", "# Вопрос (RU)"),
            (r"# Question \(EN\)\s*\n(?:\s*\n)*((?!>)[^\n])", "English question", "# Question (EN)"),
        ]

        for pattern, lang_label, heading in patterns:
            match = re.search(pattern, content)
            if match:
                # Get the line number for better error reporting
                lines_before = content[:match.start()].count('\n')
                self.add_issue(
                    Severity.ERROR,
                    f"{lang_label} missing blockquote syntax: expected '>' after '{heading}' heading",
                    line=lines_before + 1,
                )
            else:
                # Check if heading exists and has blockquote
                heading_pattern = rf"{re.escape(heading)}\s*\n(?:\s*\n)*>"
                if re.search(heading_pattern, content):
                    # Only mark as passed if we found the heading with proper blockquote
                    if lang_label == "English question":  # Only log once
                        self.add_passed("Questions use blockquote syntax (>)")

    def _check_optional_question_versions(self, content: str) -> None:
        """Validate optional Short/Detailed Version subsections for system design questions."""

        # Check Russian subsections
        has_ru_short = "## Краткая Версия" in content
        has_ru_detailed = "## Подробная Версия" in content

        # Check English subsections
        has_en_short = "## Short Version" in content
        has_en_detailed = "## Detailed Version" in content

        # If no versions present, skip validation
        if not any([has_ru_short, has_ru_detailed, has_en_short, has_en_detailed]):
            return

        # If one language has versions, both should have them
        if has_ru_short != has_en_short:
            self.add_issue(
                Severity.WARNING,
                "Mismatch: RU has 'Краткая Версия' but EN missing 'Short Version' (or vice versa)",
            )

        if has_ru_detailed != has_en_detailed:
            self.add_issue(
                Severity.WARNING,
                "Mismatch: RU has 'Подробная Версия' but EN missing 'Detailed Version' (or vice versa)",
            )

        # If Short Version exists, check it comes before Detailed
        if has_ru_short and has_ru_detailed:
            ru_short_pos = content.find("## Краткая Версия")
            ru_detailed_pos = content.find("## Подробная Версия")
            if ru_short_pos > ru_detailed_pos:
                self.add_issue(
                    Severity.ERROR,
                    "RU: 'Краткая Версия' must come before 'Подробная Версия'",
                )

        if has_en_short and has_en_detailed:
            en_short_pos = content.find("## Short Version")
            en_detailed_pos = content.find("## Detailed Version")
            if en_short_pos > en_detailed_pos:
                self.add_issue(
                    Severity.ERROR,
                    "EN: 'Short Version' must come before 'Detailed Version'",
                )

        # Check these subsections have content
        if has_ru_short:
            self._check_subsection_has_content(
                content, "## Краткая Версия", ["## Подробная Версия", "# Question (EN)"]
            )

        if has_ru_detailed:
            self._check_subsection_has_content(
                content, "## Подробная Версия", ["# Question (EN)"]
            )

        if has_en_short:
            self._check_subsection_has_content(
                content, "## Short Version", ["## Detailed Version", "## Ответ (RU)"]
            )

        if has_en_detailed:
            self._check_subsection_has_content(
                content, "## Detailed Version", ["## Ответ (RU)"]
            )

        # Log success if used correctly
        if (has_ru_short and has_en_short and has_ru_detailed and has_en_detailed):
            self.add_passed("Optional question versions (Short/Detailed) present and aligned")

    def _check_subsection_has_content(
        self, content: str, start_heading: str, end_headings: list[str]
    ) -> None:
        """Check if subsection between heading and any of the end headings has content."""
        # Find the start position
        start_pos = content.find(start_heading)
        if start_pos == -1:
            return

        # Find the earliest end position
        end_pos = len(content)
        for end_heading in end_headings:
            pos = content.find(end_heading, start_pos + len(start_heading))
            if pos != -1 and pos < end_pos:
                end_pos = pos

        # Extract text between start and end
        text = content[start_pos + len(start_heading):end_pos].strip()

        if not text or len(text) < 50:  # Minimum 50 chars
            self.add_issue(
                Severity.WARNING,
                f"Subsection '{start_heading}' should contain substantial text (>50 chars)",
            )

    @staticmethod
    def _extract_section(content: str, heading: str) -> str:
        pattern = re.compile(
            rf"{re.escape(heading)}\s*(.*?)(\n## |\Z)", re.DOTALL
        )
        match = pattern.search(content)
        return match.group(1).strip() if match else ""
