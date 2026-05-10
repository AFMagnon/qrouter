"""Adapter / backend registry behaviour."""

from __future__ import annotations

from typing import Any

import pytest

from qrouter.adapters.registry import (
    get_adapter,
    list_adapters,
    register_adapter,
)
from qrouter.backends.base import BackendCapabilities
from qrouter.backends.registry import (
    get_backend,
    list_backends,
    register_backend,
)
from qrouter.core.circuit import Circuit
from qrouter.core.exceptions import QRouterError
from qrouter.core.result import Result


class _FakeAdapter:
    name = "fake"

    def to_ir(self, source: Any) -> Circuit:
        return Circuit(qasm="OPENQASM 3;")

    def from_ir(self, circuit: Circuit) -> str:
        return circuit.qasm


class _FakeBackend:
    name = "fake:device"
    capabilities = BackendCapabilities(max_qubits=4, is_simulator=True)

    def submit(self, circuit: Circuit, *, shots: int, **kwargs: Any) -> Result:
        return Result(shots=shots, backend=self.name, counts={"00": shots})


@pytest.mark.unit
def test_register_and_lookup_adapter() -> None:
    register_adapter(_FakeAdapter())
    assert "fake" in list_adapters()
    assert get_adapter("fake").name == "fake"


@pytest.mark.unit
def test_register_and_lookup_backend() -> None:
    register_backend(_FakeBackend())
    assert "fake:device" in list_backends()
    assert get_backend("fake:device").name == "fake:device"


@pytest.mark.unit
def test_unknown_lookup_raises() -> None:
    with pytest.raises(QRouterError):
        get_adapter("does-not-exist")
    with pytest.raises(QRouterError):
        get_backend("does-not-exist")
