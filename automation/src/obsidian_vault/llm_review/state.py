"""State models for the LLM review workflow."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Annotated, Any, Literal, Mapping, TypedDict, cast


def _append_history(
    existing: list[dict[str, Any]], new_entries: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Aggregator that appends new history entries."""

    return [*existing, *new_entries]

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


class NoteReviewStateDict(TypedDict, total=False):
    """Typed dictionary representation used by LangGraph."""

    note_path: str
    original_text: str
    current_text: str
    issues: list[ReviewIssue]
    iteration: int
    changed: bool
    max_iterations: int
    completed: bool
    error: str | None
    history: Annotated[list[dict[str, Any]], _append_history]
    decision: str | None
    qa_verification_passed: bool | None
    qa_verification_summary: str | None
    qa_failure_summary: str | None
    requires_human_review: bool
    issue_history: list[set[str]]  # Track issue signatures per iteration for oscillation detection


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
    max_iterations: int = 10
    completed: bool = False
    error: str | None = None
    requires_human_review: bool = False

    # QA verification tracking
    qa_verification_passed: bool | None = None
    qa_verification_summary: str | None = None
    qa_failure_summary: str | None = None

    # History tracking (optional, for debugging/reporting)
    history: list[dict[str, Any]] = field(default_factory=list)
    decision: str | None = None

    # Oscillation detection (track issue signatures per iteration)
    issue_history: list[set[str]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "NoteReviewState":
        """Create state from a mapping, copying mutable fields."""

        issues = [
            issue
            if isinstance(issue, ReviewIssue)
            else ReviewIssue(
                severity=issue["severity"],
                message=issue["message"],
                field=issue.get("field"),
                line=issue.get("line"),
            )
            for issue in data.get("issues", [])
        ]

        history = [dict(entry) for entry in data.get("history", [])]
        issue_history = [set(entry) for entry in data.get("issue_history", [])]

        return cls(
            note_path=cast(str, data["note_path"]),
            original_text=cast(str, data["original_text"]),
            current_text=cast(str, data.get("current_text", data["original_text"])),
            issues=issues,
            iteration=cast(int, data.get("iteration", 0)),
            changed=cast(bool, data.get("changed", False)),
            max_iterations=cast(int, data.get("max_iterations", 5)),
            completed=cast(bool, data.get("completed", False)),
            error=data.get("error"),
            requires_human_review=cast(bool, data.get("requires_human_review", False)),
            qa_verification_passed=data.get("qa_verification_passed"),
            qa_verification_summary=data.get("qa_verification_summary"),
            qa_failure_summary=data.get("qa_failure_summary"),
            history=history,
            decision=data.get("decision"),
            issue_history=issue_history,
        )

    def to_dict(self) -> NoteReviewStateDict:
        """Convert state to a typed dictionary for LangGraph."""

        return {
            "note_path": self.note_path,
            "original_text": self.original_text,
            "current_text": self.current_text,
            "issues": list(self.issues),
            "iteration": self.iteration,
            "changed": self.changed,
            "max_iterations": self.max_iterations,
            "completed": self.completed,
            "error": self.error,
            "requires_human_review": self.requires_human_review,
            "qa_verification_passed": self.qa_verification_passed,
            "qa_verification_summary": self.qa_verification_summary,
            "qa_failure_summary": self.qa_failure_summary,
            "history": [dict(entry) for entry in self.history],
            "decision": self.decision,
            "issue_history": [list(entry) for entry in self.issue_history],
        }

    def add_history_entry(self, node: str, message: str, **kwargs) -> dict[str, Any]:
        """Add an entry to the history log and return it."""
        entry = {
            "iteration": self.iteration,
            "node": node,
            "message": message,
            **kwargs,
        }
        self.history.append(entry)
        return entry

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

    def record_current_issues(self) -> None:
        """Record the current issues as a signature for oscillation detection."""
        # Create a signature from current issues (severity + message)
        current_signatures = {
            f"{issue.severity}:{issue.message}" for issue in self.issues
        }
        self.issue_history.append(current_signatures)

    def detect_oscillation(self) -> tuple[bool, str | None]:
        """Detect if the same issues are reappearing across iterations.

        Detection strategies:
        1. Immediate reversal (N-1): Same issue fixed then reappears
        2. Cycle detection (N-2, N-3): Issues repeat in a pattern
        3. No progress: Issue count not decreasing

        Returns:
            (is_oscillating, explanation) tuple
        """
        # STRATEGY 1: Immediate reversal detection
        # Check if issue from previous iteration reappeared
        if len(self.issue_history) >= 2:
            current_issues = self.issue_history[-1]
            previous_issues = self.issue_history[-2]

            # Check for exact match (issue disappeared and came back)
            # This shouldn't happen if fixes are working
            reverted_issues = current_issues & previous_issues

            if len(reverted_issues) > 0 and len(reverted_issues) == len(current_issues):
                # ALL current issues are from previous iteration = oscillation
                explanation = (
                    f"Oscillation detected: All {len(reverted_issues)} issue(s) from "
                    f"iteration {self.iteration - 1} reappeared in iteration {self.iteration}. "
                    f"Fixer likely reversed its own changes. "
                    f"Issues: {list(reverted_issues)[:3]}"
                )
                return True, explanation

        # STRATEGY 2: Original cycle detection (existing logic)
        if len(self.issue_history) < 3:
            return False, None

        current_issues = self.issue_history[-1]

        # Check against issues 2-3 iterations ago
        for i in range(2, min(4, len(self.issue_history))):
            if i >= len(self.issue_history):
                break

            previous_issues = self.issue_history[-i]
            common_issues = current_issues & previous_issues

            if len(common_issues) > 0:
                oscillation_rate = len(common_issues) / len(current_issues) if current_issues else 0

                if oscillation_rate > 0.5:  # More than 50% of issues are repeating
                    explanation = (
                        f"Oscillation detected: {len(common_issues)} issue(s) from "
                        f"iteration {self.iteration - i + 1} reappeared in iteration {self.iteration}. "
                        f"This suggests conflicting validators or unstable fixes. "
                        f"Repeating issues: {list(common_issues)[:3]}"
                    )
                    return True, explanation

        # STRATEGY 3: No-progress detection
        if len(self.issue_history) >= 3:
            last_3_counts = [len(issues) for issues in self.issue_history[-3:]]

            # If issue count hasn't decreased in last 3 iterations
            if last_3_counts[0] <= last_3_counts[1] <= last_3_counts[2]:
                # AND they're all the same count
                if last_3_counts[0] == last_3_counts[2]:
                    explanation = (
                        f"Oscillation detected: Issue count stuck at {last_3_counts[0]} "
                        f"for 3 consecutive iterations. No progress being made."
                    )
                    return True, explanation

        return False, None
