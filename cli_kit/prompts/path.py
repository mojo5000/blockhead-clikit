from __future__ import annotations

from pathlib import Path
from typing import Any

import questionary

from cli_kit.errors import Aborted
from cli_kit.prompts._style import qstyle
from cli_kit.theme import theme


def _build(**kw: Any):
    return questionary.path(**kw)


def path(message: str, *, default: str = "", must_exist: bool = False) -> str:
    answer = _build(message=message, default=default, style=qstyle(), qmark=theme().qmark).ask()
    if answer is None:
        raise Aborted()
    if must_exist and not Path(answer).exists():
        raise ValueError(f"path does not exist: {answer}")
    return answer
