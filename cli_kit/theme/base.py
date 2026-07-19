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
