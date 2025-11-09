"""Agent factory functions for creating configured PydanticAI agents."""

from __future__ import annotations

from loguru import logger
from pydantic_ai import Agent

from .config import get_openrouter_model
from .models import (
    BilingualParityResult,
    ConceptEnrichmentResult,
    IssueFixResult,
    MetadataSanityResult,
    QAFailureSummaryResult,
    QAVerificationResult,
    TechnicalReviewResult,
)
from .prompts import (
    BILINGUAL_PARITY_PROMPT,
    CONCEPT_ENRICHMENT_PROMPT,
    ISSUE_FIX_PROMPT,
    METADATA_SANITY_PROMPT,
    QA_FAILURE_SUMMARY_PROMPT,
    QA_VERIFICATION_PROMPT,
    TECHNICAL_REVIEW_PROMPT,
)
from .settings import (
    BILINGUAL_PARITY_SETTINGS,
    CONCEPT_ENRICHMENT_SETTINGS,
    ISSUE_FIX_SETTINGS,
    METADATA_SANITY_SETTINGS,
    QA_FAILURE_SUMMARY_SETTINGS,
    QA_VERIFICATION_SETTINGS,
    TECHNICAL_REVIEW_SETTINGS,
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


def get_qa_failure_summary_agent() -> Agent:
    """Get the QA failure summarizer agent (lazy initialization).

    Uses moderate temperature (0.3) for analytical summarization to diagnose
    why automated review failed and provide actionable recommendations.
    """
    logger.debug("Creating QA failure summary agent with custom settings")
    return Agent(
        model=get_openrouter_model(agent_settings=QA_FAILURE_SUMMARY_SETTINGS),
        output_type=QAFailureSummaryResult,
        system_prompt=QA_FAILURE_SUMMARY_PROMPT,
    )
