from __future__ import annotations

from typing import Any

import questionary

from cli_kit.errors import Aborted
from cli_kit.prompts._style import qstyle
from cli_kit.theme import theme


def _build(**kw: Any):
    return questionary.text(**kw)


def _ask(question: Any) -> Any:
    answer = question.ask()
    if answer is None:
        raise Aborted()
    return answer


def text(message: str, *, default: str = "", validate=None) -> str:
    return _ask(
        _build(
            message=message,
            default=default,
            validate=validate,
            style=qstyle(),
            qmark=theme().qmark,
        )
    )
