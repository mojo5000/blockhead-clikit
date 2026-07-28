# blockhead-clikit

[![CI](https://github.com/mojo5000/blockhead-clikit/actions/workflows/ci.yml/badge.svg)](https://github.com/mojo5000/blockhead-clikit/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/blockhead-clikit.svg)](https://pypi.org/project/blockhead-clikit/)
[![Python versions](https://img.shields.io/pypi/pyversions/blockhead-clikit.svg)](https://pypi.org/project/blockhead-clikit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A small, reusable **click + rich + questionary** framework for building smooth
Python CLIs — themed prompts, a persistent menu tree, subprocess helpers, and a
Django management-command bridge.

The distributable package is **`blockhead-clikit`**; the import name is
**`cli_kit`** (kept stable so existing `from cli_kit import …` code needs no
changes).

![A blockhead-clikit menu: a themed banner over a breadcrumb-titled list of
workspace actions, one highlighted by the selection cursor.](docs/images/menu-example.png)

## Prerequisites

- **Python 3.12+** — the package declares `requires-python = ">=3.12"`. Check
  with `python --version`.
- **[uv](https://docs.astral.sh/uv/)** (recommended) — used for installing,
  locking, and running. Install it with `curl -LsSf https://astral.sh/uv/install.sh | sh`
  (or `brew install uv`). Plain `pip` works too; the README just leads with `uv`.
- **A real terminal** — the interactive menu and prompts drive a TTY (arrow
  keys, shortcut keystrokes, spinners). In a non-interactive context (CI, a
  pipe) drive the same actions as [CLI commands](#run-it-as-a-cli) instead.

Runtime dependencies (`click`, `rich`, `questionary`) are pulled in
automatically. The optional Django bridge needs Django, installed via the
`django` extra — see [Install](#install).

## Install

```bash
uv add blockhead-clikit
# or
pip install blockhead-clikit
```

Consumers needing the Django bridge (`cli_kit.django_cmd`) add the `django`
extra (Django is imported lazily, so only these consumers pull it in):

```bash
uv add "blockhead-clikit[django]"
```

### Installing from git (unreleased fixes / pinning a branch)

You can also depend on it straight from the repository — useful for pinning an
unreleased commit or tracking a branch before it's published to PyPI:

```bash
uv add "blockhead-clikit @ git+https://github.com/mojo5000/blockhead-clikit@v0.1.0"
```

The part after the `@` at the end of the URL is a **git ref** — a tag, branch,
or commit. Choose deliberately:

| Ref you write         | You get                                              | Use when |
| --------------------- | ---------------------------------------------------- | -------- |
| `@v0.1.0` (a **tag**) | Exactly that release, frozen. Never moves.           | **Default.** Reproducible builds; you upgrade on purpose. |
| `@main` (a **branch**)| Whatever `main` pointed to **when you last locked**. | You want to track the latest and re-lock often. |
| `@<commit-sha>`       | One exact commit.                                    | Pinning to an unreleased fix. |

> **Pick the newest tag, not `v0.1.0` by rote.** The example above uses
> `v0.1.0` because it's the current release — check the
> [tags](https://github.com/mojo5000/blockhead-clikit/tags) (or run
> `git ls-remote --tags origin`) and use the latest, so you don't accidentally
> pin an old version copied from these docs. (For released versions, prefer the
> plain PyPI install above and pin with a normal version specifier.)

**Tag vs. branch when updating.** A tag is frozen, so a change here can't
silently break a git-pinned consumer — you upgrade on purpose:

```bash
# tracking a TAG: bump the tag in the URL (e.g. v0.1.0 → v0.2.0), then
uv lock --upgrade-package blockhead-clikit

# tracking a BRANCH (@main): the URL doesn't change; re-lock to pull the
# latest commit on that branch
uv lock --upgrade-package blockhead-clikit
```

With `@main`, the pin lives in your `uv.lock` (the exact commit), so builds
stay reproducible until you re-lock — but a plain `uv sync` on a fresh checkout
will fetch whatever the lock recorded, not necessarily today's `main`.

## Quick start

This runs as-is — it depends only on `cli_kit` and the standard library, so you
can copy it into a file and `python that_file.py`:

```python
import time

from cli_kit import Menu, ui, use_theme

use_theme("clay")  # or "blockhead", "zigablocks", "mono"

def configure():
    with ui.status("Configuring…"):   # themed spinner
        time.sleep(2)
    ui.success("Configuration complete.")

menu = Menu("My App")
menu.add("Configure", configure, shortcut="c")   # renders as "(C)onfigure"; press c to run it
menu.run()
```

Navigate with ↑/↓ + Enter, press an item's **shortcut key** to jump straight to
it, **Backspace** to go back a level, and **q** to quit at the top.

To shell out to another process instead of sleeping, use `sh.run`, which gives
you the same themed spinner around a real command:

```python
from cli_kit import sh

# spinner shows while the command runs; capture=True collects its output
sh.run(["git", "pull"], spinner="Updating…", capture=True, check=True)
```

## Run the example

[`examples/menu_app.py`](examples/menu_app.py) is a single, self-contained file
that drives the same actions two ways — an interactive menu and a `click` CLI.
It depends only on `cli_kit` and the standard library, so it runs anywhere the
package is installed.

### Run it as a menu

```bash
# from a checkout of this repo (deps already synced via `uv sync`)
uv run python examples/menu_app.py

# or, if you've installed blockhead-clikit into your own environment
python examples/menu_app.py
```

You get a themed menu (on the **clay** theme) with shortcut-marked labels —
**(G)reet**, **(C)onfigure**, **(R)un**, **(D)eploy** — and a **Settings**
submenu you descend into and leave with Backspace / **← Back**. Omitted inputs
are collected with questionary prompts; Ctrl-C during an action returns you to
the menu.

### Run it as a CLI

Pass a subcommand and the same file behaves as a plain `click` app — no menu,
so it works in scripts and CI:

```bash
uv run python examples/menu_app.py --help
uv run python examples/menu_app.py greet --name Ada
uv run python examples/menu_app.py configure --env staging
uv run python examples/menu_app.py deploy --replicas 2
```

Omit a flag and the interactive prompt fills it in — e.g. `greet` with no
`--name` asks for one. Same actions, same code, both surfaces — wired once with
`expose`.

## What you get

- **`theme`** — swappable presets (`clay`, `blockhead`, `zigablocks`, `mono`);
  register your own via `register_theme()`.
- **`ui`** — `banner`, `success`/`error`/`warn`/`info`, `kv`, `panel`, `table`,
  `badge`, `status` (spinner), and step reports.
- **`prompts`** — themed `text`/`confirm`/`select`/`multiselect`/`number`/`path`
  + `validators`, plus a tty-aware `resolve` contract (value-supplied →
  short-circuit; missing + no tty + required → error naming the flag).
- **`sh.run(...)`** — subprocess with echo, spinner, `dry_run`, typed `CommandFailed`.
- **`Menu`** — persistent nav loop: back-nav, breadcrumb, remember-last,
  error failsafe, **shortcut hotkeys** (labelled inline as `(C)onfigure`, and
  pressing the key selects the item), submenus, destructive confirms, and
  type-to-filter search.
- **`registry.expose`** — one plain callable becomes both a click command and a
  menu item, killing menu/command drift.
- **`django_cmd.ActionCommand`** — subclass to get a `manage.py` command
  (Django imported lazily; only needed with the `django` extra).

See [`cli_kit/README.md`](cli_kit/README.md) for the full API and design notes,
and [`examples/README.md`](examples/README.md) for the example walkthrough.

## Develop

```bash
uv sync --all-extras   # runtime + dev deps (pytest, ruff, coverage) + django extra
uv run pytest          # run the suite
uv run pytest --cov    # with coverage
uv run ruff check .    # lint
uv run ruff format .   # format
```

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full workflow and release
process.

## License

[MIT](LICENSE) © Steve Motola.
