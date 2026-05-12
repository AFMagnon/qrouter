"""Plugin registry for circuit adapters.

Adapters can be registered three ways:
1. Built-ins are imported and registered lazily on first lookup, so a
   `pip install qrouter` without `[qiskit]` does not pay the Qiskit
   import cost or fail when Qiskit is missing.
2. Third-party plugins declare a `qrouter.adapters` entry point in
   their own `pyproject.toml`; the registry scans them lazily on first
   miss.
3. Direct calls to `register_adapter` for tests or notebooks.
"""

from __future__ import annotations

import importlib
from importlib.metadata import entry_points
from threading import RLock
from typing import Final, cast

from qrouter.adapters.base import CircuitAdapter
from qrouter.core.exceptions import QRouterError

#: Built-in adapters: name → (module path, class name).
_BUILTIN_FACTORIES: Final[dict[str, tuple[str, str]]] = {
    "openqasm": ("qrouter.adapters.openqasm_adapter", "OpenQasmAdapter"),
    "qiskit": ("qrouter.adapters.qiskit_adapter", "QiskitAdapter"),
    "braket": ("qrouter.adapters.braket_adapter", "BraketAdapter"),
    "quri": ("qrouter.adapters.quri_adapter", "QuriAdapter"),
}

_ADAPTERS: dict[str, CircuitAdapter] = {}
_ENTRY_POINTS_LOADED = False
_LOCK = RLock()


def register_adapter(adapter: CircuitAdapter) -> None:
    """Register or replace an adapter under its `name`."""
    if not isinstance(adapter, CircuitAdapter):
        raise QRouterError(f"Object {adapter!r} does not satisfy the CircuitAdapter protocol.")
    with _LOCK:
        _ADAPTERS[adapter.name] = adapter


def _try_load_builtin(name: str) -> CircuitAdapter | None:
    factory = _BUILTIN_FACTORIES.get(name)
    if factory is None:
        return None
    module_name, class_name = factory
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        return None
    cls = getattr(module, class_name, None)
    if cls is None:  # pragma: no cover — would indicate a packaging bug
        return None
    try:
        instance = cast(CircuitAdapter, cls())
    except Exception:  # pragma: no cover
        return None
    register_adapter(instance)
    return instance


def _load_entry_points() -> None:
    global _ENTRY_POINTS_LOADED
    with _LOCK:
        if _ENTRY_POINTS_LOADED:
            return
        for ep in entry_points(group="qrouter.adapters"):
            try:
                obj = ep.load()
            except Exception:  # noqa: S112  # broken third-party plugin; skip
                continue
            adapter = obj() if callable(obj) else obj
            if isinstance(adapter, CircuitAdapter):
                _ADAPTERS.setdefault(adapter.name, adapter)
        _ENTRY_POINTS_LOADED = True


def get_adapter(name: str) -> CircuitAdapter:
    """Look up a registered adapter by name."""
    with _LOCK:
        if name in _ADAPTERS:
            return _ADAPTERS[name]
        builtin = _try_load_builtin(name)
        if builtin is not None:
            return builtin
        _load_entry_points()
        if name in _ADAPTERS:
            return _ADAPTERS[name]
    raise QRouterError(
        f"No adapter registered for {name!r}. "
        f"Known built-ins: {sorted(_BUILTIN_FACTORIES)}. "
        f"Currently registered: {sorted(_ADAPTERS)}."
    )


def list_adapters() -> list[str]:
    """Return the names of every registered adapter (excluding unloaded built-ins)."""
    _load_entry_points()
    with _LOCK:
        return sorted(_ADAPTERS)


__all__ = ["get_adapter", "list_adapters", "register_adapter"]
