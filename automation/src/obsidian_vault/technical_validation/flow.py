"""Technical validation workflow orchestrated with LangChain agents."""

from __future__ import annotations

import io
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

from langchain.agents import AgentExecutor
from loguru import logger
from ruamel.yaml import YAML

from obsidian_vault.utils import (
    TaxonomyLoader,
    build_note_index,
    collect_validatable_files,
    discover_repo_root,
    ensure_vault_exists,
    parse_note,
)
from obsidian_vault.validators import Severity, ValidatorRegistry
from obsidian_vault.validators.base import ValidationIssue

from .agents import TechnicalAgentConfig, build_technical_validation_agent, extract_agent_payload

_yaml = YAML()
_yaml.default_flow_style = False
_yaml.allow_unicode = True


def _frontmatter_to_text(frontmatter: dict) -> str:
    """Serialize frontmatter to a readable YAML string for agent context."""

    buffer = io.StringIO()
    _yaml.dump(frontmatter or {}, buffer)
    return buffer.getvalue()


@dataclass(slots=True)
class TechnicalValidationFinding:
    """Detailed issue description enriched with agent guidance."""

    validator: str
    issue: ValidationIssue
    fix: str | None = None
    references: list[str] = field(default_factory=list)


@dataclass(slots=True)
class TechnicalValidationReport:
    """Aggregated validation report for a single note."""

    path: Path
    findings: list[TechnicalValidationFinding] = field(default_factory=list)
    summary: str | None = None

    @property
    def highest_severity(self) -> Severity | None:
        """Return the most severe issue for quick triage."""

        if not self.findings:
            return None
        severity_order = {
            Severity.CRITICAL: 4,
            Severity.ERROR: 3,
            Severity.WARNING: 2,
            Severity.INFO: 1,
        }
        return max(self.findings, key=lambda finding: severity_order[finding.issue.severity]).issue.severity


class TechnicalValidationFlow:
    """End-to-end pipeline for performing technical validation across notes."""

    def __init__(
        self,
        *,
        repo_root: Path,
        vault_root: Path,
        taxonomy_loader: TaxonomyLoader,
        note_index: set[str],
        agent: AgentExecutor | None = None,
    ) -> None:
        self.repo_root = repo_root
        self.vault_root = vault_root
        self.taxonomy_loader = taxonomy_loader
        self.note_index = note_index
        self.agent = agent or build_technical_validation_agent(config=TechnicalAgentConfig())

    @classmethod
    def from_repo(
        cls,
        repo_root: Path | None = None,
        *,
        agent: AgentExecutor | None = None,
    ) -> "TechnicalValidationFlow":
        """Construct the flow by discovering repository metadata."""

        discovered_root = repo_root or discover_repo_root()
        vault_root = ensure_vault_exists(discovered_root)
        taxonomy_loader = TaxonomyLoader(discovered_root)
        _ = taxonomy_loader.load()
        note_index = build_note_index(vault_root)
        logger.debug(
            "Initialized technical validation flow: repo={}, vault={}, notes={}",
            discovered_root,
            vault_root,
            len(note_index),
        )
        return cls(
            repo_root=discovered_root,
            vault_root=vault_root,
            taxonomy_loader=taxonomy_loader,
            note_index=note_index,
            agent=agent,
        )

    def validate_all(self) -> list[TechnicalValidationReport]:
        """Run validation for every note in the vault."""

        targets = collect_validatable_files(self.vault_root)
        return self.validate_paths(targets)

    def validate_paths(self, paths: Sequence[Path]) -> list[TechnicalValidationReport]:
        """Run validation for a provided set of note paths."""

        reports: list[TechnicalValidationReport] = []
        for note_path in paths:
            report = self._validate_single(note_path)
            if report.findings:
                reports.append(report)
        return reports

    def _validate_single(self, note_path: Path) -> TechnicalValidationReport:
        """Validate a single note returning detailed findings."""

        logger.debug("Validating note: {}", note_path)
        frontmatter, body = parse_note(note_path)
        validators = ValidatorRegistry.create_validators(
            content=body,
            frontmatter=frontmatter,
            path=str(note_path),
            taxonomy=self.taxonomy_loader,
            vault_root=self.vault_root,
            note_index=self.note_index,
        )

        findings: list[TechnicalValidationFinding] = []
        for validator in validators:
            summary = validator.validate()
            for issue in summary.issues:
                findings.append(
                    TechnicalValidationFinding(
                        validator=validator.__class__.__name__,
                        issue=issue,
                    )
                )

        if not findings:
            logger.debug("No validator issues detected for {}", note_path)
            return TechnicalValidationReport(path=note_path)

        enriched_findings, summary_text = self._call_agent(note_path, frontmatter, body, findings)
        return TechnicalValidationReport(path=note_path, findings=enriched_findings, summary=summary_text)

    def _call_agent(
        self,
        note_path: Path,
        frontmatter: dict,
        body: str,
        findings: list[TechnicalValidationFinding],
    ) -> tuple[list[TechnicalValidationFinding], str | None]:
        """Enrich validator findings using the LangChain agent."""

        issues_payload = [
            {
                "validator": finding.validator,
                "severity": finding.issue.severity.value,
                "message": finding.issue.message,
                "field": finding.issue.field,
                "line": finding.issue.line,
            }
            for finding in findings
        ]
        issues_json = json.dumps(issues_payload, ensure_ascii=False, indent=2)
        excerpt = body[:2000]
        frontmatter_text = _frontmatter_to_text(frontmatter)

        agent_inputs = {
            "input": "Provide issue analysis and fixes.",
            "chat_history": [],
            "note_path": str(note_path),
            "topic": frontmatter.get("topic", "unknown"),
            "frontmatter": frontmatter_text,
            "issues_json": issues_json,
            "content_excerpt": excerpt,
        }

        logger.debug("Invoking technical validation agent for {}", note_path)
        result = self.agent.invoke(agent_inputs)
        payload = extract_agent_payload(result)

        enriched_findings = self._merge_agent_guidance(findings, payload.get("issues", []))
        summary_text = payload.get("summary")
        return enriched_findings, str(summary_text) if summary_text is not None else None

    def _merge_agent_guidance(
        self,
        findings: list[TechnicalValidationFinding],
        agent_issues: Iterable[dict[str, object]],
    ) -> list[TechnicalValidationFinding]:
        """Merge agent-provided fixes with raw validator findings."""

        guidance_by_key: dict[tuple[str, str], dict[str, object]] = {}
        for entry in agent_issues:
            validator = str(entry.get("validator", ""))
            problem_message = str(entry.get("problem", ""))
            fix = entry.get("fix")
            references = entry.get("references")
            key = (validator, problem_message)
            guidance_by_key[key] = {
                "fix": str(fix) if fix is not None else None,
                "references": [str(ref) for ref in references]
                if isinstance(references, (list, tuple))
                else [],
            }

        merged: list[TechnicalValidationFinding] = []
        for finding in findings:
            key = (finding.validator, finding.issue.message)
            guidance = guidance_by_key.get(key)
            if guidance:
                merged.append(
                    TechnicalValidationFinding(
                        validator=finding.validator,
                        issue=finding.issue,
                        fix=guidance["fix"],
                        references=guidance["references"],
                    )
                )
            else:
                merged.append(finding)
        return merged


def run_technical_validation(
    *,
    repo_root: Path | None = None,
    agent: AgentExecutor | None = None,
    paths: Sequence[Path] | None = None,
) -> list[TechnicalValidationReport]:
    """Convenience wrapper for running the technical validation flow."""

    flow = TechnicalValidationFlow.from_repo(repo_root, agent=agent)
    if paths is not None:
        return flow.validate_paths(paths)
    return flow.validate_all()
