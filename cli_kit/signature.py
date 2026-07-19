"""Introspect an action's signature into parameter specs.

Shared by registry (click flags) and django_cmd (Django args) so the mapping
logic exists once.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ParamSpec:
    name: str
    has_default: bool
    default: Any
    annotation: Any


def params_of(fn: Callable) -> list[ParamSpec]:
    sig = inspect.signature(fn)
    specs: list[ParamSpec] = []
    for name, param in sig.parameters.items():
        if name in {"self", "cls"}:
            continue
        if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            continue
        has_default = param.default is not inspect.Parameter.empty
        specs.append(
            ParamSpec(
                name=name,
                has_default=has_default,
                default=param.default if has_default else None,
                annotation=(
                    param.annotation if param.annotation is not inspect.Parameter.empty else None
                ),
            )
        )
    return specs
