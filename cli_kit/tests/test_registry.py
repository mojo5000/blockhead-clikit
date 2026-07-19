import click
from click.testing import CliRunner

from cli_kit import prompts
from cli_kit.menu import Menu
from cli_kit.registry import cli_command, expose


def test_cli_command_builds_runnable_command():
    ran = {}

    def migrate(force=False):
        ran["force"] = force
        click.echo("migrated")

    grp = click.Group()
    cli_command(grp, migrate)
    result = CliRunner().invoke(grp, ["migrate"])
    assert result.exit_code == 0
    assert "migrated" in result.output
    assert ran["force"] is False


def test_cli_command_flag_from_bool_default():
    def migrate(force=False):
        click.echo(f"force={force}")

    grp = click.Group()
    cli_command(grp, migrate)
    result = CliRunner().invoke(grp, ["migrate", "--force"])
    assert "force=True" in result.output


def test_expose_adds_to_menu_group():
    def seed():
        return 0

    menu = Menu("Main")
    expose(seed, menu=(menu, "Seed data", "Django"))
    assert "Django" in menu.submenus()
    assert menu.submenus()["Django"].items()[0].label == "Seed data"


def test_expose_both_surfaces():
    def seed():
        click.echo("seeded")

    grp = click.Group()
    menu = Menu("Main")
    expose(seed, cli=grp, menu=(menu, "Seed"))
    # CLI surface
    assert "seed" in grp.commands
    # menu surface (root)
    assert menu.items()[0].label == "Seed"


def test_expose_reuses_existing_group():
    def action_a():
        click.echo("action a")

    def action_b():
        click.echo("action b")

    menu = Menu("Main")
    expose(action_a, menu=(menu, "Action A", "Django"))
    expose(action_b, menu=(menu, "Action B", "Django"))
    # Both actions should be in the same "Django" submenu
    assert "Django" in menu.submenus()
    django_group = menu.submenus()["Django"]
    labels = [item.label for item in django_group.items()]
    assert "Action A" in labels
    assert "Action B" in labels
    assert len(labels) == 2


def test_cli_command_required_arg_is_positional():
    def greet(target):
        click.echo(f"hi {target}")

    grp = click.Group()
    cli_command(grp, greet)
    runner = CliRunner()

    # With required argument
    result = runner.invoke(grp, ["greet", "world"])
    assert result.exit_code == 0
    assert "hi world" in result.output

    # Missing required argument
    result = runner.invoke(grp, ["greet"])
    assert result.exit_code == 2


def test_cli_command_maps_input_required_to_usage_error(monkeypatch):
    """A missing required input on a non-tty stdin exits 2 (Click usage error),
    not an uncaught traceback."""
    monkeypatch.setattr(prompts.resolve_mod, "is_interactive", lambda: False)

    def make_ws(name=""):
        # name is missing and there's no tty → resolve raises InputRequired,
        # which the Click adapter must translate into a UsageError.
        resolved = prompts.resolve(name, prompt="Workspace name:", flag_name="name")
        click.echo(f"made {resolved}")

    grp = click.Group()
    cli_command(grp, make_ws)
    result = CliRunner().invoke(grp, ["make-ws"])
    assert result.exit_code == 2
    assert "--name" in result.output


def test_cli_command_nonbool_default_is_option():
    def deploy(env="dev"):
        click.echo(f"env={env}")

    grp = click.Group()
    cli_command(grp, deploy)
    runner = CliRunner()

    # With default
    result = runner.invoke(grp, ["deploy"])
    assert result.exit_code == 0
    assert "env=dev" in result.output

    # With option override
    result = runner.invoke(grp, ["deploy", "--env", "prod"])
    assert result.exit_code == 0
    assert "env=prod" in result.output
