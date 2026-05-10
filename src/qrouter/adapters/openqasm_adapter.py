"""OpenQASM 2/3 adapter.

The canonical IR is OpenQASM 3, so this adapter is mostly a no-op:
- `to_ir`   accepts QASM 3 verbatim, or upgrades QASM 2 first.
- `from_ir` returns QASM 3 verbatim, or downgrades to QASM 2 if the
  caller explicitly requested version 2.
"""

from __future__ import annotations

from qrouter.core.circuit import Circuit
from qrouter.core.exceptions import ConversionError
from qrouter.core.ir import (
    downgrade_qasm3_to_qasm2,
    extract_metadata,
    upgrade_qasm2_to_qasm3,
    validate_qasm3,
)


class OpenQasmAdapter:
    name = "openqasm"

    def __init__(self, version: int = 3) -> None:
        if version not in (2, 3):
            raise ConversionError(f"OpenQASM version must be 2 or 3, got {version!r}.")
        self.version = version

    def to_ir(self, source: str) -> Circuit:
        if not isinstance(source, str):
            raise ConversionError(f"OpenQasmAdapter expects a `str`; got {type(source).__name__}.")
        qasm3 = upgrade_qasm2_to_qasm3(source) if self.version == 2 else source
        validate_qasm3(qasm3)
        metadata = extract_metadata(qasm3)
        return Circuit(qasm=qasm3, metadata=metadata)

    def from_ir(self, circuit: Circuit) -> str:
        validate_qasm3(circuit.qasm)
        if self.version == 3:
            return circuit.qasm
        return downgrade_qasm3_to_qasm2(circuit.qasm)


__all__ = ["OpenQasmAdapter"]
