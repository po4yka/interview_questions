"""PydanticAI agents for note review and fixing.

This package has been refactored from a single large file into smaller, focused modules:

- models.py: Pydantic result models
- config.py: OpenRouter configuration and settings
- prompts.py: System prompts for each agent
- settings.py: Per-agent model settings
- factories.py: Agent factory functions
- runners.py: Agent runner functions (async)

Public API exports maintain backward compatibility with the original agents.py file.
"""

from .config import (
    AgentModelSettings,
    OpenRouterConfig,
    get_openrouter_model,
)
from .factories import (
    get_bilingual_parity_agent,
    get_concept_enrichment_agent,
    get_issue_fix_agent,
    get_metadata_sanity_agent,
    get_qa_failure_summary_agent,
    get_qa_verification_agent,
    get_technical_review_agent,
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
from .runners import (
    run_bilingual_parity_check,
    run_concept_enrichment,
    run_issue_fixing,
    run_metadata_sanity_check,
    run_qa_failure_summary,
    run_qa_verification,
    run_technical_review,
)

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
