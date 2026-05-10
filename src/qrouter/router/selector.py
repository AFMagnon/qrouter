"""Selector: evaluate a policy against a circuit and return a backend id.

Predicates are simple Python expressions evaluated against a tightly
controlled namespace. The whitelist intentionally excludes builtins and
double-underscore attributes so a malicious policy file cannot escape
the sandbox.
"""

from __future__ import annotations

from typing import Any

from qrouter.core.circuit import Circuit
from qrouter.core.exceptions import RoutingError
from qrouter.router.policy import Policy, get_active_policy

_ALLOWED_NAMES: frozenset[str] = frozenset(
    {
        "n_qubits",
        "n_clbits",
        "gate_count",
        "has_measurement",
        "has_mid_circuit_measurement",
        "has_classical_control",
        "requires_real_hw",
        "shots",
    }
)


def _build_namespace(circuit: Circuit, *, shots: int, hints: dict[str, Any]) -> dict[str, Any]:
    md = circuit.metadata
    ns: dict[str, Any] = {
        "n_qubits": md.n_qubits,
        "n_clbits": md.n_clbits,
        "gate_count": md.gate_count,
        "has_measurement": md.has_measurement,
        "has_mid_circuit_measurement": md.has_mid_circuit_measurement,
        "has_classical_control": md.has_classical_control,
        "requires_real_hw": bool(hints.get("requires_real_hw", False)),
        "shots": shots,
    }
    return ns


def _evaluate(predicate: str, namespace: dict[str, Any]) -> bool:
    if not _ALLOWED_NAMES.issuperset(_extract_names(predicate)):
        raise RoutingError(
            f"Predicate {predicate!r} references variables outside the whitelist "
            f"{sorted(_ALLOWED_NAMES)}."
        )
    return bool(eval(predicate, {"__builtins__": {}}, namespace))  # noqa: S307


def _extract_names(predicate: str) -> set[str]:
    import ast

    tree = ast.parse(predicate, mode="eval")
    return {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}


def select_backend(
    circuit: Circuit,
    *,
    shots: int = 1024,
    policy: Policy | None = None,
    hints: dict[str, Any] | None = None,
) -> str:
    """Return the backend id that the active policy maps the circuit to."""
    active = policy or get_active_policy()
    if active is None or not active.rules:
        raise RoutingError(
            "No routing policy is active. Pass a backend explicitly or "
            "call `qrouter.load_policy(...)` first."
        )
    namespace = _build_namespace(circuit, shots=shots, hints=hints or {})
    for rule in active.rules:
        if rule.default is not None:
            return rule.default
        assert rule.predicate is not None and rule.backend is not None
        if _evaluate(rule.predicate, namespace):
            return rule.backend
    raise RoutingError("No rule matched and no default was provided.")


__all__ = ["select_backend"]
