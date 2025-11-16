# LLM Review System

AI-powered note review and fixing system for the Interview Questions Obsidian vault.

## Overview

This module implements an automated system for reviewing and improving Markdown notes using:

- **PydanticAI**: Structured LLM interactions with OpenRouter (optimized model selection per agent type)
- **LangGraph**: Stateful, cyclic workflow orchestration
- **Existing validators**: Integration with vault validation rules

### Model Selection (Updated 2025-11)

The system uses specialized models optimized for each agent task:

- **DeepSeek V3.1**: Technical review, QA verification, coordination, failure analysis (excellent reasoning)
- **MiniMax M2**: Issue fixing (superior code generation at 8% of Claude Sonnet cost)
- **Qwen-Turbo**: Metadata validation, bilingual parity (most cost-effective for simple tasks)
- **Qwen3-Max**: Concept enrichment (enhanced multilingual support for bilingual content)

## Architecture

### Components

1. **State Management** (`state.py`)

   - `NoteReviewState`: Tracks the review workflow for a single note
   - `ReviewIssue`: Standardized issue representation

2. **AI Agents** (`agents/`)

   - `technical_review_agent`: Reviews technical/factual correctness (DeepSeek V3.1)
   - `metadata_sanity_agent`: Lightweight frontmatter/structure check (Qwen-Turbo)
   - `issue_fix_agent`: Fixes formatting and structure issues (MiniMax M2)
   - `qa_verification_agent`: Final quality verification (DeepSeek V3.1)
   - `concept_enrichment_agent`: Enriches concept notes (Qwen3-Max)
   - `bilingual_parity_agent`: Checks EN/RU parity (Qwen-Turbo)
   - `qa_failure_summary_agent`: Analyzes failures (DeepSeek V3.1)
   - `fix_coordinator_agent`: Plans fix strategies (DeepSeek V3.1)
   - Per-agent model optimization via `settings.py`

3. **Workflow** (`graph.py`)
   - `ReviewGraph`: LangGraph-based orchestration
   - Four main nodes:
     - `initial_llm_review`: Technical review phase
     - `metadata_sanity_check`: High-level metadata validation
     - `run_validators`: Runs existing validation scripts
     - `llm_fix_issues`: Iterative issue fixing

### Workflow Diagram

```
┌─────────────────────┐
│   Load Note Text    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Initial LLM Review  │  ← Technical/factual check
│  (technical_review) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Metadata Sanity     │  ← NEW: Lightweight YAML/structure check
│  (metadata_check)   │     Catches schema problems early
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Run Validators     │  ← Existing automation
│  (format/structure) │     Merges metadata findings
└──────────┬──────────┘
           │
           ▼
      ┌────────┐
      │ Issues?│
      └───┬─┬──┘
          │ │
       No │ │ Yes
          │ │
          │ ▼
          │ ┌─────────────────────┐
          │ │  LLM Fix Issues     │
          │ │  (issue_fix_agent)  │
          │ └──────────┬──────────┘
          │            │
          │            ▼
          │    ┌──────────────┐
          │    │ Max iter?    │
          │    └───┬──────┬───┘
          │        │      │
          │     No │      │ Yes
          │        │      │
          │        └──────┘
          │            │
          ▼            ▼
     ┌────────────────────┐
     │       Done         │
     └────────────────────┘
```

## Usage

### CLI Command

```bash
# Dry run (default - safe for testing)
vault-app llm-review

# Dry run with specific pattern
vault-app llm-review --pattern "InterviewQuestions/70-Kotlin/**/*.md"

# Actually modify files
vault-app llm-review --no-dry-run

# With custom settings
vault-app llm-review \
  --pattern "InterviewQuestions/**/*.md" \
  --no-dry-run \
  --max-iterations 10 \
  --report review-report.md
```

### Python API

```python
from pathlib import Path
from obsidian_vault.llm_review import (
    CompletionMode,
    ProcessingProfile,
    create_review_graph,
)

# Create the review graph
vault_root = Path("InterviewQuestions")
graph = create_review_graph(
    vault_root=vault_root,
    max_iterations=5,
    completion_mode=CompletionMode.STANDARD,
    processing_profile=ProcessingProfile.THOROUGH,
)

# Process a single note
note_path = vault_root / "70-Kotlin/q-coroutine-basics--kotlin--easy.md"
state = await graph.process_note(note_path)

# Check results
if state.changed:
    print(f"Modified: {state.iteration} iterations")
    print(f"Final issues: {len(state.issues)}")
    print(f"History: {state.history}")

# Access analytics from the session
print(graph.get_analytics_summary())
```

## Processing Profiles & Analytics

The review workflow provides multiple processing profiles that trade execution
time for stability or thoroughness. Select the appropriate profile via the
`processing_profile` argument when creating the graph.

| Profile                       | Description                                                                                  |
| ----------------------------- | -------------------------------------------------------------------------------------------- |
| `ProcessingProfile.BALANCED`  | Default behaviour. Keeps validator concurrency and smart selection for faster runs.          |
| `ProcessingProfile.STABILITY` | Runs metadata/parity helpers sequentially to improve determinism and aid debugging.          |
| `ProcessingProfile.THOROUGH`  | Always executes the full validator suite and adds two extra iterations for maximum coverage. |

Analytics are collected automatically per note. Retrieve granular data with
`ReviewGraph.get_note_analytics(path)` or fetch aggregate metrics using
`ReviewGraph.get_analytics_summary()`.

## Configuration

### Environment Variables

```bash
# Required: OpenRouter API key
export OPENROUTER_API_KEY="sk-or-v1-..."

# Optional: Override default model (per-agent models are pre-configured)
export OPENROUTER_MODEL="deepseek/deepseek-chat-v3.1"

# Optional: Model parameters (applied to all agents unless overridden)
export OPENROUTER_TEMPERATURE="0.2"
export OPENROUTER_MAX_TOKENS="65536"
export OPENROUTER_TIMEOUT="60.0"

# Optional: OpenRouter metadata
export OPENROUTER_HTTP_REFERER="your-app-url"
export OPENROUTER_APP_TITLE="Interview Questions Vault"
```

### Parameters

| Parameter            | Default                      | Description                                           |
| -------------------- | ---------------------------- | ----------------------------------------------------- |
| `pattern`            | `InterviewQuestions/**/*.md` | File glob pattern                                     |
| `dry_run`            | `true`                       | Preview mode (no file modifications)                  |
| `max_iterations`     | `5`                          | Max fix iterations per note                           |
| `report`             | `None`                       | Path for detailed report                              |
| `processing_profile` | `balanced`                   | Choose between balanced, stability, or thorough modes |

## Features

### 1. Technical Review

The initial LLM review phase checks:

- Technical accuracy of explanations
- Correctness of code examples
- Logical consistency
- Completeness of technical content
- Accuracy of complexity analysis (Big-O notation)

### 2. Metadata Sanity Check (NEW)

A lightweight validation layer that runs BEFORE detailed validators to catch common schema problems early:

**YAML Structural Integrity**:

- Is frontmatter present and parseable?
- Are required fields present (id, title, topic, difficulty, etc.)?
- Are field types correct (lists vs strings)?

**Topic Consistency**:

- Does the `topic` field match the file's folder location?
- Is the MOC field appropriate for the topic?
- Example: topic=kotlin should be in 70-Kotlin/ with moc=moc-kotlin

**Timestamp Freshness**:

- Are `created` and `updated` dates present and valid?
- Is `updated` >= `created`?
- Are dates in the correct format (YYYY-MM-DD)?

**Bilingual Structure Ordering**:

- Are both EN and RU sections present?
- Are required sections in expected order?
- Sections: "# Question (EN)", "# Вопрос (RU)", "## Answer (EN)", "## Ответ (RU)"

**Common Formatting Issues**:

- Brackets in YAML fields that shouldn't have them (moc field)?
- Double brackets in YAML arrays (related field)?
- Russian characters in tags (should be English only)?

This phase significantly reduces validator churn by catching and fixing structural problems before detailed validation runs.

### 3. Iterative Fixing

The fix loop addresses:

- YAML frontmatter formatting
- Required section presence
- Tag formatting (English-only)
- Bilingual structure (EN/RU)
- Link formatting
- File organization

### 3. Vault Rule Compliance

Enforces all vault rules:

- Both EN and RU in same file
- Exactly ONE topic from taxonomy
- English-only tags
- Proper YAML format (no brackets in `moc`, arrays for `related`)
- Required sections (Question EN/RU, Answer EN/RU)
- No emoji anywhere
- `status: draft` for AI-modified notes

## Safety Features

### 1. Dry Run by Default

All commands default to `--dry-run` to prevent accidental modifications.

### 2. In-place writes

LLM review writes directly without creating independent backup copies. Run the dry-run first and rely on Git history (`git diff`, `git checkout -- <note>`) if you need to inspect or undo changes.

### 3. Iteration Limits

Prevents infinite loops with configurable `max_iterations`.

### 4. Error Handling

Comprehensive error handling with detailed logging and history tracking.

### 5. Validation Integration

Uses the same validation logic as CI/CD to ensure consistency.

## GitHub Actions Integration

### Manual Workflow

Trigger via GitHub UI:

1. Go to Actions → LLM Note Polishing
2. Click "Run workflow"
3. Configure options:
   - Dry run: true/false
   - Pattern: file glob
   - Max iterations: number
   - Create PR: true/false

### Scheduled Runs

Weekly dry-run reports (Sunday 2 AM UTC):

- Reviews all notes
- Generates report
- No file modifications
- Creates artifact for review

### PR-based Changes

When `dry_run=false` and `create_pr=true`:

1. Runs LLM review
2. Creates new branch
3. Commits changes
4. Opens PR with detailed summary
5. Uploads report as artifact

## Development

### Adding New Agents

```python
from pydantic import BaseModel
from pydantic_ai import Agent
from .agents import get_openrouter_model

class NewResult(BaseModel):
    # Define result structure
    pass

new_agent = Agent(
    model=get_openrouter_model,
    result_type=NewResult,
    system_prompt="Your prompt here..."
)
```

### Extending the Workflow

```python
# Add new node
workflow.add_node("new_node", self._new_node_handler)

# Add edge
workflow.add_edge("existing_node", "new_node")

# Or conditional edge
workflow.add_conditional_edges(
    "new_node",
    self._decision_function,
    {
        "continue": "next_node",
        "stop": END,
    }
)
```

### Custom Validators

Validators are auto-discovered via `ValidatorRegistry`. See existing validators in `obsidian_vault/validators/`.

## Troubleshooting

### API Key Issues

```bash
# Check if key is set
echo $OPENROUTER_API_KEY

# Test connectivity
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"
```

### Import Errors

```bash
# Reinstall dependencies
cd automation
uv sync

# Or with pip
pip install -e .
```

### Model Errors

If you encounter model-specific errors, you can override per-agent models in `settings.py`:

```python
# In agents/settings.py, modify agent settings
TECHNICAL_REVIEW_SETTINGS = AgentModelSettings(
    model="deepseek/deepseek-chat-v3.1",  # Change to alternative model
    temperature=0.3,
    # ...
)
```

Or override via environment variable for all agents:

```bash
export OPENROUTER_MODEL="your-preferred-model"
```

### Validation Failures

If notes repeatedly fail validation:

1. Check the issue descriptions in the report
2. Review the history in `state.history`
3. Run validators manually: `vault-app validate path/to/note.md`
4. Check if the issue is in the agent prompts

## Performance

### Benchmarks

Typical performance (varies by note complexity and API latency):

- Initial review: 2-5 seconds per note
- Fix iteration: 1-3 seconds per iteration
- Total (5 iterations max): ~10-20 seconds per note

### Optimization Tips

1. **Use specific patterns**: `--pattern "InterviewQuestions/70-Kotlin/**/*.md"` instead of `**/*.md`
2. **Reduce iterations**: `--max-iterations 3` for simple fixes
3. **Batch processing**: Process multiple notes in one run rather than individual calls

## Costs

OpenRouter API costs vary by model (2025-11 pricing):

### Optimized Model Pricing

- **DeepSeek V3.1**: Very cost-effective, excellent reasoning (671B params, 37B active)
- **MiniMax M2**: $0.15/M input, $0.60/M output (2x faster than Claude at 8% cost)
- **Qwen-Turbo**: $0.05/M input, $0.20/M output (most affordable)
- **Qwen3-Max**: $0.22/M input, $0.88/M output (best value for multilingual)

### Estimated Cost Per Note

- **Simple notes**: $0.002-0.01 (mostly Qwen-Turbo and MiniMax M2)
- **Complex notes**: $0.01-0.03 (multiple iterations with DeepSeek V3.1)
- **Concept enrichment**: $0.01-0.05 (Qwen3-Max for bilingual content)

**Cost Optimization**: The new model selection reduces costs by 60-80% compared to previous Claude Sonnet configuration while maintaining or improving quality.

Monitor your usage at https://openrouter.ai/activity

## Security

### API Key Storage

- **Local**: Store in `.env` file (gitignored)
- **CI/CD**: Use GitHub Secrets (`OPENROUTER_API_KEY`)
- **Never** commit API keys to version control

### Data Privacy

- Notes are sent to OpenRouter/LLM provider
- Review OpenRouter's privacy policy
- Consider data sensitivity before using on proprietary content

## Future Enhancements

Potential improvements:

1. **Parallel processing**: Process multiple notes concurrently
2. **Incremental mode**: Only review recently modified notes
3. **Custom prompts**: User-configurable agent prompts
4. **Quality metrics**: Track improvement statistics
5. **A/B testing**: Compare different models or prompts
6. **Interactive mode**: Review/approve changes before saving

## Contributing

See the main automation README for contribution guidelines.

## License

Same as parent project.

## Support

For issues or questions:

1. Check existing GitHub issues
2. Review workflow logs
3. Check OpenRouter status
4. Open new issue with:
   - Error message
   - Note example (if not sensitive)
   - Workflow run link
   - Environment details
