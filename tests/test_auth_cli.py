from unittest.mock import Mock

import pytest
import requests
import requests_mock
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from client import auth_cli, auth

runner = CliRunner()


@pytest.fixture
def mock_config(mocker: MockerFixture):
    """Mock config settings."""
    mocker.patch("client.config.API_URL", "http://test-api")
    mocker.patch("client.config.REQUEST_TIMEOUT", 5)


def test_register_success(mocker: MockerFixture, mock_config, caplog):
    """Test register command success."""
    caplog.set_level("INFO")
    with requests_mock.Mocker() as m:
        m.post("http://test-api/users/register", json={"token": "test_token"}, status_code=200)
        mocker.patch("client.auth_cli.console.print")
        result = runner.invoke(
            auth_cli.auth_app,
            ["register", "--username", "testuser", "--email", "test@example.com", "--password", "pass123"],
        )
    assert result.exit_code == 0
    assert "✅ Registered successfully!" in auth_cli.console.print.call_args[0][0]
    assert "User registered: testuser" in caplog.text


def test_register_http_error(mocker: MockerFixture, mock_config, caplog):
    """Test register command with HTTP error."""
    caplog.set_level("ERROR")
    with requests_mock.Mocker() as m:
        m.post("http://test-api/users/register", json={"error": "User exists"}, status_code=400)
        mocker.patch("client.utils.handle_error")
        result = runner.invoke(
            auth_cli.auth_app,
            ["register", "--username", "testuser", "--email", "test@example.com", "--password", "pass123"],
        )
    assert result.exit_code == 0
    auth_cli.utils.handle_error.assert_called_once()
    assert auth_cli.utils.handle_error.call_args[0][2] == "Registration failed"


def test_login_success(mocker: MockerFixture, mock_config, caplog):
    """Test login command success."""
    caplog.set_level("INFO")
    with requests_mock.Mocker() as m:
        m.post("http://test-api/users/login", json={"token": "test_token"}, status_code=200)
        mocker.patch("client.auth.save_token")
        mocker.patch("client.auth_cli.console.print")
        result = runner.invoke(
            auth_cli.auth_app,
            ["login", "--email", "test@example.com", "--password", "pass123"],
        )
    assert result.exit_code == 0
    auth.save_token.assert_called_once_with("test_token")
    assert "✅ Logged in successfully!" in auth_cli.console.print.call_args[0][0]
    assert "User logged in: test@example.com" in caplog.text


def test_login_http_error(mocker: MockerFixture, mock_config, caplog):
    """Test login command with HTTP error."""
    caplog.set_level("ERROR")
    with requests_mock.Mocker() as m:
        m.post("http://test-api/users/login", json={"error": "Invalid credentials"}, status_code=401)
        mocker.patch("client.utils.handle_error")
        result = runner.invoke(
            auth_cli.auth_app,
            ["login", "--email", "test@example.com", "--password", "wrongpass"],
        )
    assert result.exit_code == 0
    auth_cli.utils.handle_error.assert_called_once()
    assert auth_cli.utils.handle_error.call_args[0][2] == "Login failed"


def test_logout(mocker: MockerFixture, caplog):
    """Test logout command."""
    caplog.set_level("INFO")
    mocker.patch("client.auth.clear_token")
    mocker.patch("client.auth_cli.console.print")
    result = runner.invoke(auth_cli.auth_app, ["logout"])
    assert result.exit_code == 0
    auth.clear_token.assert_called_once()
    assert "🔓 Logged out successfully!" in auth_cli.console.print.call_args[0][0]
    assert "User logged out" in caplog.text


def test_me_logged_in(mocker: MockerFixture, caplog):
    """Test me command when logged in."""
    caplog.set_level("DEBUG")
    mocker.patch("client.auth.get_token", return_value="test_token")
    mocker.patch("client.auth_cli.console.print")
    result = runner.invoke(auth_cli.auth_app, ["me"])
    assert result.exit_code == 0
    assert "🔐 Logged in" in auth_cli.console.print.call_args[0][0]
    assert "Checked login status: logged in" in caplog.text


def test_me_not_logged_in(mocker: MockerFixture, caplog):
    """Test me command when not logged in."""
    caplog.set_level("DEBUG")
    mocker.patch("client.auth.get_token", return_value=None)
    mocker.patch("client.auth_cli.console.print")
    result = runner.invoke(auth_cli.auth_app, ["me"])
    assert result.exit_code == 0
    assert "🔓 Not logged in" in auth_cli.console.print.call_args[0][0]
    assert "Checked login status: not logged in" in caplog.text