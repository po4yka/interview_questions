"""Strict Timestamp Policy for YAML frontmatter.

PHASE 2 FIX: This module implements strict timestamp handling rules to prevent
timestamp thrashing (where timestamps are "fixed" multiple times across iterations).

Key Principles:
1. Valid timestamps are NEVER modified
2. Created date is immutable once set
3. Updated date only changes when content actually changes
4. Git history is used for accurate timestamp reconstruction

Example Issues Prevented:
- Iteration 1: "Updated timestamps from future dates to realistic past dates (2024-10-12)"
- Iteration 2: "Updated 'updated' timestamp to a current valid date (2025-11-09)"  ← BAD!

With this policy:
- Iteration 1: Sets valid timestamps based on git history or current date
- Iteration 2+: Skips timestamp "fixes" because they're already valid
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime, date
from pathlib import Path
from typing import Literal

from loguru import logger


@dataclass
class TimestampValidationResult:
    """Result of validating timestamps in a note."""

    is_valid: bool
    created_valid: bool
    updated_valid: bool
    issues: list[str]
    suggestions: list[str]


class TimestampPolicy:
    """Strict timestamp policy enforcer.

    This class provides methods to:
    - Validate timestamps according to strict rules
    - Suggest corrections ONLY when timestamps are actually invalid
    - Use git history for accurate timestamp determination
    - Prevent re-fixing of already-valid timestamps
    """

    DATE_FORMAT = "%Y-%m-%d"

    def __init__(self, vault_root: Path):
        """Initialize timestamp policy.

        Args:
            vault_root: Path to the vault root directory
        """
        self.vault_root = vault_root

    def validate(
        self,
        yaml_data: dict,
        note_path: str | Path,
        current_date: date | None = None,
    ) -> TimestampValidationResult:
        """Validate timestamps according to strict policy.

        RULES:
        1. 'created' and 'updated' fields must be present
        2. Dates must be in YYYY-MM-DD format
        3. Dates must not be in the future
        4. 'created' must be <= 'updated'
        5. VALID timestamps are NEVER flagged for fixing

        Args:
            yaml_data: YAML frontmatter as dict
            note_path: Path to the note (for git history lookup)
            current_date: Current date (defaults to today)

        Returns:
            TimestampValidationResult with validation status
        """
        if current_date is None:
            current_date = datetime.now().date()

        issues = []
        suggestions = []
        created_valid = True
        updated_valid = True

        # Check for presence
        if "created" not in yaml_data:
            issues.append("Missing 'created' timestamp field")
            created_valid = False

        if "updated" not in yaml_data:
            issues.append("Missing 'updated' timestamp field")
            updated_valid = False

        # Validate 'created' field
        if "created" in yaml_data:
            created_str = yaml_data["created"]
            try:
                created = datetime.strptime(str(created_str), self.DATE_FORMAT).date()

                if created > current_date:
                    issues.append(
                        f"'created' date {created} is in the future (today is {current_date})"
                    )
                    created_valid = False
            except (ValueError, TypeError):
                issues.append(
                    f"Invalid 'created' date format: {created_str!r} (expected YYYY-MM-DD)"
                )
                created_valid = False

        # Validate 'updated' field
        if "updated" in yaml_data:
            updated_str = yaml_data["updated"]
            try:
                updated = datetime.strptime(str(updated_str), self.DATE_FORMAT).date()

                if updated > current_date:
                    issues.append(
                        f"'updated' date {updated} is in the future (today is {current_date})"
                    )
                    updated_valid = False
            except (ValueError, TypeError):
                issues.append(
                    f"Invalid 'updated' date format: {updated_str!r} (expected YYYY-MM-DD)"
                )
                updated_valid = False

        # Cross-field validation
        if "created" in yaml_data and "updated" in yaml_data:
            try:
                created = datetime.strptime(str(yaml_data["created"]), self.DATE_FORMAT).date()
                updated = datetime.strptime(str(yaml_data["updated"]), self.DATE_FORMAT).date()

                if created > updated:
                    issues.append(
                        f"'created' ({created}) is after 'updated' ({updated}) - "
                        f"this violates temporal logic and must be corrected"
                    )
                    # Mark both as invalid since we can't determine which is wrong
                    created_valid = False
                    updated_valid = False
            except (ValueError, TypeError):
                pass  # Already caught above

        is_valid = created_valid and updated_valid and len(issues) == 0

        return TimestampValidationResult(
            is_valid=is_valid,
            created_valid=created_valid,
            updated_valid=updated_valid,
            issues=issues,
            suggestions=suggestions,
        )

    def get_git_created_date(self, note_path: Path) -> date | None:
        """Get the creation date from git history.

        Args:
            note_path: Absolute path to the note file

        Returns:
            Date of first commit for this file, or None if not in git
        """
        try:
            # Get first commit date for this file
            result = subprocess.run(
                ["git", "log", "--follow", "--format=%aI", "--reverse", "--", str(note_path)],
                cwd=note_path.parent,
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0 and result.stdout.strip():
                # Get first line (earliest commit)
                first_commit_iso = result.stdout.strip().split("\n")[0]
                # Parse ISO date (YYYY-MM-DDTHH:MM:SS...)
                created_date = datetime.fromisoformat(first_commit_iso).date()
                logger.debug(f"Git created date for {note_path.name}: {created_date}")
                return created_date
        except Exception as e:
            logger.debug(f"Could not get git created date for {note_path.name}: {e}")

        return None

    def get_git_updated_date(self, note_path: Path) -> date | None:
        """Get the last modification date from git history.

        Args:
            note_path: Absolute path to the note file

        Returns:
            Date of last commit for this file, or None if not in git
        """
        try:
            # Get last commit date for this file
            result = subprocess.run(
                ["git", "log", "-1", "--format=%aI", "--", str(note_path)],
                cwd=note_path.parent,
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0 and result.stdout.strip():
                last_commit_iso = result.stdout.strip()
                updated_date = datetime.fromisoformat(last_commit_iso).date()
                logger.debug(f"Git updated date for {note_path.name}: {updated_date}")
                return updated_date
        except Exception as e:
            logger.debug(f"Could not get git updated date for {note_path.name}: {e}")

        return None

    def suggest_fix(
        self,
        yaml_data: dict,
        note_path: Path,
        current_date: date | None = None,
    ) -> dict[str, str]:
        """Suggest timestamp corrections ONLY if timestamps are invalid.

        IMPORTANT: This method returns an empty dict if timestamps are already valid.
        This prevents unnecessary "fixes" that cause oscillation.

        Args:
            yaml_data: Current YAML frontmatter
            note_path: Path to the note file
            current_date: Current date (defaults to today)

        Returns:
            Dict with 'created' and/or 'updated' keys ONLY if they need fixing
        """
        if current_date is None:
            current_date = datetime.now().date()

        validation = self.validate(yaml_data, note_path, current_date)

        # CRITICAL: If timestamps are valid, return empty dict
        if validation.is_valid:
            logger.debug(f"Timestamps for {note_path.name} are valid - no fixes needed")
            return {}

        fixes = {}

        # Fix 'created' only if invalid
        if not validation.created_valid:
            # Try git history first
            git_created = self.get_git_created_date(note_path)
            if git_created:
                fixes["created"] = git_created.strftime(self.DATE_FORMAT)
                logger.debug(f"Suggesting 'created' from git: {fixes['created']}")
            else:
                # Fallback to current date
                fixes["created"] = current_date.strftime(self.DATE_FORMAT)
                logger.debug(f"Suggesting 'created' as current date: {fixes['created']}")

        # Fix 'updated' only if invalid
        if not validation.updated_valid:
            # Try git history first
            git_updated = self.get_git_updated_date(note_path)
            if git_updated:
                fixes["updated"] = git_updated.strftime(self.DATE_FORMAT)
                logger.debug(f"Suggesting 'updated' from git: {fixes['updated']}")
            else:
                # Fallback to current date
                fixes["updated"] = current_date.strftime(self.DATE_FORMAT)
                logger.debug(f"Suggesting 'updated' as current date: {fixes['updated']}")

        return fixes

    def format_rule_for_prompt(self) -> str:
        """Format timestamp rules for inclusion in fixer agent prompt.

        Returns:
            Formatted string with strict timestamp rules
        """
        return """
STRICT TIMESTAMP POLICY (PHASE 2 FIX - FOLLOW EXACTLY):

1. IF timestamps are VALID (YYYY-MM-DD format, not in future), DO NOT MODIFY THEM
   - Even if they're "old" dates, valid timestamps are CORRECT
   - Changing valid timestamps causes oscillation

2. IF 'created' or 'updated' is MISSING:
   - Use git history if available
   - Fallback to current date: {current_date}

3. IF timestamp has INVALID format (not YYYY-MM-DD):
   - Fix format to YYYY-MM-DD
   - Preserve the date if possible

4. IF timestamp is in the FUTURE:
   - Replace with current date: {current_date}

5. IF 'created' is AFTER 'updated' (temporal logic violation):
   - This is CRITICAL ERROR - violates causality
   - Set 'updated' to current date (most recent change is now)
   - Keep 'created' unchanged (original creation date is authoritative)
   - Example: created: 2025-10-05, updated: 2025-01-25 → created: 2025-10-05, updated: 2025-11-09

6. NEVER "update" timestamps just because they're old
   - Old timestamps are often correct (file created in the past)
   - Only fix if actually INVALID

CRITICAL: If a field says "created: 2024-10-12", that's VALID. Don't change it!
""".strip()

    def get_fix_description(self, field: Literal["created", "updated"], old_value: str, new_value: str) -> str:
        """Get a human-readable description of a timestamp fix.

        Args:
            field: Which field was fixed ('created' or 'updated')
            old_value: Old timestamp value
            new_value: New timestamp value

        Returns:
            Description for logging/history
        """
        if old_value == "":
            return f"Set missing '{field}' timestamp to {new_value}"
        else:
            return f"Fixed invalid '{field}' timestamp from '{old_value}' to '{new_value}'"
