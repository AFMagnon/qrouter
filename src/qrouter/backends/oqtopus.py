"""OQTOPUS Cloud backend (via quri-parts-oqtopus). Phase 3."""

from __future__ import annotations

from typing import Any

from qrouter.backends.base import BackendCapabilities
from qrouter.core.circuit import Circuit
from qrouter.core.exceptions import BackendError
from qrouter.core.result import Result


class OqtopusBackend:
    name = "oqtopus"

    def __init__(self, device: str) -> None:
        self.device = device
        self.capabilities = BackendCapabilities(
            max_qubits=64,  # placeholder; queried at runtime in Phase 3
            is_simulator=False,
            supports_mid_circuit_measurement=False,
            notes="Capabilities are queried from OQTOPUS Cloud at submission time.",
        )

    def submit(  # pragma: no cover — Phase 3
        self, circuit: Circuit, *, shots: int, **kwargs: Any
    ) -> Result:
        raise BackendError("OqtopusBackend.submit is not yet implemented (Phase 3).")


__all__ = ["OqtopusBackend"]
