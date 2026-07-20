from rich import box

from cli_kit.theme.base import Theme

BLOCKHEAD = Theme(
    name="blockhead",
    accent="magenta",
    success="green",
    error="red",
    warn="yellow",
    muted="dim",
    ok="✓",
    fail="✗",
    arrow="▸",
    bullet="■",
    box=box.HEAVY,
    spinner="line",
    qmark=">",
)
