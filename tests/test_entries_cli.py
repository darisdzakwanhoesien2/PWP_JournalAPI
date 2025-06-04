import pytest
import requests
import requests_mock
from pytest_mock import MockerFixture
from typer.testing import CliRunner
from client import entries, auth
import client.entries_cli
import client.utils

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
            json=[
                {"id": 1, "title": "Test Entry", "tags": ["tag1"], "last_updated": "2023-01-01T00:00:00"},
                {"id": 2, "title": "Another Entry", "tags": ["tag2"], "last_updated": "2023-01-02T00:00:00"}
            ],
            status_code=200,
        )
        console_mock = mocker.patch("client.entries_cli.console.print")
        result = runner.invoke(entries.entry_app, ["list"])
    
    assert result.exit_code == 0
    print_calls = [call[0][0] for call in console_mock.call_args_list]
    assert any("[1] Test Entry - Tags: tag1" in call for call in print_calls)
    assert any("[2] Another Entry - Tags: tag2" in call for call in print_calls)
    assert "Listed journal entries" in caplog.text
    assert m.last_request.headers["Authorization"] == "Bearer test_token"
    assert m.last_request.timeout == 5

def test_list_entries_empty(mocker: MockerFixture, mock_config, caplog):
    """Test list_entries when no entries exist."""
    caplog.set_level("INFO")
    mocker.patch("client.auth.get_auth", return_value={"Authorization": "Bearer test_token"})
    with requests_mock.Mocker() as m:
        m.get("http://test-api/entries", json=[], status_code=200)
        console_mock = mocker.patch("client.entries_cli.console.print")
        result = runner.invoke(entries.entry_app, ["list"])
    
    assert result.exit_code == 0
    assert "⚠️ No journal entries found." in console_mock.call_args[0][0]
    assert "Listed journal entries" in caplog.text
    assert m.last_request.timeout == 5

def test_list_entries_not_logged_in(mocker: MockerFixture, mock_config):
    """Test list_entries when not logged in."""
    mocker.patch("client.auth.get_auth", return_value={})
    console_mock = mocker.patch("client.entries_cli.console.print")
    result = runner.invoke(entries.entry_app, ["list"])
    
    assert result.exit_code == 1
    assert "❌ Please login first." in console_mock.call_args[0][0]

def test_list_entries_http_error(mocker: MockerFixture, mock_config, caplog):
    """Test list_entries with HTTP error."""
    caplog.set_level("ERROR")
    mocker.patch("client.auth.get_auth", return_value={"Authorization": "Bearer test_token"})
    with requests_mock.Mocker() as m:
        m.get("http://test-api/entries", json={"error": "Unauthorized"}, status_code=401)
        handle_error_mock = mocker.patch("client.utils.handle_error")
        result = runner.invoke(entries.entry_app, ["list"])
    
    assert result.exit_code == 1
    handle_error_mock.assert_called_once()
    assert handle_error_mock.call_args[0][0].status_code == 401
    assert handle_error_mock.call_args[0][0].json() == {"error": "Unauthorized"}
    assert handle_error_mock.call_args[0][2] == "Failed to list entries"
    assert "Failed to list entries" in caplog.text

def test_list_entries_network_error(mocker: MockerFixture, mock_config, caplog):
    """Test list_entries with network error."""
    caplog.set_level("ERROR")
    mocker.patch("client.auth.get_auth", return_value={"Authorization": "Bearer test_token"})
    with requests_mock.Mocker() as m:
        m.get("http://test-api/entries", exc=requests.exceptions.RequestException("Network error"))
        handle_error_mock = mocker.patch("client.utils.handle_error")
        result = runner.invoke(entries.entry_app, ["list"])
    
    assert result.exit_code == 1
    handle_error_mock.assert_called_once()
    assert isinstance(handle_error_mock.call_args[0][1], requests.exceptions.RequestException)
    assert handle_error_mock.call_args[0][2] == "Failed to list entries"
    assert "Failed to list entries" in caplog.text

def test_create_entry_success(mocker: MockerFixture, mock_config, caplog):
    """Test create entry command success."""
    caplog.set_level("INFO")
    mocker.patch("client.auth.get_auth", return_value={"Authorization": "Bearer test_token"})
    with requests_mock.Mocker() as m:
        m.post(
            "http://test-api/entries",
            json={"id": 1, "title": "Test Title", "content": "Test Content", "tags": ["tag1", "tag2"]},
            status_code=201
        )
        console_mock = mocker.patch("client.entries_cli.console.print")
        result = runner.invoke(entries.entry_app, ["create", "Test Title", "Test Content", "--tags", "tag1,tag2"])
    
    assert result.exit_code == 0
    assert "✅ Entry created successfully!" in console_mock.call_args[0][0]
    assert "Created entry: Test Title" in caplog.text
    assert m.last_request.json() == {"title": "Test Title", "content": "Test Content", "tags": ["tag1", "tag2"]}
    assert m.last_request.headers["Authorization"] == "Bearer test_token"
    assert m.last_request.timeout == 5

def test_create_entry_no_tags(mocker: MockerFixture, mock_config, caplog):
    """Test create entry without tags."""
    caplog.set_level("INFO")
    mocker.patch("client.auth.get_auth", return_value={"Authorization": "Bearer test_token"})
    with requests_mock.Mocker() as m:
        m.post(
            "http://test-api/entries",
            json={"id": 1, "title": "Test Title", "content": "Test Content", "tags": []},
            status_code=201
        )
        console_mock = mocker.patch("client.entries_cli.console.print")
        result = runner.invoke(entries.entry_app, ["create", "Test Title", "Test Content"])
    
    assert result.exit_code == 0
    assert "✅ Entry created successfully!" in console_mock.call_args[0][0]
    assert "Created entry: Test Title" in caplog.text
    assert m.last_request.json() == {"title": "Test Title", "content": "Test Content", "tags": []}
    assert m.last_request.timeout == 5

def test_create_entry_invalid_input(mocker: MockerFixture, mock_config, caplog):
    """Test create entry with empty title."""
    caplog.set_level("ERROR")
    mocker.patch("client.auth.get_auth", return_value={"Authorization": "Bearer test_token"})
    console_mock = mocker.patch("client.entries_cli.console.print")
    result = runner.invoke(entries.entry_app, ["create", "", "Test Content"])
    
    assert result.exit_code == 1
    assert "❌ Title cannot be empty." in console_mock.call_args[0][0]
    assert "Invalid input" in caplog.text

def test_create_entry_not_logged_in(mocker: MockerFixture, mock_config):
    """Test create entry when not logged in."""
    mocker.patch("client.auth.get_auth", return_value={})
    console_mock = mocker.patch("client.entries_cli.console.print")
    result = runner.invoke(entries.entry_app, ["create", "Test Title", "Test Content"])
    
    assert result.exit_code == 1
    assert "❌ Please login first." in console_mock.call_args[0][0]

def test_create_entry_http_error(mocker: MockerFixture, mock_config, caplog):
    """Test create entry with HTTP error."""
    caplog.set_level("ERROR")
    mocker.patch("client.auth.get_auth", return_value={"Authorization": "Bearer test_token"})
    with requests_mock.Mocker() as m:
        m.post("http://test-api/entries", json={"error": "Bad request"}, status_code=400)
        handle_error_mock = mocker.patch("client.utils.handle_error")
        result = runner.invoke(entries.entry_app, ["create", "Test Title", "Test Content"])
    
    assert result.exit_code == 1
    handle_error_mock.assert_called_once()
    assert handle_error_mock.call_args[0][0].status_code == 400
    assert handle_error_mock.call_args[0][0].json() == {"error": "Bad request"}
    assert handle_error_mock.call_args[0][2] == "Failed to create entry"
    assert "Failed to create entry" in caplog.text

def test_delete_entry_success(mocker: MockerFixture, mock_config, caplog):
    """Test delete entry successfully."""
    caplog.set_level("INFO")
    mocker.patch("client.auth.get_auth", return_value={"Authorization": "Bearer test_token"})
    with requests_mock.Mocker() as m:
        m.delete("http://test-api/entries/1", json={"message": "Entry deleted successfully"}, status_code=200)
        console_mock = mocker.patch("client.entries_cli.console.print")
        result = runner.invoke(entries.entry_app, ["delete", "1"])
    
    assert result.exit_code == 0
    assert "✅ Entry deleted successfully!" in console_mock.call_args[0][0]
    assert "Deleted entry ID 1" in caplog.text
    assert m.last_request.headers["Authorization"] == "Bearer test_token"
    assert m.last_request.timeout == 5

def test_delete_entry_not_found(mocker: MockerFixture, mock_config, caplog):
    """Test delete entry when entry not found."""
    caplog.set_level("ERROR")
    mocker.patch("client.auth.get_auth", return_value={"Authorization": "Bearer test_token"})
    with requests_mock.Mocker() as m:
        m.delete("http://test-api/entries/1", json={"error": "Not found"}, status_code=404)
        console_mock = mocker.patch("client.entries_cli.console.print")
        result = runner.invoke(entries.entry_app, ["delete", "1"])
    
    assert result.exit_code == 0
    assert "⚠️ Entry not found." in console_mock.call_args[0][0]
    assert "Failed to delete entry" in caplog.text

def test_delete_entry_invalid_id(mocker: MockerFixture, mock_config, caplog):
    """Test delete entry with invalid ID."""
    caplog.set_level("ERROR")
    mocker.patch("client.auth.get_auth", return_value={"Authorization": "Bearer test_token"})
    console_mock = mocker.patch("client.entries_cli.console.print")
    result = runner.invoke(entries.entry_app, ["delete", "invalid"])
    
    assert result.exit_code == 1
    assert "❌ Invalid entry ID. Must be a positive integer." in console_mock.call_args[0][0]
    assert "Invalid input" in caplog.text

def test_delete_entry_not_logged_in(mocker: MockerFixture, mock_config):
    """Test delete entry when not logged in."""
    mocker.patch("client.auth.get_auth", return_value={})
    console_mock = mocker.patch("client.entries_cli.console.print")
    result = runner.invoke(entries.entry_app, ["delete", "1"])
    
    assert result.exit_code == 1
    assert "❌ Please login first." in console_mock.call_args[0][0]

def test_delete_entry_http_error(mocker: MockerFixture, mock_config, caplog):
    """Test delete entry with other HTTP error."""
    caplog.set_level("ERROR")
    mocker.patch("client.auth.get_auth", return_value={"Authorization": "Bearer test_token"})
    with requests_mock.Mocker() as m:
        m.delete("http://test-api/entries/1", json={"error": "Unauthorized"}, status_code=401)
        handle_error_mock = mocker.patch("client.utils.handle_error")
        result = runner.invoke(entries.entry_app, ["delete", "1"])
    
    assert result.exit_code == 1
    handle_error_mock.assert_called_once()
    assert handle_error_mock.call_args[0][0].status_code == 401
    assert handle_error_mock.call_args[0][0].json() == {"error": "Unauthorized"}
    assert handle_error_mock.call_args[0][2] == "Failed to delete entry"
    assert "Failed to delete entry" in caplog.text

def test_update_entry_success(mocker: MockerFixture, mock_config, caplog):
    """Test update entry command success."""
    caplog.set_level("INFO")
    mocker.patch("client.auth.get_auth", return_value={"Authorization": "Bearer test_token"})
    with requests_mock.Mocker() as m:
        m.put(
            "http://test-api/entries/1",
            json={"id": 1, "title": "Updated Title", "content": "Updated Content", "tags": ["tag3"]},
            status_code=200
        )
        console_mock = mocker.patch("client.entries_cli.console.print")
        result = runner.invoke(entries.entry_app, ["update", "1", "Updated Title", "Updated Content", "--tags", "tag3"])
    
    assert result.exit_code == 0
    assert "✅ Entry updated successfully!" in console_mock.call_args[0][0]
    assert "Updated entry ID 1" in caplog.text
    assert m.last_request.json() == {"title": "Updated Title", "content": "Updated Content", "tags": ["tag3"]}
    assert m.last_request.headers["Authorization"] == "Bearer test_token"
    assert m.last_request.timeout == 5

def test_update_entry_no_tags(mocker: MockerFixture, mock_config, caplog):
    """Test update entry without tags."""
    caplog.set_level("INFO")
    mocker.patch("client.auth.get_auth", return_value={"Authorization": "Bearer test_token"})
    with requests_mock.Mocker() as m:
        m.put(
            "http://test-api/entries/1",
            json={"id": 1, "title": "Updated Title", "content": "Updated Content", "tags": []},
            status_code=200
        )
        console_mock = mocker.patch("client.entries_cli.console.print")
        result = runner.invoke(entries.entry_app, ["update", "1", "Updated Title", "Updated Content"])
    
    assert result.exit_code == 0
    assert "✅ Entry updated successfully!" in console_mock.call_args[0][0]
    assert "Updated entry ID 1" in caplog.text
    assert m.last_request.json() == {"title": "Updated Title", "content": "Updated Content", "tags": []}
    assert m.last_request.timeout == 5

def test_update_entry_invalid_input(mocker: MockerFixture, mock_config, caplog):
    """Test update entry with empty title."""
    caplog.set_level("ERROR")
    mocker.patch("client.auth.get_auth", return_value={"Authorization": "Bearer test_token"})
    console_mock = mocker.patch("client.entries_cli.console.print")
    result = runner.invoke(entries.entry_app, ["update", "1", "", "Updated Content"])
    
    assert result.exit_code == 1
    assert "❌ Title cannot be empty." in console_mock.call_args[0][0]
    assert "Invalid input" in caplog.text

def test_update_entry_not_logged_in(mocker: MockerFixture, mock_config):
    """Test update entry when not logged in."""
    mocker.patch("client.auth.get_auth", return_value={})
    console_mock = mocker.patch("client.entries_cli.console.print")
    result = runner.invoke(entries.entry_app, ["update", "1", "Updated Title", "Updated Content"])
    
    assert result.exit_code == 1
    assert "❌ Please login first." in console_mock.call_args[0][0]

def test_update_entry_http_error(mocker: MockerFixture, mock_config, caplog):
    """Test update entry with HTTP error."""
    caplog.set_level("ERROR")
    mocker.patch("client.auth.get_auth", return_value={"Authorization": "Bearer test_token"})
    with requests_mock.Mocker() as m:
        m.put("http://test-api/entries/1", json={"error": "Not found"}, status_code=404)
        handle_error_mock = mocker.patch("client.utils.handle_error")
        result = runner.invoke(entries.entry_app, ["update", "1", "Updated Title", "Updated Content"])
    
    assert result.exit_code == 1
    handle_error_mock.assert_called_once()
    assert handle_error_mock.call_args[0][0].status_code == 404
    assert handle_error_mock.call_args[0][0].json() == {"error": "Not found"}
    assert handle_error_mock.call_args[0][2] == "Failed to update entry"
    assert "Failed to update entry" in caplog.text