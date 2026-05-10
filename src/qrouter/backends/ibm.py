"""IBM Quantum backend (via qiskit-ibm-runtime). Phase 3."""

from __future__ import annotations

from typing import Any

from qrouter.backends.base import BackendCapabilities
from qrouter.core.circuit import Circuit
from qrouter.core.exceptions import BackendError
from qrouter.core.result import Result


class IBMQuantumBackend:
    name = "ibm"

    def __init__(self, device: str) -> None:
        self.device = device
        self.capabilities = BackendCapabilities(
            max_qubits=156,  # placeholder; queried lazily in Phase 3
            is_simulator=False,
            supports_mid_circuit_measurement=True,
            supports_classical_control=True,
            native_gates=frozenset({"cz", "ecr", "rz", "sx", "x", "id", "measure"}),
            notes=(
                "Native gate set varies per device. ECR is native on "
                "Falcon/Eagle; CZ is native on Heron and later."
            ),
        )

    def submit(  # pragma: no cover — Phase 3
        self, circuit: Circuit, *, shots: int, **kwargs: Any
    ) -> Result:
        raise BackendError("IBMQuantumBackend.submit is not yet implemented (Phase 3).")


__all__ = ["IBMQuantumBackend"]
