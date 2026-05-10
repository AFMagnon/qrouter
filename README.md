# qrouter

A unified Python router for quantum computing platforms.

Write your quantum circuit once. Run it on **Qiskit (IBM Quantum)**, **Amazon Braket**, **QURI Parts**, **OQTOPUS Cloud**, or any **OpenQASM 2/3** target — without rewriting code.

> Status: **Pre-alpha** (scaffolding stage). API will change before 0.1.

---

## Why qrouter?

Every quantum SDK has its own circuit type, its own job submission API, its own result format. Switching platforms means rewriting code, and Qiskit ships breaking changes every major release. `qrouter` provides:

- A single `Circuit` type that converts to/from every supported SDK via **OpenQASM 3** as the canonical intermediate representation.
- A single `run()` entry point that submits jobs to any backend and returns a unified `Result`.
- A **routing layer** that picks the best backend per circuit based on a declarative policy.
- **Version-resilient adapters** that absorb Qiskit 1.x / 2.x / 3.x differences so your code keeps working.
- **First-class support for the Japanese quantum ecosystem** (QURI Parts, quri-parts-oqtopus, OQTOPUS Cloud) — a gap left by qBraid and TKET.

## Supported platforms (MVP)

| Platform | Circuit conversion | Job submission |
|---|---|---|
| Qiskit (IBM Quantum) | ✓ | ✓ via `qiskit-ibm-runtime` |
| Amazon Braket | ✓ | ✓ via `amazon-braket-sdk` |
| QURI Parts | ✓ | ✓ via `quri-parts-qulacs` (local) |
| OQTOPUS Cloud | ✓ | ✓ via `quri-parts-oqtopus` |
| OpenQASM 2 / 3 | ✓ | (target IR) |
| Local simulator | — | ✓ Aer / qulacs |

## Supported gates (MVP)

- **1Q**: `H, X, Y, Z, S, S†, T, T†, RX, RY, RZ, U1, U2, U3, P`
- **2Q**: `CX (CNOT), CZ, CY, SWAP, iSWAP, CRX, CRY, CRZ, RXX, RYY, RZZ, RZX, ECR`
- **3Q**: `CCX (Toffoli), CSWAP (Fredkin)`
- **Other**: `measure, reset, barrier`, parameterized gates

> `ECR` (Echoed Cross-Resonance) is the IBM Falcon/Eagle native 2Q gate; `CZ` is native on Heron and later. Both are preserved through transpilation to avoid lossy rewrites on IBM hardware.

## Installation

```bash
# Core only
pip install qrouter

# With backends you actually use
pip install "qrouter[qiskit]"
pip install "qrouter[braket]"
pip install "qrouter[quri]"
pip install "qrouter[oqtopus]"

# Everything
pip install "qrouter[all]"
```

Recommended dev setup uses [uv](https://github.com/astral-sh/uv):

```bash
uv sync --all-extras
```

## Quickstart

### One-shot conversion (most common)

```python
from qiskit import QuantumCircuit
from qrouter import to_quri, to_braket, to_qasm

qc = QuantumCircuit(2, 2)
qc.h(0); qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

qc_quri   = to_quri(qc)        # qiskit → QURI Parts
qc_braket = to_braket(qc)      # qiskit → Amazon Braket
qasm      = to_qasm(qc)        # qiskit → OpenQASM 3 string
```

The source SDK is detected automatically from the object's type. The same
helpers work with any supported SDK as input:

```python
from braket.circuits import Circuit as BraketCircuit
qc_qiskit = to_qiskit(BraketCircuit().h(0).cnot(0, 1))  # braket → qiskit
```

For programmatic targets:

```python
from qrouter import convert
qc_x = convert(qc, target="quri")
```

### Run on a backend

```python
from qrouter import Circuit, run

result = run(Circuit.from_qiskit(qc), backend="local:aer", shots=1024)
print(result.counts)            # {"00": 512, "11": 512}
print(result.backend)           # "local:aer"
print(result.duration_ms)
```

## Authentication

All credentials are read from environment variables. No tokens are ever written to logs.

| Backend | Variables |
|---|---|
| IBM Quantum | `IBM_QUANTUM_TOKEN`, `IBM_QUANTUM_INSTANCE` (optional), `IBM_QUANTUM_CHANNEL` (default `"ibm_quantum"`) |
| Amazon Braket | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`, `AWS_BRAKET_S3_BUCKET`, `AWS_BRAKET_S3_PREFIX` |
| OQTOPUS Cloud | `OQTOPUS_API_TOKEN`, `OQTOPUS_API_URL` |

A `.env` file in the working directory is auto-loaded if present.

## Routing policies

Declarative routing lets you direct circuits to the right backend without changing user code:

```yaml
# qrouter.policy.yaml
rules:
  - if: "n_qubits <= 20 and not requires_real_hw"
    backend: "local:qulacs"
  - if: "n_qubits <= 30"
    backend: "braket:sv1"
  - default: "ibm:ibm_brisbane"
```

```python
from qrouter import run, load_policy
load_policy("qrouter.policy.yaml")
result = run(circ, shots=1024)   # backend auto-selected
```

## Architecture

```
┌────────────────────────────────────────────────────┐
│ ① Facade API                                       │
│   Circuit / run() / Result / Policy                │
├────────────────────────────────────────────────────┤
│ ② Routing Layer                                    │
│   Policy(YAML/Py) → Selector → Backend ID          │
├────────────────────────────────────────────────────┤
│ ③ Transpilation Pipeline                           │
│   Source SDK ─► OpenQASM3 IR ─► Target SDK         │
├────────────────────────────────────────────────────┤
│ ④ Execution & Normalization                        │
│   Backend Adapter → Provider SDK → Result(unified) │
│   + Retry / Timeout / Logging / Metrics            │
└────────────────────────────────────────────────────┘
```

Adapters and Backends are loaded as plugins via Python `entry_points`, so a third party can add support for a new SDK without touching `qrouter` itself.

## Roadmap

- **0.1**: Circuit conversion (Qiskit / QURI Parts / Braket / OpenQASM 2-3) + local execution.
- **0.2**: IBM Quantum and Amazon Braket job submission.
- **0.3**: OQTOPUS Cloud submission, unified Result, retry/timeout.
- **0.4**: Routing layer (policy-driven).
- **0.5**: Property-based tests across all conversions; Qiskit version matrix.
- **1.0**: Stable public API.
- **post-1.0**: Cirq, PennyLane, PyQuil; auto-routing; pulse level; error mitigation hooks.

## Acknowledgements

Architecturally inspired by [Tranqu](https://github.com/oqtopus-team/tranqu) (Apache-2.0). See [NOTICE](./NOTICE) for full attribution.

## License

Apache License 2.0. See [LICENSE](./LICENSE).
