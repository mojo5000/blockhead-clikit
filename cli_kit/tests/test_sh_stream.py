"""Contract for sh.stream — the tee-and-capture subprocess runner.

Pins the behaviors the deploy port will rely on: output is both shown live and
returned, stderr is folded into stdout, `filter` shapes display without dropping
captured text, failures carry the tail, and dry_run matches `run`.
"""

from __future__ import annotations

import pytest

from cli_kit import sh
from cli_kit.errors import CommandFailed
from cli_kit.tests.test_sh import sh_console_capture


def test_captures_and_echoes_output():
    with sh_console_capture() as cap:
        result = sh.stream(["printf", "a\nb\nc\n"])
    out = cap.get()
    # shown live…
    assert "a" in out and "b" in out and "c" in out
    # …and returned for error context
    assert result.stdout == "a\nb\nc\n"
    assert result.returncode == 0


def test_echoes_command_line_by_default():
    with sh_console_capture() as cap:
        sh.stream(["echo", "hi"])
    assert "echo hi" in cap.get()


def test_echo_false_suppresses_command_line():
    with sh_console_capture() as cap:
        sh.stream(["echo", "hi"], echo=False)
    out = cap.get()
    assert "echo hi" not in out
    assert "hi" in out  # the command's own output still streams


def test_stderr_is_merged_into_stdout():
    result = sh.stream(["sh", "-c", "echo out; echo err 1>&2"])
    assert "out" in result.stdout
    assert "err" in result.stdout
    assert result.stderr == ""


def test_filter_transforms_displayed_lines_but_keeps_raw_capture():
    with sh_console_capture() as cap:
        result = sh.stream(
            ["printf", "keep\nNOISE\n"],
            echo=False,
            filter=lambda line: f">> {line}" if line != "NOISE" else "quieted",
        )
    shown = cap.get()
    assert ">> keep" in shown
    assert "quieted" in shown
    # raw output is captured verbatim regardless of how it was displayed
    assert result.stdout == "keep\nNOISE\n"


def test_filter_none_drops_line_from_display_but_not_capture():
    # echo=False so the command line (which contains both tokens) doesn't
    # pollute the display assertion — we're testing the *streamed* lines.
    with sh_console_capture() as cap:
        result = sh.stream(
            ["printf", "visible\nsecret\n"],
            echo=False,
            filter=lambda line: None if line == "secret" else line,
        )
    shown = cap.get()
    assert "visible" in shown
    assert "secret" not in shown
    assert "secret\n" in result.stdout  # still captured


def test_check_raises_command_failed_with_tail():
    with pytest.raises(CommandFailed) as exc:
        sh.stream(["sh", "-c", "echo boom; exit 3"], check=True)
    assert exc.value.returncode == 3
    assert exc.value.cmd == ["sh", "-c", "echo boom; exit 3"]
    assert "boom" in (exc.value.output or "")


def test_no_check_returns_nonzero_without_raising():
    result = sh.stream(["false"], check=False)
    assert result.returncode != 0


def test_dry_run_does_not_execute():
    # `false` would exit 1 if run; dry_run must skip it and report success.
    result = sh.stream(["false"], dry_run=True)
    assert result.returncode == 0
    assert result.stdout == ""


def test_dry_run_echoes_would_run():
    with sh_console_capture() as cap:
        sh.stream(["rm", "-rf", "nope"], dry_run=True)
    assert "would run" in cap.get()
    assert "rm" in cap.get()
