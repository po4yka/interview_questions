"""Validate code formatting rules for inline code references."""

from __future__ import annotations

import re

from .base import BaseValidator, Severity
from .config import COMMON_TYPE_NAMES, UNESCAPED_GENERIC_PATTERN
from .registry import ValidatorRegistry


SETEXT_UNDERLINE_PATTERN = re.compile(r"^(=+|-+)\s*$")


@ValidatorRegistry.register
class CodeFormatValidator(BaseValidator):
    """
    Validate code formatting rules as specified in NOTE-REVIEW-PROMPT.md.

    Checks:
    - Generic types with angle brackets wrapped in backticks
    - Type names, class names wrapped in backticks
    - Method names and API references wrapped in backticks
    """

    def validate(self):
        if not self.content:
            return self._summary

        self._check_unescaped_generics()
        self._check_unescaped_type_names()

        return self._summary

    def _check_unescaped_generics(self) -> None:
        """
        Find generic types not wrapped in backticks outside code blocks.

        Examples of issues:
        - ArrayList<String> → should be `ArrayList<String>`
        - Map<String, Int> → should be `Map<String, Int>`
        """

        # Split content by code blocks to avoid checking inside them
        parts = self._split_by_code_blocks(self.content)

        issues_found = []

        for _part_idx, (part, is_code_block) in enumerate(parts):
            if is_code_block:
                continue  # Skip code blocks

            for match in UNESCAPED_GENERIC_PATTERN.finditer(part):
                type_with_generic = match.group(0)
                line_num = self.content[: self.content.find(part) + match.start()].count("\n") + 1

                # Avoid duplicate reporting
                if type_with_generic not in issues_found:
                    issues_found.append(type_with_generic)
                    self.add_issue(
                        Severity.ERROR,
                        f"Generic type '{type_with_generic}' not wrapped in backticks "
                        f"(will be interpreted as HTML tag). Use: `{type_with_generic}`",
                        line=line_num,
                    )

        if not issues_found:
            self.add_passed("No unescaped generic types found")

    def _check_unescaped_type_names(self) -> None:
        """
        Find common type names that should be wrapped in backticks.

        This is a heuristic check for common types mentioned in NOTE-REVIEW-PROMPT.md:
        - String, Int, Boolean, etc.
        - ArrayList, HashMap, etc.
        - Parcelable, Bundle, etc.
        """

        parts = self._split_by_code_blocks(self.content)
        issues_found = set()
        offset = 0

        for part, is_code_block in parts:
            if is_code_block:
                offset += len(part)
                continue

            for type_name in COMMON_TYPE_NAMES:
                if type_name in issues_found:
                    continue

                pattern = rf"(?<!`)\b{re.escape(type_name)}\b(?!`)"

                for match in re.finditer(pattern, part):
                    line_start = part.rfind("\n", 0, match.start()) + 1
                    line_end = part.find("\n", match.start())
                    if line_end == -1:
                        line_end = len(part)

                    line_text_raw = part[line_start:line_end]
                    normalized_line = self._normalize_heading_candidate(line_text_raw)
                    next_line_raw = self._get_next_line(part, line_end)
                    normalized_next = self._normalize_heading_candidate(next_line_raw)

                    if normalized_line.startswith("#") or self._is_setext_heading_line(
                        normalized_line, normalized_next
                    ):
                        continue

                    issues_found.add(type_name)
                    absolute_match_start = offset + match.start()
                    line_num = self.content[:absolute_match_start].count("\n") + 1

                    self.add_issue(
                        Severity.WARNING,
                        f"Type name '{type_name}' found without backticks (line ~{line_num}). "
                        f"Consider wrapping in backticks: `{type_name}`",
                    )
                    break

            offset += len(part)

        if not issues_found:
            self.add_passed("Common type names appear properly formatted")

    def _split_by_code_blocks(self, content: str) -> list[tuple[str, bool]]:
        """
        Split content into parts: (text, is_code_block).

        Returns list of tuples where:
        - First element is the text
        - Second element is True if it's inside a code block, False otherwise
        """
        parts = []

        # Pattern to match code blocks (``` ... ```)
        code_block_pattern = r"```[\s\S]*?```"

        last_end = 0
        for match in re.finditer(code_block_pattern, content):
            # Add text before code block
            if match.start() > last_end:
                parts.append((content[last_end : match.start()], False))

            # Add code block
            parts.append((match.group(0), True))
            last_end = match.end()

        # Add remaining text
        if last_end < len(content):
            parts.append((content[last_end:], False))

        return parts if parts else [(content, False)]

    @staticmethod
    def _normalize_heading_candidate(line: str) -> str:
        """Remove leading whitespace and blockquote markers for heading checks."""

        stripped = line.lstrip()
        while stripped.startswith(">"):
            stripped = stripped[1:].lstrip()
        return stripped.rstrip("\r")

    @staticmethod
    def _get_next_line(part: str, line_end: int) -> str:
        """Return the following line (without newline) for heading detection."""

        if line_end >= len(part):
            return ""

        next_line_start = line_end
        if part[line_end : line_end + 1] == "\n":
            next_line_start += 1
        elif part[line_end : line_end + 2] == "\r\n":
            next_line_start += 2
        else:
            if part[line_end : line_end + 1] == "\r":
                next_line_start += 1
                if part[next_line_start : next_line_start + 1] == "\n":
                    next_line_start += 1

        if next_line_start >= len(part):
            return ""

        next_line_end = part.find("\n", next_line_start)
        if next_line_end == -1:
            next_line_end = len(part)

        return part[next_line_start:next_line_end].rstrip("\r")

    @staticmethod
    def _is_setext_heading_line(current_line: str, next_line: str) -> bool:
        """Check whether the current and next line compose a Setext heading."""

        if not current_line.strip():
            return False

        next_stripped = next_line.strip()
        if not next_stripped:
            return False

        return bool(SETEXT_UNDERLINE_PATTERN.fullmatch(next_stripped))
