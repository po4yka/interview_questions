"""Agent-specific model settings for fine-tuned behavior."""

from __future__ import annotations

from .config import AgentModelSettings

# Agent-specific model settings
# These defaults balance creativity vs determinism for each agent's role
# Updated 2025-11: Optimized model selection based on OpenRouter benchmarks

TECHNICAL_REVIEW_SETTINGS = AgentModelSettings(
    # DeepSeek V3.1: Excellent reasoning capabilities, 671B params (37B active), 128K context
    # Ideal for creative technical insight while maintaining high accuracy
    model="deepseek/deepseek-chat-v3.1",
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
    # MiniMax M2: 10B activated (230B total), excellent for code generation & editing
    # 2x faster than Claude at 8% cost, optimal for deterministic fixes
    # Cost: $0.15/M input, $0.60/M output
    model="minimax/minimax-m2",
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
    # Qwen-Turbo: Most cost-effective option for simple validation tasks
    # 1M context, fast speed, low cost ($0.05/M input, $0.20/M output)
    model="qwen/qwen-turbo",
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
    # DeepSeek V3.1: Superior reasoning for critical verification and edge case discovery
    # Supports thinking modes for comprehensive quality analysis
    model="deepseek/deepseek-chat-v3.1",
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
    # Qwen3-Max: Enhanced multilingual support, improved reasoning, and long-tail knowledge
    # Ideal for bilingual content generation ($0.22/M input, $0.88/M output)
    # 131K context for comprehensive technical documentation
    model="qwen/qwen3-max",
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
    # Qwen-Turbo: Multilingual support at lowest cost, perfect for EN/RU parity checks
    # Fast processing for repetitive comparison tasks
    model="qwen/qwen-turbo",
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
    # DeepSeek V3.1: Strong analytical capabilities for pattern recognition and diagnosis
    # Excellent for providing actionable recommendations
    model="deepseek/deepseek-chat-v3.1",
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

FIX_COORDINATOR_SETTINGS = AgentModelSettings(
    # DeepSeek V3.1: Superior reasoning for strategic planning and dependency resolution
    # Optimized for agent capabilities and systematic task coordination
    model="deepseek/deepseek-chat-v3.1",
    # Low-moderate temperature for strategic planning with some flexibility
    # Needs to understand issue patterns and create optimal execution plans
    temperature=0.2,
    # Moderate penalties for clear, systematic planning
    presence_penalty=0.2,
    frequency_penalty=0.2,
    # Coordinator produces structured fix plan with groups, priorities, and dependencies
    # Set moderate limit for detailed planning output
    max_tokens=8192,  # 8K tokens
)
