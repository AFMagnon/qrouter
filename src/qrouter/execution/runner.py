"""Top-level `run()` entry point.

Wires the routing layer to the backend registry. Phase 3 will add:
- Async variant `arun` (httpx-based polling).
- Retry decoration via `tenacity`.
- Structured logging hooks.
"""

from __future__ import annotations

import time
from typing import Any

from qrouter.backends.registry import get_backend
from qrouter.core.circuit import Circuit
from qrouter.core.result import Result
from qrouter.observability.logging import get_logger
from qrouter.router.selector import select_backend

_log = get_logger(__name__)


def run(
    circuit: Circuit,
    *,
    backend: str | None = None,
    shots: int = 1024,
    hints: dict[str, Any] | None = None,
    **kwargs: Any,
) -> Result:
    """Submit `circuit` to a backend and return a unified `Result`.

    If `backend` is omitted, the active routing policy decides.
    """
    if backend is None:
        backend = select_backend(circuit, shots=shots, hints=hints)
    target = get_backend(backend)
    started = time.perf_counter()
    _log.info(
        "submitting_circuit",
        backend=backend,
        shots=shots,
        n_qubits=circuit.metadata.n_qubits,
    )
    result = target.submit(circuit, shots=shots, **kwargs)
    duration_ms = (time.perf_counter() - started) * 1000.0
    if not result.duration_ms:
        result = result.model_copy(update={"duration_ms": duration_ms})
    _log.info("job_completed", backend=backend, job_id=result.job_id, duration_ms=duration_ms)
    return result


__all__ = ["run"]
