"""Braket adapter — round-trip and gate-name normalization."""

from __future__ import annotations

import pytest

pytest.importorskip("braket.circuits")

from braket.circuits import Circuit as BraketCircuit

from qrouter.adapters.braket_adapter import BraketAdapter
from qrouter.core.circuit import Circuit


@pytest.mark.unit
def test_bell_to_ir_uses_canonical_cx() -> None:
    bc = BraketCircuit().h(0).cnot(0, 1)
    circuit = BraketAdapter().to_ir(bc)
    assert "OPENQASM 3" in circuit.qasm
    assert 'include "stdgates.inc";' in circuit.qasm
    # Braket emits "cnot"; we normalize to "cx".
    assert "cx q[0]" in circuit.qasm
    assert "cnot q[0]" not in circuit.qasm
    assert circuit.metadata.n_qubits == 2


@pytest.mark.unit
def test_round_trip_via_braket() -> None:
    bc = BraketCircuit().h(0).cnot(0, 1)

    adapter = BraketAdapter()
    circuit = adapter.to_ir(bc)
    bc2 = adapter.from_ir(circuit)

    assert isinstance(bc2, BraketCircuit)
    assert bc.qubit_count == bc2.qubit_count


@pytest.mark.unit
def test_canonical_ir_is_consumable_by_braket() -> None:
    canonical = 'OPENQASM 3.0;\ninclude "stdgates.inc";\nqubit[2] q;\nh q[0];\ncx q[0], q[1];\n'
    circuit = Circuit(qasm=canonical)
    bc = BraketAdapter().from_ir(circuit)
    assert bc.qubit_count == 2


@pytest.mark.unit
def test_ecr_passes_through_unchanged() -> None:
    bc = BraketCircuit().h(0).ecr(0, 1)
    circuit = BraketAdapter().to_ir(bc)
    assert "ecr" in circuit.qasm.lower()
    bc2 = BraketAdapter().from_ir(circuit)
    assert bc2.qubit_count == 2
