"""Gap analysis workflow for identifying missing interview questions."""

from __future__ import annotations

import asyncio
import json
import os
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from textwrap import dedent
from typing import Any, Iterable, Sequence, TYPE_CHECKING

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from loguru import logger
from pydantic import BaseModel, Field, ValidationError, model_validator

from .agent import (
    ALLOWED_DIFFICULTY,
    ALLOWED_QUESTION_KIND,
    ALLOWED_TOPICS,
    CARD_REVIEW_CHECKLIST,
    VAULT_RULES_SNIPPET,
)
from .duplicate_checker import DuplicateChecker
from .models import GeneratedCard, SourceInfo
from .note_builder import NoteWriter
from obsidian_vault.llm_review import CompletionMode, ProcessingProfile, create_review_graph
from obsidian_vault.llm_review.agents.config import AgentModelSettings, OpenRouterConfig
from obsidian_vault.utils import (
    discover_repo_root,
    ensure_vault_exists,
    parse_note,
)
try:  # pragma: no cover - optional dependency hook
    from obsidian_vault.utils.graph_analytics import VaultGraph as _VaultGraph
except Exception:  # pragma: no cover - gracefully handle missing obsidiantools
    _VaultGraph = None

if TYPE_CHECKING:  # pragma: no cover - typing only
    from obsidian_vault.utils.graph_analytics import VaultGraph
else:  # pragma: no cover - at runtime we treat the dependency as optional
    VaultGraph = Any
from obsidian_vault.utils.taxonomy_loader import TaxonomyLoader


@dataclass(slots=True)
class ExistingNote:
    """Lightweight representation of an existing vault note."""

    path: Path
    topic: str
    slug: str
    difficulty: str
    question_kind: str
    title_en: str
    title_ru: str
    subtopics: list[str]
    tags: list[str]
    question_en: str | None = None
    question_ru: str | None = None
    answer_en: str | None = None
    answer_ru: str | None = None


@dataclass(slots=True)
class TopicMemory:
    """Aggregated snapshot for a single topic used as LLM memory."""

    topic: str
    total_notes: int
    difficulty_distribution: dict[str, int]
    question_kind_distribution: dict[str, int]
    subtopic_counts: dict[str, int]
    tag_counts: dict[str, int]
    underrepresented_subtopics: list[str]
    taxonomy_gaps: list[str]
    highlights: list[dict[str, object]]
    atomic_points: list["AtomicCoveragePoint"]


@dataclass(slots=True)
class AtomicCoveragePoint:
    """Fine-grained coverage signal for a specific subtopic."""

    subtopic: str
    note_count: int
    average_inbound: float
    average_outbound: float
    isolated_slugs: list[str]
    neighbor_examples: list[str]


@dataclass(slots=True)
class TopicRecommendation:
    """Recommendation for a topic including new cards to create."""

    topic: str
    rationale: str
    missing_concepts: list[str]
    cards: list[GeneratedCard]


@dataclass(slots=True)
class GapAnalysisResult:
    """Outcome from analyzing the vault for missing coverage."""

    topics: list[TopicRecommendation]
    duplicates: list[str]
    unique_cards: list[GeneratedCard]
    analyzed_on: date
    total_notes: int

    def total_recommendations(self) -> int:
        return sum(len(topic.cards) for topic in self.topics)


@dataclass(slots=True)
class GapApplicationResult:
    """Result from applying coverage recommendations."""

    created_paths: list[str]
    reviewed_notes: int


@dataclass(slots=True)
class GapAnalysisConfig:
    """Configuration for :class:`GapAnalysisAgent`."""

    agent_settings: AgentModelSettings | None = None
    temperature: float = 0.0
    max_tokens: int | None = 3200
    max_retries: int = 2
    max_notes_per_topic: int = 40
    max_question_chars: int = 220
    max_answer_chars: int = 260
    max_highlights_per_topic: int = 12
    max_atomic_points_per_topic: int = 10
    max_atomic_neighbors: int = 5


class _CardModel(BaseModel):
    slug: str = Field(..., pattern=r"^[a-z0-9\-]+$")
    topic: str
    difficulty: str
    question_kind: str
    title_en: str = Field(..., min_length=5)
    title_ru: str = Field(..., min_length=5)
    question_en: str = Field(..., min_length=5)
    question_ru: str = Field(..., min_length=5)
    answer_en: str = Field(..., min_length=50)
    answer_ru: str = Field(..., min_length=50)
    follow_ups_en: list[str] = Field(default_factory=list)
    follow_ups_ru: list[str] = Field(default_factory=list)
    subtopics: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    aliases: list[str] = Field(default_factory=list)
    related: list[str] = Field(default_factory=list)
    sources: list[dict[str, str]] = Field(default_factory=list)
    original_language: str | None = Field(default=None)

    @model_validator(mode="after")
    def _validate_enums(self) -> "_CardModel":
        if self.topic not in ALLOWED_TOPICS:
            raise ValueError(f"Unsupported topic: {self.topic}")
        if self.difficulty not in ALLOWED_DIFFICULTY:
            raise ValueError(f"Unsupported difficulty: {self.difficulty}")
        if self.question_kind not in ALLOWED_QUESTION_KIND:
            raise ValueError(f"Unsupported question_kind: {self.question_kind}")
        return self


class _TopicRecommendationModel(BaseModel):
    topic: str
    rationale: str = Field(..., min_length=20)
    missing_concepts: list[str] = Field(default_factory=list)
    cards: list[_CardModel]

    @model_validator(mode="after")
    def _validate_cards(self) -> "_TopicRecommendationModel":
        if not self.cards:
            raise ValueError("Each topic recommendation must include at least one card")
        return self


class _GapReportModel(BaseModel):
    topics: list[_TopicRecommendationModel]

    @model_validator(mode="after")
    def _validate_topics(self) -> "_GapReportModel":
        if not self.topics:
            raise ValueError("Agent returned no recommendations")
        return self


class GapAnalysisAgent:
    """Agent that reviews the vault snapshot and proposes new Q&A pairs."""

    def __init__(self, config: GapAnalysisConfig | None = None) -> None:
        self.config = config or GapAnalysisConfig()
        self._parser = PydanticOutputParser(pydantic_object=_GapReportModel)
        self._prompt = self._build_prompt()
        self._llm = self._build_llm()

    def _build_llm(self) -> ChatOpenAI:
        base_config = OpenRouterConfig.from_environment(
            override_model=(self.config.agent_settings.model if self.config.agent_settings else None)
        )
        settings = dict(base_config.settings_kwargs)
        if self.config.agent_settings:
            overrides = self.config.agent_settings
            if overrides.max_tokens is not None:
                settings["max_tokens"] = overrides.max_tokens
            if overrides.temperature is not None:
                settings["temperature"] = overrides.temperature
            if overrides.top_p is not None:
                settings["top_p"] = overrides.top_p
            if overrides.presence_penalty is not None:
                settings["presence_penalty"] = overrides.presence_penalty
            if overrides.frequency_penalty is not None:
                settings["frequency_penalty"] = overrides.frequency_penalty
            if overrides.timeout is not None:
                settings["timeout"] = overrides.timeout

        settings.setdefault("temperature", self.config.temperature)
        if self.config.max_tokens is not None:
            settings.setdefault("max_tokens", self.config.max_tokens)

        headers = dict(base_config.headers)
        extra_headers = settings.pop("extra_headers", None)
        if isinstance(extra_headers, dict):
            headers.update(extra_headers)

        temperature = settings.pop("temperature", 0.0)
        timeout = settings.pop("timeout", None)
        max_tokens = settings.pop("max_tokens", None)

        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            logger.error("OPENROUTER_API_KEY environment variable not set for gap analysis agent")
            raise ValueError(
                "OPENROUTER_API_KEY environment variable is required to analyze coverage gaps."
            )

        logger.debug("Initializing OpenRouter ChatOpenAI model for gap analysis", model=base_config.model)

        return ChatOpenAI(
            model=base_config.model,
            temperature=temperature,
            timeout=timeout,
            max_tokens=max_tokens,
            model_kwargs=settings or None,
            openai_api_base="https://openrouter.ai/api/v1",
            openai_api_key=api_key,
            default_headers=headers or None,
        )

    def _build_prompt(self) -> ChatPromptTemplate:
        instructions = dedent(
            """
            You are an expert curator for a bilingual Obsidian vault of interview questions.
            Review the existing coverage per topic and propose the highest-value missing questions.
            Follow the vault requirements strictly, generate bilingual content, and avoid duplicates.
            The user is providing a structured topic inventory with coverage statistics, underrepresented
            subtopics, taxonomy gaps, and representative note highlights. Use this "memory" to reason
            about nuanced missing angles before proposing new questions.
            Produce a JSON report that matches the provided schema.
            """
        )
        return ChatPromptTemplate.from_messages(
            [
                ("system", instructions + "\n\n" + VAULT_RULES_SNIPPET + "\n" + CARD_REVIEW_CHECKLIST),
                (
                    "human",
                    "Structured topic inventory (JSON per topic):\n{topic_inventory}\n\n"
                    "Use these statistics, underrepresented subtopics, taxonomy gaps, and note highlights to identify nuanced coverage gaps."
                    "\n{format_instructions}",
                ),
            ]
        )

    def analyze(self, notes: Sequence[ExistingNote], *, vault_root: Path) -> GapAnalysisResult:
        logger.info("Running gap analysis agent", note_count=len(notes))
        taxonomy = TaxonomyLoader(vault_root).load()
        vault_graph: VaultGraph | None = None
        if _VaultGraph is None:
            logger.warning(
                "obsidiantools is unavailable; atomic coverage signals disabled for gap analysis",
            )
        else:
            try:
                vault_graph = _VaultGraph(vault_root)
                logger.debug("Initialized obsidiantools VaultGraph for gap analysis")
            except Exception as error:  # pragma: no cover - graceful fallback when obsidiantools fails
                logger.warning(
                    "Unable to initialize obsidiantools vault graph; atomic coverage signals disabled",
                    error=str(error),
                )
        topic_memories = _build_topic_memories(
            notes,
            max_per_topic=self.config.max_notes_per_topic,
            max_question_chars=self.config.max_question_chars,
            max_answer_chars=self.config.max_answer_chars,
            max_highlights=self.config.max_highlights_per_topic,
            max_atomic_points=self.config.max_atomic_points_per_topic,
            max_atomic_neighbors=self.config.max_atomic_neighbors,
            vault_graph=vault_graph,
            vault_root=vault_root,
            taxonomy=taxonomy,
        )
        formatted_inventory = _format_topic_inventory(topic_memories)
        logger.debug("Prepared topic inventory for agent", topics=len(topic_memories))

        format_instructions = self._parser.get_format_instructions()
        messages = self._prompt.format_messages(
            topic_inventory=formatted_inventory or "No notes present in the vault.",
            format_instructions=format_instructions,
        )

        last_error: ValidationError | None = None
        for attempt in range(1, self.config.max_retries + 2):
            logger.debug("Gap analysis agent call", attempt=attempt)
            response = self._llm.invoke(messages)
            try:
                parsed = self._parser.parse(response.content)
                logger.success("Gap analysis agent succeeded", attempt=attempt)
                break
            except ValidationError as error:
                last_error = error
                logger.warning("Failed to parse agent output on attempt {}: {}", attempt, error)
                messages = [
                    ("system", "Reformat the previous response to satisfy the JSON schema."),
                    (
                        "human",
                        "The previous output failed schema validation with error:\n"
                        f"{error}\n\nPlease return a corrected JSON report that matches the schema exactly."
                        f"\nSchema instructions:\n{format_instructions}",
                    ),
                ]
        else:  # pragma: no cover - defensive guard
            raise last_error if last_error else RuntimeError("Gap analysis agent failed without error")

        assert parsed is not None  # for mypy
        report_model: _GapReportModel = parsed
        recommendations = [
            TopicRecommendation(
                topic=topic_model.topic,
                rationale=topic_model.rationale,
                missing_concepts=topic_model.missing_concepts,
                cards=[_convert_card(card_model) for card_model in topic_model.cards],
            )
            for topic_model in report_model.topics
        ]

        generated_cards = [card for recommendation in recommendations for card in recommendation.cards]
        logger.debug("Generated candidate cards from gap analysis", count=len(generated_cards))

        duplicate_checker = DuplicateChecker(vault_root)
        unique_cards, duplicates = duplicate_checker.filter_new_cards(generated_cards)

        filtered_recommendations: list[TopicRecommendation] = []
        unique_by_slug = {card.slug: card for card in unique_cards}
        for recommendation in recommendations:
            filtered_cards = [unique_by_slug[card.slug] for card in recommendation.cards if card.slug in unique_by_slug]
            if filtered_cards:
                filtered_recommendations.append(
                    TopicRecommendation(
                        topic=recommendation.topic,
                        rationale=recommendation.rationale,
                        missing_concepts=recommendation.missing_concepts,
                        cards=filtered_cards,
                    )
                )
            else:
                logger.info("Recommendation skipped due to duplicates", topic=recommendation.topic)

        result = GapAnalysisResult(
            topics=filtered_recommendations,
            duplicates=duplicates,
            unique_cards=unique_cards,
            analyzed_on=date.today(),
            total_notes=len(notes),
        )
        logger.success("Gap analysis complete", unique_cards=len(unique_cards), duplicates=len(duplicates))
        return result


@dataclass(slots=True)
class GapWorkflowConfig:
    """Configuration for :class:`GapAnalysisWorkflow`."""

    dry_run: bool = False
    auto_create: bool = False
    completion_mode: CompletionMode = CompletionMode.STANDARD
    processing_profile: ProcessingProfile = ProcessingProfile.BALANCED
    review_iterations: int = 6


class GapAnalysisWorkflow:
    """Coordinates the coverage analysis and optional note creation."""

    def __init__(
        self,
        *,
        repo_root: Path | None = None,
        agent: GapAnalysisAgent | None = None,
    ) -> None:
        resolved_repo = repo_root or discover_repo_root()
        vault_root = ensure_vault_exists(resolved_repo)
        self.repo_root = resolved_repo
        self.vault_root = vault_root
        self.agent = agent or GapAnalysisAgent()
        self.note_writer = NoteWriter(vault_root)

    def analyze(self) -> GapAnalysisResult:
        notes = list(_load_existing_notes(self.vault_root))
        if not notes:
            logger.warning("Vault contains no question notes to analyze")
        return self.agent.analyze(notes, vault_root=self.vault_root)

    def apply(self, result: GapAnalysisResult, config: GapWorkflowConfig) -> GapApplicationResult:
        if not result.unique_cards:
            logger.info("No unique cards available to create from gap analysis")
            return GapApplicationResult(created_paths=[], reviewed_notes=0)

        if config.dry_run:
            logger.info("Dry run enabled - skipping note creation for gap analysis")
            return GapApplicationResult(created_paths=[], reviewed_notes=0)

        note_paths = self.note_writer.write_cards(result.unique_cards, article_url="internal://gap-analysis")
        logger.info("Created notes from gap analysis", count=len(note_paths))

        self._run_review(note_paths, config)
        return GapApplicationResult(
            created_paths=[str(path) for path in note_paths],
            reviewed_notes=len(note_paths),
        )

    def _run_review(self, note_paths: Sequence[Path], config: GapWorkflowConfig) -> None:
        if not note_paths:
            return
        logger.info("Launching review flow for gap analysis notes", count=len(note_paths))
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
        logger.success("LLM review completed for gap analysis notes")


def _load_existing_notes(vault_root: Path) -> Iterable[ExistingNote]:
    logger.info("Scanning existing notes for gap analysis")
    for note_path in sorted(vault_root.rglob("q-*.md")):
        try:
            frontmatter, body = parse_note(note_path)
        except Exception as error:  # pragma: no cover - defensive fallback
            logger.error("Failed to parse note {}: {}", note_path.name, error)
            continue

        topic = str(frontmatter.get("topic", "")).strip()
        if not topic:
            logger.debug("Skipping note without topic", path=str(note_path))
            continue

        slug = note_path.stem.split("--")[0][2:]
        difficulty = str(frontmatter.get("difficulty", "medium")).strip()
        question_kind = str(frontmatter.get("question_kind", "theory")).strip()
        title = str(frontmatter.get("title", "")).strip()
        title_en, title_ru = _split_bilingual_title(title)
        subtopics = _clean_list(frontmatter.get("subtopics", []))
        tags = _clean_list(frontmatter.get("tags", []))
        question_en = _extract_question(body, "Question (EN)")
        question_ru = _extract_question(body, "Вопрос (RU)")
        answer_en = _extract_answer(body, "Answer (EN)")
        answer_ru = _extract_answer(body, "Ответ (RU)")

        yield ExistingNote(
            path=note_path,
            topic=topic,
            slug=slug,
            difficulty=difficulty,
            question_kind=question_kind,
            title_en=title_en,
            title_ru=title_ru,
            subtopics=subtopics,
            tags=tags,
            question_en=question_en,
            question_ru=question_ru,
            answer_en=answer_en,
            answer_ru=answer_ru,
        )


def _split_bilingual_title(title: str) -> tuple[str, str]:
    if " / " in title:
        en, ru = title.split(" / ", 1)
        return en.strip(), ru.strip()
    if "/" in title:
        en, ru = title.split("/", 1)
        return en.strip(), ru.strip()
    return title.strip(), title.strip()


def _clean_list(value: object) -> list[str]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value:
        return [value.strip()]
    return []


def _extract_question(body: str, heading: str) -> str | None:
    marker = f"# {heading}"
    if marker not in body:
        return None
    section = body.split(marker, 1)[1]
    lines = section.splitlines()
    collected: list[str] = []
    for line in lines[1:]:
        if line.startswith("# "):
            break
        if line.startswith("> "):
            collected.append(line[2:].strip())
        elif line.strip() and not collected:
            collected.append(line.strip())
    text = " ".join(collected).strip()
    return text or None


def _extract_answer(body: str, heading: str) -> str | None:
    marker = f"## {heading}"
    if marker not in body:
        return None
    section = body.split(marker, 1)[1]
    lines = section.splitlines()
    collected: list[str] = []
    for line in lines[1:]:
        if line.startswith("## "):
            break
        stripped = line.strip()
        if stripped:
            collected.append(stripped)
    text = " ".join(collected).strip()
    return text or None


def _convert_card(model: _CardModel) -> GeneratedCard:
    sources: list[SourceInfo] = []
    for source in model.sources:
        url = source.get("url")
        if not url:
            continue
        sources.append(SourceInfo(url=url, note=source.get("note")))
    return GeneratedCard(
        slug=model.slug,
        topic=model.topic,
        difficulty=model.difficulty,
        question_kind=model.question_kind,
        title_en=model.title_en,
        title_ru=model.title_ru,
        question_en=model.question_en,
        question_ru=model.question_ru,
        answer_en=model.answer_en,
        answer_ru=model.answer_ru,
        follow_ups_en=list(model.follow_ups_en),
        follow_ups_ru=list(model.follow_ups_ru),
        subtopics=list(model.subtopics),
        tags=list(model.tags),
        aliases=list(model.aliases),
        related=list(model.related),
        sources=sources,
        original_language=model.original_language or "ru",
    )


def _build_topic_memories(
    notes: Sequence[ExistingNote],
    *,
    max_per_topic: int,
    max_question_chars: int,
    max_answer_chars: int,
    max_highlights: int,
    max_atomic_points: int,
    max_atomic_neighbors: int,
    vault_graph: VaultGraph | None,
    vault_root: Path,
    taxonomy: object,
) -> dict[str, TopicMemory]:
    grouped: dict[str, list[ExistingNote]] = defaultdict(list)
    for note in notes:
        grouped[note.topic].append(note)

    android_expected: set[str] = getattr(taxonomy, "android_subtopics", set()) or set()

    memories: dict[str, TopicMemory] = {}
    for topic, topic_notes in grouped.items():
        difficulties = Counter(note.difficulty or "unknown" for note in topic_notes)
        question_kinds = Counter(note.question_kind or "unknown" for note in topic_notes)
        subtopic_counts = Counter(
            subtopic
            for note in topic_notes
            for subtopic in note.subtopics
            if subtopic
        )
        tag_counts = Counter(
            tag
            for note in topic_notes
            for tag in note.tags
            if tag
        )

        underrepresented = sorted(
            subtopic
            for subtopic, count in subtopic_counts.items()
            if count <= 1
        )

        taxonomy_gaps: list[str] = []
        if topic == "android" and android_expected:
            taxonomy_gaps = sorted(subtopic for subtopic in android_expected if subtopic not in subtopic_counts)

        highlights: list[dict[str, object]] = []
        sorted_notes = sorted(topic_notes, key=lambda n: (n.difficulty, n.slug))
        highlight_limit = len(sorted_notes)
        if max_per_topic > 0:
            highlight_limit = min(highlight_limit, max_per_topic)
        if max_highlights > 0:
            highlight_limit = min(highlight_limit, max_highlights)

        for note in sorted_notes[:highlight_limit]:
            highlight = {
                "slug": note.slug,
                "title_en": note.title_en,
                "difficulty": note.difficulty,
                "question_kind": note.question_kind,
                "subtopics": list(note.subtopics),
                "question_excerpt": _truncate(note.question_en or note.question_ru or "", max_question_chars),
                "answer_excerpt": _truncate(note.answer_en or note.answer_ru or "", max_answer_chars),
                "tags": list(note.tags[:8]),
            }
            highlights.append(highlight)

        atomic_points = _build_atomic_points_for_topic(
            notes=topic_notes,
            vault_graph=vault_graph,
            vault_root=vault_root,
            max_points=max_atomic_points,
            max_neighbors=max_atomic_neighbors,
        )

        memories[topic] = TopicMemory(
            topic=topic,
            total_notes=len(topic_notes),
            difficulty_distribution=_top_counter_entries(difficulties, limit=5),
            question_kind_distribution=_top_counter_entries(question_kinds, limit=5),
            subtopic_counts=_top_counter_entries(subtopic_counts, limit=25),
            tag_counts=_top_counter_entries(tag_counts, limit=25),
            underrepresented_subtopics=underrepresented,
            taxonomy_gaps=taxonomy_gaps,
            highlights=highlights,
            atomic_points=atomic_points,
        )

    return memories


def _build_atomic_points_for_topic(
    *,
    notes: Sequence[ExistingNote],
    vault_graph: VaultGraph | None,
    vault_root: Path,
    max_points: int,
    max_neighbors: int,
) -> list[AtomicCoveragePoint]:
    """Construct per-subtopic coverage signals using obsidiantools graph data."""

    if not vault_graph or not getattr(vault_graph, "graph", None):
        return []

    graph = vault_graph.graph
    slug_to_node: dict[str, str] = {}
    node_to_slug: dict[str, str] = {}
    for note in notes:
        node_id = _resolve_graph_node(graph, note, vault_root)
        if node_id:
            slug_to_node[note.slug] = node_id
            node_to_slug[node_id] = note.slug

    if not slug_to_node:
        return []

    subtopic_map: dict[str, list[ExistingNote]] = defaultdict(list)
    for note in notes:
        if note.subtopics:
            for subtopic in note.subtopics:
                subtopic_map[subtopic].append(note)
        else:
            subtopic_map["(unspecified)"].append(note)

    points: list[AtomicCoveragePoint] = []
    for subtopic, subtopic_notes in subtopic_map.items():
        inbound_counts: list[int] = []
        outbound_counts: list[int] = []
        isolated_slugs: list[str] = []
        neighbor_counter: Counter[str] = Counter()

        for note in subtopic_notes:
            node_id = slug_to_node.get(note.slug)
            if not node_id:
                isolated_slugs.append(note.slug)
                continue

            try:
                in_degree = graph.in_degree(node_id)
            except Exception:  # pragma: no cover - defensive fallback
                in_degree = 0
            try:
                out_degree = graph.out_degree(node_id)
            except Exception:  # pragma: no cover - defensive fallback
                out_degree = 0

            inbound_counts.append(int(in_degree))
            outbound_counts.append(int(out_degree))

            if in_degree == 0 and out_degree == 0:
                isolated_slugs.append(note.slug)

            try:
                successors = list(graph.successors(node_id))
            except Exception:  # pragma: no cover - defensive fallback
                successors = []
            try:
                predecessors = list(graph.predecessors(node_id))
            except Exception:  # pragma: no cover - defensive fallback
                predecessors = []

            for neighbor in successors + predecessors:
                resolved = node_to_slug.get(neighbor, neighbor)
                neighbor_counter[resolved] += 1

        point = AtomicCoveragePoint(
            subtopic=subtopic,
            note_count=len(subtopic_notes),
            average_inbound=_average(inbound_counts),
            average_outbound=_average(outbound_counts),
            isolated_slugs=sorted(set(isolated_slugs)),
            neighbor_examples=_top_counter_list(neighbor_counter, limit=max_neighbors),
        )
        points.append(point)

    points.sort(key=lambda item: (-item.note_count, item.subtopic))
    if max_points > 0:
        points = points[:max_points]
    return points


def _format_topic_inventory(topic_memories: dict[str, TopicMemory]) -> str:
    if not topic_memories:
        return ""

    sections: list[str] = []
    for topic in sorted(topic_memories):
        memory = topic_memories[topic]
        section = {
            "topic": memory.topic,
            "stats": {
                "total_notes": memory.total_notes,
                "difficulty_distribution": memory.difficulty_distribution,
                "question_kind_distribution": memory.question_kind_distribution,
            },
            "coverage": {
                "top_subtopics": memory.subtopic_counts,
                "top_tags": memory.tag_counts,
                "underrepresented_subtopics": memory.underrepresented_subtopics,
                "taxonomy_gaps": memory.taxonomy_gaps,
            },
            "atomic_points": [
                {
                    "subtopic": point.subtopic,
                    "note_count": point.note_count,
                    "avg_inbound_links": point.average_inbound,
                    "avg_outbound_links": point.average_outbound,
                    "isolated_slugs": point.isolated_slugs,
                    "neighbor_examples": point.neighbor_examples,
                }
                for point in memory.atomic_points
            ],
            "existing_notes": memory.highlights,
        }
        sections.append(json.dumps(section, ensure_ascii=False, indent=2))

    return "\n\n".join(sections)


def _top_counter_entries(counter: Counter[str], *, limit: int) -> dict[str, int]:
    if not counter:
        return {}
    sorted_items = sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    limited = sorted_items[: limit if limit > 0 else len(sorted_items)]
    return {key: value for key, value in limited}


def _truncate(value: str | None, limit: int) -> str:
    if not value:
        return ""
    if limit <= 0 or len(value) <= limit:
        return value
    return value[:limit].rstrip() + "…"


def _average(values: Sequence[int]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 2)


def _top_counter_list(counter: Counter[str], *, limit: int) -> list[str]:
    if not counter:
        return []
    sorted_items = sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    limited = sorted_items[: limit if limit > 0 else len(sorted_items)]
    return [key for key, _ in limited]


def _resolve_graph_node(graph: object, note: ExistingNote, vault_root: Path) -> str | None:
    """Best-effort mapping of a note path to an obsidiantools graph node."""

    candidates: list[str] = []
    try:
        relative = note.path.relative_to(vault_root)
        relative_posix = relative.as_posix()
        candidates.append(relative_posix)
        if relative.suffix:
            candidates.append(relative.with_suffix("").as_posix())
    except ValueError:
        pass

    candidates.append(note.path.name)
    candidates.append(note.path.stem)

    for candidate in candidates:
        try:
            if graph.has_node(candidate):
                return candidate
        except Exception:  # pragma: no cover - defensive fallback
            return None
    return None
