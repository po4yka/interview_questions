# AI Agent Instructions - Automation Package

Comprehensive instructions for AI agents working with the Obsidian vault automation system.

**Last Updated**: 2025-11-08

---

## Overview

This document provides detailed instructions for AI agents (Claude, GPT, etc.) working with the automation package. It covers development workflows, code patterns, and best practices.

---

## System Architecture

### Package Structure

```
automation/
├── src/obsidian_vault/
│   ├── llm_review/              # LLM-based review system
│   │   ├── __init__.py         # Module exports
│   │   ├── state.py            # State management
│   │   ├── agents.py           # PydanticAI agents
│   │   ├── graph.py            # LangGraph workflow
│   │   ├── README.md           # Technical docs
│   │   └── LOGGING.md          # Logging guide
│   ├── validators/              # Note validators
│   │   ├── base.py             # Base classes
│   │   ├── registry.py         # Validator registry
│   │   ├── yaml_validator.py   # YAML validation
│   │   ├── content_validator.py # Content validation
│   │   ├── link_validator.py   # Link validation
│   │   └── ...
│   ├── utils/                   # Utility functions
│   │   ├── frontmatter.py      # YAML frontmatter handling
│   │   ├── taxonomy_loader.py  # Taxonomy management
│   │   ├── graph_analytics.py  # Network analysis
│   │   └── ...
│   ├── cli.py                   # Legacy CLI (argparse)
│   └── cli_app.py               # Modern CLI (Typer + Rich)
└── tests/                       # Test suite
```

### Key Components

1. **Validators**: Check note compliance with vault rules
2. **LLM Review**: AI-powered note improvement
3. **Graph Analytics**: Network analysis of note links
4. **CLI**: Command-line interface for all operations

---

## Core Principles

### 1. Validator Pattern

**All validators must**:

- Inherit from `BaseValidator`
- Register with `@ValidatorRegistry.register`
- Implement `validate()` method
- Use `add_issue()` and `add_passed()` for results
- Return `ValidationSummary`

**Example**:

```python
from .base import BaseValidator, Severity
from .registry import ValidatorRegistry

@ValidatorRegistry.register
class ExampleValidator(BaseValidator):
    def validate(self):
        # Check conditions
        if condition_failed:
            self.add_issue(
                Severity.ERROR,
                "Description of issue",
                field="field_name",
                line=line_number  # optional
            )
        else:
            self.add_passed("Check description")

        return self._summary
```

### 2. State Management

**LLM review uses immutable state updates**:

- State is passed through workflow
- Nodes return dicts with updates
- LangGraph merges updates into state
- Never mutate state directly

**Example**:

```python
async def _node_handler(self, state: NoteReviewState) -> dict:
    # Don't do: state.field = value
    # Do: return dict with updates
    return {
        "field": new_value,
        "changed": True,
    }
```

### 3. Logging Requirements

**All operations must log**:

- Use `loguru` logger
- Appropriate log levels (DEBUG, INFO, SUCCESS, WARNING, ERROR)
- Context in error messages
- Function entry/exit for complex operations

**Example**:

```python
from loguru import logger

async def process(item: str) -> Result:
    logger.debug(f"Processing: {item}")

    try:
        result = await operation(item)
        logger.info(f"Processed {item} successfully")
        return result
    except Exception as e:
        logger.error(f"Failed to process {item}: {e}")
        raise
```

### 4. Error Handling

**All async operations must**:

- Wrap in try-except
- Log errors with context
- Re-raise exceptions
- Return error state when appropriate

**Example**:

```python
async def risky_operation() -> Result:
    try:
        logger.debug("Starting operation")
        result = await do_something()
        return result
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        raise
```

---

## Development Workflows

### Adding a New Validator

**Steps**:

1. **Create validator file** in `src/obsidian_vault/validators/`

2. **Implement validator class**:

   ```python
   from .base import BaseValidator, Severity
   from .registry import ValidatorRegistry

   @ValidatorRegistry.register
   class MyValidator(BaseValidator):
       def validate(self):
           frontmatter = self.frontmatter
           content = self.content

           # Validation logic
           if issue:
               self.add_issue(Severity.ERROR, "Issue", field="field")
           else:
               self.add_passed("Passed")

           return self._summary
   ```

3. **Import in `validators/__init__.py`**:

   ```python
   from .my_validator import MyValidator
   ```

4. **Write tests** in `tests/test_validators.py`

5. **Test integration**:
   ```bash
   vault-app validate path/to/note.md
   ```

### Modifying LLM Agents

**Files to modify**:

- `src/obsidian_vault/llm_review/agents.py`

**Common changes**:

1. **Update system prompts**:

   ```python
   TECHNICAL_REVIEW_PROMPT = """
   Your new or updated prompt here...
   """
   ```

2. **Modify result models**:

   ```python
   class TechnicalReviewResult(BaseModel):
       existing_field: str
       new_field: Optional[str] = None  # Add new field
   ```

3. **Update agent logic**:

   ```python
   async def run_technical_review(...) -> TechnicalReviewResult:
       logger.debug(f"Starting review: {note_path}")

       # Your changes

       result = await agent.run(prompt)
       return result.data
   ```

### Extending the Workflow

**File**: `src/obsidian_vault/llm_review/graph.py`

**Add new node**:

1. **Create node handler**:

   ```python
   async def _new_node(self, state: NoteReviewState) -> dict:
       logger.info("Running new node")

       # Process state
       result = await some_operation(state.current_text)

       return {
           "updated_field": result,
           "changed": True,
       }
   ```

2. **Register in workflow**:

   ```python
   def _build_graph(self) -> StateGraph:
       workflow = StateGraph(NoteReviewState)

       # Add existing nodes
       workflow.add_node("initial_llm_review", self._initial_llm_review)
       workflow.add_node("new_node", self._new_node)  # Add new node

       # Connect with edges
       workflow.add_edge("initial_llm_review", "new_node")
       workflow.add_edge("new_node", "run_validators")

       return workflow.compile()
   ```

### Adding CLI Commands

**File**: `src/obsidian_vault/cli_app.py`

**Pattern**:

```python
@app.command()
def my_command(
    arg: str = typer.Argument(..., help="Required argument"),
    opt: str = typer.Option("default", "--option", "-o", help="Optional parameter"),
    flag: bool = typer.Option(False, "--flag", help="Boolean flag"),
):
    """
    Command description shown in help.

    Detailed explanation if needed.
    """
    logger.info(f"Running my_command with arg={arg}")

    try:
        # Implementation
        result = do_something(arg, opt, flag)

        console.print(f"[green]✓[/green] Success: {result}")

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        logger.exception(f"Command failed: {e}")
        raise typer.Exit(code=1)
```

---

## Code Patterns

### Validator Pattern

```python
@ValidatorRegistry.register
class PatternValidator(BaseValidator):
    REQUIRED_FIELDS = ["field1", "field2"]
    ALLOWED_VALUES = {"value1", "value2"}

    def validate(self):
        self._check_required_fields()
        self._check_allowed_values()
        return self._summary

    def _check_required_fields(self):
        for field in self.REQUIRED_FIELDS:
            if field not in self.frontmatter:
                self.add_issue(
                    Severity.ERROR,
                    f"Missing required field: {field}",
                    field=field
                )
            else:
                self.add_passed(f"{field} present")

    def _check_allowed_values(self):
        value = self.frontmatter.get("field")
        if value not in self.ALLOWED_VALUES:
            self.add_issue(
                Severity.ERROR,
                f"Invalid value: {value}",
                field="field"
            )
```

### Async Agent Pattern

```python
async def run_agent_task(
    input_text: str,
    context: dict,
    **kwargs: Any
) -> ResultType:
    """Execute agent task with error handling and logging."""

    logger.debug(f"Starting task with input length: {len(input_text)}")

    try:
        # Create agent
        agent = get_agent()

        # Build prompt
        prompt = build_prompt(input_text, context)

        # Run agent
        logger.debug("Executing agent...")
        result = await agent.run(prompt)

        # Log result
        logger.debug(f"Agent completed - success: {result.data.success}")

        if result.data.changes_made:
            logger.info(f"Changes made: {result.data.explanation}")

        return result.data

    except Exception as e:
        logger.error(f"Agent task failed: {e}")
        raise
```

### State Update Pattern

```python
async def _workflow_node(self, state: NoteReviewState) -> dict:
    """Process node and return state updates."""

    logger.info(f"Node processing (iteration {state.iteration})")

    try:
        # Process
        result = await process(state.current_text)

        # Build updates
        updates = {}

        if result.changed:
            updates["current_text"] = result.new_text
            updates["changed"] = True

        # Add history
        state.add_history_entry(
            "node_name",
            f"Processed with result: {result.summary}"
        )

        return updates

    except Exception as e:
        logger.error(f"Node failed: {e}")
        return {
            "error": str(e),
            "completed": True,
        }
```

---

## Testing Guidelines

### Validator Tests

```python
def test_validator():
    """Test validator with sample data."""

    # Setup
    frontmatter = {"field": "value"}
    content = "Test content"

    # Create validator
    validator = MyValidator(
        content=content,
        frontmatter=frontmatter,
        path="test.md",
        taxonomy=mock_taxonomy
    )

    # Run validation
    summary = validator.validate()

    # Assert
    assert len(summary.issues) == 0
    assert len(summary.passed) > 0
```

### Async Tests

```python
import pytest

@pytest.mark.asyncio
async def test_agent():
    """Test async agent execution."""

    # Setup
    input_text = "Test input"

    # Execute
    result = await run_agent_task(input_text, {})

    # Assert
    assert result.success
    assert result.output is not None
```

---

## Best Practices

### Code Style

1. **Use type hints**:

   ```python
   def function(arg: str, opt: Optional[int] = None) -> Result:
       pass
   ```

2. **Document functions**:

   ```python
   def function(arg: str) -> Result:
       """Short description.

       Args:
           arg: Argument description

       Returns:
           Result description
       """
   ```

3. **Use f-strings**:

   ```python
   message = f"Processing {name} with {count} items"
   ```

4. **Consistent naming**:
   - Classes: `PascalCase`
   - Functions: `snake_case`
   - Constants: `UPPER_CASE`
   - Private: `_leading_underscore`

### Logging

1. **Log at appropriate levels**:

   - `DEBUG`: Detailed execution flow
   - `INFO`: High-level progress
   - `SUCCESS`: Completion of major operations
   - `WARNING`: Non-critical issues
   - `ERROR`: Failures and exceptions

2. **Include context**:

   ```python
   logger.error(f"Failed to process {file_path}: {error}")
   # Not: logger.error(f"Failed: {error}")
   ```

3. **Log entry/exit for complex functions**:
   ```python
   async def complex_operation():
       logger.debug("Starting complex operation")
       # ...
       logger.debug("Complex operation complete")
   ```

### Error Handling

1. **Catch specific exceptions when possible**:

   ```python
   try:
       result = operation()
   except ValueError as e:
       logger.error(f"Invalid value: {e}")
       raise
   except IOError as e:
       logger.error(f"File error: {e}")
       raise
   ```

2. **Always log before re-raising**:

   ```python
   except Exception as e:
       logger.error(f"Operation failed: {e}")
       raise  # Re-raise for caller to handle
   ```

3. **Use context managers**:
   ```python
   with open(file_path) as f:
       content = f.read()
   ```

### State Management

1. **Never mutate state directly**:

   ```python
   # Don't do this
   state.field = new_value

   # Do this
   return {"field": new_value}
   ```

2. **Return partial updates**:

   ```python
   # Only update what changed
   return {"changed": True}  # Not entire state
   ```

3. **Use history tracking**:
   ```python
   state.add_history_entry("node", "What happened", extra=data)
   ```

---

## Common Tasks

### Add New Validator

```bash
# 1. Create file
touch src/obsidian_vault/validators/my_validator.py

# 2. Implement (see pattern above)

# 3. Import in __init__.py

# 4. Test
vault-app validate test-note.md
```

### Modify Agent Prompt

```python
# Edit agents.py
TECHNICAL_REVIEW_PROMPT = """
Updated prompt...
"""

# Test with dry-run
vault-app llm-review --pattern "test-note.md" --dry-run
```

### Add Workflow Node

```python
# In graph.py

# 1. Add node handler
async def _new_node(self, state: NoteReviewState) -> dict:
    # Implementation
    return updates

# 2. Register in _build_graph()
workflow.add_node("new_node", self._new_node)
workflow.add_edge("previous", "new_node")
workflow.add_edge("new_node", "next")

# 3. Test
vault-app llm-review --dry-run
```

### Debug Workflow

```bash
# Enable debug logging
export LOGURU_LEVEL=DEBUG

# Run on single note
vault-app llm-review --pattern "specific-note.md" --dry-run

# Check logs
vault-app llm-review 2>&1 | grep "ERROR\|WARNING"
```

---

## Constraints and Requirements

### MUST Follow

1. **Use loguru for all logging**
2. **Register validators with `@ValidatorRegistry.register`**
3. **Return dict updates from workflow nodes**
4. **Log errors before raising exceptions**
5. **Use type hints on all functions**
6. **Test changes before committing**
7. **Document complex functions**
8. **Handle errors gracefully**
9. **Preserve existing interfaces**
10. **Follow existing code patterns**

### MUST NOT Do

1. **Don't mutate state directly in workflow**
2. **Don't skip error logging**
3. **Don't use print() - use logger**
4. **Don't commit without tests**
5. **Don't break existing validators**
6. **Don't remove safety features (dry-run guards)**
7. **Don't hard-code configuration**
8. **Don't skip type hints**
9. **Don't use bare except:**
10. **Don't modify YAML structure without versioning**

---

## Troubleshooting

### Import Errors

```python
# Check if module can be imported
python -c "from obsidian_vault.llm_review import create_review_graph"

# Reinstall if needed
cd automation && uv sync
```

### Validator Not Running

```python
# Check if registered
from obsidian_vault.validators import ValidatorRegistry
print([v.__name__ for v in ValidatorRegistry.get_all_validators()])
```

### LangGraph Issues

```python
# Check state type
from obsidian_vault.llm_review.state import NoteReviewState
state = NoteReviewState(note_path="test", original_text="", current_text="")
print(state)  # Should work
```

### Logging Not Appearing

```bash
# Set log level
export LOGURU_LEVEL=DEBUG

# Check logger usage
grep "from loguru import logger" src/obsidian_vault/llm_review/*.py
```

---

## Resources

- **User Guide**: `LLM_REVIEW.md`
- **Technical Docs**: `src/obsidian_vault/llm_review/README.md`
- **Logging Guide**: `src/obsidian_vault/llm_review/LOGGING.md`
- **Claude Guide**: `CLAUDE.md`
- **PydanticAI**: https://ai.pydantic.dev/
- **LangGraph**: https://python.langchain.com/docs/langgraph
- **Typer**: https://typer.tiangolo.com/

---

**Version**: 1.0
**Status**: Production
**Package**: obsidian-vault 0.8.0
