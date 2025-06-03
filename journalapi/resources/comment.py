"""Comment API resources for the Journal API."""
from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from journalapi.handlers.comment_handler import CommentHandler
from journalapi.utils import json_response
from schemas import CommentSchema
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

comment_schema = CommentSchema()

class CommentCollectionResource(Resource):
    """Handle comment creation and listing for a journal entry."""

    @jwt_required()
    def get(self, entry_id: int):
        """Retrieve all comments for a journal entry."""
        try:
            comments = CommentHandler.get_comments(entry_id)
            if comments is None:
                logger.warning(f"Journal entry {entry_id} not found")
                return json_response({"error": "Entry not found"}, 404)
            logger.info(f"Retrieved {len(comments)} comments for entry {entry_id}")
            return json_response(comments, 200)
        except Exception as e:
            logger.error(f"Error retrieving comments: {e}")
            return json_response({"error": "Internal server error"}, 500)

    @jwt_required()
    def post(self, entry_id: int):
        """Create a new comment for a journal entry."""
        try:
            data = comment_schema.load(request.get_json())
            user_id = int(get_jwt_identity())
            comment = CommentHandler.add_comment(entry_id, user_id, data["content"])
            if not comment:
                logger.warning(f"Journal entry {entry_id} not found")
                return json_response({"error": "Entry not found"}, 404)
            logger.info(f"Comment created for entry {entry_id}")
            return json_response({"id": comment["id"], "_links": {"self": f"/api/entries/{entry_id}/comments/{comment['id']}"}}, 201)
        except ValidationError as e:
            logger.error(f"Validation error: {e.messages}")
            return json_response({"error": e.messages}, 422)
        except Exception as e:
            logger.error(f"Error creating comment: {e}")
            return json_response({"error": "Internal server error"}, 500)

class CommentItemResource(Resource):
    """Handle individual comment operations."""

    @jwt_required()
    def get(self, entry_id: int, comment_id: int):
        """Retrieve a single comment."""
        try:
            comment = CommentHandler.get_comment(comment_id)
            if not comment or comment["journal_entry_id"] != entry_id:
                logger.warning(f"Comment {comment_id} not found for entry {entry_id}")
                return json_response({"error": "Not found"}, 404)
            logger.info(f"Retrieved comment {comment_id}")
            return json_response(comment, 200)
        except Exception as e:
            logger.error(f"Error retrieving comment {comment_id}: {e}")
            return json_response({"error": "Internal server error"}, 500)

    @jwt_required()
    def put(self, entry_id: int, comment_id: int):
        """Update a comment by ID."""
        try:
            user_id = int(get_jwt_identity())
            data = comment_schema.load(request.get_json())
            comment = CommentHandler.update_comment(comment_id, user_id, data["content"])
            if not comment:
                logger.warning(f"Unauthorized update for comment {comment_id}")
                return json_response({"error": "Not found or unauthorized"}, 403)
            logger.info(f"Comment {comment_id} updated")
            return json_response({"message": "Comment updated", "_links": {"self": f"/api/entries/{entry_id}/comments/{comment_id}"}}, 200)
        except ValidationError as e:
            logger.error(f"Validation error: {e.messages}")
            return json_response({"error": e.messages}, 422)
        except Exception as e:
            logger.error(f"Error updating comment {comment_id}: {e}")
            return json_response({"error": "Internal server error"}, 500)

    @jwt_required()
    def delete(self, entry_id: int, comment_id: int):
        """Delete a comment by ID."""
        try:
            user_id = int(get_jwt_identity())
            success = CommentHandler.delete_comment(comment_id, user_id)
            if not success:
                logger.warning(f"Unauthorized delete for comment {comment_id}")
                return json_response({"error": "Not found or unauthorized"}, 403)
            logger.info(f"Comment {comment_id} deleted")
            return json_response({"message": "Comment deleted successfully"}, 200)
        except Exception as e:
            logger.error(f"Error deleting comment {comment_id}: {e}")
            return json_response({"error": "Internal server error"}, 500)