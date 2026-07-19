from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import questionary

from cli_kit.errors import Aborted
from cli_kit.prompts._style import qstyle


@dataclass(frozen=True)
class Choice:
    """A select option whose displayed ``title`` differs from its returned ``value``.

    Plain ``str`` choices (where the label *is* the value) still work; use
    ``Choice`` when you need to show one thing and return another — e.g. show
    ``"admin (agent)"`` but return ``"admin"``, or show a human label but return
    an id. ``value`` may be any object, not just a string.
    """

    title: str
    value: Any


def _to_questionary(choice: str | Choice) -> Any:
    if isinstance(choice, Choice):
        return questionary.Choice(title=choice.title, value=choice.value)
    return choice


def _build_select(**kw: Any):
    return questionary.select(**kw)


def _build_checkbox(**kw: Any):
    return questionary.checkbox(**kw)


def select(
    message: str,
    *,
    choices: list[str] | list[Choice] | list[str | Choice],
    default: str | None = None,
    search: bool = False,
    qmark: str = "?",
) -> Any:
    """Prompt for one choice. Returns the selected value.

    ``choices`` are plain strings (label == value) or :class:`Choice` objects
    (label ≠ value). With ``Choice`` options the return type is the chosen
    ``value`` (any type), not the displayed title. Raises :class:`Aborted` on
    cancel (Ctrl-C/ESC) so the menu failsafe can treat it as "go back".
    """
    answer = _build_select(
        message=message,
        choices=[_to_questionary(c) for c in choices],
        default=default,
        style=qstyle(),
        qmark=qmark,
        use_search_filter=search,
        # questionary rejects j/k navigation while a prefix filter is active,
        # since j/k could be part of the typed prefix. Disable it when search is on.
        use_jk_keys=not search,
    ).ask()
    if answer is None:
        raise Aborted()
    return answer


def multiselect(message: str, *, choices: list[str] | list[Choice]) -> list[Any]:
    answer = _build_checkbox(
        message=message,
        choices=[_to_questionary(c) for c in choices],
        style=qstyle(),
    ).ask()
    if answer is None:
        raise Aborted()
    return answer
