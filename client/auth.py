# PWP_JournalAPI/client/auth.py
import os
import json
from client.config import TOKEN_FILE

def save_token(token: str):
    with open(TOKEN_FILE, "w") as f:
        json.dump({"token": token}, f)

def get_token() -> str:
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, "r") as f:
        return json.load(f).get("token")

def clear_token():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
