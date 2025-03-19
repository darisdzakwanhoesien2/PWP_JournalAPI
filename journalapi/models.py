import json  # Add this if you use the JSON helper functions
from . import db
from datetime import datetime

def list_to_json(lst):
    return json.dumps(lst)

def json_to_list(json_str):
    return json.loads(json_str) if json_str else []

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    journal_entries = db.relationship("JournalEntry", back_populates="author", cascade="all, delete-orphan")
    comments = db.relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    edit_history = db.relationship("EditHistory", back_populates="editor", cascade="all, delete-orphan")

class JournalEntry(db.Model):
    __tablename__ = "journal_entries"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    tags = db.Column(db.String, default="[]")  # Stored as JSON string
    sentiment_score = db.Column(db.Float, nullable=True)
    sentiment_tag = db.Column(db.String, default="[]")  # Stored as JSON string
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author = db.relationship("User", back_populates="journal_entries")
    comments = db.relationship("Comment", back_populates="journal_entry", cascade="all, delete-orphan")
    edit_history = db.relationship("EditHistory", back_populates="journal_entry", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "content": self.content,
            "date": self.date.isoformat() if self.date else None,
            "tags": json.loads(self.tags) if self.tags else [],
            "sentiment_score": self.sentiment_score,
            "sentiment_tag": json.loads(self.sentiment_tag) if self.sentiment_tag else [],
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }

class EditHistory(db.Model):
    __tablename__ = "edit_history"
    
    id = db.Column(db.Integer, primary_key=True)
    journal_entry_id = db.Column(db.Integer, db.ForeignKey("journal_entries.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    edited_at = db.Column(db.DateTime, default=datetime.utcnow)
    previous_content = db.Column(db.Text, nullable=False)
    new_content = db.Column(db.Text, nullable=False)

    journal_entry = db.relationship("JournalEntry", back_populates="edit_history")
    editor = db.relationship("User", back_populates="edit_history")


class Comment(db.Model):
    __tablename__ = "comments"
    
    id = db.Column(db.Integer, primary_key=True)
    journal_entry_id = db.Column(db.Integer, db.ForeignKey("journal_entries.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    journal_entry = db.relationship("JournalEntry", back_populates="comments")
    author = db.relationship("User", back_populates="comments")

    def to_dict(self):
        return {
            "id": self.id,
            "journal_entry_id": self.journal_entry_id,
            "user_id": self.user_id,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
