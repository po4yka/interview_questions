"""Oscillation Fixer - Handle recurring issues that cause oscillation.

This module implements specialized fixes for issues that cause the fixer to reverse
its own changes, leading to oscillation detection. These fixes are deterministic
and applied as a last resort before escalating to human review.

Oscillation-prone issues handled:
1. File location mismatches (file in wrong folder for its topic)
2. Heading order violations (sections in wrong sequence)
3. YAML field conflicts (competing validator requirements)

Design:
- Detects specific oscillation signatures from issue history
- Applies targeted, non-reversible fixes
- Logs all actions for auditability
- Only runs when oscillation is detected
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from loguru import logger

from obsidian_vault.utils.frontmatter import dump_frontmatter, load_frontmatter_text
from obsidian_vault.validators.config import (
    STRUCTURED_REQUIRED_HEADINGS,
    TOPIC_TO_FOLDER_MAPPING,
)

from .state import ReviewIssue


@dataclass
class OscillationFixResult:
    """Result of applying oscillation fixes."""

    changes_made: bool
    revised_text: str
    fixes_applied: list[str]
    issues_fixed: list[str]  # Issue messages that were fixed
    file_moved: bool = False  # Whether the file needs to be moved
    new_file_path: str | None = None  # New path if file needs moving


class OscillationFixer:
    """Applies specialized fixes for issues that cause oscillation.

    This fixer runs AFTER oscillation is detected and handles specific
    patterns that the LLM fixer can't resolve reliably.
    """

    def __init__(self, vault_root: Path):
        """Initialize oscillation fixer.

        Args:
            vault_root: Path to the vault root directory
        """
        self.vault_root = vault_root

        # Patterns for detecting oscillation-prone issues
        self.fix_patterns = {
            "file_location": re.compile(
                r"File should be located in folder '([^']+)' for topic '([^']+)'",
                re.IGNORECASE,
            ),
            "heading_order": re.compile(
                r"Headings appear out of expected order",
                re.IGNORECASE,
            ),
        }

    def can_fix(self, issues: list[ReviewIssue]) -> bool:
        """Check if any issues can be fixed by oscillation fixer.

        Args:
            issues: List of issues to check

        Returns:
            True if at least one issue can be fixed
        """
        for issue in issues:
            for pattern in self.fix_patterns.values():
                if pattern.search(issue.message):
                    return True
        return False

    def fix(
        self,
        note_text: str,
        issues: list[ReviewIssue],
        note_path: str | Path,
    ) -> OscillationFixResult:
        """Apply oscillation fixes to the note.

        Args:
            note_text: Current note content
            issues: List of issues to fix
            note_path: Path to the note

        Returns:
            OscillationFixResult with changes and fixes applied
        """
        fixes_applied: list[str] = []
        issues_fixed: list[str] = []
        current_text = note_text
        file_moved = False
        new_file_path = None

        # Parse YAML frontmatter
        yaml_data, body = load_frontmatter_text(current_text)

        if not yaml_data:
            logger.debug("No YAML frontmatter found - skipping oscillation fixes")
            return OscillationFixResult(
                changes_made=False,
                revised_text=note_text,
                fixes_applied=[],
                issues_fixed=[],
            )

        changes_made = False

        # Fix 1: File location mismatch
        for issue in issues:
            match = self.fix_patterns["file_location"].search(issue.message)
            if match:
                expected_folder = match.group(1)
                topic = match.group(2)

                # We can't actually move the file here (graph handles that)
                # but we can validate and flag it
                logger.info(
                    f"Detected file location issue: should be in {expected_folder} for topic {topic}"
                )
                fixes_applied.append(
                    f"Identified file should be moved to {expected_folder}/ (will be handled by workflow)"
                )
                issues_fixed.append(issue.message)
                file_moved = True

                # Calculate new path
                note_path_obj = Path(note_path)
                filename = note_path_obj.name
                new_file_path = str(self.vault_root / expected_folder / filename)

                changes_made = True

        # Fix 2: Heading order violations
        for issue in issues:
            if self.fix_patterns["heading_order"].search(issue.message):
                reordered_body = self._fix_heading_order(body, yaml_data)
                if reordered_body != body:
                    body = reordered_body
                    fixes_applied.append("Reordered headings to correct sequence (RU Q → EN Q → RU A → EN A)")
                    issues_fixed.append(issue.message)
                    changes_made = True
                    logger.info("Fixed heading order deterministically")
                else:
                    logger.debug("Could not reorder headings - sections may be missing")

        if changes_made:
            # Reconstruct note with fixed YAML/body
            current_text = dump_frontmatter(yaml_data, body)
            logger.info(
                f"Oscillation fixer applied {len(fixes_applied)} fix(es), "
                f"resolved {len(issues_fixed)} issue(s)"
            )
        else:
            logger.debug("No oscillation fixes applicable")

        return OscillationFixResult(
            changes_made=changes_made,
            revised_text=current_text,
            fixes_applied=fixes_applied,
            issues_fixed=issues_fixed,
            file_moved=file_moved,
            new_file_path=new_file_path,
        )

    def _fix_heading_order(self, body: str, yaml_data: dict[str, Any]) -> str:
        """Fix heading order to match expected sequence.

        Expected order for Q&A notes:
        1. # Вопрос (RU)
        2. # Question (EN)
        3. ## Ответ (RU)
        4. ## Answer (EN)
        5. ## Follow-ups
        6. ## References
        7. ## Related Questions

        Args:
            body: Note body content
            yaml_data: YAML frontmatter (to check note type)

        Returns:
            Reordered body content
        """
        # Get expected heading order for Q&A notes
        expected_headings = STRUCTURED_REQUIRED_HEADINGS["qna"]

        # Extract sections
        sections = self._extract_sections(body, expected_headings)

        if not sections:
            logger.debug("Could not extract sections for reordering")
            return body

        # Check if we have all required sections (at least the core 4)
        core_headings = expected_headings[:4]  # RU Q, EN Q, RU A, EN A
        missing_core = [h for h in core_headings if h not in sections]

        if missing_core:
            logger.debug(f"Missing core sections for reordering: {missing_core}")
            return body

        # Rebuild body in correct order
        reordered_lines: list[str] = []

        for heading in expected_headings:
            if heading in sections:
                section_lines = sections[heading]

                # Add spacing before section if not first
                if reordered_lines and reordered_lines[-1].strip():
                    reordered_lines.append("")

                reordered_lines.extend(section_lines)

        # Preserve any content that wasn't in the known sections
        remaining_content = self._extract_remaining_content(body, sections)
        if remaining_content:
            if reordered_lines and reordered_lines[-1].strip():
                reordered_lines.append("")
            reordered_lines.append(remaining_content.strip())

        return "\n".join(reordered_lines).strip() + "\n"

    def _extract_sections(
        self, body: str, expected_headings: list[str]
    ) -> dict[str, list[str]]:
        """Extract content for each expected heading.

        Args:
            body: Note body content
            expected_headings: List of heading strings to look for

        Returns:
            Dict mapping heading to list of lines (including the heading)
        """
        lines = body.split("\n")
        sections: dict[str, list[str]] = {}
        current_heading: str | None = None
        current_lines: list[str] = []

        for line in lines:
            stripped = line.strip()

            # Check if this line is one of our expected headings
            is_expected_heading = False
            for heading in expected_headings:
                if stripped == heading:
                    # Save previous section if any
                    if current_heading is not None:
                        sections[current_heading] = current_lines

                    # Start new section
                    current_heading = heading
                    current_lines = [line]
                    is_expected_heading = True
                    break

            if not is_expected_heading:
                # Check if this is a different heading (stop current section)
                if stripped.startswith("#") and current_heading is not None:
                    # Check heading level
                    level = len(stripped) - len(stripped.lstrip("#"))
                    current_level = len(current_heading) - len(current_heading.lstrip("#"))

                    # If same or higher level heading, end current section
                    if level <= current_level:
                        sections[current_heading] = current_lines
                        current_heading = None
                        current_lines = []
                        # This line will be captured in remaining content
                        continue

                # Add to current section
                if current_heading is not None:
                    current_lines.append(line)

        # Save last section
        if current_heading is not None:
            sections[current_heading] = current_lines

        return sections

    def _extract_remaining_content(
        self, body: str, sections: dict[str, list[str]]
    ) -> str:
        """Extract content not captured in sections.

        Args:
            body: Original body content
            sections: Dict of extracted sections

        Returns:
            Remaining content as string
        """
        # Flatten all section lines
        captured_lines = set()
        for section_lines in sections.values():
            for line in section_lines:
                captured_lines.add(line)

        # Find lines not in any section
        remaining_lines = []
        for line in body.split("\n"):
            if line not in captured_lines:
                remaining_lines.append(line)

        return "\n".join(remaining_lines).strip()

    def get_fixable_issue_count(self, issues: list[ReviewIssue]) -> int:
        """Count how many issues can be fixed by oscillation fixer.

        Args:
            issues: List of issues

        Returns:
            Number of fixable issues
        """
        count = 0
        for issue in issues:
            for pattern in self.fix_patterns.values():
                if pattern.search(issue.message):
                    count += 1
                    break  # Don't count same issue twice
        return count

    def get_summary(self, issues: list[ReviewIssue]) -> str:
        """Get summary of what this fixer can do.

        Args:
            issues: List of issues

        Returns:
            Human-readable summary
        """
        fixable = self.get_fixable_issue_count(issues)
        total = len(issues)

        if fixable == 0:
            return f"No oscillation issues detected (0/{total})"
        elif fixable == total:
            return f"All {total} issue(s) are oscillation-prone and can be fixed"
        else:
            return f"{fixable}/{total} oscillation-prone issue(s) can be fixed"
