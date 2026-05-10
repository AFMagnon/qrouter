"""Run a Bell state circuit on a local simulator.

This example reflects the Phase 1 API contract; it will start working
once Phase 3 lands the Qiskit adapter and local backend.
"""

from __future__ import annotations


def main() -> None:
    from qiskit import QuantumCircuit

    from qrouter import Circuit, run

    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])

    circuit = Circuit.from_qiskit(qc)
    result = run(circuit, backend="local:aer", shots=1024)

    print(f"backend     = {result.backend}")
    print(f"shots       = {result.shots}")
    print(f"counts      = {result.counts}")
    print(f"duration_ms = {result.duration_ms:.1f}")


if __name__ == "__main__":
    main()
