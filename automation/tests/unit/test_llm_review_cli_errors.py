"""CLI regression tests for llm-review error accounting."""

from __future__ import annotations

from types import SimpleNamespace

from typer.testing import CliRunner

from obsidian_vault import cli_app

runner = CliRunner()


def test_llm_review_reports_exceptions_as_errors(monkeypatch, tmp_path):
    """Ensure per-note exceptions are counted toward summary totals."""

    repo_root = tmp_path
    vault_root = repo_root / "InterviewQuestions" / "60-CompSci"
    vault_root.mkdir(parents=True)

    ok_note = vault_root / "q-ok--cs--easy.md"
    failing_note = vault_root / "q-fail--cs--easy.md"
    ok_note.write_text("# Вопрос (RU)\n> ok\n", encoding="utf-8")
    failing_note.write_text("# Вопрос (RU)\n> fail\n", encoding="utf-8")

    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(cli_app, "discover_repo_root", lambda: repo_root)

    class FakeGraph:
        async def process_note(self, note_path):
            if "q-fail" in note_path.name:
                raise RuntimeError("boom")

            return SimpleNamespace(
                note_path=str(note_path),
                current_text=note_path.read_text(encoding="utf-8"),
                changed=False,
                error=None,
                iteration=0,
                issues=[],
                history=[],
                requires_human_review=False,
            )

    fake_graph = FakeGraph()

    import obsidian_vault.llm_review as llm_review_module

    monkeypatch.setattr(llm_review_module, "create_review_graph", lambda **_: fake_graph)

    result = runner.invoke(
        cli_app.app,
        ["llm-review", "--pattern", "InterviewQuestions/60-CompSci/*.md"],
    )

    assert result.exit_code == 1, result.output
    assert "Notes Processed" in result.stdout
    assert "Errors" in result.stdout
    assert "Notes Processed │     2" in result.stdout
    assert "Errors          │     1" in result.stdout
