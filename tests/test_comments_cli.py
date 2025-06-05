"""Tests for client/comments_cli.py."""
import pytest
import requests
from typer.testing import CliRunner
from client.comments_cli import comment_app
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

def test_list_comments_success(mock_token, requests_mock):
    """Test listing comments successfully."""
    requests_mock.get(
        f"{config.API_URL}/journal_entries/1/comments",
        json=[{"id": 1, "content": "Test comment", "timestamp": "2025-06-05"}],
        status_code=200
    )
    result = runner.invoke(comment_app, ["list", "1"])
    assert result.exit_code == 0
    assert "Comment ID: 1" in result.stdout
    assert "Content: Test comment" in result.stdout
    assert "Timestamp: 2025-06-05" in result.stdout

def test_list_comments_empty(mock_token, requests_mock):
    """Test listing comments when none exist."""
    requests_mock.get(
        f"{config.API_URL}/journal_entries/1/comments",
        json=[],
        status_code=200
    )
    result = runner.invoke(comment_app, ["list", "1"])
    assert result.exit_code == 0
    assert "No comments found" in result.stdout

def test_list_comments_no_token(mock_no_token):
    """Test listing comments without a token."""
    result = runner.invoke(comment_app, ["list", "1"])
    assert result.exit_code == 1
    assert "You must login first" in result.stdout

def test_list_comments_api_error(mock_token, requests_mock):
    """Test listing comments with API error."""
    requests_mock.get(
        f"{config.API_URL}/journal_entries/1/comments",
        json={"error": "Not found"},
        status_code=404
    )
    result = runner.invoke(comment_app, ["list", "1"])
    assert result.exit_code == 1
    assert "Error: Not found" in result.stdout

def test_add_comment_success(mock_token, requests_mock):
    """Test adding a comment successfully."""
    requests_mock.post(
        f"{config.API_URL}/journal_entries/1/comments",
        json={"id": 1, "content": "New comment"},
        status_code=201
    )
    result = runner.invoke(comment_app, ["add", "1", "New comment"])
    assert result.exit_code == 0
    assert "Comment added" in result.stdout

def test_add_comment_no_token(mock_no_token):
    """Test adding a comment without a token."""
    result = runner.invoke(comment_app, ["add", "1", "New comment"])
    assert result.exit_code == 1
    assert "You must login first" in result.stdout

def test_add_comment_empty_content(mock_token):
    """Test adding a comment with empty content."""
    result = runner.invoke(comment_app, ["add", "1", ""])
    assert result.exit_code == 1
    assert "Content cannot be empty" in result.stdout

def test_add_comment_api_error(mock_token, requests_mock):
    """Test adding a comment with API error."""
    requests_mock.post(
        f"{config.API_URL}/journal_entries/1/comments",
        json={"error": "Invalid entry"},
        status_code=400
    )
    result = runner.invoke(comment_app, ["add", "1", "New comment"])
    assert result.exit_code == 1
    assert "Error: Invalid entry" in result.stdout

def test_add_comment_validation_error(mock_token, requests_mock):
    """Test adding a comment with validation error."""
    requests_mock.post(
        f"{config.API_URL}/journal_entries/1/comments",
        json={"errors": ["Content too short"]},
        status_code=400
    )
    result = runner.invoke(comment_app, ["add", "1", "Short"])
    assert result.exit_code == 1
    assert "Validation Error: ['Content too short']" in result.stdout

def test_add_comment_unexpected_error(mock_token, requests_mock):
    """Test adding a comment with unexpected error."""
    requests_mock.post(
        f"{config.API_URL}/journal_entries/1/comments",
        json={"message": "Server error"},
        status_code=500
    )
    result = runner.invoke(comment_app, ["add", "1", "New comment"])
    assert result.exit_code == 1
    assert "Error: {'message': 'Server error'}" in result.stdout

def test_update_comment_success(mock_token, requests_mock):
    """Test updating a comment successfully."""
    requests_mock.put(
        f"{config.API_URL}/journal_entries/1/comments/1",
        json={"id": 1, "content": "Updated comment"},
        status_code=200
    )
    result = runner.invoke(comment_app, ["update", "1", "1", "Updated comment"])
    assert result.exit_code == 0
    assert "Comment updated" in result.stdout

def test_update_comment_no_token(mock_no_token):
    """Test updating a comment without a token."""
    result = runner.invoke(comment_app, ["update", "1", "1", "Updated comment"])
    assert result.exit_code == 1
    assert "You must login first" in result.stdout

def test_update_comment_api_error(mock_token, requests_mock):
    """Test updating a comment with API error."""
    requests_mock.put(
        f"{config.API_URL}/journal_entries/1/comments/1",
        json={"error": "Comment not found"},
        status_code=404
    )
    result = runner.invoke(comment_app, ["update", "1", "1", "Updated comment"])
    assert result.exit_code == 1
    assert "Error: Comment not found" in result.stdout

def test_delete_comment_success(mock_token, requests_mock):
    """Test deleting a comment successfully."""
    requests_mock.delete(
        f"{config.API_URL}/journal_entries/1/comments/1",
        status_code=200
    )
    result = runner.invoke(comment_app, ["delete", "1", "1"])
    assert result.exit_code == 0
    assert "Comment deleted" in result.stdout

def test_delete_comment_no_token(mock_no_token):
    """Test deleting a comment without a token."""
    result = runner.invoke(comment_app, ["delete", "1", "1"])
    assert result.exit_code == 1
    assert "You must login first" in result.stdout

def test_delete_comment_api_error(mock_token, requests_mock):
    """Test deleting a comment with API error."""
    requests_mock.delete(
        f"{config.API_URL}/journal_entries/1/comments/1",
        json={"error": "Comment not found"},
        status_code=404
    )
    result = runner.invoke(comment_app, ["delete", "1", "1"])
    assert result.exit_code == 1
    assert "Error: Comment not found" in result.stdout
