import pytest
from rich import box

from cli_kit.theme import Theme, register_theme, theme, use_theme


@pytest.fixture(autouse=True)
def _reset_theme():
    use_theme("zigablocks")
    yield
    use_theme("zigablocks")


def test_default_theme_is_zigablocks():
    assert theme().name == "zigablocks"


def test_use_theme_switches_active():
    use_theme("blockhead")
    assert theme().name == "blockhead"


def test_use_theme_unknown_raises():
    with pytest.raises(KeyError):
        use_theme("does-not-exist")


def test_clay_is_a_builtin_warm_orange_preset():
    # clay ships as a built-in so ./run, ./configure, and ./blockhead share one
    # palette via use_theme("clay") — no register_theme needed.
    use_theme("clay")
    t = theme()
    assert t.name == "clay"
    assert t.accent == "#cc785c"


def test_mono_uses_no_color_and_ascii():
    use_theme("mono")
    t = theme()
    # semantic tokens map to non-color styles; symbols are ascii
    assert t.success == "bold"
    assert t.ok in {"[ok]", "OK", "*", "+"}
    assert all(ord(c) < 128 for c in t.ok + t.fail + t.arrow + t.bullet)


def test_builtin_themes_use_arrow_marker():
    # The prompt marker is themed (not the hardcoded questionary "?"). All shipped
    # themes use ">" so every consumer gets the same convention out of the box.
    for name in ("zigablocks", "blockhead", "clay", "mono"):
        use_theme(name)
        assert theme().qmark == ">"


def test_theme_qmark_defaults_when_omitted():
    # A custom theme that doesn't specify qmark falls back to questionary's "?",
    # so adding the field never breaks a theme authored before it existed.
    t = Theme(
        name="no-qmark",
        accent="cyan",
        success="green",
        error="red",
        warn="yellow",
        muted="dim",
        ok="✓",
        fail="✗",
        arrow="→",
        bullet="•",
        box=box.ROUNDED,
        spinner="dots",
    )
    assert t.qmark == "?"


def test_register_theme_adds_to_registry():
    custom = Theme(
        name="custom",
        accent="magenta",
        success="green",
        error="red",
        warn="yellow",
        muted="dim",
        ok="✓",
        fail="✗",
        arrow="→",
        bullet="•",
        box=box.ROUNDED,
        spinner="dots",
    )
    register_theme(custom)
    use_theme("custom")
    assert theme().accent == "magenta"
