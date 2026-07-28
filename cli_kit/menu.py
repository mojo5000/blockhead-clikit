"""Menu tree + navigation loop.

The nav loop (Task 10) guarantees the 7 must-haves: back nav, error failsafe,
consistent error display, abort handling, shortcuts, spinner (via sh), and
destructive confirms.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from cli_kit import prompts, ui
from cli_kit.errors import Aborted

BACK = "__back__"
QUIT = "__quit__"


@dataclass
class MenuItem:
    label: str
    action: Callable[[], Any]
    shortcut: str | None = None
    destructive: bool = False

    def display_label(self) -> str:
        """The label as shown in the menu, with the shortcut key marked.

        When a ``shortcut`` letter appears in the label (case-insensitively),
        that first occurrence is wrapped in parens so the accelerator is
        visible in-line — ``"Configure"`` with ``shortcut="c"`` renders as
        ``"(C)onfigure"``. If the letter isn't in the label, the shortcut is
        appended as a ``(c)`` suffix so it's still discoverable. Items without
        a shortcut render their label unchanged.
        """
        if not self.shortcut:
            return self.label
        key = self.shortcut
        idx = self.label.lower().find(key.lower())
        if idx == -1:
            return f"{self.label} ({key})"
        matched = self.label[idx]
        return f"{self.label[:idx]}({matched}){self.label[idx + 1 :]}"


class Menu:
    def __init__(self, title: str, *, search: bool = False) -> None:
        self.title = title
        self._search = search
        self._last_choice: str | None = None
        self._items: list[MenuItem] = []
        self._submenus: dict[str, Menu] = {}
        self._shortcuts: set[str] = set()

    def add(
        self,
        label: str,
        action: Callable[[], Any],
        *,
        shortcut: str | None = None,
        destructive: bool = False,
    ) -> None:
        if shortcut is not None:
            if shortcut in self._shortcuts:
                raise ValueError(f"duplicate shortcut '{shortcut}' in menu '{self.title}'")
            self._shortcuts.add(shortcut)
        self._items.append(MenuItem(label, action, shortcut, destructive))

    def group(self, title: str, *, search: bool = False) -> Menu:
        submenu = Menu(title, search=search)
        self._submenus[title] = submenu
        return submenu

    def items(self) -> list[MenuItem]:
        return list(self._items)

    def submenus(self) -> dict[str, Menu]:
        return dict(self._submenus)

    def _default_choose(self, menu: Menu, path: list[str]) -> str:
        # The prompt message *is* the breadcrumb trail (app › group › …), so the
        # name appears once — not duplicated by a separate breadcrumb line above
        # questionary's own prompt. `>` replaces the default `?` marker.
        #
        # ESC aborts any level (→ Aborted → up a level, or quit at the top). At
        # the top level a plain `q` also quits, matching the visible "Quit"
        # item — but only when this menu isn't a type-to-filter menu, where `q`
        # is a search character.
        at_top = menu is self
        labels = [i.display_label() for i in menu._items]
        labels += [f"▸ {name}" for name in menu._submenus]
        labels.append("Quit" if at_top else "← Back")
        # Pressing an item's shortcut jumps straight to it: map the key to the
        # displayed label so the return value flows through _resolve_item like
        # any arrowed-to choice.
        shortcuts = {item.shortcut: item.display_label() for item in menu._items if item.shortcut}
        choice = prompts.select(
            " › ".join(path),
            choices=labels,
            default=menu._last_choice,
            search=menu._search,
            qmark=">",
            quit_key=at_top and not menu._search,
            shortcuts=shortcuts,
        )
        if choice in ("← Back", "Quit"):
            return QUIT if at_top else BACK
        return str(choice)

    def run(
        self,
        *,
        _choose: Callable[[Menu, list[str]], str] | None = None,
        _confirm: Callable[[str], bool] | None = None,
    ) -> None:
        choose = _choose or self._default_choose
        confirm = _confirm or (lambda msg: prompts.confirm(msg, default=False))
        self._loop(self, choose, confirm, [self.title])

    def _loop(
        self,
        menu: Menu,
        choose: Callable[[Menu, list[str]], str],
        confirm: Callable[[str], bool],
        path: list[str],
    ) -> None:
        while True:
            try:
                choice = choose(menu, path)
            except Aborted:
                # ESC / Ctrl-C at a menu prompt = leave this level: pop up to
                # the parent menu, or quit when we're already at the top.
                return
            if choice == QUIT:
                return
            if choice == BACK:
                return
            submenu = menu._resolve_submenu(choice)
            if submenu is not None:
                # Only remember choices that resolve — an unresolvable label
                # must never become `default=` for questionary's select,
                # which raises ValueError if default isn't in `choices`.
                menu._last_choice = choice
                self._loop(submenu, choose, confirm, path + [submenu.title])
                continue
            item = menu._resolve_item(choice)
            if item is None:
                continue
            menu._last_choice = choice
            self._invoke(item, confirm)

    def _resolve_submenu(self, choice: str) -> Menu | None:
        name = choice[2:] if choice.startswith("▸ ") else choice
        return self._submenus.get(name)

    def _resolve_item(self, choice: str) -> MenuItem | None:
        # `choice` is the *displayed* label (which may carry the shortcut
        # marker, e.g. "(C)onfigure"), so match on display_label(), falling
        # back to the raw label for choosers that bypass the marker.
        for item in self._items:
            if choice in (item.display_label(), item.label):
                return item
        return None

    def _invoke(self, item: MenuItem, confirm: Callable[[str], bool]) -> None:
        try:
            if item.destructive and not confirm(f"{item.label}: are you sure?"):
                return
            item.action()
        except Aborted:
            return  # abort mid-action = quietly return to the menu
        except Exception as exc:  # noqa: BLE001 — the failsafe: never let the app die
            ui.error(str(exc))
