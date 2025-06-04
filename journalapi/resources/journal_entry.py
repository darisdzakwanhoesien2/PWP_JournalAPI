"""Journal entry API resources for the Journal API."""
from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from journalapi.handlers.journal_entry_handler import JournalEntryHandler
from journalapi.utils import json_response
from journalapi.models import JournalEntry
from schemas import JournalEntrySchema

entry_schema = JournalEntrySchema()

class JournalEntryListResource(Resource):
    """Handle journal entry creation and listing."""
    @jwt_required()
    def get(self):
        """Retrieve all journal entries for the current user.
        
        Returns:
            Response: JSON response with list of entries.
        """
        user_id = int(get_jwt_identity())
        entries = JournalEntryHandler.get_entries(user_id)
        return json_response(entries, 200)

    @jwt_required()
    def post(self):
        """Create a new journal entry.
        
        Returns:
            Response: JSON response with created entry ID.
        """
        try:
            data = entry_schema.load(request.get_json())
        except ValidationError as err:
            return json_response({"errors": err.messages}, 422)
        user_id = int(get_jwt_identity())
        result = JournalEntryHandler.create_entry(
            user_id, data["title"], data["content"], data["tags"]
        )
        return json_response({"entry_id": result["entry_id"], "message": "Entry created successfully"}, 201)

class JournalEntryResource(Resource):
    """Handle individual journal entry operations."""
    @jwt_required()
    def get(self, entry_id: int):
        """Retrieve a journal entry by ID.
        
        Args:
            entry_id: The ID of the journal entry.
        
        Returns:
            Response: JSON response with entry data or error.
        """
        entry = JournalEntryHandler.get_entry(entry_id)
        if not entry:
            return json_response({"error": "Entry not found"}, 404)
        user_id = int(get_jwt_identity())
        if entry["user_id"] != user_id:
            return json_response({"error": "Unauthorized"}, 403)
        return json_response(entry, 200)

    @jwt_required()
    def put(self, entry_id: int):
        """Update a journal entry by ID.
        
        Args:
            entry_id: The ID of the journal entry.
        
        Returns:
            Response: JSON response with success message or error.
        """
        try:
            data = entry_schema.load(request.get_json())
        except ValidationError as err:
            return json_response({"errors": err.messages}, 422)
        user_id = int(get_jwt_identity())
        entry = JournalEntryHandler.get_entry(entry_id)
        if not entry:
            return json_response({"error": "Entry not found"}, 404)
        if entry["user_id"] != user_id:
            return json_response({"error": "Unauthorized"}, 403)
        updated = JournalEntryHandler.update_entry(
            entry_id, data["title"], data["content"], data["tags"]
        )
        return json_response({"message": "Entry updated successfully"}, 200)

    @jwt_required()
    def delete(self, entry_id: int):
        """Delete a journal entry by ID.
        
        Args:
            entry_id: The ID of the journal entry.
        
        Returns:
            Response: JSON response with success message or error.
        """
        user_id = int(get_jwt_identity())
        entry = JournalEntryHandler.get_entry(entry_id)
        if not entry:
            return json_response({"error": "Entry not found"}, 404)
        if entry["user_id"] != user_id:
            return json_response({"error": "Unauthorized"}, 403)
        if JournalEntryHandler.delete_entry(entry_id):
            return json_response({"message": "Entry deleted successfully"}, 200)
        return json_response({"error": "Failed to delete entry"}, 500)