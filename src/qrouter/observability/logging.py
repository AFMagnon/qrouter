"""Structured logging.

`structlog` is configured lazily so importing qrouter does not pollute
the user's logging setup. Call `configure_logging()` once at the start
of an application (or set ``QROUTER_LOG_LEVEL`` / ``QROUTER_LOG_JSON``).
"""

from __future__ import annotations

import logging
import os
import sys
from typing import Any, cast

import structlog

_CONFIGURED = False


def configure_logging(
    *,
    level: str | int | None = None,
    json: bool | None = None,
) -> None:
    """Initialise structlog. Safe to call multiple times."""
    global _CONFIGURED
    if level is None:
        level = os.environ.get("QROUTER_LOG_LEVEL", "INFO")
    if json is None:
        json = os.environ.get("QROUTER_LOG_JSON", "").lower() in {"1", "true", "yes"}

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,
        level=level,
    )

    renderer: Any = (
        structlog.processors.JSONRenderer()
        if json
        else structlog.dev.ConsoleRenderer(colors=sys.stderr.isatty())
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelNamesMapping().get(str(level).upper(), logging.INFO)
            if isinstance(level, str)
            else level
        ),
        cache_logger_on_first_use=True,
    )
    _CONFIGURED = True


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a structlog logger; auto-configures with defaults on first call."""
    if not _CONFIGURED:
        configure_logging()
    return cast(structlog.stdlib.BoundLogger, structlog.get_logger(name))


__all__ = ["configure_logging", "get_logger"]
