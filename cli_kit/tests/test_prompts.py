import pytest

from cli_kit import prompts
from cli_kit.errors import Aborted


class _FakeQuestion:
    def __init__(self, answer):
        self._answer = answer

    def ask(self):
        return self._answer


def test_text_returns_answer(monkeypatch):
    monkeypatch.setattr(prompts.text_mod, "_build", lambda **kw: _FakeQuestion("Blocks"))
    assert prompts.text("App name") == "Blocks"


def test_abort_raises_aborted(monkeypatch):
    # questionary returns None on Ctrl-C; wrapper must convert to Aborted.
    monkeypatch.setattr(prompts.text_mod, "_build", lambda **kw: _FakeQuestion(None))
    with pytest.raises(Aborted):
        prompts.text("App name")


def test_text_and_confirm_use_themed_qmark(monkeypatch):
    # text/confirm don't expose qmark, but must still carry the active theme's
    # marker down to questionary (so the marker is consistent across prompt kinds).
    from cli_kit.theme import theme

    captured = {}

    def fake_build(**kw):
        captured.update(kw)
        return _FakeQuestion("x")

    monkeypatch.setattr(prompts.text_mod, "_build", fake_build)
    prompts.text("Name")
    assert captured["qmark"] == theme().qmark

    captured.clear()

    def fake_confirm(**kw):
        captured.update(kw)
        return _FakeQuestion(True)

    monkeypatch.setattr(prompts.confirm_mod, "_build", fake_confirm)
    prompts.confirm("Sure?")
    assert captured["qmark"] == theme().qmark


def test_number_rejects_out_of_range(monkeypatch):
    monkeypatch.setattr(prompts.number_mod, "_build", lambda **kw: _FakeQuestion("70000"))
    with pytest.raises(ValueError):
        prompts.number("Port", min=1, max=65535)


def test_number_returns_int(monkeypatch):
    monkeypatch.setattr(prompts.number_mod, "_build", lambda **kw: _FakeQuestion("8000"))
    assert prompts.number("Port", min=1, max=65535) == 8000


def test_select_forwards_default(monkeypatch):
    captured = {}

    def fake_build(**kw):
        captured.update(kw)
        return _FakeQuestion("A")

    monkeypatch.setattr(prompts.select_mod, "_build_select", fake_build)
    prompts.select("Pick", choices=["A", "B"], default="B")
    assert captured["default"] == "B"


def test_select_qmark_defaults_to_active_theme(monkeypatch):
    """With no explicit qmark, select uses the active theme's marker; an explicit
    qmark still overrides it per call."""
    from cli_kit.theme import theme

    captured = {}

    def fake_build(**kw):
        captured.update(kw)
        return _FakeQuestion("A")

    monkeypatch.setattr(prompts.select_mod, "_build_select", fake_build)
    prompts.select("Pick", choices=["A", "B"])
    assert captured["qmark"] == theme().qmark  # theme-driven default
    prompts.select("Pick", choices=["A", "B"], qmark="?")
    assert captured["qmark"] == "?"  # explicit override wins


def test_select_search_flag_maps_to_questionary(monkeypatch):
    captured = {}

    def fake_build(**kw):
        captured.update(kw)
        return _FakeQuestion("A")

    monkeypatch.setattr(prompts.select_mod, "_build_select", fake_build)
    prompts.select("Pick", choices=["A", "B"], search=True)
    assert captured["use_search_filter"] is True


def test_select_search_defaults_off(monkeypatch):
    captured = {}

    def fake_build(**kw):
        captured.update(kw)
        return _FakeQuestion("A")

    monkeypatch.setattr(prompts.select_mod, "_build_select", fake_build)
    prompts.select("Pick", choices=["A", "B"])
    assert captured["use_search_filter"] is False


def test_select_search_disables_jk_keys(monkeypatch):
    # questionary raises ValueError if j/k nav is left on while search is active.
    captured = {}

    def fake_build(**kw):
        captured.update(kw)
        return _FakeQuestion("A")

    monkeypatch.setattr(prompts.select_mod, "_build_select", fake_build)
    prompts.select("Pick", choices=["A", "B"], search=True)
    assert captured["use_jk_keys"] is False


def test_select_search_keeps_jk_keys_when_off(monkeypatch):
    captured = {}

    def fake_build(**kw):
        captured.update(kw)
        return _FakeQuestion("A")

    monkeypatch.setattr(prompts.select_mod, "_build_select", fake_build)
    prompts.select("Pick", choices=["A", "B"])
    assert captured["use_jk_keys"] is True


def test_select_choice_maps_title_and_value(monkeypatch):
    # Choice(title, value): the displayed title differs from the returned value.
    # Verify _build_select receives questionary.Choice objects carrying both.
    import questionary

    captured = {}

    def fake_build(**kw):
        captured.update(kw)
        # simulate the user picking the first option's *value*
        return _FakeQuestion(kw["choices"][0].value)

    monkeypatch.setattr(prompts.select_mod, "_build_select", fake_build)
    result = prompts.select(
        "Pick",
        choices=[prompts.Choice("admin (agent)", "admin"), prompts.Choice("bot (agent)", "bot")],
    )
    assert result == "admin"
    forwarded = captured["choices"]
    assert all(isinstance(c, questionary.Choice) for c in forwarded)


def test_select_mixed_str_and_choice(monkeypatch):
    # Plain strings and Choice objects can coexist in one choices list.
    def fake_build(**kw):
        return _FakeQuestion(kw["choices"][0])  # the plain string passes through untouched

    monkeypatch.setattr(prompts.select_mod, "_build_select", fake_build)
    result = prompts.select("Pick", choices=["plain", prompts.Choice("Labelled", 42)])
    assert result == "plain"


def test_select_choice_value_can_be_nonstring(monkeypatch):
    def fake_build(**kw):
        return _FakeQuestion(kw["choices"][0].value)

    monkeypatch.setattr(prompts.select_mod, "_build_select", fake_build)
    result = prompts.select("Pick", choices=[prompts.Choice("id 7", 7)])
    assert result == 7


def test_select_with_search_builds_real_questionary():
    # Regression: the interactive menu crashed because search=True was passed
    # to questionary without disabling j/k nav. Exercise the real builder (no
    # monkeypatch of _build_select) so an incompatible kwarg combo raises here.
    prompts.select_mod._build_select(
        message="Pick",
        choices=["A", "B"],
        use_search_filter=True,
        use_jk_keys=False,
    )
