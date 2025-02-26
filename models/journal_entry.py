from extensions import db
from datetime import datetime
import json

def list_to_json(lst):
    return json.dumps(lst)

def json_to_list(json_str):
    return json.loads(json_str) if json_str else []

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
