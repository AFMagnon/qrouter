"""Execution layer: submit / poll / cancel jobs with retry & timeout."""

from __future__ import annotations

from qrouter.execution.runner import run

__all__ = ["run"]
