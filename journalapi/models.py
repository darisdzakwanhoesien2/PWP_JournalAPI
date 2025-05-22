"""Database models for the Journal API."""
from datetime import datetime
import json
from werkzeug.security import check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """Represents a user in the Journal API."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    entries = db.relationship("JournalEntry", backref="user", lazy=True)
    comments = db.relationship("Comment", backref="user", lazy=True)

    def __repr__(self):
        """Return a string representation of the User."""
        return f"<User {self.username}>"

    def to_dict(self):
        """Convert the User to a dictionary.
        
        Returns:
            dict: User data as a dictionary.
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email
        }

    def check_password(self, password):
        """Check if the provided password matches the stored hash.
        
        Args:
            password (str): The password to verify.
        
        Returns:
            bool: True if the password matches, False otherwise."""        
        return check_password_hash(self.password, password)

class JournalEntry(db.Model):
    """Represents a journal entry in the Journal API."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.Text, nullable=True)
    sentiment_score = db.Column(db.Float, nullable=True)
    sentiment_tag = db.Column(db.Text, nullable=True)
    last_updated = db.Column(db.DateTime, nullable=True)
    comments = db.relationship("Comment", backref="journal_entry", lazy=True)
    history = db.relationship("EditHistory", backref="journal_entry", lazy=True)

    def __repr__(self):
        """Return a string representation of the JournalEntry."""
        return f"<JournalEntry {self.id}>"

    def to_dict(self):
        """Convert the JournalEntry to a dictionary.
        
        Returns:
            dict: JournalEntry data as a dictionary.
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "content": self.content,
            "tags": json.loads(self.tags) if self.tags else [],
            "sentiment_score": self.sentiment_score,
            "sentiment_tag": json.loads(self.sentiment_tag) if self.sentiment_tag else [],
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        }

class Comment(db.Model):
    """Represents a comment on a journal entry."""
    id = db.Column(db.Integer, primary_key=True)
    journal_entry_id = db.Column(db.Integer, db.ForeignKey("journal_entry.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        """Return a string representation of the Comment."""
        return f"<Comment {self.id}>"

    def to_dict(self):
        """Convert the Comment to a dictionary.
        
        Returns:
            dict: Comment data as a dictionary.
        """
        return {
            "id": self.id,
            "journal_entry_id": self.journal_entry_id,
            "user_id": self.user_id,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }

class EditHistory(db.Model):
    """Tracks edit history for journal entries."""
    id = db.Column(db.Integer, primary_key=True)
    journal_entry_id = db.Column(db.Integer, db.ForeignKey("journal_entry.id"), nullable=False)
    old_content = db.Column(db.Text, nullable=False)
    edited_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        """Return a string representation of the EditHistory."""
        return f"<EditHistory {self.id}>"

    def to_dict(self):
        """Convert the EditHistory to a dictionary.
        
        Returns:
            dict: EditHistory data as a dictionary.
        """
        return {
            "id": self.id,
            "journal_entry_id": self.journal_entry_id,
            "old_content": self.old_content,
            "edited_at": self.edited_at.isoformat() if self.edited_at else None
        }