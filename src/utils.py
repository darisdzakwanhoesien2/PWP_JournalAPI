import re

"""
Utility functions to generate HATEOAS links for API resources.
"""

def user_links(user_id):
    return {
        "self": f"/users/{user_id}",
        "entries": f"/users/{user_id}/entries"
    }

def users_collection_links():
    return {
        "self": "/users"
    }

def entry_links(entry_id, user_id):
    return {
        "self": f"/entries/{entry_id}",
        "user": f"/users/{user_id}",
        "comments": f"/entries/{entry_id}/comments",
        "edit_history": f"/entries/{entry_id}/edit_history"
    }

def entries_collection_links(user_id=None):
    links = {
        "self": "/entries"
    }
    if user_id is not None:
        links["user"] = f"/users/{user_id}"
    return links

def comment_links(comment_id, entry_id):
    return {
        "self": f"/comments/{comment_id}",
        "entry": f"/entries/{entry_id}"
    }

def comments_collection_links(entry_id):
    return {
        "self": f"/entries/{entry_id}/comments"
    }

def edit_history_links(entry_id, edit_id):
    return {
        "self": f"/entries/{entry_id}/edit_history/{edit_id}",
        "entry": f"/entries/{entry_id}"
    }

def edit_history_collection_links(entry_id):
    return {
        "self": f"/entries/{entry_id}/edit_history"
    }
