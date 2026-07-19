import pytest

from cli_kit import sh
from cli_kit.errors import CommandFailed


def test_run_captures_output():
    result = sh.run(["echo", "hello"], capture=True)
    assert result.returncode == 0
    assert "hello" in result.stdout


def test_dry_run_does_not_execute():
    # `false` would exit 1 if run; dry_run must skip it and report success.
    result = sh.run(["false"], dry_run=True)
    assert result.returncode == 0


def test_dry_run_echoes_would_run():
    with sh_console_capture() as cap:
        sh.run(["rm", "-rf", "nope"], dry_run=True)
    assert "would run" in cap.get()
    assert "rm" in cap.get()


def test_check_raises_command_failed_on_nonzero():
    with pytest.raises(CommandFailed) as exc:
        sh.run(["false"], capture=True, check=True)
    assert exc.value.returncode != 0
    assert exc.value.cmd == ["false"]


def test_no_check_returns_nonzero_without_raising():
    result = sh.run(["false"], capture=True, check=False)
    assert result.returncode != 0


def test_input_is_written_to_stdin():
    # `cat` echoes its stdin — proves `input` reaches the process without a shell.
    result = sh.run(["cat"], input="secret-token", capture=True)
    assert result.returncode == 0
    assert result.stdout == "secret-token"


def test_input_without_capture_still_feeds_stdin():
    # No capture: `grep -q` exits 0 only if it saw the pattern on stdin. This
    # proves stdin is fed even when we're not capturing output (the ECR-login shape).
    result = sh.run(["grep", "-q", "found"], input="found me", check=False)
    assert result.returncode == 0


def test_input_dry_run_does_not_execute():
    result = sh.run(["cat"], input="x", dry_run=True)
    assert result.returncode == 0
    assert result.stdout == ""


# helper: sh writes through the shared ui console
from contextlib import contextmanager  # noqa: E402

from cli_kit.ui import console  # noqa: E402


@contextmanager
def sh_console_capture():
    with console.capture() as cap:
        yield cap
