"""Markdown report generation for validation results."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from validators.base import Severity, ValidationIssue


@dataclass
class FileResult:
    path: str
    issues: List[ValidationIssue]
    passed: List[str]


class ReportGenerator:
    """Produce markdown summaries of validation runs."""

    def __init__(self, results: Iterable[FileResult]):
        self.results = list(results)

    def write_markdown(self, report_path: Path) -> None:
        lines: List[str] = []
        lines.append("# Validation Report")
        lines.append("")
        lines.extend(self._build_summary_section())
        lines.append("")
        for result in self.results:
            lines.extend(self._build_file_section(result))
        report_path.write_text("\n".join(lines), encoding="utf-8")

    def _build_summary_section(self) -> List[str]:
        severity_counter = Counter()
        for result in self.results:
            for issue in result.issues:
                severity_counter[issue.severity.value] += 1
        lines = ["## Summary", ""]
        if not severity_counter:
            lines.append("- All files passed without issues.")
            return lines
        for severity, count in sorted(severity_counter.items(), reverse=True):
            lines.append(f"- {severity}: {count}")
        return lines

    def _build_file_section(self, result: FileResult) -> List[str]:
        lines = [f"## {result.path}", ""]
        if result.issues:
            lines.append("### Issues")
            lines.append("")
            for issue in result.issues:
                context = f" (field: {issue.field})" if issue.field else ""
                lines.append(f"- **{issue.severity.value}**: {issue.message}{context}")
            lines.append("")
        else:
            lines.append("No issues found.")
            lines.append("")
        if result.passed:
            lines.append("### Passed Checks")
            lines.append("")
            for item in result.passed:
                lines.append(f"- {item}")
            lines.append("")
        return lines
