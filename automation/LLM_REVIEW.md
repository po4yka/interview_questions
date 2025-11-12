# LLM-Based Note Review System

Automated AI-powered review and improvement system for Obsidian vault notes.

## Quick Start

### 1. Install Dependencies

```bash
cd automation
uv sync
```

This installs all required dependencies including:

- `pydantic-ai`: Structured LLM interactions
- `langgraph`: Workflow orchestration
- `openai`: OpenRouter API client

### 2. Set Up API Key

Get your OpenRouter API key from https://openrouter.ai/keys

```bash
export OPENROUTER_API_KEY="sk-or-v1-..."
```

Or create a `.env` file in the automation directory:

```bash
echo "OPENROUTER_API_KEY=sk-or-v1-..." > automation/.env
```

### 3. Run a Dry-Run Test

```bash
cd automation
uv run vault-app llm-review --dry-run --pattern "InterviewQuestions/70-Kotlin/**/*.md"
```

This will:

- Review all Kotlin notes
- Show what changes would be made
- NOT modify any files
- Generate a report

## What It Does

The LLM review system performs three phases for each note:

### Phase 1: Technical Review

Uses AI (Polaris Alpha via OpenRouter) to review:

- **Technical accuracy**: Are explanations correct?
- **Code correctness**: Do code examples work?
- **Completeness**: Is important information missing?
- **Complexity analysis**: Is Big-O notation accurate?

### Phase 2: Metadata Sanity Check

Lightweight AI-powered check of frontmatter and structure BEFORE detailed validators run:

- **YAML integrity**: Is frontmatter present and parseable?
- **Topic consistency**: Does topic match folder location and MOC?
- **Timestamp freshness**: Are created/updated dates valid and consistent?
- **Bilingual structure**: Are EN/RU sections present and in correct order?
- **Common formatting**: Brackets in YAML, Russian in tags, etc.

This phase catches schema problems early, reducing validator churn and providing clearer guidance to the fix agent.

### Phase 3: Iterative Fixing

Runs existing vault validators, then uses AI to fix:

- YAML frontmatter issues
- Missing required sections
- Tag formatting (English-only)
- Bilingual structure (EN/RU)
- Link formatting errors
- File organization

The system iterates (up to 5 times by default) until:

- All issues are fixed, OR
- Maximum iterations reached, OR
- No more fixes can be applied

### Phase 4: Knowledge-Gap Agent (Concept Enrichment)

**NEW**: When validators complain about missing concept files, the system now:

1. **Auto-creates concept stub files** with valid YAML frontmatter (as before)
2. **Enriches stubs with meaningful content** using the knowledge-gap agent
3. **Drafts seed content** instead of generic placeholders:
   - Technical definitions (2-4 sentences explaining WHAT, WHY, WHERE)
   - 3-5 key points covering essential aspects
   - Usage examples and common scenarios (when relevant)
   - Proper bilingual parity (EN/RU sections with equivalent content)

**Example transformation**:

Before (generic stub):

```markdown
# Summary (EN)

Test Concept is a fundamental concept in software development.

## Key Points (EN)

- To be documented
```

After (enriched):

```markdown
# Summary (EN)

Test Concept is a software testing approach that validates individual units of code
in isolation from dependencies. It forms the foundation of automated testing strategies,
enabling rapid feedback during development and facilitating refactoring.

## Key Points (EN)

- **Isolation**: Tests run independently without external dependencies
- **Fast execution**: Unit tests should complete in milliseconds
- **Test structure**: Follow the Arrange-Act-Assert (AAA) pattern
- **Mocking**: Use test doubles to isolate the system under test
- **Coverage**: Aim for high code coverage while focusing on meaningful scenarios
```

**Benefits**:

- **Reduced validator churn**: Concept files have meaningful content from the start
- **Better downstream passes**: Validators see complete documentation instead of placeholders
- **Improved vault quality**: Auto-generated concepts are actually useful for interview prep
- **Human intervention still needed**: Files marked `status: draft` with disclaimer for human review

**How it works**:

- Agent uses taxonomy context (topic, subtopics) to infer relevant content
- Can incorporate excerpts from Q&A notes that reference the concept
- Preserves YAML frontmatter exactly as-is (no modifications)
- Falls back to generic stub if enrichment fails (graceful degradation)

## Usage Examples

### Review Specific Folder

```bash
# Kotlin notes only
uv run vault-app llm-review --pattern "InterviewQuestions/70-Kotlin/**/*.md"

# Android notes only
uv run vault-app llm-review --pattern "InterviewQuestions/40-Android/**/*.md"

# Algorithms (easy difficulty)
uv run vault-app llm-review --pattern "InterviewQuestions/20-Algorithms/*--easy.md"
```

### Actually Modify Files

```bash
uv run vault-app llm-review --no-dry-run
```

Changes are written in place; rely on `git status`/`git diff` and revert via Git when needed.

### Generate Detailed Report

```bash
uv run vault-app llm-review \
  --dry-run \
  --report llm-review-report.md \
  --pattern "InterviewQuestions/**/*.md"

# View the report
cat llm-review-report.md
```

### Custom Iteration Limit

```bash
# More iterations for complex notes
uv run vault-app llm-review --max-iterations 10

# Fewer iterations for simple fixes
uv run vault-app llm-review --max-iterations 3
```

## GitHub Actions

### Manual Trigger

1. Go to GitHub repository → Actions
2. Select "LLM Note Polishing" workflow
3. Click "Run workflow"
4. Configure:
   - **Dry run**: `true` (safe) or `false` (modify files)
   - **Pattern**: File glob pattern
   - **Max iterations**: Number (default: 5)
   - **Create PR**: `true` or `false`

### Scheduled Runs

The workflow runs automatically:

- **When**: Every Sunday at 2 AM UTC
- **Mode**: Dry-run only (no file modifications)
- **Output**: Report uploaded as artifact

### PR-Based Workflow

When running with `dry_run=false` and `create_pr=true`:

1. System reviews and fixes notes
2. Creates a new branch: `llm-review/YYYYMMDD-HHMMSS`
3. Commits all changes
4. Opens a Pull Request
5. Uploads detailed report as artifact

**Review the PR carefully** before merging, especially:

- Technical accuracy of modified content
- Code examples still work
- YAML frontmatter is valid
- Bilingual structure preserved

## Safety Features

### 1. Dry-Run by Default

All CLI commands default to `--dry-run`:

```bash
# These are equivalent
vault-app llm-review
vault-app llm-review --dry-run
```

### 2. In-place writes

Modifications are saved directly; there are no automatic backup copies. Always run the dry-run first and rely on Git history (`git diff`, `git checkout -- <note>`) to inspect or revert changes before committing.

### 3. Validation Integration

Uses the **same validators** as CI/CD:

- YAML validation
- Content structure validation
- Link validation
- Android-specific validation
- Format validation

This ensures consistency with existing automation.

### 4. Detailed Logging

All operations are logged with:

- What was checked
- What issues were found
- What fixes were applied
- Why decisions were made

View history in the report.

## Configuration

### Environment Variables

| Variable             | Required | Default                     | Description        |
| -------------------- | -------- | --------------------------- | ------------------ |
| `OPENROUTER_API_KEY` | Yes      | -                           | OpenRouter API key |
| `OPENROUTER_MODEL`   | No       | `anthropic/claude-sonnet-4` | Model to use       |

### CLI Options

| Option             | Short | Default                      | Description               |
| ------------------ | ----- | ---------------------------- | ------------------------- |
| `--pattern`        | `-p`  | `InterviewQuestions/**/*.md` | File glob pattern         |
| `--dry-run`        | -     | `true`                       | Preview without modifying |
| `--no-dry-run`     | -     | -                            | Actually modify files     |
| `--max-iterations` | `-m`  | `5`                          | Max fix iterations        |
| `--report`         | `-r`  | `None`                       | Report file path          |

## Costs

OpenRouter charges per token:

- **Input**: ~$3 per million tokens
- **Output**: ~$15 per million tokens

Estimated cost per note: **$0.01-0.05**

For 100 notes: **~$1-5**

Monitor usage: https://openrouter.ai/activity

## Best Practices

### 1. Start with Dry-Run

Always test with dry-run first:

```bash
# Test on a few notes
vault-app llm-review --pattern "InterviewQuestions/70-Kotlin/q-test-*.md"

# Review the proposed changes
# If good, run for real
vault-app llm-review --no-dry-run --pattern "InterviewQuestions/70-Kotlin/q-test-*.md"
```

### 2. Use Specific Patterns

Avoid processing all notes at once:

```bash
# Good: Specific folder
--pattern "InterviewQuestions/70-Kotlin/**/*.md"

# Better: Even more specific
--pattern "InterviewQuestions/70-Kotlin/q-*--easy.md"

# Avoid: All notes (expensive and slow)
--pattern "InterviewQuestions/**/*.md"
```

### 3. Review Changes Carefully

When using in CI/CD:

1. Let it create a PR
2. Review the diff carefully
3. Check technical accuracy
4. Verify code examples
5. Test any complex changes
6. Merge only if confident

### 4. Use Reports

Always generate reports for non-trivial runs:

```bash
vault-app llm-review \
  --report "reports/llm-review-$(date +%Y%m%d).md" \
  --pattern "InterviewQuestions/**/*.md"
```

Keep reports for:

- Tracking improvements over time
- Understanding what was changed
- Debugging issues

### 5. Archive Before Bulk Operations

```bash
# Create an optional archive
tar -czf vault-archive-$(date +%Y%m%d).tar.gz InterviewQuestions/

# Then run LLM review
vault-app llm-review --no-dry-run --pattern "..."
```

## Troubleshooting

### "OPENROUTER_API_KEY not set"

```bash
# Check if set
echo $OPENROUTER_API_KEY

# Set it
export OPENROUTER_API_KEY="sk-or-v1-..."

# Or use .env file
echo "OPENROUTER_API_KEY=sk-or-v1-..." > automation/.env
```

### "LLM review dependencies not installed"

```bash
cd automation
uv sync

# Or reinstall
rm -rf .venv
uv sync
```

### "No notes found matching pattern"

Check your pattern:

```bash
# List files matching pattern
find InterviewQuestions -name "*.md" | grep "Kotlin"

# Use correct pattern
vault-app llm-review --pattern "InterviewQuestions/70-Kotlin/**/*.md"
```

### "Max iterations reached"

Some issues may be too complex to auto-fix:

1. Check the report for details
2. Review the specific issue
3. Fix manually if needed
4. Re-run validators to verify

### API Rate Limits

OpenRouter has rate limits:

1. Reduce `max_iterations`
2. Process fewer notes at once
3. Add delays between notes (future enhancement)
4. Upgrade OpenRouter plan

## Advanced Usage

### Python API

```python
import asyncio
from pathlib import Path
from obsidian_vault.llm_review import create_review_graph

async def review_notes():
    vault_root = Path("InterviewQuestions")
    graph = create_review_graph(vault_root, max_iterations=5)

    notes = list(vault_root.glob("70-Kotlin/**/*.md"))
    for note in notes:
        state = await graph.process_note(note)

        if state.changed:
            print(f"Modified: {note.name}")
            note.write_text(state.current_text)

asyncio.run(review_notes())
```

### Custom Model

Override the default model:

```python
# In agents.py
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

def get_openrouter_model(model_name: str = "anthropic/claude-3.5-sonnet") -> OpenAIChatModel:
    # Or use environment variable
    model_name = os.getenv("OPENROUTER_MODEL", model_name)
    api_key = os.getenv("OPENROUTER_API_KEY")

    return OpenAIChatModel(
        model_name,
        provider=OpenAIProvider(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        ),
    )
```

### Extending Validators

Add custom validators:

```python
# In automation/src/obsidian_vault/validators/

from .base import BaseValidator, Severity
from .registry import ValidatorRegistry

@ValidatorRegistry.register
class CustomValidator(BaseValidator):
    def validate(self):
        # Your validation logic
        if some_condition:
            self.add_issue(
                Severity.ERROR,
                "Issue description",
                field="field_name"
            )
        else:
            self.add_passed("Check passed")

        return self._summary
```

## Migration Guide

### From Manual Review

If you currently review notes manually:

1. **Start small**: Pick 5-10 notes
2. **Run dry-run**: See what would change
3. **Review proposed changes**: Are they good?
4. **Apply to subset**: Use `--no-dry-run` on those notes
5. **Validate results**: Run `vault-app validate`
6. **Expand gradually**: Increase scope if results are good

### From Other AI Tools

If you use Cursor, Claude, or other AI tools:

1. **Complementary use**: LLM review handles bulk operations
2. **Manual for complex**: Use manual AI for complex reasoning
3. **Automation for consistency**: LLM review ensures format consistency
4. **Best of both**: Combine approaches as needed

## FAQ

### Q: Is my data sent to OpenRouter?

**A:** Yes, note content is sent to OpenRouter's API for processing. Review their privacy policy. Don't use on highly sensitive content without approval.

### Q: Can I use a different model?

**A:** Yes, modify `get_openrouter_model()` in `agents.py` or set `OPENROUTER_MODEL` environment variable.

### Q: Will it break my notes?

**A:** Unlikely if used correctly:

- Start with `--dry-run`
- Review changes in PR or via `git diff`
- Test on subset first

### Q: How accurate are the fixes?

**A:** Generally good for:

- Formatting issues (very accurate)
- YAML fixes (very accurate)
- Technical content (mostly accurate, review recommended)

Less reliable for:

- Complex technical nuances
- Domain-specific details
- Code that requires execution

### Q: Can I run this locally vs CI?

**A:** Both!

- **Local**: Faster feedback, immediate iteration
- **CI**: Consistent environment, PR-based review

### Q: How do I revert changes?

```bash
# Revert a note before committing
git checkout -- note.md

# Undo an applied run (if already committed)
git revert HEAD
```

## Support

Issues or questions:

1. Check automation README
2. Review LLM review module README
3. Check GitHub issues
4. Open new issue with:
   - Command used
   - Error message
   - Note example (if not sensitive)
   - Report file

## Related Documentation

- [Automation README](README.md) - General automation setup
- [LLM Review Module README](src/obsidian_vault/llm_review/README.md) - Technical details
- [Vault Rules](../00-Administration/Vault-Rules/TAXONOMY.md) - Validation rules
- [Claude Code Guide](../CLAUDE.md) - AI tool guide

---

**Version**: 1.0
**Last Updated**: 2025-11-08
**Status**: Production Ready
