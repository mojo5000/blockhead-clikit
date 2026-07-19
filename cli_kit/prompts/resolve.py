"""The non-interactive input contract for cli_kit prompts.

The themed wrappers (``text``/``select``/``confirm``) unconditionally
``.ask()`` — they assume an interactive terminal. That is the right default
for the menu, but it hangs (or crashes) when a command runs in a script or
CI where there is no tty and no human to answer.

``resolve`` closes that gap. It is a three-state, tty-aware adapter that sits
*in front of* the themed wrappers:

1. A value was supplied up front (e.g. a ``--flag``) → return it, no prompt.
2. Missing + not a tty + required → raise ``InputRequired`` naming the flag.
3. Missing + not a tty + optional → return ``default``.
4. Missing + tty → prompt via the themed wrapper (which raises ``Aborted``
   on Ctrl-C / ESC, funnelling into the same error path as everything else).

This layer is deliberately Click-free so it stays usable by every surface
(the menu, the Django management-command adapter, and the Click adapter).
Each surface translates ``InputRequired`` into its own error; see
``cli_kit.registry`` for the Click mapping.
"""

from __future__ import annotations

import sys
from typing import Any

from cli_kit.errors import InputRequired
from cli_kit.prompts.confirm import confirm as _confirm
from cli_kit.prompts.select import select as _select
from cli_kit.prompts.text import text as _text


def is_interactive() -> bool:
    """True iff stdin is a tty. Mocked in tests to exercise both branches."""
    return sys.stdin.isatty()


def _is_supplied(value: Any) -> bool:
    """True if ``value`` was meaningfully provided (not None, not empty str)."""
    if value is None:
        return False
    if isinstance(value, str) and value == "":
        return False
    return True


def resolve(
    value: Any,
    *,
    prompt: str,
    default: Any = None,
    choices: list[str] | None = None,
    validate: Any = None,
    required: bool = True,
    flag_name: str | None = None,
) -> Any:
    """Resolve a single CLI input against the interactive/non-interactive contract.

    Parameters
    ----------
    value : the value already supplied (typically a parsed flag/option result)
    prompt : the message shown when prompting interactively, and echoed in the
        non-tty "missing required input" error
    default : default for the prompt; also the return value for a missing
        *optional* input on a non-tty stdin
    choices : when given, prompt with ``select`` over these options instead of
        free-text ``text``
    validate : optional validator forwarded to the themed ``text`` wrapper
    required : if True, a missing value on a non-tty stdin raises ``InputRequired``
    flag_name : the ``--flag`` the user should pass; named in the non-tty error

    Raises
    ------
    InputRequired : required input missing with no interactive terminal.
    Aborted : the user cancelled the interactive prompt (Ctrl-C / ESC).
    """
    if _is_supplied(value):
        return value

    if not is_interactive():
        if required:
            flag = f"--{flag_name.replace('_', '-')}" if flag_name else "(missing flag)"
            raise InputRequired(
                f"Missing required input: {prompt}\n"
                f"Pass {flag} on the command line, or run in an interactive terminal.",
                flag=flag if flag_name else None,
            )
        return default

    if choices is not None:
        return _select(prompt, choices=choices, default=default)

    return _text(prompt, default="" if default is None else default, validate=validate)


def confirm_or_yes(
    yes: bool,
    prompt: str,
    *,
    default: bool = False,
    danger: bool = False,
) -> bool:
    """Confirmation helper for destructive / gated commands.

    - ``yes=True`` (the ``--yes`` flag) → return True silently, no prompt.
    - Non-interactive stdin without ``--yes`` → raise ``InputRequired`` telling
      the user to pass ``--yes`` to confirm in scripts.
    - Interactive stdin → ask via the themed ``confirm`` wrapper (which raises
      ``Aborted`` on Ctrl-C / ESC). Destructive prompts (``danger=True``)
      default to False regardless of the caller's ``default``.
    """
    if yes:
        return True

    if not is_interactive():
        raise InputRequired(
            f"{prompt}\nPass --yes to confirm in non-interactive mode.",
            flag="--yes",
        )

    effective_default = False if danger else default
    return _confirm(prompt, default=effective_default)
