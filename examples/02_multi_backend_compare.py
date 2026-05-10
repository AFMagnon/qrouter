"""Run the same circuit on multiple backends and compare counts."""

from __future__ import annotations


def main() -> None:
    from qiskit import QuantumCircuit

    from qrouter import Circuit, run

    qc = QuantumCircuit(3, 3)
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.measure_all(add_bits=False)

    circuit = Circuit.from_qiskit(qc)

    for backend in ("local:aer", "local:qulacs", "braket:sv1"):
        result = run(circuit, backend=backend, shots=2048)
        print(f"{backend:15s}  counts={result.counts}")


if __name__ == "__main__":
    main()
