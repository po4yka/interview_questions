from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

pytest.importorskip("langchain", reason="LangChain is required for technical validation agents")
pytest.importorskip("langchain_openai", reason="LangChain OpenAI bindings are required")

from obsidian_vault.technical_validation import TechnicalValidationFlow
from obsidian_vault.validators import Severity, ValidatorRegistry
from obsidian_vault.validators.base import BaseValidator


class DummyValidator(BaseValidator):
    """Simple validator that always raises one issue for testing."""

    def validate(self):  # type: ignore[override]
        self.add_issue(Severity.ERROR, "Dummy problem detected", field="title", line=1)
        return self._summary


class StubAgent:
    """Agent stub returning deterministic JSON payloads."""

    def __init__(self) -> None:
        self.invocations: list[dict[str, object]] = []

    def invoke(self, inputs: dict[str, object]) -> dict[str, object]:
        self.invocations.append(inputs)
        issues = json.loads(inputs["issues_json"])  # type: ignore[index]
        payload = {
            "summary": "Resolve the dummy validator findings.",
            "issues": [
                {
                    "validator": issues[0]["validator"],
                    "problem": issues[0]["message"],
                    "severity": issues[0]["severity"],
                    "fix": "Update the title field to satisfy the validator.",
                    "references": ["https://example.com/docs/dummy"],
                }
            ],
        }
        return {"output": json.dumps(payload)}


def test_technical_validation_flow_enriches_findings(tmp_path):
    original_validators = ValidatorRegistry.get_all_validators()
    ValidatorRegistry.clear()
    ValidatorRegistry.register(DummyValidator)

    note_path = tmp_path / "note.md"
    note_path.write_text(
        """---\ntitle: Sample\ntopic: algorithms\n---\nSample body content.\n""",
        encoding="utf-8",
    )

    agent = StubAgent()
    flow = TechnicalValidationFlow(
        repo_root=tmp_path,
        vault_root=tmp_path,
        taxonomy_loader=SimpleNamespace(load=lambda: None),
        note_index={note_path.name},
        agent=agent,  # type: ignore[arg-type]
    )

    try:
        reports = flow.validate_paths([note_path])

        assert len(reports) == 1
        report = reports[0]
        assert report.summary == "Resolve the dummy validator findings."
        assert len(report.findings) == 1
        finding = report.findings[0]
        assert finding.validator == "DummyValidator"
        assert finding.fix == "Update the title field to satisfy the validator."
        assert finding.references == ["https://example.com/docs/dummy"]
        assert agent.invocations, "Expected agent to be invoked"
    finally:
        ValidatorRegistry.clear()
        for validator in original_validators:
            ValidatorRegistry.register(validator)
