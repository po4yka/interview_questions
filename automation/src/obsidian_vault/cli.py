#!/usr/bin/env python3
"""
Unified CLI for Obsidian Interview Questions vault automation.

Commands:
- vault validate: Comprehensive note validation
- vault normalize: Normalize concept frontmatter
- vault check-translations: Find notes missing translations
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable

from obsidian_vault.utils import (
    discover_repo_root,
    parse_note,
    build_note_index,
    collect_markdown_files,
    collect_validatable_files,
    dump_yaml,
    listify,
    TaxonomyLoader,
    FileResult,
    ReportGenerator,
)
from obsidian_vault.validators import Severity, ValidatorRegistry
import obsidian_vault.validators  # noqa: F401 - triggers auto-registration


# ============================================================================
# Validation Command
# ============================================================================

def cmd_validate(args: argparse.Namespace) -> int:
    """Run comprehensive note validation."""
    repo_root = discover_repo_root()
    vault_dir = repo_root / "InterviewQuestions"

    if not vault_dir.exists():
        print("InterviewQuestions directory not found. Run from repository root.", file=sys.stderr)
        return 1

    targets = _determine_validation_targets(args, repo_root, vault_dir)
    if not targets:
        print("No Markdown notes found for validation.", file=sys.stderr)
        return 1

    taxonomy = TaxonomyLoader(repo_root).load()
    note_index = build_note_index(vault_dir)

    # Choose parallel or sequential processing
    if args.parallel and len(targets) > 1:
        results = _validate_parallel(
            targets,
            repo_root,
            vault_dir,
            taxonomy,
            note_index,
            max_workers=args.workers,
            quiet=args.quiet,
        )
    else:
        results = []
        for file_path in targets:
            result = _validate_single_file(file_path, repo_root, vault_dir, taxonomy, note_index)
            results.append(result)

    # Check for critical issues
    exit_code = 0
    for result in results:
        if any(issue.severity == Severity.CRITICAL for issue in result.issues):
            exit_code = 1
            break

    if args.report:
        report_path = Path(args.report)
        ReportGenerator(results).write_markdown(report_path)

    if args.quiet:
        _print_quiet_summary(results)
    else:
        _print_detailed_results(results)

    return exit_code


def _validate_single_file(
    file_path: Path,
    repo_root: Path,
    vault_dir: Path,
    taxonomy,
    note_index: set[str],
) -> FileResult:
    """Validate a single file and return the result."""
    frontmatter, body = parse_note(file_path)

    validators = ValidatorRegistry.create_validators(
        content=body,
        frontmatter=frontmatter,
        path=str(file_path),
        taxonomy=taxonomy,
        vault_root=vault_dir,
        note_index=note_index,
    )
    issues = []
    passed = []
    for validator in validators:
        summary = validator.validate()
        issues.extend(summary.issues)
        passed.extend(summary.passed)

    return FileResult(
        path=str(file_path.relative_to(repo_root)),
        issues=issues,
        passed=passed,
    )


def _validate_parallel(
    targets: list[Path],
    repo_root: Path,
    vault_dir: Path,
    taxonomy,
    note_index: set[str],
    max_workers: int = 4,
    quiet: bool = False,
) -> list[FileResult]:
    """Validate files in parallel using ThreadPoolExecutor."""
    results: list[FileResult] = []
    total = len(targets)

    if not quiet:
        print(f"Validating {total} files using {max_workers} workers...", file=sys.stderr)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_path = {
            executor.submit(
                _validate_single_file,
                file_path,
                repo_root,
                vault_dir,
                taxonomy,
                note_index,
            ): file_path
            for file_path in targets
        }

        completed = 0
        for future in as_completed(future_to_path):
            file_path = future_to_path[future]
            try:
                result = future.result()
                results.append(result)
                completed += 1

                if not quiet and completed % 50 == 0:
                    print(f"Progress: {completed}/{total} files validated", file=sys.stderr)
            except Exception as e:
                print(f"Error validating {file_path}: {e}", file=sys.stderr)
                completed += 1

    if not quiet:
        print(f"Completed: {completed}/{total} files validated", file=sys.stderr)

    results.sort(key=lambda r: r.path)
    return results


def _determine_validation_targets(args: argparse.Namespace, repo_root: Path, vault_dir: Path) -> list[Path]:
    """Determine which files to validate based on args."""
    if args.all:
        return collect_validatable_files(vault_dir)

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
            if candidate.is_file() and candidate.suffix.lower() == ".md":
                return [candidate.resolve()]
            if candidate.is_dir():
                return collect_validatable_files(candidate)

    print(f"Path not found: {args.path}", file=sys.stderr)
    return []


def _print_detailed_results(results: Iterable[FileResult]) -> None:
    """Print detailed validation results."""
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


def _print_quiet_summary(results: Iterable[FileResult]) -> None:
    """Print quiet summary of validation results."""
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


# ============================================================================
# Normalize Command
# ============================================================================

def cmd_normalize(args: argparse.Namespace) -> int:
    """Normalize concept note frontmatter."""
    repo_root = discover_repo_root()
    vault_dir = repo_root / "InterviewQuestions"
    concept_dir = vault_dir / "10-Concepts"

    if not concept_dir.exists():
        print(f"Concepts directory not found: {concept_dir}", file=sys.stderr)
        return 1

    # Load taxonomy for topic validation and MOC mapping
    taxonomy = TaxonomyLoader(repo_root).load()
    allowed_topics = set(taxonomy.topics.keys()) if taxonomy and taxonomy.topics else set()

    # Build MOC map from taxonomy
    moc_map = _build_moc_map(taxonomy) if taxonomy else {}

    files = sorted(concept_dir.glob("c-*.md"))
    if not files:
        print("No concept files found.", file=sys.stderr)
        return 0

    updated = 0
    for path in files:
        if _normalize_concept_file(path, allowed_topics, moc_map, args.dry_run):
            updated += 1

    action = "Would update" if args.dry_run else "Updated"
    print(f"{action} {updated} concept notes out of {len(files)}")
    return 0


def _normalize_concept_file(
    path: Path,
    allowed_topics: set[str],
    moc_map: dict[str, str],
    dry_run: bool = False,
) -> bool:
    """Normalize a single concept file. Returns True if updated."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return False

    try:
        header, body = text.split("\n---\n", 1)
    except ValueError:
        return False

    frontmatter = parse_note(path)[0]

    # Extract and normalize fields
    tags = [t for t in listify(frontmatter.get("tags")) if t]

    # Topic inference and validation
    topic = frontmatter.get("topic")
    if topic not in allowed_topics:
        topic = None
    if topic is None:
        for tag in tags:
            candidate = tag.split("/")[-1]
            if candidate in allowed_topics:
                topic = candidate
                break
    if topic is None:
        topic = "cs"

    # Subtopics
    subtopics = [s for s in listify(frontmatter.get("subtopics")) if s]
    if not subtopics:
        for tag in tags:
            candidate = tag.split("/")[-1]
            if candidate not in {topic, "concept"}:
                subtopics.append(candidate)
    if not subtopics:
        subtopics = ["fundamentals"]
    subtopics = list(dict.fromkeys(subtopics))[:3]

    # Other fields with defaults
    question_kind = frontmatter.get("question_kind")
    if question_kind not in {"theory", "coding", "system-design", "android"}:
        question_kind = "theory"

    difficulty = frontmatter.get("difficulty")
    if difficulty not in {"easy", "medium", "hard"}:
        difficulty = "medium"

    original_language = frontmatter.get("original_language")
    if original_language not in {"en", "ru"}:
        original_language = "en"

    language_tags = listify(frontmatter.get("language_tags")) or ["en", "ru"]

    status = frontmatter.get("status")
    if status not in {"draft", "reviewed", "ready", "retired"}:
        status = "draft"

    sources = frontmatter.get("sources")
    normalized_sources = sources if isinstance(sources, list) else []

    related = frontmatter.get("related")
    normalized_related = related if isinstance(related, list) else []

    moc = moc_map.get(topic, "moc-cs")

    # ID normalization
    note_id = _normalize_id(frontmatter)

    # Dates
    created = _normalize_date(frontmatter.get("created"))
    updated_date = _normalize_date(frontmatter.get("updated")) or created

    aliases = listify(frontmatter.get("aliases"))

    # Tags cleanup
    if "concept" not in tags:
        tags.insert(0, "concept")
    diff_tag = f"difficulty/{difficulty}"
    if diff_tag not in tags:
        tags.append(diff_tag)
    tags = list(dict.fromkeys(tags))[:8]

    # Build ordered frontmatter
    ordered = {
        "id": note_id,
        "title": frontmatter.get("title", ""),
        "aliases": aliases,
        "summary": frontmatter.get("summary", ""),
        "topic": topic,
        "subtopics": subtopics,
        "question_kind": question_kind,
        "difficulty": difficulty,
        "original_language": original_language,
        "language_tags": language_tags,
        "sources": normalized_sources,
        "status": status,
        "moc": moc,
        "related": normalized_related,
        "created": created,
        "updated": updated_date,
        "tags": tags,
    }

    yaml_text = dump_yaml(ordered)
    new_text = "---\n" + yaml_text + "---\n" + body

    if new_text != text:
        if not dry_run:
            path.write_text(new_text, encoding="utf-8")
        return True
    return False


def _build_moc_map(taxonomy) -> dict[str, str]:
    """Build topic -> MOC mapping from taxonomy."""
    # Fallback hardcoded map in case taxonomy doesn't provide it
    default_map = {
        "algorithms": "moc-algorithms",
        "data-structures": "moc-algorithms",
        "system-design": "moc-system-design",
        "android": "moc-android",
        "kotlin": "moc-kotlin",
        "programming-languages": "moc-cs",
        "architecture-patterns": "moc-architecture-patterns",
        "concurrency": "moc-cs",
        "distributed-systems": "moc-system-design",
        "databases": "moc-backend",
        "networking": "moc-system-design",
        "operating-systems": "moc-cs",
        "security": "moc-security",
        "performance": "moc-performance",
        "cloud": "moc-cloud",
        "testing": "moc-testing",
        "devops-ci-cd": "moc-devops",
        "tools": "moc-tools",
        "debugging": "moc-tools",
        "ui-ux-accessibility": "moc-android",
        "behavioral": "moc-cs",
        "cs": "moc-cs",
    }

    # Could enhance TaxonomyLoader to provide MOC mapping in the future
    return default_map


def _normalize_id(frontmatter: dict) -> str:
    """Normalize note ID from frontmatter."""
    ID_PATTERN = re.compile(r"^(\d{8}-\d{6})$")

    raw_id = frontmatter.get("id")
    if isinstance(raw_id, str):
        candidate = raw_id
        if raw_id.startswith("ivc-"):
            candidate = raw_id[4:]
        elif raw_id.startswith("iv-"):
            candidate = raw_id[3:]
        if ID_PATTERN.match(candidate):
            return candidate

    # Fallback to created date or current timestamp
    created_raw = frontmatter.get("created")
    if isinstance(created_raw, str) and re.match(r"\d{4}-\d{2}-\d{2}", created_raw):
        return created_raw.replace("-", "") + "-000000"

    return dt.datetime.now().strftime("%Y%m%d-%H%M%S")


def _normalize_date(value) -> str:
    """Normalize date value to YYYY-MM-DD format."""
    if value is None or value == "":
        return "2025-01-01"
    if isinstance(value, dt.date):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, str):
        return value
    return str(value)


# ============================================================================
# Check Translations Command
# ============================================================================

def cmd_check_translations(args: argparse.Namespace) -> int:
    """Find notes missing Russian or English translations."""
    repo_root = discover_repo_root()
    vault_dir = repo_root / "InterviewQuestions"

    if not vault_dir.exists():
        print("InterviewQuestions directory not found.", file=sys.stderr)
        return 1

    note_files = list(vault_dir.glob("**/q-*.md"))
    if not note_files:
        print("No question notes found.", file=sys.stderr)
        return 0

    missing = []
    for path in note_files:
        text = path.read_text(encoding="utf-8")
        has_ru_answer = "## Ответ (RU)" in text
        has_en_answer = "## Answer (EN)" in text
        if not has_ru_answer or not has_en_answer:
            missing.append(str(path.relative_to(repo_root)))

    if args.output:
        output_path = Path(args.output)
        output_path.write_text("\n".join(missing), encoding="utf-8")
        print(f"Wrote {len(missing)} entries to {output_path}")
    else:
        if missing:
            print(f"Found {len(missing)} notes missing translations:\n")
            for path in missing:
                print(f"  - {path}")
        else:
            print("All notes have both EN and RU translations.")

    return 0


# ============================================================================
# Main CLI
# ============================================================================

def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="vault",
        description="Obsidian Interview Questions vault automation",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate notes for structure, format, and quality",
    )
    validate_parser.add_argument(
        "path",
        nargs="?",
        help="File or directory to validate (relative to vault root or InterviewQuestions/)",
    )
    validate_parser.add_argument(
        "--all",
        action="store_true",
        help="Validate all notes in InterviewQuestions/",
    )
    validate_parser.add_argument(
        "--report",
        type=str,
        help="Optional path to write a markdown validation report",
    )
    validate_parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only print summary (suitable for CI)",
    )
    validate_parser.add_argument(
        "--parallel",
        action="store_true",
        help="Use parallel processing for faster validation",
    )
    validate_parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of worker threads for parallel processing (default: 4)",
    )

    # Normalize command
    normalize_parser = subparsers.add_parser(
        "normalize",
        help="Normalize concept note frontmatter",
    )
    normalize_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes",
    )

    # Check translations command
    check_parser = subparsers.add_parser(
        "check-translations",
        help="Find notes missing Russian or English translations",
    )
    check_parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Write results to file (default: print to stdout)",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "validate":
        return cmd_validate(args)
    elif args.command == "normalize":
        return cmd_normalize(args)
    elif args.command == "check-translations":
        return cmd_check_translations(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
