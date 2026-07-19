"""Themed one-line feedback. The SINGLE place feedback styling lives."""

from __future__ import annotations

from rich.markup import escape

from cli_kit.theme import theme
from cli_kit.ui.console import console


def success(msg: str) -> None:
    t = theme()
    console.print(f"[{t.success}]{escape(t.ok)}[/] {escape(msg)}")


def error(msg: str) -> None:
    t = theme()
    console.print(f"[{t.error}]{escape(t.fail)}[/] {escape(msg)}")


def warn(msg: str) -> None:
    t = theme()
    console.print(f"[{t.warn}]{escape(t.bullet)}[/] {escape(msg)}")


def info(msg: str) -> None:
    t = theme()
    console.print(f"[{t.muted}]{escape(msg)}[/]")


def breadcrumb(path: list[str]) -> None:
    if not path:
        return
    t = theme()
    trail = " › ".join(escape(p) for p in path)
    console.print(f"[{t.muted}]{trail}[/]")
