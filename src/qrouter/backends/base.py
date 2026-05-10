"""Backend protocol and capability descriptor.

Each backend exposes a small set of capabilities (max qubits, supported
gates, simulator vs. real hardware, …) so the routing layer can match
circuits to feasible backends without trial-and-error submission.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from qrouter.core.circuit import Circuit
from qrouter.core.result import Result


@dataclass(frozen=True, slots=True)
class BackendCapabilities:
    """Static description of what a backend can run."""

    max_qubits: int
    is_simulator: bool
    supports_mid_circuit_measurement: bool = False
    supports_classical_control: bool = False
    supports_statevector: bool = False
    supports_expectation: bool = False
    native_gates: frozenset[str] = field(default_factory=frozenset)
    notes: str = ""


@runtime_checkable
class Backend(Protocol):
    """A platform-specific execution target."""

    #: Stable identifier of the form ``"<provider>:<device>"``.
    #: Examples: ``"local:aer"``, ``"ibm:ibm_brisbane"``, ``"oqtopus:kawasaki"``.
    name: str

    #: Static capabilities used by the routing layer.
    capabilities: BackendCapabilities

    def submit(self, circuit: Circuit, *, shots: int, **kwargs: object) -> Result:
        """Submit a circuit, block until the result is ready, return it.

        Async submission and polling are added in Phase 3 via the
        ``execution`` package.
        """
        ...


__all__ = ["Backend", "BackendCapabilities"]
