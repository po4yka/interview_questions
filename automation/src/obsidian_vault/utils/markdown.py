"""
Markdown parsing and manipulation using marko.

This module provides AST-based Markdown parsing and manipulation for
analyzing and transforming note content. Marko provides a fully-featured
CommonMark-compliant parser with extensibility.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import marko
from marko import Markdown
from marko.block import BlockElement, Heading
from marko.inline import Link, RawText


class MarkdownAnalyzer:
    """Analyzer for Markdown content using marko AST."""

    def __init__(self, markdown_text: str | None = None):
        """
        Initialize the Markdown analyzer.

        Args:
            markdown_text: Optional markdown text to analyze
        """
        self.parser = Markdown()
        self.text = markdown_text
        self.ast = self.parser.parse(markdown_text) if markdown_text else None

    def parse(self, markdown_text: str):
        """
        Parse Markdown text and build AST.

        Args:
            markdown_text: Markdown text to parse

        Returns:
            Self for method chaining
        """
        self.text = markdown_text
        self.ast = self.parser.parse(markdown_text)
        return self

    def parse_file(self, file_path: Path):
        """
        Parse Markdown from a file.

        Args:
            file_path: Path to the markdown file

        Returns:
            Self for method chaining
        """
        text = file_path.read_text(encoding="utf-8")
        return self.parse(text)

    def get_headings(self) -> list[dict[str, Any]]:
        """
        Extract all headings from the document.

        Returns:
            List of dictionaries with heading info:
            {
                'level': int (1-6),
                'text': str (heading text),
                'children': list (child elements)
            }

        Example:
            >>> analyzer = MarkdownAnalyzer("# Title\\n## Subtitle")
            >>> headings = analyzer.get_headings()
            >>> print(headings[0]['text'])
            'Title'
        """
        if not self.ast:
            return []

        headings = []
        for element in self._walk_ast(self.ast):
            if isinstance(element, Heading):
                text = self._extract_text(element)
                headings.append({"level": element.level, "text": text, "children": element.children})

        return headings

    def get_links(self) -> list[dict[str, str]]:
        """
        Extract all links from the document.

        Returns:
            List of dictionaries with link info:
            {
                'text': str (link text),
                'url': str (link destination),
                'title': str (optional link title)
            }

        Example:
            >>> analyzer = MarkdownAnalyzer("[Link](https://example.com)")
            >>> links = analyzer.get_links()
            >>> print(links[0]['url'])
            'https://example.com'
        """
        if not self.ast:
            return []

        links = []
        for element in self._walk_ast(self.ast):
            if isinstance(element, Link):
                text = self._extract_text(element)
                links.append({"text": text, "url": element.dest, "title": getattr(element, "title", "")})

        return links

    def get_wikilinks(self) -> list[str]:
        """
        Extract Obsidian-style wikilinks [[link]].

        This extracts both simple [[note]] and aliased [[note|alias]] links.

        Returns:
            List of wikilink targets

        Example:
            >>> analyzer = MarkdownAnalyzer("See [[c-coroutines]] and [[q-kotlin|Kotlin Q&A]]")
            >>> wikilinks = analyzer.get_wikilinks()
            >>> print(wikilinks)
            ['c-coroutines', 'q-kotlin']
        """
        if not self.text:
            return []

        import re

        # Match [[link]] or [[link|alias]]
        pattern = r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]"
        matches = re.findall(pattern, self.text)
        return matches

    def has_heading(self, text: str, level: int | None = None) -> bool:
        """
        Check if document has a specific heading.

        Args:
            text: Heading text to search for
            level: Optional heading level (1-6) to match

        Returns:
            True if heading exists, False otherwise

        Example:
            >>> analyzer = MarkdownAnalyzer("# Question (EN)")
            >>> analyzer.has_heading("Question (EN)")
            True
            >>> analyzer.has_heading("Question (EN)", level=1)
            True
        """
        headings = self.get_headings()
        for heading in headings:
            if heading["text"] == text:
                if level is None or heading["level"] == level:
                    return True
        return False

    def get_text_between_headings(self, start_heading: str, end_heading: str | None = None) -> str:
        """
        Extract text between two headings.

        Args:
            start_heading: Starting heading text
            end_heading: Optional ending heading text (extracts to end if None)

        Returns:
            Text content between headings

        Example:
            >>> md = "# Question\\nWhat is it?\\n# Answer\\nIt is..."
            >>> analyzer = MarkdownAnalyzer(md)
            >>> text = analyzer.get_text_between_headings("Question", "Answer")
            >>> print(text.strip())
            'What is it?'
        """
        if not self.text:
            return ""

        lines = self.text.split("\n")
        headings = self.get_headings()

        start_idx = None
        end_idx = None

        # Find heading positions
        for i, heading in enumerate(headings):
            if heading["text"] == start_heading:
                # Find line number of this heading
                for j, line in enumerate(lines):
                    if line.strip().startswith("#" * heading["level"]) and start_heading in line:
                        start_idx = j + 1
                        break

            if end_heading and heading["text"] == end_heading:
                for j, line in enumerate(lines):
                    if line.strip().startswith("#" * heading["level"]) and end_heading in line:
                        end_idx = j
                        break

        if start_idx is None:
            return ""

        if end_idx is None:
            return "\n".join(lines[start_idx:])

        return "\n".join(lines[start_idx:end_idx])

    def count_code_blocks(self) -> int:
        """
        Count code blocks in the document.

        Returns:
            Number of fenced code blocks

        Example:
            >>> md = "```python\\ncode\\n```\\n\\n```kotlin\\ncode\\n```"
            >>> analyzer = MarkdownAnalyzer(md)
            >>> analyzer.count_code_blocks()
            2
        """
        if not self.text:
            return 0

        import re

        # Count fenced code blocks
        pattern = r"```[\s\S]*?```"
        matches = re.findall(pattern, self.text)
        return len(matches)

    def render(self) -> str:
        """
        Render the AST back to Markdown.

        Returns:
            Rendered Markdown text

        Example:
            >>> analyzer = MarkdownAnalyzer("# Title")
            >>> rendered = analyzer.render()
            >>> print(rendered)
            '# Title'
        """
        if not self.ast:
            return ""

        return self.parser.render(self.ast)

    def _walk_ast(self, node):
        """Walk the AST tree and yield all nodes."""
        yield node
        if hasattr(node, "children") and node.children:
            for child in node.children:
                yield from self._walk_ast(child)

    def _extract_text(self, node) -> str:
        """Extract plain text from a node."""
        if isinstance(node, RawText):
            return node.children

        text_parts = []
        if hasattr(node, "children") and node.children:
            for child in node.children:
                text_parts.append(self._extract_text(child))

        return "".join(text_parts)


# Convenience functions


def parse_markdown(text: str) -> MarkdownAnalyzer:
    """
    Parse Markdown text.

    Args:
        text: Markdown text

    Returns:
        MarkdownAnalyzer instance
    """
    return MarkdownAnalyzer(text)


def parse_markdown_file(file_path: Path) -> MarkdownAnalyzer:
    """
    Parse Markdown from file.

    Args:
        file_path: Path to markdown file

    Returns:
        MarkdownAnalyzer instance
    """
    analyzer = MarkdownAnalyzer()
    return analyzer.parse_file(file_path)


def extract_headings(markdown_text: str) -> list[dict[str, Any]]:
    """
    Extract headings from Markdown text.

    Args:
        markdown_text: Markdown text

    Returns:
        List of heading dictionaries
    """
    analyzer = MarkdownAnalyzer(markdown_text)
    return analyzer.get_headings()


def extract_wikilinks(markdown_text: str) -> list[str]:
    """
    Extract Obsidian-style wikilinks from Markdown text.

    Args:
        markdown_text: Markdown text

    Returns:
        List of wikilink targets
    """
    analyzer = MarkdownAnalyzer(markdown_text)
    return analyzer.get_wikilinks()


def has_required_headings(markdown_text: str, required_headings: list[str]) -> dict[str, bool]:
    """
    Check if Markdown has all required headings.

    Args:
        markdown_text: Markdown text
        required_headings: List of required heading texts

    Returns:
        Dictionary mapping heading text to presence boolean

    Example:
        >>> md = "# Question (EN)\\n## Answer (EN)"
        >>> result = has_required_headings(md, ["Question (EN)", "Answer (EN)", "References"])
        >>> print(result)
        {'Question (EN)': True, 'Answer (EN)': True, 'References': False}
    """
    analyzer = MarkdownAnalyzer(markdown_text)
    return {heading: analyzer.has_heading(heading) for heading in required_headings}
