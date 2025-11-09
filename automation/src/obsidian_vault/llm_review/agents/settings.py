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
    # Technical reviews return full note text + analysis
    # Model supports 128K output, set generous limit for large notes
    max_tokens=65536,  # 64K tokens
)

ISSUE_FIX_SETTINGS = AgentModelSettings(
    # Lower temperature for deterministic, conservative fixes
    temperature=0.1,
    # Higher penalties to discourage repetition and encourage precise, minimal changes
    presence_penalty=0.3,
    frequency_penalty=0.3,
    # Issue fixing returns complete revised note text
    # Model supports 128K output, set generous limit
    max_tokens=65536,  # 64K tokens
)

METADATA_SANITY_SETTINGS = AgentModelSettings(
    # Very low temperature for structured, deterministic metadata validation
    temperature=0.1,
    # Moderate penalties for clear, concise issue reporting
    presence_penalty=0.2,
    frequency_penalty=0.2,
    # Metadata checks produce compact JSON (issues, warnings, suggestions)
    # Set moderate limit to allow detailed issue descriptions
    max_tokens=8192,  # 8K tokens
)

QA_VERIFICATION_SETTINGS = AgentModelSettings(
    # Moderate temperature for thorough, creative verification
    # Needs to think critically and find edge cases
    temperature=0.3,
    # Lower penalties to allow comprehensive issue exploration
    presence_penalty=0.1,
    frequency_penalty=0.1,
    # QA verification produces detailed findings (factual errors, parity issues, quality concerns)
    # Set generous limit for comprehensive analysis
    max_tokens=16384,  # 16K tokens
)

CONCEPT_ENRICHMENT_SETTINGS = AgentModelSettings(
    # Moderate-high temperature for creative, knowledge-rich content generation
    # Needs to synthesize information and provide meaningful explanations
    temperature=0.4,
    # Lower penalties to allow varied technical vocabulary and comprehensive coverage
    presence_penalty=0.0,
    frequency_penalty=0.1,
    # Concept enrichment creates full bilingual concept notes with examples and references
    # Set generous limit for comprehensive content generation
    max_tokens=32768,  # 32K tokens
)

BILINGUAL_PARITY_SETTINGS = AgentModelSettings(
    # Low temperature for consistent, deterministic parity checking
    # Should be precise and analytical, not creative
    temperature=0.2,
    # Moderate penalties for clear, concise issue reporting
    presence_penalty=0.2,
    frequency_penalty=0.2,
    # Parity checks produce JSON with parity issues and missing sections
    # Set moderate limit for detailed difference descriptions
    max_tokens=8192,  # 8K tokens
)

QA_FAILURE_SUMMARY_SETTINGS = AgentModelSettings(
    # Moderate temperature for analytical summarization with diagnostic insight
    # Needs to analyze patterns and provide actionable recommendations
    temperature=0.3,
    # Lower penalties to allow comprehensive analysis and varied recommendations
    presence_penalty=0.1,
    frequency_penalty=0.1,
    # Failure summaries provide iteration analysis, unresolved issues, and recommendations
    # Set generous limit for comprehensive diagnostic output
    max_tokens=16384,  # 16K tokens
)
