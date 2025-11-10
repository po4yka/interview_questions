"""Log sanitization to prevent sensitive data leakage.

This module provides utilities to sanitize logs and prevent accidental
exposure of API keys, tokens, and other sensitive information.
"""

from __future__ import annotations

import re
from typing import Any


# Patterns for sensitive data
SENSITIVE_PATTERNS = [
    # API Keys
    (re.compile(r'(api[_-]?key["\']?\s*[:=]\s*["\']?)([A-Za-z0-9\-_]{20,})', re.IGNORECASE), r'\1***REDACTED***'),
    (re.compile(r'(openrouter[_-]?api[_-]?key["\']?\s*[:=]\s*["\']?)([A-Za-z0-9\-_]{20,})', re.IGNORECASE), r'\1***REDACTED***'),
    (re.compile(r'(firecrawl[_-]?api[_-]?key["\']?\s*[:=]\s*["\']?)([A-Za-z0-9\-_]{20,})', re.IGNORECASE), r'\1***REDACTED***'),

    # Bearer tokens
    (re.compile(r'(Bearer\s+)([A-Za-z0-9\-_\.]{20,})', re.IGNORECASE), r'\1***REDACTED***'),
    (re.compile(r'(token["\']?\s*[:=]\s*["\']?)([A-Za-z0-9\-_]{20,})', re.IGNORECASE), r'\1***REDACTED***'),

    # Authorization headers
    (re.compile(r'(Authorization["\']?\s*[:=]\s*["\']?)([^"\'\s]{20,})', re.IGNORECASE), r'\1***REDACTED***'),

    # Passwords
    (re.compile(r'(password["\']?\s*[:=]\s*["\']?)([^"\'\s]+)', re.IGNORECASE), r'\1***REDACTED***'),
    (re.compile(r'(passwd["\']?\s*[:=]\s*["\']?)([^"\'\s]+)', re.IGNORECASE), r'\1***REDACTED***'),

    # Secrets
    (re.compile(r'(secret["\']?\s*[:=]\s*["\']?)([^"\'\s]{8,})', re.IGNORECASE), r'\1***REDACTED***'),

    # Common API key formats (sk-, pk-, etc.)
    (re.compile(r'\b(sk|pk|rk|tok)[-_]([A-Za-z0-9]{20,})', re.IGNORECASE), r'\1-***REDACTED***'),
]

# Environment variable patterns
ENV_VAR_PATTERNS = [
    re.compile(r'OPENROUTER_API_KEY', re.IGNORECASE),
    re.compile(r'FIRECRAWL_API_KEY', re.IGNORECASE),
    re.compile(r'API_KEY', re.IGNORECASE),
    re.compile(r'.*_TOKEN', re.IGNORECASE),
    re.compile(r'.*_SECRET', re.IGNORECASE),
    re.compile(r'.*_PASSWORD', re.IGNORECASE),
]


def sanitize_string(text: str) -> str:
    """Sanitize a string by redacting sensitive information.

    Args:
        text: String to sanitize

    Returns:
        Sanitized string with sensitive data redacted

    Example:
        >>> sanitize_string("API_KEY=sk-1234567890abcdef")
        'API_KEY=***REDACTED***'
    """
    if not text:
        return text

    sanitized = text
    for pattern, replacement in SENSITIVE_PATTERNS:
        sanitized = pattern.sub(replacement, sanitized)

    return sanitized


def sanitize_dict(data: dict[str, Any], max_depth: int = 5) -> dict[str, Any]:
    """Recursively sanitize a dictionary by redacting sensitive values.

    Args:
        data: Dictionary to sanitize
        max_depth: Maximum recursion depth to prevent infinite loops

    Returns:
        New dictionary with sensitive values redacted
    """
    if max_depth <= 0:
        return {"_redacted": "max_depth_exceeded"}

    sanitized = {}
    for key, value in data.items():
        # Check if key name is sensitive
        key_is_sensitive = any(pattern.match(str(key)) for pattern in ENV_VAR_PATTERNS)

        if key_is_sensitive:
            sanitized[key] = "***REDACTED***"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value, max_depth - 1)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_dict(item, max_depth - 1) if isinstance(item, dict)
                else sanitize_string(str(item)) if isinstance(item, str)
                else item
                for item in value
            ]
        elif isinstance(value, str):
            sanitized[key] = sanitize_string(value)
        else:
            sanitized[key] = value

    return sanitized


def sanitize_log_record(record: dict[str, Any]) -> dict[str, Any]:
    """Sanitize a log record before writing to file.

    This is designed to work with loguru's custom serialization.

    Args:
        record: Log record dictionary

    Returns:
        Sanitized log record
    """
    sanitized = record.copy()

    # Sanitize the message
    if "message" in sanitized:
        sanitized["message"] = sanitize_string(str(sanitized["message"]))

    # Sanitize extra fields
    if "extra" in sanitized and isinstance(sanitized["extra"], dict):
        sanitized["extra"] = sanitize_dict(sanitized["extra"])

    # Sanitize exception info
    if "exception" in sanitized and sanitized["exception"]:
        if isinstance(sanitized["exception"], dict):
            if "value" in sanitized["exception"]:
                sanitized["exception"]["value"] = sanitize_string(
                    str(sanitized["exception"]["value"])
                )

    return sanitized


def is_sensitive_key(key: str) -> bool:
    """Check if a dictionary key name suggests sensitive data.

    Args:
        key: Dictionary key name

    Returns:
        True if the key name suggests sensitive data

    Example:
        >>> is_sensitive_key("API_KEY")
        True
        >>> is_sensitive_key("username")
        False
    """
    return any(pattern.match(key) for pattern in ENV_VAR_PATTERNS)


def redact_url_params(url: str) -> str:
    """Redact sensitive query parameters from URLs.

    Args:
        url: URL string

    Returns:
        URL with sensitive parameters redacted

    Example:
        >>> redact_url_params("https://api.com?key=secret123&page=1")
        'https://api.com?key=***REDACTED***&page=1'
    """
    # Redact common sensitive parameter names
    sensitive_params = ['key', 'token', 'api_key', 'apikey', 'secret', 'password', 'auth']

    for param in sensitive_params:
        # Match param=value in query string
        url = re.sub(
            rf'({param}=)([^&\s]+)',
            r'\1***REDACTED***',
            url,
            flags=re.IGNORECASE
        )

    return url


# Pre-configured sanitizer for common use cases
def sanitize_for_logging(value: Any) -> Any:
    """Sanitize any value for safe logging.

    This is a convenience function that handles different types appropriately.

    Args:
        value: Any value to sanitize

    Returns:
        Sanitized value safe for logging
    """
    if value is None:
        return None
    elif isinstance(value, str):
        return sanitize_string(value)
    elif isinstance(value, dict):
        return sanitize_dict(value)
    elif isinstance(value, (list, tuple)):
        return [sanitize_for_logging(item) for item in value]
    else:
        # For other types, convert to string and sanitize
        return sanitize_string(str(value))
