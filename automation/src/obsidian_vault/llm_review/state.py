"""State models for the LLM review workflow."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from obsidian_vault.validators.base import ValidationIssue


@dataclass
class ReviewIssue:
    """A single issue identified during review."""

    severity: Literal["CRITICAL", "ERROR", "WARNING", "INFO"]
    message: str
    field: str | None = None
    line: int | None = None

    @classmethod
    def from_validation_issue(cls, issue: ValidationIssue) -> ReviewIssue:
        """Convert a ValidationIssue to ReviewIssue."""
        return cls(
            severity=issue.severity.value,
            message=issue.message,
            field=issue.field,
            line=issue.line,
        )


@dataclass
class NoteReviewState:
    """State for a single note review workflow.

    This state is passed through LangGraph nodes and tracks the full
    lifecycle of reviewing and fixing a single note.
    """

    # Input fields (set at initialization)
    note_path: str
    original_text: str

    # Working state (modified during workflow)
    current_text: str
    issues: list[ReviewIssue] = field(default_factory=list)
    iteration: int = 0

    # Flags and metadata
    changed: bool = False
    max_iterations: int = 5
    completed: bool = False
    error: str | None = None

    # History tracking (optional, for debugging/reporting)
    history: list[dict] = field(default_factory=list)

    def add_history_entry(self, node: str, message: str, **kwargs) -> None:
        """Add an entry to the history log."""
        entry = {
            "iteration": self.iteration,
            "node": node,
            "message": message,
            **kwargs,
        }
        self.history.append(entry)

    def has_critical_issues(self) -> bool:
        """Check if there are any critical issues."""
        return any(issue.severity == "CRITICAL" for issue in self.issues)

    def has_any_issues(self) -> bool:
        """Check if there are any issues at all."""
        return len(self.issues) > 0

    def should_continue(self) -> bool:
        """Determine if iteration should continue."""
        return (
            self.has_any_issues()
            and self.iteration < self.max_iterations
            and not self.completed
            and self.error is None
        )
