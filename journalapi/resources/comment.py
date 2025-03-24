from flask_restful import Resource, Api
from flask import jsonify, request, url_for
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from journalapi.handlers.comment_handler import CommentHandler
from journalapi.utils import JsonResponse

class JournalCommentsResource(Resource):
    @jwt_required()
    def post(self, entry_id):
        data = request.get_json()
        current_user_id = int(get_jwt_identity())

        if not data or "content" not in data:
            return JsonResponse({"error": "Missing required fields"}, 400)

        comment = CommentService.add_comment(entry_id, current_user_id, data["content"])
        return JsonResponse({"message": "Comment added successfully", "comment": comment}, 201)

    @jwt_required()
    def get(self, entry_id):
        comments = CommentService.get_comments(entry_id)
        return JsonResponse(comments, 200)

class CommentsResource(Resource):
    @jwt_required()
    def put(self, comment_id):
        data = request.get_json()
        current_user_id = int(get_jwt_identity())

        if not data or "content" not in data:
            return JsonResponse({"error": "Missing required content"}, 400)

        updated_comment = CommentService.update_comment(comment_id, current_user_id, data["content"])
        if updated_comment:
            return JsonResponse({"message": "Comment updated", "comment": updated_comment}, 200)
        return JsonResponse({"error": "Comment not found or unauthorized"}, 404)

    @jwt_required()
    def delete(self, comment_id):
        current_user_id = int(get_jwt_identity())

        if CommentService.delete_comment(comment_id, current_user_id):
            return JsonResponse({"message": "Comment deleted"}, 200)
        return JsonResponse({"error": "Comment not found or unauthorized"}, 404)