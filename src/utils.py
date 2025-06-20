## current code
from flask import url_for

def user_links(user_id):
    return {
        'self': url_for('users.get_user', id=user_id, _external=True),
        'entries': url_for('entries.get_entries_by_user', id=user_id, _external=True)
    }

def users_collection_links():
    return {
        'self': url_for('users.get_users', _external=True),
        'register': url_for('users.register_user', _external=True)
    }

def entry_links(entry_id, user_id=None):
    links = {
        'self': url_for('entries.get_entry', id=entry_id, _external=True),
        'comments': url_for('entries.get_comments', id=entry_id, _external=True),
        'edit_history': url_for('entries.get_edit_history', id=entry_id, _external=True)
    }
    if user_id is not None:
        links['user'] = url_for('users.get_user', id=user_id, _external=True)
    return links

def entries_collection_links(user_id=None):
    links = {
        'self': url_for('entries.get_entries', _external=True)
    }
    if user_id is not None:
        links['user'] = url_for('users.get_user', id=user_id, _external=True)
    return links

def comment_links(comment_id, entry_id=None):
    links = {
        'self': url_for('entries.get_comment', comment_id=comment_id, _external=True)
    }
    if entry_id is not None:
        links['entry'] = url_for('entries.get_entry', id=entry_id, _external=True)
    return links

def comments_collection_links(entry_id):
    return {
        'self': url_for('entries.get_comments', id=entry_id, _external=True),
        'entry': url_for('entries.get_entry', id=entry_id, _external=True)
    }

def edit_history_links(entry_id, edit_id):
    return {
        'self': url_for('entries.get_edit_history_item', id=entry_id, edit_id=edit_id, _external=True),
        'entry': url_for('entries.get_entry', id=entry_id, _external=True)
    }

def edit_history_collection_links(entry_id):
    return {
        'self': url_for('entries.get_edit_history', id=entry_id, _external=True),
        'entry': url_for('entries.get_entry', id=entry_id, _external=True)
    }
