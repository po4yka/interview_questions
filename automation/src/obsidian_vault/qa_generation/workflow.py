"""End-to-end workflow for generating and reviewing new Q&A notes from articles."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from loguru import logger

from .agent import CardGenerationAgent
from .duplicate_checker import DuplicateChecker
from .firecrawl import FirecrawlClient, FirecrawlError
from .models import WorkflowResult
from .note_builder import NoteWriter
from obsidian_vault.llm_review import CompletionMode, ProcessingProfile, create_review_graph
from obsidian_vault.utils import discover_repo_root, ensure_vault_exists


@dataclass(slots=True)
class WorkflowConfig:
    max_cards: int = 3
    dry_run: bool = False
    completion_mode: CompletionMode = CompletionMode.STANDARD
    processing_profile: ProcessingProfile = ProcessingProfile.BALANCED
    review_iterations: int = 6


class NoteIngestionWorkflow:
    """Coordinates the Q&A note ingestion pipeline."""

    def __init__(
        self,
        *,
        repo_root: Path | None = None,
        firecrawl_client: FirecrawlClient | None = None,
        card_agent: CardGenerationAgent | None = None,
    ) -> None:
        resolved_repo = repo_root or discover_repo_root()
        vault_root = ensure_vault_exists(resolved_repo)
        self.repo_root = resolved_repo
        self.vault_root = vault_root
        self.firecrawl = firecrawl_client or FirecrawlClient()
        self.card_agent = card_agent or CardGenerationAgent()
        self.note_writer = NoteWriter(self.vault_root)

    def run(self, url: str, config: WorkflowConfig | None = None) -> WorkflowResult:
        workflow_config = config or WorkflowConfig()
        logger.info("Starting Q&A ingestion workflow", url=url, dry_run=workflow_config.dry_run)

        try:
            article_markdown = self.firecrawl.fetch_markdown(url)
        except FirecrawlError as error:
            logger.error("Failed to fetch article via Firecrawl: {}", error)
            raise

        generated_cards = self.card_agent.generate_cards(
            article_markdown=article_markdown,
            url=url,
            max_cards=workflow_config.max_cards,
        )
        if not generated_cards:
            logger.warning("Card generation agent returned no candidates")

        duplicate_checker = DuplicateChecker(self.vault_root)
        unique_cards, duplicates = duplicate_checker.filter_new_cards(generated_cards)
        logger.info(
            "Filtered cards", unique=len(unique_cards), duplicates=len(duplicates), skipped=duplicates
        )

        created_paths: list[str] = []
        if not workflow_config.dry_run and unique_cards:
            created = self.note_writer.write_cards(unique_cards, article_url=url)
            created_paths = [str(path) for path in created]
            self._run_review(created, workflow_config)
        elif workflow_config.dry_run:
            logger.info("Dry run enabled - not writing notes to disk")

        result = WorkflowResult(
            article_url=url,
            article_text=article_markdown,
            generated_cards=unique_cards,
            created_paths=created_paths,
            skipped_duplicates=duplicates,
            run_date=date.today(),
        )
        logger.success("Q&A ingestion workflow complete", created=len(created_paths))
        return result

    def _run_review(self, note_paths: list[Path], config: WorkflowConfig) -> None:
        if not note_paths:
            return
        logger.info("Launching LLM review flow for new notes", count=len(note_paths))
        review_graph = create_review_graph(
            self.vault_root,
            max_iterations=config.review_iterations,
            dry_run=False,
            completion_mode=config.completion_mode,
            processing_profile=config.processing_profile,
        )
        async def _review_all() -> None:
            for note_path in note_paths:
                logger.debug("Running review for {}", note_path.name)
                await review_graph.process_note(note_path)

        asyncio.run(_review_all())
        logger.success("LLM review completed for all new notes")
