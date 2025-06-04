import json
import os
from pathlib import Path
from unittest.mock import mock_open

import pytest
from pytest_mock import MockerFixture
from client import auth

@pytest.fixture
def mock_token_file(mocker: MockerFixture):
    """Fixture to mock token file path."""
    mocker.patch("client.auth.TOKEN_FILE", "/tmp/.journal_token")
    return "/tmp/.journal_token"

def test_save_token_success(mocker: MockerFixture, mock_token_file: str, caplog):
    """Test saving token successfully."""
    caplog.set_level("INFO")
    mock_path = mocker.patch("pathlib.Path")
    mock_path.return_value.parent.mkdir.side_effect = None
    mock_file = mock_open()
    mocker.patch("builtins.open", mock_file)

    auth.save_token("test_token")

    mock_path.assert_called_once_with(mock_token_file)
    mock_path.return_value.parent.mkdir.assert_called_once_with(parents=True, exist_ok=True)
    mock_file.assert_called_once_with(mock_token_file, "w", encoding="utf-8")
    mock_file().write.assert_called_once()
    assert "Token saved successfully" in caplog.text

def test_save_token_oserror(mocker: MockerFixture, mock_token_file: str, caplog):
    """Test save_token with OSError."""
    caplog.set_level("ERROR")
    mocker.patch("pathlib.Path").return_value.parent.mkdir.side_effect = OSError("Permission denied")
    with pytest.raises(OSError, match="Permission denied"):
        auth.save_token("test_token")
    assert "Failed to save token: Permission denied" in caplog.text

def test_save_token_json_error(mocker: MockerFixture, mock_token_file: str, caplog):
    """Test save_token with JSON encode error."""
    caplog.set_level("ERROR")
    mocker.patch("pathlib.Path").return_value.parent.mkdir.side_effect = None
    mocker.patch("json.dump", side_effect=json.JSONEncodeError("Invalid JSON", "", 0))
    with pytest.raises(json.JSONEncodeError):
        auth.save_token("test_token")
    assert "Failed to save token: Invalid JSON" in caplog.text

def test_get_token_success(mocker: MockerFixture, mock_token_file: str, caplog):
    """Test retrieving token successfully."""
    caplog.set_level("DEBUG")
    mocker.patch("os.path.exists", return_value=True)
    mock_file = mock_open(read_data='{"token": "test_token"}')
    mocker.patch("builtins.open", mock_file)

    token = auth.get_token()

    assert token == "test_token"
    mock_file.assert_called_once_with(mock_token_file, "r", encoding="utf-8")
    assert "Token file not found" not in caplog.text

def test_get_token_file_not_found(mocker: MockerFixture, mock_token_file: str, caplog):
    """Test get_token when token file doesn't exist."""
    caplog.set_level("DEBUG")
    mocker.patch("os.path.exists", return_value=False)

    token = auth.get_token()

    assert token is None
    assert "Token file not found" in caplog.text

def test_get_token_json_error(mocker: MockerFixture, mock_token_file: str, caplog):
    """Test get_token with JSON decode error."""
    caplog.set_level("ERROR")
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("builtins.open", mock_open(read_data="invalid json"))
    mocker.patch("json.load", side_effect=json.JSONDecodeError("Invalid JSON", "", 0))

    token = auth.get_token()

    assert token is None
    assert "Failed to read token: Invalid JSON" in caplog.text

def test_get_token_oserror(mocker: MockerFixture, mock_token_file: str, caplog):
    """Test get_token with OSError."""
    caplog.set_level("ERROR")
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("builtins.open", side_effect=OSError("File error"))

    token = auth.get_token()

    assert token is None
    assert "Failed to read token: File error" in caplog.text

def test_clear_token_success(mocker: MockerFixture, mock_token_file: str, caplog):
    """Test clearing token successfully."""
    caplog.set_level("INFO")
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("os.remove")

    auth.clear_token()

    mocker.patch("os.remove").assert_called_once_with(mock_token_file)
    assert "Token cleared successfully" in caplog.text

def test_clear_token_no_file(mocker: MockerFixture, mock_token_file: str, caplog):
    """Test clear_token when token file doesn't exist."""
    caplog.set_level("INFO")
    mocker.patch("os.path.exists", return_value=False)

    auth.clear_token()

    mocker.patch("os.remove").assert_not_called()
    assert "Token cleared successfully" not in caplog.text

def test_clear_token_oserror(mocker: MockerFixture, mock_token_file: str, caplog):
    """Test clear_token with OSError."""
    caplog.set_level("ERROR")
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("os.remove", side_effect=OSError("Permission denied"))

    with pytest.raises(OSError, match="Permission denied"):
        auth.clear_token()
    assert "Failed to clear token: Permission denied" in caplog.text

def test_get_auth_with_token(mocker: MockerFixture, caplog):
    """Test get_auth with a valid token."""
    caplog.set_level("DEBUG")
    mocker.patch("client.auth.get_token", return_value="test_token")

    headers = auth.get_auth()

    assert headers == {"Authorization": "Bearer test_token"}
    assert "Authorization header generated" in caplog.text

def test_get_auth_no_token(mocker: MockerFixture, caplog):
    """Test get_auth when no token exists."""
    caplog.set_level("DEBUG")
    mocker.patch("client.auth.get_token", return_value=None)

    headers = auth.get_auth()

    assert headers == {}
    assert "No token found, returning empty auth header" in caplog.text