from __future__ import annotations

from collections.abc import Callable
from typing import Any

import questionary

from cli_kit.errors import Aborted
from cli_kit.prompts._style import qstyle
from cli_kit.theme import theme

# questionary ships no type hints; a validate callback maps input -> ok | message.
Validate = Callable[[str], bool | str]


def _build(**kw: Any) -> questionary.Question:
    return questionary.text(**kw)


def _ask(question: questionary.Question) -> str:
    answer = question.ask()
    if answer is None:
        raise Aborted()
    return str(answer)


def text(message: str, *, default: str = "", validate: Validate | None = None) -> str:
    return _ask(
        _build(
            message=message,
            default=default,
            validate=validate,
            style=qstyle(),
            qmark=theme().qmark,
        )
    )
