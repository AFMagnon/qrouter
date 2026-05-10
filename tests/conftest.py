"""Shared pytest fixtures.

Integration tests are skipped unless the corresponding credentials are
present in the environment, so the unit suite always runs hermetically.
"""

from __future__ import annotations

import os

import pytest


def _has_env(*names: str) -> bool:
    return all(os.environ.get(n) for n in names)


@pytest.fixture(scope="session")
def has_ibm_credentials() -> bool:
    return _has_env("IBM_QUANTUM_TOKEN")


@pytest.fixture(scope="session")
def has_aws_credentials() -> bool:
    return _has_env("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_DEFAULT_REGION")


@pytest.fixture(scope="session")
def has_oqtopus_credentials() -> bool:
    return _has_env("OQTOPUS_API_TOKEN", "OQTOPUS_API_URL")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Skip integration tests when credentials are missing."""
    skip_integration = pytest.mark.skip(reason="integration test: required credentials are not set")
    for item in items:
        if "integration" not in item.keywords:
            continue
        needs = set(item.keywords) & {"needs_ibm", "needs_aws", "needs_oqtopus"}
        if "needs_ibm" in needs and not _has_env("IBM_QUANTUM_TOKEN"):
            item.add_marker(skip_integration)
        if "needs_aws" in needs and not _has_env("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"):
            item.add_marker(skip_integration)
        if "needs_oqtopus" in needs and not _has_env("OQTOPUS_API_TOKEN", "OQTOPUS_API_URL"):
            item.add_marker(skip_integration)
