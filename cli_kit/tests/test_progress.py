"""Behavior + theme-configurability contract for ui.progress.

Pins what callers rely on (step advances/retitles, paused() interrupts and
resumes, the bar reads the active theme) — not rich's internals beyond the few
column attributes we deliberately drive from the theme.
"""

from __future__ import annotations

import pytest
from rich.progress import BarColumn, SpinnerColumn

from cli_kit import ui
from cli_kit.theme import theme, use_theme


@pytest.fixture(autouse=True)
def _reset_theme():
    # Default to zigablocks for the test body, but restore whatever theme was
    # active on entry so switching to mono here can't leak into another module's
    # import-time theme state (e.g. run's `clay`).
    previous = theme().name
    use_theme("zigablocks")
    yield
    use_theme(previous)


def _columns(task: ui.Task):
    return task._progress.columns


def _task_row(task: ui.Task):
    return task._progress.tasks[0]


def test_step_advances_progress():
    with ui.progress("work", total=100) as task:
        assert _task_row(task).completed == 0
        task.step(25)
        assert _task_row(task).completed == 25
        task.step(15)
        assert _task_row(task).completed == 40


def test_step_retitles_when_description_given():
    with ui.progress("start", total=100) as task:
        assert _task_row(task).description == "start"
        task.step(10, "now doing X")
        assert _task_row(task).description == "now doing X"
        assert _task_row(task).completed == 10


def test_step_without_description_keeps_label():
    with ui.progress("keep me", total=100) as task:
        task.step(10)
        assert _task_row(task).description == "keep me"


def test_total_is_respected():
    with ui.progress("work", total=50) as task:
        assert _task_row(task).total == 50
        task.step(50)
        assert _task_row(task).finished


def test_paused_resumes_the_bar():
    with ui.progress("work", total=100) as task:
        assert task._progress.live.is_started
        with task.paused():
            assert not task._progress.live.is_started  # stopped while prompting
        assert task._progress.live.is_started  # resumed after the block


def test_paused_leaves_bar_stopped_on_abort_but_context_tears_down():
    # If the paused block raises (caller aborts), the bar is left stopped and the
    # enclosing `progress` context still tears it down cleanly — no dead bar.
    with pytest.raises(RuntimeError):
        with ui.progress("work", total=100) as task:
            with task.paused():
                raise RuntimeError("user aborted")
    # Reaching here means the context manager exited without hanging or erroring.


def test_bar_reads_accent_and_muted_from_theme():
    with ui.progress("work") as task:
        bar = next(c for c in _columns(task) if isinstance(c, BarColumn))
        # zigablocks: accent drives the filled bar, muted the remaining track.
        from cli_kit.theme import theme

        t = theme()
        assert bar.complete_style == t.accent
        assert bar.finished_style == t.accent
        assert bar.style == t.muted


def test_spinner_reads_theme():
    from cli_kit.theme import theme

    with ui.progress("work") as task:
        spinner_col = next(c for c in _columns(task) if isinstance(c, SpinnerColumn))
        assert spinner_col.spinner.name == theme().spinner

    use_theme("mono")
    with ui.progress("work") as task:
        spinner_col = next(c for c in _columns(task) if isinstance(c, SpinnerColumn))
        assert spinner_col.spinner.name == "line"  # mono's spinner, not the default


def test_mono_theme_uses_no_color_styles():
    use_theme("mono")
    with ui.progress("work") as task:
        bar = next(c for c in _columns(task) if isinstance(c, BarColumn))
        # mono maps accent→"bold", muted→"dim": no raw color leaks into the bar.
        assert bar.complete_style == "bold"
        assert bar.style == "dim"


def test_progress_is_exported_from_ui():
    assert hasattr(ui, "progress")
    assert hasattr(ui, "Task")
