"""One-shot conversion between SDKs — the most common use case.

The source SDK is detected from the object's type, so callers do not
have to spell it out:

    qc_quri = to_quri(qc)        # qiskit → QURI Parts
    qc_braket = to_braket(qc)    # qiskit → Braket
    qasm = to_qasm(qc)           # any → OpenQASM 3 string

For programmatic targets:

    qc_x = convert(qc, target="quri")
"""

from __future__ import annotations


def main() -> None:
    from qiskit import QuantumCircuit

    from qrouter import to_braket, to_qasm, to_quri

    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])

    qc_quri = to_quri(qc)
    qc_braket = to_braket(qc)
    qasm = to_qasm(qc)

    print(
        f"qiskit → QURI Parts: qubits={qc_quri.qubit_count}, gates={[g.name for g in qc_quri.gates]}"
    )
    print(f"qiskit → Braket:    qubits={qc_braket.qubit_count}")
    print("qiskit → OpenQASM3:")
    print(qasm)


if __name__ == "__main__":
    main()
