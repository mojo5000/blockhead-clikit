from rich import box

from cli_kit.theme.base import Theme

# "clay" — an Anthropic-ish warm orange (#cc785c). Shipped as a built-in preset so
# every consumer (./run, ./configure, ./blockhead) shares one palette definition
# via ``use_theme("clay")`` instead of hand-rolling equivalent colors. This is the
# single source of truth for the warm-orange identity.
CLAY = Theme(
    name="clay",
    accent="#cc785c",
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
)
