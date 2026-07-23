# blockhead-clikit

A small, reusable **click + rich + questionary** framework for building smooth
Python CLIs — themed prompts, a persistent menu tree, subprocess helpers, and a
Django management-command bridge.

The distributable package is **`blockhead-clikit`**; the import name is
**`cli_kit`** (kept stable so existing `from cli_kit import …` code needs no
changes).

## Requirements

- **Python 3.12+** — the package declares `requires-python = ">=3.12"`.
- **[uv](https://docs.astral.sh/uv/)** — used for installing, locking, and
  running. Install it with `curl -LsSf https://astral.sh/uv/install.sh | sh`
  (or `brew install uv`). Not strictly required — any pip-based workflow that
  can install a git dependency works too — but every command in this README
  assumes `uv`.
- **git access to this repo** — it's a private git dependency (see below), so
  you need to be able to `git clone` it (SSH keys or a token already set up).

Runtime dependencies (`click`, `rich`, `questionary`) are pulled in
automatically. The optional Django bridge needs Django, installed via the
`django` extra — see the end of Install.

## Install

This is a private git dependency — depend on it by URL (no package index needed).
`uv` uses your existing git credentials, so a private repo works exactly like a
public one as long as you can `git clone` it.

The part after the `@` at the end of the URL is a **git ref** — a tag, branch,
or commit. Choose deliberately:

| Ref you write         | You get                                              | Use when |
| --------------------- | ---------------------------------------------------- | -------- |
| `@v0.1.0` (a **tag**) | Exactly that release, frozen. Never moves.           | **Default.** Reproducible builds; you upgrade on purpose. |
| `@main` (a **branch**)| Whatever `main` pointed to **when you last locked**. | You want to track the latest and re-lock often. |
| `@<commit-sha>`       | One exact commit.                                    | Pinning to an unreleased fix. |

> **Pick the newest tag, not `v0.1.0` by rote.** The examples below use
> `v0.1.0` because it's the current release — check the
> [tags](https://github.com/mojo5000/blockhead-clikit/tags) (or run
> `git ls-remote --tags origin`) and use the latest, so you don't accidentally
> pin an old version copied from these docs.

```toml
# in a consumer's pyproject.toml — pin a specific release tag
[project]
dependencies = [
    "blockhead-clikit @ git+ssh://git@github.com/mojo5000/blockhead-clikit@v0.1.0",
]
```

```bash
# or add it directly
uv add "blockhead-clikit @ git+ssh://git@github.com/mojo5000/blockhead-clikit@v0.1.0"
```

**Tag vs. branch when updating.** A tag is frozen, so a change here can't
silently break every project at once — each consumer upgrades on purpose:

```bash
# tracking a TAG: bump the tag in pyproject.toml (e.g. v0.1.0 → v0.2.0), then
uv lock --upgrade-package blockhead-clikit

# tracking a BRANCH (@main): the URL doesn't change; re-lock to pull the
# latest commit on that branch
uv lock --upgrade-package blockhead-clikit
```

With `@main`, the pinning lives in your `uv.lock` (the exact commit), so builds
stay reproducible until you re-lock — but a plain `uv sync` on a fresh checkout
will fetch whatever the lock recorded, not necessarily today's `main`.

Consumers needing the Django bridge (`cli_kit.django_cmd`) add the `django`
extra (Django is imported lazily, so only these consumers pull it in):

```bash
uv add "blockhead-clikit[django] @ git+ssh://git@github.com/mojo5000/blockhead-clikit@v0.1.0"
```

## Quick start

This runs as-is — it depends only on `cli_kit` and the standard library, so you
can copy it into a file and `python that_file.py`:

```python
import time

from cli_kit import Menu, ui, use_theme

use_theme("blockhead")  # or "clay", "zigablocks", "mono"

def configure():
    with ui.status("Configuring…"):   # themed spinner
        time.sleep(2)
    ui.success("Configuration complete.")

menu = Menu("My App")
menu.add("Configure", configure, shortcut="c")
menu.run()
```

For a fuller, ready-to-run example with **Configure / Run / Deploy** actions,
see [`samples/menu_app.py`](samples/menu_app.py):

```bash
uv run python samples/menu_app.py
```

To shell out to another process instead of sleeping, use `sh.run`, which gives
you the same themed spinner around a real command:

```python
from cli_kit import sh

# spinner shows while the command runs; capture=True collects its output
sh.run(["git", "pull"], spinner="Updating…", capture=True, check=True)
```

## What you get

- **`theme`** — swappable presets (`blockhead`, `clay`, `zigablocks`, `mono`);
  register your own via `register_theme()`.
- **`ui`** — `banner`, `success`/`error`/`warn`/`info`, `kv`, `panel`, `table`, `badge`.
- **`prompts`** — themed `text`/`confirm`/`select`/`multiselect`/`number`/`path`
  + `validators`, plus a tty-aware `resolve` contract (value-supplied →
  short-circuit; missing + no tty + required → error naming the flag).
- **`sh.run(...)`** — subprocess with echo, spinner, `dry_run`, typed `CommandFailed`.
- **`Menu`** — persistent nav loop: back-nav, breadcrumb, remember-last,
  error failsafe, shortcuts, destructive confirms, type-to-filter search.
- **`registry.expose`** — one plain callable becomes both a click command and a
  menu item, killing menu/command drift.
- **`django_cmd.ActionCommand`** — subclass to get a `manage.py` command
  (Django imported lazily; only needed with the `django` extra).

See [`cli_kit/README.md`](cli_kit/README.md) for the full API and design notes.

## Develop

```bash
uv sync            # install runtime + dev deps
uv run pytest      # run the suite
```
