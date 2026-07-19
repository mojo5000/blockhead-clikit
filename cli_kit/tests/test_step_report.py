"""StepReport: accumulation, ok-flips-on-fail, one row per step, theme-driven glyphs."""

import pytest

from cli_kit import ui
from cli_kit.theme import use_theme


@pytest.fixture(autouse=True)
def _reset_theme():
    use_theme("zigablocks")
    yield
    use_theme("zigablocks")


def test_ok_true_with_no_failures():
    report = ui.StepReport("Deployment")
    report.done("Infrastructure")
    report.skip("Frontend", "up to date")
    assert report.ok is True


def test_ok_flips_false_on_any_failure():
    report = ui.StepReport("Deployment")
    report.done("Infrastructure")
    report.fail("Migrations", "connection refused")
    report.done("Frontend")
    assert report.ok is False


def test_empty_report_is_ok_and_renders_nothing():
    report = ui.StepReport("Deployment")
    assert report.ok is True
    with ui.console.capture() as cap:
        report.render()
    assert cap.get() == ""


def test_render_emits_one_row_per_step():
    report = ui.StepReport("Deployment")
    report.done("Infrastructure")
    report.skip("Frontend", "up to date")
    report.fail("Migrations", "connection refused")
    with ui.console.capture() as cap:
        report.render()
    out = cap.get()
    # every step name + detail appears
    assert "Infrastructure" in out
    assert "Frontend" in out
    assert "up to date" in out
    assert "Migrations" in out
    assert "connection refused" in out
    assert "Deployment" in out  # title


def test_glyphs_come_from_theme_zigablocks():
    report = ui.StepReport("Run")
    report.done("A")
    report.skip("B")
    report.fail("C")
    with ui.console.capture() as cap:
        report.render()
    out = cap.get()
    # zigablocks: ok=✓, bullet=•, fail=✗
    assert "✓" in out
    assert "•" in out
    assert "✗" in out


def test_glyphs_reskin_under_mono_no_emoji():
    use_theme("mono")
    report = ui.StepReport("Run")
    report.done("A")
    report.skip("B")
    report.fail("C")
    with ui.console.capture() as cap:
        report.render()
    out = cap.get()
    # mono: ok=[ok], bullet=-, fail=[x]; the emoji/unicode glyphs must NOT leak
    assert "[ok]" in out
    assert "[x]" in out
    assert "✓" not in out
    assert "✗" not in out
    assert "•" not in out


def test_detail_is_optional():
    report = ui.StepReport("Run")
    report.done("NoDetail")
    with ui.console.capture() as cap:
        report.render()
    assert "NoDetail" in cap.get()
