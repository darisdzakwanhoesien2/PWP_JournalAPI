# journalapi/resources/journal_entry.py
from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
import json

from extensions import db
from journalapi.models import JournalEntry, EditHistory
from journalapi.utils import JsonResponse
from schemas import JournalEntrySchema

entry_schema = JournalEntrySchema()

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


class JournalEntryListResource(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        entries = JournalEntry.query.filter_by(user_id=user_id).all()
        data = []
        for e in entries:
            data.append({
                "id": e.id,
                "title": e.title,
                "tags": json.loads(e.tags),
                "last_updated": e.last_updated.isoformat() if e.last_updated else None
            })
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
            tags=json.dumps(data.get("tags", []))
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

        return JsonResponse({
            "id": entry.id,
            "title": entry.title,
            "content": entry.content,
            "tags": json.loads(entry.tags),
            "sentiment_score": entry.sentiment_score,
            "sentiment_tag": json.loads(entry.sentiment_tag),
            "date": entry.date.isoformat() if entry.date else None,
            "last_updated": entry.last_updated.isoformat() if entry.last_updated else None
        }, 200)

    @jwt_required()
    def put(self, entry_id):
        """Full replacement + log to EditHistory."""
        user_id = get_jwt_identity()
        try:
            data = entry_schema.load(request.get_json())
        except ValidationError as err:
            return JsonResponse({"errors": err.messages}, 422)

        entry = JournalEntry.query.get(entry_id)
        if not entry or entry.user_id != user_id:
            return JsonResponse({"error": "Not found"}, 404)

        # Capture the previous content before we overwrite it
        old_content = entry.content

        # Update the entry
        entry.title = data["title"]
        entry.content = data["content"]
        entry.tags = json.dumps(data["tags"])
        db.session.commit()

        # Create an edit-history record
        edit_record = EditHistory(
            journal_entry_id=entry.id,
            user_id=user_id,
            previous_content=old_content,
            new_content=data["content"]
        )
        db.session.add(edit_record)
        db.session.commit()

        return JsonResponse({"message": "Entry fully replaced, edit logged"}, 200)

    @jwt_required()
    def delete(self, entry_id):
        user_id = get_jwt_identity()
        entry = JournalEntry.query.get(entry_id)
        if not entry or entry.user_id != user_id:
            return JsonResponse({"error": "Not found"}, 404)

        db.session.delete(entry)
        db.session.commit()
        return JsonResponse({"message": "Entry deleted successfully"}, 200)
