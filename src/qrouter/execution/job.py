"""Async-friendly job handle. Phase 3 implementation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from qrouter.core.result import Result


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class Job:
    """Handle to an in-flight backend job."""

    id: str
    backend: str
    status: JobStatus = JobStatus.QUEUED
    result: Result | None = None


__all__ = ["Job", "JobStatus"]
