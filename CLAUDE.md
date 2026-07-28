# CLAUDE.md

Guidance for working in **blockhead-clikit** — a reusable click + rich +
questionary CLI framework. Distributable name: `blockhead-clikit`; import name:
`cli_kit` (kept stable — never rename it).

## Core model: action → adapter

An **action** is a plain callable that does the work and knows nothing about how
it's invoked. Each surface (click command, menu item, Django management command)
is a thin **adapter**.

- Wire one action into both the CLI and the menu with `expose(action, cli=...,
  menu=(menu, "Label", "Group"))`. Prefer this over hand-writing the same action
  into two surfaces — divergence between menu and CLI is the bug this prevents.
- `cli_command(group, action)` derives click params from the action's signature:
  no default → `Argument`; `bool` default → `--x/--no-x`; else → `--x` option.
- Only drop to explicit wiring (`menu.add(...)`, `cli_command(...)`) for cases
  that genuinely diverge (menu-only composites, CLI-only commands).

## Layering — never import upward

    theme ← ui ← prompts ← menu    (sh & registry depend on ui only)

A lower layer must not import a higher one. If `prompts` needs something from
`menu`, the design is wrong — push the shared piece down.

## Cancellation contract

Every `prompts.*` wrapper raises `Aborted` when the user cancels (Ctrl-C / ESC /
Backspace). The menu loop catches it and treats it as "go back / quit" — so:

- **Do not** catch `Aborted` inside an action to keep going; let it propagate.
- `Aborted` and `CommandFailed` are the stable public exception names. Do not
  rename them to `*Error` (ruff's N818 is ignored on purpose for this reason).

## Menu specifics

- Shortcuts are **per-menu**: the same key may be reused in a different submenu,
  but is unique within one menu (duplicate → `ValueError` at `add` time).
- Shortcuts are functional hotkeys and render inline in the label
  (`shortcut="c"` on `"Configure"` → `(C)onfigure`, and pressing `c` selects it).
  The wiring lives in `prompts.select(..., shortcuts=...)`; keep the display
  label and the hotkey map in sync (see `MenuItem.display_label`).
- Reserved keys: `q`/`Q` (quit) and Backspace (back) are owned by the nav loop;
  a shortcut on a reserved key is skipped, and shortcuts are ignored in a
  `search=True` menu (there the char is filter text).

## Non-interactive / TTY

The themed prompts assume a TTY. For code that must also run without one (CI,
pipes), gate input through `prompts.resolve(...)` / `confirm_or_yes(...)`, which
are Click-free and raise `InputRequired` (mapped to a click `UsageError` by the
registry adapter) instead of hanging.

## Themes

Built-in presets: `zigablocks` (default active), `blockhead`, `clay`, `mono`.
`use_theme("clay")` switches at runtime; every `ui`/`prompts` call reads the
active theme at render time. Add your own with `register_theme(Theme(...))`.

## Dev workflow

```bash
uv sync --all-extras     # runtime + dev deps + django extra
uv run pytest            # suite (testpaths = cli_kit/tests)
uv run pytest --cov      # with coverage
uv run ruff check .      # lint  (line-length 100; S=bandit, T20=no print)
uv run ruff format .     # format
uv run mypy cli_kit      # types (PEP 561; keep annotations honest)
```

Conventions the linter enforces, worth knowing before you write code:

- **Line length 100.**
- **No `print`** in library code (`T20`) — use `ui.*` (`success`/`error`/`info`
  /`warn`) or `ui.console`.
- **Match the surrounding style** — comment density, docstring voice, and naming
  in this repo are deliberate; mirror the file you're editing.

## Where things live

- `cli_kit/menu.py` — menu tree + nav loop
- `cli_kit/registry.py` — `expose` / `cli_command` (the click adapter)
- `cli_kit/prompts/` — questionary wrappers + `resolve` contract + validators
- `cli_kit/theme/` — presets + active-theme registry
- `cli_kit/ui/` — rich components (banner, status, feedback, layout, report)
- `cli_kit/sh.py` — subprocess helper (`sh.run`)
- `cli_kit/django_cmd.py` — `ActionCommand` bridge (Django imported lazily)
- `examples/menu_app.py` — the runnable, dual-surface example
- `cli_kit/README.md` — full API + design notes
