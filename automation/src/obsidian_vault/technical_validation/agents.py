"""Agent utilities for the technical validation workflow."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Sequence

from langchain.agents import create_tool_calling_agent
from langchain.agents.agent import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from loguru import logger

try:
    from langchain_community.tools.tavily_search import TavilySearchResults
except ImportError as error:  # pragma: no cover - dependency guard
    TavilySearchResults = None  # type: ignore[assignment]
    logger.warning("langchain-community not available: {}", error)

from obsidian_vault.llm_review.agents.config import AgentModelSettings, OpenRouterConfig


@dataclass(slots=True)
class TechnicalAgentConfig:
    """Configuration for the LangChain-based validation agent."""

    agent_settings: AgentModelSettings | None = None
    enable_web_search: bool = True


def _resolve_langchain_llm(config: TechnicalAgentConfig) -> ChatOpenAI:
    """Return a LangChain chat model configured for OpenRouter."""

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY environment variable is required for technical validation agents.",
        )

    base_config = OpenRouterConfig.from_environment(
        override_model=(config.agent_settings.model if config.agent_settings else None)
    )

    settings = dict(base_config.settings_kwargs)
    if config.agent_settings:
        overrides = config.agent_settings
        if overrides.temperature is not None:
            settings["temperature"] = overrides.temperature
        if overrides.top_p is not None:
            settings["top_p"] = overrides.top_p
        if overrides.max_tokens is not None:
            settings["max_tokens"] = overrides.max_tokens
        if overrides.presence_penalty is not None:
            settings["presence_penalty"] = overrides.presence_penalty
        if overrides.frequency_penalty is not None:
            settings["frequency_penalty"] = overrides.frequency_penalty
        if overrides.timeout is not None:
            settings["timeout"] = overrides.timeout

    headers: dict[str, str] = dict(base_config.headers)
    extra_headers = settings.pop("extra_headers", None)
    if isinstance(extra_headers, dict):
        headers.update(extra_headers)

    temperature = settings.pop("temperature", 0.0)
    timeout = settings.pop("timeout", None)
    max_tokens = settings.pop("max_tokens", None)

    model_kwargs: dict[str, Any] = {}
    for key in ("top_p", "presence_penalty", "frequency_penalty", "seed", "parallel_tool_calls"):
        if key in settings:
            model_kwargs[key] = settings.pop(key)
    model_kwargs.update(settings)

    logger.debug(
        "Initializing LangChain ChatOpenAI model: {} (model_kwargs={})",
        base_config.model,
        model_kwargs,
    )

    return ChatOpenAI(
        model=base_config.model,
        temperature=temperature,
        timeout=timeout,
        max_tokens=max_tokens,
        model_kwargs=model_kwargs or None,
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=api_key,
        default_headers=headers or None,
    )


def _build_tools(config: TechnicalAgentConfig) -> list[BaseTool]:
    """Construct the tool set for the validation agent."""

    tools: list[BaseTool] = []
    if not config.enable_web_search:
        return tools

    if TavilySearchResults is None:
        logger.warning("Tavily search disabled: langchain-community package not available")
        return tools

    tavily_key = os.getenv("TAVILY_API_KEY")
    if not tavily_key:
        logger.warning("TAVILY_API_KEY not set. Web documentation search will be unavailable.")
        return tools

    tools.append(TavilySearchResults(max_results=5))
    logger.debug("Enabled TavilySearchResults tool for documentation lookup")
    return tools


def build_technical_validation_agent(
    *,
    config: TechnicalAgentConfig | None = None,
    tools: Sequence[BaseTool] | None = None,
) -> AgentExecutor:
    """Create an AgentExecutor that can reason about validator issues."""

    resolved_config = config or TechnicalAgentConfig()
    llm = _resolve_langchain_llm(resolved_config)
    toolset = list(tools) if tools is not None else _build_tools(resolved_config)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a senior reviewer ensuring bilingual interview notes are technically sound. "
                "Assess validator findings, consult current documentation using the available tools, "
                "and respond with JSON containing keys 'issues' and 'summary'. Each issue entry must "
                "include 'validator', 'severity', 'problem', 'fix', and optional 'references'.",
            ),
            MessagesPlaceholder("chat_history"),
            (
                "human",
                "Analyze note {note_path} with taxonomy topic {topic}.\n"
                "Frontmatter:\n{frontmatter}\n\n"
                "Validator issues (JSON):\n{issues_json}\n\n"
                "Content excerpt:\n{content_excerpt}\n",
            ),
        ]
    )

    agent = create_tool_calling_agent(llm, toolset, prompt)
    executor = AgentExecutor(agent=agent, tools=toolset, verbose=False)
    return executor


def extract_agent_payload(agent_result: dict[str, Any]) -> dict[str, Any]:
    """Parse the agent output ensuring valid JSON is returned."""

    raw_output = agent_result.get("output")
    if raw_output is None:
        logger.error("Agent result missing 'output' key: {}", agent_result)
        raise ValueError("Agent execution did not return output text")

    if isinstance(raw_output, dict):
        return raw_output

    try:
        return json.loads(raw_output)
    except json.JSONDecodeError as error:
        logger.warning("Agent output was not valid JSON: {}", error)
        return {"summary": raw_output, "issues": []}
