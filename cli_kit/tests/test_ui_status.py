"""Contract for ui.status — the themed indeterminate spinner.

Pins that the spinner glyph and message styling come from the active theme
(the configurability contract), asserted across two themes so it can't silently
hard-code one.
"""

from __future__ import annotations

import pytest
from rich.status import Status

from cli_kit import ui
from cli_kit.theme import theme, use_theme


@pytest.fixture(autouse=True)
def _reset_theme():
    previous = theme().name
    use_theme("zigablocks")
    yield
    use_theme(previous)


def test_returns_a_status_context_manager():
    s = ui.status("Working…")
    assert isinstance(s, Status)
    # usable as a context manager without raising
    with s:
        pass


def test_spinner_reads_theme():
    assert ui.status("x")._spinner.name == theme().spinner  # zigablocks → dots

    use_theme("mono")
    assert ui.status("x")._spinner.name == "line"  # mono's spinner, not a default


def test_message_carries_text_and_accent_style():
    # The status renderable is a Spinner whose .text is a rich Text carrying the
    # message and the accent style span — assert both, rather than a hard-coded
    # color, so re-theming re-styles the message.
    text = ui.status("Logging into ECR").renderable.text
    assert text.plain == "Logging into ECR"
    assert any(span.style == theme().accent for span in text.spans)  # cyan on zigablocks

    use_theme("mono")
    text = ui.status("x").renderable.text
    assert any(span.style == theme().accent for span in text.spans)  # "bold" on mono


def test_status_is_exported_from_ui():
    assert hasattr(ui, "status")
