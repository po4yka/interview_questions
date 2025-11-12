"""Utility helpers used by validation tooling."""

from .atomic_file import (
    FileWriteError,
    atomic_write,
    locked_read,
)
from .error_context import (
    ErrorContext,
    chain_exceptions,
    error_context,
    format_exception_with_context,
    get_error_summary,
    log_exception_with_context,
    safe_operation,
)
from .common import (
    build_note_index,
    collect_markdown_files,
    collect_validatable_files,
    discover_repo_root,
    dump_yaml,
    ensure_vault_exists,
    listify,
    parse_note,
    safe_resolve_path,
    sanitize_text_for_yaml,
)
from .input_validation import (
    sanitize_filename,
    validate_choice,
    validate_integer,
    validate_path,
    validate_string,
    validate_url,
)
from .frontmatter import (
    FrontmatterHandler,
    dump_frontmatter,
    load_frontmatter,
    load_frontmatter_text,
    update_frontmatter,
)
from .log_sanitizer import (
    is_sensitive_key,
    redact_url_params,
    sanitize_dict,
    sanitize_for_logging,
    sanitize_log_record,
    sanitize_string,
)
from .logging_config import (
    critical,
    debug,
    error,
    get_logger,
    info,
    setup_logging,
    success,
    warning,
)
from .markdown import (
    MarkdownAnalyzer,
    extract_headings,
    extract_wikilinks,
    has_required_headings,
    parse_markdown,
    parse_markdown_file,
)
from .report_generator import FileResult, ReportGenerator
from .taxonomy_loader import TaxonomyLoader
from .yaml_loader import load_yaml

__all__ = [
    # Common utilities
    "discover_repo_root",
    "parse_note",
    "build_note_index",
    "collect_markdown_files",
    "collect_validatable_files",
    "dump_yaml",
    "listify",
    "sanitize_text_for_yaml",
    # Security utilities
    "safe_resolve_path",
    "ensure_vault_exists",
    # Input validation
    "validate_choice",
    "validate_url",
    "validate_integer",
    "validate_path",
    "validate_string",
    "sanitize_filename",
    # Atomic file operations
    "atomic_write",
    "locked_read",
    "FileWriteError",
    # Error context and handling
    "ErrorContext",
    "error_context",
    "safe_operation",
    "format_exception_with_context",
    "log_exception_with_context",
    "get_error_summary",
    "chain_exceptions",
    # YAML loading
    "load_yaml",
    # Frontmatter (robust YAML with order/comment preservation)
    "FrontmatterHandler",
    "load_frontmatter",
    "load_frontmatter_text",
    "dump_frontmatter",
    "update_frontmatter",
    # Logging (loguru-based)
    "setup_logging",
    "get_logger",
    "debug",
    "info",
    "warning",
    "error",
    "critical",
    "success",
    # Log sanitization
    "sanitize_string",
    "sanitize_dict",
    "sanitize_log_record",
    "sanitize_for_logging",
    "is_sensitive_key",
    "redact_url_params",
    # Markdown (AST-based parsing and analysis)
    "MarkdownAnalyzer",
    "parse_markdown",
    "parse_markdown_file",
    "extract_headings",
    "extract_wikilinks",
    "has_required_headings",
    # Taxonomy
    "TaxonomyLoader",
    # Reporting
    "FileResult",
    "ReportGenerator",
]
