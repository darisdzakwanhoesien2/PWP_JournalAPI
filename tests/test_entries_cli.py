import pytest
import requests
import requests_mock
from pytest_mock import MockerFixture
from typer.testing import CliRunner
from client import entries_cli, auth

runner = CliRunner()

@pytest.fixture
def mock_config(mocker: MockerFixture):
    """Mock config settings."""
    mocker.patch("client.config.API_URL", "http://test-api")
    mocker.patch("client.config.REQUEST_TIMEOUT", 5)


def test_list_entries_success(mocker: MockerFixture, mock_config, caplog):
    """Test list_entries command success."""
    caplog.set_level("INFO")
    mocker.patch("client.auth.get_auth", return_value={"Authorization": "Bearer test_token"})
    with requests_mock.Mocker() as m:
        m.get(
            "http://test-api/entries",
            json=[{"id": 1, "title": "Test Entry", "tags": ["tag1"], "last_updated": "2023-01-01"}],
            status_code=200,
        )
        mocker.patch("client.entries_cli.console.print")
        result = runner.invoke(entries_cli.entry_app, ["list"])
    assert result.exit_code == 0
    assert "[1] Test Entry - Tags: tag1" in entries_cli.console.print.call_args_list[0][0][0]
    assert "Listed journal entries" in caplog.text


def test_list_entries_empty(mocker: MockerFixture, mock_config, caplog):
    """Test list_entries when no entries exist."""
    caplog.set_level("INFO")
    mocker.patch("client.auth.get_auth", return_value={"Authorization": "Bearer test_token"})
    with requests_mock.Mocker() as m:
        m.get("http://test-api/entries", json=[], status_code=200)
        mocker.patch("client.entries_cli.console.print")
        result = runner.invoke(entries_cli.entry_app, ["list"])
    assert result.exit_code == 0
    assert "⚠️ No journal entries found." in entries_cli.console.print.call_args[0][0]
    assert "Listed journal entries" in caplog.text


def test_list_entries_not_logged_in(mocker: MockerFixture, mock_config):
    """Test list_entries when not logged in."""
    mocker.patch("client.auth.get_auth", return_value={})
    mocker.patch("client.entries_cli.console.print")
    result = runner.invoke(entries_cli.entry_app, ["list"])
    assert result.exit_code == 1
    assert "❌ Please login first." in entries_cli.console.print.call_args[0][0]


def test_list_entries_http_error(mocker: MockerFixture, mock_config, caplog):
    """Test list_entries with HTTP error."""
    caplog.set_level("ERROR")
    mocker.patch("client.auth.get_auth", return_value={"Authorization": "Bearer test_token"})
    with requests_mock.Mocker() as m:
        m.get("http://test-api/entries", json={"error": "Unauthorized"}, status_code=401)
        mocker.patch("client.utils.handle_error")
        result = runner.invoke(entries_cli.entry_app, ["list"])
    assert result.exit_code == 0
    entries_cli.utils.handle_error.assert_called_once()
    assert entries_cli.utils.handle_error.call_args[0][2] == "Failed to list entries"


def test_create_entry_success(mocker: MockerFixture, mock_config, caplog):
    """Test create entry command success."""
    caplog.set_level("INFO")
    mocker.patch("client.auth.get_auth", return_value={"Authorization": "Bearer test_token"})
    with requests_mock.Mocker() as m:
        m.post("http://test-api/entries", json={}, status_code=201)
        mocker.patch("client.entries_cli.console.print")
        result = runner.invoke(entries_cli.entry_app, ["create", "Test Title", "Test Content", "--tags", "tag1,tag2"])
    assert result.exit_code == 0
    assert "✅ Entry created successfully!" in entries_cli.console.print.call_args[0][0]
    assert "Created entry: Test Title" in caplog.text


def test_create_entry_no_tags(mocker: MockerFixture, mock_config, caplog):
    """Test create entry without tags."""
    caplog.set_level("INFO")
    mocker.patch("client.auth.get_auth", return_value={"Authorization": "Bearer test_token"})
    with requests_mock.Mocker() as m:
        m.post("http://test-api/entries", json={}, status_code=201)
        mocker.patch("client.entries_cli.console.print")
        result = runner.invoke(entries_cli.entry_app, ["create", "Test Title", "Test Content"])
    assert result.exit_code == 0
    assert "✅ Entry created successfully!" in entries_cli.console.print.call_args[0][0]
    assert "Created entry: Test Title" in caplog.text


def test_create_entry_not_logged_in(mocker: MockerFixture, mock_config):
    """Test create entry when not logged in."""
    mocker.patch("client.auth.get_auth", return_value={})
    mocker.patch("client.entries_cli.console.print")
    result = runner.invoke(entries_cli.entry_app, ["create", "Test Title", "Test Content"])
    assert result.exit_code == 1
    assert "❌ Please login first." in entries_cli.console.print.call_args[0][0]


def test_create_entry_http_error(mocker: MockerFixture, mock_config, caplog):
    """Test create entry with HTTP error."""
    caplog.set_level("ERROR")
    mocker.patch("client.auth.get_auth", return_value={"Authorization": "Bearer test_token"})
    with requests_mock.Mocker() as m:
        m.post("http://test-api/entries", json={"error": "Bad request"}, status_code=400)
        mocker.patch("client.utils.handle_error")
        result = runner.invoke(entries_cli.entry_app, ["create", "Test Title", "Test Content"])
    assert result.exit_code == 0
    entries_cli.utils.handle_error.assert_called_once()
    assert entries_cli.utils.handle_error.call_args[0][2] == "Failed to create entry"


def test_delete_entry_success(mocker: MockerFixture, mock_config, caplog):
    """Test delete entry command success."""
    caplog.set_level("INFO")
    mocker.patch("client.auth.get_auth", return_value={"Authorization": "Bearer test_token"})
    with requests_mock.Mocker() as m:
        m.delete("http://test-api/entries/1", json={}, status_code=200)
        mocker.patch("client.entries_cli.console.print")
        result = runner.invoke(entries_cli.entry_app, ["delete", "1"])
    assert result.exit_code == 0
    assert "✅ Entry deleted successfully!" in entries_cli.console.print.call_args[0][0]
    assert "Deleted entry ID 1" in caplog.text


def test_delete_entry_not_found(mocker: MockerFixture, mock_config, caplog):
    """Test delete entry when entry not found."""
    caplog.set_level("ERROR")
    mocker.patch("client.auth.get_auth", return_value={"Authorization": "Bearer test_token"})
    with requests_mock.Mocker() as m:
        m.delete("http://test-api/entries/1", json={"error": "Not found"}, status_code=404)
        mocker.patch("client.entries_cli.console.print")
        result = runner.invoke(entries_cli.entry_app, ["delete", "1"])
    assert result.exit_code == 0
    assert "⚠️ Entry not found." in entries_cli.console.print.call_args[0][0]


def test_delete_entry_not_logged_in(mocker: MockerFixture, mock_config):
    """Test delete entry when not logged in."""
    mocker.patch("client.auth.get_auth", return_value={})
    mocker.patch("client.entries_cli.console.print")
    result = runner.invoke(entries_cli.entry_app, ["delete", "1"])
    assert result.exit_code == 1
    assert "❌ Please login first." in entries_cli.console.print.call_args[0][0]


def test_delete_entry_http_error(mocker: MockerFixture, mock_config, caplog):
    """Test delete entry with other HTTP error."""
    caplog.set_level("ERROR")
    mocker.patch("client.auth.get_auth", return_value={"Authorization": "Bearer test_token"})
    with requests_mock.Mocker() as m:
        m.delete("http://test-api/entries/1", json={"error": "Unauthorized"}, status_code=401)
        mocker.patch("client.utils.handle_error")
        result = runner.invoke(entries_cli.entry_app, ["delete", "1"])
    assert result.exit_code == 0
    entries_cli.utils.handle_error.assert_called_once()
    assert entries_cli.utils.handle_error.call_args[0][2] == "Failed to delete entry"