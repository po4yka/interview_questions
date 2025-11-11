"""Atomic file operations with locking support.

This module provides safe file operations that prevent data corruption
during concurrent access and ensure atomic writes.
"""

from __future__ import annotations

import fcntl
import os
import tempfile
from pathlib import Path
from typing import Any

from loguru import logger


class FileWriteError(Exception):
    """Raised when atomic file write fails."""

    pass


def atomic_write(path: Path, content: str, encoding: str = "utf-8", create_backup: bool = True) -> None:
    """Write content to a file atomically with optional backup.

    This function ensures that:
    1. The file is never partially written (atomic operation)
    2. No concurrent writes corrupt the file (file locking)
    3. Original content can be recovered if something goes wrong (backup)

    Args:
        path: Path to the file to write
        content: Content to write to the file
        encoding: Text encoding (default: utf-8)
        create_backup: Whether to create a .backup file before writing

    Raises:
        FileWriteError: If the write operation fails

    Example:
        >>> atomic_write(Path("note.md"), "# Updated content", create_backup=True)
    """
    path = Path(path).resolve()

    # Create parent directory if it doesn't exist
    path.parent.mkdir(parents=True, exist_ok=True)

    # Create backup if requested and file exists
    if create_backup and path.exists():
        backup_path = path.with_suffix(path.suffix + ".backup")
        try:
            # Read original with lock
            with open(path, "r", encoding=encoding) as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)  # Shared lock for reading
                try:
                    original_content = f.read()
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

            # Write backup atomically
            _write_temp_and_rename(backup_path, original_content, encoding)
            logger.debug(f"Created backup: {backup_path.name}")
        except Exception as e:
            logger.warning(f"Failed to create backup for {path.name}: {e}")
            # Continue with write even if backup fails

    # Write content atomically
    try:
        _write_temp_and_rename(path, content, encoding)
        logger.debug(f"Atomically wrote {len(content)} bytes to {path.name}")
    except Exception as e:
        error_msg = f"Atomic write failed for {path}: {e}"
        logger.error(error_msg)
        raise FileWriteError(error_msg) from e


def _write_temp_and_rename(path: Path, content: str, encoding: str) -> None:
    """Write content to a temporary file and rename it atomically.

    This is the core atomic write operation using temp file + rename.
    On Unix systems, rename is atomic. On Windows, it may not be atomic
    if the target exists, so we handle that case carefully.

    Args:
        path: Target file path
        content: Content to write
        encoding: Text encoding
    """
    # Create temp file in the same directory to ensure same filesystem
    # (rename across filesystems is not atomic)
    fd = None
    temp_path = None

    try:
        fd, temp_path_str = tempfile.mkstemp(
            dir=path.parent,
            prefix=f".{path.stem}_",
            suffix=".tmp",
            text=True
        )
        temp_path = Path(temp_path_str)

        # Write to temp file with exclusive lock
        with os.fdopen(fd, "w", encoding=encoding) as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # Exclusive lock for writing
            try:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())  # Ensure written to disk
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        fd = None  # File closed by os.fdopen context manager

        # Set permissions to match original file if it exists
        if path.exists():
            try:
                original_stat = path.stat()
                os.chmod(temp_path, original_stat.st_mode)
            except Exception as e:
                logger.debug(f"Could not preserve permissions: {e}")

        # Atomic rename (on Unix, this is guaranteed atomic)
        # On Windows, we need to handle the case where target exists
        if os.name == 'nt' and path.exists():
            # Windows: need to remove target first
            # This creates a small race condition window, but it's unavoidable
            path.unlink()

        temp_path.rename(path)

    except Exception as e:
        # Clean up temp file on error
        if fd is not None:
            try:
                os.close(fd)
            except Exception as cleanup_error:
                logger.debug("Failed to close temp fd: {}", cleanup_error)
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink()
            except Exception as cleanup_error:
                logger.debug("Failed to remove temp file %s: %s", temp_path, cleanup_error)
        raise


def locked_read(path: Path, encoding: str = "utf-8") -> str:
    """Read a file with shared lock to prevent concurrent writes.

    Args:
        path: Path to the file to read
        encoding: Text encoding (default: utf-8)

    Returns:
        File content as string

    Raises:
        FileNotFoundError: If the file doesn't exist
        FileWriteError: If reading fails
    """
    path = Path(path).resolve()

    try:
        with open(path, "r", encoding=encoding) as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)  # Shared lock
            try:
                content = f.read()
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        return content
    except Exception as e:
        error_msg = f"Locked read failed for {path}: {e}"
        logger.error(error_msg)
        raise FileWriteError(error_msg) from e


def safe_backup_and_write(path: Path, new_content: str, encoding: str = "utf-8") -> bool:
    """Create a backup and write new content atomically.

    This is a convenience function that combines backup creation and atomic write.

    Args:
        path: Path to the file
        new_content: New content to write
        encoding: Text encoding

    Returns:
        True if successful, False otherwise
    """
    try:
        atomic_write(path, new_content, encoding=encoding, create_backup=True)
        return True
    except FileWriteError as e:
        logger.error(f"Failed to write {path}: {e}")
        return False
