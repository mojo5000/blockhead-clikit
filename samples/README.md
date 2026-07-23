# Samples

Runnable examples built with `blockhead-clikit` itself.

## `menu_app.py`

A minimal menu with three actions — **Configure**, **Run**, **Deploy** — each
showing a themed spinner for a few seconds and then a success message. It
depends on nothing but the library and the standard library, so it runs
anywhere `blockhead-clikit` is installed.

```bash
# from a checkout of this repo (deps already synced via `uv sync`)
uv run python samples/menu_app.py

# or, if you've installed blockhead-clikit into your own environment
python samples/menu_app.py
```

Use ↑/↓ (or the `c` / `r` / `d` shortcuts) to pick an action. Ctrl-C at the
menu quits; Ctrl-C during an action returns you to the menu.
