"""Phased-run summary: accumulate done/skip/fail steps, then render a themed table.

    report = ui.StepReport("Deployment")
    report.done("Infrastructure")
    report.skip("Frontend", "up to date")
    report.fail("Migrations", "connection refused")
    report.render()          # one themed row per step, status glyph + color from theme
    if not report.ok:        # any failures? → drives the exit code
        sys.exit(1)

Any multi-step CLI has this accumulate-then-summarize shape. `StepReport` owns the
status vocabulary + accumulation and renders a table built like `ui.table`'s (themed
box, accent header, shared console). Glyphs and colors come from the active theme
(`t.ok`/`t.bullet`/`t.fail`, `t.success`/`t.muted`/`t.error`) — never hard-coded — so
an ascii/`mono` terminal renders `[ok]`/`-`/`[x]`, not emoji tofu.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from cli_kit.theme import theme
from cli_kit.ui.layout import Cell, table


class StepStatus(Enum):
    DONE = "done"
    SKIP = "skip"
    FAIL = "fail"


@dataclass
class Step:
    name: str
    status: StepStatus
    detail: str = ""


@dataclass
class StepReport:
    """Accumulates deploy/skip/fail steps and renders them as a themed table."""

    title: str
    steps: list[Step] = field(default_factory=list)

    def done(self, name: str, detail: str = "") -> None:
        self.steps.append(Step(name, StepStatus.DONE, detail))

    def skip(self, name: str, detail: str = "") -> None:
        self.steps.append(Step(name, StepStatus.SKIP, detail))

    def fail(self, name: str, detail: str = "") -> None:
        self.steps.append(Step(name, StepStatus.FAIL, detail))

    @property
    def ok(self) -> bool:
        """True unless any step failed. Drives the caller's exit code."""
        return not any(s.status is StepStatus.FAIL for s in self.steps)

    def render(self) -> None:
        """Print the summary as a themed table (one row per step).

        Renders through :func:`cli_kit.ui.table`; the per-row status color comes
        from a :class:`Cell` styled with the theme token for that status, so this
        no longer hand-builds a rich Table.
        """
        if not self.steps:
            return
        t = theme()
        glyphs = {
            StepStatus.DONE: (t.ok, t.success),
            StepStatus.SKIP: (t.bullet, t.muted),
            StepStatus.FAIL: (t.fail, t.error),
        }
        rows = []
        for step in self.steps:
            glyph, style = glyphs[step.status]
            rows.append(
                [
                    Cell(f"{glyph} {step.status.value}", style=style),
                    step.name,
                    step.detail,
                ]
            )
        table(rows, columns=["Status", "Step", "Detail"], title=self.title)


__all__ = ["StepReport", "Step", "StepStatus"]
