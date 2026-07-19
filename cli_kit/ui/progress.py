"""Themed determinate progress bar for long-running, multi-step tasks.

    with ui.progress("Deploying infra", total=100) as task:
        task.step(25, "Checking state…")     # advance + retitle in one call
        with task.paused():                  # stop the bar to prompt, then resume
            if not prompts.confirm("Deploy now?", default=True):
                return                        # bar torn down cleanly on the way out
        task.step(40, "Applying…")

`rich.Progress` stays private to this module — callers only ever see `ui.progress`
and the `Task` handle. Appearance flows from the active theme (spinner glyph, bar
complete-color from `accent`, remaining-color from `muted`, box), so re-skinning the
CLI re-skins the bar for free.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
)

from cli_kit.theme import theme
from cli_kit.ui.console import console


class Task:
    """Handle onto one bar. `step()` advances + retitles; `paused()` interrupts."""

    def __init__(self, progress: Progress, task_id: TaskID) -> None:
        self._progress = progress
        self._task_id = task_id

    def step(self, advance: float, description: str | None = None) -> None:
        """Advance the bar by `advance`, optionally changing the label."""
        if description is not None:
            self._progress.update(self._task_id, advance=advance, description=description)
        else:
            self._progress.update(self._task_id, advance=advance)

    @contextmanager
    def paused(self) -> Iterator[None]:
        """Stop rendering for the duration of the block, then resume.

        Use around a prompt so the live bar doesn't fight the question. The bar
        resumes on normal exit and is left stopped if the block raises (e.g. the
        caller aborts) — the enclosing `ui.progress` context tears it down either
        way, so no dead half-rendered bar survives.
        """
        self._progress.stop()
        yield
        self._progress.start()


@contextmanager
def progress(description: str, *, total: float = 100) -> Iterator[Task]:
    """Themed determinate progress bar. Yields a `Task` for the duration.

    The bar is rendered on the shared console (so `NO_COLOR` and test capture
    apply) and removed when the block exits.
    """
    t = theme()
    bar = Progress(
        SpinnerColumn(spinner_name=t.spinner),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(complete_style=t.accent, finished_style=t.accent, style=t.muted),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    )
    with bar:
        task_id = bar.add_task(description, total=total)
        yield Task(bar, task_id)
