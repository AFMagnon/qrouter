"""Local simulator backends.

Two simulators are exposed by default:

- ``local:aer``    — IBM's `qiskit-aer` (high-performance, supports
  mid-circuit measurement and noise).
- ``local:qulacs`` — QunaSys's qulacs via QURI Parts (very fast on
  modest qubit counts).

Both backends share the same submission contract: take a `Circuit`,
shots, and return a normalized `Result`. The adapters are loaded lazily
so users who only have one of the two stacks installed do not pay an
import cost for the other.
"""

from __future__ import annotations

import time
from typing import Any

from qrouter.backends.base import BackendCapabilities
from qrouter.core.circuit import Circuit
from qrouter.core.exceptions import BackendError
from qrouter.core.ir import SUPPORTED_GATES
from qrouter.core.result import Result


class LocalAerBackend:
    """Run circuits on `qiskit_aer.AerSimulator`."""

    name = "local:aer"
    capabilities = BackendCapabilities(
        max_qubits=32,
        is_simulator=True,
        supports_mid_circuit_measurement=True,
        supports_classical_control=True,
        supports_statevector=True,
        supports_expectation=True,
        native_gates=frozenset(SUPPORTED_GATES),
    )

    def submit(
        self,
        circuit: Circuit,
        *,
        shots: int,
        method: str | None = None,
        seed: int | None = None,
        **kwargs: Any,
    ) -> Result:
        try:
            from qiskit import qasm3 as q_qasm3
            from qiskit_aer import AerSimulator
        except ImportError as exc:  # pragma: no cover — guarded by extras
            raise BackendError(
                "Aer is not installed. Install with `pip install qrouter[qiskit]`."
            ) from exc

        try:
            qc = q_qasm3.loads(circuit.qasm)
        except Exception as exc:
            raise BackendError(f"Failed to parse circuit IR for Aer: {exc}") from exc

        sim_kwargs: dict[str, Any] = dict(kwargs)
        if method is not None:
            sim_kwargs["method"] = method
        simulator = AerSimulator(**sim_kwargs)

        run_kwargs: dict[str, Any] = {"shots": shots}
        if seed is not None:
            run_kwargs["seed_simulator"] = seed

        started = time.perf_counter()
        try:
            job = simulator.run(qc, **run_kwargs)
            aer_result = job.result()
        except Exception as exc:
            raise BackendError(f"Aer execution failed: {exc}") from exc
        duration_ms = (time.perf_counter() - started) * 1000.0

        # Aer separates classical registers with spaces in count keys.
        # qrouter's convention is a single contiguous bitstring.
        raw_counts = aer_result.get_counts() if aer_result.results else {}
        counts: dict[str, int] = {str(k).replace(" ", ""): int(v) for k, v in raw_counts.items()}

        job_id = ""
        if hasattr(job, "job_id"):
            try:
                job_id = str(job.job_id())
            except Exception:  # pragma: no cover — provider-side variation
                job_id = ""

        return Result(
            counts=counts,
            shots=shots,
            backend=self.name,
            job_id=job_id,
            duration_ms=duration_ms,
            raw={"backend_name": getattr(aer_result, "backend_name", "")},
            metadata={"method": sim_kwargs.get("method", "automatic")},
        )


class LocalQulacsBackend:
    """Run circuits on `qulacs` via QURI Parts."""

    name = "local:qulacs"
    capabilities = BackendCapabilities(
        max_qubits=30,
        is_simulator=True,
        supports_mid_circuit_measurement=False,
        supports_statevector=True,
        supports_expectation=True,
        native_gates=frozenset(SUPPORTED_GATES),
    )

    def submit(
        self,
        circuit: Circuit,
        *,
        shots: int,
        seed: int | None = None,
        **kwargs: Any,
    ) -> Result:
        try:
            from qrouter.adapters.quri_adapter import QuriAdapter
        except ImportError as exc:  # pragma: no cover
            raise BackendError("QURI Parts adapter unavailable: " + str(exc)) from exc
        try:
            from quri_parts.qulacs.sampler import create_qulacs_vector_sampler
        except ImportError as exc:  # pragma: no cover — guarded by extras
            raise BackendError(
                "qulacs is not installed. Install with `pip install qrouter[quri]`."
            ) from exc

        try:
            qp_circuit = QuriAdapter().from_ir(circuit)
        except Exception as exc:
            raise BackendError(f"Failed to load circuit IR into QURI Parts: {exc}") from exc

        sampler = create_qulacs_vector_sampler()

        started = time.perf_counter()
        try:
            sampling = sampler(qp_circuit, shots)
        except Exception as exc:
            raise BackendError(f"Qulacs execution failed: {exc}") from exc
        duration_ms = (time.perf_counter() - started) * 1000.0

        n_qubits = circuit.metadata.n_qubits or qp_circuit.qubit_count
        counts: dict[str, int] = {}
        for state, count in sampling.items():
            # qulacs returns integer states with qubit 0 in the lowest bit;
            # qrouter's bitstring convention is the same (rightmost char = q0).
            bitstring = format(int(state), f"0{n_qubits}b")
            counts[bitstring] = counts.get(bitstring, 0) + int(count)

        return Result(
            counts=counts,
            shots=shots,
            backend=self.name,
            duration_ms=duration_ms,
            metadata={"seed": seed} if seed is not None else {},
        )


__all__ = ["LocalAerBackend", "LocalQulacsBackend"]
