"""Validate system design question patterns and best practices."""

from __future__ import annotations

from .base import BaseValidator, Severity
from .config import OPTIONAL_VERSION_SUBSECTIONS, SYSTEM_DESIGN_SUBSECTIONS
from .registry import ValidatorRegistry


@ValidatorRegistry.register
class SystemDesignValidator(BaseValidator):
    """Validate system design question patterns and recommend best practices."""

    def validate(self):
        # Only run for system-design or hard android questions
        question_kind = self.frontmatter.get("question_kind")
        difficulty = self.frontmatter.get("difficulty")
        topic = self.frontmatter.get("topic")

        is_system_design = question_kind == "system-design" or (
            topic == "android" and difficulty == "hard" and question_kind == "android"
        )

        if not is_system_design:
            return self._summary

        self._check_has_versions_for_complex_questions()
        self._check_has_requirements_section()
        self._check_has_architecture_section()

        return self._summary

    def _check_has_versions_for_complex_questions(self) -> None:
        """Recommend Short/Detailed versions for complex system design questions."""
        content = self.content
        difficulty = self.frontmatter.get("difficulty")

        has_versions = (
            OPTIONAL_VERSION_SUBSECTIONS["short"]["en"] in content
            or OPTIONAL_VERSION_SUBSECTIONS["short"]["ru"] in content
        )

        if difficulty == "hard" and not has_versions:
            self.add_issue(
                Severity.INFO,
                "Consider adding '## Short Version' and '## Detailed Version' "
                "subsections for complex system design questions (provides flexibility for different interview depths)",
            )
        elif has_versions:
            self.add_passed("Question includes multiple complexity versions (Short/Detailed)")

    def _check_has_requirements_section(self) -> None:
        """Check for Requirements subsection in answer."""
        content = self.content

        has_ru_requirements = SYSTEM_DESIGN_SUBSECTIONS["requirements"]["ru"] in content
        has_en_requirements = SYSTEM_DESIGN_SUBSECTIONS["requirements"]["en"] in content

        if has_ru_requirements and has_en_requirements:
            self.add_passed("Answer includes Requirements sections")
        elif has_ru_requirements or has_en_requirements:
            self.add_issue(
                Severity.WARNING,
                "Requirements section present in one language but missing in the other",
            )
        else:
            self.add_issue(
                Severity.INFO,
                "System design answers should include '### Requirements' section "
                "(Functional/Non-functional requirements)",
            )

    def _check_has_architecture_section(self) -> None:
        """Check for Architecture subsection in answer."""
        content = self.content

        has_ru_architecture = SYSTEM_DESIGN_SUBSECTIONS["architecture"]["ru"] in content
        has_en_architecture = SYSTEM_DESIGN_SUBSECTIONS["architecture"]["en"] in content

        if has_ru_architecture and has_en_architecture:
            self.add_passed("Answer includes Architecture sections")
        elif has_ru_architecture or has_en_architecture:
            self.add_issue(
                Severity.WARNING,
                "Architecture section present in one language but missing in the other",
            )
        else:
            self.add_issue(
                Severity.INFO,
                "System design answers should include '### Architecture' section "
                "(High-level system design, components, data flow)",
            )
