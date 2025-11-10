#!/usr/bin/env python3
"""
Unified CLI for Obsidian Interview Questions vault automation.

Commands:
- vault validate: Comprehensive note validation
- vault normalize: Normalize concept frontmatter
- vault check-translations: Find notes missing translations
- vault graph-stats: Display vault network statistics
- vault orphans: Find orphaned notes (no links)
- vault broken-links: Find notes with broken links
- vault link-report: Generate comprehensive link health report
- vault graph-export: Export vault graph to various formats
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from collections import Counter
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import obsidian_vault.validators  # noqa: F401 - triggers auto-registration
from obsidian_vault.utils import (
    FileResult,
    ReportGenerator,
    TaxonomyLoader,
    build_note_index,
    collect_validatable_files,
    discover_repo_root,
    dump_yaml,
    listify,
    parse_note,
)
from obsidian_vault.utils.graph_analytics import VaultGraph, generate_link_health_report
from obsidian_vault.validators import Severity, ValidatorRegistry


def cmd_validate(args: argparse.Namespace) -> int:
    """Run comprehensive note validation."""
    from obsidian_vault.utils import ensure_vault_exists

    repo_root = discover_repo_root()

    try:
        vault_dir = ensure_vault_exists(repo_root)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    targets = _determine_validation_targets(args, repo_root, vault_dir)
    if not targets:
        print("No Markdown notes found for validation.", file=sys.stderr)
        return 1

    taxonomy = TaxonomyLoader(repo_root).load()
    note_index = build_note_index(vault_dir)

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


def _determine_validation_targets(
    args: argparse.Namespace, repo_root: Path, vault_dir: Path
) -> list[Path]:
    """Determine which files to validate based on args."""
    from obsidian_vault.utils import safe_resolve_path

    if args.all:
        return collect_validatable_files(vault_dir)

    if not args.path:
        print("Either provide a path or use --all", file=sys.stderr)
        return []

    try:
        safe_path = safe_resolve_path(args.path, vault_dir)
    except ValueError:
        try:
            safe_path = safe_resolve_path(args.path, repo_root)
        except ValueError as e:
            print(
                f"Invalid path: {e}\n\n"
                f"Valid path examples:\n"
                f"  - InterviewQuestions/40-Android\n"
                f"  - 40-Android/q-compose-state--android--medium.md\n"
                f"  - Or use --all to validate entire vault",
                file=sys.stderr
            )
            return []

    if not safe_path.exists():
        print(
            f"Path not found: {args.path}\n\n"
            f"Valid path examples:\n"
            f"  - InterviewQuestions/40-Android\n"
            f"  - 40-Android/q-compose-state--android--medium.md\n"
            f"  - Or use --all to validate entire vault",
            file=sys.stderr
        )
        return []

    if safe_path.is_file() and safe_path.suffix.lower() == ".md":
        return [safe_path]
    if safe_path.is_dir():
        return collect_validatable_files(safe_path)

    print(f"Invalid path: {args.path} is not a markdown file or directory", file=sys.stderr)
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

    taxonomy = TaxonomyLoader(repo_root).load()
    allowed_topics = set(taxonomy.topics.keys()) if taxonomy and taxonomy.topics else set()

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

    tags = [t for t in listify(frontmatter.get("tags")) if t]

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

    subtopics = [s for s in listify(frontmatter.get("subtopics")) if s]
    if not subtopics:
        for tag in tags:
            candidate = tag.split("/")[-1]
            if candidate not in {topic, "concept"}:
                subtopics.append(candidate)
    if not subtopics:
        subtopics = ["fundamentals"]
    subtopics = list(dict.fromkeys(subtopics))[:3]

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

    note_id = _normalize_id(frontmatter)

    created = _normalize_date(frontmatter.get("created"))
    updated_date = _normalize_date(frontmatter.get("updated")) or created

    aliases = listify(frontmatter.get("aliases"))

    if "concept" not in tags:
        tags.insert(0, "concept")
    diff_tag = f"difficulty/{difficulty}"
    if diff_tag not in tags:
        tags.append(diff_tag)
    tags = list(dict.fromkeys(tags))[:8]

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

    return default_map


def _normalize_id(frontmatter: dict) -> str:
    """Normalize note ID from frontmatter."""
    id_pattern = re.compile(r"^(\d{8}-\d{6})$")
    raw_id = frontmatter.get("id")
    if isinstance(raw_id, str):
        candidate = raw_id
        if raw_id.startswith("ivc-"):
            candidate = raw_id[4:]
        elif raw_id.startswith("iv-"):
            candidate = raw_id[3:]
        if id_pattern.match(candidate):
            return candidate

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
    from obsidian_vault.utils import ensure_vault_exists

    repo_root = discover_repo_root()

    try:
        vault_dir = ensure_vault_exists(repo_root)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
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


def cmd_graph_stats(args: argparse.Namespace) -> int:
    """Display vault network statistics."""
    from obsidian_vault.utils import ensure_vault_exists

    repo_root = discover_repo_root()

    try:
        vault_dir = ensure_vault_exists(repo_root)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    try:
        vg = VaultGraph(vault_dir)
        stats = vg.get_network_statistics()
        quality = vg.analyze_link_quality()

        print("=" * 80)
        print("Vault Network Statistics")
        print("=" * 80)
        print(f"\nBasic Metrics:")
        print(f"  Total Notes:          {stats['total_notes']}")
        print(f"  Total Links:          {stats['total_links']}")
        print(f"  Average Degree:       {stats['average_degree']:.2f}")
        print(f"  Network Density:      {stats['density']:.4f}")
        print(f"  Connected Components: {stats['connected_components']}")

        print(f"\nLink Quality:")
        print(f"  Reciprocal Links:     {quality['reciprocal_links']}")
        print(f"  Unidirectional Links: {quality['unidirectional_links']}")
        print(f"  Orphaned Notes:       {stats['orphaned_notes']} ({quality['orphaned_ratio']:.1%})")
        print(f"  Isolated Notes:       {stats['isolated_notes']} ({quality['isolated_ratio']:.1%})")

        if args.hubs:
            hubs = vg.get_hub_notes(args.hubs)
            if hubs:
                print(f"\nTop {args.hubs} Hub Notes (Most Outgoing Links):")
                for note, degree in hubs:
                    print(f"  {note}: {degree} outgoing")

        if args.authorities:
            authorities = vg.get_authority_notes(args.authorities)
            if authorities:
                print(f"\nTop {args.authorities} Authority Notes (Most Incoming Links):")
                for note, degree in authorities:
                    print(f"  {note}: {degree} incoming")

        print()
        return 0

    except Exception as e:
        print(f"Error analyzing vault graph: {e}", file=sys.stderr)
        return 1


def cmd_orphans(args: argparse.Namespace) -> int:
    """Find orphaned notes (no incoming or outgoing links)."""
    from obsidian_vault.utils import ensure_vault_exists

    repo_root = discover_repo_root()

    try:
        vault_dir = ensure_vault_exists(repo_root)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    try:
        vg = VaultGraph(vault_dir)
        orphans = vg.get_orphaned_notes()

        if not orphans:
            print("No orphaned notes found. All notes have at least one link!")
            return 0

        print(f"Found {len(orphans)} orphaned notes (no incoming or outgoing links):\n")
        for note in orphans:
            print(f"  - {note}")

        if args.output:
            output_path = Path(args.output)
            output_path.write_text("\n".join(orphans), encoding="utf-8")
            print(f"\nWrote {len(orphans)} orphaned notes to {output_path}")

        return 0

    except Exception as e:
        print(f"Error finding orphaned notes: {e}", file=sys.stderr)
        return 1


def cmd_broken_links(args: argparse.Namespace) -> int:
    """Find notes with broken links (links to non-existent notes)."""
    from obsidian_vault.utils import ensure_vault_exists

    repo_root = discover_repo_root()

    try:
        vault_dir = ensure_vault_exists(repo_root)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    try:
        vg = VaultGraph(vault_dir)
        broken = vg.get_broken_links()

        if not broken:
            print("No broken links found. All links point to existing notes!")
            return 0

        total_broken = sum(len(targets) for targets in broken.values())
        print(f"Found {len(broken)} notes with {total_broken} broken links:\n")

        for source, targets in sorted(broken.items()):
            print(f"  {source}:")
            for target in targets:
                print(f"    → {target} (missing)")

        if args.output:
            output_path = Path(args.output)
            lines = []
            for source, targets in sorted(broken.items()):
                lines.append(f"{source}:")
                for target in targets:
                    lines.append(f"  - {target}")
            output_path.write_text("\n".join(lines), encoding="utf-8")
            print(f"\nWrote broken links report to {output_path}")

        return 1 if broken else 0

    except Exception as e:
        print(f"Error finding broken links: {e}", file=sys.stderr)
        return 1


def cmd_link_report(args: argparse.Namespace) -> int:
    """Generate comprehensive link health report."""
    from obsidian_vault.utils import ensure_vault_exists

    repo_root = discover_repo_root()

    try:
        vault_dir = ensure_vault_exists(repo_root)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    try:
        report = generate_link_health_report(vault_dir)

        if args.output:
            output_path = Path(args.output)
            output_path.write_text(report, encoding="utf-8")
            print(f"Link health report written to {output_path}")
        else:
            print(report)

        return 0

    except Exception as e:
        print(f"Error generating link health report: {e}", file=sys.stderr)
        return 1


def cmd_graph_export(args: argparse.Namespace) -> int:
    """Export vault graph to various formats."""
    from obsidian_vault.utils import ensure_vault_exists, validate_choice

    repo_root = discover_repo_root()

    try:
        vault_dir = ensure_vault_exists(repo_root)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    try:
        vg = VaultGraph(vault_dir)
        output_path = Path(args.output)

        # Determine format from extension if not specified
        format_map = {
            ".gexf": "gexf",
            ".graphml": "graphml",
            ".json": "json",
            ".csv": "csv",
        }

        export_format = args.format
        if not export_format:
            suffix = output_path.suffix.lower()
            export_format = format_map.get(suffix, "gexf")

        # Validate export format
        try:
            export_format = validate_choice(
                export_format,
                {"gexf", "graphml", "json", "csv"}
            )
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

        vg.export_graph_data(output_path, format=export_format)
        print(f"Graph exported to {output_path} (format: {export_format})")

        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error exporting graph: {e}", file=sys.stderr)
        return 1


def cmd_communities(args: argparse.Namespace) -> int:
    """Detect communities (clusters) of related notes."""
    from obsidian_vault.utils import ensure_vault_exists, validate_choice

    repo_root = discover_repo_root()

    try:
        vault_dir = ensure_vault_exists(repo_root)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    try:
        # Validate algorithm choice
        try:
            algorithm = validate_choice(
                args.algorithm,
                {"louvain", "greedy", "label_propagation"}
            )
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

        print(f"Detecting communities using {algorithm} algorithm...", file=sys.stderr)
        vg = VaultGraph(vault_dir)
        communities = vg.detect_communities(algorithm=algorithm, min_size=args.min_size)

        if not communities:
            print("No communities found.")
            return 0

        # Limit to top N if specified
        if args.top:
            communities = communities[:args.top]

        # Print summary
        print("=" * 80)
        print(f"Vault Communities ({args.algorithm} algorithm)")
        print("=" * 80)
        print()

        for comm in communities:
            topics_str = ", ".join([f"{topic}({count})" for topic, count in comm["topics"][:3]])
            print(f"Community {comm['id']}:")
            print(f"  Size: {comm['size']} notes")
            print(f"  Density: {comm['density']:.3f}")
            if topics_str:
                print(f"  Topics: {topics_str}")

            if args.show_notes:
                print("  Notes:")
                for note in comm["notes"][:10]:  # Limit to first 10
                    print(f"    - {note}")
                if len(comm["notes"]) > 10:
                    print(f"    ...and {len(comm['notes']) - 10} more")

            print()

        # Print statistics
        total_notes = sum(c["size"] for c in communities)
        avg_size = total_notes / len(communities) if communities else 0
        avg_density = sum(c["density"] for c in communities) / len(communities) if communities else 0

        print("Statistics:")
        print(f"  Total communities: {len(communities)}")
        print(f"  Total notes in communities: {total_notes}")
        print(f"  Average community size: {avg_size:.1f}")
        print(f"  Average community density: {avg_density:.3f}")

        # Write output file if requested
        if args.output:
            output_lines = [
                f"# Vault Communities ({args.algorithm} algorithm)\n\n",
                f"**Total Communities**: {len(communities)}\n",
                f"**Algorithm**: {args.algorithm}\n",
                f"**Minimum Size**: {args.min_size}\n\n",
                "---\n\n",
            ]

            for comm in communities:
                output_lines.append(f"## Community {comm['id']}\n\n")
                output_lines.append(f"- **Size**: {comm['size']} notes\n")
                output_lines.append(f"- **Density**: {comm['density']:.3f}\n")

                if comm["topics"]:
                    topics_str = ", ".join([f"{t}({c})" for t, c in comm["topics"]])
                    output_lines.append(f"- **Topics**: {topics_str}\n")

                output_lines.append("\n**Notes**:\n\n")
                for note in comm["notes"]:
                    output_lines.append(f"- {note}\n")

                output_lines.append("\n---\n\n")

            Path(args.output).write_text("".join(output_lines), encoding="utf-8")
            print(f"\nCommunities report written to {args.output}")

        return 0

    except Exception as e:
        print(f"Error detecting communities: {e}", file=sys.stderr)
        return 1


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

    # Graph statistics command
    stats_parser = subparsers.add_parser(
        "graph-stats",
        help="Display vault network statistics and link quality metrics",
    )
    stats_parser.add_argument(
        "--hubs",
        type=int,
        metavar="N",
        help="Show top N hub notes (most outgoing links)",
    )
    stats_parser.add_argument(
        "--authorities",
        type=int,
        metavar="N",
        help="Show top N authority notes (most incoming links)",
    )

    # Orphans command
    orphans_parser = subparsers.add_parser(
        "orphans",
        help="Find orphaned notes (no incoming or outgoing links)",
    )
    orphans_parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Write results to file (default: print to stdout)",
    )

    # Broken links command
    broken_parser = subparsers.add_parser(
        "broken-links",
        help="Find notes with broken links (links to non-existent notes)",
    )
    broken_parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Write results to file (default: print to stdout)",
    )

    # Link health report command
    report_parser = subparsers.add_parser(
        "link-report",
        help="Generate comprehensive markdown link health report",
    )
    report_parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output file path (default: print to stdout)",
    )

    # Graph export command
    export_parser = subparsers.add_parser(
        "graph-export",
        help="Export vault graph to various formats for external analysis",
    )
    export_parser.add_argument(
        "output",
        type=str,
        help="Output file path",
    )
    export_parser.add_argument(
        "--format",
        "-f",
        choices=["gexf", "graphml", "json", "csv"],
        help="Export format (default: auto-detect from file extension)",
    )

    # Communities command
    communities_parser = subparsers.add_parser(
        "communities",
        help="Detect communities (clusters) of related notes",
    )
    communities_parser.add_argument(
        "--algorithm",
        "-a",
        choices=["louvain", "greedy", "label_propagation"],
        default="louvain",
        help="Community detection algorithm (default: louvain)",
    )
    communities_parser.add_argument(
        "--min-size",
        "-m",
        type=int,
        default=2,
        help="Minimum community size (default: 2)",
    )
    communities_parser.add_argument(
        "--top",
        "-n",
        type=int,
        help="Show only top N communities",
    )
    communities_parser.add_argument(
        "--show-notes",
        action="store_true",
        help="Show notes in each community",
    )
    communities_parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Write results to file",
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
    elif args.command == "graph-stats":
        return cmd_graph_stats(args)
    elif args.command == "orphans":
        return cmd_orphans(args)
    elif args.command == "broken-links":
        return cmd_broken_links(args)
    elif args.command == "link-report":
        return cmd_link_report(args)
    elif args.command == "graph-export":
        return cmd_graph_export(args)
    elif args.command == "communities":
        return cmd_communities(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
