"""Validator package exports."""

# Core base classes
from .base import Severity, ValidationIssue, BaseValidator  # noqa: F401

# Registry for validator management
from .registry import ValidatorRegistry  # noqa: F401

# All validators (auto-registered via decorators)
from .yaml_validator import YAMLValidator  # noqa: F401
from .content_validator import ContentValidator  # noqa: F401
from .link_validator import LinkValidator  # noqa: F401
from .format_validator import FormatValidator  # noqa: F401
from .code_format_validator import CodeFormatValidator  # noqa: F401
from .android_validator import AndroidValidator  # noqa: F401
from .system_design_validator import SystemDesignValidator  # noqa: F401

# Shared configuration
from .config import (  # noqa: F401
    STRUCTURED_REQUIRED_HEADINGS,
    FILENAME_PATTERN,
    TOPIC_TO_FOLDER_MAPPING,
    COMMON_TYPE_NAMES,
    SYSTEM_DESIGN_SUBSECTIONS,
    OPTIONAL_VERSION_SUBSECTIONS,
)

__all__ = [
    # Core
    "Severity",
    "ValidationIssue",
    "BaseValidator",
    "ValidatorRegistry",
    # Validators
    "YAMLValidator",
    "ContentValidator",
    "LinkValidator",
    "FormatValidator",
    "CodeFormatValidator",
    "AndroidValidator",
    "SystemDesignValidator",
    # Config
    "STRUCTURED_REQUIRED_HEADINGS",
    "FILENAME_PATTERN",
    "TOPIC_TO_FOLDER_MAPPING",
    "COMMON_TYPE_NAMES",
    "SYSTEM_DESIGN_SUBSECTIONS",
    "OPTIONAL_VERSION_SUBSECTIONS",
]
