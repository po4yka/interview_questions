"""Shared configuration and constants for validators."""

from __future__ import annotations

import re

# ============================================================================
# Content Structure Constants
# ============================================================================

# Required headings for different note types
STRUCTURED_REQUIRED_HEADINGS = {
    "qna": [
        "# Вопрос (RU)",
        "# Question (EN)",
        "## Ответ (RU)",
        "## Answer (EN)",
        "## Follow-ups",
        "## References",
        "## Related Questions",
    ],
    "concept": [
        "# Summary (EN)",
        "## Summary (RU)",
    ],
}

# Generic/low-quality follow-up question patterns to detect
GENERIC_FOLLOWUP_PATTERNS = [
    (r"What else\??\s*$", "generic 'What else?'"),
    (r"Tell me more\??", "generic 'Tell me more'"),
    (r"Can you explain\??\s*$", "generic 'Can you explain?'"),
    (r"Anything else\??", "generic 'Anything else?'"),
    (r"What about\?\s*$", "incomplete 'What about?'"),
]

# Recommended follow-up question count ranges
FOLLOWUP_MIN_RECOMMENDED = 3
FOLLOWUP_MAX_RECOMMENDED = 7
FOLLOWUP_IDEAL_RANGE = (3, 5)

# Minimum character length for subsection content
MIN_SUBSECTION_CONTENT_LENGTH = 50

# Minimum character length for follow-up questions
MIN_FOLLOWUP_QUESTION_LENGTH = 20

# ============================================================================
# File Format Constants
# ============================================================================

# Filename pattern for question notes
FILENAME_PATTERN = re.compile(r"^q-[a-z0-9-]+--[a-z0-9-]+--(easy|medium|hard)\.md$")

# Topic to folder mapping
TOPIC_TO_FOLDER_MAPPING = {
    "algorithms": "20-Algorithms",
    "system-design": "30-System-Design",
    "android": "40-Android",
    "backend": "50-Backend",
    "cs": "60-CompSci",
    "kotlin": "70-Kotlin",
    "tools": "80-Tools",
    "behavioral": "00-Behavioural",
}

# Special folder patterns
CONCEPTS_FOLDER = "10-Concepts"
MOCS_FOLDER = "90-MOCs"

# File prefixes
CONCEPT_PREFIX = "c-"
MOC_PREFIX = "moc-"
QUESTION_PREFIX = "q-"

# ============================================================================
# Code Format Constants
# ============================================================================

# Common type names that should be wrapped in backticks
# NOTE: Excludes overly-generic words that have natural language meanings
# (Context, Flow, Coroutine) to prevent oscillation on stylistic issues
COMMON_TYPE_NAMES = [
    # Java/Kotlin primitives and basic types
    "String",
    "Int",
    "Long",
    "Float",
    "Double",
    "Boolean",
    "Char",
    "Byte",
    "Short",
    # Collections
    "List",
    "ArrayList",
    "LinkedList",
    "Set",
    "HashSet",
    "TreeSet",
    "Map",
    "HashMap",
    "TreeMap",
    "LinkedHashMap",
    "Queue",
    "Deque",
    "Stack",
    # Android types (specific classes only, not generic words)
    "Activity",
    "Fragment",
    "View",
    "ViewGroup",
    "Intent",
    "Bundle",
    # "Context",  # REMOVED - too generic, has natural language meaning
    "Application",
    "Service",
    "BroadcastReceiver",
    "ContentProvider",
    "ViewModel",
    "LiveData",
    "MutableLiveData",
    "StateFlow",
    "SharedFlow",
    # "Flow",  # REMOVED - too generic, has natural language meaning
    # "Coroutine",  # REMOVED - too generic, has natural language meaning
    "Parcelable",
    "Serializable",
    # Common patterns
    "Observable",
    "Disposable",
    "Callback",
    "Listener",
]

# Pattern for detecting unescaped generic types (e.g., ArrayList<String>)
UNESCAPED_GENERIC_PATTERN = re.compile(r"(?<!`)(?<!`)\b([A-Z][a-zA-Z0-9]*)<([^>]+)>(?!`)(?!`)")

# ============================================================================
# Link Quality Constants
# ============================================================================

# Recommended range for related links
RELATED_LINKS_MIN_RECOMMENDED = 2
RELATED_LINKS_MAX_RECOMMENDED = 5

# ============================================================================
# System Design Constants
# ============================================================================

# System design answer subsection headings
SYSTEM_DESIGN_SUBSECTIONS = {
    "requirements": {
        "ru": "### Требования",
        "en": "### Requirements",
    },
    "architecture": {
        "ru": "### Архитектура",
        "en": "### Architecture",
    },
}

# Optional question version subsection headings
OPTIONAL_VERSION_SUBSECTIONS = {
    "short": {
        "ru": "## Краткая Версия",
        "en": "## Short Version",
    },
    "detailed": {
        "ru": "## Подробная Версия",
        "en": "## Detailed Version",
    },
}
