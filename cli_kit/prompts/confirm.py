from __future__ import annotations

from typing import Any

import questionary

from cli_kit.errors import Aborted
from cli_kit.prompts._style import qstyle
from cli_kit.theme import theme


def _build(**kw: Any) -> questionary.Question:
    return questionary.confirm(**kw)


def confirm(message: str, *, default: bool = False) -> bool:
    answer = _build(message=message, default=default, style=qstyle(), qmark=theme().qmark).ask()
    if answer is None:
        raise Aborted()
    return bool(answer)
