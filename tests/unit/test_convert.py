"""Ergonomic top-level converters: detect_source / convert / to_*."""

from __future__ import annotations

import pytest

pytest.importorskip("qiskit")
pytest.importorskip("braket.circuits")
pytest.importorskip("quri_parts.circuit")
pytest.importorskip("quri_parts.qiskit")

from braket.circuits import Circuit as BraketCircuit
from qiskit import QuantumCircuit
from quri_parts.circuit import QuantumCircuit as QPCircuit

import qrouter
from qrouter import (
    Circuit,
    QRouterError,
    convert,
    detect_source,
    to_braket,
    to_ir,
    to_qasm,
    to_qiskit,
    to_quri,
)


def _bell_qiskit() -> QuantumCircuit:
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    return qc


@pytest.mark.unit
def test_detect_source_each_sdk() -> None:
    assert detect_source(_bell_qiskit()) == "qiskit"
    assert detect_source(BraketCircuit().h(0).cnot(0, 1)) == "braket"
    qp = QPCircuit(2)
    qp.add_H_gate(0)
    assert detect_source(qp) == "quri"
    assert detect_source("OPENQASM 3.0; qubit[1] q; h q[0];") == "openqasm"
    assert detect_source(Circuit(qasm="OPENQASM 3.0; qubit[1] q;")) == "ir"


@pytest.mark.unit
def test_detect_source_rejects_unknown_type() -> None:
    with pytest.raises(QRouterError):
        detect_source(42)


@pytest.mark.unit
def test_to_quri_from_qiskit_one_liner() -> None:
    qc_quri = to_quri(_bell_qiskit())
    assert qc_quri.qubit_count == 2
    assert [g.name for g in qc_quri.gates] == ["H", "CNOT"]


@pytest.mark.unit
def test_to_braket_from_qiskit_one_liner() -> None:
    bc = to_braket(_bell_qiskit())
    assert isinstance(bc, BraketCircuit)
    assert bc.qubit_count == 2


@pytest.mark.unit
def test_to_qiskit_from_braket() -> None:
    bc = BraketCircuit().h(0).cnot(0, 1)
    qc = to_qiskit(bc)
    assert isinstance(qc, QuantumCircuit)
    assert qc.num_qubits == 2


@pytest.mark.unit
def test_to_qasm_emits_canonical_qasm3() -> None:
    qasm = to_qasm(_bell_qiskit())
    assert isinstance(qasm, str)
    assert "OPENQASM 3" in qasm
    assert "cx q[0], q[1]" in qasm


@pytest.mark.unit
def test_to_ir_returns_canonical_circuit() -> None:
    ir = to_ir(_bell_qiskit())
    assert isinstance(ir, Circuit)
    assert ir.metadata.n_qubits == 2


@pytest.mark.unit
def test_convert_with_explicit_target() -> None:
    qc_quri = convert(_bell_qiskit(), target="quri")
    assert qc_quri.qubit_count == 2


@pytest.mark.unit
def test_same_sdk_is_noop_and_keeps_identity() -> None:
    qc = _bell_qiskit()
    assert to_qiskit(qc) is qc


@pytest.mark.unit
def test_top_level_namespace_exposes_helpers() -> None:
    for name in (
        "convert",
        "detect_source",
        "to_qiskit",
        "to_quri",
        "to_braket",
        "to_qasm",
        "to_ir",
    ):
        assert hasattr(qrouter, name), f"qrouter.{name} should be exposed"
