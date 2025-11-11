"""Analytics helpers for the LangGraph review workflow.

This module centralizes collection of per-note and per-iteration metrics so the
system can reason about stability issues and long running behaviour.  The data
structures are intentionally lightweight – they only depend on the standard
library and are safe to import from any coroutine used by LangGraph.

Example usage (internal to :mod:`graph`::

    recorder = ReviewAnalyticsRecorder()
    recorder.start_note("InterviewQuestions/q-demo.md", profile="balanced")
    recorder.record_iteration(
        note_path="InterviewQuestions/q-demo.md",
        iteration=1,
        metadata_issues=2,
        structural_issues=1,
        parity_issues=0,
    )
    recorder.set_iteration_decision("InterviewQuestions/q-demo.md", 1, "continue")
    recorder.record_qa_attempt(
        note_path="InterviewQuestions/q-demo.md",
        iteration=1,
        passed=False,
        summary="Missing Russian translation",
    )
    recorder.finalize(
        note_path="InterviewQuestions/q-demo.md",
        final_issue_count=0,
        iterations=2,
        elapsed_seconds=42.0,
        qa_passed=True,
    )

The recorder keeps a per-note store of :class:`NoteAnalytics` objects and can
produce aggregated summaries once a batch has finished processing.  The graphs
can then expose this data so callers may visualise trends or ship metrics to a
monitoring stack.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from statistics import mean
from typing import Any


@dataclass
class IterationAnalytics:
    """Per-iteration snapshot captured after validators have run."""

    iteration: int
    metadata_issues: int
    structural_issues: int
    parity_issues: int
    total_issues: int
    decision: str | None = None


@dataclass
class QAAttemptAnalytics:
    """Metadata for each QA verification attempt."""

    iteration: int
    passed: bool | None
    summary: str | None = None


@dataclass
class NoteAnalytics:
    """Collected metrics for a single note run through the workflow."""

    note_path: str
    profile: str
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    elapsed_seconds: float | None = None
    iterations: int = 0
    final_issue_count: int = 0
    initial_issue_count: int | None = None
    qa_passed: bool | None = None
    error: str | None = None
    requires_human_review: bool = False
    iteration_stats: list[IterationAnalytics] = field(default_factory=list)
    qa_attempts: list[QAAttemptAnalytics] = field(default_factory=list)

    def record_iteration(self, stats: IterationAnalytics) -> None:
        """Append iteration analytics and track the first issue count."""
        if self.initial_issue_count is None:
            self.initial_issue_count = stats.total_issues
        self.iteration_stats.append(stats)

    def set_decision(self, iteration: int, decision: str) -> None:
        """Attach the decision that followed a specific iteration."""
        for stat in self.iteration_stats:
            if stat.iteration == iteration:
                stat.decision = decision
                break

    def add_qa_attempt(self, attempt: QAAttemptAnalytics) -> None:
        """Store a QA verification attempt."""
        self.qa_attempts.append(attempt)

    def finalize(
        self,
        *,
        iterations: int,
        final_issue_count: int,
        elapsed_seconds: float,
        qa_passed: bool | None,
        error: str | None,
        requires_human_review: bool,
    ) -> None:
        """Mark the note as complete and persist summary level data."""
        self.iterations = iterations
        self.final_issue_count = final_issue_count
        self.elapsed_seconds = elapsed_seconds
        self.qa_passed = qa_passed
        self.error = error
        self.requires_human_review = requires_human_review
        self.completed_at = datetime.utcnow()

    @property
    def issues_resolved(self) -> int | None:
        """Return the number of issues resolved during the run."""
        if self.initial_issue_count is None:
            return None
        return self.initial_issue_count - self.final_issue_count


class ReviewAnalyticsRecorder:
    """In-memory analytics collector for a review session."""

    def __init__(self, *, enabled: bool = True) -> None:
        self._enabled = enabled
        self._notes: dict[str, NoteAnalytics] = {}

    def start_note(self, note_path: str, *, profile: str) -> None:
        """Initialise tracking for a note."""
        if not self._enabled:
            return
        self._notes[note_path] = NoteAnalytics(note_path=note_path, profile=profile)

    def record_iteration(
        self,
        note_path: str,
        *,
        iteration: int,
        metadata_issues: int,
        structural_issues: int,
        parity_issues: int,
    ) -> None:
        """Store validator outcome for the iteration."""
        if not self._enabled:
            return
        stats = IterationAnalytics(
            iteration=iteration,
            metadata_issues=metadata_issues,
            structural_issues=structural_issues,
            parity_issues=parity_issues,
            total_issues=metadata_issues + structural_issues + parity_issues,
        )
        self._notes.setdefault(
            note_path, NoteAnalytics(note_path=note_path, profile="unknown")
        ).record_iteration(stats)

    def set_iteration_decision(self, note_path: str, iteration: int, decision: str) -> None:
        """Attach a routing decision to a recorded iteration."""
        if not self._enabled:
            return
        if note_path in self._notes:
            self._notes[note_path].set_decision(iteration, decision)

    def record_qa_attempt(
        self,
        note_path: str,
        *,
        iteration: int,
        passed: bool | None,
        summary: str | None,
    ) -> None:
        """Store information about a QA verification run."""
        if not self._enabled:
            return
        attempt = QAAttemptAnalytics(iteration=iteration, passed=passed, summary=summary)
        self._notes.setdefault(
            note_path, NoteAnalytics(note_path=note_path, profile="unknown")
        ).add_qa_attempt(attempt)

    def finalize(
        self,
        note_path: str,
        *,
        iterations: int,
        final_issue_count: int,
        elapsed_seconds: float,
        qa_passed: bool | None,
        error: str | None,
        requires_human_review: bool,
    ) -> None:
        """Mark a note run as finished and attach summary data."""
        if not self._enabled:
            return
        self._notes.setdefault(
            note_path, NoteAnalytics(note_path=note_path, profile="unknown")
        ).finalize(
            iterations=iterations,
            final_issue_count=final_issue_count,
            elapsed_seconds=elapsed_seconds,
            qa_passed=qa_passed,
            error=error,
            requires_human_review=requires_human_review,
        )

    def get_note(self, note_path: str) -> NoteAnalytics | None:
        """Return analytics for a specific note if present."""
        return self._notes.get(note_path)

    def iter_notes(self) -> Iterable[NoteAnalytics]:
        """Iterate over all recorded note analytics objects."""
        return self._notes.values()

    def summary(self) -> dict[str, Any]:
        """Return aggregated statistics for all tracked notes."""
        if not self._enabled or not self._notes:
            return {
                "enabled": self._enabled,
                "notes_tracked": 0,
                "avg_duration_seconds": None,
                "avg_iterations": None,
                "avg_issues_resolved": None,
            }

        completed = [note for note in self._notes.values() if note.elapsed_seconds is not None]
        if not completed:
            return {
                "enabled": self._enabled,
                "notes_tracked": len(self._notes),
                "avg_duration_seconds": None,
                "avg_iterations": None,
                "avg_issues_resolved": None,
            }

        durations = [note.elapsed_seconds for note in completed if note.elapsed_seconds is not None]
        iterations = [note.iterations for note in completed]
        issues_resolved = [
            note.issues_resolved
            for note in completed
            if note.issues_resolved is not None
        ]

        return {
            "enabled": self._enabled,
            "notes_tracked": len(self._notes),
            "avg_duration_seconds": mean(durations) if durations else None,
            "avg_iterations": mean(iterations) if iterations else None,
            "avg_issues_resolved": mean(issues_resolved) if issues_resolved else None,
        }
