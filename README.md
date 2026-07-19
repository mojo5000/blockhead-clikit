# blockhead-clikit

A small, reusable **click + rich + questionary** framework for building smooth
Python CLIs — themed prompts, a persistent menu tree, subprocess helpers, and a
Django management-command bridge.

The distributable package is **`blockhead-clikit`**; the import name is
**`cli_kit`** (kept stable so existing `from cli_kit import …` code needs no
changes).

## Install

This is a private git dependency — depend on it by URL (no package index needed).
`uv` uses your existing git credentials, so a private repo works exactly like a
public one as long as you can `git clone` it.

```toml
# in a consumer's pyproject.toml
[project]
dependencies = [
    "blockhead-clikit @ git+ssh://git@github.com/mojo5000/blockhead-clikit@v0.1.0",
]
```

```bash
# or add it directly
uv add "blockhead-clikit @ git+ssh://git@github.com/mojo5000/blockhead-clikit@v0.1.0"

# updating later: bump the tag, then
uv lock --upgrade-package blockhead-clikit
```

Each consumer **pins a tag/commit**, so a change here can't silently break every
project at once — you bump each one when you're ready. Consumers needing the
Django bridge (`cli_kit.django_cmd`) add the `django` extra:
`blockhead-clikit[django] @ git+…`.

## Quick start

```python
from cli_kit import ui, prompts, sh, Menu, use_theme, expose

use_theme("blockhead")  # or "clay", "zigablocks", "mono"

def seed():
    sh.run(["python", "create_sample_data.py"], spinner="seeding", capture=True)
    ui.success("seeded")

menu = Menu("My App")
menu.add("Seed data", seed, shortcut="s")
menu.run()
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
