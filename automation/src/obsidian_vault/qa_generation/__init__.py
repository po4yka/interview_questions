"""Q&A ingestion workflow for creating interview notes from articles."""

from .agent import CardGenerationAgent, CardGenerationConfig
from .firecrawl import FirecrawlClient, FirecrawlError
from .gap_analysis import (
    GapAnalysisAgent,
    GapAnalysisConfig,
    GapAnalysisResult,
    GapAnalysisWorkflow,
    GapApplicationResult,
    GapWorkflowConfig,
    TopicRecommendation,
)
from .models import GeneratedCard, SourceInfo, WorkflowResult
from .note_builder import NoteWriter, build_note_content, generate_note_id, slugify
from .workflow import NoteIngestionWorkflow, WorkflowConfig

__all__ = [
    "NoteIngestionWorkflow",
    "WorkflowConfig",
    "CardGenerationAgent",
    "CardGenerationConfig",
    "GapAnalysisAgent",
    "GapAnalysisConfig",
    "GapAnalysisResult",
    "GapAnalysisWorkflow",
    "GapWorkflowConfig",
    "GapApplicationResult",
    "TopicRecommendation",
    "FirecrawlClient",
    "FirecrawlError",
    "GeneratedCard",
    "SourceInfo",
    "WorkflowResult",
    "NoteWriter",
    "build_note_content",
    "generate_note_id",
    "slugify",
]
