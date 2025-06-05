"""Tests for client/entries_cli.py."""
import pytest
import requests
from typer.testing import CliRunner
from client.entries_cli import entry_app
from client import auth, config

runner = CliRunner()

@pytest.fixture
def mock_token():
    """Mock a valid token."""
    with pytest.MonkeyPatch.context() as m:
        m.setattr(auth, "get_token", lambda: "valid_token")
        yield

@pytest.fixture
def mock_no_token():
    """Mock no token."""
    with pytest.MonkeyPatch.context() as m:
        m.setattr(auth, "get_token", lambda: None)
        yield

def test_list_entries_success(mock_token, requests_mock):
    """Test listing entries successfully."""
    requests_mock.get(
        f"{config.API_URL}/journal_entries",
        json=[{"id": 1, "title": "Test Entry", "tags": ["test"], "last_updated": "2025-06-05"}],
        status_code=200
    )
    result = runner.invoke(entry_app, ["list"])
    assert result.exit_code == 0
    assert "[1] Test Entry - Tags: ['test']" in result.stdout
    assert "Last updated: 2025-06-05" in result.stdout

def test_list_entries_empty(mock_token, requests_mock):
    """Test listing entries when none exist."""
    requests_mock.get(
        f"{config.API_URL}/journal_entries",
        json=[],
        status_code=200
    )
    result = runner.invoke(entry_app, ["list"])
    assert result.exit_code == 0
    assert "No journal entries found" in result.stdout

def test_list_entries_no_token(mock_no_token):
    """Test listing entries without a token."""
    result = runner.invoke(entry_app, ["list"])
    assert result.exit_code == 1
    assert "You must login first" in result.stdout

def test_list_entries_api_error(mock_token, requests_mock):
    """Test listing entries with API error."""
    requests_mock.get(
        f"{config.API_URL}/journal_entries",
        json={"error": "Unauthorized"},
        status_code=401
    )
    result = runner.invoke(entry_app, ["list"])
    assert result.exit_code == 1
    assert "Error: Unauthorized" in result.stdout

def test_create_entry_success(mock_token, requests_mock):
    """Test creating an entry successfully."""
    requests_mock.post(
        f"{config.API_URL}/journal_entries",
        json={"id": 1, "title": "New Entry", "content": "Content", "tags": ["test"]},
        status_code=201
    )
    result = runner.invoke(entry_app, ["create", "New Entry", "Content", "--tags", "test"])
    assert result.exit_code == 0
    assert "Entry created successfully" in result.stdout

def test_create_entry_no_token(mock_no_token):
    """Test creating an entry without a token."""
    result = runner.invoke(entry_app, ["create", "New Entry", "Content"])
    assert result.exit_code == 1
    assert "You must login first" in result.stdout

def test_create_entry_empty_title(mock_token):
    """Test creating an entry with empty title."""
    result = runner.invoke(entry_app, ["create", "", "Content"])
    assert result.exit_code == 1
    assert "Title cannot be empty" in result.stdout

def test_create_entry_api_error(mock_token, requests_mock):
    """Test creating an entry with API error."""
    requests_mock.post(
        f"{config.API_URL}/journal_entries",
        json={"error": "Invalid data"},
        status_code=400
    )
    result = runner.invoke(entry_app, ["create", "New Entry", "Content"])
    assert result.exit_code == 1
    assert "Error: Invalid data" in result.stdout

def test_delete_entry_success(mock_token, requests_mock):
    """Test deleting an entry successfully."""
    requests_mock.delete(
        f"{config.API_URL}/journal_entries/1",
        status_code=200
    )
    result = runner.invoke(entry_app, ["delete", "1"])
    assert result.exit_code == 0
    assert "Entry deleted successfully" in result.stdout

def test_delete_entry_no_token(mock_no_token):
    """Test deleting an entry without a token."""
    result = runner.invoke(entry_app, ["delete", "1"])
    assert result.exit_code == 1
    assert "You must login first" in result.stdout

def test_delete_entry_not_found(mock_token, requests_mock):
    """Test deleting an entry that does not exist."""
    requests_mock.delete(
        f"{config.API_URL}/journal_entries/1",
        json={"error": "Entry not found"},
        status_code=404
    )
    result = runner.invoke(entry_app, ["delete", "1"])
    assert result.exit_code == 0
    assert "Entry not found" in result.stdout

def test_delete_entry_api_error(mock_token, requests_mock):
    """Test deleting an entry with other API error."""
    requests_mock.delete(
        f"{config.API_URL}/journal_entries/1",
        json={"error": "Unauthorized"},
        status_code=401
    )
    result = runner.invoke(entry_app, ["delete", "1"])
    assert result.exit_code == 1
    assert "Error: Unauthorized" in result.stdout