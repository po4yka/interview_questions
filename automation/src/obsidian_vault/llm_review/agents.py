"""PydanticAI agents for note review and fixing."""

from __future__ import annotations

import os
from typing import Any

from loguru import logger
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import ModelSettings, OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider


class TechnicalReviewResult(BaseModel):
    """Result of technical/factual review."""

    has_issues: bool = Field(description="Whether technical issues were found")
    issues_found: list[str] = Field(
        default_factory=list, description="List of technical issues identified"
    )
    revised_text: str = Field(description="Revised note text (may be same as input if no changes)")
    changes_made: bool = Field(description="Whether any changes were made to the text")
    explanation: str = Field(description="Explanation of what was reviewed and changed")


class IssueFixResult(BaseModel):
    """Result of fixing formatting/structure issues."""

    revised_text: str = Field(description="Note text with issues fixed")
    fixes_applied: list[str] = Field(
        default_factory=list, description="List of fixes that were applied"
    )
    changes_made: bool = Field(description="Whether any changes were made")


DEFAULT_OPENROUTER_MODEL = "anthropic/claude-sonnet-4"
DEFAULT_TEMPERATURE = 0.2


def _get_float_from_env(var_name: str) -> float | None:
    """Return a float value from the environment if it can be parsed."""

    raw_value = os.getenv(var_name)
    if raw_value is None:
        return None

    try:
        return float(raw_value)
    except ValueError:
        logger.warning(
            "Invalid float value for %s: %s — ignoring", var_name, raw_value
        )
        return None


def get_openrouter_model(model_name: str | None = None) -> OpenAIChatModel:
    """Get an OpenRouter model configured for use with PydanticAI.

    Args:
        model_name: Optional model identifier override. If omitted, uses the
            ``OPENROUTER_MODEL`` environment variable or the default model.

    Returns:
        Configured OpenAIChatModel instance

    Raises:
        ValueError: If OPENROUTER_API_KEY is not set
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("OPENROUTER_API_KEY environment variable not set")
        raise ValueError(
            "OPENROUTER_API_KEY environment variable is required. "
            "Get your API key from https://openrouter.ai/keys"
        )

    resolved_model = model_name or os.getenv(
        "OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL
    )
    logger.debug(f"Initializing OpenRouter model: {resolved_model}")

    headers: dict[str, str] = {}
    http_referer = os.getenv("OPENROUTER_HTTP_REFERER")
    if http_referer:
        headers["HTTP-Referer"] = http_referer

    app_title = os.getenv("OPENROUTER_APP_TITLE")
    if app_title:
        headers["X-Title"] = app_title

    temperature = _get_float_from_env("OPENROUTER_TEMPERATURE")
    if temperature is None:
        temperature = DEFAULT_TEMPERATURE

    top_p = _get_float_from_env("OPENROUTER_TOP_P")

    settings_kwargs: dict[str, Any] = {"temperature": temperature}
    if top_p is not None:
        settings_kwargs["top_p"] = top_p
    if headers:
        settings_kwargs["extra_headers"] = headers

    settings = ModelSettings(**settings_kwargs)

    return OpenAIChatModel(
        resolved_model,
        provider=OpenAIProvider(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        ),
        settings=settings,
    )


# System prompts
TECHNICAL_REVIEW_PROMPT = """You are the **technical accuracy reviewer** for bilingual interview-preparation notes.

PRIMARY GOAL
- Confirm every technical statement, code sample, algorithm analysis, and terminology usage is factually correct.
- Apply the smallest possible change set to fix inaccuracies while preserving author voice and formatting.

REVIEW PROCEDURE
1. Read the entire note (including RU/EN sections) to understand intent.
2. Verify:
   - Explanations match accepted computer science knowledge.
   - Code snippets compile/run conceptually and solve the stated task.
   - Big-O or resource analyses are mathematically sound.
   - Terminology is used precisely in both languages.
3. Compare EN/RU sections for semantic alignment when edits are required.
4. Only edit text that is technically incorrect, incomplete, or misleading.

NEVER DO
- Modify YAML frontmatter or metadata formatting.
- Reorder headings, lists, or sections that are already valid.
- Introduce new concepts, references, or files that are not in the source note.
- Paraphrase correct passages or rewrite entire paragraphs without a technical reason.

EDITING RULES
- Make surgical edits in-place; keep unaffected surrounding text identical.
- Update both language sections when a change is required for accuracy.
- Preserve Markdown syntax, spacing, and bilingual structure.
- If unsure about correctness, flag the issue in ``issues_found`` rather than guessing.

OUTPUT FORMAT
Respond **only** with a JSON object matching ``TechnicalReviewResult``:
{
  "has_issues": bool,
  "issues_found": list[str],
  "revised_text": str,
  "changes_made": bool,
  "explanation": str
}
- ``revised_text`` must contain the full note text, unchanged when no edits are necessary.
- ``issues_found`` should list precise technical problems that were discovered (empty list if none).
- ``explanation`` should summarise the review approach and key fixes (or confirm no changes).

QUALITY BAR
- Treat ambiguous claims as issues that require clarification.
- Double-check algorithm complexity, edge cases, and platform specifics before accepting them.
- Ensure final content in both languages remains aligned and technically rigorous.
"""

ISSUE_FIX_PROMPT = """You are an expert at fixing formatting and structural issues in Markdown notes.

You will receive:
1. The current note text
2. A list of validation issues to fix

Your task is to fix ALL the reported issues while:
- Preserving the semantic meaning
- Maintaining technical accuracy
- Keeping the bilingual structure (EN/RU sections)
- Following Obsidian vault conventions

CRITICAL: Make ONLY targeted, minimal changes to fix the specific issues reported.
- Fix ONLY what is broken - do not rewrite working content
- Add missing sections if required, but preserve all existing content
- Change ONLY the specific fields/lines that have validation errors
- DO NOT restructure or rewrite sections that are already correct
- If a word needs backticks, add backticks - don't rewrite the sentence
- If a link is invalid, fix/remove that link - don't rewrite the paragraph

CRITICAL RULES (from vault documentation):
1. Both EN and RU content must be in the SAME file
2. YAML frontmatter format:
   - moc: moc-name (NO brackets)
   - related: [file1, file2] (array format, NO double brackets)
   - tags must be English-only
   - Exactly ONE topic from taxonomy
3. Required sections:
   - # Question (EN)
   - # Вопрос (RU)
   - ## Answer (EN)
   - ## Ответ (RU)
4. No emoji anywhere
5. status: draft for AI-modified notes
6. NEVER suggest or add links to concept files that don't exist in the vault

Fix each issue precisely with minimal changes and return the corrected text."""


def get_technical_review_agent() -> Agent:
    """Get the technical review agent (lazy initialization)."""
    logger.debug("Creating technical review agent")
    return Agent(
        model=get_openrouter_model(),
        output_type=TechnicalReviewResult,
        system_prompt=TECHNICAL_REVIEW_PROMPT,
    )


def get_issue_fix_agent() -> Agent:
    """Get the issue fix agent (lazy initialization)."""
    logger.debug("Creating issue fix agent")
    return Agent(
        model=get_openrouter_model(),
        output_type=IssueFixResult,
        system_prompt=ISSUE_FIX_PROMPT,
    )


async def run_technical_review(
    note_text: str, note_path: str, **kwargs: Any
) -> TechnicalReviewResult:
    """Run technical review on a note.

    Args:
        note_text: The note content to review
        note_path: Path to the note (for context)
        **kwargs: Additional context

    Returns:
        TechnicalReviewResult with findings and revised text
    """
    logger.debug(f"Starting technical review for: {note_path}")
    logger.debug(f"Note length: {len(note_text)} characters")

    prompt = (
        "Review the following interview question note for technical accuracy, "
        "code correctness, and completeness while preserving formatting.\n\n"
        f"Note path: {note_path}\n\n"
        "```markdown\n"
        f"{note_text}\n"
        "```"
    )

    try:
        agent = get_technical_review_agent()
        logger.debug("Running technical review agent...")
        result = await agent.run(prompt)

        logger.debug(
            f"Technical review complete - "
            f"has_issues: {result.output.has_issues}, "
            f"changes_made: {result.output.changes_made}, "
            f"issues_found: {len(result.output.issues_found)}"
        )

        if result.output.changes_made:
            logger.info(f"Technical review made changes: {result.output.explanation}")

        return result.output
    except Exception as e:
        logger.error(f"Technical review failed for {note_path}: {e}")
        raise


async def run_issue_fixing(
    note_text: str, issues: list[str], note_path: str, **kwargs: Any
) -> IssueFixResult:
    """Fix formatting and structure issues in a note.

    Args:
        note_text: Current note content
        issues: List of issues to fix
        note_path: Path to the note
        **kwargs: Additional context

    Returns:
        IssueFixResult with corrected text
    """
    logger.debug(f"Starting issue fixing for: {note_path}")
    logger.debug(f"Number of issues to fix: {len(issues)}")

    for i, issue in enumerate(issues, 1):
        logger.debug(f"  Issue {i}: {issue[:100]}...")  # Log first 100 chars

    issues_text = "\n".join(f"- {issue}" for issue in issues)

    prompt = f"""Fix the following issues in this note:

Note path: {note_path}

ISSUES TO FIX:
{issues_text}

CURRENT NOTE CONTENT:
{note_text}

Fix ALL issues while preserving meaning and following vault rules.
Return the corrected text."""

    try:
        agent = get_issue_fix_agent()
        logger.debug("Running issue fix agent...")
        result = await agent.run(prompt)

        logger.debug(
            f"Issue fixing complete - "
            f"changes_made: {result.output.changes_made}, "
            f"fixes_applied: {len(result.output.fixes_applied)}"
        )

        if result.output.fixes_applied:
            logger.info(f"Applied fixes: {', '.join(result.output.fixes_applied[:5])}...")

        return result.output
    except Exception as e:
        logger.error(f"Issue fixing failed for {note_path}: {e}")
        raise
