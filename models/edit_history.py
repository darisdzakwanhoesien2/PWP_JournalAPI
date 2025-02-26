from extensions import db
from datetime import datetime

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
