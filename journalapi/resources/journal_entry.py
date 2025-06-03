"""Journal entry API resources for the Journal API."""
from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from journalapi.handlers.journal_entry_handler import JournalEntryHandler
from journalapi.utils import json_response
from schemas import JournalEntrySchema
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

entry_schema = JournalEntrySchema()

class JournalEntryListResource(Resource):
    """Handle journal entry creation and listing."""

    @jwt_required()
    def get(self):
        """Retrieve all journal entries for the authenticated user."""
        try:
            user_id = int(get_jwt_identity())
            entries = JournalEntryHandler.get_entries(user_id)
            logger.info(f"Retrieved {len(entries)} entries for user {user_id}")
            return json_response(entries, 200)
        except Exception as e:
            logger.error(f"Error retrieving entries: {e}")
            return json_response({"error": "Internal server error"}, 500)

    @jwt_required()
    def post(self):
        """Create a new journal entry."""
        try:
            user_id = int(get_jwt_identity())
            data = entry_schema.load(request.get_json())
            entry = JournalEntryHandler.create_entry(
                user_id=user_id,
                title=data["title"],
                content=data["content"],
                tags=data.get("tags", [])
            )
            logger.info(f"Created entry ID {entry['id']} for user {user_id}")
            return json_response({"id": entry["id"], "_links": {"self": f"/api/entries/{entry['id']}"}}, 201)
        except ValidationError as e:
            logger.error(f"Validation error: {e.messages}")
            return json_response({"error": e.messages}, 422)
        except Exception as e:
            logger.error(f"Error creating entry: {e}")
            return json_response({"error": "Internal server error"}, 500)

class JournalEntryResource(Resource):
    """Handle individual journal entry operations."""

    @jwt_required()
    def get(self, entry_id: int):
        """Retrieve a journal entry by ID."""
        try:
            user_id = int(get_jwt_identity())
            entry = JournalEntryHandler.get_entry(entry_id)
            if not entry or entry["user_id"] != user_id:
                logger.warning(f"Unauthorized access to entry {entry_id}")
                return json_response({"error": "Not found or unauthorized"}, 403)
            logger.info(f"Retrieved entry {entry_id}")
            return json_response(entry, 200)
        except Exception as e:
            logger.error(f"Error retrieving entry {entry_id}: {e}")
            return json_response({"error": "Internal server error"}, 500)

    @jwt_required()
    def put(self, entry_id: int):
        """Update a journal entry by ID."""
        try:
            user_id = int(get_jwt_identity())
            data = entry_schema.load(request.get_json())
            entry = JournalEntryHandler.update_entry(
                entry_id=entry_id,
                title=data.get("title"),
                content=data.get("content"),
                tags=data.get("tags")
            )
            if not entry:
                logger.warning(f"Unauthorized update to entry {entry_id}")
                return json_response({"error": "Not found or unauthorized"}, 403)
            logger.info(f"Updated entry {entry_id}")
            return json_response({"message": "Entry updated", "_links": {"self": f"/api/entries/{entry_id}"}}, 200)
        except ValidationError as e:
            logger.error(f"Validation error: {e.messages}")
            return json_response({"error": e.messages}, 422)
        except Exception as e:
            logger.error(f"Error updating entry {entry_id}: {e}")
            return json_response({"error": "Internal server error"}, 500)

    @jwt_required()
    def delete(self, entry_id: int):
        """Delete a journal entry by ID."""
        try:
            user_id = int(get_jwt_identity())
            success = JournalEntryHandler.delete_entry(entry_id)
            if not success:
                logger.warning(f"Unauthorized delete for entry {entry_id}")
                return json_response({"error": "Not found or unauthorized"}, 403)
            logger.info(f"Deleted entry {entry_id}")
            return json_response({"message": "Entry deleted successfully"}, 200)
        except Exception as e:
            logger.error(f"Error deleting entry {entry_id}: {e}")
            return json_response({"error": "Internal server error"}, 500)