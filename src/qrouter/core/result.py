"""Unified result type.

Backends return wildly different result objects (Qiskit's `SamplerResult`,
Braket's `GateModelQuantumTaskResult`, raw counts, statevectors, …).
`Result` normalizes them into a single Pydantic model so downstream code
can treat every backend identically.

Bit-string convention: keys in `counts` are little-endian
(qubit 0 on the right, matching Qiskit). Adapters re-encode if the
provider uses a different convention.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Result(BaseModel):
    """Canonical execution result."""

    model_config = ConfigDict(
        frozen=True,
        arbitrary_types_allowed=True,
        extra="forbid",
    )

    counts: dict[str, int] = Field(
        default_factory=dict,
        description="Bitstring → occurrence count. Keys are little-endian.",
    )
    expectation_value: float | None = Field(
        default=None,
        description="Expectation value if the backend computed one.",
    )
    statevector: list[complex] | None = Field(
        default=None,
        description="Final statevector if the backend is a simulator that returned one.",
    )
    shots: int = Field(default=0, ge=0)
    backend: str = Field(default="", description="Resolved backend identifier.")
    job_id: str = Field(default="", description="Provider-side job id.")
    duration_ms: float = Field(
        default=0.0,
        ge=0.0,
        description="Wall-clock time including queue and execution.",
    )
    raw: dict[str, Any] = Field(
        default_factory=dict,
        description="Provider-native result, kept verbatim as an escape hatch.",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


__all__ = ["Result"]
