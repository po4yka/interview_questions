"""PydanticAI agents for note review and fixing.

This module has been refactored into the agents/ package for better maintainability.
All exports from this module maintain backward compatibility.

The agents/ package contains:
- models.py: Pydantic result models (~140 LoC)
- config.py: OpenRouter configuration (~220 LoC)
- prompts.py: System prompts (~520 LoC)
- settings.py: Per-agent settings (~65 LoC)
- factories.py: Agent factory functions (~145 LoC)
- runners.py: Agent runner functions (~465 LoC)

Original file: 1636 LoC → Split into 6 focused modules averaging ~260 LoC each.
"""

# Re-export all public APIs from the agents package for backward compatibility
from .agents import *  # noqa: F401, F403

__all__ = [
    # Result models
    "TechnicalReviewResult",
    "IssueFixResult",
    "MetadataSanityResult",
    "QAVerificationResult",
    "BilingualParityResult",
    "ConceptEnrichmentResult",
    "QAFailureSummaryResult",
    # Configuration
    "AgentModelSettings",
    "OpenRouterConfig",
    "get_openrouter_model",
    # Agent factories
    "get_technical_review_agent",
    "get_issue_fix_agent",
    "get_metadata_sanity_agent",
    "get_qa_verification_agent",
    "get_concept_enrichment_agent",
    "get_bilingual_parity_agent",
    "get_qa_failure_summary_agent",
    # Agent runners
    "run_technical_review",
    "run_issue_fixing",
    "run_metadata_sanity_check",
    "run_qa_verification",
    "run_concept_enrichment",
    "run_bilingual_parity_check",
    "run_qa_failure_summary",
]
