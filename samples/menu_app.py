"""A minimal, runnable blockhead-clikit sample.

Builds a menu with three actions — Configure / Run / Deploy — each of which
just shows a themed spinner for a couple of seconds and prints a message. It
uses nothing but the library itself (plus the stdlib `time`), so you can
copy this file anywhere blockhead-clikit is installed and run it as-is:

    python samples/menu_app.py

Ctrl-C at the menu quits; Ctrl-C during an action returns to the menu.
"""

import time

from cli_kit import Menu, ui, use_theme

# Pick any built-in theme: "blockhead", "clay", "zigablocks", or "mono".
use_theme("blockhead")


def _work(message: str, done: str, seconds: float = 2.5) -> None:
    """Show a themed spinner for a few seconds, then a success line."""
    with ui.status(message):
        time.sleep(seconds)
    ui.success(done)


def configure() -> None:
    _work("Configuring…", "Configuration complete.")


def run() -> None:
    _work("Running…", "Run finished.")


def deploy() -> None:
    _work("Deploying…", "Deployed successfully.")


def main() -> None:
    ui.banner("Sample App")

    menu = Menu("Sample App")
    menu.add("Configure", configure, shortcut="c")
    menu.add("Run", run, shortcut="r")
    menu.add("Deploy", deploy, shortcut="d")
    menu.run()


if __name__ == "__main__":
    main()
