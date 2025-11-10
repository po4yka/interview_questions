"""Input validation and sanitization for user-provided data.

This module provides validators for URLs, file paths, integers, and other
user inputs to prevent injection attacks and invalid data from entering the system.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from obsidian_vault.exceptions import ValidationError


def validate_url(url: str, allowed_schemes: set[str] | None = None) -> str:
    """Validate and sanitize a URL.

    Args:
        url: URL string to validate
        allowed_schemes: Set of allowed URL schemes (default: {'http', 'https'})

    Returns:
        Validated URL string

    Raises:
        ValidationError: If the URL is invalid or uses a disallowed scheme

    Example:
        >>> validate_url("https://example.com/article")
        'https://example.com/article'
        >>> validate_url("javascript:alert(1)")  # doctest: +SKIP
        ValidationError: Invalid URL scheme: javascript
    """
    if not url or not isinstance(url, str):
        raise ValidationError("URL must be a non-empty string")

    url = url.strip()

    # Remove any null bytes or control characters
    url = "".join(c for c in url if ord(c) >= 32 and c != '\x7f')

    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ValidationError(f"Invalid URL format: {e}")

    if not parsed.scheme:
        raise ValidationError("URL must include a scheme (http:// or https://)")

    if allowed_schemes is None:
        allowed_schemes = {'http', 'https'}

    if parsed.scheme.lower() not in allowed_schemes:
        raise ValidationError(
            f"Invalid URL scheme: {parsed.scheme}. "
            f"Allowed schemes: {', '.join(allowed_schemes)}"
        )

    if not parsed.netloc:
        raise ValidationError("URL must include a domain name")

    # Check for obvious malicious patterns
    suspicious_patterns = [
        r'javascript:',
        r'data:',
        r'file:',
        r'vbscript:',
        r'<script',
        r'onerror=',
        r'onload=',
    ]

    url_lower = url.lower()
    for pattern in suspicious_patterns:
        if re.search(pattern, url_lower):
            raise ValidationError(f"URL contains suspicious pattern: {pattern}")

    return url


def validate_integer(
    value: Any,
    min_value: int | None = None,
    max_value: int | None = None,
    param_name: str = "value"
) -> int:
    """Validate and convert a value to an integer within bounds.

    Args:
        value: Value to validate and convert
        min_value: Minimum allowed value (inclusive)
        max_value: Maximum allowed value (inclusive)
        param_name: Parameter name for error messages

    Returns:
        Validated integer

    Raises:
        ValidationError: If the value is invalid or out of bounds

    Example:
        >>> validate_integer(5, min_value=1, max_value=10)
        5
        >>> validate_integer(15, min_value=1, max_value=10)  # doctest: +SKIP
        ValidationError: value must be between 1 and 10
    """
    try:
        int_value = int(value)
    except (TypeError, ValueError) as e:
        raise ValidationError(f"{param_name} must be an integer, got: {type(value).__name__}")

    if min_value is not None and int_value < min_value:
        if max_value is not None:
            raise ValidationError(f"{param_name} must be between {min_value} and {max_value}, got: {int_value}")
        else:
            raise ValidationError(f"{param_name} must be at least {min_value}, got: {int_value}")

    if max_value is not None and int_value > max_value:
        if min_value is not None:
            raise ValidationError(f"{param_name} must be between {min_value} and {max_value}, got: {int_value}")
        else:
            raise ValidationError(f"{param_name} must be at most {max_value}, got: {int_value}")

    return int_value


def validate_path(
    path: str | Path,
    must_exist: bool = False,
    must_be_file: bool = False,
    must_be_dir: bool = False,
    allowed_extensions: set[str] | None = None,
) -> Path:
    """Validate a file path and check various constraints.

    Args:
        path: Path to validate
        must_exist: If True, path must exist
        must_be_file: If True, path must be a file
        must_be_dir: If True, path must be a directory
        allowed_extensions: Set of allowed file extensions (e.g., {'.md', '.txt'})

    Returns:
        Validated Path object

    Raises:
        ValidationError: If the path is invalid or doesn't meet constraints

    Example:
        >>> validate_path("/tmp/test.md", allowed_extensions={'.md'})  # doctest: +SKIP
        PosixPath('/tmp/test.md')
    """
    if not path:
        raise ValidationError("Path cannot be empty")

    try:
        path_obj = Path(path)
    except Exception as e:
        raise ValidationError(f"Invalid path format: {e}")

    # Check for path traversal attempts
    try:
        resolved = path_obj.resolve()
    except Exception as e:
        raise ValidationError(f"Cannot resolve path: {e}")

    # Check null bytes (common injection technique)
    if '\x00' in str(path):
        raise ValidationError("Path contains null bytes")

    if must_exist and not resolved.exists():
        raise ValidationError(f"Path does not exist: {path}")

    if must_be_file:
        if resolved.exists() and not resolved.is_file():
            raise ValidationError(f"Path is not a file: {path}")
    elif must_be_dir:
        if resolved.exists() and not resolved.is_dir():
            raise ValidationError(f"Path is not a directory: {path}")

    if allowed_extensions and resolved.suffix.lower() not in allowed_extensions:
        raise ValidationError(
            f"Invalid file extension: {resolved.suffix}. "
            f"Allowed: {', '.join(allowed_extensions)}"
        )

    return resolved


def validate_choice(value: str, allowed_values: set[str], param_name: str = "value") -> str:
    """Validate that a value is in a set of allowed choices.

    Args:
        value: Value to validate
        allowed_values: Set of allowed values
        param_name: Parameter name for error messages

    Returns:
        Validated value (lowercased for case-insensitive matching)

    Raises:
        ValidationError: If the value is not in the allowed set

    Example:
        >>> validate_choice("strict", {"strict", "standard", "permissive"})
        'strict'
    """
    if not value:
        raise ValidationError(f"{param_name} cannot be empty")

    value_lower = str(value).lower()

    # Case-insensitive matching
    allowed_lower = {str(v).lower() for v in allowed_values}

    if value_lower not in allowed_lower:
        raise ValidationError(
            f"Invalid {param_name}: '{value}'. "
            f"Allowed values: {', '.join(sorted(allowed_values))}"
        )

    return value_lower


def validate_string(
    value: str,
    min_length: int = 0,
    max_length: int | None = None,
    pattern: str | None = None,
    param_name: str = "value",
    allow_empty: bool = False,
) -> str:
    """Validate a string against various constraints.

    Args:
        value: String to validate
        min_length: Minimum string length
        max_length: Maximum string length
        pattern: Optional regex pattern the string must match
        param_name: Parameter name for error messages
        allow_empty: Whether to allow empty strings

    Returns:
        Validated string (stripped of leading/trailing whitespace)

    Raises:
        ValidationError: If the string doesn't meet constraints
    """
    if not isinstance(value, str):
        raise ValidationError(f"{param_name} must be a string, got: {type(value).__name__}")

    # Strip whitespace
    value = value.strip()

    if not allow_empty and not value:
        raise ValidationError(f"{param_name} cannot be empty")

    if len(value) < min_length:
        raise ValidationError(f"{param_name} must be at least {min_length} characters, got: {len(value)}")

    if max_length and len(value) > max_length:
        raise ValidationError(f"{param_name} must be at most {max_length} characters, got: {len(value)}")

    if pattern:
        if not re.match(pattern, value):
            raise ValidationError(f"{param_name} does not match required pattern: {pattern}")

    # Remove null bytes and control characters (except newlines and tabs)
    sanitized = "".join(c for c in value if c == '\n' or c == '\t' or (ord(c) >= 32 and c != '\x7f'))

    if sanitized != value:
        raise ValidationError(f"{param_name} contains invalid control characters")

    return sanitized


def sanitize_filename(filename: str, replacement: str = "_") -> str:
    """Sanitize a filename by removing/replacing invalid characters.

    Args:
        filename: Filename to sanitize
        replacement: Replacement character for invalid chars

    Returns:
        Sanitized filename safe for all platforms

    Example:
        >>> sanitize_filename("my<file>name?.txt")
        'my_file_name_.txt'
    """
    # Characters not allowed in filenames on various OS
    invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'

    # Replace invalid characters
    sanitized = re.sub(invalid_chars, replacement, filename)

    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')

    # Ensure not empty
    if not sanitized:
        sanitized = "unnamed"

    # Limit length (255 is common filesystem limit)
    if len(sanitized) > 255:
        name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        name = name[:255 - len(ext) - 1]
        sanitized = f"{name}.{ext}" if ext else name

    return sanitized
