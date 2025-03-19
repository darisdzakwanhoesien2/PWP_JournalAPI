from journalapi import db
from journalapi.models import JournalEntry
from datetime import datetime, timezone
import json

class JournalEntryService:

    @staticmethod
    def create_entry(user_id, title, content, tags=None):
        tags = tags or []
        sentiment_score = 0.75  # Example sentiment score
        sentiment_tag = ["positive"]  # Example sentiment tag

        new_entry = JournalEntry(
            user_id=user_id,
            title=title,
            content=content,
            tags=json.dumps(tags),
            sentiment_score=sentiment_score,
            sentiment_tag=json.dumps(sentiment_tag),
            last_updated=datetime.now(timezone.utc) # datetime.utcnow()
        )
        db.session.add(new_entry)
        db.session.commit()
        
        return {"entry_id": new_entry.id}  #Return only entry_id


    @staticmethod
    def get_entries(user_id):
        """Retrieve all journal entries for a user."""
        entries = JournalEntry.query.filter_by(user_id=user_id).all()
        return [entry.to_dict() for entry in entries]  # Fix: Convert to JSON list

    @staticmethod
    def get_entry(entry_id):
        """Retrieve a specific journal entry."""
        entry = db.session.get(JournalEntry, entry_id)  # Fix for SQLAlchemy 2.0
        return entry.to_dict() if entry else None

    @staticmethod
    def update_entry(entry_id, title=None, content=None, tags=None):
        entry = JournalEntry.query.get(entry_id)
        if not entry:
            return None

        if title:
            entry.title = title
        if content:
            entry.content = content
        if tags:
            entry.tags = json.dumps(tags)
        entry.last_updated = datetime.now(timezone.utc) #datetime.utcnow()

        db.session.commit()
        return entry.to_dict()  # ✅ Fix: Convert to JSON

    @staticmethod
    def delete_entry(entry_id):
        entry = db.session.get(JournalEntry, entry_id)  # ✅ Fix for SQLAlchemy 2.0
        if entry:
            db.session.delete(entry)
            db.session.commit()
            return True
        return False