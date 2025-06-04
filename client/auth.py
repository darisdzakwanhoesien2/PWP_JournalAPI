# PWP_JournalAPI/client/auth.py
"""Client authentication utilities for the Journal API CLI."""
import os
import json
from journalapi.utils import generate_token
from .config import TOKEN_FILE

def save_token(token):
    """Save JWT token to file."""
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    with open(TOKEN_FILE, 'w') as f:
        json.dump({'token': token}, f)

def get_token():
    """Retrieve JWT token from file."""
    try:
        with open(TOKEN_FILE, 'r') as f:
            data = json.load(f)
            return data.get('token')
    except FileNotFoundError:
        return None

def clear_token():
    """Remove token file."""
    try:
        os.remove(TOKEN_FILE)
    except FileNotFoundError:
        pass

def get_auth():
    """Get authorization header with token."""
    token = get_token()
    return {'Authorization': f'Bearer {token}'} if token else {}