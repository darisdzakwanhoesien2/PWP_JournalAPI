## current code
from datetime import datetime

"""
Data model classes for User, Entry, Comment, and EditHistory.
"""

class User:
    """
    Represents a user in the system.
    """
    def __init__(self, id, username, email, registered_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.registered_at = registered_at or datetime.utcnow().isoformat()

    def to_dict(self):
        """
        Convert User instance to dictionary.
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'registered_at': self.registered_at
        }

    @staticmethod
    def from_dict(data):
        """
        Create User instance from dictionary.
        """
        return User(
            id=data['id'],
            username=data['username'],
            email=data['email'],
            registered_at=data.get('registered_at')
        )

class Entry:
    """
    Represents an entry or post created by a user.
    """
    def __init__(self, id, user_id, title, content, created_at=None, updated_at=None):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.content = content
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or self.created_at

    def to_dict(self):
        """
        Convert Entry instance to dictionary.
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @staticmethod
    def from_dict(data):
        """
        Create Entry instance from dictionary.
        """
        return Entry(
            id=data['id'],
            user_id=data['user_id'],
            title=data['title'],
            content=data['content'],
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

class Comment:
    """
    Represents a comment on an entry.
    """
    def __init__(self, id, entry_id, user_id, content, created_at=None, updated_at=None):
        self.id = id
        self.entry_id = entry_id
        self.user_id = user_id
        self.content = content
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.updated_at = updated_at or self.created_at

    def to_dict(self):
        """
        Convert Comment instance to dictionary.
        """
        return {
            'id': self.id,
            'entry_id': self.entry_id,
            'user_id': self.user_id,
            'content': self.content,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @staticmethod
    def from_dict(data):
        """
        Create Comment instance from dictionary.
        """
        return Comment(
            id=data['id'],
            entry_id=data['entry_id'],
            user_id=data['user_id'],
            content=data['content'],
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

class EditHistory:
    """
    Represents an edit history record for an entry.
    """
    def __init__(self, id, entry_id, edited_at=None, changes=None):
        self.id = id
        self.entry_id = entry_id
        self.edited_at = edited_at or datetime.utcnow().isoformat()
        self.changes = changes or {}

    def to_dict(self):
        """
        Convert EditHistory instance to dictionary.
        """
        return {
            'id': self.id,
            'entry_id': self.entry_id,
            'edited_at': self.edited_at,
            'changes': self.changes
        }

    @staticmethod
    def from_dict(data):
        """
        Create EditHistory instance from dictionary.
        """
        return EditHistory(
            id=data['id'],
            entry_id=data['entry_id'],
            edited_at=data.get('edited_at'),
            changes=data.get('changes', {})
        )
