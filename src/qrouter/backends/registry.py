"""Plugin registry for backends. Mirrors `adapters.registry`."""

from __future__ import annotations

import importlib
from importlib.metadata import entry_points
from threading import RLock
from typing import Final

from qrouter.backends.base import Backend
from qrouter.core.exceptions import QRouterError

#: Built-in backends. `(module, class, args)` — args are passed to the
#: constructor for backends that need a device id.
_BUILTIN_FACTORIES: Final[dict[str, tuple[str, str, tuple[object, ...]]]] = {
    "local:aer": ("qrouter.backends.local", "LocalAerBackend", ()),
    "local:qulacs": ("qrouter.backends.local", "LocalQulacsBackend", ()),
}

_BACKENDS: dict[str, Backend] = {}
_ENTRY_POINTS_LOADED = False
_LOCK = RLock()


def register_backend(backend: Backend) -> None:
    """Register or replace a backend under its `name`."""
    if not isinstance(backend, Backend):
        raise QRouterError(f"Object {backend!r} does not satisfy the Backend protocol.")
    with _LOCK:
        _BACKENDS[backend.name] = backend


def _try_load_builtin(name: str) -> Backend | None:
    factory = _BUILTIN_FACTORIES.get(name)
    if factory is None:
        return None
    module_name, class_name, args = factory
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        return None
    cls = getattr(module, class_name, None)
    if cls is None:  # pragma: no cover
        return None
    try:
        instance = cls(*args)
    except Exception:  # pragma: no cover
        return None
    register_backend(instance)
    return instance


def _load_entry_points() -> None:
    global _ENTRY_POINTS_LOADED
    with _LOCK:
        if _ENTRY_POINTS_LOADED:
            return
        for ep in entry_points(group="qrouter.backends"):
            try:
                obj = ep.load()
            except Exception:  # noqa: S112  # broken third-party plugin; skip
                continue
            backend = obj() if callable(obj) else obj
            if isinstance(backend, Backend):
                _BACKENDS.setdefault(backend.name, backend)
        _ENTRY_POINTS_LOADED = True


def get_backend(name: str) -> Backend:
    with _LOCK:
        if name in _BACKENDS:
            return _BACKENDS[name]
        builtin = _try_load_builtin(name)
        if builtin is not None:
            return builtin
        _load_entry_points()
        if name in _BACKENDS:
            return _BACKENDS[name]
    raise QRouterError(
        f"No backend registered for {name!r}. "
        f"Known built-ins: {sorted(_BUILTIN_FACTORIES)}. "
        f"Currently registered: {sorted(_BACKENDS)}."
    )


def list_backends() -> list[str]:
    _load_entry_points()
    with _LOCK:
        return sorted(_BACKENDS)


__all__ = ["get_backend", "list_backends", "register_backend"]
