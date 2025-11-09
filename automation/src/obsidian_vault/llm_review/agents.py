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


class BilingualParityResult(BaseModel):
    """Result of bilingual parity check between EN and RU sections."""

    has_parity_issues: bool = Field(
        description="Whether parity issues were found between EN and RU content"
    )
    parity_issues: list[str] = Field(
        default_factory=list,
        description="List of semantic mismatches or missing translations between EN and RU",
    )
    missing_sections: list[str] = Field(
        default_factory=list,
        description="Sections that exist in one language but not the other",
    )
    summary: str = Field(
        description="Brief summary of the parity check result"
    )


class ConceptEnrichmentResult(BaseModel):
    """Result of enriching an auto-generated concept stub with meaningful content."""

    enriched_content: str = Field(
        description="The enriched concept note with meaningful definitions, examples, and references"
    )
    added_sections: list[str] = Field(
        default_factory=list,
        description="List of sections that were added or significantly enriched",
    )
    key_concepts: list[str] = Field(
        default_factory=list,
        description="Key technical concepts covered in the enriched content",
    )
    related_concepts: list[str] = Field(
        default_factory=list,
        description="Suggested related concept files (without c- prefix or .md extension)",
    )
    explanation: str = Field(
        description="Brief explanation of what was enriched and the knowledge sources used"
    )


DEFAULT_OPENROUTER_MODEL = "anthropic/claude-sonnet-4"
DEFAULT_TEMPERATURE = 0.2
DEFAULT_TIMEOUT = 60.0


@dataclass
class AgentModelSettings:
    """Per-agent model configuration overrides.

    Allows fine-tuning model behavior for different agent types.
    If a field is None, it will use the value from environment variables
    or the default configuration.
    """

    model: str | None = None
    temperature: float | None = None
    top_p: float | None = None
    max_tokens: int | None = None
    presence_penalty: float | None = None
    frequency_penalty: float | None = None
    timeout: float | None = None


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


def get_openrouter_model(
    model_name: str | None = None,
    agent_settings: AgentModelSettings | None = None,
) -> OpenAIChatModel:
    """Get an OpenRouter model configured for use with PydanticAI.

    Args:
        model_name: Optional model identifier override. If omitted, uses the
            ``OPENROUTER_MODEL`` environment variable or the default model.
        agent_settings: Optional per-agent configuration overrides. If provided,
            these settings will override the base configuration from environment
            variables for this specific agent instance.

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

    # Start with base configuration from environment
    config = OpenRouterConfig.from_environment(model_name)

    # Apply per-agent overrides if provided
    if agent_settings:
        if agent_settings.model is not None:
            config.model = agent_settings.model
        if agent_settings.temperature is not None:
            config.settings_kwargs["temperature"] = agent_settings.temperature
        if agent_settings.top_p is not None:
            config.settings_kwargs["top_p"] = agent_settings.top_p
        if agent_settings.max_tokens is not None:
            config.settings_kwargs["max_tokens"] = agent_settings.max_tokens
        if agent_settings.presence_penalty is not None:
            config.settings_kwargs["presence_penalty"] = agent_settings.presence_penalty
        if agent_settings.frequency_penalty is not None:
            config.settings_kwargs["frequency_penalty"] = agent_settings.frequency_penalty
        if agent_settings.timeout is not None:
            config.settings_kwargs["timeout"] = agent_settings.timeout

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

BILINGUAL_PARITY_PROMPT = """You are a **bilingual parity checker** for Obsidian interview notes.

Your role is to verify that English (EN) and Russian (RU) sections are semantically equivalent and technically consistent.

This check runs EARLY in the review loop (after validators) to catch translation drift BEFORE the final QA stage, reducing recycle time.

PRIMARY GOALS:
1. Verify EN and RU sections convey the same technical information
2. Detect missing translations or incomplete sections
3. Identify semantic drift where one language has more/different details than the other
4. Flag technical inconsistencies between language versions

WHAT TO CHECK:

1. **Section Completeness**:
   - Both "# Question (EN)" and "# Вопрос (RU)" exist
   - Both "## Answer (EN)" and "## Ответ (RU)" exist
   - Optional sections (Follow-ups, References, Related Questions) are present in both languages if in one
   - No orphaned sections in only one language

2. **Semantic Equivalence**:
   - Question and answer convey the same technical meaning in both languages
   - Code explanations are consistent (same algorithms, same complexity analysis)
   - Key technical terms are translated accurately
   - Examples and edge cases are covered in both languages

3. **Content Depth Parity**:
   - One language version is not significantly longer or more detailed than the other
   - Both versions cover the same technical points
   - No important details present in only one language
   - Trade-offs, pros/cons are equivalent

4. **Technical Accuracy Across Languages**:
   - Complexity analysis matches (e.g., both say O(n), not O(n) vs O(n log n))
   - Algorithm names/techniques are consistent
   - Code examples are identical or semantically equivalent
   - Platform-specific details match

WHAT NOT TO CHECK:
- Technical factual accuracy (already handled by technical_review agent)
- YAML frontmatter validation (already handled by metadata_sanity and validators)
- Code correctness (already handled by technical_review)
- Formatting/style issues (already handled by validators)

OUTPUT FORMAT:
Return a JSON object matching `BilingualParityResult`:
{
  "has_parity_issues": bool,  // true if EN and RU are not equivalent
  "parity_issues": list[str],  // Specific semantic mismatches or drift
  "missing_sections": list[str],  // Sections present in one language but not the other
  "summary": str  // 1-2 sentence summary of parity status
}

EXAMPLES OF PARITY ISSUES:

**Missing Translation**:
- "EN Answer section explains recursion with 3 examples, RU Answer section only has 1 example"
- "Follow-ups section exists in EN but missing in RU"

**Semantic Drift**:
- "EN says time complexity is O(n log n), RU says O(n²)"
- "EN explains HashMap collision handling, RU explanation omits collision handling"
- "RU version includes trade-offs discussion not present in EN"

**Incomplete Content**:
- "EN Question is a full paragraph, RU Question is only one sentence"
- "EN code example has detailed comments, RU code example lacks comments"

DECISION CRITERIA:
- Set `has_parity_issues = true` if you find any semantic mismatches or missing content
- Set `has_parity_issues = false` if EN and RU are semantically equivalent (minor wording differences are OK)

Be precise and specific in identifying parity issues. The goal is to ensure interview candidates get equivalent content regardless of language preference.
"""

CONCEPT_ENRICHMENT_PROMPT = """You are a **knowledge-gap agent** that enriches auto-generated concept stub files.

Your role is to transform generic placeholder content into meaningful, technically accurate concept documentation suitable for interview preparation.

INPUT CONTEXT:
You will receive:
1. An auto-generated concept stub with valid YAML frontmatter but generic placeholder content
2. The concept name/topic to document
3. Topic/subtopic context from taxonomy
4. Excerpts from Q&A notes that reference this concept (if available)

PRIMARY GOALS:
1. Write a clear, concise definition/summary of the concept (2-4 sentences)
2. Identify 3-5 key points that capture the essential aspects
3. Provide brief usage examples or common scenarios
4. Suggest related concepts (if relevant)
5. Maintain bilingual structure (EN/RU sections)

CONTENT REQUIREMENTS:

1. **Summary Sections**:
   - Replace "is a fundamental concept in software development" with a SPECIFIC technical definition
   - Explain WHAT it is, WHY it matters, and WHERE it's commonly used
   - Keep it concise (2-4 sentences) but informative

2. **Key Points Sections**:
   - Replace "To be documented" with 3-5 concrete bullet points
   - Each point should be a distinct, important aspect of the concept
   - Focus on technical characteristics, use cases, or trade-offs
   - Be specific but concise (1-2 lines per point)

3. **Use Cases / Trade-offs** (add if relevant):
   - When to use this concept
   - Common scenarios or patterns
   - Advantages and disadvantages

4. **References** (add if possible):
   - Replace "To be documented" with relevant documentation links
   - Official docs, reputable articles, or standard references
   - Avoid adding references if you're uncertain about URLs

5. **Bilingual Parity**:
   - Ensure EN and RU sections convey the same technical information
   - Translate definitions accurately, maintaining technical precision
   - Use proper Russian technical terminology

CRITICAL RULES:
1. DO NOT modify YAML frontmatter (keep it exactly as-is)
2. DO NOT add wikilinks to concepts that don't exist (you won't know what exists)
3. DO NOT invent URLs or references - only add if you're confident they're correct
4. DO NOT make up technical details - be accurate or stay generic
5. DO preserve the note structure (section ordering, markdown formatting)
6. DO maintain the "auto-generated" disclaimer at the bottom of each section

QUALITY BAR:
- Definitions should be technically accurate and interview-relevant
- Key points should help a candidate understand the concept quickly
- Content should be more valuable than "To be documented" but NOT a full tutorial
- Think "concise technical summary" not "comprehensive guide"

OUTPUT FORMAT:
Return a JSON object matching `ConceptEnrichmentResult`:
{
  "enriched_content": str,        // Full note text with enriched content
  "added_sections": list[str],    // Sections that were enriched
  "key_concepts": list[str],      // Technical concepts covered
  "related_concepts": list[str],  // Suggested related concepts (names only, no c- or .md)
  "explanation": str              // Brief explanation of enrichment
}

EXAMPLES OF GOOD ENRICHMENT:

**Before (generic)**:
```
# Summary (EN)

Test Concept is a fundamental concept in software development.
```

**After (enriched)**:
```
# Summary (EN)

Test Concept is a software testing approach that validates individual units of code in isolation from dependencies. It forms the foundation of automated testing strategies, enabling rapid feedback during development and facilitating refactoring. Commonly implemented using frameworks like JUnit (Java), pytest (Python), or JUnit/Mockito (Kotlin/Android).
```

**Before (generic)**:
```
## Key Points (EN)

- To be documented
```

**After (enriched)**:
```
## Key Points (EN)

- **Isolation**: Tests run independently without external dependencies (databases, networks, file systems)
- **Fast execution**: Unit tests should complete in milliseconds to enable rapid feedback loops
- **Test structure**: Follow the Arrange-Act-Assert (AAA) pattern for clarity and maintainability
- **Mocking**: Use test doubles (mocks, stubs, fakes) to isolate the system under test
- **Coverage**: Aim for high code coverage while focusing on meaningful test scenarios
```
"""


# Agent-specific model settings
# These defaults balance creativity vs determinism for each agent's role

TECHNICAL_REVIEW_SETTINGS = AgentModelSettings(
    # Slightly higher temperature for creative technical insight
    # but not too high to avoid hallucinations
    temperature=0.3,
    # Lower penalties to allow varied phrasing when explaining technical concepts
    presence_penalty=0.0,
    frequency_penalty=0.1,
)

ISSUE_FIX_SETTINGS = AgentModelSettings(
    # Lower temperature for deterministic, conservative fixes
    temperature=0.1,
    # Higher penalties to discourage repetition and encourage precise, minimal changes
    presence_penalty=0.3,
    frequency_penalty=0.3,
)

METADATA_SANITY_SETTINGS = AgentModelSettings(
    # Very low temperature for structured, deterministic metadata validation
    temperature=0.1,
    # Moderate penalties for clear, concise issue reporting
    presence_penalty=0.2,
    frequency_penalty=0.2,
)

QA_VERIFICATION_SETTINGS = AgentModelSettings(
    # Moderate temperature for thorough, creative verification
    # Needs to think critically and find edge cases
    temperature=0.3,
    # Lower penalties to allow comprehensive issue exploration
    presence_penalty=0.1,
    frequency_penalty=0.1,
)

CONCEPT_ENRICHMENT_SETTINGS = AgentModelSettings(
    # Moderate-high temperature for creative, knowledge-rich content generation
    # Needs to synthesize information and provide meaningful explanations
    temperature=0.4,
    # Lower penalties to allow varied technical vocabulary and comprehensive coverage
    presence_penalty=0.0,
    frequency_penalty=0.1,
)

BILINGUAL_PARITY_SETTINGS = AgentModelSettings(
    # Low temperature for consistent, deterministic parity checking
    # Should be precise and analytical, not creative
    temperature=0.2,
    # Moderate penalties for clear, concise issue reporting
    presence_penalty=0.2,
    frequency_penalty=0.2,
)


def get_technical_review_agent() -> Agent:
    """Get the technical review agent (lazy initialization).

    Uses slightly higher temperature (0.3) for creative technical insight
    while maintaining accuracy.
    """
    logger.debug("Creating technical review agent with custom settings")
    return Agent(
        model=get_openrouter_model(agent_settings=TECHNICAL_REVIEW_SETTINGS),
        output_type=TechnicalReviewResult,
        system_prompt=TECHNICAL_REVIEW_PROMPT,
    )


def get_issue_fix_agent() -> Agent:
    """Get the issue fix agent (lazy initialization).

    Uses lower temperature (0.1) and higher penalties (0.3) for
    deterministic, conservative fixes with minimal changes.
    """
    logger.debug("Creating issue fix agent with custom settings")
    return Agent(
        model=get_openrouter_model(agent_settings=ISSUE_FIX_SETTINGS),
        output_type=IssueFixResult,
        system_prompt=ISSUE_FIX_PROMPT,
    )


def get_metadata_sanity_agent() -> Agent:
    """Get the metadata sanity check agent (lazy initialization).

    Uses very low temperature (0.1) for structured, deterministic
    metadata validation.
    """
    logger.debug("Creating metadata sanity check agent with custom settings")
    return Agent(
        model=get_openrouter_model(agent_settings=METADATA_SANITY_SETTINGS),
        output_type=MetadataSanityResult,
        system_prompt=METADATA_SANITY_PROMPT,
    )


def get_qa_verification_agent() -> Agent:
    """Get the QA verification agent (lazy initialization).

    Uses moderate temperature (0.3) for thorough, creative verification
    to find edge cases and quality issues.
    """
    logger.debug("Creating QA verification agent with custom settings")
    return Agent(
        model=get_openrouter_model(agent_settings=QA_VERIFICATION_SETTINGS),
        output_type=QAVerificationResult,
        system_prompt=QA_VERIFICATION_PROMPT,
    )


def get_concept_enrichment_agent() -> Agent:
    """Get the concept enrichment agent (lazy initialization).

    Uses moderate-high temperature (0.4) for creative, knowledge-rich
    content generation to transform generic stubs into meaningful documentation.
    """
    logger.debug("Creating concept enrichment agent with custom settings")
    return Agent(
        model=get_openrouter_model(agent_settings=CONCEPT_ENRICHMENT_SETTINGS),
        output_type=ConceptEnrichmentResult,
        system_prompt=CONCEPT_ENRICHMENT_PROMPT,
    )


def get_bilingual_parity_agent() -> Agent:
    """Get the bilingual parity check agent (lazy initialization).

    Uses low temperature (0.2) for consistent, deterministic parity checking
    to catch translation drift early in the review loop.
    """
    logger.debug("Creating bilingual parity check agent with custom settings")
    return Agent(
        model=get_openrouter_model(agent_settings=BILINGUAL_PARITY_SETTINGS),
        output_type=BilingualParityResult,
        system_prompt=BILINGUAL_PARITY_PROMPT,
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


async def run_concept_enrichment(
    concept_stub: str,
    concept_name: str,
    topic: str,
    referencing_notes: list[str] | None = None,
    **kwargs: Any,
) -> ConceptEnrichmentResult:
    """Enrich an auto-generated concept stub with meaningful content.

    This agent transforms generic placeholder content into a useful technical summary
    with definitions, key points, and examples.

    Args:
        concept_stub: The auto-generated concept file content (with generic placeholders)
        concept_name: Name of the concept (e.g., "dependency-injection", "coroutines")
        topic: Topic/domain from taxonomy (e.g., "kotlin", "android", "architecture-patterns")
        referencing_notes: Optional list of Q&A note excerpts that reference this concept
        **kwargs: Additional context

    Returns:
        ConceptEnrichmentResult with enriched content and metadata
    """
    logger.debug(f"Starting concept enrichment for: {concept_name} (topic: {topic})")

    # Build context from referencing notes
    references_context = ""
    if referencing_notes:
        logger.debug(f"Including {len(referencing_notes)} referencing notes as context")
        references_context = "\n\nREFERENCING NOTES (for context):\n"
        references_context += "\n---\n".join(referencing_notes[:5])  # Limit to 5 for token efficiency

    prompt = f"""Enrich this auto-generated concept stub with meaningful technical content.

CONCEPT NAME: {concept_name}
TOPIC/DOMAIN: {topic}

CURRENT STUB CONTENT:
```markdown
{concept_stub}
```
{references_context}

Transform the generic placeholder content into a concise, technically accurate summary suitable for interview preparation.
Focus on:
1. Clear definition in Summary sections (replace generic text)
2. 3-5 concrete key points (replace "To be documented")
3. Maintain bilingual parity (EN and RU sections must convey same information)
4. Preserve YAML frontmatter exactly as-is
5. Keep the structure and section ordering

Return the enriched content with meaningful definitions, key points, and context."""

    try:
        agent = get_concept_enrichment_agent()
        logger.debug("Running concept enrichment agent...")
        result = await agent.run(prompt)

        logger.debug(
            f"Concept enrichment complete - "
            f"added_sections: {len(result.output.added_sections)}, "
            f"key_concepts: {len(result.output.key_concepts)}, "
            f"related_concepts: {len(result.output.related_concepts)}"
        )

        logger.info(f"Enriched concept '{concept_name}': {result.output.explanation}")

        return result.output
    except Exception as e:
        logger.error(f"Concept enrichment failed for {concept_name}: {e}")
        raise


async def run_bilingual_parity_check(
    note_text: str, note_path: str, **kwargs: Any
) -> BilingualParityResult:
    """Check bilingual parity between EN and RU sections.

    This check runs early in the review loop (after validators) to catch
    translation drift before the final QA stage, reducing recycle time.

    Args:
        note_text: The note content to check
        note_path: Path to the note (for context)
        **kwargs: Additional context

    Returns:
        BilingualParityResult with parity findings
    """
    logger.debug(f"Starting bilingual parity check for: {note_path}")
    logger.debug(f"Note length: {len(note_text)} characters")

    prompt = (
        "Check bilingual parity between EN and RU sections in this note. "
        "Verify that both languages convey the same technical information and that "
        "no sections are missing in one language.\n\n"
        f"Note path: {note_path}\n\n"
        "```markdown\n"
        f"{note_text}\n"
        "```"
    )

    try:
        agent = get_bilingual_parity_agent()
        logger.debug("Running bilingual parity agent...")
        result = await agent.run(prompt)

        logger.debug(
            f"Bilingual parity check complete - "
            f"has_parity_issues: {result.output.has_parity_issues}, "
            f"parity_issues: {len(result.output.parity_issues)}, "
            f"missing_sections: {len(result.output.missing_sections)}"
        )

        if result.output.has_parity_issues:
            logger.warning(
                f"Parity check found {len(result.output.parity_issues)} issue(s) "
                f"and {len(result.output.missing_sections)} missing section(s)"
            )
        else:
            logger.success(f"Bilingual parity check passed: {result.output.summary}")

        return result.output
    except Exception as e:
        logger.error(f"Bilingual parity check failed for {note_path}: {e}")
        raise
