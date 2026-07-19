# cli_kit

A reusable click + rich + questionary CLI framework. `cp -r` this folder into any
Python project. **No Django required** (the `django_cmd` bridge imports Django lazily).

## Core idea

An **action** is a plain callable that does the work. Every way of invoking it —
click command, interactive menu item, Django management command — is a thin **adapter**.

    def migrate(force: bool = False) -> int:      # the action — knows nothing about surfaces
        return sh.run(["python", "manage.py", "migrate"]).returncode

    expose(migrate, cli=cli, menu=(menu, "Migrate", "Django"))   # 1:1 sugar → both surfaces

For divergent cases, wire surfaces explicitly:

    cli_command(cli, migrate)                       # CLI only
    menu.add("Full reset", lambda: (down(), up()))  # menu-only composite

## What you get

- `theme` — swappable presets (`zigablocks`, `blockhead`, `mono`). `use_theme("mono")`.
- `ui` — `banner`, `success`/`error`/`warn`/`info`, `kv`, `panel`, `table`, `badge`.
- `prompts` — themed `text`/`confirm`/`select`/`multiselect`/`number`/`path` + `validators`.
  Cancelling raises `Aborted` (the menu treats it as "go back").
- `sh.run(...)` — subprocess with echo, spinner, `dry_run`, and typed `CommandFailed`.
- `Menu` — persistent nav loop guaranteeing: back nav, error failsafe (an action error
  returns you to the menu, never kills the app), consistent error display, abort
  handling, shortcut keys, spinners, destructive confirms.
- `django_cmd.ActionCommand` — subclass, set `action`, get a `manage.py` command.

## Quick start

    from cli_kit import ui, prompts, sh, Menu, use_theme, expose

    use_theme("blockhead")

    def seed():
        sh.run(["python", "create_sample_data.py"], spinner="seeding", capture=True)
        ui.success("seeded")

    menu = Menu("My App")
    menu.add("Seed data", seed, shortcut="s")
    menu.run()

## Menu extras

    menu = Menu("Main", search=True)                 # type-to-filter this menu
    django = menu.group("Django", search=True)        # …and any submenu, independently

- **Search** — `Menu(search=True)` / `menu.group(..., search=True)` opt a menu into
  type-to-filter (questionary's `use_search_filter`). Off by default; turn it on for
  menus long enough that scanning beats scrolling.
- **Breadcrumb** — the nav loop prints a dim `Main › Django` trail above every prompt
  automatically, so you always know where you are in the tree. No wiring required.
- **Remember-last** — a menu reopens with the previously chosen item preselected.
  Back/Quit are never remembered, and a choice that no longer resolves (e.g. items
  changed since last visit) is dropped rather than fed back into `default=`.
- **Wrap-around & long menus** — arrowing past the last item wraps to the first (and
  vice versa), and menus longer than the terminal scroll — both are questionary's
  native behavior, not something `cli_kit` reimplements. There's no separate paging
  knob; `search=True` is the intended "find it fast" answer for long menus.

## Adding a theme

    from cli_kit import Theme, register_theme
    register_theme(Theme(name="mine", accent="blue", ...))
    use_theme("mine")

## Layering (do not import upward)

    theme ← ui ← prompts ← menu ;  sh & registry depend on ui only.
