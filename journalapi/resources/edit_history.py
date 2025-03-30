# journalapi/resources/edit_history.py
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from journalapi.models import EditHistory
from journalapi.utils import JsonResponse

class EditHistoryResource(Resource):
    @jwt_required()
    def get(self, entry_id):
        """Retrieve all edit history records for a given JournalEntry."""
        user_id = get_jwt_identity()
        
        # If you need to verify that the current user is the owner 
        # of this entry, you'd do a quick check here – 
        # for instance, checking if the entry_id belongs to the user.

        edits = EditHistory.query.filter_by(journal_entry_id=entry_id).all()
        data = []
        for edit in edits:
            data.append({
                "id": edit.id,
                "edited_at": edit.edited_at.isoformat(),
                "editor_id": edit.user_id,
                "previous_content": edit.previous_content,
                "new_content": edit.new_content
            })

        return JsonResponse(data, 200)
