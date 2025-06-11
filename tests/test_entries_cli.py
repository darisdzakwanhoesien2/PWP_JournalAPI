import pytest
import requests
from client import auth, config
from client.entries_cli import entry_app
from typer.testing import CliRunner

@pytest.fixture
def runner():
    return CliRunner()

def test_entry_list_success(runner, monkeypatch):
    def mock_get(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def json(self):
                return self.json_data

            def raise_for_status(self):
                if self.status_code >= 400:
                    raise requests.exceptions.HTTPError("Request failed", response=self)
        return MockResponse([{"id": 1, "title": "Test Entry", "content": "Test Content", "tags": ["life", "personal"]}], 200)

    monkeypatch.setattr(requests, "get", mock_get)
    monkeypatch.setattr(auth, "get_token", lambda: "test_token")
    result = runner.invoke(entry_app, ["list"], env={"API_URL": "http://localhost:5000"})
    assert result.exit_code == 0
    assert "[1] Test Entry" in result.output
    assert "Tags: ['life', 'personal']" in result.output

def test_entry_create_success(runner, monkeypatch):
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
        return MockResponse({"message": "Entry created successfully"}, 201)

    monkeypatch.setattr(requests, "post", mock_post)
    monkeypatch.setattr(auth, "get_token", lambda: "test_token")
    result = runner.invoke(entry_app, ["create", "Test", "My first entry", "--tags", "life,personal"], env={"API_URL": "http://localhost:5000"})
    assert result.exit_code == 0
    assert "Entry created successfully" in result.output

def test_entry_list_failure(runner, monkeypatch):
    def mock_get(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def json(self):
                return self.json_data

            def raise_for_status(self):
                if self.status_code >= 400:
                    raise requests.exceptions.HTTPError("Request failed", response=self)
        return MockResponse({"error": "Unauthorized"}, 401)

    monkeypatch.setattr(requests, "get", mock_get)
    monkeypatch.setattr(auth, "get_token", lambda: "test_token")
    result = runner.invoke(entry_app, ["list"], env={"API_URL": "http://localhost:5000"})
    assert result.exit_code == 1
    assert "❌ Failed to list entries: Unauthorized" in result.output

def test_entry_create_failure(runner, monkeypatch):
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
        return MockResponse({"error": "Unauthorized"}, 401)

    monkeypatch.setattr(requests, "post", mock_post)
    monkeypatch.setattr(auth, "get_token", lambda: "test_token")
    result = runner.invoke(entry_app, ["create", "Test", "My first entry", "--tags", "life,personal"], env={"API_URL": "http://localhost:5000"})
    assert result.exit_code == 1
    assert "❌ Failed to create entry: Unauthorized" in result.output

def test_entry_create_long_title(runner, monkeypatch):
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
        return MockResponse({"message": "Entry created successfully"}, 201)

    monkeypatch.setattr(requests, "post", mock_post)
    monkeypatch.setattr(auth, "get_token", lambda: "test_token")
    long_title = "A" * 200
    result = runner.invoke(entry_app, ["create", long_title, "My first entry", "--tags", "life,personal"], env={"API_URL": "http://localhost:5000"})
    assert result.exit_code == 0
    assert "Entry created successfully" in result.output

def test_entry_create_long_content(runner, monkeypatch):
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
        return MockResponse({"message": "Entry created successfully"}, 201)

    monkeypatch.setattr(requests, "post", mock_post)
    monkeypatch.setattr(auth, "get_token", lambda: "test_token")
    long_content = "A" * 2000
    result = runner.invoke(entry_app, ["create", "Test", long_content, "--tags", "life,personal"], env={"API_URL": "http://localhost:5000"})
    assert result.exit_code == 0
    assert "Entry created successfully" in result.output

def test_entry_create_many_tags(runner, monkeypatch):
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
        return MockResponse({"message": "Entry created successfully"}, 201)

    monkeypatch.setattr(requests, "post", mock_post)
    monkeypatch.setattr(auth, "get_token", lambda: "test_token")
    many_tags = ",".join(["tag"] * 20)
    result = runner.invoke(entry_app, ["create", "Test", "My first entry", "--tags", many_tags], env={"API_URL": "http://localhost:5000"})
    assert result.exit_code == 0
    assert "Entry created successfully" in result.output
