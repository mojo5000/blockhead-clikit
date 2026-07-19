import pytest

from cli_kit.menu import Menu


def test_add_item():
    m = Menu("Main")
    m.add("Migrate", lambda: 0)
    assert [i.label for i in m.items()] == ["Migrate"]


def test_group_creates_submenu():
    m = Menu("Main")
    dj = m.group("Django")
    dj.add("Migrate", lambda: 0)
    assert "Django" in m.submenus()
    assert m.submenus()["Django"].items()[0].label == "Migrate"


def test_destructive_and_shortcut_recorded():
    m = Menu("Main")
    m.add("Reset", lambda: 0, shortcut="r", destructive=True)
    item = m.items()[0]
    assert item.shortcut == "r"
    assert item.destructive is True


def test_duplicate_shortcut_raises():
    m = Menu("Main")
    m.add("Start", lambda: 0, shortcut="s")
    with pytest.raises(ValueError):
        m.add("Stop", lambda: 0, shortcut="s")
