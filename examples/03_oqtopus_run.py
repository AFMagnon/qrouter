"""Submit a circuit to OQTOPUS Cloud.

Requires:
    OQTOPUS_API_TOKEN
    OQTOPUS_API_URL
"""

from __future__ import annotations


def main() -> None:
    from quri_parts.circuit import QuantumCircuit

    from qrouter import Circuit, run

    qc = QuantumCircuit(2)
    qc.add_H_gate(0)
    qc.add_CNOT_gate(0, 1)
    # measurement is added by the OQTOPUS backend during submission

    circuit = Circuit.from_quri(qc)
    result = run(circuit, backend="oqtopus:kawasaki", shots=1024)

    print(f"job_id  = {result.job_id}")
    print(f"counts  = {result.counts}")


if __name__ == "__main__":
    main()
