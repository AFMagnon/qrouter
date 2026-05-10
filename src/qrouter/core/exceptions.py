"""Exception hierarchy for qrouter.

Every error raised by the library inherits from `QRouterError` so callers
can catch a single root.
"""

from __future__ import annotations


class QRouterError(Exception):
    """Root of the qrouter exception hierarchy."""


class ConversionError(QRouterError):
    """Raised when a circuit cannot be converted to/from the canonical IR."""


class UnsupportedGateError(ConversionError):
    """Raised when a gate cannot be expressed in the target SDK or backend."""

    def __init__(self, gate: str, target: str) -> None:
        self.gate = gate
        self.target = target
        super().__init__(
            f"Gate {gate!r} is not supported by target {target!r}. "
            "Provide a decomposition or pick a different backend."
        )


class BackendError(QRouterError):
    """Raised by backend adapters for submission/execution failures."""


class AuthenticationError(BackendError):
    """Raised when credentials are missing or invalid."""


class JobTimeoutError(BackendError):
    """Raised when a job exceeds its allotted time."""


class RoutingError(QRouterError):
    """Raised when no rule in the active policy matches a circuit."""


__all__ = [
    "AuthenticationError",
    "BackendError",
    "ConversionError",
    "JobTimeoutError",
    "QRouterError",
    "RoutingError",
    "UnsupportedGateError",
]
