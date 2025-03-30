# journalapi/resources/journal_entry.py
from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
import json

from extensions import db
from journalapi.models import JournalEntry
from journalapi.utils import JsonResponse
from schemas import JournalEntrySchema

entry_schema = JournalEntrySchema()

class JournalEntryListResource(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        entries = JournalEntry.query.filter_by(user_id=user_id).all()
        data = [entry.to_dict() for entry in entries]
        return JsonResponse(data, 200)

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        try:
            data = entry_schema.load(request.get_json())
        except ValidationError as err:
            return JsonResponse({"errors": err.messages}, 422)

        new_entry = JournalEntry(
            user_id=user_id,
            title=data["title"],
            content=data["content"],
            tags=json.dumps(data.get("tags", [])),
            sentiment_score=0.75,  # example sentiment score
            sentiment_tag=json.dumps(["positive"])
        )
        db.session.add(new_entry)
        db.session.commit()
        return JsonResponse({"entry_id": new_entry.id}, 201)

class JournalEntryResource(Resource):
    @jwt_required()
    def get(self, entry_id):
        user_id = get_jwt_identity()
        entry = JournalEntry.query.get(entry_id)
        if not entry or entry.user_id != user_id:
            return JsonResponse({"error": "Not found"}, 404)
        return JsonResponse(entry.to_dict(), 200)

    @jwt_required()
    def put(self, entry_id):
        user_id = get_jwt_identity()
        try:
            data = entry_schema.load(request.get_json())
        except ValidationError as err:
            return JsonResponse({"errors": err.messages}, 422)

        entry = JournalEntry.query.get(entry_id)
        if not entry or entry.user_id != user_id:
            return JsonResponse({"error": "Not found"}, 404)

        entry.title = data["title"]
        entry.content = data["content"]
        entry.tags = json.dumps(data["tags"])
        db.session.commit()
        return JsonResponse({"message": "Entry fully replaced"}, 200)

    @jwt_required()
    def delete(self, entry_id):
        user_id = get_jwt_identity()
        entry = JournalEntry.query.get(entry_id)
        if not entry or entry.user_id != user_id:
            return JsonResponse({"error": "Not found"}, 404)
        db.session.delete(entry)
        db.session.commit()
        return JsonResponse({"message": "Entry deleted successfully"}, 200)
