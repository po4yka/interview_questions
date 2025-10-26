#!/usr/bin/env python3
"""Validation tooling for the Obsidian Interview Vault."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, List, Tuple

def _discover_repo_root() -> Path:
    """Best-effort discovery of the vault root."""

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


ROOT = _discover_repo_root()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from validators.android_validator import AndroidValidator  # type: ignore
from validators.content_validator import ContentValidator  # type: ignore
from validators.format_validator import FormatValidator  # type: ignore
from validators.link_validator import LinkValidator  # type: ignore
from validators.yaml_validator import YAMLValidator  # type: ignore
from validators.base import Severity  # type: ignore
from utils.report_generator import FileResult, ReportGenerator
from utils.taxonomy_loader import TaxonomyLoader
from utils.yaml_loader import load_yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate Obsidian notes for the Interview Questions vault.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        help="File or directory to validate (relative to vault root or InterviewQuestions/).",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Validate all notes in InterviewQuestions/.",
    )
    parser.add_argument(
        "--report",
        type=str,
        help="Optional path to write a markdown validation report.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only print summary (suitable for CI).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = ROOT
    vault_dir = repo_root / "InterviewQuestions"

    if not vault_dir.exists():
        print("InterviewQuestions directory not found. Run from repository root.", file=sys.stderr)
        return 1

    targets = determine_targets(args, repo_root, vault_dir)
    if not targets:
        print("No Markdown notes found for validation.", file=sys.stderr)
        return 1

    taxonomy = TaxonomyLoader(repo_root).load()
    note_index = build_note_index(vault_dir)

    results: List[FileResult] = []
    exit_code = 0

    for file_path in targets:
        frontmatter, body = parse_note(file_path)
        validators = [
            YAMLValidator(content=body, frontmatter=frontmatter, path=str(file_path), taxonomy=taxonomy),
            ContentValidator(content=body, frontmatter=frontmatter, path=str(file_path), taxonomy=taxonomy),
            LinkValidator(
                content=body,
                frontmatter=frontmatter,
                path=str(file_path),
                taxonomy=taxonomy,
                index=note_index,
            ),
            FormatValidator(
                content=body,
                frontmatter=frontmatter,
                path=str(file_path),
                taxonomy=taxonomy,
                vault_root=vault_dir,
            ),
            AndroidValidator(content=body, frontmatter=frontmatter, path=str(file_path), taxonomy=taxonomy),
        ]
        issues = []
        passed = []
        for validator in validators:
            summary = validator.validate()
            issues.extend(summary.issues)
            passed.extend(summary.passed)
        results.append(
            FileResult(
                path=str(file_path.relative_to(repo_root)),
                issues=issues,
                passed=passed,
            )
        )
        if any(issue.severity == Severity.CRITICAL for issue in issues):
            exit_code = 1

    if args.report:
        report_path = Path(args.report)
        ReportGenerator(results).write_markdown(report_path)

    if args.quiet:
        print_quiet_summary(results)
    else:
        print_detailed_results(results)

    return exit_code


def determine_targets(args: argparse.Namespace, repo_root: Path, vault_dir: Path) -> List[Path]:
    if args.all:
        return sorted(vault_dir.rglob("*.md"))

    if not args.path:
        print("Either provide a path or use --all", file=sys.stderr)
        return []

    explicit = Path(args.path)
    candidates = [
        explicit,
        repo_root / args.path,
        vault_dir / args.path,
    ]
    for candidate in candidates:
        if candidate.exists():
            return collect_markdown_files(candidate)

    print(f"Path not found: {args.path}", file=sys.stderr)
    return []


def collect_markdown_files(path: Path) -> List[Path]:
    if path.is_file() and path.suffix.lower() == ".md":
        return [path.resolve()]
    if path.is_dir():
        return sorted([p.resolve() for p in path.rglob("*.md")])
    return []


def parse_note(path: Path) -> Tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines()
    try:
        end = lines[1:].index("---") + 1
    except ValueError:
        return {}, text
    frontmatter_text = "\n".join(lines[1:end])
    body = "\n".join(lines[end + 1 :])
    frontmatter = load_yaml(frontmatter_text)
    return frontmatter, body


def build_note_index(vault_dir: Path) -> set[str]:
    return {path.name for path in vault_dir.rglob("*.md")}


def print_detailed_results(results: Iterable[FileResult]) -> None:
    for result in results:
        print("=" * 80)
        print(f"Validation Report: {result.path}")
        print("=" * 80)
        if result.issues:
            severity_counts = Counter(issue.severity.value for issue in result.issues)
            overall = ", ".join(f"{k}: {v}" for k, v in sorted(severity_counts.items()))
            print(f"Issues detected ({overall})")
            print("-" * 80)
            for issue in result.issues:
                context = f" [field: {issue.field}]" if issue.field else ""
                print(f"- {issue.severity.value}: {issue.message}{context}")
            print("")
        else:
            print("No issues found.")
        if result.passed:
            print("Passed checks:")
            for item in result.passed:
                print(f"+ {item}")
        print("")


def print_quiet_summary(results: Iterable[FileResult]) -> None:
    total_files = 0
    severity_counter = Counter()
    for result in results:
        total_files += 1
        for issue in result.issues:
            severity_counter[issue.severity.value] += 1
    print(f"Validated {total_files} files.")
    if severity_counter:
        summary = ", ".join(f"{k}: {v}" for k, v in sorted(severity_counter.items()))
        print(f"Issues -> {summary}")
    else:
        print("No issues detected.")


if __name__ == "__main__":
    sys.exit(main())
