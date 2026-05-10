"""Routing layer: pick a backend per circuit from a declarative policy."""

from __future__ import annotations

from qrouter.router.policy import Policy, load_policy
from qrouter.router.selector import select_backend

__all__ = ["Policy", "load_policy", "select_backend"]
