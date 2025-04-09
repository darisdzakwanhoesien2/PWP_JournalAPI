# PWP_JournalAPI/client/auth.py
# client/auth.py

import os
import json
from client.config import TOKEN_FILE

def save_token(token: str):
    """
    Save JWT token to a file for future authenticated requests.
    """
    try:
        with open(TOKEN_FILE, "w") as f:
            json.dump({"token": token}, f)
    except Exception as e:
        print(f"[red]❌ Failed to save token: {e}[/red]")

def get_token() -> str:
    """
    Load the saved JWT token from file.
    Returns the token string or None if not found.
    """
    if not os.path.exists(TOKEN_FILE):
        return None
    try:
        with open(TOKEN_FILE, "r") as f:
            return json.load(f).get("token")
    except Exception as e:
        print(f"[red]❌ Failed to read token: {e}[/red]")
        return None

def clear_token():
    """
    Delete the stored JWT token to log out the user.
    """
    if os.path.exists(TOKEN_FILE):
        try:
            os.remove(TOKEN_FILE)
        except Exception as e:
            print(f"[red]❌ Failed to clear token: {e}[/red]")

def get_auth():
    """
    Return the authorization header if token exists.
    Used by CLI commands to attach bearer token.
    """
    token = get_token()
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}
