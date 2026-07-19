"""Theme registry + active-theme state."""

from __future__ import annotations

from cli_kit.theme.base import Theme
from cli_kit.theme.blockhead import BLOCKHEAD
from cli_kit.theme.clay import CLAY
from cli_kit.theme.mono import MONO
from cli_kit.theme.zigablocks import ZIGABLOCKS

_REGISTRY: dict[str, Theme] = {t.name: t for t in (ZIGABLOCKS, BLOCKHEAD, CLAY, MONO)}
_active: Theme = ZIGABLOCKS


def theme() -> Theme:
    """The currently active theme."""
    return _active


def use_theme(name: str) -> None:
    """Set the active theme by name. Raises KeyError if unknown."""
    global _active
    _active = _REGISTRY[name]


def register_theme(t: Theme) -> None:
    """Register a custom theme so apps can add their own without editing cli_kit."""
    _REGISTRY[t.name] = t


__all__ = ["Theme", "theme", "use_theme", "register_theme"]
