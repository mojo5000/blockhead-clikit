"""The Theme interface every preset implements."""

from __future__ import annotations

from dataclasses import dataclass

from rich import box as rich_box


@dataclass(frozen=True)
class Theme:
    name: str
    # palette — SEMANTIC rich style strings, never literal colors elsewhere
    accent: str
    success: str
    error: str
    warn: str
    muted: str
    # symbols — swappable per brand / ascii for mono
    ok: str
    fail: str
    arrow: str
    bullet: str
    # structure
    box: rich_box.Box
    spinner: str
    # prompt marker questionary shows before a question ("? " by default). Part of
    # the theme so the marker is one swappable convention, not hardcoded per call.
    # Defaulted (and placed last) so existing/custom themes that omit it keep
    # questionary's "?" without every constructor needing to pass it.
    qmark: str = "?"
