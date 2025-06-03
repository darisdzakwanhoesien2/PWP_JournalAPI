"""Database models for the Journal API."""
import json
import logging
from datetime import datetime, timezone

from werkzeug.security import check_password_hash
from extensions import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class User(db.Model):
    """Represents a user in the Journal API."""
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    entries = db.relationship(
        "JournalEntry",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )
    comments = db.relationship(
        "Comment",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        """Return a string representation of the User instance."""
        return f"<User {self.username}>"

    def to_dict(self):
        """Convert User instance to a dictionary."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "_links": {
                "self": f"/api/users/{self.id}",
                "entries": "/api/entries"
            }
        }

    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

class JournalEntry(db.Model):
    """Represents a journal entry in the Journal API."""
    __tablename__ = "journal_entry"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.Text, nullable=True)
    sentiment_score = db.Column(db.Float, nullable=True)
    sentiment_tag = db.Column(db.Text, nullable=True)
    last_updated = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    comments = db.relationship(
        "Comment",
        backref="journal_entry",
        lazy=True,
        cascade="all, delete"
    )
    history = db.relationship(
        "EditHistory",
        backref="journal_entry",
        lazy=True,
        cascade="all, delete"
    )

    def __repr__(self):
        """Return a string representation of the JournalEntry instance."""
        return f"<JournalEntry {self.id}>"

    def to_dict(self):
        """Convert JournalEntry instance to a dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "content": self.content,
            "tags": json.loads(self.tags) if self.tags else [],
            "sentiment_score": self.sentiment_score,
            "sentiment_tag": json.loads(self.sentiment_tag) if self.sentiment_tag else [],
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "_links": {
                "self": f"/api/entries/{self.id}",
                "comments": f"/api/entries/{self.id}/comments",
                "history": f"/api/entries/{self.id}/history"
            }
        }

class Comment(db.Model):
    """Represents a comment on a journal entry."""
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True)
    journal_entry_id = db.Column(db.ForeignKey("journal_entry.id"), nullable=False)
    user_id = db.Column(db.ForeignKey("user.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        """Return a string representation of the Comment instance."""
        return f"<Comment {self.id}>"

    def to_dict(self):
        """Convert Comment instance to a dictionary."""
        return {
            "id": self.id,
            "journal_entry_id": self.journal_entry_id,
            "user_id": self.user_id,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "_links": {
                "self": f"/api/entries/{self.journal_entry_id}/comments/{self.id}"
            }
        }

class EditHistory(db.Model):
    """Tracks edit history for journal entries."""
    __tablename__ = "edit_history"
    id = db.Column(db.Integer, primary_key=True)
    journal_entry_id = db.Column(db.ForeignKey("journal_entry.id"), nullable=False)
    user_id = db.Column(db.ForeignKey("user.id"), nullable=False)
    old_content = db.Column(db.Text, nullable=False)
    new_content = db.Column(db.Text, nullable=False)
    edited_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        """Return a string representation of the EditHistory instance."""
        return f"<EditHistory {self.id}>"

    def to_dict(self):
        """Convert EditHistory instance to a dictionary."""
        return {
            "id": self.id,
            "journal_entry_id": self.journal_entry_id,
            "user_id": self.user_id,
            "old_content": self.old_content,
            "new_content": self.new_content,
            "edited_at": self.edited_at.isoformat() if self.edited_at else None,
            "_links": {
                "self": f"/api/entries/{self.journal_entry_id}/history/{self.id}"
            }
        }
