from database import db
from models.journal_entry import JournalEntry
from datetime import datetime
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
            last_updated=datetime.utcnow()
        )
        db.session.add(new_entry)
        db.session.commit()
        return new_entry

    @staticmethod
    def get_entries(user_id):
        return JournalEntry.query.filter_by(user_id=user_id).all()

    @staticmethod
    def get_entry(entry_id):
        return JournalEntry.query.get(entry_id)

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
        entry.last_updated = datetime.utcnow()

        db.session.commit()
        return entry

    @staticmethod
    def delete_entry(entry_id):
        entry = JournalEntry.query.get(entry_id)
        if entry:
            db.session.delete(entry)
            db.session.commit()
            return True
        return False