from cli_kit.menu import Menu


def _scripted_chooser(sequence):
    """Return a chooser that yields each queued choice in order."""
    calls = iter(sequence)

    def _choose(menu, path):
        return next(calls)

    return _choose


def test_runs_selected_action_then_quits():
    hits = []
    m = Menu("Main")
    m.add("Ping", lambda: hits.append("ping"))
    m.run(_choose=_scripted_chooser(["Ping", "__quit__"]))
    assert hits == ["ping"]


def test_action_exception_does_not_kill_app(capsys):
    hits = []

    def boom():
        raise RuntimeError("kaboom")

    m = Menu("Main")
    m.add("Boom", boom)
    m.add("After", lambda: hits.append("after"))
    # Boom raises, loop must survive and let "After" run next.
    m.run(_choose=_scripted_chooser(["Boom", "After", "__quit__"]))
    assert hits == ["after"]


def test_back_returns_from_submenu():
    hits = []
    m = Menu("Main")
    dj = m.group("Django")
    dj.add("Migrate", lambda: hits.append("migrate"))
    # enter Django, run Migrate, back to main, quit
    m.run(_choose=_scripted_chooser(["Django", "Migrate", "__back__", "__quit__"]))
    assert hits == ["migrate"]


def test_destructive_declined_skips_action():
    hits = []
    m = Menu("Main")
    m.add("Reset", lambda: hits.append("reset"), destructive=True)
    m.run(
        _choose=_scripted_chooser(["Reset", "__quit__"]),
        _confirm=lambda msg: False,  # user declines
    )
    assert hits == []


def test_destructive_confirmed_runs_action():
    hits = []
    m = Menu("Main")
    m.add("Reset", lambda: hits.append("reset"), destructive=True)
    m.run(_choose=_scripted_chooser(["Reset", "__quit__"]), _confirm=lambda msg: True)
    assert hits == ["reset"]


def test_last_choice_becomes_default_on_reopen():
    seen_defaults = []

    def choose(menu, path):
        seen_defaults.append(menu._last_choice)
        # first open: pick B; second open: quit
        return "B" if menu._last_choice is None else "__quit__"

    m = Menu("Main")
    m.add("A", lambda: None)
    m.add("B", lambda: None)
    m.run(_choose=choose)
    # first call default None, second call default "B" (remembered)
    assert seen_defaults == [None, "B"]


def test_back_and_quit_are_not_remembered():
    m = Menu("Main")
    dj = m.group("Django")
    dj.add("Migrate", lambda: None)
    # enter Django, back out, quit
    m.run(_choose=_scripted_chooser(["▸ Django", "__back__", "__quit__"]))
    # Django submenu remembers nothing (only saw Back)
    assert dj._last_choice is None
    # Main remembers the submenu marker it descended into
    assert m._last_choice == "▸ Django"


def test_breadcrumb_path_grows_with_depth():
    seen_paths = []

    def choose(menu, path):
        seen_paths.append(list(path))
        if menu.title == "Main":
            return "▸ Django"
        return "__back__" if menu.title == "Django" else "__quit__"

    m = Menu("Main")
    m.group("Django").add("Migrate", lambda: None)
    # Main → Django → back to Main → quit
    seq = iter(["▸ Django", "__back__", "__quit__"])

    def choose2(menu, path):
        seen_paths.append(list(path))
        return next(seq)

    m.run(_choose=choose2)
    assert ["Main"] in seen_paths
    assert ["Main", "Django"] in seen_paths


def test_unresolvable_choice_is_not_remembered():
    # A custom chooser returning a label that matches neither an item nor a
    # submenu must not poison _last_choice — that value later becomes
    # `default=` for questionary's select, which raises if it isn't a member
    # of `choices`.
    m = Menu("Main")
    m.add("A", lambda: None)
    m.run(_choose=_scripted_chooser(["Bogus Label", "__quit__"]))
    assert m._last_choice is None


def test_search_opt_in_reaches_select(monkeypatch):
    from cli_kit import prompts

    captured = {}

    def fake_select(
        message, *, choices, default=None, search=False, qmark="?", quit_key=False, shortcuts=None
    ):
        captured["search"] = search
        return "__quit__"

    monkeypatch.setattr(prompts, "select", fake_select)
    m = Menu("Main", search=True)
    m.add("A", lambda: None)
    m.run()  # uses _default_choose → real prompts.select (patched)
    assert captured["search"] is True


def test_default_choose_uses_breadcrumb_message_and_arrow_qmark(monkeypatch):
    # The prompt message is the '›'-joined path (name shown once, not doubled by a
    # separate breadcrumb), and the marker is '>' not '?'.
    from cli_kit import prompts

    captured = {}

    def fake_select(
        message, *, choices, default=None, search=False, qmark="?", quit_key=False, shortcuts=None
    ):
        captured["message"] = message
        captured["qmark"] = qmark
        captured["quit_key"] = quit_key
        return "__quit__"

    monkeypatch.setattr(prompts, "select", fake_select)
    m = Menu("grist")
    m.add("A", lambda: None)
    m.run()
    assert captured["message"] == "grist"
    assert captured["qmark"] == ">"


def test_top_level_menu_binds_quit_key(monkeypatch):
    # The top-level menu asks select to bind `q` as a quit shortcut.
    from cli_kit import prompts

    seen = []

    def fake_select(
        message, *, choices, default=None, search=False, qmark="?", quit_key=False, shortcuts=None
    ):
        seen.append((message, quit_key))
        if message == "Main":
            # Descend into Django exactly once so we observe both a top and a
            # sub prompt; on the way back up, quit rather than descend again
            # (otherwise run() loops forever re-entering the submenu).
            descended = any(msg == "Main › Django" for msg, _ in seen)
            return "__quit__" if descended else "▸ Django"
        return "← Back"

    monkeypatch.setattr(prompts, "select", fake_select)
    m = Menu("Main")
    m.group("Django").add("Migrate", lambda: None)
    m.run()
    assert ("Main", True) in seen  # top level → q quits
    assert ("Main › Django", False) in seen  # submenu → q is not bound


def test_default_choose_passes_item_shortcuts(monkeypatch):
    # The menu maps each item's shortcut char to its displayed label so the key
    # jumps straight to that item; items without a shortcut aren't in the map.
    from cli_kit import prompts

    captured = {}

    def fake_select(
        message, *, choices, default=None, search=False, qmark="?", quit_key=False, shortcuts=None
    ):
        captured["shortcuts"] = shortcuts
        return "__quit__"

    monkeypatch.setattr(prompts, "select", fake_select)
    m = Menu("Main")
    m.add("Configure", lambda: None, shortcut="c")
    m.add("Run", lambda: None)  # no shortcut → absent from the map
    m.run()
    assert captured["shortcuts"] == {"c": "(C)onfigure"}


def test_shortcut_keypress_selects_item_in_live_menu():
    # End-to-end: pressing an item's shortcut key runs that item's action.
    from prompt_toolkit.application.current import create_app_session
    from prompt_toolkit.input.defaults import create_pipe_input
    from prompt_toolkit.output import DummyOutput

    hits = []
    m = Menu("Main")
    m.add("Configure", lambda: hits.append("configure"), shortcut="c")
    m.add("Run", lambda: hits.append("run"), shortcut="r")

    with create_pipe_input() as inp:
        with create_app_session(input=inp, output=DummyOutput()):
            inp.send_text("r")  # shortcut → Run
            inp.send_text("q")  # quit
            m.run()
    assert hits == ["run"]


def test_search_menu_does_not_bind_quit_key(monkeypatch):
    # In a type-to-filter menu, `q` is a search character, so it must not be
    # hijacked as a quit shortcut even at the top level.
    from cli_kit import prompts

    captured = {}

    def fake_select(
        message, *, choices, default=None, search=False, qmark="?", quit_key=False, shortcuts=None
    ):
        captured["quit_key"] = quit_key
        return "__quit__"

    monkeypatch.setattr(prompts, "select", fake_select)
    m = Menu("Main", search=True)
    m.add("A", lambda: None)
    m.run()
    assert captured["quit_key"] is False


def test_abort_at_top_level_quits():
    from cli_kit.errors import Aborted

    hits = []

    def choose(menu, path):
        hits.append(menu.title)
        raise Aborted()  # ESC / Ctrl-C at the top prompt

    m = Menu("Main")
    m.add("A", lambda: hits.append("A"))
    m.run(_choose=choose)  # must return, not loop forever
    assert hits == ["Main"]


def test_abort_in_submenu_pops_one_level():
    from cli_kit.errors import Aborted

    calls = iter(["▸ Django", "abort", "__quit__"])

    def choose(menu, path):
        step = next(calls)
        if step == "abort":
            raise Aborted()  # ESC inside Django → back to Main
        return step

    m = Menu("Main")
    m.group("Django").add("Migrate", lambda: None)
    # Reaching the final __quit__ proves the abort popped to Main rather than
    # quitting the whole app.
    m.run(_choose=choose)
