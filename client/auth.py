"""Authentication utilities for the Journal API client."""
import json
import os
from typing import Dict, Optional

from .config import TOKEN_FILE


def save_token(token: str) -> None:
    """Save JWT token to a file for authenticated requests.

    Args:
        token: The JWT token to save.

    Raises:
        OSError: If the file cannot be written.
    """
    try:
        os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            json.dump({"token": token}, f)
    except OSError as e:
        print(f"[red]❌ Failed to save token: {e}[/red]")
        raise


def get_token() -> Optional[str]:
    """Load the saved JWT token from file.

    Returns:
        Optional[str]: The token string or None if not found or invalid.

    Raises:
        json.JSONDecodeError: If the token file contains invalid JSON.
        OSError: If the file cannot be read.
    """
    if not os.path.exists(TOKEN_FILE):
        return None
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("token")
    except (OSError, json.JSONDecodeError) as e:
        print(f"[red]❌ Failed to read token: {e}[/red]")
        return None


def remove_token() -> None:
    """Delete the stored JWT token to log out the user.

    Raises:
        OSError: If the file cannot be deleted.
    """
    if os.path.exists(TOKEN_FILE):
        try:
            os.remove(TOKEN_FILE)
        except OSError as e:
            print(f"[red]❌ Failed to clear token: {e}[/red]")
            raise


def get_auth() -> Dict[str, str]:
    """Return the authorization header if token exists.

    Returns:
        Dict[str, str]: Authorization header with bearer token or empty dict.
    """
    token = get_token()
    return {"Authorization": f"Bearer {token}"} if token else {}
