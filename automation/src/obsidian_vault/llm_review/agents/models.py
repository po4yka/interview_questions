"""Pydantic models for agent results."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator


class TechnicalReviewResult(BaseModel):
    """Result of technical/factual review."""

    has_issues: bool = Field(description="Whether technical issues were found")
    issues_found: list[str] = Field(
        default_factory=list, description="List of technical issues identified"
    )
    revised_text: str = Field(description="Revised note text (may be same as input if no changes)")
    changes_made: bool = Field(description="Whether any changes were made to the text")
    explanation: str = Field(description="Explanation of what was reviewed and changed")


class IssueFixResult(BaseModel):
    """Result of fixing formatting/structure issues."""

    revised_text: str = Field(description="Note text with issues fixed")
    fixes_applied: list[str] = Field(
        default_factory=list, description="List of fixes that were applied"
    )
    changes_made: bool = Field(description="Whether any changes were made")


class MetadataSanityResult(BaseModel):
    """Result of metadata/frontmatter sanity check."""

    has_issues: bool = Field(description="Whether metadata issues were found")
    issues_found: list[str] = Field(
        default_factory=list,
        description="List of metadata sanity issues (topic consistency, timestamp freshness, bilingual ordering)",
    )
    warnings: list[str] = Field(
        default_factory=list, description="Non-critical warnings about metadata"
    )
    suggestions: list[str] = Field(
        default_factory=list, description="Suggestions for improvement"
    )


class QAVerificationResult(BaseModel):
    """Result of final QA/critic verification before marking as complete."""

    is_acceptable: bool = Field(
        description="Whether the note is acceptable to mark as complete (no critical issues)"
    )
    factual_errors: list[str] = Field(
        default_factory=list,
        description="Any factual or technical errors found in the final content",
    )
    bilingual_parity_issues: list[str] = Field(
        default_factory=list,
        description="Issues where EN and RU content are not semantically equivalent",
    )
    quality_concerns: list[str] = Field(
        default_factory=list,
        description="Non-critical quality concerns or improvements suggested",
    )
    summary: str = Field(
        description="Brief summary of the verification result and overall note quality"
    )

    @model_validator(mode="before")
    @classmethod
    def _coerce_optional_lists(cls, values: Any) -> Any:
        """Ensure optional list fields default to empty lists when None."""

        if isinstance(values, dict):
            for key in ("factual_errors", "bilingual_parity_issues", "quality_concerns"):
                if values.get(key) is None:
                    values[key] = []
        return values


class BilingualParityResult(BaseModel):
    """Result of bilingual parity check between EN and RU sections."""

    has_parity_issues: bool = Field(
        description="Whether parity issues were found between EN and RU content"
    )
    parity_issues: list[str] = Field(
        default_factory=list,
        description="List of semantic mismatches or missing translations between EN and RU",
    )
    missing_sections: list[str] = Field(
        default_factory=list,
        description="Sections that exist in one language but not the other",
    )
    summary: str = Field(
        description="Brief summary of the parity check result"
    )


class ConceptEnrichmentResult(BaseModel):
    """Result of enriching an auto-generated concept stub with meaningful content."""

    enriched_content: str = Field(
        description="The enriched concept note with meaningful definitions, examples, and references"
    )
    added_sections: list[str] = Field(
        default_factory=list,
        description="List of sections that were added or significantly enriched",
    )
    key_concepts: list[str] = Field(
        default_factory=list,
        description="Key technical concepts covered in the enriched content",
    )
    related_concepts: list[str] = Field(
        default_factory=list,
        description="Suggested related concept files (without c- prefix or .md extension)",
    )
    explanation: str = Field(
        description="Brief explanation of what was enriched and the knowledge sources used"
    )


class IssueGroup(BaseModel):
    """A group of related issues that should be fixed together."""

    group_type: str = Field(
        description="Type of issues in this group (e.g., 'backticks', 'timestamps', 'parity', 'yaml_format')"
    )
    issues: list[str] = Field(
        description="List of issue messages in this group"
    )
    priority: int = Field(
        description="Priority level (1=highest, 5=lowest) based on severity and dependencies"
    )
    recommended_fixer: str = Field(
        description="Which fixer should handle this group: 'deterministic' or 'llm'"
    )
    dependencies: list[str] = Field(
        default_factory=list,
        description="Group types that should be fixed before this one (e.g., ['yaml_format'] must be fixed before ['links'])"
    )
    rationale: str = Field(
        description="Explanation of why these issues are grouped and prioritized this way"
    )


class FixPlanResult(BaseModel):
    """Result of coordinating and planning the fix strategy."""

    issue_groups: list[IssueGroup] = Field(
        description="Prioritized groups of related issues with fix strategy"
    )
    fix_order: list[str] = Field(
        description="Recommended order to process groups (by group_type)"
    )
    estimated_iterations: int = Field(
        description="Estimated number of iterations needed to resolve all issues"
    )
    high_risk_fixes: list[str] = Field(
        default_factory=list,
        description="Issues that are risky to fix automatically and might need human review"
    )
    explanation: str = Field(
        description="Overall fix strategy explanation"
    )

    @model_validator(mode="before")
    @classmethod
    def _coerce_optional_lists(cls, values: Any) -> Any:
        """Ensure optional list fields default to empty lists when None."""

        if isinstance(values, dict):
            if values.get("high_risk_fixes") is None:
                values["high_risk_fixes"] = []
        return values


class QAFailureSummaryResult(BaseModel):
    """Result of summarizing repeated QA failures for human follow-up."""

    failure_type: str = Field(
        description="Classification of failure: 'max_iterations_reached' | 'qa_verification_failed' | 'persistent_issues'"
    )
    unresolved_issues: list[str] = Field(
        default_factory=list,
        description="List of issues that could not be automatically resolved",
    )
    iteration_summary: str = Field(
        description="Summary of what happened across iterations (e.g., 'Fixed 8/12 issues, 4 remained unresolved')"
    )
    recommended_actions: list[str] = Field(
        default_factory=list,
        description="Specific actionable steps for manual review/fixing",
    )
    qa_failure_reasons: list[str] = Field(
        default_factory=list,
        description="Specific reasons why QA verification failed (factual errors, parity issues, etc.)",
    )
    human_readable_summary: str = Field(
        description="Concise 3-5 sentence summary for human reviewer explaining what went wrong and what needs attention"
    )

    @model_validator(mode="before")
    @classmethod
    def _coerce_optional_failure_lists(cls, values: Any) -> Any:
        """Ensure list fields are empty lists when the agent returns null."""

        if isinstance(values, dict):
            for key in ("unresolved_issues", "recommended_actions", "qa_failure_reasons"):
                if values.get(key) is None:
                    values[key] = []
        return values
