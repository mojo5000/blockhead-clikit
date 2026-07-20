from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import questionary

from cli_kit.errors import Aborted
from cli_kit.prompts._style import qstyle
from cli_kit.theme import theme


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


@dataclass(frozen=True)
class Separator:
    """A non-selectable divider rendered between groups of choices.

    ``line`` is the text shown for the divider; it defaults to questionary's
    own separator glyph when omitted. Separators are skipped by cursor
    navigation and never returned as an answer.
    """

    line: str | None = None


def _to_questionary(choice: str | Choice | Separator) -> Any:
    if isinstance(choice, Separator):
        return (
            questionary.Separator()
            if choice.line is None
            else questionary.Separator(choice.line)
        )
    if isinstance(choice, Choice):
        return questionary.Choice(title=choice.title, value=choice.value)
    return choice


def _bind_abort_keys(question: Any, *, quit_key: bool) -> Any:
    """Wire ESC (and optionally ``q``) to abort a select prompt.

    questionary 2.x binds only Ctrl-C/Ctrl-Q to cancel; ESC does nothing. We
    reach through the returned :class:`Question` to its prompt_toolkit
    ``Application`` and add the missing bindings so a bare ESC — and, when
    ``quit_key`` is set, a plain ``q``/``Q`` — exits the prompt the same way
    Ctrl-C does (raising ``KeyboardInterrupt``, which questionary turns into a
    ``None`` answer and we turn into :class:`Aborted`).
    """
    from prompt_toolkit.keys import Keys

    bindings = question.application.key_bindings

    @bindings.add(Keys.Escape, eager=True)
    def _(event: Any) -> None:
        event.app.exit(exception=KeyboardInterrupt, style="class:aborting")

    if quit_key:
        for key in ("q", "Q"):

            @bindings.add(key, eager=True)
            def _(event: Any) -> None:
                event.app.exit(exception=KeyboardInterrupt, style="class:aborting")

    return question


def _build_select(*, quit_key: bool = False, **kw: Any):
    return _bind_abort_keys(questionary.select(**kw), quit_key=quit_key)


def _build_checkbox(**kw: Any):
    return questionary.checkbox(**kw)


def select(
    message: str,
    *,
    choices: list[str] | list[Choice] | list[str | Choice | Separator],
    default: str | None = None,
    search: bool = False,
    qmark: str | None = None,
    quit_key: bool = False,
) -> Any:
    """Prompt for one choice. Returns the selected value.

    ``choices`` are plain strings (label == value) or :class:`Choice` objects
    (label ≠ value). With ``Choice`` options the return type is the chosen
    ``value`` (any type), not the displayed title. Raises :class:`Aborted` on
    cancel (Ctrl-C/ESC) so the menu failsafe can treat it as "go back".

    ``qmark`` defaults to the active theme's marker (``theme().qmark``); pass an
    explicit string to override it for one call.

    ``quit_key`` additionally binds a plain ``q``/``Q`` keypress to abort — used
    by the top-level menu so ``q`` quits the app. Leave it off for search menus
    (where ``q`` is a filter character) and for value-selection prompts.
    """
    answer = _build_select(
        quit_key=quit_key,
        message=message,
        choices=[_to_questionary(c) for c in choices],
        default=default,
        style=qstyle(),
        qmark=theme().qmark if qmark is None else qmark,
        use_search_filter=search,
        # questionary rejects j/k navigation while a prefix filter is active,
        # since j/k could be part of the typed prefix. Disable it when search is on.
        use_jk_keys=not search,
    ).ask()
    if answer is None:
        raise Aborted()
    return answer


def multiselect(
    message: str, *, choices: list[str] | list[Choice] | list[str | Choice | Separator]
) -> list[Any]:
    answer = _build_checkbox(
        message=message,
        choices=[_to_questionary(c) for c in choices],
        style=qstyle(),
        qmark=theme().qmark,
    ).ask()
    if answer is None:
        raise Aborted()
    return answer
