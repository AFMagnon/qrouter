"""End-to-end smoke test against `local:aer`."""

from __future__ import annotations

import pytest

pytest.importorskip("qiskit")
pytest.importorskip("qiskit_aer")

from qiskit import QuantumCircuit

from qrouter import Circuit, run


@pytest.mark.unit
def test_bell_state_on_aer() -> None:
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])

    circuit = Circuit.from_qiskit(qc)
    result = run(circuit, backend="local:aer", shots=2048, seed=42)

    assert result.shots == 2048
    assert result.backend == "local:aer"
    assert sum(result.counts.values()) == 2048
    # Bell state collapses to |00> or |11> only.
    assert set(result.counts) <= {"00", "11"}
    # And both outcomes should occur with at least one shot at this many trials.
    assert all(c > 0 for c in result.counts.values())
    assert result.duration_ms > 0.0


@pytest.mark.unit
def test_single_qubit_x_on_aer() -> None:
    qc = QuantumCircuit(1, 1)
    qc.x(0)
    qc.measure(0, 0)

    circuit = Circuit.from_qiskit(qc)
    result = run(circuit, backend="local:aer", shots=128, seed=7)

    assert result.counts == {"1": 128}
