"""Qiskit adapter.

Implements `CircuitAdapter` for `qiskit.QuantumCircuit`.

We rely on Qiskit's own QASM 3 round-trip (`qiskit.qasm3.dumps`/
`qiskit.qasm3.loads`) as the primary path. Version-specific quirks
(e.g. `Loader` rename in 2.x) are absorbed by `version_compat`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qrouter.core.circuit import Circuit
from qrouter.core.exceptions import ConversionError
from qrouter.core.ir import extract_metadata, validate_qasm3

if TYPE_CHECKING:
    from qiskit import QuantumCircuit


class QiskitAdapter:
    name = "qiskit"

    def to_ir(self, source: Any) -> Circuit:
        try:
            from qiskit import QuantumCircuit
            from qiskit import qasm3 as q_qasm3
        except ImportError as exc:  # pragma: no cover — guarded by extras
            raise ConversionError(
                "Qiskit is not installed. Install with `pip install qrouter[qiskit]`."
            ) from exc

        if not isinstance(source, QuantumCircuit):
            raise ConversionError(
                f"QiskitAdapter expects a qiskit.QuantumCircuit; got {type(source).__name__}."
            )

        try:
            qasm = q_qasm3.dumps(source)
        except Exception as exc:
            raise ConversionError(f"qiskit.qasm3.dumps failed: {exc}") from exc

        validate_qasm3(qasm)
        metadata = extract_metadata(qasm)
        return Circuit(qasm=qasm, metadata=metadata)

    def from_ir(self, circuit: Circuit) -> QuantumCircuit:
        try:
            from qiskit import qasm3 as q_qasm3
        except ImportError as exc:  # pragma: no cover
            raise ConversionError(
                "Qiskit is not installed. Install with `pip install qrouter[qiskit]`."
            ) from exc

        try:
            return q_qasm3.loads(circuit.qasm)
        except Exception as exc:
            raise ConversionError(f"qiskit.qasm3.loads failed: {exc}") from exc


__all__ = ["QiskitAdapter"]
