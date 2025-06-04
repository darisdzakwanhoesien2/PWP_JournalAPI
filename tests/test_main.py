from pytest_mock import MockerFixture
from typer.testing import CliRunner
from client import main

runner = CliRunner()

def test_main_app_help(mocker: MockerFixture, caplog):
    """Test main CLI help command."""
    caplog.set_level("INFO")
    mocker.patch("client.main.logger.info")
    result = runner.invoke(main.app, ["--help"])
    assert result.exit_code == 0
    assert "PWP Journal API CLI - Manage your journal entries" in result.output
    assert main.logger.info.call_args[0][0] == "Starting Journal API CLI"

def test_main_app_subcommands(mocker: MockerFixture):
    """Test main CLI subcommands registration."""
    assert "auth" in [cmd.name for cmd in main.app.registered_commands]
    assert "entry" in [cmd.name for cmd in main.app.registered_commands]
    assert "comment" in [cmd.name for cmd in main.app.registered_commands]