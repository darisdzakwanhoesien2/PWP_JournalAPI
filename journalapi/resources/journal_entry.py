from flask_restful import Resource, Api
from flask import jsonify, request, url_for
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from journalapi.handlers.journal_entry_handler import JournalEntryHandler
from journalapi.utils import JsonResponse

class JornalEntriesResource(Resource):
    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity())
        entries = JournalEntryService.get_entries(user_id) 
        return JsonResponse(entries, 200)
    @jwt_required()
    def post(self):
        data = request.get_json()
        current_user_id = int(get_jwt_identity())

        entry = JournalEntryService.create_entry(
            user_id=current_user_id,
            title=data["title"],
            content=data["content"],
            tags=data.get("tags", [])
        )

        return JsonResponse({
            "message": "Entry created successfully",
            "entry_id": entry["entry_id"]
        }, 201)

class JournalEntryResource(Resource):
    @jwt_required()
    def get(self, entry_id):
        user_id = int(get_jwt_identity())
        entry = JournalEntryService.get_entry(entry_id)

        if not entry or entry.get("user_id") != user_id:
            return JsonResponse({"error": "Entry not found"}, 404) 

        return JsonResponse(entry, 200)

    @jwt_required()
    def put(self, entry_id):
        user_id = int(get_jwt_identity())
        data = request.get_json()

        updated_entry = JournalEntryService.update_entry(
            entry_id,
            title=data.get("title"),
            content=data.get("content"),
            tags=data.get("tags")
        )

        if not updated_entry or updated_entry.get("user_id") != user_id:
            return JsonResponse({"error": "Entry not found"}, 404) 

        return JsonResponse({
            "message": "Entry updated successfully", 
            "entry": updated_entry
            }, 200)

    @jwt_required()
    def delete(self, entry_id):
        user_id = int(get_jwt_identity())
        if not JournalEntryService.delete_entry(entry_id):
            return JsonResponse({"error": "Entry not found"}, 404)

        return JsonResponse({"message": "Entry deleted successfully"}, 200)