"""Canonical intermediate representation (IR).

qrouter uses **OpenQASM 3** as the single canonical IR. Every adapter
converts in and out of this form. Centralising IR concerns here lets
adapters stay focused on a single direction of conversion each.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Final

from qrouter.core.exceptions import ConversionError

if TYPE_CHECKING:
    from qrouter.core.circuit import CircuitMetadata

#: Standard 1-qubit gate set understood by the canonical IR.
STD_1Q_GATES: Final[frozenset[str]] = frozenset(
    {
        "id",
        "x",
        "y",
        "z",
        "h",
        "s",
        "sdg",
        "t",
        "tdg",
        "sx",
        "sxdg",
        "rx",
        "ry",
        "rz",
        "p",
        "u",
        "u1",
        "u2",
        "u3",
    }
)

#: Standard 2-qubit gate set (includes IBM-native `ecr` and parametrized
#: forms that show up natively on Falcon/Eagle/Heron hardware).
STD_2Q_GATES: Final[frozenset[str]] = frozenset(
    {
        "cx",
        "cy",
        "cz",
        "swap",
        "iswap",
        "crx",
        "cry",
        "crz",
        "cp",
        "cu",
        "rxx",
        "ryy",
        "rzz",
        "rzx",
        "ecr",
    }
)

#: Standard 3-qubit gate set.
STD_3Q_GATES: Final[frozenset[str]] = frozenset({"ccx", "cswap"})

#: Union of all gates the canonical IR understands without decomposition.
SUPPORTED_GATES: Final[frozenset[str]] = STD_1Q_GATES | STD_2Q_GATES | STD_3Q_GATES


# ----------------------------------------------------------------------
# QASM 2 ↔ 3 translation
# ----------------------------------------------------------------------

_QASM2_HEADER = re.compile(r"^\s*OPENQASM\s+2(\.\d+)?\s*;", re.MULTILINE)
_QASM3_HEADER = re.compile(r"^\s*OPENQASM\s+3(\.\d+)?\s*;", re.MULTILINE)
_QELIB1_INC = re.compile(r'^\s*include\s+"qelib1\.inc"\s*;', re.MULTILINE)
_STDGATES_INC = re.compile(r'^\s*include\s+"stdgates\.inc"\s*;', re.MULTILINE)
_QREG = re.compile(r"\bqreg\s+(\w+)\s*\[\s*(\d+)\s*\]\s*;")
_CREG = re.compile(r"\bcreg\s+(\w+)\s*\[\s*(\d+)\s*\]\s*;")
_QUBIT_DECL = re.compile(r"\bqubit\s*\[\s*(\d+)\s*\]\s+(\w+)\s*;")
_BIT_DECL = re.compile(r"\bbit\s*\[\s*(\d+)\s*\]\s+(\w+)\s*;")
_MEASURE_2_TO_3 = re.compile(
    r"\bmeasure\s+(\w+(?:\[\s*\d+\s*\])?)\s*->\s*(\w+(?:\[\s*\d+\s*\])?)\s*;"
)
_MEASURE_3_TO_2 = re.compile(
    r"\b(\w+(?:\[\s*\d+\s*\])?)\s*=\s*measure\s+(\w+(?:\[\s*\d+\s*\])?)\s*;"
)


def upgrade_qasm2_to_qasm3(src: str) -> str:
    """Translate OpenQASM 2.0 to OpenQASM 3.

    Handles the common surface used in practice: header, stdlib include,
    register declarations, and measurement syntax. More exotic QASM 2
    constructs (`opaque`, `if`, custom gate definitions referencing
    qelib1) are passed through verbatim — they may not parse as QASM 3.
    """
    if not _QASM2_HEADER.search(src):
        if _QASM3_HEADER.search(src):
            return src
        raise ConversionError("Source is not OpenQASM 2.0 (no `OPENQASM 2.0;` header found).")
    out = _QASM2_HEADER.sub("OPENQASM 3.0;", src, count=1)
    out = _QELIB1_INC.sub('include "stdgates.inc";', out, count=1)
    out = _QREG.sub(r"qubit[\2] \1;", out)
    out = _CREG.sub(r"bit[\2] \1;", out)
    out = _MEASURE_2_TO_3.sub(r"\2 = measure \1;", out)
    return out


def downgrade_qasm3_to_qasm2(src: str) -> str:
    """Translate OpenQASM 3 to OpenQASM 2.0 on a best-effort basis.

    Loses anything QASM 2 cannot express (boxes, complex types,
    classical control beyond simple `if`, parameterised gates not in
    qelib1). Callers who need a lossless target should pick a richer
    backend.
    """
    if not _QASM3_HEADER.search(src):
        if _QASM2_HEADER.search(src):
            return src
        raise ConversionError("Source is not OpenQASM 3 (no `OPENQASM 3;` header found).")
    out = _QASM3_HEADER.sub("OPENQASM 2.0;", src, count=1)
    out = _STDGATES_INC.sub('include "qelib1.inc";', out, count=1)
    out = _QUBIT_DECL.sub(r"qreg \2[\1];", out)
    out = _BIT_DECL.sub(r"creg \2[\1];", out)
    out = _MEASURE_3_TO_2.sub(r"measure \2 -> \1;", out)
    return out


# ----------------------------------------------------------------------
# Metadata extraction
# ----------------------------------------------------------------------


def extract_metadata(qasm: str) -> CircuitMetadata:
    """Walk the OpenQASM 3 AST and report basic shape information.

    Falls back to lightweight regex counting if the official `openqasm3`
    parser is unavailable or rejects the source — useful for partial
    fragments emitted by some adapters during round-tripping.
    """

    try:
        return _extract_metadata_via_ast(qasm)
    except Exception:
        return _extract_metadata_via_regex(qasm)


def _extract_metadata_via_ast(qasm: str) -> CircuitMetadata:
    import openqasm3
    from openqasm3 import ast

    from qrouter.core.circuit import CircuitMetadata

    program = openqasm3.parse(qasm)

    n_qubits = 0
    n_clbits = 0
    gate_count = 0
    has_measurement = False
    has_classical_control = False
    parameters: set[str] = set()

    def _size_of(expr: ast.Expression | None) -> int:
        if expr is None:
            return 1
        if isinstance(expr, ast.IntegerLiteral):
            return int(expr.value)
        return 1

    for stmt in program.statements:
        if isinstance(stmt, ast.QubitDeclaration):
            n_qubits += _size_of(stmt.size)
        elif isinstance(stmt, ast.ClassicalDeclaration) and isinstance(stmt.type, ast.BitType):
            n_clbits += _size_of(stmt.type.size)
        elif isinstance(stmt, ast.QuantumGate):
            gate_count += 1
        elif isinstance(stmt, ast.QuantumMeasurement | ast.QuantumMeasurementStatement):
            has_measurement = True
        elif isinstance(stmt, ast.BranchingStatement):
            has_classical_control = True
        elif isinstance(stmt, ast.IODeclaration) and stmt.io_identifier == ast.IOKeyword.input:
            parameters.add(stmt.identifier.name)

    return CircuitMetadata(
        n_qubits=n_qubits,
        n_clbits=n_clbits,
        gate_count=gate_count,
        has_measurement=has_measurement,
        has_classical_control=has_classical_control,
        parameters=tuple(sorted(parameters)),
    )


def _extract_metadata_via_regex(qasm: str) -> CircuitMetadata:
    """Cheap fallback when the AST parser refuses input."""
    from qrouter.core.circuit import CircuitMetadata

    n_qubits = sum(int(m.group(1)) for m in _QUBIT_DECL.finditer(qasm))
    n_qubits += sum(int(m.group(2)) for m in _QREG.finditer(qasm))
    n_clbits = sum(int(m.group(1)) for m in _BIT_DECL.finditer(qasm))
    n_clbits += sum(int(m.group(2)) for m in _CREG.finditer(qasm))
    has_measurement = bool(_MEASURE_2_TO_3.search(qasm) or _MEASURE_3_TO_2.search(qasm))
    # Crude gate count: any non-empty, non-declaration semicolon-terminated
    # line that isn't a directive.
    gate_count = 0
    _skip_prefixes = (
        "//",
        "OPENQASM",
        "include",
        "qubit",
        "bit",
        "qreg",
        "creg",
        "gate",
        "input",
        "output",
    )
    for raw in qasm.splitlines():
        line = raw.strip()
        if not line or line.startswith(_skip_prefixes):
            continue
        if "measure" in line:
            continue
        if line.endswith(";"):
            gate_count += 1
    return CircuitMetadata(
        n_qubits=n_qubits,
        n_clbits=n_clbits,
        gate_count=gate_count,
        has_measurement=has_measurement,
        has_classical_control=False,
        parameters=(),
    )


# ----------------------------------------------------------------------
# Validation
# ----------------------------------------------------------------------


def validate_qasm3(src: str) -> None:
    """Raise `ConversionError` if the source does not parse as QASM 3."""
    import openqasm3

    try:
        openqasm3.parse(src)
    except Exception as exc:
        raise ConversionError(f"Invalid OpenQASM 3 source: {exc}") from exc


__all__ = [
    "STD_1Q_GATES",
    "STD_2Q_GATES",
    "STD_3Q_GATES",
    "SUPPORTED_GATES",
    "downgrade_qasm3_to_qasm2",
    "extract_metadata",
    "upgrade_qasm2_to_qasm3",
    "validate_qasm3",
]
