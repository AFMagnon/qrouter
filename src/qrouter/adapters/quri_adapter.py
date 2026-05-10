"""QURI Parts adapter.

Implements `CircuitAdapter` for `quri_parts.circuit.QuantumCircuit` /
`ImmutableQuantumCircuit`.

Direction reference:
- ``to_ir``   uses ``quri_parts.openqasm.circuit.convert_to_qasm_str``,
  the official QASM3 emitter shipped by QURI Parts.
- ``from_ir`` round-trips through Qiskit because QURI Parts does not
  ship a native QASM3 *parser*: we ``qiskit.qasm3.loads`` the IR, strip
  the final measurements (QURI Parts has no first-class measurement
  gate — sampling does it), and hand the Qiskit circuit to
  ``quri_parts.qiskit.circuit.circuit_from_qiskit``.

This is why ``qrouter[quri]`` pulls in ``quri-parts-qiskit``.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from qrouter.core.circuit import Circuit
from qrouter.core.exceptions import ConversionError
from qrouter.core.ir import extract_metadata, validate_qasm3

if TYPE_CHECKING:
    from quri_parts.rust.circuit.circuit import ImmutableQuantumCircuit

_QASM_HEADER = re.compile(r"^\s*OPENQASM\s+3\s*;", re.MULTILINE)


def _normalize_qasm_header(qasm: str) -> str:
    """QURI Parts emits ``OPENQASM 3;``; some parsers require ``3.0``.

    Normalising here keeps every downstream consumer happy and avoids
    spreading the workaround through the codebase.
    """
    return _QASM_HEADER.sub("OPENQASM 3.0;", qasm, count=1)


class QuriAdapter:
    name = "quri"

    def to_ir(self, source: Any) -> Circuit:
        try:
            from quri_parts.openqasm.circuit import convert_to_qasm_str
        except ImportError as exc:  # pragma: no cover — guarded by extras
            raise ConversionError(
                "QURI Parts is not installed. Install with `pip install qrouter[quri]`."
            ) from exc

        try:
            qasm = convert_to_qasm_str(source)
        except Exception as exc:
            raise ConversionError(f"quri_parts.openqasm.convert_to_qasm_str failed: {exc}") from exc

        qasm = _normalize_qasm_header(qasm)
        validate_qasm3(qasm)
        return Circuit(qasm=qasm, metadata=extract_metadata(qasm))

    def from_ir(self, circuit: Circuit) -> ImmutableQuantumCircuit:
        try:
            from qiskit import qasm3 as q_qasm3
            from quri_parts.qiskit.circuit import circuit_from_qiskit
        except ImportError as exc:  # pragma: no cover — guarded by extras
            raise ConversionError(
                "QURI Parts (with Qiskit bridge) is not installed. "
                "Install with `pip install qrouter[quri,qiskit]`."
            ) from exc

        try:
            qiskit_qc = q_qasm3.loads(circuit.qasm)
        except Exception as exc:
            raise ConversionError(f"qiskit.qasm3.loads failed: {exc}") from exc

        # QURI Parts circuits do not carry an explicit measurement gate;
        # sampling handles it. Strip terminal measurements before
        # crossing over so the converter does not reject the circuit.
        try:
            stripped = qiskit_qc.remove_final_measurements(inplace=False)
        except Exception as exc:
            raise ConversionError(
                f"Failed to strip measurements before QURI Parts conversion: {exc}"
            ) from exc

        try:
            return circuit_from_qiskit(stripped)
        except Exception as exc:
            raise ConversionError(
                f"quri_parts.qiskit.circuit.circuit_from_qiskit failed: {exc}"
            ) from exc


__all__ = ["QuriAdapter"]
