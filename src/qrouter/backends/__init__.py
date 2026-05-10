"""Execution backends.

A backend is anything that takes a `Circuit` plus run-time parameters
(shots, observables, …) and returns a `Result`. Backends are loaded
through the `qrouter.backends` Python entry-point group, mirroring the
adapter registry.
"""

from __future__ import annotations

from qrouter.backends.base import Backend, BackendCapabilities
from qrouter.backends.registry import (
    get_backend,
    list_backends,
    register_backend,
)

__all__ = [
    "Backend",
    "BackendCapabilities",
    "get_backend",
    "list_backends",
    "register_backend",
]
