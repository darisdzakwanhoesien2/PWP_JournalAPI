# PWP_JournalAPI/client/config.py
"""Configuration settings for the Journal API CLI."""
import os
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:5000/api")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 5))
TOKEN_FILE = os.path.expanduser("~/.journal_token")