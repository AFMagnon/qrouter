"""One-shot conversion helpers — the ergonomic top-level surface.

Most users do not want to think about the canonical IR. They have a
circuit in one SDK and want the same circuit in another:

    from qrouter import to_quri
    qc_quri = to_quri(my_qiskit_circuit)

These helpers wrap the underlying adapters in a `source-autodetect,
go-through-IR, return-target-native` pipeline. The source SDK is
inferred from the object's module name (``qiskit.*`` → ``qiskit``,
``braket.*`` → ``braket``, ``quri_parts.*`` → ``quri``, ``str`` →
``openqasm``, an existing :class:`Circuit` stays as-is).
"""

from __future__ import annotations

from typing import Any, Literal, cast

from qrouter.adapters.openqasm_adapter import OpenQasmAdapter
from qrouter.adapters.registry import get_adapter
from qrouter.core.circuit import Circuit
from qrouter.core.exceptions import QRouterError

Target = Literal["qiskit", "braket", "quri", "openqasm", "ir"]


def detect_source(obj: Any) -> str:
    """Return the adapter name that handles ``obj``.

    Raises :class:`QRouterError` if no built-in adapter matches.
    """
    if isinstance(obj, Circuit):
        return "ir"
    if isinstance(obj, str):
        return "openqasm"
    module = type(obj).__module__ or ""
    if module.startswith("qiskit"):
        return "qiskit"
    if module.startswith("braket"):
        return "braket"
    if module.startswith("quri_parts"):
        return "quri"
    raise QRouterError(
        f"Cannot detect a source adapter for object of type "
        f"{type(obj).__module__}.{type(obj).__name__}. "
        "Pass `source=...` explicitly or wrap with `Circuit.from_qasm(...)`."
    )


def convert(
    source: Any,
    target: Target,
    *,
    source_adapter: str | None = None,
    version: int = 3,
) -> Any:
    """Convert ``source`` (any supported SDK) to ``target`` (any supported SDK).

    Args:
        source: A circuit object (Qiskit / Braket / QURI Parts), a
            QASM string, or a :class:`Circuit` already in canonical IR.
        target: One of ``"qiskit"``, ``"braket"``, ``"quri"``,
            ``"openqasm"``, or ``"ir"`` (returns the canonical
            :class:`Circuit`).
        source_adapter: Override autodetection (e.g. when the source
            object subclasses something unexpected).
        version: OpenQASM version when ``source`` or ``target`` is a
            string. Defaults to 3.

    Returns:
        The circuit in the requested target's native form.
    """
    src_name = source_adapter or detect_source(source)

    if src_name == target:
        # `to_qiskit(qiskit_qc)` is a sane no-op; keep referential identity.
        return source

    # Source → canonical IR
    if src_name == "ir":
        ir: Circuit = source
    elif src_name == "openqasm":
        ir = OpenQasmAdapter(version=version).to_ir(source)
    else:
        ir = get_adapter(src_name).to_ir(source)

    # Canonical IR → target
    if target == "ir":
        return ir
    if target == "openqasm":
        return OpenQasmAdapter(version=version).from_ir(ir)
    return get_adapter(target).from_ir(ir)


def to_qiskit(source: Any) -> Any:
    """Convert ``source`` to a ``qiskit.QuantumCircuit``."""
    return convert(source, "qiskit")


def to_braket(source: Any) -> Any:
    """Convert ``source`` to a ``braket.circuits.Circuit``."""
    return convert(source, "braket")


def to_quri(source: Any) -> Any:
    """Convert ``source`` to a QURI Parts ``ImmutableQuantumCircuit``."""
    return convert(source, "quri")


def to_qasm(source: Any, *, version: int = 3) -> str:
    """Convert ``source`` to an OpenQASM string (version 2 or 3)."""
    return cast(str, convert(source, "openqasm", version=version))


def to_ir(source: Any) -> Circuit:
    """Convert ``source`` to the canonical :class:`Circuit` (OpenQASM 3)."""
    return cast(Circuit, convert(source, "ir"))


__all__ = [
    "Target",
    "convert",
    "detect_source",
    "to_braket",
    "to_ir",
    "to_qasm",
    "to_qiskit",
    "to_quri",
]
