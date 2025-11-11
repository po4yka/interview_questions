"""Validate code formatting rules for inline code references."""

from __future__ import annotations

import re

from .base import BaseValidator, Severity
from .config import COMMON_TYPE_NAMES, UNESCAPED_GENERIC_PATTERN
from .registry import ValidatorRegistry


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

        for part, is_code_block in parts:
            if is_code_block:
                continue

            for type_name in COMMON_TYPE_NAMES:
                # Look for type name not in backticks
                # Pattern: type name not preceded/followed by backtick or alphanumeric
                pattern = rf"(?<!`)\b{re.escape(type_name)}\b(?!`)"

                matches = list(re.finditer(pattern, part))
                if matches and type_name not in issues_found:
                    # Skip matches that occur in Markdown headings
                    filtered_matches = []
                    for match in matches:
                        line_start = part.rfind("\n", 0, match.start()) + 1
                        line_end = part.find("\n", match.start())
                        if line_end == -1:
                            line_end = len(part)

                        line_text = part[line_start:line_end].lstrip()
                        if line_text.startswith("#"):
                            continue
                        filtered_matches.append(match)

                    if not filtered_matches:
                        continue

                    issues_found.add(type_name)
                    # Only report first occurrence to avoid spam
                    first_match = filtered_matches[0]
                    line_num = (
                        self.content[: self.content.find(part) + first_match.start()].count("\n")
                        + 1
                    )

                    self.add_issue(
                        Severity.WARNING,
                        f"Type name '{type_name}' found without backticks (line ~{line_num}). "
                        f"Consider wrapping in backticks: `{type_name}`",
                    )

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
