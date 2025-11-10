"""Firecrawl API client used to fetch article text."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

from firecrawl import FirecrawlApp
from loguru import logger


class FirecrawlError(RuntimeError):
    """Raised when Firecrawl cannot return article contents."""


@dataclass(slots=True)
class FirecrawlClient:
    """Lightweight wrapper around the official Firecrawl Python SDK."""

    api_key: str | None = None
    timeout: float = 30.0
    _app: FirecrawlApp | None = field(init=False, default=None, repr=False)

    def _resolve_api_key(self) -> str:
        key = self.api_key or os.getenv("FIRECRAWL_API_KEY")
        if not key:
            raise FirecrawlError(
                "FIRECRAWL_API_KEY environment variable is required to fetch articles via Firecrawl."
            )
        return key

    def _get_app(self) -> FirecrawlApp:
        if self._app is None:
            api_key = self._resolve_api_key()
            logger.debug("Initialising Firecrawl SDK client")
            self._app = FirecrawlApp(api_key=api_key)
        return self._app

    def fetch_markdown(self, url: str) -> str:
        """Retrieve the article text as Markdown."""

        logger.info("Requesting article via Firecrawl", url=url)
        try:
            client = self._get_app()
            response: dict[str, Any] = client.scrape_url(
                url=url,
                params={"formats": ["markdown"]},
            )
        except Exception as error:  # pragma: no cover - network failures are rare
            logger.error("Firecrawl SDK request failed: {}", error)
            raise FirecrawlError(f"Firecrawl request failed: {error}") from error

        markdown = self._extract_markdown(response)
        if not markdown:
            logger.error("Firecrawl response missing markdown content: {}", response)
            raise FirecrawlError("Firecrawl response did not include markdown content")

        logger.success("Article fetched successfully via Firecrawl", url=url)
        return markdown

    @staticmethod
    def _extract_markdown(payload: dict[str, Any]) -> str | None:
        markdown = payload.get("markdown")
        if markdown:
            return markdown

        data = payload.get("data")
        if isinstance(data, dict):
            markdown = data.get("markdown")
            if markdown:
                return markdown
            content = data.get("content")
            if isinstance(content, dict):
                markdown = content.get("markdown")
                if markdown:
                    return markdown

        content = payload.get("content")
        if isinstance(content, dict):
            markdown = content.get("markdown")
            if markdown:
                return markdown

        return None
