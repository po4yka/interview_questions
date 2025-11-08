"""Common utilities shared across scripts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Tuple


def discover_repo_root() -> Path:
    """
    Best-effort discovery of the vault repository root.

    Searches from the current file location upwards and from cwd upwards
    until it finds a directory containing 'InterviewQuestions'.

    Returns:
        Path to the repository root.
    """
    search_points = [
        Path(__file__).resolve(),
        *Path(__file__).resolve().parents,
        Path.cwd(),
        *Path.cwd().parents,
    ]
    for candidate in search_points:
        base = candidate if candidate.is_dir() else candidate.parent
        if (base / "InterviewQuestions").exists():
            return base
    return Path.cwd()


def parse_note(path: Path) -> Tuple[dict, str]:
    """
    Parse a markdown note into frontmatter and body.

    Args:
        path: Path to the markdown file

    Returns:
        Tuple of (frontmatter dict, body text)
    """
    from obsidian_vault.utils.yaml_loader import load_yaml

    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text

    lines = text.splitlines()
    try:
        end = lines[1:].index("---") + 1
    except ValueError:
        return {}, text

    frontmatter_text = "\n".join(lines[1:end])
    body = "\n".join(lines[end + 1:])
    frontmatter = load_yaml(frontmatter_text)
    return frontmatter or {}, body


def build_note_index(vault_dir: Path) -> set[str]:
    """
    Build an index of all markdown note filenames in the vault.

    Args:
        vault_dir: Path to the vault directory

    Returns:
        Set of note filenames
    """
    return {path.name for path in vault_dir.rglob("*.md")}


def collect_markdown_files(path: Path, pattern: str = "*.md") -> list[Path]:
    """
    Collect markdown files from a path (file or directory).

    Args:
        path: File or directory path
        pattern: Glob pattern for files (default: "*.md")

    Returns:
        List of markdown file paths
    """
    if path.is_file() and path.suffix.lower() == ".md":
        return [path.resolve()]
    if path.is_dir():
        return sorted(path.rglob(pattern))
    return []


def collect_validatable_files(root: Path) -> list[Path]:
    """
    Collect validatable markdown files from vault, excluding templates and system folders.

    Args:
        root: Vault root directory

    Returns:
        List of markdown file paths to validate
    """
    allowed_prefixes = {
        "10-Concepts",
        "20-Algorithms",
        "30-System-Design",
        "40-Android",
        "50-Backend",
        "60-CompSci",
        "70-Kotlin",
        "80-Tools",
    }
    excluded_prefixes = {
        "_templates",
        ".obsidian",
        "validators",
        "utils",
    }

    # Check if root is already a specific folder (e.g., "40-Android")
    root_name = root.name
    is_specific_folder = root_name in allowed_prefixes

    result: list[Path] = []
    for candidate in root.rglob("*.md"):
        relative_parts = candidate.relative_to(root).parts
        if not relative_parts:
            continue
        first = relative_parts[0]

        # Skip loose files at vault root, but include if we're in a specific folder
        if len(relative_parts) == 1 and not is_specific_folder:
            continue

        if first in excluded_prefixes:
            continue
        if allowed_prefixes and first not in allowed_prefixes and not is_specific_folder:
            continue
        result.append(candidate.resolve())
    return sorted(result)


def dump_yaml(data: dict) -> str:
    """
    Dump a dictionary to YAML format with specific formatting.

    This custom dumper ensures consistent formatting for vault frontmatter:
    - Inline arrays for simple lists
    - Proper quoting with json.dumps
    - Consistent field ordering

    Args:
        data: Dictionary to serialize

    Returns:
        YAML-formatted string
    """
    def format_scalar(value):
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return str(value)
        return json.dumps(str(value), ensure_ascii=False)

    lines = []
    for key, value in data.items():
        if isinstance(value, list):
            if not value:
                lines.append(f"{key}: []")
            elif all(isinstance(item, (str, int, float, bool)) or item is None for item in value):
                rendered = ", ".join(format_scalar(item) for item in value)
                lines.append(f"{key}: [{rendered}]")
            else:
                lines.append(f"{key}:")
                for item in value:
                    if isinstance(item, dict):
                        lines.append("  -")
                        for subkey, subval in item.items():
                            lines.append(f"    {subkey}: {format_scalar(subval)}")
                    else:
                        lines.append(f"  - {format_scalar(item)}")
        elif isinstance(value, dict):
            lines.append(f"{key}:")
            for subkey, subval in value.items():
                lines.append(f"  {subkey}: {format_scalar(subval)}")
        else:
            lines.append(f"{key}: {format_scalar(value)}")
    return "\n".join(lines) + "\n"


def listify(value) -> list[str]:
    """
    Convert a value to a list of strings.

    Args:
        value: None, string, or list

    Returns:
        List of strings
    """
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]
