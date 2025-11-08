"""Base classes shared by validation modules."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Severity(str, Enum):
    """Represents issue severity."""

    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class ValidationIssue:
    """Structured representation of a validation issue."""

    severity: Severity
    message: str
    field: str | None = None
    line: int | None = None


@dataclass
class ValidationSummary:
    """Holds issues and passed checks for a validator run."""

    issues: list[ValidationIssue] = field(default_factory=list)
    passed: list[str] = field(default_factory=list)


class BaseValidator:
    """Base class implementing helper methods used by concrete validators."""

    def __init__(self, *, content: str, frontmatter: dict, path: str, taxonomy):
        self.content = content
        self.frontmatter = frontmatter or {}
        self.path = path
        self.taxonomy = taxonomy
        self._summary = ValidationSummary()

    @property
    def issues(self) -> list[ValidationIssue]:
        return self._summary.issues

    @property
    def passed(self) -> list[str]:
        return self._summary.passed

    def add_issue(
        self,
        severity: Severity,
        message: str,
        *,
        field: str | None = None,
        line: int | None = None,
    ) -> None:
        """Record a validation issue."""

        self._summary.issues.append(
            ValidationIssue(severity=severity, message=message, field=field, line=line)
        )

    def add_passed(self, message: str) -> None:
        """Record a passed check."""

        self._summary.passed.append(message)

    def validate(self) -> ValidationSummary:
        """Run validator logic in subclasses."""

        raise NotImplementedError
