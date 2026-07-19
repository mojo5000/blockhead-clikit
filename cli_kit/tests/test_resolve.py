"""Tests for the resolve / confirm_or_yes interactive/non-interactive contract.

Ported from blockhead's ``test_prompts.py`` and adapted to cli_kit: the errors
are cli_kit-native (``InputRequired``, not ``click.UsageError``), and the
interactive path is mocked at the themed-wrapper ``_build`` layer the way
``test_prompts.py`` already does, so theming and the ``Aborted``-on-cancel
funnel stay exercised.
"""

import pytest

from cli_kit import prompts
from cli_kit.errors import Aborted, InputRequired


class _FakeQuestion:
    def __init__(self, answer):
        self._answer = answer

    def ask(self):
        return self._answer


# --- resolve() -------------------------------------------------------------


def test_resolve_returns_supplied_value_unchanged():
    """If a value was supplied (e.g. --flag), no prompt should fire."""
    assert prompts.resolve("hello", prompt="x", flag_name="x") == "hello"


def test_resolve_treats_empty_string_as_missing(monkeypatch):
    monkeypatch.setattr(prompts.resolve_mod, "is_interactive", lambda: False)
    assert prompts.resolve("", prompt="x", required=False, default="fb", flag_name="x") == "fb"


def test_resolve_non_tty_required_raises_naming_flag(monkeypatch):
    monkeypatch.setattr(prompts.resolve_mod, "is_interactive", lambda: False)
    with pytest.raises(InputRequired) as excinfo:
        prompts.resolve(None, prompt="Workspace name:", flag_name="name")
    assert "--name" in str(excinfo.value)
    assert "Workspace name:" in str(excinfo.value)
    assert excinfo.value.flag == "--name"


def test_resolve_non_tty_required_underscore_flag_is_hyphenated(monkeypatch):
    monkeypatch.setattr(prompts.resolve_mod, "is_interactive", lambda: False)
    with pytest.raises(InputRequired) as excinfo:
        prompts.resolve(None, prompt="x", flag_name="repo_path")
    assert "--repo-path" in str(excinfo.value)


def test_resolve_input_required_is_aborted_subclass():
    # Menu failsafe treats Aborted as "go back"; InputRequired must inherit it.
    assert issubclass(InputRequired, Aborted)


def test_resolve_non_tty_optional_returns_default(monkeypatch):
    monkeypatch.setattr(prompts.resolve_mod, "is_interactive", lambda: False)
    assert (
        prompts.resolve(None, prompt="x", required=False, default="fallback", flag_name="x")
        == "fallback"
    )


def test_resolve_interactive_prompts_via_text(monkeypatch):
    monkeypatch.setattr(prompts.resolve_mod, "is_interactive", lambda: True)
    monkeypatch.setattr(prompts.text_mod, "_build", lambda **kw: _FakeQuestion("user-typed"))
    assert prompts.resolve(None, prompt="enter:", flag_name="name") == "user-typed"


def test_resolve_interactive_ctrl_c_raises_aborted(monkeypatch):
    # The themed text wrapper converts questionary's None (Ctrl-C) into Aborted.
    monkeypatch.setattr(prompts.resolve_mod, "is_interactive", lambda: True)
    monkeypatch.setattr(prompts.text_mod, "_build", lambda **kw: _FakeQuestion(None))
    with pytest.raises(Aborted):
        prompts.resolve(None, prompt="x", flag_name="x")


def test_resolve_interactive_forwards_default_and_validate(monkeypatch):
    monkeypatch.setattr(prompts.resolve_mod, "is_interactive", lambda: True)
    captured = {}

    def fake_build(**kw):
        captured.update(kw)
        return _FakeQuestion("ok")

    monkeypatch.setattr(prompts.text_mod, "_build", fake_build)
    validator = lambda v: True  # noqa: E731
    prompts.resolve(None, prompt="enter:", default="my-default", validate=validator, flag_name="x")
    assert captured["message"] == "enter:"
    assert captured["default"] == "my-default"
    assert captured["validate"] is validator


def test_resolve_interactive_with_choices_uses_select(monkeypatch):
    monkeypatch.setattr(prompts.resolve_mod, "is_interactive", lambda: True)
    captured = {}

    def fake_build(**kw):
        captured.update(kw)
        return _FakeQuestion("B")

    monkeypatch.setattr(prompts.select_mod, "_build_select", fake_build)
    result = prompts.resolve(None, prompt="Pick", choices=["A", "B"], default="B", flag_name="x")
    assert result == "B"
    assert captured["choices"] == ["A", "B"]
    assert captured["default"] == "B"


# --- confirm_or_yes() ------------------------------------------------------


def test_confirm_or_yes_with_yes_flag_returns_true_without_prompt():
    assert prompts.confirm_or_yes(True, prompt="really?") is True


def test_confirm_or_yes_non_tty_without_flag_raises(monkeypatch):
    monkeypatch.setattr(prompts.resolve_mod, "is_interactive", lambda: False)
    with pytest.raises(InputRequired) as excinfo:
        prompts.confirm_or_yes(False, prompt="Destroy?")
    assert "--yes" in str(excinfo.value)
    assert excinfo.value.flag == "--yes"


def test_confirm_or_yes_interactive_returns_user_answer(monkeypatch):
    monkeypatch.setattr(prompts.resolve_mod, "is_interactive", lambda: True)
    monkeypatch.setattr(prompts.confirm_mod, "_build", lambda **kw: _FakeQuestion(True))
    assert prompts.confirm_or_yes(False, prompt="ok?") is True


def test_confirm_or_yes_interactive_ctrl_c_aborts(monkeypatch):
    monkeypatch.setattr(prompts.resolve_mod, "is_interactive", lambda: True)
    monkeypatch.setattr(prompts.confirm_mod, "_build", lambda **kw: _FakeQuestion(None))
    with pytest.raises(Aborted):
        prompts.confirm_or_yes(False, prompt="ok?")


def test_confirm_or_yes_danger_forces_default_false(monkeypatch):
    monkeypatch.setattr(prompts.resolve_mod, "is_interactive", lambda: True)
    captured = {}

    def fake_build(**kw):
        captured.update(kw)
        return _FakeQuestion(False)

    monkeypatch.setattr(prompts.confirm_mod, "_build", fake_build)
    prompts.confirm_or_yes(False, prompt="Destroy?", default=True, danger=True)
    assert captured["default"] is False
