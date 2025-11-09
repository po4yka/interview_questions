"""Retry utilities for handling transient failures.

Provides async retry decorators for LLM API calls and other operations
that may fail temporarily due to network issues, rate limits, or service errors.
"""

from __future__ import annotations

import asyncio
import functools
from typing import Any, Callable, TypeVar, cast

from loguru import logger

from obsidian_vault.exceptions import LLMRateLimitError, LLMTimeoutError

T = TypeVar("T")


def async_retry(
    max_attempts: int = 3,
    initial_delay: float = 2.0,
    exponential_base: float = 2.0,
    max_delay: float = 30.0,
    retry_on: tuple[type[Exception], ...] = (Exception,),
    skip_on: tuple[type[Exception], ...] = (),
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Async retry decorator with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts (including the first try)
        initial_delay: Initial delay in seconds before first retry
        exponential_base: Base for exponential backoff calculation
        max_delay: Maximum delay between retries in seconds
        retry_on: Tuple of exception types to retry on
        skip_on: Tuple of exception types to never retry (even if in retry_on)

    Returns:
        Decorator function

    Example:
        @async_retry(
            max_attempts=3,
            initial_delay=2.0,
            retry_on=(LLMTimeoutError, LLMRateLimitError)
        )
        async def my_llm_call(...):
            ...
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Exception | None = None
            delay = initial_delay

            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except skip_on as e:
                    # Don't retry these exceptions
                    logger.debug(
                        "Not retrying {} (attempt {}/{}) due to non-retryable error: {}",
                        func.__name__,
                        attempt,
                        max_attempts,
                        type(e).__name__,
                    )
                    raise
                except retry_on as e:
                    last_exception = e

                    # Don't retry if this was the last attempt
                    if attempt >= max_attempts:
                        logger.error(
                            "Failed {} after {} attempts. Last error: {} - {}",
                            func.__name__,
                            max_attempts,
                            type(e).__name__,
                            str(e),
                        )
                        break

                    # Calculate delay for next retry
                    current_delay = min(
                        initial_delay * (exponential_base ** (attempt - 1)), max_delay
                    )

                    # Check if exception has retry_after hint (for rate limits)
                    retry_after = None
                    if isinstance(e, LLMRateLimitError) and e.retry_after:
                        retry_after = e.retry_after
                        current_delay = max(current_delay, retry_after)

                    logger.warning(
                        "Attempt {}/{} failed for {}: {} - {}. Retrying in {:.1f}s...",
                        attempt,
                        max_attempts,
                        func.__name__,
                        type(e).__name__,
                        str(e)[:100],
                        current_delay,
                    )

                    # Wait before retry
                    await asyncio.sleep(current_delay)

                    # Update delay for next iteration
                    delay = current_delay

            # All retries exhausted, raise the last exception
            if last_exception:
                raise last_exception

            # Should never reach here, but just in case
            raise RuntimeError(f"Retry logic failed unexpectedly in {func.__name__}")

        return wrapper

    return decorator


def sync_retry(
    max_attempts: int = 3,
    initial_delay: float = 2.0,
    exponential_base: float = 2.0,
    max_delay: float = 30.0,
    retry_on: tuple[type[Exception], ...] = (Exception,),
    skip_on: tuple[type[Exception], ...] = (),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Synchronous retry decorator with exponential backoff.

    Same as async_retry but for synchronous functions.

    Args:
        max_attempts: Maximum number of attempts (including the first try)
        initial_delay: Initial delay in seconds before first retry
        exponential_base: Base for exponential backoff calculation
        max_delay: Maximum delay between retries in seconds
        retry_on: Tuple of exception types to retry on
        skip_on: Tuple of exception types to never retry (even if in retry_on)

    Returns:
        Decorator function
    """
    import time

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Exception | None = None
            delay = initial_delay

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except skip_on as e:
                    # Don't retry these exceptions
                    logger.debug(
                        "Not retrying {} (attempt {}/{}) due to non-retryable error: {}",
                        func.__name__,
                        attempt,
                        max_attempts,
                        type(e).__name__,
                    )
                    raise
                except retry_on as e:
                    last_exception = e

                    # Don't retry if this was the last attempt
                    if attempt >= max_attempts:
                        logger.error(
                            "Failed {} after {} attempts. Last error: {} - {}",
                            func.__name__,
                            max_attempts,
                            type(e).__name__,
                            str(e),
                        )
                        break

                    # Calculate delay for next retry
                    current_delay = min(
                        initial_delay * (exponential_base ** (attempt - 1)), max_delay
                    )

                    logger.warning(
                        "Attempt {}/{} failed for {}: {} - {}. Retrying in {:.1f}s...",
                        attempt,
                        max_attempts,
                        func.__name__,
                        type(e).__name__,
                        str(e)[:100],
                        current_delay,
                    )

                    # Wait before retry
                    time.sleep(current_delay)

                    # Update delay for next iteration
                    delay = current_delay

            # All retries exhausted, raise the last exception
            if last_exception:
                raise last_exception

            # Should never reach here, but just in case
            raise RuntimeError(f"Retry logic failed unexpectedly in {func.__name__}")

        return cast(Callable[..., T], wrapper)

    return decorator
