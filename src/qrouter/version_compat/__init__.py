"""Compatibility shims for vendor SDKs that ship breaking changes.

Currently focused on Qiskit 1.x → 2.x → 3.x. Each shim resolves at
import time so the cost is paid once.
"""

from __future__ import annotations
