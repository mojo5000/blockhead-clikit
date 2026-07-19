from cli_kit.errors import Aborted, CommandFailed


def test_aborted_is_exception():
    assert issubclass(Aborted, Exception)


def test_command_failed_carries_context():
    err = CommandFailed(cmd=["git", "status"], returncode=1, output="fatal: boom")
    assert err.cmd == ["git", "status"]
    assert err.returncode == 1
    assert err.output == "fatal: boom"
    assert "git status" in str(err)
    assert "1" in str(err)
