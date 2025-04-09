# PWP_JournalAPI/client/config.py
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")
TOKEN_FILE = os.path.expanduser("~/.journal_token")