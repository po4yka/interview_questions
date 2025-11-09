"""OpenRouter model configuration and settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from loguru import logger
from pydantic_ai.models.openai import ModelSettings, OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider


DEFAULT_OPENROUTER_MODEL = "openrouter/polaris-alpha"
DEFAULT_TEMPERATURE = 0.2
DEFAULT_TIMEOUT = 60.0


@dataclass
class AgentModelSettings:
    """Per-agent model configuration overrides.

    Allows fine-tuning model behavior for different agent types.
    If a field is None, it will use the value from environment variables
    or the default configuration.
    """

    model: str | None = None
    temperature: float | None = None
    top_p: float | None = None
    max_tokens: int | None = None
    presence_penalty: float | None = None
    frequency_penalty: float | None = None
    timeout: float | None = None


def _get_float_from_env(var_name: str) -> float | None:
    """Return a float value from the environment if it can be parsed."""

    raw_value = os.getenv(var_name)
    if raw_value is None:
        return None

    try:
        return float(raw_value)
    except ValueError:
        logger.warning(
            "Invalid float value for %s: %s — ignoring", var_name, raw_value
        )
        return None


def _get_int_from_env(var_name: str) -> int | None:
    """Return an int value from the environment if it can be parsed."""

    raw_value = os.getenv(var_name)
    if raw_value is None:
        return None

    try:
        return int(raw_value)
    except ValueError:
        logger.warning(
            "Invalid integer value for %s: %s — ignoring", var_name, raw_value
        )
        return None


def _get_bool_from_env(var_name: str) -> bool | None:
    """Return a bool value from the environment if it can be parsed."""

    raw_value = os.getenv(var_name)
    if raw_value is None:
        return None

    normalized = raw_value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False

    logger.warning("Invalid boolean value for %s: %s — ignoring", var_name, raw_value)
    return None


@dataclass
class OpenRouterConfig:
    """Runtime configuration for OpenRouter requests."""

    model: str
    headers: dict[str, str]
    settings_kwargs: dict[str, Any]

    @classmethod
    def from_environment(cls, override_model: str | None = None) -> "OpenRouterConfig":
        """Construct configuration, applying environment overrides with validation."""

        resolved_model = override_model or os.getenv(
            "OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL
        )

        headers: dict[str, str] = {}
        http_referer = os.getenv("OPENROUTER_HTTP_REFERER")
        if http_referer:
            headers["HTTP-Referer"] = http_referer

        app_title = os.getenv("OPENROUTER_APP_TITLE")
        if app_title:
            headers["X-Title"] = app_title

        settings_kwargs: dict[str, Any] = {}

        temperature = _get_float_from_env("OPENROUTER_TEMPERATURE")
        if temperature is None:
            temperature = DEFAULT_TEMPERATURE
        settings_kwargs["temperature"] = temperature

        top_p = _get_float_from_env("OPENROUTER_TOP_P")
        if top_p is not None:
            settings_kwargs["top_p"] = top_p

        presence_penalty = _get_float_from_env("OPENROUTER_PRESENCE_PENALTY")
        if presence_penalty is not None:
            settings_kwargs["presence_penalty"] = presence_penalty

        frequency_penalty = _get_float_from_env("OPENROUTER_FREQUENCY_PENALTY")
        if frequency_penalty is not None:
            settings_kwargs["frequency_penalty"] = frequency_penalty

        max_tokens = _get_int_from_env("OPENROUTER_MAX_TOKENS")
        if max_tokens is not None:
            settings_kwargs["max_tokens"] = max_tokens

        seed = _get_int_from_env("OPENROUTER_SEED")
        if seed is not None:
            settings_kwargs["seed"] = seed

        timeout = _get_float_from_env("OPENROUTER_TIMEOUT")
        if timeout is None:
            timeout = DEFAULT_TIMEOUT
        settings_kwargs["timeout"] = timeout

        parallel_tool_calls = _get_bool_from_env("OPENROUTER_PARALLEL_TOOL_CALLS")
        if parallel_tool_calls is not None:
            settings_kwargs["parallel_tool_calls"] = parallel_tool_calls

        if headers:
            settings_kwargs["extra_headers"] = headers

        return cls(resolved_model, headers, settings_kwargs)


def get_openrouter_model(
    model_name: str | None = None,
    agent_settings: AgentModelSettings | None = None,
) -> OpenAIChatModel:
    """Get an OpenRouter model configured for use with PydanticAI.

    Args:
        model_name: Optional model identifier override. If omitted, uses the
            ``OPENROUTER_MODEL`` environment variable or the default model.
        agent_settings: Optional per-agent configuration overrides. If provided,
            these settings will override the base configuration from environment
            variables for this specific agent instance.

    Returns:
        Configured OpenAIChatModel instance

    Raises:
        ValueError: If OPENROUTER_API_KEY is not set
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("OPENROUTER_API_KEY environment variable not set")
        raise ValueError(
            "OPENROUTER_API_KEY environment variable is required. "
            "Get your API key from https://openrouter.ai/keys"
        )

    # Start with base configuration from environment
    config = OpenRouterConfig.from_environment(model_name)

    # Apply per-agent overrides if provided
    if agent_settings:
        if agent_settings.model is not None:
            config.model = agent_settings.model
        if agent_settings.temperature is not None:
            config.settings_kwargs["temperature"] = agent_settings.temperature
        if agent_settings.top_p is not None:
            config.settings_kwargs["top_p"] = agent_settings.top_p
        if agent_settings.max_tokens is not None:
            config.settings_kwargs["max_tokens"] = agent_settings.max_tokens
        if agent_settings.presence_penalty is not None:
            config.settings_kwargs["presence_penalty"] = agent_settings.presence_penalty
        if agent_settings.frequency_penalty is not None:
            config.settings_kwargs["frequency_penalty"] = agent_settings.frequency_penalty
        if agent_settings.timeout is not None:
            config.settings_kwargs["timeout"] = agent_settings.timeout

    logger.debug(
        "Initializing OpenRouter model: %s (settings: %s)",
        config.model,
        {k: v for k, v in config.settings_kwargs.items() if k != "extra_headers"},
    )

    settings = ModelSettings(**config.settings_kwargs)

    return OpenAIChatModel(
        config.model,
        provider=OpenAIProvider(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        ),
        settings=settings,
    )
