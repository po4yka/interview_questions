#!/usr/bin/env python3
"""
Severity Reporter for Validation Results

Formats validation results into readable reports with severity levels.
"""

from typing import List
from collections import defaultdict


try:
    from .validator import ValidationIssue, Severity
except ImportError:
    # For standalone execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from validator import ValidationIssue, Severity


class SeverityReporter:
    """Format validation results into reports"""

    def __init__(self):
        """Initialize reporter"""
        self.severity_symbols = {
            Severity.REQUIRED: "❌",
            Severity.FORBIDDEN: "🚫",
            Severity.WARNING: "⚠️",
            Severity.NOTE: "💡"
        }

    def generate_report(
        self,
        issues: List[ValidationIssue],
        filename: str,
        total_checks: int = 50
    ) -> str:
        """
        Generate formatted validation report

        Args:
            issues: List of validation issues
            filename: Name of file being validated
            total_checks: Total number of checks performed

        Returns:
            Formatted report string
        """
        # Group issues by severity
        by_severity = defaultdict(list)
        for issue in issues:
            by_severity[issue.severity].append(issue)

        # Determine overall status
        has_required = len(by_severity[Severity.REQUIRED]) > 0
        has_forbidden = len(by_severity[Severity.FORBIDDEN]) > 0
        has_warnings = len(by_severity[Severity.WARNING]) > 0

        if has_required or has_forbidden:
            status = "FAILED"
        elif has_warnings:
            status = "PASSED_WITH_WARNINGS"
        else:
            status = "PASSED"

        # Build report
        lines = [
            f"# Validation Report: {filename}",
            "",
            f"**Status**: {status}",
            "",
            "---",
            ""
        ]

        # Required checks section
        required_count = len(by_severity[Severity.REQUIRED])
        required_passed = total_checks - required_count
        if required_count == 0:
            lines.append(f"## REQUIRED Checks: {required_passed}/{required_passed} ✅")
            lines.append("")
            lines.append("**Result**: All REQUIRED checks passed")
        else:
            lines.append(f"## REQUIRED Checks: {required_passed}/{total_checks} ❌")
            lines.append("")
            for issue in by_severity[Severity.REQUIRED]:
                lines.append(f"❌ **{issue.category}**: {issue.message}")
                if issue.suggestion:
                    lines.append(f"   → {issue.suggestion}")
                lines.append("")
            lines.append(f"**Result**: {required_count} REQUIRED checks failed")

        lines.append("")
        lines.append("---")
        lines.append("")

        # Forbidden checks section
        forbidden_count = len(by_severity[Severity.FORBIDDEN])
        if forbidden_count == 0:
            lines.append("## FORBIDDEN Checks: Passed ✅")
            lines.append("")
            lines.append("**Result**: No FORBIDDEN violations")
        else:
            lines.append(f"## FORBIDDEN Checks: {forbidden_count} violations 🚫")
            lines.append("")
            for issue in by_severity[Severity.FORBIDDEN]:
                lines.append(f"🚫 **{issue.category}**: {issue.message}")
                if issue.suggestion:
                    lines.append(f"   → {issue.suggestion}")
                lines.append("")
            lines.append(f"**Result**: {forbidden_count} FORBIDDEN violations found")

        lines.append("")
        lines.append("---")
        lines.append("")

        # Warnings section
        warning_count = len(by_severity[Severity.WARNING])
        if warning_count > 0:
            lines.append(f"## WARNINGS: {warning_count} issues ⚠️")
            lines.append("")
            for issue in by_severity[Severity.WARNING]:
                lines.append(f"⚠️ **{issue.category}**: {issue.message}")
                if issue.suggestion:
                    lines.append(f"   → {issue.suggestion}")
                lines.append("")
            lines.append("---")
            lines.append("")

        # Notes section
        note_count = len(by_severity[Severity.NOTE])
        if note_count > 0:
            lines.append(f"## NOTES: {note_count} suggestions 💡")
            lines.append("")
            for issue in by_severity[Severity.NOTE]:
                lines.append(f"💡 **{issue.category}**: {issue.message}")
                if issue.suggestion:
                    lines.append(f"   → {issue.suggestion}")
                lines.append("")
            lines.append("---")
            lines.append("")

        # Summary
        lines.append("## Summary")
        lines.append("")

        if status == "PASSED":
            lines.append("**Overall**: Note is fully compliant ✅")
        elif status == "PASSED_WITH_WARNINGS":
            lines.append("**Overall**: Note is valid but has warnings")
        else:
            lines.append("**Overall**: Note requires fixes before approval ❌")

        lines.append("")
        lines.append(f"**Critical Issues**: {required_count + forbidden_count}")
        lines.append(f"**Warnings**: {warning_count}")
        lines.append(f"**Suggestions**: {note_count}")
        lines.append("")

        # Recommendation
        if status == "FAILED":
            lines.append("**Recommendation**: Fix all REQUIRED and FORBIDDEN issues before proceeding.")
        elif status == "PASSED_WITH_WARNINGS":
            lines.append("**Recommendation**: Address warnings to improve note quality.")
        else:
            lines.append("**Recommendation**: Note is ready for human review.")

        return "\n".join(lines)

    def generate_summary(self, issues: List[ValidationIssue]) -> str:
        """
        Generate brief summary of issues

        Args:
            issues: List of validation issues

        Returns:
            Brief summary string
        """
        by_severity = defaultdict(int)
        for issue in issues:
            by_severity[issue.severity] += 1

        if not issues:
            return "✅ No issues found"

        parts = []
        if by_severity[Severity.REQUIRED]:
            parts.append(f"❌ {by_severity[Severity.REQUIRED]} required")
        if by_severity[Severity.FORBIDDEN]:
            parts.append(f"🚫 {by_severity[Severity.FORBIDDEN]} forbidden")
        if by_severity[Severity.WARNING]:
            parts.append(f"⚠️ {by_severity[Severity.WARNING]} warnings")
        if by_severity[Severity.NOTE]:
            parts.append(f"💡 {by_severity[Severity.NOTE]} notes")

        return ", ".join(parts)


def main():
    """Example usage"""
    # Create example issues
    issues = [
        ValidationIssue(
            severity=Severity.REQUIRED,
            category="YAML Completeness",
            message="Missing 'related' field",
            suggestion="Add 'related: [...]' to YAML frontmatter"
        ),
        ValidationIssue(
            severity=Severity.FORBIDDEN,
            category="Tag Requirements",
            message="Russian in tags: корутины",
            suggestion="Use English only in tags"
        ),
        ValidationIssue(
            severity=Severity.WARNING,
            category="Content Quality",
            message="Missing '## Follow-ups' section",
            suggestion="Add common variations and edge cases"
        ),
        ValidationIssue(
            severity=Severity.NOTE,
            category="Link Quality",
            message="Only 2 related links (recommend 3-5)",
            suggestion="Add more related concepts or questions"
        )
    ]

    reporter = SeverityReporter()

    # Generate full report
    report = reporter.generate_report(issues, "q-test--kotlin--medium.md", total_checks=50)
    print(report)
    print()

    # Generate summary
    summary = reporter.generate_summary(issues)
    print(f"Summary: {summary}")


if __name__ == '__main__':
    main()
