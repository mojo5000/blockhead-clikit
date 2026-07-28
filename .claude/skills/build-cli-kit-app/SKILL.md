---
name: build-cli-kit-app
description: >-
  Scaffold or extend a Python CLI built with blockhead-clikit (import name
  `cli_kit`) — a click + rich + questionary framework. Use when the user wants
  to create a cli_kit app, add a menu, add a command exposed to both a menu and
  a click CLI, wire questionary prompts, add submenus/Back, use shortcut
  hotkeys, or apply a theme. Triggers on "cli_kit", "blockhead-clikit",
  "clikit menu", "expose a command to menu and CLI".
---

# Build a blockhead-clikit app

`cli_kit` (package `blockhead-clikit`) builds interactive CLIs from plain
callables. The central idea: write an **action** (a normal function), then wire
it into surfaces (a `click` CLI, an interactive `Menu`) with adapters. Do not
hand-write the same logic into two surfaces.

## Install

```bash
uv add blockhead-clikit          # or: pip install blockhead-clikit
uv add "blockhead-clikit[django]"  # only if you use the ActionCommand bridge
```

## Recipe

1. **Pick a theme** at startup: `use_theme("clay")` (`clay`, `blockhead`,
   `zigablocks`, `mono`).
2. **Write actions** as plain functions. Give them defaulted parameters so the
   same function works as a click option *and* a menu prompt.
3. **Collect input** with `prompts.text` / `prompts.select` / `prompts.number` /
   `prompts.confirm` — fall back to a prompt only when a value wasn't supplied.
4. **Build a `Menu`**, `menu.add(label, action, shortcut="x")`. Use
   `menu.group("Name")` for submenus; **Back** is automatic.
5. **Expose to the CLI** with `expose(action, cli=group)` so `--help` and
   subcommands work non-interactively.
6. **Run**: menu with no args, click group with a subcommand.

## Rules that keep it correct

- **Never catch `Aborted`** inside an action — the menu treats it as go-back.
- Shortcuts are **per-menu unique**; they render inline (`shortcut="c"` on
  `"Configure"` → `(C)onfigure`) and pressing the key selects the item.
- `q`/Backspace/ESC are reserved for quit/back; don't assign them as shortcuts.
  Shortcuts are inert in a `search=True` menu (the char is filter text).
- For code that must run **without a TTY** (CI/pipes), gate input through
  `prompts.resolve(...)` / `confirm_or_yes(...)` rather than the raw wrappers.
- Emit output via `ui.*` (`success`/`error`/`info`/`warn`) or `ui.console`,
  never `print`.

## Template

```python
"""A blockhead-clikit app: interactive menu + click CLI from one set of actions."""
from __future__ import annotations

import sys

import click

from cli_kit import Menu, expose, prompts, ui, use_theme

use_theme("clay")


# --- actions: plain functions, defaulted params so they map to click options ---
def greet(name: str = "") -> None:
    """Say hello (prompts for a name when not given)."""
    name = name or prompts.text("Your name?", default="world")
    ui.success(f"Hello, {name}!")


def deploy(replicas: int = 0) -> None:
    """Deploy with a chosen replica count."""
    replicas = replicas or prompts.number("How many replicas?", default=3, min=1, max=10)
    with ui.status(f"Deploying {replicas}…"):
        ...  # real work
    ui.success(f"Deployed {replicas}.")


# --- click group ---
@click.group(help="My app. Run with no command for the menu.")
def cli() -> None:
    pass


# --- interactive menu ---
def build_menu() -> Menu:
    menu = Menu("My App")
    menu.add("Greet", greet, shortcut="g")
    menu.add("Deploy", deploy, shortcut="d")
    settings = menu.group("Settings")
    settings.add("Reset", lambda: ui.warn("reset"), shortcut="x", destructive=True)
    return menu


def main() -> None:
    for action in (greet, deploy):
        expose(action, cli=cli)  # same actions, both surfaces
    if len(sys.argv) > 1:
        cli()                    # `app deploy --replicas 2`
        return
    ui.banner("My App")
    build_menu().run()           # interactive menu


if __name__ == "__main__":
    main()
```

## Verify

Run both surfaces before declaring done:

```bash
uv run python app.py --help
uv run python app.py greet --name Ada     # CLI path
uv run python app.py                       # interactive menu
```

See `cli_kit/README.md` for the full API and `examples/menu_app.py` for a
complete, runnable version of this template.
