"""Adapter protocol.

Every supported SDK implements this protocol in both directions:
SDK → canonical IR via `to_ir`, canonical IR → SDK via `from_ir`.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from qrouter.core.circuit import Circuit


@runtime_checkable
class CircuitAdapter(Protocol):
    """Bidirectional converter between an SDK and the canonical IR."""

    #: Stable identifier, e.g. "qiskit", "braket", "quri", "openqasm".
    name: str

    def to_ir(self, source: Any) -> Circuit:
        """Convert an SDK-native circuit to the canonical IR."""
        ...

    def from_ir(self, circuit: Circuit) -> Any:
        """Convert the canonical IR back to an SDK-native circuit."""
        ...


__all__ = ["CircuitAdapter"]
