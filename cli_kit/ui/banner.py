"""Themed banner."""

from __future__ import annotations

from rich.markup import escape
from rich.panel import Panel

from cli_kit.theme import theme
from cli_kit.ui.console import console


def banner(title: str, subtitle: str | None = None) -> None:
    t = theme()
    body = f"[bold {t.accent}]{escape(title)}[/]"
    if subtitle:
        body += f"\n[{t.muted}]{escape(subtitle)}[/]"
    console.print(Panel.fit(body, border_style=t.accent, box=t.box))
