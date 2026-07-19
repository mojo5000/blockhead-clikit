import pytest

from cli_kit import ui
from cli_kit.theme import theme, use_theme


@pytest.fixture(autouse=True)
def _reset_theme():
    use_theme("zigablocks")
    yield
    use_theme("zigablocks")


def test_success_includes_ok_symbol_and_message():
    with ui.console.capture() as cap:
        ui.success("migrated")
    out = cap.get()
    assert theme().ok in out
    assert "migrated" in out


def test_error_includes_fail_symbol_and_message():
    with ui.console.capture() as cap:
        ui.error("port in use")
    out = cap.get()
    assert theme().fail in out
    assert "port in use" in out


def test_mono_theme_error_uses_ascii_symbol():
    use_theme("mono")
    with ui.console.capture() as cap:
        ui.error("boom")
    assert "[x]" in cap.get()


def test_breadcrumb_joins_path():
    with ui.console.capture() as cap:
        ui.breadcrumb(["Main", "Django", "Migrations"])
    out = cap.get()
    assert "Main › Django › Migrations" in out


def test_breadcrumb_empty_prints_nothing():
    with ui.console.capture() as cap:
        ui.breadcrumb([])
    assert cap.get() == ""
