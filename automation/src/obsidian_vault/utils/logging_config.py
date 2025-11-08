"""
Logging configuration using Loguru.

Provides two logging levels:
- Console: INFO level with useful, concise messages
- File: DEBUG level with detailed diagnostic information

The file logs are stored in ~/.cache/obsidian-vault/vault.log with rotation.
"""

from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger


def setup_logging(
    console_level: str = "INFO",
    file_level: str = "DEBUG",
    log_file: Path | None = None,
    rotation: str = "10 MB",
    retention: str = "1 week",
) -> None:
    """
    Configure logging for the application.

    Args:
        console_level: Logging level for console output (default: INFO)
        file_level: Logging level for file output (default: DEBUG)
        log_file: Path to log file (default: ~/.cache/obsidian-vault/vault.log)
        rotation: When to rotate the log file (default: 10 MB)
        retention: How long to keep old logs (default: 1 week)
    """
    # Remove default handler
    logger.remove()

    # Console handler - clean, useful messages only
    logger.add(
        sys.stderr,
        level=console_level,
        format="<level>{level: <8}</level> | <level>{message}</level>",
        colorize=True,
        backtrace=False,
        diagnose=False,
    )

    # File handler - detailed debug information
    if log_file is None:
        # Default to ~/.cache/obsidian-vault/vault.log
        cache_dir = Path.home() / ".cache" / "obsidian-vault"
        cache_dir.mkdir(parents=True, exist_ok=True)
        log_file = cache_dir / "vault.log"

    logger.add(
        log_file,
        level=file_level,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation=rotation,
        retention=retention,
        backtrace=True,
        diagnose=True,
        enqueue=True,  # Thread-safe
    )

    logger.debug(f"Logging initialized - Console: {console_level}, File: {file_level} ({log_file})")


def get_logger() -> logger:
    """
    Get the configured logger instance.

    Returns:
        Configured loguru logger
    """
    return logger


# Convenience functions for common log levels
def debug(message: str, **kwargs) -> None:
    """Log a debug message (file only)."""
    logger.debug(message, **kwargs)


def info(message: str, **kwargs) -> None:
    """Log an info message (console and file)."""
    logger.info(message, **kwargs)


def warning(message: str, **kwargs) -> None:
    """Log a warning message (console and file)."""
    logger.warning(message, **kwargs)


def error(message: str, **kwargs) -> None:
    """Log an error message (console and file)."""
    logger.error(message, **kwargs)


def critical(message: str, **kwargs) -> None:
    """Log a critical message (console and file)."""
    logger.critical(message, **kwargs)


def success(message: str, **kwargs) -> None:
    """Log a success message (console and file)."""
    logger.success(message, **kwargs)
