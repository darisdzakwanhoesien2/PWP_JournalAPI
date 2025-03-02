import json  # Add this if you use the JSON helper functions
from extensions import db
from datetime import datetime

def list_to_json(lst):
    return json.dumps(lst)

def json_to_list(json_str):
    return json.loads(json_str) if json_str else []

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
