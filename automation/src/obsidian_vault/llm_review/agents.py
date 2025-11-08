"""PydanticAI agents for note review and fixing."""

from __future__ import annotations

import os
from dataclasses import dataclass
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


class MetadataSanityResult(BaseModel):
    """Result of metadata/frontmatter sanity check."""

    has_issues: bool = Field(description="Whether metadata issues were found")
    issues_found: list[str] = Field(
        default_factory=list,
        description="List of metadata sanity issues (topic consistency, timestamp freshness, bilingual ordering)",
    )
    warnings: list[str] = Field(
        default_factory=list, description="Non-critical warnings about metadata"
    )
    suggestions: list[str] = Field(
        default_factory=list, description="Suggestions for improvement"
    )


class QAVerificationResult(BaseModel):
    """Result of final QA/critic verification before marking as complete."""

    is_acceptable: bool = Field(
        description="Whether the note is acceptable to mark as complete (no critical issues)"
    )
    factual_errors: list[str] = Field(
        default_factory=list,
        description="Any factual or technical errors found in the final content",
    )
    bilingual_parity_issues: list[str] = Field(
        default_factory=list,
        description="Issues where EN and RU content are not semantically equivalent",
    )
    quality_concerns: list[str] = Field(
        default_factory=list,
        description="Non-critical quality concerns or improvements suggested",
    )
    summary: str = Field(
        description="Brief summary of the verification result and overall note quality"
    )


DEFAULT_OPENROUTER_MODEL = "anthropic/claude-sonnet-4"
DEFAULT_TEMPERATURE = 0.2
DEFAULT_TIMEOUT = 60.0


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


def _get_int_from_env(var_name: str) -> int | None:
    """Return an int value from the environment if it can be parsed."""

    raw_value = os.getenv(var_name)
    if raw_value is None:
        return None

    try:
        return int(raw_value)
    except ValueError:
        logger.warning(
            "Invalid integer value for %s: %s — ignoring", var_name, raw_value
        )
        return None


def _get_bool_from_env(var_name: str) -> bool | None:
    """Return a bool value from the environment if it can be parsed."""

    raw_value = os.getenv(var_name)
    if raw_value is None:
        return None

    normalized = raw_value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False

    logger.warning("Invalid boolean value for %s: %s — ignoring", var_name, raw_value)
    return None


@dataclass
class OpenRouterConfig:
    """Runtime configuration for OpenRouter requests."""

    model: str
    headers: dict[str, str]
    settings_kwargs: dict[str, Any]

    @classmethod
    def from_environment(cls, override_model: str | None = None) -> "OpenRouterConfig":
        """Construct configuration, applying environment overrides with validation."""

        resolved_model = override_model or os.getenv(
            "OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL
        )

        headers: dict[str, str] = {}
        http_referer = os.getenv("OPENROUTER_HTTP_REFERER")
        if http_referer:
            headers["HTTP-Referer"] = http_referer

        app_title = os.getenv("OPENROUTER_APP_TITLE")
        if app_title:
            headers["X-Title"] = app_title

        settings_kwargs: dict[str, Any] = {}

        temperature = _get_float_from_env("OPENROUTER_TEMPERATURE")
        if temperature is None:
            temperature = DEFAULT_TEMPERATURE
        settings_kwargs["temperature"] = temperature

        top_p = _get_float_from_env("OPENROUTER_TOP_P")
        if top_p is not None:
            settings_kwargs["top_p"] = top_p

        presence_penalty = _get_float_from_env("OPENROUTER_PRESENCE_PENALTY")
        if presence_penalty is not None:
            settings_kwargs["presence_penalty"] = presence_penalty

        frequency_penalty = _get_float_from_env("OPENROUTER_FREQUENCY_PENALTY")
        if frequency_penalty is not None:
            settings_kwargs["frequency_penalty"] = frequency_penalty

        max_tokens = _get_int_from_env("OPENROUTER_MAX_TOKENS")
        if max_tokens is not None:
            settings_kwargs["max_tokens"] = max_tokens

        seed = _get_int_from_env("OPENROUTER_SEED")
        if seed is not None:
            settings_kwargs["seed"] = seed

        timeout = _get_float_from_env("OPENROUTER_TIMEOUT")
        if timeout is None:
            timeout = DEFAULT_TIMEOUT
        settings_kwargs["timeout"] = timeout

        parallel_tool_calls = _get_bool_from_env("OPENROUTER_PARALLEL_TOOL_CALLS")
        if parallel_tool_calls is not None:
            settings_kwargs["parallel_tool_calls"] = parallel_tool_calls

        if headers:
            settings_kwargs["extra_headers"] = headers

        return cls(resolved_model, headers, settings_kwargs)


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

    config = OpenRouterConfig.from_environment(model_name)
    logger.debug(
        "Initializing OpenRouter model: %s (settings: %s)",
        config.model,
        {k: v for k, v in config.settings_kwargs.items() if k != "extra_headers"},
    )

    settings = ModelSettings(**config.settings_kwargs)

    return OpenAIChatModel(
        config.model,
        provider=OpenAIProvider(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        ),
        settings=settings,
    )


# System prompts
TECHNICAL_REVIEW_PROMPT = """You are the **technical accuracy reviewer** for bilingual Obsidian interview notes.

REFERENCE MATERIAL (non-exhaustive):
- 00-Administration/AI-Agents/AGENT-CHECKLIST.md — vault compliance rules.
- 00-Administration/AI-Agents/NOTE-REVIEW-PROMPT.md — review workflow expectations.

PRIMARY GOALS
- Validate every technical statement, algorithm explanation, complexity analysis, and code example for factual accuracy.
- Keep changes surgical and respect the existing formatting, bilingual order (RU first), and author voice.

REVIEW PROCEDURE
1. Read the entire note (RU + EN) to understand scope, question, and solution.
2. Cross-check against standard CS/Android/system design knowledge and the vault rules above.
3. Confirm blockquoted questions, YAML integrity, and section ordering remain intact (do not edit YAML fields).
4. When an issue is found, update the minimal fragment in **both languages** so they stay semantically aligned.
5. If correctness cannot be confirmed with high confidence, flag the concern instead of guessing.

NEVER DO
- Modify or regenerate YAML frontmatter, aliases, tags, or metadata formatting.
- Reorder headings, lists, code blocks, or sections that already follow vault conventions.
- Introduce new references, concepts, or files that are absent from the original note.
- Rewrite large sections merely for style; only change content when technically necessary.

EDITING RULES
- Preserve Markdown syntax, indentation, spacing, wikilinks, and bilingual structure.
- Keep RU and EN sections technically equivalent after edits.
- Prefer explicit corrections over vague wording; show the right complexity, edge cases, and terminology.
- Use ``issues_found`` to list each discrete technical problem (empty when none were found).

OUTPUT FORMAT
Respond **only** with a JSON object matching ``TechnicalReviewResult``:
{
  "has_issues": bool,
  "issues_found": list[str],
  "revised_text": str,
  "changes_made": bool,
  "explanation": str
}
- ``revised_text`` must contain the full note text, identical to the input when no corrections are needed.
- ``explanation`` summarises the verification steps and key fixes (or explicitly states that no issues were found).

QUALITY BAR
- Treat ambiguous or underspecified claims as issues that must be resolved or flagged.
- Double-check complexity analysis, edge cases, and platform-specific guidance against senior-level expectations.
- Ensure the final RU and EN content remains technically rigorous and mutually consistent.
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

METADATA_SANITY_PROMPT = """You are a metadata/frontmatter sanity checker for Obsidian interview notes.

Your job is to perform a LIGHTWEIGHT, HIGH-LEVEL sanity check on YAML frontmatter and document structure BEFORE detailed validators run. Focus on issues that would cause validator churn or are easy to spot early.

WHAT TO CHECK:

1. **YAML Structural Integrity**:
   - Is YAML frontmatter present and parseable?
   - Are required fields present (id, title, topic, difficulty, moc, related, tags)?
   - Are field types correct (lists vs strings, no nested objects where not expected)?

2. **Topic Consistency**:
   - Does the `topic` field match the file's folder location?
   - Is the MOC field appropriate for the topic?
   - Example: topic=kotlin should be in 70-Kotlin/ folder with moc=moc-kotlin

3. **Timestamp Freshness**:
   - Are `created` and `updated` dates present?
   - Is `updated` date >= `created` date?
   - Are dates in the future (likely error)?
   - Format check: YYYY-MM-DD

4. **Bilingual Structure Ordering**:
   - Does the note have both EN and RU sections?
   - Are sections in the expected order?
   - Required sections present: "# Question (EN)", "# Вопрос (RU)", "## Answer (EN)", "## Ответ (RU)"

5. **Common Formatting Issues**:
   - Brackets in YAML fields that shouldn't have them (moc field)?
   - Double brackets in YAML arrays (related field)?
   - Russian characters in tags (should be English only)?

WHAT NOT TO CHECK:
- Detailed content validation (leave for validators)
- Technical accuracy (leave for technical review)
- Specific tag requirements beyond English-only
- Link validity
- Code correctness

OUTPUT FORMAT:
Return a JSON object matching `MetadataSanityResult`:
{
  "has_issues": bool,
  "issues_found": list[str],  // Critical/error-level issues
  "warnings": list[str],      // Non-critical warnings
  "suggestions": list[str]    // Optional improvements
}

Be concise and specific. Each issue should be actionable and help guide the fix agent.
Examples:
- "YAML field 'moc' contains brackets: '[[moc-kotlin]]' (should be 'moc-kotlin')"
- "Topic 'kotlin' but file in '40-Android/' folder (should be '70-Kotlin/')"
- "Missing required section: '# Question (EN)'"
- "Date 'updated' (2024-01-01) is earlier than 'created' (2025-01-01)"
- "Tags contain Russian characters: ['корутины'] (should be English only)"
"""

QA_VERIFICATION_PROMPT = """You are the **final QA/critic agent** for bilingual Obsidian interview notes.

Your role is to perform a FINAL verification check AFTER all validator issues have been resolved and before marking the note as complete.

PRIMARY GOALS:
1. Verify no new factual/technical errors were introduced during the fix iterations
2. Confirm bilingual parity (EN and RU sections are semantically equivalent)
3. Assess overall note quality and identify any remaining risks
4. Provide a clear pass/fail decision with reasoning

WHAT TO CHECK:

1. **Factual Accuracy**:
   - Technical statements, algorithm explanations, complexity analysis
   - Code examples are correct and runnable
   - No incorrect claims or outdated information
   - Platform-specific guidance is accurate

2. **Bilingual Parity**:
   - RU and EN sections convey the same technical information
   - No missing translations or semantic drift between languages
   - Code examples and technical terms are consistent
   - Both versions are complete and equivalent

3. **Content Quality**:
   - Answer is complete and addresses the question
   - Explanation is clear and well-structured
   - Technical depth is appropriate for the difficulty level
   - No placeholder or incomplete sections (except "Follow-ups" which is optional)

4. **Format Integrity** (quick check):
   - YAML frontmatter is present and looks reasonable
   - Required sections exist (Question EN/RU, Answer EN/RU)
   - No obvious formatting issues

WHAT NOT TO CHECK:
- Detailed YAML validation (validators already checked this)
- Specific tag requirements (validators already checked this)
- Link validity (validators already checked this)
- Style preferences (accept author's voice)

OUTPUT FORMAT:
Return a JSON object matching `QAVerificationResult`:
{
  "is_acceptable": bool,  // true = safe to complete, false = needs more work
  "factual_errors": list[str],  // Critical technical errors that MUST be fixed
  "bilingual_parity_issues": list[str],  // EN/RU semantic mismatches
  "quality_concerns": list[str],  // Non-critical improvements or warnings
  "summary": str  // 2-3 sentence summary of verification result
}

DECISION CRITERIA:
- Set `is_acceptable = true` if:
  - No factual errors
  - No bilingual parity issues
  - Content is complete and correct (quality_concerns are acceptable)

- Set `is_acceptable = false` if:
  - Any factual/technical errors exist
  - EN and RU content are not equivalent
  - Answer is incomplete or incorrect

Be thorough but pragmatic. Minor style issues should go in quality_concerns, not block completion.
The goal is to catch serious problems that would mislead interview candidates, not to demand perfection.
"""


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


def get_metadata_sanity_agent() -> Agent:
    """Get the metadata sanity check agent (lazy initialization)."""
    logger.debug("Creating metadata sanity check agent")
    return Agent(
        model=get_openrouter_model(),
        output_type=MetadataSanityResult,
        system_prompt=METADATA_SANITY_PROMPT,
    )


def get_qa_verification_agent() -> Agent:
    """Get the QA verification agent (lazy initialization)."""
    logger.debug("Creating QA verification agent")
    return Agent(
        model=get_openrouter_model(),
        output_type=QAVerificationResult,
        system_prompt=QA_VERIFICATION_PROMPT,
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


async def run_metadata_sanity_check(
    note_text: str, note_path: str, **kwargs: Any
) -> MetadataSanityResult:
    """Run metadata/frontmatter sanity check on a note.

    Args:
        note_text: The note content to check
        note_path: Path to the note (for context)
        **kwargs: Additional context

    Returns:
        MetadataSanityResult with findings
    """
    logger.debug(f"Starting metadata sanity check for: {note_path}")
    logger.debug(f"Note length: {len(note_text)} characters")

    prompt = (
        "Perform a high-level metadata/frontmatter sanity check on this note. "
        "Focus on YAML structure, topic consistency, timestamps, and bilingual sections.\n\n"
        f"Note path: {note_path}\n\n"
        "```markdown\n"
        f"{note_text}\n"
        "```"
    )

    try:
        agent = get_metadata_sanity_agent()
        logger.debug("Running metadata sanity agent...")
        result = await agent.run(prompt)

        logger.debug(
            f"Metadata sanity check complete - "
            f"has_issues: {result.output.has_issues}, "
            f"issues_found: {len(result.output.issues_found)}, "
            f"warnings: {len(result.output.warnings)}, "
            f"suggestions: {len(result.output.suggestions)}"
        )

        if result.output.has_issues:
            logger.warning(
                f"Metadata sanity check found {len(result.output.issues_found)} issue(s)"
            )

        return result.output
    except Exception as e:
        logger.error(f"Metadata sanity check failed for {note_path}: {e}")
        raise


async def run_qa_verification(
    note_text: str, note_path: str, iteration_count: int, **kwargs: Any
) -> QAVerificationResult:
    """Run final QA/critic verification on a note before marking complete.

    This agent performs a final check to ensure:
    - No factual errors were introduced during fixes
    - Bilingual parity is maintained
    - Overall quality is acceptable

    Args:
        note_text: The final note content to verify
        note_path: Path to the note (for context)
        iteration_count: Number of fix iterations that were performed
        **kwargs: Additional context

    Returns:
        QAVerificationResult with verification findings and pass/fail decision
    """
    logger.debug(f"Starting QA verification for: {note_path}")
    logger.debug(f"Note length: {len(note_text)} characters, iterations: {iteration_count}")

    prompt = (
        "Perform a final QA/critic verification on this note. "
        "All validator issues have been resolved. Your job is to ensure no factual errors "
        "were introduced, bilingual parity is maintained, and overall quality is acceptable.\n\n"
        f"Note path: {note_path}\n"
        f"Fix iterations performed: {iteration_count}\n\n"
        "```markdown\n"
        f"{note_text}\n"
        "```"
    )

    try:
        agent = get_qa_verification_agent()
        logger.debug("Running QA verification agent...")
        result = await agent.run(prompt)

        logger.debug(
            f"QA verification complete - "
            f"is_acceptable: {result.output.is_acceptable}, "
            f"factual_errors: {len(result.output.factual_errors)}, "
            f"bilingual_parity_issues: {len(result.output.bilingual_parity_issues)}, "
            f"quality_concerns: {len(result.output.quality_concerns)}"
        )

        if not result.output.is_acceptable:
            logger.warning(
                f"QA verification found issues preventing completion: "
                f"{len(result.output.factual_errors)} factual errors, "
                f"{len(result.output.bilingual_parity_issues)} parity issues"
            )
        else:
            logger.success(f"QA verification passed: {result.output.summary}")

        return result.output
    except Exception as e:
        logger.error(f"QA verification failed for {note_path}: {e}")
        raise
