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
        return JsonResponse([
            {
                "id": e.id,
                "title": e.title,
                "tags": json.loads(e.tags),
                "last_updated": e.last_updated.isoformat()
            } for e in entries
        ], 200)

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data or not data.get("title") or not data.get("content"):
            return JsonResponse({"error": "Missing title or content"}, 400)

        entry = JournalEntry(
            user_id=user_id,
            title=data["title"],
            content=data["content"],
            tags=json.dumps(data.get("tags", []))
        )
        db.session.add(entry)
        db.session.commit()
        return JsonResponse({"entry_id": entry.id}, 201)

class JournalEntryResource(Resource):
    @jwt_required()
    def get(self, entry_id):
        user_id = get_jwt_identity()
        entry = db.session.get(JournalEntry, entry_id)
        if not entry or entry.user_id != user_id:
            return JsonResponse({"error": "Not found"}, 404)

        return JsonResponse({
            "id": entry.id,
            "title": entry.title,
            "content": entry.content,
            "tags": json.loads(entry.tags),
            "sentiment_score": entry.sentiment_score,
            "sentiment_tag": json.loads(entry.sentiment_tag),
            "date": entry.date.isoformat(),
            "last_updated": entry.last_updated.isoformat()
        }, 200)

    @jwt_required()
    def put(self, entry_id):
        user_id = get_jwt_identity()
        data = request.get_json()

        required_fields = ["title", "content", "tags"]
        if not data or any(f not in data for f in required_fields):
            return JsonResponse({"error": "Missing required fields for full replacement"}, 400)

        entry = db.session.get(JournalEntry, entry_id)
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
        entry = db.session.get(JournalEntry, entry_id)
        if not entry or entry.user_id != user_id:
            return JsonResponse({"error": "Not found"}, 404)

        db.session.delete(entry)
        db.session.commit()
        return JsonResponse({"message": "Entry deleted successfully"}, 200)
