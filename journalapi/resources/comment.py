from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import Comment
from .. import db
from ..utils import JsonResponse

class CommentCollectionResource(Resource):
    @jwt_required()
    def get(self, entry_id):
        comments = Comment.query.filter_by(journal_entry_id=entry_id).all()
        return JsonResponse([
            {
                "id": c.id,
                "user_id": c.user_id,
                "content": c.content,
                "timestamp": c.timestamp.isoformat()
            } for c in comments
        ], 200)

    @jwt_required()
    def post(self, entry_id):
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data or "content" not in data:
            return JsonResponse({"error": "Missing content"}, 400)

        comment = Comment(journal_entry_id=entry_id, user_id=user_id, content=data["content"])
        db.session.add(comment)
        db.session.commit()
        return JsonResponse({"comment_id": comment.id}, 201)

class CommentItemResource(Resource):
    @jwt_required()
    def put(self, entry_id, comment_id):
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data or "content" not in data:
            return JsonResponse({"error": "Missing content for full replacement"}, 400)

        comment = db.session.get(Comment, comment_id)
        if not comment or comment.user_id != user_id or comment.journal_entry_id != entry_id:
            return JsonResponse({"error": "Not found"}, 404)

        comment.content = data["content"]
        db.session.commit()
        return JsonResponse({"message": "Comment fully replaced"}, 200)

    @jwt_required()
    def delete(self, entry_id, comment_id):
        user_id = get_jwt_identity()
        comment = db.session.get(Comment, comment_id)
        if not comment or comment.user_id != user_id or comment.journal_entry_id != entry_id:
            return JsonResponse({"error": "Not found"}, 404)

        db.session.delete(comment)
        db.session.commit()
        return JsonResponse({"message": "Comment deleted successfully"}, 200)
