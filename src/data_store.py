## current code
import json
import os
from threading import Lock

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
    with lock:
        if not os.path.exists(file_path):
            return []
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

def _save_data(file_path, data, lock):
    with lock:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

def load_users():
    return _load_data(USERS_FILE, users_lock)

def save_users(users):
    _save_data(USERS_FILE, users, users_lock)

def load_entries():
    return _load_data(ENTRIES_FILE, entries_lock)

def save_entries(entries):
    _save_data(ENTRIES_FILE, entries, entries_lock)

import logging

def load_comments():
    logging.info(f"Loading comments from {COMMENTS_FILE}")
    return _load_data(COMMENTS_FILE, comments_lock)

def save_comments(comments):
    logging.info(f"Saving comments to {COMMENTS_FILE}: {comments}")
    _save_data(COMMENTS_FILE, comments, comments_lock)

def load_edit_history():
    return _load_data(EDIT_HISTORY_FILE, edit_history_lock)

def save_edit_history(edit_history):
    _save_data(EDIT_HISTORY_FILE, edit_history, edit_history_lock)

def get_next_id(items):
    if not items:
        return 1
    max_id = max(item.get('id', 0) for item in items)
    return max_id + 1
