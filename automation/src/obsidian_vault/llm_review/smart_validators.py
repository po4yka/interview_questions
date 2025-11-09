"""Smart Validator Selection - Only run validators relevant to changes.

PHASE 2 FIX: This module determines which validators need to run based on
what content changed, reducing unnecessary LLM calls.

Example Optimization:
- Before: Run metadata + structural + parity on every iteration = 3 LLM calls
- After: If only YAML changed, skip parity check = 2 LLM calls (33% reduction)

Key Insight:
If the fixer only modified YAML frontmatter and didn't touch the content body,
there's no need to re-run bilingual parity checks or structural validators.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from loguru import logger


@dataclass
class ContentDiff:
    """Represents what changed between two versions of a note."""

    yaml_changed: bool
    body_changed: bool
    structure_changed: bool  # Sections added/removed/reordered
    code_changed: bool  # Code blocks modified


ValidatorType = Literal["metadata", "structural", "parity"]


class SmartValidatorSelector:
    """Determines which validators need to run based on content changes.

    This prevents wasted LLM calls by skipping validators that couldn't
    possibly find new issues based on what changed.
    """

    def __init__(self):
        """Initialize smart validator selector."""
        pass

    def detect_changes(
        self,
        content_before: str,
        content_after: str,
    ) -> ContentDiff:
        """Detect what changed between two versions of a note.

        Args:
            content_before: Note content before fixes
            content_after: Note content after fixes

        Returns:
            ContentDiff describing what changed
        """
        # Simple but effective heuristics

        # Parse both versions
        yaml_before, body_before = self._parse_note(content_before)
        yaml_after, body_after = self._parse_note(content_after)

        # Check what changed
        yaml_changed = yaml_before != yaml_after
        body_changed = body_before != body_after

        # Check if structure changed (section headers)
        structure_changed = False
        if body_changed:
            sections_before = self._extract_sections(body_before)
            sections_after = self._extract_sections(body_after)
            structure_changed = sections_before != sections_after

        # Check if code blocks changed
        code_changed = False
        if body_changed:
            code_blocks_before = self._extract_code_blocks(body_before)
            code_blocks_after = self._extract_code_blocks(body_after)
            code_changed = code_blocks_before != code_blocks_after

        return ContentDiff(
            yaml_changed=yaml_changed,
            body_changed=body_changed,
            structure_changed=structure_changed,
            code_changed=code_changed,
        )

    def select_validators(
        self,
        diff: ContentDiff,
        iteration: int,
    ) -> list[ValidatorType]:
        """Select which validators need to run based on changes.

        RULES:
        1. First iteration: Run ALL validators (establish baseline)
        2. YAML changed: Run metadata validator
        3. Body changed: Run structural + parity validators
        4. Structure changed: Run all validators
        5. Nothing changed: Run only parity (quick sanity check)

        Args:
            diff: ContentDiff describing what changed
            iteration: Current iteration number (1-indexed)

        Returns:
            List of validator types to run
        """
        # First iteration: always run all validators
        if iteration == 1:
            logger.debug("Iteration 1: Running all validators")
            return ["metadata", "structural", "parity"]

        validators_needed: list[ValidatorType] = []

        # If YAML changed, need to validate metadata
        if diff.yaml_changed:
            validators_needed.append("metadata")
            logger.debug("YAML changed → metadata validator needed")

        # If body changed, need to validate structure and parity
        if diff.body_changed:
            validators_needed.append("structural")
            validators_needed.append("parity")
            logger.debug("Body changed → structural + parity validators needed")

        # If structure changed, run all validators (major change)
        if diff.structure_changed:
            if "metadata" not in validators_needed:
                validators_needed.append("metadata")
            logger.debug("Structure changed → all validators needed")

        # If nothing changed, still run parity as sanity check
        # (but skip metadata/structural since those couldn't have changed)
        if not diff.yaml_changed and not diff.body_changed:
            validators_needed.append("parity")
            logger.debug("No changes → parity-only sanity check")

        # Deduplicate and sort for consistency
        validators_needed = sorted(set(validators_needed))

        logger.info(f"Smart selection: Running {len(validators_needed)} validator(s): {validators_needed}")

        return validators_needed

    def _parse_note(self, content: str) -> tuple[str, str]:
        """Parse note into YAML and body sections.

        Args:
            content: Full note content

        Returns:
            Tuple of (yaml_section, body_section)
        """
        if not content.startswith("---"):
            return ("", content)

        # Find end of YAML frontmatter
        parts = content.split("---", 2)
        if len(parts) < 3:
            return ("", content)

        yaml_section = parts[1].strip()
        body_section = parts[2].strip()

        return (yaml_section, body_section)

    def _extract_sections(self, body: str) -> list[str]:
        """Extract section headers from body.

        Args:
            body: Note body content

        Returns:
            List of section headers (lines starting with #)
        """
        sections = []
        for line in body.split("\n"):
            stripped = line.strip()
            if stripped.startswith("#"):
                sections.append(stripped)
        return sections

    def _extract_code_blocks(self, body: str) -> list[str]:
        """Extract code blocks from body.

        Args:
            body: Note body content

        Returns:
            List of code blocks (content between ``` markers)
        """
        code_blocks = []
        in_code_block = False
        current_block = []

        for line in body.split("\n"):
            if line.strip().startswith("```"):
                if in_code_block:
                    # End of code block
                    code_blocks.append("\n".join(current_block))
                    current_block = []
                    in_code_block = False
                else:
                    # Start of code block
                    in_code_block = True
            elif in_code_block:
                current_block.append(line)

        return code_blocks

    def should_skip_validator(
        self,
        validator_type: ValidatorType,
        selected_validators: list[ValidatorType],
    ) -> bool:
        """Check if a validator should be skipped.

        Args:
            validator_type: Type of validator to check
            selected_validators: List of validators selected to run

        Returns:
            True if validator should be skipped
        """
        return validator_type not in selected_validators

    def get_skip_reason(
        self,
        validator_type: ValidatorType,
        diff: ContentDiff,
    ) -> str:
        """Get explanation for why a validator was skipped.

        Args:
            validator_type: Type of validator that was skipped
            diff: ContentDiff describing what changed

        Returns:
            Human-readable explanation
        """
        if validator_type == "metadata":
            if not diff.yaml_changed:
                return "YAML frontmatter unchanged - metadata validator skipped"

        if validator_type == "structural":
            if not diff.body_changed:
                return "Body content unchanged - structural validator skipped"

        if validator_type == "parity":
            if not diff.body_changed and not diff.structure_changed:
                return "Content structure unchanged - parity validator skipped"

        return f"{validator_type} validator skipped (no relevant changes)"

    def estimate_savings(
        self,
        selected_validators: list[ValidatorType],
        total_validators: int = 3,
    ) -> tuple[int, float]:
        """Estimate LLM call savings from smart selection.

        Args:
            selected_validators: Validators that will run
            total_validators: Total number of validators available

        Returns:
            Tuple of (calls_saved, percentage_saved)
        """
        calls_used = len(selected_validators)
        calls_saved = total_validators - calls_used
        percentage_saved = (calls_saved / total_validators) * 100 if total_validators > 0 else 0

        return (calls_saved, percentage_saved)
