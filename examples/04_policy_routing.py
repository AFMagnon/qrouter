"""Use a YAML routing policy instead of a hard-coded backend.

Backend ids are picked from circuit metadata: small circuits run
locally, larger ones spill to managed simulators or hardware.
"""

from __future__ import annotations


def main() -> None:
    from pathlib import Path

    from qiskit import QuantumCircuit

    from qrouter import Circuit, load_policy, run  # type: ignore[attr-defined]

    load_policy(Path(__file__).with_name("qrouter.policy.yaml"))

    qc = QuantumCircuit(4, 4)
    qc.h(range(4))
    qc.measure(range(4), range(4))

    circuit = Circuit.from_qiskit(qc)
    result = run(circuit, shots=1024)

    print(f"selected backend: {result.backend}")
    print(f"counts: {result.counts}")


if __name__ == "__main__":
    main()
