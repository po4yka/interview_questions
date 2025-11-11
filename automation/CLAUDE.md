# Claude Code Agent Guide - Automation Package

Quick reference for using Claude Code with the Obsidian vault automation package.

**Last Updated**: 2025-11-08

---

## Overview

This automation package provides tools for validating, analyzing, and improving Obsidian vault notes. The LLM review system uses PydanticAI + LangGraph to automatically review and fix notes.

## Quick Start

### Setup

```bash
# Install dependencies
cd automation
uv sync

# Set API key for LLM review
export OPENROUTER_API_KEY="sk-or-v1-..."
```

### Common Commands

```bash
# Validate notes
vault-app validate --all

# LLM review (dry-run)
vault-app llm-review --pattern "InterviewQuestions/**/*.md"

# LLM review (apply changes)
vault-app llm-review --no-dry-run --backup

# Graph statistics
vault-app graph-stats --hubs 10

# Find orphaned notes
vault-app orphans
```

---

## Package Structure

```
automation/
├── src/obsidian_vault/
│   ├── llm_review/          # LLM-based review system
│   │   ├── agents.py        # PydanticAI agents
│   │   ├── graph.py         # LangGraph workflow
│   │   ├── state.py         # State management
│   │   ├── README.md        # Technical documentation
│   │   └── LOGGING.md       # Logging guide
│   ├── validators/          # Note validators
│   ├── utils/               # Utility functions
│   ├── cli.py               # Legacy CLI
│   └── cli_app.py           # Modern CLI (Typer + Rich)
├── tests/                   # Test suite
├── pyproject.toml           # Dependencies and config
└── LLM_REVIEW.md            # User guide
```

---

## Development Workflows

### Adding a New Validator

1. Create validator class in `src/obsidian_vault/validators/`
2. Inherit from `BaseValidator`
3. Register with `@ValidatorRegistry.register`
4. Implement `validate()` method

```python
from .base import BaseValidator, Severity
from .registry import ValidatorRegistry

@ValidatorRegistry.register
class MyValidator(BaseValidator):
    def validate(self):
        # Check something
        if issue:
            self.add_issue(Severity.ERROR, "Issue description", field="field_name")
        else:
            self.add_passed("Check passed")

        return self._summary
```

### Modifying LLM Agents

**agents.py** contains:

- `get_openrouter_model()` - Model initialization
- `get_technical_review_agent()` - Technical review agent
- `get_issue_fix_agent()` - Issue fixing agent

To modify agent behavior:

1. Edit system prompts (`TECHNICAL_REVIEW_PROMPT`, `ISSUE_FIX_PROMPT`)
2. Adjust result models (`TechnicalReviewResult`, `IssueFixResult`)
3. Update agent logic in `run_technical_review()` or `run_issue_fixing()`

### Extending the Workflow

**graph.py** contains the LangGraph workflow:

```python
# Add new node
workflow.add_node("new_node", self._new_node_handler)

# Add edge
workflow.add_edge("existing_node", "new_node")

# Node handler
async def _new_node_handler(self, state: NoteReviewState) -> dict:
    # Process state
    return {"updated_field": new_value}
```

### Adding CLI Commands

In **cli_app.py**:

```python
@app.command()
def my_command(
    arg: str = typer.Argument(..., help="Description"),
    opt: bool = typer.Option(False, "--option", help="Description"),
):
    """Command description."""
    # Implementation
```

---

## Testing

### Run Tests

```bash
cd automation
pytest
pytest --cov=obsidian_vault
pytest tests/test_validators.py -v
```

### Test Structure

```
tests/
├── test_validators.py       # Validator tests
├── test_graph.py            # LLM review workflow tests
├── test_cli.py              # CLI tests
└── fixtures/                # Test fixtures
```

---

## LLM Review System

### Architecture

**Two-phase processing**:

1. **Technical review**: AI checks for accuracy
2. **Iterative fixing**: Fix issues until clean or max iterations

**Workflow**:

```
START → Technical Review → Validators
                              ↓
        ┌─────────────────────┴─────────────┐
        ↓                                   ↓
    Fix Issues ──→ Validators           END (done)
        ↑               ↓
        └──(continue)───┘
```

### Usage

```bash
# Basic dry-run
vault-app llm-review

# Specific pattern
vault-app llm-review --pattern "InterviewQuestions/70-Kotlin/**/*.md"

# Apply changes
vault-app llm-review --no-dry-run --backup --max-iterations 5

# Generate report
vault-app llm-review --report review-report.md
```

### Configuration

**Environment variables**:

```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
export LOGURU_LEVEL=DEBUG  # For verbose logging
```

**Parameters**:

- `--pattern`: File glob pattern (default: `InterviewQuestions/**/*.md`)
- `--dry-run/--no-dry-run`: Preview or apply changes (default: `--dry-run`)
- `--max-iterations`: Max fix iterations (default: 5)
- `--backup/--no-backup`: Create backups (default: `--backup`)
- `--report`: Report file path

### Logging

**Log levels**:

- `DEBUG`: Detailed execution (development)
- `INFO`: Progress tracking (production)
- `SUCCESS`: Completions
- `WARNING`: Non-critical issues
- `ERROR`: Failures

**Enable debug logging**:

```bash
export LOGURU_LEVEL=DEBUG
vault-app llm-review
```

**Filter logs**:

```bash
# Only errors
vault-app llm-review 2>&1 | grep "ERROR"

# Save to file
vault-app llm-review 2>&1 | tee llm-review.log
```

---

## Best Practices

### For Development

1. **Use virtual environment**:

   ```bash
   cd automation
   uv venv
   source .venv/bin/activate
   ```

2. **Install in editable mode**:

   ```bash
   uv pip install -e .
   ```

3. **Run tests before committing**:

   ```bash
   pytest
   ruff check .
   mypy src/
   ```

4. **Use DEBUG logging**:
   ```bash
   export LOGURU_LEVEL=DEBUG
   ```

### For LLM Review

1. **Always start with dry-run**:

   ```bash
   vault-app llm-review --dry-run
   ```

2. **Test on small subset**:

   ```bash
   vault-app llm-review --pattern "InterviewQuestions/70-Kotlin/q-test-*.md"
   ```

3. **Use backups**:

   ```bash
   vault-app llm-review --no-dry-run --backup
   ```

4. **Monitor costs**:

   - Check OpenRouter usage: https://openrouter.ai/activity
   - Estimate: $0.01-0.05 per note

5. **Review changes carefully**:

   ```bash
   # Generate report
   vault-app llm-review --report report.md --dry-run

   # Review diff before applying
   git diff note.md
   ```

### For Validation

1. **Validate before committing**:

   ```bash
   vault-app validate --all
   ```

2. **Check specific notes**:

   ```bash
   vault-app validate path/to/note.md
   ```

3. **Generate reports**:
   ```bash
   vault-app validate --all --report validation-report.md
   ```

---

## Common Tasks

### Add New LLM Agent

1. **Define result model** in `agents.py`:

   ```python
   class NewResult(BaseModel):
       result_field: str
       changes_made: bool
   ```

2. **Create agent factory**:

   ```python
   def get_new_agent() -> Agent:
       return Agent(
           model=get_openrouter_model(),
           result_type=NewResult,
           system_prompt="Your prompt...",
       )
   ```

3. **Create execution function**:
   ```python
   async def run_new_task(text: str, **kwargs) -> NewResult:
       agent = get_new_agent()
       result = await agent.run(f"Task: {text}")
       return result.data
   ```

### Modify Workflow

1. **Add node to graph** in `graph.py`:

   ```python
   workflow.add_node("new_step", self._new_step)
   ```

2. **Implement handler**:

   ```python
   async def _new_step(self, state: NoteReviewState) -> dict:
       # Process
       return {"field": value}
   ```

3. **Connect with edges**:
   ```python
   workflow.add_edge("previous_step", "new_step")
   workflow.add_edge("new_step", "next_step")
   ```

### Debug LLM Issues

1. **Enable debug logging**:

   ```bash
   export LOGURU_LEVEL=DEBUG
   ```

2. **Check specific note**:

   ```bash
   vault-app llm-review --pattern "path/to/specific-note.md" --dry-run
   ```

3. **Review logs**:

   ```bash
   vault-app llm-review 2>&1 | tee debug.log
   grep "ERROR\|WARNING" debug.log
   ```

4. **Check API errors**:
   ```bash
   grep "failed for" debug.log
   ```

---

## Troubleshooting

### Import Errors

```bash
# Reinstall dependencies
cd automation
rm -rf .venv
uv sync

# Verify installation
python -c "from obsidian_vault.llm_review import create_review_graph; print('OK')"
```

### API Key Issues

```bash
# Check if set
echo $OPENROUTER_API_KEY

# Test connectivity
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"
```

### Validation Failures

```bash
# Run validators manually
vault-app validate path/to/note.md

# Check specific validator
python -c "
from obsidian_vault.validators import ValidatorRegistry
print([v.__name__ for v in ValidatorRegistry.get_all_validators()])
"
```

### LLM Review Issues

1. **Max iterations reached**:

   - Increase: `--max-iterations 10`
   - Check what issues remain
   - May need manual fixing

2. **No changes applied**:

   - Check if issues are fixable
   - Review agent prompts
   - Verify validators are working

3. **Unexpected changes**:
   - Review agent prompts
   - Check log for agent reasoning
   - Use `--dry-run` to preview

---

## Resources

### Documentation

- **User Guide**: `LLM_REVIEW.md`
- **Technical Docs**: `src/obsidian_vault/llm_review/README.md`
- **Logging Guide**: `src/obsidian_vault/llm_review/LOGGING.md`
- **This Guide**: `CLAUDE.md`
- **Agent Instructions**: `AGENTS.md`

### Code References

- **Validators**: `src/obsidian_vault/validators/`
- **LLM Agents**: `src/obsidian_vault/llm_review/agents.py`
- **Workflow**: `src/obsidian_vault/llm_review/graph.py`
- **CLI**: `src/obsidian_vault/cli_app.py`

### External

- **PydanticAI**: https://ai.pydantic.dev/
- **LangGraph**: https://python.langchain.com/docs/langgraph
- **OpenRouter**: https://openrouter.ai/docs

---

## Quick Reference

### Validation

```bash
vault-app validate --all                    # Validate all notes
vault-app validate path/to/note.md          # Validate specific note
vault-app validate --all --report report.md # Generate report
```

### LLM Review

```bash
vault-app llm-review                        # Dry-run all notes
vault-app llm-review --no-dry-run           # Apply changes
vault-app llm-review --pattern "**/*.md"    # Specific pattern
vault-app llm-review --max-iterations 10    # More iterations
```

### Graph Analytics

```bash
vault-app graph-stats                       # Network statistics
vault-app graph-stats --hubs 10             # Top 10 hubs
vault-app orphans                           # Find orphaned notes
vault-app broken-links                      # Find broken links
vault-app link-report --output report.md    # Generate report
```

### Development

```bash
pytest                                      # Run tests
pytest --cov=obsidian_vault                # With coverage
ruff check .                                # Lint
ruff format .                               # Format
mypy src/                                   # Type check
```

---

**Version**: 1.0
**Status**: Production Ready
**Package**: obsidian-vault 0.8.0
