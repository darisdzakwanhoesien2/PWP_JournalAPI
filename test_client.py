import json
import os
from pathlib import Path
import pytest
from typer.testing import CliRunner
# import requests_mock
from client.auth import save_token, get_token, clear_token, get_auth
from client.auth_cli import auth_app
from client.comments_cli import comment_app
from client.entries_cli import entry_app
from client.utils import handle_error
from client.main import app
from rich.console import Console

# Initialize CliRunner for testing Typer commands
runner = CliRunner()

# Mock config values to isolate tests from environment
@pytest.fixture(autouse=True)
def setup_config(mocker):
    """Mock configuration values from config.py."""
    mocker.patch("client.config.API_URL", "http://mockapi/api")
    mocker.patch("client.config.TOKEN_FILE", "temp_token.json")
    mocker.patch("client.config.REQUEST_TIMEOUT", 5)
    yield

@pytest.fixture
def console():
    """Provide a Console instance for capturing output."""
    return Console(record=True)

# Tests for auth.py
def test_save_token(tmp_path, mocker):
    """Test saving a JWT token to a file."""
    token_file = tmp_path / "token.json"
    mocker.patch("client.auth.TOKEN_FILE", str(token_file))
    
    save_token("test-token")
    assert token_file.exists()
    with open(token_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["token"] == "test-token"
    assert "saved_at" in data

def test_save_token_error(tmp_path, mocker, caplog):
    """Test error handling when saving token fails."""
    token_file = tmp_path / "readonly" / "token.json"
    mocker.patch("client.auth.TOKEN_FILE", str(token_file))
    # Simulate read-only directory by not creating parent
    with pytest.raises(OSError):
        save_token("test-token")
    assert "Failed to save token" in caplog.text

def test_get_token(tmp_path, mocker):
    """Test retrieving a saved JWT token."""
    token_file = tmp_path / "token.json"
    mocker.patch("client.auth.TOKEN_FILE", str(token_file))
    with open(token_file, "w", encoding="utf-8") as f:
        json.dump({"token": "test-token", "saved_at": 1234567890}, f)
    
    token = get_token()
    assert token == "test-token"

def test_get_token_not_found(tmp_path, mocker, caplog):
    """Test retrieving token when file doesn't exist."""
    token_file = tmp_path / "nonexistent.json"
    mocker.patch("client.auth.TOKEN_FILE", str(token_file))
    token = get_token()
    assert token is None
    assert "Token file not found" in caplog.text

def test_get_token_corrupted(tmp_path, mocker, caplog):
    """Test retrieving token from a corrupted file."""
    token_file = tmp_path / "corrupted.json"
    mocker.patch("client.auth.TOKEN_FILE", str(token_file))
    with open(token_file, "w", encoding="utf-8") as f:
        f.write("not json")
    
    token = get_token()
    assert token is None
    assert "Failed to read token" in caplog.text

def test_clear_token(tmp_path, mocker):
    """Test clearing a saved token."""
    token_file = tmp_path / "token.json"
    mocker.patch("client.auth.TOKEN_FILE", str(token_file))
    token_file.write_text("{}", encoding="utf-8")
    
    clear_token()
    assert not token_file.exists()

def test_clear_token_not_found(tmp_path, mocker, caplog):
    """Test clearing a non-existent token."""
    token_file = tmp_path / "nonexistent.json"
    mocker.patch("client.auth.TOKEN_FILE", str(token_file))
    clear_token()
    assert "Token file not found" in caplog.text

def test_get_auth_with_token(tmp_path, mocker):
    """Test generating auth headers with a token."""
    token_file = tmp_path / "token.json"
    mocker.patch("client.auth.TOKEN_FILE", str(token_file))
    with open(token_file, "w", encoding="utf-8") as f:
        json.dump({"token": "test-token"}, f)
    
    headers = get_auth()
    assert headers == {"Authorization": "Bearer test-token"}

def test_get_auth_no_token(tmp_path, mocker):
    """Test generating auth headers with no token."""
    token_file = tmp_path / "nonexistent.json"
    mocker.patch("client.auth.TOKEN_FILE", str(token_file))
    headers = get_auth()
    assert headers == {}

# Tests for auth_cli.py
def test_register_success(requests_mock, console):
    """Test successful user registration."""
    requests_mock.post(
        "http://mockapi/api/users/register",
        json={"message": "User registered successfully", "_links": {"self": "/api/users/1"}},
        status_code=201
    )
    
    result = runner.invoke(auth_app, ["register", "-u", "testuser", "-e", "test@example.com", "-p", "testpass123"])
    assert result.exit_code == 0
    assert "✅ Registered successfully!" in console.getvalue()

def test_register_failure(requests_mock, console):
    """Test registration failure due to duplicate email."""
    requests_mock.post(
        "http://mockapi/api/users/register",
        json={"error": "Email already registered"},
        status_code=400
    )
    
    result = runner.invoke(auth_app, ["register", "-u", "testuser", "-e", "test@example.com", "-p", "testpass123"])
    assert result.exit_code == 1
    assert "Registration failed: Email already registered" in console.getvalue()

def test_login_success(tmp_path, mocker, requests_mock, console):
    """Test successful login and token storage."""
    token_file = tmp_path / "token.json"
    mocker.patch("client.auth.TOKEN_FILE", str(token_file))
    requests_mock.post(
        "http://mockapi/api/users/login",
        json={"token": "test-token", "_links": {"self": "/api/users/1"}},
        status_code=200
    )
    
    result = runner.invoke(auth_app, ["login", "-e", "test@example.com", "-p", "testpass123"])
    assert result.exit_code == 0
    assert "✅ Logged in successfully!" in console.getvalue()
    assert token_file.exists()
    with open(token_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["token"] == "test-token"

def test_login_failure(requests_mock, console):
    """Test login failure due to invalid credentials."""
    requests_mock.post(
        "http://mockapi/api/users/login",
        json={"error": "Invalid credentials"},
        status_code=401
    )
    
    result = runner.invoke(auth_app, ["login", "-e", "test@example.com", "-p", "wrongpass"])
    assert result.exit_code == 1
    assert "Login failed: Invalid credentials" in console.getvalue()

def test_logout(tmp_path, mocker, console):
    """Test logout by clearing token."""
    token_file = tmp_path / "token.json"
    mocker.patch("client.auth.TOKEN_FILE", str(token_file))
    token_file.write_text("{}", encoding="utf-8")
    
    result = runner.invoke(auth_app, ["logout"])
    assert result.exit_code == 0
    assert "🔓 Logged out successfully!" in console.getvalue()
    assert not token_file.exists()

def test_me_logged_in(tmp_path, mocker, console):
    """Test 'me' command when logged in."""
    token_file = tmp_path / "token.json"
    mocker.patch("client.auth.TOKEN_FILE", str(token_file))
    with open(token_file, "w", encoding="utf-8") as f:
        json.dump({"token": "test-token"}, f)
    
    result = runner.invoke(auth_app, ["me"])
    assert result.exit_code == 0
    assert "🔐 Logged in" in console.getvalue()

def test_me_not_logged_in(tmp_path, mocker, console):
    """Test 'me' command when not logged in."""
    token_file = tmp_path / "nonexistent.json"
    mocker.patch("client.auth.TOKEN_FILE", str(token_file))
    
    result = runner.invoke(auth_app, ["me"])
    assert result.exit_code == 0
    assert "🔓 Not logged in" in console.getvalue()

# Tests for comments_cli.py
def test_list_comments_success(tmp_path, mocker, requests_mock, console):
    """Test listing comments for a journal entry."""
    token_file = tmp_path / "token.json"
    mocker.patch("client.auth.TOKEN_FILE", str(token_file))
    with open(token_file, "w", encoding="utf-8") as f:
        json.dump({"token": "test-token"}, f)
    
    requests_mock.get(
        "http://mockapi/api/journal_entries/1/comments",
        json=[
            {"id": 1, "content": "Test comment", "user_id": 1},
            {"id": 2, "content": "Another comment", "user_id": 2}
        ],
        status_code=200
    )
    
    result = runner.invoke(comment_app, ["list", "1"])
    assert result.exit_code == 0
    output = console.getvalue()
    assert "[1] Test comment (by user 1)" in output
    assert "[2] Another comment (by user 2)" in output

def test_list_comments_empty(tmp_path, mocker, requests_mock, console):
    """Test listing comments when none exist."""
    token_file = tmp_path / "token.json"
    mocker.patch("client.auth.TOKEN_FILE", str(token_file))
    with open(token_file, "w", encoding="utf-8") as f:
        json.dump({"token": "test-token"}, f)
    
    requests_mock.get(
        "http://mockapi/api/journal_entries/1/comments",
        json=[],
        status_code=200
    )
    
    result = runner.invoke(comment_app, ["list", "1"])
    assert result.exit_code == 0
    assert "⚠️ No comments found." in console.getvalue()

def test_list_comments_unauthenticated(tmp_path, mocker, console):
    """Test listing comments without authentication."""
    token_file = tmp_path / "nonexistent.json"
    mocker.patch("client.auth.TOKEN_FILE", str(token_file))
    
    result = runner.invoke(comment_app, ["list", "1"])
    assert result.exit_code == 1
    assert "Please login first" in console.getvalue()

def test_add_comment_success(tmp_path, mocker, requests_mock, console):
    """Test adding a comment to a journal entry."""
    token_file = tmp_path / "token.json"
    mocker.patch("client.auth.TOKEN_FILE", str(token_file))
    with open(token_file, "w", encoding="utf-8") as f:
        json.dump({"token": "test-token"}, f)
    
    requests_mock.post(
        "http://mockapi/api/journal_entries/1/comments",
        json={"id": 1, "_links": {"self": "/api/journal_entries/1/comments/1"}},
        status_code=201
    )
    
    result = runner.invoke(comment_app, ["add", "1", "Test comment"])
    assert result.exit_code == 0
    assert "✅ Comment added successfully!" in console.getvalue()

def test_add_comment_failure(tmp_path, mocker, requests_mock, console):
    """Test adding a comment with invalid entry ID."""
    token_file = tmp_path / "token.json"
    mocker.patch("client.auth.TOKEN_FILE", str(token_file))
    with open(token_file, "w", encoding="utf-8") as f:
        json.dump({"token": "test-token"}, f)
    
    requests_mock.post(
        "http://mockapi/api/journal_entries/999/comments",
        json={"error": "Entry not found"},
        status_code=404
    )
    
    result = runner.invoke(comment_app, ["add", "999", "Test comment"])
    assert result.exit_code == 1
    assert "Failed to add comment: Entry not found" in console.getvalue()

def test_delete_comment_success(tmp_path, mocker, requests_mock, console):
    """Test deleting a comment."""
    token_file = tmp_path / "token.json"
    mocker.patch("client.auth.TOKEN_FILE", str(token_file))
    with open(token_file, "w", encoding="utf-8") as f:
        json.dump({"token": "test-token"}, f)
    
    requests_mock.delete(
        "http://mockapi/api/journal_entries/1/comments/1",
        json={"message": "Comment deleted successfully"},
        status_code=200
    )
    
    result = runner.invoke(comment_app, ["delete", "1", "1"])
    assert result.exit_code == 0
    assert "✅ Comment deleted successfully!" in console.getvalue()

def test_delete_comment_failure(tmp_path, mocker, requests_mock, console):
    """Test deleting a non-existent comment."""
    token_file = tmp_path / "token.json"
    mocker.patch("client.auth.TOKEN_FILE", str(token_file))
    with open(token_file, "w", encoding="utf-8") as f:
        json.dump({"token": "test-token"}, f)
    
    requests_mock.delete(
        "http://mockapi/api/journal_entries/1/comments/999",
        json={"error": "Not found or unauthorized"},
        status_code=403
    )
    
    result = runner.invoke(comment_app, ["delete", "1", "999"])
    assert result.exit_code == 1
    assert "Failed to delete comment: Not found or unauthorized" in console.getvalue()

# Tests for entries_cli.py
def test_list_entries_success(tmp_path, mocker, requests_mock, console):
    """Test listing journal entries."""
    token_file = tmp_path / "token.json"
    mocker.patch("client.auth.TOKEN_FILE", str(token_file))
    with open(token_file, "w", encoding="utf-8") as f:
        json.dump({"token": "test-token"}, f)
    
    requests_mock.get(
        "http://mockapi/api/entries",
        json=[
            {"id": 1, "title": "Entry 1", "tags": ["tag1"], "last_updated": "2025-06-03T12:00:00Z"},
            {"id": 2, "title": "Entry 2", "tags": ["tag2"], "last_updated": "2025-06-03T12:01:00Z"}
        ],
        status_code=200
    )
    
    result = runner.invoke(entry_app, ["list"])
    assert result.exit_code == 0
    output = console.getvalue()
    assert "[1] Entry 1 - Tags: tag1" in output
    assert "[2] Entry 2 - Tags: tag2" in output

def test_list_entries_empty(tmp_path, mocker, requests_mock, console):
    """Test listing entries when none exist."""
    token_file = tmp_path / "token.json"
    mocker.patch("client.auth.TOKEN_FILE", str(token_file))
    with open(token_file, "w", encoding="utf-8") as f:
        json.dump({"token": "test-token"}, f)
    
    requests_mock.get(
        "http://mockapi/api/entries",
        json=[],
        status_code=200
    )
    
    result = runner.invoke(entry_app, ["list"])
    assert result.exit_code == 0
    assert "⚠️ No journal entries found." in console.getvalue()

def test_list_entries_unauthenticated(tmp_path, mocker, console):
    """Test listing entries without authentication."""
    token_file = tmp_path / "nonexistent.json"
    mocker.patch("client.auth.TOKEN_FILE", str(token_file))
    
    result = runner.invoke(entry_app, ["list"])
    assert result.exit_code == 1
    assert "❌ Please login first." in console.getvalue()

def test_create_entry_success(tmp_path, mocker, requests_mock, console):
    """Test creating a journal entry."""
    token_file = tmp_path / "token.json"
    mocker.patch("client.auth.TOKEN_FILE", str(token_file))
    with open(token_file, "w", encoding="utf-8") as f:
        json.dump({"token": "test-token"}, f)
    
    requests_mock.post(
        "http://mockapi/api/entries",
        json={"id": 1, "_links": {"self": "/api/entries/1"}},
        status_code=201
    )
    
    result = runner.invoke(entry_app, ["create", "Test Entry", "Test content", "--tags", "tag1,tag2"])
    assert result.exit_code == 0
    assert "✅ Entry created successfully!" in console.getvalue()

def test_create_entry_unauthenticated(tmp_path, mocker, console):
    """Test creating an entry without authentication."""
    token_file = tmp_path / "nonexistent.json"
    mocker.patch("client.auth.TOKEN_FILE", str(token_file))
    
    result = runner.invoke(entry_app, ["create", "Test Entry", "Test content"])
    assert result.exit_code == 1
    assert "❌ Please login first." in console.getvalue()

def test_delete_entry_success(tmp_path, mocker, requests_mock, console):
    """Test deleting a journal entry."""
    token_file = tmp_path / "token.json"
    mocker.patch("client.auth.TOKEN_FILE", str(token_file))
    with open(token_file, "w", encoding="utf-8") as f:
        json.dump({"token": "test-token"}, f)
    
    requests_mock.delete(
        "http://mockapi/api/entries/1",
        json={"message": "Entry deleted successfully"},
        status_code=200
    )
    
    result = runner.invoke(entry_app, ["delete", "1"])
    assert result.exit_code == 0
    assert "✅ Entry deleted successfully!" in console.getvalue()

def test_delete_entry_not_found(tmp_path, mocker, requests_mock, console):
    """Test deleting a non-existent entry."""
    token_file = tmp_path / "token.json"
    mocker.patch("client.auth.TOKEN_FILE", str(token_file))
    with open(token_file, "w", encoding="utf-8") as f:
        json.dump({"token": "test-token"}, f)
    
    requests_mock.delete(
        "http://mockapi/api/entries/999",
        json={"error": "Not found or unauthorized"},
        status_code=404
    )
    
    result = runner.invoke(entry_app, ["delete", "999"])
    assert result.exit_code == 0
    assert "⚠️ Entry not found." in console.getvalue()

# Tests for utils.py
def test_handle_error_json(requests_mock, console, caplog):
    """Test handling HTTP error with JSON response."""
    response = requests_mock.post(
        "http://mockapi/api/test",
        json={"error": "Test error"},
        status_code=400
    )
    handle_error(response, requests_mock.HTTPError(), "Test operation failed")
    assert "❌ Test operation failed: Test error" in console.getvalue()
    assert "Test operation failed: {'error': 'Test error'}" in caplog.text

def test_handle_error_non_json(requests_mock, console, caplog):
    """Test handling HTTP error with non-JSON response."""
    response = requests_mock.post(
        "http://mockapi/api/test",
        text="Server error",
        status_code=500
    )
    handle_error(response, requests_mock.HTTPError(), "Test operation failed")
    assert "❌ Server error: Server error" in console.getvalue()
    assert "Test operation failed: Server error" in caplog.text

# Tests for main.py
def test_main_app_help():
    """Test the main CLI app help message."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "PWP Journal API CLI - Manage your journal entries" in result.output
    assert "auth  Manage user authentication" in result.output
    assert "entry  Manage journal entries" in result.output
    assert "comment  Manage comments" in result.output

# Note: config.py is tested indirectly through mocked configuration values above.