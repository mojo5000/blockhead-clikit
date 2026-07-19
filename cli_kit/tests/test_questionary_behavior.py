"""Pin questionary's native wrap-around so an upgrade can't silently drop it.

cli_kit's menu relies on wrap-around navigation (roadmap 'nice-to-have') being
provided by questionary rather than reimplemented. This guards that contract.
"""

from questionary.prompts.common import Choice, InquirerControl


def _control():
    return InquirerControl([Choice("a"), Choice("b"), Choice("c")])


def test_select_next_wraps_from_last_to_first():
    ctrl = _control()
    ctrl.pointed_at = ctrl.choice_count - 1
    ctrl.select_next()
    assert ctrl.pointed_at == 0


def test_select_previous_wraps_from_first_to_last():
    ctrl = _control()
    ctrl.pointed_at = 0
    ctrl.select_previous()
    assert ctrl.pointed_at == ctrl.choice_count - 1
