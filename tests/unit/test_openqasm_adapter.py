"""OpenQASM adapter — version handling and metadata extraction."""

from __future__ import annotations

import pytest

from qrouter.adapters.openqasm_adapter import OpenQasmAdapter
from qrouter.core.exceptions import ConversionError

QASM3_BELL = """\
OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
bit[2] c;
h q[0];
cx q[0], q[1];
c[0] = measure q[0];
c[1] = measure q[1];
"""

QASM2_BELL = """\
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0], q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
"""


@pytest.mark.unit
def test_qasm3_passthrough_to_ir() -> None:
    a = OpenQasmAdapter(version=3)
    circuit = a.to_ir(QASM3_BELL)
    assert circuit.qasm == QASM3_BELL
    assert circuit.metadata.n_qubits == 2
    assert circuit.metadata.n_clbits == 2
    assert circuit.metadata.has_measurement is True


@pytest.mark.unit
def test_qasm3_passthrough_from_ir() -> None:
    a = OpenQasmAdapter(version=3)
    circuit = a.to_ir(QASM3_BELL)
    assert a.from_ir(circuit) == QASM3_BELL


@pytest.mark.unit
def test_qasm2_upgrade_to_qasm3() -> None:
    a = OpenQasmAdapter(version=2)
    circuit = a.to_ir(QASM2_BELL)
    assert "OPENQASM 3" in circuit.qasm
    assert 'include "stdgates.inc"' in circuit.qasm
    assert "qubit[2] q;" in circuit.qasm
    assert "bit[2] c;" in circuit.qasm
    assert "c[0] = measure q[0];" in circuit.qasm
    assert circuit.metadata.n_qubits == 2
    assert circuit.metadata.n_clbits == 2


@pytest.mark.unit
def test_qasm3_downgrade_to_qasm2_round_trip() -> None:
    up = OpenQasmAdapter(version=2)
    down = OpenQasmAdapter(version=2)
    circuit = up.to_ir(QASM2_BELL)
    rendered = down.from_ir(circuit)
    assert "OPENQASM 2.0" in rendered
    assert 'include "qelib1.inc"' in rendered
    assert "qreg q[2];" in rendered
    assert "creg c[2];" in rendered
    assert "measure q[0] -> c[0];" in rendered


@pytest.mark.unit
def test_invalid_version_rejected() -> None:
    with pytest.raises(ConversionError):
        OpenQasmAdapter(version=4)


@pytest.mark.unit
def test_non_string_input_rejected() -> None:
    a = OpenQasmAdapter(version=3)
    with pytest.raises(ConversionError):
        a.to_ir(123)  # type: ignore[arg-type]


@pytest.mark.unit
def test_missing_header_rejected() -> None:
    a = OpenQasmAdapter(version=2)
    with pytest.raises(ConversionError):
        a.to_ir("h q[0];")
