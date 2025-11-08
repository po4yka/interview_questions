"""Graph analytics and integrity checks using obsidiantools.

This module provides advanced vault analysis using obsidiantools library:
- Link/backlink graph analysis
- Orphaned note detection
- Hub/authority identification
- Metadata extraction
- Network statistics
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import networkx as nx
import pandas as pd
from obsidiantools.api import Vault


class VaultGraph:
    """Wrapper around obsidiantools Vault for graph analytics."""

    def __init__(self, vault_path: Path):
        """
        Initialize vault graph analyzer.

        Args:
            vault_path: Path to the Obsidian vault directory
        """
        self.vault_path = vault_path
        self.vault = Vault(vault_path).connect()
        self.graph = self.vault.graph

    def get_orphaned_notes(self) -> list[str]:
        """
        Find notes with no incoming or outgoing links.

        Returns:
            List of note names that are orphaned
        """
        orphans = []
        for node in self.graph.nodes():
            in_degree = self.graph.in_degree(node)
            out_degree = self.graph.out_degree(node)
            if in_degree == 0 and out_degree == 0:
                orphans.append(node)
        return sorted(orphans)

    def get_isolated_notes(self) -> list[str]:
        """
        Find notes with no incoming links (but may have outgoing links).

        Returns:
            List of note names with no backlinks
        """
        isolated = []
        for node in self.graph.nodes():
            if self.graph.in_degree(node) == 0:
                isolated.append(node)
        return sorted(isolated)

    def get_hub_notes(self, top_n: int = 10) -> list[tuple[str, int]]:
        """
        Find notes with the most outgoing links (hubs).

        Args:
            top_n: Number of top hubs to return

        Returns:
            List of (note_name, out_degree) tuples, sorted by out_degree descending
        """
        out_degrees = [(node, self.graph.out_degree(node)) for node in self.graph.nodes()]
        out_degrees.sort(key=lambda x: x[1], reverse=True)
        return out_degrees[:top_n]

    def get_authority_notes(self, top_n: int = 10) -> list[tuple[str, int]]:
        """
        Find notes with the most incoming links (authorities).

        Args:
            top_n: Number of top authorities to return

        Returns:
            List of (note_name, in_degree) tuples, sorted by in_degree descending
        """
        in_degrees = [(node, self.graph.in_degree(node)) for node in self.graph.nodes()]
        in_degrees.sort(key=lambda x: x[1], reverse=True)
        return in_degrees[:top_n]

    def get_broken_links(self) -> dict[str, list[str]]:
        """
        Find broken links (links to non-existent notes).

        Returns:
            Dictionary mapping note names to list of broken link targets
        """
        all_notes = set(self.graph.nodes())
        broken = {}

        for source_note in self.graph.nodes():
            broken_targets = []
            for target_note in self.graph.successors(source_note):
                if target_note not in all_notes:
                    broken_targets.append(target_note)
            if broken_targets:
                broken[source_note] = broken_targets

        return broken

    def get_network_statistics(self) -> dict[str, int | float]:
        """
        Calculate basic network statistics.

        Returns:
            Dictionary with network metrics
        """
        graph = self.graph

        stats = {
            "total_notes": graph.number_of_nodes(),
            "total_links": graph.number_of_edges(),
            "orphaned_notes": len(self.get_orphaned_notes()),
            "isolated_notes": len(self.get_isolated_notes()),
        }

        # Average degree
        if graph.number_of_nodes() > 0:
            total_degree = sum(dict(graph.degree()).values())
            stats["average_degree"] = total_degree / graph.number_of_nodes()
        else:
            stats["average_degree"] = 0.0

        # Density (actual edges / possible edges)
        stats["density"] = nx.density(graph)

        # Connected components (weakly connected for directed graph)
        stats["connected_components"] = nx.number_weakly_connected_components(graph)

        return stats

    def get_strongly_connected_components(self) -> list[list[str]]:
        """
        Find strongly connected components (circular reference clusters).

        Returns:
            List of components, each component is a list of note names
        """
        sccs = list(nx.strongly_connected_components(self.graph))
        # Filter out single-node components
        sccs = [list(component) for component in sccs if len(component) > 1]
        # Sort by size descending
        sccs.sort(key=len, reverse=True)
        return sccs

    def get_shortest_path(self, source: str, target: str) -> list[str] | None:
        """
        Find shortest path between two notes.

        Args:
            source: Source note name
            target: Target note name

        Returns:
            List of note names forming the path, or None if no path exists
        """
        try:
            return nx.shortest_path(self.graph, source, target)
        except (nx.NodeNotFound, nx.NetworkXNoPath):
            return None

    def get_notes_by_tag(self, tag: str) -> list[str]:
        """
        Find all notes with a specific tag.

        Args:
            tag: Tag to search for (without #)

        Returns:
            List of note names with the tag
        """
        notes_with_tag = []

        if hasattr(self.vault, "get_note_metadata"):
            for note_name in self.graph.nodes():
                metadata = self.vault.get_note_metadata(note_name)
                if metadata and "tags" in metadata:
                    tags = metadata.get("tags", [])
                    if tag in tags or f"#{tag}" in tags:
                        notes_with_tag.append(note_name)

        return sorted(notes_with_tag)

    def export_graph_data(self, output_path: Path, format: str = "gexf") -> None:
        """
        Export graph to various formats for external analysis.

        Args:
            output_path: Path to save the exported graph
            format: Export format - 'gexf', 'graphml', 'json', 'csv'
        """
        if format == "gexf":
            nx.write_gexf(self.graph, str(output_path))
        elif format == "graphml":
            nx.write_graphml(self.graph, str(output_path))
        elif format == "json":
            import json

            data = nx.node_link_data(self.graph)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        elif format == "csv":
            # Export as edge list
            edges_df = pd.DataFrame(
                [(u, v) for u, v in self.graph.edges()], columns=["source", "target"]
            )
            edges_df.to_csv(output_path, index=False)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def analyze_link_quality(self) -> dict[str, any]:
        """
        Analyze link quality and patterns.

        Returns:
            Dictionary with link quality metrics
        """
        stats = self.get_network_statistics()

        # Reciprocal links (bidirectional connections)
        reciprocal_count = 0
        for u, v in self.graph.edges():
            if self.graph.has_edge(v, u):
                reciprocal_count += 1

        # Since we count both directions, divide by 2
        reciprocal_pairs = reciprocal_count // 2

        quality = {
            "total_links": stats["total_links"],
            "reciprocal_links": reciprocal_pairs,
            "unidirectional_links": stats["total_links"] - (reciprocal_pairs * 2),
            "orphaned_ratio": (
                stats["orphaned_notes"] / stats["total_notes"] if stats["total_notes"] > 0 else 0
            ),
            "isolated_ratio": (
                stats["isolated_notes"] / stats["total_notes"] if stats["total_notes"] > 0 else 0
            ),
        }

        return quality


def generate_link_health_report(vault_path: Path) -> str:
    """
    Generate a comprehensive link health report.

    Args:
        vault_path: Path to the Obsidian vault

    Returns:
        Markdown-formatted health report
    """
    vg = VaultGraph(vault_path)
    stats = vg.get_network_statistics()
    quality = vg.analyze_link_quality()
    orphans = vg.get_orphaned_notes()
    hubs = vg.get_hub_notes(10)
    authorities = vg.get_authority_notes(10)
    broken = vg.get_broken_links()

    report_lines = [
        "# Vault Link Health Report",
        "",
        "## Network Statistics",
        "",
        f"- **Total Notes**: {stats['total_notes']}",
        f"- **Total Links**: {stats['total_links']}",
        f"- **Average Degree**: {stats['average_degree']:.2f}",
        f"- **Network Density**: {stats['density']:.4f}",
        f"- **Connected Components**: {stats['connected_components']}",
        "",
        "## Link Quality",
        "",
        f"- **Reciprocal Links**: {quality['reciprocal_links']}",
        f"- **Unidirectional Links**: {quality['unidirectional_links']}",
        f"- **Orphaned Notes**: {stats['orphaned_notes']} ({quality['orphaned_ratio']:.1%})",
        f"- **Isolated Notes**: {stats['isolated_notes']} ({quality['isolated_ratio']:.1%})",
        "",
    ]

    if orphans:
        report_lines.extend(
            [
                "## Orphaned Notes (No Links)",
                "",
                "Notes with no incoming or outgoing links:",
                "",
            ]
        )
        for note in orphans[:20]:  # Limit to top 20
            report_lines.append(f"- {note}")
        if len(orphans) > 20:
            report_lines.append(f"\n_...and {len(orphans) - 20} more_")
        report_lines.append("")

    if hubs:
        report_lines.extend(
            [
                "## Top Hub Notes (Most Outgoing Links)",
                "",
            ]
        )
        for note, degree in hubs:
            report_lines.append(f"- **{note}**: {degree} outgoing links")
        report_lines.append("")

    if authorities:
        report_lines.extend(
            [
                "## Top Authority Notes (Most Incoming Links)",
                "",
            ]
        )
        for note, degree in authorities:
            report_lines.append(f"- **{note}**: {degree} incoming links")
        report_lines.append("")

    if broken:
        report_lines.extend(
            [
                "## Broken Links",
                "",
                "Notes with links to non-existent targets:",
                "",
            ]
        )
        for source, targets in list(broken.items())[:20]:  # Limit to top 20
            report_lines.append(f"- **{source}**:")
            for target in targets:
                report_lines.append(f"  - `{target}` (missing)")
        if len(broken) > 20:
            report_lines.append(f"\n_...and {len(broken) - 20} more notes with broken links_")
        report_lines.append("")

    return "\n".join(report_lines)
