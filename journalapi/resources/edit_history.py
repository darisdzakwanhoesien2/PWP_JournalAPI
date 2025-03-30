# journalapi/resources/edit_history.py
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from journalapi.models import EditHistory
from journalapi.utils import JsonResponse

class EditHistoryResource(Resource):
    @jwt_required()
    def get(self, entry_id):
        user_id = get_jwt_identity()
        # (Optionally, you can check that the user owns the entry.)
        edits = EditHistory.query.filter_by(journal_entry_id=entry_id).all()
        data = [edit.to_dict() for edit in edits]
        return JsonResponse(data, 200)
