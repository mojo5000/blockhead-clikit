"""Themed layout components: kv, panel, table, badge.

``table`` escapes cell/column text by default (no accidental markup injection).
A caller that genuinely wants a styled cell — a status color, a clickable link —
wraps that value in :class:`Cell`, which carries an explicit rich style/link and
is the *only* way markup reaches the output. Columns carry optional style/justify
via :class:`Col`. Plain strings still work for both rows and columns, so the
simple ``table([("a", "b")], columns=["A", "B"])`` call is unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from rich.markup import escape
from rich.panel import Panel
from rich.table import Table

from cli_kit.theme import theme
from cli_kit.ui.console import console

# rich's column alignment vocabulary; kept explicit so ``Col.justify`` is a real
# type rather than a bare ``str``.
Justify = Literal["default", "left", "center", "right", "full"]

_STATUS_TOKEN = {
    "success": "success",
    "error": "error",
    "warn": "warn",
    "info": "muted",
}


@dataclass(frozen=True)
class Col:
    """A table column: header ``name`` + optional per-column rich style/justify.

    ``style`` applies to every cell in the column (e.g. ``"bold"``, ``"dim"``);
    a per-:class:`Cell` style overrides it. ``justify`` is passed to rich
    (``"left"``/``"right"``/``"center"``).
    """

    name: str
    style: str | None = None
    justify: Justify = "left"


@dataclass(frozen=True)
class Cell:
    """A single styled cell. The ONE way a caller opts a cell into markup.

    ``text`` is escaped, then wrapped in ``style`` (a rich style string, e.g. a
    theme token like ``theme().success``) and/or made a link (``link=``). Bare
    strings passed as cells are escaped and rendered plain, so styling is always
    explicit and injection-safe.
    """

    text: str
    style: str | None = None
    link: str | None = None

    def render(self) -> str:
        body = escape(self.text)
        if self.link:
            body = f"[link={self.link}]{body}[/link]"
        if self.style:
            body = f"[{self.style}]{body}[/]"
        return body


def _render_cell(value: Any) -> str:
    """A row value → a rich-ready string. ``Cell`` styles explicitly; anything
    else is stringified + escaped (plain, injection-safe)."""
    if isinstance(value, Cell):
        return value.render()
    return escape(str(value))


def kv(pairs: dict[str, str], title: str | None = None) -> None:
    t = theme()
    grid = Table.grid(padding=(0, 2))
    grid.add_column(style="bold")
    grid.add_column(style=t.accent)
    for key, value in pairs.items():
        grid.add_row(escape(key), escape(value))
    safe_title = escape(title) if title else None
    console.print(Panel.fit(grid, title=safe_title, border_style=t.accent, box=t.box))


def panel(renderable: Any, title: str | None = None) -> None:
    t = theme()
    # Escape string renderables; pass through rich objects unchanged
    if isinstance(renderable, str):
        renderable = escape(renderable)
    safe_title = escape(title) if title else None
    console.print(Panel.fit(renderable, title=safe_title, border_style=t.accent, box=t.box))


def table(
    rows: list[tuple[Any, ...]] | list[list[Any]],
    columns: list[str | Col],
    *,
    title: str | None = None,
    show_header: bool = True,
) -> None:
    """Print a themed table.

    ``columns`` are plain header strings or :class:`Col` specs (per-column
    style/justify). ``rows`` hold plain values (escaped, rendered plain) or
    :class:`Cell` objects (explicitly styled/linked). Box + accent header come
    from the active theme — never a hardcoded color.
    """
    t = theme()
    tbl = Table(
        title=escape(title) if title else None,
        box=t.box,
        header_style=f"bold {t.accent}",
        show_header=show_header,
    )
    for col in columns:
        if isinstance(col, Col):
            tbl.add_column(escape(col.name), style=col.style, justify=col.justify)
        else:
            tbl.add_column(escape(col))
    for row in rows:
        tbl.add_row(*[_render_cell(cell) for cell in row])
    console.print(tbl)


def badge(label: str, status: str = "info") -> str:
    t = theme()
    # Unknown status values fall back to the muted token
    style = getattr(t, _STATUS_TOKEN.get(status, "muted"))
    return f"[{style}]{escape(label)}[/]"
