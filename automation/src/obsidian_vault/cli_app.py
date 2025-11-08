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
)
from obsidian_vault.utils.graph_analytics import VaultGraph, generate_link_health_report
from obsidian_vault.validators import Severity, ValidatorRegistry

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
    try:
        repo_root = discover_repo_root()
        vault_dir = repo_root / "InterviewQuestions"

        if not vault_dir.exists():
            console.print("[red]✗[/red] InterviewQuestions directory not found")
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
            raise typer.Exit(code=1)

        # Load taxonomy and note index
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            progress.add_task("Loading taxonomy and building note index...", total=None)
            taxonomy = TaxonomyLoader(repo_root).load()
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

        # Generate report if requested
        if report:
            ReportGenerator(results).write_markdown(Path(report))
            console.print(f"\n[green]✓[/green] Report written to {report}")

        # Display results
        if quiet:
            _print_summary(results)
        else:
            _print_detailed_results(results)

        raise typer.Exit(code=1 if has_critical else 0)

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
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
    try:
        repo_root = discover_repo_root()
        vault_dir = repo_root / "InterviewQuestions"

        if not vault_dir.exists():
            console.print("[red]✗[/red] InterviewQuestions directory not found")
            raise typer.Exit(code=1)

        with console.status("[bold green]Analyzing vault graph...", spinner="dots"):
            vg = VaultGraph(vault_dir)
            stats = vg.get_network_statistics()
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

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        raise typer.Exit(code=1)


@app.command()
def orphans(
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Write results to file"),
):
    """
    Find orphaned notes (no incoming or outgoing links).

    Helps identify disconnected content that needs linking.
    """
    try:
        repo_root = discover_repo_root()
        vault_dir = repo_root / "InterviewQuestions"

        if not vault_dir.exists():
            console.print("[red]✗[/red] InterviewQuestions directory not found")
            raise typer.Exit(code=1)

        with console.status("[bold green]Finding orphaned notes...", spinner="dots"):
            vg = VaultGraph(vault_dir)
            orphan_notes = vg.get_orphaned_notes()

        if not orphan_notes:
            console.print("[green]✓[/green] No orphaned notes found! All notes have at least one link.")
            return

        console.print(f"\n[yellow]Found {len(orphan_notes)} orphaned notes:[/yellow]\n")
        for note in orphan_notes:
            console.print(f"  • {note}")

        if output:
            Path(output).write_text("\n".join(orphan_notes), encoding="utf-8")
            console.print(f"\n[green]✓[/green] Wrote {len(orphan_notes)} orphaned notes to {output}")

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        raise typer.Exit(code=1)


@app.command()
def broken_links(
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Write results to file"),
):
    """
    Find notes with broken links (links to non-existent notes).

    Helps maintain vault integrity by identifying missing link targets.
    """
    try:
        repo_root = discover_repo_root()
        vault_dir = repo_root / "InterviewQuestions"

        if not vault_dir.exists():
            console.print("[red]✗[/red] InterviewQuestions directory not found")
            raise typer.Exit(code=1)

        with console.status("[bold green]Finding broken links...", spinner="dots"):
            vg = VaultGraph(vault_dir)
            broken = vg.get_broken_links()

        if not broken:
            console.print("[green]✓[/green] No broken links found! All links point to existing notes.")
            return

        total_broken = sum(len(targets) for targets in broken.values())
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

        raise typer.Exit(code=1)

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        raise typer.Exit(code=1)


@app.command()
def link_report(
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
):
    """
    Generate comprehensive markdown link health report.

    Creates a detailed report with statistics, orphans, hubs, and authorities.
    """
    try:
        repo_root = discover_repo_root()
        vault_dir = repo_root / "InterviewQuestions"

        if not vault_dir.exists():
            console.print("[red]✗[/red] InterviewQuestions directory not found")
            raise typer.Exit(code=1)

        with console.status("[bold green]Generating link health report...", spinner="dots"):
            report = generate_link_health_report(vault_dir)

        if output:
            Path(output).write_text(report, encoding="utf-8")
            console.print(f"[green]✓[/green] Link health report written to {output}")
        else:
            console.print(report)

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
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
    try:
        repo_root = discover_repo_root()
        vault_dir = repo_root / "InterviewQuestions"

        if not vault_dir.exists():
            console.print("[red]✗[/red] InterviewQuestions directory not found")
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

        with console.status(f"[bold green]Exporting graph to {export_format.upper()}...", spinner="dots"):
            vg = VaultGraph(vault_dir)
            vg.export_graph_data(output_path, format=export_format)

        console.print(f"[green]✓[/green] Graph exported to {output_path} (format: {export_format})")

    except ValueError as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        raise typer.Exit(code=1)


# ============================================================================
# Main entry point
# ============================================================================

if __name__ == "__main__":
    app()
