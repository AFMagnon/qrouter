"""Logging / metrics. Quiet by default, JSON-friendly when configured."""

from __future__ import annotations

from qrouter.observability.logging import configure_logging, get_logger

__all__ = ["configure_logging", "get_logger"]
