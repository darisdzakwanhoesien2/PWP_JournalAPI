# PWP_JournalAPI/journalapi/handlers/journal_entry_handler.py
"""Handler for journal entry operations."""
import json
from datetime import datetime, timezone
from extensions import db
from journalapi.models import JournalEntry
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JournalEntryHandler:
    """Handles journal entry creation, retrieval, update, and deletion."""

    @staticmethod
    def create_entry(user_id: int, title: str, content: str, tags: list = None) -> dict:
        """Create a new journal entry."""
        tags = tags or []
        try:
            entry = JournalEntry(
                user_id=user_id,
                title=title,
                content=content,
                tags=json.dumps(tags),
                sentiment_score=0.0,  # Placeholder for future sentiment analysis
                sentiment_tag=json.dumps([]),
                last_updated=datetime.now(timezone.utc)
            )
            db.session.add(entry)
            db.session.commit()
            logger.info(f"Journal entry created for user {user_id}")
            return {"id": entry.id}
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create journal entry: {e}")
            raise

    @staticmethod
    def get_entries(user_id: int) -> list:
        """Retrieve all journal entries for a user."""
        try:
            entries = JournalEntry.query.filter_by(user_id=user_id).all()
            logger.info(f"Retrieved entries for user {user_id}")
            return [entry.to_dict() for entry in entries]
        except Exception as e:
            logger.error(f"Failed to retrieve entries: {e}")
            raise

    @staticmethod
    def get_entry(entry_id: int) -> dict:
        """Retrieve a single journal entry."""
        try:
            entry = db.session.get(JournalEntry, entry_id)
            if not entry:
                logger.warning(f"Journal entry {entry_id} not found")
                return None
            logger.info(f"Retrieved journal entry {entry_id}")
            return entry.to_dict()
        except Exception as e:
            logger.error(f"Failed to retrieve entry {entry_id}: {e}")
            raise

    @staticmethod
    def update_entry(entry_id: int, title: str = None, content: str = None, tags: list = None) -> dict:
        """Update a journal entry."""
        try:
            entry = db.session.get(JournalEntry, entry_id)
            if not entry:
                logger.warning(f"Journal entry {entry_id} not found")
                return None
            if title:
                entry.title = title
            if content:
                entry.content = content
            if tags is not None:
                entry.tags = json.dumps(tags)
            entry.last_updated = datetime.now(timezone.utc)
            db.session.commit()
            logger.info(f"Journal entry {entry_id}")
            return entry.to_dict()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update entry {entry_id}: {e}")
            raise

    @staticmethod
    def delete_entry(entry_id: int) -> bool:
        """Delete a journal entry."""
        try:
            entry = db.session.get(JournalEntry, entry_id)
            if not entry:
                logger.warning(f"Journal entry {entry_id} not found")
                return False
            db.session.delete(entry)
            db.session.commit()
            logger.info(f"Journal entry {entry_id} deleted")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to delete entry {entry_id}: {e}")
            raise