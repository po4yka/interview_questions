"""Utility helpers used by validation tooling."""

from .common import (
    build_note_index,
    collect_markdown_files,
    collect_validatable_files,
    discover_repo_root,
    dump_yaml,
    listify,
    parse_note,
)
from .frontmatter import (
    FrontmatterHandler,
    dump_frontmatter,
    load_frontmatter,
    load_frontmatter_text,
    update_frontmatter,
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
    # YAML loading
    "load_yaml",
    # Frontmatter (robust YAML with order/comment preservation)
    "FrontmatterHandler",
    "load_frontmatter",
    "load_frontmatter_text",
    "dump_frontmatter",
    "update_frontmatter",
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
