# client/token.py
import os
import json

TOKEN_FILE = os.path.expanduser("~/.journal_token")

def save_token(token: str):
    with open(TOKEN_FILE, "w") as f:
        json.dump({"token": token}, f)

def load_token() -> str:
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, "r") as f:
        return json.load(f).get("token")

def clear_token():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
