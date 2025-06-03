# PWP_JournalAPI/client/main.py
"""Token utilities for the Journal API CLI."""
import os
import json

TOKEN_FILE = os.path.expanduser("~/.journal_token")

def save_token(token: str) -> None:
    """Save JWT token to a file.

    Args:
        token: The JWT token to save.
    """
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump({"token": token}, f)

def load_token() -> Optional[str]:
    """Retrieve the saved JWT token from file.

    Returns:
        The token string or None if not found.
    """
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        return json.load(f).get("token")

def clear_token() -> None:
    """Delete the stored JWT token."""
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)