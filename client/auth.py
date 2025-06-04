# client/auth.py
"""Authentication utilities for the Journal API client."""
import json
import os
from typing import Dict, Optional

from .config import TOKEN_FILE

def save_token(token: str) -> None:
    """Save JWT token to a file for authenticated requests.
    
    Args:
        token: The JWT token to save.
    """
    try:
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            json.dump({"token": token}, f)
    except OSError as e:
        print(f"[red]❌ Failed to save token: {e}[/red]")

def get_token() -> Optional[str]:
    """Load the saved JWT token from file.
    
    Returns:
        Optional[str]: The token string or None if not found.
    """
    if not os.path.exists(TOKEN_FILE):
        return None
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("token")
    except (OSError, json.JSONDecodeError) as e:
        print(f"[red]❌ Failed to read token: {e}[/red]")
        return None

def clear_token() -> None:
    """Delete the stored JWT token to log out the user."""
    if os.path.exists(TOKEN_FILE):
        try:
            os.remove(TOKEN_FILE)
        except OSError as e:
            print(f"[red]❌ Failed to clear token: {e}[/red]")

def get_auth() -> Dict[str, str]:
    """Return the authorization header if token exists.
    
    Returns:
        Dict[str, str]: Authorization header with bearer token or empty dict.
    """
    token = get_token()
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}