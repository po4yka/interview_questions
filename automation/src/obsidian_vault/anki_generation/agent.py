"""LangChain agent responsible for generating bilingual Q&A cards."""

from __future__ import annotations

from dataclasses import dataclass
import os
from textwrap import dedent
from typing import Iterable, Literal

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from loguru import logger
from pydantic import BaseModel, Field, HttpUrl, ValidationError, model_validator

from obsidian_vault.anki_generation.models import GeneratedCard, SourceInfo
from obsidian_vault.llm_review.agents.config import AgentModelSettings, OpenRouterConfig


ALLOWED_TOPICS: tuple[str, ...] = (
    "algorithms",
    "system-design",
    "android",
    "backend",
    "cs",
    "kotlin",
    "tools",
)

ALLOWED_DIFFICULTY: tuple[str, ...] = ("easy", "medium", "hard")
ALLOWED_QUESTION_KIND: tuple[str, ...] = ("coding", "theory", "practical", "system-design", "android")


VAULT_RULES_SNIPPET = dedent(
    """
    Vault requirements:
    - Every note is bilingual (Russian first, then English) with matching meaning.
    - YAML frontmatter must include: id, title, aliases, topic, subtopics, question_kind, difficulty,
      original_language, language_tags, status=draft, moc, related, created, updated, tags, sources.
    - Tags are English only and must include lang/ru, lang/en, and difficulty/<level>.
    - Question belongs to one topic folder only and references moc-<topic> plus at least two related items.
    - Answers should be substantial (≥3 paragraphs in RU and EN) with clear structure and no emoji.
    """
)

CARD_REVIEW_CHECKLIST = dedent(
    """
    Quality checklist before returning cards:
    1. Are the slugs concise kebab-case identifiers that match the question scope?
    2. Do EN/RU titles, questions, and answers provide equivalent information and enough depth?
    3. Do answers cite concrete facts from the article and highlight actionable insights?
    4. Are follow-up questions practical and different between RU and EN where appropriate?
    5. Are tags reusable, English only, and free of duplicates?
    """
)


class _SourceModel(BaseModel):
    url: HttpUrl
    note: str | None = Field(default=None, max_length=200)


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
    sources: list[_SourceModel] = Field(default_factory=list)
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


class _GenerationResponse(BaseModel):
    cards: list[_CardModel]

    @model_validator(mode="after")
    def _validate_card_count(self) -> "_GenerationResponse":
        if not self.cards:
            raise ValueError("Agent returned no cards")
        return self


@dataclass(slots=True)
class CardGenerationConfig:
    """Configuration for :class:`CardGenerationAgent`."""

    agent_settings: AgentModelSettings | None = None
    temperature: float = 0.2
    max_tokens: int | None = 2400
    summary_temperature: float = 0.0
    summary_max_tokens: int | None = 800
    summary_source_max_chars: int = 12000
    summary_bullet_count: int = 8
    max_article_chars: int = 6000
    max_retries: int = 2
    retry_feedback_max_chars: int = 1500


class CardGenerationAgent:
    """Orchestrates the LangChain call that produces Q&A cards."""

    def __init__(self, config: CardGenerationConfig | None = None) -> None:
        self.config = config or CardGenerationConfig()
        self._parser = PydanticOutputParser(pydantic_object=_GenerationResponse)
        self._prompt = self._build_prompt()
        self._summary_prompt = self._build_summary_prompt()
        self._llm = self._build_llm()
        self._summary_llm = self._build_llm(purpose="summary")

    def _build_llm(self, *, purpose: Literal["generation", "summary"] = "generation") -> ChatOpenAI:
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

        if purpose == "summary":
            settings.setdefault("temperature", self.config.summary_temperature)
            if self.config.summary_max_tokens is not None:
                settings.setdefault("max_tokens", self.config.summary_max_tokens)
        else:
            settings.setdefault("temperature", self.config.temperature)
            if self.config.max_tokens is not None:
                settings.setdefault("max_tokens", self.config.max_tokens)

        headers = dict(base_config.headers)
        extra_headers = settings.pop("extra_headers", None)
        if isinstance(extra_headers, dict):
            headers.update(extra_headers)

        temperature = settings.pop("temperature", 0.2)
        timeout = settings.pop("timeout", None)
        max_tokens = settings.pop("max_tokens", None)

        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            logger.error("OPENROUTER_API_KEY environment variable not set for card generation agent")
            raise ValueError(
                "OPENROUTER_API_KEY environment variable is required to generate cards."
            )

        logger.debug(
            "Initializing OpenRouter ChatOpenAI model for card generation", model=base_config.model
        )

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
        format_instructions = self._parser.get_format_instructions()
        system_prompt = dedent(
            """
            You are an expert bilingual interviewer who creates Anki-style Obsidian notes.
            Work step-by-step: reason about the article, identify discrete Q&A opportunities,
            and only then draft polished bilingual content that satisfies every vault rule.
            """
        ).strip()
        human_prompt = dedent(
            """
            Article URL: {url}
            Maximum requested cards: {max_requested_cards}

            Article insights (LLM summary):
            {article_summary}

            Article excerpts (truncated markdown):
            {article_markdown}

            Vault rules to follow:
            {vault_rules}

            Checklist before finalizing cards:
            {quality_checklist}

            Feedback from previous attempt (if any):
            {feedback}

            Return JSON with a `cards` array. Each card must include slug, topic, difficulty,
            question_kind, title_en, title_ru, question_en, question_ru, answer_en, answer_ru,
            follow_ups_en, follow_ups_ru, subtopics, tags, aliases, related, sources, and original_language.
            Topics must be one of {topics}. Difficulties must be {difficulties}. Ensure tags include
            lang/ru, lang/en, difficulty/<level>, and other reusable English keywords. Sources must
            include the article URL.

            {format_instructions}
            """
        ).strip()
        return ChatPromptTemplate.from_messages([("system", system_prompt), ("human", human_prompt)])

    def _build_summary_prompt(self) -> ChatPromptTemplate:
        system_prompt = dedent(
            """
            You are a meticulous research assistant. Extract the most important concepts and
            facts from the article for downstream note generation.
            """
        ).strip()
        human_prompt = dedent(
            """
            Summarize the following article markdown into at most {bullet_count} bullet points.
            Focus on interview-ready insights, definitions, trade-offs, and step-by-step processes.
            Keep bullets concise but information rich. Use English only. Return plain text bullets.

            Article markdown (truncated):
            {article_markdown}
            """
        ).strip()
        return ChatPromptTemplate.from_messages([("system", system_prompt), ("human", human_prompt)])

    def generate_cards(self, *, article_markdown: str, url: str, max_cards: int) -> list[GeneratedCard]:
        logger.info("Generating candidate cards from article", url=url, max_cards=max_cards)
        summary = self._summarize_article(article_markdown)
        article_excerpt = _truncate_text(article_markdown, self.config.max_article_chars)
        payload = {
            "url": url,
            "article_markdown": article_excerpt,
            "article_summary": summary or "(Summary unavailable)",
            "vault_rules": VAULT_RULES_SNIPPET,
            "quality_checklist": CARD_REVIEW_CHECKLIST,
            "feedback": "No additional feedback. Return well-structured JSON only.",
            "topics": ", ".join(ALLOWED_TOPICS),
            "difficulties": ", ".join(ALLOWED_DIFFICULTY),
            "max_requested_cards": max_cards,
            "format_instructions": self._parser.get_format_instructions(),
        }
        parsed = self._invoke_with_retries(payload)

        cards: list[GeneratedCard] = []
        limit = max_cards if max_cards > 0 else len(parsed.cards)
        for card in parsed.cards[:limit]:
            sources = [SourceInfo(url=str(source.url), note=source.note) for source in card.sources]
            generated = GeneratedCard(
                slug=card.slug,
                topic=card.topic,
                difficulty=card.difficulty,
                question_kind=card.question_kind,
                title_en=card.title_en,
                title_ru=card.title_ru,
                question_en=card.question_en,
                question_ru=card.question_ru,
                answer_en=card.answer_en,
                answer_ru=card.answer_ru,
                follow_ups_en=list(card.follow_ups_en or []),
                follow_ups_ru=list(card.follow_ups_ru or []),
                subtopics=list(_clean_strings(card.subtopics)),
                tags=list(_clean_strings(card.tags)),
                aliases=list(_clean_strings(card.aliases)),
                related=list(_clean_strings(card.related)),
                sources=sources,
                original_language=card.original_language or "ru",
            )
            cards.append(generated)

        logger.success("Generated {} card(s) from article", len(cards))
        return cards

    def _summarize_article(self, article_markdown: str) -> str:
        if not article_markdown:
            return ""
        truncated_source = _truncate_text(
            article_markdown,
            self.config.summary_source_max_chars,
            suffix="\n...[input truncated]...",
        )
        messages = self._summary_prompt.format_messages(
            article_markdown=truncated_source,
            bullet_count=self.config.summary_bullet_count,
        )
        logger.debug(
            "Summarizing article before card generation", chars=len(truncated_source)
        )
        response = self._summary_llm.invoke(messages)
        content = response.content if hasattr(response, "content") else str(response)
        cleaned = content.strip()
        if cleaned:
            logger.debug("Article summary prepared: {}", cleaned[:200])
        else:
            logger.warning("Summary step returned empty content; falling back to raw excerpt")
        return cleaned

    def _invoke_with_retries(self, payload: dict[str, object]) -> _GenerationResponse:
        attempts = self.config.max_retries + 1
        last_error: ValidationError | None = None
        raw_output: str = ""
        for attempt in range(1, attempts + 1):
            formatted_prompt = self._prompt.format_messages(**payload)
            response = self._llm.invoke(formatted_prompt)
            raw_output = response.content if hasattr(response, "content") else str(response)
            try:
                parsed = self._parser.parse(raw_output)
                if attempt > 1:
                    logger.info("Agent response parsed successfully after {} attempts", attempt)
                return parsed
            except ValidationError as error:
                last_error = error
                logger.warning(
                    "Card generation agent response failed validation", attempt=attempt, error=str(error)
                )
                if attempt >= attempts:
                    logger.error("Exceeded maximum retries for card generation agent")
                    raise
                payload["feedback"] = _format_retry_feedback_text(
                    error,
                    raw_output,
                    max_chars=self.config.retry_feedback_max_chars,
                )
        assert last_error is not None
        raise last_error


def _clean_strings(values: Iterable[str]) -> Iterable[str]:
    for value in values:
        normalized = value.strip()
        if normalized:
            yield normalized


def _truncate_text(text: str, limit: int, *, suffix: str = "\n...[truncated]...") -> str:
    if limit <= 0:
        return text
    if len(text) <= limit:
        return text
    return text[:limit] + suffix


def _format_retry_feedback_text(error: object, previous_output: str, *, max_chars: int) -> str:
    error_text = str(error).strip() or "Unknown validation error"
    trimmed_output = previous_output.strip()
    if max_chars > 0 and len(trimmed_output) > max_chars:
        trimmed_output = trimmed_output[:max_chars] + "..."
    feedback = dedent(
        f"""
        The previous response could not be parsed.
        Validation error: {error_text}
        Previous response (truncated):
        {trimmed_output}

        Return ONLY valid JSON that satisfies the schema and fix every issue.
        """
    ).strip()
    return feedback
