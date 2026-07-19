"""Themed subprocess runner. Single place for echo, spinner, dry-run, failure."""

from __future__ import annotations

import os
import subprocess
from collections.abc import Callable
from pathlib import Path

from cli_kit.errors import CommandFailed
from cli_kit.theme import theme
from cli_kit.ui import console


def run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    capture: bool = False,
    check: bool = False,
    dry_run: bool = False,
    spinner: str | None = None,
    input: str | None = None,  # noqa: A002 — mirrors subprocess.run's own kwarg name
) -> subprocess.CompletedProcess:
    """Run a command. `input`, if given, is written to the process's stdin — the
    no-shell way to feed a secret to a tool (e.g. `docker login --password-stdin`)
    without putting it on the command line. Passing `input` forces text mode."""
    t = theme()
    printable = " ".join(cmd)

    if dry_run:
        console.print(f"[{t.muted}]{t.arrow} would run: {printable}[/]")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    console.print(f"[{t.muted}]{t.arrow} {printable}[/]")
    merged_env = {**os.environ, **(env or {})}

    def _exec() -> subprocess.CompletedProcess:
        return subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            env=merged_env,
            capture_output=capture,
            # text mode is required whenever we pass a str stdin; capture already
            # implies it, so enable it for either.
            text=capture or input is not None,
            input=input,
            check=False,
        )

    if capture and spinner:
        with console.status(f"[{t.accent}]{spinner}[/]", spinner=t.spinner):
            result = _exec()
    else:
        result = _exec()

    if check and result.returncode != 0:
        output = result.stdout if capture else None
        raise CommandFailed(cmd=cmd, returncode=result.returncode, output=output)
    return result


def stream(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    check: bool = False,
    dry_run: bool = False,
    echo: bool = True,
    filter: Callable[[str], str | None] | None = None,  # noqa: A002 — reads best at call sites
) -> subprocess.CompletedProcess:
    """Run a command, teeing its output to the console live *and* capturing it.

    Bridges the gap between ``run(capture=True)`` (silent until done) and
    ``run(capture=False)`` (nothing captured): the user sees output as it
    streams, and the full text is returned so ``CommandFailed`` can carry the
    tail on a non-zero exit. Built for long, chatty commands (``tofu apply``,
    ``aws``) where both live feedback and error context matter.

    stderr is merged into stdout so interleaved tool output stays in order; the
    returned ``CompletedProcess`` has that combined text in ``.stdout`` and an
    empty ``.stderr`` (parity of shape with ``run(capture=True)``).

    ``filter`` transforms or drops each line *for display only* — returning None
    hides a line from the console while the raw line is still captured, so
    callers can quiet noisy tools without losing error context. ``echo`` prints
    the themed command line before running, matching ``run``.
    """
    t = theme()
    printable = " ".join(cmd)

    if dry_run:
        console.print(f"[{t.muted}]{t.arrow} would run: {printable}[/]")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    if echo:
        console.print(f"[{t.muted}]{t.arrow} {printable}[/]")
    merged_env = {**os.environ, **(env or {})}

    captured: list[str] = []
    proc = subprocess.Popen(
        cmd,
        cwd=str(cwd) if cwd else None,
        env=merged_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # merge so interleaved output keeps its order
        text=True,
        bufsize=1,  # line-buffered
    )

    # stdout=PIPE guarantees a readable stream; guard narrows the type for callers.
    if proc.stdout is None:  # pragma: no cover — defensive, PIPE always yields a stream
        raise CommandFailed(cmd=cmd, returncode=-1, output="no stdout stream")
    for raw in proc.stdout:
        line = raw.rstrip("\n")
        captured.append(raw)
        shown = filter(line) if filter is not None else line
        if shown is not None:
            console.print(shown, markup=False, highlight=False)
    returncode = proc.wait()

    output = "".join(captured)
    result = subprocess.CompletedProcess(cmd, returncode, stdout=output, stderr="")
    if check and returncode != 0:
        raise CommandFailed(cmd=cmd, returncode=returncode, output=output)
    return result
