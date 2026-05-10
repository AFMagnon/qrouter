"""QURI Parts adapter — round-trip and qulacs end-to-end."""

from __future__ import annotations

import pytest

pytest.importorskip("quri_parts.circuit")
pytest.importorskip("quri_parts.openqasm")
pytest.importorskip("quri_parts.qiskit")
pytest.importorskip("quri_parts.qulacs")

from quri_parts.circuit import QuantumCircuit as QPCircuit

from qrouter import Circuit, run
from qrouter.adapters.quri_adapter import QuriAdapter


@pytest.mark.unit
def test_qp_to_ir_emits_qasm3() -> None:
    qc = QPCircuit(2)
    qc.add_H_gate(0)
    qc.add_CNOT_gate(0, 1)

    circuit = QuriAdapter().to_ir(qc)
    assert "OPENQASM 3" in circuit.qasm
    assert "h q[0]" in circuit.qasm
    assert "cx q[0], q[1]" in circuit.qasm
    assert circuit.metadata.n_qubits == 2


@pytest.mark.unit
def test_qp_round_trip_via_qiskit_bridge() -> None:
    qc = QPCircuit(3)
    qc.add_H_gate(0)
    qc.add_CNOT_gate(0, 1)
    qc.add_CNOT_gate(1, 2)

    adapter = QuriAdapter()
    circuit = adapter.to_ir(qc)
    qp_back = adapter.from_ir(circuit)

    assert qp_back.qubit_count == 3
    gate_names = [g.name for g in qp_back.gates]
    assert gate_names.count("H") == 1
    assert gate_names.count("CNOT") == 2


@pytest.mark.unit
def test_qulacs_executes_bell_state() -> None:
    qc = QPCircuit(2)
    qc.add_H_gate(0)
    qc.add_CNOT_gate(0, 1)

    circuit = Circuit.from_quri(qc)
    result = run(circuit, backend="local:qulacs", shots=2048)

    assert result.shots == 2048
    assert result.backend == "local:qulacs"
    assert sum(result.counts.values()) == 2048
    # Bell collapses only to |00> or |11>.
    assert set(result.counts) <= {"00", "11"}
    assert all(c > 0 for c in result.counts.values())
