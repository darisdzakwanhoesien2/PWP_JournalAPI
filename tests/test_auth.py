"""Tests for client/auth.py."""
import json
import os
from unittest.mock import patch, mock_open
import pytest
from client.auth import save_token, get_token, remove_token, get_auth
from client.config import TOKEN_FILE


def test_save_token_success(tmp_path):
    """Test saving a token successfully."""
    token_file = tmp_path / "token.json"
    with patch("client.auth.TOKEN_FILE", str(token_file)):
        save_token("test_token")
        with open(token_file, "r", encoding="utf-8") as f:
            assert json.load(f) == {"token": "test_token"}


def test_save_token_oserror(tmp_path):
    """Test save_token with OSError."""
    token_file = tmp_path / "token.json"
    with patch("client.auth.TOKEN_FILE", str(token_file)):
        with patch("builtins.open", side_effect=OSError("Permission denied")):
            with pytest.raises(OSError, match="Permission denied"):
                save_token("test_token")


def test_get_token_success(tmp_path):
    """Test getting a token successfully."""
    token_file = tmp_path / "token.json"
    with open(token_file, "w", encoding="utf-8") as f:
        json.dump({"token": "test_token"}, f)
    with patch("client.auth.TOKEN_FILE", str(token_file)):
        assert get_token() == "test_token"


def test_get_token_file_not_exists(tmp_path):
    """Test get_token when token file does not exist."""
    token_file = tmp_path / "nonexistent.json"
    with patch("client.auth.TOKEN_FILE", str(token_file)):
        assert get_token() is None


def test_get_token_invalid_json(tmp_path):
    """Test get_token with invalid JSON."""
    token_file = tmp_path / "token.json"
    with open(token_file, "w", encoding="utf-8") as f:
        f.write("invalid json")
    with patch("client.auth.TOKEN_FILE", str(token_file)):
        assert get_token() is None


def test_get_token_oserror(tmp_path):
    """Test get_token with OSError."""
    token_file = tmp_path / "token.json"
    with patch("client.auth.TOKEN_FILE", str(token_file)):
        with patch("builtins.open", side_effect=OSError("Permission denied")):
            assert get_token() is None


def test_remove_token_success(tmp_path):
    """Test removing a token successfully."""
    token_file = tmp_path / "token.json"
    with open(token_file, "w", encoding="utf-8") as f:
        f.write("dummy")
    with patch("client.auth.TOKEN_FILE", str(token_file)):
        remove_token()
        assert not os.path.exists(token_file)


def test_remove_token_file_not_exists(tmp_path):
    """Test remove_token when file does not exist."""
    token_file = tmp_path / "nonexistent.json"
    with patch("client.auth.TOKEN_FILE", str(token_file)):
        remove_token()  # Should not raise an error


def test_remove_token_oserror(tmp_path):
    """Test remove_token with OSError."""
    token_file = tmp_path / "token.json"
    with open(token_file, "w", encoding="utf-8") as f:
        f.write("dummy")
    with patch("client.auth.TOKEN_FILE", str(token_file)):
        with patch("os.remove", side_effect=OSError("Permission denied")):
            with pytest.raises(OSError, match="Permission denied"):
                remove_token()


def test_get_auth_with_token(tmp_path):
    """Test get_auth when token exists."""
    token_file = tmp_path / "token.json"
    with open(token_file, "w", encoding="utf-8") as f:
        json.dump({"token": "test_token"}, f)
    with patch("client.auth.TOKEN_FILE", str(token_file)):
        assert get_auth() == {"Authorization": "Bearer test_token"}


def test_get_auth_no_token(tmp_path):
    """Test get_auth when no token exists."""
    token_file = tmp_path / "nonexistent.json"
    with patch("client.auth.TOKEN_FILE", str(token_file)):
        assert get_auth() == {}