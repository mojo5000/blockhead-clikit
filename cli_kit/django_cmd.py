"""Bridge: expose an action as a Django management command.

Django is imported lazily so `import cli_kit` never requires Django. Only code
that actually subclasses ActionCommand (inside a Django app) pays for Django.
"""

from __future__ import annotations

from collections.abc import Callable

from cli_kit.errors import CommandFailed
from cli_kit.signature import params_of


def _base_command():
    from django.core.management.base import BaseCommand  # lazy import

    return BaseCommand


class _ActionCommandMeta(type):
    """Build the class with Django's BaseCommand as a base, lazily."""

    def __new__(mcs, name, bases, namespace):
        if name == "ActionCommand":
            return super().__new__(mcs, name, bases, namespace)
        base = _base_command()
        # Include methods and attributes from ActionCommand in the namespace
        for attr in ["action", "add_arguments", "handle"]:
            if attr not in namespace and hasattr(ActionCommand, attr):
                namespace[attr] = getattr(ActionCommand, attr)
        return type(name, (base,), namespace)


class ActionCommand(metaclass=_ActionCommandMeta):
    action: Callable | None = None

    def add_arguments(self, parser) -> None:
        if self.action is None:
            return
        for spec in params_of(self.action):
            if spec.has_default:
                if isinstance(spec.default, bool):
                    parser.add_argument(
                        f"--{spec.name.replace('_', '-')}",
                        dest=spec.name,
                        action="store_true",
                        default=spec.default,
                    )
                else:
                    parser.add_argument(
                        f"--{spec.name.replace('_', '-')}",
                        dest=spec.name,
                        default=spec.default,
                    )
            else:
                parser.add_argument(spec.name)

    def handle(self, *args, **options) -> None:
        from cli_kit import ui

        if self.action is None:
            raise NotImplementedError("ActionCommand subclass must set `action`")
        wanted = {s.name for s in params_of(self.action)}
        kwargs = {k: v for k, v in options.items() if k in wanted}
        try:
            self.action(**kwargs)
        except CommandFailed as exc:
            ui.error(str(exc))
            raise SystemExit(exc.returncode) from exc
        except Exception as exc:  # noqa: BLE001 — surface consistently, then exit non-zero
            ui.error(str(exc))
            raise SystemExit(1) from exc
