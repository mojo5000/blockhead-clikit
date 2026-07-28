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
            questionary.Separator() if choice.line is None else questionary.Separator(choice.line)
        )
    if isinstance(choice, Choice):
        return questionary.Choice(title=choice.title, value=choice.value)
    return choice


class _AbortPrompt(Exception):
    """Private signal: an abort key was pressed inside a running select prompt.

    We exit the prompt_toolkit ``Application`` with *this* rather than
    ``KeyboardInterrupt`` so questionary never sees a cancel it would announce
    with its own "Cancelled by user" line. ``select`` catches it and re-raises
    :class:`Aborted`, funnelling into the same menu failsafe as every other
    cancel. Kept private to this module — callers only ever see ``Aborted``.
    """


def _bind_shortcut_keys(
    question: questionary.Question, shortcuts: dict[str, Any], reserved: set[str]
) -> None:
    """Bind single-key accelerators that jump straight to a choice.

    ``shortcuts`` maps a key character to the value ``select`` should return
    when that key is pressed — the menu passes ``{"c": "(C)onfigure", …}`` so
    ``c`` selects that item without arrowing to it. Each bound key exits the
    prompt_toolkit ``Application`` with its value as the result (mirroring how
    the abort keys exit, but returning rather than raising).

    ``reserved`` names keys already claimed by an abort binding (e.g. ``q`` as
    the quit key); a shortcut on a reserved key is skipped so the two never
    fight over the same char. ``eager=True`` so the accelerator fires before
    any default binding consumes the key.
    """
    bindings: Any = question.application.key_bindings

    for key, value in shortcuts.items():
        if key in reserved:
            continue

        def _pick(event: Any, _value: Any = value) -> None:
            event.app.exit(result=_value)

        _pick._cli_kit_shortcut = True  # type: ignore[attr-defined]
        bindings.add(key, eager=True)(_pick)


def _bind_abort_keys(question: questionary.Question, *, quit_key: bool, search: bool) -> set[str]:
    """Wire the standard "go back / quit" keys onto a select prompt.

    questionary 2.x only binds Ctrl-C/Ctrl-Q to cancel. We reach through the
    returned :class:`Question` to its prompt_toolkit ``Application`` and add the
    keys cli_kit treats as the universal back/quit gesture:

    - ``Backspace`` — the primary, instant "back one level" key, *except* in
      search menus, where Backspace edits the type-to-filter text and must be
      left alone.
    - ``q`` / ``Q`` — when ``quit_key`` is set (top-level, non-search menus).
    - ``Escape`` — always, as a bonus. Note ESC is the lead byte of every
      arrow/function-key escape sequence, so prompt_toolkit waits out its
      escape timeout before firing this — hence the perceptible delay ESC has
      that Backspace/``q`` do not. Backspace and ``q`` are the smooth path;
      ESC is kept only so muscle memory still works.

    Every bound key exits the prompt with :class:`_AbortPrompt`, which
    :func:`select` converts to :class:`Aborted`. Returns the set of literal
    character keys it reserved (e.g. ``{"q", "Q"}``) so shortcut binding can
    steer clear of them.
    """
    from prompt_toolkit.keys import Keys

    # questionary always builds its Application with a concrete KeyBindings, but
    # the type is declared Optional[KeyBindingsBase]; we reach past that here.
    bindings: Any = question.application.key_bindings

    def _abort(event: Any) -> None:
        event.app.exit(exception=_AbortPrompt, style="class:aborting")

    # Tag so callers/tests can tell *our* abort binding apart from questionary's
    # own bindings on the same key (e.g. its Backspace filter-edit handler).
    _abort._cli_kit_abort = True  # type: ignore[attr-defined]

    # ESC is always an abort key. Backspace aborts only when it isn't needed to
    # edit filter text (i.e. not a search menu). q/Q only where it isn't a
    # filter character either. eager=True so they fire before any default
    # binding can consume the key.
    keys: list[Any] = [Keys.Escape]
    if not search:
        keys.append(Keys.Backspace)
    if quit_key:
        keys += ["q", "Q"]
    for key in keys:
        bindings.add(key, eager=True)(_abort)

    # Only literal char keys matter for shortcut collision (Escape/Backspace are
    # not shortcut candidates); q/Q are the ones a shortcut could clash with.
    return {"q", "Q"} if quit_key else set()


def _build_select(
    *,
    quit_key: bool = False,
    search: bool = False,
    shortcuts: dict[str, Any] | None = None,
    **kw: Any,
) -> questionary.Question:
    question = questionary.select(**kw)
    reserved = _bind_abort_keys(question, quit_key=quit_key, search=search)
    # Shortcut chars are filter characters in a search menu, so leave them alone
    # there — same reason Backspace/q aren't bound as abort keys under search.
    if shortcuts and not search:
        _bind_shortcut_keys(question, shortcuts, reserved)
    return question


def _build_checkbox(**kw: Any) -> questionary.Question:
    return questionary.checkbox(**kw)


def select(
    message: str,
    *,
    choices: list[str] | list[Choice] | list[str | Choice | Separator],
    default: str | None = None,
    search: bool = False,
    qmark: str | None = None,
    quit_key: bool = False,
    shortcuts: dict[str, Any] | None = None,
) -> Any:
    """Prompt for one choice. Returns the selected value.

    ``choices`` are plain strings (label == value) or :class:`Choice` objects
    (label ≠ value). With ``Choice`` options the return type is the chosen
    ``value`` (any type), not the displayed title. Raises :class:`Aborted` when
    the user backs out (Backspace / ESC / Ctrl-C, plus ``q`` when ``quit_key``
    is set) so the menu failsafe can treat it as "go back".

    ``qmark`` defaults to the active theme's marker (``theme().qmark``); pass an
    explicit string to override it for one call.

    ``quit_key`` additionally binds a plain ``q``/``Q`` keypress to abort — used
    by the top-level menu so ``q`` quits the app. Leave it off for search menus
    (where ``q`` is a filter character) and for value-selection prompts.
    Backspace and ESC abort regardless of ``quit_key``.

    ``shortcuts`` maps a single key character to the value to return when that
    key is pressed — a menu passes ``{"c": "(C)onfigure", …}`` so ``c`` jumps
    straight to that choice. A shortcut on a reserved key (``q``/``Q`` under
    ``quit_key``) is skipped, and shortcuts are ignored entirely under
    ``search`` (where the char is filter text).
    """
    try:
        answer = _build_select(
            quit_key=quit_key,
            search=search,
            shortcuts=shortcuts,
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
    except _AbortPrompt:
        # An abort key exited the prompt directly (rather than questionary
        # mapping it to a None answer). Same meaning: back out.
        raise Aborted() from None
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
    return list(answer)
