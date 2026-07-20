from rich import box

from cli_kit.theme.base import Theme

ZIGABLOCKS = Theme(
    name="zigablocks",
    accent="cyan",
    success="green",
    error="red",
    warn="yellow",
    muted="dim",
    ok="✓",
    fail="✗",
    arrow="→",
    bullet="•",
    box=box.ROUNDED,
    spinner="dots",
    qmark=">",
)
