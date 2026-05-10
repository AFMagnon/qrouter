"""Retry helpers (Phase 3 will wire these into backend submission)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from tenacity import (
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from qrouter.core.exceptions import BackendError


def with_backoff(
    func: Callable[..., Any],
    *,
    max_attempts: int = 5,
    multiplier: float = 1.0,
    max_wait: float = 30.0,
) -> Callable[..., Any]:
    """Wrap `func` so transient `BackendError`s are retried with exponential backoff."""

    def wrapped(*args: Any, **kwargs: Any) -> Any:
        for attempt in Retrying(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=multiplier, max=max_wait),
            retry=retry_if_exception_type(BackendError),
            reraise=True,
        ):
            with attempt:
                return func(*args, **kwargs)
        return None  # pragma: no cover — unreachable

    return wrapped


__all__ = ["with_backoff"]
