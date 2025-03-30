# journalapi/models.py
from datetime import datetime
from extensions import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    journal_entries = db.relationship(
        "JournalEntry", backref="author", cascade="all, delete-orphan"
    )
    comments = db.relationship(
        "Comment", backref="author", cascade="all, delete-orphan"
    )

class JournalEntry(db.Model):
    __tablename__ = "journal_entries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String, default="[]")
    sentiment_score = db.Column(db.Float)
    sentiment_tag = db.Column(db.String, default="[]")
    date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    comments = db.relationship("Comment", backref="journal_entry", cascade="all, delete-orphan")

class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    journal_entry_id = db.Column(db.Integer, db.ForeignKey("journal_entries.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# If you want EditHistory, define it here too:
# If you want EditHistory, define it here:
class EditHistory(db.Model):
    __tablename__ = "edit_history"
    id = db.Column(db.Integer, primary_key=True)
    journal_entry_id = db.Column(db.Integer, db.ForeignKey("journal_entries.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    edited_at = db.Column(db.DateTime, default=datetime.utcnow)
    previous_content = db.Column(db.Text, nullable=False)
    new_content = db.Column(db.Text, nullable=False)
