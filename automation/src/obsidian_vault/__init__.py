"""Obsidian Interview Questions Vault - Automation Tools.

This package provides comprehensive automation for maintaining an Obsidian vault
of interview questions with bilingual content (English/Russian).

Modules:
- validators: Comprehensive validation framework for note structure and quality
- utils: Utility helpers for YAML loading, taxonomy management, and reporting
- cli: Unified command-line interface with subcommands

Use the 'vault' CLI tool with subcommands:
- vault validate: Comprehensive note validation
- vault normalize: Normalize concept frontmatter
- vault check-translations: Find missing translations
"""

__version__ = "0.3.0"

__all__ = ["validators", "utils", "cli"]
