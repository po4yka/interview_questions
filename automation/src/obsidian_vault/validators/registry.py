"""Validator registry for automatic validator discovery and instantiation."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, List, Type

from .base import BaseValidator

if TYPE_CHECKING:
    from utils.taxonomy_loader import TaxonomyLoader


class ValidatorRegistry:
    """Registry for managing and instantiating validators."""

    _validators: List[Type[BaseValidator]] = []

    @classmethod
    def register(cls, validator_class: Type[BaseValidator]) -> Type[BaseValidator]:
        """Register a validator class.

        Args:
            validator_class: The validator class to register

        Returns:
            The validator class (for use as a decorator)
        """
        if validator_class not in cls._validators:
            cls._validators.append(validator_class)
        return validator_class

    @classmethod
    def get_all_validators(cls) -> List[Type[BaseValidator]]:
        """Get all registered validator classes.

        Returns:
            List of registered validator classes
        """
        return cls._validators.copy()

    @classmethod
    def create_validators(
        cls,
        *,
        content: str,
        frontmatter: dict,
        path: str,
        taxonomy: "TaxonomyLoader",
        vault_root: Path | None = None,
        note_index: set[str] | None = None,
    ) -> List[BaseValidator]:
        """Create instances of all registered validators.

        Args:
            content: The note body content
            frontmatter: The note's YAML frontmatter
            path: The file path
            taxonomy: The taxonomy loader
            vault_root: The vault root directory (optional, for FormatValidator)
            note_index: Set of all note IDs (optional, for LinkValidator)

        Returns:
            List of instantiated validators
        """
        validators = []

        for validator_class in cls._validators:
            # Check if validator needs vault_root (FormatValidator)
            if validator_class.__name__ == "FormatValidator" and vault_root:
                validator = validator_class(
                    content=content,
                    frontmatter=frontmatter,
                    path=path,
                    taxonomy=taxonomy,
                    vault_root=vault_root,
                )
            # Check if validator needs note_index (LinkValidator uses 'index' parameter)
            elif validator_class.__name__ == "LinkValidator" and note_index:
                validator = validator_class(
                    content=content,
                    frontmatter=frontmatter,
                    path=path,
                    taxonomy=taxonomy,
                    index=note_index,
                )
            else:
                validator = validator_class(
                    content=content,
                    frontmatter=frontmatter,
                    path=path,
                    taxonomy=taxonomy,
                )

            validators.append(validator)

        return validators

    @classmethod
    def clear(cls) -> None:
        """Clear all registered validators. Useful for testing."""
        cls._validators.clear()
