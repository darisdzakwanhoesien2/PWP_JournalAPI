import pytest
import requests
from client import auth, config
from client.auth_cli import auth_app
from typer.testing import CliRunner


@pytest.fixture
def runner():
    return CliRunner()

def test_register_success(runner, monkeypatch):
    def mock_post(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def json(self):
                return self.json_data

            def raise_for_status(self):
                if self.status_code >= 400:
                    raise requests.exceptions.HTTPError("Request failed", response=self)
        return MockResponse({"message": "User registered successfully"}, 201)

    monkeypatch.setattr(requests, "post", mock_post)
    result = runner.invoke(auth_app, ["register", "--username", "testuser", "--email", "test@example.com", "--password", "password123"])
    assert result.exit_code == 0
    assert "✅ Registered!" in result.output

def test_register_failure(runner, monkeypatch):
    def mock_post(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def json(self):
                return self.json_data

            def raise_for_status(self):
                if self.status_code >= 400:
                    raise requests.exceptions.HTTPError("Request failed", response=self)
        return MockResponse({"error": "Email already registered"}, 400)

    monkeypatch.setattr(requests, "post", mock_post)
    result = runner.invoke(auth_app, ["register", "--username", "testuser", "--email", "test@example.com", "--password", "password123"])
    assert result.exit_code == 0
    assert "❌ Registration failed: Email already registered" in result.output

def test_login_success(runner, monkeypatch):
    def mock_post(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def json(self):
                return self.json_data

            def raise_for_status(self):
                if self.status_code >= 400:
                    raise requests.exceptions.HTTPError("Request failed", response=self)
        return MockResponse({"token": "test_token"}, 200)

    monkeypatch.setattr(requests, "post", mock_post)
    monkeypatch.setattr(auth, "save_token", lambda x: None)
    result = runner.invoke(auth_app, ["login", "--email", "test@example.com", "--password", "password123"])
    assert result.exit_code == 0
    assert "✅ Logged in" in result.output

def test_login_failure(runner, monkeypatch):
    def mock_post(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def json(self):
                return self.json_data

            def raise_for_status(self):
                if self.status_code >= 400:
                    raise requests.exceptions.HTTPError("Request failed", response=self)
        return MockResponse({"error": "Invalid credentials"}, 401)

    monkeypatch.setattr(requests, "post", mock_post)
    result = runner.invoke(auth_app, ["login", "--email", "test@example.com", "--password", "password123"])
    assert result.exit_code == 0
    assert "❌ Login failed: Invalid credentials" in result.output

def test_logout_success(runner, monkeypatch):
    monkeypatch.setattr(auth, "get_token", lambda: "test_token")
    monkeypatch.setattr(auth, "remove_token", lambda: None)
    result = runner.invoke(auth_app, ["logout"])
    assert result.exit_code == 0
    assert "🔓 Logged out" in result.output

def test_logout_failure(runner, monkeypatch):
    monkeypatch.setattr(auth, "get_token", lambda: None)
    result = runner.invoke(auth_app, ["logout"])
    assert result.exit_code == 0
    assert "⚠️ Not logged in" in result.output
