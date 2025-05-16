# PWP_JournalAPI/journalapi/resources/edit_history.py
# PWP_JournalAPI/journalapi/resources/edit_history.py
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from journalapi.models import EditHistory
from journalapi.utils import JsonResponse

class EditHistoryResource(Resource):
    @jwt_required()
    def get(self, entry_id):
        edits = EditHistory.query.filter_by(journal_entry_id=entry_id).all()
        data = [edit.to_dict() for edit in edits]
        return JsonResponse(data, 200)