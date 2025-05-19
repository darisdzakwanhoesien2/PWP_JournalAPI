# PWP_JournalAPI/client/config.py
import os

API_URL = os.getenv("API_URL", "https://project_2012966-pwp-deploy-tests.2.rahtiapp.fi")
TOKEN_FILE = os.path.expanduser("~/.journal_token")