import pytest
import requests
import requests_mock
from pytest_mock import MockerFixture
from typer.testing import CliRunner
from client import comments_cli, auth

runner = CliRunner()

@pytest.fixture
def mock_config(mocker: MockerFixture):
    """Mock config settings."""
    mocker.patch("client.config.API_URL", "http://test-api")
    mocker.patch("client.config.REQUEST_TIMEOUT", 5)

def test_list_comments_success(mocker: MockerFixture, mock_config, caplog):
    """Test list_comments command success."""
    caplog.set_level("INFO")
    mocker.patch("client.comments_cli.ensure_auth", return_value={"Authorization": "Bearer test_token"})
    with requests_mock.Mocker() as m:
        m.get(
            "http://test-api/journal_entries/1/comments",
            json=[{"id": 1, "content": "Great!", "user_id": 1}],
            status_code=200,
        )
        mocker.patch("client.comments_cli.console.print")
        result = runner.invoke(comments_cli.comment_app, ["list", "1"])
    assert result.exit_code == 0
    assert "[1] Great! (by user 1)" in comments_cli.console.print.call_args[0][0]
    assert "Listed comments for entry ID 1" in caplog.text

def test_list_comments_empty(mocker: MockerFixture, mock_config, caplog):
    """Test list_comments when no comments exist."""
    caplog.set_level("INFO")
    mocker.patch("client.comments_cli.ensure_auth", return_value={"Authorization": "Bearer test_token"})
    with requests_mock.Mocker() as m:
        m.get("http://test-api/journal_entries/1/comments", json=[], status_code=200)
        mocker.patch("client.comments_cli.console.print")
        result = runner.invoke(comments_cli.comment_app, ["list", "1"])
    assert result.exit_code == 0
    assert "⚠️ No comments found." in comments_cli.console.print.call_args[0][0]
    assert "Listed comments for entry ID 1" in caplog.text

def test_list_comments_http_error(mocker: MockerFixture, mock_config, caplog):
    """Test list_comments with HTTP error."""
    caplog.set_level("ERROR")
    mocker.patch("client.comments_cli.ensure_auth", return_value={"Authorization": "Bearer test_token"})
    with requests_mock.Mocker() as m:
        m.get("http://test-api/journal_entries/1/comments", json={"error": "Not found"}, status_code=404)
        mocker.patch("client.utils.handle_error")
        result = runner.invoke(comments_cli.comment_app, ["list", "1"])
    assert result.exit_code == 0
    comments_cli.utils.handle_error.assert_called_once()
    assert comments_cli.utils.handle_error.call_args[0][2] == "Failed to list comments"

def test_add_comment_success(mocker: MockerFixture, mock_config, caplog):
    """Test add_comment command success."""
    caplog.set_level("INFO")
    mocker.patch("client.comments_cli.ensure_auth", return_value={"Authorization": "Bearer test_token"})
    with requests_mock.Mocker() as m:
        m.post("http://test-api/journal_entries/1/comments", json={}, status_code=201)
        mocker.patch("client.comments_cli.console.print")
        result = runner.invoke(comments_cli.comment_app, ["add", "1", "Great post!"])
    assert result.exit_code == 0
    assert "✅ Comment added successfully!" in comments_cli.console.print.call_args[0][0]
    assert "Added comment to entry ID 1" in caplog.text

def test_add_comment_http_error(mocker: MockerFixture, mock_config, caplog):
    """Test add_comment with HTTP error."""
    caplog.set_level("ERROR")
    mocker.patch("client.comments_cli.ensure_auth", return_value={"Authorization": "Bearer test_token"})
    with requests_mock.Mocker() as m:
        m.post("http://test-api/journal_entries/1/comments", json={"error": "Unauthorized"}, status_code=401)
        mocker.patch("client.utils.handle_error")
        result = runner.invoke(comments_cli.comment_app, ["add", "1", "Great post!"])
    assert result.exit_code == 0
    comments_cli.utils.handle_error.assert_called_once()
    assert comments_cli.utils.handle_error.call_args[0][2] == "Failed to add comment"

def test_delete_comment_success(mocker: MockerFixture, mock_config, caplog):
    """Test delete_comment command success."""
    caplog.set_level("INFO")
    mocker.patch("client.comments_cli.ensure_auth", return_value={"Authorization": "Bearer test_token"})
    with requests_mock.Mocker() as m:
        m.delete("http://test-api/journal_entries/1/comments/1", json={}, status_code=200)
        mocker.patch("client.comments_cli.console.print")
        result = runner.invoke(comments_cli.comment_app, ["delete", "1", "1"])
    assert result.exit_code == 0
    assert "✅ Comment deleted successfully!" in comments_cli.console.print.call_args[0][0]
    assert "Deleted comment ID 1 from entry ID 1" in caplog.text

def test_delete_comment_http_error(mocker: MockerFixture, mock_config, caplog):
    """Test delete_comment with HTTP error."""
    caplog.set_level("ERROR")
    mocker.patch("client.comments_cli.ensure_auth", return_value={"Authorization": "Bearer test_token"})
    with requests_mock.Mocker() as m:
        m.delete("http://test-api/journal_entries/1/comments/1", json={"error": "Not found"}, status_code=404)
        mocker.patch("client.utils.handle_error")
        result = runner.invoke(comments_cli.comment_app, ["delete", "1", "1"])
    assert result.exit_code == 0
    comments_cli.utils.handle_error.assert_called_once()
    assert comments_cli.utils.handle_error.call_args[0][2] == "Failed to delete comment"