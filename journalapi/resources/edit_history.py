# PWP_JournalAPI/journalapi/resources/edit_history.py
"""Edit history API resources for the Journal API."""
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from journalapi.models import EditHistory, JournalEntry
from journalapi.utils import json_response
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EditHistoryResource(Resource):
    """Handle edit history retrieval for a journal entry."""

    @jwt_required()
    def get(self, entry_id: int):
        """Retrieve edit history for a journal entry.

        Args:
            entry_id (int): ID of the journal entry.

        Returns:
            JSON response with edit history or error message.
        """
        try:
            user_id = int(get_jwt_identity())
            entry = db.session.get(JournalEntry, entry_id)
            if not entry or entry.user_id != user_id:
                logger.warning(f"Unauthorized access to entry {entry_id} by user {user_id}")
                return json_response({"error": "Journal entry not found or unauthorized"}, 403)
            edits = EditHistory.query.filter_by(journal_entry_id=entry_id).all()
            logger.info(f"Retrieved {len(edits)} edit history records for entry {entry_id}")
            return json_response([edit.to_dict() for edit in edits], 200)
        except ValueError as ve:
            logger.error(f"Invalid user ID format: {ve}")
            return json_response({"error": "Invalid authentication token"}, 401)
        except Exception as e:
            logger.error(f"Error retrieving edit history for entry {entry_id}: {e}")
            return json_response({"error": "Internal server error"}, 500)