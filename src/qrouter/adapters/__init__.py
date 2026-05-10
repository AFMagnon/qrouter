"""Circuit adapters: convert between vendor SDKs and the canonical IR.

Adapters implement the `CircuitAdapter` protocol. They are discovered
either by direct import (built-ins) or via the `qrouter.adapters` Python
entry-point group (third-party plugins).
"""

from __future__ import annotations

from qrouter.adapters.base import CircuitAdapter
from qrouter.adapters.registry import get_adapter, list_adapters, register_adapter

__all__ = [
    "CircuitAdapter",
    "get_adapter",
    "list_adapters",
    "register_adapter",
]
