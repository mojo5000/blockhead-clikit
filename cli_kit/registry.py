"""Action → surface adapters. cli_command builds a click command; expose is
the 1:1 convenience wiring both click and menu from one call.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import click

from cli_kit.errors import InputRequired
from cli_kit.menu import Menu
from cli_kit.signature import params_of


def cli_command(group: click.Group, action: Callable, *, name: str | None = None) -> click.Command:
    cmd_name = name or action.__name__.replace("_", "-")
    params: list[click.Parameter] = []
    for spec in params_of(action):
        if not spec.has_default:
            params.append(click.Argument([spec.name]))
        elif isinstance(spec.default, bool):
            flag = f"--{spec.name.replace('_', '-')}/--no-{spec.name.replace('_', '-')}"
            params.append(click.Option([flag], default=spec.default))
        else:
            params.append(click.Option([f"--{spec.name.replace('_', '-')}"], default=spec.default))

    def callback(**kwargs: Any) -> Any:
        # Translate cli_kit's surface-agnostic InputRequired into Click's own
        # error so a missing required input on a non-tty stdin exits 2 with a
        # usage message instead of an uncaught traceback. cli_kit.prompts stays
        # Click-free; the mapping lives here, in the Click adapter.
        try:
            return action(**kwargs)
        except InputRequired as exc:
            raise click.UsageError(str(exc)) from exc

    command = click.Command(cmd_name, params=params, callback=callback, help=action.__doc__)
    group.add_command(command)
    return command


def expose(
    action: Callable,
    *,
    cli: click.Group | None = None,
    menu: tuple | None = None,
    name: str | None = None,
) -> None:
    if cli is not None:
        cli_command(cli, action, name=name)
    if menu is not None:
        menu_obj: Menu = menu[0]
        label: str = menu[1]
        if len(menu) >= 3:
            group_title: str = menu[2]
            existing = menu_obj.submenus().get(group_title)
            target = existing if existing is not None else menu_obj.group(group_title)
        else:
            target = menu_obj
        target.add(label, action)
