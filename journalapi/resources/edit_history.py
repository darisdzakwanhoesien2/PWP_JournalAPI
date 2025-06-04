"""Edit history API resource for the Journal API."""
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from journalapi.models import EditHistory, JournalEntry
from journalapi.utils import json_response

class EditHistoryResource(Resource):
    """Handle edit history retrieval for a journal entry."""
    @jwt_required()
    def get(self, entry_id: int):
        """Retrieve edit history for a journal entry.
        
        Args:
            entry_id: The ID of the journal entry.
        
        Returns:
            Response: JSON response with edit history data or error.
        """
        user_id = int(get_jwt_identity())
        entry = JournalEntry.query.get(entry_id)
        if not entry:
            return json_response({"error": "Journal entry not found"}, 404)
        if entry.user_id != user_id:
            return json_response({"error": "Unauthorized"}, 403)
        history = EditHistory.query.filter_by(journal_entry_id=entry_id).all()
        return json_response([h.to_dict() for h in history], 200)