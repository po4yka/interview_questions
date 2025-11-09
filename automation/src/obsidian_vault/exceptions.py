"""
Custom exception classes for the Obsidian Vault automation package.

This module provides a hierarchy of custom exceptions that enable:
- Better error distinction and handling
- More informative error messages with context
- Domain-specific error information
- Easier debugging and error recovery

Exception Hierarchy:
    VaultError (base)
    ├── VaultConfigError
    ├── VaultFileError
    ├── VaultParsingError
    ├── ValidationError
    │   ├── TaxonomyError
    │   ├── FrontmatterError
    │   └── ContentStructureError
    ├── LLMError
    │   ├── LLMConfigError
    │   ├── LLMResponseError
    │   ├── LLMTimeoutError
    │   └── LLMRateLimitError
    └── GraphError
        ├── OrphanNoteError
        └── BrokenLinkError
"""

from pathlib import Path
from typing import Any, Optional


class VaultError(Exception):
    """Base exception for all vault-related errors."""

    pass


class VaultConfigError(VaultError):
    """Raised when there's a configuration or setup error.

    Examples:
        - Missing required configuration files
        - Invalid configuration values
        - Missing environment variables
    """

    pass


class VaultFileError(VaultError):
    """Raised when file system operations fail.

    Attributes:
        path: The file path that caused the error
        original_error: The underlying exception (if any)
    """

    def __init__(
        self, path: Path, message: str, original_error: Optional[Exception] = None
    ):
        """Initialize file error with context.

        Args:
            path: The file path that caused the error
            message: Human-readable error description
            original_error: The underlying exception (optional)
        """
        self.path = path
        self.original_error = original_error
        error_msg = f"{message}: {path}"
        if original_error:
            error_msg += f" ({type(original_error).__name__}: {original_error})"
        super().__init__(error_msg)


class VaultParsingError(VaultError):
    """Raised when YAML or markdown parsing fails.

    Attributes:
        path: The file that failed to parse
        line: The line number where parsing failed (if known)
        original_error: The underlying parsing exception
    """

    def __init__(
        self,
        path: Path,
        message: str,
        line: Optional[int] = None,
        original_error: Optional[Exception] = None,
    ):
        """Initialize parsing error with location context.

        Args:
            path: The file that failed to parse
            message: Human-readable error description
            line: The line number where parsing failed (optional)
            original_error: The underlying exception (optional)
        """
        self.path = path
        self.line = line
        self.original_error = original_error
        error_msg = f"{message} in {path}"
        if line is not None:
            error_msg += f" at line {line}"
        if original_error:
            error_msg += f" ({type(original_error).__name__}: {original_error})"
        super().__init__(error_msg)


class ValidationError(VaultError):
    """Base exception for validation errors.

    Raised when note content or structure doesn't meet requirements.
    """

    pass


class TaxonomyError(ValidationError):
    """Raised when a topic/subtopic is not in the controlled vocabulary.

    Attributes:
        field: The field name (e.g., 'topic', 'subtopics')
        value: The invalid value
        valid_values: List of valid values from taxonomy
    """

    def __init__(self, field: str, value: str, valid_values: list[str]):
        """Initialize taxonomy error with suggestions.

        Args:
            field: The field name that failed validation
            value: The invalid value provided
            valid_values: List of valid values from TAXONOMY.md
        """
        self.field = field
        self.value = value
        self.valid_values = valid_values

        # Show first 10 valid values as examples
        examples = ", ".join(valid_values[:10])
        if len(valid_values) > 10:
            examples += f", ... ({len(valid_values) - 10} more)"

        super().__init__(
            f"Invalid {field}: '{value}' not in taxonomy. "
            f"Valid values: {examples}"
        )


class FrontmatterError(ValidationError):
    """Raised when YAML frontmatter is invalid or incomplete.

    Attributes:
        path: The note file with invalid frontmatter
        missing_fields: List of required fields that are missing
        invalid_fields: Dict of field names to error messages
    """

    def __init__(
        self,
        path: Path,
        missing_fields: Optional[list[str]] = None,
        invalid_fields: Optional[dict[str, str]] = None,
    ):
        """Initialize frontmatter error with field details.

        Args:
            path: The note file with invalid frontmatter
            missing_fields: List of required fields that are missing
            invalid_fields: Dict mapping field names to error descriptions
        """
        self.path = path
        self.missing_fields = missing_fields or []
        self.invalid_fields = invalid_fields or {}

        errors = []
        if self.missing_fields:
            errors.append(f"Missing fields: {', '.join(self.missing_fields)}")
        if self.invalid_fields:
            field_errors = [
                f"{field}: {error}" for field, error in self.invalid_fields.items()
            ]
            errors.append(f"Invalid fields: {'; '.join(field_errors)}")

        error_msg = f"Invalid frontmatter in {path}"
        if errors:
            error_msg += " - " + "; ".join(errors)

        super().__init__(error_msg)


class ContentStructureError(ValidationError):
    """Raised when note content structure is invalid.

    Examples:
        - Missing required sections (Question, Answer)
        - Missing translations
        - Invalid markdown structure
    """

    pass


class LLMError(VaultError):
    """Base exception for LLM-related errors."""

    pass


class LLMConfigError(LLMError):
    """Raised when LLM configuration is invalid.

    Examples:
        - Missing API key
        - Invalid model name
        - Invalid configuration parameters
    """

    pass


class LLMResponseError(LLMError):
    """Raised when LLM returns an invalid or truncated response.

    Attributes:
        response_excerpt: First 200 chars of the invalid response
        note_path: The note being processed
    """

    def __init__(
        self,
        message: str,
        response_excerpt: Optional[str] = None,
        note_path: Optional[str] = None,
    ):
        """Initialize LLM response error with context.

        Args:
            message: Human-readable error description
            response_excerpt: First 200 chars of invalid response
            note_path: The note being processed (optional)
        """
        self.response_excerpt = response_excerpt
        self.note_path = note_path

        error_msg = message
        if note_path:
            error_msg += f" (note: {note_path})"
        if response_excerpt:
            excerpt = response_excerpt[:200]
            if len(response_excerpt) > 200:
                excerpt += "..."
            error_msg += f"\nResponse excerpt: {excerpt}"

        super().__init__(error_msg)


class LLMTimeoutError(LLMError):
    """Raised when an LLM request times out.

    Attributes:
        timeout_seconds: The timeout duration
        note_path: The note being processed
    """

    def __init__(self, timeout_seconds: float, note_path: str):
        """Initialize timeout error.

        Args:
            timeout_seconds: The timeout duration that was exceeded
            note_path: The note being processed
        """
        self.timeout_seconds = timeout_seconds
        self.note_path = note_path
        super().__init__(
            f"LLM request timed out after {timeout_seconds}s for {note_path}"
        )


class LLMRateLimitError(LLMError):
    """Raised when LLM API rate limit is exceeded.

    Attributes:
        retry_after: Seconds to wait before retrying (if provided by API)
        note_path: The note being processed
    """

    def __init__(
        self, message: str, retry_after: Optional[int] = None, note_path: Optional[str] = None
    ):
        """Initialize rate limit error.

        Args:
            message: Human-readable error description
            retry_after: Seconds to wait before retrying
            note_path: The note being processed (optional)
        """
        self.retry_after = retry_after
        self.note_path = note_path

        error_msg = message
        if note_path:
            error_msg += f" (note: {note_path})"
        if retry_after:
            error_msg += f". Retry after {retry_after} seconds"

        super().__init__(error_msg)


class GraphError(VaultError):
    """Base exception for graph analysis errors."""

    pass


class OrphanNoteError(GraphError):
    """Raised when a note has no incoming or outgoing links.

    Attributes:
        note_path: The orphaned note
    """

    def __init__(self, note_path: str):
        """Initialize orphan note error.

        Args:
            note_path: The path to the orphaned note
        """
        self.note_path = note_path
        super().__init__(
            f"Orphan note detected: {note_path} has no links to or from other notes"
        )


class BrokenLinkError(GraphError):
    """Raised when a link points to a non-existent note.

    Attributes:
        source: The note containing the broken link
        target: The missing note being linked to
    """

    def __init__(self, source: str, target: str):
        """Initialize broken link error.

        Args:
            source: The note containing the broken link
            target: The missing note being linked to
        """
        self.source = source
        self.target = target
        super().__init__(f"Broken link: {source} → {target} (target not found)")
