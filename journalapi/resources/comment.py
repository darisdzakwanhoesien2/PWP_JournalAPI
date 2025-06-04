# journalapi/resources/comment.py
"""Comment API resources for the Journal API."""
from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from journalapi.handlers.comment_handler import CommentHandler
from journalapi.utils import json_response
from journalapi.models import JournalEntry
from schemas import CommentSchema

comment_schema = CommentSchema()

class CommentCollectionResource(Resource):
    """Handle comment creation and listing for a journal entry."""
    @jwt_required()
    def get(self, entry_id: int):
        """Retrieve all comments for a journal entry.
        
        Args:
            entry_id: The ID of the journal entry.
        
        Returns:
            Response: JSON response with list of comments.
        """
        if not JournalEntry.query.get(entry_id):
            return json_response({"error": "Journal entry not found"}, 404)
        comments = CommentHandler.get_comments(entry_id)
        data = [
            {
                **c,
                "_links": {
                    "self": f"/journal_entries/{entry_id}/comments/{c['id']}",
                    "edit": f"/journal_entries/{entry_id}/comments/{c['id']}",
                    "delete": f"/journal_entries/{entry_id}/comments/{c['id']}"
                }
            } for c in comments
        ]
        return json_response(data, 200)

    @jwt_required()
    def post(self, entry_id: int):
        """Create a new comment for a journal entry.
        
        Args:
            entry_id: The ID of the journal entry.
        
        Returns:
            Response: JSON response with created comment data.
        """
        if not JournalEntry.query.get(entry_id):
            return json_response({"error": "Journal entry not found"}, 404)
        try:
            data = comment_schema.load(request.get_json())
        except ValidationError as err:
            return json_response({"errors": err.messages}, 422)
        user_id = int(get_jwt_identity())
        comment = CommentHandler.add_comment(entry_id, user_id, data["content"])
        return json_response({"comment_id": comment["id"], "message": "Comment created successfully"}, 201)

class CommentItemResource(Resource):
    """Handle individual comment operations."""
    @jwt_required()
    def put(self, entry_id: int, comment_id: int):
        """Update a comment by ID.
        
        Args:
            entry_id: The ID of the journal entry.
            comment_id: The ID of the comment.
        
        Returns:
            Response: JSON response with success message or error.
        """
        if not JournalEntry.query.get(entry_id):
            return json_response({"error": "Journal entry not found"}, 404)
        try:
            data = comment_schema.load(request.get_json())
        except ValidationError as err:
            return json_response({"errors": err.messages}, 422)
        user_id = int(get_jwt_identity())
        comment = CommentHandler.update_comment(comment_id, user_id, data["content"])
        if not comment:
            return json_response({"error": "Not found or unauthorized"}, 404)
        return json_response({"message": "Comment fully replaced"}, 200)

    @jwt_required()
    def delete(self, entry_id: int, comment_id: int):
        """Delete a comment by ID.
        
        Args:
            entry_id: The ID of the journal entry.
            comment_id: The ID of the comment.
        
        Returns:
            Response: JSON response with success message or error.
        """
        if not JournalEntry.query.get(entry_id):
            return json_response({"error": "Journal entry not found"}, 404)
        user_id = int(get_jwt_identity())
        if CommentHandler.delete_comment(comment_id, user_id):
            return json_response({"message": "Comment deleted successfully"}, 200)
        return json_response({"error": "Not found or unauthorized"}, 404)