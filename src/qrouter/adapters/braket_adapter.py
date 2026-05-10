"""Amazon Braket adapter.

Implements `CircuitAdapter` for `braket.circuits.Circuit`.

Braket already speaks OpenQASM 3, so the conversion is mostly
gate-name normalisation between the canonical IR (which sticks to
``stdgates.inc`` names like ``cx``) and Braket's parser (which uses
``cnot`` and refuses ``include "stdgates.inc"``):

- to_ir: drop Braket's terminal measurements out of the *parsed* AST
  (we keep them in the IR string, since the canonical form measures
  explicitly), inject the stdgates include, rewrite ``cnot`` → ``cx``.
- from_ir: strip the include and rewrite ``cx`` → ``cnot``.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from qrouter.core.circuit import Circuit
from qrouter.core.exceptions import ConversionError
from qrouter.core.ir import extract_metadata, validate_qasm3

if TYPE_CHECKING:
    from braket.circuits import Circuit as BraketCircuit

#: Braket-specific gate names → canonical (stdgates.inc) names.
#: Sources: AWS Braket OpenQASM 3 supported gates documentation.
_BRAKET_TO_STD: dict[str, str] = {
    "cnot": "cx",
    "si": "sdg",
    "ti": "tdg",
    "v": "sx",
    "vi": "sxdg",
    "phaseshift": "p",
    "cphaseshift": "cp",
    "ccnot": "ccx",
}

#: Reverse direction: canonical → Braket.
_STD_TO_BRAKET: dict[str, str] = {v: k for k, v in _BRAKET_TO_STD.items()}

_INCLUDE_STDGATES = re.compile(r'^\s*include\s+"stdgates\.inc"\s*;\s*\n?', re.MULTILINE)
_HEADER_LINE = re.compile(r"^(OPENQASM\s+3(?:\.\d+)?\s*;)\s*$", re.MULTILINE)


def _replace_gate_names(qasm: str, mapping: dict[str, str]) -> str:
    """Rewrite gate-call lines.

    Restricted to lines that *look* like a gate call (``name args ;``)
    to avoid accidentally rewriting comments or string literals.
    """
    out_lines: list[str] = []
    for raw in qasm.splitlines(keepends=True):
        stripped = raw.lstrip()
        if not stripped or stripped.startswith(
            (
                "//",
                "/*",
                "include",
                "OPENQASM",
                "qubit",
                "bit",
                "qreg",
                "creg",
                "gate",
                "input",
                "output",
            )
        ):
            out_lines.append(raw)
            continue
        head, _, rest = stripped.partition(" ")
        head_no_paren = head.split("(", 1)[0]
        if head_no_paren in mapping:
            indent = raw[: len(raw) - len(stripped)]
            replaced = head.replace(head_no_paren, mapping[head_no_paren], 1)
            out_lines.append(f"{indent}{replaced} {rest}" if rest else f"{indent}{replaced}")
        else:
            out_lines.append(raw)
    return "".join(out_lines)


class BraketAdapter:
    name = "braket"

    def to_ir(self, source: Any) -> Circuit:
        try:
            from braket.circuits import Circuit as BraketCircuit
        except ImportError as exc:  # pragma: no cover — guarded by extras
            raise ConversionError(
                "amazon-braket-sdk is not installed. Install with `pip install qrouter[braket]`."
            ) from exc

        if not isinstance(source, BraketCircuit):
            raise ConversionError(
                f"BraketAdapter expects a braket.circuits.Circuit; got {type(source).__name__}."
            )

        try:
            program = source.to_ir(ir_type="OPENQASM")
            qasm = program.source
        except Exception as exc:
            raise ConversionError(f"braket Circuit.to_ir failed: {exc}") from exc

        if not _INCLUDE_STDGATES.search(qasm):
            qasm = _HEADER_LINE.sub(r'\1\ninclude "stdgates.inc";', qasm, count=1)
        qasm = _replace_gate_names(qasm, _BRAKET_TO_STD)

        validate_qasm3(qasm)
        return Circuit(qasm=qasm, metadata=extract_metadata(qasm))

    def from_ir(self, circuit: Circuit) -> BraketCircuit:
        try:
            from braket.circuits import Circuit as BraketCircuit
        except ImportError as exc:  # pragma: no cover
            raise ConversionError(
                "amazon-braket-sdk is not installed. Install with `pip install qrouter[braket]`."
            ) from exc

        qasm = _INCLUDE_STDGATES.sub("", circuit.qasm)
        qasm = _replace_gate_names(qasm, _STD_TO_BRAKET)

        try:
            return BraketCircuit.from_ir(qasm)
        except Exception as exc:
            raise ConversionError(
                f"braket Circuit.from_ir failed: {exc}\nSource after normalisation:\n{qasm}"
            ) from exc


__all__ = ["BraketAdapter"]
