# Examples

Runnable examples built with `blockhead-clikit` itself.

## `menu_app.py`

A single file that drives the same actions two ways, showing off the whole
surface:

- **`click` CLI commands** — every action is also a subcommand
  (`greet`, `configure`, `run`, `deploy`, `reset`), wired up with
  `cli_kit.expose` so the CLI and the menu never drift apart.
- **`questionary` input** — `prompts.text`, `prompts.select`, `prompts.number`,
  and `prompts.confirm` collect input interactively when a flag is omitted.
- **Submenus + Back** — a **Settings** submenu you descend into, with
  Backspace / **← Back** to return.
- **Shortcut hotkeys** — items added with `shortcut="c"` render their
  accelerator inline (**(C)onfigure**, **(R)un**, **(D)eploy**), and pressing
  that key jumps straight to the item.
- **The `clay` theme by default** — a warm, Anthropic-ish orange.

It depends on nothing but the library and the standard library, so it runs
anywhere `blockhead-clikit` is installed.

### Run it as a menu

```bash
# from a checkout of this repo (deps already synced via `uv sync`)
uv run python examples/menu_app.py

# or, if you've installed blockhead-clikit into your own environment
python examples/menu_app.py
```

> `uv run` runs a `.py` path as a script, so you can drop `python` —
> `uv run examples/menu_app.py` works the same.

Use ↑/↓ + Enter to pick an item, or press its **shortcut key** (e.g. `c` for
Configure) to jump straight to it. **Backspace** goes back a level (and out of
the **Settings** submenu); **q** quits at the top. Ctrl-C during an action
returns you to the menu.

### Run it as a CLI

Pass a subcommand and it behaves as a plain `click` app — no menu:

```bash
uv run python examples/menu_app.py --help
uv run python examples/menu_app.py greet --name Ada
uv run python examples/menu_app.py configure --env staging
uv run python examples/menu_app.py deploy --replicas 2
```

Omit a flag and the interactive prompt fills it in — e.g. `greet` with no
`--name` asks for one via `questionary`.
