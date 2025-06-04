"""Tests for CLI end-to-end flow."""
import os
import pytest
import time
from typer.testing import CliRunner
from unittest.mock import patch
from client.main import app as cli_app
from journalapi.models import User, JournalEntry, Comment

def test_cli_end_to_end(client, app, db_session, tmp_path, monkeypatch):
    """Test the full CLI workflow: register, login, create entry, comment, list.
    
    Args:
        client: Flask test client.
        app: Flask application instance.
        db_session: SQLAlchemy database session.
        tmp_path: Temporary directory for token file.
        monkeypatch: Pytest monkeypatch fixture for mocking.
    """
    runner = CliRunner()
    email = f"foo_{int(time.time())}@example.com"
    token_file = tmp_path / ".journal_token"
    os.environ["TOKEN_FILE"] = str(token_file)

    # Mock requests to use test client
    def mock_requests(method, url, **kwargs):
        class MockResponse:
            def __init__(self, response):
                self.status_code = response.status_code
                self.json_data = response.json()
            def json(self):
                return self.json_data

        if method.lower() == "post":
            response = client.post(url.replace("http://localhost:5000", ""), json=kwargs.get("json"), headers=kwargs.get("headers"))
        elif method.lower() == "get":
            response = client.get(url.replace("http://localhost:5000", ""), headers=kwargs.get("headers"))
        elif method.lower() == "put":
            response = client.put(url.replace("http://localhost:5000", ""), json=kwargs.get("json"), headers=kwargs.get("headers"))
        elif method.lower() == "delete":
            response = client.delete(url.replace("http://localhost:5000", ""), headers=kwargs.get("headers"))
        return MockResponse(response)

    with patch("requests.post", side_effect=mock_requests), \
         patch("requests.get", side_effect=mock_requests), \
         patch("requests.put", side_effect=mock_requests), \
         patch("requests.delete", side_effect=mock_requests):

        # Register
        result = runner.invoke(cli_app, [
            "auth", "register",
            "--username", "foo",
            "--email", email,
            "--password", "testpass123"
        ])
        assert result.exit_code == 0
        assert "✅ Registered!" in result.output

        # Invalid registration (duplicate email)
        result = runner.invoke(cli_app, [
            "auth", "register",
            "--username", "foo2",
            "--email", email,
            "--password", "testpass123"
        ])
        assert result.exit_code == 0
        assert "Validation Error" in result.output

        # Login
        result = runner.invoke(cli_app, [
            "auth", "login",
            "--email", email,
            "--password", "testpass123"
        ])
        assert result.exit_code == 0
        assert "✅ Logged in" in result.output
        assert token_file.exists()

        # Invalid login
        result = runner.invoke(cli_app, [
            "auth", "login",
            "--email", email,
            "--password", "wrongpassword"
        ])
        assert result.exit_code == 0
        assert "Login failed" in result.output

        # Create entry
        result = runner.invoke(cli_app, [
            "entry", "create",
            "First Post", "This is my first journal.",
            "--tags", "test,cli"
        ])
        assert result.exit_code == 0
        assert "✅ Entry created successfully!" in result.output

        # Invalid entry (empty title)
        result = runner.invoke(cli_app, [
            "entry", "create",
            "", "Invalid entry.",
            "--tags", "invalid"
        ])
        assert result.exit_code == 1

        # List entries
        result = runner.invoke(cli_app, ["entry", "list"])
        assert result.exit_code == 0
        assert "First Post" in result.output

        # Extract entry ID
        with app.app_context():
            user = db_session.session.query(User).filter_by(email=email).first()
            entry = user.entries[0]
            entry_id = entry.id

        # Add comment
        result = runner.invoke(cli_app, ["comment", "add", str(entry_id), "hello!"])
        assert result.exit_code == 0
        assert "✅ Comment added" in result.output

        # Invalid comment (empty content)
        result = runner.invoke(cli_app, ["comment", "add", str(entry_id), ""])
        assert result.exit_code == 0
        assert "Validation Error" in result.output

        # List comments
        result = runner.invoke(cli_app, ["comment", "list", str(entry_id)])
        assert result.exit_code == 0
        assert "hello!" in result.output

        # Non-existent entry
        result = runner.invoke(cli_app, ["comment", "list", str(entry_id + 1)])
        assert result.exit_code == 0
        assert "not found" in result.output.lower()

        # Delete entry
        result = runner.invoke(cli_app, ["entry", "delete", str(entry_id)])
        assert result.exit_code == 0
        assert "✅ Entry deleted successfully" in result.output
        with app.app_context():
            assert db_session.session.query(JournalEntry).get(entry_id) is None

        # Logout
        result = runner.invoke(cli_app, ["auth", "logout"])
        assert result.exit_code == 0
        assert "🔓 Logged out" in result.output
        assert not token_file.exists()