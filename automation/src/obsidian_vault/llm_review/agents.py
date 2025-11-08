"""PydanticAI agents for note review and fixing."""

from __future__ import annotations

import os
from typing import Any

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel


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


def get_openrouter_model(model_name: str = "anthropic/claude-sonnet-4") -> OpenAIModel:
    """Get an OpenRouter model configured for use with PydanticAI.

    Args:
        model_name: The model identifier (default: Polaris Alpha via Claude Sonnet 4)

    Returns:
        Configured OpenAIModel instance

    Raises:
        ValueError: If OPENROUTER_API_KEY is not set
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY environment variable is required. "
            "Get your API key from https://openrouter.ai/keys"
        )

    return OpenAIModel(
        model_name=model_name,
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )


# Agent for initial technical review
technical_review_agent = Agent(
    model=get_openrouter_model,
    result_type=TechnicalReviewResult,
    system_prompt="""You are an expert technical reviewer for interview preparation notes.

Your task is to review notes for technical accuracy and factual correctness.

FOCUS ON:
- Technical accuracy of explanations
- Correctness of code examples
- Logical consistency
- Completeness of technical content
- Accuracy of complexity analysis (Big-O notation)

DO NOT:
- Change formatting or structure (this will be handled separately)
- Modify YAML frontmatter
- Change language-specific sections
- Alter bilingual structure (EN/RU sections)

If you find technical issues, correct them while preserving:
- The original structure and formatting
- All YAML frontmatter
- All markdown headings and sections
- Bilingual content organization

Return the corrected text with clear explanation of changes.""",
)


# Agent for fixing formatting and structure issues
issue_fix_agent = Agent(
    model=get_openrouter_model,
    result_type=IssueFixResult,
    system_prompt="""You are an expert at fixing formatting and structural issues in Markdown notes.

You will receive:
1. The current note text
2. A list of validation issues to fix

Your task is to fix ALL the reported issues while:
- Preserving the semantic meaning
- Maintaining technical accuracy
- Keeping the bilingual structure (EN/RU sections)
- Following Obsidian vault conventions

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

Fix each issue precisely and return the corrected text.""",
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
    prompt = f"""Review this interview question note for technical accuracy.

Note path: {note_path}

Note content:
{note_text}

Check for technical correctness, code accuracy, and completeness.
If you find issues, fix them while preserving structure and formatting."""

    result = await technical_review_agent.run(prompt)
    return result.data


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
    issues_text = "\n".join(f"- {issue}" for issue in issues)

    prompt = f"""Fix the following issues in this note:

Note path: {note_path}

ISSUES TO FIX:
{issues_text}

CURRENT NOTE CONTENT:
{note_text}

Fix ALL issues while preserving meaning and following vault rules.
Return the corrected text."""

    result = await issue_fix_agent.run(prompt)
    return result.data
