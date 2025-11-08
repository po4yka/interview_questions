# LLM Review System - Logging Guide

## Overview

The LLM review system uses **loguru** for comprehensive logging at all stages of the workflow. This enables detailed debugging and monitoring of the review process.

## Log Levels

The system uses the following log levels:

### DEBUG (Most Verbose)
**When to use**: Development, troubleshooting, detailed analysis

**What is logged**:
- Model initialization details
- Agent creation
- Note file reading (character counts)
- State initialization
- Taxonomy loading details
- Note index building
- Decision point evaluations
- Issue details (first 100 chars of each issue)
- LangGraph workflow steps
- Individual issue processing

**Example**:
```
DEBUG | Initializing OpenRouter model: anthropic/claude-sonnet-4
DEBUG | Creating technical review agent
DEBUG | Starting technical review for: q-coroutines--kotlin--medium.md
DEBUG | Note length: 2547 characters
DEBUG | Running technical review agent...
DEBUG | Technical review complete - has_issues: False, changes_made: False, issues_found: 0
```

### INFO (Standard Operation)
**When to use**: Normal operation, tracking workflow progress

**What is logged**:
- Workflow initialization
- Note processing start/end
- LangGraph workflow execution
- Continuation decisions with issue counts
- Taxonomy and index loading
- High-level workflow status

**Example**:
```
INFO | ======================================================================
INFO | Processing note: q-coroutines--kotlin--medium.md
INFO | Starting LangGraph workflow for q-coroutines--kotlin--medium.md
INFO | Continuing to iteration 2 - 3 issue(s) remaining
INFO | ======================================================================
```

### SUCCESS (Completion)
**When to use**: Successful completion of major operations

**What is logged**:
- Workflow completion with summary
- ReviewGraph initialization
- Clean validation (no issues)

**Example**:
```
SUCCESS | Completed review for q-coroutines--kotlin--medium.md - changed: True, iterations: 2, final_issues: 0
SUCCESS | No issues remaining - workflow complete
SUCCESS | ReviewGraph initialized successfully
```

### WARNING (Non-Critical Issues)
**When to use**: Max iterations reached, potential problems

**What is logged**:
- Max iterations limit reached
- Unexpected but non-fatal conditions

**Example**:
```
WARNING | Max iterations (5) reached
```

### ERROR (Failures)
**When to use**: Operation failures, exceptions

**What is logged**:
- API key missing
- File read failures
- Agent execution failures
- Validation failures
- Workflow errors
- Exception details

**Example**:
```
ERROR | OPENROUTER_API_KEY environment variable not set
ERROR | Failed to read note /path/to/note.md: [Errno 2] No such file or directory
ERROR | Technical review failed for q-test.md: API rate limit exceeded
ERROR | LangGraph workflow failed for note.md: Connection timeout
```

## Logging by Component

### agents.py

**get_openrouter_model()**:
```
DEBUG | Initializing OpenRouter model: {model_name}
ERROR | OPENROUTER_API_KEY environment variable not set
```

**get_technical_review_agent()**:
```
DEBUG | Creating technical review agent
```

**get_issue_fix_agent()**:
```
DEBUG | Creating issue fix agent
```

**run_technical_review()**:
```
DEBUG | Starting technical review for: {note_path}
DEBUG | Note length: {len} characters
DEBUG | Running technical review agent...
DEBUG | Technical review complete - has_issues: {bool}, changes_made: {bool}, issues_found: {count}
INFO  | Technical review made changes: {explanation}
ERROR | Technical review failed for {note_path}: {error}
```

**run_issue_fixing()**:
```
DEBUG | Starting issue fixing for: {note_path}
DEBUG | Number of issues to fix: {count}
DEBUG | Issue 1: {issue[:100]}...
DEBUG | Running issue fix agent...
DEBUG | Issue fixing complete - changes_made: {bool}, fixes_applied: {count}
INFO  | Applied fixes: {fix1}, {fix2}, ...
ERROR | Issue fixing failed for {note_path}: {error}
```

### graph.py

**ReviewGraph.__init__()**:
```
(No direct logging - initialization is lightweight)
```

**_initial_llm_review()**:
```
INFO  | Running initial technical review for {note_path}
INFO  | Technical review made changes: {explanation}
INFO  | No technical issues found
ERROR | Error in technical review: {error}
```

**_run_validators()**:
```
INFO  | Running validators (iteration {n})
INFO  | Found {count} issues
ERROR | Error running validators: {error}
```

**_llm_fix_issues()**:
```
INFO  | Fixing {count} issues
INFO  | Applied fixes: {fixes}
WARNING | No fixes could be applied
ERROR | Error fixing issues: {error}
```

**_should_continue_fixing()**:
```
DEBUG | Decision point - iteration: {i}/{max}, issues: {count}, error: {bool}, completed: {bool}
WARNING | Max iterations ({max}) reached
SUCCESS | No issues remaining - workflow complete
ERROR | Stopping due to error: {error}
INFO  | Completed flag set - stopping iteration
INFO  | Continuing to iteration {n} - {count} issue(s) remaining
```

**process_note()**:
```
INFO  | ======================================================================
INFO  | Processing note: {note_name}
DEBUG | Full path: {full_path}
DEBUG | Read {count} characters from note
DEBUG | Initialized state with max_iterations={n}
INFO  | Starting LangGraph workflow for {note_name}
DEBUG | LangGraph workflow completed
SUCCESS | Completed review for {note_name} - changed: {bool}, iterations: {n}, final_issues: {count}
ERROR | Failed to read note {path}: {error}
ERROR | LangGraph workflow failed for {path}: {error}
ERROR | Workflow ended with error: {error}
DEBUG | Workflow history: {count} entries
INFO  | ======================================================================
```

**create_review_graph()**:
```
INFO  | Initializing ReviewGraph
DEBUG | Vault root: {path}
DEBUG | Max iterations: {n}
DEBUG | Repo root: {path}
INFO  | Loading taxonomy from TAXONOMY.md
DEBUG | Taxonomy loaded - topics: {count}
ERROR | Failed to load taxonomy: {error}
INFO  | Building note index
DEBUG | Note index built - {count} notes indexed
ERROR | Failed to build note index: {error}
SUCCESS | ReviewGraph initialized successfully
```

## Usage Examples

### Enable Debug Logging

```bash
# Set log level via environment variable
export LOGURU_LEVEL=DEBUG

# Run with verbose logging
vault-app llm-review --pattern "InterviewQuestions/**/*.md"
```

### Filter Logs

```bash
# Show only errors and warnings
vault-app llm-review 2>&1 | grep -E "ERROR|WARNING"

# Show workflow progress (INFO and above)
vault-app llm-review 2>&1 | grep -E "INFO|SUCCESS|WARNING|ERROR"
```

### Save Logs to File

The CLI automatically logs to both console and logfiles (if configured in logging_config.py).

To explicitly save logs:

```bash
vault-app llm-review --pattern "..." 2>&1 | tee llm-review.log
```

## Log Analysis

### Common Patterns

**Normal successful run**:
```
INFO  | Processing note: note1.md
INFO  | Starting LangGraph workflow
INFO  | Running initial technical review
INFO  | Running validators (iteration 1)
INFO  | Found 2 issues
INFO  | Fixing 2 issues
INFO  | Applied fixes: ...
INFO  | Running validators (iteration 2)
SUCCESS | No issues remaining - workflow complete
SUCCESS | Completed review for note1.md - changed: True, iterations: 2, final_issues: 0
```

**Hit max iterations**:
```
INFO  | Processing note: complex-note.md
...
INFO  | Running validators (iteration 5)
INFO  | Found 1 issues
WARNING | Max iterations (5) reached
SUCCESS | Completed review - changed: True, iterations: 5, final_issues: 1
```

**Error during processing**:
```
INFO  | Processing note: bad-note.md
INFO  | Starting LangGraph workflow
INFO  | Running initial technical review
ERROR | Technical review failed: API rate limit exceeded
ERROR | Error in technical review: RateLimitError
SUCCESS | Completed review - changed: False, iterations: 0, final_issues: 0
```

### Debugging Failed Runs

1. **Check for API errors**:
   ```bash
   grep "ERROR.*API" llm-review.log
   ```

2. **Find which notes failed**:
   ```bash
   grep "ERROR.*failed for" llm-review.log
   ```

3. **See iteration counts**:
   ```bash
   grep "Completed review" llm-review.log | grep -o "iterations: [0-9]*"
   ```

4. **Check what issues were found**:
   ```bash
   grep "Found .* issues" llm-review.log
   ```

## Performance Monitoring

### Typical Log Volume

For a single note:
- **DEBUG**: 30-50 log lines
- **INFO**: 10-15 log lines
- **SUCCESS**: 2-3 log lines
- **WARNING**: 0-1 log lines
- **ERROR**: 0 log lines (on success)

For 100 notes (INFO level):
- ~1000-1500 log lines
- ~100-200 KB log file

### Log Rotation

If processing large numbers of notes, consider log rotation:

```python
from loguru import logger

logger.add(
    "logs/llm-review_{time}.log",
    rotation="100 MB",
    retention="10 days",
    compression="zip"
)
```

## Best Practices

### For Development

- Use **DEBUG** level
- Review full workflow execution
- Check state transitions
- Verify issue detection and fixing

### For Production

- Use **INFO** level
- Monitor for ERROR and WARNING
- Track completion statistics
- Save logs for audit trail

### For Troubleshooting

1. **Enable DEBUG** for affected notes
2. **Check ERROR logs** first
3. **Review decision points** (iteration choices)
4. **Examine issue details** (what was detected)
5. **Verify fixes applied** (what changed)

## Log Message Format

Loguru default format:
```
{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}
```

Example:
```
2025-11-08 12:34:56 | INFO     | graph:process_note:281 - Processing note: example.md
```

## Related Files

- `automation/src/obsidian_vault/utils/logging_config.py` - Logging setup
- `automation/src/obsidian_vault/llm_review/agents.py` - Agent logging
- `automation/src/obsidian_vault/llm_review/graph.py` - Workflow logging
- `automation/src/obsidian_vault/llm_review/state.py` - State history (not logs)

## Future Enhancements

Potential logging improvements:

1. **Structured logging**: JSON output for parsing
2. **Performance metrics**: Timing for each stage
3. **API call tracking**: Request/response logging
4. **Token usage**: Track LLM token consumption
5. **Custom log levels**: Add TRACE for ultra-verbose

---

**Version**: 1.0
**Last Updated**: 2025-11-08
**Status**: Complete
