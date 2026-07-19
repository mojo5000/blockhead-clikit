"""cli_kit — a reusable click+rich+questionary CLI framework."""

from cli_kit import prompts, sh, ui  # noqa: E402  (submodule imports after errors/theme)
from cli_kit.errors import Aborted, CommandFailed
from cli_kit.menu import Menu
from cli_kit.registry import cli_command, expose
from cli_kit.theme import Theme, register_theme, theme, use_theme

__all__ = [
    "Aborted",
    "CommandFailed",
    "Theme",
    "theme",
    "use_theme",
    "register_theme",
    "ui",
    "sh",
    "prompts",
    "Menu",
    "cli_command",
    "expose",
]
