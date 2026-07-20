from rich import box

from cli_kit.theme.base import Theme

# No color: semantic tokens map to styles that render in a dumb terminal / CI log.
MONO = Theme(
    name="mono",
    accent="bold",
    success="bold",
    error="bold",
    warn="bold",
    muted="dim",
    ok="[ok]",
    fail="[x]",
    arrow="->",
    bullet="-",
    box=box.ASCII,
    spinner="line",
    qmark=">",
)
