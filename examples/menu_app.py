"""A runnable blockhead-clikit sample that shows off the whole surface.

One file, two ways to drive the same actions:

* **As a CLI** — thanks to `click`, every action is also a subcommand::

      python examples/menu_app.py greet --name Ada
      python examples/menu_app.py configure --env staging
      python examples/menu_app.py --help

* **As an interactive menu** — run it with no arguments and you get a themed
  menu with shortcut keys, a **Settings** submenu, and **Back** navigation::

      python examples/menu_app.py

The actions are plain functions wired into *both* surfaces with
`cli_kit.expose`, so the CLI and the menu never drift apart. Questionary
prompts (`prompts.text` / `prompts.number` / `prompts.confirm`) collect input
interactively; the same values can be passed as flags on the command line.

Everything here depends only on `cli_kit` and the standard library, so you can
copy this file anywhere blockhead-clikit is installed and run it as-is.

Menu keys: ↑/↓ + Enter to pick, Backspace to go **Back** a level, `q` to quit
at the top. Ctrl-C during an action returns you to the menu.
"""

from __future__ import annotations

import time

import click

from cli_kit import Menu, expose, prompts, ui, use_theme

# Default to the "clay" theme (warm Anthropic-ish orange). Swap for any built-in
# preset: "blockhead", "clay", "zigablocks", or "mono".
use_theme("clay")


# --- actions -------------------------------------------------------------
# Plain functions. Their parameters have defaults, so `expose` maps them to
# click *options* (--name, --env, ...) and, when a flag is omitted at the menu,
# a questionary prompt fills it in. That's the "input for questionary" path.


def greet(name: str = "") -> None:
    """Say hello to someone (prompts for a name when not given)."""
    name = name or prompts.text("Your name?", default="world")
    ui.success(f"Hello, {name}!")


def configure(env: str = "") -> None:
    """Configure the app for an environment."""
    env = env or prompts.select(
        "Which environment?",
        choices=["dev", "staging", "prod"],
        default="dev",
    )
    with ui.status(f"Configuring for {env}…"):
        time.sleep(2.0)
    ui.success(f"Configured for {env}.")


def run() -> None:
    """Run the app."""
    with ui.status("Running…"):
        time.sleep(2.0)
    ui.success("Run finished.")


def deploy(replicas: int = 0) -> None:
    """Deploy the app with a chosen number of replicas."""
    replicas = replicas or prompts.number("How many replicas?", default=3, min=1, max=10)
    with ui.status(f"Deploying {replicas} replica(s)…"):
        time.sleep(2.0)
    ui.success(f"Deployed {replicas} replica(s).")


def reset() -> None:
    """Reset all local state (destructive)."""
    with ui.status("Resetting…"):
        time.sleep(1.5)
    ui.warn("Local state reset.")


# --- click CLI group -----------------------------------------------------


@click.group(help="Sample blockhead-clikit app. Run with no command for the menu.")
def cli() -> None:
    pass


# --- interactive menu ----------------------------------------------------


def build_menu() -> Menu:
    menu = Menu("Sample App")

    # Top-level actions. `shortcut=` marks the accelerator, which the menu now
    # renders inline in the label — e.g. "Greet" → "(G)reet".
    menu.add("Greet", greet, shortcut="g")
    menu.add("Configure", configure, shortcut="c")
    menu.add("Run", run, shortcut="r")
    menu.add("Deploy", deploy, shortcut="d")

    # A submenu. Selecting "▸ Settings" descends into it; Backspace (or the
    # "← Back" item) returns to the top level.
    settings = menu.group("Settings")
    settings.add("Reset local state", reset, shortcut="x", destructive=True)

    return menu


def main() -> None:
    # Wire every action into the click group so `--help` and subcommands work.
    expose(greet, cli=cli)
    expose(configure, cli=cli)
    expose(run, cli=cli)
    expose(deploy, cli=cli)
    expose(reset, cli=cli)

    import sys

    # With arguments → behave as a CLI. Without → open the interactive menu.
    if len(sys.argv) > 1:
        cli()
        return

    ui.banner("Sample App")
    build_menu().run()


if __name__ == "__main__":
    main()
