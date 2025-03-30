from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Comment, JournalEntry
from .. import db
from ..utils import JsonResponse

class CommentCollectionResource(Resource):
    @jwt_required()
    def get(self, entry_id):
        comments = Comment.query.filter_by(journal_entry_id=entry_id).all()
        return JsonResponse([{"id": c.id, "content": c.content} for c in comments], 200)

    @jwt_required()
    def post(self, entry_id):
        user_id = get_jwt_identity()
        data = request.get_json()
        comment = Comment(journal_entry_id=entry_id, user_id=user_id, content=data["content"])
        db.session.add(comment)
        db.session.commit()
        return JsonResponse({"comment_id": comment.id}, 201)

class CommentItemResource(Resource):
    @jwt_required()
    def put(self, entry_id, comment_id):
        user_id = get_jwt_identity()
        comment = Comment.query.get(comment_id)
        if not comment or comment.user_id != user_id or comment.journal_entry_id != entry_id:
            return JsonResponse({"error": "Not found"}, 404)
        comment.content = request.get_json()["content"]
        db.session.commit()
        return JsonResponse({"message": "Updated"}, 200)

    @jwt_required()
    def delete(self, entry_id, comment_id):
        user_id = get_jwt_identity()
        comment = Comment.query.get(comment_id)
        if not comment or comment.user_id != user_id or comment.journal_entry_id != entry_id:
            return JsonResponse({"error": "Not found"}, 404)
        db.session.delete(comment)
        db.session.commit()
        return JsonResponse({"message": "Deleted"}, 200)
