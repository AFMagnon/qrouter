"""qrouter — a unified Python router for quantum computing platforms.

Public API:
    Circuit       — unified circuit type (canonical IR is OpenQASM 3)
    Result        — unified job-result type
    Job           — unified job handle
    run           — submit a circuit to a backend, return a Result
    load_policy   — load a routing policy from YAML or a Python dict
    register_backend, register_adapter — plugin extension points
"""

from __future__ import annotations

from qrouter._version import __version__
from qrouter.adapters import register_adapter
from qrouter.backends import register_backend
from qrouter.convert import (
    convert,
    detect_source,
    to_braket,
    to_ir,
    to_qasm,
    to_qiskit,
    to_quri,
)
from qrouter.core.circuit import Circuit
from qrouter.core.exceptions import (
    BackendError,
    ConversionError,
    QRouterError,
    UnsupportedGateError,
)
from qrouter.core.result import Result
from qrouter.execution import run
from qrouter.router import load_policy

__all__ = [
    "BackendError",
    "Circuit",
    "ConversionError",
    "QRouterError",
    "Result",
    "UnsupportedGateError",
    "__version__",
    "convert",
    "detect_source",
    "load_policy",
    "register_adapter",
    "register_backend",
    "run",
    "to_braket",
    "to_ir",
    "to_qasm",
    "to_qiskit",
    "to_quri",
]
