"""
Modern CLI application using Typer and Rich.

This is an enhanced version of the vault CLI with:
- Beautiful terminal output using Rich
- Automatic documentation from type hints
- Better error messages and help text
- Progress bars and tables
- Type validation

For backward compatibility, the original argparse CLI remains available.
Use `vault-app` for this enhanced version.
"""

from __future__ import annotations

import sys
from enum import Enum
from pathlib import Path
from typing import Optional

import typer
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text

from obsidian_vault.utils import (
    FileResult,
    ReportGenerator,
    TaxonomyLoader,
    build_note_index,
    collect_validatable_files,
    discover_repo_root,
    parse_note,
    setup_logging,
)
from obsidian_vault.utils.graph_analytics import VaultGraph, generate_link_health_report
from obsidian_vault.validators import Severity, ValidatorRegistry

# Initialize logging
setup_logging()

# Create Typer app and Rich console
app = typer.Typer(
    name="vault-app",
    help="Obsidian Interview Questions vault automation toolkit",
    add_completion=False,
    rich_markup_mode="rich",
)
console = Console()


# Enum for output formats
class ExportFormat(str, Enum):
    """Graph export formats."""

    gexf = "gexf"
    graphml = "graphml"
    json = "json"
    csv = "csv"


# ============================================================================
# Validation Command
# ============================================================================


@app.command()
def validate(
    path: Optional[str] = typer.Argument(None, help="File or directory to validate"),
    all: bool = typer.Option(False, "--all", "-a", help="Validate all notes in vault"),
    parallel: bool = typer.Option(False, "--parallel", "-p", help="Use parallel processing"),
    workers: int = typer.Option(4, "--workers", "-w", help="Number of parallel workers"),
    report: Optional[str] = typer.Option(None, "--report", "-r", help="Write report to file"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Only print summary"),
):
    """
    Validate vault notes for structure, format, and quality.

    Checks YAML frontmatter, content structure, links, and more.
    """
    logger.info("Starting validation")
    try:
        repo_root = discover_repo_root()
        vault_dir = repo_root / "InterviewQuestions"
        logger.debug(f"Repository root: {repo_root}")
        logger.debug(f"Vault directory: {vault_dir}")

        if not vault_dir.exists():
            console.print("[red]✗[/red] InterviewQuestions directory not found")
            logger.error(f"Vault directory not found: {vault_dir}")
            raise typer.Exit(code=1)

        # Determine targets
        if all:
            targets = collect_validatable_files(vault_dir)
        elif path:
            explicit = Path(path)
            candidates = [explicit, repo_root / path, vault_dir / path]
            targets = []
            for candidate in candidates:
                if candidate.exists():
                    if candidate.is_file() and candidate.suffix.lower() == ".md":
                        targets = [candidate.resolve()]
                        break
                    if candidate.is_dir():
                        targets = collect_validatable_files(candidate)
                        break
            if not targets:
                console.print(f"[red]✗[/red] Path not found: {path}")
                raise typer.Exit(code=1)
        else:
            console.print("[yellow]⚠[/yellow] Either provide a path or use --all")
            raise typer.Exit(code=1)

        if not targets:
            console.print("[yellow]⚠[/yellow] No Markdown notes found")
            logger.warning("No Markdown notes found to validate")
            raise typer.Exit(code=1)

        logger.info(f"Found {len(targets)} file(s) to validate")
        logger.debug(f"Targets: {[str(t) for t in targets[:5]]}{'...' if len(targets) > 5 else ''}")

        # Load taxonomy and note index
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            progress.add_task("Loading taxonomy and building note index...", total=None)
            logger.debug("Loading taxonomy")
            taxonomy = TaxonomyLoader(repo_root).load()
            logger.debug("Building note index")
            note_index = build_note_index(vault_dir)

        # Validate files
        console.print(f"\n[bold]Validating {len(targets)} file(s)...[/bold]\n")

        if parallel and len(targets) > 1:
            # For now, use sequential (can enhance with actual parallel processing)
            results = _validate_files(targets, repo_root, vault_dir, taxonomy, note_index)
        else:
            results = _validate_files(targets, repo_root, vault_dir, taxonomy, note_index)

        # Check for critical issues
        has_critical = any(
            any(issue.severity == Severity.CRITICAL for issue in result.issues)
            for result in results
        )

        total_issues = sum(len(result.issues) for result in results)
        logger.info(f"Validation complete: {total_issues} issue(s) found")
        logger.debug(f"Critical issues: {has_critical}")

        # Generate report if requested
        if report:
            ReportGenerator(results).write_markdown(Path(report))
            console.print(f"\n[green]✓[/green] Report written to {report}")
            logger.info(f"Validation report written to {report}")

        # Display results
        if quiet:
            _print_summary(results)
        else:
            _print_detailed_results(results)

        logger.success("Validation complete" if not has_critical else "Validation complete with critical issues")
        raise typer.Exit(code=1 if has_critical else 0)

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        logger.exception(f"Validation failed with error: {e}")
        raise typer.Exit(code=1)


def _validate_files(targets, repo_root, vault_dir, taxonomy, note_index) -> list[FileResult]:
    """Validate a list of files."""
    results = []

    with Progress(console=console) as progress:
        task = progress.add_task("[cyan]Validating...", total=len(targets))

        for file_path in targets:
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

            results.append(
                FileResult(
                    path=str(file_path.relative_to(repo_root)),
                    issues=issues,
                    passed=passed,
                )
            )
            progress.advance(task)

    return results


def _print_summary(results):
    """Print summary table."""
    total_files = len(results)
    severity_counts = {"CRITICAL": 0, "ERROR": 0, "WARNING": 0, "INFO": 0}

    for result in results:
        for issue in result.issues:
            severity_counts[issue.severity.value] += 1

    table = Table(title="Validation Summary", show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", justify="right", style="magenta")

    table.add_row("Files Validated", str(total_files))
    table.add_row("Total Issues", str(sum(severity_counts.values())))
    for severity, count in severity_counts.items():
        if count > 0:
            color = {
                "CRITICAL": "red",
                "ERROR": "red",
                "WARNING": "yellow",
                "INFO": "blue",
            }[severity]
            table.add_row(f"  {severity}", f"[{color}]{count}[/{color}]")

    console.print(table)


def _print_detailed_results(results):
    """Print detailed results for each file."""
    for result in results:
        if result.issues:
            severity_counts = {}
            for issue in result.issues:
                severity_counts[issue.severity.value] = severity_counts.get(issue.severity.value, 0) + 1

            summary = ", ".join(f"{k}: {v}" for k, v in sorted(severity_counts.items()))
            title = f"📄 {result.path} - Issues: {summary}"

            panel_content = []
            for issue in result.issues:
                color = {
                    "CRITICAL": "red",
                    "ERROR": "red",
                    "WARNING": "yellow",
                    "INFO": "blue",
                }.get(issue.severity.value, "white")

                field_info = f" [dim]\\[{issue.field}][/dim]" if issue.field else ""
                panel_content.append(f"[{color}]●[/{color}] {issue.severity.value}: {issue.message}{field_info}")

            console.print(
                Panel(
                    "\n".join(panel_content),
                    title=title,
                    border_style="red" if "CRITICAL" in severity_counts else "yellow",
                )
            )
        else:
            console.print(f"[green]✓[/green] {result.path} - No issues")


# ============================================================================
# Graph Analytics Commands
# ============================================================================


@app.command()
def graph_stats(
    hubs: Optional[int] = typer.Option(None, "--hubs", "-h", help="Show top N hub notes"),
    authorities: Optional[int] = typer.Option(None, "--authorities", "-a", help="Show top N authority notes"),
):
    """
    Display vault network statistics and link quality metrics.

    Shows total notes, links, density, orphaned notes, and more.
    """
    logger.info("Analyzing vault graph statistics")
    try:
        repo_root = discover_repo_root()
        vault_dir = repo_root / "InterviewQuestions"
        logger.debug(f"Vault directory: {vault_dir}")

        if not vault_dir.exists():
            console.print("[red]✗[/red] InterviewQuestions directory not found")
            logger.error(f"Vault directory not found: {vault_dir}")
            raise typer.Exit(code=1)

        with console.status("[bold green]Analyzing vault graph...", spinner="dots"):
            logger.debug("Building vault graph")
            vg = VaultGraph(vault_dir)
            logger.debug("Calculating network statistics")
            stats = vg.get_network_statistics()
            logger.debug("Analyzing link quality")
            quality = vg.analyze_link_quality()

        # Create main statistics table
        table = Table(title="Vault Network Statistics", show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", justify="right", style="magenta")

        table.add_row("Total Notes", str(stats["total_notes"]))
        table.add_row("Total Links", str(stats["total_links"]))
        table.add_row("Average Degree", f"{stats['average_degree']:.2f}")
        table.add_row("Network Density", f"{stats['density']:.4f}")
        table.add_row("Connected Components", str(stats["connected_components"]))
        table.add_row("", "")  # Separator
        table.add_row("Reciprocal Links", str(quality["reciprocal_links"]))
        table.add_row("Unidirectional Links", str(quality["unidirectional_links"]))
        table.add_row("Orphaned Notes", f"{stats['orphaned_notes']} ({quality['orphaned_ratio']:.1%})")
        table.add_row("Isolated Notes", f"{stats['isolated_notes']} ({quality['isolated_ratio']:.1%})")

        console.print(table)

        # Show hubs if requested
        if hubs:
            hub_notes = vg.get_hub_notes(hubs)
            if hub_notes:
                hub_table = Table(title=f"Top {hubs} Hub Notes", show_header=True, header_style="bold green")
                hub_table.add_column("Note", style="cyan")
                hub_table.add_column("Outgoing Links", justify="right", style="green")

                for note, degree in hub_notes:
                    hub_table.add_row(note, str(degree))

                console.print("\n", hub_table)

        # Show authorities if requested
        if authorities:
            authority_notes = vg.get_authority_notes(authorities)
            if authority_notes:
                auth_table = Table(
                    title=f"Top {authorities} Authority Notes",
                    show_header=True,
                    header_style="bold blue",
                )
                auth_table.add_column("Note", style="cyan")
                auth_table.add_column("Incoming Links", justify="right", style="blue")

                for note, degree in authority_notes:
                    auth_table.add_row(note, str(degree))

                console.print("\n", auth_table)

        logger.success(f"Graph statistics complete: {stats['total_notes']} notes, {stats['total_links']} links")

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        logger.exception(f"Graph stats failed with error: {e}")
        raise typer.Exit(code=1)


@app.command()
def orphans(
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Write results to file"),
):
    """
    Find orphaned notes (no incoming or outgoing links).

    Helps identify disconnected content that needs linking.
    """
    logger.info("Finding orphaned notes")
    try:
        repo_root = discover_repo_root()
        vault_dir = repo_root / "InterviewQuestions"

        if not vault_dir.exists():
            console.print("[red]✗[/red] InterviewQuestions directory not found")
            logger.error(f"Vault directory not found: {vault_dir}")
            raise typer.Exit(code=1)

        with console.status("[bold green]Finding orphaned notes...", spinner="dots"):
            vg = VaultGraph(vault_dir)
            orphan_notes = vg.get_orphaned_notes()

        if not orphan_notes:
            console.print("[green]✓[/green] No orphaned notes found! All notes have at least one link.")
            logger.success("No orphaned notes found")
            return

        logger.warning(f"Found {len(orphan_notes)} orphaned notes")
        logger.debug(f"Orphaned notes: {orphan_notes[:5]}{'...' if len(orphan_notes) > 5 else ''}")

        console.print(f"\n[yellow]Found {len(orphan_notes)} orphaned notes:[/yellow]\n")
        for note in orphan_notes:
            console.print(f"  • {note}")

        if output:
            Path(output).write_text("\n".join(orphan_notes), encoding="utf-8")
            console.print(f"\n[green]✓[/green] Wrote {len(orphan_notes)} orphaned notes to {output}")
            logger.info(f"Wrote orphaned notes to {output}")

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        logger.exception(f"Orphans command failed with error: {e}")
        raise typer.Exit(code=1)


@app.command()
def broken_links(
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Write results to file"),
):
    """
    Find notes with broken links (links to non-existent notes).

    Helps maintain vault integrity by identifying missing link targets.
    """
    logger.info("Finding broken links")
    try:
        repo_root = discover_repo_root()
        vault_dir = repo_root / "InterviewQuestions"

        if not vault_dir.exists():
            console.print("[red]✗[/red] InterviewQuestions directory not found")
            logger.error(f"Vault directory not found: {vault_dir}")
            raise typer.Exit(code=1)

        with console.status("[bold green]Finding broken links...", spinner="dots"):
            vg = VaultGraph(vault_dir)
            broken = vg.get_broken_links()

        if not broken:
            console.print("[green]✓[/green] No broken links found! All links point to existing notes.")
            logger.success("No broken links found")
            return

        total_broken = sum(len(targets) for targets in broken.values())
        logger.error(f"Found {len(broken)} notes with {total_broken} broken links")
        console.print(f"\n[red]Found {len(broken)} notes with {total_broken} broken links:[/red]\n")

        for source, targets in sorted(broken.items()):
            console.print(f"[cyan]{source}:[/cyan]")
            for target in targets:
                console.print(f"  [red]→[/red] {target} [dim](missing)[/dim]")

        if output:
            lines = []
            for source, targets in sorted(broken.items()):
                lines.append(f"{source}:")
                for target in targets:
                    lines.append(f"  - {target}")
            Path(output).write_text("\n".join(lines), encoding="utf-8")
            console.print(f"\n[green]✓[/green] Wrote broken links report to {output}")
            logger.info(f"Wrote broken links report to {output}")

        raise typer.Exit(code=1)

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        logger.exception(f"Broken links command failed with error: {e}")
        raise typer.Exit(code=1)


@app.command()
def link_report(
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
):
    """
    Generate comprehensive markdown link health report.

    Creates a detailed report with statistics, orphans, hubs, and authorities.
    """
    logger.info("Generating link health report")
    try:
        repo_root = discover_repo_root()
        vault_dir = repo_root / "InterviewQuestions"

        if not vault_dir.exists():
            console.print("[red]✗[/red] InterviewQuestions directory not found")
            logger.error(f"Vault directory not found: {vault_dir}")
            raise typer.Exit(code=1)

        with console.status("[bold green]Generating link health report...", spinner="dots"):
            logger.debug("Generating comprehensive link health report")
            report = generate_link_health_report(vault_dir)

        if output:
            Path(output).write_text(report, encoding="utf-8")
            console.print(f"[green]✓[/green] Link health report written to {output}")
            logger.success(f"Link health report written to {output}")
        else:
            console.print(report)
            logger.success("Link health report generated")

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        logger.exception(f"Link report command failed with error: {e}")
        raise typer.Exit(code=1)


@app.command()
def graph_export(
    output: str = typer.Argument(..., help="Output file path"),
    format: Optional[ExportFormat] = typer.Option(
        None, "--format", "-f", help="Export format (auto-detected from extension if not specified)"
    ),
):
    """
    Export vault graph to various formats for external analysis.

    Supports GEXF, GraphML, JSON, and CSV formats.
    """
    logger.info(f"Exporting graph to {output}")
    try:
        repo_root = discover_repo_root()
        vault_dir = repo_root / "InterviewQuestions"

        if not vault_dir.exists():
            console.print("[red]✗[/red] InterviewQuestions directory not found")
            logger.error(f"Vault directory not found: {vault_dir}")
            raise typer.Exit(code=1)

        output_path = Path(output)

        # Determine format
        if format:
            export_format = format.value
        else:
            format_map = {
                ".gexf": "gexf",
                ".graphml": "graphml",
                ".json": "json",
                ".csv": "csv",
            }
            export_format = format_map.get(output_path.suffix.lower(), "gexf")

        logger.debug(f"Export format: {export_format}")

        with console.status(f"[bold green]Exporting graph to {export_format.upper()}...", spinner="dots"):
            vg = VaultGraph(vault_dir)
            vg.export_graph_data(output_path, format=export_format)

        console.print(f"[green]✓[/green] Graph exported to {output_path} (format: {export_format})")
        logger.success(f"Graph exported to {output_path} (format: {export_format})")

    except ValueError as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        logger.error(f"Invalid export format: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        logger.exception(f"Graph export failed with error: {e}")
        raise typer.Exit(code=1)


@app.command()
def communities(
    algorithm: str = typer.Option(
        "louvain",
        "--algorithm",
        "-a",
        help="Algorithm: louvain, greedy, or label_propagation",
    ),
    min_size: int = typer.Option(2, "--min-size", "-m", help="Minimum community size"),
    top_n: Optional[int] = typer.Option(None, "--top", "-n", help="Show only top N communities"),
    show_notes: bool = typer.Option(False, "--show-notes", help="Show notes in each community"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Write results to file"),
):
    """
    Detect communities (clusters) of related notes using graph algorithms.

    Communities are groups of notes that are more densely connected to each
    other than to notes outside the group. Useful for understanding vault
    organization and discovering hidden topic clusters.
    """
    logger.info(f"Detecting communities using {algorithm} algorithm")
    try:
        repo_root = discover_repo_root()
        vault_dir = repo_root / "InterviewQuestions"

        if not vault_dir.exists():
            console.print("[red]✗[/red] InterviewQuestions directory not found")
            logger.error(f"Vault directory not found: {vault_dir}")
            raise typer.Exit(code=1)

        with console.status("[bold green]Analyzing vault communities...", spinner="dots"):
            logger.debug("Building vault graph")
            vg = VaultGraph(vault_dir)
            logger.debug(f"Detecting communities with algorithm={algorithm}, min_size={min_size}")
            communities_data = vg.detect_communities(algorithm=algorithm, min_size=min_size)

        if not communities_data:
            console.print("[yellow]⚠[/yellow] No communities found")
            logger.warning("No communities detected")
            return

        # Limit to top N if specified
        if top_n:
            communities_data = communities_data[:top_n]

        logger.success(f"Detected {len(communities_data)} communities")

        # Create summary table
        summary_table = Table(
            title=f"Vault Communities ({algorithm} algorithm)",
            show_header=True,
            header_style="bold cyan",
        )
        summary_table.add_column("ID", style="cyan", no_wrap=True)
        summary_table.add_column("Size", justify="right", style="magenta")
        summary_table.add_column("Density", justify="right", style="green")
        summary_table.add_column("Top Topics", style="yellow")

        for comm in communities_data:
            topics_str = ", ".join(
                [f"{topic} ({count})" for topic, count in comm["topics"][:3]]
            )
            summary_table.add_row(
                str(comm["id"]),
                str(comm["size"]),
                f"{comm['density']:.3f}",
                topics_str or "—",
            )

        console.print(summary_table)

        # Show detailed notes if requested
        if show_notes:
            console.print()
            for comm in communities_data:
                panel_content = []
                panel_content.append(f"[bold]Size:[/bold] {comm['size']} notes")
                panel_content.append(f"[bold]Density:[/bold] {comm['density']:.3f}")

                if comm["topics"]:
                    topics_str = ", ".join([f"{t} ({c})" for t, c in comm["topics"]])
                    panel_content.append(f"[bold]Topics:[/bold] {topics_str}")

                panel_content.append("\n[bold]Notes:[/bold]")
                for note in comm["notes"][:10]:  # Limit to first 10
                    panel_content.append(f"  • {note}")
                if len(comm["notes"]) > 10:
                    panel_content.append(f"  [dim]...and {len(comm['notes']) - 10} more[/dim]")

                console.print(
                    Panel(
                        "\n".join(panel_content),
                        title=f"Community {comm['id']}",
                        border_style="blue",
                    )
                )

        # Generate text output if requested
        if output:
            output_lines = [
                f"# Vault Communities ({algorithm} algorithm)\n",
                f"**Total Communities**: {len(communities_data)}\n",
                f"**Algorithm**: {algorithm}\n",
                f"**Minimum Size**: {min_size}\n\n",
                "---\n\n",
            ]

            for comm in communities_data:
                output_lines.append(f"## Community {comm['id']}\n\n")
                output_lines.append(f"- **Size**: {comm['size']} notes\n")
                output_lines.append(f"- **Density**: {comm['density']:.3f}\n")

                if comm["topics"]:
                    topics_str = ", ".join([f"{t} ({c})" for t, c in comm["topics"]])
                    output_lines.append(f"- **Topics**: {topics_str}\n")

                output_lines.append("\n**Notes**:\n\n")
                for note in comm["notes"]:
                    output_lines.append(f"- {note}\n")

                output_lines.append("\n---\n\n")

            Path(output).write_text("".join(output_lines), encoding="utf-8")
            console.print(f"\n[green]✓[/green] Communities report written to {output}")
            logger.info(f"Communities report written to {output}")

        # Show statistics
        total_notes = sum(c["size"] for c in communities_data)
        avg_size = total_notes / len(communities_data) if communities_data else 0
        avg_density = (
            sum(c["density"] for c in communities_data) / len(communities_data)
            if communities_data
            else 0
        )

        console.print(f"\n[bold]Statistics:[/bold]")
        console.print(f"  Total communities: {len(communities_data)}")
        console.print(f"  Total notes in communities: {total_notes}")
        console.print(f"  Average community size: {avg_size:.1f}")
        console.print(f"  Average community density: {avg_density:.3f}")

        logger.success(
            f"Community detection complete: {len(communities_data)} communities, "
            f"{total_notes} notes"
        )

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        logger.exception(f"Community detection failed: {e}")
        raise typer.Exit(code=1)


# ============================================================================
# LLM Review Command
# ============================================================================


@app.command()
def llm_review(
    pattern: str = typer.Option(
        "InterviewQuestions/**/*.md",
        "--pattern",
        "-p",
        help="Glob pattern for notes to process",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--no-dry-run",
        help="Preview changes without modifying files",
    ),
    max_iterations: int = typer.Option(
        5,
        "--max-iterations",
        "-m",
        help="Maximum fix iterations per note",
    ),
    backup: bool = typer.Option(
        True,
        "--backup/--no-backup",
        help="Create backups before modifying files",
    ),
    report: Optional[str] = typer.Option(
        None,
        "--report",
        "-r",
        help="Write detailed report to file",
    ),
):
    """
    Review and fix notes using LLM (PydanticAI + LangGraph).

    This command uses AI to:
    1. Review notes for technical accuracy
    2. Fix formatting and structure issues
    3. Ensure compliance with vault rules

    Requires OPENROUTER_API_KEY environment variable.
    """
    import asyncio
    from pathlib import Path

    logger.info("Starting LLM-based note review")

    try:
        # Check for API key
        import os

        if not os.getenv("OPENROUTER_API_KEY"):
            console.print(
                "[red]✗[/red] OPENROUTER_API_KEY environment variable not set\n"
                "Get your API key from https://openrouter.ai/keys"
            )
            raise typer.Exit(code=1)

        repo_root = discover_repo_root()
        vault_dir = repo_root / "InterviewQuestions"

        if not vault_dir.exists():
            console.print("[red]✗[/red] InterviewQuestions directory not found")
            raise typer.Exit(code=1)

        # Import LLM review module
        from obsidian_vault.llm_review import create_review_graph

        # Collect notes matching pattern
        if pattern.startswith("InterviewQuestions/"):
            # Use glob directly on vault_dir with the sub-pattern
            search_pattern = pattern.replace("InterviewQuestions/", "", 1)
            notes = list(vault_dir.glob(search_pattern))
            # Filter to only .md files
            notes = [n for n in notes if n.suffix == ".md" and n.is_file()]
        else:
            # Fallback to full pattern matching
            from obsidian_vault.utils.common import collect_validatable_files

            notes = list(collect_validatable_files(repo_root / pattern.split("/")[0]))

        if not notes:
            console.print(f"[yellow]⚠[/yellow] No notes found matching pattern: {pattern}")
            raise typer.Exit(code=0)

        console.print(f"\n[bold]Found {len(notes)} note(s) to review[/bold]\n")

        if dry_run:
            console.print("[yellow]⚠[/yellow] DRY RUN MODE - No files will be modified\n")

        # Create review graph
        with console.status("[bold green]Initializing LLM review system...", spinner="dots"):
            review_graph = create_review_graph(
                vault_root=vault_dir,
                max_iterations=max_iterations,
            )

        # Process notes
        results = []

        async def process_all():
            for note_path in notes:
                console.print(f"[cyan]Processing:[/cyan] {note_path.relative_to(repo_root)}")
                state = await review_graph.process_note(note_path)
                results.append((note_path, state))

                # Show summary
                if state.error:
                    console.print(f"  [red]✗[/red] Error: {state.error}")
                elif state.changed:
                    console.print(
                        f"  [green]✓[/green] Modified "
                        f"({state.iteration} iteration(s), {len(state.issues)} final issue(s))"
                    )
                else:
                    console.print("  [green]✓[/green] No changes needed")

                # Save if not dry-run
                if not dry_run and state.changed:
                    if backup:
                        backup_path = note_path.with_suffix(".md.backup")
                        backup_path.write_text(state.original_text, encoding="utf-8")
                        console.print(f"  [dim]Backup: {backup_path.name}[/dim]")

                    note_path.write_text(state.current_text, encoding="utf-8")
                    console.print(f"  [dim]Saved changes to {note_path.name}[/dim]")

                console.print()

        asyncio.run(process_all())

        # Generate summary
        total = len(results)
        modified = sum(1 for _, state in results if state.changed)
        errors = sum(1 for _, state in results if state.error)

        table = Table(title="LLM Review Summary", show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", justify="right", style="magenta")

        table.add_row("Notes Processed", str(total))
        table.add_row("Modified", f"[{'yellow' if dry_run else 'green'}]{modified}[/]")
        table.add_row("Errors", f"[{'red' if errors > 0 else 'green'}]{errors}[/]")
        table.add_row("Unchanged", str(total - modified - errors))

        console.print(table)

        # Generate detailed report if requested
        if report:
            report_lines = ["# LLM Review Report\n"]
            report_lines.append(f"**Total notes**: {total}\n")
            report_lines.append(f"**Modified**: {modified}\n")
            report_lines.append(f"**Errors**: {errors}\n")
            report_lines.append(f"**Dry run**: {dry_run}\n")
            report_lines.append("\n---\n\n")

            for note_path, state in results:
                report_lines.append(f"## {note_path.relative_to(repo_root)}\n\n")
                report_lines.append(f"**Changed**: {state.changed}\n")
                report_lines.append(f"**Iterations**: {state.iteration}\n")
                report_lines.append(f"**Final issues**: {len(state.issues)}\n")

                if state.error:
                    report_lines.append(f"**Error**: {state.error}\n")

                if state.history:
                    report_lines.append("\n**History**:\n")
                    for entry in state.history:
                        report_lines.append(
                            f"- [{entry['iteration']}] {entry['node']}: {entry['message']}\n"
                        )

                report_lines.append("\n---\n\n")

            Path(report).write_text("".join(report_lines), encoding="utf-8")
            console.print(f"\n[green]✓[/green] Report written to {report}")

        logger.success(
            f"LLM review complete: {total} notes, {modified} modified, {errors} errors"
        )

        if errors > 0:
            raise typer.Exit(code=1)

    except ImportError as e:
        console.print(
            f"[red]✗ Error:[/red] LLM review dependencies not installed\n"
            f"Install with: pip install pydantic-ai langgraph\n"
            f"Details: {e}"
        )
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        logger.exception(f"LLM review failed: {e}")
        raise typer.Exit(code=1)


# ============================================================================
# Main entry point
# ============================================================================

if __name__ == "__main__":
    app()
