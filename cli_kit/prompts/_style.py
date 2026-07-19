"""Build a questionary Style from the active theme."""

from __future__ import annotations

from questionary import Style

from cli_kit.theme import theme


def qstyle() -> Style:
    t = theme()
    # questionary styles take color names; accent drives the pointer/highlight.
    return Style([("pointer", t.accent), ("highlighted", t.accent), ("qmark", t.accent)])
