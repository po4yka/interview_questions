"""Agent-specific model settings for fine-tuned behavior."""

from __future__ import annotations

from .config import AgentModelSettings

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

QA_FAILURE_SUMMARY_SETTINGS = AgentModelSettings(
    # Moderate temperature for analytical summarization with diagnostic insight
    # Needs to analyze patterns and provide actionable recommendations
    temperature=0.3,
    # Lower penalties to allow comprehensive analysis and varied recommendations
    presence_penalty=0.1,
    frequency_penalty=0.1,
)
