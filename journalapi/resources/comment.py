"""Comment API resources for the Journal API."""
from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from extensions import db
from journalapi.models import Comment
from journalapi.utils import json_response
from schemas import CommentSchema

comment_schema = CommentSchema()

class CommentCollectionResource(Resource):
    """Handle comment creation and listing for a journal entry."""
    @jwt_required()
    def get(self, entry_id):
        """Retrieve all comments for a journal entry.
        
        Args:
            entry_id (int): The ID of the journal entry.
        
        Returns:
            tuple: JSON response with list of comments.
        """
        comments = Comment.query.filter_by(journal_entry_id=entry_id).all()
        data = []
        for c in comments:
            item = {
                "id": c.id,
                "journal_entry_id": c.journal_entry_id,
                "user_id": c.user_id,
                "content": c.content,
                "timestamp": c.timestamp.isoformat() if c.timestamp else None,
                "_links": {
                    "self": {"href": f"/entries/{entry_id}/comments/{c.id}"},
                    "edit": {"href": f"/entries/{entry_id}/comments/{c.id}"},
                    "delete": {"href": f"/entries/{entry_id}/comments/{c.id}"}
                }
            }
            data.append(item)
        return json_response(data, 200)

    @jwt_required()
    def post(self, entry_id):
        """Create a new comment for a journal entry.
        
        Args:
            entry_id (int): The ID of the journal entry.
        
        Returns:
            tuple: JSON response with created comment data.
        """
        try:
            data = comment_schema.load(request.get_json())
        except ValidationError as err:
            return json_response({"errors": err.messages}, 422)
        user_id = int(get_jwt_identity())
        comment = Comment(journal_entry_id=entry_id, user_id=user_id, content=data["content"])
        db.session.add(comment)
        db.session.commit()
        return json_response({"comment_id": comment.id}, 201)

class CommentItemResource(Resource):
    """Handle individual comment operations."""
    @jwt_required()
    def put(self, entry_id, comment_id):
        """Update a comment by ID.
        
        Args:
            entry_id (int): The ID of the journal entry.
            comment_id (int): The ID of the comment.
        
        Returns:
            tuple: JSON response with success message or error.
        """
        try:
            data = comment_schema.load(request.get_json())
        except ValidationError as err:
            return json_response({"errors": err.messages}, 422)
        user_id = int(get_jwt_identity())
        comment = db.session.get(Comment, comment_id)
        if not comment or comment.user_id != user_id or comment.journal_entry_id != entry_id:
            return json_response({"error": "Not found"}, 404)
        comment.content = data["content"]
        db.session.commit()
        return json_response({"message": "Comment fully replaced"}, 200)

    @jwt_required()
    def delete(self, entry_id, comment_id):
        """Delete a comment by ID.
        
        Args:
            entry_id (int): The ID of the journal entry.
            comment_id (int): The ID of the comment.
        
        Returns:
            tuple: JSON response with success message or error.
        """
        user_id = int(get_jwt_identity())
        comment = db.session.get(Comment, comment_id)
        if not comment or comment.user_id != user_id or comment.journal_entry_id != entry_id:
            return json_response({"error": "Not found"}, 404)
        db.session.delete(comment)
        db.session.commit()
        return json_response({"message": "Comment deleted successfully"}, 200)

# # PWP_JournalAPI/journalapi/resources/comment.py
# # journalapi/resources/comment.py
# from flask_restful import Resource
# from flask import request
# from flask_jwt_extended import jwt_required, get_jwt_identity
# from marshmallow import ValidationError
# from extensions import db
# from journalapi.models import Comment
# from journalapi.utils import JsonResponse
# from schemas import CommentSchema

# comment_schema = CommentSchema()

# class CommentCollectionResource(Resource):
#     @jwt_required()
#     def get(self, entry_id):
#         comments = Comment.query.filter_by(journal_entry_id=entry_id).all()
#         data = []
#         for c in comments:
#             item = {
#                 "id": c.id,
#                 "journal_entry_id": c.journal_entry_id,
#                 "user_id": c.user_id,
#                 "content": c.content,
#                 "timestamp": c.timestamp.isoformat() if c.timestamp else None,
#                 "_links": {
#                     "self": {"href": f"/entries/{entry_id}/comments/{c.id}"},
#                     "edit": {"href": f"/entries/{entry_id}/comments/{c.id}"},
#                     "delete": {"href": f"/entries/{entry_id}/comments/{c.id}"}
#                 }
#             }
#             data.append(item)
#         return JsonResponse(data, 200)

#     @jwt_required()
#     def post(self, entry_id):
#         try:
#             data = comment_schema.load(request.get_json())
#         except ValidationError as err:
#             return JsonResponse({"errors": err.messages}, 422)
#         user_id = int(get_jwt_identity())
#         comment = Comment(journal_entry_id=entry_id, user_id=user_id, content=data["content"])
#         db.session.add(comment)
#         db.session.commit()
#         return JsonResponse({"comment_id": comment.id}, 201)

# class CommentItemResource(Resource):
#     @jwt_required()
#     def put(self, entry_id, comment_id):
#         try:
#             data = comment_schema.load(request.get_json())
#         except ValidationError as err:
#             return JsonResponse({"errors": err.messages}, 422)
#         user_id = int(get_jwt_identity())
#         comment = db.session.get(Comment, comment_id)
#         if not comment or comment.user_id != user_id or comment.journal_entry_id != entry_id:
#             return JsonResponse({"error": "Not found"}, 404)
#         comment.content = data["content"]
#         db.session.commit()
#         return JsonResponse({"message": "Comment fully replaced"}, 200)

#     @jwt_required()
#     def delete(self, entry_id, comment_id):
#         user_id = int(get_jwt_identity())
#         comment = db.session.get(Comment, comment_id)
#         if not comment or comment.user_id != user_id or comment.journal_entry_id != entry_id:
#             return JsonResponse({"error": "Not found"}, 404)
#         db.session.delete(comment)
#         db.session.commit()
#         return JsonResponse({"message": "Comment deleted successfully"}, 200)