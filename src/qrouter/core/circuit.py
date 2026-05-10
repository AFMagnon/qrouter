"""Unified circuit type.

`Circuit` wraps an OpenQASM 3 string (the canonical IR) and exposes
`from_*` / `to_*` round-trippers for each supported SDK. Conversion is
delegated to `qrouter.adapters` so adding a new SDK does not require
touching this module.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


@dataclass(slots=True)
class CircuitMetadata:
    """Lightweight metadata derived from the canonical IR."""

    n_qubits: int = 0
    n_clbits: int = 0
    gate_count: int = 0
    has_measurement: bool = False
    has_mid_circuit_measurement: bool = False
    has_classical_control: bool = False
    parameters: tuple[str, ...] = ()


@dataclass(slots=True)
class Circuit:
    """Unified quantum circuit.

    The canonical representation is OpenQASM 3 (`qasm` field). Adapters
    convert to/from this form. Two circuits are considered equivalent
    when their canonical IR strings (after normalization) match.
    """

    qasm: str
    metadata: CircuitMetadata = field(default_factory=CircuitMetadata)

    # ------------------------------------------------------------------
    # Constructors — implementations live in qrouter.adapters.*
    # ------------------------------------------------------------------

    @classmethod
    def from_qiskit(cls, qc: Any) -> Circuit:  # pragma: no cover — Phase 3
        from qrouter.adapters.qiskit_adapter import QiskitAdapter

        return QiskitAdapter().to_ir(qc)

    @classmethod
    def from_quri(cls, qc: Any) -> Circuit:  # pragma: no cover — Phase 3
        from qrouter.adapters.quri_adapter import QuriAdapter

        return QuriAdapter().to_ir(qc)

    @classmethod
    def from_braket(cls, qc: Any) -> Circuit:  # pragma: no cover — Phase 3
        from qrouter.adapters.braket_adapter import BraketAdapter

        return BraketAdapter().to_ir(qc)

    @classmethod
    def from_qasm(cls, src: str, version: int = 3) -> Circuit:  # pragma: no cover
        from qrouter.adapters.openqasm_adapter import OpenQasmAdapter

        return OpenQasmAdapter(version=version).to_ir(src)

    # ------------------------------------------------------------------
    # Targets
    # ------------------------------------------------------------------

    def to_qiskit(self) -> Any:  # pragma: no cover — Phase 3
        from qrouter.adapters.qiskit_adapter import QiskitAdapter

        return QiskitAdapter().from_ir(self)

    def to_quri(self) -> Any:  # pragma: no cover — Phase 3
        from qrouter.adapters.quri_adapter import QuriAdapter

        return QuriAdapter().from_ir(self)

    def to_braket(self) -> Any:  # pragma: no cover — Phase 3
        from qrouter.adapters.braket_adapter import BraketAdapter

        return BraketAdapter().from_ir(self)

    def to_qasm(self, version: int = 3) -> str:  # pragma: no cover
        from qrouter.adapters.openqasm_adapter import OpenQasmAdapter

        return OpenQasmAdapter(version=version).from_ir(self)


__all__ = ["Circuit", "CircuitMetadata"]
