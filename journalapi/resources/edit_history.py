"""Edit history API resources for the Journal API."""
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from journalapi.models import EditHistory
from journalapi.utils import json_response

class EditHistoryResource(Resource):
    """Handle edit history retrieval for a journal entry."""
    @jwt_required()
    def get(self, entry_id):
        """Retrieve edit history for a journal entry.
        
        Args:
            entry_id (int): The ID of the journal entry.
        
        Returns:
            tuple: JSON response with list of edit history records.
        """
        edits = EditHistory.query.filter_by(journal_entry_id=entry_id).all()
        data = [edit.to_dict() for edit in edits]
        return json_response(data, 200)