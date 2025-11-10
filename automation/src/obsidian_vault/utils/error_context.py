"""Error context preservation and enhanced exception handling.

This module provides utilities to capture and preserve error context,
making debugging easier and error messages more informative.
"""

from __future__ import annotations

import sys
import traceback
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator

from loguru import logger


class ErrorContext:
    """Container for error context information.

    Stores relevant context about where and why an error occurred,
    making debugging significantly easier.
    """

    def __init__(
        self,
        operation: str,
        file_path: Path | str | None = None,
        details: dict[str, Any] | None = None,
    ):
        """Initialize error context.

        Args:
            operation: Description of the operation being performed
            file_path: Path to the file being processed (if applicable)
            details: Additional context details
        """
        self.operation = operation
        self.file_path = Path(file_path) if file_path else None
        self.details = details or {}

    def __str__(self) -> str:
        """Format error context as a string."""
        parts = [f"Operation: {self.operation}"]

        if self.file_path:
            parts.append(f"File: {self.file_path}")

        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            parts.append(f"Details: {details_str}")

        return " | ".join(parts)


@contextmanager
def error_context(
    operation: str,
    file_path: Path | str | None = None,
    log_errors: bool = True,
    **details: Any,
) -> Generator[ErrorContext, None, None]:
    """Context manager for capturing and preserving error context.

    Usage:
        with error_context("parsing YAML", file_path="note.md", line=42):
            parse_yaml(content)

    Args:
        operation: Description of the operation
        file_path: Path to the file being processed
        log_errors: Whether to log errors automatically
        **details: Additional context details

    Yields:
        ErrorContext object that can be updated during execution
    """
    ctx = ErrorContext(operation, file_path, details)

    try:
        yield ctx
    except Exception as e:
        # Preserve the original exception while adding context
        if log_errors:
            logger.error(
                f"Error during {operation}: {type(e).__name__}: {e}"
            )
            logger.error(f"Context: {ctx}")

        # Add context to exception (without losing original traceback)
        if not hasattr(e, "_error_context"):
            e._error_context = []  # type: ignore
        e._error_context.append(ctx)  # type: ignore

        # Re-raise with original traceback
        raise


def format_exception_with_context(exc: Exception) -> str:
    """Format an exception with all preserved error context.

    Args:
        exc: Exception to format

    Returns:
        Formatted exception string with context

    Example:
        >>> try:
        ...     with error_context("parsing", file_path="test.md"):
        ...         raise ValueError("Invalid value")
        ... except Exception as e:
        ...     print(format_exception_with_context(e))
    """
    lines = []

    # Exception type and message
    lines.append(f"{type(exc).__name__}: {exc}")

    # Error contexts (if any)
    if hasattr(exc, "_error_context"):
        contexts = getattr(exc, "_error_context", [])
        if contexts:
            lines.append("\nError Context Trail:")
            for i, ctx in enumerate(contexts, 1):
                lines.append(f"  {i}. {ctx}")

    # Original traceback
    tb = traceback.format_exception(type(exc), exc, exc.__traceback__)
    lines.append("\nTraceback:")
    lines.extend(tb)

    return "\n".join(lines)


def log_exception_with_context(
    exc: Exception,
    message: str = "An error occurred",
    level: str = "error",
) -> None:
    """Log an exception with full context.

    Args:
        exc: Exception to log
        message: Log message
        level: Log level (error, warning, critical)
    """
    formatted = format_exception_with_context(exc)

    log_func = getattr(logger, level, logger.error)
    log_func(f"{message}:\n{formatted}")


def get_error_summary(exc: Exception) -> dict[str, Any]:
    """Extract a structured summary from an exception.

    Args:
        exc: Exception to summarize

    Returns:
        Dictionary with error information
    """
    summary = {
        "type": type(exc).__name__,
        "message": str(exc),
        "has_context": hasattr(exc, "_error_context"),
    }

    if hasattr(exc, "_error_context"):
        contexts = getattr(exc, "_error_context", [])
        summary["contexts"] = [
            {
                "operation": ctx.operation,
                "file_path": str(ctx.file_path) if ctx.file_path else None,
                "details": ctx.details,
            }
            for ctx in contexts
        ]

    # Add traceback information
    if exc.__traceback__:
        tb_lines = traceback.extract_tb(exc.__traceback__)
        summary["traceback"] = [
            {
                "file": frame.filename,
                "line": frame.lineno,
                "function": frame.name,
                "code": frame.line,
            }
            for frame in tb_lines
        ]

    return summary


@contextmanager
def safe_operation(
    operation: str,
    file_path: Path | str | None = None,
    fallback_value: Any = None,
    suppress_errors: bool = False,
    **details: Any,
) -> Generator[ErrorContext, None, None]:
    """Context manager for operations that should not crash the program.

    This is useful for non-critical operations where you want to log errors
    but continue execution.

    Args:
        operation: Description of the operation
        file_path: Path to the file being processed
        fallback_value: Value to return if operation fails (when suppress_errors=True)
        suppress_errors: If True, suppress exceptions and return fallback_value
        **details: Additional context details

    Yields:
        ErrorContext object
    """
    ctx = ErrorContext(operation, file_path, details)

    try:
        yield ctx
    except Exception as e:
        logger.error(f"Error during {operation}: {type(e).__name__}: {e}")
        logger.error(f"Context: {ctx}")

        if suppress_errors:
            logger.warning(
                f"Suppressing error and continuing (fallback_value={fallback_value})"
            )
        else:
            # Add context and re-raise
            if not hasattr(e, "_error_context"):
                e._error_context = []  # type: ignore
            e._error_context.append(ctx)  # type: ignore
            raise


def chain_exceptions(
    new_exception: Exception,
    cause: Exception,
    context: ErrorContext | None = None,
) -> Exception:
    """Chain exceptions while preserving context.

    Args:
        new_exception: New exception to raise
        cause: Original exception that caused the new one
        context: Optional error context to attach

    Returns:
        New exception with proper chaining

    Example:
        >>> try:
        ...     risky_operation()
        ... except ValueError as e:
        ...     ctx = ErrorContext("data processing", file_path="data.csv")
        ...     raise chain_exceptions(
        ...         ProcessingError("Failed to process data"),
        ...         e,
        ...         ctx
        ...     )
    """
    # Set the cause explicitly (Python 3 exception chaining)
    new_exception.__cause__ = cause

    # Preserve error context from cause
    if hasattr(cause, "_error_context"):
        cause_contexts = getattr(cause, "_error_context", [])
        if not hasattr(new_exception, "_error_context"):
            new_exception._error_context = []  # type: ignore
        new_exception._error_context.extend(cause_contexts)  # type: ignore

    # Add new context if provided
    if context:
        if not hasattr(new_exception, "_error_context"):
            new_exception._error_context = []  # type: ignore
        new_exception._error_context.append(context)  # type: ignore

    return new_exception
