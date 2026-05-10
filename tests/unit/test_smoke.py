"""Smoke tests for the Phase 2 scaffolding.

These confirm the package imports cleanly and exposes its declared API.
Phase 3 will replace them with proper behavioural tests.
"""

from __future__ import annotations

import pytest

import qrouter


@pytest.mark.unit
def test_version_is_string() -> None:
    assert isinstance(qrouter.__version__, str)
    assert qrouter.__version__.count(".") >= 1


@pytest.mark.unit
def test_public_api_surface() -> None:
    for name in (
        "Circuit",
        "Result",
        "QRouterError",
        "ConversionError",
        "UnsupportedGateError",
        "BackendError",
    ):
        assert hasattr(qrouter, name), f"qrouter is missing {name!r}"


@pytest.mark.unit
def test_result_is_pydantic_model() -> None:
    from qrouter import Result

    r = Result(counts={"00": 5, "11": 5}, shots=10, backend="local:aer")
    assert r.shots == 10
    assert r.counts["11"] == 5
    assert r.backend == "local:aer"
