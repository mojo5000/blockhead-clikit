import pytest

from cli_kit import ui
from cli_kit.theme import use_theme


@pytest.fixture(autouse=True)
def _reset_theme():
    use_theme("zigablocks")
    yield
    use_theme("zigablocks")


def test_banner_renders_title_and_subtitle():
    with ui.console.capture() as cap:
        ui.banner("Blocks", subtitle="local dev")
    out = cap.get()
    assert "Blocks" in out
    assert "local dev" in out


def test_kv_renders_keys_and_values():
    with ui.console.capture() as cap:
        ui.kv({"Frontend": "http://localhost:3000", "API": "http://localhost:8000"})
    out = cap.get()
    assert "Frontend" in out
    assert "http://localhost:3000" in out
    assert "API" in out


def test_table_renders_columns_and_rows():
    with ui.console.capture() as cap:
        ui.table([("Web", "up"), ("API", "down")], columns=["Service", "State"])
    out = cap.get()
    assert "Service" in out
    assert "Web" in out
    assert "down" in out


def test_table_plain_cells_are_escaped():
    """A bare string cell containing markup is escaped, not interpreted."""
    with ui.console.capture() as cap:
        ui.table([("[red]danger[/red]",)], columns=["Name"])
    out = cap.get()
    assert "[red]danger[/red]" in out


def test_table_cell_applies_style_via_theme_token():
    """A Cell styled with a theme token renders the text (styled, not escaped-away)."""
    use_theme("clay")
    from cli_kit.theme import theme

    with ui.console.capture() as cap:
        ui.table([(ui.Cell("healthy", style=theme().success),)], columns=["Status"])
    out = cap.get()
    # The text survives; the literal style token is NOT printed as text.
    assert "healthy" in out
    assert "green" not in out


def test_table_cell_link_is_not_escaped_into_text():
    """A Cell link becomes a real link, so the [link=...] markup is consumed."""
    with ui.console.capture() as cap:
        ui.table(
            [(ui.Cell("http://localhost:3000", link="http://localhost:3000"),)],
            columns=["URL"],
        )
    out = cap.get()
    assert "http://localhost:3000" in out
    # The markup directive itself must not appear as literal text.
    assert "[link=" not in out


def test_table_col_style_and_title_and_no_header():
    with ui.console.capture() as cap:
        ui.table(
            [("a", "b")],
            columns=[ui.Col("Key", style="bold"), ui.Col("Value", justify="right")],
            title="Detail",
            show_header=True,
        )
    out = cap.get()
    assert "Detail" in out
    assert "Key" in out

    with ui.console.capture() as cap:
        ui.table([("a", "b")], columns=["K", "V"], show_header=False)
    out = cap.get()
    # header suppressed: the column names should not render
    assert "K" not in out
    assert "a" in out


def test_badge_returns_markup_without_printing():
    chip = ui.badge("up", status="success")
    assert "up" in chip
    assert isinstance(chip, str)


def test_panel_renders_body_and_title():
    with ui.console.capture() as cap:
        ui.panel("some body text", title="Info")
    out = cap.get()
    assert "some body text" in out
    assert "Info" in out


def test_kv_escapes_markup_in_values():
    """Verify that markup-like strings in kv values are escaped, not interpreted."""
    with ui.console.capture() as cap:
        ui.kv({"Status": "[red]DOWN[/red]"})
    out = cap.get()
    # The literal bracketed text should appear in output, not be interpreted as markup
    assert "[red]DOWN[/red]" in out


def test_kv_title_is_escaped():
    """Verify that markup-like strings in kv titles are escaped, not interpreted."""
    with ui.console.capture() as cap:
        ui.kv({"K": "v"}, title="[red]TITLE[/red]")
    out = cap.get()
    # The literal bracketed text should appear in output, not be interpreted as markup
    assert "[red]TITLE[/red]" in out
