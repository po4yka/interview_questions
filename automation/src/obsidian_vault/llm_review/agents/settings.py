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
    # Set sufficient max_tokens to ensure complete JSON responses
    # Technical reviews typically need full note text + analysis
    max_tokens=8192,
)

ISSUE_FIX_SETTINGS = AgentModelSettings(
    # Lower temperature for deterministic, conservative fixes
    temperature=0.1,
    # Higher penalties to discourage repetition and encourage precise, minimal changes
    presence_penalty=0.3,
    frequency_penalty=0.3,
    # Set sufficient max_tokens for fixing issues and returning full note text
    max_tokens=8192,
)

METADATA_SANITY_SETTINGS = AgentModelSettings(
    # Very low temperature for structured, deterministic metadata validation
    temperature=0.1,
    # Moderate penalties for clear, concise issue reporting
    presence_penalty=0.2,
    frequency_penalty=0.2,
    # Metadata checks produce compact JSON, but set reasonable limit
    max_tokens=2048,
)

QA_VERIFICATION_SETTINGS = AgentModelSettings(
    # Moderate temperature for thorough, creative verification
    # Needs to think critically and find edge cases
    temperature=0.3,
    # Lower penalties to allow comprehensive issue exploration
    presence_penalty=0.1,
    frequency_penalty=0.1,
    # QA verification may produce detailed findings
    max_tokens=4096,
)

CONCEPT_ENRICHMENT_SETTINGS = AgentModelSettings(
    # Moderate-high temperature for creative, knowledge-rich content generation
    # Needs to synthesize information and provide meaningful explanations
    temperature=0.4,
    # Lower penalties to allow varied technical vocabulary and comprehensive coverage
    presence_penalty=0.0,
    frequency_penalty=0.1,
    # Concept enrichment needs space for full bilingual content
    max_tokens=8192,
)

BILINGUAL_PARITY_SETTINGS = AgentModelSettings(
    # Low temperature for consistent, deterministic parity checking
    # Should be precise and analytical, not creative
    temperature=0.2,
    # Moderate penalties for clear, concise issue reporting
    presence_penalty=0.2,
    frequency_penalty=0.2,
    # Parity checks produce compact JSON with issue lists
    max_tokens=2048,
)

QA_FAILURE_SUMMARY_SETTINGS = AgentModelSettings(
    # Moderate temperature for analytical summarization with diagnostic insight
    # Needs to analyze patterns and provide actionable recommendations
    temperature=0.3,
    # Lower penalties to allow comprehensive analysis and varied recommendations
    presence_penalty=0.1,
    frequency_penalty=0.1,
    # Failure summaries need space for detailed analysis
    max_tokens=4096,
)
