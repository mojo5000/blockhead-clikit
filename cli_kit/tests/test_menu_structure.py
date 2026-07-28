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


def test_display_label_marks_shortcut_inline():
    m = Menu("Main")
    m.add("Configure", lambda: 0, shortcut="c")
    assert m.items()[0].display_label() == "(C)onfigure"


def test_display_label_appends_when_letter_absent():
    m = Menu("Main")
    m.add("Reset local state", lambda: 0, shortcut="x")
    assert m.items()[0].display_label() == "Reset local state (x)"


def test_display_label_unchanged_without_shortcut():
    m = Menu("Main")
    m.add("Run", lambda: 0)
    assert m.items()[0].display_label() == "Run"


def test_display_label_marks_first_matching_letter():
    m = Menu("Main")
    m.add("Deploy", lambda: 0, shortcut="d")
    assert m.items()[0].display_label() == "(D)eploy"
