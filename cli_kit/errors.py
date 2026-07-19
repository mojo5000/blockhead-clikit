"""Typed errors that every surface funnels into one error path."""

from __future__ import annotations


class Aborted(Exception):
    """Raised when the user cancels a prompt or menu action (Ctrl-C / ESC)."""


class InputRequired(Aborted):
    """A required input was missing and no interactive terminal was available.

    Raised by ``cli_kit.prompts.resolve`` when a value is neither supplied
    up front nor obtainable by prompting (stdin is not a tty). Subclasses
    ``Aborted`` so the menu nav loop's failsafe already treats it as
    "quietly go back" — in practice a menu is always interactive, so this
    fires only on non-tty surfaces (scripts, CI). Each surface adapter is
    responsible for translating it into its own error (e.g. the Click
    adapter maps it to ``click.UsageError``).

    ``flag`` carries the ``--flag`` the caller should pass, so adapters can
    surface it without re-parsing the message.
    """

    def __init__(self, message: str, *, flag: str | None = None) -> None:
        self.flag = flag
        super().__init__(message)


class CommandFailed(Exception):
    """A subprocess exited non-zero. Carries context for consistent display."""

    def __init__(self, cmd: list[str], returncode: int, output: str | None = None) -> None:
        self.cmd = cmd
        self.returncode = returncode
        self.output = output
        super().__init__(f"command failed (exit {returncode}): {' '.join(cmd)}")
