"""Handler for journal entry management operations."""
from extensions import db
from journalapi.models import JournalEntry, EditHistory
from datetime import datetime, timezone
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JournalEntryHandler:
    """Handles journal entry creation, retrieval, and management."""

    @staticmethod
    def create_entry(user_id: int, title: str, content: str, tags: list) -> dict:
        """Create a new journal entry."""
        try:
            entry = JournalEntry(
                user_id=user_id,
                title=title,
                content=content,
                tags=json.dumps(tags)
            )
            db.session.add(entry)
            db.session.commit()
            logger.info(f"Journal entry created for user {user_id}")
            return entry.to_dict()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create journal entry for user {user_id}: {e}")
            raise

    @staticmethod
    def get_entries(user_id: int) -> list:
        """Retrieve all journal entries for a user."""
        try:
            entries = JournalEntry.query.filter_by(user_id=user_id).all()
            logger.info(f"Retrieved {len(entries)} entries for user {user_id}")
            return [entry.to_dict() for entry in entries]
        except Exception as e:
            logger.error(f"Failed to retrieve entries for user {user_id}: {e}")
            raise

    @staticmethod
    def get_entry(entry_id: int) -> dict:
        """Retrieve a journal entry by ID."""
        try:
            entry = db.session.get(JournalEntry, entry_id)
            if not entry:
                logger.warning(f"Journal entry {entry_id} not found")
                return None
            logger.info(f"Retrieved journal entry {entry_id}")
            return entry.to_dict()
        except Exception as e:
            logger.error(f"Failed to retrieve journal entry {entry_id}: {e}")
            raise

    @staticmethod
    def update_entry(entry_id: int, title: str = None, content: str = None, tags: list = None) -> dict:
        """Update a journal entry."""
        try:
            entry = db.session.get(JournalEntry, entry_id)
            if not entry:
                logger.warning(f"Journal entry {entry_id} not found")
                return None
            # Store previous state for edit history
            previous_content = entry.content
            new_content = content if content is not None else entry.content
            # Update fields if provided
            if title:
                entry.title = title
            if content:
                entry.content = content
            if tags is not None:
                entry.tags = json.dumps(tags)
            entry.last_updated = datetime.now(timezone.utc)
            # Create edit history record if content changed
            if previous_content != new_content:
                edit_history = EditHistory(
                    journal_entry_id=entry_id,
                    user_id=entry.user_id,
                    old_content=previous_content,
                    new_content=new_content,
                    edited_at=datetime.now(timezone.utc)
                )
                db.session.add(edit_history)
            db.session.commit()
            logger.info(f"Journal entry {entry_id} updated")
            return entry.to_dict()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update journal entry {entry_id}: {e}")
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
            logger.error(f"Failed to delete journal entry {entry_id}: {e}")
            raise