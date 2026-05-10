"""Amazon Braket backend (real devices and managed simulators). Phase 3."""

from __future__ import annotations

from typing import Any

from qrouter.backends.base import BackendCapabilities
from qrouter.core.circuit import Circuit
from qrouter.core.exceptions import BackendError
from qrouter.core.result import Result


class BraketBackend:
    name = "braket"

    def __init__(self, device_arn: str, *, is_simulator: bool = False) -> None:
        self.device_arn = device_arn
        self.capabilities = BackendCapabilities(
            max_qubits=34,  # default for SV1; refined per device in Phase 3
            is_simulator=is_simulator,
            supports_statevector=is_simulator,
            supports_expectation=True,
        )

    def submit(  # pragma: no cover — Phase 3
        self, circuit: Circuit, *, shots: int, **kwargs: Any
    ) -> Result:
        raise BackendError("BraketBackend.submit is not yet implemented (Phase 3).")


__all__ = ["BraketBackend"]
