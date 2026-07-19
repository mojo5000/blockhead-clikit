from __future__ import annotations

from typing import Any

import questionary

from cli_kit.errors import Aborted
from cli_kit.prompts._style import qstyle


def _build(**kw: Any):
    return questionary.text(**kw)


def number(
    message: str,
    *,
    default: int | None = None,
    min: int | None = None,  # noqa: A002
    max: int | None = None,  # noqa: A002
) -> int:
    raw = _build(
        message=message,
        default="" if default is None else str(default),
        style=qstyle(),
    ).ask()
    if raw is None:
        raise Aborted()
    value = int(raw)  # raises ValueError on non-numeric — surfaced by the failsafe
    if (min is not None and value < min) or (max is not None and value > max):
        raise ValueError(f"{value} out of range [{min}, {max}]")
    return value
