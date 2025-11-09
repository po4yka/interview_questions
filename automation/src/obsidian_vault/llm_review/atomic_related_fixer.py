"""Atomic Related Field Fixes - Prevent oscillation in related field.

PHASE 3 FIX: This module ensures that related field fixes are atomic and
don't oscillate between adding and removing links.

Problem Example:
- Iteration 1: Adds links to reach minimum (2) → [c-kotlin, c-flow, c-coroutines]
- Iteration 2: Removes links to stay under maximum (5) → [c-kotlin, c-flow]
- This causes oscillation!

Solution:
- Target the MIDDLE of the range (3-4 items) instead of edges
- Never add AND remove in the same iteration
- Use Fix Memory to track related field state
- Prioritize concept links (c-*) over question links (q-*)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from loguru import logger


@dataclass
class RelatedFieldAnalysis:
    """Analysis of current related field state."""

    current_count: int
    needs_more: bool
    needs_fewer: bool
    optimal_count: int  # Target count (3-4)
    action: Literal["add", "remove", "none"]
    how_many: int  # How many to add or remove


class AtomicRelatedFixer:
    """Ensures related field fixes are atomic and don't oscillate.

    This class provides strict rules for fixing the related field to
    prevent the add-then-remove oscillation pattern.
    """

    # Constraints from vault rules
    MIN_RELATED = 2
    MAX_RELATED = 5
    OPTIMAL_MIN = 3  # Target lower bound
    OPTIMAL_MAX = 4  # Target upper bound

    def analyze_related_field(self, related_items: list[str]) -> RelatedFieldAnalysis:
        """Analyze current related field and determine what action to take.

        Args:
            related_items: Current list of related items

        Returns:
            RelatedFieldAnalysis with recommended action
        """
        current_count = len(related_items)

        # Determine if we need changes
        needs_more = current_count < self.MIN_RELATED
        needs_fewer = current_count > self.MAX_RELATED

        # Determine optimal target
        if current_count < self.OPTIMAL_MIN:
            # Too few - add to reach optimal minimum
            optimal_count = self.OPTIMAL_MIN
            action = "add"
            how_many = self.OPTIMAL_MIN - current_count
        elif current_count > self.OPTIMAL_MAX:
            # Too many - remove to reach optimal maximum
            optimal_count = self.OPTIMAL_MAX
            action = "remove"
            how_many = current_count - self.OPTIMAL_MAX
        else:
            # Already in optimal range - no change needed
            optimal_count = current_count
            action = "none"
            how_many = 0

        return RelatedFieldAnalysis(
            current_count=current_count,
            needs_more=needs_more,
            needs_fewer=needs_fewer,
            optimal_count=optimal_count,
            action=action,
            how_many=how_many,
        )

    def prioritize_items(
        self, items: list[str], keep_concepts: bool = True
    ) -> list[str]:
        """Prioritize related items (concepts before questions).

        Args:
            items: List of related items
            keep_concepts: If True, prioritize concept files (c-*)

        Returns:
            Sorted list with concepts first, then questions
        """
        concepts = [item for item in items if item.startswith("c-")]
        questions = [item for item in items if item.startswith("q-")]
        mocs = [item for item in items if item.startswith("moc-")]
        other = [item for item in items if not any(item.startswith(p) for p in ["c-", "q-", "moc-"])]

        if keep_concepts:
            # Concepts first (most valuable), then MOCs, then questions
            return concepts + mocs + questions + other
        else:
            # Questions first (when removing, keep concepts)
            return questions + other + mocs + concepts

    def suggest_items_to_add(
        self,
        current_items: list[str],
        available_concepts: list[str],
        available_questions: list[str],
        how_many: int,
    ) -> list[str]:
        """Suggest items to add to related field.

        Prioritizes concept links over question links.

        Args:
            current_items: Current related items
            available_concepts: Available concept files
            available_questions: Available question files
            how_many: How many items to add

        Returns:
            List of items to add (up to how_many)
        """
        suggestions = []
        current_set = set(current_items)

        # First, try to add concepts (more valuable)
        for concept in available_concepts:
            if concept not in current_set and len(suggestions) < how_many:
                suggestions.append(concept)

        # If still need more, add questions
        if len(suggestions) < how_many:
            for question in available_questions:
                if question not in current_set and len(suggestions) < how_many:
                    suggestions.append(question)

        return suggestions

    def suggest_items_to_remove(
        self, current_items: list[str], how_many: int
    ) -> list[str]:
        """Suggest items to remove from related field.

        Prioritizes removing question links over concept links.

        Args:
            current_items: Current related items
            how_many: How many items to remove

        Returns:
            List of items to remove (up to how_many)
        """
        # Prioritize removing questions, keep concepts
        prioritized = self.prioritize_items(current_items, keep_concepts=False)

        # Take the first 'how_many' items (lowest priority)
        to_remove = prioritized[:how_many]

        return to_remove

    def format_rules_for_prompt(self) -> str:
        """Format related field rules for inclusion in fixer agent prompt.

        Returns:
            Formatted string with strict related field rules
        """
        return f"""
ATOMIC RELATED FIELD FIXING RULES (PHASE 3 FIX - FOLLOW EXACTLY):

1. TARGET THE MIDDLE OF THE RANGE:
   - Minimum allowed: {self.MIN_RELATED} items
   - Maximum allowed: {self.MAX_RELATED} items
   - OPTIMAL TARGET: {self.OPTIMAL_MIN}-{self.OPTIMAL_MAX} items ← AIM FOR THIS

2. NEVER ADD AND REMOVE IN SAME ITERATION:
   - If current count < {self.OPTIMAL_MIN}: ADD exactly enough to reach {self.OPTIMAL_MIN}
   - If current count > {self.OPTIMAL_MAX}: REMOVE exactly enough to reach {self.OPTIMAL_MAX}
   - If current count is {self.OPTIMAL_MIN}-{self.OPTIMAL_MAX}: DO NOT CHANGE

3. PRIORITIZE CONCEPT LINKS (c-*) OVER QUESTION LINKS (q-*):
   - When adding: Add concepts first, then questions
   - When removing: Remove questions first, keep concepts

4. EXAMPLES:

   CORRECT:
   - Current: [c-kotlin]                  → Add 2 concepts → [c-kotlin, c-flow, c-coroutines]
   - Current: [c-a, c-b, c-c, c-d]        → Already optimal → NO CHANGE
   - Current: [c-a, q-b, q-c, q-d, q-e, q-f] → Remove 2 questions → [c-a, q-b, q-c, q-d]

   INCORRECT:
   - Current: [c-kotlin, c-flow]          → Add 3, then remove 2 → OSCILLATION!
   - Current: [c-a, c-b, c-c, c-d, c-e]   → Remove to {self.MIN_RELATED} → TOO AGGRESSIVE!
   - Current: [c-a, c-b, c-c]             → Add to {self.MAX_RELATED} → TOO AGGRESSIVE!

5. IF FIX MEMORY SAYS FIELD WAS ALREADY FIXED:
   - DO NOT modify related field again
   - Explain that it was already fixed in previous iteration

6. VALIDATION:
   - After fixing, count should be {self.OPTIMAL_MIN}-{self.OPTIMAL_MAX}
   - Never go below {self.MIN_RELATED} or above {self.MAX_RELATED}
   - All items must be valid file references
""".strip()

    def validate_fix(
        self, items_before: list[str], items_after: list[str]
    ) -> tuple[bool, str]:
        """Validate that a related field fix is atomic and correct.

        Args:
            items_before: Related items before fix
            items_after: Related items after fix

        Returns:
            Tuple of (is_valid, explanation)
        """
        before_count = len(items_before)
        after_count = len(items_after)

        # Check if count is in valid range
        if after_count < self.MIN_RELATED:
            return (
                False,
                f"After fix, count is {after_count} which is below minimum {self.MIN_RELATED}",
            )

        if after_count > self.MAX_RELATED:
            return (
                False,
                f"After fix, count is {after_count} which exceeds maximum {self.MAX_RELATED}",
            )

        # Check if fix was atomic (didn't both add and remove)
        added = set(items_after) - set(items_before)
        removed = set(items_before) - set(items_after)

        if len(added) > 0 and len(removed) > 0:
            return (
                False,
                f"Non-atomic fix: Added {len(added)} items AND removed {len(removed)} items. "
                f"Should only add OR remove, not both!",
            )

        # Check if optimal target was reached
        if after_count < self.OPTIMAL_MIN or after_count > self.OPTIMAL_MAX:
            # Not necessarily invalid, but not optimal
            logger.warning(
                f"Related field count {after_count} is outside optimal range "
                f"{self.OPTIMAL_MIN}-{self.OPTIMAL_MAX}"
            )

        return (True, f"Valid fix: count changed from {before_count} to {after_count}")

    def get_fix_description(
        self, items_before: list[str], items_after: list[str]
    ) -> str:
        """Get a human-readable description of a related field fix.

        Args:
            items_before: Related items before fix
            items_after: Related items after fix

        Returns:
            Description for logging/history
        """
        added = set(items_after) - set(items_before)
        removed = set(items_before) - set(items_after)

        if len(added) > 0:
            return f"Added {len(added)} related item(s) to reach optimal count: {', '.join(added)}"
        elif len(removed) > 0:
            return f"Removed {len(removed)} related item(s) to reach optimal count: {', '.join(removed)}"
        else:
            return "Related field already at optimal count - no changes"
