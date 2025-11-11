"""Fix Memory system to prevent oscillation by tracking already-fixed fields.

This module implements the Fix Memory system from Phase 1 of the agent system fixes.
It tracks which fields have been fixed in previous iterations to prevent the fixer
from re-modifying already-corrected fields, which is a major cause of oscillation.

Key Features:
1. Tracks field paths and their fixed values
2. Detects regressions when fixed fields are modified again
3. Provides context to fixer agent about what's already been fixed
4. Prevents circular fix loops

Example Usage:
    memory = FixMemory()

    # After fixing a field in iteration 1
    memory.mark_fixed("created", "2024-10-12", iteration=1)
    memory.mark_fixed("updated", "2025-11-09", iteration=1)

    # In iteration 2, check before fixing
    if memory.is_fixed("created"):
        # Skip this fix to avoid regression
        value = memory.get_fixed_value("created")
        logger.info(f"Field 'created' already fixed to '{value}' - skipping")

    # Detect regressions
    regressions = memory.detect_regressions(new_yaml_data)
    if regressions:
        logger.error(f"Regressions detected: {regressions}")
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from loguru import logger


@dataclass
class FieldFix:
    """Record of a single field being fixed."""

    field_path: str  # e.g., "metadata.created" or "related[0]"
    value: Any  # The value that was set
    iteration: int  # Which iteration this was fixed in
    fix_description: str  # Human-readable description of the fix


@dataclass
class FixMemory:
    """Tracks fields modified across iterations to prevent re-fixing.

    This class maintains a record of all fields that have been successfully fixed
    during the review workflow. It provides methods to:
    - Mark fields as fixed
    - Check if a field has been fixed
    - Detect regressions (when a fixed field is changed again)
    - Generate context for the fixer agent

    Attributes:
        fixed_fields: Set of field paths that have been fixed
        field_history: Detailed history of each field fix
        iteration_fixes: Mapping from iteration number to list of field paths fixed
    """

    fixed_fields: set[str] = field(default_factory=set)
    field_history: dict[str, FieldFix] = field(default_factory=dict)
    iteration_fixes: dict[int, list[str]] = field(default_factory=dict)

    def mark_fixed(
        self, field_path: str, value: Any, iteration: int, description: str = ""
    ) -> None:
        """Record that a field was fixed.

        Args:
            field_path: YAML field key (e.g., "created", "updated") or
                       nested path with dots (e.g., "parent.child")
            value: The value that was set
            iteration: Which iteration this fix was made in
            description: Human-readable description of what was fixed
        """
        self.fixed_fields.add(field_path)
        self.field_history[field_path] = FieldFix(
            field_path=field_path,
            value=value,
            iteration=iteration,
            fix_description=description,
        )

        if iteration not in self.iteration_fixes:
            self.iteration_fixes[iteration] = []
        self.iteration_fixes[iteration].append(field_path)

        logger.debug(
            f"FixMemory: Marked '{field_path}' as fixed in iteration {iteration} "
            f"(value: {value!r})"
        )

    def is_fixed(self, field_path: str) -> bool:
        """Check if field was already fixed.

        Args:
            field_path: Dot-notation path to the field

        Returns:
            True if this field was fixed in a previous iteration
        """
        return field_path in self.fixed_fields

    def get_fixed_value(self, field_path: str) -> Any | None:
        """Get the value that was set when fixing this field.

        Args:
            field_path: Dot-notation path to the field

        Returns:
            The value that was set, or None if field wasn't fixed
        """
        if field_path in self.field_history:
            return self.field_history[field_path].value
        return None

    def get_fixed_iteration(self, field_path: str) -> int | None:
        """Get the iteration number when this field was fixed.

        Args:
            field_path: Dot-notation path to the field

        Returns:
            The iteration number, or None if field wasn't fixed
        """
        if field_path in self.field_history:
            return self.field_history[field_path].iteration
        return None

    def detect_regressions(
        self, current_yaml: dict[str, Any], current_iteration: int
    ) -> list[str]:
        """Detect if any previously-fixed fields have been changed.

        This is a critical check to prevent oscillation. If a field that was
        fixed in a previous iteration has been modified again, this is a
        regression that should be flagged.

        Args:
            current_yaml: Current YAML frontmatter as a dict
            current_iteration: The current iteration number

        Returns:
            List of regression messages (empty if no regressions)
        """
        regressions = []

        for field_path, field_fix in self.field_history.items():
            # Skip if this field was fixed in the current iteration
            # (that's not a regression, it's the current fix)
            if field_fix.iteration == current_iteration:
                continue

            # Get the current value of this field
            current_value = self._get_field_value(current_yaml, field_path)

            # Compare with the fixed value
            if current_value != field_fix.value:
                regressions.append(
                    f"Field '{field_path}' was fixed to '{field_fix.value}' in "
                    f"iteration {field_fix.iteration}, but is now '{current_value}' "
                    f"(regression detected in iteration {current_iteration})"
                )

        if regressions:
            logger.warning(
                f"FixMemory: Detected {len(regressions)} regression(s) in iteration {current_iteration}"
            )

        return regressions

    def _get_field_value(self, yaml_data: dict[str, Any], field_path: str) -> Any:
        """Get value from YAML using dot notation.

        Args:
            yaml_data: YAML frontmatter as a dict
            field_path: Dot-notation path (e.g., "metadata.created")

        Returns:
            The value at that path, or None if not found
        """
        parts = field_path.split(".")
        current = yaml_data

        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        return current

    def get_context_for_fixer(self, current_iteration: int) -> str:
        """Generate context string to include in fixer agent prompt.

        This provides the fixer agent with information about what fields
        have already been fixed, so it knows not to modify them again.

        Args:
            current_iteration: The current iteration number

        Returns:
            Formatted string to include in fixer prompt
        """
        if not self.fixed_fields:
            return "No fields have been fixed yet in this session."

        lines = [
            "PREVIOUSLY FIXED FIELDS (DO NOT MODIFY THESE):",
            "",
            "The following fields were already corrected in previous iterations.",
            "You MUST NOT modify these fields again, as doing so causes oscillation.",
            "",
        ]

        # Group by iteration
        for iteration in sorted(self.iteration_fixes.keys()):
            if iteration >= current_iteration:
                continue  # Don't include current iteration

            field_paths = self.iteration_fixes[iteration]
            lines.append(f"Iteration {iteration}:")

            for field_path in field_paths:
                field_fix = self.field_history[field_path]
                lines.append(
                    f"  - {field_path} = {field_fix.value!r}"
                    + (f" ({field_fix.fix_description})" if field_fix.fix_description else "")
                )

            lines.append("")

        lines.extend(
            [
                "IMPORTANT RULES:",
                "1. If an issue mentions a field from the list above, DO NOT fix it",
                "2. If you need to fix a related issue, find an alternative approach",
                "3. Explain in your reasoning why you're skipping already-fixed fields",
                "",
            ]
        )

        return "\n".join(lines)

    def extract_fixes_from_description(
        self, fix_descriptions: list[str], yaml_before: dict[str, Any], yaml_after: dict[str, Any], iteration: int
    ) -> None:
        """Automatically extract fixed fields by comparing YAML before and after.

        This method compares the YAML frontmatter before and after fixes were applied,
        identifies which fields changed, and marks them as fixed in memory.

        Args:
            fix_descriptions: List of human-readable fix descriptions
            yaml_before: YAML frontmatter before fixes
            yaml_after: YAML frontmatter after fixes
            iteration: Current iteration number
        """
        # Common metadata fields to track
        metadata_fields = [
            "created",
            "updated",
            "title",
            "aliases",
            "topic",
            "subtopics",
            "difficulty",
            "status",
            "moc",
            "related",
            "tags",
            "question_kind",
            "original_language",
            "language_tags",
        ]

        for field in metadata_fields:
            before_val = yaml_before.get(field)
            after_val = yaml_after.get(field)

            if before_val != after_val:
                # Field was modified - mark as fixed
                # FIX: Use direct field name, not "metadata." prefix
                # YAML frontmatter has fields at root level, not under 'metadata' key
                description = self._infer_fix_description(field, fix_descriptions)
                self.mark_fixed(
                    field,  # Direct field name matches YAML structure
                    after_val,
                    iteration,
                    description,
                )

    def _infer_fix_description(self, field: str, fix_descriptions: list[str]) -> str:
        """Infer which fix description applies to a field.

        Args:
            field: Field name (e.g., "created")
            fix_descriptions: List of fix descriptions from the fixer

        Returns:
            Best matching description, or generic message
        """
        # Look for fix descriptions mentioning this field
        field_lower = field.lower()
        for desc in fix_descriptions:
            if field_lower in desc.lower():
                return desc

        return f"Modified {field} field"

    def clear(self) -> None:
        """Clear all fix memory (use when starting a new note)."""
        self.fixed_fields.clear()
        self.field_history.clear()
        self.iteration_fixes.clear()

    def get_summary(self) -> str:
        """Get a summary of what's been fixed.

        Returns:
            Human-readable summary string
        """
        if not self.fixed_fields:
            return "No fields fixed yet"

        total_fixes = len(self.fixed_fields)
        iterations = len(self.iteration_fixes)

        return (
            f"FixMemory: {total_fixes} field(s) fixed across {iterations} iteration(s). "
            f"Fields: {', '.join(sorted(self.fixed_fields))}"
        )
