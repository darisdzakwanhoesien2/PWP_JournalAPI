# journalapi/resources/comment.py
from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from extensions import db
from journalapi.models import Comment
from journalapi.utils import JsonResponse
from schemas import CommentSchema

comment_schema = CommentSchema()

class CommentCollectionResource(Resource):
    @jwt_required()
    def get(self, entry_id):
        comments = Comment.query.filter_by(journal_entry_id=entry_id).all()
        data = []
        for c in comments:
            data.append({
                "id": c.id,
                "user_id": c.user_id,
                "content": c.content,
                "timestamp": c.timestamp.isoformat() if c.timestamp else None
            })
        return JsonResponse(data, 200)

    @jwt_required()
    def post(self, entry_id):
        user_id = get_jwt_identity()
        try:
            data = comment_schema.load(request.get_json())
        except ValidationError as err:
            return JsonResponse({"errors": err.messages}, 422)

        comment = Comment(
            journal_entry_id=entry_id,
            user_id=user_id,
            content=data["content"]
        )
        db.session.add(comment)
        db.session.commit()

        return JsonResponse({"comment_id": comment.id}, 201)

class CommentItemResource(Resource):
    @jwt_required()
    def put(self, entry_id, comment_id):
        user_id = get_jwt_identity()
        try:
            data = comment_schema.load(request.get_json())
        except ValidationError as err:
            return JsonResponse({"errors": err.messages}, 422)

        comment = Comment.query.get(comment_id)
        if not comment or comment.user_id != user_id or comment.journal_entry_id != entry_id:
            return JsonResponse({"error": "Not found"}, 404)

        comment.content = data["content"]
        db.session.commit()
        return JsonResponse({"message": "Comment fully replaced"}, 200)

    @jwt_required()
    def delete(self, entry_id, comment_id):
        user_id = get_jwt_identity()
        comment = Comment.query.get(comment_id)
        if not comment or comment.user_id != user_id or comment.journal_entry_id != entry_id:
            return JsonResponse({"error": "Not found"}, 404)

        db.session.delete(comment)
        db.session.commit()
        return JsonResponse({"message": "Comment deleted successfully"}, 200)
