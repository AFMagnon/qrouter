"""Policy parsing + selector predicate sandboxing."""

from __future__ import annotations

import pytest

from qrouter.core.circuit import Circuit, CircuitMetadata
from qrouter.core.exceptions import RoutingError
from qrouter.router.policy import Policy, load_policy
from qrouter.router.selector import select_backend


def _make_circuit(n_qubits: int) -> Circuit:
    return Circuit(qasm="OPENQASM 3;", metadata=CircuitMetadata(n_qubits=n_qubits))


@pytest.mark.unit
def test_load_policy_from_dict() -> None:
    policy = load_policy(
        {
            "rules": [
                {"if": "n_qubits <= 20", "backend": "local:qulacs"},
                {"default": "ibm:ibm_brisbane"},
            ]
        }
    )
    assert isinstance(policy, Policy)
    assert len(policy.rules) == 2


@pytest.mark.unit
def test_first_matching_rule_wins() -> None:
    load_policy(
        {
            "rules": [
                {"if": "n_qubits <= 5", "backend": "local:qulacs"},
                {"if": "n_qubits <= 30", "backend": "braket:sv1"},
                {"default": "ibm:ibm_brisbane"},
            ]
        }
    )
    assert select_backend(_make_circuit(3)) == "local:qulacs"
    assert select_backend(_make_circuit(20)) == "braket:sv1"
    assert select_backend(_make_circuit(50)) == "ibm:ibm_brisbane"


@pytest.mark.unit
def test_predicate_sandbox_rejects_unknown_names() -> None:
    load_policy(
        {
            "rules": [
                {"if": "__import__('os').system('echo bad')", "backend": "x"},
            ]
        }
    )
    with pytest.raises(RoutingError):
        select_backend(_make_circuit(1))


@pytest.mark.unit
def test_either_conditional_or_default_required() -> None:
    with pytest.raises(ValueError, match="either a conditional"):
        Policy.model_validate({"rules": [{"if": "n_qubits<=1", "backend": "x", "default": "y"}]})
    with pytest.raises(ValueError, match="either a conditional"):
        Policy.model_validate({"rules": [{"if": "n_qubits<=1"}]})
