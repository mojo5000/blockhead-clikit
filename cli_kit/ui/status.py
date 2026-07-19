"""Themed spinner for indeterminate waits.

    with ui.status("Logging into ECR…"):
        ...                      # spinner + message styled from the active theme

For work with no measurable progress (a network call, a poll) where a
determinate `ui.progress` bar would be dishonest. The spinner glyph comes from
`t.spinner` and the message is styled with `t.accent`, so it re-skins with the
theme; it renders on the shared console. `rich`'s `Status` stays private — callers
only ever see `ui.status`.
"""

from __future__ import annotations

from rich.markup import escape
from rich.status import Status

from cli_kit.theme import theme
from cli_kit.ui.console import console


def status(message: str) -> Status:
    """A themed spinner context manager. Enter to show it, exit to clear it."""
    t = theme()
    return console.status(f"[{t.accent}]{escape(message)}[/]", spinner=t.spinner)
