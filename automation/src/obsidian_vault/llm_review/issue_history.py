"""Helpers for working with validator issue history snapshots."""

from __future__ import annotations

from collections.abc import Iterable

_NON_BLOCKING_SEVERITIES = {"WARNING", "INFO"}


def _severity_from_signature(signature: str) -> str:
    """Extract the severity prefix from an issue signature."""
    severity, _, _ = signature.partition(":")

    if not severity:
        return signature

    # Signatures may occasionally contain Enum reprs like "Severity.WARNING".
    if "." in severity:
        severity = severity.rsplit(".", 1)[-1]

    return severity


def filter_blocking_issue_history(history: Iterable[set[str]]) -> list[set[str]]:
    """Return a copy of the issue history with warnings/info removed.

    Args:
        history: Sequence of issue signature sets captured each iteration.

    Returns:
        List mirroring the input ordering where each set only contains
        signatures with blocking severities (ERROR/CRITICAL).
    """
    filtered: list[set[str]] = []
    for iteration in history:
        filtered.append(
            {
                signature
                for signature in iteration
                if _severity_from_signature(signature) not in _NON_BLOCKING_SEVERITIES
            }
        )
    return filtered
