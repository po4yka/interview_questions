"""
Robust frontmatter handling with order and comment preservation.

This module uses python-frontmatter and ruamel.yaml to provide:
- Clean extraction/insertion of YAML frontmatter blocks
- Preservation of field order in YAML
- Preservation of comments in frontmatter
- Round-trip safe reading and writing

This is crucial for Obsidian vault maintenance where metadata readability
and user comments are important.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import frontmatter
from ruamel.yaml import YAML


class FrontmatterHandler:
    """Handler for reading and writing frontmatter with preservation."""

    def __init__(self):
        """Initialize the frontmatter handler with ruamel.yaml configuration."""
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.default_flow_style = False
        self.yaml.width = 4096  # Prevent line wrapping
        self.yaml.indent(mapping=2, sequence=2, offset=0)

    def load(self, file_path: Path) -> tuple[dict[str, Any], str]:
        """
        Load a markdown file and extract frontmatter and content.

        Args:
            file_path: Path to the markdown file

        Returns:
            Tuple of (frontmatter dict, content body)

        Example:
            >>> handler = FrontmatterHandler()
            >>> fm, content = handler.load(Path("note.md"))
            >>> print(fm['title'])
            >>> print(content)
        """
        with open(file_path, "r", encoding="utf-8") as f:
            post = frontmatter.load(f, handler=self._get_yaml_handler())

        return dict(post.metadata), post.content

    def load_from_text(self, text: str) -> tuple[dict[str, Any], str]:
        """
        Load frontmatter and content from markdown text.

        Args:
            text: Markdown text with frontmatter

        Returns:
            Tuple of (frontmatter dict, content body)

        Example:
            >>> handler = FrontmatterHandler()
            >>> text = "---\\ntitle: Test\\n---\\nContent"
            >>> fm, content = handler.load_from_text(text)
        """
        post = frontmatter.loads(text, handler=self._get_yaml_handler())
        return dict(post.metadata), post.content

    def dump(
        self,
        frontmatter_data: dict[str, Any],
        content: str,
        file_path: Path | None = None,
    ) -> str:
        """
        Create markdown with frontmatter from data and content.

        Args:
            frontmatter_data: Dictionary of frontmatter fields
            content: Markdown content body
            file_path: Optional path to write the file to

        Returns:
            Complete markdown text with frontmatter

        Example:
            >>> handler = FrontmatterHandler()
            >>> markdown = handler.dump(
            ...     {"title": "Test", "tags": ["tag1", "tag2"]},
            ...     "# Content\\n\\nBody text"
            ... )
            >>> print(markdown)
        """
        post = frontmatter.Post(content, handler=self._get_yaml_handler(), **frontmatter_data)
        text = frontmatter.dumps(post, handler=self._get_yaml_handler())

        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)

        return text

    def update(
        self,
        file_path: Path,
        updates: dict[str, Any],
        remove_keys: list[str] | None = None,
    ) -> None:
        """
        Update frontmatter fields in a file while preserving order and comments.

        Args:
            file_path: Path to the markdown file
            updates: Dictionary of fields to add or update
            remove_keys: Optional list of keys to remove

        Example:
            >>> handler = FrontmatterHandler()
            >>> handler.update(
            ...     Path("note.md"),
            ...     {"status": "reviewed", "updated": "2025-01-08"},
            ...     remove_keys=["draft"]
            ... )
        """
        fm, content = self.load(file_path)

        # Apply updates
        for key, value in updates.items():
            fm[key] = value

        # Remove keys if specified
        if remove_keys:
            for key in remove_keys:
                fm.pop(key, None)

        # Write back
        self.dump(fm, content, file_path)

    def _get_yaml_handler(self):
        """Get a frontmatter YAMLHandler configured with ruamel.yaml."""
        from frontmatter import YAMLHandler

        # Create a custom handler that uses our configured ruamel.yaml instance
        class RuamelYAMLHandler(YAMLHandler):
            def __init__(self, yaml_instance):
                self.yaml = yaml_instance

            def load(self, fm, **kwargs):
                return self.yaml.load(fm)

            def export(self, metadata, **kwargs):
                from io import StringIO

                stream = StringIO()
                self.yaml.dump(metadata, stream)
                return stream.getvalue()

        return RuamelYAMLHandler(self.yaml)


# Convenience functions for backward compatibility
_default_handler = FrontmatterHandler()


def load_frontmatter(file_path: Path) -> tuple[dict[str, Any], str]:
    """
    Load frontmatter and content from a markdown file.

    Args:
        file_path: Path to the markdown file

    Returns:
        Tuple of (frontmatter dict, content body)
    """
    return _default_handler.load(file_path)


def load_frontmatter_text(text: str) -> tuple[dict[str, Any], str]:
    """
    Load frontmatter and content from markdown text.

    Args:
        text: Markdown text with frontmatter

    Returns:
        Tuple of (frontmatter dict, content body)
    """
    return _default_handler.load_from_text(text)


def dump_frontmatter(
    frontmatter_data: dict[str, Any],
    content: str,
    file_path: Path | None = None,
) -> str:
    """
    Create markdown with frontmatter.

    Args:
        frontmatter_data: Dictionary of frontmatter fields
        content: Markdown content body
        file_path: Optional path to write the file to

    Returns:
        Complete markdown text with frontmatter
    """
    return _default_handler.dump(frontmatter_data, content, file_path)


def update_frontmatter(
    file_path: Path,
    updates: dict[str, Any],
    remove_keys: list[str] | None = None,
) -> None:
    """
    Update frontmatter fields while preserving order and comments.

    Args:
        file_path: Path to the markdown file
        updates: Dictionary of fields to add or update
        remove_keys: Optional list of keys to remove
    """
    _default_handler.update(file_path, updates, remove_keys)


# For compatibility with existing code that uses parse_note
def parse_note_frontmatter(file_path: Path) -> tuple[dict[str, Any], str]:
    """
    Parse a markdown note file into frontmatter and body.

    This is a compatibility wrapper for the existing parse_note function.

    Args:
        file_path: Path to the markdown file

    Returns:
        Tuple of (frontmatter dict, body text)
    """
    return load_frontmatter(file_path)
