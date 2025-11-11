"""Modern CLI application using Typer and Rich.

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

import json
import os
from enum import Enum
from pathlib import Path
from typing import Annotated, Any, Never, cast

import typer
from dotenv import load_dotenv
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from obsidian_vault.llm_review import CompletionMode, ProcessingProfile
from obsidian_vault.qa_generation.gap_analysis import GapAnalysisWorkflow, GapWorkflowConfig
from obsidian_vault.qa_generation.workflow import NoteIngestionWorkflow, WorkflowConfig
from obsidian_vault.technical_validation import TechnicalValidationFlow
from obsidian_vault.utils import (
    FileResult,
    ReportGenerator,
    TaxonomyLoader,
    atomic_write,
    build_note_index,
    collect_validatable_files,
    discover_repo_root,
    parse_note,
    sanitize_text_for_yaml,
    setup_logging,
    validate_integer,
    validate_url,
)
from obsidian_vault.utils.graph_analytics import VaultGraph, generate_link_health_report
from obsidian_vault.validators import Severity, ValidatorRegistry

load_dotenv()
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent.parent / ".env")
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")

setup_logging()

app = typer.Typer(
    name="vault-app",
    help="Obsidian Interview Questions vault automation toolkit",
    add_completion=False,
    rich_markup_mode="rich",
)
console = Console()


def _abort(exc: Exception | None = None) -> Never:
    """Exit the CLI with a consistent Typer handling."""
    if exc is None:
        raise typer.Exit(code=1) from None
    raise typer.Exit(code=1) from exc


class ExportFormat(str, Enum):
    """Graph export formats."""

    gexf = "gexf"
    graphml = "graphml"
    json = "json"
    csv = "csv"


@app.command()
def validate(
    path: str | None = typer.Argument(None, help="File or directory to validate"),
    all_notes: bool = typer.Option(False, "--all", "-a", help="Validate all notes in vault"),
    parallel: bool = typer.Option(False, "--parallel", "-p", help="Use parallel processing"),
    workers: int = typer.Option(4, "--workers", "-w", help="Number of parallel workers"),
    report: str | None = typer.Option(None, "--report", "-r", help="Write report to file"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Only print summary"),
):
    """Validate vault notes for structure, format, and quality.

    Checks YAML frontmatter, content structure, links, and more.
    """
    from obsidian_vault.utils import ensure_vault_exists, safe_resolve_path

    logger.info("Starting validation")
    try:
        repo_root = discover_repo_root()
        logger.debug(f"Repository root: {repo_root}")

        try:
            vault_dir = ensure_vault_exists(repo_root)
            logger.debug(f"Vault directory: {vault_dir}")
        except ValueError as e:
            console.print(f"[red]✗[/red] {e}")
            logger.error(f"Vault directory not found: {e}")
            _abort(e)

        if all_notes:
            targets = collect_validatable_files(vault_dir)
        elif path:
            try:
                safe_path = safe_resolve_path(path, vault_dir)
            except ValueError:
                try:
                    safe_path = safe_resolve_path(path, repo_root)
                except ValueError as e:
                    console.print(
                        f"[red]✗[/red] Invalid path: {e}\n\n"
                        f"Valid path examples:\n"
                        f"  • InterviewQuestions/40-Android\n"
                        f"  • 40-Android/q-compose-state--android--medium.md\n"
                        f"  • Or use --all to validate entire vault"
                    )
                    _abort(e)

            if not safe_path.exists():
                console.print(
                    f"[red]✗[/red] Path not found: {path}\n\n"
                    f"Valid path examples:\n"
                    f"  • InterviewQuestions/40-Android\n"
                    f"  • 40-Android/q-compose-state--android--medium.md"
                )
                _abort()

            if safe_path.is_file() and safe_path.suffix.lower() == ".md":
                targets = [safe_path]
            elif safe_path.is_dir():
                targets = collect_validatable_files(safe_path)
            else:
                console.print(
                    f"[red]✗[/red] Invalid path: {path} is not a markdown file or directory"
                )
                _abort()
        else:
            console.print("[yellow]⚠[/yellow] Either provide a path or use --all")
            _abort()

        if not targets:
            console.print("[yellow]⚠[/yellow] No Markdown notes found")
            logger.warning("No Markdown notes found to validate")
            _abort()

        logger.info(f"Found {len(targets)} file(s) to validate")
        logger.debug(f"Targets: {[str(t) for t in targets[:5]]}{'...' if len(targets) > 5 else ''}")

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

        console.print(f"\n[bold]Validating {len(targets)} file(s)...[/bold]\n")

        if parallel and len(targets) > 1:
            # For now, use sequential (can enhance with actual parallel processing)
            results = _validate_files(targets, repo_root, vault_dir, taxonomy, note_index)
        else:
            results = _validate_files(targets, repo_root, vault_dir, taxonomy, note_index)

        has_critical = any(
            any(issue.severity == Severity.CRITICAL for issue in result.issues)
            for result in results
        )

        total_issues = sum(len(result.issues) for result in results)
        logger.info(f"Validation complete: {total_issues} issue(s) found")
        logger.debug(f"Critical issues: {has_critical}")

        if report:
            ReportGenerator(results).write_markdown(Path(report))
            console.print(f"\n[green]✓[/green] Report written to {report}")
            logger.info(f"Validation report written to {report}")

        if quiet:
            _print_summary(results)
        else:
            _print_detailed_results(results)

        logger.success(
            "Validation complete"
            if not has_critical
            else "Validation complete with critical issues"
        )
        raise typer.Exit(code=1 if has_critical else 0)

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        logger.exception(f"Validation failed with error: {e}")
        _abort(e)


@app.command("technical-validate")
def technical_validate(
    path: str | None = typer.Argument(None, help="File or directory to analyze"),
    all_notes: bool = typer.Option(False, "--all", "-a", help="Validate every note in the vault"),
    limit: int | None = typer.Option(None, "--limit", "-l", help="Limit the number of notes"),
    json_output: str | None = typer.Option(None, "--json", help="Write JSON results to file"),
):
    """Run the LangChain-powered technical validation workflow."""
    from obsidian_vault.utils import ensure_vault_exists, safe_resolve_path

    logger.info("Starting technical validation run")
    try:
        repo_root = discover_repo_root()
        vault_dir = ensure_vault_exists(repo_root)
    except ValueError as error:
        console.print(f"[red]✗[/red] {error}")
        logger.error("Vault discovery failed: {}", error)
        _abort(error)

    if all_notes:
        targets = collect_validatable_files(vault_dir)
    elif path:
        try:
            safe_path = safe_resolve_path(path, vault_dir)
        except ValueError:
            try:
                safe_path = safe_resolve_path(path, repo_root)
            except ValueError as error:
                console.print(f"[red]✗[/red] Invalid path: {error}")
                _abort(error)

        if safe_path.is_file() and safe_path.suffix.lower() == ".md":
            targets = [safe_path]
        elif safe_path.is_dir():
            targets = collect_validatable_files(safe_path)
        else:
            console.print(f"[red]✗[/red] Invalid path: {path} is not a markdown file or directory")
            _abort()
    else:
        console.print("[yellow]⚠[/yellow] Either provide a path or use --all")
        _abort()

    if not targets:
        console.print("[yellow]⚠[/yellow] No Markdown notes found")
        logger.warning("No Markdown notes available for technical validation")
        _abort()

    if limit is not None and limit > 0:
        targets = targets[:limit]
        logger.debug("Limiting validation to {} notes", len(targets))

    flow = TechnicalValidationFlow.from_repo(repo_root)
    reports = flow.validate_paths(targets)

    if not reports:
        console.print("[green]✓[/green] No technical issues detected in the selected notes.")
        logger.success("Technical validation completed without findings")
        raise typer.Exit(code=0)

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Note")
    table.add_column("Severity", style="magenta")
    table.add_column("Summary", style="white")

    for report in reports:
        relative_path = report.path.relative_to(repo_root)
        severity = report.highest_severity.value if report.highest_severity else "INFO"
        summary = (report.summary or "See detailed findings below.").strip()
        table.add_row(
            str(relative_path), severity, summary[:160] + ("…" if len(summary) > 160 else "")
        )

    console.print("\n[bold]Technical Validation Findings[/bold]\n")
    console.print(table)

    for report in reports:
        relative_path = report.path.relative_to(repo_root)
        console.print()
        console.rule(f"{relative_path}")
        for finding in report.findings:
            issue = finding.issue
            context = f" (field: {issue.field})" if issue.field else ""
            location = f" line {issue.line}" if issue.line is not None else ""
            console.print(
                f"[bold]{issue.severity.value}[/bold]{context}{location}: {issue.message}",
            )
            if finding.fix:
                console.print(f"  [green]Suggested fix:[/green] {finding.fix}")
            if finding.references:
                console.print(f"  [blue]References:[/blue] {' | '.join(finding.references)}")
        if report.summary:
            console.print(f"\n[italic]Agent summary:[/italic] {report.summary}")

    if json_output:
        output_path = Path(json_output)
        payload = [
            {
                "path": str(report.path.relative_to(repo_root)),
                "summary": report.summary,
                "issues": [
                    {
                        "validator": finding.validator,
                        "severity": finding.issue.severity.value,
                        "message": finding.issue.message,
                        "field": finding.issue.field,
                        "line": finding.issue.line,
                        "fix": finding.fix,
                        "references": finding.references,
                    }
                    for finding in report.findings
                ],
            }
            for report in reports
        ]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        console.print(f"\n[green]✓[/green] JSON report written to {output_path}")
        logger.info("Technical validation JSON report written to {}", output_path)

    logger.success("Technical validation completed with {} notes showing issues", len(reports))
    raise typer.Exit(code=0)


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
            severity_counts: dict[str, int] = {}
            for issue in result.issues:
                severity_counts[issue.severity.value] = (
                    severity_counts.get(issue.severity.value, 0) + 1
                )

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
                panel_content.append(
                    f"[{color}]●[/{color}] {issue.severity.value}: {issue.message}{field_info}"
                )

            console.print(
                Panel(
                    "\n".join(panel_content),
                    title=title,
                    border_style="red" if "CRITICAL" in severity_counts else "yellow",
                )
            )
        else:
            console.print(f"[green]✓[/green] {result.path} - No issues")


@app.command()
def graph_stats(
    hubs: int | None = typer.Option(None, "--hubs", "-h", help="Show top N hub notes"),
    authorities: int | None = typer.Option(
        None, "--authorities", "-a", help="Show top N authority notes"
    ),
):
    """Display vault network statistics and link quality metrics.

    Shows total notes, links, density, orphaned notes, and more.
    """
    from obsidian_vault.utils import ensure_vault_exists

    logger.info("Analyzing vault graph statistics")
    try:
        repo_root = discover_repo_root()
        logger.debug(f"Repository root: {repo_root}")

        try:
            vault_dir = ensure_vault_exists(repo_root)
            logger.debug(f"Vault directory: {vault_dir}")
        except ValueError as e:
            console.print(f"[red]✗[/red] {e}")
            logger.error(f"Vault directory error: {e}")
            _abort(e)

        with console.status("[bold green]Analyzing vault graph...", spinner="dots"):
            logger.debug("Building vault graph")
            vg = VaultGraph(vault_dir)
            logger.debug("Calculating network statistics")
            stats = vg.get_network_statistics()
            logger.debug("Analyzing link quality")
            quality = vg.analyze_link_quality()

        table = Table(title="Vault Network Statistics", show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", justify="right", style="magenta")

        table.add_row("Total Notes", str(stats["total_notes"]))
        table.add_row("Total Links", str(stats["total_links"]))
        table.add_row("Average Degree", f"{stats['average_degree']:.2f}")
        table.add_row("Network Density", f"{stats['density']:.4f}")
        table.add_row("Connected Components", str(stats["connected_components"]))
        table.add_row("", "")
        table.add_row("Reciprocal Links", str(quality["reciprocal_links"]))
        table.add_row("Unidirectional Links", str(quality["unidirectional_links"]))
        table.add_row(
            "Orphaned Notes", f"{stats['orphaned_notes']} ({quality['orphaned_ratio']:.1%})"
        )
        table.add_row(
            "Isolated Notes", f"{stats['isolated_notes']} ({quality['isolated_ratio']:.1%})"
        )

        console.print(table)

        if hubs:
            hub_notes = vg.get_hub_notes(hubs)
            if hub_notes:
                hub_table = Table(
                    title=f"Top {hubs} Hub Notes", show_header=True, header_style="bold green"
                )
                hub_table.add_column("Note", style="cyan")
                hub_table.add_column("Outgoing Links", justify="right", style="green")

                for note, degree in hub_notes:
                    hub_table.add_row(note, str(degree))

                console.print("\n", hub_table)

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

        logger.success(
            f"Graph statistics complete: {stats['total_notes']} notes, {stats['total_links']} links"
        )

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        logger.exception(f"Graph stats failed with error: {e}")
        _abort(e)


@app.command()
def orphans(
    output: str | None = typer.Option(None, "--output", "-o", help="Write results to file"),
):
    """Find orphaned notes (no incoming or outgoing links).

    Helps identify disconnected content that needs linking.
    """
    from obsidian_vault.utils import ensure_vault_exists

    logger.info("Finding orphaned notes")
    try:
        repo_root = discover_repo_root()

        try:
            vault_dir = ensure_vault_exists(repo_root)
        except ValueError as e:
            console.print(f"[red]✗[/red] {e}")
            logger.error(f"Vault directory error: {e}")
            _abort(e)

        with console.status("[bold green]Finding orphaned notes...", spinner="dots"):
            vg = VaultGraph(vault_dir)
            orphan_notes = vg.get_orphaned_notes()

        if not orphan_notes:
            console.print(
                "[green]✓[/green] No orphaned notes found! All notes have at least one link."
            )
            logger.success("No orphaned notes found")
            return

        logger.warning(f"Found {len(orphan_notes)} orphaned notes")
        logger.debug(f"Orphaned notes: {orphan_notes[:5]}{'...' if len(orphan_notes) > 5 else ''}")

        console.print(f"\n[yellow]Found {len(orphan_notes)} orphaned notes:[/yellow]\n")
        for note in orphan_notes:
            console.print(f"  • {note}")

        if output:
            Path(output).write_text("\n".join(orphan_notes), encoding="utf-8")
            console.print(
                f"\n[green]✓[/green] Wrote {len(orphan_notes)} orphaned notes to {output}"
            )
            logger.info(f"Wrote orphaned notes to {output}")

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        logger.exception(f"Orphans command failed with error: {e}")
        _abort(e)


@app.command()
def broken_links(
    output: str | None = typer.Option(None, "--output", "-o", help="Write results to file"),
):
    """Find notes with broken links (links to non-existent notes).

    Helps maintain vault integrity by identifying missing link targets.
    """
    from obsidian_vault.utils import ensure_vault_exists

    logger.info("Finding broken links")
    try:
        repo_root = discover_repo_root()

        try:
            vault_dir = ensure_vault_exists(repo_root)
        except ValueError as e:
            console.print(f"[red]✗[/red] {e}")
            logger.error(f"Vault directory error: {e}")
            _abort(e)

        with console.status("[bold green]Finding broken links...", spinner="dots"):
            vg = VaultGraph(vault_dir)
            broken = vg.get_broken_links()

        if not broken:
            console.print(
                "[green]✓[/green] No broken links found! All links point to existing notes."
            )
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

        _abort()

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        logger.exception(f"Broken links command failed with error: {e}")
        _abort(e)


@app.command()
def link_report(
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
):
    """Generate comprehensive markdown link health report.

    Creates a detailed report with statistics, orphans, hubs, and authorities.
    """
    from obsidian_vault.utils import ensure_vault_exists

    logger.info("Generating link health report")
    try:
        repo_root = discover_repo_root()

        try:
            vault_dir = ensure_vault_exists(repo_root)
        except ValueError as e:
            console.print(f"[red]✗[/red] {e}")
            logger.error(f"Vault directory error: {e}")
            _abort(e)

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
        _abort(e)


@app.command()
def graph_export(
    output: Annotated[str, typer.Argument(..., help="Output file path")],
    export_format: Annotated[
        ExportFormat | None,
        typer.Option(
            "--format",
            "-f",
            help="Export format (auto-detected from extension if not specified)",
        ),
    ] = None,
):
    """Export vault graph to various formats for external analysis.

    Supports GEXF, GraphML, JSON, and CSV formats.
    """
    from obsidian_vault.utils import ensure_vault_exists, validate_choice

    logger.info(f"Exporting graph to {output}")
    try:
        repo_root = discover_repo_root()

        try:
            vault_dir = ensure_vault_exists(repo_root)
        except ValueError as e:
            console.print(f"[red]✗[/red] {e}")
            logger.error(f"Vault directory error: {e}")
            _abort(e)

        output_path = Path(output)

        if export_format:
            resolved_format = export_format.value
        else:
            format_map = {
                ".gexf": "gexf",
                ".graphml": "graphml",
                ".json": "json",
                ".csv": "csv",
            }
            resolved_format = format_map.get(output_path.suffix.lower(), "gexf")

        try:
            resolved_format = validate_choice(resolved_format, {"gexf", "graphml", "json", "csv"})
        except ValueError as e:
            console.print(f"[red]✗ Error:[/red] {e}")
            _abort(e)

        logger.debug(f"Export format: {resolved_format}")

        with console.status(
            f"[bold green]Exporting graph to {resolved_format.upper()}...", spinner="dots"
        ):
            vg = VaultGraph(vault_dir)
            vg.export_graph_data(output_path, format=resolved_format)

        console.print(
            f"[green]✓[/green] Graph exported to {output_path} (format: {resolved_format})"
        )
        logger.success(f"Graph exported to {output_path} (format: {resolved_format})")

    except ValueError as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        logger.error(f"Invalid export format: {e}")
        _abort(e)
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        logger.exception(f"Graph export failed with error: {e}")
        _abort(e)


@app.command()
def communities(
    algorithm: str = typer.Option(
        "louvain",
        "--algorithm",
        "-a",
        help="Algorithm: louvain, greedy, or label_propagation",
    ),
    min_size: int = typer.Option(2, "--min-size", "-m", help="Minimum community size"),
    top_n: int | None = typer.Option(None, "--top", "-n", help="Show only top N communities"),
    show_notes: bool = typer.Option(False, "--show-notes", help="Show notes in each community"),
    output: str | None = typer.Option(None, "--output", "-o", help="Write results to file"),
):
    """Detect clusters of related notes using graph algorithms.

    Communities are groups of notes that are more densely connected to each
    other than to notes outside the group. Useful for understanding vault
    organization and discovering hidden topic clusters.
    """
    from obsidian_vault.utils import ensure_vault_exists, validate_choice

    try:
        algorithm = validate_choice(algorithm, {"louvain", "greedy", "label_propagation"})
    except ValueError as e:
        console.print(f"[red]✗[/red] {e}")
        _abort(e)

    logger.info(f"Detecting communities using {algorithm} algorithm")
    try:
        repo_root = discover_repo_root()

        try:
            vault_dir = ensure_vault_exists(repo_root)
        except ValueError as e:
            console.print(f"[red]✗[/red] {e}")
            logger.error(f"Vault directory error: {e}")
            _abort(e)

        with console.status("[bold green]Analyzing vault communities...", spinner="dots"):
            logger.debug("Building vault graph")
            vg = VaultGraph(vault_dir)
            logger.debug(f"Detecting communities with algorithm={algorithm}, min_size={min_size}")
            communities_data = cast(
                list[dict[str, Any]], vg.detect_communities(algorithm=algorithm, min_size=min_size)
            )

        if not communities_data:
            console.print("[yellow]⚠[/yellow] No communities found")
            logger.warning("No communities detected")
            return

        if top_n:
            communities_data = communities_data[:top_n]

        logger.success(f"Detected {len(communities_data)} communities")

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
            topics_str = ", ".join([f"{topic} ({count})" for topic, count in comm["topics"][:3]])
            summary_table.add_row(
                str(comm["id"]),
                str(comm["size"]),
                f"{comm['density']:.3f}",
                topics_str or "—",
            )

        console.print(summary_table)

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

        total_notes = sum(c["size"] for c in communities_data)
        avg_size = total_notes / len(communities_data) if communities_data else 0
        avg_density = (
            sum(c["density"] for c in communities_data) / len(communities_data)
            if communities_data
            else 0
        )

        console.print("\n[bold]Statistics:[/bold]")
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
        _abort(e)


@app.command()
def suggest_links(
    note: str | None = typer.Option(None, "--note", "-n", help="Specific note to analyze"),
    top_k: int = typer.Option(5, "--top", "-k", help="Number of suggestions per note"),
    min_similarity: float = typer.Option(
        0.3, "--min-similarity", "-s", help="Minimum similarity threshold (0.0-1.0)"
    ),
    include_existing: bool = typer.Option(
        False, "--include-existing", help="Include already linked notes"
    ),
    output: str | None = typer.Option(None, "--output", "-o", help="Write results to file"),
):
    """Suggest missing links using ML-based content similarity (TF-IDF).

    Uses machine learning to analyze note content and suggest related notes
    that should be linked but currently aren't. Based on TF-IDF vectorization
    and cosine similarity.
    """
    from obsidian_vault.utils import ensure_vault_exists

    logger.info("Analyzing notes for link suggestions using ML")
    try:
        repo_root = discover_repo_root()

        try:
            vault_dir = ensure_vault_exists(repo_root)
        except ValueError as e:
            console.print(f"[red]✗[/red] {e}")
            logger.error(f"Vault directory error: {e}")
            _abort(e)

        with console.status("[bold green]Analyzing note content with TF-IDF...", spinner="dots"):
            logger.debug("Building vault graph")
            vg = VaultGraph(vault_dir)
            logger.debug(
                f"Generating link suggestions: note={note}, top_k={top_k}, "
                f"min_similarity={min_similarity}"
            )
            suggestions: dict[str, list[tuple[str, float]]]
            suggestions = vg.suggest_links(
                note_name=note,
                top_k=top_k,
                min_similarity=min_similarity,
                exclude_existing=not include_existing,
            )

        if not suggestions:
            console.print("[yellow]⚠[/yellow] No link suggestions found")
            logger.warning("No link suggestions generated")
            return

        stats: dict[str, Any] = vg.analyze_link_predictions(suggestions)
        logger.success(
            f"Generated {stats['total_suggestions']} suggestions "
            f"for {stats['total_notes_analyzed']} notes"
        )

        if note and note in suggestions:
            # Show suggestions for specific note
            console.print(f"\n[bold cyan]Link Suggestions for {note}[/bold cyan] (top {top_k})\n")

            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("Rank", style="cyan", width=6)
            table.add_column("Suggested Note", style="green")
            table.add_column("Similarity", justify="right", style="yellow")

            for i, (suggested_note, similarity) in enumerate(suggestions[note], 1):
                table.add_row(str(i), suggested_note, f"{similarity:.3f}")

            console.print(table)

        else:
            console.print(
                f"\n[bold cyan]Link Suggestions Summary[/bold cyan] "
                f"(showing top {min(10, len(suggestions))} notes with suggestions)\n"
            )

            sorted_notes = sorted(suggestions.items(), key=lambda x: len(x[1]), reverse=True)[:10]

            for note_name, note_suggestions in sorted_notes:
                if not note_suggestions:
                    continue

                console.print(f"\n[bold]{note_name}[/bold]")
                for i, (suggested, sim) in enumerate(note_suggestions, 1):
                    console.print(f"  {i}. {suggested} (similarity: {sim:.3f})")

        console.print("\n[bold]Statistics:[/bold]")
        console.print(f"  Notes analyzed: {stats['total_notes_analyzed']}")
        console.print(f"  Total suggestions: {stats['total_suggestions']}")
        console.print(f"  Avg suggestions per note: {stats['avg_suggestions_per_note']:.1f}")
        console.print(f"  Avg similarity: {stats['avg_similarity']:.3f}")
        console.print(
            f"  Similarity range: {stats['min_similarity']:.3f} - {stats['max_similarity']:.3f}"
        )

        if output:
            output_lines = [
                "# Link Suggestions (ML-Based)\n\n",
                "**Algorithm**: TF-IDF + Cosine Similarity\n",
                f"**Minimum Similarity**: {min_similarity}\n",
                f"**Top K**: {top_k}\n\n",
                "## Statistics\n\n",
                f"- **Notes Analyzed**: {stats['total_notes_analyzed']}\n",
                f"- **Total Suggestions**: {stats['total_suggestions']}\n",
                f"- **Avg Suggestions/Note**: {stats['avg_suggestions_per_note']:.1f}\n",
                f"- **Avg Similarity**: {stats['avg_similarity']:.3f}\n\n",
                "---\n\n",
            ]

            sorted_all = sorted(suggestions.items())

            for note_name, note_sugg in sorted_all:
                if not note_sugg:
                    continue

                output_lines.append(f"## {note_name}\n\n")
                for i, (suggested, sim) in enumerate(note_sugg, 1):
                    output_lines.append(f"{i}. [[{suggested}]] (similarity: {sim:.3f})\n")
                output_lines.append("\n")

            Path(output).write_text("".join(output_lines), encoding="utf-8")
            console.print(f"\n[green]✓[/green] Link suggestions written to {output}")
            logger.info(f"Link suggestions written to {output}")

        logger.success("Link suggestion analysis complete")

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        logger.exception(f"Link suggestion failed: {e}")
        _abort(e)


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
        10,
        "--max-iterations",
        "-m",
        help="Maximum fix iterations per note",
    ),
    completion_mode: str = typer.Option(
        "standard",
        "--completion-mode",
        "-c",
        help="Completion strictness: strict (no issues), standard (allow warnings), permissive (allow some errors)",
    ),
    max_concurrent: int = typer.Option(
        5,
        "--max-concurrent",
        help="Maximum number of notes to process concurrently",
    ),
    backup: bool = typer.Option(
        True,
        "--backup/--no-backup",
        help="Create backups before modifying files",
    ),
    report: str | None = typer.Option(
        None,
        "--report",
        "-r",
        help="Write detailed report to file",
    ),
):
    """Review and fix notes using LLM (PydanticAI + LangGraph).

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
        import os

        if not os.getenv("OPENROUTER_API_KEY"):
            console.print(
                "[red]✗[/red] OPENROUTER_API_KEY environment variable not set\n"
                "Get your API key from https://openrouter.ai/keys"
            )
            _abort()

        repo_root = discover_repo_root()
        vault_dir = repo_root / "InterviewQuestions"

        if not vault_dir.exists():
            console.print("[red]✗[/red] InterviewQuestions directory not found")
            _abort()

        from obsidian_vault.llm_review import CompletionMode, create_review_graph

        try:
            mode = CompletionMode(completion_mode.lower())
        except ValueError:
            console.print(
                f"[red]✗[/red] Invalid completion mode: {completion_mode}\n"
                f"Valid options: strict, standard, permissive"
            )
            _abort()

        if pattern.startswith("InterviewQuestions/"):
            search_pattern = pattern.replace("InterviewQuestions/", "", 1)
            notes = list(vault_dir.glob(search_pattern))
            notes = [n for n in notes if n.suffix == ".md" and n.is_file()]
        else:
            from obsidian_vault.utils.common import collect_validatable_files

            notes = list(collect_validatable_files(repo_root / pattern.split("/")[0]))

        if not notes:
            console.print(f"[yellow]⚠[/yellow] No notes found matching pattern: {pattern}")
            raise typer.Exit(code=0)

        console.print(f"\n[bold]Found {len(notes)} note(s) to review[/bold]\n")

        if dry_run:
            console.print("[yellow]⚠[/yellow] DRY RUN MODE - No files will be modified\n")

        with console.status("[bold green]Initializing LLM review system...", spinner="dots"):
            review_graph = create_review_graph(
                vault_root=vault_dir,
                max_iterations=max_iterations,
                dry_run=dry_run,
                completion_mode=mode,
            )

        results: list[tuple[Path, Any]] = []
        error_results: list[tuple[Path, Exception]] = []

        async def process_all():
            """Process notes in parallel with concurrency limit."""
            semaphore = asyncio.Semaphore(max_concurrent)

            async def process_one(note_path: Path) -> tuple[Path, Any | None, Exception | None]:
                """Process a single note with semaphore control."""
                async with semaphore:
                    console.print(f"[cyan]Processing:[/cyan] {note_path.relative_to(repo_root)}")
                    try:
                        state = await review_graph.process_note(note_path)

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
                            sanitized_text = sanitize_text_for_yaml(state.current_text)
                            if sanitized_text != state.current_text:
                                logger.warning(
                                    f"Sanitized {len(state.current_text) - len(sanitized_text)} "
                                    f"invalid character(s) from {note_path.name}"
                                )

                            # Use atomic write with optional backup
                            try:
                                atomic_write(
                                    note_path,
                                    sanitized_text,
                                    encoding="utf-8",
                                    create_backup=backup,
                                )
                                console.print(f"  [dim]Saved changes to {note_path.name}[/dim]")
                                if backup:
                                    console.print(
                                        f"  [dim]Backup created: {note_path.name}.backup[/dim]"
                                    )
                            except Exception as e:  # pragma: no cover - disk errors
                                console.print(
                                    f"  [red]✗[/red] Failed to save {note_path.name}: {e}"
                                )
                                logger.error(f"Failed to write {note_path}: {e}")

                        console.print()
                        return (note_path, state, None)
                    except Exception as exc:
                        console.print(f"  [red]✗[/red] Error: {exc}")
                        logger.exception("LLM review crashed for {}", note_path)
                        console.print()
                        return (note_path, None, exc)

            console.print(f"[bold]Processing up to {max_concurrent} notes concurrently[/bold]\n")
            tasks = [process_one(note_path) for note_path in notes]
            results_list = await asyncio.gather(*tasks)

            for note_path, state, exc in results_list:
                if exc:
                    error_results.append((note_path, exc))
                else:
                    results.append((note_path, state))

        asyncio.run(process_all())

        total = len(results) + len(error_results)
        modified = sum(1 for _, state in results if state.changed)
        errors = len(error_results) + sum(1 for _, state in results if state.error)
        unchanged = max(total - modified - errors, 0)

        table = Table(title="LLM Review Summary", show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", justify="right", style="magenta")

        table.add_row("Notes Processed", str(total))
        table.add_row("Modified", f"[{'yellow' if dry_run else 'green'}]{modified}[/]")
        table.add_row("Errors", f"[{'red' if errors > 0 else 'green'}]{errors}[/]")
        table.add_row("Unchanged", str(unchanged))

        console.print(table)

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

            if error_results:
                report_lines.append("## Notes that failed before producing a state\n\n")
                for note_path, exc in error_results:
                    report_lines.append(f"### {note_path.relative_to(repo_root)}\n\n")
                    report_lines.append("**Changed**: False\n")
                    report_lines.append("**Iterations**: 0\n")
                    report_lines.append("**Final issues**: 0\n")
                    report_lines.append(f"**Error**: {exc}\n")
                    report_lines.append("\n---\n\n")

            Path(report).write_text("".join(report_lines), encoding="utf-8")
            console.print(f"\n[green]✓[/green] Report written to {report}")

        message = f"LLM review complete: {total} notes, {modified} modified, {errors} errors"
        if errors > 0:
            logger.warning(message)
        else:
            logger.success(message)

        if errors > 0:
            _abort()

    except ImportError as e:
        console.print(
            f"[red]✗ Error:[/red] LLM review dependencies not installed\n"
            f"Install with: pip install pydantic-ai langgraph\n"
            f"Details: {e}"
        )
        _abort(e)
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        logger.exception(f"LLM review failed: {e}")
        _abort(e)


@app.command("qa-ingest")
def qa_ingest(
    url: str = typer.Argument(..., help="URL of the article to convert into Q&A notes"),
    max_cards: int = typer.Option(3, "--max-cards", help="Maximum number of cards to generate"),
    dry_run: bool = typer.Option(
        False,
        "--dry-run/--no-dry-run",
        help="If enabled, do not write files or run review; only show a preview",
    ),
    completion_mode: str = typer.Option(
        "standard",
        "--completion-mode",
        help="Completion strictness for automated review (strict | standard | permissive)",
    ),
    processing_profile: str = typer.Option(
        "balanced",
        "--profile",
        help="Processing profile for review (balanced | stability | thorough)",
    ),
    review_iterations: int = typer.Option(
        6,
        "--review-iterations",
        help="Maximum number of automated fix iterations during review",
    ),
):
    """Generate new bilingual notes from an external article using Firecrawl + LLM."""
    from obsidian_vault.exceptions import ValidationError

    # Validate inputs
    try:
        url = validate_url(url)
    except ValidationError as e:
        console.print(f"[red]✗[/red] Invalid URL: {e}")
        _abort(e)

    try:
        max_cards = validate_integer(max_cards, min_value=1, max_value=5, param_name="max_cards")
    except ValidationError as e:
        console.print(f"[red]✗[/red] {e}")
        _abort(e)

    if not os.getenv("FIRECRAWL_API_KEY"):
        console.print(
            "[red]✗[/red] FIRECRAWL_API_KEY environment variable not set."
            "\nCreate a Firecrawl account and set the API key to fetch articles."
        )
        _abort()

    if not os.getenv("OPENROUTER_API_KEY"):
        console.print(
            "[red]✗[/red] OPENROUTER_API_KEY environment variable not set."
            "\nObtain an API key from https://openrouter.ai/keys and export it before running."
        )
        _abort()

    try:
        mode = CompletionMode(completion_mode.lower())
    except ValueError:
        console.print(
            f"[red]✗[/red] Invalid completion mode: {completion_mode}\n"
            "Valid options: strict, standard, permissive"
        )
        _abort()

    try:
        profile = ProcessingProfile(processing_profile.lower())
    except ValueError:
        console.print(
            f"[red]✗[/red] Invalid processing profile: {processing_profile}\n"
            "Valid options: balanced, stability, thorough"
        )
        _abort()

    console.print(Panel.fit(f"[bold]Fetching and processing article:[/bold]\n{url}"))
    workflow = NoteIngestionWorkflow()
    config = WorkflowConfig(
        max_cards=max_cards,
        dry_run=dry_run,
        completion_mode=mode,
        processing_profile=profile,
        review_iterations=review_iterations,
    )

    try:
        result = workflow.run(url, config=config)
    except Exception as exc:  # pragma: no cover - top-level workflow guard
        console.print(f"[red]✗ Error:[/red] {exc}")
        logger.exception("Q&A ingestion workflow failed: {}", exc)
        _abort(exc)

    created_count = len(result.created_paths)
    duplicates_count = len(result.skipped_duplicates)
    console.print()
    summary_table = Table(title="Q&A Ingestion Summary", show_header=True, header_style="bold cyan")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="magenta", justify="right")
    summary_table.add_row("Generated cards", str(len(result.generated_cards)))
    summary_table.add_row("Written notes", str(created_count))
    summary_table.add_row("Skipped duplicates", str(duplicates_count))
    summary_table.add_row("Dry run", "Yes" if dry_run else "No")
    console.print(summary_table)

    if result.created_paths:
        console.print("\n[bold]Created notes:[/bold]")
        for path in result.created_paths:
            console.print(f"  • {path}")

    if result.skipped_duplicates:
        console.print("\n[yellow]⚠[/yellow] Skipped potential duplicates:")
        for slug in result.skipped_duplicates:
            console.print(f"  • {slug}")

    if dry_run:
        console.print(
            "\n[yellow]⚠[/yellow] Dry run mode was enabled. No files were written and review did not run."
        )

    logger.success("Q&A ingestion completed", created=created_count, duplicates=duplicates_count)


@app.command("qa-gap-analysis")
def qa_gap_analysis(
    preview_only: bool = typer.Option(
        False,
        "--preview-only/--create-notes",
        help="Only generate the report without writing new notes",
    ),
    auto_create: bool = typer.Option(
        False,
        "--auto-create",
        help="Skip the confirmation prompt and immediately create notes",
    ),
    completion_mode: str = typer.Option(
        "standard",
        "--completion-mode",
        help="Completion strictness for automated review (strict | standard | permissive)",
    ),
    processing_profile: str = typer.Option(
        "balanced",
        "--profile",
        help="Processing profile for review (balanced | stability | thorough)",
    ),
    review_iterations: int = typer.Option(
        6,
        "--review-iterations",
        help="Maximum number of automated fix iterations during review",
    ),
):
    """Analyze vault coverage, propose missing questions, and optionally create notes."""
    if not os.getenv("OPENROUTER_API_KEY"):
        console.print(
            "[red]✗[/red] OPENROUTER_API_KEY environment variable not set."
            "\nObtain an API key from https://openrouter.ai/keys and export it before running."
        )
        _abort()

    try:
        mode = CompletionMode(completion_mode.lower())
    except ValueError:
        console.print(
            f"[red]✗[/red] Invalid completion mode: {completion_mode}\n"
            "Valid options: strict, standard, permissive"
        )
        _abort()

    try:
        profile = ProcessingProfile(processing_profile.lower())
    except ValueError:
        console.print(
            f"[red]✗[/red] Invalid processing profile: {processing_profile}\n"
            "Valid options: balanced, stability, thorough"
        )
        _abort()

    workflow = GapAnalysisWorkflow()
    config = GapWorkflowConfig(
        dry_run=preview_only,
        auto_create=auto_create,
        completion_mode=mode,
        processing_profile=profile,
        review_iterations=review_iterations,
    )

    console.print("[bold]Analyzing vault coverage. This may take a moment...[/bold]")

    try:
        result = workflow.analyze()
    except Exception as exc:  # pragma: no cover - top-level workflow guard
        console.print(f"[red]✗ Error:[/red] {exc}")
        logger.exception("Gap analysis workflow failed: {}", exc)
        _abort(exc)

    console.print()
    summary_table = Table(title="Coverage Gap Report", show_header=True, header_style="bold cyan")
    summary_table.add_column("Topic", style="cyan")
    summary_table.add_column("Rationale", style="magenta")
    summary_table.add_column("Proposed", justify="right")
    for topic in result.topics:
        rationale = topic.rationale
        if len(rationale) > 90:
            rationale = rationale[:87] + "..."
        summary_table.add_row(topic.topic, rationale, str(len(topic.cards)))
    console.print(summary_table)

    for topic in result.topics:
        console.print(f"\n[bold]{topic.topic} recommendations:[/bold]")
        for card in topic.cards:
            console.print(
                f"  • {card.slug} — {card.title_en} "
                f"(difficulty={card.difficulty}, kind={card.question_kind})"
            )

    if result.duplicates:
        console.print("\n[yellow]⚠[/yellow] Potential duplicates skipped:")
        for slug in result.duplicates:
            console.print(f"  • {slug}")

    console.print(
        f"\n[bold]Total recommendations:[/bold] {result.total_recommendations()}"
        f" from {result.total_notes} existing notes"
    )

    if not result.unique_cards:
        console.print("\n[yellow]⚠[/yellow] No unique notes to create after duplicate filtering")
        raise typer.Exit(code=0)

    if preview_only:
        console.print(
            "\n[yellow]⚠[/yellow] Preview-only mode enabled. Notes were not created and review did not run."
        )
        return

    should_create = auto_create or typer.confirm(
        "\nCreate the proposed notes and run automated review now?"
    )
    if not should_create:
        console.print("\n[yellow]⚠[/yellow] Creation cancelled by user. Report preserved above.")
        return

    try:
        apply_result = workflow.apply(result, config)
    except Exception as exc:  # pragma: no cover - top-level workflow guard
        console.print(f"[red]✗ Error:[/red] {exc}")
        logger.exception("Failed to create notes from gap analysis: {}", exc)
        _abort(exc)

    if apply_result.created_paths:
        console.print("\n[bold]Created notes:[/bold]")
        for path in apply_result.created_paths:
            console.print(f"  • {path}")

    console.print(
        f"\n[green]✓[/green] Gap analysis flow completed with {apply_result.reviewed_notes} notes reviewed"
    )
    logger.success(
        "Gap analysis workflow completed",
        created=len(apply_result.created_paths),
        reviewed=apply_result.reviewed_notes,
    )


if __name__ == "__main__":
    app()
