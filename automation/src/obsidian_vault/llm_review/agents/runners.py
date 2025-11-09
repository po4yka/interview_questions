"""Agent runner functions for executing LLM review tasks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from loguru import logger
from pydantic_ai import Agent
from pydantic_ai.exceptions import AgentRunError, ModelHTTPError, UserError

from obsidian_vault.exceptions import LLMResponseError
from obsidian_vault.utils.retry import async_retry

from .config import get_openrouter_model
from .factories import (
    get_bilingual_parity_agent,
    get_concept_enrichment_agent,
    get_issue_fix_agent,
    get_metadata_sanity_agent,
    get_qa_failure_summary_agent,
    get_qa_verification_agent,
)
from .models import (
    BilingualParityResult,
    ConceptEnrichmentResult,
    IssueFixResult,
    MetadataSanityResult,
    QAFailureSummaryResult,
    QAVerificationResult,
    TechnicalReviewResult,
)
from .prompts import TECHNICAL_REVIEW_PROMPT
from .settings import TECHNICAL_REVIEW_SETTINGS


def _build_taxonomy_context(taxonomy) -> dict[str, str]:
    """Build taxonomy context for the technical review prompt.

    Args:
        taxonomy: Taxonomy object with topics and android_subtopics

    Returns:
        Dictionary with formatted taxonomy context strings
    """
    from obsidian_vault.utils.taxonomy_loader import Taxonomy

    if taxonomy is None or not isinstance(taxonomy, Taxonomy):
        return {
            "valid_topics": "Not available",
            "android_subtopics": "Not available",
            "topic_folder_mapping": "Not available",
        }

    # Format topics list
    topics_list = sorted(taxonomy.topics) if taxonomy.topics else []
    valid_topics = ", ".join(topics_list) if topics_list else "Not available"

    # Format Android subtopics
    android_subs = sorted(taxonomy.android_subtopics) if taxonomy.android_subtopics else []
    android_subtopics = ", ".join(android_subs) if android_subs else "Not available"

    # Topic → Folder mapping (canonical mapping from TAXONOMY.md)
    topic_folder_mapping = """
    algorithms → 20-Algorithms/
    data-structures → 20-Algorithms/ (or 60-CompSci/)
    system-design → 30-System-Design/
    android → 40-Android/
    kotlin → 70-Kotlin/
    databases → 50-Backend/
    networking → 50-Backend/ (or 60-CompSci/)
    operating-systems → 60-CompSci/
    concurrency → 60-CompSci/ (or 70-Kotlin/ if Kotlin-specific)
    tools → 80-Tools/
    """

    return {
        "valid_topics": valid_topics,
        "android_subtopics": android_subtopics,
        "topic_folder_mapping": topic_folder_mapping.strip(),
    }


def _build_related_notes_context(
    note_path: str,
    vault_root,
    note_index: set[str] | None = None,
) -> str:
    """Build context from related notes mentioned in frontmatter.

    Args:
        note_path: Path to the current note
        vault_root: Path to vault root
        note_index: Set of available note filenames

    Returns:
        Formatted string with related notes context
    """
    from pathlib import Path
    from obsidian_vault.utils.common import parse_note

    if vault_root is None or note_index is None:
        return "Related notes context: Not available"

    try:
        # Parse the current note to get frontmatter
        current_path = Path(vault_root) / note_path if not Path(note_path).is_absolute() else Path(note_path)
        if not current_path.exists():
            return "Related notes context: Not available (note not found)"

        frontmatter, _ = parse_note(current_path)

        # Extract related notes from frontmatter
        related = frontmatter.get("related", [])
        if not related:
            return "Related notes context: No related notes specified in frontmatter"

        # Ensure related is a list
        if isinstance(related, str):
            related = [related]

        # Build context from related notes
        context_parts = ["Related notes context (from frontmatter):"]

        for note_name in related[:5]:  # Limit to 5 related notes to avoid context bloat
            # Add .md extension if not present
            if not note_name.endswith(".md"):
                note_name_with_ext = f"{note_name}.md"
            else:
                note_name_with_ext = note_name

            # Check if note exists in index
            if note_name_with_ext not in note_index:
                context_parts.append(f"  - {note_name}: (file not found in vault)")
                continue

            # Try to find and read the related note
            related_note_path = None
            for path in Path(vault_root).rglob(note_name_with_ext):
                related_note_path = path
                break

            if related_note_path and related_note_path.exists():
                try:
                    rel_frontmatter, rel_body = parse_note(related_note_path)
                    title = rel_frontmatter.get("title", note_name)
                    topic = rel_frontmatter.get("topic", "unknown")

                    # Extract first paragraph from body as summary
                    summary = ""
                    for line in rel_body.split("\n"):
                        line = line.strip()
                        if line and not line.startswith("#") and not line.startswith(">"):
                            summary = line[:150]  # First 150 chars
                            break

                    context_parts.append(
                        f"  - {note_name} (topic: {topic}): {title}"
                        + (f" - {summary}..." if summary else "")
                    )
                except Exception as e:
                    logger.debug("Failed to read related note {}: {}", note_name, e)
                    context_parts.append(f"  - {note_name}: (error reading file)")
            else:
                context_parts.append(f"  - {note_name}: (file not found)")

        return "\n".join(context_parts)

    except Exception as e:
        logger.debug("Error building related notes context: {}", e)
        return f"Related notes context: Error ({str(e)})"


@async_retry(
    max_attempts=3,
    initial_delay=2.0,
    retry_on=(ConnectionError, TimeoutError),
    skip_on=(ValueError, KeyError, LLMResponseError),
)
async def run_technical_review(
    note_text: str,
    note_path: str,
    taxonomy = None,
    vault_root = None,
    note_index: set[str] | None = None,
    **kwargs: Any
) -> TechnicalReviewResult:
    """Run technical review on a note with taxonomy and related notes context.

    This function includes retry logic for transient network errors.
    JSON parsing errors and validation errors are not retried.

    Args:
        note_text: The note content to review
        note_path: Path to the note (for context)
        taxonomy: Taxonomy object with controlled vocabularies
        vault_root: Path to vault root (for reading related notes)
        note_index: Set of available note filenames
        **kwargs: Additional context

    Returns:
        TechnicalReviewResult with findings and revised text

    Raises:
        LLMResponseError: If the LLM returns invalid or truncated JSON
        ConnectionError: If network connection fails (after retries)
        TimeoutError: If request times out (after retries)
    """
    logger.debug(f"Starting technical review for: {note_path}")
    logger.debug(f"Note length: {len(note_text)} characters")

    # Build taxonomy context
    taxonomy_context = _build_taxonomy_context(taxonomy)
    logger.debug(f"Taxonomy context: {len(taxonomy_context.get('valid_topics', ''))} topics")

    # Build related notes context
    related_notes_context = _build_related_notes_context(
        note_path=note_path,
        vault_root=vault_root,
        note_index=note_index,
    )
    logger.debug(f"Related notes context: {len(related_notes_context)} chars")

    # Format the system prompt with context
    formatted_system_prompt = TECHNICAL_REVIEW_PROMPT.format(
        valid_topics=taxonomy_context["valid_topics"],
        android_subtopics=taxonomy_context["android_subtopics"],
        topic_folder_mapping=taxonomy_context["topic_folder_mapping"],
        related_notes_context=related_notes_context,
    )

    # Create agent with contextualized system prompt
    agent = Agent(
        model=get_openrouter_model(agent_settings=TECHNICAL_REVIEW_SETTINGS),
        output_type=TechnicalReviewResult,
        system_prompt=formatted_system_prompt,
    )

    prompt = (
        "Review the following interview question note for technical accuracy, "
        "code correctness, and completeness while preserving formatting.\n\n"
        f"Note path: {note_path}\n\n"
        "```markdown\n"
        f"{note_text}\n"
        "```"
    )

    try:
        logger.debug("Running technical review agent with taxonomy and related notes context...")
        result = await agent.run(prompt)

        # Log the raw result for debugging
        logger.debug(f"Agent run result type: {type(result)}")
        logger.debug(f"Agent run result.output type: {type(result.output)}")

        logger.debug(
            f"Technical review complete - "
            f"has_issues: {result.output.has_issues}, "
            f"changes_made: {result.output.changes_made}, "
            f"issues_found: {len(result.output.issues_found)}"
        )

        if result.output.changes_made:
            logger.info(f"Technical review made changes: {result.output.explanation}")

        return result.output
    except AgentRunError as e:
        # pydantic-ai specific error when the agent fails to run
        error_msg = str(e)
        logger.error("Technical review agent run failed for {}: {}", note_path, e)
        logger.debug("Exception type: {}", type(e).__name__)
        logger.debug("Exception details: {}", repr(e))

        # Extract error details if available
        response_excerpt = None
        if hasattr(e, '__cause__') and e.__cause__:
            logger.debug("Underlying cause: {} - {}", type(e.__cause__).__name__, e.__cause__)
            # Try to extract from the cause if it's a Pydantic error
            cause = e.__cause__
            if hasattr(cause, 'errors'):
                logger.debug("Pydantic validation errors: {}", cause.errors())
                response_excerpt = str(cause.errors()[:3])  # First 3 errors
            else:
                response_excerpt = str(cause)[:500]

        # Raise custom exception with context
        raise LLMResponseError(
            "LLM agent run failed. "
            "This usually means the model returned an invalid response format, "
            "the response was truncated, or there was a validation error. "
            "Check agent settings, model capacity, and response format.",
            response_excerpt=response_excerpt,
            note_path=note_path,
        ) from e
    except (ValueError, json.JSONDecodeError) as e:
        # Enhanced error logging for JSON parsing and Pydantic validation issues
        error_msg = str(e)
        logger.error("Technical review failed for {} due to validation error: {}", note_path, e)
        logger.debug("Exception type: {}", type(e).__name__)
        logger.debug("Exception details: {}", repr(e))

        # Extract problematic JSON excerpt if available
        response_excerpt = None

        # Try to extract from Pydantic validation error
        if hasattr(e, 'errors'):
            # Pydantic ValidationError
            logger.debug("Pydantic validation errors: {}", e.errors())
            response_excerpt = str(e.errors()[:3])  # First 3 errors
        elif "input_value=" in error_msg:
            # Extract from error message
            import re
            match = re.search(r"input_value='([^']*)'", error_msg)
            if match:
                response_excerpt = match.group(1)

        if response_excerpt:
            logger.debug("Problematic response excerpt: {}", response_excerpt[:500])

        # Raise custom exception with context
        raise LLMResponseError(
            "LLM returned invalid or truncated JSON response. "
            "This usually means max_tokens is too low, the model truncated the output, "
            "or the response format doesn't match the expected schema. "
            "Check agent settings and model capacity.",
            response_excerpt=response_excerpt,
            note_path=note_path,
        ) from e
    except (ConnectionError, TimeoutError, ModelHTTPError) as e:
        # Log network errors (will be retried by decorator)
        logger.warning(
            "Network error during technical review for {}: {} - Will retry",
            note_path,
            str(e),
        )
        raise
    except Exception as e:
        # Log unexpected errors
        logger.error(
            "Unexpected error during technical review for {}: {} ({})",
            note_path,
            str(e),
            type(e).__name__,
        )
        logger.exception("Full traceback:")
        raise


async def run_issue_fixing(
    note_text: str, issues: list[str], note_path: str, **kwargs: Any
) -> IssueFixResult:
    """Fix formatting and structure issues in a note.

    Args:
        note_text: Current note content
        issues: List of issues to fix
        note_path: Path to the note
        **kwargs: Additional context including:
            - available_concepts: List of concept file basenames
            - available_qa_files: List of Q&A file basenames
            - valid_moc_files: List of MOC file basenames
            - fix_history: Formatted string of previous fix attempts

    Returns:
        IssueFixResult with corrected text
    """
    logger.debug(f"Starting issue fixing for: {note_path}")
    logger.debug(f"Number of issues to fix: {len(issues)}")

    for i, issue in enumerate(issues, 1):
        logger.debug(f"  Issue {i}: {issue[:100]}...")  # Log first 100 chars

    # Extract vault index from kwargs
    available_concepts = kwargs.get('available_concepts', [])
    available_qa_files = kwargs.get('available_qa_files', [])
    valid_moc_files = kwargs.get('valid_moc_files', [])
    fix_history = kwargs.get('fix_history', 'No previous fix attempts in this session.')

    # Build vault index context
    context_parts = []
    if available_concepts:
        # Limit to avoid token bloat
        concept_sample = available_concepts[:100]
        context_parts.append(
            f"AVAILABLE CONCEPT FILES (use ONLY these for concept links):\n"
            f"{', '.join(concept_sample)}"
            + (f"\n...and {len(available_concepts) - 100} more" if len(available_concepts) > 100 else "")
        )

    if valid_moc_files:
        context_parts.append(
            f"AVAILABLE MOC FILES:\n{', '.join(valid_moc_files)}"
        )

    if available_qa_files:
        # Sample Q&As for context (limit to 50 to avoid token limits)
        qa_sample = available_qa_files[:50]
        context_parts.append(
            f"AVAILABLE Q&A FILES (sample):\n{', '.join(qa_sample)}"
            + (f"\n...and {len(available_qa_files) - 50} more" if len(available_qa_files) > 50 else "")
        )

    vault_context = "\n\n".join(context_parts) if context_parts else "No vault index available."

    issues_text = "\n".join(f"- {issue}" for issue in issues)

    prompt = f"""Fix the following issues in this note.

Note path: {note_path}

{vault_context}

{fix_history}

CRITICAL RULES FOR FIXING:
1. When adding concept links ([[c-...]]), ONLY use concepts from the available list above
2. When adding MOC links, ONLY use MOC files from the available list above
3. If a required concept doesn't exist in the list, DO NOT add a broken link - note the missing file instead
4. Prefer existing concept files over creating new references
5. Do not invent or guess concept file names
6. Review the PREVIOUS FIX ATTEMPTS above - do NOT repeat failed strategies

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
        logger.error("Issue fixing failed for {}: {}", note_path, e)
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
        logger.error("Metadata sanity check failed for {}: {}", note_path, e)
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
        logger.error("QA verification failed for {}: {}", note_path, e)
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
        logger.error("Concept enrichment failed for {}: {}", concept_name, e)
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
        logger.error("Bilingual parity check failed for {}: {}", note_path, e)
        raise


async def run_qa_failure_summary(
    note_text: str,
    note_path: str,
    history: list[dict[str, Any]],
    unresolved_issues: list[str],
    qa_verification_summary: str | None,
    iteration_count: int,
    max_iterations: int,
    **kwargs: Any,
) -> QAFailureSummaryResult:
    """Summarize repeated QA failures for human follow-up.

    This agent triggers when the workflow reaches max iterations or QA verification
    fails repeatedly, creating an actionable summary for manual review.

    Args:
        note_text: The current note content (with remaining issues)
        note_path: Path to the note (for context)
        history: Full workflow history showing all iterations
        unresolved_issues: List of issues that could not be resolved
        qa_verification_summary: Summary from QA verification (if run)
        iteration_count: Number of iterations performed
        max_iterations: Maximum iterations allowed
        **kwargs: Additional context

    Returns:
        QAFailureSummaryResult with failure analysis and recommendations
    """
    logger.debug(f"Starting QA failure summary for: {note_path}")
    logger.debug(
        f"Iterations: {iteration_count}/{max_iterations}, "
        f"Unresolved issues: {len(unresolved_issues)}"
    )

    # Format history for context
    history_summary = []
    for entry in history:
        iteration = entry.get("iteration", "?")
        node = entry.get("node", "unknown")
        message = entry.get("message", "")
        history_summary.append(f"[Iteration {iteration}] {node}: {message}")

    history_text = "\n".join(history_summary)

    # Format unresolved issues
    issues_text = "\n".join(f"- {issue}" for issue in unresolved_issues)

    prompt = f"""Analyze this failed automated review and create an actionable summary for human follow-up.

Note path: {note_path}
Iterations: {iteration_count}/{max_iterations}
QA Verification Status: {'Run - Failed' if qa_verification_summary else 'Not Run'}

WORKFLOW HISTORY:
{history_text}

UNRESOLVED ISSUES:
{issues_text}

QA VERIFICATION SUMMARY:
{qa_verification_summary or 'QA verification was not run (did not reach QA stage)'}

CURRENT NOTE CONTENT:
```markdown
{note_text}
```

Analyze why the automated workflow could not resolve these issues and provide specific, actionable recommendations for manual review."""

    try:
        agent = get_qa_failure_summary_agent()
        logger.debug("Running QA failure summary agent...")
        result = await agent.run(prompt)

        logger.info(
            f"QA failure summary complete - "
            f"Failure type: {result.output.failure_type}, "
            f"Unresolved: {len(result.output.unresolved_issues)}, "
            f"Recommendations: {len(result.output.recommended_actions)}"
        )

        logger.warning(
            f"Automated review failed for {note_path}:\n"
            f"{result.output.human_readable_summary}"
        )

        return result.output
    except Exception as e:
        logger.error("QA failure summary failed for {}: {}", note_path, e)
        raise
