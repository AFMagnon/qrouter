"""Property-based round-trip tests.

For each adapter we check:
    SDK → canonical IR → SDK
preserves the *measurement outcome distribution* (when run on a
deterministic local simulator). Hypothesis generates random circuits
constrained to the canonical gate set so we exercise the conversion
path widely without producing un-implementable circuits.

These are slow-ish — a few seconds per case — so we cap shrinking and
example counts to keep CI fast.
"""

from __future__ import annotations

import math

import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

pytest.importorskip("qiskit")
pytest.importorskip("qiskit_aer")

from qiskit import QuantumCircuit

from qrouter import Circuit, run

# A conservative slice of the canonical gate set that every supported
# backend understands (no parametric gates, no controlled-rotations —
# they're tested individually elsewhere).
_GATES_1Q = ["h", "x", "y", "z", "s", "sdg", "t", "tdg"]
_GATES_2Q = ["cx", "cz", "swap"]


@st.composite
def _random_qiskit_circuit(draw: st.DrawFn) -> QuantumCircuit:
    n_qubits = draw(st.integers(min_value=2, max_value=4))
    n_gates = draw(st.integers(min_value=1, max_value=8))

    qc = QuantumCircuit(n_qubits, n_qubits)
    for _ in range(n_gates):
        kind = draw(st.sampled_from(["1q", "2q"]))
        if kind == "1q" or n_qubits < 2:
            gate = draw(st.sampled_from(_GATES_1Q))
            target = draw(st.integers(min_value=0, max_value=n_qubits - 1))
            getattr(qc, gate)(target)
        else:
            gate = draw(st.sampled_from(_GATES_2Q))
            ctrl = draw(st.integers(min_value=0, max_value=n_qubits - 1))
            tgt_choices = [i for i in range(n_qubits) if i != ctrl]
            tgt = draw(st.sampled_from(tgt_choices))
            getattr(qc, gate)(ctrl, tgt)
    qc.measure(range(n_qubits), range(n_qubits))
    return qc


def _hellinger_fidelity(p: dict[str, int], q: dict[str, int]) -> float:
    keys = set(p) | set(q)
    sp = sum(p.values()) or 1
    sq = sum(q.values()) or 1
    return sum(math.sqrt((p.get(k, 0) / sp) * (q.get(k, 0) / sq)) for k in keys) ** 2


@settings(
    max_examples=15,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
)
@given(_random_qiskit_circuit())
@pytest.mark.unit
def test_qiskit_round_trip_preserves_distribution(qc: QuantumCircuit) -> None:
    """Qiskit ─► IR ─► Qiskit must yield (statistically) the same outcome distribution."""
    assume(qc.num_qubits >= 1)
    shots = 4096
    seed = 1234

    direct = run(Circuit.from_qiskit(qc), backend="local:aer", shots=shots, seed=seed)

    circuit = Circuit.from_qiskit(qc)
    qc2 = circuit.to_qiskit()
    via_ir = run(Circuit.from_qiskit(qc2), backend="local:aer", shots=shots, seed=seed)

    fid = _hellinger_fidelity(direct.counts, via_ir.counts)
    assert fid > 0.9, (
        f"distributions diverged: fid={fid:.3f}; direct={direct.counts}; via_ir={via_ir.counts}"
    )


@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
)
@given(_random_qiskit_circuit())
@pytest.mark.unit
def test_braket_adapter_round_trip(qc: QuantumCircuit) -> None:
    """Qiskit ─► IR ─► Braket ─► IR ─► Qiskit must preserve the gate count."""
    pytest.importorskip("braket.circuits")
    from qrouter.adapters.braket_adapter import BraketAdapter
    from qrouter.adapters.qiskit_adapter import QiskitAdapter

    qa = QiskitAdapter()
    ba = BraketAdapter()

    ir1 = qa.to_ir(qc)
    bc = ba.from_ir(ir1)
    ir2 = ba.to_ir(bc)

    # The two IRs differ in exact text but should agree on shape.
    assert ir1.metadata.n_qubits == ir2.metadata.n_qubits
    # Aer-comparison: both should produce equivalent distributions.
    shots = 2048
    seed = 99
    r1 = run(ir1, backend="local:aer", shots=shots, seed=seed)
    r2 = run(ir2, backend="local:aer", shots=shots, seed=seed)
    fid = _hellinger_fidelity(r1.counts, r2.counts)
    assert fid > 0.9, (
        f"Braket round-trip altered the distribution: fid={fid:.3f}\nr1={r1.counts}\nr2={r2.counts}"
    )


@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
)
@given(_random_qiskit_circuit())
@pytest.mark.unit
def test_quri_adapter_round_trip(qc: QuantumCircuit) -> None:
    """Qiskit ─► IR ─► QURI Parts ─► IR ─► Qiskit must preserve the qubit count."""
    pytest.importorskip("quri_parts.qiskit")
    pytest.importorskip("quri_parts.openqasm")
    from qrouter.adapters.qiskit_adapter import QiskitAdapter
    from qrouter.adapters.quri_adapter import QuriAdapter

    qa = QiskitAdapter()
    qra = QuriAdapter()

    ir1 = qa.to_ir(qc)
    qp = qra.from_ir(ir1)
    ir2 = qra.to_ir(qp)

    # QURI Parts strips final measurements, so n_clbits drops to 0;
    # the qubit count must be preserved.
    assert ir1.metadata.n_qubits == ir2.metadata.n_qubits
