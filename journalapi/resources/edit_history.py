# journalapi/resources/edit_history.py
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from journalapi.models import EditHistory
from journalapi.utils import JsonResponse

class EditHistoryResource(Resource):
    @jwt_required()
    def get(self, entry_id):
        user_id = int(get_jwt_identity())
        edits = EditHistory.query.filter_by(journal_entry_id=entry_id).all()
        data = []
        for edit in edits:
            item = edit.to_dict()
            item["_links"] = {
                "self": {"href": f"/entries/{entry_id}/history/{edit.id}"},
                "entry": {"href": f"/entries/{entry_id}"}
            }
            data.append(item)
        response_data = {
            "edits": data,
            "_links": {
                "self": {"href": f"/entries/{entry_id}/history"},
                "entry": {"href": f"/entries/{entry_id}"}
            }
        }
        return JsonResponse(response_data, 200)