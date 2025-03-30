from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import JournalEntry
from .. import db
from ..utils import JsonResponse
import json

class JournalEntryListResource(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        entries = JournalEntry.query.filter_by(user_id=user_id).all()
        return JsonResponse([e.title for e in entries], 200)

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        data = request.get_json()
        entry = JournalEntry(user_id=user_id, title=data["title"], content=data["content"], tags=json.dumps(data.get("tags", [])))
        db.session.add(entry)
        db.session.commit()
        return JsonResponse({"entry_id": entry.id}, 201)

class JournalEntryResource(Resource):
    @jwt_required()
    def get(self, entry_id):
        user_id = get_jwt_identity()
        entry = JournalEntry.query.get(entry_id)
        if not entry or entry.user_id != user_id:
            return JsonResponse({"error": "Not found"}, 404)
        return JsonResponse({"title": entry.title, "content": entry.content}, 200)

    @jwt_required()
    def put(self, entry_id):
        user_id = get_jwt_identity()
        data = request.get_json()
        entry = JournalEntry.query.get(entry_id)
        if not entry or entry.user_id != user_id:
            return JsonResponse({"error": "Not found"}, 404)
        entry.title = data["title"]
        entry.content = data["content"]
        entry.tags = json.dumps(data.get("tags", []))
        db.session.commit()
        return JsonResponse({"message": "Updated"}, 200)

    @jwt_required()
    def delete(self, entry_id):
        user_id = get_jwt_identity()
        entry = JournalEntry.query.get(entry_id)
        if not entry or entry.user_id != user_id:
            return JsonResponse({"error": "Not found"}, 404)
        db.session.delete(entry)
        db.session.commit()
        return JsonResponse({"message": "Deleted"}, 200)