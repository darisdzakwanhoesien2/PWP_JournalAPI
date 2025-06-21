## current code
import json
import os
from threading import Lock
import logging

"""Module for loading and saving data to JSON files with thread-safe access."""

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# File paths
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
ENTRIES_FILE = os.path.join(DATA_DIR, 'entries.json')
COMMENTS_FILE = os.path.join(DATA_DIR, 'comments.json')
EDIT_HISTORY_FILE = os.path.join(DATA_DIR, 'edit_history.json')

# Thread locks for concurrent access
users_lock = Lock()
entries_lock = Lock()
comments_lock = Lock()
edit_history_lock = Lock()

def _load_data(file_path, lock):
    """Load JSON data from a file with thread-safe locking.
    Returns an empty list if file does not exist or JSON is invalid."""
    with lock:
        if not os.path.exists(file_path):
            return []
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

def _save_data(file_path, data, lock):
    """Save JSON data to a file with thread-safe locking."""
    with lock:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

def load_users():
    """Load users data from JSON file."""
    return _load_data(USERS_FILE, users_lock)

def save_users(users):
    """Save users data to JSON file."""
    _save_data(USERS_FILE, users, users_lock)

def load_entries():
    """Load entries data from JSON file."""
    return _load_data(ENTRIES_FILE, entries_lock)

def save_entries(entries):
    """Save entries data to JSON file."""
    _save_data(ENTRIES_FILE, entries, entries_lock)

def load_comments():
    """Load comments data from JSON file."""
    logging.info("Loading comments from %s", COMMENTS_FILE)
    return _load_data(COMMENTS_FILE, comments_lock)

def save_comments(comments):
    """Save comments data to JSON file."""
    logging.info("Saving comments to %s: %s", COMMENTS_FILE, comments)
    _save_data(COMMENTS_FILE, comments, comments_lock)

def load_edit_history():
    """Load edit history data from JSON file."""
    return _load_data(EDIT_HISTORY_FILE, edit_history_lock)

def save_edit_history(edit_history):
    """Save edit history data to JSON file."""
    _save_data(EDIT_HISTORY_FILE, edit_history, edit_history_lock)

def get_next_id(items):
    """Get the next available ID for a list of items with 'id' fields."""
    if not items:
        return 1
    max_id = max(item.get('id', 0) for item in items)
    return max_id + 1
