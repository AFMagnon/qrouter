"""Qiskit adapter — round-trip and metadata."""

from __future__ import annotations

import pytest

pytest.importorskip("qiskit")

from qiskit import QuantumCircuit

from qrouter.adapters.qiskit_adapter import QiskitAdapter
from qrouter.core.circuit import Circuit
from qrouter.core.exceptions import ConversionError


@pytest.mark.unit
def test_bell_to_ir_extracts_metadata() -> None:
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])

    circuit = QiskitAdapter().to_ir(qc)
    assert isinstance(circuit, Circuit)
    assert "OPENQASM 3" in circuit.qasm
    assert circuit.metadata.n_qubits == 2
    assert circuit.metadata.has_measurement is True


@pytest.mark.unit
def test_round_trip_preserves_gate_set() -> None:
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.cx(0, 1)
    qc.ecr(1, 2)
    qc.rzz(0.5, 0, 2)

    adapter = QiskitAdapter()
    circuit = adapter.to_ir(qc)
    qc2 = adapter.from_ir(circuit)

    names1 = sorted(instr.operation.name for instr in qc.data)
    names2 = sorted(instr.operation.name for instr in qc2.data)
    assert names1 == names2


@pytest.mark.unit
def test_ecr_gate_preserved_in_qasm() -> None:
    qc = QuantumCircuit(2)
    qc.ecr(0, 1)

    circuit = QiskitAdapter().to_ir(qc)
    assert "ecr" in circuit.qasm.lower()


@pytest.mark.unit
def test_non_quantumcircuit_input_rejected() -> None:
    with pytest.raises(ConversionError):
        QiskitAdapter().to_ir("not a circuit")
