"""Resolve Qiskit version-specific imports.

Qiskit 1.x kept many things in `qiskit.providers.fake_provider`; 2.0
removed `qiskit.pulse` outright; 3.0 will move more. This module
exposes a single stable surface that the rest of qrouter imports from.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version


def qiskit_major_version() -> int | None:
    """Return Qiskit's major version, or None if Qiskit is not installed."""
    try:
        return int(version("qiskit").split(".", 1)[0])
    except (PackageNotFoundError, ValueError):
        return None


__all__ = ["qiskit_major_version"]
