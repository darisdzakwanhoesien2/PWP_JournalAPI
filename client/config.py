"""Configuration for the Journal API client."""
import os

API_URL = os.getenv("API_URL", "http://localhost:5000/api")
TOKEN_FILE = os.path.expanduser("~/.journal_token")