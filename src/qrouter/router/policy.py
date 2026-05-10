"""Routing policy loader and data model.

A policy is an ordered list of rules. The first rule whose predicate
matches a circuit's metadata wins. A `default` rule can be appended for
fallback.

Example YAML:

    rules:
      - if: "n_qubits <= 20 and not requires_real_hw"
        backend: "local:qulacs"
      - if: "n_qubits <= 30"
        backend: "braket:sv1"
      - default: "ibm:ibm_brisbane"
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Rule(BaseModel):
    model_config = ConfigDict(extra="forbid")

    predicate: str | None = Field(default=None, alias="if")
    backend: str | None = None
    default: str | None = None

    @model_validator(mode="after")
    def _validate_shape(self) -> Rule:
        has_default = self.default is not None
        has_conditional = self.predicate is not None and self.backend is not None
        if has_default == has_conditional:
            raise ValueError(
                "Each rule must be either a conditional ({if, backend}) "
                "or a default ({default}), not both."
            )
        return self


class Policy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rules: list[Rule] = Field(default_factory=list)


_ACTIVE_POLICY: Policy | None = None


def load_policy(source: str | Path | dict[str, Any]) -> Policy:
    """Load a policy from a YAML file path or an in-memory dict."""
    global _ACTIVE_POLICY
    if isinstance(source, (str, Path)):
        text = Path(source).read_text(encoding="utf-8")
        data = yaml.safe_load(text)
    else:
        data = source
    policy = Policy.model_validate(data)
    _ACTIVE_POLICY = policy
    return policy


def get_active_policy() -> Policy | None:
    """Return the most recently loaded policy, if any."""
    return _ACTIVE_POLICY


__all__ = ["Policy", "Rule", "get_active_policy", "load_policy"]
