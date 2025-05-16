# PWP_JournalAPI/journalapi/handlers/journal_entry_handler.py
from journalapi import db
from journalapi.models import JournalEntry
from datetime import datetime, timezone
import json

class JournalEntryHandler:
    @staticmethod
    def create_entry(user_id, title, content, tags=None):
        tags = tags or []
        sentiment_score = 0.75
        sentiment_tag = ["positive"]
        new_entry = JournalEntry(
            user_id=user_id,
            title=title,
            content=content,
            tags=json.dumps(tags),
            sentiment_score=sentiment_score,
            sentiment_tag=json.dumps(sentiment_tag),
            last_updated=datetime.now(timezone.utc)
        )
        db.session.add(new_entry)
        db.session.commit()
        return {"entry_id": new_entry.id}

    @staticmethod
    def get_entries(user_id):
        entries = JournalEntry.query.filter_by(user_id=user_id).all()
        return [entry.to_dict() for entry in entries]

    @staticmethod
    def get_entry(entry_id):
        entry = db.session.get(JournalEntry, entry_id)
        return entry.to_dict() if entry else None

    @staticmethod
    def update_entry(entry_id, title=None, content=None, tags=None):
        entry = db.session.get(JournalEntry, entry_id)
        if not entry:
            return None
        if title:
            entry.title = title
        if content:
            entry.content = content
        if tags is not None:
            entry.tags = json.dumps(tags)
        db.session.commit()
        return entry.to_dict()

    @staticmethod
    def delete_entry(entry_id):
        entry = db.session.get(JournalEntry, entry_id)
        if entry:
            db.session.delete(entry)
            db.session.commit()
            return True
        return False
